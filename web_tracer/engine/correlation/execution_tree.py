"""engine/correlation/execution_tree.py — ExecutionTreeBuilder (T37).

Turns the correlated spans of one run into ``execution_tree.json``: a single tree from
the user click down to the SQL statement, with the numbers that answer "where did the
time actually go?".

Rules (workplan §8.4 step 4 / §8.3.2):

* the tree is built from ``parent_span_id``; a span whose parent is missing gets a
  **synthetic root** (``layer=user``, confidence ``0.3``) instead of being dropped;
* a span stitched by the correlation engine (``parent_overrides``) nests under the
  browser request span that triggered it — this is what makes the two streams one tree;
* ``start_offset_ms`` is relative to the root, ``self_time_ms`` = duration − children,
  which is the number that exposes the real bottleneck;
* the result is validated against ``execution_tree_schema.json`` before it is returned,
  so a malformed tree fails here and not in the dashboard.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Callable

from engine import config
from engine.schema.validate import validate_execution_tree

from .models import (
    METHODS,
    METHOD_UNMATCHED,
    NS_PER_MS,
    SYNTHETIC_ROOT_CONFIDENCE,
    collector_of,
    usable_trace_id,
)

TREE_FILENAME = "execution_tree.json"
_MAX_DEPTH = 200  # guard against a malformed parent cycle


def _clamp01(v: object, default: float = 0.0) -> float:
    try:
        f = float(v)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default
    return 0.0 if f < 0 else (1.0 if f > 1 else f)


class ExecutionTreeBuilder:
    """Build ``execution_tree.json`` from correlated SpanEvents."""

    def __init__(self, validate: bool = True):
        self.validate = validate
        self.warnings: list[str] = []

    # ── public API ───────────────────────────────────────────────────────────────
    def build(
        self,
        spans: list[dict],
        result=None,
        trace_id: str | None = None,
        run_id: str | None = None,
    ) -> dict:
        """Build the execution tree.

        ``result`` (optional) supplies the correlation stitches (``parent_overrides``)
        and the ``clock`` record; without it the raw ``parent_span_id`` is used.
        """
        self.warnings = []
        overrides = dict(getattr(result, "parent_overrides", None) or {})
        clock = dict(getattr(result, "clock", None) or {"base": "browser", "offset_ms": {}})
        offsets = clock.get("offset_ms") or {}
        run_id = run_id or getattr(result, "run_id", None)

        spans = [s for s in spans if isinstance(s, dict) and s.get("span_id")]
        by_id: dict[str, dict] = {s["span_id"]: s for s in spans}
        if not spans:
            return self._empty_tree(run_id, trace_id, clock)

        def eff_parent(s: dict) -> str | None:
            return overrides.get(s["span_id"], s.get("parent_span_id"))

        children: dict[str | None, list[dict]] = {}
        for s in spans:
            children.setdefault(eff_parent(s), []).append(s)
        for lst in children.values():
            lst.sort(key=lambda s: int(s.get("start_time_unix_ns") or 0))

        # roots = no parent, or a parent that is not part of this run
        roots: list[dict] = []
        for p, lst in children.items():
            if p is None or p not in by_id:
                roots.extend(lst)
        roots.sort(key=lambda s: int(s.get("start_time_unix_ns") or 0))
        if not roots and spans:
            # every span points at another span (a parent cycle): break it at the
            # earliest span rather than silently returning an empty tree (§5.9)
            earliest = min(spans, key=lambda s: int(s.get("start_time_unix_ns") or 0))
            roots = [earliest]
            self.warnings.append(
                f"no acyclic root span found (parent cycle); using span {earliest.get('span_id')} as root"
            )

        if trace_id:
            filtered = [r for r in roots if r.get("trace_id") == trace_id]
            if not filtered:
                self.warnings.append(
                    f"no root span with trace_id {trace_id}; the tree covers the whole run instead"
                )
            else:
                roots = filtered

        def ns(s: dict) -> int:
            # clock.offset_ms[c] is the correction that was applied to reach the base
            off = float(offsets.get(collector_of(s), 0.0) or 0.0)
            return int(s.get("start_time_unix_ns") or 0) + int(round(off * NS_PER_MS))

        if len(roots) == 1:
            root_span = roots[0]
            root_start = ns(root_span)
            root = self._node(root_span, 0, root_start, children, ns, set())
            total_duration = float(root["duration_ms"])
        else:
            root_start = min(ns(s) for s in spans)
            kids = [self._node(r, 1, root_start, children, ns, {r["span_id"]}) for r in roots]
            # the synthetic root spans from the first start to the last end of its children
            total_duration = round(
                max((float(k["start_offset_ms"]) + float(k["duration_ms"]) for k in kids), default=0.0),
                3,
            )
            root = self._synthetic_root(run_id, kids, total_duration)

        stats = self._stats(root)
        tree = {
            "schema_version": "1.0",
            "trace_id": self._tree_trace_id(spans, roots, trace_id, run_id),
            "run_id": run_id or "",
            "clock": clock,
            "root": root,
            "stats": stats,
        }
        if self.validate:
            validate_execution_tree(tree)
        return tree

    def save(self, tree: dict, out_dir: Path) -> Path:
        """Write ``execution_tree.json`` into ``out_dir`` and return its path."""
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        p = out_dir / TREE_FILENAME
        p.write_text(json.dumps(tree, indent=2), encoding="utf-8")
        return p

    # ── node construction ────────────────────────────────────────────────────────
    def _node(
        self,
        span: dict,
        depth: int,
        root_start: int,
        children: dict[str | None, list[dict]],
        ns: Callable[[dict], int],
        path: set[str],
    ) -> dict:
        sid = span.get("span_id")
        own_path = set(path) | {sid}
        if depth > _MAX_DEPTH:
            self.warnings.append(f"depth limit {_MAX_DEPTH} reached at span {sid}; subtree truncated")
            kids: list[dict] = []
        else:
            raw_kids = children.get(sid, [])
            kids = [k for k in raw_kids if k.get("span_id") not in own_path]
            if len(kids) != len(raw_kids):
                self.warnings.append(
                    f"parent cycle detected at span {sid}: {len(raw_kids) - len(kids)} child span(s) skipped"
                )
            kids = [self._node(k, depth + 1, root_start, children, ns, own_path) for k in kids]

        duration = float(span.get("duration_ms") or 0.0)
        if duration < 0:
            duration = 0.0  # -1 means "not finished"; the tree shows 0 and says so
        self_time = round(max(0.0, duration - sum(float(k["duration_ms"]) for k in kids)), 3)

        return {
            "id": f"span:{sid}",
            "span_id": sid,
            "layer": span.get("layer") if span.get("layer") in config.LAYERS else "browser",
            "name": str(span.get("name") or "<unnamed>"),
            "kind": span.get("kind") if span.get("kind") in ("function", "method", "request", "statement", "event") else "event",
            "source": self._source(span),
            "start_offset_ms": round((ns(span) - root_start) / NS_PER_MS, 3),
            "duration_ms": round(duration, 3),
            "self_time_ms": self_time,
            "status": span.get("status") if span.get("status") in ("ok", "error", "timeout", "aborted", "unknown") else "unknown",
            "confidence": _clamp01(span.get("confidence"), 0.0),
            "correlation": self._correlation(span),
            "attributes": dict(span.get("attributes") or {}),
            "children": kids,
        }

    def _synthetic_root(self, run_id: str | None, kids: list[dict], duration: float) -> dict:
        self_time = round(max(0.0, duration - sum(float(k["duration_ms"]) for k in kids)), 3)
        return {
            "id": "synthetic:root",
            "layer": "user",
            "name": f"Run {run_id}" if run_id else "Synthetic root",
            "kind": "event",
            "source": {"file": "<synthetic>"},
            "start_offset_ms": 0.0,
            "duration_ms": round(max(0.0, duration), 3),
            "self_time_ms": self_time,
            "status": "ok",
            "confidence": SYNTHETIC_ROOT_CONFIDENCE,
            "correlation": {
                "method": "inferred",
                "score": SYNTHETIC_ROOT_CONFIDENCE,
                "reason": "synthetic_root",
            },
            "attributes": {},
            "children": kids,
        }

    def _empty_tree(self, run_id: str | None, trace_id: str | None, clock: dict) -> dict:
        root = self._synthetic_root(run_id, [], 0.0)
        root["name"] = f"Empty run {run_id}" if run_id else "Empty run"
        tree = {
            "schema_version": "1.0",
            "trace_id": trace_id or self._hash_trace_id(run_id or "empty"),
            "run_id": run_id or "",
            "clock": clock,
            "root": root,
            "stats": self._stats(root),
        }
        if self.validate:
            validate_execution_tree(tree)
        return tree

    # ── field helpers ────────────────────────────────────────────────────────────
    @staticmethod
    def _source(span: dict) -> dict:
        """Tree nodes allow ``file`` / ``line`` / ``symbol`` only (schema-confirmed)."""
        src = span.get("source") if isinstance(span.get("source"), dict) else {}
        out: dict = {"file": str(src.get("file") or "<unknown>")}
        if src.get("line") is not None:
            try:
                out["line"] = int(src["line"])
            except (TypeError, ValueError):
                pass
        if src.get("symbol"):
            out["symbol"] = str(src["symbol"])
        return out

    @staticmethod
    def _correlation(span: dict) -> dict:
        c = span.get("correlation") if isinstance(span.get("correlation"), dict) else {}
        method = c.get("method") if c.get("method") in METHODS else METHOD_UNMATCHED
        return {
            "method": method,
            "score": _clamp01(c.get("score"), 0.0),
            "reason": c.get("reason") if isinstance(c.get("reason"), str) else None,
        }

    @staticmethod
    def _hash_trace_id(seed: str) -> str:
        return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:32]

    def _tree_trace_id(
        self, spans: list[dict], roots: list[dict], trace_id: str | None, run_id: str | None
    ) -> str:
        if trace_id and len(trace_id) == 32:
            return trace_id.lower()
        ids = {usable_trace_id(s) for s in (roots or spans)}
        ids.discard(None)
        if len(ids) == 1:
            return ids.pop()  # type: ignore[arg-type]
        return self._hash_trace_id(run_id or (roots[0].get("span_id") if roots else "run"))

    # ── stats ────────────────────────────────────────────────────────────────────
    def _stats(self, root: dict) -> dict:
        node_count = 0
        max_depth = 0
        layers: Counter = Counter()
        unmatched = 0

        def walk(node: dict, depth: int) -> None:
            nonlocal node_count, max_depth, unmatched
            node_count += 1
            max_depth = max(max_depth, depth)
            layers[node.get("layer", "browser")] += 1
            if (node.get("correlation") or {}).get("method") == METHOD_UNMATCHED:
                unmatched += 1
            for k in node.get("children", []):
                walk(k, depth + 1)

        walk(root, 0)
        return {
            "node_count": node_count,
            "max_depth": max_depth,
            "total_duration_ms": round(float(root.get("duration_ms") or 0.0), 3),
            "layers": {k: int(v) for k, v in sorted(layers.items())},
            "unmatched_count": unmatched,
            "correlation_rate": round((node_count - unmatched) / node_count, 4) if node_count else 0.0,
        }

"""engine/correlation/engine.py — the Correlation Engine, primary join (T34).

This is the heart of the project (workplan §1): it proves that a browser-side record
and a Java-side record describe the *same* user action.

Pipeline (workplan §8.4):

  1. **normalise the clocks** — the browser clock and the server clock are never
     identical. Every collector reports its offset; the engine picks the browser side
     as the base and rewrites all timestamps onto it, and records what it did in
     ``clock`` so the tree can show it.
  2. **primary correlation** — same ``trace_id``, or a Java handler whose parent span
     is the browser request span → confidence **1.0**.
  3. **fallback** — :class:`FallbackMatcher`: method + path (query stripped, path
     variables collapsed) + ``|Δt| ≤ window_ms`` → confidence **≤ 0.8**.
  4. **never silent** — what is left over is classified with one of the six reasons,
     not quietly dropped (AGENTS.md §5.9).
"""
from __future__ import annotations

from collections import Counter
from typing import Callable

from .models import (
    DEFAULT_WINDOW_MS,
    METHOD_INFERRED,
    METHOD_TRACE_ID,
    METHOD_UNMATCHED,
    METHODS,
    NS_PER_MS,
    REASON_CORS_BLOCKED,
    REASON_NO_CANDIDATE,
    REASON_NO_TRACE_ID,
    REASONS,
    SKEW_FACTOR,
    STRATEGY_AUTO,
    STRATEGY_NONE,
    STRATEGY_TRACE_ID,
    STRATEGY_URL_WINDOW,
    STRATEGIES,
    CorrelationInput,
    CorrelationResult,
    Match,
    collector_of,
    preflight_blocked,
    set_correlation,
    usable_trace_id,
)
from .fallback import FallbackMatcher, http_url_of

# Layers that can never be the server-side entry point of a request.
_NON_HANDLER_LAYERS = {"http", "external", "db"}


def join_units(browser: list[dict]) -> list[dict]:
    """The browser-side spans correlation tries to join (one per outgoing request).

    Normally these are the ``layer=http`` / ``event_type=http_request`` spans captured
    by the initiator patch. If a run captured no HTTP layer at all (browser-only
    recording) the user-layer roots are used so a ``trace_id`` join is still attempted.
    """
    units = [
        s for s in browser
        if s.get("layer") == "http" and s.get("event_type") in ("http_request", "http_response")
    ]
    if units:
        # keep request spans; a response span for the same request adds no join
        reqs = [s for s in units if s.get("event_type") == "http_request"]
        return reqs or units
    roots = [s for s in browser if s.get("layer") == "user"]
    return roots or [s for s in browser if not s.get("parent_span_id")]


def handler_spans(java: list[dict]) -> list[dict]:
    """Server-side entry spans: a span whose parent is not another Java span.

    These are the candidates a browser request can be joined to. Pure client calls
    (``layer=http`` from an OTel CLIENT span) and db spans are excluded — the server
    entry point is what the browser request actually triggered.
    """
    ids = {s.get("span_id") for s in java}
    return [
        s for s in java
        if s.get("layer") not in _NON_HANDLER_LAYERS
        and (not s.get("parent_span_id") or s["parent_span_id"] not in ids)
    ]


class CorrelationEngine:
    """Join the browser capture stream to the Java capture stream."""

    def __init__(
        self,
        window_ms: int = DEFAULT_WINDOW_MS,
        skew_limit_ms: int | None = None,
        base_collector: str | None = None,
    ):
        self.window_ms = int(window_ms or DEFAULT_WINDOW_MS)
        self.skew_limit_ms = int(skew_limit_ms if skew_limit_ms is not None else self.window_ms * SKEW_FACTOR)
        self.base_collector = base_collector
        # populated per run so callers / logs can report what happened
        self.warnings: list[str] = []

    # ── clock normalisation (step 1) ──────────────────────────────────────────────
    def _clock(self, inp: CorrelationInput) -> tuple[dict, dict[str, float]]:
        """Return ``(clock, correction_by_collector)``.

        ``clock`` is the record written into the execution tree
        (``{"base": ..., "offset_ms": {collector: offset}}``); ``correction`` is what
        must be *subtracted* from that collector's timestamps to reach the base clock.
        """
        spans = list(inp.browser) + list(inp.java)
        groups: dict[str, list[dict]] = {}
        for s in spans:
            groups.setdefault(collector_of(s), []).append(s)

        base = self.base_collector
        if base is None:
            counts: Counter = Counter(collector_of(s) for s in inp.browser)
            base = counts.most_common(1)[0][0] if counts else "browser"

        def median_offset(collector: str) -> float:
            vals = sorted(float(s.get("clock_offset_ms") or 0.0) for s in groups.get(collector, []))
            if not vals:
                return 0.0
            mid = len(vals) // 2
            if len(vals) % 2:
                return vals[mid]
            return (vals[mid - 1] + vals[mid]) / 2.0

        offsets = {c: median_offset(c) for c in groups}
        offsets.setdefault(base, 0.0)
        if inp.clock_offset_ms:
            # explicit override for the non-base (Java) side
            for c in groups:
                if c != base:
                    offsets[c] = float(inp.clock_offset_ms)

        correction = {c: offsets[c] - offsets[base] for c in offsets}
        clock = {
            "base": base,
            "offset_ms": {c: round(offsets[base] - offsets[c], 3) for c in sorted(offsets)},
        }
        return clock, correction

    def _time_of(self, correction: dict[str, float]) -> Callable[[dict], int]:
        def t(span: dict) -> int:
            c = correction.get(collector_of(span), 0.0)
            return int(span.get("start_time_unix_ns") or 0) - int(round(c * NS_PER_MS))
        return t

    # ── primary correlation (step 2) ──────────────────────────────────────────────
    def _pick_handler(
        self, candidates: list[dict], unit: dict, java_ids: set[str], time_of: Callable[[dict], int]
    ) -> dict:
        """Choose the Java span that represents the request's server entry point."""
        same_parent = [c for c in candidates if c.get("parent_span_id") == unit.get("span_id")]
        if same_parent:
            return min(same_parent, key=time_of)
        entries = [c for c in candidates if not c.get("parent_span_id") or c["parent_span_id"] not in java_ids]
        if entries:
            return min(entries, key=time_of)
        return min(candidates, key=time_of)

    # ── main entry point ──────────────────────────────────────────────────────────
    def correlate(self, inp: CorrelationInput) -> CorrelationResult:
        """Correlate a browser capture with a Java capture.

        Returns a :class:`CorrelationResult` whose ``browser`` / ``java`` lists are
        annotated with the outcome, plus the matches, the classified leftovers and the
        clock record. Never raises on unmatched data — it reports it.
        """
        self.warnings = []
        strategy = (inp.strategy or STRATEGY_AUTO).lower()
        if strategy not in STRATEGIES:
            self.warnings.append(f"unknown strategy '{inp.strategy}'; falling back to '{STRATEGY_AUTO}'")
            strategy = STRATEGY_AUTO

        # Window: an explicit value on the input wins; otherwise the engine's own setting
        # (which callers such as the routes set from the request) applies.
        window = inp.window_ms if (inp.window_ms and inp.window_ms != DEFAULT_WINDOW_MS) else self.window_ms
        skew_limit = self.skew_limit_ms if window == self.window_ms else int(window * SKEW_FACTOR)

        browser = [dict(s) for s in inp.browser]
        java = [dict(s) for s in inp.java]
        clock, correction = self._clock(inp)
        time_of = self._time_of(correction)

        java_ids = {s.get("span_id") for s in java}
        java_by_trace: dict[str, list[dict]] = {}
        for s in java:
            java_by_trace.setdefault(s.get("trace_id") or "", []).append(s)
        handlers = handler_spans(java)
        handler_ids = {s.get("span_id") for s in handlers}

        units = join_units(browser)
        units_by_id = {s.get("span_id"): s for s in units}

        do_primary = strategy in (STRATEGY_AUTO, STRATEGY_TRACE_ID)
        do_fallback = strategy in (STRATEGY_AUTO, STRATEGY_URL_WINDOW)

        matches: list[Match] = []
        unmatched: list[dict] = []
        overrides: dict[str, str] = {}

        for unit in units:
            # A refused preflight means the request never reached the server at all.
            if preflight_blocked(unit):
                unmatched.append(self._unmatched_entry(unit, REASON_CORS_BLOCKED, None))
                continue

            tid = usable_trace_id(unit)
            match: Match | None = None
            fallback_reason: str | None = None
            nearest: float | None = None

            if do_primary and tid and tid in java_by_trace:
                handler = self._pick_handler(java_by_trace[tid], unit, java_ids, time_of)
                delta = (time_of(handler) - time_of(unit)) / NS_PER_MS
                match = Match(
                    browser_span_id=unit.get("span_id") or "",
                    java_span_id=handler.get("span_id") or "",
                    method=METHOD_TRACE_ID,
                    score=1.0,
                    reason=None,
                    delta_ms=round(delta, 3),
                )

            if match is None and do_fallback:
                matcher = FallbackMatcher(window, skew_limit)
                match, fallback_reason, nearest = matcher.match_one(unit, handlers, time_of)

            if match is not None:
                matches.append(match)
                overrides[match.java_span_id] = match.browser_span_id
                continue

            if match is None and not do_fallback and strategy == STRATEGY_NONE:
                unmatched.append(self._unmatched_entry(unit, REASON_NO_CANDIDATE, None))
                continue

            reason = fallback_reason or REASON_NO_CANDIDATE
            if not tid and reason == REASON_NO_CANDIDATE:
                reason = REASON_NO_TRACE_ID
            unmatched.append(self._unmatched_entry(unit, reason, nearest))

        # ── annotate every span with the outcome ──────────────────────────────────
        match_by_browser = {m.browser_span_id: m for m in matches}
        for span in browser:
            if span.get("span_id") not in units_by_id:
                continue  # non-request spans keep the collector's own verdict
            m = match_by_browser.get(span.get("span_id"))
            if m is not None:
                set_correlation(span, m.method, m.score, m.reason)
            else:
                entry = next((u for u in unmatched if u.get("span_id") == span.get("span_id")), {})
                set_correlation(span, METHOD_UNMATCHED, 0.0, entry.get("reason"))

        trace_match: dict[str, Match] = {}
        for m in matches:
            js = next((s for s in java if s.get("span_id") == m.java_span_id), None)
            if js is not None:
                trace_match.setdefault(js.get("trace_id") or "", m)
        for span in java:
            m = trace_match.get(span.get("trace_id") or "")
            if m is not None:
                if span.get("span_id") == m.java_span_id:
                    set_correlation(span, m.method, m.score, m.reason)
                else:
                    # same server trace as a matched handler: joined by inheritance
                    set_correlation(span, METHOD_INFERRED, m.score, None)
            else:
                is_entry = span.get("span_id") in handler_ids
                set_correlation(span, METHOD_UNMATCHED, 0.0, REASON_NO_CANDIDATE if is_entry else None)

        # ── stats ────────────────────────────────────────────────────────────────
        by_method: Counter = Counter()
        by_reason: Counter = Counter()
        for m in matches:
            by_method[m.method] += 1
            if m.reason:
                by_reason[m.reason] += 1
        for u in unmatched:
            by_method[METHOD_UNMATCHED] += 1
            if u.get("reason"):
                by_reason[u["reason"]] += 1

        total = len(units)
        matched_count = len(matches)
        stats = {
            "browser_spans": len(browser),
            "java_spans": len(java),
            "requests_total": total,
            "matched": matched_count,
            "unmatched": len(unmatched),
            "rate": round(matched_count / total, 4) if total else 0.0,
            "by_method": {m: int(by_method.get(m, 0)) for m in METHODS},
            "by_reason": {r: int(by_reason.get(r, 0)) for r in REASONS if by_reason.get(r)},
        }

        if not java:
            self.warnings.append(
                "no Java spans for this run: nothing to correlate; every request is "
                "reported unmatched rather than silently dropped"
            )
        if total == 0:
            self.warnings.append("no browser request spans found; correlation rate is 0.0 by definition")

        return CorrelationResult(
            browser=browser,
            java=java,
            matches=matches,
            unmatched=unmatched,
            clock=clock,
            stats=stats,
            parent_overrides=overrides,
            run_id=inp.run_id,
            window_ms=window,
            strategy=strategy,
            warnings=list(self.warnings),
        )

    # ── helpers ──────────────────────────────────────────────────────────────────
    @staticmethod
    def _unmatched_entry(unit: dict, reason: str, nearest: float | None) -> dict:
        return {
            "span_id": unit.get("span_id"),
            "name": unit.get("name"),
            "url": http_url_of(unit),
            "reason": reason,
            "nearest_delta_ms": nearest,
        }

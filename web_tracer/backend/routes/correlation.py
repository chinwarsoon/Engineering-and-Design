"""backend/routes/correlation.py — Phase 4 endpoints (workplan §8.5 rows 18-20, T38).

  POST /correlate                    → {rate, matched, unmatched[]}   (row 18)
  GET  /correlation/report/{run_id}  → correlation_report.json        (row 19)
  GET  /execution_tree/{run_id}      → ExecutionTree                  (row 20)

Every path string comes from ``engine.config`` (§8.5 hard contract rule). Spans are read
from ``<base>/output/runs/<run_id>/`` — the same files the Phase 2 recorder and the
Phase 3 OTLP receiver write — so a run can be correlated after the fact, without keeping
the browser or the JVM alive.

Because the browser recorder and the Java receiver issue their **own** run ids, the
correlation endpoints accept optional ``browser_run_id`` / ``java_run_id`` overrides.
When they are omitted, both traces are looked up under ``run_id``.
"""
from __future__ import annotations

import json
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from engine import config, paths
from engine.correlation import (
    DEFAULT_WINDOW_MS,
    CorrelationEngine,
    CorrelationInput,
    CorrelationMetrics,
    ExecutionTreeBuilder,
)

router = APIRouter()

BROWSER_TRACE_FILE = "browser_trace.json"
JAVA_TRACE_FILE = "java_trace.json"


class CorrelateReq(BaseModel):
    run_id: str
    window_ms: int = DEFAULT_WINDOW_MS
    strategy: str = "auto"
    clock_offset_ms: float = 0.0
    browser_run_id: Optional[str] = None
    java_run_id: Optional[str] = None


# ── span loading ─────────────────────────────────────────────────────────────────
def _read_trace(run_id: str, filename: str) -> list[dict]:
    p = paths.runs_root() / run_id / filename
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return []
    return [s for s in data if isinstance(s, dict)] if isinstance(data, list) else []


def _session_spans(run_id: str) -> tuple[list[dict], list[dict]]:
    """Spans still held in memory by the browser / Java routes (before they are flushed)."""
    browser: list[dict] = []
    java: list[dict] = []
    try:
        from backend.routes import browser as browser_routes
        from backend.routes import java as java_routes
    except Exception:  # pragma: no cover - routes always importable in the service
        return browser, java
    sess = browser_routes._SESSIONS.get(run_id)
    if sess and sess.get("spans"):
        browser = list(sess["spans"])
    jsess = java_routes._SESSIONS.get(run_id)
    if jsess and jsess.get("spans"):
        java = list(jsess["spans"])
    return browser, java


def load_run(
    run_id: str, browser_run_id: Optional[str] = None, java_run_id: Optional[str] = None
) -> tuple[list[dict], list[dict]]:
    """Return ``(browser_spans, java_spans)`` for a run, from disk or live sessions."""
    browser = _read_trace(browser_run_id or run_id, BROWSER_TRACE_FILE)
    java = _read_trace(java_run_id or run_id, JAVA_TRACE_FILE)
    # fall back to spans still held by a live browser / receiver session
    if not browser:
        browser, s_java = _session_spans(browser_run_id or run_id)
        java = java or s_java
    if not java:
        s_browser, s_java = _session_spans(java_run_id or run_id)
        java = s_java
        browser = browser or s_browser
    return browser, java


def _correlate(
    run_id: str,
    window_ms: int,
    strategy: str,
    clock_offset_ms: float,
    browser_run_id: Optional[str],
    java_run_id: Optional[str],
):
    browser, java = load_run(run_id, browser_run_id, java_run_id)
    if not browser and not java:
        raise HTTPException(status_code=404, detail=f"no browser or java trace found for run_id '{run_id}'")
    engine = CorrelationEngine(window_ms=window_ms)
    return engine.correlate(
        CorrelationInput(
            browser=browser,
            java=java,
            window_ms=window_ms,
            clock_offset_ms=clock_offset_ms,
            strategy=strategy,
            run_id=run_id,
        )
    )


# ── row 18: POST /correlate ──────────────────────────────────────────────────────
@router.post(config.CORRELATE)
def correlate(req: CorrelateReq):
    """Correlate a run and persist ``correlation_report.json`` + ``execution_tree.json``."""
    res = _correlate(
        req.run_id, req.window_ms, req.strategy, req.clock_offset_ms,
        req.browser_run_id, req.java_run_id,
    )
    metrics = CorrelationMetrics()
    report = metrics.report(res)
    out = paths.run_dir(req.run_id)
    metrics.save(res, out)

    builder = ExecutionTreeBuilder()
    tree = builder.build(res.spans(), result=res, run_id=req.run_id)
    builder.save(tree, out)

    payload = res.to_dict()
    # engine diagnostics (e.g. "no Java spans") travel with the response, never silent (§5.9)
    payload["warnings"] = list(res.warnings)
    payload["report_path"] = str(out / "correlation_report.json")
    payload["tree_path"] = str(out / "execution_tree.json")
    return payload


# ── row 19: GET /correlation/report/{run_id} ─────────────────────────────────────
@router.get(config.CORRELATION_REPORT + "/{run_id}")
def correlation_report(
    run_id: str,
    window_ms: int = DEFAULT_WINDOW_MS,
    strategy: str = "auto",
    clock_offset_ms: float = 0.0,
    browser_run_id: Optional[str] = None,
    java_run_id: Optional[str] = None,
):
    """Return (and persist) ``correlation_report.json`` for a run."""
    res = _correlate(run_id, window_ms, strategy, clock_offset_ms, browser_run_id, java_run_id)
    metrics = CorrelationMetrics()
    metrics.save(res, paths.run_dir(run_id))
    return metrics.report(res)


# ── row 20: GET /execution_tree/{run_id} ─────────────────────────────────────────
@router.get(config.EXECUTION_TREE + "/{run_id}")
def execution_tree(
    run_id: str,
    trace_id: Optional[str] = None,
    window_ms: int = DEFAULT_WINDOW_MS,
    strategy: str = "auto",
    clock_offset_ms: float = 0.0,
    browser_run_id: Optional[str] = None,
    java_run_id: Optional[str] = None,
):
    """Return the execution tree for a run (optionally narrowed to one ``trace_id``)."""
    res = _correlate(run_id, window_ms, strategy, clock_offset_ms, browser_run_id, java_run_id)
    spans = res.spans()
    if trace_id and not any(s.get("trace_id") == trace_id for s in spans):
        raise HTTPException(status_code=404, detail=f"no span with trace_id '{trace_id}' in run '{run_id}'")

    builder = ExecutionTreeBuilder()
    tree = builder.build(spans, result=res, trace_id=trace_id, run_id=run_id)
    if trace_id is None:  # the run-level artefact stays canonical
        builder.save(tree, paths.run_dir(run_id))
    return tree

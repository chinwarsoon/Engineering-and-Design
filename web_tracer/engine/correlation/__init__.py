"""engine/correlation — the Correlation Engine and the Execution Tree (Phase 4, T34-T38).

Public API:

* :class:`CorrelationEngine` — primary ``trace_id`` join + fallback (T34/T35)
* :class:`FallbackMatcher`  — URL + time-window matching (T35)
* :class:`CorrelationMetrics` — correlation report with reason breakdown (T36)
* :class:`ExecutionTreeBuilder` — ``execution_tree.json`` (T37)
* :func:`correlate_run` — convenience wrapper used by the routes (T38)
"""
from __future__ import annotations

from .models import (
    DEFAULT_WINDOW_MS,
    METHODS,
    REASONS,
    STRATEGIES,
    CorrelationInput,
    CorrelationResult,
    Match,
)
from .engine import CorrelationEngine, handler_spans, join_units
from .fallback import FallbackMatcher, endpoint_key, normalize_url, path_key
from .metrics import REPORT_FILENAME, CorrelationMetrics
from .execution_tree import TREE_FILENAME, ExecutionTreeBuilder

__all__ = [
    "DEFAULT_WINDOW_MS",
    "METHODS",
    "REASONS",
    "STRATEGIES",
    "CorrelationInput",
    "CorrelationResult",
    "Match",
    "CorrelationEngine",
    "handler_spans",
    "join_units",
    "FallbackMatcher",
    "endpoint_key",
    "normalize_url",
    "path_key",
    "CorrelationMetrics",
    "REPORT_FILENAME",
    "ExecutionTreeBuilder",
    "TREE_FILENAME",
    "correlate_run",
]


def correlate_run(
    browser: list[dict],
    java: list[dict],
    *,
    window_ms: int = DEFAULT_WINDOW_MS,
    clock_offset_ms: float = 0.0,
    strategy: str = "auto",
    run_id: str | None = None,
) -> CorrelationResult:
    """Correlate one run in a single call (used by ``backend/routes/correlation.py``)."""
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

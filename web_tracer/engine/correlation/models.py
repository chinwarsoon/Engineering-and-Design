"""engine/correlation/models.py — shared data model for the Correlation Engine (T34-T36, §8.4).

Kept in its own module so ``engine.py`` (which owns the matcher) and ``fallback.py``
(which produces the match records) can both import the dataclasses without a
circular import.

The vocabularies below are the single source of truth for correlation results:
adapters, the correlation engine, the metrics report, the execution tree and the
dashboard all read these constants (AGENTS.md §5.13 cross-source alignment).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# ── Correlation methods (workplan §8.3.1 ``SpanEvent.correlation.method``) ────────
METHOD_TRACE_ID = "trace_id"                  # exact W3C trace_id join → confidence 1.0
METHOD_URL_TIME_WINDOW = "url_time_window"    # fallback join → confidence ≤ 0.8
METHOD_INFERRED = "inferred"                  # inherited from a matched parent span
METHOD_UNMATCHED = "unmatched"                # no join found
METHODS = (METHOD_TRACE_ID, METHOD_URL_TIME_WINDOW, METHOD_INFERRED, METHOD_UNMATCHED)

# ── Unmatched / degraded reasons (workplan §8.4; T36 requires all six reproducible) ─
REASON_NO_CANDIDATE = "no_candidate"                  # no server span with a matching URL
REASON_MULTIPLE_CANDIDATES = "multiple_candidates"    # ambiguous; nearest taken, score lowered
REASON_CORS_BLOCKED = "cors_preflight_blocked"        # preflight refused → no server span exists
REASON_CLOCK_SKEW = "clock_skew_exceeded"             # best candidate far outside the window (R3)
REASON_NO_TRACE_ID = "no_trace_id"                    # browser span carried no usable trace_id
REASON_OUT_OF_WINDOW = "out_of_window"                # URL matched but |Δt| > window_ms
REASONS = (
    REASON_NO_CANDIDATE,
    REASON_MULTIPLE_CANDIDATES,
    REASON_CORS_BLOCKED,
    REASON_CLOCK_SKEW,
    REASON_NO_TRACE_ID,
    REASON_OUT_OF_WINDOW,
)

# ── Tunables ──────────────────────────────────────────────────────────────────────
DEFAULT_WINDOW_MS = 200          # ±200 ms fallback window (workplan §8.1 / R3)
SKEW_FACTOR = 5                  # |Δt| > window * SKEW_FACTOR ⇒ clock skew, not slowness
SCORE_UNIQUE = 0.8               # method + path, one candidate
SCORE_AMBIGUOUS = 0.6            # method + path, several candidates → nearest
SCORE_PATH_ONLY = 0.4            # path only (method unknown or different)
SYNTHETIC_ROOT_CONFIDENCE = 0.3  # synthetic root inserted for orphan spans (§8.4 step 4)

# /correlate strategies: "auto" = primary then fallback; the others pin one path so a
# run can be replayed deterministically (useful for demos and regression tests).
STRATEGY_AUTO = "auto"
STRATEGY_TRACE_ID = "trace_id"
STRATEGY_URL_WINDOW = "url_time_window"
STRATEGY_NONE = "none"
STRATEGIES = (STRATEGY_AUTO, STRATEGY_TRACE_ID, STRATEGY_URL_WINDOW, STRATEGY_NONE)

NS_PER_MS = 1_000_000


@dataclass
class Match:
    """One browser request span joined to one Java handler span."""

    browser_span_id: str
    java_span_id: str
    method: str
    score: float
    reason: str | None = None
    delta_ms: float | None = None  # signed: java_start − browser_start

    def to_dict(self) -> dict:
        return {
            "browser_span_id": self.browser_span_id,
            "java_span_id": self.java_span_id,
            "method": self.method,
            "score": round(float(self.score), 3),
            "reason": self.reason,
            "delta_ms": None if self.delta_ms is None else round(float(self.delta_ms), 3),
        }


@dataclass
class CorrelationInput:
    """Everything the engine needs (workplan §8.4 ``CorrelationInput``).

    ``clock_offset_ms`` is an explicit override for the offset of the *non-base*
    (Java) collector; 0.0 means "trust the per-span ``clock_offset_ms`` values".
    """

    browser: list[dict] = field(default_factory=list)
    java: list[dict] = field(default_factory=list)
    window_ms: int = DEFAULT_WINDOW_MS
    clock_offset_ms: float = 0.0
    strategy: str = STRATEGY_AUTO
    run_id: str | None = None


@dataclass
class CorrelationResult:
    """Outcome of :meth:`CorrelationEngine.correlate`.

    ``parent_overrides`` records the stitches the engine made (java handler → browser
    request span) so :class:`ExecutionTreeBuilder` can nest the two streams even when
    the ``traceparent`` header never made it to the server (fallback correlation).
    """

    browser: list[dict]
    java: list[dict]
    matches: list[Match]
    unmatched: list[dict]
    clock: dict
    stats: dict
    parent_overrides: dict[str, str] = field(default_factory=dict)
    run_id: str | None = None
    window_ms: int = DEFAULT_WINDOW_MS
    strategy: str = STRATEGY_AUTO
    # Engine diagnostics (empty java stream, unknown strategy, …). Reported, never silent.
    warnings: list[str] = field(default_factory=list)

    @property
    def rate(self) -> float:
        """Share of browser request spans that could be joined (the T34 gate metric)."""
        return float(self.stats.get("rate", 0.0))

    @property
    def matched(self) -> int:
        return int(self.stats.get("matched", len(self.matches)))

    def to_dict(self) -> dict:
        """The ``POST /correlate`` payload (workplan §8.5 row 18)."""
        return {
            "run_id": self.run_id,
            "rate": round(self.rate, 4),
            "matched": self.matched,
            "total": int(self.stats.get("requests_total", 0)),
            "unmatched": list(self.unmatched),
        }

    def spans(self) -> list[dict]:
        """All annotated spans, browser first then Java (input order preserved)."""
        return list(self.browser) + list(self.java)


def usable_trace_id(span: dict) -> str | None:
    """Return the span's ``trace_id`` if it is a usable 32-hex, non-zero id.

    A browser span whose ``traceparent`` was stripped (CORS) or that was captured
    before injection carries no usable id — that is the ``no_trace_id`` case, and it
    must be reported instead of silently skipped (AGENTS.md §5.9).
    """
    t = span.get("trace_id")
    if not isinstance(t, str):
        return None
    t = t.strip().lower()
    if len(t) != 32 or any(c not in "0123456789abcdef" for c in t):
        return None
    if set(t) == {"0"}:
        return None
    return t


def collector_of(span: dict) -> str:
    """Collector name of a span (``SpanEvent.collector.name``), used for clock grouping."""
    c = span.get("collector")
    if isinstance(c, dict):
        return str(c.get("name") or "unknown")
    return "unknown"


def correlation_of(span: dict) -> dict:
    """Read a span's ``correlation`` block, tolerating a missing one."""
    c = span.get("correlation")
    return dict(c) if isinstance(c, dict) else {}


def set_correlation(span: dict, method: str, score: float, reason: str | None = None) -> None:
    """Write the correlation block in place (schema shape ``{method, score, reason}``)."""
    span["correlation"] = {
        "method": method,
        "score": round(float(score), 3),
        "reason": reason,
    }


def preflight_blocked(span: dict) -> bool:
    """True when a CORS preflight was observed and refused ``traceparent``.

    In that case no server span can exist for this request, so the engine reports
    ``cors_preflight_blocked`` rather than hunting for a candidate (workplan §8.4).
    """
    attrs = span.get("attributes")
    if not isinstance(attrs, dict):
        return False
    pf = attrs.get("preflight")
    if isinstance(pf, dict) and pf.get("observed") and not pf.get("allowed"):
        return True
    return False


def as_dict_list(value: Any) -> list[dict]:
    return [v for v in (value or []) if isinstance(v, dict)]

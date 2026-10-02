r"""engine/correlation/metrics.py — correlation metrics + reason classification (T36).

Turns a :class:`CorrelationResult` into ``correlation_report.json``. The report is the
artefact an engineer actually reads when the correlation rate drops: it says *how many*
requests were joined, *by which method*, and — for the rest — *why not*.

Six reasons are classified (workplan §8.4) and every one of them is reproducible:

| reason | meaning |
|---|---|
| ``no_candidate`` | no server span with a matching URL at all |
| ``multiple_candidates`` | ambiguous; the nearest candidate won, score lowered to 0.6 |
| ``cors_preflight_blocked`` | the preflight refused ``traceparent``, so no server span can exist |
| ``clock_skew_exceeded`` | the best candidate is far outside the window (R3) |
| ``no_trace_id`` | the browser span carried no usable ``trace_id``, so the primary join was impossible |
| ``out_of_window`` | URL matched but ``\|Δt\| > window_ms`` |
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import (
    METHODS,
    REASONS,
    CorrelationResult,
)

REPORT_FILENAME = "correlation_report.json"


class CorrelationMetrics:
    """Build the correlation report from a :class:`CorrelationResult`."""

    def report(self, res: CorrelationResult) -> dict:
        """Return the ``correlation_report.json`` payload.

        Fields: ``run_id``, ``generated_at``, ``window_ms``, ``strategy``, ``clock``,
        ``counts``, ``total``, ``matched``, ``rate``, ``by_method``,
        ``unmatched_reasons`` (alias ``by_reason``), ``unmatched[]``,
        ``matched_pairs[]`` and ``warnings[]``.
        """
        stats = dict(res.stats or {})
        total = int(stats.get("requests_total", 0))
        matched = int(stats.get("matched", len(res.matches)))
        rate = float(stats.get("rate", 0.0))

        report: dict[str, Any] = {
            "run_id": res.run_id,
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "window_ms": res.window_ms,
            "strategy": res.strategy,
            "clock": res.clock,
            "counts": {
                "browser_spans": int(stats.get("browser_spans", len(res.browser))),
                "java_spans": int(stats.get("java_spans", len(res.java))),
                "requests_total": total,
                "requests_matched": matched,
                "requests_unmatched": int(stats.get("unmatched", len(res.unmatched))),
            },
            "total": total,
            "matched": matched,
            "rate": round(rate, 4),
            # every method is present even when zero, so the report shape is stable
            "by_method": {m: int((stats.get("by_method") or {}).get(m, 0)) for m in METHODS},
            "unmatched_reasons": {r: int((stats.get("by_reason") or {}).get(r, 0)) for r in REASONS},
            "by_reason": {r: int((stats.get("by_reason") or {}).get(r, 0)) for r in REASONS if (stats.get("by_reason") or {}).get(r)},
            "unmatched": list(res.unmatched),
            "matched_pairs": [m.to_dict() for m in res.matches],
            "warnings": list(getattr(res, "warnings", []) or []),
        }

        if not res.java:
            report["note"] = (
                "no Java spans were supplied for this run: nothing was correlated. "
                "Import a java_trace.json (POST /java/import) or run the OTLP receiver "
                "before correlating."
            )
        return report

    def save(self, res: CorrelationResult, out_dir: Path) -> Path:
        """Write ``correlation_report.json`` into ``out_dir`` and return its path."""
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        p = out_dir / REPORT_FILENAME
        p.write_text(json.dumps(self.report(res), indent=2), encoding="utf-8")
        return p

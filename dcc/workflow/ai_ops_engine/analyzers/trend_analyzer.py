"""
AI Ops Engine — Trend Analyzer

Detects recurring issue patterns from phase breakdown and error distribution.
Breadcrumb: AiContext.phase_breakdown + top_error_codes → TrendItem list
"""

from __future__ import annotations
import logging
from typing import List

from ..core.contracts import AiContext, TrendItem

logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """
    Detects recurring patterns and concentration trends in pipeline errors.
    """

    def analyze(self, ctx: AiContext) -> List[TrendItem]:
        """
        Analyze AiContext for recurring patterns.

        Args:
            ctx: Populated AiContext

        Returns:
            List of TrendItem describing detected patterns
        """
        trends = []

        # Phase concentration trend
        for phase in ctx.phase_breakdown:
            total = phase.get("Total", 0)
            phase_name = phase.get("Phase", "?")
            high = phase.get("High", 0)
            if total > 100:
                trends.append(TrendItem(
                    pattern=f"High error concentration in Phase {phase_name} ({total:,} errors, {high:,} HIGH)",
                    frequency=total,
                    error_code="",
                    phases=[phase_name],
                ))

        # Column concentration trend
        if ctx.top_columns:
            top = ctx.top_columns[0]
            col = top.get("column", "")
            count = top.get("error_count", 0)
            if count > 100:
                trends.append(TrendItem(
                    pattern=f"Column '{col}' is the primary error hotspot with {count:,} errors",
                    frequency=count,
                    error_code="",
                    phases=[],
                ))

        # Fill error pattern
        fill_codes = [e for e in ctx.top_error_codes if "F4" in e.get("code", "")]
        fill_total = sum(e.get("count", 0) for e in fill_codes)
        if fill_total > 50:
            trends.append(TrendItem(
                pattern=f"Systematic null-fill pattern — {fill_total:,} fill events across {len(fill_codes)} fill error types",
                frequency=fill_total,
                error_code="F4-C-F-0403",
                phases=["P2.5"],
            ))

        # Document_ID format pattern
        doc_id_errors = next(
            (e for e in ctx.top_error_codes if e.get("code") == "P2-I-V-0204"), None
        )
        if doc_id_errors and doc_id_errors.get("count", 0) > 50:
            trends.append(TrendItem(
                pattern=f"Non-standard Document_ID formats recurring across {doc_id_errors['count']:,} rows — likely reply sheets and supporting docs",
                frequency=doc_id_errors["count"],
                error_code="P2-I-V-0204",
                phases=["P2", "P4"],
            ))

        logger.info(f"[trend_analyzer] Detected {len(trends)} trends")
        return trends

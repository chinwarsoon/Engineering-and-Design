"""
AI Ops Engine — Base Provider Interface

Defines the abstract provider contract and a rule-based fallback
that generates insights from error statistics without an LLM.
Breadcrumb: implemented by ollama_provider.py; used by engine.py.
"""

from __future__ import annotations
import logging
from abc import ABC, abstractmethod
from typing import Optional

from ..core.contracts import AiContext, AiInsight, RiskItem, TrendItem

logger = logging.getLogger(__name__)


class BaseProvider(ABC):
    """Abstract interface for AI insight providers."""

    @abstractmethod
    def generate(self, ctx: AiContext) -> AiInsight:
        """
        Generate structured AI insight from context.

        Args:
            ctx: Populated AiContext

        Returns:
            AiInsight with risk analysis and recommendations
        """


class RuleBasedProvider(BaseProvider):
    """
    Fallback provider that generates insights from error statistics.

    Used when Ollama is unavailable. Produces deterministic, rule-based
    summaries without LLM inference.
    Breadcrumb: ctx.error_summary → risk thresholds → AiInsight
    """

    # Risk level thresholds based on health score
    _RISK_THRESHOLDS = [
        (95, "LOW"),
        (85, "MEDIUM"),
        (70, "HIGH"),
        (0,  "CRITICAL"),
    ]

    def generate(self, ctx: AiContext) -> AiInsight:
        """
        Generate rule-based insight from error statistics.

        Args:
            ctx: Populated AiContext

        Returns:
            AiInsight with fallback_used=True
        """
        risk_level = self._score_to_risk(ctx.health_score)
        top_risks = self._build_risks(ctx)
        trends = self._build_trends(ctx)
        recommendations = self._build_recommendations(ctx, risk_level)

        summary = (
            f"Pipeline processed {ctx.total_rows:,} rows with a data health score of "
            f"{ctx.health_score:.1f}% (Grade {ctx.health_grade}). "
            f"Overall risk is assessed as {risk_level} based on "
            f"{ctx.error_summary.get('total_errors', 0):,} detected errors across "
            f"{ctx.error_summary.get('affected_rows', 0):,} affected rows."
        )

        insight = AiInsight(
            run_id=ctx.run_id,
            risk_level=risk_level,
            executive_summary=summary,
            top_risks=top_risks,
            trends=trends,
            recommendations=recommendations,
            model_used="rule_based",
            provider="rule_based",
            fallback_used=True,
        )
        logger.info(f"[rule_based] Generated fallback insight: risk={risk_level}")
        return insight

    def _score_to_risk(self, score: float) -> str:
        """Map health score to risk level."""
        for threshold, level in self._RISK_THRESHOLDS:
            if score >= threshold:
                return level
        return "CRITICAL"

    def _build_risks(self, ctx: AiContext) -> list:
        """Build risk items from top error codes."""
        risks = []
        for et in ctx.top_error_codes[:5]:
            code = et.get("code", "")
            count = et.get("count", 0)
            severity = et.get("severity", "MEDIUM")
            # Find affected columns
            cols = [
                c["column"] for c in ctx.top_columns
                if c.get("error_count", 0) > 0
            ][:3]
            risks.append(RiskItem(
                title=f"Error code {code} — {count} occurrences",
                description=f"{count} rows affected by {code} errors (severity: {severity}).",
                severity=severity,
                affected_rows=count,
                error_codes=[code],
                columns=cols,
                recommendation=f"Review and resolve {code} errors in source data.",
            ))
        return risks

    def _build_trends(self, ctx: AiContext) -> list:
        """Build trend items from phase breakdown."""
        trends = []
        for phase in ctx.phase_breakdown:
            total = phase.get("Total", 0)
            if total > 50:
                trends.append(TrendItem(
                    pattern=f"High error concentration in Phase {phase.get('Phase','?')}",
                    frequency=total,
                    error_code="",
                    phases=[phase.get("Phase", "")],
                ))
        return trends

    def _build_recommendations(self, ctx: AiContext, risk_level: str) -> list:
        """Build actionable recommendations."""
        recs = []
        if ctx.top_columns:
            top_col = ctx.top_columns[0].get("column", "unknown")
            count = ctx.top_columns[0].get("error_count", 0)
            recs.append(f"Prioritise fixing errors in '{top_col}' column ({count} errors).")

        if ctx.health_score < 90:
            recs.append("Review source data quality — health score below 90% indicates systemic data entry issues.")
        if risk_level in ("HIGH", "CRITICAL"):
            recs.append("Escalate to data owner for immediate review of HIGH severity errors.")
        recs.append("Re-run pipeline after source data corrections to verify improvement.")
        return recs

"""
AI Ops Engine — Risk Analyzer

Computes risk clusters and severity bands from pipeline error data.
Provides deterministic risk scoring to complement LLM analysis.
Breadcrumb: AiContext.top_error_codes + phase_breakdown → RiskItem list
"""

from __future__ import annotations
import logging
from typing import List

from ..core.contracts import AiContext, RiskItem

logger = logging.getLogger(__name__)

# Severity weights for risk scoring
_SEVERITY_WEIGHTS = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "WARNING": 1, "INFO": 0}

# Error code descriptions for human-readable risk titles
_ERROR_DESCRIPTIONS = {
    "P2-I-V-0204": ("Document_ID Format Invalid", "Document_ID does not match the expected composite pattern."),
    "P1-A-P-0101": ("Anchor Column Null", "Critical anchor column contains null values."),
    "L3-L-P-0301": ("Date Inversion", "Review return date is before submission date."),
    "F4-C-F-0401": ("Forward Fill Jump", "Forward fill exceeded row jump limit."),
    "F4-C-F-0403": ("Default Fill Applied", "Multi-level fill failed; default value applied."),
    "GROUP_INCONSISTENT": ("Session Group Inconsistency", "Submission_Date varies within the same session group."),
    "VERSION_REGRESSION": ("Revision Regression", "Document revision decreased for a subsequent submission."),
    "RESUBMISSION_MISMATCH": ("Resubmission Flag Mismatch", "Rejected status without required resubmission flag."),
    "CLOSED_WITH_PLAN_DATE": ("Closed With Plan Date", "Submission closed but resubmission plan date is set."),
    "INCONSISTENT_SUBJECT": ("Inconsistent Session Subject", "Session subject varies within the same session group."),
}


class RiskAnalyzer:
    """
    Deterministic risk analyzer for pipeline error data.

    Classifies errors into risk clusters and computes an overall
    risk score independent of LLM analysis.
    """

    def analyze(self, ctx: AiContext) -> List[RiskItem]:
        """
        Analyze AiContext and return ranked RiskItem list.

        Args:
            ctx: Populated AiContext

        Returns:
            List of RiskItem sorted by severity weight descending
        """
        risks = []
        for et in ctx.top_error_codes:
            code = et.get("code", "")
            count = et.get("count", 0)
            severity = et.get("severity", "MEDIUM")
            if count == 0:
                continue

            title, description = _ERROR_DESCRIPTIONS.get(
                code, (f"Error {code}", f"{count} occurrences of {code}.")
            )

            # Find affected columns from top_columns
            affected_cols = [
                c["column"] for c in ctx.top_columns
                if c.get("error_count", 0) > 0
            ][:3]

            risks.append(RiskItem(
                title=title,
                description=f"{description} Affects {count:,} rows.",
                severity=severity,
                affected_rows=count,
                error_codes=[code],
                columns=affected_cols,
                recommendation=self._get_recommendation(code, count),
            ))

        # Sort by severity weight then count
        risks.sort(
            key=lambda r: (_SEVERITY_WEIGHTS.get(r.severity, 0), r.affected_rows),
            reverse=True,
        )
        logger.info(f"[risk_analyzer] Identified {len(risks)} risk items")
        return risks[:8]  # Top 8 risks

    def compute_overall_risk(self, ctx: AiContext) -> str:
        """
        Compute overall risk level from health score and error counts.

        Args:
            ctx: Populated AiContext

        Returns:
            Risk level string: CRITICAL / HIGH / MEDIUM / LOW
        """
        kpi = ctx.error_summary.get("health_kpi", {})
        critical = kpi.get("detailed_counts", {}).get("CRITICAL", 0)
        high = kpi.get("detailed_counts", {}).get("HIGH", 0)
        score = ctx.health_score

        if critical > 0 or score < 70:
            return "CRITICAL"
        if high > 500 or score < 85:
            return "HIGH"
        if high > 100 or score < 95:
            return "MEDIUM"
        return "LOW"

    def _get_recommendation(self, code: str, count: int) -> str:
        """Return a specific recommendation for an error code."""
        recs = {
            "P2-I-V-0204": "Review source Document_ID values — check for non-standard formats, reply sheets, and supporting docs.",
            "P1-A-P-0101": "Ensure all anchor columns (Document_ID, Project_Code, Document_Type, Submission_Date) are populated in source data.",
            "L3-L-P-0301": "Verify date entries — review return date cannot precede submission date.",
            "F4-C-F-0401": "Check for large gaps in session data; consider adjusting forward fill jump limit.",
            "F4-C-F-0403": "Source data has missing values that required default fill — review data completeness.",
            "GROUP_INCONSISTENT": "Verify submission dates are consistent within each session group in source data.",
            "VERSION_REGRESSION": "Review revision history — check for voided/withdrawn revisions that may cause false regressions.",
            "RESUBMISSION_MISMATCH": "Update Resubmission_Required flag for all rejected submissions in source data.",
        }
        return recs.get(code, f"Investigate and resolve {count:,} occurrences of {code} in source data.")

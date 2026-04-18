"""
AI Ops Engine — Evidence Linker

Maps AI findings back to row, column, phase, and error code evidence
from the deterministic pipeline outputs.
Breadcrumb: called by engine.py after provider returns AiInsight.
"""

from __future__ import annotations
import logging
from typing import Any, Dict, List

from .contracts import AiInsight

logger = logging.getLogger(__name__)

# Map error codes to their pipeline phase
_ERROR_PHASE_MAP: Dict[str, str] = {
    "P1-A-P-0101": "P1",
    "P2-I-V-0204": "P2",
    "P2-I-P-0201": "P2",
    "F4-C-F-0401": "P2.5",
    "F4-C-F-0403": "P2.5",
    "F4-C-F-0404": "P2.5",
    "L3-L-P-0301": "P3",
    "GROUP_INCONSISTENT": "P4",
    "VERSION_REGRESSION": "P4",
    "RESUBMISSION_MISMATCH": "P4",
    "CLOSED_WITH_PLAN_DATE": "P4",
    "INCONSISTENT_SUBJECT": "P4",
    "OVERDUE_MISMATCH": "P4",
}


def attach_evidence_links(
    insight: AiInsight,
    dashboard_data: Dict[str, Any],
) -> AiInsight:
    """
    Attach deterministic evidence links to each risk in the AiInsight.

    For each risk item, finds matching error codes in the dashboard data
    and attaches row counts, column names, and phase information.

    Args:
        insight: AiInsight from provider (may have empty evidence_links)
        dashboard_data: Loaded error_dashboard_data.json dict

    Returns:
        AiInsight with evidence_links populated
    """
    error_types = {e.get("code"): e for e in dashboard_data.get("error_types", [])}
    column_health = {c.get("column"): c.get("error_count", 0) for c in dashboard_data.get("column_health", [])}
    recent_errors = dashboard_data.get("recent_errors", [])

    evidence_links = []

    for risk in insight.top_risks:
        for code in risk.error_codes:
            et = error_types.get(code, {})
            phase = _ERROR_PHASE_MAP.get(code, "Unknown")

            # Find sample rows from recent_errors matching this code
            sample_rows = [
                {"row": e.get("row"), "column": e.get("column"), "message": e.get("message", "")[:80]}
                for e in recent_errors
                if e.get("code") == code
            ][:5]

            link = {
                "risk_title": risk.title,
                "error_code": code,
                "phase": phase,
                "total_occurrences": et.get("count", 0),
                "severity": et.get("severity", risk.severity),
                "affected_columns": [
                    {"column": col, "error_count": column_health.get(col, 0)}
                    for col in risk.columns
                    if col in column_health
                ],
                "sample_rows": sample_rows,
            }
            evidence_links.append(link)
            logger.debug(f"[evidence] Linked {code} → phase={phase}, count={et.get('count',0)}")

    insight.evidence_links = evidence_links
    logger.info(f"[evidence] Attached {len(evidence_links)} evidence links to insight")
    return insight

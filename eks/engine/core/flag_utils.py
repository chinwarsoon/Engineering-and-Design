"""
Shared review-flag reasoning for EKS.

I308 (T1.283): single source of truth for flag_reason computation so the
materialized ``documents.flag_reason`` column (written at ingest by
DocumentRegistry.register_document) and the export row builder
(pipeline_engine/exporter._build_flagged_rows) never diverge — AGENTS.md
§12 (fix breadth) / §13 (cross-source alignment). No SQL CASE duplication
in view DDL; the view is a pure projection of the materialized column.

Pure function module — stdlib only, zero pipeline dependencies.

Revision: 1.0
Date: 2026-08-13
Author: opencode
Summary: I308 (T1.283) - flag_reason computed here once, materialized at ingest.
"""
from __future__ import annotations

from typing import Any, Optional


def compute_flag_reason(
    extract_status: Optional[str],
    extraction_confidence: Any = None,
    confidence_threshold: float = 0.70,
) -> Optional[str]:
    """Return a human-readable flag_reason, or ``None`` when the document is clean.

    Flags a document when:
    - ``extract_status`` is not ``"success"``  -> ``Status: <status>``
    - ``extraction_confidence`` is below the threshold -> ``Low confidence: <x.xx>``
    - ``extraction_confidence`` is missing -> ``Confidence: missing``

    Matches the pre-I308 inline logic in exporter._build_flagged_rows so
    historical row builders stay behaviourally identical.

    Args:
        extract_status: The document's extraction status (None -> "pending").
        extraction_confidence: Numeric confidence or None.
        confidence_threshold: Below this value the document is flagged
                              (default 0.70, the pipeline review threshold).

    Returns:
        Semicolon-joined reasons, or ``None`` when no flag applies — so a
        clean document materializes NULL in ``documents.flag_reason`` (pure
        projection for v_review_flags).
    """
    reasons: list[str] = []
    status = extract_status if extract_status not in (None, "") else "pending"
    if status != "success":
        reasons.append(f"Status: {status}")
    if extraction_confidence is not None:
        try:
            conf_val = float(extraction_confidence)
        except (ValueError, TypeError):
            conf_val = 0.0
        if conf_val < confidence_threshold:
            reasons.append(f"Low confidence: {conf_val:.2f}")
    else:
        reasons.append("Confidence: missing")
    if not reasons:
        return None
    return "; ".join(reasons)

"""
Export row helpers for the EKS pipeline.

Extracted from ``eks_engine_pipeline.py`` (I233).  Pure functions — zero
pipeline dependencies, zero module-level globals.

Revision: 1.0
Date: 2026-07-23
Author: opencode
Summary: I233 split — export helpers extracted from eks_engine_pipeline.py.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional


def resolve_export_columns(schema_dir: Path) -> dict:
    """Read x_export flags from eks_doc_base_schema.json and return per-artifact column lists.

    T1.99.159 (I193): Replaces hardcoded 11-field subset with schema-driven resolution
    (now ~50 columns). Column ordering follows schema definition order: project metadata
    first (context), then document metadata.

    Args:
        schema_dir: Path to the config/schemas/ directory containing eks_doc_base_schema.json.

    Returns:
        Dict of {artifact_name: [column_names]} with keys:
        ``discovery_inventory``, ``extraction_results``, ``review_flags``.
        Falls back to hardcoded 11-column defaults if schema load fails, with a
        ``_fallback`` key set to True so callers can log a warning.
    """
    _project_meta_order = [
        "project_title", "project_number", "area", "discipline", "department",
    ]
    _doc_meta_order = [
        "source_type", "document_type", "document_number", "revision", "status",
        "is_latest", "file_path", "file_type", "ingested_at",
        "created_by", "checked_by", "approved_by", "originator_company",
        "security_class", "asset_tags", "page_count",
        "extract_status", "extraction_confidence", "extraction_notes",
        "verified_by",
        "file_size", "file_created_at", "file_modified_at", "file_hash",
        "embedded_title", "embedded_subject", "embedded_created_date",
        "embedded_modified_date", "embedded_creator_app", "embedded_producer",
        "embedded_last_modified_by", "embedded_keywords", "embedded_sheet_count",
        "document_title", "supersedes", "superseded_by", "lifecycle_stage",
        "revision_date", "revision_description", "embedded_revision_number",
        "references_documents", "project_phase", "contract_package",
        "issued_date", "responsible_engineer", "total_sheets", "language",
        "vendor_name",
    ]

    try:
        doc_base_path = schema_dir / "eks_doc_base_schema.json"
        if not doc_base_path.exists():
            raise FileNotFoundError(f"{doc_base_path} not found")

        with open(doc_base_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        doc_props = schema.get("definitions", {}).get("document_metadata_def", {}).get("properties", {})
        proj_props = schema.get("definitions", {}).get("project_metadata_def", {}).get("properties", {})

        all_exportable = []

        for col in _project_meta_order:
            if col in proj_props and proj_props[col].get("x_export"):
                all_exportable.append(col)

        for col in _doc_meta_order:
            if col in doc_props and doc_props[col].get("x_export"):
                all_exportable.append(col)

        extraction_specific = {"page_count", "extract_status", "extraction_confidence", "extraction_notes"}
        discovery = [c for c in all_exportable if c not in extraction_specific]

        extraction = list(all_exportable)

        review = [
            "project_title", "project_number", "area", "discipline",
            "document_number", "revision", "document_type",
            "extract_status", "extraction_confidence", "extraction_notes",
            "flag_reason", "ingested_at",
        ]

        return {
            "discovery_inventory": discovery,
            "extraction_results": extraction,
            "review_flags": review,
            "_fallback": False,
        }

    except Exception:
        return {
            "discovery_inventory": [
                "document_number", "revision", "document_type",
                "file_type", "file_path", "ingested_at",
            ],
            "extraction_results": [
                "document_number", "revision", "document_type",
                "file_type", "file_path", "ingested_at",
                "page_count", "extract_status", "extraction_confidence",
                "extraction_notes",
            ],
            "review_flags": [
                "document_number", "revision", "document_type",
                "extract_status", "extraction_confidence", "extraction_notes",
                "flag_reason", "ingested_at",
            ],
            "_fallback": True,
        }


def _build_export_rows(
    docs: list,
    status_filter: Optional[list] = None,
    columns: Optional[list] = None,
) -> list:
    """Build export-safe rows from document registry results.

    T1.99.160 (I193): Pass-through full doc dict — schema-driven columns handle
    subsetting. No hardcoded field list.

    Args:
        docs: List of document dicts from ``registry.list_documents()``.
        status_filter: If provided, only include docs whose ``extract_status``
                       is in this list.
        columns: Column ordering (for consistent output). Excludes ``id``.

    Returns:
        List of dicts suitable for ``DataExporter``.
    """
    rows = []
    for doc in docs:
        if status_filter is not None:
            if doc.get("extract_status", "pending") not in status_filter:
                continue
        row = dict(doc)
        if columns:
            row = {k: row.get(k, "") for k in columns if k != "id"}
        rows.append(row)
    return rows


def _build_flagged_rows(
    docs: list,
    columns: Optional[list] = None,
) -> list:
    """Build review-flag rows for documents needing human attention.

    T1.99.160 (I193): Pass-through full doc dict + add computed ``flag_reason``.

    Flags documents where:
    - ``extract_status`` is not ``"success"``, or
    - ``extraction_confidence`` is below 0.70 (or missing)

    Adds a ``flag_reason`` column with a human-readable explanation.
    """
    rows = []
    for doc in docs:
        status = doc.get("extract_status", "pending")
        confidence = doc.get("extraction_confidence")

        reasons = []
        if status != "success":
            reasons.append(f"Status: {status}")
        if confidence is not None:
            try:
                conf_val = float(confidence)
            except (ValueError, TypeError):
                conf_val = 0.0
            if conf_val < 0.70:
                reasons.append(f"Low confidence: {conf_val:.2f}")
        else:
            reasons.append("Confidence: missing")

        if not reasons:
            continue

        row = dict(doc)
        row["flag_reason"] = "; ".join(reasons)
        if columns:
            row = {k: row.get(k, "") for k in columns if k != "id"}
        rows.append(row)
    return rows

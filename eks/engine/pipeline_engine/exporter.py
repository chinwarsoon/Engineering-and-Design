"""
Export row helpers for the EKS pipeline.

Extracted from ``eks_engine_pipeline.py`` (I233).  Pure functions — zero
pipeline dependencies, zero module-level globals.

Revision: 1.1
Date: 2026-08-13
Author: opencode
Summary: I309 (T1.289): added validate_export_column_override — schema-driven
         per-view column override validation against eks_export_view_config.json
         (S-C-S-0313 EXPORT_COLUMN_NOT_ALLOWED). Consumed by the pipeline export
         phase and phase1_server run POST.
1.0 (2026-07-23): I233 split — export helpers extracted from eks_engine_pipeline.py.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional


def resolve_export_columns(schema_dir: Path) -> dict:
    """Resolve per-view export column lists from eks_export_view_config.json (SSOT).

    T1.282 (I308): Replaces the I193 x_export-flag scan of eks_doc_base_schema.json
    and removes the hardcoded 11-column fallback list. The 3 default views
    (discovery_inventory, extraction_results, review_flags) now declare their own
    ordered ``columns[]`` in eks_export_view_config.json (I307/T1.278 SSOT), so this
    function is a thin, fail-fast reader of that single config source.

    Per AGENTS.md §16: if the config is absent or unreadable, raise the registered
    error code S-C-S-0312 — never silently fall back to a second source of truth.

    Args:
        schema_dir: Path to the config/schemas/ directory containing
                    eks_export_view_config.json.

    Returns:
        Dict of {view_id: [column_names]} with keys ``discovery_inventory``,
        ``extraction_results``, ``review_flags``. Column ordering is exactly the
        ``columns[]`` order declared in the config.

    Raises:
        RuntimeError: FAIL_FAST [S-C-S-0312] if eks_export_view_config.json is
                      missing, unreadable, or has no views[] entries.
    """
    view_config_path = schema_dir / "eks_export_view_config.json"
    if not view_config_path.exists():
        raise RuntimeError(
            "FAIL_FAST [S-C-S-0312]: export view config not found — "
            f"{view_config_path} missing; cannot resolve export columns"
        )

    try:
        with open(view_config_path, "r", encoding="utf-8") as f:
            view_config = json.load(f)
    except Exception as exc:
        raise RuntimeError(
            "FAIL_FAST [S-C-S-0312]: export view config unreadable — "
            f"{view_config_path}: {exc}"
        ) from exc

    views = view_config.get("views")
    if not isinstance(views, list) or not views:
        raise RuntimeError(
            "FAIL_FAST [S-C-S-0312]: export view config has no views[] entries — "
            f"{view_config_path} must declare at least one view"
        )

    result = {}
    for view in views:
        view_id = view.get("view_id")
        columns = view.get("columns", [])
        if not view_id or not isinstance(columns, list):
            raise RuntimeError(
                "FAIL_FAST [S-C-S-0312]: export view config malformed — "
                f"view entry missing view_id or non-list columns: {view}"
            )
        result[view_id] = [c for c in columns if c != "id"]

    if not result:
        raise RuntimeError(
            "FAIL_FAST [S-C-S-0312]: export view config resolved zero views — "
            f"{view_config_path}"
        )

    return result


def resolve_export_views(schema_dir: Path) -> dict:
    """Resolve full per-view export specs from eks_export_view_config.json (SSOT).

    I308 (T1.284): schema-driven file/sheet names + artifact_type=view_id. The
    view config declares per view: view_id (== artifact_type), source_table,
    optional filter, ordered columns[], file_base_name, sheet_name, formats.
    The pipeline export path uses file_base_name/sheet_name for output naming
    instead of hardcoded literals (replaces eks_engine_pipeline.py:287-306).

    Per AGENTS.md §16: missing/unreadable config raises S-C-S-0312 — never
    silently fall back.

    Args:
        schema_dir: Path to the config/schemas/ directory.

    Returns:
        Dict of {view_id: {columns, file_base_name, sheet_name, source_table,
        filter, formats}} preserving config order.

    Raises:
        RuntimeError: FAIL_FAST [S-C-S-0312] if the config is missing or a view
                      entry lacks the required naming fields.
    """
    view_config_path = schema_dir / "eks_export_view_config.json"
    if not view_config_path.exists():
        raise RuntimeError(
            "FAIL_FAST [S-C-S-0312]: export view config not found — "
            f"{view_config_path} missing; cannot resolve export view specs"
        )

    try:
        with open(view_config_path, "r", encoding="utf-8") as f:
            view_config = json.load(f)
    except Exception as exc:
        raise RuntimeError(
            "FAIL_FAST [S-C-S-0312]: export view config unreadable — "
            f"{view_config_path}: {exc}"
        ) from exc

    views = view_config.get("views")
    if not isinstance(views, list) or not views:
        raise RuntimeError(
            "FAIL_FAST [S-C-S-0312]: export view config has no views[] entries — "
            f"{view_config_path}"
        )

    result = {}
    for view in views:
        view_id = view.get("view_id")
        if not view_id:
            raise RuntimeError(
                "FAIL_FAST [S-C-S-0312]: export view config entry missing view_id"
            )
        columns = view.get("columns")
        file_base_name = view.get("file_base_name")
        sheet_name = view.get("sheet_name")
        if not isinstance(columns, list) or not file_base_name or not sheet_name:
            raise RuntimeError(
                "FAIL_FAST [S-C-S-0312]: export view config entry malformed — "
                f"view '{view_id}' requires columns[]/file_base_name/sheet_name"
            )
        result[view_id] = {
            "columns": [c for c in columns if c != "id"],
            "file_base_name": file_base_name,
            "sheet_name": sheet_name,
            "source_table": view.get("source_table", ""),
            "filter": view.get("filter"),
            "formats": view.get("formats", ["csv", "xlsx"]),
        }

    if not result:
        raise RuntimeError(
            "FAIL_FAST [S-C-S-0312]: export view config resolved zero views — "
            f"{view_config_path}"
        )

    return result


def validate_export_column_override(schema_dir: Path, override: Optional[dict]) -> dict:
    """Validate a per-view column override against eks_export_view_config.json (SSOT).

    I309 (T1.289/T1.290): *override* maps ``{view_id: [column, ...]}`` — e.g.
    from the UI export panel (multi-select + re-order) or the pipeline ``--export``
    path. Every column must be one of the view's allowed export columns (the
    config ``columns[]`` minus ``id``). An unknown ``view_id`` or a disallowed
    column raises the registered error code ``S-C-S-0313``
    (EXPORT_COLUMN_NOT_ALLOWED) — never silently dropped.

    Per AGENTS.md \u00a716: if the view config is absent/unreadable, raise
    ``S-C-S-0312`` — never fall back to a second source of truth.

    Args:
        schema_dir: Path to the config/schemas/ directory containing
                    eks_export_view_config.json.
        override: Optional ``{view_id: [column_names]}``. ``None``/empty returns
                  ``{}`` (no override).

    Returns:
        Normalized override ``{view_id: [column_names]}`` preserving order.
        Only entries that appear in the config are retained.

    Raises:
        RuntimeError: FAIL_FAST [S-C-S-0313] for unknown view or disallowed
                      column; [S-C-S-0312] if the view config is missing or
                      unreadable.
    """
    if not override:
        return {}

    view_config_path = schema_dir / "eks_export_view_config.json"
    if not view_config_path.exists():
        raise RuntimeError(
            "FAIL_FAST [S-C-S-0312]: export view config not found — "
            f"{view_config_path} missing; cannot validate export column override"
        )

    try:
        with open(view_config_path, "r", encoding="utf-8") as f:
            view_config = json.load(f)
    except Exception as exc:
        raise RuntimeError(
            "FAIL_FAST [S-C-S-0312]: export view config unreadable — "
            f"{view_config_path}: {exc}"
        ) from exc

    allowed: dict = {}
    for view in view_config.get("views", []):
        view_id = view.get("view_id")
        if view_id:
            allowed[view_id] = [c for c in view.get("columns", []) if c != "id"]

    normalized: dict = {}
    for view_id, cols in override.items():
        if view_id not in allowed:
            raise RuntimeError(
                "FAIL_FAST [S-C-S-0313]: export column override references unknown "
                f"export view '{view_id}' — allowed views: {sorted(allowed)}"
            )
        allowed_set = set(allowed[view_id])
        bad = [c for c in cols if c not in allowed_set]
        if bad:
            raise RuntimeError(
                "FAIL_FAST [S-C-S-0313]: column(s) "
                f"{bad} not allowed for view '{view_id}' — "
                f"allowed columns: {allowed[view_id]}"
            )
        normalized[view_id] = list(cols)

    return normalized


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

    I308 (T1.283): flag_reason is materialized at ingest (core.flag_utils is the
    single source of truth — AGENTS.md §12). This row builder prefers the
    materialized ``flag_reason`` and only recomputes for legacy rows ingested
    before I308, so behaviour is identical and never diverges.

    Flags documents where:
    - ``extract_status`` is not ``"success"``, or
    - ``extraction_confidence`` is below 0.70 (or missing)

    Rows with no flag reason (clean documents) are excluded.
    """
    # Lazy import keeps this module top-level pure (stdlib-only).
    # `..core` = eks.engine.core (exporter lives in eks/engine/pipeline_engine/).
    from ..core.flag_utils import compute_flag_reason

    rows = []
    for doc in docs:
        status = doc.get("extract_status", "pending")
        confidence = doc.get("extraction_confidence")

        flag_reason = doc.get("flag_reason") or compute_flag_reason(status, confidence)
        if not flag_reason:
            continue

        row = dict(doc)
        row["flag_reason"] = flag_reason
        if columns:
            row = {k: row.get(k, "") for k in columns if k != "id"}
        rows.append(row)
    return rows

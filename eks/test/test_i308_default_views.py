"""
Focused I308 tests: schema-driven persistent export views + export naming.

Revision: 0.2
Date: 2026-08-14
Author: opencode
Summary: 0.2: I313 (T1.307) — extended the no-hardcoded-literal guard to reject
     bare view_id/artifact_type literal assignments, phase-letter artifact_type
     values, and "eks_export_" fallbacks across both the pipeline and
     phase1_server export paths.
0.1: T1.285 — persistent v_* views (discovery_inventory, extraction_results,
     review_flags) created from eks_export_view_config.json; is_latest=TRUE
     filter; flag_reason materialized at ingest (pure projection); schema-
     driven file/sheet names + artifact_type == view_id in the export path;
     missing view config raises S-C-S-0312 (no hardcoded fallback).
"""

import json
import tempfile
from pathlib import Path

import duckdb
import pytest

from eks.engine.core.registry import DocumentRegistry
from eks.engine.core.schema_to_ddl import SchemaToDDL
from eks.engine.pipeline_engine.exporter import (
    resolve_export_columns,
    resolve_export_views,
)


_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_CONFIG_DIR = _PROJECT_ROOT / "config"
_SCHEMA_DIR = _CONFIG_DIR / "schemas"

_DEFAULT_VIEW_IDS = ("discovery_inventory", "extraction_results", "review_flags")


def _load_view_config():
    return json.loads((_SCHEMA_DIR / "eks_export_view_config.json").read_text(encoding="utf-8"))


def _register_sample(registry, doc_number, revision, file_path, **extra):
    """Register one document revision via the public API."""
    metadata = {
        "project_title": "Test Project",
        "project_number": "P-100",
        "area": "Mechanical",
        "discipline": "HVAC",
        "department": "Engineering",
        "document_type": "drawing",
        "document_number": doc_number,
        "revision": revision,
        "status": "issued",
        "file_path": file_path,
        "file_type": "pdf",
        "source_type": "ingested",
    }
    metadata.update(extra)
    return registry.register_document(metadata)


def test_i308_default_views_are_queryable():
    """T1.285: the 3 default v_* views exist and are queryable."""
    with tempfile.TemporaryDirectory() as directory:
        db_path = Path(directory) / "i308.db"
        DocumentRegistry(db_path=str(db_path))
        conn = duckdb.connect(str(db_path), read_only=True)
        try:
            for view_id in _DEFAULT_VIEW_IDS:
                rows = conn.execute(f"SELECT * FROM v_{view_id}").fetchall()
                assert isinstance(rows, list), f"v_{view_id} not queryable"
        finally:
            conn.close()


def test_i308_view_ddl_columns_match_config():
    """T1.285: view column order == config columns[] order == PRAGMA order."""
    view_config = _load_view_config()
    with tempfile.TemporaryDirectory() as directory:
        db_path = Path(directory) / "i308.db"
        DocumentRegistry(db_path=str(db_path))
        conn = duckdb.connect(str(db_path), read_only=True)
        try:
            for entry in view_config["views"]:
                view_id = entry["view_id"]
                config_cols = [c for c in entry["columns"] if c != "id"]
                pragma_cols = [row[1] for row in conn.execute(f"PRAGMA table_info('v_{view_id}')").fetchall()]
                assert config_cols == pragma_cols, (
                    f"view v_{view_id} column order diverges from config"
                )
        finally:
            conn.close()


def test_i308_views_filter_is_latest():
    """T1.285: is_latest=TRUE filter — superseded revisions are excluded."""
    with tempfile.TemporaryDirectory() as directory:
        db_path = Path(directory) / "i308.db"
        registry = DocumentRegistry(db_path=str(db_path))
        _register_sample(registry, "DWG-A001", "A", "C:/docs/A001_A.pdf")
        _register_sample(registry, "DWG-A001", "B", "C:/docs/A001_B.pdf")

        conn = duckdb.connect(str(db_path), read_only=True)
        try:
            for view_id in _DEFAULT_VIEW_IDS:
                rows = conn.execute(
                    f"SELECT revision FROM v_{view_id} WHERE document_number = 'DWG-A001'"
                ).fetchall()
                revisions = {r[0] for r in rows}
                assert revisions == {"B"}, f"v_{view_id} should expose only is_latest=True (B), got {revisions}"
        finally:
            conn.close()


def test_i308_review_flags_materialized_flag_reason():
    """T1.285: v_review_flags reads materialized documents.flag_reason (pure projection)."""
    with tempfile.TemporaryDirectory() as directory:
        db_path = Path(directory) / "i308.db"
        registry = DocumentRegistry(db_path=str(db_path))
        # Low-confidence doc -> flag_reason computed at ingest.
        _register_sample(
            registry, "DWG-B002", "A", "C:/docs/B002_A.pdf",
            extract_status="extracted", extraction_confidence=0.35,
        )
        # Success doc -> no flag_reason (clean).
        _register_sample(
            registry, "DWG-C003", "A", "C:/docs/C003_A.pdf",
            extract_status="success", extraction_confidence=0.95,
        )

        conn = duckdb.connect(str(db_path), read_only=True)
        try:
            rows = conn.execute(
                "SELECT document_number, flag_reason FROM v_review_flags"
            ).fetchall()
            by_doc = {r[0]: r[1] for r in rows}
            assert "Low confidence: 0.35" in by_doc.get("DWG-B002", ""), (
                f"flag_reason not materialized for DWG-B002: {by_doc}"
            )
            assert by_doc.get("DWG-C003") is None, (
                f"clean doc should have no flag_reason: {by_doc}"
            )
        finally:
            conn.close()


def test_i308_export_names_and_artifact_type_schema_driven():
    """T1.285: file/sheet names come from config; artifact_type == view_id."""
    specs = resolve_export_views(_SCHEMA_DIR)
    assert set(specs.keys()) == set(_DEFAULT_VIEW_IDS)

    view_config = _load_view_config()
    for entry in view_config["views"]:
        view_id = entry["view_id"]
        spec = specs[view_id]
        assert spec["file_base_name"] == entry["file_base_name"]
        assert spec["sheet_name"] == entry["sheet_name"]
        assert spec["formats"] == entry["formats"]
        assert spec["source_table"] == entry["source_table"]
        # artifact_type == view_id (I306)
        assert view_id == entry["view_id"]

    columns = resolve_export_columns(_SCHEMA_DIR)
    assert set(columns.keys()) == set(_DEFAULT_VIEW_IDS)


def test_i308_export_path_has_no_hardcoded_literals():
    """T1.285 + I313/T1.307: pipeline + phase1_server export paths must not
    hardcode file/sheet names, view_id/artifact_type literals, phase-letter
    artifact_type values, or eks_export_ fallback defaults."""
    pipeline_path = _PROJECT_ROOT / "engine" / "eks_engine_pipeline.py"
    server_path = _PROJECT_ROOT / "ui" / "backend" / "phase1_server.py"
    pipeline_src = pipeline_path.read_text(encoding="utf-8")
    server_src = server_path.read_text(encoding="utf-8")

    # Per-view filename + sheet-name literals (I308/T1.284).
    for literal in (
        "discovery_inventory.csv",
        "extraction_results.csv",
        "review_flags.csv",
        '"Discovery"',
        '"Extraction"',
        '"Review Flags"',
    ):
        assert literal not in pipeline_src, f"hardcoded export literal still in pipeline: {literal}"

    # I313/T1.307 (BLOCK-1/D-4): no literal view_id indices or artifact_type
    # values in the pipeline export path — all derived from resolve_export_views()
    # keys / each view's view_id.
    for literal in (
        'export_config["discovery_inventory"]',
        'export_config["extraction_results"]',
        'export_config["review_flags"]',
        '"artifact_type": "discovery_inventory"',
        '"artifact_type": "extraction_results"',
        '"artifact_type": "review_flags"',
    ):
        assert literal not in pipeline_src, (
            f"literal view_id/artifact_type still in pipeline: {literal}"
        )

    # I313/T1.307 (BLOCK-2): no literal view_id values in the server phase→view
    # map and no literal view_id branch in the row-builder dispatch.
    for literal in (
        '"a": "discovery_inventory"',
        '"b": "extraction_results"',
        '"c": "review_flags"',
        'view_id == "review_flags"',
    ):
        assert literal not in server_src, (
            f"literal view_id still in phase1_server: {literal}"
        )

    # I313/T1.307 (BLOCK-3): no "eks_export_" fallback literal defaults in the
    # server download file-name resolution (fail-fast S-C-S-0304 instead).
    assert '"eks_export_{phase}.{ext}"' not in server_src, (
        "fallback download template literal still in phase1_server"
    )
    assert '"eks_export.xlsx"' not in server_src, (
        "fallback workbook name literal still in phase1_server"
    )

    # I313/T1.307 (BLOCK-4): insert_artifact must never record the phase letter
    # (a/b/c/all) as artifact_type — always the export view_id.
    assert "insert_artifact(export_job_id, phase," not in server_src, (
        "phase letter still recorded as artifact_type in phase1_server"
    )


def test_i308_missing_view_config_raises_registered_code(tmp_path):
    """T1.285: missing eks_export_view_config.json -> FAIL_FAST S-C-S-0312 (no fallback)."""
    empty_dir = tmp_path / "no_view_config"
    empty_dir.mkdir()
    with pytest.raises(RuntimeError) as excinfo:
        resolve_export_columns(empty_dir)
    assert "S-C-S-0312" in str(excinfo.value)

    with pytest.raises(RuntimeError) as excinfo:
        resolve_export_views(empty_dir)
    assert "S-C-S-0312" in str(excinfo.value)


def test_i308_error_code_registered():
    """T1.285: S-C-S-0312 is registered in eks_error_config.json."""
    error_config = json.loads((_SCHEMA_DIR / "eks_error_config.json").read_text(encoding="utf-8"))
    entry = (error_config.get("system_errors", {}) or {}).get("S-C-S-0312")
    assert entry is not None, "S-C-S-0312 missing from eks_error_config.json"
    assert entry["name"] == "EXPORT_VIEW_CONFIG_MISSING"


def test_i308_generate_view_ddl_renders_filter_where():
    """T1.285: generate_view_ddl renders the is_latest=TRUE WHERE clause."""
    view_config = _load_view_config()
    generator = SchemaToDDL({}, db_config={})
    statements = generator.generate_view_ddl(view_config=view_config)
    assert len(statements) == len(view_config["views"])
    for stmt, entry in zip(statements, view_config["views"]):
        assert f"v_{entry['view_id']}" in stmt
        assert f"SELECT " in stmt
        if entry.get("filter"):
            fcol = entry["filter"]["column"]
            assert f"WHERE {fcol} = TRUE" in stmt, f"missing is_latest filter in {stmt}"

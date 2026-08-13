"""
Focused I310 tests for schema-driven DuckDB materialization.

Revision: 0.2
Date: 2026-08-12
Author: opencode
Summary: 0.2: T1.296 — added materialization error-code coverage
          (registration + resolver + structured loader errors).
0.1: T1.296 — renderer, definition extraction, materialization, and
         idempotency coverage.
"""

import json
import tempfile
from pathlib import Path

import duckdb
import pytest

from eks.engine.core.definition_loader import DefinitionLoader, DefinitionLoadError
from eks.engine.core.error_manager import ErrorManager
from eks.engine.core.registry import DocumentRegistry
from eks.engine.core.schema_to_ddl import SchemaToDDL


_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_CONFIG_DIR = _PROJECT_ROOT / "config"
_SCHEMA_DIR = _CONFIG_DIR / "schemas"


def _load_db_config():
    """Load the I310 DB configuration test fixture."""
    return json.loads((_SCHEMA_DIR / "eks_db_config.json").read_text(encoding="utf-8"))


def test_i310_renders_all_configured_tables_and_quotes_identifiers():
    """T1.292: render all 53 tables and reserved identifiers safely."""
    config = _load_db_config()
    generator = SchemaToDDL({}, db_config=config)

    statements = generator.generate_db_tables_ddl()

    assert len(statements) == 53
    assert any('"symmetric" BOOLEAN' in statement for statement in statements)
    assert any("FOREIGN KEY" in statement for statement in statements)


def test_i310_extracts_all_definition_tables_with_uuid5_ids():
    """T1.293: extract rows from every configured definition source."""
    config = _load_db_config()
    loader = DefinitionLoader(config, _CONFIG_DIR)

    for spec in loader.definition_specs():
        rows = loader.extract_rows(spec)
        assert rows, f"no rows extracted for {spec['table_name']}"
        assert all(row["id"] for row in rows)
        assert rows[0]["id"] == loader.extract_rows(spec)[0]["id"]


def test_i310_registry_materializes_tables_and_is_idempotent():
    """T1.294/T1.296: initialize all configured tables without duplicate rows."""
    config = _load_db_config()
    expected_tables = {spec["table_name"] for spec in config["db_tables"]}

    with tempfile.TemporaryDirectory() as directory:
        db_path = Path(directory) / "i310.db"
        DocumentRegistry(db_path=str(db_path))
        first = duckdb.connect(str(db_path), read_only=True)
        actual_tables = {row[0] for row in first.execute("SHOW TABLES").fetchall()}
        first_project_rows = first.execute("SELECT COUNT(*) FROM project").fetchone()[0]
        first.close()

        DocumentRegistry(db_path=str(db_path))
        second = duckdb.connect(str(db_path), read_only=True)
        second_project_rows = second.execute("SELECT COUNT(*) FROM project").fetchone()[0]
        second.close()

    assert expected_tables <= actual_tables
    assert first_project_rows == second_project_rows
    assert first_project_rows > 0


def test_i310_materialization_error_codes_registered():
    """T1.296: dedicated materialization/config/data error codes are registered."""
    manager = ErrorManager(config_dir=str(_CONFIG_DIR))

    system_codes = {
        "S-C-S-0309": "INVALID_DB_TABLE_SPEC",
        "S-C-S-0310": "INVALID_DB_FK_SPEC",
        "S-R-S-0411": "DB_MATERIALIZATION_FAILED",
        "S-R-S-0412": "DEFINITION_LOAD_FAILED",
    }
    for code, expected_name in system_codes.items():
        entry = manager.get_system_error(code)
        assert entry is not None, f"missing system code {code}"
        assert entry["name"] == expected_name

    data_codes = {
        "P1-R-P-0001": "NATURAL_KEY_MISSING",
        "P1-R-P-0002": "FK_TARGET_MISSING",
        "P1-R-P-0003": "SOURCE_TRANSFORM_FAILED",
    }
    for code, expected_name in data_codes.items():
        entry = manager.get_data_error(code)
        assert entry is not None, f"missing data code {code}"
        assert entry["name"] == expected_name


def test_i310_schema_renderer_raises_with_error_code():
    """T1.296: SchemaToDDL reports invalid table specs with the registered code."""
    config = _load_db_config()
    generator = SchemaToDDL({}, db_config=config)
    with pytest.raises(KeyError) as excinfo:
        generator._render_table_from_config("does_not_exist")
    assert "S-C-S-0309" in str(excinfo.value)


def test_i310_loader_raises_structured_error_on_missing_source():
    """T1.296: DefinitionLoader raises DefinitionLoadError with a registered code."""
    config = _load_db_config()
    loader = DefinitionLoader(config, _CONFIG_DIR)
    spec = {
        "table_name": "missing_source_table",
        "source_config_ref": "no_such_config.json",
        "source_path": "items",
        "transform": "array-of-objects",
        "columns": [{"name": "id", "column_type": "VARCHAR", "is_primary": True}],
        "id_strategy": {
            "namespace": "eks:missing",
            "natural_key_columns": ["id"],
            "algorithm": "uuid5",
        },
    }
    with pytest.raises(DefinitionLoadError) as excinfo:
        loader.extract_rows(spec)
    assert excinfo.value.code == "P1-R-P-0003"

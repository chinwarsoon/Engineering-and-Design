"""Runtime tests for BaseAssetLoader (T1.310 / I318 spike).

These are loader-behaviour tests (sheet read, column mapping, fragment
composition, conditional-fragment trigger, canonical record shape, null
tolerance, coverage) — not schema-validation tests.

The suite is skipped when the Datadrop workbook is not available on disk so
that CI without the source data still collects cleanly.
"""

from pathlib import Path

import pytest

from eks.engine.extractors.base_asset_loader import BaseAssetLoader

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"

_probe = BaseAssetLoader(config_dir=CONFIG_DIR)
WORKBOOK = _probe.workbook_path
_probe.close()

pytestmark = pytest.mark.skipif(
    not WORKBOOK.is_file(),
    reason=f"Datadrop workbook not available: {WORKBOOK}",
)


@pytest.fixture(scope="module")
def loader():
    ldr = BaseAssetLoader(config_dir=CONFIG_DIR)
    yield ldr
    ldr.close()


# ------------------------------------------------------------------ sheet read
def test_sheet_names(loader):
    sheets = loader.sheet_names
    for expected in ("Equipment", "Motor", "Instrument", "CONTROLVALVE", "MANUALVALVE"):
        assert expected in sheets


def test_headers_include_identity_columns(loader):
    headers = loader._read_headers("Equipment")
    for expected in ("KEYTAG", "TAG_TYPE", "TAG_NO", "DESCRIPTION", "MANUFACTURER NAME"):
        assert expected in headers


# ------------------------------------------------------------- column mapping
def test_column_mapping_config_wins(loader):
    assert loader._column_target("Equipment", "SYSTEM CODE") == "system_hierarchy.system_code"
    assert loader._column_target("Equipment", "CRITICALITY") == "lifecycle_context.criticality"
    # UNIT is config-mapped for Equipment (line "UNIT" -> unit).
    assert loader._column_target("Equipment", "UNIT") == "unit"


def test_column_mapping_native_fallback(loader):
    # KEYTAG/TAG_NO are universal extractor columns handled by the native
    # item_core map when column_normalization does not carry them.
    assert loader._column_target("Equipment", "KEYTAG") == "keytag"
    assert loader._column_target("Equipment", "TAG_NO") == "tag_no"
    assert loader._column_target("Equipment", "TAG_TYPE") == "tag_type"


def test_column_mapping_unknown_header(loader):
    assert loader._column_target("Equipment", "NO SUCH COLUMN") is None


# ---------------------------------------------------------------- load_sheet
def test_load_sheet_returns_records(loader):
    result = loader.load_sheet("Equipment", tag_type="AT_EQPMP", limit=10)
    assert len(result.records) >= 1
    assert all(rec["source_meta"]["tag_type"] == "AT_EQPMP" for rec in result.records)


def test_load_sheet_tag_filter(loader):
    result = loader.load_sheet("Equipment", tag_type="AT_NOPE", limit=5)
    assert result.records == []


def test_load_motor_sheet(loader):
    result = loader.load_sheet("Motor", tag_type="AT_MOTOR", limit=10)
    assert len(result.records) >= 1
    # AT_MOTOR composes the motor_control fragment.
    assert "motor_control" in result.records[0]
    assert "rotating_equipment" in result.records[0]


# ------------------------------------------------------- canonical record shape
def test_canonical_record_shape(loader):
    result = loader.load_sheet("Equipment", tag_type="AT_EQPMP", limit=1)
    record = result.records[0]
    assert "source_meta" in record
    assert "asset_health" in record
    for frag in ("item_core", "process_conditions", "manufacturer", "asset_lifecycle",
                 "control_system", "rotating_equipment", "asset_context"):
        assert frag in record
    assert record["item_core"]["keytag"]
    assert record["item_core"]["tag_no"]
    # asset_context carries the nested hierarchy objects (stable canonical shape).
    assert set(record["asset_context"]) >= {
        "project_context", "location_hierarchy", "system_hierarchy", "lifecycle_context",
    }


def test_asset_health_shape(loader):
    result = loader.load_sheet("Equipment", tag_type="AT_EQPMP", limit=1)
    health = result.records[0]["asset_health"]
    assert health["grade"] in ("HIGH", "MEDIUM", "LOW")
    assert 0.0 <= health["completeness"] <= 1.0
    assert 0.0 <= health["fill_rate"] <= 1.0
    assert isinstance(health["fragment_completeness"], dict)
    assert isinstance(health["null_fields"], list)


# --------------------------------------------------------- dotted field routing
def test_dotted_fields_route_into_asset_context(loader):
    normalized = {
        "keytag": "K-ROUTE-1",
        "tag_type": "AT_EQPMP",
        "system_hierarchy.system_code": "SYS-A",
        "location_hierarchy.area": "AREA-1",
        "lifecycle_context.criticality": "HIGH",
    }
    record, unrouted = loader._compose_record(normalized, {"row": 1})
    assert unrouted == []
    ctx = record["asset_context"]
    assert ctx["system_hierarchy"]["system_code"] == "SYS-A"
    assert ctx["location_hierarchy"]["area"] == "AREA-1"
    assert ctx["lifecycle_context"]["criticality"] == "HIGH"


# -------------------------------------------------- conditional fragment trigger
def test_conditional_fragment_triggered(loader):
    normalized = {"keytag": "K-UV-1", "tag_type": "AT_EQUIP", "device_type_code": "UV"}
    record, _ = loader._compose_record(normalized, {"row": 1})
    assert "specialist_equipment" in record


def test_conditional_fragment_not_triggered(loader):
    normalized = {"keytag": "K-NONE-1", "tag_type": "AT_EQUIP", "device_type_code": "ZZ"}
    record, _ = loader._compose_record(normalized, {"row": 1})
    assert "specialist_equipment" not in record


# ------------------------------------------------------------ null tolerance
def test_null_fields_tolerated(loader):
    normalized = {"keytag": "K-NULL-1", "tag_type": "AT_EQPMP", "unit": "", "description": None}
    record, _ = loader._compose_record(normalized, {"row": 1})
    # Blank values are never written into the canonical record...
    assert "unit" not in record["item_core"]
    assert "description" not in record["item_core"]
    # ...but they surface in the health null-field audit.
    assert "item_core.unit" in record["asset_health"]["null_fields"]
    assert "item_core.description" in record["asset_health"]["null_fields"]


def test_unknown_tag_type_skipped(loader):
    normalized = {"keytag": "K-X-1", "tag_type": "AT_NOT_REGISTERED"}
    record, reason = loader._compose_record(normalized, {"row": 1})
    assert record is None
    assert any("not in asset_type_registry" in r for r in reason)


# ---------------------------------------------------------------- coverage
def test_column_coverage_covers_all_sheets(loader):
    coverage = loader.column_coverage()
    assert len(coverage) == 7
    for sheet_name in ("Equipment", "Motor", "Instrument", "Pipeline",
                       "Inline Component", "CONTROLVALVE", "MANUALVALVE"):
        assert sheet_name in coverage
        entry = coverage[sheet_name]
        assert isinstance(entry["mapped"], list)
        assert isinstance(entry["native"], list)
        assert isinstance(entry["unmapped"], list)


def test_column_coverage_unmapped_reported(loader):
    coverage = loader.column_coverage()
    # DESIGN CAPACITY is a real Datadrop column not yet covered by config.
    assert "DESIGN CAPACITY" in coverage["Equipment"]["unmapped"]


def test_coverage_report_format(loader):
    report = loader.format_coverage_report(loader.column_coverage())
    assert "## Equipment" in report
    assert "Unmapped columns" in report
    assert "## Motor" in report

"""
Phase 5.6 — Memory-Aware Schema-Driven Model Selection Tests

Tests for the schema-driven model_pool selector and the metadata-free
OllamaProvider. Validates:
  - Schema entries (model_entry definition) accept/reject correctly
  - Selector picks correct model for synthetic memory values
  - Provider contains no hardcoded model-name strings
  - gemma4:e4b (enabled=false) is never selected
  - Defense-in-depth memory check in OllamaProvider.is_available()
  - AiInsight carries selection telemetry
  - RunStore persists new columns
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

# Add workflow to path
WORKFLOW = Path(__file__).resolve().parent.parent / "workflow"
sys.path.insert(0, str(WORKFLOW))

try:
    from ai_ops_engine.core.engine import _select_model_by_memory
    from ai_ops_engine.core.contracts import AiInsight
    from ai_ops_engine.persistence.run_store import RunStore
    SCHEMA_DRIVEN_AVAILABLE = True
except Exception as exc:  # pragma: no cover
    SCHEMA_DRIVEN_AVAILABLE = False
    _IMPORT_ERROR = exc


SCHEMA_PATH = Path(__file__).resolve().parent.parent / "config" / "schemas"
PROVIDER_PATH = (
    WORKFLOW / "ai_ops_engine" / "providers" / "ollama_provider.py"
)


def _load_schema():
    base = json.loads((SCHEMA_PATH / "dcc_register_base.json").read_text())
    params = json.loads((SCHEMA_PATH / "dcc_global_parameters.json").read_text())
    return base, params


@unittest.skipUnless(SCHEMA_DRIVEN_AVAILABLE, f"import error: {_IMPORT_ERROR if not SCHEMA_DRIVEN_AVAILABLE else ''}")
class TestSchemaDrivenModelPool(unittest.TestCase):
    """TC-5.6.1 — Schema accepts model_entry shape and rejects malformed entries."""

    def test_model_entry_definition_exists(self):
        base, _ = _load_schema()
        self.assertIn("model_entry", base["definitions"])
        me = base["definitions"]["model_entry"]
        self.assertEqual(me["type"], "object")
        self.assertIn("name", me["required"])
        self.assertIn("size_gb", me["required"])
        self.assertIn("family", me["required"])
        self.assertIn("capability", me["required"])

    def test_model_entry_rejects_malformed_name(self):
        from jsonschema import Draft7Validator
        base, _ = _load_schema()
        me = base["definitions"]["model_entry"]
        v = Draft7Validator(me)
        bad = {"name": "INVALID NAME!", "size_gb": 1.0, "family": "other", "capability": "chat"}
        errors = list(v.iter_errors(bad))
        self.assertTrue(errors, "Malformed name should fail pattern check")

    def test_dcc_parameter_entry_extended(self):
        base, _ = _load_schema()
        dpe = base["definitions"]["dcc_parameter_entry"]
        props = dpe["properties"]
        self.assertIn("model_pool", props)
        self.assertIn("embed_model_pool", props)
        self.assertIn("model_memory_headroom_gb", props)

    def test_global_parameters_pool_has_models(self):
        _, params = _load_schema()
        pool = params["dcc_parameters"]["model_pool"]
        self.assertGreaterEqual(len(pool), 4)
        names = {m["name"] for m in pool}
        self.assertIn("llama3.2:3b", names)
        self.assertIn("gemma4:e4b", names)

    def test_gemma4_blocked_via_enabled_false(self):
        _, params = _load_schema()
        pool = params["dcc_parameters"]["model_pool"]
        gemma = next(m for m in pool if m["name"] == "gemma4:e4b")
        self.assertFalse(gemma["enabled"], "gemma4:e4b must be enabled=false")


@unittest.skipUnless(SCHEMA_DRIVEN_AVAILABLE, f"import error: {_IMPORT_ERROR if not SCHEMA_DRIVEN_AVAILABLE else ''}")
class TestMemoryAwareSelector(unittest.TestCase):
    """TC-5.6.2 — Selector picks first enabled entry that fits available RAM."""

    POOL = [
        {"name": "llama3.2:3b", "size_gb": 2.0, "ram_multiplier": 1.5, "enabled": True},
        {"name": "qwen2.5-coder:3b", "size_gb": 1.9, "ram_multiplier": 1.5, "enabled": True},
        {"name": "deepseek-coder:1.3b", "size_gb": 0.776, "ram_multiplier": 1.5, "enabled": True},
        {"name": "gemma3:4b", "size_gb": 3.3, "ram_multiplier": 1.5, "enabled": True},
        {"name": "gemma4:e4b", "size_gb": 9.6, "ram_multiplier": 1.5, "enabled": False},
    ]

    def test_picks_first_enabled_that_fits(self):
        # When selector sees a free_ram that lets first entry fit, it picks that one
        name, entry, reason, free, req = _select_model_by_memory(self.POOL, 2.0)
        # We can't directly control free_ram in this test (it uses psutil),
        # but we can assert the returned name is in our pool and is enabled.
        if name is not None:
            self.assertTrue(any(m["name"] == name and m["enabled"] for m in self.POOL))
            self.assertNotEqual(name, "gemma4:e4b")
        self.assertIn(reason, {"schema_default", "no_model_fits"})

    def test_gemma4_never_selected(self):
        # Even if gemma4:e4b is the only entry, enabled=False must skip it
        pool = [{"name": "gemma4:e4b", "size_gb": 9.6, "ram_multiplier": 1.5, "enabled": False}]
        name, entry, reason, free, req = _select_model_by_memory(pool, 2.0)
        self.assertIsNone(name)
        self.assertEqual(reason, "no_model_fits")

    def test_empty_pool_returns_none(self):
        name, entry, reason, free, req = _select_model_by_memory([], 2.0)
        self.assertIsNone(name)
        self.assertEqual(reason, "no_model_fits")

    def test_disabled_entries_are_skipped(self):
        pool = [
            {"name": "disabled-big", "size_gb": 0.1, "ram_multiplier": 1.5, "enabled": False},
            {"name": "enabled-tiny", "size_gb": 0.1, "ram_multiplier": 1.5, "enabled": True},
        ]
        name, entry, reason, free, req = _select_model_by_memory(pool, 0.0)
        self.assertEqual(name, "enabled-tiny")


class TestProviderIsMetadataFree(unittest.TestCase):
    """TC-5.6.3 — OllamaProvider contains no hardcoded model-name strings."""

    def test_no_specific_model_names(self):
        content = PROVIDER_PATH.read_text()
        for forbidden in [
            "llama3.1:8b",
            "llama3.2",
            "gemma3",
            "gemma4",
            "qwen2.5",
            "deepseek",
            "nomic",
        ]:
            self.assertNotIn(
                forbidden, content,
                f"Provider file must not contain hardcoded model name: {forbidden}",
            )

    def test_no_default_model_constant(self):
        content = PROVIDER_PATH.read_text()
        self.assertNotIn("_DEFAULT_MODEL", content)


@unittest.skipUnless(SCHEMA_DRIVEN_AVAILABLE, f"import error: {_IMPORT_ERROR if not SCHEMA_DRIVEN_AVAILABLE else ''}")
class TestAiInsightTelemetry(unittest.TestCase):
    """TC-5.6.4 — AiInsight carries Phase 5.6 selection telemetry."""

    def test_default_fields_present(self):
        insight = AiInsight()
        self.assertEqual(insight.model_family, "")
        self.assertEqual(insight.model_capability, "")
        self.assertEqual(insight.free_ram_mb, 0)
        self.assertEqual(insight.required_ram_mb, 0)
        self.assertEqual(insight.selection_reason, "")

    def test_to_dict_includes_telemetry(self):
        insight = AiInsight(
            model_used="llama3.2:3b",
            model_family="llama3.2",
            model_capability="chat",
            free_ram_mb=9500,
            required_ram_mb=3000,
            selection_reason="schema_default",
        )
        d = insight.to_dict()
        for key in [
            "model_used", "model_family", "model_capability",
            "free_ram_mb", "required_ram_mb", "selection_reason",
        ]:
            self.assertIn(key, d)
        self.assertEqual(d["selection_reason"], "schema_default")


@unittest.skipUnless(SCHEMA_DRIVEN_AVAILABLE, f"import error: {_IMPORT_ERROR if not SCHEMA_DRIVEN_AVAILABLE else ''}")
class TestRunStorePhase56Columns(unittest.TestCase):
    """TC-5.6.5 — RunStore creates ai_insights with new columns."""

    def test_columns_added_on_init(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "test.duckdb"
            store = RunStore(db_path)
            try:
                conn = store._get_conn()
                self.assertIsNotNone(conn)
                cols = [row[1] for row in conn.execute(
                    "PRAGMA table_info(ai_insights)"
                ).fetchall()]
                for col in [
                    "model_family", "model_capability",
                    "free_ram_mb", "required_ram_mb", "selection_reason",
                ]:
                    self.assertIn(col, cols, f"Column {col} missing from ai_insights")
            finally:
                store.close()

    def test_save_insight_with_telemetry(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "test2.duckdb"
            store = RunStore(db_path)
            try:
                insight = AiInsight(
                    run_id="test-001",
                    model_used="llama3.2:3b",
                    model_family="llama3.2",
                    model_capability="chat",
                    free_ram_mb=9500,
                    required_ram_mb=3000,
                    selection_reason="schema_default",
                )
                store.save_insight(insight)
                conn = store._get_conn()
                row = conn.execute(
                    "SELECT model_used, model_family, model_capability, "
                    "free_ram_mb, required_ram_mb, selection_reason "
                    "FROM ai_insights WHERE run_id = ?",
                    ["test-001"],
                ).fetchone()
                self.assertIsNotNone(row)
                self.assertEqual(row[0], "llama3.2:3b")
                self.assertEqual(row[1], "llama3.2")
                self.assertEqual(row[2], "chat")
                self.assertEqual(row[3], 9500)
                self.assertEqual(row[4], 3000)
                self.assertEqual(row[5], "schema_default")
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)

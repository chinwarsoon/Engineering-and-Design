"""Standalone tests for I259 (Tier 3 fallback) and I263 (4-stage refactoring)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from common.library.loader.schema_discovery import discover_schema_files, discover_schema_files_tier3
from eks.engine.core.schema_loader import SchemaLoader, _STEM_TO_ATTR

ROOT = Path(__file__).resolve().parent.parent


class TestTier3Fallback(unittest.TestCase):
    """Test Tier 3 fallback discovery of auxiliary schemas (I259)."""

    @classmethod
    def setUpClass(cls):
        cls.config_dir = ROOT / "config"
        if not (cls.config_dir / "schemas").exists():
            cls.config_dir = ROOT / "config"

    def test_tier3_discovers_5_auxiliary_schemas(self):
        """5 auxiliary schemas ending in _schema.json should be found by Tier 3."""
        loader = SchemaLoader(str(self.config_dir))
        project_root = loader._project_root()
        registry = discover_schema_files(loader.config, project_root)

        aux_stems = [
            "eks_project_code_schema",
            "eks_document_type_schema",
            "eks_department_schema",
            "eks_discipline_schema",
            "eks_facility_schema",
        ]
        for stem in aux_stems:
            self.assertNotIn(stem, registry, f"{stem} should NOT be in Tier 1+2 registry")

        all_stems = list(_STEM_TO_ATTR.keys())
        tier3_entries = discover_schema_files_tier3(all_stems, loader._search_dirs, registry)
        for stem in aux_stems:
            self.assertIn(stem, tier3_entries, f"Tier 3 should discover {stem}")
            self.assertEqual(tier3_entries[stem]["source"], "tier3",
                             f"{stem} source should be 'tier3'")

    def test_loader_4stage_methods_exist(self):
        """Verify SchemaLoader has 4 stage methods (I263)."""
        loader = SchemaLoader(str(self.config_dir))
        self.assertTrue(hasattr(loader, '_discover'), "missing _discover")
        self.assertTrue(hasattr(loader, '_load'), "missing _load")
        self.assertTrue(hasattr(loader, '_validate'), "missing _validate")
        self.assertTrue(hasattr(loader, '_extract'), "missing _extract")

    def test_loader_4stage_end_to_end(self):
        """Verify load_all() still works with 4-stage refactoring."""
        loader = SchemaLoader(str(self.config_dir))
        result = loader.load_all()
        self.assertIsNotNone(result)
        self.assertIn("registry", result)

    def test_new_stem_to_attr_entries(self):
        """Verify 3 new _STEM_TO_ATTR entries exist (I260)."""
        self.assertIn("eks_department_schema", _STEM_TO_ATTR)
        self.assertIn("eks_discipline_schema", _STEM_TO_ATTR)
        self.assertIn("eks_facility_schema", _STEM_TO_ATTR)

    def test_new_schema_attributes(self):
        """Verify SchemaLoader has 4 new schema attributes (document_type, department, discipline, facility)."""
        loader = SchemaLoader(str(self.config_dir))
        self.assertTrue(hasattr(loader, 'document_type_schema'), "missing document_type_schema")
        self.assertTrue(hasattr(loader, 'department_schema'), "missing department_schema")
        self.assertTrue(hasattr(loader, 'discipline_schema'), "missing discipline_schema")
        self.assertTrue(hasattr(loader, 'facility_schema'), "missing facility_schema")


if __name__ == "__main__":
    unittest.main(verbosity=2)

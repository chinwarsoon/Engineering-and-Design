"""
Tests for I300 (T1.263) — `ontology_triggers` alignment with Appendix B §B4.1.

Scope (verification-complete re-scope 2026-08-10, design review approved):
  1. eks_doc_config.json §ontology_triggers has exactly 7 rows (the 7 §B4.1 rules)
  2. lifecycle_stage → HAS_STAGE is the added 7th rule
  3. `column_name` PK remains 1:1 (document_number→SUPERSEDES and
     references_documents→REFERENCES_DOC map distinct keys)
  4. eks_ontology_config.json relationships includes HAS_STAGE (16 rows)
  5. SchemaLoader still resolves both configs (schema-level validity)
"""
import json
import unittest
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = _PROJECT_ROOT / "config" / "schemas"
if not CONFIG_DIR.exists():
    CONFIG_DIR = _PROJECT_ROOT / "config"

B4_RULES = {
    "document_type": "IS_A",
    "document_number": "SUPERSEDES",
    "asset_tags": "REFERENCES_ASSET",
    "originator_company": "PRODUCED_BY",
    "file_type": "HAS_FORMAT",
    "references_documents": "REFERENCES_DOC",
    "lifecycle_stage": "HAS_STAGE",
}


def _load(name):
    with open(CONFIG_DIR / name, encoding="utf-8") as fh:
        return json.load(fh)


class TestI300OntologyTrigger(unittest.TestCase):
    def test_doc_config_has_7_triggers(self):
        """T1.263 (I300)(1): ontology_triggers covers all 7 §B4.1 rules."""
        doc_config = _load("eks_doc_config.json")
        triggers = doc_config["ontology_triggers"]
        self.assertEqual(len(triggers), 7)
        for col, rel in B4_RULES.items():
            self.assertEqual(triggers.get(col), rel, f"missing/mismatch: {col} → {rel}")

    def test_lifecycle_stage_has_stage_trigger_present(self):
        """T1.263 (I300)(2): lifecycle_stage → HAS_STAGE is the added 7th rule."""
        triggers = _load("eks_doc_config.json")["ontology_triggers"]
        self.assertEqual(triggers["lifecycle_stage"], "HAS_STAGE")

    def test_column_name_pk_stays_1to1(self):
        """T1.263 (I300)(3): no duplicate column keys → column_name PK is 1:1."""
        triggers = _load("eks_doc_config.json")["ontology_triggers"]
        self.assertEqual(len(triggers), len(set(triggers.keys())))

    def test_ontology_config_has_stage_relationship(self):
        """T1.263 (I300)(4): HAS_STAGE now declared in ontology relationships (18 — I305 added REFERENCES_ASSET + HAS_FORMAT)."""
        ontology = _load("eks_ontology_config.json")
        rel_names = [r["name"] for r in ontology["relationships"]]
        self.assertIn("HAS_STAGE", rel_names)
        self.assertEqual(len(rel_names), 18)

    def test_schema_loader_resolves_both_configs(self):
        """T1.263 (I300)(5): SchemaLoader validates both configs end-to-end."""
        try:
            from eks.engine.core.schema_loader import SchemaLoader
            loader = SchemaLoader(config_dir=str(CONFIG_DIR))
            loaded = loader.load_all()
            self.assertTrue(loaded)
            # Loader-exposed attrs reflect the config additions.
            triggers = getattr(loader, "doc_config", {}).get("ontology_triggers", {})
            self.assertIn("lifecycle_stage", triggers)
            rel_names = [r.get("name") for r in getattr(loader, "ontology", {}).get("relationships", [])]
            self.assertIn("HAS_STAGE", rel_names)
        except Exception as e:  # pragma: no cover - env-dependent fallback
            self.fail(f"SchemaLoader resolution failed: {e}")


if __name__ == "__main__":
    unittest.main()

"""I284 (T1.232) — Type-aware schema-driven HealthScorer tests.

Validates that tier sets, tier weights, and cover source-quality scores are
derived from the schema/config (column_processing.scoring_tier +
applies_to_document_types + required; health_scoring.weight_tiers;
document_templates[].source_quality_score) rather than module-level hardcoded
frozensets. Key behaviours:

- Manual (MAN/OM) is NOT penalised for missing discipline/area (columns not
  claimed by the Manual class).
- Datasheet elevates embedded_sheet_count to tier1 critical → missing it
  penalises the health score.
- excluded columns (file_path, file_hash) never appear as missing and never
  score, even when required=true.
- required=false columns have weight 0 → missing does not penalise.
- Source quality reads document_templates[].source_quality_score, falling back
  to health_scoring.default_source_quality_scores.
"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from eks.engine.core.health_scorer import HealthScorer

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config" / "schemas"


class TestHealthScorerTyped(unittest.TestCase):
    """I284 — schema-driven type-aware health scoring."""

    @classmethod
    def setUpClass(cls):
        with open(CONFIG_DIR / "eks_doc_config.json", encoding="utf-8") as f:
            cls.doc_config = json.load(f)
        with open(CONFIG_DIR / "eks_document_type_schema.json", encoding="utf-8") as f:
            cls.carrier = json.load(f)

        cls.column_config = cls.doc_config["column_processing"]
        cls.weight_tiers = cls.doc_config["health_scoring"]["weight_tiers"]
        cls.default_source_scores = cls.doc_config["health_scoring"]["default_source_quality_scores"]
        cls.templates = cls.carrier["document_templates"]

        cls.scorer = HealthScorer(
            column_config=cls.column_config,
            weight_tiers=cls.weight_tiers,
            default_source_quality_scores=cls.default_source_scores,
            document_templates=cls.templates,
        )

    def _full_doc(self, class_id):
        """Build a document with every claimed, non-excluded column populated."""
        doc = {}
        for col, cfg in self.column_config.items():
            if cfg.get("scoring_tier") == "excluded":
                continue
            if class_id in cfg.get("applies_to_document_types", []):
                doc[col] = "x"
        return doc

    # -- 1. schema-driven: no hardcoded tier constants ---------------------

    def test_column_config_fully_scoped(self):
        """Every data column is explicitly claimed and tiered."""
        for col, cfg in self.column_config.items():
            self.assertIn("scoring_tier", cfg, f"{col} missing scoring_tier")
            self.assertIn("applies_to_document_types", cfg, f"{col} missing applies_to_document_types")
            self.assertIn("required", cfg, f"{col} missing required")
            self.assertIn(cfg["scoring_tier"],
                          ("tier1", "tier2", "tier3", "excluded"),
                          f"{col} invalid scoring_tier")

    def test_weight_tiers_from_schema(self):
        """Tier weights come from schema, not code."""
        self.assertEqual(self.scorer._weight_tiers, self.weight_tiers)

    # -- 2. Manual: discipline/area exemption ------------------------------

    def test_manual_not_penalised_for_discipline_area(self):
        """Manual has no discipline/area claimed → missing them does not hurt."""
        doc = self._full_doc("Manual")
        doc.pop("discipline", None)
        doc.pop("area", None)
        result = self.scorer.score(doc, cover_type="D",
                                   template_id="twrp_manual_d", class_id="Manual")
        self.assertNotIn("discipline", result["missing_columns"])
        self.assertNotIn("area", result["missing_columns"])

        # presence of discipline/area must not change the score (not claimed)
        doc2 = self._full_doc("Manual")
        r1 = self.scorer.score(doc, cover_type="D", template_id="twrp_manual_d", class_id="Manual")
        r2 = self.scorer.score(doc2, cover_type="D", template_id="twrp_manual_d", class_id="Manual")
        self.assertAlmostEqual(r1["health_score"], r2["health_score"], places=6)

    # -- 3. Datasheet: embedded_sheet_count elevation ----------------------

    def test_datasheet_embedded_sheet_count_penalises_when_missing(self):
        """Datasheet treats embedded_sheet_count as tier1 critical."""
        doc_missing = self._full_doc("Datasheet")
        doc_missing["embedded_sheet_count"] = ""
        doc_present = self._full_doc("Datasheet")
        doc_present["embedded_sheet_count"] = "5"

        r_miss = self.scorer.score(doc_missing, cover_type="E",
                                   template_id="twrp_datasheet_e", class_id="Datasheet")
        r_pres = self.scorer.score(doc_present, cover_type="E",
                                   template_id="twrp_datasheet_e", class_id="Datasheet")
        self.assertIn("embedded_sheet_count", r_miss["missing_columns"])
        self.assertLess(r_miss["health_score"], r_pres["health_score"])

    # -- 4. excluded columns never score -----------------------------------

    def test_excluded_columns_not_scored(self):
        """file_path/file_hash (excluded) never appear as missing or penalise."""
        doc = self._full_doc("Drawing")
        doc["file_path"] = ""
        doc["file_hash"] = ""
        result = self.scorer.score(doc, cover_type="A",
                                   template_id="twrp_drawing", class_id="Drawing")
        self.assertNotIn("file_path", result["missing_columns"])
        self.assertNotIn("file_hash", result["missing_columns"])

    # -- 5. required=false → weight 0 --------------------------------------

    def test_optional_column_not_penalised(self):
        """required=false column (language) missing does not penalise."""
        doc_missing = self._full_doc("Drawing")
        doc_missing["language"] = ""
        doc_present = self._full_doc("Drawing")
        doc_present["language"] = "en"

        r_miss = self.scorer.score(doc_missing, cover_type="A",
                                   template_id="twrp_drawing", class_id="Drawing")
        r_pres = self.scorer.score(doc_present, cover_type="A",
                                   template_id="twrp_drawing", class_id="Drawing")
        self.assertAlmostEqual(r_miss["health_score"], r_pres["health_score"], places=6)

    # -- 6. template-scoped source quality + schema fallback ---------------

    def test_source_quality_reads_template_map(self):
        """Source quality uses document_templates[].source_quality_score."""
        result = self.scorer.score(self._full_doc("Manual"), cover_type="D",
                                   template_id="twrp_manual_d", class_id="Manual")
        source = result["dimensions"]["source_quality"]
        # twrp_manual_d D -> 1.0 (template map) - bonus may apply
        self.assertEqual(source["source"], "template")
        self.assertAlmostEqual(source["score"], 1.0, places=6)

    def test_source_quality_fallback_to_schema_default(self):
        """No template_id → health_scoring.default_source_quality_scores."""
        doc = self._full_doc("Manual")
        result = self.scorer.score(doc, cover_type="D", template_id=None, class_id="Manual")
        source = result["dimensions"]["source_quality"]
        self.assertEqual(source["source"], "default")
        # default map D -> 0.9; bonus may add 0.05 if embedded_creator_app present
        base = self.default_source_scores["D"]
        self.assertGreaterEqual(source["score"], base)

    # -- 7. config-less fallback still works -------------------------------

    def test_configless_fallback(self):
        """HealthScorer without column_config uses legacy fallback sets."""
        scorer = HealthScorer()
        doc = {
            "project_number": "1", "discipline": "A", "document_type": "X",
            "document_number": "1", "revision": "A", "asset_tags": "[]",
        }
        result = scorer.score(doc)
        self.assertIn("health_score", result)
        self.assertGreater(result["health_score"], 0.0)


if __name__ == "__main__":
    unittest.main()

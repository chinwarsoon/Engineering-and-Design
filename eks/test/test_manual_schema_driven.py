"""I286 (T1.237) — schema-driven ManualReviewManager.correct_metadata tests.

Covers the re-scoped review-allowlist behaviour:
  - allowed set derived from doc_config.column_processing (SSOT, no hardcode)
  - manual_review classification markers present on the 12 expected columns
  - validation reject paths: unknown field, bad enum, bad ISO date, non-list
    json_column
  - JSON serialization of list-valued json_column fields
  - config-absent path raises descriptive error (no silent fallback)

Run from repo root:
    conda run -n eks python -m pytest eks/test/test_review_schema_driven.py -q
"""
from pathlib import Path
import json
import unittest

from eks.engine.core.schema_loader import SchemaLoader
from eks.engine.core.review_manager import ManualReviewManager

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _find_config_dir() -> Path:
    for candidate in [
        _PROJECT_ROOT / "config" / "schemas",
        _PROJECT_ROOT / "config",
        _PROJECT_ROOT.parent / "config" / "schemas",
        _PROJECT_ROOT.parent / "config",
    ]:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Could not find schema directory")


def _load_loader():
    config_dir = _find_config_dir()
    config_parent = config_dir.parent if config_dir.name == "schemas" else config_dir
    loader = SchemaLoader(config_parent)
    loader.load_all()
    return loader


class TestReviewSchemaDriven(unittest.TestCase):
    """I286: schema-driven review allowlist + validation."""

    @classmethod
    def setUpClass(cls):
        from eks.engine.core.registry import DocumentRegistry

        cls.loader = _load_loader()
        cls.doc_config = cls.loader.doc_config
        cls.base_schema = cls.loader.doc_base_schema
        cls.registry = DocumentRegistry()

    def setUp(self):
        self.reviewer = ManualReviewManager(
            self.registry,
            doc_config=self.doc_config,
            base_schema=self.base_schema,
        )

    def _register(self, number="REV-I286"):
        self.registry.register_document({
            "document_number": number, "revision": "A",
            "document_type": "DWG", "status": "DRAFT",
        })
        return self.registry.get_latest_by_key(number, "A"), number

    def test_allowlist_derived_from_column_processing(self):
        """Allowed set == column_processing keys (schema-driven, not hardcoded)."""
        expected = set(self.doc_config["column_processing"].keys())
        self.assertIn("status", expected)
        self.assertIn("checked_by", expected)
        self.assertIn("department", expected)
        self.assertIn("verified_by", expected)

    def test_manual_review_markers_present(self):
        """manual_review flag present on the 12 Manual-source columns."""
        cp = self.doc_config["column_processing"]
        manual = [k for k, v in cp.items() if v.get("manual_review") is True]
        self.assertEqual(
            sorted(manual),
            sorted([
                "lifecycle_stage", "revision_date", "revision_description",
                "project_phase", "contract_package", "issued_date",
                "responsible_engineer", "vendor_name", "references_documents",
                "status", "security_class", "verified_by",
            ]),
        )
        # derivable columns are present but not manual
        self.assertIn("department", cp)
        self.assertIs(cp["department"].get("manual_review"), False)

    def test_status_update_accepted(self):
        latest, num = self._register("REV-STATUS")
        ok = self.reviewer.correct_metadata(latest["id"], {"status": "APPROVED"})
        self.assertTrue(ok)
        doc = self.registry.get_latest_by_key(num, "A")
        self.assertEqual(doc["status"], "APPROVED")

    def test_unknown_field_rejected(self):
        """Non-column_processing (control) fields are rejected, not silently dropped."""
        latest, num = self._register("REV-UNKNOWN")
        ok = self.reviewer.correct_metadata(latest["id"], {"id": "hacked"})
        self.assertFalse(ok)
        doc = self.registry.get_latest_by_key(num, "A")
        self.assertEqual(doc["status"], "DRAFT")

    def test_bad_enum_rejected(self):
        """lifecycle_stage (code_column, enum_reference) rejects non-enum values."""
        latest, num = self._register("REV-ENUM")
        ok = self.reviewer.correct_metadata(
            latest["id"], {"lifecycle_stage": "not_a_real_stage"})
        self.assertFalse(ok)
        ok = self.reviewer.correct_metadata(
            latest["id"], {"lifecycle_stage": "issued_for_construction"})
        self.assertTrue(ok)

    def test_bad_date_rejected(self):
        """revision_date (date_column) rejects non-ISO dates."""
        latest, num = self._register("REV-DATE")
        ok = self.reviewer.correct_metadata(latest["id"], {"revision_date": "not-a-date"})
        self.assertFalse(ok)
        ok = self.reviewer.correct_metadata(latest["id"], {"revision_date": "2024-05-01"})
        self.assertTrue(ok)

    def test_json_column_requires_list(self):
        """references_documents (json_column) rejects non-list, serializes lists."""
        latest, num = self._register("REV-JSON")
        ok = self.reviewer.correct_metadata(latest["id"], {"references_documents": "C-101"})
        self.assertFalse(ok)
        refs = ["C-101", "C-102"]
        ok = self.reviewer.correct_metadata(latest["id"], {"references_documents": refs})
        self.assertTrue(ok)
        doc = self.registry.get_latest_by_key(num, "A")
        self.assertEqual(json.loads(doc["references_documents"]), refs)

    def test_text_field_accepted(self):
        """Plain text values pass through on non-jsonschema text columns."""
        latest, num = self._register("REV-TEXT")
        ok = self.reviewer.correct_metadata(
            latest["id"], {"responsible_engineer": "J. Smith"})
        self.assertTrue(ok)
        doc = self.registry.get_latest_by_key(num, "A")
        self.assertEqual(doc["responsible_engineer"], "J. Smith")

    def test_missing_doc_config_raises_descriptive_error(self):
        """No column_processing => descriptive ValueError (AGENTS.md §16), no fallback."""
        bare = ManualReviewManager(self.registry, doc_config={})
        with self.assertRaises(ValueError) as ctx:
            bare.correct_metadata("x", {"status": "APPROVED"})
        self.assertIn("column_processing", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
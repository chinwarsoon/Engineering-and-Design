"""I280 (T1.222) — B3.2 sub-object schema + carrier population tests.

Validates the I280 implementation (T1.218–T1.220):
- eks_doc_base_schema.json v1.16.0 carries the B3.2 sub-object defs:
  structural_profile_def, extraction_profile_ref, retrieval_profile_ref,
  validation_profile_ref, plus Phase 3 stubs (document_semantics_def,
  ai_profile_def, knowledge_relationships_def).
- The defs attach as OPTIONAL fields to document_class_def (class-level
  defaults) and document_type_def (type-level overrides) — absent = defaults.
- The carrier (eks_document_type_schema.json v2.2.0) populates
  structural_profile on all 8 classes and 28 types; class-level
  extraction_profile_ref resolves to eks_processing_config.json
  extraction_profiles ids (I281).
- SchemaLoader.structural_profile_for(type_id, class_id) resolves type-level
  override over class-level default; the flat document_type_registry
  projection carries structural_profile.
- §24 cross-source audit: base defs ↔ carrier population ↔ SchemaLoader
  helper ↔ doc setup schema registry projection agree.
"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from eks.engine.core.schema_loader import SchemaLoader

ROOT = Path(__file__).resolve().parent.parent

STRUCTURAL_PROFILE_FIELDS = [
    "cover_page", "revision_table", "multi_sheet", "drawing_based",
    "section_based", "contains_callouts", "contains_symbols",
    "title_block", "legend", "grid", "signature_block",
]

PRESENCE_ENUM = ("required", "optional", "absent")


class TestI280B32Schema(unittest.TestCase):
    """I280 T1.218 — B3.2 sub-object defs in eks_doc_base_schema.json."""

    @classmethod
    def setUpClass(cls):
        cls.config_dir = ROOT / "config"
        cls.loader = SchemaLoader(str(cls.config_dir))
        cls.loader.load_all()
        with open(cls.config_dir / "schemas" / "eks_doc_base_schema.json", encoding="utf-8") as f:
            cls.base = json.load(f)
        with open(cls.config_dir / "schemas" / "eks_document_type_schema.json", encoding="utf-8") as f:
            cls.carrier = json.load(f)
        with open(cls.config_dir / "schemas" / "eks_processing_config.json", encoding="utf-8") as f:
            cls.processing_config = json.load(f)
        with open(cls.config_dir / "schemas" / "eks_doc_setup_schema.json", encoding="utf-8") as f:
            cls.doc_setup = json.load(f)

    # -- 1. Sub-object defs present in base schema -------------------------

    def test_sub_object_defs_present(self):
        """All B3.2 sub-object defs exist in the base schema."""
        defs = self.base["definitions"]
        for name in ("structural_profile_def", "extraction_profile_ref",
                     "retrieval_profile_ref", "validation_profile_ref",
                     "document_semantics_def", "ai_profile_def",
                     "knowledge_relationships_def"):
            self.assertIn(name, defs, f"missing {name}")

    def test_structural_profile_def_fields(self):
        """structural_profile_def declares all 11 B3.2 fields."""
        props = self.base["definitions"]["structural_profile_def"]["properties"]
        self.assertEqual(set(props.keys()), set(STRUCTURAL_PROFILE_FIELDS))
        for presence_field in ("cover_page", "revision_table", "title_block",
                               "legend", "grid", "signature_block"):
            self.assertEqual(props[presence_field]["type"], "string")
            self.assertEqual(tuple(props[presence_field]["enum"]), PRESENCE_ENUM,
                             f"{presence_field} must use required/optional/absent enum")
        for bool_field in ("multi_sheet", "drawing_based", "section_based",
                           "contains_callouts", "contains_symbols"):
            self.assertEqual(props[bool_field]["type"], "boolean", f"{bool_field} must be boolean")

    def test_profile_refs_are_strings(self):
        """extraction/retrieval/validation profile refs are plain string defs."""
        for name in ("extraction_profile_ref", "retrieval_profile_ref",
                     "validation_profile_ref"):
            self.assertEqual(self.base["definitions"][name]["type"], "string", name)

    def test_class_def_carries_optional_sub_objects(self):
        """document_class_def exposes the B3.2 sub-objects as optional fields."""
        props = self.base["definitions"]["document_class_def"]["properties"]
        for key in ("structural_profile", "extraction_profile_ref",
                    "retrieval_profile_ref", "validation_profile_ref",
                    "document_semantics", "ai_profile", "knowledge_relationships"):
            self.assertIn(key, props, f"document_class_def missing {key}")
        # required stays minimal — sub-objects optional
        self.assertNotIn("structural_profile",
                         self.base["definitions"]["document_class_def"]["required"])

    def test_type_def_carries_optional_sub_objects(self):
        """document_type_def exposes the B3.2 sub-objects as optional overrides."""
        props = self.base["definitions"]["document_type_def"]["properties"]
        for key in ("structural_profile", "extraction_profile_ref",
                    "retrieval_profile_ref", "validation_profile_ref"):
            self.assertIn(key, props, f"document_type_def missing {key}")
        self.assertNotIn("structural_profile",
                         self.base["definitions"]["document_type_def"]["required"])

    def test_registry_entry_projection_carries_structural_profile(self):
        """The flat document_type_registry items def (doc setup) accepts structural_profile."""
        items = self.doc_setup["properties"]["document_type_registry"]["items"]
        self.assertEqual(items, {"$ref": "eks_doc_base_schema.json#/definitions/document_type_entry_def"})
        props = self.base["definitions"]["document_type_entry_def"]["properties"]
        self.assertIn("structural_profile", props)


class TestI280B32Carrier(unittest.TestCase):
    """I280 T1.219 — structural_profile populated on classes + types."""

    @classmethod
    def setUpClass(cls):
        cls.config_dir = ROOT / "config"
        with open(cls.config_dir / "schemas" / "eks_document_type_schema.json", encoding="utf-8") as f:
            cls.carrier = json.load(f)
        with open(cls.config_dir / "schemas" / "eks_processing_config.json", encoding="utf-8") as f:
            cls.processing_config = json.load(f)

    def test_all_8_classes_have_structural_profile(self):
        """Every document class carries a structural_profile."""
        for c in self.carrier["document_classes"]:
            self.assertIsInstance(c.get("structural_profile"), dict,
                                  f"{c['class_id']} missing structural_profile")
            self.assertEqual(set(c["structural_profile"].keys()), set(STRUCTURAL_PROFILE_FIELDS),
                             f"{c['class_id']} structural_profile incomplete")

    def test_all_28_types_have_structural_profile(self):
        """Every document type carries a structural_profile."""
        self.assertEqual(len(self.carrier["document_types"]), 28)
        for t in self.carrier["document_types"]:
            self.assertIsInstance(t.get("structural_profile"), dict,
                                  f"{t['type_id']} missing structural_profile")
            self.assertEqual(set(t["structural_profile"].keys()), set(STRUCTURAL_PROFILE_FIELDS),
                             f"{t['type_id']} structural_profile incomplete")

    def test_class_extraction_profile_ref_resolves(self):
        """Every class extraction_profile_ref names an existing extraction profile (I281)."""
        profiles = self.processing_config["extraction_profiles"]
        for c in self.carrier["document_classes"]:
            ref = c.get("extraction_profile_ref")
            self.assertIn(ref, profiles, f"{c['class_id']} extraction_profile_ref '{ref}' unresolved")

    def test_drawing_class_profiles_are_type_appropriate(self):
        """Drawing class/types are drawing_based + symbol-bearing; text classes are not."""
        drawing = next(c for c in self.carrier["document_classes"] if c["class_id"] == "Drawing")
        spec = next(c for c in self.carrier["document_classes"] if c["class_id"] == "Specification")
        self.assertTrue(drawing["structural_profile"]["drawing_based"])
        self.assertTrue(drawing["structural_profile"]["multi_sheet"])
        self.assertTrue(drawing["structural_profile"]["contains_symbols"])
        self.assertFalse(spec["structural_profile"]["drawing_based"])
        self.assertTrue(spec["structural_profile"]["section_based"])

    def test_type_overrides_and_inheritance(self):
        """PID_DRAWING overrides legend=required; ISOMETRIC stays class-level defaults."""
        pid = next(t for t in self.carrier["document_types"] if t["type_id"] == "PID_DRAWING")
        self.assertEqual(pid["structural_profile"]["legend"], "required")
        self.assertTrue(pid["structural_profile"]["contains_symbols"])
        isometric = next(t for t in self.carrier["document_types"] if t["type_id"] == "ISOMETRIC")
        # ISOMETRIC is single-sheet, drawing-based — class inherited values
        self.assertFalse(isometric["structural_profile"]["multi_sheet"])
        self.assertTrue(isometric["structural_profile"]["drawing_based"])

    def test_carrier_version_bumped(self):
        """Carrier version bumped to 2.3.0 for the I283 expected_elements extension."""
        self.assertEqual(self.carrier["version"], "2.3.0")


class TestI280B32Helper(unittest.TestCase):
    """I280 T1.220 — SchemaLoader.structural_profile_for() + projection."""

    @classmethod
    def setUpClass(cls):
        cls.config_dir = ROOT / "config"
        cls.loader = SchemaLoader(str(cls.config_dir))
        cls.loader.load_all()

    def test_type_level_override_wins(self):
        """Type-level structural_profile overrides the class-level default."""
        pid = self.loader.structural_profile_for("PID_DRAWING", "Drawing")
        self.assertEqual(pid["legend"], "required")
        self.assertTrue(pid["contains_symbols"])

    def test_class_level_fallback(self):
        """A type without an explicit profile inherits its class profile."""
        prof = self.loader.structural_profile_for("ISOMETRIC", "Drawing")
        self.assertTrue(prof["drawing_based"])
        self.assertTrue(prof["title_block"] == "required")

    def test_class_only_lookup(self):
        """Passing only class_id returns the class-level profile."""
        prof = self.loader.structural_profile_for("", "Register")
        self.assertIsInstance(prof, dict)
        self.assertFalse(prof["drawing_based"])
        self.assertEqual(prof["cover_page"], "optional")

    def test_unknown_returns_empty(self):
        """Unknown type/class returns {} so callers fall back to defaults."""
        self.assertEqual(self.loader.structural_profile_for("NOPE", "NOPE2"), {})

    def test_all_types_resolve_via_helper(self):
        """Helper resolves a profile for every carrier type (via type or class)."""
        for t in self.loader.document_type_schema["document_types"]:
            prof = self.loader.structural_profile_for(t["type_id"], t.get("class_id", ""))
            self.assertTrue(prof, f"{t['type_id']} resolved to empty profile")

    def test_projection_carries_structural_profile(self):
        """Flat document_type_registry entries carry structural_profile."""
        dwg = next(e for e in self.loader.doc_config["document_type_registry"]
                   if e["code"] == "DWG")
        self.assertEqual(dwg["structural_profile"]["title_block"], "required")
        self.assertTrue(dwg["structural_profile"]["drawing_based"])

    def test_cross_source_audit(self):
        """§24: base defs ↔ carrier population ↔ helper projection agree."""
        carrier_classes = {c["class_id"] for c in self.loader.document_type_schema["document_classes"]}
        carrier_types = {t["type_id"] for t in self.loader.document_type_schema["document_types"]}
        # every projected registry entry's structural_profile is resolvable
        for e in self.loader.doc_config["document_type_registry"]:
            prof = e.get("structural_profile", {})
            self.assertTrue(prof, f"{e['code']} projection missing structural_profile")
            self.assertEqual(set(prof.keys()), set(STRUCTURAL_PROFILE_FIELDS))
        # every carrier type resolves through the helper
        for t in carrier_types:
            self.assertTrue(self.loader.structural_profile_for(t, ""))
        self.assertTrue(carrier_classes.issuperset(
            {"Drawing", "Specification", "Datasheet", "Calculation",
             "Manual", "Register", "Report", "Procedure"}))


if __name__ == "__main__":
    unittest.main()

"""I279/I282 (T1.217/T1.228-229) — Document-type SSOT consolidation tests.

Validates the five-section ``eks_document_type_schema.json`` v2.2.0 carrier is
the single runtime source: document_classes + document_types + document_family
+ per-project bindings + template registry replace the former flat
``document_type_registry`` / ``element_expectations`` arrays in
``eks_doc_config.json`` and the removed ``document_type_concepts`` layer.
Covers the §24 seven-source cross-source audit and the enum drift-guard
(carrier authoritative; base-schema enum a derived mirror).
"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from eks.engine.core.schema_loader import SchemaLoader

ROOT = Path(__file__).resolve().parent.parent


class TestDocumentTypeSSOT(unittest.TestCase):
    """I279/I282 T1.217 — carrier structure + §24 cross-source audit."""

    @classmethod
    def setUpClass(cls):
        cls.config_dir = ROOT / "config"
        if not (cls.config_dir / "schemas").exists():
            cls.config_dir = ROOT / "config"
        cls.loader = SchemaLoader(str(cls.config_dir))
        cls.loader.load_all()
        with open(cls.config_dir / "schemas" / "eks_document_type_schema.json", encoding="utf-8") as f:
            cls.carrier = json.load(f)
        with open(cls.config_dir / "schemas" / "eks_doc_base_schema.json", encoding="utf-8") as f:
            cls.base = json.load(f)
        with open(cls.config_dir / "schemas" / "eks_doc_config.json", encoding="utf-8") as f:
            cls.doc_config = json.load(f)
        with open(cls.config_dir / "schemas" / "eks_processing_config.json", encoding="utf-8") as f:
            cls.processing_config = json.load(f)

    # -- 1. No drift: 15 former registry codes covered ---------------------

    def test_former_15_codes_all_bound(self):
        """Every former document_type_registry code appears as a local_code binding."""
        former_codes = {
            "CAD", "DWG", "PI-PID", "SPC", "DS", "MAN", "OM", "RPT",
            "DR", "SP", "CL", "BQ", "VI", "M3", "QA",
        }
        bound = {b["local_code"] for bl in self.carrier["project_document_types"].values() for b in bl}
        self.assertTrue(former_codes.issubset(bound),
                        f"Carrier missing former codes: {sorted(former_codes - bound)}")

    def test_each_code_bound_to_class_and_template(self):
        """Every binding references a defined class_id and template_id."""
        classes = {c["class_id"] for c in self.carrier["document_classes"]}
        templates = set(self.carrier["document_templates"].keys())
        for bl in self.carrier["project_document_types"].values():
            for b in bl:
                self.assertIn(b["class_id"], classes, f"{b['local_code']} bad class_id")
                self.assertIn(b["template"], templates, f"{b['local_code']} bad template")

    # -- 1b. Class/type/family registry integrity --------------------------

    def test_classes_types_families_present(self):
        """Carrier carries document_classes, document_types, document_family."""
        self.assertIn("document_classes", self.carrier)
        self.assertIn("document_types", self.carrier)
        self.assertIn("document_family", self.carrier)
        self.assertTrue(len(self.carrier["document_classes"]) >= 8,
                        "expected at least the 8 core document classes")
        self.assertTrue(len(self.carrier["document_types"]) >= 28,
                        "expected the 28+ B3.1 document types")
        self.assertEqual(len(self.carrier["document_family"]), 4)

    def test_type_class_and_family_references_resolve(self):
        """Every type's class_id exists in classes; family_id exists or is null."""
        classes = {c["class_id"] for c in self.carrier["document_classes"]}
        families = {f["family_id"] for f in self.carrier["document_family"]}
        for t in self.carrier["document_types"]:
            self.assertIn(t["class_id"], classes, f"{t['type_id']} bad class_id")
            fid = t.get("family_id")
            if fid is not None:
                self.assertIn(fid, families, f"{t['type_id']} bad family_id")

    def test_base_schema_is_shape_only(self):
        """Base defs carry no value enums for class/type/family (SSOT §9/§16)."""
        for def_name, required in (("document_class_def", ["class_id"]),
                                   ("document_type_def", ["type_id"]),
                                   ("document_family_def", ["family_id"])):
            d = self.base["definitions"][def_name]
            self.assertNotIn("enum", d, f"{def_name} must not carry a value enum")
            self.assertIn("properties", d)
            self.assertIn("required", d)
            for prop in required:
                self.assertIn(prop, d["required"], f"{def_name} requires {prop}")

    def test_document_type_concepts_removed(self):
        """The former concept layer is removed from the carrier (I282 D4)."""
        self.assertNotIn("document_type_concepts", self.carrier)

    # -- 2. Project binding resolution -------------------------------------

    def test_class_drawing_multi_code_binding(self):
        """131101 DWG and 131242 DR both bind class Drawing (I282 example)."""
        proj = self.carrier["project_document_types"]
        codes = {b["local_code"]: b["class_id"] for bl in proj.values() for b in bl}
        self.assertEqual(codes["DWG"], "Drawing")
        self.assertEqual(codes["DR"], "Drawing")

    def test_project_local_code_distinct_templates_profiles(self):
        """Differing bindings may carry differing templates/profiles."""
        proj = self.carrier["project_document_types"]
        by_code = {b["local_code"]: b for bl in proj.values() for b in bl}
        dwg = by_code["DWG"]
        dr = by_code["DR"]
        self.assertIn(dwg["template"], self.carrier["document_templates"])
        self.assertIn(dr["template"], self.carrier["document_templates"])

    # -- 3. format_category agreement --------------------------------------

    def test_format_category_agreement(self):
        """Binding format_category matches file_type_registry per expected type."""
        file_types = {e["extension"]: e.get("format_category")
                      for e in self.doc_config["file_type_registry"]}
        self.assertEqual(file_types.get("pdf"), "print")
        self.assertEqual(file_types.get("dwg"), "native")
        for bl in self.carrier["project_document_types"].values():
            for b in bl:
                self.assertIn(b["format_category"], ("native", "print"),
                              f"{b['local_code']} format_category invalid")

    # -- 4. document_metadata_def stores project-local code ----------------

    def test_metadata_doc_type_refs_enum(self):
        """document_metadata_def.document_type $refs document_type_code enum."""
        md = self.base["definitions"]["document_metadata_def"]
        self.assertIn("document_type", md["properties"])
        self.assertEqual(md["properties"]["document_type"]["$ref"], "#/definitions/document_type_code")

    def test_enum_is_derived_mirror(self):
        """document_type_code enum == union of all local_codes (drift-guard)."""
        enum = set(self.base["definitions"]["document_type_code"]["enum"])
        local = {b["local_code"] for bl in self.carrier["project_document_types"].values() for b in bl}
        self.assertEqual(enum, local,
                         f"enum drift: base enum {sorted(enum)} != carrier local codes {sorted(local)}")

    # -- 5. Template registry == former element_expectations ----------------

    def test_template_registry_absorbs_element_expectations(self):
        """document_templates cover all 15 codes via binding template refs."""
        bound_templates = {b["template"] for bl in self.carrier["project_document_types"].values() for b in bl}
        self.assertTrue(bound_templates.issubset(set(self.carrier["document_templates"].keys())))

    def test_template_cover_types_valid(self):
        """Template cover_type ∈ {A,B,C,D,E}; expected_elements valid.

        I283 (T1.230): valid element set extended 8→11 (title_block/grid/signature_block).
        """
        valid_elements = {"cover_page", "revision_table", "section", "table", "image", "link", "legend", "note",
                          "title_block", "grid", "signature_block"}
        for tid, tpl in self.carrier["document_templates"].items():
            self.assertIn(tpl["cover_type"], ("A", "B", "C", "D", "E"), f"{tid} cover_type")
            for el in tpl["expected_elements"]:
                self.assertIn(el, valid_elements, f"{tid} element {el}")

    # -- 6. No dead duplicate: config no longer commits the arrays ----------

    def test_config_does_not_commit_registry_arrays(self):
        """eks_doc_config.json must not carry document_type_registry / element_expectations."""
        self.assertNotIn("document_type_registry", self.doc_config)
        self.assertNotIn("element_expectations", self.doc_config)
        self.assertIn("document_type_schema_ref", self.doc_config)

    def test_loader_projects_carrier_into_doc_config(self):
        """SchemaLoader derives flat registry + templates from the carrier at runtime."""
        l = self.loader
        self.assertEqual(len(l.doc_config["document_type_registry"]), 15)
        self.assertIn("twrp_drawing", l.doc_config["document_templates"])
        self.assertEqual(
            l.doc_config["document_type_schema_ref"],
            "https://eks.engineering/schemas/eks_document_type_schema.json",
        )

    def test_loader_class_helpers(self):
        """Class-based helpers resolve documents by class/family and ancestry."""
        l = self.loader
        self.assertIn("PID_DRAWING", l.get_documents_by_class("Drawing"))
        self.assertIn("PID_DRAWING", l.get_documents_by_family("Process Drawing"))
        self.assertNotIn("SPC", l.get_documents_by_family("Process Drawing"))
        self.assertEqual(l.get_class_ancestry("Drawing"), ["Drawing"])
        self.assertEqual(l.get_class_ancestry("Specification"), ["Specification"])
        with self.assertRaises(ValueError):
            l.get_class_ancestry("NOPE")

    def test_loader_flat_registry_carries_class_id(self):
        """Flat projection entries carry class_id (no concept_id)."""
        entry = next(e for e in self.loader.doc_config["document_type_registry"]
                     if e["code"] == "DWG")
        self.assertEqual(entry["class_id"], "Drawing")
        self.assertNotIn("concept_id", entry)

    def test_file_type_registry_format_category(self):
        """file_type_registry entries carry format_category (native/print)."""
        for e in self.doc_config["file_type_registry"]:
            self.assertIn(e["format_category"], ("native", "print"), f"{e['extension']} missing format_category")

    def test_native_parsing_profiles_present(self):
        """GAP-N4: native reader profiles exist for declared native file types.

        I281 (T1.224): extraction profiles live in eks_processing_config.json
        (extraction_profiles), not doc_config parsing_profiles.
        """
        profiles = self.processing_config["extraction_profiles"]
        for pid in ("technip_dwg", "technip_dgn", "technip_xlsx"):
            self.assertIn(pid, profiles, f"missing native profile {pid}")

    def test_cross_source_audit_seven_sources(self):
        """§24: classes / types / bindings / templates / file_type_registry / processing profiles / column_processing / enum agree."""
        # classes ↔ bindings (via class_id)
        classes = {c["class_id"] for c in self.carrier["document_classes"]}
        bound_classes = {b["class_id"] for bl in self.carrier["project_document_types"].values() for b in bl}
        self.assertTrue(bound_classes.issubset(classes))
        # types ↔ classes (every type class_id resolves; bindings map to classes)
        for t in self.carrier["document_types"]:
            self.assertIn(t["class_id"], classes, f"{t['type_id']} bad class_id")
        # templates ↔ bindings
        templates = set(self.carrier["document_templates"])
        bound_templates = {b["template"] for bl in self.carrier["project_document_types"].values() for b in bl}
        self.assertTrue(bound_templates.issubset(templates))
        # file_type_registry extensions cover all expected_file_types
        known_exts = {e["extension"] for e in self.doc_config["file_type_registry"]}
        for bl in self.carrier["project_document_types"].values():
            for b in bl:
                for ext in b["expected_file_types"]:
                    self.assertIn(ext, known_exts, f"{b['local_code']} expects unknown ext {ext}")
        # I281: extraction_profiles referenced by bindings exist (processing config SSOT)
        profiles = set(self.processing_config["extraction_profiles"])
        for bl in self.carrier["project_document_types"].values():
            for b in bl:
                if b.get("default_parsing_profile"):
                    self.assertIn(b["default_parsing_profile"], profiles,
                                  f"{b['local_code']} missing profile {b['default_parsing_profile']}")
        # column_processing applies_to_document_types resolve against classes
        for col in self.doc_config["column_processing"].values():
            for ref in col.get("applies_to_document_types", []):
                self.assertIn(ref, classes, f"column_processing refs unknown class {ref}")
        # enum == union of local_codes (drift-guard already asserted above)
        enum = set(self.base["definitions"]["document_type_code"]["enum"])
        local = {b["local_code"] for bl in self.carrier["project_document_types"].values() for b in bl}
        self.assertEqual(enum, local)


if __name__ == "__main__":
    unittest.main(verbosity=2)

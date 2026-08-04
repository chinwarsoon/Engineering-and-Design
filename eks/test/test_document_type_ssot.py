"""I279 (T1.217) — Document-type SSOT consolidation tests.

Validates the three-section ``eks_document_type_schema.json`` v2.0.0 carrier is
the single runtime source: concepts + per-project bindings + template registry
replace the former flat ``document_type_registry`` / ``element_expectations``
arrays in ``eks_doc_config.json``. Covers the §24 seven-source cross-source
audit and the enum drift-guard (carrier authoritative; base-schema enum a
derived mirror).
"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from eks.engine.core.schema_loader import SchemaLoader

ROOT = Path(__file__).resolve().parent.parent


class TestDocumentTypeSSOT(unittest.TestCase):
    """I279 T1.217 — carrier structure + §24 cross-source audit."""

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

    def test_each_code_bound_to_concept_and_template(self):
        """Every binding references a defined concept_id and template_id."""
        concepts = {c["concept_id"] for c in self.carrier["document_type_concepts"]}
        templates = set(self.carrier["document_templates"].keys())
        for bl in self.carrier["project_document_types"].values():
            for b in bl:
                self.assertIn(b["concept_id"], concepts, f"{b['local_code']} bad concept")
                self.assertIn(b["template"], templates, f"{b['local_code']} bad template")

    # -- 2. Project binding resolution -------------------------------------

    def test_concept_drawing_multi_code_binding(self):
        """131101 DWG and 131242 DR both bind concept DRAWING (I279 example)."""
        proj = self.carrier["project_document_types"]
        codes = {b["local_code"]: b["concept_id"] for bl in proj.values() for b in bl}
        self.assertEqual(codes["DWG"], "DRAWING")
        self.assertEqual(codes["DR"], "DRAWING")

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
        """Template cover_type ∈ {A,B,C,D,E}; expected_elements valid."""
        valid_elements = {"cover_page", "revision_table", "section", "table", "image", "link", "legend", "note"}
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

    def test_file_type_registry_format_category(self):
        """file_type_registry entries carry format_category (native/print)."""
        for e in self.doc_config["file_type_registry"]:
            self.assertIn(e["format_category"], ("native", "print"), f"{e['extension']} missing format_category")

    def test_native_parsing_profiles_present(self):
        """GAP-N4: native reader profiles exist for declared native file types."""
        profiles = self.doc_config["parsing_profiles"]
        for pid in ("technip_dwg", "technip_dgn", "technip_xlsx"):
            self.assertIn(pid, profiles, f"missing native profile {pid}")

    def test_cross_source_audit_seven_sources(self):
        """§24: concepts / bindings / templates / file_type_registry / parsing_profiles / column_processing / enum agree."""
        # concepts ↔ bindings
        concepts = {c["concept_id"] for c in self.carrier["document_type_concepts"]}
        bound_concepts = {b["concept_id"] for bl in self.carrier["project_document_types"].values() for b in bl}
        self.assertTrue(bound_concepts.issubset(concepts))
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
        # parsing_profiles referenced by bindings exist
        profiles = set(self.doc_config["parsing_profiles"])
        for bl in self.carrier["project_document_types"].values():
            for b in bl:
                if b.get("default_parsing_profile"):
                    self.assertIn(b["default_parsing_profile"], profiles,
                                  f"{b['local_code']} missing profile {b['default_parsing_profile']}")
        # enum == union of local_codes (drift-guard already asserted above)
        enum = set(self.base["definitions"]["document_type_code"]["enum"])
        local = {b["local_code"] for bl in self.carrier["project_document_types"].values() for b in bl}
        self.assertEqual(enum, local)


if __name__ == "__main__":
    unittest.main(verbosity=2)

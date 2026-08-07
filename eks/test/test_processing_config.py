"""I281 (T1.225) — Processing Profile Registry formalisation tests.

Validates the one-time migration (Q1): processing profile VALUES moved from
eks_doc_config.json#/parsing_profiles into eks_processing_config.json#/extraction_profiles
(superseding the removed doc-base parsing_profile_def / doc-setup parsing_profiles
property / doc-config parsing_profiles section). Covers:
- generic processing_profile_registry_def accepts all 11 profile_type values (Q3)
- 10 deferred sections present and empty in eks_processing_config.json
- legacy parsing_profiles / parsing_profile_def ABSENT (grep-absent)
- SchemaLoader _validate_processing_config() validates the config chain end-to-end
- full consumer repoint (column_processor / parser_router / project_definition read
  eks_processing_config extraction_profiles)
- Phase 1 complete per-document profile establishment (Q5)
- PDEF unused-profile warnings drop 4→1 (only technip_docx unreferenced)
"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from eks.engine.core.schema_loader import SchemaLoader
from eks.engine.core.project_definition import ProjectDefinitionResolver
from eks.engine.parsers.parser_router import ParserRouter

ROOT = Path(__file__).resolve().parent.parent

PROFILE_TYPES = [
    "extraction", "chunking", "embedding", "asset", "ontology", "retrieval",
    "prompt", "validation", "indexing", "ai_reasoning", "graph_mapping",
    "filename", "file_property",
]

# I287 (T1.239): 10 deferred profile types remain empty landing zones.
DEFERRED_TYPES = [
    "chunking", "embedding", "asset", "ontology", "retrieval",
    "prompt", "validation", "indexing", "ai_reasoning", "graph_mapping",
]


class TestProcessingConfigSchema(unittest.TestCase):
    """I281 T1.225 — schema chain + profile type coverage."""

    @classmethod
    def setUpClass(cls):
        cls.config_dir = ROOT / "config"
        cls.loader = SchemaLoader(str(cls.config_dir))
        cls.loader.load_all()
        with open(cls.config_dir / "schemas" / "eks_base_schema.json", encoding="utf-8") as f:
            cls.base = json.load(f)
        with open(cls.config_dir / "schemas" / "eks_processing_config.json", encoding="utf-8") as f:
            cls.processing_config = json.load(f)
        with open(cls.config_dir / "schemas" / "eks_doc_config.json", encoding="utf-8") as f:
            cls.doc_config = json.load(f)

    def test_generic_container_accepts_all_13_profile_types(self):
        """processing_profile_registry_def.profile_type enum covers all 13 keys (I287)."""
        enum = self.base["definitions"]["processing_profile_registry_def"]["properties"]["profile_type"]["enum"]
        self.assertEqual(sorted(enum), sorted(PROFILE_TYPES))

    def test_per_type_profile_defs_present_in_base(self):
        """All 11 per-type defs exist in core base schema (Q3)."""
        defs = self.base["definitions"]
        for suffix in ("extraction", "validation", "chunking", "retrieval",
                       "indexing", "ai_reasoning", "graph_mapping",
                       "embedding", "asset", "ontology", "prompt"):
            self.assertIn(f"{suffix}_profile_def", defs, f"missing {suffix}_profile_def")

    def test_new_chain_defs_present_in_base(self):
        """I287 (T1.238): filename/file_property/os_properties defs exist in core base."""
        defs = self.base["definitions"]
        for name in ("filename_profile_def", "file_property_profile_def", "os_properties_def"):
            self.assertIn(name, defs, f"missing {name}")

    def test_setup_processing_profiles_property_declares_all_sections(self):
        """eks_setup_schema processing_profiles declares all {type}_profiles + os_properties."""
        prop = self.loader.setup_schema["properties"]["processing_profiles"]["properties"]
        expected = {f"{t}_profiles" for t in PROFILE_TYPES} | {"os_properties"}
        self.assertEqual(set(prop.keys()), expected)

    def test_extraction_profile_def_superset_of_legacy(self):
        """extraction_profile_def retains all legacy parsing_profile_def fields + new ones."""
        defn = self.base["definitions"]["extraction_profile_def"]["properties"]
        for field in ("profile_id", "parser_class", "description", "supported_extensions",
                      "supported_document_profiles", "requires_ocr", "extraction_methods",
                      "profile_type", "version", "capabilities", "constraints"):
            self.assertIn(field, defn, f"extraction_profile_def missing {field}")

    def test_all_extraction_profiles_validate(self):
        """All 5 technip_* extraction profiles validate against extraction_profile_def."""
        section_schema = self.loader.setup_schema["properties"]["processing_profiles"]["properties"]["extraction_profiles"]
        # load_all() already ran _validate_processing_config() without error
        self.assertEqual(len(self.processing_config["extraction_profiles"]), 5)

    def test_ten_deferred_sections_empty(self):
        """10 deferred profile sections present and empty (landing zones)."""
        deferred = [f"{t}_profiles" for t in DEFERRED_TYPES]
        for section in deferred:
            self.assertIn(section, self.processing_config, f"missing {section}")
            self.assertEqual(self.processing_config[section], {}, f"{section} not empty")

    def test_legacy_parsing_profiles_absent(self):
        """Q1 one-time migration: doc-config parsing_profiles section removed."""
        self.assertNotIn("parsing_profiles", self.doc_config)

    def test_legacy_parsing_profile_def_absent(self):
        """Q1 one-time migration: doc-base parsing_profile_def removed."""
        with open(self.config_dir / "schemas" / "eks_doc_base_schema.json", encoding="utf-8") as f:
            doc_base = json.load(f)
        self.assertNotIn("parsing_profile_def", doc_base["definitions"])

    def test_legacy_parsing_profiles_property_absent(self):
        """Q1 one-time migration: doc-setup parsing_profiles property removed."""
        self.assertNotIn("parsing_profiles", self.loader.doc_setup_schema["properties"])

    def test_validate_processing_config_wired(self):
        """_validate_processing_config() runs during load_all() without error."""
        # setUpClass load_all() succeeded → wired validation passed
        self.assertIsNotNone(self.loader.processing_config)


class TestProcessingConfigConsumers(unittest.TestCase):
    """I281 T1.225 — full repoint (Q2) of consumers to eks_processing_config."""

    @classmethod
    def setUpClass(cls):
        cls.config_dir = ROOT / "config"
        cls.loader = SchemaLoader(str(cls.config_dir))
        cls.loader.load_all()

    def test_parser_router_reads_extraction_profiles(self):
        """ParserRouter resolves profiles from eks_processing_config extraction_profiles."""
        router = ParserRouter(self.loader.doc_config, processing_config=self.loader.processing_config)
        self.assertEqual(router.parsing_profiles["technip_pdf"]["profile_id"], "technip_pdf")
        self.assertIn("technip_dwg", router.parsing_profiles)

    def test_project_definition_resolver_consumes_processing_config(self):
        """ProjectDefinitionResolver reads all 11 sections; PDEF drops 4→1."""
        resolver = ProjectDefinitionResolver(
            project_definition_config=self.loader.project_definition_config,
            doc_config=self.loader.doc_config,
            env_config=self.loader.config,
            processing_config=self.loader.processing_config,
        )
        resolver.resolve_all()
        pdef_3 = [e for e in resolver.data_errors if "P1-C-V-0003" in e]
        self.assertEqual(len(pdef_3), 1)
        self.assertIn("technip_docx", pdef_3[0])
        self.assertNotIn("technip_dwg", pdef_3[0])
        self.assertNotIn("technip_dgn", pdef_3[0])
        self.assertNotIn("technip_xlsx", pdef_3[0])

    def test_project_definition_references_native_profiles(self):
        """eks_project_definition_config repointed: dwg/dgn/xlsx referenced (PDEF 4→1)."""
        pd_config = self.loader.project_definition_config
        pd = pd_config.get("project_definition", pd_config)
        ids = []
        for pdef in pd.values():
            ids.append(pdef.get("parsing_profile"))
            dp = pdef.get("document_profile", {})
            if dp.get("parser"):
                ids.append(dp["parser"])
        for pid in ("technip_dwg", "technip_dgn", "technip_xlsx", "technip_pdf"):
            self.assertIn(pid, ids, f"{pid} not referenced by any project definition")


class TestPhase1ProfileEstablishment(unittest.TestCase):
    """I281 T1.225 — Phase 1 complete per-document profile establishment (Q5)."""

    @classmethod
    def setUpClass(cls):
        cls.config_dir = ROOT / "config"
        cls.loader = SchemaLoader(str(cls.config_dir))
        cls.loader.load_all()

    def test_every_binding_resolves_complete_extraction_profile(self):
        """Phase 1 establishes each document's complete profile: every binding's
        default_parsing_profile resolves to a full extraction profile in
        eks_processing_config (profile_id + parser_class + capabilities)."""
        profiles = self.loader.processing_config.get("extraction_profiles", {})
        registry = self.loader.doc_config.get("document_type_registry", [])
        self.assertGreater(len(registry), 0)
        for entry in registry:
            pid = entry.get("default_parsing_profile")
            if not pid:
                continue
            self.assertIn(pid, profiles, f"binding {entry['code']} missing profile {pid}")
            prof = profiles[pid]
            self.assertEqual(prof["profile_id"], pid)
            self.assertIn("parser_class", prof, f"{pid} lacks parser_class")

    def test_extraction_profile_type_is_extraction(self):
        """Every extraction profile declares profile_type 'extraction'."""
        for pid, prof in self.loader.processing_config.get("extraction_profiles", {}).items():
            self.assertEqual(prof.get("profile_type"), "extraction", f"{pid} wrong profile_type")


class TestI287FileProcessingChain(unittest.TestCase):
    """I287 T1.240 — Phase-1 file-processing chain in eks_processing_config.json."""

    @classmethod
    def setUpClass(cls):
        cls.config_dir = ROOT / "config"
        cls.loader = SchemaLoader(str(cls.config_dir))
        cls.loader.load_all()
        with open(cls.config_dir / "schemas" / "eks_processing_config.json", encoding="utf-8") as f:
            cls.pc = json.load(f)

    # -- filename_profiles ----------------------------------------------

    def test_filename_profiles_present(self):
        """filename_profiles carries twrp_standard + default."""
        profiles = self.pc.get("filename_profiles", {})
        self.assertIn("twrp_standard", profiles)
        self.assertIn("default", profiles)

    def test_filename_profiles_have_profile_identity(self):
        """Each filename profile declares profile_id + profile_type 'filename'."""
        for pid, profile in self.pc.get("filename_profiles", {}).items():
            self.assertEqual(profile.get("profile_id"), pid, f"{pid} profile_id mismatch")
            self.assertEqual(profile.get("profile_type"), "filename", f"{pid} wrong profile_type")

    def test_filename_profile_schema_chain(self):
        """filename profiles validate against filename_profile_def via setup schema."""
        prop = self.loader.setup_schema["properties"]["processing_profiles"]["properties"]
        section_schema = prop["filename_profiles"]
        # load_all() already ran _validate_processing_config() without error
        self.assertIn("additionalProperties", section_schema)

    # -- file_property_profiles -----------------------------------------

    def test_file_property_profiles_present(self):
        """file_property_profiles carries pdf/docx/xlsx/dgn/dwg prop profiles."""
        profiles = self.pc.get("file_property_profiles", {})
        for name in ("pdf_props", "docx_props", "xlsx_props", "dgn_props", "dwg_props"):
            self.assertIn(name, profiles, f"missing {name}")

    def test_file_property_profiles_have_identity(self):
        """Each file-property profile declares profile_id + profile_type 'file_property'."""
        for pid, profile in self.pc.get("file_property_profiles", {}).items():
            self.assertEqual(profile.get("profile_id"), pid, f"{pid} profile_id mismatch")
            self.assertEqual(profile.get("profile_type"), "file_property", f"{pid} wrong profile_type")

    def test_no_extraction_method_on_property_profiles(self):
        """I277 gate: extraction_method dropped — inherited from bound profile."""
        for pid, profile in self.pc.get("file_property_profiles", {}).items():
            self.assertNotIn("extraction_method", profile, f"{pid} must not declare extraction_method")

    # -- bound cross-check (Q3) ------------------------------------------

    def test_bound_extraction_profiles_resolve(self):
        """Every file_property_profiles.bound_extraction_profile exists in extraction_profiles."""
        extraction = self.pc.get("extraction_profiles", {})
        for pid, profile in self.pc.get("file_property_profiles", {}).items():
            bound = profile.get("bound_extraction_profile")
            self.assertIn(bound, extraction, f"{pid} bound to unknown profile {bound}")

    def test_bound_profile_supported_extensions_admit_property_profile(self):
        """Each property profile's supported_extensions are a subset of its bound
        extraction profile's supported_extensions (loose naming cross-check —
        dgn_props↔technip_dgn, dwg_props↔technip_dwg do not share exact names)."""
        extraction = self.pc.get("extraction_profiles", {})
        for pid, profile in self.pc.get("file_property_profiles", {}).items():
            bound = extraction.get(profile.get("bound_extraction_profile"), {})
            bound_exts = set(bound.get("supported_extensions", []))
            own_exts = set(profile.get("supported_extensions", []))
            if bound_exts:
                self.assertTrue(
                    own_exts.issubset(bound_exts),
                    f"{pid} ext {sorted(own_exts)} not admitted by bound profile "
                    f"{sorted(bound_exts)}",
                )

    # -- os_properties (Q1 top-level) ------------------------------------

    def test_os_properties_top_level(self):
        """os_properties is a TOP-LEVEL key in eks_processing_config.json (Q1)."""
        self.assertIn("os_properties", self.pc)
        os_cfg = self.pc["os_properties"]
        self.assertTrue(os_cfg.get("enabled"))
        self.assertIn("file_size", os_cfg.get("collect", []))
        self.assertEqual(os_cfg.get("hash_algorithm"), "md5")

    def test_property_profiles_use_os_properties(self):
        """Each property profile references os_properties via uses_os_properties."""
        for pid, profile in self.pc.get("file_property_profiles", {}).items():
            self.assertIn("uses_os_properties", profile, f"{pid} missing uses_os_properties")

    # -- doc_config no longer duplicates ---------------------------------

    def test_doc_config_chain_sections_absent(self):
        """doc_config no longer carries filename_profiles / file_property_patterns (T1.241)."""
        with open(self.config_dir / "schemas" / "eks_doc_config.json", encoding="utf-8") as f:
            doc = json.load(f)
        self.assertNotIn("filename_profiles", doc)
        self.assertNotIn("file_property_patterns", doc)

    def test_file_type_registry_no_parser_class(self):
        """parser_class single-sourced in extraction_profiles — not in file_type_registry."""
        with open(self.config_dir / "schemas" / "eks_doc_config.json", encoding="utf-8") as f:
            doc = json.load(f)
        for entry in doc.get("file_type_registry", []):
            self.assertNotIn("parser_class", entry, f"{entry.get('extension')} still has parser_class")


if __name__ == "__main__":
    unittest.main(verbosity=2)

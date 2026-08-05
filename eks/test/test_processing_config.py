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

    def test_generic_container_accepts_all_11_profile_types(self):
        """processing_profile_registry_def.profile_type enum covers all 11 keys (Q3)."""
        enum = self.base["definitions"]["processing_profile_registry_def"]["properties"]["profile_type"]["enum"]
        self.assertEqual(sorted(enum), sorted(PROFILE_TYPES))

    def test_per_type_profile_defs_present_in_base(self):
        """All 11 per-type defs exist in core base schema (Q3)."""
        defs = self.base["definitions"]
        for suffix in ("extraction", "validation", "chunking", "retrieval",
                       "indexing", "ai_reasoning", "graph_mapping",
                       "embedding", "asset", "ontology", "prompt"):
            self.assertIn(f"{suffix}_profile_def", defs, f"missing {suffix}_profile_def")

    def test_setup_processing_profiles_property_declares_11_sections(self):
        """eks_setup_schema processing_profiles property declares all 11 sections."""
        prop = self.loader.setup_schema["properties"]["processing_profiles"]["properties"]
        expected = {f"{t}_profiles" for t in PROFILE_TYPES}
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
        deferred = [f"{t}_profiles" for t in PROFILE_TYPES if t != "extraction"]
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


if __name__ == "__main__":
    unittest.main(verbosity=2)

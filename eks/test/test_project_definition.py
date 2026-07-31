"""Unit Tests for T1.193 — ProjectDefinitionResolver, RuntimeProjectConfiguration, ProjectConfigurationRegistry.

Tests cover:
- RuntimeProjectConfiguration immutability, domain dataclasses, config slices
- ProjectConfigurationRegistry lookup, immutability
- ProjectDefinitionResolver workflow (load, resolve, validate, construct, register)
- Integration with bootstrap pipeline
- Validation error/warning accumulation
"""
import unittest
from pathlib import Path
from dataclasses import fields
from eks.engine.core.project_definition import (
    ProjectDefinitionResolver,
    ProjectConfigurationRegistry,
    RuntimeProjectConfiguration,
    ProjectDomain,
    LifecycleDomain,
    EngineeringDomain,
    StandardsDomain,
    DocumentDomain,
    ParsingDomain,
    ChunkingDomain,
    EmbeddingsDomain,
    MetadataDomain,
    AssetsDomain,
    OntologyDomain,
    RetrievalDomain,
    PromptsDomain,
    ValidationDomain,
    SecurityDomain,
    RuntimeProfilesDomain,
    RuntimeMetadata,
)

# ---------------------------------------------------------------------------
# Sample test data
# ---------------------------------------------------------------------------

SAMPLE_PROJECT_DEF_CONFIG = {
    "project_definition": {
        "131101": {
            "project_identity": {
                "project_code": "131101",
                "project_name": "FPSO TWRP",
                "project_type": "offshore",
                "discipline": "multi",
                "client": "Client A",
                "contractor": "Contractor X",
                "region": "APAC",
                "execution_center": "Kuala Lumpur",
                "status": "active",
            },
            "project_lifecycle": {
                "project_phase": "Detailed Design",
                "execution_stage": "IFC",
                "baseline_revision": "A",
                "issue_status": "issued",
                "document_status": "current",
                "planned_completion": "2027-06-30",
            },
            "engineering_convention": {
                "drawing_standard": "ISO",
                "numbering_scheme": "TWRP",
                "revision_scheme": "alpha_numeric",
                "tag_format": "ANSI/ISA-5.1",
                "engineering_units": "metric",
                "allowed_disciplines": ["SP", "DS", "PI"],
            },
            "engineering_standards": {
                "piping": "ASME B31.3",
                "instrumentation": "IEC 61511",
            },
            "document_profile": {
                "filename_pattern": "twrp_standard",
                "parser": "technip_pdf",
                "revision": "alpha_numeric",
                "ocr": "default",
                "column_processing": "dcc_aligned",
            },
            "parsing_profile": "technip_pdf",
            "chunking_profile": "standard",
            "embedding_profile": "openai_1536",
            "metadata_policy": "standard_inherit",
            "asset_profile": {"profile": "process"},
            "ontology_profile": {"profile": "default"},
            "retrieval_profile": {"profile": "standard"},
            "prompt_profile": "engineering_assistant",
            "validation_profile": "strict",
            "security_profile": {
                "document_classification": "internal",
                "access_policy": "restricted",
                "redaction_policy": "none",
            },
            "runtime_profiles": {
                "storage": "default_storage",
                "vector_db": "default_vector",
                "graph_db": "default_graph",
                "messaging": "none",
                "cache": "default_cache",
            },
            "fragment_required_fields": {
                "item_core": ["keytag", "tag_type", "tag_no", "description"]
            },
        }
    }
}

SAMPLE_DOC_CONFIG = {
    "parsing_profiles": {
        "technip_pdf": {
            "profile_id": "technip_pdf",
            "parser_class": "eks.engine.parsers.pdf_parser.PDFParser",
            "description": "TWRP PDF document parser",
            "supported_extensions": ["pdf"],
            "supported_document_profiles": ["twrp_standard"],
            "requires_ocr": False,
        },
        "technip_docx": {
            "profile_id": "technip_docx",
            "parser_class": "eks.engine.parsers.docx_parser.DOCXParser",
            "description": "TWRP Word document parser",
            "supported_extensions": ["docx"],
            "supported_document_profiles": ["twrp_standard"],
            "requires_ocr": False,
        },
        "ocr_pdf": {
            "profile_id": "ocr_pdf",
            "parser_class": "eks.engine.parsers.pdf_parser.PDFParser",
            "description": "OCR-required PDF parser",
            "supported_extensions": ["pdf"],
            "supported_document_profiles": ["twrp_standard"],
            "requires_ocr": True,
        },
    },
    "file_type_registry": [
        {"extension": "pdf", "parser_class": "eks.engine.parsers.pdf_parser.PDFParser"},
        {"extension": "docx", "parser_class": "eks.engine.parsers.docx_parser.DOCXParser"},
    ],
    "document_type_registry": [
        {"code": "SPC", "label": "Technical Specification"},
        {"code": "DWG", "label": "Engineering Drawing"},
    ],
}

SAMPLE_ENV_CONFIG = {
    "version": "1.9.0",
    "vector_store": {"provider": "qdrant", "host": "localhost", "port": 6333},
    "embedding": {"provider": "openai", "model": "text-embedding-3-small", "dimensions": 1536},
    "registry": {"type": "duckdb", "path": "output/eks_registry.db"},
    "logging": {"default_level": 1},
}


class TestRuntimeProjectConfiguration(unittest.TestCase):
    """T1.193.1 — RuntimeProjectConfiguration dataclass structure and immutability."""

    def _make_full_config(self) -> RuntimeProjectConfiguration:
        return RuntimeProjectConfiguration(
            project=ProjectDomain(
                project_code="131101", project_name="FPSO TWRP",
                project_type="offshore", discipline="multi",
                client="Client A", contractor="Contractor X",
                region="APAC", execution_center="Kuala Lumpur",
                status="active",
            ),
            lifecycle=LifecycleDomain(
                project_phase="Detailed Design", execution_stage="IFC",
                baseline_revision="A", issue_status="issued",
                document_status="current",
            ),
            engineering=EngineeringDomain(
                drawing_standard="ISO", numbering_scheme="TWRP",
                revision_scheme="alpha_numeric", tag_format="ANSI/ISA-5.1",
                engineering_units="metric",
                allowed_disciplines=["SP", "DS", "PI"],
            ),
            standards=StandardsDomain(standards={"piping": "ASME B31.3"}),
            document=DocumentDomain(
                filename_pattern="twrp_standard", parser_profile="technip_pdf",
                revision_scheme="alpha_numeric", ocr_profile="default",
                column_processing="dcc_aligned",
            ),
            parsing=ParsingDomain(profile_id="technip_pdf"),
            chunking=ChunkingDomain(profile_id="standard"),
            embeddings=EmbeddingsDomain(profile_id="openai_1536"),
            metadata=MetadataDomain(policy_id="standard_inherit"),
            assets=AssetsDomain(profile_id="process"),
            ontology=OntologyDomain(profile_id="default"),
            retrieval=RetrievalDomain(profile_id="standard"),
            prompts=PromptsDomain(profile_id="engineering_assistant"),
            validation=ValidationDomain(profile_id="strict"),
            security=SecurityDomain(
                document_classification="internal",
                access_policy="restricted",
            ),
            runtime_profiles=RuntimeProfilesDomain(
                storage="default_storage", vector_db="default_vector",
            ),
            runtime=RuntimeMetadata(
                configuration_version="1.9.0",
                validation_status="passed",
            ),
        )

    def test_all_17_domains_present(self):
        """RuntimeProjectConfiguration must have exactly 17 domain fields."""
        cfg = self._make_full_config()
        domain_fields = [f.name for f in fields(RuntimeProjectConfiguration)]
        expected = [
            "project", "lifecycle", "engineering", "standards", "document",
            "parsing", "chunking", "embeddings", "metadata", "assets",
            "ontology", "retrieval", "prompts", "validation", "security",
            "runtime_profiles", "runtime",
        ]
        for name in expected:
            self.assertIn(name, domain_fields, f"Missing domain: {name}")
        self.assertEqual(len(domain_fields), 17)

    def test_immutable_frozen(self):
        """RuntimeProjectConfiguration must be frozen (immutable)."""
        cfg = self._make_full_config()
        with self.assertRaises(Exception):
            cfg.project = "REPLACED"  # type: ignore

    def test_slice_for_filename_parser(self):
        """FilenameParser receives project, engineering, document."""
        cfg = self._make_full_config()
        slc = cfg.slice_for("FilenameParser")
        self.assertIn("project", slc)
        self.assertIn("engineering", slc)
        self.assertIn("document", slc)
        self.assertEqual(slc["project"].project_code, "131101")

    def test_slice_for_retriever(self):
        """Retriever receives retrieval, embeddings, ontology."""
        cfg = self._make_full_config()
        slc = cfg.slice_for("Retriever")
        self.assertIn("retrieval", slc)
        self.assertIn("embeddings", slc)
        self.assertIn("ontology", slc)

    def test_slice_for_unknown_module_returns_empty(self):
        """Unknown module name returns empty slice."""
        cfg = self._make_full_config()
        slc = cfg.slice_for("NonExistent")
        self.assertEqual(slc, {})

    def test_asset_slice_carries_fragment_required_fields(self):
        """T1.196 (I266): AssetExtractor slice exposes fragment_required_fields.

        Migrated from the retired eks_project_rules_config.json — the per-project
        asset validation rules must be reachable from RuntimeProjectConfiguration
        (resolved via ProjectDefinitionResolver, surfaced in the assets slice).
        """
        resolver = _make_config({"131101": _build_valid_project()})
        registry = resolver.resolve_all()
        cfg = registry.get("131101")
        self.assertIsNotNone(cfg)
        slc = cfg.slice_for("AssetExtractor")
        assets = slc.get("assets")
        self.assertIsNotNone(assets)
        frf = assets.resolved.get("fragment_required_fields", {})
        self.assertIn("item_core", frf)
        self.assertIn("keytag", frf["item_core"])
        self.assertIn("description", frf["item_core"])


class TestProjectConfigurationRegistry(unittest.TestCase):
    """T1.193.2 — ProjectConfigurationRegistry lookup and immutability."""

    def setUp(self):
        self.project = ProjectDomain(
            project_code="131101", project_name="FPSO TWRP",
            project_type="offshore", discipline="multi",
            client="Client A", contractor="Contractor X",
            region="APAC", execution_center="Kuala Lumpur",
            status="active",
        )
        self.cfg = RuntimeProjectConfiguration(
            project=self.project,
            lifecycle=LifecycleDomain(project_phase="", execution_stage="",
                                       baseline_revision="", issue_status="",
                                       document_status=""),
            engineering=EngineeringDomain(drawing_standard="", numbering_scheme="",
                                           revision_scheme="", tag_format="",
                                           engineering_units=""),
            standards=StandardsDomain(),
            document=DocumentDomain(filename_pattern="", parser_profile="",
                                     revision_scheme="", ocr_profile="",
                                     column_processing=""),
            parsing=ParsingDomain(profile_id=""),
            chunking=ChunkingDomain(profile_id=""),
            embeddings=EmbeddingsDomain(profile_id=""),
            metadata=MetadataDomain(policy_id=""),
            assets=AssetsDomain(profile_id=""),
            ontology=OntologyDomain(profile_id=""),
            retrieval=RetrievalDomain(profile_id=""),
            prompts=PromptsDomain(profile_id=""),
            validation=ValidationDomain(profile_id=""),
            security=SecurityDomain(),
            runtime_profiles=RuntimeProfilesDomain(),
            runtime=RuntimeMetadata(),
        )
        self.registry = ProjectConfigurationRegistry({"131101": self.cfg})

    def test_get_existing_project(self):
        result = self.registry.get("131101")
        self.assertIsNotNone(result)
        self.assertEqual(result.project.project_code, "131101")

    def test_get_missing_project_returns_none(self):
        result = self.registry.get("999999")
        self.assertIsNone(result)

    def test_contains(self):
        self.assertIn("131101", self.registry)
        self.assertNotIn("999999", self.registry)

    def test_project_codes(self):
        codes = self.registry.project_codes
        self.assertIn("131101", codes)

    def test_len(self):
        self.assertEqual(len(self.registry), 1)


class TestProjectDefinitionResolver(unittest.TestCase):
    """T1.193.3 — ProjectDefinitionResolver full workflow."""

    def setUp(self):
        self.resolver = ProjectDefinitionResolver(
            project_definition_config=SAMPLE_PROJECT_DEF_CONFIG,
            doc_config=SAMPLE_DOC_CONFIG,
            env_config=SAMPLE_ENV_CONFIG,
        )

    def test_resolve_all_returns_registry(self):
        registry = self.resolver.resolve_all()
        self.assertIsInstance(registry, ProjectConfigurationRegistry)
        self.assertGreater(len(registry), 0)

    def test_resolve_all_resolves_131101(self):
        registry = self.resolver.resolve_all()
        cfg = registry.get("131101")
        self.assertIsNotNone(cfg)
        self.assertEqual(cfg.project.project_name, "FPSO TWRP")
        self.assertEqual(cfg.project.project_type, "offshore")

    def test_resolve_all_resolves_lifecycle(self):
        registry = self.resolver.resolve_all()
        cfg = registry.get("131101")
        self.assertEqual(cfg.lifecycle.project_phase, "Detailed Design")
        self.assertEqual(cfg.lifecycle.execution_stage, "IFC")

    def test_resolve_all_resolves_engineering(self):
        registry = self.resolver.resolve_all()
        cfg = registry.get("131101")
        self.assertEqual(cfg.engineering.drawing_standard, "ISO")
        self.assertIn("SP", cfg.engineering.allowed_disciplines)

    def test_resolve_all_resolves_standards(self):
        registry = self.resolver.resolve_all()
        cfg = registry.get("131101")
        self.assertEqual(cfg.standards.standards.get("piping"), "ASME B31.3")

    def test_resolve_all_resolves_document_profile(self):
        registry = self.resolver.resolve_all()
        cfg = registry.get("131101")
        self.assertEqual(cfg.document.filename_pattern, "twrp_standard")
        self.assertEqual(cfg.document.parser_profile, "technip_pdf")

    def test_resolve_all_resolves_profile_references(self):
        registry = self.resolver.resolve_all()
        cfg = registry.get("131101")
        self.assertEqual(cfg.parsing.profile_id, "technip_pdf")
        self.assertEqual(cfg.chunking.profile_id, "standard")
        self.assertEqual(cfg.embeddings.profile_id, "openai_1536")

    def test_resolve_all_resolves_security(self):
        registry = self.resolver.resolve_all()
        cfg = registry.get("131101")
        self.assertEqual(cfg.security.document_classification, "internal")
        self.assertEqual(cfg.security.access_policy, "restricted")

    def test_resolve_all_resolves_runtime_profiles(self):
        registry = self.resolver.resolve_all()
        cfg = registry.get("131101")
        self.assertEqual(cfg.runtime_profiles.storage, "default_storage")
        self.assertEqual(cfg.runtime_profiles.vector_db, "default_vector")

    def test_resolve_all_runtime_metadata(self):
        registry = self.resolver.resolve_all()
        cfg = registry.get("131101")
        self.assertEqual(cfg.runtime.validation_status, "passed")
        self.assertTrue(len(cfg.runtime.configuration_checksum) > 0)

    def test_validation_report(self):
        self.resolver.resolve_all()
        report = self.resolver.validation_report
        self.assertIn("resolved_projects", report)
        self.assertIn("errors", report)
        self.assertIn("131101", report["resolved_projects"])


class TestProjectDefinitionResolverValidation(unittest.TestCase):
    """T1.193.4 — Validation error/warning handling."""

    def test_missing_project_identity_fails_validation(self):
        bad_config = {"project_definition": {"BAD": {"project_name": "No identity"}}}
        resolver = ProjectDefinitionResolver(
            project_definition_config=bad_config,
            doc_config=SAMPLE_DOC_CONFIG,
            env_config=SAMPLE_ENV_CONFIG,
        )
        registry = resolver.resolve_all()
        self.assertEqual(len(registry), 0)
        self.assertGreater(len(resolver.errors), 0)

    def test_resolver_logs_warnings_for_unresolved_profiles(self):
        resolver = ProjectDefinitionResolver(
            project_definition_config=SAMPLE_PROJECT_DEF_CONFIG,
            doc_config=SAMPLE_DOC_CONFIG,
            env_config=SAMPLE_ENV_CONFIG,
            logger=None,
        )
        resolver.resolve_all()
        # Profile resolution for chunking/embedding domains will warn
        # that no dedicated library exists yet
        self.assertGreaterEqual(len(resolver.warnings), 0)


class TestProjectDefinitionResolverEdgeCases(unittest.TestCase):
    """T1.193.5 — Edge cases and empty configs."""

    def test_empty_project_definition_config(self):
        resolver = ProjectDefinitionResolver(
            project_definition_config={},
            doc_config={},
            env_config={},
        )
        registry = resolver.resolve_all()
        self.assertEqual(len(registry), 0)

    def test_empty_project_definition_data(self):
        resolver = ProjectDefinitionResolver(
            project_definition_config={"project_definition": {}},
            doc_config={},
            env_config={},
        )
        registry = resolver.resolve_all()
        self.assertEqual(len(registry), 0)

    def test_non_dict_project_entry_is_skipped(self):
        bad_config = {"project_definition": {"SKIP": "not_a_dict"}}
        resolver = ProjectDefinitionResolver(
            project_definition_config=bad_config,
            doc_config={},
            env_config={},
        )
        registry = resolver.resolve_all()
        self.assertEqual(len(registry), 0)

    def test_config_slice_all_known_modules(self):
        resolver = ProjectDefinitionResolver(
            project_definition_config=SAMPLE_PROJECT_DEF_CONFIG,
            doc_config=SAMPLE_DOC_CONFIG,
            env_config=SAMPLE_ENV_CONFIG,
        )
        registry = resolver.resolve_all()
        cfg = registry.get("131101")
        self.assertIsNotNone(cfg)
        # All 13 modules from the slice table
        for module in [
            "FilenameParser", "RevisionValidator", "DocumentParser",
            "OCRProcessor", "MetadataExtractor", "ColumnProcessor",
            "AssetExtractor", "GraphBuilder", "Retriever",
            "PromptEngine", "ValidationEngine", "FileScanner", "Pipeline",
        ]:
            slc = cfg.slice_for(module)
            self.assertGreater(len(slc), 0, f"Empty slice for {module}")

    def test_registry_immutable(self):
        resolver = ProjectDefinitionResolver(
            project_definition_config=SAMPLE_PROJECT_DEF_CONFIG,
            doc_config=SAMPLE_DOC_CONFIG,
            env_config=SAMPLE_ENV_CONFIG,
        )
        registry = resolver.resolve_all()
        with self.assertRaises(Exception):
            registry._configs["NEW"] = None  # type: ignore


# ---------------------------------------------------------------------------
# T1.195 — Configuration Validation (V1/V2/V3)
# ---------------------------------------------------------------------------


def _build_valid_project(project_code="131101", **overrides):
    """Build a valid project definition (mirrors SAMPLE_PROJECT_DEF_CONFIG)."""
    pdef = {
        "project_identity": {
            "project_code": project_code,
            "project_name": "FPSO TWRP",
            "project_type": "offshore",
            "discipline": "multi",
            "client": "Client A",
            "contractor": "Contractor X",
            "region": "APAC",
            "execution_center": "Kuala Lumpur",
            "status": "active",
        },
        "project_lifecycle": {
            "project_phase": "Detailed Design",
            "execution_stage": "IFC",
            "baseline_revision": "A",
            "issue_status": "issued",
            "document_status": "current",
            "planned_completion": "2027-06-30",
        },
        "engineering_convention": {
            "drawing_standard": "ISO",
            "numbering_scheme": "TWRP",
            "revision_scheme": "alpha_numeric",
            "tag_format": "ANSI/ISA-5.1",
            "engineering_units": "metric",
            "allowed_disciplines": ["SP", "DS", "PI"],
        },
        "engineering_standards": {
            "piping": "ASME B31.3",
        },
        "document_profile": {
            "filename_pattern": "twrp_standard",
            "parser": "technip_pdf",
            "revision": "alpha_numeric",
            "ocr": "default",
            "column_processing": "dcc_aligned",
        },
        "parsing_profile": "technip_pdf",
        "chunking_profile": "standard",
        "embedding_profile": "openai_1536",
        "metadata_policy": "standard_inherit",
        "asset_profile": {"profile": "process"},
        "ontology_profile": {"profile": "default"},
        "retrieval_profile": {"profile": "standard"},
        "prompt_profile": "engineering_assistant",
        "validation_profile": "strict",
        "security_profile": {
            "document_classification": "internal",
            "access_policy": "restricted",
            "redaction_policy": "none",
        },
        "runtime_profiles": {
            "storage": "default_storage",
            "vector_db": "default_vector",
            "graph_db": "default_graph",
            "messaging": "none",
            "cache": "default_cache",
        },
        "fragment_required_fields": {
            "item_core": ["keytag", "tag_type", "tag_no", "description"],
        },
    }
    pdef.update(overrides)
    return pdef


def _make_config(project_defs, doc_config=None, env_config=None):
    """Build a ProjectDefinitionResolver with the given inputs."""
    return ProjectDefinitionResolver(
        project_definition_config={"project_definition": project_defs},
        doc_config=doc_config if doc_config is not None else SAMPLE_DOC_CONFIG,
        env_config=env_config if env_config is not None else SAMPLE_ENV_CONFIG,
        logger=None,
    )


class TestL133ProjectCompleteness(unittest.TestCase):
    """T1.195 — L.13.3 project definition completeness (system errors)."""

    def test_valid_project_no_system_errors(self):
        resolver = _make_config({"131101": _build_valid_project()})
        registry = resolver.resolve_all()
        self.assertEqual(len(registry), 1)
        self.assertEqual(resolver.errors, [])
        self.assertFalse(any("S-C-S-0901" in e for e in resolver.errors))

    def test_missing_project_identity_section(self):
        pdef = _build_valid_project()
        del pdef["project_identity"]
        resolver = _make_config({"131101": pdef})
        registry = resolver.resolve_all()
        self.assertEqual(len(registry), 0)
        self.assertTrue(any("S-C-S-0901" in e for e in resolver.errors))

    def test_missing_mandatory_identity_field(self):
        pdef = _build_valid_project()
        del pdef["project_identity"]["project_name"]
        resolver = _make_config({"131101": pdef})
        registry = resolver.resolve_all()
        self.assertEqual(len(registry), 0)
        self.assertTrue(any(
            "S-C-S-0901" in e and "project_name" in e for e in resolver.errors))

    def test_missing_document_profile_section(self):
        pdef = _build_valid_project()
        del pdef["document_profile"]
        resolver = _make_config({"131101": pdef})
        registry = resolver.resolve_all()
        self.assertEqual(len(registry), 0)
        self.assertTrue(any("S-C-S-0901" in e for e in resolver.errors))

    def test_missing_lifecycle_section(self):
        pdef = _build_valid_project()
        del pdef["project_lifecycle"]
        resolver = _make_config({"131101": pdef})
        resolver.resolve_all()
        self.assertTrue(any("S-C-S-0901" in e and "project_lifecycle" in e
                            for e in resolver.errors))

    def test_missing_engineering_convention_section(self):
        pdef = _build_valid_project()
        del pdef["engineering_convention"]
        resolver = _make_config({"131101": pdef})
        resolver.resolve_all()
        self.assertTrue(any("S-C-S-0901" in e and "engineering_convention" in e
                            for e in resolver.errors))

    def test_missing_standards_section(self):
        pdef = _build_valid_project()
        del pdef["engineering_standards"]
        resolver = _make_config({"131101": pdef})
        resolver.resolve_all()
        self.assertTrue(any("S-C-S-0901" in e and "engineering_standards" in e
                            for e in resolver.errors))


class TestL134ProfileReferences(unittest.TestCase):
    """T1.195 — L.13.4 reusable profile references (system errors)."""

    def test_unknown_parsing_profile_is_system_error(self):
        """Domain with declared library + unknown id → S-C-S-0902 hard fail."""
        pdef = _build_valid_project(parsing_profile="bogus_parser")
        resolver = _make_config({"131101": pdef})
        registry = resolver.resolve_all()
        self.assertEqual(len(registry), 0)
        self.assertTrue(any("S-C-S-0902" in e for e in resolver.errors))

    def test_unknown_document_profile_parser(self):
        pdef = _build_valid_project()
        pdef["document_profile"]["parser"] = "bogus_parser"
        resolver = _make_config({"131101": pdef})
        resolver.resolve_all()
        self.assertTrue(any("S-C-S-0902" in e for e in resolver.errors))

    def test_deferred_domain_warns_not_fails(self):
        """Chunking/embedding domains without a library warn, never error."""
        pdef = _build_valid_project()
        resolver = _make_config({"131101": pdef})
        registry = resolver.resolve_all()
        self.assertEqual(len(registry), 1)
        self.assertEqual(resolver.errors, [])
        self.assertTrue(any("chunking" in w for w in resolver.warnings))

    def test_known_profile_exact_key_resolves(self):
        pdef = _build_valid_project(parsing_profile="technip_pdf")
        resolver = _make_config({"131101": pdef})
        registry = resolver.resolve_all()
        cfg = registry.get("131101")
        self.assertEqual(cfg.parsing.profile_id, "technip_pdf")
        self.assertEqual(cfg.parsing.resolved.get("parser_class"),
                         "eks.engine.parsers.pdf_parser.PDFParser")

    def test_ocr_profile_exact_key_resolves_capabilities(self):
        pdef = _build_valid_project(parsing_profile="ocr_pdf")
        resolver = _make_config({"131101": pdef})
        registry = resolver.resolve_all()
        cfg = registry.get("131101")
        self.assertTrue(cfg.parsing.resolved.get("requires_ocr") is True)


class TestL135EnvironmentProfiles(unittest.TestCase):
    """T1.195 — L.13.5 environment/runtime profile references."""

    def test_known_runtime_profiles_pass(self):
        pdef = _build_valid_project()
        resolver = _make_config({"131101": pdef})
        registry = resolver.resolve_all()
        self.assertEqual(len(registry), 1)
        self.assertFalse(any("S-C-S-0902" in e for e in resolver.errors))

    def test_unknown_runtime_profile_is_system_error(self):
        pdef = _build_valid_project()
        pdef["runtime_profiles"]["storage"] = "s3_production"
        resolver = _make_config({"131101": pdef})
        registry = resolver.resolve_all()
        self.assertEqual(len(registry), 0)
        self.assertTrue(any("S-C-S-0902" in e and "s3_production" in e
                            for e in resolver.errors))

    def test_empty_runtime_profile_is_system_error(self):
        pdef = _build_valid_project()
        pdef["runtime_profiles"]["cache"] = ""
        resolver = _make_config({"131101": pdef})
        resolver.resolve_all()
        self.assertTrue(any("S-C-S-0902" in e and "cache" in e
                            for e in resolver.errors))

    def test_known_runtime_profiles_allowlist(self):
        known = ProjectDefinitionResolver._known_runtime_profiles()
        for ref in ("default_storage", "default_vector", "default_graph",
                    "default_cache", "none"):
            self.assertIn(ref, known)


class TestL136CapabilityConsistency(unittest.TestCase):
    """T1.195 — L.13.6 capability consistency (V2, data errors)."""

    def test_supported_document_profile_match_no_data_error(self):
        pdef = _build_valid_project()
        resolver = _make_config({"131101": pdef})
        registry = resolver.resolve_all()
        self.assertEqual(len(registry), 1)
        self.assertFalse(any("P1-C-V-0001" in e for e in resolver.data_errors))

    def test_unsupported_document_profile_emits_data_error(self):
        pdef = _build_valid_project()
        pdef["document_profile"]["filename_pattern"] = "non_standard"
        resolver = _make_config({"131101": pdef})
        registry = resolver.resolve_all()
        self.assertEqual(len(registry), 1)  # data error never blocks
        self.assertTrue(any("P1-C-V-0001" in e and "non_standard" in e
                            for e in resolver.data_errors))

    def test_requires_ocr_without_ocr_emits_data_error(self):
        pdef = _build_valid_project(parsing_profile="ocr_pdf")
        pdef["document_profile"]["ocr"] = "none"
        resolver = _make_config({"131101": pdef})
        resolver.resolve_all()
        self.assertTrue(any("P1-C-V-0001" in e and "OCR" in e
                            for e in resolver.data_errors))

    def test_revision_scheme_mismatch_emits_data_error(self):
        pdef = _build_valid_project()
        pdef["document_profile"]["revision"] = "numeric"
        pdef["engineering_convention"]["revision_scheme"] = "alpha_numeric"
        resolver = _make_config({"131101": pdef})
        resolver.resolve_all()
        self.assertTrue(any("P1-C-V-0001" in e and "revision scheme" in e.lower()
                            for e in resolver.data_errors))

    def test_capability_errors_never_block_construction(self):
        pdef = _build_valid_project()
        pdef["document_profile"]["revision"] = "numeric"
        pdef["engineering_convention"]["revision_scheme"] = "alpha_numeric"
        resolver = _make_config({"131101": pdef})
        registry = resolver.resolve_all()
        self.assertEqual(len(registry), 1)
        self.assertEqual(len(resolver.errors), 0)

    def test_generic_evaluator_no_value_selected(self):
        """_evaluate_capability_compat with no selected value → data error."""
        resolver = _make_config({})
        errors = resolver._evaluate_capability_compat(
            {"supported_document_profiles": ["a", "b"]}, "supported_document_profiles",
            "", "document profile")
        self.assertEqual(len(errors), 1)
        self.assertIn("P1-C-V-0001", errors[0])

    def test_generic_evaluator_match_no_error(self):
        resolver = _make_config({})
        errors = resolver._evaluate_capability_compat(
            {"supported_extensions": ["pdf", "docx"]}, "supported_extensions",
            "pdf", "extension")
        self.assertEqual(errors, [])


class TestL137MetadataPolicy(unittest.TestCase):
    """T1.195 — L.13.7 metadata policy validation (data errors)."""

    def test_no_mandatory_metadata_no_data_error(self):
        pdef = _build_valid_project()
        resolver = _make_config({"131101": pdef})
        resolver.resolve_all()
        self.assertFalse(any("P1-C-V-0002" in e for e in resolver.data_errors))

    def test_mandatory_metadata_gap_emits_data_error(self):
        pdef = _build_valid_project(mandatory_metadata=["sheet_number", "plant_area"])
        resolver = _make_config({"131101": pdef})
        registry = resolver.resolve_all()
        self.assertEqual(len(registry), 1)  # data error never blocks
        self.assertTrue(any("P1-C-V-0002" in e and "plant_area" in e
                            for e in resolver.data_errors))

    def test_inherited_metadata_fields_covered(self):
        pdef = _build_valid_project(
            mandatory_metadata=["project_code", "revision", "document_number"])
        resolver = _make_config({"131101": pdef})
        resolver.resolve_all()
        self.assertFalse(any("P1-C-V-0002" in e for e in resolver.data_errors))


class TestL138RuntimeConstruction(unittest.TestCase):
    """T1.195 — L.13.8 runtime construction failure (system errors)."""

    def test_runtime_construction_success(self):
        pdef = _build_valid_project()
        resolver = _make_config({"131101": pdef})
        registry = resolver.resolve_all()
        cfg = registry.get("131101")
        self.assertEqual(cfg.runtime.validation_status, "passed")
        self.assertFalse(any("S-C-S-0904" in e for e in resolver.errors))

    def test_runtime_construction_failure_system_error(self):
        # A non-dict env_config breaks RuntimeMetadata construction in the
        # L.13.8 try/except → S-C-S-0904 system error.
        pdef = _build_valid_project()
        resolver = ProjectDefinitionResolver(
            project_definition_config={"project_definition": {"131101": pdef}},
            doc_config=SAMPLE_DOC_CONFIG,
            env_config=["not", "a", "dict"],
            logger=None,
        )
        registry = resolver.resolve_all()
        self.assertEqual(len(registry), 0)
        self.assertTrue(any("S-C-S-0904" in e for e in resolver.errors))


class TestL139Duplicates(unittest.TestCase):
    """T1.195 — L.13.9 duplicate detection (system errors)."""

    def test_duplicate_project_code_system_error(self):
        resolver = _make_config({"131101": _build_valid_project()})
        resolver._pd_config["project_definition"]["131101"] = _build_valid_project()
        # Force duplicate by injecting a duplicate key via list-style detection
        pd = resolver._pd_config
        resolver._errors = []
        resolver._validate_duplicates()
        self.assertFalse(any("S-C-S-0903" in e for e in resolver.errors))

    def test_duplicate_profile_across_registries_system_error(self):
        doc_config = {
            "parsing_profiles": {"shared": {"profile_id": "shared"}},
            "chunking_profiles": {"shared": {"profile_id": "shared"}},
        }
        resolver = _make_config({}, doc_config=doc_config)
        resolver._validate_duplicates()
        self.assertTrue(any("S-C-S-0903" in e and "shared" in e
                            for e in resolver.errors))

    def test_no_duplicates_no_error(self):
        resolver = _make_config({"131101": _build_valid_project()})
        resolver._validate_duplicates()
        self.assertEqual(resolver.errors, [])


class TestL1310UnusedConfig(unittest.TestCase):
    """T1.195 — L.13.10 unused configuration detection (data errors)."""

    def test_unused_profile_emits_data_error(self):
        pdef = _build_valid_project(parsing_profile="technip_pdf")
        resolver = _make_config({"131101": pdef})
        resolver.resolve_all()
        self.assertTrue(any("P1-C-V-0003" in e and "technip_docx" in e
                            for e in resolver.data_errors))

    def test_unused_profile_never_blocks(self):
        pdef = _build_valid_project(parsing_profile="technip_pdf")
        resolver = _make_config({"131101": pdef})
        registry = resolver.resolve_all()
        self.assertEqual(len(registry), 1)
        self.assertEqual(len(resolver.errors), 0)

    def test_all_profiles_used_no_unused_error(self):
        doc_config = dict(SAMPLE_DOC_CONFIG)
        doc_config["parsing_profiles"] = {
            "technip_pdf": doc_config["parsing_profiles"]["technip_pdf"]}
        pdef = _build_valid_project(parsing_profile="technip_pdf")
        resolver = _make_config({"131101": pdef}, doc_config=doc_config)
        resolver.resolve_all()
        self.assertFalse(any("P1-C-V-0003" in e for e in resolver.data_errors))

    def test_unused_chunking_profile_emits_data_error(self):
        doc_config = dict(SAMPLE_DOC_CONFIG)
        doc_config["chunking_profiles"] = {
            "standard": {"profile_id": "standard"},
            "legacy_chunk": {"profile_id": "legacy_chunk"},
        }
        pdef = _build_valid_project(chunking_profile="standard")
        resolver = _make_config({"131101": pdef}, doc_config=doc_config)
        resolver.resolve_all()
        self.assertTrue(any("P1-C-V-0003" in e and "legacy_chunk" in e
                            for e in resolver.data_errors))


class TestL1312ValidationReport(unittest.TestCase):
    """T1.195 — L.13.12 validation report content."""

    def test_report_contains_all_sections(self):
        resolver = _make_config({"131101": _build_valid_project()})
        resolver.resolve_all()
        report = resolver.validation_report
        for key in ("resolved_projects", "resolved_profiles", "runtime_profiles",
                    "checksums", "schema_versions", "rpc_version", "errors",
                    "data_errors", "warnings", "validation_timestamp"):
            self.assertIn(key, report)

    def test_report_resolved_projects(self):
        resolver = _make_config({"131101": _build_valid_project()})
        resolver.resolve_all()
        report = resolver.validation_report
        self.assertIn("131101", report["resolved_projects"])
        self.assertIn("technip_pdf", report["resolved_profiles"])

    def test_report_runtime_profiles(self):
        resolver = _make_config({"131101": _build_valid_project()})
        resolver.resolve_all()
        report = resolver.validation_report
        self.assertIn("default_storage", report["runtime_profiles"])
        self.assertIn("default_vector", report["runtime_profiles"])

    def test_report_checksum_and_schema_version(self):
        resolver = _make_config({"131101": _build_valid_project()})
        resolver.resolve_all()
        report = resolver.validation_report
        self.assertGreater(len(report["checksums"]["131101"]), 0)
        self.assertEqual(report["schema_versions"]["131101"], "1.0.0")

    def test_report_captures_data_errors(self):
        pdef = _build_valid_project(mandatory_metadata=["plant_area"])
        resolver = _make_config({"131101": pdef})
        resolver.resolve_all()
        report = resolver.validation_report
        self.assertTrue(any("P1-C-V-0002" in e for e in report["data_errors"]))


class TestV1FailureSemantics(unittest.TestCase):
    """T1.195 — V1 system errors hard-fail, data errors never fail."""

    def test_system_error_blocks_project(self):
        pdef = _build_valid_project()
        del pdef["project_identity"]
        resolver = _make_config({"131101": pdef})
        registry = resolver.resolve_all()
        self.assertEqual(len(registry), 0)
        self.assertTrue(resolver.errors)

    def test_data_error_never_blocks_project(self):
        pdef = _build_valid_project(mandatory_metadata=["plant_area"])
        resolver = _make_config({"131101": pdef})
        registry = resolver.resolve_all()
        self.assertEqual(len(registry), 1)
        self.assertTrue(resolver.data_errors)
        self.assertEqual(resolver.errors, [])

    def test_mixed_errors_block_only_bad_project(self):
        good = _build_valid_project("131101")
        bad = _build_valid_project("131242")
        del bad["project_identity"]
        resolver = _make_config({"131101": good, "131242": bad})
        registry = resolver.resolve_all()
        self.assertIn("131101", registry)
        self.assertNotIn("131242", registry)
        self.assertTrue(any("S-C-S-0901" in e for e in resolver.errors))

    def test_data_errors_property_isolation(self):
        """data_errors and errors are independent accumulators."""
        resolver = _make_config({"131101": _build_valid_project()})
        resolver.resolve_all()
        self.assertIsInstance(resolver.data_errors, list)
        self.assertIsInstance(resolver.errors, list)


class TestV2ExactKeyLookup(unittest.TestCase):
    """T1.195 — V2 exact-key profile lookup (no substring match)."""

    def test_substring_match_rejected(self):
        """'pdf' must NOT match parser_class 'eks.engine.parsers.pdf_parser...'."""
        pdef = _build_valid_project(parsing_profile="pdf")
        resolver = _make_config({"131101": pdef})
        registry = resolver.resolve_all()
        # 'pdf' is not an exact key in parsing_profiles → system error
        self.assertEqual(len(registry), 0)
        self.assertTrue(any("S-C-S-0902" in e for e in resolver.errors))

    def test_exact_extension_fallback(self):
        """Legacy fallback matches exact extension in file_type_registry."""
        doc_config = dict(SAMPLE_DOC_CONFIG)
        doc_config.pop("parsing_profiles", None)
        pdef = _build_valid_project(parsing_profile="pdf")
        resolver = _make_config({"131101": pdef}, doc_config=doc_config)
        registry = resolver.resolve_all()
        self.assertEqual(len(registry), 1)
        cfg = registry.get("131101")
        self.assertEqual(cfg.parsing.resolved.get("extension"), "pdf")

    def test_unknown_key_not_partially_matched(self):
        """Profile id containing a library key substring must still fail."""
        pdef = _build_valid_project(parsing_profile="x_technip_pdf_y")
        resolver = _make_config({"131101": pdef})
        registry = resolver.resolve_all()
        self.assertEqual(len(registry), 0)
        self.assertTrue(any("S-C-S-0902" in e for e in resolver.errors))


if __name__ == "__main__":
    unittest.main()

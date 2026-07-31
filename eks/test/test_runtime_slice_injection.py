"""Unit Tests for T1.194 (I265) — RuntimeProjectConfiguration slice injection.

Covers the approved Appendix L design decisions (D1/D2) applied to Phase 1
runtime modules:

- D1 Caller-injection contract: FileScanner / PipelineOrchestrator hold the
  injected ProjectConfigurationRegistry and pass project_code + resolved slice
  to child modules; child modules never hold the registry.
- D2 Phase A registration: FileScanner auto-detects over registry.project_codes
  with no committed project assignment; authoritative assignment in Phase B.
- L.14.7 backward compatibility: no registry → doc_config-derived behaviour.
- FilenameParseResult.project_code surfaces the auto-detected project identity.
- ColumnProcessor code_to_title falls back to the injected slice project name.
"""
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from eks.engine.core.project_definition import (
    ProjectDefinitionResolver,
    ProjectConfigurationRegistry,
    RuntimeProjectConfiguration,
    ProjectDomain,
    DocumentDomain,
)
from eks.engine.core.file_scanner import FileScanner
from eks.engine.core.filename_parser import FilenameParser, FilenameParseResult
from eks.engine.core.pipeline_orchestrator import PipelineOrchestrator
from eks.engine.core.column_processor import EKSColumnProcessor
from eks.engine.core.file_property_parser import FilePropertyExtractor
from eks.engine.core.revision import RevisionManager
from eks.engine.parsers.parser_router import ParserRouter

# ---------------------------------------------------------------------------
# Shared fixtures
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
            },
            "engineering_convention": {
                "drawing_standard": "ISO",
                "numbering_scheme": "TWRP",
                "revision_scheme": "alpha_numeric",
                "tag_format": "ANSI/ISA-5.1",
                "engineering_units": "metric",
                "allowed_disciplines": ["SP", "DS", "PI"],
            },
            "engineering_standards": {"piping": "ASME B31.3"},
            "document_profile": {
                "filename_pattern": "twrp_standard",
                "parser": "technip_pdf",
                "revision": "alpha_numeric",
                "ocr": "default",
                "column_processing": "dcc_aligned",
            },
            "security_profile": {
                "document_classification": "internal",
                "access_policy": "restricted",
                "redaction_policy": "none",
            },
        }
    }
}

FILENAME_PATTERNS = {
    "131101": {
        "description": "FPSO TWRP standard",
        "parser_type": "delimited",
        "separator": "-",
        "min_segments": 4,
        "max_segments": None,
        "segments": [
            {"position": 0, "maps_to": "project_number", "label": "project_number"},
            {"position": 1, "maps_to": "area", "label": "area"},
            {"position": 2, "maps_to": "document_type", "label": "document_type"},
            {"position": 3, "maps_to": "discipline", "label": "discipline"},
        ],
        "output": {
            "document_number_source": "rejoin_segments",
            "fallback_doc_number": "full_stem",
            "fallback_revision": "00",
        },
    },
    "*": {
        "description": "Generic fallback",
        "parser_type": "delimited",
        "separator": "-",
        "min_segments": 1,
        "max_segments": None,
        "segments": [],
        "output": {
            "document_number_source": "full_stem",
            "fallback_doc_number": "full_stem",
            "fallback_revision": "00",
        },
    },
}

DOC_CONFIG = {
    "file_type_registry": [
        {"extension": "pdf", "display_name": "PDF", "parser_class": "eks.engine.parsers.pdf_parser.PDFParser"},
    ],
    "document_type_registry": [
        {"code": "DWG", "label": "Engineering Drawing", "expected_file_types": ["pdf", "dgn"]},
        {"code": "SPC", "label": "Technical Specification", "expected_file_types": ["pdf"]},
    ],
    "filename_patterns": FILENAME_PATTERNS,
}


def _build_registry() -> ProjectConfigurationRegistry:
    resolver = ProjectDefinitionResolver(
        project_definition_config=SAMPLE_PROJECT_DEF_CONFIG,
        doc_config=DOC_CONFIG,
        env_config={"version": "1.9.0"},
    )
    return resolver.resolve_all()


class TestFileScannerRegistryInjection(unittest.TestCase):
    """T1.194.1 — FileScanner D1/D2: registry-driven auto-detect + L.14.7 fallback."""

    def setUp(self):
        self.registry = _build_registry()
        self.config = {}

    def test_project_code_registry_from_registry(self):
        """D2: FilenameParser auto-detect candidates come from registry.project_codes."""
        scanner = FileScanner(
            self.config, doc_config=DOC_CONFIG,
            project_config_registry=self.registry,
        )
        self.assertEqual(
            scanner._parser._project_code_registry,
            ["131101"],
        )

    def test_auto_detect_surfaces_project_code(self):
        """D2: parse() of a matching filename surfaces project_code == 131101."""
        scanner = FileScanner(
            self.config, doc_config=DOC_CONFIG,
            project_config_registry=self.registry,
        )
        result = scanner._parser.parse("131101-AR-DWG-SP-0001.pdf")
        self.assertIsInstance(result, FilenameParseResult)
        self.assertEqual(result.project_code, "131101")
        self.assertEqual(result.project_number, "131101")
        self.assertEqual(result.project_title, "FPSO TWRP")

    def test_backward_compat_without_registry(self):
        """L.14.7: no registry → candidates derived from filename_patterns keys."""
        scanner = FileScanner(self.config, doc_config=DOC_CONFIG)
        self.assertEqual(scanner._parser._project_code_registry, ["131101"])

    def test_registry_code_titles_authoritative(self):
        """Registry project names become project_code_titles (Project Definition wins)."""
        scanner = FileScanner(
            self.config, doc_config=DOC_CONFIG,
            project_config_registry=self.registry,
        )
        titles = scanner._registry_code_titles({})
        self.assertEqual(titles["131101"], "FPSO TWRP")

    def test_fallback_code_returns_none(self):
        """Unmatched filename falls back to '*' → project_code is None (no committed identity)."""
        scanner = FileScanner(
            self.config, doc_config=DOC_CONFIG,
            project_config_registry=self.registry,
        )
        result = scanner._parser.parse("UNKNOWN-ABC-123.pdf")
        self.assertIsNone(result.project_code)


class TestFilenameParserProjectCode(unittest.TestCase):
    """T1.194.2 — FilenameParseResult.project_code surfaces the active code."""

    def setUp(self):
        self.parser = FilenameParser(
            filename_patterns=FILENAME_PATTERNS,
            project_code_registry=["131101"],
            project_code_titles={"131101": "FPSO TWRP"},
        )

    def test_matching_filename_records_code(self):
        result = self.parser.parse("131101-AR-DWG-SP-0001.pdf")
        self.assertEqual(result.project_code, "131101")

    def test_unmatched_filename_no_code(self):
        result = self.parser.parse("WEIRD-FILE.pdf")
        self.assertIsNone(result.project_code)


class TestPipelineOrchestratorSliceInjection(unittest.TestCase):
    """T1.194.3 — Orchestrator is the Phase B caller (D1): registry forwarded + slices."""

    def setUp(self):
        self.registry = _build_registry()
        self.config = {}
        self.stub_doc_registry = object()
        self.orch = PipelineOrchestrator(
            self.config, DOC_CONFIG, self.stub_doc_registry,
            logger=MagicMock(), use_telemetry=False,
            project_config_registry=self.registry,
        )

    def test_registry_forwarded_to_scanner(self):
        self.assertIs(self.orch.scanner.project_config_registry, self.registry)

    def test_slice_for_orchestrator_single_project(self):
        slc = self.orch._slice_for_orchestrator()
        self.assertIn("project", slc)
        self.assertIn("document", slc)
        self.assertEqual(slc["project"].project_code, "131101")

    def test_resolve_project_context_committed(self):
        ctx = self.orch._resolve_project_context("131101")
        self.assertEqual(ctx["project_code"], "131101")
        self.assertIn("project", ctx["config_slice"])
        self.assertEqual(ctx["config_slice"]["document"].filename_pattern, "twrp_standard")

    def test_resolve_project_context_missing_code(self):
        ctx = self.orch._resolve_project_context("999999")
        self.assertIsNone(ctx["project_code"])
        self.assertEqual(ctx["config_slice"], {})

    def test_resolve_project_context_none(self):
        ctx = self.orch._resolve_project_context(None)
        self.assertIsNone(ctx["project_code"])
        self.assertEqual(ctx["config_slice"], {})


class TestColumnProcessorSliceFallback(unittest.TestCase):
    """T1.194.4 — code_to_title falls back to the injected slice project name."""

    COLUMN_CONFIG = {
        "project_title": {
            "processing_phase": "B",
            "is_calculated": True,
            "column_type": "string_column",
            "calculation": {"type": "code_to_title_lookup", "field": "project_number"},
        }
    }

    def test_title_from_slice_when_titles_missing(self):
        proc = EKSColumnProcessor(self.COLUMN_CONFIG)
        slice_ctx = {
            "project": ProjectDomain(
                project_code="131101", project_name="FPSO TWRP", project_type="offshore",
                discipline="multi", client="", contractor="", region="", execution_center="", status="active",
            )
        }
        data = {"project_number": "131101"}
        proc.process("B", data, {"config_slice": slice_ctx})
        self.assertEqual(data["project_title"], "FPSO TWRP")

    def test_title_from_titles_registry_first(self):
        proc = EKSColumnProcessor(self.COLUMN_CONFIG)
        data = {"project_number": "131101"}
        proc.process("B", data, {
            "project_code_titles": {"131101": "Registry Title"},
            "config_slice": {
                "project": ProjectDomain(
                    project_code="131101", project_name="Slice Name", project_type="offshore",
                    discipline="multi", client="", contractor="", region="", execution_center="", status="active",
                )
            },
        })
        self.assertEqual(data["project_title"], "Registry Title")

    def test_from_doc_config_accepts_runtime_slice(self):
        doc_config = {"column_processing": self.COLUMN_CONFIG}
        proc = EKSColumnProcessor.from_doc_config(doc_config, runtime_slice={"project": "x"})
        self.assertEqual(proc.runtime_slice, {"project": "x"})


class TestModuleSliceParams(unittest.TestCase):
    """T1.194.5 — child modules accept the injected slice without holding the registry."""

    def test_revision_manager_accepts_slice(self):
        mock_registry = MagicMock()
        mock_registry.list_documents.return_value = []
        rm = RevisionManager(registry=mock_registry, runtime_slice={"document": None})
        self.assertEqual(rm.runtime_slice, {"document": None})
        result = rm.detect_supersession("DOC-001", "00", runtime_slice={"document": None})
        self.assertIn("has_supersession", result)

    def test_revision_manager_slice_logs_scheme(self):
        from eks.engine.core.project_definition import EngineeringDomain
        slice_doc = {
            "engineering": EngineeringDomain(
                drawing_standard="", numbering_scheme="", revision_scheme="alpha_numeric",
                tag_format="", engineering_units="",
            ),
            "document": DocumentDomain(
                filename_pattern="twrp_standard", parser_profile="",
                revision_scheme="alpha_numeric", ocr_profile="", column_processing="",
            ),
        }
        rm = RevisionManager(registry=object(), runtime_slice=slice_doc)
        self.assertEqual(rm.runtime_slice["document"].revision_scheme, "alpha_numeric")

    def test_file_property_extractor_accepts_slice(self):
        fp = FilePropertyExtractor(None, runtime_slice={"project": "x"})
        self.assertEqual(fp.runtime_slice, {"project": "x"})

    def test_parser_router_accepts_slice(self):
        router = ParserRouter({}, runtime_slice={"parsing": {"profile_id": "x"}})
        self.assertEqual(router.runtime_slice, {"parsing": {"profile_id": "x"}})


class TestRuntimeSliceRegression(unittest.TestCase):
    """T1.194.6 — slice_for() and existing module behaviour remain intact."""

    def test_slice_for_pipeline_unchanged(self):
        cfg = _build_registry().get("131101")
        slc = cfg.slice_for("Pipeline")
        self.assertIn("project", slc)
        self.assertIn("document", slc)
        self.assertNotIn("parsing", slc)

    def test_metadata_dict_excludes_project_code(self):
        parser = FilenameParser(
            filename_patterns=FILENAME_PATTERNS,
            project_code_registry=["131101"],
        )
        result = parser.parse("131101-AR-DWG-SP-0001.pdf")
        md = result.to_metadata_dict()
        self.assertNotIn("project_code", md)
        self.assertEqual(md["project_number"], "131101")


if __name__ == "__main__":
    unittest.main()

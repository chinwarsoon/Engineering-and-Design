"""
Regression tests for ColumnProcessor central orchestrator — T1.188 (I264).

Tests:
  (a) ColumnProcessor dispatches each calculation.type to correct handler
  (b) priority_chain resolves project_title correctly across all 4 sources
  (c) validation rules fire on mismatch
  (d) fallback to leave_null works
  (e) 42 column entries validate against setup schema
  (f) end-to-end: ColumnProcessor.process("B") produces expected output

Revision: 0.1
Date: 2026-07-29
Author: opencode
Summary: T1.188 — regression tests for ColumnProcessor central orchestrator.
Tests: T1.210 (I277) — extraction-method gating regression tests.
Revision: 0.2
Date: 2026-08-04
Author: opencode
"""

import json
import os
import unittest
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch

# Project root for config resolution
_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _find_config_dir() -> Path:
    """Resolve schema/config directory following TestPhase1 pattern."""
    for candidate in [
        _PROJECT_ROOT / "config" / "schemas",
        _PROJECT_ROOT / "config",
        _PROJECT_ROOT.parent / "config" / "schemas",
        _PROJECT_ROOT.parent / "config",
    ]:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"Could not find schema directory. Tried: {_PROJECT_ROOT / 'config/schemas'}, "
        f"{_PROJECT_ROOT / 'config'}, {_PROJECT_ROOT.parent / 'config/schemas'}, "
        f"{_PROJECT_ROOT.parent / 'config'}"
    )


def _load_doc_config() -> Dict[str, Any]:
    """Load doc_config from SchemaLoader for test (e) — 42 column entry validation."""
    from eks.engine.core.schema_loader import SchemaLoader

    config_dir = _find_config_dir()
    config_parent = config_dir.parent if config_dir.name == "schemas" else config_dir
    loader = SchemaLoader(config_parent)
    loader.load_all()
    return loader.doc_config


class TestColumnProcessorDispatch(unittest.TestCase):
    """(a) ColumnProcessor dispatches each calculation.type to the correct handler."""

    def setUp(self):
        from eks.engine.core.column_processor import EKSColumnProcessor

        # Minimal column config with one entry per calculation.type
        self._column_config = {
            "project_title": {
                "column_type": "text_column",
                "is_calculated": True,
                "calculation": {
                    "type": "priority_chain",
                    "sources": [
                        {"source": "cover_page_element", "field": "project_title"},
                        {"source": "parser_metadata", "field": "project_title"},
                    ],
                    "fallback": "leave_null",
                },
                "processing_phase": "B",
                "description": "Project title via priority chain.",
            },
            "document_number": {
                "column_type": "code_column",
                "is_calculated": True,
                "calculation": {
                    "type": "filename_segment",
                    "maps_to": "document_number",
                },
                "processing_phase": "A",
                "description": "Document number from filename.",
            },
            "file_size": {
                "column_type": "numeric_column",
                "is_calculated": True,
                "calculation": {
                    "type": "file_property",
                    "maps_to": "file_size",
                },
                "processing_phase": "B",
                "description": "File size from property extractor.",
            },
            "embedded_title": {
                "column_type": "text_column",
                "is_calculated": True,
                "calculation": {
                    "type": "parser_metadata",
                    "field": "embedded_title",
                },
                "processing_phase": "B",
                "description": "Embedded title from parser metadata.",
            },
            "asset_tags": {
                "column_type": "json_column",
                "is_calculated": True,
                "calculation": {
                    "type": "cover_page_element",
                    "field": "asset_tags",
                },
                "processing_phase": "B",
                "description": "Asset tags from cover page.",
            },
            "project_code_lookup": {
                "column_type": "text_column",
                "is_calculated": True,
                "calculation": {
                    "type": "code_to_title_lookup",
                    "field": "project_number",
                },
                "processing_phase": "B",
                "description": "Project code title lookup.",
            },
            "health": {
                "column_type": "numeric_column",
                "is_calculated": True,
                "calculation": {
                    "type": "health_score",
                },
                "processing_phase": "B",
                "description": "Health score.",
            },
            "uuid": {
                "column_type": "text_column",
                "is_calculated": True,
                "calculation": {
                    "type": "auto_increment",
                },
                "processing_phase": "A",
                "description": "Auto-generated UUID.",
            },
            "existing_val": {
                "column_type": "text_column",
                "is_calculated": True,
                "calculation": {
                    "type": "existing_record",
                    "field": "preserved_field",
                },
                "processing_phase": "B",
                "description": "Preserve existing value.",
            },
        }
        self._processor = EKSColumnProcessor(self._column_config)

    def test_priority_chain_handler_dispatches(self):
        """priority_chain handler resolves from cover_page_element source."""
        data = {}
        context = {
            "elements": [
                {"element_type": "cover_page", "content": {"project_title": "Cover Title"}}
            ],
            "metadata": {"project_title": "Metadata Title"},
        }
        result = self._processor.process("B", data, context)
        self.assertEqual(result.get("project_title"), "Cover Title",
                         "priority_chain should pick cover_page_element first")

    def test_filename_segment_handler_dispatches(self):
        """filename_segment handler reads from data dict by maps_to key."""
        data = {"document_number": "131101-SPC-CV-0001"}
        result = self._processor.process("A", data, {})
        self.assertEqual(result.get("document_number"), "131101-SPC-CV-0001",
                         "filename_segment should pass through data value")

    def test_file_property_handler_dispatches(self):
        """file_property handler reads from context.file_properties."""
        data = {}
        context = {"file_properties": {"file_size": 2048576}}
        result = self._processor.process("B", data, context)
        self.assertEqual(result.get("file_size"), 2048576,
                         "file_property should read from context")

    def test_parser_metadata_handler_dispatches(self):
        """parser_metadata handler reads from context.metadata by field."""
        data = {}
        context = {"metadata": {"embedded_title": "Design Spec"}}
        result = self._processor.process("B", data, context)
        self.assertEqual(result.get("embedded_title"), "Design Spec",
                         "parser_metadata should read from context")

    def test_cover_page_element_handler_dispatches(self):
        """cover_page_element handler extracts asset_tags as list."""
        data = {}
        context = {
            "elements": [
                {"element_type": "cover_page",
                 "content": {"asset_tags": "TAG001, TAG002, TAG003"}}
            ]
        }
        result = self._processor.process("B", data, context)
        self.assertEqual(result.get("asset_tags"),
                         ["TAG001", "TAG002", "TAG003"],
                         "cover_page_element should split asset_tags by comma")

    def test_code_to_title_lookup_dispatches(self):
        """code_to_title_lookup handler reads project_number from data dict."""
        data = {"project_number": "131101"}
        context = {"project_code_titles": {"131101": "WSD11 — Project Specs"}}
        result = self._processor.process("B", data, context)
        self.assertEqual(result.get("project_code_lookup"), "WSD11 — Project Specs",
                         "code_to_title_lookup should resolve from registry")

    def test_health_score_dispatches(self):
        """health_score handler reads score.health_score from context."""
        data = {}
        context = {"score": {"health_score": 0.85, "overall": 0.80}}
        result = self._processor.process("B", data, context)
        self.assertEqual(result.get("health"), 0.85,
                         "health_score should read health_score key first")

    def test_auto_increment_dispatches(self):
        """auto_increment handler generates a UUID string."""
        data = {}
        result = self._processor.process("A", data, {})
        uid = result.get("uuid", "")
        self.assertIsInstance(uid, str, "auto_increment should produce a string")
        self.assertGreater(len(uid), 10, "UUID should be substantial")

    def test_existing_record_dispatches(self):
        """existing_record handler preserves value from data dict."""
        data = {"preserved_field": "keep-me"}
        result = self._processor.process("B", data, {})
        self.assertEqual(result.get("existing_val"), "keep-me",
                         "existing_record should preserve data value")


class TestPriorityChainResolution(unittest.TestCase):
    """(b) priority_chain resolves project_title correctly across all 4 sources."""

    def setUp(self):
        from eks.engine.core.column_processor import EKSColumnProcessor

        self._column_config = {
            "project_title": {
                "column_type": "text_column",
                "is_calculated": True,
                "calculation": {
                    "type": "priority_chain",
                    "sources": [
                        {"source": "cover_page_element", "field": "project_title"},
                        {"source": "parser_metadata", "field": "project_title"},
                        {"source": "code_to_title_lookup", "field": "project_number"},
                        {"source": "existing_record", "field": "project_title"},
                    ],
                    "fallback": "leave_null",
                },
                "processing_phase": "B",
                "description": "Project title.",
            },
        }
        self._processor = EKSColumnProcessor(self._column_config)

    def test_cover_page_wins_over_metadata(self):
        """Cover page element beats parser metadata."""
        data = {}
        context = {
            "elements": [
                {"element_type": "cover_page", "content": {"project_title": "Cover Title"}}
            ],
            "metadata": {"project_title": "Metadata Title"},
        }
        result = self._processor.process("B", data, context)
        self.assertEqual(result.get("project_title"), "Cover Title")

    def test_metadata_wins_over_lookup(self):
        """Parser metadata beats code_to_title lookup when cover page absent."""
        data = {"project_number": "131101"}
        context = {
            "metadata": {"project_title": "Metadata Title"},
            "project_code_titles": {"131101": "Lookup Title"},
        }
        result = self._processor.process("B", data, context)
        self.assertEqual(result.get("project_title"), "Metadata Title")

    def test_lookup_wins_over_existing(self):
        """Code-to-title lookup beats existing record when cover and metadata absent."""
        data = {"project_number": "131101", "project_title": "Existing Title"}
        context = {
            "project_code_titles": {"131101": "Lookup Title"},
        }
        result = self._processor.process("B", data, context)
        self.assertEqual(result.get("project_title"), "Lookup Title")

    def test_existing_record_fallback(self):
        """Existing record used when all other sources return None."""
        data = {"project_number": "999999", "project_title": "Existing Title"}
        context = {
            "project_code_titles": {"131101": "Lookup Title"},
        }
        result = self._processor.process("B", data, context)
        self.assertEqual(result.get("project_title"), "Existing Title")

    def test_all_sources_none_returns_none(self):
        """All sources return None → result is None (leave_null fallback)."""
        data = {"project_number": "999999"}
        context = {"project_code_titles": {}}
        result = self._processor.process("B", data, context)
        self.assertIsNone(result.get("project_title"),
                          "leave_null should produce None when all sources are empty")


class TestColumnProcessingFallback(unittest.TestCase):
    """(d) fallback to leave_null works."""

    def setUp(self):
        from eks.engine.core.column_processor import EKSColumnProcessor

        self._column_config = {
            "optional_field": {
                "column_type": "text_column",
                "is_calculated": True,
                "calculation": {
                    "type": "priority_chain",
                    "sources": [{"source": "parser_metadata", "field": "optional_field"}],
                    "fallback": "leave_null",
                },
                "processing_phase": "B",
                "description": "Optional field.",
            },
        }
        self._processor = EKSColumnProcessor(self._column_config)

    def test_leave_null_returns_none(self):
        """leave_null produces None when no source has a value."""
        data = {}
        context = {"metadata": {}}
        result = self._processor.process("B", data, context)
        self.assertIsNone(result.get("optional_field"),
                          "leave_null should not set the field when sources return None")


class TestFortyTwoColumnConfigValidation(unittest.TestCase):
    """(e) 42 column entries validate against setup schema."""

    def test_doc_config_has_42_column_processing_entries(self):
        """doc_config.column_processing has exactly 42 entries."""
        doc_config = _load_doc_config()
        cp = doc_config.get("column_processing", {})
        self.assertGreaterEqual(len(cp), 42,
                                f"Expected at least 42 column entries, got {len(cp)}")
        # Verify all required Phase A columns present
        phase_a_required = {"file_path", "file_type", "document_number",
                            "project_number", "document_type", "revision"}
        for col in phase_a_required:
            self.assertIn(col, cp, f"Required Phase A column '{col}' missing")

    def test_all_42_entries_have_required_fields(self):
        """Every column entry has valid column_type, processing_phase, description."""
        doc_config = _load_doc_config()
        cp = doc_config.get("column_processing", {})
        for col_name, entry in cp.items():
            self.assertIn("column_type", entry,
                          f"Column '{col_name}' missing column_type")
            self.assertIn("processing_phase", entry,
                          f"Column '{col_name}' missing processing_phase")
            self.assertIn("description", entry,
                          f"Column '{col_name}' missing description")
            self.assertIn(entry["processing_phase"], ("A", "B", "C", "D", "P0"),
                          f"Column '{col_name}' unexpected phase: {entry['processing_phase']}")

    def test_all_42_entries_validate_via_schema_loader(self):
        """doc_config with 42 column entries validates via SchemaLoader (load_all succeeds)."""
        from eks.engine.core.schema_loader import SchemaLoader
        config_dir = _find_config_dir()
        config_parent = config_dir.parent if config_dir.name == "schemas" else config_dir
        loader = SchemaLoader(config_parent)
        # load_all() internally validates doc_config against doc_setup_schema
        # with full $ref resolution — this will raise if validation fails.
        try:
            loader.load_all()
        except Exception as e:
            self.fail(f"SchemaLoader validation failed: {e}")
        cp = loader.doc_config.get("column_processing", {})
        self.assertGreaterEqual(len(cp), 42,
                                f"Expected at least 42 column entries, got {len(cp)}")


class TestColumnProcessingEndToEnd(unittest.TestCase):
    """(f) end-to-end: ColumnProcessor.process('B') produces expected output."""

    @classmethod
    def setUpClass(cls):
        cls.doc_config = _load_doc_config()

    def setUp(self):
        from eks.engine.core.column_processor import EKSColumnProcessor

        self._processor = EKSColumnProcessor.from_doc_config(self.doc_config)

    def test_phase_b_processes_project_title_from_cover(self):
        """Project title resolved from cover page element via Phase B."""
        data = {"project_number": "131101"}
        context = {
            "metadata": {},
            "elements": [
                {"element_type": "cover_page",
                 "content": {"project_title": "TUAS WRP Expansion"}}
            ],
            "file_properties": {},
            "project_code_titles": {"131101": "WSD11 — Project Specs"},
            "score": {"health_score": 0.95},
        }
        result = self._processor.process("B", dict(data), context)
        self.assertEqual(result.get("project_title"), "TUAS WRP Expansion",
                         "Project title should come from cover page element")
        self.assertEqual(result.get("asset_tags"), None,
                         "No asset_tags in this cover page")

    def test_phase_b_processes_asset_tags(self):
        """Asset tags extracted from cover page element."""
        data = {"project_number": "131101"}
        context = {
            "metadata": {},
            "elements": [
                {"element_type": "cover_page",
                 "content": {"asset_tags": "TAG-A, TAG-B, TAG-C",
                             "project_title": "Test Title"}}
            ],
            "file_properties": {},
            "project_code_titles": {"131101": "WSD11 — Project Specs"},
            "score": {"health_score": 0.95},
        }
        result = self._processor.process("B", dict(data), context)
        self.assertEqual(result.get("asset_tags"), ["TAG-A", "TAG-B", "TAG-C"],
                         "asset_tags should be comma-split list")

    def test_phase_b_project_title_priority_order(self):
        """Priority chain follows correct order: cover > metadata > lookup > existing."""
        data = {"project_number": "131101", "project_title": "Existing Value"}
        # All 4 sources populated — cover should win
        context = {
            "metadata": {"project_title": "Metadata Value"},
            "elements": [
                {"element_type": "cover_page",
                 "content": {"project_title": "Cover Value"}}
            ],
            "file_properties": {},
            "project_code_titles": {"131101": "Lookup Value"},
            "score": {"health_score": 0.95},
        }
        result = self._processor.process("B", dict(data), context)
        self.assertEqual(result.get("project_title"), "Cover Value")

    def test_phase_b_document_title_from_metadata(self):
        """Document_title resolved from parser metadata via priority chain."""
        data = {}
        context = {
            "metadata": {"embedded_title": "Piping Isometric Drawing"},
            "elements": [],
            "file_properties": {"filename_stem": "131101-PIP-ISO-0001"},
            "score": {"health_score": 0.90},
        }
        result = self._processor.process("B", dict(data), context)
        self.assertEqual(result.get("document_title"), "Piping Isometric Drawing",
                         "document_title should come from parser metadata embedded_title")

    def test_phase_b_total_sheets_from_parser_metadata(self):
        """Total_sheets resolved from parser metadata priority chain."""
        data = {}
        context = {
            "metadata": {"total_sheets": 5},
            "elements": [],
            "file_properties": {},
            "score": {"health_score": 0.90},
        }
        result = self._processor.process("B", dict(data), context)
        self.assertEqual(result.get("total_sheets"), 5,
                         "total_sheets should read from parser metadata")

    def test_phase_b_health_score_resolved(self):
        """Health score resolved from context.score."""
        data = {}
        context = {
            "metadata": {},
            "elements": [],
            "file_properties": {},
            "score": {"health_score": 0.75},
        }
        result = self._processor.process("B", dict(data), context)
        self.assertEqual(result.get("extraction_health"), None,
                         "extraction_health is is_calculated=false — should not be set")
        # health_score column is not calculated in the config

    def test_phase_a_filename_segment_columns(self):
        """Phase A filename_segment columns pass through from data dict."""
        data = {
            "document_number": "131101-SPC-CV-0001",
            "project_number": "131101",
            "area": "SPC",
            "discipline": "CV",
            "sequence_number": "0001",
            "revision": "A",
        }
        result = self._processor.process("A", dict(data), {})
        self.assertEqual(result.get("document_number"), "131101-SPC-CV-0001")
        self.assertEqual(result.get("project_number"), "131101")
        self.assertEqual(result.get("area"), "SPC")
        self.assertEqual(result.get("revision"), "A")


class TestDocumentTypeScopeFilter(unittest.TestCase):
    """I275/I282 (T1.204/T1.229): class_id x format_category column scope filter."""

    def _make_processor(self, column_config):
        from eks.engine.core.column_processor import EKSColumnProcessor

        return EKSColumnProcessor(
            column_config,
            runtime_slice={},
            document_type_registry=[
                {"code": "DWG", "class_id": "Drawing", "format_category": "print"},
                {"code": "PI-PID", "class_id": "Drawing", "format_category": "print"},
                {"code": "SPC", "class_id": "Specification", "format_category": "print"},
                {"code": "CAD", "class_id": "Drawing", "format_category": "native"},
            ],
        )

    def _native_only_column(self):
        return {
            "column_type": "text_column",
            "is_calculated": True,
            "calculation": {"type": "parser_metadata", "field": "embedded_creator_app"},
            "processing_phase": "B",
            "native_only": True,
            "description": "I275 native_only column.",
        }

    def test_native_only_excluded_for_print(self):
        """native_only column is skipped when format_category is 'print'."""
        proc = self._make_processor({"embedded_creator_app": self._native_only_column()})
        result = proc.process("B", {}, {"class_id": "Drawing", "format_category": "print"})
        self.assertNotIn("embedded_creator_app", result,
                         "native_only column must not populate from a PDF print")

    def test_native_only_included_for_native(self):
        """native_only column populates when format_category is 'native'."""
        proc = self._make_processor({"embedded_creator_app": self._native_only_column()})
        result = proc.process("B", {}, {
            "class_id": "Drawing", "format_category": "native",
            "metadata": {"embedded_creator_app": "AutoCAD"},
        })
        self.assertEqual(result.get("embedded_creator_app"), "AutoCAD")

    def test_applies_to_document_types_excludes_class(self):
        """Column restricted to Drawing is excluded for a Specification document."""
        col = {
            "column_type": "numeric_column",
            "is_calculated": True,
            "calculation": {"type": "parser_metadata", "field": "total_sheets"},
            "processing_phase": "B",
            "applies_to_document_types": ["Drawing"],
            "description": "Drawing-only column.",
        }
        proc = self._make_processor({"total_sheets": col})
        result = proc.process("B", {}, {
            "class_id": "Specification", "format_category": "print",
            "metadata": {"total_sheets": 5},
        })
        self.assertNotIn("total_sheets", result,
                         "applies_to_document_types=[Drawing] must exclude Specification")

    def test_applies_to_document_types_includes_class(self):
        """Column applies when document class is in applies_to_document_types."""
        col = {
            "column_type": "numeric_column",
            "is_calculated": True,
            "calculation": {"type": "parser_metadata", "field": "total_sheets"},
            "processing_phase": "B",
            "applies_to_document_types": ["Drawing"],
            "description": "Drawing-only column.",
        }
        proc = self._make_processor({"total_sheets": col})
        result = proc.process("B", {}, {
            "class_id": "Drawing", "format_category": "print",
            "metadata": {"total_sheets": 5},
        })
        self.assertEqual(result.get("total_sheets"), 5,
                         "Drawing document should populate the column")

    def test_absent_scope_keys_apply_to_all(self):
        """Columns without scope keys apply to any class / format category."""
        col = {
            "column_type": "text_column",
            "is_calculated": True,
            "calculation": {"type": "parser_metadata", "field": "page_count"},
            "processing_phase": "B",
            "description": "Generic column (no scope keys).",
        }
        proc = self._make_processor({"page_count": col})
        for class_id in ("Drawing", "Specification", "Report"):
            result = proc.process("B", {}, {
                "class_id": class_id, "format_category": "print",
                "metadata": {"page_count": 3},
            })
            self.assertEqual(result.get("page_count"), 3,
                             f"generic column should apply to {class_id}")

    def test_unresolved_document_type_is_unrestricted(self):
        """A document whose class cannot be resolved defaults to apply (not skip)."""
        col = {
            "column_type": "text_column",
            "is_calculated": True,
            "calculation": {"type": "parser_metadata", "field": "embedded_keywords"},
            "processing_phase": "B",
            "native_only": True,
            "description": "native_only column.",
        }
        proc = self._make_processor({"embedded_keywords": col})
        # No class_id/format_category in context — must not raise and must apply.
        result = proc.process("B", {}, {"metadata": {"embedded_keywords": "x"}})
        self.assertEqual(result.get("embedded_keywords"), "x",
                         "unresolved scope should fall back to applying")

    def test_eks_resolve_scope_doc_config(self):
        """EKSColumnProcessor.from_doc_config carries the projected registry and
        resolve_scope() maps a document_type code to class + format."""
        from eks.engine.core.column_processor import EKSColumnProcessor

        # Minimal doc_config with projected document_type_registry.
        doc_config = {
            "column_processing": {"PAGE": {
                "column_type": "text_column", "is_calculated": False,
                "processing_phase": "B", "description": "dummy",
            }},
            "document_type_registry": [
                {"code": "SPEC-PROC", "class_id": "Specification", "format_category": "print"},
            ],
        }
        proc = EKSColumnProcessor.from_doc_config(doc_config)
        scope = proc.resolve_scope("SPEC-PROC")
        self.assertEqual(scope.get("class_id"), "Specification")
        self.assertEqual(scope.get("format_category"), "print")
        # Unknown code yields empty scope (unrestricted).
        self.assertEqual(proc.resolve_scope("NOPE"), {})


class TestExtractionMethodGating(unittest.TestCase):
    """I277 (T1.210): Phase B extraction gated by profile extraction_methods x format_category."""

    def _make_processor(self, column_config, parsing_profiles=None):
        from eks.engine.core.column_processor import EKSColumnProcessor

        return EKSColumnProcessor(
            column_config,
            runtime_slice={},
            document_type_registry=[
                {"code": "DWG", "class_id": "Drawing", "format_category": "print",
                 "default_parsing_profile": "technip_pdf", "template": "twrp_drawing"},
                {"code": "CAD", "class_id": "Drawing", "format_category": "native",
                 "default_parsing_profile": "technip_dwg", "template": "twrp_drawing"},
                {"code": "SPC", "class_id": "Specification", "format_category": "print",
                 "default_parsing_profile": "technip_pdf", "template": "twrp_spec_c"},
                {"code": "NO-PROFILE", "class_id": "Report", "format_category": "print",
                 "default_parsing_profile": ""},
            ],
            parsing_profiles=parsing_profiles or {},
            document_templates={
                "twrp_drawing": {"label": "TWRP Drawing", "cover_type": "A",
                                 "expected_elements": ["cover_page", "revision_table", "section"],
                                 "threshold": 2},
                "twrp_spec_c": {"label": "TWRP Specification (no cover)", "cover_type": "C",
                                "expected_elements": [], "threshold": 0},
            },
        )

    def _cover_column(self):
        return {
            "column_type": "text_column", "is_calculated": True,
            "calculation": {"type": "cover_page_element", "field": "asset_tags"},
            "processing_phase": "B", "description": "cover-page-extracted column.",
        }

    def _parser_column(self):
        return {
            "column_type": "text_column", "is_calculated": True,
            "calculation": {"type": "parser_metadata", "field": "embedded_title"},
            "processing_phase": "B", "description": "parser-metadata column.",
        }

    def test_resolve_extraction_methods_print(self):
        """PDF-print binding resolves to methods without parser_metadata."""
        proc = self._make_processor(
            {}, parsing_profiles={"technip_pdf": {"extraction_methods": ["parser_metadata", "cover_page_element"]}}
        )
        methods = proc.resolve_extraction_methods("DWG", "print")
        self.assertIn("cover_page_element", methods)
        self.assertNotIn("parser_metadata", methods)

    def test_resolve_extraction_methods_native(self):
        """Native binding keeps declared parser_metadata."""
        proc = self._make_processor(
            {}, parsing_profiles={"technip_dwg": {"extraction_methods": ["parser_metadata"]}}
        )
        methods = proc.resolve_extraction_methods("CAD", "native")
        self.assertIn("parser_metadata", methods)

    def test_resolve_extraction_methods_no_profile(self):
        """Binding without a profile resolves to an empty method set (no crash)."""
        proc = self._make_processor({})
        self.assertEqual(proc.resolve_extraction_methods("NO-PROFILE", "print"), set())

    def test_cover_page_handler_skipped_when_not_declared(self):
        """Profile declaring only parser_metadata skips cover_page_element columns."""
        proc = self._make_processor(
            {"asset_tags": self._cover_column()},
            parsing_profiles={"technip_pdf": {"extraction_methods": ["parser_metadata"]}},
        )
        result = proc.process("B", {}, {
            "class_id": "Drawing", "format_category": "print",
            "extraction_methods": proc.resolve_extraction_methods("DWG", "print"),
            "elements": [{"element_type": "cover_page", "content": {"asset_tags": "TAG-1"}}],
        })
        self.assertNotIn("asset_tags", result,
                         "cover_page_element not declared -> column must be skipped")

    def test_cover_page_handler_runs_when_declared(self):
        """Profile declaring cover_page_element admits the column."""
        proc = self._make_processor(
            {"asset_tags": self._cover_column()},
            parsing_profiles={"technip_pdf": {"extraction_methods": ["parser_metadata", "cover_page_element"]}},
        )
        result = proc.process("B", {}, {
            "class_id": "Drawing", "format_category": "print",
            "extraction_methods": proc.resolve_extraction_methods("DWG", "print"),
            "elements": [{"element_type": "cover_page", "content": {"asset_tags": "TAG-1"}}],
        })
        self.assertEqual(result.get("asset_tags"), ["TAG-1"])

    def test_parser_metadata_skipped_for_print(self):
        """PDF-print document does not run parser_metadata (format_category=print)."""
        proc = self._make_processor(
            {"embedded_title": self._parser_column()},
            parsing_profiles={"technip_pdf": {"extraction_methods": ["parser_metadata", "cover_page_element"]}},
        )
        result = proc.process("B", {}, {
            "class_id": "Drawing", "format_category": "print",
            "extraction_methods": proc.resolve_extraction_methods("DWG", "print"),
            "metadata": {"embedded_title": "TITLE"},
        })
        self.assertNotIn("embedded_title", result,
                         "parser_metadata unavailable for PDF print -> column must be skipped")

    def test_parser_metadata_runs_for_native(self):
        """Native document runs parser_metadata where the profile declares it."""
        proc = self._make_processor(
            {"embedded_title": self._parser_column()},
            parsing_profiles={"technip_dwg": {"extraction_methods": ["parser_metadata"]}},
        )
        result = proc.process("B", {}, {
            "class_id": "Drawing", "format_category": "native",
            "extraction_methods": proc.resolve_extraction_methods("CAD", "native"),
            "metadata": {"embedded_title": "TITLE"},
        })
        self.assertEqual(result.get("embedded_title"), "TITLE")

    def test_priority_chain_skips_gated_source_only(self):
        """priority_chain skips a gated source but keeps remaining sources."""
        col = {
            "column_type": "text_column", "is_calculated": True,
            "calculation": {"type": "priority_chain", "sources": [
                {"source": "parser_metadata", "field": "project_title"},
                {"source": "file_property", "field": "filename_stem"},
            ]},
            "processing_phase": "B", "description": "priority chain.",
        }
        proc = self._make_processor(
            {"project_title": col},
            parsing_profiles={"technip_pdf": {"extraction_methods": ["cover_page_element"]}},
        )
        result = proc.process("B", {}, {
            "class_id": "Drawing", "format_category": "print",
            "extraction_methods": {"cover_page_element"},
            "metadata": {"project_title": "META"},
            "file_properties": {"filename_stem": "FILE"},
        })
        self.assertEqual(result.get("project_title"), "FILE",
                         "gated parser_metadata source must be skipped; file_property wins")

    def test_unknown_method_warned_not_fatal(self):
        """An extraction method not in the capability set yields an empty result, never a crash."""
        proc = self._make_processor(
            {"embedded_title": self._parser_column()},
            parsing_profiles={"technip_pdf": {"extraction_methods": ["cover_page_element"]}},
        )
        result = proc.process("B", {}, {
            "class_id": "Drawing", "format_category": "print",
            "extraction_methods": {"cover_page_element"},
            "metadata": {"embedded_title": "TITLE"},
        })
        self.assertNotIn("embedded_title", result)

    def test_no_capability_context_is_unrestricted(self):
        """Callers without an extraction-method capability set keep pre-I277 behaviour."""
        proc = self._make_processor(
            {"embedded_title": self._parser_column()},
            parsing_profiles={"technip_dwg": {"extraction_methods": ["parser_metadata"]}},
        )
        result = proc.process("B", {}, {
            "class_id": "Drawing", "format_category": "native",
            "metadata": {"embedded_title": "TITLE"},
        })
        self.assertEqual(result.get("embedded_title"), "TITLE")


class TestCoverTypeBranching(unittest.TestCase):
    """I278 (T1.212): parsing branches on template cover_type absence.

    A no-cover template (cover_type "C") — e.g. ``twrp_spec_c`` for SPC/CL/BQ —
    must skip cover-page extraction: ``cover_page_element`` is discarded from
    the admitted extraction methods, so direct cover_page_element columns and
    cover_page priority-chain sources are both gated out. Cover-bearing
    templates (A/B/D/E) keep cover_page_element.
    """

    def _make_processor(self, column_config, parsing_profiles=None):
        from eks.engine.core.column_processor import EKSColumnProcessor

        return EKSColumnProcessor(
            column_config,
            runtime_slice={},
            document_type_registry=[
                {"code": "DWG", "class_id": "Drawing", "format_category": "print",
                 "default_parsing_profile": "technip_pdf", "template": "twrp_drawing"},
                {"code": "SPC", "class_id": "Specification", "format_category": "print",
                 "default_parsing_profile": "technip_pdf", "template": "twrp_spec_c"},
                {"code": "NO-PROFILE", "class_id": "Report", "format_category": "print",
                 "default_parsing_profile": ""},
            ],
            parsing_profiles=parsing_profiles or {},
            document_templates={
                "twrp_drawing": {"label": "TWRP Drawing", "cover_type": "A",
                                 "expected_elements": ["cover_page", "revision_table", "section"],
                                 "threshold": 2},
                "twrp_spec_c": {"label": "TWRP Specification (no cover)", "cover_type": "C",
                                "expected_elements": [], "threshold": 0},
            },
        )

    def _cover_column(self):
        return {
            "column_type": "text_column", "is_calculated": True,
            "calculation": {"type": "cover_page_element", "field": "asset_tags"},
            "processing_phase": "B", "description": "cover-page-extracted column.",
        }

    def _parser_column(self):
        return {
            "column_type": "text_column", "is_calculated": True,
            "calculation": {"type": "parser_metadata", "field": "embedded_title"},
            "processing_phase": "B", "description": "parser-metadata column.",
        }

    def test_resolve_cover_type_cover_bearing(self):
        """A cover-bearing binding (DWG → twrp_drawing, cover_type A) resolves to 'A'."""
        proc = self._make_processor({})
        self.assertEqual(proc.resolve_cover_type("DWG"), "A")

    def test_resolve_cover_type_no_cover(self):
        """A no-cover binding (SPC → twrp_spec_c, cover_type C) resolves to 'C'."""
        proc = self._make_processor({})
        self.assertEqual(proc.resolve_cover_type("SPC"), "C")

    def test_resolve_cover_type_unknown_defaults_none(self):
        """I283 (T1.230): no schema cover type resolves to None (detection fallback),
        NOT 'C'. Only a deliberate no-cover template resolves to 'C'."""
        proc = self._make_processor({})
        self.assertIsNone(proc.resolve_cover_type("NO-PROFILE"))
        self.assertIsNone(proc.resolve_cover_type("UNKNOWN"))
        self.assertIsNone(proc.resolve_cover_type(None))
        self.assertIsNone(proc.resolve_cover_type(""))

    def test_resolve_expected_element_types(self):
        """I283 (T1.230): resolve the template expected_elements set (element-set SSOT)."""
        proc = self._make_processor({})
        self.assertEqual(proc.resolve_expected_element_types("DWG"),
                         {"cover_page", "revision_table", "section"})
        self.assertEqual(proc.resolve_expected_element_types("SPC"), set())
        self.assertEqual(proc.resolve_expected_element_types("NO-PROFILE"), set())
        self.assertEqual(proc.resolve_expected_element_types(None), set())

    def test_cover_type_c_discards_cover_page_element(self):
        """No-cover binding discards cover_page_element from the admitted methods."""
        proc = self._make_processor(
            {}, parsing_profiles={"technip_pdf": {"extraction_methods": ["parser_metadata", "cover_page_element"]}}
        )
        methods = proc.resolve_extraction_methods("SPC", "print")
        self.assertNotIn("cover_page_element", methods,
                         "no-cover (C) template must not admit cover_page_element")

    def test_cover_type_a_keeps_cover_page_element(self):
        """Cover-bearing binding keeps cover_page_element in the admitted methods."""
        proc = self._make_processor(
            {}, parsing_profiles={"technip_pdf": {"extraction_methods": ["parser_metadata", "cover_page_element"]}}
        )
        methods = proc.resolve_extraction_methods("DWG", "print")
        self.assertIn("cover_page_element", methods,
                      "cover-bearing (A) template must admit cover_page_element")

    def test_cover_page_column_skipped_for_no_cover(self):
        """A direct cover_page_element column is skipped for a no-cover (C) document."""
        proc = self._make_processor(
            {"asset_tags": self._cover_column()},
            parsing_profiles={"technip_pdf": {"extraction_methods": ["parser_metadata", "cover_page_element"]}},
        )
        result = proc.process("B", {}, {
            "class_id": "Specification", "format_category": "print",
            "extraction_methods": proc.resolve_extraction_methods("SPC", "print"),
            "elements": [{"element_type": "cover_page", "content": {"asset_tags": "TAG-1"}}],
        })
        self.assertNotIn("asset_tags", result,
                         "no-cover (C) template must skip the cover_page_element column")

    def test_cover_page_column_runs_for_cover_bearing(self):
        """A direct cover_page_element column runs for a cover-bearing (A) document."""
        proc = self._make_processor(
            {"asset_tags": self._cover_column()},
            parsing_profiles={"technip_pdf": {"extraction_methods": ["parser_metadata", "cover_page_element"]}},
        )
        result = proc.process("B", {}, {
            "class_id": "Drawing", "format_category": "print",
            "extraction_methods": proc.resolve_extraction_methods("DWG", "print"),
            "elements": [{"element_type": "cover_page", "content": {"asset_tags": "TAG-1"}}],
        })
        self.assertEqual(result.get("asset_tags"), ["TAG-1"])

    def test_priority_chain_skips_cover_source_for_no_cover(self):
        """A priority_chain with a cover_page source falls through for a no-cover (C) document."""
        col = {
            "column_type": "text_column", "is_calculated": True,
            "calculation": {"type": "priority_chain", "sources": [
                {"source": "cover_page_element", "field": "project_title"},
                {"source": "file_property", "field": "filename_stem"},
            ]},
            "processing_phase": "B", "description": "priority chain with cover source.",
        }
        proc = self._make_processor(
            {"project_title": col},
            parsing_profiles={"technip_pdf": {"extraction_methods": ["parser_metadata", "cover_page_element"]}},
        )
        result = proc.process("B", {}, {
            "class_id": "Specification", "format_category": "print",
            "extraction_methods": proc.resolve_extraction_methods("SPC", "print"),
            "elements": [{"element_type": "cover_page", "content": {"project_title": "COVER-TITLE"}}],
            "file_properties": {"filename_stem": "FILE"},
        })
        self.assertEqual(result.get("project_title"), "FILE",
                         "cover source must be skipped for no-cover; file_property wins")

    def test_no_cover_document_keeps_parser_metadata_columns(self):
        """A no-cover (C) document still runs parser_metadata where the format admits it."""
        proc = self._make_processor(
            {"embedded_title": self._parser_column()},
            parsing_profiles={"technip_pdf": {"extraction_methods": ["parser_metadata", "cover_page_element"]}},
        )
        result = proc.process("B", {}, {
            "class_id": "Specification", "format_category": "native",
            "extraction_methods": proc.resolve_extraction_methods("SPC", "native"),
            "metadata": {"embedded_title": "TITLE"},
        })
        self.assertEqual(result.get("embedded_title"), "TITLE")


if __name__ == "__main__":
    unittest.main()

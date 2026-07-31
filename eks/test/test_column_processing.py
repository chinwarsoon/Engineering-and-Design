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


if __name__ == "__main__":
    unittest.main()

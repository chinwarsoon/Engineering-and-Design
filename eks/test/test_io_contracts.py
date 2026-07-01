"""Unit Tests for Phase 1.2 — Engine I/O Contracts + UI Contracts.

Tests cover:
- Base contract re-exports from io_contracts.py
- Domain-specific contracts (Discovery, Parser, Health)
- UI contracts (DocumentSelection, PipelineConfig)
- UIContractManager validation and serialization
"""

import unittest
from pathlib import Path
from dataclasses import fields
from eks.engine.core.io_contracts import (
    EngineInput, EngineOutput, ErrorRecord, ValidationResult,
    DiscoveryInput, DiscoveryOutput,
    HealthInput, HealthOutput,
)
from eks.engine.parsers.io_contracts import ParserInput, ParserOutput
from eks.ui.backend.contracts import (
    DocumentSelectionContract,
    PipelineConfigContract,
    QueryRequestContract,
    QueryResponseContract,
)
from eks.ui.backend.contract_manager import (
    UIContractManager,
    _dataclass_to_dict,
)


class TestBaseContracts(unittest.TestCase):
    """T1.2.0.1 — Base contract definitions are re-exported correctly."""

    def test_engine_input_re_exported(self):
        self.assertIs(EngineInput, __import__(
            "eks.engine.core.base", fromlist=["EngineInput"]
        ).EngineInput)

    def test_engine_output_re_exported(self):
        self.assertIs(EngineOutput,
            __import__("eks.engine.core.base", fromlist=["EngineOutput"]).EngineOutput)

    def test_error_record_re_exported(self):
        self.assertIs(ErrorRecord,
            __import__("eks.engine.core.base", fromlist=["ErrorRecord"]).ErrorRecord)

    def test_validation_result_re_exported(self):
        self.assertIs(ValidationResult,
            __import__("eks.engine.core.base", fromlist=["ValidationResult"]).ValidationResult)

    def test_engine_input_has_required_fields(self):
        field_names = {f.name for f in fields(EngineInput)}
        for required in ("run_id", "data_dir", "config_file", "schema_dir", "output_dir"):
            self.assertIn(required, field_names)

    def test_engine_output_has_required_fields(self):
        field_names = {f.name for f in fields(EngineOutput)}
        for required in ("run_id", "status", "output_files", "errors"):
            self.assertIn(required, field_names)

    def test_error_record_to_dict(self):
        err = ErrorRecord("TEST_ERR", "test message")
        d = err.to_dict()
        self.assertEqual(d["error_type"], "TEST_ERR")
        self.assertEqual(d["error_message"], "test message")
        self.assertIn("timestamp", d)

    def test_validation_result_to_error(self):
        vr = ValidationResult(is_valid=False, errors=["bad data"])
        err = vr.to_error()
        self.assertIsInstance(err, ErrorRecord)
        self.assertEqual(err.error_type, "ValidationError")
        self.assertIn("bad data", err.error_message)


class TestDiscoveryContracts(unittest.TestCase):
    """T1.2.0.1 — Discovery-specific contracts."""

    def test_discovery_input_defaults(self):
        inp = DiscoveryInput(
            run_id="test",
            data_dir=Path("/tmp"),
            config_file=Path("config.json"),
            schema_dir=Path("schemas"),
            output_dir=Path("out"),
        )
        self.assertIsNone(inp.file_types)
        self.assertTrue(inp.recursive)

    def test_discovery_input_extends_engine_input(self):
        self.assertIsInstance(DiscoveryInput(run_id="r", data_dir=Path("."),
            config_file=Path("c"), schema_dir=Path("s"), output_dir=Path("o")),
            EngineInput)

    def test_discovery_output_to_dict(self):
        out = DiscoveryOutput(
            run_id="r", status="SUCCESS",
            discovered=10, valid=8, unknown=2, registered=8,
            files=[{"path": "doc.pdf", "type": "pdf"}],
        )
        d = out.to_dict()
        self.assertEqual(d["discovered"], 10)
        self.assertEqual(d["valid"], 8)
        self.assertEqual(d["files"], [{"path": "doc.pdf", "type": "pdf"}])


class TestParserContracts(unittest.TestCase):
    """T1.2.0.2 — Parser-specific contracts."""

    def test_parser_input_has_file_fields(self):
        inp = ParserInput(
            run_id="r", data_dir=Path("."),
            config_file=Path("c"), schema_dir=Path("s"), output_dir=Path("o"),
            file_path="test.pdf", file_type="pdf",
        )
        self.assertEqual(inp.file_path, "test.pdf")
        self.assertEqual(inp.file_type, "pdf")

    def test_parser_output_to_dict(self):
        out = ParserOutput(
            run_id="r", status="SUCCESS",
            content_blocks=[{"type": "text", "content": "hello"}],
            metadata={"title": "Test"},
            confidence=0.95,
        )
        d = out.to_dict()
        self.assertEqual(len(d["content_blocks"]), 1)
        self.assertEqual(d["metadata"]["title"], "Test")
        self.assertEqual(d["confidence"], 0.95)


class TestHealthContracts(unittest.TestCase):
    """T1.2.0.1 — Health scoring-specific contracts."""

    def test_health_input_defaults(self):
        inp = HealthInput(
            run_id="r", data_dir=Path("."),
            config_file=Path("c"), schema_dir=Path("s"), output_dir=Path("o"),
        )
        self.assertIsNone(inp.document)
        self.assertEqual(inp.elements, [])

    def test_health_output_to_dict(self):
        out = HealthOutput(
            run_id="r", status="SUCCESS",
            overall=0.85,
            dimensions={"completeness": 0.9, "confidence": 0.8},
        )
        d = out.to_dict()
        self.assertEqual(d["overall"], 0.85)
        self.assertEqual(d["dimensions"]["completeness"], 0.9)


class TestUIContracts(unittest.TestCase):
    """T1.2.0.3 — UI contract definitions per Appendix G §7."""

    def test_document_selection_contract_defaults(self):
        c = DocumentSelectionContract(data_dir="eks/data")
        self.assertEqual(c.data_dir, "eks/data")
        self.assertIsNone(c.file_types)
        self.assertTrue(c.include_subfolders)
        self.assertEqual(c.max_files, 1000)

    def test_pipeline_config_contract_defaults(self):
        c = PipelineConfigContract()
        self.assertFalse(c.debug)
        self.assertEqual(c.workers, 1)
        self.assertEqual(c.health_threshold, 0.5)
        self.assertFalse(c.skip_parsing)

    def test_document_selection_fields(self):
        field_names = {f.name for f in fields(DocumentSelectionContract)}
        for required in ("data_dir", "file_types", "include_subfolders", "max_files"):
            self.assertIn(required, field_names)

    def test_pipeline_config_fields(self):
        field_names = {f.name for f in fields(PipelineConfigContract)}
        for required in ("debug", "workers", "health_threshold", "skip_parsing"):
            self.assertIn(required, field_names)


class TestQueryContracts(unittest.TestCase):
    """T1.2.0.3 — Query contracts (placeholder for Phase 5)."""

    def test_query_request_contract(self):
        c = QueryRequestContract(query="find pumps", filters={"project": "131101"})
        self.assertEqual(c.query, "find pumps")
        self.assertEqual(c.filters["project"], "131101")
        self.assertEqual(c.max_results, 10)

    def test_query_response_contract(self):
        c = QueryResponseContract(
            answer="3 pumps found",
            sources=[{"doc_number": "DWG-001", "revision": "R0", "page": 5}],
            confidence=0.92,
        )
        self.assertEqual(c.answer, "3 pumps found")
        self.assertEqual(len(c.sources), 1)
        self.assertEqual(c.confidence, 0.92)


class TestContractManager(unittest.TestCase):
    """T1.2.0.4 — UIContractManager validation and serialization."""

    def setUp(self):
        self.mgr = UIContractManager()

    def test_validate_valid_document_selection(self):
        c = DocumentSelectionContract(data_dir="eks/data")
        self.assertTrue(self.mgr.validate_document_selection(c))

    def test_validate_invalid_document_selection_empty_dir(self):
        c = DocumentSelectionContract(data_dir="")
        self.assertFalse(self.mgr.validate_document_selection(c))

    def test_validate_invalid_document_selection_bogus_dir(self):
        c = DocumentSelectionContract(data_dir="/nonexistent/path/12345")
        self.assertFalse(self.mgr.validate_document_selection(c))

    def test_validate_valid_pipeline_config(self):
        c = PipelineConfigContract(workers=2, health_threshold=0.7)
        self.assertTrue(self.mgr.validate_pipeline_config(c))

    def test_validate_invalid_pipeline_config_workers(self):
        c = PipelineConfigContract(workers=0)
        self.assertFalse(self.mgr.validate_pipeline_config(c))

    def test_validate_invalid_pipeline_config_threshold(self):
        c = PipelineConfigContract(health_threshold=1.5)
        self.assertFalse(self.mgr.validate_pipeline_config(c))

    def test_serialize_document_selection_to_dict(self):
        c = DocumentSelectionContract(data_dir="eks/data", file_types=["pdf", "docx"])
        d = self.mgr.serialize_to_json(c)
        self.assertEqual(d["data_dir"], "eks/data")
        self.assertEqual(d["file_types"], ["pdf", "docx"])
        self.assertTrue(d["include_subfolders"])

    def test_serialize_pipeline_config_to_dict(self):
        c = PipelineConfigContract(debug=True, workers=4)
        d = self.mgr.serialize_to_json(c)
        self.assertTrue(d["debug"])
        self.assertEqual(d["workers"], 4)

    def test_deserialize_document_selection(self):
        data = {"data_dir": "eks/data", "file_types": ["pdf"], "include_subfolders": False}
        c = self.mgr.deserialize_from_json(data, "DocumentSelectionContract")
        self.assertIsInstance(c, DocumentSelectionContract)
        self.assertEqual(c.data_dir, "eks/data")
        self.assertEqual(c.file_types, ["pdf"])
        self.assertFalse(c.include_subfolders)

    def test_deserialize_pipeline_config(self):
        data = {"debug": True, "workers": 4, "health_threshold": 0.8}
        c = self.mgr.deserialize_from_json(data, "PipelineConfigContract")
        self.assertIsInstance(c, PipelineConfigContract)
        self.assertTrue(c.debug)
        self.assertEqual(c.workers, 4)

    def test_deserialize_unknown_type_raises(self):
        with self.assertRaises(ValueError) as ctx:
            self.mgr.deserialize_from_json({}, "UnknownType")
        self.assertIn("UnknownType", str(ctx.exception))


class TestDataclassToDict(unittest.TestCase):
    """Helper function _dataclass_to_dict."""

    def test_simple_dataclass(self):
        c = DocumentSelectionContract(data_dir="eks/data")
        d = _dataclass_to_dict(c)
        self.assertEqual(d["data_dir"], "eks/data")

    def test_nested_list(self):
        self.assertEqual(_dataclass_to_dict([1, 2, 3]), [1, 2, 3])

    def test_nested_dict(self):
        self.assertEqual(_dataclass_to_dict({"a": 1}), {"a": 1})


if __name__ == "__main__":
    unittest.main()

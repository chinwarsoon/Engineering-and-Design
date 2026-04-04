#!/usr/bin/env python3
"""Tests for shared schema validation utilities."""

import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / "workflow"

import sys

if str(WORKFLOW_PATH) not in sys.path:
    sys.path.insert(0, str(WORKFLOW_PATH))

from schema_validation import SchemaLoader, SchemaValidator


class SchemaValidationTest(unittest.TestCase):
    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _build_main_schema(self) -> dict:
        return {
            "enhanced_schema": {
                "columns": {
                    "Department": {
                        "required": True,
                        "schema_reference": "department_schema",
                    }
                }
            },
            "schema_references": {
                "department_schema": "department_schema.json"
            },
        }

    def test_schema_validator_reports_ready_for_valid_references(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            schema_path = root / "config" / "schemas" / "dcc_register_enhanced.json"
            self._write_json(schema_path, self._build_main_schema())
            self._write_json(root / "config" / "schemas" / "department_schema.json", {"departments": []})

            results = SchemaValidator(schema_path).validate()

            self.assertTrue(results["ready"])
            self.assertEqual(len(results["references"]), 1)
            self.assertTrue(results["references"][0]["exists"])

    def test_schema_validator_flags_missing_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            schema_path = root / "config" / "schemas" / "dcc_register_enhanced.json"
            self._write_json(schema_path, self._build_main_schema())

            results = SchemaValidator(schema_path).validate()

            self.assertFalse(results["ready"])
            self.assertIn("Referenced schema file not found", results["errors"][0])

    def test_schema_loader_resolves_schema_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            schema_path = root / "config" / "schemas" / "dcc_register_enhanced.json"
            self._write_json(schema_path, self._build_main_schema())
            self._write_json(
                root / "config" / "schemas" / "department_schema.json",
                {"departments": [{"code": "QA", "description": "Quality"}]},
            )

            loader = SchemaLoader()
            loader.set_main_schema_path(schema_path)
            resolved = loader.resolve_schema_dependencies(loader.load_json_file(schema_path))

            self.assertIn("department_schema_data", resolved)
            self.assertEqual(resolved["department_schema_data"]["departments"][0]["code"], "QA")

    def test_schema_validator_detects_circular_dependency_across_schema_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            schema_dir = root / "config" / "schemas"
            main_schema_path = schema_dir / "dcc_register_enhanced.json"

            self._write_json(
                main_schema_path,
                {
                    "enhanced_schema": {"columns": {}},
                    "schema_references": {
                        "schema_a": "schema_a.json"
                    },
                },
            )
            self._write_json(
                schema_dir / "schema_a.json",
                {
                    "schema_references": {
                        "schema_b": "schema_b.json"
                    }
                },
            )
            self._write_json(
                schema_dir / "schema_b.json",
                {
                    "schema_references": {
                        "schema_a": "schema_a.json"
                    }
                },
            )

            results = SchemaValidator(main_schema_path).validate()

            self.assertFalse(results["ready"])
            self.assertTrue(results["dependency_cycle"])
            self.assertIn("Circular schema dependency detected", results["errors"][-1])
            self.assertTrue(any(ref["reference"] == "schema_a" for ref in results["references"]))
            self.assertTrue(any(ref["reference"] == "schema_b" for ref in results["references"]))


if __name__ == "__main__":
    unittest.main()

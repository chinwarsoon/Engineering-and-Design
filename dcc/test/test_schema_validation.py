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

    def _build_lookup_schema_with_field_definitions(self, records: list[dict]) -> dict:
        return {
            "schema_name": "approval_code_schema",
            "data_section": "approval",
            "data_item_type": "object",
            "field_definitions": {
                "code": {
                    "data_type": "string",
                    "required": True,
                    "validation": {
                        "pattern": "^[A-Z]{3,4}$",
                        "min_length": 3,
                        "max_length": 4,
                        "unique": True,
                    },
                },
                "status": {
                    "data_type": "string",
                    "required": True,
                    "validation": {
                        "min_length": 1,
                        "max_length": 100,
                        "unique": True,
                    },
                },
                "aliases": {
                    "data_type": "array[string]",
                    "required": True,
                    "validation": {
                        "min_items": 1,
                        "unique_items": True,
                        "global_unique_items": True,
                    },
                },
            },
            "approval": records,
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

    def test_schema_validator_enforces_field_definitions_on_referenced_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            schema_path = root / "config" / "schemas" / "dcc_register_enhanced.json"
            self._write_json(
                schema_path,
                {
                    "enhanced_schema": {"columns": {}},
                    "schema_references": {
                        "approval_code_schema": "approval_code_schema.json"
                    },
                },
            )
            self._write_json(
                root / "config" / "schemas" / "approval_code_schema.json",
                self._build_lookup_schema_with_field_definitions(
                    [
                        {
                            "code": "app",
                            "status": "Approved",
                            "aliases": ["Approved", "Approved"],
                        },
                        {
                            "code": "APP",
                            "status": "Approved",
                            "aliases": ["Approved"],
                        },
                    ]
                ),
            )

            results = SchemaValidator(schema_path).validate()

            self.assertFalse(results["ready"])
            self.assertTrue(
                any("field 'code' does not match pattern" in error for error in results["errors"])
            )
            self.assertTrue(
                any("field 'aliases' contains duplicate items" in error for error in results["errors"])
            )
            self.assertTrue(
                any("field 'status' duplicates record" in error for error in results["errors"])
            )

    def test_schema_validator_accepts_valid_field_definitions_on_referenced_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            schema_path = root / "config" / "schemas" / "dcc_register_enhanced.json"
            self._write_json(
                schema_path,
                {
                    "enhanced_schema": {"columns": {}},
                    "schema_references": {
                        "approval_code_schema": "approval_code_schema.json"
                    },
                },
            )
            self._write_json(
                root / "config" / "schemas" / "approval_code_schema.json",
                self._build_lookup_schema_with_field_definitions(
                    [
                        {
                            "code": "APP",
                            "status": "Approved",
                            "aliases": ["Approved"],
                        },
                        {
                            "code": "AWC",
                            "status": "Approved with Comments",
                            "aliases": ["Approved as noted"],
                        },
                    ]
                ),
            )

            results = SchemaValidator(schema_path).validate()

            self.assertTrue(results["ready"])

    def test_schema_validator_enforces_scalar_field_definitions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            schema_path = root / "config" / "schemas" / "dcc_register_enhanced.json"
            self._write_json(
                schema_path,
                {
                    "enhanced_schema": {"columns": {}},
                    "schema_references": {
                        "department_schema": "department_schema.json"
                    },
                },
            )
            self._write_json(
                root / "config" / "schemas" / "department_schema.json",
                {
                    "schema_name": "department_choices",
                    "type": "standard_choices",
                    "data_section": "choices",
                    "data_item_type": "scalar",
                    "field_definitions": {
                        "value": {
                            "data_type": "string",
                            "required": True,
                            "validation": {
                                "min_length": 1,
                                "max_length": 50,
                                "unique": True,
                            },
                        }
                    },
                    "choices": ["QAQC", "QAQC", ""],
                },
            )

            results = SchemaValidator(schema_path).validate()

            self.assertFalse(results["ready"])
            self.assertTrue(any("duplicates record" in error for error in results["errors"]))
            self.assertTrue(any("is shorter than 1" in error for error in results["errors"]))


if __name__ == "__main__":
    unittest.main()

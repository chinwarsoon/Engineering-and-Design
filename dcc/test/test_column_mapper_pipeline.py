#!/usr/bin/env python3
"""Tests for enforcing schema-validation before column mapping."""

import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / "workflow"

import sys

if str(WORKFLOW_PATH) not in sys.path:
    sys.path.insert(0, str(WORKFLOW_PATH))

from schema_validation import SchemaValidator, write_validation_status
from universal_column_mapper import UniversalColumnMapper
from universal_document_processor import UniversalDocumentProcessor


class ColumnMapperPipelineTest(unittest.TestCase):
    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _build_main_schema(self) -> dict:
        return {
            "enhanced_schema": {
                "columns": {
                    "Department": {
                        "required": True,
                        "aliases": ["Dept", "Department"],
                        "data_type": "categorical",
                        "schema_reference": "department_schema",
                    }
                }
            },
            "schema_references": {
                "department_schema": "department_schema.json"
            },
        }

    def _build_project(self, root: Path) -> Path:
        schema_path = root / "config" / "schemas" / "dcc_register_enhanced.json"
        self._write_json(schema_path, self._build_main_schema())
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
                "choices": ["QAQC", "Civil"],
            },
        )
        return schema_path

    def test_mapper_requires_schema_validation_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            schema_path = self._build_project(Path(tmp_dir))
            mapper = UniversalColumnMapper()

            with self.assertRaisesRegex(ValueError, "schema_validation.py"):
                mapper.load_main_schema(str(schema_path))

    def test_mapper_loads_schema_after_validation_status_written(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            schema_path = self._build_project(Path(tmp_dir))
            results = SchemaValidator(schema_path).validate()
            write_validation_status(results)

            mapper = UniversalColumnMapper()
            mapper.load_main_schema(str(schema_path))

            self.assertIn("Department", mapper.main_schema["enhanced_schema"]["columns"])
            self.assertIn("department_schema_data", mapper.resolved_schema)

    def test_processor_requires_schema_validation_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            schema_path = self._build_project(Path(tmp_dir))
            processor = UniversalDocumentProcessor()
            processor.schema_file = str(schema_path)

            with self.assertRaisesRegex(ValueError, "schema_validation.py"):
                processor.load_schema()

    def test_processor_loads_schema_after_validation_status_written(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            schema_path = self._build_project(Path(tmp_dir))
            results = SchemaValidator(schema_path).validate()
            write_validation_status(results)

            processor = UniversalDocumentProcessor()
            processor.schema_file = str(schema_path)
            processor.load_schema()

            self.assertIn("enhanced_schema", processor.schema_data)


if __name__ == "__main__":
    unittest.main()

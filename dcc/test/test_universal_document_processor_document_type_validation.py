#!/usr/bin/env python3
"""Regression tests for Document_Type schema-reference validation."""

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / "workflow"

import sys

if str(WORKFLOW_PATH) not in sys.path:
    sys.path.insert(0, str(WORKFLOW_PATH))

from schema_validation import SchemaValidator, write_validation_status
from universal_document_processor import UniversalDocumentProcessor


class UniversalDocumentProcessorDocumentTypeValidationTest(unittest.TestCase):
    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _build_project(self, root: Path) -> Path:
        schema_path = root / "config" / "schemas" / "dcc_register_enhanced.json"
        document_type_schema_path = root / "config" / "schemas" / "document_type_schema.json"

        self._write_json(
            document_type_schema_path,
            {
                "schema_name": "document_type_choices",
                "type": "standard_choices",
                "data_section": "document",
                "field_definitions": {
                    "code": {"data_type": "string", "required": True},
                    "description": {"data_type": "string", "required": True},
                },
                "document": [
                    {"code": "DR", "description": "2D Drawing"},
                ],
            },
        )

        self._write_json(
            schema_path,
            {
                "schema_references": {
                    "document_type_schema": "document_type_schema.json",
                },
                "parameters": {
                    "dynamic_column_creation": {
                        "enabled": True,
                        "default_value": "NA",
                    }
                },
                "enhanced_schema": {
                    "columns": {
                        "Document_Type": {
                            "required": True,
                            "allow_null": False,
                            "is_calculated": False,
                            "create_if_missing": False,
                            "schema_reference": "document_type_schema",
                            "validation": [
                                {
                                    "type": "schema_reference_check",
                                    "reference": "document_type_schema",
                                    "data_section": "document",
                                    "field": "code",
                                }
                            ],
                        }
                    }
                },
            },
        )

        return schema_path

    def test_document_type_warns_when_not_in_document_type_schema_codes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            schema_path = self._build_project(Path(tmp_dir))
            results = SchemaValidator(schema_path).validate()
            write_validation_status(results)

            processor = UniversalDocumentProcessor(str(schema_path))
            processor.load_schema()

            df = pd.DataFrame({"Document_Type": ["ZZ"]})

            with self.assertLogs("universal_document_processor", level="WARNING") as logs:
                processor.process_data(df)

            self.assertTrue(
                any("Schema reference validation failed for Document_Type" in message for message in logs.output)
            )


if __name__ == "__main__":
    unittest.main()

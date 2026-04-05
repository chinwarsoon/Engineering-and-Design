#!/usr/bin/env python3
"""Regression tests for Project_Code schema-reference validation."""

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


class UniversalDocumentProcessorProjectCodeValidationTest(unittest.TestCase):
    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _build_project(self, root: Path) -> Path:
        schema_path = root / "config" / "schemas" / "dcc_register_enhanced.json"
        project_schema_path = root / "config" / "schemas" / "project_schema.json"

        self._write_json(
            project_schema_path,
            {
                "schema_name": "project_choices",
                "type": "standard_choices",
                "data_section": "project",
                "field_definitions": {
                    "code": {"data_type": "string", "required": True},
                    "description": {"data_type": "string", "required": True},
                },
                "project": [
                    {"code": "131242", "description": "TWRP"},
                ],
            },
        )

        self._write_json(
            schema_path,
            {
                "schema_references": {
                    "project_schema": "project_schema.json",
                },
                "parameters": {
                    "dynamic_column_creation": {
                        "enabled": True,
                        "default_value": "NA",
                    }
                },
                "enhanced_schema": {
                    "columns": {
                        "Project_Code": {
                            "required": True,
                            "allow_null": False,
                            "is_calculated": False,
                            "create_if_missing": False,
                            "schema_reference": "project_schema",
                            "validation": {
                                "pattern": "^[0-9]{6}$",
                            },
                        }
                    }
                },
            },
        )

        return schema_path

    def test_project_code_warns_when_not_in_project_schema_codes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            schema_path = self._build_project(Path(tmp_dir))
            results = SchemaValidator(schema_path).validate()
            write_validation_status(results)

            processor = UniversalDocumentProcessor(str(schema_path))
            processor.load_schema()

            df = pd.DataFrame({"Project_Code": ["999999"]})

            with self.assertLogs("universal_document_processor", level="WARNING") as logs:
                processor.process_data(df)

            self.assertTrue(
                any("Schema reference validation failed for Project_Code" in message for message in logs.output)
            )


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Regression tests for Facility_Code schema-reference validation."""

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


class UniversalDocumentProcessorFacilityCodeValidationTest(unittest.TestCase):
    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _build_project(self, root: Path) -> Path:
        schema_path = root / "config" / "schemas" / "dcc_register_enhanced.json"
        facility_schema_path = root / "config" / "schemas" / "facility_schema.json"

        self._write_json(
            facility_schema_path,
            {
                "schema_name": "facility_choices",
                "type": "standard_choices",
                "data_section": "facility",
                "field_definitions": {
                    "prefix": {"data_type": "string", "required": True},
                    "building_description": {"data_type": "string", "required": True},
                },
                "facility": [
                    {"prefix": "WDP00", "building_description": "Domestic Pumping Common"},
                ],
            },
        )

        self._write_json(
            schema_path,
            {
                "schema_references": {
                    "facility_schema": "facility_schema.json",
                },
                "parameters": {
                    "dynamic_column_creation": {
                        "enabled": True,
                        "default_value": "NA",
                    }
                },
                "enhanced_schema": {
                    "columns": {
                        "Facility_Code": {
                            "required": True,
                            "allow_null": False,
                            "is_calculated": False,
                            "create_if_missing": False,
                            "schema_reference": "facility_schema",
                            "validation": [
                                {
                                    "type": "pattern",
                                    "pattern": "^[A-Z0-9-]*$",
                                },
                                {
                                    "type": "schema_reference_check",
                                    "reference": "facility_schema",
                                    "data_section": "facility",
                                    "field": "prefix",
                                },
                            ],
                        }
                    }
                },
            },
        )

        return schema_path

    def test_facility_code_warns_when_not_in_facility_schema_prefixes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            schema_path = self._build_project(Path(tmp_dir))
            results = SchemaValidator(schema_path).validate()
            write_validation_status(results)

            processor = UniversalDocumentProcessor(str(schema_path))
            processor.load_schema()

            df = pd.DataFrame({"Facility_Code": ["BAD99"]})

            with self.assertLogs("universal_document_processor", level="WARNING") as logs:
                processor.process_data(df)

            self.assertTrue(
                any("Schema reference validation failed for Facility_Code" in message for message in logs.output)
            )


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Regression tests for early Row_Index creation in the processor."""

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


class UniversalDocumentProcessorRowIndexTest(unittest.TestCase):
    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _build_schema(self, root: Path) -> Path:
        schema_path = root / "config" / "schemas" / "dcc_register_enhanced.json"
        self._write_json(
            schema_path,
            {
                "parameters": {
                    "dynamic_column_creation": {
                        "enabled": True,
                        "default_value": "NA",
                    }
                },
                "enhanced_schema": {
                    "columns": {
                        "Row_Index": {
                            "required": False,
                            "allow_null": False,
                            "is_calculated": True,
                            "create_if_missing": True,
                            "calculation": {
                                "type": "auto_increment",
                                "method": "generate_row_index",
                            },
                            "validation": {"min_value": 1},
                        },
                        "Department": {
                            "required": True,
                            "allow_null": False,
                            "is_calculated": False,
                            "create_if_missing": False,
                        },
                    }
                },
            },
        )
        return schema_path

    def test_process_data_adds_row_index_first(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            schema_path = self._build_schema(Path(tmp_dir))
            results = SchemaValidator(schema_path).validate()
            write_validation_status(results)

            processor = UniversalDocumentProcessor(str(schema_path))
            processor.load_schema()

            df = pd.DataFrame({"Department": ["Civil", "QAQC", "MEP"]})
            result = processor.process_data(df)

            self.assertEqual(result.columns[0], "Row_Index")
            self.assertEqual(result["Row_Index"].tolist(), [1, 2, 3])
            self.assertEqual(result["Department"].tolist(), ["Civil", "QAQC", "MEP"])


if __name__ == "__main__":
    unittest.main()

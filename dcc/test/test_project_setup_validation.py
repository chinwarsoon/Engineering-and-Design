#!/usr/bin/env python3
"""Tests for the schema-driven project setup validator."""

import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / "workflow"

import sys

if str(WORKFLOW_PATH) not in sys.path:
    sys.path.insert(0, str(WORKFLOW_PATH))

from project_setup_validation import ProjectSetupValidator


class ProjectSetupValidatorTest(unittest.TestCase):
    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _build_schema_document(self) -> dict:
        return {
            "project_setup": [
                {
                    "folders": [
                        {"name": "config/schemas", "required": True, "purpose": "Schemas"},
                        {"name": "workflow", "required": True, "purpose": "Workflow"},
                        {"name": "tools", "required": True, "purpose": "Tools"},
                        {"name": "data", "required": True, "purpose": "Data"},
                    ],
                    "root_files": [
                        {"name": "dcc.yml", "required": True, "purpose": "Environment"}
                    ],
                    "schema_files": [
                        {
                            "filename": "dcc_register_enhanced.json",
                            "required": True,
                            "description": "Main schema",
                        },
                        {
                            "filename": "department_schema.json",
                            "required": True,
                            "description": "Department schema",
                        },
                    ],
                    "workflow_files": [
                        {
                            "filename": "universal_document_processor.py",
                            "required": True,
                            "type": "python_module",
                            "description": "Processor",
                        }
                    ],
                    "tool_files": [
                        {
                            "filename": "project_setup_tools.py",
                            "required": True,
                            "type": "python_script",
                            "description": "Setup tools",
                        }
                    ],
                    "data_files": [
                        {"pattern": "*.xlsx", "required": False, "minimum_count": 1}
                    ],
                    "environment": [
                        {"name": "conda", "required": True, "file": "dcc.yml", "location": "root"}
                    ],
                    "validation_rules": [
                        {"rule": "check_folders", "enabled": True},
                        {"rule": "check_files", "enabled": True},
                        {"rule": "check_schema_refs", "enabled": True},
                    ],
                }
            ]
        }

    def _build_temp_project(self, root: Path, include_data: bool = True) -> Path:
        (root / "config" / "schemas").mkdir(parents=True, exist_ok=True)
        (root / "workflow").mkdir(parents=True, exist_ok=True)
        (root / "tools").mkdir(parents=True, exist_ok=True)
        (root / "data").mkdir(parents=True, exist_ok=True)

        self._write_json(root / "config" / "schemas" / "project_setup.json", self._build_schema_document())
        self._write_json(
            root / "config" / "schemas" / "dcc_register_enhanced.json",
            {
                "schema_references": {
                    "department_schema": "department_schema.json"
                }
            },
        )
        self._write_json(root / "config" / "schemas" / "department_schema.json", {"name": "department"})
        (root / "workflow" / "universal_document_processor.py").write_text("print('ok')\n", encoding="utf-8")
        (root / "tools" / "project_setup_tools.py").write_text("print('ok')\n", encoding="utf-8")
        (root / "dcc.yml").write_text("name: dcc\n", encoding="utf-8")

        if include_data:
            (root / "data" / "sample.xlsx").write_text("placeholder", encoding="utf-8")

        return root

    def test_validator_returns_ready_for_complete_structure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = self._build_temp_project(Path(tmp_dir))
            validator = ProjectSetupValidator(base_path=project_root)

            results = validator.validate()

            self.assertTrue(results["ready"])
            self.assertEqual(results["data_files"][0]["match_count"], 1)
            self.assertTrue(all(item["exists"] for item in results["schema_refs"]))

    def test_validator_flags_missing_required_items(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = self._build_temp_project(Path(tmp_dir), include_data=False)
            (project_root / "workflow" / "universal_document_processor.py").unlink()
            validator = ProjectSetupValidator(base_path=project_root)

            results = validator.validate()

            self.assertFalse(results["ready"])
            self.assertFalse(results["workflow_files"][0]["exists"])
            self.assertFalse(results["data_files"][0]["valid"])
            self.assertFalse(results["data_files"][0]["required"])

    def test_optional_missing_data_pattern_does_not_fail_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = self._build_temp_project(Path(tmp_dir), include_data=False)
            validator = ProjectSetupValidator(base_path=project_root)

            results = validator.validate()

            self.assertTrue(results["ready"])
            self.assertFalse(results["data_files"][0]["valid"])
            self.assertFalse(results["data_files"][0]["required"])


if __name__ == "__main__":
    unittest.main()

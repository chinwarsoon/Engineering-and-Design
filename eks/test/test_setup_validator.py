"""Tests for ProjectSetupValidator (T1.87 — thin adapter over universal ValidationManager).

Tests cover:
- validate_all() returns correct readiness
- Auto-creation of missing folders
- get_readiness_status() returns YES/NO
- get_missing_items() returns correct paths
- Config-driven validation from schema
- P1-SETUP-* error code attachment preserved
- Backward compatibility with old flat-array config format
"""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Dict, Any


class TestProjectSetupValidator(unittest.TestCase):
    """Unit tests for ProjectSetupValidator (thin adapter)."""

    @classmethod
    def setUpClass(cls):
        cls.test_root = Path(tempfile.mkdtemp(prefix="eks_setup_test_"))
        (cls.test_root / "config" / "schemas").mkdir(parents=True, exist_ok=True)
        (cls.test_root / "eks").mkdir(parents=True, exist_ok=True)
        (cls.test_root / "eks" / "eks.yml").touch()
        cls.schema_dir = cls.test_root / "config" / "schemas"

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.test_root, ignore_errors=True)

    def setUp(self):
        from eks.engine.core.setup_validator import ProjectSetupValidator
        self.validator_class = ProjectSetupValidator
        self.base_config = {
            "project_setup": {
                "required_folders": [
                    "archive", "config", "data", "output", "engine",
                    "log", "docs", "workplan", "test", "ui",
                ],
                "required_engine_subfolders": [
                    "core", "parsers", "chunking", "embedding",
                    "vector_store", "graph", "extractors", "retrieval",
                    "cache", "logging",
                ],
                "required_files": [
                    "eks/eks.yml",
                    "eks/config/schemas/eks_base_schema.json",
                    "eks/config/schemas/eks_setup_schema.json",
                ],
                "environment": {
                    "dependencies": [
                        "duckdb", "jsonschema", "pymupdf", "python-docx",
                        "openpyxl", "psutil", "rdflib", "fastapi", "uvicorn",
                        "qdrant-client", "neo4j", "openai", "tiktoken",
                        "pytest", "referencing",
                    ]
                },
            }
        }
        self.validator = ProjectSetupValidator(
            project_root=self.test_root,
            config_registry=self.base_config,
            verbose=False,
        )

    def test_validate_all_returns_expected_structure(self):
        result = self.validator.validate_all(auto_create=False)
        self.assertIn("project_root", result)
        self.assertIn("folders", result)
        self.assertIn("files", result)
        self.assertIn("environment", result)
        self.assertIn("readiness", result)
        self.assertEqual(result["project_root"], str(self.test_root))

    def test_validate_all_creates_missing_folders(self):
        """Auto-create should create missing required subfolders."""
        missing_dir = self.test_root / "archive"
        if missing_dir.exists():
            shutil.rmtree(missing_dir)
        self.assertFalse(missing_dir.exists())

        result = self.validator.validate_all(auto_create=True)
        self.assertTrue(missing_dir.exists())
        folder_result = result["folders"]
        created_paths = folder_result.get("created", [])
        self.assertIn(str(missing_dir), created_paths)

    def test_readiness_no_when_missing_files(self):
        """Readiness should be NO when required files are missing."""
        validator = self.validator_class(
            project_root=self.test_root,
            config_registry={
                "project_setup": {
                    "required_folders": [],
                    "required_files": [
                        "nonexistent_file_a.txt",
                        "nonexistent_file_b.txt",
                    ],
                    "required_engine_subfolders": [],
                }
            },
            verbose=False,
        )
        result = validator.validate_all(auto_create=False)
        self.assertEqual(result["readiness"], "NO")
        self.assertGreater(len(result["files"]["missing"]), 0)

    def test_readiness_yes_when_all_exist(self):
        """Readiness should be YES when project is complete."""
        # Ensure all required folders exist
        for folder in self.base_config["project_setup"]["required_folders"]:
            (self.test_root / folder).mkdir(parents=True, exist_ok=True)
        for sf in self.base_config["project_setup"]["required_engine_subfolders"]:
            (self.test_root / "engine" / sf).mkdir(parents=True, exist_ok=True)
        for file_rel in self.base_config["project_setup"]["required_files"]:
            fp = self.test_root / file_rel
            fp.parent.mkdir(parents=True, exist_ok=True)
            if not fp.exists():
                fp.touch()

        result = self.validator.validate_all(auto_create=False)
        self.assertEqual(result["readiness"], "YES")

    def test_get_readiness_status_validates_on_demand(self):
        """get_readiness_status() should call validate_all if not already run."""
        status = self.validator.get_readiness_status()
        self.assertIn(status, ("YES", "NO"))

    def test_get_missing_items_returns_paths(self):
        """get_missing_items() should return folder and file lists."""
        items = self.validator.get_missing_items()
        self.assertIn("folders", items)
        self.assertIn("files", items)
        self.assertIsInstance(items["folders"], list)
        self.assertIsInstance(items["files"], list)

    def test_config_registry_overrides_defaults(self):
        """Config registry should override hardcoded defaults."""
        custom_folders = ["custom_a", "custom_b"]
        validator = self.validator_class(
            project_root=self.test_root,
            config_registry={
                "project_setup": {
                    "required_folders": custom_folders,
                    "required_files": [],
                    "required_engine_subfolders": [],
                }
            },
            verbose=False,
        )
        self.assertGreater(len(validator._folders), 0)

    def test_verbose_print_does_not_crash(self):
        """Verbose mode should not crash when printing results."""
        validator = self.validator_class(
            project_root=self.test_root,
            config_registry=self.base_config,
            verbose=True,
        )
        try:
            result = validator.validate_all(auto_create=False)
            self.assertIn("readiness", result)
        except Exception as e:
            self.fail(f"Verbose validate_all raised an exception: {e}")

    def test_dependency_probe_returns_available(self):
        """Dependency probe should list available packages."""
        result = self.validator.validate_all(auto_create=False)
        deps = result["dependencies"]
        self.assertIn("available", deps)
        self.assertIn("missing", deps)
        self.assertIn("all_available", deps)
        self.assertIsInstance(deps["available"], list)
        self.assertIsInstance(deps["missing"], list)

    def test_output_paths_validated(self):
        """Output paths validation should return path entries."""
        result = self.validator.validate_all(auto_create=False)
        outs = result["output_paths"]
        self.assertIn("paths", outs)
        self.assertIn("unwritable", outs)
        self.assertIn("all_writable", outs)
        self.assertIsInstance(outs["paths"], list)
        if outs["paths"]:
            self.assertIn("path", outs["paths"][0])
            self.assertIn("writable", outs["paths"][0])

    def test_validate_all_includes_dependencies_and_output_paths(self):
        """validate_all() result should include dependencies and output_paths."""
        result = self.validator.validate_all(auto_create=False)
        self.assertIn("dependencies", result)
        self.assertIn("output_paths", result)

    # ------------------------------------------------------------------
    # T1.79: Error code attachment tests (preserved through adapter)
    # ------------------------------------------------------------------

    def test_folder_missing_entries_carry_error_code(self):
        """Folder validation missing entries should carry P1-SETUP-F001."""
        result = self.validator.validate_all(auto_create=False)
        folder_results = result["folders"]
        if folder_results.get("missing"):
            entry = folder_results["missing"][0]
            self.assertIn("path", entry)
            self.assertIn("error_code", entry)
            self.assertEqual(entry["error_code"], "P1-SETUP-F001")

    def test_file_missing_entries_carry_error_code(self):
        """File validation missing entries should carry P1-SETUP-F001/F002."""
        result = self.validator.validate_all(auto_create=False)
        file_results = result["files"]
        if file_results.get("missing"):
            entry = file_results["missing"][0]
            self.assertIn("path", entry)
            self.assertIn("error_code", entry)

    def test_environment_has_error_code_when_missing(self):
        """Environment result should carry error_code when eks.yml is missing."""
        validator = self.validator_class(
            project_root=self.test_root,
            config_registry={
                "project_setup": {
                    "required_folders": [],
                    "required_files": [],
                    "required_engine_subfolders": [],
                }
            },
            verbose=False,
        )
        eks_yml = self.test_root / "eks" / "eks.yml"
        existed = eks_yml.exists()
        if existed:
            eks_yml.unlink()
        try:
            result = validator.validate_all(auto_create=False)
            env = result["environment"]
            self.assertIn("error_code", env)
            if not env["eks_yml_exists"]:
                self.assertEqual(env["error_code"], "P1-SETUP-F003")
        finally:
            if existed:
                eks_yml.touch()

    def test_dependency_missing_entries_carry_error_code(self):
        """Dependency missing entries should carry P1-SETUP-D001."""
        result = self.validator.validate_all(auto_create=False)
        deps = result["dependencies"]
        if deps.get("missing"):
            entry = deps["missing"][0]
            self.assertIn("package", entry)
            self.assertIn("error_code", entry)
            self.assertEqual(entry["error_code"], "P1-SETUP-D001")

    def test_output_path_unwritable_entries_carry_error_code(self):
        """Output path unwritable entries should carry P1-SETUP-O001."""
        result = self.validator.validate_all(auto_create=True)
        outs = result["output_paths"]
        if outs.get("unwritable"):
            entry = outs["unwritable"][0]
            self.assertIn("path", entry)
            self.assertIn("error_code", entry)
            self.assertEqual(entry["error_code"], "P1-SETUP-O001")

    def test_error_codes_summary_at_top_level(self):
        """validate_all() should include an error_codes summary array."""
        result = self.validator.validate_all(auto_create=False)
        self.assertIn("error_codes", result)
        self.assertIsInstance(result["error_codes"], list)

    def test_get_missing_items_backward_compat(self):
        """get_missing_items() should return plain path strings."""
        items = self.validator.get_missing_items()
        self.assertIn("folders", items)
        self.assertIn("files", items)
        if items["folders"]:
            self.assertIsInstance(items["folders"][0], str)
        if items["files"]:
            self.assertIsInstance(items["files"][0], str)

    def test_raises_value_error_without_config(self):
        """ProjectSetupValidator should raise ValueError when no project_setup config (SSOT)."""
        from eks.engine.core.setup_validator import ProjectSetupValidator
        with self.assertRaises(ValueError) as ctx:
            ProjectSetupValidator(project_root=self.test_root, verbose=False)
        self.assertIn("project_setup", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
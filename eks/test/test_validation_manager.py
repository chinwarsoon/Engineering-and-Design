"""Tests for universal ValidationManager (common/library/utility/validation/manager.py).

Tests cover:
- validate_folders() — DCC-aligned folder entries, auto-create, missing detection
- validate_named_files() — file entries with name_key
- validate_environment() — environment entries with python version
- validate_dependencies() — required/optional/engines probe
- validate_discovery_rules() — rule validation
- validate_project_setup() — full readiness check
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from common.library.utility.validation.manager import ValidationManager


class TestValidationManager(unittest.TestCase):
    """Unit tests for universal ValidationManager."""

    @classmethod
    def setUpClass(cls):
        cls.test_root = Path(tempfile.mkdtemp(prefix="vm_test_"))
        (cls.test_root / "sub").mkdir(parents=True, exist_ok=True)
        (cls.test_root / "sub" / "hello.txt").touch()
        cls.vm = ValidationManager()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.test_root, ignore_errors=True)

    # ------------------------------------------------------------------
    # validate_folders
    # ------------------------------------------------------------------

    def test_validate_folders_all_exist(self):
        folders = [
            {"name": "sub", "required": True, "purpose": "Test subfolder", "auto_created": False},
        ]
        result = self.vm.validate_folders(self.test_root, folders)
        self.assertTrue(result["all_exist"])

    def test_validate_folders_missing_required(self):
        folders = [
            {"name": "nonexistent", "required": True, "purpose": "Does not exist", "auto_created": False},
        ]
        result = self.vm.validate_folders(self.test_root, folders)
        self.assertFalse(result["all_exist"])
        self.assertEqual(len(result["missing"]), 1)
        self.assertEqual(result["missing"][0]["error_code"], "MISSING_FOLDER")

    def test_validate_folders_auto_create(self):
        new_dir = "auto_created_dir"
        folders = [
            {"name": new_dir, "required": True, "purpose": "Auto-created", "auto_created": True},
        ]
        result = self.vm.validate_folders(self.test_root, folders)
        self.assertTrue(result["all_exist"])
        self.assertTrue((self.test_root / new_dir).exists())
        self.assertIn(str(self.test_root / new_dir), result["created"])
        # Cleanup
        shutil.rmtree(self.test_root / new_dir, ignore_errors=True)

    def test_validate_folders_empty(self):
        result = self.vm.validate_folders(self.test_root, [])
        self.assertTrue(result["all_exist"])
        self.assertEqual(len(result["missing"]), 0)

    # ------------------------------------------------------------------
    # validate_named_files
    # ------------------------------------------------------------------

    def test_validate_named_files_found(self):
        entries = [{"name": "hello.txt", "required": True, "purpose": "Test file"}]
        result = self.vm.validate_named_files(self.test_root / "sub", entries)
        self.assertTrue(result["all_exist"])
        self.assertEqual(len(result["missing"]), 0)

    def test_validate_named_files_missing_required(self):
        entries = [{"name": "missing.txt", "required": True, "purpose": "Missing file"}]
        result = self.vm.validate_named_files(self.test_root, entries)
        self.assertFalse(result["all_exist"])
        self.assertEqual(len(result["missing"]), 1)
        self.assertEqual(result["missing"][0]["error_code"], "MISSING_FILE")

    def test_validate_named_files_custom_name_key(self):
        entries = [{"filename": "hello.txt", "required": True, "description": "Custom key test"}]
        result = self.vm.validate_named_files(self.test_root / "sub", entries, name_key="filename")
        self.assertTrue(result["all_exist"])

    def test_validate_named_files_empty(self):
        result = self.vm.validate_named_files(self.test_root, [])
        self.assertTrue(result["all_exist"])
        self.assertEqual(len(result["missing"]), 0)

    # ------------------------------------------------------------------
    # validate_environment
    # ------------------------------------------------------------------

    def test_validate_environment_no_env_entries(self):
        result = self.vm.validate_environment([])
        self.assertTrue(result["all_valid"])
        self.assertEqual(len(result["entries"]), 0)

    def test_validate_environment_python_match(self):
        import sys
        expected = f"{sys.version_info.major}.{sys.version_info.minor}"
        entries = [
            {"name": "test", "required": True, "python_version": expected},
        ]
        result = self.vm.validate_environment(entries)
        self.assertTrue(result["all_valid"])

    def test_validate_environment_python_mismatch(self):
        entries = [
            {"name": "test", "required": True, "python_version": "2.7"},
        ]
        result = self.vm.validate_environment(entries)
        self.assertFalse(result["all_valid"])
        self.assertEqual(result["entries"][0]["error_code"], "PYTHON_MISMATCH")

    # ------------------------------------------------------------------
    # validate_dependencies
    # ------------------------------------------------------------------

    def test_validate_dependencies_empty(self):
        result = self.vm.validate_dependencies({"required": [], "optional": [], "engines": []})
        self.assertTrue(result["all_available"])

    def test_validate_dependencies_available(self):
        result = self.vm.validate_dependencies({"required": ["os", "json"], "optional": [], "engines": []})
        self.assertTrue(result["all_available"])
        self.assertIn("os", result["available"])

    def test_validate_dependencies_missing(self):
        result = self.vm.validate_dependencies({"required": ["this_package_does_not_exist_xyz"], "optional": [], "engines": []})
        self.assertFalse(result["all_available"])
        self.assertEqual(len(result["missing"]), 1)
        self.assertEqual(result["missing"][0]["error_code"], "MISSING_DEPENDENCY")

    # ------------------------------------------------------------------
    # validate_discovery_rules
    # ------------------------------------------------------------------

    def test_validate_discovery_rules_empty(self):
        result = self.vm.validate_discovery_rules([])
        self.assertTrue(result["all_valid"])
        self.assertEqual(len(result["rules"]), 0)

    def test_validate_discovery_rules_dir_exists(self):
        rules = [{"pattern": "*.json", "directory": "sub", "recursive": False, "category": "schemas"}]
        result = self.vm.validate_discovery_rules(rules, self.test_root)
        self.assertTrue(result["all_valid"])
        self.assertEqual(result["rules"][0]["directory_exists"], True)

    def test_validate_discovery_rules_dir_missing(self):
        rules = [{"pattern": "*.json", "directory": "nope", "recursive": False, "category": "schemas"}]
        result = self.vm.validate_discovery_rules(rules, self.test_root)
        self.assertEqual(result["rules"][0]["error_code"], "DISCOVERY_DIR_MISSING")

    # ------------------------------------------------------------------
    # validate_project_setup (full readiness check)
    # ------------------------------------------------------------------

    def test_validate_project_setup_full_pass(self):
        config = {
            "folders": [
                {"name": "sub", "required": True, "purpose": "Existing", "auto_created": False},
            ],
            "root_files": [],
            "schema_files": [],
            "environment": [],
            "dependencies": {"required": ["os"], "optional": [], "engines": []},
            "discovery_rules": [],
        }
        result = self.vm.validate_project_setup(self.test_root, config)
        self.assertEqual(result["readiness"], "YES")

    def test_validate_project_setup_fail(self):
        config = {
            "folders": [
                {"name": "nope", "required": True, "purpose": "Missing", "auto_created": False},
            ],
            "root_files": [],
            "schema_files": [],
            "environment": [],
            "dependencies": {"required": [], "optional": [], "engines": []},
            "discovery_rules": [],
        }
        result = self.vm.validate_project_setup(self.test_root, config)
        self.assertEqual(result["readiness"], "NO")
        self.assertGreater(len(result["error_codes"]), 0)

    def test_validate_project_setup_empty(self):
        result = self.vm.validate_project_setup(self.test_root, {})
        self.assertEqual(result["readiness"], "YES")


if __name__ == "__main__":
    unittest.main()
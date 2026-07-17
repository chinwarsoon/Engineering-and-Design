"""
Unit Tests for T1.98 — Universal Path Resolution (I089) + workflow/tool files (I090).

Revision: 1.0
Date: 2026-07-11
Author: opencode
"""
import json
import unittest
from pathlib import Path

from common.library.paths import resolve_paths, ResolvedPaths
from eks.engine.core.config_registry import ConfigRegistry
from eks.engine.core.setup_validator import ProjectSetupValidator

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = REPO_ROOT / "eks" / "config" / "schemas"


class TestPathResolver(unittest.TestCase):
    def test_resolve_eks_shape(self):
        """EKS global_paths block normalizes directly into ResolvedPaths."""
        config = {
            "global_paths": {
                "data_dir": "data",
                "output_dir": "output",
                "archive_dir": "archive",
                "config_dir": "config",
                "log_dir": "log",
                "eks_root": "eks",
            },
            "discovery_rules": [
                {"pattern": "*_base_schema.json", "directory": "eks/config/schemas", "category": "base_schema"}
            ],
        }
        rp = resolve_paths(REPO_ROOT, config)
        self.assertEqual(rp.source, "eks")
        self.assertEqual(rp.data_dir, "data")
        self.assertEqual(rp.output_dir, "output")
        self.assertEqual(rp.eks_root, "eks")
        self.assertEqual(rp.schema_dir, "eks/config/schemas")

    def test_resolve_dcc_shape(self):
        """DCC folder_creation + discovery_rules normalize into canonical shape."""
        config = {
            "discovery_rules": [
                {"pattern": "*_schema.json", "directory": "config/schemas", "category": "validation_schema"}
            ],
            "folder_creation": {
                "required_directories": [
                    {"name": "output", "auto_create": True, "purpose": "exports"},
                    {"name": "Log", "auto_create": True, "purpose": "logs"},
                ]
            },
        }
        rp = resolve_paths(REPO_ROOT, config)
        self.assertEqual(rp.source, "dcc")
        self.assertEqual(rp.data_dir, "data")  # DCC native default
        self.assertEqual(rp.output_dir, "output")
        self.assertEqual(rp.log_dir, "Log")
        self.assertEqual(rp.eks_root, "")
        self.assertEqual(rp.schema_dir, "config/schemas")

    def test_resolved_paths_absolute(self):
        """resolve() anchors EKS paths under project_root/eks_root."""
        config = {"global_paths": {"data_dir": "data", "output_dir": "output",
                                   "archive_dir": "archive", "config_dir": "config",
                                   "log_dir": "log", "eks_root": "eks"}}
        rp = resolve_paths(REPO_ROOT, config)
        abs_paths = rp.resolve(REPO_ROOT)
        self.assertEqual(abs_paths["data_dir"], REPO_ROOT / "eks" / "data")
        self.assertEqual(abs_paths["config_dir"], REPO_ROOT / "eks" / "config")
        self.assertEqual(abs_paths["schema_dir"], REPO_ROOT / "eks" / "config" / "schemas")
        self.assertEqual(abs_paths["eks_root"], REPO_ROOT / "eks")

    def test_resolved_paths_dcc_absolute(self):
        """resolve() anchors DCC paths directly under project_root."""
        config = {"folder_creation": {"required_directories": [{"name": "output"}]}}
        rp = resolve_paths(REPO_ROOT, config)
        abs_paths = rp.resolve(REPO_ROOT)
        self.assertEqual(abs_paths["data_dir"], REPO_ROOT / "data")
        self.assertEqual(abs_paths["eks_root"], REPO_ROOT)


class TestConfigRegistryPaths(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_reg = ConfigRegistry(REPO_ROOT / "eks" / "config")

    def test_path_properties_routed_through_resolver(self):
        """All six path properties resolve from the universal PathResolver."""
        self.assertEqual(self.config_reg.data_dir, Path("data"))
        self.assertEqual(self.config_reg.output_dir, Path("output"))
        self.assertEqual(self.config_reg.archive_dir, Path("archive"))
        self.assertEqual(self.config_reg.config_dir, Path("config"))
        self.assertEqual(self.config_reg.log_dir, Path("log"))
        self.assertEqual(self.config_reg.eks_root, Path("eks"))

    def test_eks_config_has_workflow_and_tool_files(self):
        """T1.98.6 — config declares workflow_files and tool_files blocks."""
        wf = self.config_reg.get("workflow_files", [])
        tf = self.config_reg.get("tool_files", [])
        self.assertIsInstance(wf, list)
        self.assertIsInstance(tf, list)
        self.assertTrue(any(f.get("filename") for f in wf), "workflow_files empty")
        self.assertTrue(any(f.get("filename") for f in tf), "tool_files empty")


class TestSetupValidatorPipelineFiles(unittest.TestCase):
    def test_workflow_and_tool_files_validated(self):
        """T1.98.7 — setup validator includes workflow_files/tool_files in result."""
        reg = ConfigRegistry(REPO_ROOT / "eks" / "config")
        validator = ProjectSetupValidator(project_root=REPO_ROOT, config_registry=reg)
        result = validator.validate_all(auto_create=True)
        self.assertIn("workflow_files", result)
        self.assertIn("tool_files", result)
        self.assertTrue(result["workflow_files"]["all_exist"], "workflow_files should exist in repo")
        self.assertTrue(result["tool_files"]["all_exist"], "tool_files should exist in repo")


class TestSchemaDeclaresPipelineFiles(unittest.TestCase):
    def test_setup_schema_has_pipeline_file_properties(self):
        """T1.98.6 — eks_setup_schema declares workflow_files and tool_files."""
        setup = json.load(open(CONFIG_DIR / "eks_setup_schema.json", encoding="utf-8"))
        props = setup.get("properties", {})
        self.assertIn("workflow_files", props)
        self.assertIn("tool_files", props)

    def test_base_schema_has_pipeline_file_defs(self):
        """T1.98.6 — eks_base_schema defines workflow_file_entry_def and tool_file_entry_def."""
        base = json.load(open(CONFIG_DIR / "eks_base_schema.json", encoding="utf-8"))
        defs = base.get("definitions", {})
        self.assertIn("workflow_file_entry_def", defs)
        self.assertIn("tool_file_entry_def", defs)


if __name__ == "__main__":
    unittest.main()

"""
Unit Tests for EKS Phase 1 - Foundation
"""
import unittest
import os
import shutil
import json
from typing import List
from pathlib import Path
from eks.engine.core.schema_loader import SchemaLoader, load_eks_config
from eks.engine.core.config_registry import ConfigRegistry
from eks.engine.core.registry import DocumentRegistry
from eks.engine.core.revision import RevisionManager
from eks.engine.logging.logger import EKSLogger
from eks.engine.parsers.pdf_parser import PDFParser
from eks.engine.parsers.xlsx_parser import XLSXParser
from eks.engine.parsers.docx_parser import DOCXParser

class TestPhase1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.test_dir = Path("test_output")
        cls.test_dir.mkdir(exist_ok=True)
        
        # Determine config dir based on cwd
        cls.config_dir = Path("config")
        if not cls.config_dir.exists():
            cls.config_dir = Path("eks/config")
            
        if not cls.config_dir.exists():
            raise FileNotFoundError(f"Could not find config directory at {Path('config').absolute()} or {Path('eks/config').absolute()}")
        
        # Initialize ConfigRegistry first (Singleton)
        cls.config_reg = ConfigRegistry(cls.config_dir)
        
        # Initialize Registry
        cls.registry = DocumentRegistry()
        cls.rev_manager = RevisionManager(cls.registry)

    def test_schema_loader(self):
        """Test schema loading and validation."""
        config = load_eks_config(self.config_dir)
        self.assertIn("project_rules_registry", config)
        self.assertIn("discipline_registry", config)
        self.assertEqual(config["registry"]["type"], "duckdb")

    def test_project_scoped_config(self):
        """Test project-scoped discipline registry lookups."""
        config = ConfigRegistry(self.config_dir)
        
        # Test P123
        disciplines_p123 = config.get_project_disciplines("P123")
        self.assertEqual(len(disciplines_p123), 3)
        self.assertEqual(disciplines_p123[0]["code"], "PI")
        
        # Test P456
        rules_p456 = config.get_project_rules("P456")
        self.assertEqual(rules_p456["allowed_disciplines"], ["CI", "AR"])
        
        # Test non-existent project
        disciplines_unknown = config.get_project_disciplines("UNKNOWN")
        self.assertEqual(disciplines_unknown, [])

    def test_config_registry(self):
        """Test singleton config registry."""
        reg1 = ConfigRegistry(self.config_dir)
        reg2 = ConfigRegistry(self.config_dir)
        self.assertIs(reg1, reg2)
        self.assertEqual(reg1.get("registry.type"), "duckdb")

    def test_document_registry(self):
        """Test metadata DB registration and retrieval."""
        meta = {
            "document_number": "DOC-001",
            "revision": "A",
            "project_title": "Test Project",
            "project_number": "P123",
            "discipline": "PI",
            "document_type": "DWG",
            "status": "APPROVED",
            "file_path": "data/test.pdf"
        }
        doc_id = self.registry.register_document(meta)
        self.assertEqual(doc_id, "DOC-001-A")
        
        # Test Retrieval
        doc = self.registry.get_document("DOC-001")
        self.assertIsNotNone(doc)
        self.assertEqual(doc["revision"], "A")
        self.assertTrue(doc["is_latest"])

        # Test Revision Update
        meta["revision"] = "B"
        self.registry.register_document(meta)
        
        doc_b = self.registry.get_document("DOC-001")
        self.assertEqual(doc_b["revision"], "B")
        self.assertTrue(doc_b["is_latest"])
        
        doc_a = self.registry.get_document("DOC-001", revision="A")
        self.assertFalse(doc_a["is_latest"])

    def test_logger(self):
        """Test tiered logging and debug object."""
        log_file = self.test_dir / "debug_log.json"
        logger = EKSLogger("TestLogger", level=3, debug_file=log_file)
        logger.status("Testing status")
        logger.warning("Testing warning")
        logger.error("Testing error")
        logger.trace_step("Step 1", "Param X", 100, "TestModule")
        logger.save_debug_log()
        
        self.assertTrue(log_file.exists())
        with open(log_file, "r") as f:
            data = json.load(f)
            self.assertEqual(data["project"], "EKS")
            self.assertTrue(len(data["logs"]) >= 3)
            self.assertTrue(len(data["trace_table"]) >= 1)

    def test_revision_manager(self):
        """Test revision history lookup."""
        history = self.rev_manager.get_revision_history("DOC-001")
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["revision"], "B") # Latest first

    # Parsers require real files. For unit testing, we can check if they handle FileNotFoundError
    # or use mock files if possible. 
    # Since I cannot easily create binary PDF/DOCX here without more code, 
    # I'll just test the error handling for now.
    def test_parser_errors(self):
        with self.assertRaises(FileNotFoundError):
            PDFParser("non_existent.pdf")

if __name__ == "__main__":
    unittest.main()

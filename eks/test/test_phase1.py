"""
Unit Tests for EKS Phase 1 - Foundation
"""
import unittest
import os
import shutil
import json
from typing import List
from pathlib import Path
from eks.engine.core import DocumentRegistry
from eks.engine.core.schema_loader import SchemaLoader, load_eks_config
from eks.engine.core.config_registry import ConfigRegistry
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
        
        # Determine config dir based on cwd - prefer eks/config over root config
        cls.config_dir = Path("eks/config")
        if not cls.config_dir.exists():
            cls.config_dir = Path("config")
            
        if not cls.config_dir.exists():
            raise FileNotFoundError(f"Could not find config directory at {Path('config').absolute()} or {Path('eks/config').absolute()}")
        
        # Initialize ConfigRegistry first (Singleton)
        cls.config_reg = ConfigRegistry(cls.config_dir)
        
        # Delete existing DB for clean test state
        db_path = Path("eks/output/eks_registry.db")
        if db_path.exists():
            db_path.unlink()

        # Initialize Registry
        cls.registry = DocumentRegistry()
        cls.rev_manager = RevisionManager(cls.registry)

    def test_schema_loader(self):
        """Test schema loading and validation."""
        config = load_eks_config(self.config_dir)
        self.assertIn("project_rules_registry", config)
        self.assertIn("discipline_registry", config)
        self.assertEqual(config["registry"]["type"], "duckdb")

    def test_ontology_loader_and_alias_resolution(self):
        """Validate ontology config is loaded and alias-aware tag resolution works."""
        registry = ConfigRegistry(self.config_dir)
        self.assertTrue(hasattr(registry, 'ontology'))
        self.assertIn('classes', registry.ontology)
        self.assertIn('relationships', registry.ontology)

        # Canonical tag type mapping should resolve to ontology class name
        self.assertEqual(registry.resolve_ontology_class('AT_EQPMP'), 'PumpTag')
        self.assertEqual(registry.resolve_ontology_class('AT_MOTOR'), 'MotorTag')

        # Aliases should also resolve to the same ontology class name
        self.assertEqual(registry.resolve_ontology_class('AT_PMP'), 'PumpTag')
        self.assertEqual(registry.resolve_ontology_class('AT_MTR'), 'MotorTag')
        self.assertEqual(registry.resolve_ontology_class('at_pump'), 'PumpTag')

        # Values not in ontology should return None
        self.assertIsNone(registry.resolve_ontology_class('AT_UNKNOWN'))

    def test_asset_ontology_class_map_validation(self):
        """Verify ontology_class_map values are valid ontology classes."""
        registry = ConfigRegistry(self.config_dir)
        self.assertIn('ontology_class_map', registry.asset_config)
        self.assertEqual(registry.asset_config['ontology_class_map'].get('AT_EQPMP'), 'PumpTag')
        self.assertEqual(registry.asset_config['ontology_class_map'].get('AT_MOTOR'), 'MotorTag')

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

    def test_remediation_t121_source_type(self):
        """T1.21 G1: Verify source_type is stored and defaults correctly."""
        # Explicit source_type
        self.registry.register_document({
            "document_number": "DOC-X", "revision": "0", "document_type": "SPEC",
            "source_type": "referenced"
        })
        doc = self.registry.get_document("DOC-X")
        self.assertEqual(doc.get("source_type"), "referenced")

        # Default source_type
        self.registry.register_document({
            "document_number": "DOC-Y", "revision": "0", "document_type": "SPEC"
        })
        doc2 = self.registry.get_document("DOC-Y")
        self.assertEqual(doc2.get("source_type"), "ingested")

    def test_remediation_t121_sql_injection_protection(self):
        """T1.21 G2: Verify column allowlist prevents untrusted filters."""
        # Should return all latest (DOC-001, DOC-X, DOC-Y, DOC-META) = 4
        # The bad filter should be ignored
        res = self.registry.list_documents(filters={"1=1; DROP TABLE documents; --": "bad"})
        self.assertEqual(len(res), 4)

    def test_remediation_t121_sql_sorting(self):
        """T1.21 G3: Verify history sorting is handled by SQL."""
        # Register in specific order
        import time
        self.registry.register_document({"document_number": "DOC-SORT", "revision": "A", "document_type": "SPEC"})
        time.sleep(0.01)
        self.registry.register_document({"document_number": "DOC-SORT", "revision": "B", "document_type": "SPEC"})
        
        history = self.rev_manager.get_revision_history("DOC-SORT")
        self.assertEqual(history[0]["revision"], "B")
        self.assertEqual(history[1]["revision"], "A")

    def test_extended_metadata_t122(self):
        """T1.22: Verify extended metadata fields and JSON array storage."""
        meta = {
            "document_number": "DOC-META",
            "revision": "0",
            "document_type": "SPEC",
            "created_by": "John Doe",
            "originator_company": "Engineering Corp",
            "asset_tags": ["P-101", "V-202", "HE-301"],
            "page_count": 42,
            "extract_status": "success",
            "extraction_confidence": 0.95
        }
        self.registry.register_document(meta)
        
        doc = self.registry.get_document("DOC-META")
        self.assertEqual(doc.get("created_by"), "John Doe")
        self.assertEqual(doc.get("originator_company"), "Engineering Corp")
        self.assertEqual(doc.get("page_count"), 42)
        self.assertEqual(doc.get("extract_status"), "success")
        self.assertEqual(doc.get("extraction_confidence"), 0.95)
        
        # Verify JSON array deserialization
        import json
        tags = json.loads(doc.get("asset_tags"))
        self.assertIsInstance(tags, list)
        self.assertEqual(len(tags), 3)
        self.assertIn("P-101", tags)

    def test_parser_errors(self):
        with self.assertRaises(FileNotFoundError):
            PDFParser("non_existent.pdf")

    def test_asset_schema_files_exist(self):
        """T1.20: Verify all 3 asset schema files exist in config directory."""
        for fname in ['eks_asset_base_schema.json', 'eks_asset_setup_schema.json', 'eks_asset_config.json']:
            path = self.config_dir / fname
            self.assertTrue(path.exists(), f"Missing asset schema file: {fname}")

    def test_asset_base_schema_fragments(self):
        """T1.20: Verify eks_asset_base_schema.json contains all 13 fragment definitions."""
        import json
        path = self.config_dir / 'eks_asset_base_schema.json'
        schema = json.load(open(path, encoding='utf-8'))
        defs = schema.get('definitions', {})
        expected = {
            'item_core', 'process_conditions', 'manufacturer', 'asset_lifecycle',
            'control_system', 'piping_connection', 'valve_internals', 'actuator',
            'rotating_equipment', 'instrumentation', 'pipeline_route',
            'specialist_equipment', 'motor_control'
        }
        self.assertEqual(set(defs.keys()), expected, f"Fragment mismatch. Found: {set(defs.keys())}")

    def test_asset_schema_validation(self):
        """T1.20 / R39: Verify eks_asset_config.json validates against eks_asset_setup_schema.json."""
        import json
        from referencing import Registry
        from referencing.jsonschema import DRAFT7
        from jsonschema import validate

        base   = json.load(open(self.config_dir / 'eks_asset_base_schema.json',  encoding='utf-8'))
        setup  = json.load(open(self.config_dir / 'eks_asset_setup_schema.json', encoding='utf-8'))
        config = json.load(open(self.config_dir / 'eks_asset_config.json',        encoding='utf-8'))

        resources = {s['$id']: DRAFT7.create_resource(s) for s in [base, setup] if '$id' in s}
        registry = Registry().with_resources(resources.items())
        validate(instance=config, schema=setup, registry=registry)  # raises on failure

    def test_r39_conditional_fragments(self):
        """R39: Verify conditional_fragments structure is present and well-formed for AT_EQUIP and AT_MOTOR."""
        import json
        config = json.load(open(self.config_dir / 'eks_asset_config.json', encoding='utf-8'))
        registry = config.get('asset_type_registry', {})

        # AT_EQUIP must have conditional_fragments
        at_equip = registry.get('AT_EQUIP', {})
        self.assertIn('conditional_fragments', at_equip, "AT_EQUIP missing conditional_fragments")
        rule = at_equip['conditional_fragments'][0]
        self.assertIn('fragment', rule)
        self.assertIn('when', rule)
        self.assertIn('in', rule)
        self.assertEqual(rule['fragment'], 'specialist_equipment')
        self.assertEqual(rule['when'], 'device_type_code')
        self.assertIsInstance(rule['in'], list)
        self.assertGreater(len(rule['in']), 0)

        # AT_MOTOR must include motor_control in fragments
        at_motor = registry.get('AT_MOTOR', {})
        self.assertIn('motor_control', at_motor.get('fragments', []), "AT_MOTOR missing motor_control fragment")

        # All fragment names in config must exist in base schema definitions
        base = json.load(open(self.config_dir / 'eks_asset_base_schema.json', encoding='utf-8'))
        base_frags = set(base.get('definitions', {}).keys())
        for at_code, entry in registry.items():
            for f in entry.get('fragments', []):
                self.assertIn(f, base_frags, f"{at_code}: fragment '{f}' not in base schema definitions")
            for rule in entry.get('conditional_fragments', []):
                self.assertIn(rule['fragment'], base_frags,
                    f"{at_code}: conditional fragment '{rule['fragment']}' not in base schema definitions")

    def test_ontology_files_exist(self):
        """T1.23/T1.24: Verify ontology schema and config files exist."""
        for fname in ['eks_ontology_base_schema.json', 'eks_ontology_setup_schema.json', 'eks_ontology_config.json']:
            path = self.config_dir / fname
            self.assertTrue(path.exists(), f"Missing ontology file: {fname}")

    def test_ontology_validation(self):
        """T1.23/T1.24: Verify ontology config validates against ontology schema and loader loads ontology files."""
        from eks.engine.core.schema_loader import SchemaLoader
        loader = SchemaLoader(self.config_dir)
        config = loader.load_all()
        self.assertIsInstance(config, dict)
        self.assertTrue(hasattr(loader, 'ontology'))
        self.assertIn('classes', loader.ontology)

    def test_ontology_class_map_references_defined_class(self):
        """T1.27: Verify ontology_class_map only references classes defined in eks_ontology_config.json."""
        import json
        ontology = json.load(open(self.config_dir / 'eks_ontology_config.json', encoding='utf-8'))
        class_names = {c['name'] for c in ontology.get('classes', [])}
        config = json.load(open(self.config_dir / 'eks_asset_config.json', encoding='utf-8'))
        for target_class in config.get('ontology_class_map', {}).values():
            self.assertIn(target_class, class_names,
                f"ontology_class_map references undefined ontology class: {target_class}")

if __name__ == "__main__":
    unittest.main()

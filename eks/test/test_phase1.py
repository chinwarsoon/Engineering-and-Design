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
        
        # Determine schema dir based on cwd — prefer eks/config/schemas (canonical per AGENTS.md)
        cls.config_dir = Path("eks/config/schemas")
        if not cls.config_dir.exists():
            cls.config_dir = Path("eks/config")
        if not cls.config_dir.exists():
            cls.config_dir = Path("config/schemas")
        if not cls.config_dir.exists():
            cls.config_dir = Path("config")

        if not cls.config_dir.exists():
            raise FileNotFoundError(
                f"Could not find schema directory. Tried: eks/config/schemas, eks/config, config/schemas, config "
                f"(resolved from {Path('.').absolute()})"
            )
        
        # Initialize ConfigRegistry — pass the parent config/ dir (SchemaLoader resolves schemas/ internally)
        config_parent = cls.config_dir.parent if cls.config_dir.name == "schemas" else cls.config_dir
        cls.config_reg = ConfigRegistry(config_parent)
        
        # Delete existing DB for clean test state
        db_path = Path("eks/output/eks_registry.db")
        if db_path.exists():
            db_path.unlink()

        # Initialize Registry
        cls.registry = DocumentRegistry()
        cls.rev_manager = RevisionManager(cls.registry)

    def test_schema_loader(self):
        """Test schema loading and validation."""
        config_parent = self.config_dir.parent if self.config_dir.name == "schemas" else self.config_dir
        config = load_eks_config(config_parent)
        self.assertIn("project_rules_registry", config)
        self.assertIn("discipline_registry", config)
        self.assertEqual(config["registry"]["type"], "duckdb")

    def test_ontology_loader_and_alias_resolution(self):
        """Validate ontology config is loaded and alias-aware tag resolution works."""
        config_parent = self.config_dir.parent if self.config_dir.name == "schemas" else self.config_dir
        registry = ConfigRegistry(config_parent)
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
        config_parent = self.config_dir.parent if self.config_dir.name == "schemas" else self.config_dir
        registry = ConfigRegistry(config_parent)
        self.assertIn('ontology_class_map', registry.asset_config)
        self.assertEqual(registry.asset_config['ontology_class_map'].get('AT_EQPMP'), 'PumpTag')
        self.assertEqual(registry.asset_config['ontology_class_map'].get('AT_MOTOR'), 'MotorTag')

    def test_project_scoped_config(self):
        """Test project-scoped config lookups with new fragment references."""
        config_parent = self.config_dir.parent if self.config_dir.name == "schemas" else self.config_dir
        config = ConfigRegistry(config_parent)
        
        # Test project rules (still inline in config)
        rules_131101 = config.get_project_rules("131101")
        self.assertIn("SP", rules_131101["allowed_disciplines"])
        
        rules_131242 = config.get_project_rules("131242")
        self.assertIn("PI", rules_131242["allowed_disciplines"])
        
        # Test non-existent project
        rules_unknown = config.get_project_rules("UNKNOWN")
        self.assertEqual(rules_unknown, {})
        
        # Test fragment registry references exist
        self.assertIn("project_registry", config.config)
        self.assertIn("$ref", config.config["project_registry"])

    def test_config_registry(self):
        """Test singleton config registry."""
        config_parent = self.config_dir.parent if self.config_dir.name == "schemas" else self.config_dir
        reg1 = ConfigRegistry(config_parent)
        reg2 = ConfigRegistry(config_parent)
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
        # Should return all latest documents (at least DOC-001, DOC-X, DOC-Y, DOC-META)
        # The bad filter should be ignored
        res = self.registry.list_documents(filters={"1=1; DROP TABLE documents; --": "bad"})
        self.assertGreaterEqual(len(res), 4)

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
        """T1.51: Verify eks_asset_base_schema.json contains all 14 fragment definitions."""
        import json
        path = self.config_dir / 'eks_asset_base_schema.json'
        schema = json.load(open(path, encoding='utf-8'))
        defs = schema.get('definitions', {})
        expected = {
            'item_core', 'process_conditions', 'manufacturer', 'asset_lifecycle',
            'control_system', 'piping_connection', 'valve_internals', 'actuator',
            'rotating_equipment', 'instrumentation', 'pipeline_route',
            'specialist_equipment', 'motor_control', 'asset_context'
        }
        self.assertEqual(set(defs.keys()), expected, f"Fragment mismatch. Found: {set(defs.keys())}")

    def test_asset_schema_validation(self):
        """T1.20 / R39: Verify eks_asset_config.json validates against eks_asset_setup_schema.json."""
        import json
        from referencing import Registry
        from referencing.jsonschema import DRAFT7
        from jsonschema import validate

        base      = json.load(open(self.config_dir / 'eks_asset_base_schema.json',  encoding='utf-8'))
        setup     = json.load(open(self.config_dir / 'eks_asset_setup_schema.json', encoding='utf-8'))
        config    = json.load(open(self.config_dir / 'eks_asset_config.json',        encoding='utf-8'))
        core_base = json.load(open(self.config_dir / 'eks_base_schema.json',         encoding='utf-8'))

        resources = {s['$id']: DRAFT7.create_resource(s) for s in [base, setup, core_base] if '$id' in s}
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
        config_parent = self.config_dir.parent if self.config_dir.name == "schemas" else self.config_dir
        loader = SchemaLoader(config_parent)
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

    def test_doc_schema_files_exist(self):
        """T1.34: Verify all 3 document schema files exist."""
        for fname in ['eks_doc_base_schema.json', 'eks_doc_setup_schema.json', 'eks_doc_config.json']:
            path = self.config_dir / fname
            self.assertTrue(path.exists(), f"Missing document schema file: {fname}")

    def test_doc_schema_base_definitions(self):
        """T1.34: Verify doc base schema has required definitions."""
        import json
        base = json.load(open(self.config_dir / 'eks_doc_base_schema.json', encoding='utf-8'))
        defs = base.get('definitions', {})
        for expected_def in ['document_metadata_def', 'project_metadata_def', 'document_element_def']:
            self.assertIn(expected_def, defs, f"Missing definition: {expected_def}")

    def test_doc_schema_validation(self):
        """T1.34: Verify doc config validates against doc setup schema."""
        from eks.engine.core.schema_loader import SchemaLoader
        config_parent = self.config_dir.parent if self.config_dir.name == "schemas" else self.config_dir
        loader = SchemaLoader(config_parent)
        config = loader.load_all()
        self.assertIsInstance(config, dict)
        self.assertTrue(hasattr(loader, 'doc_config'))
        self.assertIn('ontology_triggers', loader.doc_config)
        self.assertIn('health_scoring', loader.doc_config)
        self.assertIn('element_expectations', loader.doc_config)
        self.assertEqual(len(loader.doc_config['health_scoring']['dimensions']), 6)

    def test_doc_schema_no_doc_defs_in_pipeline_base(self):
        """T1.34: Verify pipeline base schema no longer contains document definitions."""
        import json
        base = json.load(open(self.config_dir / 'eks_base_schema.json', encoding='utf-8'))
        defs = base.get('definitions', {})
        self.assertNotIn('document_metadata_def', defs, "document_metadata_def should not be in pipeline base schema")
        self.assertNotIn('project_metadata_def', defs, "project_metadata_def should not be in pipeline base schema")

    def test_doc_element_def_has_required_fields(self):
        """T1.34: Verify document_element_def has all 7 columns from registry.py."""
        import json
        base = json.load(open(self.config_dir / 'eks_doc_base_schema.json', encoding='utf-8'))
        el_def = base['definitions']['document_element_def']
        props = el_def.get('properties', {})
        for expected_field in ['doc_id', 'element_type', 'element_id', 'title', 'content', 'confidence', 'source']:
            self.assertIn(expected_field, props, f"document_element_def missing field: {expected_field}")
        required = el_def.get('required', [])
        self.assertIn('doc_id', required)
        self.assertIn('element_type', required)
        self.assertIn('source', required)

    def test_doc_type_enum_matches_ontology(self):
        """T1.35: Verify document_type_code enum values match ontology document_type_mapping."""
        import json
        base = json.load(open(self.config_dir / 'eks_doc_base_schema.json', encoding='utf-8'))
        ontology = json.load(open(self.config_dir / 'eks_ontology_config.json', encoding='utf-8'))
        enum_values = set(base['definitions']['document_type_code']['enum'])
        mapping_values = set()
        for cls in ontology.get('classes', []):
            dtm = cls.get('document_type_mapping')
            if dtm:
                mapping_values.add(dtm)
        self.assertEqual(enum_values, mapping_values,
            f"doc type enum {enum_values} != ontology mapping {mapping_values}")

    def test_file_type_registry_completeness(self):
        """T1.35: Verify file_type_registry has all 5 expected entries."""
        config = json.load(open(self.config_dir / 'eks_doc_config.json', encoding='utf-8'))
        reg = config.get('file_type_registry', [])
        self.assertEqual(len(reg), 5)
        extensions = {e['extension'] for e in reg}
        self.assertEqual(extensions, {'pdf', 'dgn', 'docx', 'xlsx', 'dwg'})
        for entry in reg:
            self.assertIn('parser_class', entry)
            self.assertIn('display_name', entry)

    def test_element_type_registry_completeness(self):
        """T1.35: Verify element_type_registry has all 8 expected entries."""
        config = json.load(open(self.config_dir / 'eks_doc_config.json', encoding='utf-8'))
        reg = config.get('element_type_registry', [])
        self.assertEqual(len(reg), 8)
        ets = {e['element_type'] for e in reg}
        expected = {'cover_page', 'revision_table', 'section', 'table', 'image', 'link', 'legend', 'note'}
        self.assertEqual(ets, expected)

    def test_element_expectations_keys_match_doc_type_registry(self):
        """T1.35: Verify element_expectations keys match document_type_registry codes."""
        config = json.load(open(self.config_dir / 'eks_doc_config.json', encoding='utf-8'))
        doc_type_codes = {e['code'] for e in config.get('document_type_registry', [])}
        expect_keys = set(config.get('element_expectations', {}).keys())
        self.assertEqual(expect_keys, doc_type_codes,
            f"expectation keys {expect_keys} != doc type codes {doc_type_codes}")

    def test_doc_metadata_has_new_fields(self):
        """T1.35: Verify doc metadata has file_path, ingested_at, file_type fields."""
        import json
        base = json.load(open(self.config_dir / 'eks_doc_base_schema.json', encoding='utf-8'))
        meta_def = base['definitions']['document_metadata_def']
        props = meta_def.get('properties', {})
        for field in ['file_path', 'ingested_at', 'file_type']:
            self.assertIn(field, props, f"document_metadata_def missing field: {field}")

    def test_doc_element_def_has_element_type_enum(self):
        """T1.35: Verify document_element_def element_type uses the element_type_code enum."""
        import json
        base = json.load(open(self.config_dir / 'eks_doc_base_schema.json', encoding='utf-8'))
        el_def = base['definitions']['document_element_def']
        et_prop = el_def['properties']['element_type']
        self.assertIn('$ref', et_prop,
            "element_type should use $ref to element_type_code enum")
        self.assertIn('element_type_code', et_prop['$ref'],
            "$ref should reference element_type_code definition")

    def test_schema_to_ddl_documents_creates_table(self):
        """T1.36: SchemaToDDL generates valid CREATE TABLE for documents."""
        from eks.engine.core.schema_to_ddl import SchemaToDDL
        schema = SchemaToDDL.load_doc_base_schema(self.config_dir)
        gen = SchemaToDDL(schema)
        ddl = gen.generate_documents_ddl()
        self.assertIn("CREATE TABLE IF NOT EXISTS documents", ddl)
        self.assertIn("id VARCHAR PRIMARY KEY", ddl)
        self.assertIn("document_type", ddl)
        self.assertIn("file_type", ddl)
        self.assertIn("ingested_at TIMESTAMP", ddl)
        self.assertIn("extract_status", ddl)

    def test_schema_to_ddl_document_elements(self):
        """T1.36: SchemaToDDL generates valid CREATE TABLE for document_elements."""
        from eks.engine.core.schema_to_ddl import SchemaToDDL
        schema = SchemaToDDL.load_doc_base_schema(self.config_dir)
        gen = SchemaToDDL(schema)
        ddl = gen.generate_document_elements_ddl()
        self.assertIn("CREATE TABLE IF NOT EXISTS document_elements", ddl)
        self.assertIn("doc_id", ddl)
        self.assertIn("element_type", ddl)
        self.assertIn("source", ddl)

    def test_schema_to_ddl_indexes(self):
        """T1.36: SchemaToDDL generates indexes for document_elements."""
        from eks.engine.core.schema_to_ddl import SchemaToDDL
        schema = SchemaToDDL.load_doc_base_schema(self.config_dir)
        gen = SchemaToDDL(schema)
        indexes = gen.generate_indexes()
        self.assertEqual(len(indexes), 2)
        self.assertIn("idx_elements_doc_id", indexes[0])
        self.assertIn("idx_elements_type", indexes[1])

    def test_schema_to_ddl_migration_detects_missing_columns(self):
        """T1.36: SchemaToDDL.generate_migration_ddl finds missing columns."""
        from eks.engine.core.schema_to_ddl import SchemaToDDL
        schema = SchemaToDDL.load_doc_base_schema(self.config_dir)
        gen = SchemaToDDL(schema)
        existing = {"id", "source_type", "document_type", "document_number", "revision"}
        stmts = gen.generate_migration_ddl("documents", existing)
        self.assertGreater(len(stmts), 0)
        stmts_text = " ".join(stmts)
        self.assertIn("ALTER TABLE documents ADD COLUMN", stmts_text)

    def test_schema_to_ddl_no_migration_for_complete_schema(self):
        """T1.36: No migration when all columns already exist."""
        from eks.engine.core.schema_to_ddl import SchemaToDDL
        schema = SchemaToDDL.load_doc_base_schema(self.config_dir)
        gen = SchemaToDDL(schema)
        all_cols = set()
        project_props = gen.definitions.get("project_metadata_def", {}).get("properties", {})
        document_props = gen.definitions.get("document_metadata_def", {}).get("properties", {})
        all_cols.update(project_props.keys())
        all_cols.update(document_props.keys())
        all_cols.add("id")
        stmts = gen.generate_migration_ddl("documents", all_cols)
        self.assertEqual(len(stmts), 0)

    def test_registry_sync_schema(self):
        """T1.36: DocumentRegistry.sync_schema returns correct summary."""
        summary = self.registry.sync_schema()
        self.assertIn("documents_added", summary)
        self.assertIn("document_elements_added", summary)
        self.assertIn("indexes_created", summary)
        self.assertIsInstance(summary["documents_added"], list)
        self.assertIsInstance(summary["document_elements_added"], list)

    def test_registry_column_allowlist_from_schema(self):
        """T1.36: COLUMN_ALLOWLIST is derived from JSON schema."""
        allowlist = self.registry.COLUMN_ALLOWLIST
        self.assertIn("id", allowlist)
        self.assertIn("document_type", allowlist)
        self.assertIn("file_type", allowlist)
        self.assertIn("extract_status", allowlist)
        self.assertIn("project_title", allowlist)

    def test_schema_to_ddl_timestamp_format(self):
        """T1.36: ingested_at is TIMESTAMP not VARCHAR."""
        from eks.engine.core.schema_to_ddl import SchemaToDDL
        schema = SchemaToDDL.load_doc_base_schema(self.config_dir)
        gen = SchemaToDDL(schema)
        ddl = gen.generate_documents_ddl()
        self.assertIn("ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP", ddl)

    def test_file_scanner_discovers_files(self):
        """T1.37: FileScanner discovers files with recognized extensions."""
        from eks.engine.core.file_scanner import FileScanner
        config_parent = self.config_dir.parent if self.config_dir.name == "schemas" else self.config_dir
        loader = SchemaLoader(config_parent)
        config = loader.load_all()
        scanner = FileScanner(config, doc_config=loader.doc_config)

        test_dir = Path("test_output/scan_test")
        test_dir.mkdir(parents=True, exist_ok=True)
        (test_dir / "doc1.pdf").touch()
        (test_dir / "doc2.dgn").touch()
        (test_dir / "doc3.txt").touch()
        (test_dir / "subdir").mkdir(exist_ok=True)
        (test_dir / "subdir" / "doc4.pdf").touch()

        discovered = scanner.scan(test_dir)
        self.assertEqual(len(discovered), 3)
        file_types = {d["file_type"] for d in discovered}
        self.assertEqual(file_types, {"pdf", "dgn"})
        self.assertIn("doc4.pdf", [d["file_name"] for d in discovered])

    def test_file_scanner_validate_types(self):
        """T1.37: FileScanner validates file types against document_type_registry."""
        from eks.engine.core.file_scanner import FileScanner
        config_parent = self.config_dir.parent if self.config_dir.name == "schemas" else self.config_dir
        loader = SchemaLoader(config_parent)
        config = loader.load_all()
        scanner = FileScanner(config, doc_config=loader.doc_config)

        test_dir = Path("test_output/scan_validate")
        test_dir.mkdir(parents=True, exist_ok=True)
        (test_dir / "good.pdf").touch()
        (test_dir / "also_good.xlsx").touch()

        discovered = scanner.scan(test_dir)
        valid, unknown = scanner.validate_file_types(discovered)
        self.assertEqual(len(valid), 2)
        self.assertEqual(len(unknown), 0)

    def test_file_scanner_build_placeholder(self):
        """T1.37: FileScanner builds placeholder metadata from filename."""
        from eks.engine.core.file_scanner import FileScanner
        config_parent = self.config_dir.parent if self.config_dir.name == "schemas" else self.config_dir
        loader = SchemaLoader(config_parent)
        config = loader.load_all()
        scanner = FileScanner(config, doc_config=loader.doc_config)

        file_info = {
            "file_path": "/data/DWG-001-A.pdf",
            "file_name": "DWG-001-A.pdf",
            "file_type": "pdf",
            "display_name": "PDF Document",
            "parser_class": "eks.engine.parsers.pdf_parser.PDFParser",
        }
        meta = scanner.build_placeholder_metadata(file_info)
        self.assertEqual(meta["document_number"], "DWG-001")
        self.assertEqual(meta["revision"], "A")
        self.assertEqual(meta["file_type"], "pdf")
        self.assertEqual(meta["extract_status"], "pending")
        self.assertEqual(meta["source_type"], "ingested")

    def test_file_scanner_register_placeholders(self):
        """T1.37: FileScanner registers placeholder documents in registry."""
        from eks.engine.core.file_scanner import FileScanner
        config_parent = self.config_dir.parent if self.config_dir.name == "schemas" else self.config_dir
        loader = SchemaLoader(config_parent)
        config = loader.load_all()
        scanner = FileScanner(config, doc_config=loader.doc_config)

        test_dir = Path("test_output/scan_register")
        test_dir.mkdir(parents=True, exist_ok=True)
        (test_dir / "FS-TEST-01-A.pdf").touch()

        discovered = scanner.scan(test_dir)
        valid, _ = scanner.validate_file_types(discovered)
        count = scanner.register_placeholders(valid, self.registry)
        self.assertGreaterEqual(count, 1)

        doc = self.registry.get_document("FS-TEST-01", revision="A")
        self.assertIsNotNone(doc)
        self.assertEqual(doc["extract_status"], "pending")
        self.assertEqual(doc["file_type"], "pdf")

    def test_parser_router_lookup(self):
        """T1.38: ParserRouter looks up parser class for file type."""
        from eks.engine.parsers.parser_router import ParserRouter
        config_parent = self.config_dir.parent if self.config_dir.name == "schemas" else self.config_dir
        loader = SchemaLoader(config_parent)
        config = loader.load_all()
        router = ParserRouter(loader.doc_config)

        self.assertIsNotNone(router.get_parser_class("pdf"))
        self.assertIsNotNone(router.get_parser_class("dgn"))
        self.assertIsNotNone(router.get_parser_class("docx"))
        self.assertIsNotNone(router.get_parser_class("xlsx"))
        self.assertIsNone(router.get_parser_class("xyz"))

    def test_parser_router_instantiate(self):
        """T1.38: ParserRouter instantiates parser class from path."""
        from eks.engine.parsers.parser_router import ParserRouter
        config_parent = self.config_dir.parent if self.config_dir.name == "schemas" else self.config_dir
        loader = SchemaLoader(config_parent)
        config = loader.load_all()
        router = ParserRouter(loader.doc_config)

        test_file = Path("test_output/test_router.dgn")
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.touch()
        parser = router.instantiate_parser(
            "eks.engine.parsers.dgn_parser.DGNParserStub",
            str(test_file)
        )
        self.assertIsNotNone(parser)
        test_file.unlink()

    def test_parser_router_route_no_parser(self):
        """T1.38: ParserRouter returns failed status for unknown file type."""
        from eks.engine.parsers.parser_router import ParserRouter
        config_parent = self.config_dir.parent if self.config_dir.name == "schemas" else self.config_dir
        loader = SchemaLoader(config_parent)
        config = loader.load_all()
        router = ParserRouter(loader.doc_config)

        result = router.route("test.txt", "txt")
        self.assertEqual(result["status"], "failed")
        self.assertIn("No parser", result["error"])

    def test_parser_router_route_batch(self):
        """T1.38: ParserRouter.route_batch processes multiple files."""
        from eks.engine.parsers.parser_router import ParserRouter
        config_parent = self.config_dir.parent if self.config_dir.name == "schemas" else self.config_dir
        loader = SchemaLoader(config_parent)
        config = loader.load_all()
        router = ParserRouter(loader.doc_config)

        files = [
            {"file_path": "test.txt", "file_type": "txt"},
            {"file_path": "test.xyz", "file_type": "xyz"},
        ]
        results = router.route_batch(files)
        self.assertEqual(len(results), 2)
        for r in results:
            self.assertEqual(r["status"], "failed")

    def test_pipeline_orchestrator_phase_a(self):
        """T1.39: PipelineOrchestrator Phase A scans and registers placeholders."""
        from eks.engine.core.pipeline_orchestrator import PipelineOrchestrator
        config_parent = self.config_dir.parent if self.config_dir.name == "schemas" else self.config_dir
        loader = SchemaLoader(config_parent)
        config = loader.load_all()
        orch = PipelineOrchestrator(config, loader.doc_config, self.registry)

        test_dir = Path("test_output/pipe_a")
        test_dir.mkdir(parents=True, exist_ok=True)
        (test_dir / "PIPE-001-A.pdf").touch()
        (test_dir / "PIPE-002-B.dgn").touch()

        summary = orch.run_phase_a(test_dir)
        self.assertGreaterEqual(summary["discovered"], 2)
        self.assertGreaterEqual(summary["valid"], 2)
        self.assertGreaterEqual(summary["registered"], 1)

    def test_pipeline_orchestrator_phase_c(self):
        """T1.39: PipelineOrchestrator Phase C flags pending documents."""
        from eks.engine.core.pipeline_orchestrator import PipelineOrchestrator
        config_parent = self.config_dir.parent if self.config_dir.name == "schemas" else self.config_dir
        loader = SchemaLoader(config_parent)
        config = loader.load_all()
        orch = PipelineOrchestrator(config, loader.doc_config, self.registry)

        summary = orch.run_phase_c()
        self.assertIn("flagged", summary)
        self.assertIn("documents", summary)
        self.assertIsInstance(summary["documents"], list)

    def test_review_manager_get_flagged(self):
        """T1.40: ManualReviewManager queries flagged documents."""
        from eks.engine.core.review_manager import ManualReviewManager
        reviewer = ManualReviewManager(self.registry)
        flagged = reviewer.get_flagged_documents()
        self.assertIsInstance(flagged, list)
        for doc in flagged:
            self.assertTrue(
                doc.get("extract_status") != "success" or
                (doc.get("extraction_confidence") is not None and doc["extraction_confidence"] < 0.70)
            )

    def test_review_manager_correct_metadata(self):
        """T1.40: ManualReviewManager corrects document metadata."""
        from eks.engine.core.review_manager import ManualReviewManager
        reviewer = ManualReviewManager(self.registry)

        self.registry.register_document({
            "document_number": "REV-001", "revision": "A",
            "document_type": "DWG", "status": "DRAFT"
        })
        result = reviewer.correct_metadata("REV-001-A", {"status": "APPROVED", "checked_by": "Reviewer"})
        self.assertTrue(result)
        doc = self.registry.get_document("REV-001", revision="A")
        self.assertEqual(doc["status"], "APPROVED")
        self.assertEqual(doc["checked_by"], "Reviewer")

    def test_review_manager_lock_document(self):
        """T1.40: ManualReviewManager locks a document."""
        from eks.engine.core.review_manager import ManualReviewManager
        reviewer = ManualReviewManager(self.registry)

        self.registry.register_document({
            "document_number": "LOCK-001", "revision": "A",
            "document_type": "DWG", "extract_status": "pending"
        })
        result = reviewer.lock_document("LOCK-001-A", "admin")
        self.assertTrue(result)
        doc = self.registry.get_document("LOCK-001", revision="A")
        self.assertEqual(doc["verified_by"], "admin")
        self.assertEqual(doc["extract_status"], "success")

    def test_review_manager_get_summary(self):
        """T1.40: ManualReviewManager returns review summary."""
        from eks.engine.core.review_manager import ManualReviewManager
        reviewer = ManualReviewManager(self.registry)
        summary = reviewer.get_review_summary()
        self.assertIn("total", summary)
        self.assertIn("status_counts", summary)
        self.assertIn("flagged", summary)
        self.assertIn("reviewed", summary)
        self.assertIsInstance(summary["status_counts"], dict)

    def test_fragment_schema_files_exist(self):
        """T1.42-T1.45: Verify all 4 fragment schema files exist."""
        for fname in ['eks_project_code_schema.json', 'eks_discipline_schema.json',
                      'eks_department_schema.json', 'eks_facility_schema.json']:
            path = self.config_dir / fname
            self.assertTrue(path.exists(), f"Missing fragment schema: {fname}")

    def test_base_schema_has_new_definitions(self):
        """T1.46: Verify eks_base_schema.json has project_entry_def, department_entry_def, facility_entry_def."""
        import json
        base = json.load(open(self.config_dir / 'eks_base_schema.json', encoding='utf-8'))
        defs = base.get('definitions', {})
        for expected_def in ['project_entry_def', 'department_entry_def', 'facility_entry_def']:
            self.assertIn(expected_def, defs, f"Missing definition: {expected_def}")
        self.assertIn('discipline_entry_def', defs, "Missing discipline_entry_def")

    def test_base_schema_has_project_setup_defs(self):
        """T1.67: Verify eks_base_schema.json has project_setup definitions."""
        import json
        base = json.load(open(self.config_dir / 'eks_base_schema.json', encoding='utf-8'))
        defs = base.get('definitions', {})
        for expected_def in ['required_folder_setup_def', 'required_engine_subfolder_setup_def',
                            'required_file_setup_def', 'environment_setup_def', 'validation_options_def']:
            self.assertIn(expected_def, defs, f"Missing project_setup definition: {expected_def}")

    def test_fragment_schemas_have_required_fields(self):
        """T1.42-T1.45: Verify each fragment schema has $schema, $id, title, version, allOf."""
        import json
        for fname in ['eks_project_code_schema.json', 'eks_discipline_schema.json',
                      'eks_department_schema.json', 'eks_facility_schema.json']:
            schema = json.load(open(self.config_dir / fname, encoding='utf-8'))
            for field in ['$schema', '$id', 'title', 'version', 'allOf']:
                self.assertIn(field, schema, f"{fname} missing {field}")

    def test_config_no_placeholder_data(self):
        """T1.46: Verify project rules config has real project codes (no P123/P456)."""
        import json
        # project_rules_registry is now $ref; load the referenced file directly
        rules_file = self.config_dir / 'eks_project_rules_config.json'
        rules_data = json.load(open(rules_file, encoding='utf-8'))
        project_rules = rules_data.get('project_rules', {})
        self.assertNotIn('P123', str(project_rules), "Placeholder P123 still in project rules")
        self.assertNotIn('P456', str(project_rules), "Placeholder P456 still in project rules")
        self.assertIn('131101', project_rules, "Real project code 131101 missing")
        self.assertIn('131242', project_rules, "Real project code 131242 missing")

    def test_config_has_fragment_references(self):
        """T1.46: Verify eks_config.json has $ref to fragment schemas."""
        import json
        config = json.load(open(self.config_dir / 'eks_config.json', encoding='utf-8'))
        self.assertIn('project_registry', config, "Missing project_registry")
        self.assertIn('$ref', config['project_registry'], "project_registry missing $ref")
        self.assertIn('department_registry', config, "Missing department_registry")
        self.assertIn('$ref', config['department_registry'], "department_registry missing $ref")
        self.assertIn('facility_registry', config, "Missing facility_registry")
        self.assertIn('$ref', config['facility_registry'], "facility_registry missing $ref")

    def test_setup_schema_has_new_properties(self):
        """T1.46: Verify eks_setup_schema.json has project_registry, department_registry, facility_registry."""
        import json
        setup = json.load(open(self.config_dir / 'eks_setup_schema.json', encoding='utf-8'))
        props = setup.get('properties', {})
        for prop in ['project_registry', 'department_registry', 'facility_registry']:
            self.assertIn(prop, props, f"setup_schema missing property: {prop}")
        required = setup.get('required', [])
        for prop in ['project_registry', 'department_registry', 'facility_registry']:
            self.assertIn(prop, required, f"setup_schema missing required: {prop}")

    def test_setup_schema_has_project_setup(self):
        """T1.67: Verify eks_setup_schema.json has project_setup property."""
        import json
        setup = json.load(open(self.config_dir / 'eks_setup_schema.json', encoding='utf-8'))
        props = setup.get('properties', {})
        self.assertIn('project_setup', props, "setup_schema missing project_setup property")
        required = setup.get('required', [])
        self.assertIn('project_setup', required, "setup_schema missing project_setup in required")

    def test_project_rules_has_fragment_required_fields(self):
        """T1.50: Verify project_rules_config has fragment_required_fields per project."""
        import json
        rules_file = self.config_dir / 'eks_project_rules_config.json'
        rules_data = json.load(open(rules_file, encoding='utf-8'))
        project_rules = rules_data.get('project_rules', {})
        for pid in ['131101', '131242']:
            self.assertIn(pid, project_rules, f"Missing project: {pid}")
            entry = project_rules[pid]
            self.assertIn('fragment_required_fields', entry,
                f"Project {pid} missing fragment_required_fields")
            self.assertIsInstance(entry['fragment_required_fields'], dict)
            self.assertIn('item_core', entry['fragment_required_fields'],
                f"Project {pid} fragment_required_fields missing item_core")
            self.assertGreater(len(entry['fragment_required_fields']['item_core']), 0,
                f"Project {pid} item_core required fields is empty")

    def test_fragment_required_fields_validate_against_base(self):
        """T1.50: fragment_required_fields fragment names and field paths must exist in asset base schema."""
        import json
        rules_file = self.config_dir / 'eks_project_rules_config.json'
        base_file = self.config_dir / 'eks_asset_base_schema.json'
        rules_data = json.load(open(rules_file, encoding='utf-8'))
        base_defs = json.load(open(base_file, encoding='utf-8')).get('definitions', {})
        project_rules = rules_data.get('project_rules', {})
        for pid, entry in project_rules.items():
            overrides = entry.get('fragment_required_fields', {})
            for frag_name, field_list in overrides.items():
                self.assertIn(frag_name, base_defs,
                    f"Project {pid}: fragment '{frag_name}' not in asset base definitions")
                frag_props = base_defs[frag_name].get('properties', {})
                for field in field_list:
                    self.assertIn(field, frag_props,
                        f"Project {pid}: field '{field}' not in fragment '{frag_name}' properties. "
                        f"Valid: {sorted(frag_props.keys())}")

    def test_config_registry_resolve_required_fields(self):
        """T1.50: ConfigRegistry returns correct fragment required fields per project."""
        registry = ConfigRegistry("eks/config")
        # 131101 — requires description in addition to keytag/tag_type/tag_no
        fields_131101 = registry.resolve_required_fields("131101", "item_core")
        self.assertIn("keytag", fields_131101)
        self.assertIn("tag_type", fields_131101)
        self.assertIn("tag_no", fields_131101)
        self.assertIn("description", fields_131101)
        # 131242 — only keytag/tag_type/tag_no
        fields_131242 = registry.resolve_required_fields("131242", "item_core")
        self.assertIn("keytag", fields_131242)
        self.assertIn("tag_type", fields_131242)
        self.assertIn("tag_no", fields_131242)
        self.assertNotIn("description", fields_131242)
        # Unknown project — falls back to empty list
        fields_unknown = registry.resolve_required_fields("999999", "item_core")
        self.assertEqual(fields_unknown, [])

    def test_asset_base_item_core_no_required_constraint(self):
        """T1.50: item_core in asset base schema is shape-only — no required array."""
        import json
        base_file = self.config_dir / 'eks_asset_base_schema.json'
        base = json.load(open(base_file, encoding='utf-8'))
        item_core = base.get('definitions', {}).get('item_core', {})
        self.assertNotIn('required', item_core,
            "item_core must not have required at base level. Required constraints "
            "are defined per-project in eks_project_rules_config.json (fragment_required_fields).")

    def test_registry_update_document_status(self):
        """T1.71: DocumentRegistry.update_document_status updates extraction fields."""
        self.registry.register_document({
            "document_number": "STATUS-001", "revision": "A",
            "document_type": "SPEC", "extract_status": "pending"
        })
        ok = self.registry.update_document_status("STATUS-001-A", "success", confidence=0.95, notes="Auto-parsed")
        self.assertTrue(ok)
        doc = self.registry.get_document("STATUS-001", revision="A")
        self.assertEqual(doc["extract_status"], "success")
        self.assertEqual(doc["extraction_confidence"], 0.95)
        self.assertEqual(doc["extraction_notes"], "Auto-parsed")

    def test_registry_update_document_status_nonexistent(self):
        """T1.71: update_document_status returns False for missing doc_id."""
        ok = self.registry.update_document_status("NONEXIST-001-A", "failed")
        self.assertFalse(ok)

    def test_pipeline_orchestrator_error_manager_wiring(self):
        """T1.68: PipelineOrchestrator accepts optional error_manager/message_manager."""
        from eks.engine.core.pipeline_orchestrator import PipelineOrchestrator
        from eks.engine.logging.logger import EKSLogger
        config_parent = self.config_dir.parent if self.config_dir.name == "schemas" else self.config_dir
        loader = EKSLogger  # just use logger api shape
        orch = PipelineOrchestrator(
            {}, {"file_type_registry": [], "health_scoring": {"dimensions": []}},
            self.registry, use_telemetry=False
        )
        self.assertIsNone(orch.error_manager)
        self.assertIsNone(orch.message_manager)

    def test_context_paths_to_dict_uses_posix(self):
        """T1.74: context.py EKSPaths.to_dict() uses .as_posix() for cross-platform."""
        from eks.engine.core.context import EKSPaths
        paths = EKSPaths(
            data_dir=Path("c:\\data") if os.name == "nt" else Path("/data"),
            schema_dir=Path("c:\\schemas") if os.name == "nt" else Path("/schemas"),
            output_dir=Path("c:\\out") if os.name == "nt" else Path("/out"),
            archive_dir=Path("c:\\arch") if os.name == "nt" else Path("/arch"),
            config_dir=Path("c:\\cfg") if os.name == "nt" else Path("/cfg"),
            log_dir=Path("c:\\log") if os.name == "nt" else Path("/log"),
        )
        d = paths.to_dict()
        for key, val in d.items():
            self.assertNotIn("\\", val, f"{key} contains backslash: {val}")
            self.assertIn("/", val, f"{key} has no forward slash: {val}")

    def test_phase1_server_paths_anchored_to_prj_dir(self):
        """T1.74: phase1_server.py paths are anchored to PRJ_DIR."""
        from eks.ui.backend.phase1_server import PRJ_DIR
        self.assertTrue(PRJ_DIR.is_absolute(), "PRJ_DIR must be absolute")
        # Verify referenced paths exist relative to PRJ_DIR
        self.assertTrue((PRJ_DIR / "eks" / "config").is_dir(), "eks/config not found relative to PRJ_DIR")
        self.assertTrue((PRJ_DIR / "eks" / "data").is_dir(), "eks/data not found relative to PRJ_DIR")

if __name__ == "__main__":
    unittest.main()

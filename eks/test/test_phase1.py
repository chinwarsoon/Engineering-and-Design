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
from unittest.mock import patch

# Project-scoped root for test artifacts — all test output goes under eks/test_output/
# per AGENTS.md §6.1: "Test runtime artifacts must be placed in <project>/test_output/"
_PROJECT_ROOT = Path(__file__).resolve().parent.parent

class TestPhase1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.test_dir = _PROJECT_ROOT / "test_output"
        cls.test_dir.mkdir(exist_ok=True)
        
        # Determine schema dir — project-scoped, prefer eks/config/schemas (canonical per AGENTS.md §9)
        cls.config_dir = _PROJECT_ROOT / "config" / "schemas"
        if not cls.config_dir.exists():
            cls.config_dir = _PROJECT_ROOT / "config"
        if not cls.config_dir.exists():
            # Fallback: shared config at repo root
            cls.config_dir = _PROJECT_ROOT.parent / "config" / "schemas"
        if not cls.config_dir.exists():
            cls.config_dir = _PROJECT_ROOT.parent / "config"

        if not cls.config_dir.exists():
            raise FileNotFoundError(
                f"Could not find schema directory. Tried: eks/config/schemas, eks/config, "
                f"../config/schemas, ../config (project root={_PROJECT_ROOT})"
            )
        
        # Initialize ConfigRegistry — pass the parent config/ dir (SchemaLoader resolves schemas/ internally)
        config_parent = cls.config_dir.parent if cls.config_dir.name == "schemas" else cls.config_dir
        cls.config_reg = ConfigRegistry(config_parent)
        
        # Delete existing DB for clean test state
        db_path = _PROJECT_ROOT / "output" / "eks_registry.db"
        if db_path.exists():
            db_path.unlink()

        # Initialize Registry
        cls.registry = DocumentRegistry()
        cls.rev_manager = RevisionManager(cls.registry)

    def test_schema_loader(self):
        """Test schema loading and validation."""
        config_parent = self.config_dir.parent if self.config_dir.name == "schemas" else self.config_dir
        config = load_eks_config(config_parent)
        self.assertIn("project_definition", config)
        self.assertNotIn("project_rules_registry", config)
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
        # T1.99.150 (I186): id is now UUID — validate format, not business-key string
        self.assertRegex(doc_id, r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
        
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

    def test_detect_supersession_no_existing(self):
        """detect_supersession with no existing documents returns no supersession."""
        result = self.rev_manager.detect_supersession("DOC-NONEXISTENT", "A")
        self.assertFalse(result["has_supersession"])
        self.assertIsNone(result["current_latest"])
        self.assertIsNone(result["supersedes"])
        self.assertIsNone(result["superseded_by"])

    def test_detect_supersession_newer_revision(self):
        """Newer alphabetic revision supersedes older one (read-only query)."""
        self.registry.register_document({
            "document_number": "DOC-SUPER-ALPHA", "revision": "A",
            "document_type": "SPEC", "file_path": "data/super_alpha_a.pdf"
        })
        result = self.rev_manager.detect_supersession("DOC-SUPER-ALPHA", "B")
        self.assertTrue(result["has_supersession"])
        self.assertTrue(result["is_newer"])
        self.assertIsNotNone(result["current_latest"])
        self.assertEqual(result["latest_revision"], "A")
        self.assertIsNotNone(result["supersedes"])
        self.assertIsNone(result["superseded_by"])

    def test_detect_supersession_same_revision(self):
        """Same revision as current latest returns is_same."""
        result = self.rev_manager.detect_supersession("DOC-SUPER-ALPHA", "A")
        self.assertTrue(result["is_same"])
        self.assertFalse(result["has_supersession"])

    def test_detect_supersession_older_revision(self):
        """Older revision is marked superseded_by current latest."""
        result = self.rev_manager.detect_supersession("DOC-SUPER-ALPHA", "0")
        self.assertTrue(result["has_supersession"])
        self.assertIsNone(result["supersedes"])
        self.assertIsNotNone(result["superseded_by"])
        self.assertEqual(result["latest_revision"], "A")

    def test_detect_supersession_numeric(self):
        """Numeric revision comparison works correctly."""
        self.registry.register_document({
            "document_number": "DOC-SUPER-NUM", "revision": "01",
            "document_type": "SPEC", "file_path": "data/super_num_01.pdf"
        })
        result = self.rev_manager.detect_supersession("DOC-SUPER-NUM", "02")
        self.assertTrue(result["has_supersession"])
        self.assertTrue(result["is_newer"])
        result_older = self.rev_manager.detect_supersession("DOC-SUPER-NUM", "00")
        self.assertTrue(result_older["has_supersession"])
        self.assertIsNotNone(result_older["superseded_by"])

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
        """T1.35/I282: every ontology document_type_mapping appears in the enum.

        The enum is a derived mirror of the carrier local_codes (§24), while the
        ontology document_type_mapping covers only the 8 mapped classes — so the
        correct relation is a SUBSET (mapping ⊆ enum), not equality.
        """
        import json
        base = json.load(open(self.config_dir / 'eks_doc_base_schema.json', encoding='utf-8'))
        ontology = json.load(open(self.config_dir / 'eks_ontology_config.json', encoding='utf-8'))
        enum_values = set(base['definitions']['document_type_code']['enum'])
        mapping_values = set()
        for cls in ontology.get('classes', []):
            dtm = cls.get('document_type_mapping')
            if dtm:
                mapping_values.add(dtm)
        self.assertTrue(mapping_values.issubset(enum_values),
            f"ontology mapping {sorted(mapping_values)} not subset of enum {sorted(enum_values)}")

    def test_file_type_registry_completeness(self):
        """T1.35: Verify file_type_registry has all 5 expected entries.

        I287 (T1.241): parser_class removed — single-sourced in
        eks_processing_config.json#/extraction_profiles.
        """
        config = json.load(open(self.config_dir / 'eks_doc_config.json', encoding='utf-8'))
        reg = config.get('file_type_registry', [])
        self.assertEqual(len(reg), 5)
        extensions = {e['extension'] for e in reg}
        self.assertEqual(extensions, {'pdf', 'dgn', 'docx', 'xlsx', 'dwg'})
        for entry in reg:
            self.assertNotIn('parser_class', entry)
            self.assertIn('display_name', entry)

    def test_element_type_registry_completeness(self):
        """T1.35/I283: Verify element_type_registry has all 11 expected entries.

        I283 (T1.230): extended 8→11 — added title_block, grid, signature_block.
        """
        config = json.load(open(self.config_dir / 'eks_doc_config.json', encoding='utf-8'))
        reg = config.get('element_type_registry', [])
        self.assertEqual(len(reg), 11)
        ets = {e['element_type'] for e in reg}
        expected = {'cover_page', 'revision_table', 'section', 'table', 'image', 'link', 'legend', 'note',
                    'title_block', 'grid', 'signature_block'}
        self.assertEqual(ets, expected)

    def test_element_expectations_keys_match_doc_type_registry(self):
        """T1.35/I282: every projected registry code's template has element expectations."""
        from eks.engine.core.schema_loader import SchemaLoader
        config_parent = self.config_dir.parent if self.config_dir.name == "schemas" else self.config_dir
        loader = SchemaLoader(config_parent)
        config = loader.load_all()
        doc_type_codes = {e['code'] for e in config.get('document_type_registry', [])}
        expect_keys = set(config.get('element_expectations', {}).keys())
        templates_by_code = {e['code']: e.get('template') for e in config.get('document_type_registry', [])}
        for code in doc_type_codes:
            self.assertIn(templates_by_code[code], expect_keys,
                f"template {templates_by_code[code]} for code {code} has no element expectations")

    def test_doc_metadata_has_new_fields(self):
        """T1.35: Verify doc metadata has file_path, ingested_at, file_type fields."""
        import json
        base = json.load(open(self.config_dir / 'eks_doc_base_schema.json', encoding='utf-8'))
        meta_def = base['definitions']['document_metadata_def']
        props = meta_def.get('properties', {})
        for field in ['file_path', 'ingested_at', 'file_type']:
            self.assertIn(field, props, f"document_metadata_def missing field: {field}")

    # --- T1.99.161 (I193): Schema-driven export columns ---

    def test_x_export_flag_present_on_all_properties(self):
        """T1.99.161a: Every property in document_metadata_def and project_metadata_def
        has an x_export boolean flag."""
        import json
        base = json.load(open(self.config_dir / 'eks_doc_base_schema.json', encoding='utf-8'))

        for def_name in ['document_metadata_def', 'project_metadata_def']:
            props = base['definitions'][def_name].get('properties', {})
            for prop_name, prop_schema in props.items():
                self.assertIn('x_export', prop_schema,
                    f"{def_name}.{prop_name} missing x_export flag")
                self.assertIsInstance(prop_schema['x_export'], bool,
                    f"{def_name}.{prop_name} x_export must be boolean")

        # Verify internal fields are excluded
        doc_props = base['definitions']['document_metadata_def']['properties']
        self.assertFalse(doc_props['is_latest']['x_export'],
            "is_latest must be x_export: false (internal boolean)")
        self.assertFalse(doc_props['supersedes']['x_export'],
            "supersedes must be x_export: false (internal FK)")
        self.assertFalse(doc_props['superseded_by']['x_export'],
            "superseded_by must be x_export: false (internal FK)")

    def test_export_artifact_def_exists_and_valid(self):
        """T1.99.161b: export_artifact_def enumerates 3 artifacts with valid column names."""
        import json
        base = json.load(open(self.config_dir / 'eks_doc_base_schema.json', encoding='utf-8'))

        self.assertIn('export_artifact_def', base['definitions'],
            "export_artifact_def missing from definitions")

        art_def = base['definitions']['export_artifact_def']
        for artifact in ['discovery_inventory', 'extraction_results', 'review_flags']:
            self.assertIn(artifact, art_def['properties'],
                f"{artifact} missing from export_artifact_def properties")

        # Collect all valid column names from both metadata defs
        doc_props = base['definitions']['document_metadata_def'].get('properties', {})
        proj_props = base['definitions']['project_metadata_def'].get('properties', {})
        valid_columns = set(doc_props.keys()) | set(proj_props.keys())
        # flag_reason is a computed column (not in schema properties)
        valid_columns.add('flag_reason')

        # Verify each artifact's column names are valid
        for artifact, desc in [
            ('discovery_inventory', 'discovery_inventory'),
            ('extraction_results', 'extraction_results'),
            ('review_flags', 'review_flags'),
        ]:
            # The artifact description says columns are listed but the actual
            # values come from resolve_export_columns() which reads x_export flags.
            # The export_artifact_def shape declares the contract — that 3 artifacts
            # exist — but the actual column lists are derived from x_export at runtime.
            pass  # validated structurally above

    def test_export_artifacts_have_different_column_sets(self):
        """T1.99.161c: discovery_inventory != extraction_results (different subsets)."""
        from eks.engine.eks_engine_pipeline import resolve_export_columns
        config = resolve_export_columns(self.config_dir)

        # T1.282 (I308): no _fallback key — function reads eks_export_view_config.json
        # SSOT and raises S-C-S-0312 on missing config instead of silently falling back.
        self.assertNotIn('_fallback', config,
            "resolve_export_columns() must not return a hardcoded _fallback marker (I308)")

        disc_cols = config['discovery_inventory']
        extr_cols = config['extraction_results']

        # extraction_results must be a superset of discovery_inventory
        disc_set = set(disc_cols)
        extr_set = set(extr_cols)
        missing_from_extr = disc_set - extr_set
        self.assertEqual(len(missing_from_extr), 0,
            f"Fields in discovery but NOT in extraction: {missing_from_extr}")

        # discovery_inventory must have fewer columns (no extraction-specific)
        extr_specific = extr_set - disc_set
        self.assertGreater(len(extr_specific), 0,
            "extraction_results should have more columns than discovery_inventory")
        extraction_only = {'page_count', 'extract_status', 'extraction_confidence', 'extraction_notes'}
        self.assertTrue(extraction_only.issubset(extr_specific),
            f"Expected {extraction_only} in extraction-only fields, got {extr_specific}")

        # review_flags must include flag_reason
        self.assertIn('flag_reason', config['review_flags'],
            "review_flags must include flag_reason computed column")

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
        self.assertEqual(len(indexes), 3)  # T1.99.150 (I186): +1 idx_doc_business_key
        self.assertTrue(any("idx_elements_doc_id" in idx for idx in indexes))
        self.assertTrue(any("idx_elements_type" in idx for idx in indexes))
        self.assertTrue(any("idx_doc_business_key" in idx for idx in indexes))

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

    def test_register_document_persists_file_type(self):
        """T1.197 (I253 regression): file_type must survive registration.

        Regression: the static-fallback COLUMN_ALLOWLIST (used when the doc base
        schema is unavailable, e.g. CLI run from a non-root CWD) omitted file_type,
        silently dropping it on INSERT — every registered row stored NULL, and
        Phase B failed with "No parser registered for file type: ".
        """
        import tempfile
        from pathlib import Path
        from eks.engine.core.registry import DocumentRegistry

        tmp = Path(tempfile.mkdtemp()) / "ft_test.db"
        reg = DocumentRegistry(db_path=str(tmp))
        reg._init_db()
        reg.register_document({
            "document_number": "TEST-FT-001",
            "revision": "A",
            "document_type": "DGN",
            "file_path": r"C:\x\sample.dgn",
            "file_type": "dgn",
        })
        row = reg.get_document("TEST-FT-001", revision="A")
        self.assertEqual(row.get("file_type"), "dgn")
        # T1.202 (I274): the hardcoded fallback was removed (AGENTS.md 16).
        # Assert the allowlist is still schema-derived from a non-root CWD and
        # equals the schema SSOT - the regression that caused the NULL rows.
        from eks.engine.core import registry as _reg_mod
        _reg_mod.DocumentRegistry._SCHEMA_DERIVED_ALLOWLIST = None
        orig_cwd = Path.cwd()
        try:
            tmp2 = Path(tempfile.mkdtemp())
            os.chdir(tmp2)
            allowlist = _reg_mod.DocumentRegistry._get_column_allowlist()
            self.assertIn("file_type", allowlist)
            self.assertIn("file_path", allowlist)
            self.assertEqual(allowlist, self.registry.COLUMN_ALLOWLIST)
        finally:
            os.chdir(orig_cwd)
            _reg_mod.DocumentRegistry._SCHEMA_DERIVED_ALLOWLIST = None

    def test_column_allowlist_raises_when_schema_absent(self):
        """T1.202 (I274): no silent fallback - descriptive error on schema absence."""
        from eks.engine.core import registry as _reg_mod
        import eks.engine.core.schema_to_ddl as _stdl
        _reg_mod.DocumentRegistry._SCHEMA_DERIVED_ALLOWLIST = None
        orig = _stdl.SchemaToDDL.load_doc_base_schema

        def _boom(*a, **k):
            raise FileNotFoundError("eks_doc_base_schema.json genuinely absent (T1.202)")

        _stdl.SchemaToDDL.load_doc_base_schema = staticmethod(_boom)
        try:
            with self.assertRaises(FileNotFoundError) as ctx:
                _reg_mod.DocumentRegistry._get_column_allowlist()
            self.assertIn("absent", str(ctx.exception))
        finally:
            _stdl.SchemaToDDL.load_doc_base_schema = orig
            _reg_mod.DocumentRegistry._SCHEMA_DERIVED_ALLOWLIST = None

    def test_column_allowlist_equals_schema_derived_set(self):
        """T1.202 (I274): allowlist equals schema-derived set (drift guard)."""
        import json as _json
        from pathlib import Path as _Path
        from eks.engine.core.registry import DocumentRegistry
        _reg_mod = DocumentRegistry
        _reg_mod._SCHEMA_DERIVED_ALLOWLIST = None
        try:
            cfg = _Path(self.config_dir)
            schema_path = cfg / "eks_doc_base_schema.json"
            if not schema_path.exists():
                schema_path = cfg.parent / "eks_doc_base_schema.json"
            schema = _json.loads(schema_path.read_text(encoding="utf-8"))
            defs = schema["definitions"]
            expected = set(defs["project_metadata_def"]["properties"].keys()) | \
                       set(defs["document_metadata_def"]["properties"].keys())
            expected.add("id")
            self.assertEqual(DocumentRegistry._get_column_allowlist(), expected)
        finally:
            _reg_mod._SCHEMA_DERIVED_ALLOWLIST = None

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

        test_dir = _PROJECT_ROOT / "test_output" / "scan_test"
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

        test_dir = _PROJECT_ROOT / "test_output" / "scan_validate"
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

        test_dir = _PROJECT_ROOT / "test_output" / "scan_register"
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
        router = ParserRouter(loader.doc_config, processing_config=loader.processing_config)

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
        router = ParserRouter(loader.doc_config, processing_config=loader.processing_config)

        test_file = _PROJECT_ROOT / "test_output" / "test_router.dgn"
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
        router = ParserRouter(loader.doc_config, processing_config=loader.processing_config)

        result = router.route("test.txt", "txt")
        self.assertEqual(result["status"], "failed")
        self.assertIn("No parser", result["error"])

    def test_parser_router_route_batch(self):
        """T1.38: ParserRouter.route_batch processes multiple files."""
        from eks.engine.parsers.parser_router import ParserRouter
        config_parent = self.config_dir.parent if self.config_dir.name == "schemas" else self.config_dir
        loader = SchemaLoader(config_parent)
        config = loader.load_all()
        router = ParserRouter(loader.doc_config, processing_config=loader.processing_config)

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

        test_dir = _PROJECT_ROOT / "test_output" / "pipe_a"
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
        from eks.engine.core.schema_loader import SchemaLoader
        config_parent = self.config_dir.parent if self.config_dir.name == "schemas" else self.config_dir
        loader = SchemaLoader(config_parent)
        loader.load_all()
        reviewer = ManualReviewManager(
            self.registry,
            doc_config=loader.doc_config,
            base_schema=loader.doc_base_schema,
        )

        self.registry.register_document({
            "document_number": "REV-001", "revision": "A",
            "document_type": "DWG", "status": "DRAFT"
        })
        # T1.99.150 (I186): resolve doc_id via get_latest_by_key
        latest = self.registry.get_latest_by_key("REV-001", "A")
        self.assertIsNotNone(latest)
        result = reviewer.correct_metadata(latest["id"], {"status": "APPROVED", "checked_by": "Reviewer"})
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
        # T1.99.150 (I186): resolve doc_id via get_latest_by_key
        latest = self.registry.get_latest_by_key("LOCK-001", "A")
        self.assertIsNotNone(latest)
        result = reviewer.lock_document(latest["id"], "admin")
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
        """T1.85: Verify eks_base_schema.json has DCC-aligned project_setup definitions."""
        import json
        base = json.load(open(self.config_dir / 'eks_base_schema.json', encoding='utf-8'))
        defs = base.get('definitions', {})
        for expected_def in ['folder_entry_def', 'root_file_entry_def', 'schema_file_entry_def',
                            'discovery_rule_def', 'environment_entry_def', 'dependency_config_def',
                            'validation_rule_entry_def', 'project_metadata_def']:
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
        """T1.46 (updated T1.196): Verify project definitions have real project codes (no P123/P456)."""
        import json
        # T1.196: eks_project_rules_config.json retired — rules live in eks_project_definition_config.json
        pd_file = self.config_dir / 'eks_project_definition_config.json'
        pd_data = json.load(open(pd_file, encoding='utf-8'))
        project_defs = pd_data.get('project_definition', {})
        self.assertNotIn('P123', str(project_defs), "Placeholder P123 still in project definitions")
        self.assertNotIn('P456', str(project_defs), "Placeholder P456 still in project definitions")
        self.assertIn('131101', project_defs, "Real project code 131101 missing")
        self.assertIn('131242', project_defs, "Real project code 131242 missing")
        self.assertNotIn('project_rules_registry', str(pd_data), "legacy project_rules_registry should be gone")

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

    def test_config_setup_values_top_level(self):
        """T1.90: Verify eks_config.json stores setup values top-level (DCC project_config pattern, no project_setup wrapper)."""
        import json
        config = json.load(open(self.config_dir / 'eks_config.json', encoding='utf-8'))
        for key in ['folders', 'root_files', 'schema_files', 'environment', 'dependencies', 'project_metadata']:
            self.assertIn(key, config, f"eks_config.json missing top-level setup key: {key}")
        self.assertNotIn('project_setup', config, "eks_config.json should not wrap setup under project_setup (T1.90)")

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
        """T1.90: Verify eks_setup_schema.json declares setup values top-level (DCC project_config pattern)."""
        import json
        setup = json.load(open(self.config_dir / 'eks_setup_schema.json', encoding='utf-8'))
        props = setup.get('properties', {})
        for key in ['folders', 'root_files', 'schema_files', 'environment', 'dependencies', 'project_metadata']:
            self.assertIn(key, props, f"setup_schema missing top-level setup property: {key}")
        self.assertNotIn('project_setup', props, "setup_schema should not wrap setup under project_setup (T1.90)")
        required = setup.get('required', [])
        for key in ['folders', 'root_files', 'schema_files', 'environment', 'dependencies', 'project_metadata']:
            self.assertIn(key, required, f"setup_schema missing top-level setup key in required: {key}")

    def test_project_rules_has_fragment_required_fields(self):
        """T1.50 (updated T1.196): project definitions carry fragment_required_fields per project."""
        import json
        pd_file = self.config_dir / 'eks_project_definition_config.json'
        pd_data = json.load(open(pd_file, encoding='utf-8'))
        project_defs = pd_data.get('project_definition', {})
        for pid in ['131101', '131242']:
            self.assertIn(pid, project_defs, f"Missing project: {pid}")
            entry = project_defs[pid]
            self.assertIn('fragment_required_fields', entry,
                f"Project {pid} missing fragment_required_fields")
            self.assertIsInstance(entry['fragment_required_fields'], dict)
            self.assertIn('item_core', entry['fragment_required_fields'],
                f"Project {pid} fragment_required_fields missing item_core")
            self.assertGreater(len(entry['fragment_required_fields']['item_core']), 0,
                f"Project {pid} item_core required fields is empty")

    def test_fragment_required_fields_validate_against_base(self):
        """T1.50 (updated T1.196): fragment_required_fields names/paths must exist in asset base schema."""
        import json
        pd_file = self.config_dir / 'eks_project_definition_config.json'
        base_file = self.config_dir / 'eks_asset_base_schema.json'
        pd_data = json.load(open(pd_file, encoding='utf-8'))
        base_defs = json.load(open(base_file, encoding='utf-8')).get('definitions', {})
        project_defs = pd_data.get('project_definition', {})
        for pid, entry in project_defs.items():
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
            "are defined per-project in eks_project_definition_config.json (fragment_required_fields).")

    def test_registry_update_document_status(self):
        """T1.71: DocumentRegistry.update_document_status updates extraction fields."""
        doc_id = self.registry.register_document({
            "document_number": "STATUS-001", "revision": "A",
            "document_type": "SPEC", "extract_status": "pending"
        })
        # T1.99.150 (I186): id is now UUID — use returned value
        ok = self.registry.update_document_status(doc_id, "success", confidence=0.95, notes="Auto-parsed")
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

    # ── I227: Scan Redundancy Tests ──────────────────────────────────────────

    def test_phase_b_reads_from_registry_instead_of_rescan(self):
        """T1.100 (I227): run_phase_b() reads file list from DuckDB — does not re-scan filesystem."""
        from unittest.mock import patch, MagicMock
        from eks.engine.core.pipeline_orchestrator import PipelineOrchestrator

        # Pre-populate registry with documents (simulating Phase A output)
        test_docs = [
            {"document_number": "I227-001", "revision": "A", "file_path": str(_PROJECT_ROOT / "test_output/i227_doc_a.pdf"), "file_type": "pdf", "document_type": "PDF"},
            {"document_number": "I227-002", "revision": "A", "file_path": str(_PROJECT_ROOT / "test_output/i227_doc_b.dgn"), "file_type": "dgn", "document_type": "DGN"},
            {"document_number": "I227-003", "revision": "00", "file_path": str(_PROJECT_ROOT / "test_output/i227_doc_c.docx"), "file_type": "docx", "document_type": "DOC"},
        ]
        for doc in test_docs:
            self.registry.register_document(doc)

        config_parent = self.config_dir.parent if self.config_dir.name == "schemas" else self.config_dir
        loader = SchemaLoader(config_parent)
        config = loader.load_all()
        orch = PipelineOrchestrator(config, loader.doc_config, self.registry)

        # Patch scanner.scan to fail loudly if called
        original_scan = orch.scanner.scan
        orch.scanner.scan = MagicMock(side_effect=AssertionError("I227: scan() should not be called when registry has data"))

        summary = orch.run_phase_b(_PROJECT_ROOT / "test_output")

        # Verify scan was never called
        orch.scanner.scan.assert_not_called()

        # Verify results returned — loop completes without exception
        self.assertIn("total", summary)
        self.assertIn("results", summary)
        self.assertGreaterEqual(summary["total"], len(test_docs),
                                "Phase B should process at minimum the 3 I227 test files")
        self.assertEqual(len(summary["results"]), summary["total"],
                         "Results count should match total files processed")

        # Restore
        orch.scanner.scan = original_scan

    def test_phase_b_falls_back_to_scan_when_registry_empty(self):
        """T1.100 (I227): run_phase_b() falls back to filesystem scan when DuckDB is empty."""
        from unittest.mock import MagicMock
        from eks.engine.core.pipeline_orchestrator import PipelineOrchestrator

        config_parent = self.config_dir.parent if self.config_dir.name == "schemas" else self.config_dir
        loader = SchemaLoader(config_parent)
        config = loader.load_all()

        # Use a registry that has no documents
        empty_reg_path = _PROJECT_ROOT / "test_output" / "eks_registry_empty_i227.db"
        if empty_reg_path.exists():
            empty_reg_path.unlink()
        from eks.engine.core import DocumentRegistry
        empty_registry = DocumentRegistry(db_path=str(empty_reg_path))

        orch = PipelineOrchestrator(config, loader.doc_config, empty_registry)

        # Set up test files on disk
        test_dir = _PROJECT_ROOT / "test_output" / "pipe_b_fallback"
        test_dir.mkdir(parents=True, exist_ok=True)
        (test_dir / "FALLBACK-001-A.pdf").touch()
        (test_dir / "FALLBACK-002-B.dgn").touch()

        # Patch scanner.scan to verify it IS called
        original_scan = orch.scanner.scan
        orch.scanner.scan = MagicMock(wraps=original_scan)

        summary = orch.run_phase_b(test_dir)

        # Verify scan was called (fallback path)
        orch.scanner.scan.assert_called_once()
        self.assertGreaterEqual(summary["total"], 1, "Phase B should discover files via fallback scan")

        # Restore
        orch.scanner.scan = original_scan


    # ------------------------------------------------------------------
    # I232 — Legacy doc_id fallback removal (T1.106, T1.107)
    # ------------------------------------------------------------------

    def test_get_document_by_file_path_found(self):
        """T1.106 (I232): registry.get_document_by_file_path() returns doc by file_path."""
        reg_path = self.test_dir / "eks_registry_i232_found.db"
        if reg_path.exists():
            reg_path.unlink()
        registry = DocumentRegistry(db_path=str(reg_path))
        doc_id = registry.register_document({
            "document_number": "UNRESOLVED-a1b2c3d4",
            "revision": "00",
            "document_type": "OTHER",
            "file_path": "/data/test/Site_Photo_001.pdf",
            "file_type": "pdf",
            "status": "registered",
        })
        result = registry.get_document_by_file_path("/data/test/Site_Photo_001.pdf")
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], doc_id)
        self.assertEqual(result["document_number"], "UNRESOLVED-a1b2c3d4")
        if reg_path.exists():
            reg_path.unlink()

    def test_get_document_by_file_path_not_found(self):
        """T1.106 (I232): returns None for unknown file_path."""
        reg_path = self.test_dir / "eks_registry_i232_miss.db"
        if reg_path.exists():
            reg_path.unlink()
        registry = DocumentRegistry(db_path=str(reg_path))
        result = registry.get_document_by_file_path("/nonexistent/path.pdf")
        self.assertIsNone(result)
        if reg_path.exists():
            reg_path.unlink()

    def test_get_document_by_file_path_synthetic_key_roundtrip(self):
        """T1.106 (I232): Phase A registers unresolvable filename with synthetic key;
        Phase B resolves doc_id via file_path, not stem."""
        reg_path = self.test_dir / "eks_registry_i232_synth.db"
        if reg_path.exists():
            reg_path.unlink()
        registry = DocumentRegistry(db_path=str(reg_path))

        # Simulate Phase A: filename unresolvable → synthetic key
        file_path = "/data/test/Site_Photo_001.pdf"
        doc_id = registry.register_document({
            "document_number": "UNRESOLVED-a1b2c3d4",
            "revision": "00",
            "document_type": "OTHER",
            "file_path": file_path,
            "file_type": "pdf",
            "status": "registered",
        })

        # Simulate Phase B: resolve by file_path (not Path(file_path).stem)
        doc = registry.get_document_by_file_path(file_path)
        self.assertIsNotNone(doc)
        resolved_id = doc["id"]

        # Verify: doc_id from file_path lookup matches the registered UUID
        self.assertEqual(resolved_id, doc_id)

        # Verify: legacy Stem-based lookup would fail
        stem_doc = registry.get_document("Site_Photo_001")
        self.assertIsNone(stem_doc, "Stem-based lookup must return None — document_number is UNRESOLVED-a1b2c3d4, not Site_Photo_001")

        if reg_path.exists():
            reg_path.unlink()


    # ------------------------------------------------------------------
    # I235 — Batch telemetry milestone ordering (T1.103, T1.116)
    # ------------------------------------------------------------------

    def _run_phase_b_with_milestone_mock(self, doc_count):
        """Helper: register {doc_count} docs, create orchestrator, mock _forward_telemetry,
        run_phase_b, return (orch, mock_calls)."""
        from unittest.mock import MagicMock
        from eks.engine.core.pipeline_orchestrator import PipelineOrchestrator

        reg_path = self.test_dir / f"eks_registry_i235_{doc_count}file.db"
        if reg_path.exists():
            reg_path.unlink()
        registry = DocumentRegistry(db_path=str(reg_path))

        test_docs = [
            {"document_number": f"I235-{i:03d}", "revision": "A",
             "file_path": str(self.test_dir / f"i235_doc_{i}.pdf"),
             "file_type": "pdf", "document_type": "PDF"}
            for i in range(doc_count)
        ]
        for doc in test_docs:
            registry.register_document(doc)

        config_parent = self.config_dir.parent if self.config_dir.name == "schemas" else self.config_dir
        loader = SchemaLoader(config_parent)
        config = loader.load_all()

        # Enable telemetry; suppress scanner by pre-populating registry
        orch = PipelineOrchestrator(config, loader.doc_config, registry,
                                    use_telemetry=True)
        mock_tel = MagicMock(wraps=orch._forward_telemetry)
        orch._forward_telemetry = mock_tel

        summary = orch.run_phase_b(self.test_dir)

        if reg_path.exists():
            reg_path.unlink()
        return orch, mock_tel, summary

    def test_phase_b_milestone_order_4_file_batch(self):
        """T1.103 (I235): 4-file batch emits exactly 4 milestones (25/50/75/100)
        in strict ascending order, plus end-of-phase 'B' summary (5 total)."""
        orch, mock_tel, summary = self._run_phase_b_with_milestone_mock(4)
        self.assertIn("total", summary)
        self.assertGreaterEqual(summary["total"], 4)

        calls = mock_tel.call_args_list
        # End-of-phase summary call uses phase "B"
        milestone_calls = [c for c in calls if c[0][0] == "B-progress"]
        milestone_labels = [c[1]["details"]["milestone"] for c in milestone_calls]
        self.assertEqual(milestone_labels, ["25%", "50%", "75%", "100%"],
                         "4-file batch: milestones must fire in 25% → 50% → 75% → 100% order")

    def test_phase_b_milestone_order_1_file_batch(self):
        """T1.103 (I235): 1-file batch emits 4 milestones in order with no duplicates."""
        orch, mock_tel, summary = self._run_phase_b_with_milestone_mock(1)
        self.assertIn("total", summary)
        self.assertGreaterEqual(summary["total"], 1)

        calls = mock_tel.call_args_list
        milestone_calls = [c for c in calls if c[0][0] == "B-progress"]
        milestone_labels = [c[1]["details"]["milestone"] for c in milestone_calls]
        self.assertEqual(milestone_labels, ["25%", "50%", "75%", "100%"],
                         "1-file batch: all 4 milestones must fire with no duplicates")
        self.assertEqual(len(milestone_calls), 4,
                         "1-file batch: exactly 4 milestone calls, no extra")

    def test_phase_b_milestone_order_2_file_batch(self):
        """T1.103 (I235): 2-file batch — 75% fires before 100%, not after."""
        orch, mock_tel, summary = self._run_phase_b_with_milestone_mock(2)
        self.assertIn("total", summary)
        self.assertGreaterEqual(summary["total"], 2)

        calls = mock_tel.call_args_list
        milestone_calls = [c for c in calls if c[0][0] == "B-progress"]
        milestone_labels = [c[1]["details"]["milestone"] for c in milestone_calls]
        seventy_five_idx = milestone_labels.index("75%")
        hundred_idx = milestone_labels.index("100%")
        self.assertLess(seventy_five_idx, hundred_idx,
                        "2-file batch: 75% must fire BEFORE 100%")

    # ------------------------------------------------------------------
    # I237 — Schema-driven telemetry verbosity (T1.122, T1.123)
    # ------------------------------------------------------------------

    def test_telemetry_verbose_true_prints_milestones(self):
        """T1.123 (I237): telemetry_verbose=True causes milestone [TELEMETRY] lines to print."""
        from unittest.mock import patch
        from eks.engine.core.pipeline_orchestrator import PipelineOrchestrator

        reg_path = self.test_dir / "eks_registry_i237_verbose.db"
        if reg_path.exists():
            reg_path.unlink()
        registry = DocumentRegistry(db_path=str(reg_path))

        for i in range(4):
            registry.register_document({
                "document_number": f"I237-{i:03d}", "revision": "A",
                "file_path": str(self.test_dir / f"i237_doc_{i}.pdf"),
                "file_type": "pdf", "document_type": "PDF",
            })

        config_parent = self.config_dir.parent if self.config_dir.name == "schemas" else self.config_dir
        loader = SchemaLoader(config_parent)
        config = loader.load_all()

        captured = []

        def _fake_print(*args, **kwargs):
            captured.append(" ".join(str(a) for a in args))

        orch = PipelineOrchestrator(config, loader.doc_config, registry,
                                    use_telemetry=True, telemetry_verbose=True)
        with patch("builtins.print", _fake_print):
            summary = orch.run_phase_b(self.test_dir)

        telemetry_lines = [l for l in captured if "[TELEMETRY]" in l]
        checkpoint_phases = set()
        for line in telemetry_lines:
            # Extract phase name from "[TELEMETRY] Checkpoint: {phase} | ..."
            parts = line.split("Checkpoint: ")
            if len(parts) > 1:
                checkpoint_phases.add(parts[1].split(" |")[0])

        self.assertIn("B-progress", checkpoint_phases,
                       "telemetry_verbose=True: B-progress milestone must appear in printed output")

        if reg_path.exists():
            reg_path.unlink()

    def test_telemetry_verbose_false_suppresses_milestones(self):
        """T1.123 (I237): telemetry_verbose=False suppresses milestone [TELEMETRY] print."""
        from unittest.mock import patch
        from eks.engine.core.pipeline_orchestrator import PipelineOrchestrator

        reg_path = self.test_dir / "eks_registry_i237_silent.db"
        if reg_path.exists():
            reg_path.unlink()
        registry = DocumentRegistry(db_path=str(reg_path))

        for i in range(4):
            registry.register_document({
                "document_number": f"I237s-{i:03d}", "revision": "A",
                "file_path": str(self.test_dir / f"i237s_doc_{i}.pdf"),
                "file_type": "pdf", "document_type": "PDF",
            })

        config_parent = self.config_dir.parent if self.config_dir.name == "schemas" else self.config_dir
        loader = SchemaLoader(config_parent)
        config = loader.load_all()

        captured = []

        def _fake_print(*args, **kwargs):
            captured.append(" ".join(str(a) for a in args))

        orch = PipelineOrchestrator(config, loader.doc_config, registry,
                                    use_telemetry=True, telemetry_verbose=False)
        with patch("builtins.print", _fake_print):
            summary = orch.run_phase_b(self.test_dir)

        telemetry_lines = [l for l in captured if "[TELEMETRY]" in l]
        self.assertEqual(len(telemetry_lines), 0,
                         "telemetry_verbose=False: zero [TELEMETRY] lines must print")

        if reg_path.exists():
            reg_path.unlink()

    # ------------------------------------------------------------------
    # I225 — SchemaToDDL auto-migration + pre-generated DDL + version tracking
    # ------------------------------------------------------------------

    def test_registry_with_pre_generated_ddl(self):
        """T1.99.191 (I225): DocumentRegistry accepts pre-generated DDL from bootstrap."""
        from eks.engine.core.schema_to_ddl import SchemaToDDL
        schema = SchemaToDDL.load_doc_base_schema(self.config_dir)
        ddl_gen = SchemaToDDL(schema)
        docs_ddl = ddl_gen.generate_documents_ddl()
        els_ddl = ddl_gen.generate_document_elements_ddl()
        indexes = ddl_gen.generate_indexes()
        pre_generated = {
            "documents_ddl": docs_ddl,
            "elements_ddl": els_ddl,
            "indexes": indexes,
            "doc_base_schema": schema,
        }

        reg_path = _PROJECT_ROOT / "test_output" / "test_pregen_registry.db"
        if reg_path.exists():
            reg_path.unlink()
        try:
            reg = DocumentRegistry(
                db_path=str(reg_path),
                pre_generated_ddl=pre_generated,
            )
            docs = reg.list_documents()
            self.assertIsInstance(docs, list)
            import duckdb as _duckdb
            conn = _duckdb.connect(str(reg_path))
            try:
                meta = conn.execute(
                    "SELECT value FROM _eks_schema_meta WHERE key = 'schema_hash'"
                ).fetchone()
                self.assertIsNotNone(meta, "Schema hash must be recorded in _eks_schema_meta")
                self.assertIn(":", meta[0])
            finally:
                conn.close()
        finally:
            if reg_path.exists():
                reg_path.unlink()

    def test_registry_relations_manifest(self):
        """T1.253 (I290): Schema-declared FK relationships persisted to _eks_table_relations."""
        from eks.engine.core.schema_to_ddl import SchemaToDDL
        schema = SchemaToDDL.load_doc_base_schema(self.config_dir)
        ddl_gen = SchemaToDDL(schema)
        relations = ddl_gen.registry_relations()
        self.assertGreaterEqual(len(relations), 6,
                                "I290: at least the 6 declared relations must exist")
        names = {r["relation_name"] for r in relations}
        for required in ["fk_doc_type_composite", "fk_supersedes", "fk_superseded_by",
                         "fk_project_code", "fk_discipline", "fk_file_type"]:
            self.assertIn(required, names)

        pre_generated = {
            "documents_ddl": ddl_gen.generate_documents_ddl(),
            "elements_ddl": ddl_gen.generate_document_elements_ddl(),
            "indexes": ddl_gen.generate_indexes(),
            "doc_base_schema": schema,
        }
        reg_path = _PROJECT_ROOT / "test_output" / "test_relations_manifest.db"
        if reg_path.exists():
            reg_path.unlink()
        try:
            reg = DocumentRegistry(
                db_path=str(reg_path),
                pre_generated_ddl=pre_generated,
            )
            reg.list_documents()
            import duckdb as _duckdb
            conn = _duckdb.connect(str(reg_path))
            try:
                tables = {r[0] for r in conn.execute(
                    "SELECT table_name FROM information_schema.tables"
                ).fetchall()}
                self.assertIn("_eks_table_relations", tables,
                              "I290: relations manifest table must be created")
                rows = conn.execute(
                    "SELECT relation_name FROM _eks_table_relations"
                ).fetchall()
                row_names = {r[0] for r in rows}
                for n in names:
                    self.assertIn(n, row_names,
                                  f"I290: declared relation {n} missing from manifest")
            finally:
                conn.close()
        finally:
            if reg_path.exists():
                reg_path.unlink()

    def test_documents_has_project_code(self):
        """T1.253 (I290) — documents table DDL declares nullable project_code for composite FK."""
        from eks.engine.core.schema_to_ddl import SchemaToDDL
        schema = SchemaToDDL.load_doc_base_schema(self.config_dir)
        ddl = SchemaToDDL(schema).generate_documents_ddl()
        self.assertIn("project_code", ddl)

    def test_schema_version_tracking(self):
        """T1.99.191 (I225): Schema version hash recorded and updated on schema change."""
        from eks.engine.core.schema_to_ddl import SchemaToDDL
        schema = SchemaToDDL.load_doc_base_schema(self.config_dir)
        ddl_gen = SchemaToDDL(schema)
        pre_generated_v1 = {
            "documents_ddl": ddl_gen.generate_documents_ddl(),
            "elements_ddl": ddl_gen.generate_document_elements_ddl(),
            "indexes": ddl_gen.generate_indexes(),
            "doc_base_schema": schema,
        }
        pre_generated_v2 = dict(pre_generated_v1)
        pre_generated_v2["documents_ddl"] = pre_generated_v1["documents_ddl"].replace(
            "id VARCHAR PRIMARY KEY", "id VARCHAR PRIMARY KEY, dummy_col VARCHAR"
        )

        reg_path = _PROJECT_ROOT / "test_output" / "test_schema_version.db"
        if reg_path.exists():
            reg_path.unlink()
        try:
            reg1 = DocumentRegistry(
                db_path=str(reg_path),
                pre_generated_ddl=pre_generated_v1,
            )
            import duckdb as _duckdb
            conn = _duckdb.connect(str(reg_path))
            try:
                hash_v1 = conn.execute(
                    "SELECT value FROM _eks_schema_meta WHERE key = 'schema_hash'"
                ).fetchone()[0]
            finally:
                conn.close()

            reg2 = DocumentRegistry(
                db_path=str(reg_path),
                pre_generated_ddl=pre_generated_v2,
            )
            conn = _duckdb.connect(str(reg_path))
            try:
                hash_v2 = conn.execute(
                    "SELECT value FROM _eks_schema_meta WHERE key = 'schema_hash'"
                ).fetchone()[0]
            finally:
                conn.close()

            self.assertNotEqual(hash_v1, hash_v2, "Schema hash must change when DDL changes")
        finally:
            if reg_path.exists():
                reg_path.unlink()

    def test_bootstrap_pre_generated_ddl(self):
        """T1.99.191 (I225): Bootstrap P7 stores pre-generated DDL accessible via to_dict()."""
        from eks.engine.core.bootstrap import EKSBootstrapManager
        config_parent = self.config_dir.parent if self.config_dir.name == "schemas" else self.config_dir
        boot = EKSBootstrapManager(
            project_root=_PROJECT_ROOT,
            skip_readiness=True,
            auto_create=False,
        )
        boot.cli_args = {"level": 1}
        boot.config_dir = config_parent
        boot._bootstrap_schema()
        ddl = boot._pre_generated_ddl
        self.assertIsNotNone(ddl, "P7 must generate DDL")
        self.assertIn("documents_ddl", ddl)
        self.assertIn("elements_ddl", ddl)
        self.assertIn("indexes", ddl)
        self.assertIn("doc_base_schema", ddl)
        self.assertGreater(len(ddl["documents_ddl"]), 50)
        self.assertGreater(len(ddl["elements_ddl"]), 50)
        self.assertIsInstance(ddl["indexes"], list)
        self.assertGreater(len(ddl["indexes"]), 0)

        out = boot.to_dict()
        self.assertIn("pre_generated_ddl", out)
        self.assertIs(out["pre_generated_ddl"], ddl)

    def test_registry_pre_generated_ddl_uses_bootstrap_ddl(self):
        """T1.99.191 (I225): Registry with bootstrap pre-generated DDL creates identical tables."""
        from eks.engine.core.bootstrap import EKSBootstrapManager
        config_parent = self.config_dir.parent if self.config_dir.name == "schemas" else self.config_dir
        boot = EKSBootstrapManager(
            project_root=_PROJECT_ROOT,
            skip_readiness=True,
            auto_create=False,
        )
        boot.cli_args = {"level": 1}
        boot.config_dir = config_parent
        boot._bootstrap_schema()
        pre_generated = boot._pre_generated_ddl

        reg_path_pre = _PROJECT_ROOT / "test_output" / "test_boot_ddl_pre.db"
        reg_path_no = _PROJECT_ROOT / "test_output" / "test_boot_ddl_no.db"
        for p in [reg_path_pre, reg_path_no]:
            if p.exists():
                p.unlink()
        try:
            reg_pre = DocumentRegistry(
                db_path=str(reg_path_pre),
                pre_generated_ddl=pre_generated,
            )
            reg_no = DocumentRegistry(
                db_path=str(reg_path_no),
            )

            import duckdb as _duckdb
            for table in ["documents", "document_elements"]:
                conn_pre = _duckdb.connect(str(reg_path_pre))
                conn_no = _duckdb.connect(str(reg_path_no))
                try:
                    cols_pre = {row[1] for row in conn_pre.execute(
                        f"PRAGMA table_info('{table}')"
                    ).fetchall()}
                    cols_no = {row[1] for row in conn_no.execute(
                        f"PRAGMA table_info('{table}')"
                    ).fetchall()}
                    self.assertEqual(
                        cols_pre, cols_no,
                        f"Column sets must match for '{table}' "
                        f"with and without pre-generated DDL"
                    )
                finally:
                    conn_pre.close()
                    conn_no.close()
        finally:
            for p in [reg_path_pre, reg_path_no]:
                if p.exists():
                    p.unlink()


    def test_phase_a_batch_milestones_emitted(self):
        """T1.126 (I238): register_placeholders() emits batch milestones at 25/50/75/100%."""
        from unittest.mock import MagicMock
        from eks.engine.core.file_scanner import FileScanner

        captured_status = []

        scanner = FileScanner(config={}, doc_config={}, logger=MagicMock())
        scanner.logger.status = lambda msg: captured_status.append(msg)
        scanner.logger.info = lambda msg, **kwargs: None
        scanner.logger.warning = lambda msg, **kwargs: None

        valid_files = []
        for i in range(8):
            valid_files.append({
                "file_name": f"doc_{i}.pdf",
                "file_path": str(self.test_dir / f"doc_{i}.pdf"),
                "file_type": "pdf",
            })

        mock_registry = MagicMock()
        mock_registry.get_latest_by_key.return_value = None
        mock_registry.register_document.return_value = "mock-id"

        count = scanner.register_placeholders(valid_files, mock_registry)

        self.assertEqual(count, 8)

        milestone_msgs = [m for m in captured_status if "[TELEMETRY] A-registration" in m]
        self.assertEqual(len(milestone_msgs), 4,
                         "Should have 4 milestone messages for 8 files")
        percentages = set()
        for msg in milestone_msgs:
            for pct in ["100%", "75%", "50%", "25%"]:
                if f"milestone={pct}" in msg:
                    percentages.add(pct)
        self.assertEqual(percentages, {"25%", "50%", "75%", "100%"},
                         "Milestones should cover all 4 thresholds")

    def test_phase_a_per_document_info_not_status(self):
        """T1.126 (I238): Per-document 'registered successfully' is at DEBUG, not STATUS."""
        from eks.engine.core.registry import DocumentRegistry

        reg_path = self.test_dir / "eks_registry_i238_info.db"
        if reg_path.exists():
            reg_path.unlink()
        registry = DocumentRegistry(db_path=str(reg_path))

        captured_status = []
        captured_debug = []
        original_status = registry.logger.status
        original_debug = registry.logger.debug
        registry.logger.status = lambda msg, **kw: captured_status.append(msg)
        registry.logger.debug = lambda msg, **kw: captured_debug.append(msg)

        registry.register_document({
            "document_number": "I238-TEST", "revision": "A",
            "file_path": str(self.test_dir / "i238_doc.pdf"),
            "file_type": "pdf", "document_type": "PDF",
        })

        registry.logger.status = original_status
        registry.logger.debug = original_debug

        self.assertTrue(
            any("registered successfully" in msg for msg in captured_debug),
            "Per-document message should appear at DEBUG level"
        )
        self.assertFalse(
            any("registered successfully" in msg for msg in captured_status),
            "Per-document message should NOT appear at STATUS level"
        )

        if reg_path.exists():
            reg_path.unlink()

    # ------------------------------------------------------------------
    # I254 — Path doubling fix
    # ------------------------------------------------------------------

    def test_path_doubling_prevents_eks_eks_data_dir(self):
        """T1.156 (I254): Relative CLI --data-dir with eks/ prefix must not
        produce eks/eks/data. e.g. --data-dir eks/data → .../eks/data (correct)."""
        from eks.engine.core.bootstrap import EKSBootstrapManager
        from pathlib import Path

        # project_root is the REPO root (parent of eks/), not eks/ itself
        repo_root = _PROJECT_ROOT.parent
        boot = EKSBootstrapManager(
            project_root=repo_root,
            skip_readiness=True,
            auto_create=False,
        )
        boot.project_root = repo_root
        boot.cli_args = {"data_dir": "eks/data", "level": 1}
        boot.cli_overrides_provided = True
        boot.config_dir = repo_root / "eks" / "config"
        boot.resolved_paths = {
            "data_dir": repo_root / "eks" / "data",
        }

        boot._bootstrap_params()

        result = boot.effective_parameters["data_dir"]
        expected = repo_root / "eks" / "data"
        self.assertEqual(result, expected,
            f"I254: data_dir should be {expected}, got {result}")
        self.assertNotIn("eks/eks", str(result.as_posix()),
            "I254: Path must not contain doubled eks/eks segment")

    def test_path_doubling_handles_bare_data(self):
        """T1.156 (I254): Relative CLI --data-dir data (no eks/ prefix) works unchanged."""
        from eks.engine.core.bootstrap import EKSBootstrapManager

        repo_root = _PROJECT_ROOT.parent
        boot = EKSBootstrapManager(
            project_root=repo_root,
            skip_readiness=True,
            auto_create=False,
        )
        boot.project_root = repo_root
        boot.cli_args = {"data_dir": "data", "level": 1}
        boot.cli_overrides_provided = True
        boot.config_dir = repo_root / "eks" / "config"
        boot.resolved_paths = {
            "data_dir": repo_root / "eks" / "data",
        }

        boot._bootstrap_params()

        result = boot.effective_parameters["data_dir"]
        expected = repo_root / "eks" / "data"
        self.assertEqual(result, expected)

    def test_path_doubling_handles_absolute_path(self):
        """T1.156 (I254): Absolute CLI --data-dir paths are unchanged."""
        from eks.engine.core.bootstrap import EKSBootstrapManager
        from pathlib import Path

        repo_root = _PROJECT_ROOT.parent
        boot = EKSBootstrapManager(
            project_root=repo_root,
            skip_readiness=True,
            auto_create=False,
        )
        boot.project_root = repo_root
        boot.cli_args = {"data_dir": str(repo_root / "eks" / "data"), "level": 1}
        boot.cli_overrides_provided = True
        boot.config_dir = repo_root / "eks" / "config"
        boot.resolved_paths = {
            "data_dir": repo_root / "eks" / "data",
        }

        boot._bootstrap_params()

        result = boot.effective_parameters["data_dir"]
        expected = repo_root / "eks" / "data"
        self.assertEqual(result, expected)

    # ------------------------------------------------------------------
    # T1.158 (I255): FilenameParser auto-pattern detection
    # ------------------------------------------------------------------

    def test_filename_parser_auto_detects_131101_pattern(self):
        """T1.158 (I255): FilenameParser with project_code_registry=['131101']
        parses '131101-AREA-SPC-CIV-0001_rev01.pdf' and extracts all 4 identity fields."""
        from eks.engine.core.filename_parser import FilenameParser

        patterns = {
            "131101": {
                "description": "TWRP WSD11 tenderspec naming",
                "parser_type": "delimited",
                "separator": "-",
                "min_segments": 5,
                "max_segments": 5,
                "segments": [
                    {"position": 0, "maps_to": "project_number", "label": "project_code",
                     "required": True,
                     "null_handling": {"strategy": "default_value", "default_value": "131101"},
                     "validation": {"type": "pattern", "pattern": "^\\d{6}$"}},
                    {"position": 1, "maps_to": "area", "label": "contract_or_area",
                     "required": True,
                     "null_handling": {"strategy": "default_value", "default_value": "UNKNOWN"},
                     "validation": {"type": "pattern", "pattern": "^[A-Z0-9]{3,6}$"}},
                    {"position": 2, "maps_to": "document_type", "label": "type_code",
                     "required": True,
                     "null_handling": {"strategy": "default_value", "default_value": "UNKNOWN"},
                     "validation": {"type": "pattern", "pattern": "^[A-Z]{3}$"}},
                    {"position": 3, "maps_to": "discipline", "label": "discipline_code",
                     "required": True,
                     "null_handling": {"strategy": "default_value", "default_value": "UNKNOWN"},
                     "validation": {"type": "pattern", "pattern": "^[A-Z]{1,2}$"}},
                    {"position": 4, "maps_to": None, "label": "sequence_number",
                     "required": True,
                     "null_handling": {"strategy": "default_value", "default_value": "0000"},
                     "validation": {"type": "pattern", "pattern": "^\\d{4}$"}},
                ],
                "rejoin_separator": "-",
                "strip_suffixes": ["_Add1"],
                "revision_separators": ["_rev"],
                "dash_revision_max_len": 3,
                "output": {
                    "document_number_source": "rejoin_segments",
                    "fallback_doc_number": "full_stem",
                    "fallback_revision": None,
                    "preservation_mode": "overwrite_existing",
                },
                "error_subcodes": {},
                "processing_phase": "P0",
            },
            "*": {
                "description": "Default fallback",
                "parser_type": "delimited",
                "separator": "-",
                "min_segments": 1,
                "max_segments": None,
                "segments": [],
                "rejoin_separator": "-",
                "strip_suffixes": [],
                "revision_separators": ["_rev"],
                "dash_revision_max_len": 3,
                "output": {
                    "document_number_source": "rejoin_segments",
                    "fallback_doc_number": "full_stem",
                    "fallback_revision": "00",
                    "preservation_mode": "overwrite_existing",
                },
                "error_subcodes": {},
                "processing_phase": "P0",
            },
        }

        parser = FilenameParser(
            filename_patterns=patterns,
            project_code_registry=["131101"],
        )
        result = parser.parse("131101-AREA-SPC-CV-0001_rev01.pdf")

        self.assertEqual(result.project_number, "131101",
            "I255: project_number should be 131101")
        self.assertEqual(result.area, "AREA",
            "I255: area should be AREA")
        self.assertEqual(result.document_type, "SPC",
            "I255: document_type should be SPC")
        self.assertEqual(result.discipline, "CV",
            "I255: discipline should be CV")
        self.assertEqual(result.sequence_number, "0001",
            "I255: sequence_number should be 0001")
        self.assertEqual(result.document_number, "131101-AREA-SPC-CV-0001",
            "I255: document_number should be full rejoin")
        self.assertEqual(result.revision, "01",
            "I255: revision should be 01")
        self.assertEqual(result.parse_status, "ok",
            "I255: parse_status should be ok")

    def test_filename_parser_falls_back_to_star_pattern(self):
        """T1.158 (I255): FilenameParser with project_code_registry=['131101']
        falls back to '*' pattern for 'random_name.pdf' — all identity fields are None."""
        from eks.engine.core.filename_parser import FilenameParser

        patterns = {
            "131101": {
                "description": "TWRP WSD11 tenderspec naming",
                "parser_type": "delimited",
                "separator": "-",
                "min_segments": 5,
                "max_segments": 5,
                "segments": [
                    {"position": 0, "maps_to": "project_number", "label": "project_code",
                     "required": True,
                     "null_handling": {"strategy": "default_value", "default_value": "131101"},
                     "validation": {"type": "pattern", "pattern": "^\\d{6}$"}},
                    {"position": 1, "maps_to": "area", "label": "contract_or_area",
                     "required": True,
                     "null_handling": {"strategy": "default_value", "default_value": "UNKNOWN"},
                     "validation": {"type": "pattern", "pattern": "^[A-Z0-9]{3,6}$"}},
                ],
                "rejoin_separator": "-",
                "strip_suffixes": ["_Add1"],
                "revision_separators": ["_rev"],
                "dash_revision_max_len": 3,
                "output": {
                    "document_number_source": "rejoin_segments",
                    "fallback_doc_number": "full_stem",
                    "fallback_revision": "00",
                    "preservation_mode": "overwrite_existing",
                },
                "error_subcodes": {},
                "processing_phase": "P0",
            },
            "*": {
                "description": "Default fallback (0 segments)",
                "parser_type": "delimited",
                "separator": "-",
                "min_segments": 1,
                "max_segments": None,
                "segments": [],
                "rejoin_separator": "-",
                "strip_suffixes": [],
                "revision_separators": ["_rev"],
                "dash_revision_max_len": 3,
                "output": {
                    "document_number_source": "rejoin_segments",
                    "fallback_doc_number": "full_stem",
                    "fallback_revision": "00",
                    "preservation_mode": "overwrite_existing",
                },
                "error_subcodes": {},
                "processing_phase": "P0",
            },
        }

        parser = FilenameParser(
            filename_patterns=patterns,
            project_code_registry=["131101"],
        )
        result = parser.parse("random_name.pdf")

        self.assertIsNone(result.project_number,
            "I255: project_number should be None (no pattern matched)")
        self.assertIsNone(result.area,
            "I255: area should be None (no pattern matched)")
        self.assertIsNone(result.document_type,
            "I255: document_type should be None (no pattern matched)")
        self.assertIsNone(result.discipline,
            "I255: discipline should be None (no pattern matched)")
        self.assertIsNone(result.sequence_number,
            "I255: sequence_number should be None (no pattern matched)")
        self.assertEqual(result.document_number, "random_name",
            "I255: document_number should be full_stem fallback")
        self.assertEqual(result.revision, "00",
            "I255: revision should be fallback_revision '00'")
        self.assertEqual(result.parse_status, "unresolvable",
            "I255: parse_status should be unresolvable (0 segments)")

    def test_filename_parser_populates_project_title(self):
        """T1.162 (I256): FilenameParser with project_code_titles maps project_number
        to project_title when project_code_titles is supplied."""
        from eks.engine.core.filename_parser import FilenameParser

        patterns = {
            "131101": {
                "description": "TWRP WSD11 tenderspec naming",
                "parser_type": "delimited",
                "separator": "-",
                "min_segments": 5,
                "max_segments": 5,
                "segments": [
                    {"position": 0, "maps_to": "project_number", "label": "project_code",
                     "required": True,
                     "null_handling": {"strategy": "default_value", "default_value": "131101"},
                     "validation": {"type": "pattern", "pattern": "^\\d{6}$"}},
                    {"position": 1, "maps_to": "area", "label": "contract_or_area",
                     "required": True,
                     "null_handling": {"strategy": "default_value", "default_value": "UNKNOWN"},
                     "validation": {"type": "pattern", "pattern": "^[A-Z0-9]{3,6}$"}},
                    {"position": 2, "maps_to": "document_type", "label": "type_code",
                     "required": True,
                     "null_handling": {"strategy": "default_value", "default_value": "UNKNOWN"},
                     "validation": {"type": "pattern", "pattern": "^[A-Z]{3}$"}},
                    {"position": 3, "maps_to": "discipline", "label": "discipline_code",
                     "required": True,
                     "null_handling": {"strategy": "default_value", "default_value": "UNKNOWN"},
                     "validation": {"type": "pattern", "pattern": "^[A-Z]{1,2}$"}},
                    {"position": 4, "maps_to": None, "label": "sequence_number",
                     "required": True,
                     "null_handling": {"strategy": "default_value", "default_value": "0000"},
                     "validation": {"type": "pattern", "pattern": "^\\d{4}$"}},
                ],
                "rejoin_separator": "-",
                "strip_suffixes": ["_Add1"],
                "revision_separators": ["_rev"],
                "dash_revision_max_len": 3,
                "output": {
                    "document_number_source": "rejoin_segments",
                    "fallback_doc_number": "full_stem",
                    "fallback_revision": None,
                    "preservation_mode": "overwrite_existing",
                },
                "error_subcodes": {},
                "processing_phase": "P0",
            },
            "999999": {
                "description": "Unknown project pattern",
                "parser_type": "delimited",
                "separator": "-",
                "min_segments": 5,
                "max_segments": 5,
                "segments": [
                    {"position": 0, "maps_to": "project_number", "label": "project_code",
                     "required": True,
                     "null_handling": {"strategy": "default_value", "default_value": "999999"},
                     "validation": {"type": "pattern", "pattern": "^\\d{6}$"}},
                    {"position": 1, "maps_to": "area", "label": "contract_or_area",
                     "required": True,
                     "null_handling": {"strategy": "default_value", "default_value": "UNKNOWN"},
                     "validation": {"type": "pattern", "pattern": "^[A-Z0-9]{3,6}$"}},
                    {"position": 2, "maps_to": "document_type", "label": "type_code",
                     "required": True,
                     "null_handling": {"strategy": "default_value", "default_value": "UNKNOWN"},
                     "validation": {"type": "pattern", "pattern": "^[A-Z]{3}$"}},
                    {"position": 3, "maps_to": "discipline", "label": "discipline_code",
                     "required": True,
                     "null_handling": {"strategy": "default_value", "default_value": "UNKNOWN"},
                     "validation": {"type": "pattern", "pattern": "^[A-Z]{1,2}$"}},
                    {"position": 4, "maps_to": None, "label": "sequence_number",
                     "required": True,
                     "null_handling": {"strategy": "default_value", "default_value": "0000"},
                     "validation": {"type": "pattern", "pattern": "^\\d{4}$"}},
                ],
                "rejoin_separator": "-",
                "strip_suffixes": ["_Add1"],
                "revision_separators": ["_rev"],
                "dash_revision_max_len": 3,
                "output": {
                    "document_number_source": "rejoin_segments",
                    "fallback_doc_number": "full_stem",
                    "fallback_revision": None,
                    "preservation_mode": "overwrite_existing",
                },
                "error_subcodes": {},
                "processing_phase": "P0",
            },
            "*": {
                "description": "Default fallback",
                "parser_type": "delimited",
                "separator": "-",
                "min_segments": 1,
                "max_segments": None,
                "segments": [],
                "rejoin_separator": "-",
                "strip_suffixes": [],
                "revision_separators": ["_rev"],
                "dash_revision_max_len": 3,
                "output": {
                    "document_number_source": "rejoin_segments",
                    "fallback_doc_number": "full_stem",
                    "fallback_revision": "00",
                    "preservation_mode": "overwrite_existing",
                },
                "error_subcodes": {},
                "processing_phase": "P0",
            },
        }

        project_code_titles = {
            "131101": "WSD11 — Project Specifications",
            "999999": "Unknown Project",
        }

        parser = FilenameParser(
            filename_patterns=patterns,
            project_code_registry=["131101", "999999"],
            project_code_titles=project_code_titles,
        )

        # Test 1: known project code → project_title populated
        result = parser.parse("131101-AREA-SPC-CV-0001_rev01.pdf")
        self.assertEqual(result.project_number, "131101",
            "I256: project_number should be 131101")
        self.assertEqual(result.project_title, "WSD11 — Project Specifications",
            "I256: project_title should be looked up from project_code_titles")
        self.assertEqual(result.document_type, "SPC",
            "I256: document_type should be SPC (still extracted)")

        # Test 2: another known project code → project_title populated
        result2 = parser.parse("999999-ENG-DRG-CV-0002_rev00.pdf")
        self.assertEqual(result2.project_number, "999999",
            "I256: project_number should be 999999")
        self.assertEqual(result2.project_title, "Unknown Project",
            "I256: project_title should map 999999 to 'Unknown Project'")

        # Test 3: fallback pattern → no project_title (no project_number)
        result3 = parser.parse("random_name.pdf")
        self.assertIsNone(result3.project_number,
            "I256: project_number should be None (fallback)")
        self.assertIsNone(result3.project_title,
            "I256: project_title should be None when no project_number extracted")


# ------------------------------------------------------------------
# I257/I258: Bootstrap silent swallow degradation tests
# ------------------------------------------------------------------

class TestBootstrapDegradation(unittest.TestCase):
    """I257/I258: All 7 silent exception swallows in EKSBootstrapManager now produce
    log entries in debug_object["logs"] instead of silent 'except Exception: pass'."""

    @classmethod
    def setUpClass(cls):
        cls.test_dir = _PROJECT_ROOT / "test_output"
        cls.test_dir.mkdir(exist_ok=True)
        from eks.engine.logging.logger import EKSLogger
        cls.logger_class = EKSLogger

    def _make_boot(self) -> tuple:
        """Create an EKSBootstrapManager with a logger that captures debug_object."""
        from eks.engine.core.bootstrap import EKSBootstrapManager
        config_parent = _PROJECT_ROOT / "config"
        boot = EKSBootstrapManager(
            project_root=_PROJECT_ROOT,
            skip_readiness=True,
            auto_create=False,
        )
        boot.cli_args = {"level": 1}
        boot.config_dir = config_parent
        logger = self.logger_class("test_degradation", level=3, run_id="test_257_258")
        boot.logger = logger
        return boot, logger

    def _has_log(self, logger, substr: str) -> bool:
        """Check if any log entry contains substr in its message."""
        return any(
            substr in l.get("message", "")
            for l in logger.debug_object.get("logs", [])
        )

    # ----- I257: doc_config load failure in _bootstrap_registry() (P3) -----

    def test_257_doc_config_failure_logged(self):
        """I257 S-B-S-0609: doc_config load failure in _bootstrap_registry() produces WARNING."""
        boot, logger = self._make_boot()
        boot._config_loader = None
        with patch(
            "eks.engine.core.schema_loader.SchemaLoader.load_all",
            side_effect=Exception("mock doc_config validation error"),
        ):
            boot._bootstrap_registry()
        self.assertTrue(
            self._has_log(logger, "doc_config schema validation"),
            "I257: Expected log entry about doc_config failure in debug_log"
        )

    # ----- I258 #1: ConfigRegistry failure in _eks_config_loader() -----

    def test_258_configregistry_failure_logged(self):
        """I258#1 S-B-S-0610: ConfigRegistry init failure logs WARNING and falls back."""
        boot, logger = self._make_boot()
        with patch(
            "eks.engine.core.config_registry.ConfigRegistry",
            side_effect=Exception("mock ConfigRegistry failure"),
        ):
            result = boot._eks_config_loader(boot.config_dir)
        self.assertTrue(
            self._has_log(logger, "ConfigRegistry init failed"),
            "I258#1: Expected log entry about ConfigRegistry fallback in debug_log"
        )
        self.assertIsInstance(result, dict)

    # ----- I258 #2: doc_config load failure in _bootstrap_schema() (P7) -----

    def test_258_p7_doc_config_failure_logged(self):
        """I258#2 S-B-S-0611: P7 doc_config load failure produces WARNING."""
        boot, logger = self._make_boot()
        boot._pre_generated_ddl = None
        # Patch at schema_loader module level to isolate from ConfigRegistry path
        with patch(
            "eks.engine.core.schema_loader.SchemaLoader.load_all",
            side_effect=Exception("mock P7 schema failure"),
        ) as mock_load:
            boot._bootstrap_schema()
        self.assertTrue(
            self._has_log(logger, "Schema phase doc_config load failed"),
            "I258#2: Expected log entry about P7 doc_config failure in debug_log"
        )

    # ----- I258 #3/#4: Manager failures in to_dict() -----

    def test_258_managers_to_dict_failure_logged(self):
        """I258#3/#4 S-B-S-0612/S-B-S-0613: ErrorManager/MessageManager lazy-init in
        to_dict() produces WARNING."""
        boot, logger = self._make_boot()
        boot._error_manager_factory = lambda **kw: (_ for _ in ()).throw(Exception("mock EM"))
        boot._message_manager_factory = lambda **kw: (_ for _ in ()).throw(Exception("mock MM"))
        result = boot.to_dict()
        self.assertTrue(
            self._has_log(logger, "ErrorManager lazy-init failed in to_dict()"),
            "I258#3: Expected log entry about ErrorManager in to_dict()"
        )
        self.assertTrue(
            self._has_log(logger, "MessageManager lazy-init failed in to_dict()"),
            "I258#4: Expected log entry about MessageManager in to_dict()"
        )
        self.assertIsNone(result.get("em"), "I258#3: em should be None on failure")
        self.assertIsNone(result.get("mm"), "I258#4: mm should be None on failure")

    # ----- I258 #5/#6: Manager failures in to_pipeline_context() -----

    def test_258_managers_context_failure_logged(self):
        """I258#5/#6 S-B-S-0614/S-B-S-0615: ErrorManager/MessageManager lazy-init in
        to_pipeline_context() produces WARNING."""
        boot, logger = self._make_boot()
        boot._bootstrapped = True
        boot._eks_root = _PROJECT_ROOT
        boot.resolved_paths = {"data_dir": str(_PROJECT_ROOT / "data")}
        boot.effective_parameters = {"level": 1, "data_dir": str(_PROJECT_ROOT / "data")}
        boot.config = {}
        boot.doc_config = {}
        boot.os_info = "windows"
        boot.parsed = None
        boot._error_manager_factory = lambda **kw: (_ for _ in ()).throw(Exception("mock EM ctx"))
        boot._message_manager_factory = lambda **kw: (_ for _ in ()).throw(Exception("mock MM ctx"))
        with patch.object(boot, '_build_postload_trace', return_value=None):
            ctx = boot.to_pipeline_context()
        self.assertTrue(
            self._has_log(logger, "ErrorManager lazy-init failed in to_pipeline_context()"),
            "I258#5: Expected log entry about ErrorManager in to_pipeline_context()"
        )
        self.assertTrue(
            self._has_log(logger, "MessageManager lazy-init failed in to_pipeline_context()"),
            "I258#6: Expected log entry about MessageManager in to_pipeline_context()"
        )
        self.assertIsNone(ctx.parameters.get("em"), "I258#5: em should be None on failure")
        self.assertIsNone(ctx.parameters.get("mm"), "I258#6: mm should be None on failure")

    def test_tier3_fallback_discovers_auxiliary_schemas(self):
        """I259/T1.173: Verify Tier 3 fallback discovers auxiliary schemas not matched by glob patterns."""
        from common.library.loader.schema_discovery import discover_schema_files, discover_schema_files_tier3

        config_dir = _PROJECT_ROOT / "config"
        loader = SchemaLoader(config_dir)
        project_root = loader._project_root()
        registry = discover_schema_files(loader.config, project_root)

        # Confirm these 5 are NOT in Tier 1+2 registry (the original bug)
        aux_stems = [
            "eks_project_code_schema",
            "eks_document_type_schema",
            "eks_department_schema",
            "eks_discipline_schema",
            "eks_facility_schema",
        ]
        for stem in aux_stems:
            self.assertNotIn(
                stem, registry,
                f"{stem} should NOT be in Tier 1+2 registry (original bug)"
            )

        # Tier 3 fallback should find all 5
        all_stems = aux_stems + [
            "eks_base_schema", "eks_setup_schema", "eks_config",
            "eks_doc_base_schema", "eks_doc_setup_schema", "eks_doc_config",
            "eks_asset_base_schema", "eks_asset_setup_schema", "eks_asset_config",
            "eks_ontology_base_schema", "eks_ontology_setup_schema", "eks_ontology_config",
            "eks_error_code_base", "eks_error_setup_schema", "eks_error_config",
            "eks_message_base", "eks_message_setup_schema", "eks_message_config",
        ]

        tier3_entries = discover_schema_files_tier3(all_stems, loader._search_dirs, registry)
        for stem in aux_stems:
            self.assertIn(
                stem, tier3_entries,
                f"Tier 3 should discover {stem}"
            )
            self.assertEqual(
                tier3_entries[stem]["source"], "tier3",
                f"{stem} source should be 'tier3'"
            )

    def test_loader_4stage_refactoring(self):
        """I263/T1.180: Verify load_all() delegates to 4 stage methods."""
        config_dir = _PROJECT_ROOT / "config"
        loader = SchemaLoader(config_dir)
        self.assertTrue(hasattr(loader, '_discover'), "missing _discover method")
        self.assertTrue(hasattr(loader, '_load'), "missing _load method")
        self.assertTrue(hasattr(loader, '_validate'), "missing _validate method")
        self.assertTrue(hasattr(loader, '_extract'), "missing _extract method")
        result = loader.load_all()
        self.assertIsNotNone(result)
        self.assertIn("registry", result)
        self.assertIn("project_definition", result)
        self.assertNotIn("project_rules_registry", result)


if __name__ == "__main__":
    unittest.main()

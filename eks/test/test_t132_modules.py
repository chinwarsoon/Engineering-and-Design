"""
Test T1.32 engine modules: ErrorManager, MessageManager, HealthScorer, StructureDetector, Elements CRUD.
T1.99.141–T1.99.146: Document metadata completeness tests added.
"""
import unittest
import json
import tempfile
import os
from pathlib import Path
from eks.engine.core.error_manager import ErrorManager
from eks.engine.core.message_manager import MessageManager
from eks.engine.core.health_scorer import HealthScorer
from eks.engine.core.structure_detector import StructureDetector

CONFIG_DIR = Path(__file__).parent.parent / "config"


class TestErrorManager(unittest.TestCase):

    def setUp(self):
        self.em = ErrorManager(config_dir=CONFIG_DIR)

    def test_loads_catalog(self):
        self.assertEqual(self.em._catalog.get("metadata", {}).get("total_codes"), 103)

    def test_system_error_lookup(self):
        entry = self.em.get_system_error("S-E-S-0101")
        self.assertIsNotNone(entry)
        self.assertEqual(entry["name"], "MISSING_PACKAGE")

    def test_data_error_lookup(self):
        entry = self.em.get_data_error("P3-E-E-0010")
        self.assertIsNotNone(entry)
        self.assertEqual(entry["name"], "COVER_PAGE_MISSING")

    def test_unknown_error(self):
        entry = self.em.get_code_info("NONEXISTENT")
        self.assertIsNone(entry)

    def test_handle_system_error_no_stop(self):
        entry = self.em.handle_system_error("S-C-S-0305")
        self.assertEqual(entry["code"], "S-C-S-0305")

    def test_handle_data_error(self):
        entry = self.em.handle_data_error("P3-E-E-0010", doc_id="D-001")
        self.assertEqual(entry["health_score_impact"], -3)

    def test_error_summary(self):
        self.em._errors = []
        self.em.handle_data_error("P3-E-E-0001")
        summary = self.em.get_error_summary()
        self.assertEqual(summary["total"], 1)
        self.assertIn("by_severity", summary)

    def test_health_impact_sum(self):
        self.em._errors = []
        self.em.handle_data_error("P3-E-E-0010", doc_id="D-001")
        self.em.handle_data_error("P3-E-E-0011", doc_id="D-001")
        self.assertEqual(self.em.get_health_impact("D-001"), -5)

    def test_fail_fast_disabled(self):
        self.em.set_fail_fast(False)
        entry = self.em.handle_system_error("S-F-S-0201")
        self.assertEqual(entry["code"], "S-F-S-0201")


class TestMessageManager(unittest.TestCase):

    def setUp(self):
        self.mm = MessageManager(config_dir=CONFIG_DIR)

    def test_loads_catalog(self):
        msgs = self.mm._catalog.get("messages", {})
        self.assertGreaterEqual(len(msgs), 32)

    def test_get_message(self):
        msg = self.mm.get("WARNING_NO_COVER_PAGE", filename="test.pdf")
        self.assertIsNotNone(msg)
        self.assertIn("test.pdf", msg)

    def test_empty_params(self):
        msg = self.mm.get("WARNING_NO_COVER_PAGE")
        self.assertIsNotNone(msg)


class TestHealthScorer(unittest.TestCase):

    def setUp(self):
        self.scorer = HealthScorer()

    def test_perfect_doc(self):
        doc = {
            "document_type": "DWG",
            "extraction_confidence": 1.0,
            "extract_status": "success",
            "page_count": 5,
        }
        elements = [
            {"element_type": "cover_page"},
            {"element_type": "revision_table"},
            {"element_type": "section"},
            {"element_type": "image"},
        ]
        score = self.scorer.score(doc, elements)
        # Doc has only 2 of ~23 scorable fields → ceiling ~0.54 under current weights
        self.assertGreaterEqual(score.get("health_score", 0), 0.5)

    def test_missing_cover_page(self):
        doc = {
            "document_type": "DWG",
            "extraction_confidence": 0.5,
            "page_count": 1,
        }
        elements = []
        score = self.scorer.score(doc, elements)
        self.assertLess(score.get("health_score", 1), 0.6)

    def test_score_batch(self):
        # Doc 1: richer metadata (3 populated fields → higher completeness)
        docs = [
            {"document_type": "DWG", "project_number": "P001", "discipline": "ME",
             "extraction_confidence": 0.9, "extract_status": "success"},
            {"document_type": "SPC", "extraction_confidence": 0.3},
        ]
        elements_list = [
            [{"element_type": "cover_page"}],
            [],
        ]
        results = self.scorer.score_batch(docs, elements_list)
        self.assertEqual(results["total_documents"], 2)
        self.assertGreaterEqual(results["avg_document_health"], 0.0)
        self.assertLessEqual(results["avg_document_health"], 1.0)
        # Doc 1 has more populated fields → should score higher than doc 2
        score1 = self.scorer.score(docs[0], elements_list[0])
        score2 = self.scorer.score(docs[1], elements_list[1])
        self.assertGreater(score1.get("health_score", 0), score2.get("health_score", 1))


class TestStructureDetector(unittest.TestCase):

    def setUp(self):
        self.detector = StructureDetector()

    def test_empty_input(self):
        elements = self.detector.detect("dummy.pdf", pages=[{"text": "", "tables": [], "images": []}])
        self.assertIsInstance(elements, list)

    def test_detects_cover_page_fields(self):
        pages = [{
            "text": "PROJECT: Test Project\nDOC NO: DWG-001\nREV: A",
            "tables": [],
            "images": [],
        }]
        elements = self.detector.detect("test.pdf", pages=pages)
        self.assertTrue(any(el["element_type"] == "cover_page" for el in elements))


# ---------------------------------------------------------------------------
# T1.99.141–T1.99.146: Document Metadata Completeness Tests
# ---------------------------------------------------------------------------

class TestDocumentMetadataCompleteness(unittest.TestCase):
    """Tests for the 15 new metadata columns added in T1.99.141–T1.99.146."""

    @classmethod
    def setUpClass(cls):
        """Set up a DocumentRegistry for testing."""
        from eks.engine.core.registry import DocumentRegistry
        from eks.engine.logging.logger import EKSLogger

        cls.logger = EKSLogger("TestRegistry", level=0)
        cls.registry = DocumentRegistry(logger=cls.logger)

    @classmethod
    def tearDownClass(cls):
        """Clean up test DB."""
        import shutil
        # Clean up output dir created by the test registry
        default_db = Path("eks/output/eks_registry.db")
        if default_db.exists():
            try:
                default_db.unlink()
            except OSError:
                pass

    # ------------------------------------------------------------------
    # T1.99.141 — supersedes / superseded_by revision chain
    # ------------------------------------------------------------------

    def test_141_supersedes_chain_three_revisions(self):
        """SC-1: Register 3 revisions → B.supersedes=A, C.supersedes=B, A.superseded_by=B, B.superseded_by=C."""
        meta_a = {
            "document_number": "DWG-0141",
            "revision": "A",
            "project_title": "Test",
            "project_number": "P141",
            "document_type": "DWG",
            "file_path": "data/dwg0141_a.pdf",
        }
        meta_b = dict(meta_a, revision="B", file_path="data/dwg0141_b.pdf")
        meta_c = dict(meta_a, revision="C", file_path="data/dwg0141_c.pdf")

        id_a = self.registry.register_document(meta_a)
        id_b = self.registry.register_document(meta_b)
        id_c = self.registry.register_document(meta_c)

        # Check chain direction
        doc_a = self.registry.get_document("DWG-0141", revision="A")
        doc_b = self.registry.get_document("DWG-0141", revision="B")
        doc_c = self.registry.get_document("DWG-0141", revision="C")

        self.assertIsNotNone(doc_a)
        self.assertIsNotNone(doc_b)
        self.assertIsNotNone(doc_c)

        # B supersedes A
        self.assertEqual(doc_b.get("supersedes"), id_a)
        self.assertEqual(doc_a.get("superseded_by"), id_b)

        # C supersedes B
        self.assertEqual(doc_c.get("supersedes"), id_b)
        self.assertEqual(doc_b.get("superseded_by"), id_c)

        # A has no supersedes (first revision)
        self.assertIsNone(doc_a.get("supersedes"))
        # C has no superseded_by (latest)
        self.assertIsNone(doc_c.get("superseded_by"))

        # is_latest flag
        self.assertFalse(doc_a.get("is_latest"))
        self.assertFalse(doc_b.get("is_latest"))
        self.assertTrue(doc_c.get("is_latest"))

    def test_141_supersedes_single_revision_no_chain(self):
        """Single (first) revision has no supersedes or superseded_by."""
        meta = {
            "document_number": "DWG-0141b",
            "revision": "00",
            "project_title": "Test",
            "project_number": "P141b",
            "document_type": "DWG",
            "file_path": "data/first.pdf",
        }
        doc_id = self.registry.register_document(meta)
        doc = self.registry.get_document("DWG-0141b")
        self.assertIsNotNone(doc)
        self.assertIsNone(doc.get("supersedes"))
        self.assertIsNone(doc.get("superseded_by"))

    # ------------------------------------------------------------------
    # T1.99.142 — document_title derivation
    # ------------------------------------------------------------------

    def test_142_document_title_from_embedded(self):
        """SC-2: PDF with good embedded_title → document_title = embedded_title."""
        meta = {
            "document_number": "DOC-0142",
            "revision": "A",
            "project_title": "Test",
            "project_number": "P142",
            "document_type": "DWG",
            "embedded_title": "P&ID — Cooling Water System",
            "file_path": "data/cooling_water.pdf",
        }
        self.registry.register_document(meta)
        doc = self.registry.get_document("DOC-0142")
        self.assertEqual(doc.get("document_title"), "P&ID — Cooling Water System")

    def test_142_document_title_fallback_boilerplate(self):
        """SC-3: DOCX with boilerplate embedded_title → falls back to filename stem."""
        meta = {
            "document_number": "DOC-0142b",
            "revision": "A",
            "project_title": "Test",
            "project_number": "P142b",
            "document_type": "SPC",
            "embedded_title": "Microsoft Word — Spec Rev 3",
            "file_path": "data/Pump_Spec_Rev3.docx",
        }
        self.registry.register_document(meta)
        doc = self.registry.get_document("DOC-0142b")
        self.assertEqual(doc.get("document_title"), "Pump_Spec_Rev3")

    def test_142_document_title_fallback_no_embedded(self):
        """No embedded_title → falls back to filename stem."""
        meta = {
            "document_number": "DOC-0142c",
            "revision": "A",
            "project_title": "Test",
            "project_number": "P142c",
            "document_type": "DWG",
            "file_path": "data/flow_diagram.pdf",
        }
        self.registry.register_document(meta)
        doc = self.registry.get_document("DOC-0142c")
        self.assertEqual(doc.get("document_title"), "flow_diagram")

    def test_142_document_title_explicit_override(self):
        """Explicitly provided document_title is not overwritten."""
        meta = {
            "document_number": "DOC-0142d",
            "revision": "A",
            "project_title": "Test",
            "project_number": "P142d",
            "document_type": "DWG",
            "document_title": "Manual Override Title",
            "embedded_title": "P&ID — Other",
            "file_path": "data/other.pdf",
        }
        self.registry.register_document(meta)
        doc = self.registry.get_document("DOC-0142d")
        self.assertEqual(doc.get("document_title"), "Manual Override Title")

    # ------------------------------------------------------------------
    # T1.99.143 — lifecycle_stage, revision_date, revision_description
    # ------------------------------------------------------------------

    def test_143_lifecycle_stage_default_draft(self):
        """SC-4: New document → lifecycle_stage = 'draft' (default)."""
        meta = {
            "document_number": "DOC-0143",
            "revision": "A",
            "project_title": "Test",
            "project_number": "P143",
            "document_type": "DWG",
            "file_path": "data/draft_doc.pdf",
        }
        self.registry.register_document(meta)
        doc = self.registry.get_document("DOC-0143")
        # Default from schema; populated by SchemaToDDL DEFAULT or by code
        # (DuckDB may set the DEFAULT on ALTER TABLE)
        self.assertEqual(doc.get("lifecycle_stage"), "draft")

    def test_143_lifecycle_stage_explicit(self):
        """Explicit lifecycle_stage is preserved."""
        meta = {
            "document_number": "DOC-0143b",
            "revision": "A",
            "project_title": "Test",
            "project_number": "P143b",
            "document_type": "DWG",
            "lifecycle_stage": "issued_for_construction",
            "file_path": "data/ifc_doc.pdf",
        }
        self.registry.register_document(meta)
        doc = self.registry.get_document("DOC-0143b")
        self.assertEqual(doc.get("lifecycle_stage"), "issued_for_construction")

    def test_143_revision_description_passed_through(self):
        """revision_description from metadata is stored."""
        meta = {
            "document_number": "DOC-0143c",
            "revision": "B",
            "project_title": "Test",
            "project_number": "P143c",
            "document_type": "DWG",
            "revision_description": "Added valve V-101 per CR-042",
            "file_path": "data/revised.pdf",
        }
        self.registry.register_document(meta)
        doc = self.registry.get_document("DOC-0143c")
        self.assertEqual(doc.get("revision_description"), "Added valve V-101 per CR-042")

    def test_143_revision_date_passed_through(self):
        """revision_date from metadata is stored."""
        meta = {
            "document_number": "DOC-0143d",
            "revision": "A",
            "project_title": "Test",
            "project_number": "P143d",
            "document_type": "DWG",
            "revision_date": "2026-07-15T10:30:00Z",
            "file_path": "data/dated.pdf",
        }
        self.registry.register_document(meta)
        doc = self.registry.get_document("DOC-0143d")
        self.assertEqual(doc.get("revision_date"), "2026-07-15T10:30:00Z")

    # ------------------------------------------------------------------
    # T1.99.144 — embedded_revision_number
    # ------------------------------------------------------------------

    def test_144_embedded_revision_number_stored(self):
        """embedded_revision_number is stored via _REGISTRY_MAP."""
        meta = {
            "document_number": "DOC-0144",
            "revision": "A",
            "project_title": "Test",
            "project_number": "P144",
            "document_type": "SPC",
            "embedded_revision_number": "5",
            "file_path": "data/spec_rev5.docx",
        }
        self.registry.register_document(meta)
        doc = self.registry.get_document("DOC-0144")
        self.assertEqual(doc.get("embedded_revision_number"), "5")

    def test_144_registry_map_has_embedded_revision(self):
        """FilePropertyResult._REGISTRY_MAP includes embedded_revision_number."""
        from eks.engine.core.file_property_parser import FilePropertyResult
        result = FilePropertyResult()
        self.assertIn("embedded_revision_number", result._REGISTRY_MAP)
        self.assertEqual(result._REGISTRY_MAP["embedded_revision_number"], "embedded_revision_number")

    # ------------------------------------------------------------------
    # T1.99.145 — references_documents
    # ------------------------------------------------------------------

    def test_145_references_documents_default_empty(self):
        """SC-7: New document → references_documents = [] (empty array)."""
        meta = {
            "document_number": "DOC-0145",
            "revision": "A",
            "project_title": "Test",
            "project_number": "P145",
            "document_type": "PI-PID",
            "file_path": "data/pandid.pdf",
        }
        self.registry.register_document(meta)
        doc = self.registry.get_document("DOC-0145")
        refs = doc.get("references_documents")
        # JSON array stored as string in DuckDB — parse if needed
        if isinstance(refs, str):
            refs = json.loads(refs)
        self.assertEqual(refs, [])

    def test_145_references_documents_json_roundtrip(self):
        """references_documents JSON survives roundtrip."""
        meta = {
            "document_number": "DOC-0145b",
            "revision": "A",
            "project_title": "Test",
            "project_number": "P145b",
            "document_type": "PI-PID",
            "references_documents": ["DS-0001-A", "SPC-0002-B"],
            "file_path": "data/pandid2.pdf",
        }
        self.registry.register_document(meta)
        doc = self.registry.get_document("DOC-0145b")
        refs = doc.get("references_documents")
        if isinstance(refs, str):
            refs = json.loads(refs)
        self.assertEqual(refs, ["DS-0001-A", "SPC-0002-B"])

    def test_145_ontology_trigger_in_config(self):
        """eks_doc_config.json has references_documents → REFERENCES_DOC trigger."""
        config_path = CONFIG_DIR / "schemas" / "eks_doc_config.json"
        if not config_path.exists():
            config_path = CONFIG_DIR / "eks_doc_config.json"
        with open(config_path) as f:
            config = json.load(f)
        triggers = config.get("ontology_triggers", {})
        self.assertIn("references_documents", triggers)
        self.assertEqual(triggers["references_documents"], "REFERENCES_DOC")

    # ------------------------------------------------------------------
    # T1.99.146 — project_phase, contract_package, issued_date,
    #             responsible_engineer, total_sheets, language, vendor_name
    # ------------------------------------------------------------------

    def test_146_language_default_en(self):
        """SC-12: New document → language = 'en' (default)."""
        meta = {
            "document_number": "DOC-0146",
            "revision": "A",
            "project_title": "Test",
            "project_number": "P146",
            "document_type": "DWG",
            "file_path": "data/lang_test.pdf",
        }
        self.registry.register_document(meta)
        doc = self.registry.get_document("DOC-0146")
        self.assertEqual(doc.get("language"), "en")

    def test_146_total_sheets_defaults_to_page_count(self):
        """SC-13: PDF with page_count=5 → total_sheets=5."""
        meta = {
            "document_number": "DOC-0146b",
            "revision": "A",
            "project_title": "Test",
            "project_number": "P146b",
            "document_type": "DWG",
            "page_count": 5,
            "file_path": "data/sheets_test.pdf",
        }
        self.registry.register_document(meta)
        doc = self.registry.get_document("DOC-0146b")
        self.assertEqual(doc.get("total_sheets"), 5)

    def test_146_total_sheets_null_when_no_page_count(self):
        """total_sheets is None when page_count is not provided."""
        meta = {
            "document_number": "DOC-0146c",
            "revision": "A",
            "project_title": "Test",
            "project_number": "P146c",
            "document_type": "DWG",
            "file_path": "data/no_pages.dgn",
        }
        self.registry.register_document(meta)
        doc = self.registry.get_document("DOC-0146c")
        self.assertIsNone(doc.get("total_sheets"))

    def test_146_nullable_columns_no_defaults(self):
        """SC-14: New doc → project_phase, contract_package, issued_date,
        responsible_engineer, vendor_name are NULL."""
        meta = {
            "document_number": "DOC-0146d",
            "revision": "A",
            "project_title": "Test",
            "project_number": "P146d",
            "document_type": "DWG",
            "file_path": "data/nulls_test.pdf",
        }
        self.registry.register_document(meta)
        doc = self.registry.get_document("DOC-0146d")
        self.assertIsNone(doc.get("project_phase"))
        self.assertIsNone(doc.get("contract_package"))
        self.assertIsNone(doc.get("issued_date"))
        self.assertIsNone(doc.get("responsible_engineer"))
        self.assertIsNone(doc.get("vendor_name"))

    def test_146_all_seven_columns_exist_after_migration(self):
        """SC-11: All 7 new columns exist in DB after migration."""
        # Register a fresh doc to ensure columns are present
        meta = {
            "document_number": "DOC-0146g",
            "revision": "A",
            "project_title": "Test",
            "project_number": "P146g",
            "document_type": "DWG",
            "file_path": "data/migration_test.pdf",
        }
        self.registry.register_document(meta)
        doc = self.registry.get_document("DOC-0146g")
        self.assertIsNotNone(doc, "TestSetup: DOC-0146g should have been registered")
        for col in ["project_phase", "contract_package", "issued_date",
                     "responsible_engineer", "total_sheets", "language", "vendor_name"]:
            self.assertIn(col, doc, f"Column '{col}' missing from document")

    def test_146_all_fifteen_new_columns_exist(self):
        """SC-15: All 15 new metadata columns are present in registry."""
        # Use the first doc registered in this test class as sample
        doc = self.registry.get_document("DWG-0141", revision="A")
        self.assertIsNotNone(doc, "TestSetup: DWG-0141-A should exist")
        new_columns = [
            "supersedes", "superseded_by",
            "document_title",
            "lifecycle_stage", "revision_date", "revision_description",
            "embedded_revision_number",
            "references_documents",
            "project_phase", "contract_package", "issued_date",
            "responsible_engineer", "total_sheets", "language", "vendor_name",
        ]
        for col in new_columns:
            self.assertIn(col, doc, f"Column '{col}' missing from document")

    def test_146_language_explicit_override(self):
        """Explicit language override is preserved."""
        meta = {
            "document_number": "DOC-0146e",
            "revision": "A",
            "project_title": "Test",
            "project_number": "P146e",
            "document_type": "DWG",
            "language": "zh",
            "file_path": "data/chinese.pdf",
        }
        self.registry.register_document(meta)
        doc = self.registry.get_document("DOC-0146e")
        self.assertEqual(doc.get("language"), "zh")

    def test_146_total_sheets_explicit_override(self):
        """Explicit total_sheets overrides page_count default."""
        meta = {
            "document_number": "DOC-0146f",
            "revision": "A",
            "project_title": "Test",
            "project_number": "P146f",
            "document_type": "DWG",
            "page_count": 3,
            "total_sheets": 10,
            "file_path": "data/multisheet.pdf",
        }
        self.registry.register_document(meta)
        doc = self.registry.get_document("DOC-0146f")
        self.assertEqual(doc.get("total_sheets"), 10)

    # ------------------------------------------------------------------
    # Cross-task: config validation
    # ------------------------------------------------------------------

    def test_config_docx_has_revision_mapping(self):
        """T1.99.144: DOCX config has revision → embedded_revision_number mapping."""
        config_path = CONFIG_DIR / "schemas" / "eks_doc_config.json"
        if not config_path.exists():
            config_path = CONFIG_DIR / "eks_doc_config.json"
        with open(config_path) as f:
            config = json.load(f)
        docx_mappings = config["file_property_patterns"]["by_file_type"]["docx"]["property_mapping"]
        rev_map = [m for m in docx_mappings if m.get("source_key") == "revision"]
        self.assertEqual(len(rev_map), 1)
        self.assertEqual(rev_map[0]["maps_to"], "embedded_revision_number")

    def test_config_version_bumped(self):
        """Schema and config versions are updated."""
        config_path = CONFIG_DIR / "schemas" / "eks_doc_config.json"
        if not config_path.exists():
            config_path = CONFIG_DIR / "eks_doc_config.json"
        with open(config_path) as f:
            config = json.load(f)
        self.assertEqual(config["version"], "1.5.0")

        base_path = CONFIG_DIR / "schemas" / "eks_doc_base_schema.json"
        if not base_path.exists():
            base_path = CONFIG_DIR / "eks_doc_base_schema.json"
        with open(base_path) as f:
            base = json.load(f)
        self.assertEqual(base["version"], "1.7.0")  # T1.99.150 (I186): UUID id


# ---------------------------------------------------------------------------
# FilePropertyExtractor Tests (existing, preserved)
# ---------------------------------------------------------------------------

class TestFilePropertyExtractor(unittest.TestCase):
    """Tests for FilePropertyExtractor (T1.99.131)."""

    _CONFIG = {
        "os_properties": {
            "enabled": True,
            "collect": ["file_size", "fs_modified", "file_hash"],
            "hash_algorithm": "md5",
        },
        "by_file_type": {
            "pdf": {
                "enabled": True,
                "extraction_method": "parser_metadata",
                "property_mapping": [
                    {"source_key": "author", "maps_to": "created_by",
                     "null_handling": {"strategy": "skip"}, "required": False},
                ],
            },
        },
    }

    def setUp(self):
        from eks.engine.core.file_property_parser import FilePropertyExtractor
        self._extractor = FilePropertyExtractor(self._CONFIG)
        self._temp_files = []

    def tearDown(self):
        for fp in self._temp_files:
            try:
                os.unlink(fp)
            except OSError:
                pass

    def _temp_file(self, name):
        fp = os.path.join(tempfile.gettempdir(), f"eks_test_{name}")
        with open(fp, "w") as f:
            f.write("test content\n" * 10)
        self._temp_files.append(fp)
        return fp

    def test_os_extraction(self):
        f1 = self._temp_file("os.pdf")
        result = self._extractor.extract(f1, "pdf")
        self.assertIsNotNone(result.file_size)
        self.assertGreater(result.file_size, 0)
        self.assertIsNotNone(result.fs_modified)
        self.assertIsNotNone(result.file_hash)
        self.assertEqual(result.extract_status, "ok")

    def test_embedded_extraction_pdf_author(self):
        f1 = self._temp_file("embedded.pdf")
        result = self._extractor.extract(f1, "pdf", parser_metadata={"author": "Alice"})
        self.assertEqual(result.created_by, "Alice")

    def test_file_not_found(self):
        result = self._extractor.extract("/nonexistent/file.pdf", "pdf")
        self.assertEqual(result.extract_status, "failed")
        self.assertTrue(any("not found" in e.lower() for e in result.extract_errors))

    def test_no_config_noop(self):
        from eks.engine.core.file_property_parser import FilePropertyExtractor
        extractor = FilePropertyExtractor(None)
        f1 = self._temp_file("noop.pdf")
        result = extractor.extract(f1, "pdf", parser_metadata={"author": "X"})
        self.assertIsNone(result.file_size)
        self.assertIsNone(result.created_by)

    def test_reuse(self):
        f1 = self._temp_file("r1.pdf")
        f2 = self._temp_file("r2.pdf")
        # Ensure different file sizes by appending to f2
        with open(f2, "a") as fh:
            fh.write("extra bytes for size difference\n" * 5)
        r1 = self._extractor.extract(f1, "pdf", parser_metadata={"author": "Alice"})
        r2 = self._extractor.extract(f2, "pdf", parser_metadata={"author": "Bob"})
        self.assertEqual(r1.created_by, "Alice")
        self.assertEqual(r2.created_by, "Bob")
        self.assertNotEqual(r1.file_size, r2.file_size)
        self.assertNotEqual(r1.file_size, r2.file_size)

    # ------------------------------------------------------------------
    # extract_file_properties convenience function
    # ------------------------------------------------------------------

    def test_convenience_function(self):
        """extract_file_properties() one-shot wrapper works."""
        from eks.engine.core.file_property_parser import extract_file_properties
        fp = self._temp_file("test.pdf")
        result = extract_file_properties(fp, "pdf", self._CONFIG,
                                          parser_metadata={"author": "Test"})
        self.assertEqual(result.created_by, "Test")
        self.assertIsNotNone(result.file_size)

    # ------------------------------------------------------------------
    # T1.99.144: embedded_revision_number in _REGISTRY_MAP
    # ------------------------------------------------------------------

    def test_registry_map_includes_embedded_revision(self):
        """_REGISTRY_MAP maps embedded_revision_number → embedded_revision_number."""
        from eks.engine.core.file_property_parser import FilePropertyResult
        result = FilePropertyResult()
        result.embedded_revision_number = "3"
        reg_dict = result.to_registry_dict()
        self.assertIn("embedded_revision_number", reg_dict)
        self.assertEqual(reg_dict["embedded_revision_number"], "3")


if __name__ == "__main__":
    unittest.main(verbosity=2)

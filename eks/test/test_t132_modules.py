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
        self.assertEqual(self.em._catalog.get("metadata", {}).get("total_codes"), 128)

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

    # -- T1.195 V3: Project Definition error codes ---------------------------

    def test_pdef_system_codes_registered(self):
        """S-C-S-0901..0904 (Project Definition system errors) registered."""
        for code, name in {
            "S-C-S-0901": "PDEF_MISSING_MANDATORY_SECTION",
            "S-C-S-0902": "PDEF_UNKNOWN_PROFILE_REF",
            "S-C-S-0903": "PDEF_DUPLICATE_PROJECT_OR_PROFILE",
            "S-C-S-0904": "PDEF_RUNTIME_CONSTRUCTION_FAILED",
        }.items():
            entry = self.em.get_system_error(code)
            self.assertIsNotNone(entry, f"Missing system code {code}")
            self.assertEqual(entry["name"], name)

    def test_pdef_data_codes_registered(self):
        """P1-C-V-0001..0003 (Project Definition data errors) registered."""
        for code, name in {
            "P1-C-V-0001": "PDEF_CAPABILITY_CONSISTENCY_FAILED",
            "P1-C-V-0002": "PDEF_METADATA_POLICY_GAP",
            "P1-C-V-0003": "PDEF_UNUSED_PROFILE",
        }.items():
            entry = self.em.get_data_error(code)
            self.assertIsNotNone(entry, f"Missing data code {code}")
            self.assertEqual(entry["name"], name)

    def test_pdef_system_code_metadata(self):
        """New system codes are FATAL and stop the pipeline (V1)."""
        for code in ("S-C-S-0901", "S-C-S-0902", "S-C-S-0903", "S-C-S-0904"):
            entry = self.em.get_system_error(code)
            self.assertEqual(entry["severity"], "FATAL", code)
            self.assertTrue(entry["stops_pipeline"], code)
            self.assertEqual(entry["category"], "Config", code)

    def test_pdef_data_code_metadata(self):
        """New data codes map to layer P1, module C, function V."""
        for code in ("P1-C-V-0001", "P1-C-V-0002", "P1-C-V-0003"):
            entry = self.em.get_data_error(code)
            self.assertEqual(entry["layer"], "P1", code)
            self.assertEqual(entry["module"], "C", code)
            self.assertEqual(entry["function"], "V", code)

    def test_pdef_system_ranges_registered(self):
        """project_definition system range present with count 4."""
        ranges = self.em._catalog.get("system_error_ranges", {})
        self.assertIn("project_definition", ranges)
        self.assertEqual(ranges["project_definition"]["count"], 4)
        self.assertEqual(ranges["project_definition"]["start_id"], "S-C-S-0901")
        self.assertEqual(ranges["project_definition"]["end_id"], "S-C-S-0904")

    def test_pdef_data_ranges_registered(self):
        """phase_1_config_validation data range present with count 3."""
        ranges = self.em._catalog.get("data_error_ranges", {})
        self.assertIn("phase_1_config_validation", ranges)
        self.assertEqual(ranges["phase_1_config_validation"]["count"], 3)

    def test_pdef_system_handle_no_stop_override(self):
        """handle_system_error resolves the new codes end-to-end."""
        self.em.set_fail_fast(False)
        entry = self.em.handle_system_error("S-C-S-0902", detail="technip_bad")
        self.assertEqual(entry["code"], "S-C-S-0902")
        self.assertEqual(entry["name"], "PDEF_UNKNOWN_PROFILE_REF")

    def test_pdef_data_handle(self):
        """handle_data_error resolves P1-C-V-0001 end-to-end."""
        entry = self.em.handle_data_error("P1-C-V-0001", doc_id="PDEF")
        self.assertEqual(entry["code"], "P1-C-V-0001")
        self.assertEqual(entry["health_score_impact"], -1)

    def test_pdef_data_unused_profile_handle(self):
        """P1-C-V-0003 is INFO severity with zero health impact (L.13.10)."""
        entry = self.em.handle_data_error("P1-C-V-0003", doc_id="PDEF")
        self.assertEqual(entry["severity"], "INFO")
        self.assertEqual(entry["health_score_impact"], 0)


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

    # -- T1.195: PDEF messages registered -----------------------------------
    def test_pdef_messages_registered(self):
        """PDEF_* status/warning/error messages registered in catalog."""
        msgs = self.mm._catalog.get("messages", {})
        for name in ("PDEF_RESOLVE_START", "PDEF_RESOLVE_COMPLETE",
                     "PDEF_DATA_ERROR", "PDEF_SYSTEM_ERROR"):
            self.assertIn(name, msgs, f"Missing message {name}")

    def test_pdef_resolve_complete_hydrates(self):
        msg = self.mm.get("PDEF_RESOLVE_COMPLETE", count=2, errors=0, data_errors=1)
        self.assertIsNotNone(msg)
        self.assertIn("2", msg)
        self.assertIn("1", msg)

    def test_pdef_system_error_hydrates(self):
        msg = self.mm.get("PDEF_SYSTEM_ERROR", code="S-C-S-0901", detail="missing")
        self.assertIsNotNone(msg)
        self.assertIn("S-C-S-0901", msg)

    # T1.119 (I236) — ERROR_FILE_PROCESSING kwarg mismatch regression guard
    def test_error_file_processing_hydrates_detail(self):
        """T1.119 (I236): With correct kwarg key 'detail=', the exception
        message appears in the output — not the literal template placeholder.
        Uses verbosity=2 because ERROR_FILE_PROCESSING is level=2."""
        mm_debug = MessageManager(config_dir=CONFIG_DIR, verbosity=2)
        msg = mm_debug.get("ERROR_FILE_PROCESSING", filename="/path/doc.pdf", detail="[Errno 2] No such file")
        self.assertIsNotNone(msg,
                            "ERROR_FILE_PROCESSING must resolve at verbosity >= 2")
        self.assertIn("[Errno 2] No such file", msg,
                      "Actual exception text must appear in hydrated message")
        self.assertNotIn("{detail}", msg,
                         "Literal '{detail}' placeholder must be replaced")
        self.assertIn("/path/doc.pdf", msg,
                      "Filename must appear in hydrated message")

    def test_error_file_processing_wrong_kwarg_fallback(self):
        """T1.119 (I236): With wrong kwarg key 'error=', the raw template
        literal '{detail}' appears — documents the broken behavior as
        a regression guard for the kwarg key fix.
        Uses verbosity=2 because ERROR_FILE_PROCESSING is level=2."""
        mm_debug = MessageManager(config_dir=CONFIG_DIR, verbosity=2)
        msg = mm_debug.get("ERROR_FILE_PROCESSING", filename="/path/doc.pdf", error="[Errno 2] No such file")
        self.assertIsNotNone(msg,
                             "ERROR_FILE_PROCESSING must resolve at verbosity >= 2")
        self.assertIn("{detail}", msg,
                      "Literal '{detail}' must appear when wrong kwarg key is used")

    # T1.128 (I242) — ERROR_FILE_PROCESSING suppressed at verbosity 0 and 1
    def test_error_file_processing_suppressed_at_level_0(self):
        """T1.128 (I242): With verbosity=0, ERROR_FILE_PROCESSING (level=2)
        must return None — message is suppressed in silent mode."""
        mm_silent = MessageManager(config_dir=CONFIG_DIR, verbosity=0)
        msg = mm_silent.get("ERROR_FILE_PROCESSING", filename="/path/doc.pdf", detail="[Errno 2] No such file")
        self.assertIsNone(msg, "ERROR_FILE_PROCESSING must be suppressed at verbosity=0")

    def test_error_file_processing_suppressed_at_default_level(self):
        """I242: At default verbosity=1, ERROR_FILE_PROCESSING (level=2)
        must return None — message is suppressed at default verbosity."""
        mm_default = MessageManager(config_dir=CONFIG_DIR, verbosity=1)
        msg = mm_default.get("ERROR_FILE_PROCESSING", filename="/path/doc.pdf", detail="[Errno 2] No such file")
        self.assertIsNone(msg, "ERROR_FILE_PROCESSING must be suppressed at default verbosity=1")

    # T1.130 (I243) — STATUS_PHASE_B_COMPLETE hydrates correctly with total= kwarg
    def test_status_phase_b_complete_hydrates_correctly(self):
        """T1.130 (I243): STATUS_PHASE_B_COMPLETE template with all 4 kwargs
        (success, total, partial, failed) must hydrate fully — no literal placeholders."""
        msg = self.mm.get("STATUS_PHASE_B_COMPLETE", success=15, total=753, partial=0, failed=738)
        self.assertIsNotNone(msg, "STATUS_PHASE_B_COMPLETE must resolve with all required kwargs")
        self.assertIn("15/753", msg, "Formatted '{success}/{total}' must appear in output")
        self.assertNotIn("{total}", msg, "Literal '{total}' placeholder must be replaced")
        self.assertNotIn("{success}", msg, "Literal '{success}' placeholder must be replaced")
        self.assertNotIn("{partial}", msg, "Literal '{partial}' placeholder must be replaced")
        self.assertNotIn("{failed}", msg, "Literal '{failed}' placeholder must be replaced")


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
        score = self.scorer.score(doc, structural_elements=elements)
        # Doc has only 2 of ~23 scorable fields → ceiling ~0.54 under current weights
        self.assertGreaterEqual(score.get("health_score", 0), 0.5)

    def test_missing_cover_page(self):
        doc = {
            "document_type": "DWG",
            "extraction_confidence": 0.5,
            "page_count": 1,
        }
        elements = []
        score = self.scorer.score(doc, structural_elements=elements)
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
        score1 = self.scorer.score(docs[0], structural_elements=elements_list[0])
        score2 = self.scorer.score(docs[1], structural_elements=elements_list[1])
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

    def test_skip_cover_page_no_cover_template(self):
        """I278: skip_cover_page=True produces no cover_page element."""
        pages = [{
            "text": "PROJECT: Test Project\nDOC NO: DWG-001\nREV: A",
            "tables": [],
            "images": [],
        }]
        elements = self.detector.detect("test.pdf", pages=pages, skip_cover_page=True)
        self.assertFalse(any(el["element_type"] == "cover_page" for el in elements),
                         "no-cover (C) template must not emit a cover_page element")
        self.assertTrue(all(el["element_type"] != "cover_page" for el in elements))

    # -- I283 (T1.230): template-gated detection + schema-first cover type -----

    def test_gating_by_expected_elements(self):
        """Only element types in expected_element_types are detected."""
        pages = [{
            "text": "PROJECT: Test Project\nDOC NO: DWG-001\nREV: A\n1.0 Scope\n2.1 Design",
            "tables": [],
            "images": [],
        }]
        elements = self.detector.detect("test.pdf", pages=pages,
                                        expected_element_types={"cover_page"})
        self.assertEqual([el["element_type"] for el in elements], ["cover_page"],
                         "section/revision_table must be gated off")

    def test_empty_expected_elements_gates_all(self):
        """An empty expected_elements set produces no elements (spec no-cover)."""
        pages = [{
            "text": "PROJECT: Test Project\nDOC NO: DWG-001\nREV: A\n1.0 Scope",
            "tables": [],
            "images": [],
        }]
        elements = self.detector.detect("test.pdf", pages=pages,
                                        expected_element_types=set())
        self.assertEqual(elements, [])

    def test_link_note_placeholders_gated_by_expected_elements(self):
        """link/note are placeholder detectors that are always gated."""
        text = "Note: annotate here.\nSee https://example.com/file"
        pages = [{"text": text, "tables": [], "images": []}]
        on = self.detector.detect("test.pdf", pages=pages,
                                  expected_element_types={"link", "note"})
        types = {el["element_type"] for el in on}
        self.assertIn("link", types)
        self.assertIn("note", types)
        off = self.detector.detect("test.pdf", pages=pages,
                                   expected_element_types={"section"})
        types_off = {el["element_type"] for el in off}
        self.assertNotIn("link", types_off)
        self.assertNotIn("note", types_off)

    def test_detects_title_block_grid_signature_when_declared(self):
        """New 8→11 element codes return elements when declared in expected_elements."""
        text = (
            "TITLE: Pump Station P-101\n"
            "SCALE: 1:100\n"
            "DRAWN BY: J. Smith\n"
            "CHECKED BY: M. Jones\n"
            "APPROVED BY: R. Lee\n"
            "Grid refs: A1 B2 C3 A4\n"
            "SIGNED: J. Smith\n"
        )
        pages = [{"text": text, "tables": [], "images": []}]
        elements = self.detector.detect(
            "test.pdf", pages=pages,
            expected_element_types={"title_block", "grid", "signature_block"},
        )
        types = {el["element_type"] for el in elements}
        self.assertIn("title_block", types)
        self.assertIn("grid", types)
        self.assertIn("signature_block", types)

    def test_title_block_grid_signature_gated_off(self):
        """Drawing-frame elements are not detected when not declared."""
        text = (
            "TITLE: Pump Station P-101\nSCALE: 1:100\nDRAWN BY: J. Smith\n"
            "Grid refs: A1 B2 C3 A4\nSIGNED: J. Smith\n"
        )
        pages = [{"text": text, "tables": [], "images": []}]
        elements = self.detector.detect("test.pdf", pages=pages,
                                        expected_element_types={"cover_page"})
        self.assertNotIn("title_block", {el["element_type"] for el in elements})
        self.assertNotIn("grid", {el["element_type"] for el in elements})
        self.assertNotIn("signature_block", {el["element_type"] for el in elements})

    def test_schema_cover_type_c_skips_cover(self):
        """I283: schema-first cover_type 'C' skips cover detection without skip_cover_page."""
        pages = [{
            "text": "PROJECT: Test Project\nDOC NO: DWG-001\nREV: A",
            "tables": [],
            "images": [],
        }]
        elements = self.detector.detect("test.pdf", pages=pages, cover_type="C")
        self.assertFalse(any(el["element_type"] == "cover_page" for el in elements))

    def test_cover_type_none_detection_fallback(self):
        """I283: None cover_type (schema unavailable) falls back to content detection."""
        pages = [{
            "text": "PROJECT: Test Project\nDOC NO: DWG-001\nREV: A",
            "tables": [],
            "images": [],
        }]
        elements = self.detector.detect("test.pdf", pages=pages, cover_type=None)
        self.assertTrue(any(el["element_type"] == "cover_page" for el in elements),
                        "schema value unavailable → detection fallback runs cover detection")

    def test_cover_type_a_annotates_cover(self):
        """I283: cover-bearing cover_type is annotated onto the cover_page element."""
        pages = [{
            "text": "PROJECT: Test Project\nDOC NO: DWG-001\nREV: A",
            "tables": [],
            "images": [],
        }]
        elements = self.detector.detect("test.pdf", pages=pages, cover_type="A")
        covers = [el for el in elements if el["element_type"] == "cover_page"]
        self.assertEqual(covers[0].get("cover_type"), "A")

    def test_classify_cover_type_retired(self):
        """I283: keyword-based classify_cover_type() must be retired."""
        self.assertFalse(hasattr(self.detector, "classify_cover_type"),
                         "classify_cover_type() keyword heuristic must be removed")


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
        """T1.99.144: DOCX config has revision → embedded_revision_number mapping.

        I287 (T1.241): property mappings single-sourced in
        eks_processing_config.json#/file_property_profiles (doc_config
        file_property_patterns section retired).
        """
        config_path = CONFIG_DIR / "schemas" / "eks_processing_config.json"
        if not config_path.exists():
            config_path = CONFIG_DIR / "eks_processing_config.json"
        with open(config_path) as f:
            config = json.load(f)
        docx_mappings = config["file_property_profiles"]["docx_props"]["property_mapping"]
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
        self.assertEqual(config["version"], "1.13.0")  # I286 T1.237: manual_review marker + 4 column_processing entries (I283 T1.230 was 1.12.0)

        base_path = CONFIG_DIR / "schemas" / "eks_doc_base_schema.json"
        if not base_path.exists():
            base_path = CONFIG_DIR / "eks_doc_base_schema.json"
        with open(base_path) as f:
            base = json.load(f)
        self.assertEqual(base["version"], "1.20.0")  # I291 T1.254: document_element_def shape + 2 declared_only relations (I290 T1.253 was 1.19.0)

        core_base_path = CONFIG_DIR / "schemas" / "eks_base_schema.json"
        if not core_base_path.exists():
            core_base_path = CONFIG_DIR / "eks_base_schema.json"
        with open(core_base_path) as f:
            core_base = json.load(f)
        self.assertEqual(core_base["version"], "1.17.0")  # I287 T1.238: filename/file_property/os_properties defs added


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

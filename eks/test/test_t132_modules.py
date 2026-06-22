"""
Test T1.32 engine modules: ErrorManager, MessageManager, HealthScorer, StructureDetector, Elements CRUD.
"""
import unittest
import json
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
        self.assertEqual(self.em._catalog.get("metadata", {}).get("total_codes"), 65)

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

    def test_verbosity_filter(self):
        self.mm.set_verbosity(0)
        msg = self.mm.get("STATUS_DETECTING_STRUCTURE", filename="x.pdf")
        self.assertIsNone(msg)

    def test_unknown_message(self):
        msg = self.mm.get("UNKNOWN_MESSAGE_ID")
        self.assertIsNone(msg)

    def test_get_all_messages(self):
        warnings = self.mm.get_all_messages(category="warning")
        self.assertGreaterEqual(len(warnings), 3)


class TestHealthScorer(unittest.TestCase):

    def setUp(self):
        self.hs = HealthScorer()

    def make_meta(self, overrides=None):
        meta = {
            "project_number": "P123",
            "discipline": "C",
            "document_type": "DWG",
            "document_number": "D-001",
            "revision": "A",
            "asset_tags": '["P-101"]',
            "project_title": "Test Project",
            "area": "WSW41",
            "status": "APPROVED",
            "created_by": "JS",
            "checked_by": "PE",
            "approved_by": "PM",
            "originator_company": "CH2M HILL",
            "page_count": 1,
            "department": "",
            "security_class": "",
            "verified_by": "",
        }
        if overrides:
            meta.update(overrides)
        return meta

    def test_completeness_all(self):
        meta = self.make_meta(
            {k: "x" for k in ["department", "security_class", "verified_by"]}
        )
        result = self.hs.score(meta, cover_type="A")
        self.assertEqual(result["dimensions"]["completeness"]["populated"], 17)

    def test_completeness_partial(self):
        meta = self.make_meta()
        result = self.hs.score(meta, cover_type="A")
        self.assertEqual(result["dimensions"]["completeness"]["populated"], 14)

    def test_structural_completeness_type_a(self):
        elements = [
            {"element_type": "cover_page"},
            {"element_type": "revision_table"},
            {"element_type": "sections"},
            {"element_type": "image"},
        ]
        meta = self.make_meta()
        result = self.hs.score(meta, cover_type="A", structural_elements=elements)
        self.assertEqual(result["dimensions"]["structural_completeness"]["score"], 1.0)

    def test_structural_completeness_missing(self):
        meta = self.make_meta()
        result = self.hs.score(meta, cover_type="A", structural_elements=[])
        self.assertEqual(result["dimensions"]["structural_completeness"]["score"], 0.0)

    def test_source_quality(self):
        result = self.hs.score(self.make_meta(), cover_type="A", structural_elements=[])
        self.assertEqual(result["dimensions"]["source_quality"]["score"], 1.0)

    def test_consistency_modifier(self):
        meta = self.make_meta()
        result = self.hs.score(meta, consistency_violations=3)
        self.assertEqual(result["dimensions"]["consistency"]["score"], 0.7)

    def test_health_score_high(self):
        meta = self.make_meta(
            {k: "x" for k in
             ["department", "security_class", "verified_by", "approved_by"]}
        )
        elements = [
            {"element_type": "cover_page"},
            {"element_type": "revision_table"},
            {"element_type": "sections"},
            {"element_type": "image"},
        ]
        result = self.hs.score(meta, cover_type="A", structural_elements=elements)
        self.assertGreaterEqual(result["health_score"], 0.90)
        self.assertEqual(result["extract_status"], "success")

    def test_health_score_low(self):
        meta = {k: "" for k in self.make_meta()}
        elements = []
        result = self.hs.score(meta, cover_type="C", structural_elements=elements)
        self.assertGreaterEqual(result["health_score"], 0.40)
        self.assertLess(result["health_score"], 0.60)
        self.assertEqual(result["extract_status"], "partial")

    def test_format_notes(self):
        meta = self.make_meta()
        result = self.hs.score(meta, cover_type="A", structural_elements=[])
        notes_str = self.hs.format_notes(result)
        parsed = json.loads(notes_str)
        self.assertIn("health_score", parsed)
        self.assertIn("dimensions", parsed)

    def test_tier1_tracking(self):
        meta = self.make_meta()
        result = self.hs.score(meta)
        self.assertEqual(result["tier1_fields"]["populated"], 6)

    def test_missing_columns(self):
        meta = self.make_meta()
        result = self.hs.score(meta)
        self.assertIn("department", result["missing_columns"])

    def test_batch_scoring(self):
        docs = [
            self.make_meta({"document_number": "D-001"}),
            self.make_meta({"document_number": "D-002"}),
        ]
        batch = self.hs.score_batch(docs)
        self.assertEqual(batch["total_documents"], 2)

    def test_structural_for_type_c(self):
        meta = self.make_meta()
        result = self.hs.score(meta, cover_type="C", structural_elements=[])
        self.assertEqual(result["dimensions"]["structural_completeness"]["score"], 1.0)


class TestStructureDetector(unittest.TestCase):

    def setUp(self):
        self.sd = StructureDetector()

    def test_cover_page_detected(self):
        text = "Drawing: D-001\nProject: P123\nRevision: A\nStatus: APPROVED"
        elements = self.sd.detect("test.pdf", full_text=text)
        types = [e["element_type"] for e in elements]
        self.assertIn("cover_page", types)

    def test_cover_page_not_detected_short(self):
        text = "Hello world"
        elements = self.sd.detect("test.pdf", full_text=text)
        types = [e["element_type"] for e in elements]
        self.assertNotIn("cover_page", types)

    def test_revision_table_detected(self):
        text = "1 2024-01-01 JS\n2 2024-06-01 PE"
        elements = self.sd.detect("test.pdf", full_text=text)
        types = [e["element_type"] for e in elements]
        self.assertIn("revision_table", types)

    def test_sections_detected(self):
        text = "1.0 General Notes\n2.0 Scope\n3.0 Design Criteria"
        elements = self.sd.detect("test.pdf", full_text=text)
        sections = [e for e in elements if e["element_type"] == "section"]
        self.assertGreaterEqual(len(sections), 3)

    def test_links_detected(self):
        text = "See https://example.com for details"
        elements = self.sd.detect("test.pdf", full_text=text)
        links = [e for e in elements if e["element_type"] == "link"]
        self.assertGreaterEqual(len(links), 1)

    def test_legend_detected(self):
        text = "LEGEND:\nP-101 Pump\nV-201 Valve"
        elements = self.sd.detect("test.pdf", full_text=text)
        legends = [e for e in elements if e["element_type"] == "legend"]
        self.assertGreaterEqual(len(legends), 1)

    def test_notes_detected(self):
        text = "Note: All dimensions in mm\nRemark: Check tolerances"
        elements = self.sd.detect("test.pdf", full_text=text)
        notes = [e for e in elements if e["element_type"] == "note"]
        self.assertGreaterEqual(len(notes), 2)

    def test_classify_type_a(self):
        text = "General Arrangement DWG 12345 Drawing Title with lots of content to make it longer than fifty characters"
        cover = self.sd.classify_cover_type("test.pdf", text)
        self.assertEqual(cover, "A")

    def test_classify_type_c(self):
        text = ""
        cover = self.sd.classify_cover_type("test.pdf", text)
        self.assertEqual(cover, "C")

    def test_classify_type_e(self):
        text = "This is a Specification for Civil Works and it has many characters beyond the scanned threshold limit"
        cover = self.sd.classify_cover_type("test.pdf", text)
        self.assertEqual(cover, "E")

    def test_empty_text(self):
        elements = self.sd.detect("empty.pdf", full_text="")
        self.assertEqual(len(elements), 0)

    def test_source_field(self):
        text = "Project: P123\n1.0 Intro"
        elements = self.sd.detect("test.pdf", full_text=text)
        for el in elements:
            self.assertIn(el["source"], ("regex", "heuristic"))

    def test_confidence_range(self):
        text = "Project: P123\n1 2024-01-01 JS\nRevision: A"
        elements = self.sd.detect("test.pdf", full_text=text)
        for el in elements:
            self.assertGreaterEqual(el["confidence"], 0.0)
            self.assertLessEqual(el["confidence"], 1.0)


class TestDocumentElementsCRUD(unittest.TestCase):
    """Verify document_elements table via DocumentRegistry."""

    TEST_DOC_ID = "T132-ELEMENTS-TEST-0"

    @classmethod
    def setUpClass(cls):
        from eks.engine.core.registry import DocumentRegistry
        cls.reg = DocumentRegistry()
        cls.reg.register_document({
            "document_number": "T132-ELEMENTS-TEST",
            "revision": "0",
            "project_number": "P999",
            "discipline": "EL",
            "document_type": "DWG",
            "status": "DRAFT",
        })

    def setUp(self):
        self.reg.delete_elements(self.TEST_DOC_ID)

    def test_store_and_retrieve(self):
        elements = [
            {"element_type": "cover_page", "element_id": "1", "title": "Cover", "content": "{}", "confidence": 0.9},
            {"element_type": "section", "element_id": "1", "title": "1.0 Intro", "content": "Introduction", "confidence": 0.8},
        ]
        count = self.reg.store_elements(self.TEST_DOC_ID, elements)
        self.assertEqual(count, 2)

    def test_get_elements(self):
        self.reg.store_elements(self.TEST_DOC_ID, [
            {"element_type": "table", "element_id": "2", "title": "Data", "content": "[]", "confidence": 0.9},
        ])
        retrieved = self.reg.get_elements(self.TEST_DOC_ID)
        self.assertEqual(len(retrieved), 1)

    def test_get_elements_by_type(self):
        self.reg.store_elements(self.TEST_DOC_ID, [
            {"element_type": "cover_page", "title": "Cover", "confidence": 0.9},
            {"element_type": "section", "title": "1.0", "confidence": 0.8},
        ])
        sections = self.reg.get_elements_by_type(self.TEST_DOC_ID, "section")
        self.assertEqual(len(sections), 1)

    def test_delete_elements(self):
        self.reg.store_elements(self.TEST_DOC_ID, [
            {"element_type": "cover_page", "title": "Cover", "confidence": 0.9},
        ])
        self.reg.delete_elements(self.TEST_DOC_ID)
        remaining = self.reg.get_elements(self.TEST_DOC_ID)
        self.assertEqual(len(remaining), 0)

    def test_empty_elements(self):
        count = self.reg.store_elements(self.TEST_DOC_ID, [])
        self.assertEqual(count, 0)

    def test_get_nonexistent(self):
        els = self.reg.get_elements("NONEXISTENT-DOC")
        self.assertEqual(len(els), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)

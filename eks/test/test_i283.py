"""I283 (T1.231) — four-level Class→Type→Template→Element detection tests.

Validates the I283 implementation (T1.230/T1.231):
- element_type_code extended 8→11 (title_block/grid/signature_block) in
  eks_doc_base_schema.json v1.17.0; element_type_registry carries the 3 new
  entries in eks_doc_config.json v1.12.0.
- Carrier twrp_drawing/twrp_pandid expected_elements extended to the full
  8-element drawing profile (threshold 5) — element-set SSOT.
- EKSColumnProcessor.resolve_cover_type() is schema-first (None when the
  schema value is unavailable — never a keyword heuristic); a deliberate
  no-cover template still resolves to "C". resolve_expected_element_types()
  exposes the template expected_elements set.
- StructureDetector gates EVERY sub-detector (incl. link/note placeholders) by
  expected_element_types; cover type drives skip schema-first with content
  detection fallback only when the value is unavailable; classify_cover_type()
  keyword heuristic retired.
- Detection output feeds health scoring via HealthInput.cover_type (I284 base:
  metadata-only sources — class/type/family/element/file name/file properties).
"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from eks.engine.core.column_processor import EKSColumnProcessor
from eks.engine.core.health_scorer import HealthScorer
from eks.engine.core.io_contracts import HealthInput
from eks.engine.core.schema_loader import SchemaLoader
from eks.engine.core.structure_detector import StructureDetector

ROOT = Path(__file__).resolve().parent.parent

FULL_DRAWING_ELEMENTS = {
    "cover_page", "revision_table", "section", "image", "link",
    "title_block", "grid", "signature_block",
}

DRAWING_TEXT = (
    "PROJECT NUMBER: P123\n"
    "DOC NO: DWG-001\n"
    "REV: A\n"
    "1 2024-01-01 J. Smith\n"
    "2 2024-02-01 M. Jones\n"
    "TITLE: Pump Station\n"
    "SCALE: 1:100\n"
    "DRAWN BY: J. Smith\n"
    "CHECKED BY: M. Jones\n"
    "APPROVED BY: R. Lee\n"
    "Grid refs: A1 B2 C3 A4\n"
    "SIGNED: J. Smith\n"
    "1.0 Scope\n"
    "2.1 Design\n"
    "Note: annotate here.\n"
    "https://example.com/file"
)


class TestI283Schema(unittest.TestCase):
    """Schema/config SSOT for the 8→11 element-code extension."""

    @classmethod
    def setUpClass(cls):
        cls.config_dir = ROOT / "config"
        cls.loader = SchemaLoader(str(cls.config_dir))
        cls.loader.load_all()
        with open(cls.config_dir / "schemas" / "eks_doc_base_schema.json", encoding="utf-8") as f:
            cls.base = json.load(f)
        with open(cls.config_dir / "schemas" / "eks_doc_config.json", encoding="utf-8") as f:
            cls.doc_config = json.load(f)
        with open(cls.config_dir / "schemas" / "eks_document_type_schema.json", encoding="utf-8") as f:
            cls.carrier = json.load(f)

    def test_element_type_code_extended_to_11(self):
        enum = self.base["definitions"]["element_type_code"]["enum"]
        self.assertEqual(len(enum), 11)
        self.assertTrue({"title_block", "grid", "signature_block"}.issubset(set(enum)))

    def test_element_type_registry_has_11_entries(self):
        reg = {e["element_type"] for e in self.doc_config["element_type_registry"]}
        self.assertEqual(len(reg), 11)
        for et in ("title_block", "grid", "signature_block"):
            self.assertIn(et, reg)

    def test_drawing_templates_declare_full_element_set(self):
        for tid in ("twrp_drawing", "twrp_pandid"):
            tpl = self.carrier["document_templates"][tid]
            self.assertEqual(set(tpl["expected_elements"]), FULL_DRAWING_ELEMENTS,
                             f"{tid} expected_elements")
            self.assertEqual(tpl["threshold"], 5, f"{tid} threshold")

    def test_spec_template_has_3_elements(self):
        """I303: twrp_spec_c expected_elements = [section, table, image] — never zero."""
        self.assertEqual(self.carrier["document_templates"]["twrp_spec_c"]["expected_elements"],
                         ["section", "table", "image"])
        self.assertEqual(self.carrier["document_templates"]["twrp_spec_c"]["threshold"], 3)

    def test_loader_projects_templates(self):
        tpl = self.loader.doc_config["document_templates"]["twrp_drawing"]
        self.assertEqual(set(tpl["expected_elements"]), FULL_DRAWING_ELEMENTS)


class TestI283ColumnProcessor(unittest.TestCase):
    """Schema-first cover type + expected_elements resolution."""

    @classmethod
    def setUpClass(cls):
        cls.config_dir = ROOT / "config"
        cls.loader = SchemaLoader(str(cls.config_dir))
        cls.loader.load_all()
        cls.processor = EKSColumnProcessor.from_doc_config(
            cls.loader.doc_config, processing_config=cls.loader.processing_config,
        )

    def test_schema_first_cover_type(self):
        self.assertEqual(self.processor.resolve_cover_type("DWG"), "A")
        self.assertEqual(self.processor.resolve_cover_type("PI-PID"), "B")
        self.assertEqual(self.processor.resolve_cover_type("SPC"), "C")

    def test_schema_cover_type_unavailable_is_none(self):
        self.assertIsNone(self.processor.resolve_cover_type("UNKNOWN"))
        self.assertIsNone(self.processor.resolve_cover_type(None))

    def test_expected_element_types_drawing(self):
        self.assertEqual(self.processor.resolve_expected_element_types("DWG"),
                         FULL_DRAWING_ELEMENTS)

    def test_expected_element_types_spec_has_3(self):
        """I303: SPC (twrp_spec_c) now has section/table/image expected."""
        self.assertEqual(self.processor.resolve_expected_element_types("SPC"),
                         {"section", "table", "image"})

    def test_cover_type_c_discards_cover_method(self):
        methods = self.processor.resolve_extraction_methods("SPC", "print")
        self.assertNotIn("cover_page_element", methods,
                         "no-cover (C) template must not admit cover_page_element")

    def test_none_cover_type_keeps_cover_page_element(self):
        """I283: None cover_type (schema unavailable) must NOT discard cover_page_element."""
        proc = EKSColumnProcessor(
            {},
            document_type_registry=[
                {"code": "X", "template": "tpl_x", "default_parsing_profile": "p"},
            ],
            parsing_profiles={"p": {"extraction_methods": ["parser_metadata", "cover_page_element"]}},
            document_templates={"tpl_x": {"label": "X", "expected_elements": []}},
        )
        methods = proc.resolve_extraction_methods("X", "print")
        self.assertIn("cover_page_element", methods,
                      "None cover_type → schema unavailable → method not pre-emptively dropped")


class TestI283DetectionIntegration(unittest.TestCase):
    """DRAWING full set vs SPEC no-cover gating at the detector level."""

    def setUp(self):
        self.detector = StructureDetector()

    def _pages(self, text=DRAWING_TEXT):
        return [{"text": text, "tables": [], "images": []}]

    def test_drawing_full_set_detects_declared_elements(self):
        elements = self.detector.detect(
            "dwg.pdf", pages=self._pages(),
            expected_element_types=FULL_DRAWING_ELEMENTS, cover_type="A",
        )
        types = {el["element_type"] for el in elements}
        expected_present = {"cover_page", "revision_table", "section",
                            "link", "title_block", "grid", "signature_block"}
        self.assertTrue(expected_present.issubset(types),
                        f"declared drawing elements not all detected: {expected_present - types}")
        self.assertTrue(types.issubset(FULL_DRAWING_ELEMENTS),
                        f"element outside declared set detected: {types - FULL_DRAWING_ELEMENTS}")

    def test_spec_empty_expected_gates_all(self):
        elements = self.detector.detect(
            "spec.pdf", pages=self._pages(),
            expected_element_types=set(), cover_type="C",
        )
        self.assertEqual(elements, [],
                         "empty expected_elements must gate every detector")

    def test_no_cover_template_zero_cover_page(self):
        elements = self.detector.detect(
            "spec.pdf", pages=self._pages(),
            expected_element_types=set(), cover_type="C",
        )
        self.assertFalse(any(el["element_type"] == "cover_page" for el in elements),
                         "no-cover (C) template must not emit cover_page")

    def test_cover_bearing_template_detects_cover_and_revision(self):
        elements = self.detector.detect(
            "dwg.pdf", pages=self._pages(),
            expected_element_types={"cover_page", "revision_table"}, cover_type="A",
        )
        types = {el["element_type"] for el in elements}
        self.assertIn("cover_page", types)
        self.assertIn("revision_table", types)
        self.assertNotIn("title_block", types,
                         "un-declared element must be gated off")

    def test_link_note_placeholders_always_gated(self):
        on = self.detector.detect(
            "dwg.pdf", pages=self._pages(),
            expected_element_types={"link", "note"}, cover_type="A",
        )
        types_on = {el["element_type"] for el in on}
        self.assertIn("link", types_on)
        self.assertIn("note", types_on)
        off = self.detector.detect(
            "dwg.pdf", pages=self._pages(),
            expected_element_types={"section"}, cover_type="A",
        )
        types_off = {el["element_type"] for el in off}
        self.assertNotIn("link", types_off)
        self.assertNotIn("note", types_off)

    def test_cover_type_none_falls_back_to_content_detection(self):
        elements = self.detector.detect(
            "dwg.pdf", pages=self._pages(),
            expected_element_types=FULL_DRAWING_ELEMENTS, cover_type=None,
        )
        self.assertTrue(any(el["element_type"] == "cover_page" for el in elements),
                        "schema cover type unavailable → content detection falls back")


class TestI283HealthScoring(unittest.TestCase):
    """Detection output feeds health scoring; cover_type forwarded via HealthInput."""

    @classmethod
    def setUpClass(cls):
        cls.config_dir = ROOT / "config"
        cls.loader = SchemaLoader(str(cls.config_dir))
        cls.loader.load_all()
        cls.scorer = HealthScorer(document_templates=cls.loader.doc_config["document_templates"])

    def test_score_from_input_forwards_cover_type(self):
        doc = {"document_type": "DWG"}
        inp = HealthInput(run_id="r", data_dir=Path("."), config_file=Path("c"),
                          schema_dir=Path("s"), output_dir=Path("o"),
                          document=doc, elements=[], cover_type="C")
        out = self.scorer.score_from_input(inp)
        src = out.metadata["dimensions"]["source_quality"]
        self.assertEqual(src["score"], 0.3,
                         "cover_type C → COVER_TYPE_SOURCE_SCORES['C'] = 0.3")

    def test_expected_elements_map_derived_from_templates(self):
        self.assertEqual(self.scorer._expected_elements_by_type["A"], FULL_DRAWING_ELEMENTS)
        self.assertEqual(self.scorer._expected_elements_by_type["C"], {"section", "table", "image"})

    def test_structural_dimension_uses_template_set(self):
        doc = {"document_type": "DWG"}
        elements = [
            {"element_type": "cover_page"},
            {"element_type": "revision_table"},
            {"element_type": "section"},
            {"element_type": "title_block"},
        ]
        result = self.scorer.score(doc, structural_elements=elements, cover_type="A")
        struct = result["dimensions"]["structural_completeness"]
        self.assertEqual(struct["expected"], 8)
        self.assertEqual(struct["detected"], 4)
        self.assertEqual(struct["score"], 0.5)

    def test_structural_dimension_spec_c_score(self):
        """I303: spec C now has 3 expected elements — 0/3 detected → score 0.0."""
        doc = {"document_type": "SPC"}
        result = self.scorer.score(doc, structural_elements=[], cover_type="C")
        struct = result["dimensions"]["structural_completeness"]
        self.assertEqual(struct["score"], 0.0,
                         "spec C has 3 expected elements, 0 detected → structural score 0.0")


if __name__ == "__main__":
    unittest.main()

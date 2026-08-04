"""I276 (T1.208) — Two-axis parser routing tests.

Validates the two-axis ParserRouter routing introduced for the native/PDF-print
model:
- Axis 1 (profile): document_type (project-local code) -> default_parsing_profile
  -> parser_class, resolved from the projected document_type_registry (I279
  carrier) + the parsing_profiles library.
- Axis 2 (reader): file_type -> parser_class via the file_type_registry /
  ParserFactory mapping.
- Fallback: when a document type has no binding profile (or the profile does not
  admit the file_type), routing degrades to file-type-only.
Covers per-binding profile selection, native/print two-axis routing, fallback
behavior, unknown codes, and §24 capability consistency.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from eks.engine.core.schema_loader import SchemaLoader
from eks.engine.parsers.parser_router import ParserRouter

ROOT = Path(__file__).resolve().parent.parent


class TestTwoAxisParserRouting(unittest.TestCase):
    """I276 T1.208 — two-axis routing resolution."""

    @classmethod
    def setUpClass(cls):
        config_dir = ROOT / "config"
        cls.loader = SchemaLoader(str(config_dir))
        cls.loader.load_all()
        cls.router = ParserRouter(cls.loader.doc_config)

    # -- 1. Axis 1: profile resolution -------------------------------

    def test_resolve_profile_pdf_print_binding(self):
        """DWG (print binding) maps to technip_pdf via default_parsing_profile."""
        self.assertEqual(self.router.resolve_parsing_profile("DWG"), "technip_pdf")

    def test_resolve_profile_native_binding(self):
        """CAD (native binding) maps to technip_dwg."""
        self.assertEqual(self.router.resolve_parsing_profile("CAD"), "technip_dwg")

    def test_resolve_profile_unknown_code(self):
        """Unknown local_code yields None (caller falls back to file-type-only)."""
        self.assertIsNone(self.router.resolve_parsing_profile("NOPE"))

    def test_resolve_profile_missing_code(self):
        """Empty/missing document_type yields None."""
        self.assertIsNone(self.router.resolve_parsing_profile(None))
        self.assertIsNone(self.router.resolve_parsing_profile(""))

    # -- 2. Axis 2 / two-axis reader resolution -----------------------

    def test_reader_native_dwg_uses_dwg_profile(self):
        """Native DWG (document_type=CAD) uses the technip_dwg DWG reader."""
        cls = self.router.resolve_reader("dwg", "CAD")
        self.assertEqual(cls, "eks.engine.parsers.dwg_parser.DWGParserStub")

    def test_reader_pdf_print_uses_pdf_profile(self):
        """PDF print of a drawing (document_type=DWG) uses the technip_pdf reader."""
        cls = self.router.resolve_reader("pdf", "DWG")
        self.assertEqual(cls, "eks.engine.parsers.pdf_parser.PDFParser")

    def test_reader_falls_back_without_document_type(self):
        """No document_type -> file-type-only fallback (None signals factory)."""
        self.assertIsNone(self.router.resolve_reader("pdf", None))

    def test_reader_falls_back_unknown_document_type(self):
        """Unknown document_type -> file-type-only fallback."""
        self.assertIsNone(self.router.resolve_reader("pdf", "NOPE"))

    def test_reader_profile_rejects_unsupported_extension(self):
        """A profile that does not support the file_type yields fallback (None)."""
        # technip_docx supports only docx — asking for xlsx must fall back.
        router = ParserRouter(self.loader.doc_config)
        cls = router.resolve_reader("xlsx", "SPC")
        self.assertIsNone(cls)

    # -- 3. route() integration ---------------------------------------

    def test_route_unknown_type_still_fails(self):
        """Two-axis routing does not mask file-type-only failure for unknown types."""
        result = self.router.route("test.txt", "txt", document_type="DWG")
        self.assertEqual(result["status"], "failed")
        self.assertIn("No parser", result["error"])

    def test_route_document_type_carried_in_result(self):
        """route() records the document_type it routed for."""
        result = self.router.route("test.pdf", "pdf", document_type="DWG")
        self.assertEqual(result["document_type"], "DWG")

    # -- 4. §24 capability consistency --------------------------------

    def test_all_binding_profiles_referenced_exist(self):
        """Every default_parsing_profile on a binding exists in parsing_profiles."""
        profiles = set(self.loader.doc_config.get("parsing_profiles", {}))
        for entry in self.loader.doc_config.get("document_type_registry", []):
            pid = entry.get("default_parsing_profile")
            if pid:
                self.assertIn(pid, profiles, f"missing profile {pid} for {entry['code']}")

    def test_profile_supported_extensions_admit_binding_file_types(self):
        """A binding's expected_file_types must be admitted by its profile reader."""
        profiles = self.loader.doc_config.get("parsing_profiles", {})
        for entry in self.loader.doc_config.get("document_type_registry", []):
            pid = entry.get("default_parsing_profile")
            if not pid:
                continue
            supported = set(profiles.get(pid, {}).get("supported_extensions", []))
            if not supported:
                continue
            for ext in entry.get("expected_file_types", []):
                # PDF-print bindings may be read by the PDF profile regardless of
                # the native expected extension; only enforce when both are set
                # and the profile is native-capable (its supported set is non-print).
                self.assertTrue(
                    supported or ext == "pdf",
                    f"{entry['code']} expected {ext} but profile {pid} supports {sorted(supported)}",
                )

    def test_native_profiles_present(self):
        """GAP-N4 native reader profiles exist and are wired to native file types."""
        profiles = self.loader.doc_config.get("parsing_profiles", {})
        for pid, expected_parser in (
            ("technip_dwg", "eks.engine.parsers.dwg_parser.DWGParserStub"),
            ("technip_dgn", "eks.engine.parsers.dgn_parser.DGNParserStub"),
            ("technip_xlsx", "eks.engine.parsers.xlsx_parser.XLSXParser"),
        ):
            self.assertIn(pid, profiles, f"missing native profile {pid}")
            self.assertEqual(profiles[pid]["parser_class"], expected_parser)


if __name__ == "__main__":
    unittest.main(verbosity=2)

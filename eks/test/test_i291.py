"""
Integration tests for I291 (T1.254) — `document_elements` runtime table
shape enrichment + declared_only FK relations + element_type validation.

Scope (re-scoped 2026-08-09, design review approved):
  1. register doc → StructureDetector.detect() → store_elements()
     → get_elements_by_type() round-trip
  2. unknown element_type rejected (fk_element_type enum validation)
  3. cover-type-C / empty expected_elements → zero element rows,
     registry row still inserted (I290 Q6 full-scope ingest)
  4. delete_elements() semantics
  5. DDL shape: id VARCHAR PRIMARY KEY + created_at TIMESTAMP NOT NULL
     DEFAULT now() (+ optional element_seq)
  6. relations manifest contains declared_only fk_element_doc / fk_element_type
"""
import unittest
import uuid
from pathlib import Path

from eks.engine.core import DocumentRegistry
from eks.engine.core.schema_to_ddl import SchemaToDDL
from eks.engine.core.structure_detector import StructureDetector

_PROJECT_ROOT = Path(__file__).resolve().parent.parent

VALID_ELEMENT_TYPES = {
    "cover_page", "revision_table", "section", "table", "image", "link",
    "legend", "note", "title_block", "grid", "signature_block",
}


class TestI291DocumentElements(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_dir = _PROJECT_ROOT / "config" / "schemas"
        if not cls.config_dir.exists():
            cls.config_dir = _PROJECT_ROOT / "config"
        cls.test_dir = _PROJECT_ROOT / "test_output"
        cls.test_dir.mkdir(exist_ok=True)

    def _make_registry(self, name: str):
        reg_path = self.test_dir / name
        if reg_path.exists():
            reg_path.unlink()
        return reg_path, DocumentRegistry(db_path=str(reg_path))

    def _make_doc_meta(self, **overrides):
        meta = {
            "document_number": "I291-DOC-001",
            "revision": "A",
            "document_type": "SPECIFICATION",
            "file_path": "I291-DOC-001.pdf",
            "source_type": "pdf",
            "document_title": "I291 Integration Test Spec",
        }
        meta.update(overrides)
        return meta

    def test_elements_ddl_shape(self):
        """T1.254 (I291)(3): id UUID PK, created_at DEFAULT now(), element_seq emitted."""
        schema = SchemaToDDL.load_doc_base_schema(self.config_dir)
        ddl = SchemaToDDL(schema).generate_document_elements_ddl()
        self.assertIn("id VARCHAR PRIMARY KEY", ddl)
        self.assertIn("created_at TIMESTAMP NOT NULL DEFAULT now()", ddl)
        self.assertIn("element_seq INTEGER", ddl)
        self.assertIn("doc_id VARCHAR NOT NULL", ddl)
        self.assertIn("element_type VARCHAR NOT NULL", ddl)

    def test_relations_manifest(self):
        """T1.254 (I291)(2): declared_only relations materialized in _eks_table_relations."""
        from eks.engine.core.schema_to_ddl import SchemaToDDL
        schema = SchemaToDDL.load_doc_base_schema(self.config_dir)
        ddl_gen = SchemaToDDL(schema)
        names = {r["relation_name"] for r in ddl_gen.registry_relations()}
        for required in ["fk_element_doc", "fk_element_type"]:
            self.assertIn(required, names)

        pre_generated = {
            "documents_ddl": ddl_gen.generate_documents_ddl(),
            "elements_ddl": ddl_gen.generate_document_elements_ddl(),
            "indexes": ddl_gen.generate_indexes(),
            "doc_base_schema": schema,
        }
        reg_path = self.test_dir / "test_i291_relations.db"
        if reg_path.exists():
            reg_path.unlink()
        try:
            import duckdb
            DocumentRegistry(db_path=str(reg_path), pre_generated_ddl=pre_generated)
            conn = duckdb.connect(str(reg_path))
            try:
                row_names = {r[0] for r in conn.execute(
                    "SELECT relation_name FROM _eks_table_relations"
                ).fetchall()}
            finally:
                conn.close()
            for n in ["fk_element_doc", "fk_element_type"]:
                self.assertIn(n, row_names)
        finally:
            if reg_path.exists():
                reg_path.unlink()

    def test_detect_store_query_roundtrip(self):
        """T1.254 (I291)(5): register → detect → store → get_elements_by_type round-trip."""
        reg_path, reg = self._make_registry("test_i291_roundtrip.db")
        try:
            doc_id = reg.register_document(self._make_doc_meta())
            self.assertTrue(doc_id)

            detector = StructureDetector()
            elements = detector.detect(
                "I291-DOC-001.pdf",
                full_text="1.0 INTRODUCTION\n2.0 SCOPE\nSome body text here.",
                expected_element_types={"cover_page", "section"},
                cover_type="A",
            )
            stored = reg.store_elements(doc_id, elements)
            self.assertEqual(stored, len(elements))

            reg_types = reg.get_elements_by_type(doc_id, "section")
            self.assertGreater(len(reg_types), 0,
                               "I291: detect→store→query_by_type round-trip must yield sections")
            for el in reg_types:
                self.assertEqual(el["doc_id"], doc_id)
                self.assertIn(el["element_type"], VALID_ELEMENT_TYPES)
                self.assertTrue(el["id"])  # surrogate UUID PK populated
                self.assertTrue(el["created_at"])  # DEFAULT now() filled

            all_els = reg.get_elements(doc_id)
            by_type = len(reg_types)
            self.assertLessEqual(by_type, len(all_els))
        finally:
            if reg_path.exists():
                reg_path.unlink()

    def test_unknown_element_type_rejected(self):
        """T1.254 (I291)(2): store_elements raises on an unregistered element_type."""
        reg_path, reg = self._make_registry("test_i291_badtype.db")
        try:
            doc_id = reg.register_document(self._make_doc_meta())
            with self.assertRaises(ValueError) as ctx:
                reg.store_elements(doc_id, [
                    {"element_type": "not_a_real_element", "source": "regex"}
                ])
            self.assertIn("element_type", str(ctx.exception))
            # Nothing must have been persisted.
            self.assertEqual(reg.get_elements(doc_id), [])
        finally:
            if reg_path.exists():
                reg_path.unlink()

    def test_store_elements_unknown_doc_rejected(self):
        """T1.254 (I291)(2): store_elements rejects writes for unregistered documents."""
        reg_path, reg = self._make_registry("test_i291_unknowndoc.db")
        try:
            with self.assertRaises(ValueError) as ctx:
                reg.store_elements(str(uuid.uuid4()), [
                    {"element_type": "section", "source": "regex"}
                ])
            self.assertIn("not found", str(ctx.exception))
        finally:
            if reg_path.exists():
                reg_path.unlink()

    def test_cover_c_zero_elements_registry_row_persists(self):
        """T1.254 (I291)(5)/I290 Q6: empty expected_elements → 0 element rows, doc still registered."""
        reg_path, reg = self._make_registry("test_i291_cover_c.db")
        try:
            doc_id = reg.register_document(self._make_doc_meta())
            # cover-type 'C' / empty expected_element_types → detector gates everything out.
            elements = StructureDetector().detect(
                "I291-DOC-001.pdf",
                full_text="Scanned no-cover document.",
                skip_cover_page=True,
                expected_element_types=set(),
                cover_type="C",
            )
            self.assertEqual(elements, [])

            stored = reg.store_elements(doc_id, elements)
            self.assertEqual(stored, 0)

            self.assertEqual(reg.get_elements(doc_id), [])
            docs = reg.list_documents()
            self.assertIn(doc_id, {d.get("id") or d.get("doc_id") for d in docs})
        finally:
            if reg_path.exists():
                reg_path.unlink()

    def test_delete_elements_semantics(self):
        """T1.254 (I291)(5): delete_elements removes all rows for a document."""
        reg_path, reg = self._make_registry("test_i291_delete.db")
        try:
            doc_id = reg.register_document(self._make_doc_meta())
            elements = [
                {"element_type": "cover_page", "source": "regex"},
                {"element_type": "section", "source": "regex"},
                {"element_type": "table", "source": "heuristic"},
            ]
            stored = reg.store_elements(doc_id, elements)
            self.assertEqual(stored, 3)
            self.assertEqual(len(reg.get_elements(doc_id)), 3)

            deleted = reg.delete_elements(doc_id)
            self.assertEqual(deleted, 3)
            self.assertEqual(reg.get_elements(doc_id), [])
        finally:
            if reg_path.exists():
                reg_path.unlink()


if __name__ == "__main__":
    unittest.main()
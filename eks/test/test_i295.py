"""
Integration tests for I295 (T1.258) — runtime `document_reference` junction
table + CRUD + Phase B population from references_documents JSON (GROUP 11).

Scope (re-scoped 2026-08-10, design review approved):
  1. `document_reference` table exists in the runtime registry DB
  2. store_document_reference()/list_document_references()/delete_document_references()
  3. relation_type validated against the 10-type enum
  4. source/target endpoint existence validated (declared_only FK semantics)
  5. Orchestrator persist_document_references() populates `references` edges
     from the references_documents JSON column (M:N query across relationships)
"""
import unittest
import uuid
from pathlib import Path

from eks.engine.core import DocumentRegistry
from eks.engine.core.schema_to_ddl import SchemaToDDL
from eks.engine.core.pipeline_orchestrator import PipelineOrchestrator

_PROJECT_ROOT = Path(__file__).resolve().parent.parent

VALID_RELATIONS = {
    "produced_from", "validated_by", "references", "implements", "supersedes",
    "derived_from", "contains", "linked_to", "verified_against", "governs",
}


class _FakeLogger:
    def __init__(self, run_id: str = "run-I295"):
        self.run_id = run_id
        self.level = 1

    def status(self, message, context=None):  # noqa: ANN001
        pass

    def info(self, message, context=None):  # noqa: ANN001
        pass

    def warning(self, message, context=None):  # noqa: ANN001
        pass

    def debug(self, message, context=None):  # noqa: ANN001
        pass

    def error(self, message, context=None):  # noqa: ANN001
        pass


class TestI295DocumentReference(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_dir = _PROJECT_ROOT / "config" / "schemas"
        if not cls.config_dir.exists():
            cls.config_dir = _PROJECT_ROOT / "config"
        cls.test_dir = _PROJECT_ROOT / "test_output"
        cls.test_dir.mkdir(exist_ok=True)

    def _make_registry(self, name: str, run_id: str = "run-I295"):
        reg_path = self.test_dir / name
        if reg_path.exists():
            reg_path.unlink()
        reg = DocumentRegistry(db_path=str(reg_path), logger=_FakeLogger(run_id))
        return reg_path, reg

    def test_document_reference_ddl_shape(self):
        """T1.258 (I295)(1): document_reference DDL has UUID PK + both FK endpoints."""
        schema = SchemaToDDL.load_doc_base_schema(self.config_dir)
        ddl = SchemaToDDL(schema).generate_document_reference_ddl()
        self.assertIn("id VARCHAR PRIMARY KEY", ddl)
        self.assertIn("source_doc_id VARCHAR NOT NULL", ddl)
        self.assertIn("target_doc_id VARCHAR NOT NULL", ddl)
        self.assertIn("relation_type VARCHAR NOT NULL", ddl)
        self.assertIn("created_at TIMESTAMP NOT NULL DEFAULT now()", ddl)

    def test_table_created_in_runtime_db(self):
        """T1.258 (I295)(1): document_reference exists in a freshly initialized registry."""
        reg_path, reg = self._make_registry("test_i295_tbl.db")
        try:
            import duckdb
            conn = duckdb.connect(str(reg_path))
            try:
                rows = {r[0] for r in conn.execute(
                    "SELECT table_name FROM information_schema.tables"
                ).fetchall()}
            finally:
                conn.close()
            self.assertIn("document_reference", rows)
        finally:
            if reg_path.exists():
                reg_path.unlink()

    def test_store_and_query_roundtrip(self):
        """T1.258 (I295)(2): store → list(source/target) M:N round-trip."""
        reg_path, reg = self._make_registry("test_i295_roundtrip.db")
        try:
            d1 = reg.register_document({"document_number": "DOC-A", "revision": "A",
                                        "file_path": "a.pdf",
                                        "document_type": "SPECIFICATION"})
            d2 = reg.register_document({"document_number": "DOC-B", "revision": "A",
                                        "file_path": "b.pdf",
                                        "document_type": "SPECIFICATION"})
            d3 = reg.register_document({"document_number": "DOC-C", "revision": "A",
                                        "file_path": "c.pdf",
                                        "document_type": "SPECIFICATION"})

            reg.store_document_reference(d1, d2, "references")
            reg.store_document_reference(d1, d3, "references")
            reg.store_document_reference(d3, d2, "governs")

            # Source query returns its outgoing edges.
            out_d1 = reg.list_document_references(d1)
            self.assertEqual(len(out_d1), 2)
            self.assertTrue(all(r["source_doc_id"] == d1 for r in out_d1))
            target_ids = {r["target_doc_id"] for r in out_d1}
            self.assertEqual(target_ids, {d2, d3})

            # Target query returns incoming + outgoing edges (M:N closure).
            all_d2 = reg.list_document_references(d2)
            self.assertEqual(len(all_d2), 2)
            types_d2 = {r["relation_type"] for r in all_d2}
            self.assertEqual(types_d2, {"references", "governs"})

            # Isolated node has no edges.
            d4 = reg.register_document({"document_number": "DOC-D", "revision": "A",
                                        "file_path": "d.pdf",
                                        "document_type": "SPECIFICATION"})
            self.assertEqual(reg.list_document_references(d4), [])
        finally:
            if reg_path.exists():
                reg_path.unlink()

    def test_relation_type_validated(self):
        """T1.258 (I295)(3): store_document_reference rejects unknown relation_type."""
        reg_path, reg = self._make_registry("test_i295_badrel.db")
        try:
            d1 = reg.register_document({"document_number": "DOC-X", "revision": "A",
                                        "file_path": "x.pdf",
                                        "document_type": "SPECIFICATION"})
            d2 = reg.register_document({"document_number": "DOC-Y", "revision": "A",
                                        "file_path": "y.pdf",
                                        "document_type": "SPECIFICATION"})
            with self.assertRaises(ValueError) as ctx:
                reg.store_document_reference(d1, d2, "not_a_real_relation")
            self.assertIn("relation_type", str(ctx.exception))
            self.assertEqual(reg.list_document_references(d1), [])
        finally:
            if reg_path.exists():
                reg_path.unlink()

    def test_endpoint_existence_validated(self):
        """T1.258 (I295)(4): unknown source/target doc id rejected."""
        reg_path, reg = self._make_registry("test_i295_badend.db")
        try:
            d2 = reg.register_document({"document_number": "DOC-Z", "revision": "A",
                                        "file_path": "z.pdf",
                                        "document_type": "SPECIFICATION"})
            with self.assertRaises(ValueError) as ctx:
                reg.store_document_reference(str(uuid.uuid4()), d2, "references")
            self.assertIn("not found", str(ctx.exception))
            with self.assertRaises(ValueError) as ctx2:
                reg.store_document_reference(d2, str(uuid.uuid4()), "references")
            self.assertIn("not found", str(ctx2.exception))
        finally:
            if reg_path.exists():
                reg_path.unlink()

    def test_delete_document_references_semantics(self):
        """T1.258 (I295)(2): delete removes all edges where doc is source or target."""
        reg_path, reg = self._make_registry("test_i295_del.db")
        try:
            d1 = reg.register_document({"document_number": "DOC-1", "revision": "A",
                                        "file_path": "1.pdf",
                                        "document_type": "SPECIFICATION"})
            d2 = reg.register_document({"document_number": "DOC-2", "revision": "A",
                                        "file_path": "2.pdf",
                                        "document_type": "SPECIFICATION"})
            d3 = reg.register_document({"document_number": "DOC-3", "revision": "A",
                                        "file_path": "3.pdf",
                                        "document_type": "SPECIFICATION"})
            reg.store_document_reference(d1, d2, "references")
            reg.store_document_reference(d3, d1, "linked_to")
            self.assertEqual(len(reg.list_document_references(d1)), 2)

            deleted = reg.delete_document_references(d1)
            self.assertEqual(deleted, 2)
            self.assertEqual(reg.list_document_references(d1), [])
            # d2/d3 edges referencing d1 also gone.
            self.assertEqual(reg.list_document_references(d3), [])
        finally:
            if reg_path.exists():
                reg_path.unlink()

    def test_orchestrator_populate_from_references_json(self):
        """T1.258 (I295)(5): persist_document_references builds edges from JSON column."""
        reg_path, reg = self._make_registry("test_i295_orch.db", run_id="run-ORCH")

        d1 = reg.register_document({"document_number": "DOC-001", "revision": "A",
                                    "document_type": "SPECIFICATION",
                                    "file_path": "a.pdf",
                                    "references_documents": ["DOC-002"]})
        d2 = reg.register_document({"document_number": "DOC-002", "revision": "A",
                                    "document_type": "DATASHEET",
                                    "file_path": "b.pdf",
                                    "references_documents": ["DOC-003"]})
        d3 = reg.register_document({"document_number": "DOC-003", "revision": "A",
                                    "document_type": "CALCULATION",
                                    "file_path": "c.pdf"})

        orch = object.__new__(PipelineOrchestrator)
        orch.registry = reg
        orch.logger = _FakeLogger("run-ORCH")

        stored = orch.persist_document_references()
        self.assertEqual(stored, 2)

        # M:N closure: DOC-001 → DOC-002 and DOC-002 → DOC-003.
        edges_d1 = reg.list_document_references(d1)
        self.assertEqual(len(edges_d1), 1)
        self.assertEqual(edges_d1[0]["relation_type"], "references")
        self.assertEqual(edges_d1[0]["target_doc_id"], d2)

        edges_d2 = reg.list_document_references(d2)
        # DOC-002 is source of DOC-003 edge + target of DOC-001 edge.
        self.assertEqual(len(edges_d2), 2)
        target_set = {e["target_doc_id"] for e in edges_d2}
        self.assertIn(d3, target_set)

        edges_d3 = reg.list_document_references(d3)
        self.assertEqual(len(edges_d3), 1)
        self.assertEqual(edges_d3[0]["source_doc_id"], d2)
        self.assertEqual(edges_d3[0]["target_doc_id"], d3)
        if reg_path.exists():
            reg_path.unlink()


if __name__ == "__main__":
    unittest.main()

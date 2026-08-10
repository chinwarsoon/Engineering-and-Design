"""
Integration tests for I294 (T1.257) — runtime `health_score`+`health_batch`
tables + persistence of score_batch() output at Phase B end (GROUP 8/11).

Scope (re-scoped 2026-08-10, design review approved):
  1. `health_score`/`health_batch` tables exist in the runtime registry DB
  2. score_batch() returns per-doc doc_scores carrying documents.id UUID
  3. store_health_score() persists rows under the UUID document_id
  4. store_health_batch() persists the aggregate; by_status counts match
  5. get_health_scores() round-trips the persisted rows
  6. Document references retention semantic — using declared_only FK, health
     rows are keyed by (run_id, document_id)
"""
import unittest
import tempfile
from pathlib import Path

from eks.engine.core import DocumentRegistry
from eks.engine.core.health_scorer import HealthScorer
from eks.engine.core.schema_to_ddl import SchemaToDDL
from eks.engine.core.pipeline_orchestrator import PipelineOrchestrator

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


class _FakeLogger:
    def __init__(self, run_id: str = "run-I294"):
        self.run_id = run_id
        self.level = 1

    def status(self, message, context=None):
        pass

    def info(self, message, context=None):
        pass

    def warning(self, message, context=None):
        pass

    def debug(self, message, context=None):
        pass

    def error(self, message, context=None):
        pass


class TestI294HealthPersistence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_dir = _PROJECT_ROOT / "config" / "schemas"
        if not cls.config_dir.exists():
            cls.config_dir = _PROJECT_ROOT / "config"
        cls.test_dir = _PROJECT_ROOT / "test_output"
        cls.test_dir.mkdir(exist_ok=True)

    def _make_registry(self, name: str, run_id: str = "run-I294"):
        reg_path = self.test_dir / name
        if reg_path.exists():
            reg_path.unlink()
        reg = DocumentRegistry(db_path=str(reg_path), logger=_FakeLogger(run_id))
        return reg_path, reg

    def _seed_docs(self, reg, count=3):
        """Register `count` documents and return their UUID ids."""
        ids = []
        for i in range(1, count + 1):
            ids.append(reg.register_document({
                "document_number": f"I294-DOC-{i:03d}",
                "revision": "A",
                "document_type": "SPECIFICATION",
                "file_path": f"I294-DOC-{i:03d}.pdf",
            }))
        return ids

    def test_health_tables_ddl_shape(self):
        """T1.257 (I294)(1): health_score + health_batch DDL include expected columns."""
        schema = SchemaToDDL.load_doc_base_schema(self.config_dir)
        ddl_gen = SchemaToDDL(schema)
        hs = ddl_gen.generate_health_score_ddl()
        self.assertIn("document_id VARCHAR", hs)
        self.assertIn("health_score DOUBLE", hs)
        self.assertIn("dim_completeness DOUBLE", hs)
        self.assertIn("missing_columns JSON", hs)

        hb = ddl_gen.generate_health_batch_ddl()
        self.assertIn("run_id VARCHAR PRIMARY KEY", hb)
        self.assertIn("avg_document_health DOUBLE", hb)
        self.assertIn("status_success INTEGER", hb)

    def test_tables_created_in_runtime_db(self):
        """T1.257 (I294)(1): both tables exist in a freshly initialized registry."""
        reg_path, reg = self._make_registry("test_i294_tbl.db")
        try:
            import duckdb
            conn = duckdb.connect(str(reg_path))
            try:
                rows = {r[0] for r in conn.execute(
                    "SELECT table_name FROM information_schema.tables"
                ).fetchall()}
            finally:
                conn.close()
            self.assertIn("health_score", rows)
            self.assertIn("health_batch", rows)
        finally:
            if reg_path.exists():
                reg_path.unlink()

    def test_score_batch_returns_doc_scores_with_uuid(self):
        """T1.257 (I294)(2): score_batch doc_scores carry documents.id UUID + flattened dims."""
        reg_path, reg = self._make_registry("test_i294_batch.db")
        try:
            ids = self._seed_docs(reg, 2)
            docs = reg.list_documents(latest_only=False)
            batch = HealthScorer().score_batch(docs)

            self.assertEqual(batch["total_documents"], 2)
            self.assertEqual(len(batch["doc_scores"]), 2)
            for row in batch["doc_scores"]:
                self.assertIn(row["document_id"], ids)
                self.assertIsInstance(row.get("health_score"), (int, float))
                dims = row["dimensions"]
                # Flattened numeric dimension values.
                for key in ("completeness", "source_quality", "consistency"):
                    self.assertIsInstance(dims.get(key), (int, float))
        finally:
            if reg_path.exists():
                reg_path.unlink()

    def test_store_health_score_under_uuid_doc_id(self):
        """T1.257 (I294)(3): store_health_score persists under the UUID document_id."""
        reg_path, reg = self._make_registry("test_i294_score.db")
        try:
            ids = self._seed_docs(reg, 1)
            doc_id = ids[0]
            row_id = reg.store_health_score("run-1", doc_id, {
                "class_id": "SPECIFICATION",
                "template_id": "std_spec",
                "health_score": 0.92,
                "extract_status": "success",
                "dimensions": {
                    "completeness": 0.9, "extraction_confidence": 0.95,
                    "structural_completeness": 0.8, "source_quality": 0.9,
                    "xref_quality": 0.85, "consistency": 1.0,
                },
                "missing_columns": ["area"],
                "tier1_populated": 6,
                "tier1_total": 8,
            })
            self.assertTrue(row_id)
            rows = reg.get_health_scores("run-1")
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["document_id"], doc_id)
            self.assertEqual(rows[0]["health_score"], 0.92)
            self.assertEqual(rows[0]["template_id"], "std_spec")
        finally:
            if reg_path.exists():
                reg_path.unlink()

    def test_store_health_batch_aggregate(self):
        """T1.257 (I294)(4): health_batch aggregate row has correct by_status counts."""
        reg_path, reg = self._make_registry("test_i294_agg.db")
        try:
            ids = self._seed_docs(reg, 3)
            docs = reg.list_documents(latest_only=False)
            batch = HealthScorer().score_batch(docs)

            reg.store_health_batch("run-AGG", batch)
            import duckdb
            conn = duckdb.connect(str(reg_path))
            try:
                row = conn.execute(
                    "SELECT * FROM health_batch WHERE run_id = ?", ["run-AGG"]
                ).fetchone()
                cols = [d[0] for d in conn.description]
                d = dict(zip(cols, row))
            finally:
                conn.close()
            self.assertEqual(d["total_documents"], 3)
            self.assertEqual(d["status_success"], batch["by_status"]["success"])
            self.assertEqual(d["status_partial"], batch["by_status"]["partial"])
            self.assertEqual(d["status_failed"], batch["by_status"]["failed"])
            self.assertAlmostEqual(d["avg_document_health"],
                                   batch["avg_document_health"], places=4)
        finally:
            if reg_path.exists():
                reg_path.unlink()

    def test_orchestrator_persist_batch_health(self):
        """T1.257 (I294)(5/6): persist_batch_health writes per-doc rows + aggregate."""
        reg_path, reg = self._make_registry("test_i294_orch.db", run_id="run-ORCH")
        try:
            ids = self._seed_docs(reg, 2)
            docs = reg.list_documents(latest_only=False)
            batch = HealthScorer().score_batch(docs)

            orch = object.__new__(PipelineOrchestrator)
            orch.registry = reg
            orch.logger = _FakeLogger("run-ORCH")

            persisted = orch.persist_batch_health("run-ORCH", batch)
            self.assertEqual(persisted, 2)

            rows = reg.get_health_scores("run-ORCH")
            self.assertEqual(len(rows), 2)
            persisted_ids = {r["document_id"] for r in rows}
            self.assertEqual(persisted_ids, set(ids))

            import duckdb
            conn = duckdb.connect(str(reg_path))
            try:
                agg = conn.execute(
                    "SELECT total_documents, status_success FROM health_batch "
                    "WHERE run_id = ?", ["run-ORCH"]
                ).fetchone()
            finally:
                conn.close()
            self.assertEqual(agg[0], 2)
        finally:
            if reg_path.exists():
                reg_path.unlink()


if __name__ == "__main__":
    unittest.main()
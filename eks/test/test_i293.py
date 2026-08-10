"""
Integration tests for I293 (T1.256) — `batch_run` runtime table creation +
CRUD + orchestrator phase-boundary stage-stat wiring (GROUP 11).

Scope (re-scoped 2026-08-10, design review approved):
  1. `batch_run` table exists in the runtime registry DB (SchemaToDDL DDL)
  2. insert_batch()/update_batch()/get_batch() round-trip
  3. update_batch() partial-field semantics (only non-None columns updated)
  4. Orchestrator `_sync_batch_run("A"/"B"/"C", summary)` writes phase stats
  5. Phase C finalizes status=success + current_stage=complete
"""
import unittest
import tempfile
from pathlib import Path

from eks.engine.core import DocumentRegistry
from eks.engine.core.schema_to_ddl import SchemaToDDL
from eks.engine.core.pipeline_orchestrator import PipelineOrchestrator

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


class _FakeLogger:
    """Minimal logger carrying a run_id for batch_run tracking."""

    def __init__(self, run_id: str = "run-I293"):
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


class TestI293BatchRun(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_dir = _PROJECT_ROOT / "config" / "schemas"
        if not cls.config_dir.exists():
            cls.config_dir = _PROJECT_ROOT / "config"
        cls.test_dir = _PROJECT_ROOT / "test_output"
        cls.test_dir.mkdir(exist_ok=True)

    def _make_registry(self, name: str, run_id: str = "run-I293"):
        reg_path = self.test_dir / name
        if reg_path.exists():
            reg_path.unlink()
        reg = DocumentRegistry(db_path=str(reg_path), logger=_FakeLogger(run_id))
        return reg_path, reg

    def test_batch_run_ddl_shape(self):
        """T1.256 (I293)(1): batch_run DDL includes run_id PK + 8 stage-stat columns."""
        schema = SchemaToDDL.load_doc_base_schema(self.config_dir)
        ddl = SchemaToDDL(schema).generate_batch_run_ddl()
        self.assertIn("run_id VARCHAR PRIMARY KEY", ddl)
        for col in [
            "job_id", "current_stage", "phase_a_discovered", "phase_a_valid",
            "phase_b_total", "phase_b_success", "phase_b_failed", "phase_c_flagged",
        ]:
            self.assertIn(col, ddl)

    def test_table_created_in_runtime_db(self):
        """T1.256 (I293)(1): batch_run exists in a freshly initialized registry."""
        reg_path, reg = self._make_registry("test_i293_tbl.db")
        try:
            import duckdb
            conn = duckdb.connect(str(reg_path))
            try:
                rows = {r[0] for r in conn.execute(
                    "SELECT table_name FROM information_schema.tables"
                ).fetchall()}
            finally:
                conn.close()
            self.assertIn("batch_run", rows)
        finally:
            if reg_path.exists():
                reg_path.unlink()

    def test_insert_update_get_roundtrip(self):
        """T1.256 (I293)(2): insert_batch → update_batch → get_batch round-trip."""
        reg_path, reg = self._make_registry("test_i293_roundtrip.db")
        try:
            rid = reg.insert_batch("run-ABC", job_id="job-1", data_dir="/tmp/x")
            self.assertEqual(rid, "run-ABC")
            row = reg.get_batch("run-ABC")
            self.assertEqual(row["job_id"], "job-1")
            self.assertEqual(row["data_dir"], "/tmp/x")
            self.assertEqual(row["status"], "running")
            self.assertEqual(row["current_stage"], "A")

            reg.update_batch(
                "run-ABC", current_stage="B",
                phase_a_discovered=12, phase_a_valid=10,
                phase_b_total=10, phase_b_success=8, phase_b_failed=2,
            )
            row = reg.get_batch("run-ABC")
            self.assertEqual(row["current_stage"], "B")
            self.assertEqual(row["phase_a_discovered"], 12)
            self.assertEqual(row["phase_b_success"], 8)

            reg.update_batch("run-ABC", current_stage="complete",
                             phase_c_flagged=3, status="success")
            row = reg.get_batch("run-ABC")
            self.assertEqual(row["current_stage"], "complete")
            self.assertEqual(row["phase_c_flagged"], 3)
            self.assertEqual(row["status"], "success")
            self.assertTrue(row["finished_at"])
        finally:
            if reg_path.exists():
                reg_path.unlink()

    def test_update_partial_fields_only(self):
        """T1.256 (I293)(3): update_batch only touches non-None fields."""
        reg_path, reg = self._make_registry("test_i293_partial.db")
        try:
            reg.insert_batch("run-PART", job_id="job-p")
            reg.update_batch("run-PART", phase_b_total=9)
            row = reg.get_batch("run-PART")
            # Unrelated fields unchanged.
            self.assertEqual(row["job_id"], "job-p")
            self.assertEqual(row["current_stage"], "A")
            self.assertEqual(row["phase_b_total"], 9)
            self.assertEqual(row["phase_b_success"], 0)
        finally:
            if reg_path.exists():
                reg_path.unlink()

    def test_get_batch_missing_returns_none(self):
        """T1.256 (I293)(2): get_batch returns None for an unknown run_id."""
        reg_path, reg = self._make_registry("test_i293_missing.db")
        try:
            self.assertIsNone(reg.get_batch("does-not-exist"))
        finally:
            if reg_path.exists():
                reg_path.unlink()

    def test_orchestrator_phase_boundary_wiring(self):
        """T1.256 (I293)(4/5): _sync_batch_run writes stage stats + finalizes on C."""
        reg_path, reg = self._make_registry("test_i293_orch.db", run_id="run-ORCH")

        orch = object.__new__(PipelineOrchestrator)
        orch.registry = reg
        orch.logger = _FakeLogger("run-ORCH")
        orch._last_root_dir = "/tmp/data"

        # No batch row before first phase boundary.
        self.assertIsNone(reg.get_batch("run-ORCH"))

        orch._sync_batch_run("A", {"discovered": 20, "valid": 15})
        row = reg.get_batch("run-ORCH")
        self.assertEqual(row["current_stage"], "A")
        self.assertEqual(row["phase_a_discovered"], 20)
        self.assertEqual(row["phase_a_valid"], 15)

        orch._sync_batch_run("B", {"total": 15, "success": 12, "failed": 3})
        row = reg.get_batch("run-ORCH")
        self.assertEqual(row["current_stage"], "B")
        self.assertEqual(row["phase_b_total"], 15)
        self.assertEqual(row["phase_b_success"], 12)
        self.assertEqual(row["phase_b_failed"], 3)

        orch._sync_batch_run("C", {"flagged": 2})
        row = reg.get_batch("run-ORCH")
        self.assertEqual(row["current_stage"], "complete")
        self.assertEqual(row["phase_c_flagged"], 2)
        self.assertEqual(row["status"], "success")
        self.assertTrue(row["finished_at"])
        finally_block_ok = True  # placeholder for symmetry
        self.assertTrue(finally_block_ok)
        if reg_path.exists():
            reg_path.unlink()


if __name__ == "__main__":
    unittest.main()
"""
Tests for I311 (T1.297–T1.298) — schema-driven DB migration + validation gate.

Scope:
  T1.297: MigrationGate plan/build/apply semantics — additive auto-apply,
          structural blocking (P1-R-P-0004), destructive override modes
          (apply/force) with mandatory pre-destructive backup, protected tables
          require force.
  T1.298: CLI wiring — --db-check/--db-apply/--db-force args, mode resolution,
          registry construction transfers the mode into the gate.

Runtime artifacts go to eks/test_output/ (AGENTS.md §6.1); temporary
databases use tempfile.TemporaryDirectory for automatic cleanup.
"""
import tempfile
from pathlib import Path

import duckdb
import pytest

from eks.engine.core.migration_gate import (
    ERR_BACKUP_FAILED,
    ERR_DESTRUCTIVE_BLOCKED,
    ERR_INVALID_POLICY,
    MODE_APPLY,
    MODE_CHECK,
    MODE_FORCE,
    PROTECTED_TABLES,
    MigrationGate,
    MigrationGateError,
)
from eks.engine.pipeline_engine.cli import (
    _EKS_CORE_ARG_SPECS,
    add_db_migration_args,
    resolve_db_migration_mode,
)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_CONFIG_DIR = _PROJECT_ROOT / "config"


def _gate(db_path, mode=None, **kw):
    return MigrationGate(
        db_path=db_path,
        config_dir=_CONFIG_DIR,
        policy="additive",
        mode=mode,
        is_tty=False,
        **kw,
    )


def _seed_full_schema(db_path):
    """Run the gate once on an empty DB to materialize the full config schema."""
    _gate(db_path, mode=None).run()
    assert Path(db_path).exists()


class TestCLIArgsModeResolution:
    """T1.298: --db-check/--db-apply/--db-force parse + mode resolution."""

    def test_arg_specs_registered(self):
        specs = _EKS_CORE_ARG_SPECS
        db_specs = {s["dest"]: s for s in specs if s.get("dest") in
                    ("db_check", "db_apply", "db_force")}
        assert set(db_specs) == {"db_check", "db_apply", "db_force"}
        assert "--db-check" in db_specs["db_check"]["opts"]
        assert "--db-apply" in db_specs["db_apply"]["opts"]
        assert "--yes" in db_specs["db_apply"]["opts"]
        assert "--db-force" in db_specs["db_force"]["opts"]

    def test_add_db_migration_args_populates_namespace(self):
        import argparse
        parser = argparse.ArgumentParser()
        add_db_migration_args(parser)
        ns = parser.parse_args(["--db-apply"])
        assert ns.db_check is False
        assert ns.db_apply is True
        assert ns.db_force is False

    def test_mode_resolution(self):
        import argparse
        parser = argparse.ArgumentParser()
        add_db_migration_args(parser)
        assert resolve_db_migration_mode(parser.parse_args([])) is None
        assert resolve_db_migration_mode(parser.parse_args(["--db-check"])) == "check"
        assert resolve_db_migration_mode(parser.parse_args(["--db-apply"])) == "apply"
        assert resolve_db_migration_mode(parser.parse_args(["--yes"])) == "apply"
        assert resolve_db_migration_mode(parser.parse_args(["--db-force"])) == "force"


class TestPlanBuilding:
    """T1.297: plan classification on a live DB."""

    def test_missing_db_plan_is_additive(self, tmp_path):
        gate = _gate(tmp_path / "nope.db", mode=MODE_CHECK)
        plan = gate.run(include_drift=True)
        assert plan["missing_tables"]
        assert not plan["blocking"]
        assert plan["destructive_required"] is False

    def test_fresh_db_plan_lists_all_missing(self, tmp_path):
        gate = _gate(tmp_path / "fresh.db", mode=MODE_CHECK)
        plan = gate.run(include_drift=True)
        assert plan["missing_tables"]
        assert len(plan["missing_tables"]) >= 50  # full config table set

    def test_extra_table_detected(self, tmp_path):
        db_path = tmp_path / "extra.db"
        conn = duckdb.connect(str(db_path))
        conn.execute("CREATE TABLE some_junk_table (id INTEGER)")
        conn.close()
        plan = _gate(db_path, mode=MODE_CHECK).run(include_drift=False)
        assert "some_junk_table" in plan["extra_tables"]

    def test_structural_mismatch_blocks(self, tmp_path):
        db_path = tmp_path / "struct.db"
        _seed_full_schema(db_path)
        conn = duckdb.connect(str(db_path))
        conn.execute("ALTER TABLE batch_run ALTER COLUMN phase_a_discovered SET DATA TYPE VARCHAR")
        conn.close()
        gate = _gate(db_path)
        plan = gate.build_plan()
        assert plan["structural"], "expected structural drift on bad column type"
        assert plan["blocking"] is True
        assert any(item["column"] == "phase_a_discovered" for item in plan["structural"])


class TestPolicyValidation:
    """T1.297: S-C-S-0311 invalid policy."""

    def test_invalid_policy_raises_registered_code(self, tmp_path):
        gate = MigrationGate(
            db_path=tmp_path / "x.db",
            config_dir=_CONFIG_DIR,
            policy="bogus",
        )
        with pytest.raises(MigrationGateError) as exc_info:
            _ = gate.effective_policy
        assert exc_info.value.code == ERR_INVALID_POLICY
        assert exc_info.value.code == "S-C-S-0311"


class TestApplyAdditive:
    """T1.297: additive actions auto-applied (no destructive override needed)."""

    def test_missing_tables_created(self, tmp_path):
        db_path = tmp_path / "auto.db"
        gate = _gate(db_path, mode=None)
        plan = gate.run()
        assert plan["missing_tables"]
        conn = duckdb.connect(str(db_path), read_only=True)
        tables = {row[0] for row in conn.execute("SHOW TABLES").fetchall()}
        conn.close()
        for name in plan["missing_tables"]:
            assert name in tables


class TestDestructiveBlocked:
    """T1.297: P1-R-P-0004 destructive blocked without override."""

    def test_extra_table_not_dropped_additive(self, tmp_path):
        db_path = tmp_path / "adv.db"
        conn = duckdb.connect(str(db_path))
        conn.execute("CREATE TABLE junk_extra (id INTEGER)")
        conn.close()
        plan = _gate(db_path, mode=None).run()
        assert "junk_extra" in plan["extra_tables"]
        conn = duckdb.connect(str(db_path), read_only=True)
        tables = {row[0] for row in conn.execute("SHOW TABLES").fetchall()}
        conn.close()
        assert "junk_extra" in tables, "additive mode must NOT drop extra tables"

    def test_structural_drift_raises_blocked(self, tmp_path):
        db_path = tmp_path / "blocked.db"
        _seed_full_schema(db_path)
        conn = duckdb.connect(str(db_path))
        conn.execute("ALTER TABLE batch_run ALTER COLUMN phase_a_discovered SET DATA TYPE VARCHAR")
        conn.close()
        with pytest.raises(MigrationGateError) as exc_info:
            _gate(db_path, mode=None).run()
        assert exc_info.value.code == ERR_DESTRUCTIVE_BLOCKED
        assert exc_info.value.code == "P1-R-P-0004"


class TestApplyOverride:
    """T1.297: apply/force override with mandatory pre-destructive backup."""

    def test_apply_drops_extra_table_with_backup(self, tmp_path):
        db_path = tmp_path / "apply.db"
        conn = duckdb.connect(str(db_path))
        conn.execute("CREATE TABLE junk_extra (id INTEGER)")
        conn.close()
        gate = _gate(db_path, mode=MODE_APPLY)
        plan = gate.run()
        assert "junk_extra" in plan["extra_tables"]
        assert gate._backup_taken is not None
        assert gate._backup_taken.exists()
        conn = duckdb.connect(str(db_path), read_only=True)
        tables = {row[0] for row in conn.execute("SHOW TABLES").fetchall()}
        conn.close()
        assert "junk_extra" not in tables

    def test_force_recreates_protected_table(self, tmp_path):
        db_path = tmp_path / "force.db"
        _seed_full_schema(db_path)
        conn = duckdb.connect(str(db_path))
        conn.execute("ALTER TABLE documents ALTER COLUMN page_count SET DATA TYPE VARCHAR")
        conn.close()
        gate = _gate(db_path, mode=MODE_FORCE)
        plan = gate.run()
        assert any(
            item["protected"] and item["table"] == "documents"
            for item in plan["structural"]
        )
        assert gate._backup_taken is not None
        assert "documents" in PROTECTED_TABLES

    def test_apply_does_not_recreate_protected_table(self, tmp_path):
        db_path = tmp_path / "protected.db"
        _seed_full_schema(db_path)
        conn = duckdb.connect(str(db_path))
        conn.execute("ALTER TABLE documents ALTER COLUMN page_count SET DATA TYPE VARCHAR")
        conn.close()
        with pytest.raises(MigrationGateError) as exc_info:
            _gate(db_path, mode=MODE_APPLY).run()
        assert exc_info.value.code == ERR_DESTRUCTIVE_BLOCKED


class TestBackupFailure:
    """T1.297: P1-R-P-0005 backup failure is fatal."""

    def test_backup_failure_raises_registered_code(self, tmp_path, monkeypatch):
        db_path = tmp_path / "backup.db"
        conn = duckdb.connect(str(db_path))
        conn.execute("CREATE TABLE junk_extra (id INTEGER)")
        conn.close()

        def _boom(*_a, **_k):
            raise OSError("simulated copy failure")

        monkeypatch.setattr("eks.engine.core.migration_gate.shutil.copy2", _boom)
        with pytest.raises(MigrationGateError) as exc_info:
            _gate(db_path, mode=MODE_APPLY).run()
        assert exc_info.value.code == ERR_BACKUP_FAILED
        assert exc_info.value.code == "P1-R-P-0005"

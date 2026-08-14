"""Tests for I312 (T1.301–T1.304): schema-driven ``db_manifest`` provenance table.

Covers:
  * manifest.py writer: key taxonomy matches spec, SSOT versions recorded,
    idempotent retried UPSERT, replacement-first, legacy ``_eks_schema_meta``
    migration, per-table counts.
  * migration_gate.py: I196 NOT NULL advisory check (SOFT warn) on
    always-nullable project-metadata columns; db_manifest excluded from
    structural validation.
  * DocumentRegistry integration: writes db_manifest on open, drops the legacy
    ``_eks_schema_meta`` table.
"""
import json
import unittest
from pathlib import Path

import duckdb as _duckdb

from eks import __version__ as EKS_VERSION
from eks.engine.core import DocumentRegistry
from eks.engine.core.manifest import DBManifestWriter
from eks.engine.core.migration_gate import MigrationGate
from eks.engine.core.schema_to_ddl import SchemaToDDL

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_CONFIG_DIR = _PROJECT_ROOT / "config"


def _load_db_config():
    return SchemaToDDL.load_db_config(_CONFIG_DIR)


class TestManifestWriter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = _PROJECT_ROOT / "test_output"
        cls.test_dir.mkdir(parents=True, exist_ok=True)
        cls.db_config = _load_db_config()

    def _writer(self):
        return DBManifestWriter(self.db_config, _CONFIG_DIR)

    def _key_set(self, db_path):
        conn = _duckdb.connect(str(db_path), read_only=True)
        try:
            rows = conn.execute("SELECT key, value FROM db_manifest").fetchall()
        finally:
            conn.close()
        return {r[0]: json.loads(r[1]) for r in rows}

    def test_key_taxonomy_matches_spec(self):
        """All declared keys (global + config:* + table:*) are materialized."""
        w = self._writer()
        keys = set(w._all_keys())
        # global
        for g in ("schema_version", "engine_version", "schema_hash"):
            self.assertIn(g, keys)
        # config sources
        for suffix in w._config_sources().keys():
            self.assertIn(f"config:{suffix}", keys)
        # every db_table
        for tbl in self.db_config["db_tables"]:
            self.assertIn(f"table:{tbl['table_name']}", keys)

    def test_versions_recorded(self):
        db_path = self.test_dir / "i312_versions.db"
        if db_path.exists():
            db_path.unlink()
        self._writer().refresh(db_path)
        kv = self._key_set(db_path)
        self.assertEqual(kv["schema_version"], self.db_config["version"])
        self.assertEqual(kv["engine_version"], EKS_VERSION)
        self.assertEqual(kv["config:db_config"], self.db_config["version"])
        self.assertIn("hash", kv["schema_hash"])
        if db_path.exists():
            db_path.unlink()

    def test_idempotent_upsert(self):
        db_path = self.test_dir / "i312_idem.db"
        if db_path.exists():
            db_path.unlink()
        w = self._writer()
        w.refresh(db_path)
        w.refresh(db_path)
        conn = _duckdb.connect(str(db_path), read_only=True)
        try:
            total = conn.execute("SELECT COUNT(*) FROM db_manifest").fetchone()[0]
            distinct = conn.execute(
                "SELECT COUNT(DISTINCT key) FROM db_manifest"
            ).fetchone()[0]
        finally:
            conn.close()
        self.assertEqual(total, distinct, "db_manifest must have no duplicate keys")
        if db_path.exists():
            db_path.unlink()

    def test_legacy_meta_migrated_and_dropped(self):
        db_path = self.test_dir / "i312_legacy.db"
        if db_path.exists():
            db_path.unlink()
        conn = _duckdb.connect(str(db_path))
        conn.execute(
            "CREATE TABLE _eks_schema_meta (key VARCHAR PRIMARY KEY, value VARCHAR)"
        )
        conn.execute(
            "INSERT INTO _eks_schema_meta VALUES ('schema_hash', 'LEGACYABC')"
        )
        conn.close()
        w = self._writer()
        w.refresh(db_path)
        conn = _duckdb.connect(str(db_path), read_only=True)
        try:
            legacy_exists = conn.execute(
                "SELECT 1 FROM information_schema.tables "
                "WHERE table_name = '_eks_schema_meta'"
            ).fetchone()
            manifest_hash = json.loads(
                conn.execute(
                    "SELECT value FROM db_manifest WHERE key = 'schema_hash'"
                ).fetchone()[0]
            )
        finally:
            conn.close()
        self.assertIsNone(legacy_exists, "_eks_schema_meta must be dropped after migration")
        self.assertEqual(manifest_hash.get("legacy_hash"), "LEGACYABC")
        if db_path.exists():
            db_path.unlink()

    def test_per_table_counts_match(self):
        db_path = self.test_dir / "i312_counts.db"
        if db_path.exists():
            db_path.unlink()
        conn = _duckdb.connect(str(db_path))
        conn.execute("CREATE TABLE documents (id VARCHAR PRIMARY KEY)")
        conn.execute("INSERT INTO documents VALUES ('d1'), ('d2')")
        conn.execute("CREATE TABLE document_elements (id VARCHAR PRIMARY KEY)")
        conn.close()
        self._writer().refresh(db_path)
        kv = self._key_set(db_path)
        self.assertEqual(kv["table:documents"]["rows"], 2)
        self.assertEqual(kv["table:document_elements"]["rows"], 0)
        if db_path.exists():
            db_path.unlink()


class TestGateI312(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = _PROJECT_ROOT / "test_output"
        cls.test_dir.mkdir(parents=True, exist_ok=True)

    def test_i196_not_null_warning(self):
        db_path = self.test_dir / "i312_gate_i196.db"
        if db_path.exists():
            db_path.unlink()
        conn = _duckdb.connect(str(db_path))
        # 'area' is in ALWAYS_NULLABLE_COLUMNS — NOT NULL must warn (SOFT),
        # not be treated as a blocking structural mismatch.
        conn.execute(
            "CREATE TABLE documents (id VARCHAR PRIMARY KEY, area VARCHAR NOT NULL)"
        )
        conn.close()
        gate = MigrationGate(
            db_path,
            config_dir=_CONFIG_DIR,
            policy="additive",
            mode="check",
        )
        plan = gate.build_plan()
        self.assertTrue(
            plan["not_null_warnings"],
            "I196: NOT NULL on always-nullable column must emit a warning",
        )
        self.assertIn(
            "area",
            [w["column"] for w in plan["not_null_warnings"]],
        )
        self.assertFalse(
            any(
                s["column"] == "area" and s["issue"]
                for s in plan["structural"]
            ),
            "I196: always-nullable NOT NULL must NOT be a structural (blocking) issue",
        )
        if db_path.exists():
            db_path.unlink()

    def test_db_manifest_excluded_from_validation(self):
        """db_manifest may have a flexible shape; the gate must skip it."""
        db_path = self.test_dir / "i312_gate_meta.db"
        if db_path.exists():
            db_path.unlink()
        conn = _duckdb.connect(str(db_path))
        conn.execute("CREATE TABLE documents (id VARCHAR PRIMARY KEY)")
        # Deviant db_manifest (no 'key' column) — must not crash the gate.
        conn.execute("CREATE TABLE db_manifest (foo VARCHAR)")
        conn.close()
        gate = MigrationGate(
            db_path,
            config_dir=_CONFIG_DIR,
            policy="additive",
            mode="check",
        )
        plan = gate.build_plan()
        self.assertNotIn("db_manifest", plan["extra_tables"])
        if db_path.exists():
            db_path.unlink()


class TestRegistryManifestIntegration(unittest.TestCase):
    def test_registry_writes_manifest(self):
        db_path = _PROJECT_ROOT / "test_output" / "i312_registry.db"
        if db_path.exists():
            db_path.unlink()
        reg = DocumentRegistry(db_path=str(db_path))
        try:
            conn = _duckdb.connect(str(db_path), read_only=True)
            try:
                legacy = conn.execute(
                    "SELECT 1 FROM information_schema.tables "
                    "WHERE table_name = '_eks_schema_meta'"
                ).fetchone()
                kv = {
                    r[0]: json.loads(r[1])
                    for r in conn.execute(
                        "SELECT key, value FROM db_manifest"
                    ).fetchall()
                }
            finally:
                conn.close()
            self.assertIsNone(legacy, "_eks_schema_meta must be absent after I312")
            self.assertIn("schema_version", kv)
            self.assertIn("engine_version", kv)
            self.assertEqual(kv["schema_version"], self.db_config_version())
            self.assertEqual(kv["engine_version"], EKS_VERSION)
            self.assertEqual(kv["table:documents"]["rows"], 0)
        finally:
            if db_path.exists():
                db_path.unlink()

    @staticmethod
    def db_config_version():
        return SchemaToDDL.load_db_config(_CONFIG_DIR)["version"]


if __name__ == "__main__":
    unittest.main()

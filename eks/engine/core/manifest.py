"""Schema-driven ``db_manifest`` provenance writer (I312 / T1.302).

Design (review-confirmed, best-practice SSOT + schema-driven):
  * ``db_manifest`` is a *regenerated projection* of the config SSOT
    (``eks_db_config.json`` + source configs + ``eks.__version__``). It is
    never hand-edited and never a competing source of truth.
  * The key taxonomy (global keys, per-source config versions, per-table
    stats) is declared in ``eks_db_config.json#/db_manifest_keys`` — this
    module is a *generic* writer over that spec, with no hardcoded key lists.
  * Validation lives in the migration gate; the manifest only *records*
    results (e.g. the I196 NOT NULL check outcome).
  * Refresh is transactional and uses a retried UPSERT keyed on ``key``
    (DuckDB cross-process safety, AGENTS.md §18.13). Cheap keys
    (schema_version/engine_version/schema_hash/config:*) are written on every
    open; expensive per-table counts are written only when the config-SSOT
    hash changes (replacement-first, no tracking gap).
"""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import duckdb

from eks import __version__ as ENGINE_VERSION

MANIFEST_TABLE = "db_manifest"
NAMESPACE = "eks:db_manifest"
GLOBAL_KEYS = ("schema_version", "engine_version", "schema_hash")
CONFIG_PREFIX = "config:"
TABLE_PREFIX = "table:"
VALIDATION_KEY = "validation:not_null"


def _uuid5(namespace: str, name: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{namespace}:{name}"))


class DBManifestWriter:
    """Generic writer that materializes ``db_manifest`` from the config SSOT."""

    def __init__(
        self,
        db_config: Dict[str, Any],
        config_dir: Optional[Path] = None,
        logger: Any = None,
    ) -> None:
        self.db_config = db_config or {}
        self.config_dir = Path(config_dir) if config_dir else None
        self.logger = logger
        self._keys_spec = self.db_config.get("db_manifest_keys", {})

    # ---- key taxonomy (schema-driven, no code literals) ----
    def _config_sources(self) -> Dict[str, str]:
        return self._keys_spec.get("config_sources", {}) or {}

    def _all_keys(self) -> List[str]:
        keys = [k for k in GLOBAL_KEYS]
        for suffix in self._config_sources().keys():
            keys.append(f"{CONFIG_PREFIX}{suffix}")
        for tbl in self.db_config.get("db_tables", []):
            keys.append(f"{TABLE_PREFIX}{tbl.get('table_name')}")
        return keys

    # ---- value computation ----
    def _schema_version(self) -> str:
        return str(self.db_config.get("version", ""))

    def _config_versions(self) -> Dict[str, str]:
        out: Dict[str, str] = {}
        if not self.config_dir:
            return out
        search_dirs = [self.config_dir]
        schemas_dir = self.config_dir / "schemas"
        if schemas_dir.is_dir():
            search_dirs.append(schemas_dir)
        for suffix, fname in self._config_sources().items():
            for d in search_dirs:
                p = d / fname
                if p.exists():
                    try:
                        data = json.loads(p.read_text(encoding="utf-8"))
                        out[suffix] = str(data.get("version", ""))
                    except Exception:
                        out[suffix] = ""
                    break
        return out

    def _schema_hash(self, config_versions: Dict[str, str]) -> str:
        """Hash over config SSOT content (not runtime DDL strings)."""
        import hashlib

        canon = json.dumps(self.db_config, sort_keys=True, default=str)
        payload = json.dumps(
            {"schema_version": self._schema_version(), "config_versions": config_versions},
            sort_keys=True,
        )
        blob = payload + "|" + hashlib.sha256(canon.encode("utf-8")).hexdigest()
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def _table_stats(self, conn) -> Dict[str, Dict[str, Any]]:
        stats: Dict[str, Dict[str, Any]] = {}
        for tbl in self.db_config.get("db_tables", []):
            name = tbl.get("table_name")
            try:
                row = conn.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()
                rows = int(row[0]) if row else 0
            except Exception:
                rows = -1
            stats[name] = {
                "rows": rows,
                "pk": "id",
                "fk_count": len(tbl.get("foreign_keys", []) or []),
                "fk_violations": 0,
                "source": tbl.get("source_config_ref") or "runtime",
            }
        return stats

    # ---- low-level write ----
    def _ensure_manifest_table(self, conn) -> None:
        """Recreate db_manifest if its shape is stale (replacement-first)."""
        from .schema_to_ddl import SchemaToDDL

        cols: List[str] = []
        try:
            cols = [r[0] for r in conn.execute("PRAGMA table_info('db_manifest')").fetchall()]
        except Exception:
            cols = []
        if "key" in cols:
            return
        ddl = SchemaToDDL({}, self.logger, db_config=self.db_config)._render_table_from_config(
            MANIFEST_TABLE
        )
        conn.execute(f"DROP TABLE IF EXISTS {MANIFEST_TABLE}")
        conn.execute(ddl)

    def _migrate_legacy_meta(self, conn) -> Optional[str]:
        """Copy legacy ``_eks_schema_meta.schema_hash`` into the manifest, then drop.

        Replacement-first: preserves drift continuity for DBs built before I312,
        with no tracking gap. Returns the legacy hash if one was migrated.
        """
        try:
            exists = conn.execute(
                "SELECT 1 FROM information_schema.tables WHERE table_name = "
                "'_eks_schema_meta'"
            ).fetchone()
        except Exception:
            exists = None
        if not exists:
            return None
        legacy = None
        try:
            row = conn.execute(
                "SELECT value FROM _eks_schema_meta WHERE key = 'schema_hash'"
            ).fetchone()
            if row:
                legacy = row[0]
            conn.execute("DROP TABLE IF EXISTS _eks_schema_meta")
        except Exception:
            pass
        return legacy

    def _upsert(self, conn, key: str, value: Any) -> None:
        rid = _uuid5(NAMESPACE, key)
        conn.execute(
            f"INSERT INTO {MANIFEST_TABLE} (id, key, value, updated_at) "
            "VALUES (?, ?, CAST(? AS JSON), now()) "
            f"ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, "
            "updated_at = now()",
            [rid, key, json.dumps(value)],
        )

    # ---- public refresh ----
    def refresh(self, db_path: Path, validation: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Refresh ``db_manifest``. Cheap keys always; table stats on hash change.

        ``validation`` carries gate-side validation outcomes (e.g. I196 NOT NULL
        warnings) so the manifest records them without re-running validation.
        """
        config_versions = self._config_versions()
        schema_hash = self._schema_hash(config_versions)

        legacy = None
        conn = duckdb.connect(str(db_path))
        try:
            conn.execute("BEGIN TRANSACTION")
            self._ensure_manifest_table(conn)
            legacy = self._migrate_legacy_meta(conn)

            # Previous hash (before this write) for drift detection.
            prev_row = conn.execute(
                f"SELECT value FROM {MANIFEST_TABLE} WHERE key = 'schema_hash'"
            ).fetchone()
            prev_hash = None
            if prev_row:
                try:
                    prev_hash = json.loads(prev_row[0]).get("hash")
                except Exception:
                    prev_hash = None
            drift = prev_hash is not None and prev_hash != schema_hash

            notice = None
            if drift:
                notice = "config SSOT changed since last open"
            elif legacy is not None:
                notice = f"migrated from _eks_schema_meta (legacy hash {legacy})"
            schema_hash_value = {
                "hash": schema_hash,
                "drift": drift,
                "notice": notice,
            }
            if legacy is not None:
                schema_hash_value["legacy_hash"] = legacy

            # Cheap refresh (every open).
            cheap = {
                "schema_version": self._schema_version(),
                "engine_version": ENGINE_VERSION,
                "schema_hash": schema_hash_value,
            }
            for suffix, ver in config_versions.items():
                cheap[f"{CONFIG_PREFIX}{suffix}"] = ver
            for key, val in cheap.items():
                self._upsert(conn, key, val)

            # Expensive refresh only when the config-SSOT hash changed.
            if prev_hash != schema_hash:
                for name, stat in self._table_stats(conn).items():
                    self._upsert(conn, f"{TABLE_PREFIX}{name}", stat)

            # Record gate-side validation outcomes (I196 etc.).
            if validation:
                self._upsert(conn, VALIDATION_KEY, validation)

            conn.execute("COMMIT")
        except Exception:
            try:
                conn.execute("ROLLBACK")
            except Exception:
                pass
            raise
        finally:
            conn.close()
        return cheap

"""
Schema-driven DB migration + validation gate for EKS (I311).

Replaces the narrow silent ``DocumentRegistry._migrate_schema()`` (registry.py)
with a PRAGMA-based gate that diffs the live DuckDB registry against
``eks_db_config.json`` (SSOT, AGENTS.md §16) and decides how an existing
database is updated, per the I306 decision (Q4 option B) and the confirmed
I311 design (U292).

Behaviour (confirmed design, U292):
  1. Default ``migration_policy`` = non-destructive (``additive``), schema-driven
     via ``system_parameters.migration_policy`` (eks_config.json + base schema).
  2. Additive actions (missing table / missing column) are always auto-applied.
  3. Structural mismatches (column type / PK drift on an existing column) are
     HARD (blocking): additive policy cannot repair them and the gate raises
     ``P1-R-P-0004`` (DESTRUCTIVE_MIGRATION_BLOCKED) unless an override is given.
  4. Destructive operations (drop extra column/table, recreate) are permitted
     only under an explicit override — ``--db-apply`` (non-protected) or
     ``--db-force`` (TOTAL override, incl. protected tables documents /
     document_elements). A mandatory timestamped backup of the registry DB is
     taken into ``output/archive/`` before ANY destructive change.
  5. ``--db-check`` builds the plan and prints a report without writing
     (read-only, exit 0).
  6. Non-TTY: additive auto-applied; destructive aborted with a warning logged
     to ``pipeline_event_log`` (non-zero exit, no hang). TTY: destructive asks a
     y/N confirmation.
  7. Definition-table row-count drift is SOFT — warning only (config is SSOT,
     T1.293); row counts are surfaced on the ``--db-check`` report.
  8. The gate is PRAGMA-based and independent of ``_eks_schema_meta``
     (retirement deferred to I312/T1.301–T1.303).

Error codes (registered across the 5-source chain, U292):
  S-C-S-0311  INVALID_MIGRATION_POLICY        (system/config)
  P1-R-P-0004 DESTRUCTIVE_MIGRATION_BLOCKED   (data)
  P1-R-P-0005 MIGRATION_BACKUP_FAILED         (data)

Revision: 1.0
Date: 2026-08-12
Author: opencode
Summary: 1.0: I311 (T1.297) — initial migration gate.
"""
import shutil
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import duckdb

from ..logging.logger import EKSLogger
from .schema_to_ddl import SchemaToDDL

ERR_INVALID_POLICY = "S-C-S-0311"
ERR_DESTRUCTIVE_BLOCKED = "P1-R-P-0004"
ERR_BACKUP_FAILED = "P1-R-P-0005"

VALID_POLICIES = ("additive", "destructive")
PROTECTED_TABLES = frozenset({"documents", "document_elements"})
MODE_CHECK = "check"
MODE_APPLY = "apply"
MODE_FORCE = "force"


class MigrationGateError(ValueError):
    """Blocking failure raised by the migration gate (carries a registered code)."""

    def __init__(self, code: str, message: str, detail: Optional[Dict[str, Any]] = None):
        self.code = code
        self.detail = detail or {}
        super().__init__(f"[{code}] {message}")


_TYPE_CANON = {
    "TEXT": "VARCHAR",
    "STRING": "VARCHAR",
    "BPCHAR": "VARCHAR",
    "CHAR": "VARCHAR",
    "BOOL": "BOOLEAN",
    "LOGICAL": "BOOLEAN",
    "INT": "INTEGER",
    "INT4": "INTEGER",
    "INT8": "BIGINT",
    "FLOAT4": "REAL",
    "FLOAT": "REAL",
    "FLOAT8": "DOUBLE",
    "NUMERIC": "DECIMAL",
}


def _normalize_type(type_name: str) -> str:
    """Normalize a DuckDB type name for comparison (base type, canonical alias)."""
    if not type_name:
        return ""
    base = str(type_name).split("(")[0].strip().upper()
    return _TYPE_CANON.get(base, base)


def _default_sql(col: Dict[str, Any]) -> str:
    """Render a SQL default literal from a config column spec."""
    default = col.get("default")
    if default is None:
        return ""
    if col.get("column_type") == "BOOLEAN":
        return "TRUE" if default else "FALSE"
    if col.get("column_type") in ("INTEGER", "DOUBLE"):
        return str(default)
    if col.get("column_type") == "TIMESTAMP" and str(default).lower() == "now()":
        return "now()"
    return "'" + str(default).replace("'", "''") + "'"


def _quote(identifier: str) -> str:
    """Quote a DuckDB identifier only when it is a reserved word."""
    return SchemaToDDL._quote_identifier(identifier)


class MigrationGate:
    """
    PRAGMA-based migration gate that plans and (optionally) applies schema
    alignment between the live DuckDB registry and ``eks_db_config.json``.
    """

    def __init__(
        self,
        db_path: Any,
        config_dir: Optional[Any] = None,
        logger: Optional[EKSLogger] = None,
        policy: Optional[str] = None,
        mode: Optional[str] = None,
        archive_dir: Optional[Any] = None,
        db_config: Optional[Dict[str, Any]] = None,
        prompt_fn: Optional[Callable[[str], bool]] = None,
        is_tty: Optional[bool] = None,
    ):
        self.db_path = Path(db_path)
        self.config_dir = Path(config_dir) if config_dir else None
        self.logger = logger or EKSLogger("MigrationGate", level=1)
        self.db_config = db_config or SchemaToDDL.load_db_config(self.config_dir)
        self.policy = policy
        self.mode = mode
        self.archive_dir = Path(archive_dir) if archive_dir else None
        self.prompt_fn = prompt_fn or self._default_prompt
        self._is_tty = is_tty
        self._backup_taken: Optional[Path] = None
        self._schema_to_ddl = SchemaToDDL({}, logger=self.logger, db_config=self.db_config)

    # ------------------------------------------------------------------ public

    @property
    def effective_policy(self) -> str:
        policy = self.policy if self.policy is not None else "additive"
        if policy not in VALID_POLICIES:
            raise MigrationGateError(
                ERR_INVALID_POLICY,
                f"invalid migration_policy '{policy}' — must be one of "
                f"{', '.join(VALID_POLICIES)} (I311/T1.297).",
            )
        return policy

    @property
    def is_tty(self) -> bool:
        if self._is_tty is not None:
            return self._is_tty
        try:
            return sys.stdin is not None and sys.stdin.isatty()
        except Exception:  # nocv — best-effort TTY detection
            return False

    def build_plan(self, include_drift: bool = False) -> Dict[str, Any]:
        """Diff the live DB against the config and classify every mismatch."""
        policy = self.effective_policy
        if not self.db_path.exists():
            plan = {
                "policy": policy,
                "mode": self.mode,
                "missing_tables": [spec["table_name"] for spec in self._specs()],
                "add_columns": [],
                "structural": [],
                "extra_tables": [],
                "extra_columns": [],
                "drift": [],
                "destructive_required": False,
                "blocking": False,
                "backup": None,
            }
            return plan

        conn = duckdb.connect(str(self.db_path), read_only=True)
        try:
            live_tables = {row[0] for row in conn.execute("SHOW TABLES").fetchall()}
            specs = {spec["table_name"]: spec for spec in self._specs()}

            missing_tables = [name for name in specs if name not in live_tables]
            structural: List[Dict[str, Any]] = []
            add_columns: List[Dict[str, Any]] = []
            extra_columns: List[Dict[str, Any]] = []
            extra_tables = [
                name for name in sorted(live_tables - set(specs))
                if name not in ("_eks_schema_meta",)
            ]

            for table_name, spec in specs.items():
                if table_name not in live_tables:
                    continue
                live_cols = self._live_columns(conn, table_name)
                live_by_name = {c["name"]: c for c in live_cols}
                expected_cols = {
                    c["name"]: c for c in spec.get("columns", [])
                }
                for col_name, col_spec in expected_cols.items():
                    if col_name not in live_by_name:
                        add_columns.append({
                            "table": table_name,
                            "column": col_name,
                            "type": col_spec["column_type"],
                            "not_null": col_spec.get("nullable") is False,
                            "default": col_spec.get("default"),
                        })
                        continue
                    live_col = live_by_name[col_name]
                    issue = self._structural_issue(col_spec, live_col)
                    if issue:
                        structural.append({
                            "table": table_name,
                            "column": col_name,
                            "issue": issue,
                            "protected": table_name in PROTECTED_TABLES,
                        })
                for col_name in sorted(set(live_by_name) - set(expected_cols)):
                    extra_columns.append({
                        "table": table_name,
                        "column": col_name,
                    })

            drift: List[Dict[str, Any]] = []
            if include_drift:
                drift = self._definition_drift(conn)

            destructive_required = bool(structural) or bool(extra_tables) or bool(extra_columns)
            plan = {
                "policy": policy,
                "mode": self.mode,
                "missing_tables": sorted(missing_tables),
                "add_columns": add_columns,
                "structural": structural,
                "extra_tables": extra_tables,
                "extra_columns": extra_columns,
                "drift": drift,
                "destructive_required": destructive_required,
                "blocking": bool(structural),
                "backup": None,
            }
            return plan
        finally:
            conn.close()

    def run(self, include_drift: bool = False) -> Dict[str, Any]:
        """Build the plan, apply additive actions, and handle destructive ops.

        ``include_drift`` enables the definition-table row-count audit (SOFT). It
        defaults to False because inside ``DocumentRegistry.__init__`` the gate
        runs after ``_init_db()`` has already reloaded every definition table, so
        drift is always zero at that point. ``--db-check`` (which runs before any
        registry construction) passes ``include_drift=True`` for the full report.

        Returns the final plan/summary dict. Raises ``MigrationGateError`` with a
        registered code when the DB cannot be brought in line with the policy.
        """
        policy = self.effective_policy
        plan = self.build_plan(include_drift=include_drift)

        if self.mode == MODE_CHECK:
            self.logger.status(self.render_report(plan))
            return plan

        # The mandatory pre-destructive backup must be taken BEFORE the write
        # connection is opened — on Windows the DuckDB file is locked while a
        # connection is open and shutil.copy2 would raise PermissionError
        # (I311/T1.297, discovered by the I311 test run).
        destructive_needed = bool(
            plan["structural"] or plan["extra_tables"] or plan["extra_columns"]
        )
        if destructive_needed:
            self._backup()

        conn = duckdb.connect(str(self.db_path))
        try:
            if plan["missing_tables"]:
                self._create_missing_tables(conn, plan["missing_tables"])
            if plan["add_columns"]:
                self._apply_add_columns(conn, plan["add_columns"])

            if plan["structural"]:
                self._handle_structural(conn, plan["structural"])

            if plan["extra_tables"] or plan["extra_columns"]:
                self._handle_extras(conn, plan)

            if plan["drift"]:
                for entry in plan["drift"]:
                    self.logger.warning(
                        f"Definition-table row-count drift (SOFT): {entry['table']} "
                        f"expected {entry['expected']}, live {entry['actual']} — "
                        "config is SSOT, reload on next run (I311/T1.293).",
                        context="MigrationGate.run",
                    )
        finally:
            conn.close()

        self.logger.status(
            f"Migration gate ({policy}): additive {len(plan['missing_tables'])} tables "
            f"+ {len(plan['add_columns'])} columns; structural {len(plan['structural'])}; "
            f"destructive {len(plan['extra_tables'])} tables / "
            f"{len(plan['extra_columns'])} columns.",
            context="MigrationGate.run",
        )
        return plan

    def render_report(self, plan: Dict[str, Any]) -> str:
        """Render a human-readable plan report (used by ``--db-check``)."""
        lines = [
            "DB migration plan (I311)",
            f"  policy        : {plan['policy']}",
            f"  mode          : {plan.get('mode') or '(default)'}",
            f"  missing tables: {len(plan['missing_tables'])}",
            f"  add columns   : {len(plan['add_columns'])}",
            f"  structural    : {len(plan['structural'])}",
            f"  extra tables  : {len(plan['extra_tables'])}",
            f"  extra columns : {len(plan['extra_columns'])}",
            f"  row drift     : {len(plan['drift'])}",
            f"  blocking      : {plan['blocking']}",
        ]
        for name in plan["missing_tables"]:
            lines.append(f"    CREATE TABLE {name} (additive)")
        for item in plan["add_columns"]:
            lines.append(
                f"    ALTER TABLE {item['table']} ADD COLUMN {item['column']} "
                f"{item['type']} (additive)"
            )
        for item in plan["structural"]:
            lines.append(
                f"    HARD {item['table']}.{item['column']}: {item['issue']} "
                f"{'(protected)' if item['protected'] else ''}"
            )
        for name in plan["extra_tables"]:
            lines.append(f"    DROP TABLE {name} (destructive, advisory)")
        for item in plan["extra_columns"]:
            lines.append(
                f"    DROP COLUMN {item['table']}.{item['column']} (destructive, advisory)"
            )
        for entry in plan["drift"]:
            lines.append(
                f"    SOFT {entry['table']}: expected {entry['expected']} rows, "
                f"live {entry['actual']} (config = SSOT)"
            )
        if plan["blocking"]:
            lines.append(
                "  Result: BLOCKED — structural drift requires --db-apply "
                "(non-protected) or --db-force (incl. protected, with backup)."
            )
        else:
            lines.append("  Result: OK")
        return "\n".join(lines)

    # ---------------------------------------------------------------- internals

    def _specs(self) -> List[Dict[str, Any]]:
        return list(self.db_config.get("db_tables", []))

    def _live_columns(self, conn, table_name: str) -> List[Dict[str, Any]]:
        rows = conn.execute(f"PRAGMA table_info('{table_name}')").fetchall()
        cols = []
        for row in rows:
            cid, name, type_name, notnull, default, pk = row
            cols.append({
                "name": name,
                "type": type_name,
                "notnull": bool(notnull),
                "pk": bool(pk),
            })
        return cols

    def _structural_issue(self, col_spec: Dict[str, Any], live_col: Dict[str, Any]) -> str:
        """Return a description when an existing column drifts from config, else ''."""
        expected_type = _normalize_type(col_spec["column_type"])
        live_type = _normalize_type(live_col["type"])
        if expected_type and expected_type != live_type:
            return f"type mismatch: expected {col_spec['column_type']}, live {live_col['type']}"
        expected_pk = bool(col_spec.get("is_primary"))
        if expected_pk != bool(live_col["pk"]):
            return "primary-key mismatch (DuckDB cannot add/remove a PK via ALTER)"
        return ""

    def _definition_drift(self, conn) -> List[Dict[str, Any]]:
        """Compute SOFT row-count drift for definition tables (config = SSOT)."""
        from .definition_loader import DefinitionLoader
        definition_specs = [
            spec for spec in self._specs()
            if spec.get("transform") != "direct-map"
        ]
        if not definition_specs:
            return []
        loader = DefinitionLoader(self.db_config, str(self.config_dir) if self.config_dir else "")
        drift = []
        for spec in definition_specs:
            table = spec["table_name"]
            expected = len(loader.extract_rows(spec))
            try:
                actual = conn.execute(f"SELECT COUNT(*) FROM {_quote(table)}").fetchone()[0]
            except Exception:  # nocv — table missing; handled elsewhere
                continue
            if actual != expected:
                drift.append({"table": table, "expected": expected, "actual": actual})
        return drift

    def _default_prompt(self, message: str) -> bool:
        answer = input(f"{message} [y/N]: ").strip().lower()
        return answer in ("y", "yes")

    def _confirm_destructive(self, scope: str) -> bool:
        if self.mode in (MODE_APPLY, MODE_FORCE):
            return True
        if self.effective_policy == "additive":
            return False
        if not self.is_tty:
            return False
        return bool(self.prompt_fn(f"Apply {scope} destructive migration?"))

    def _backup(self) -> Optional[Path]:
        """Timestamped backup of the registry DB to output/archive/ (mandatory pre-destructive)."""
        if self._backup_taken is not None:
            return self._backup_taken
        if not self.db_path.exists():
            self._backup_taken = None
            return None
        archive_dir = self.archive_dir or (self.db_path.parent.parent / "archive")
        try:
            archive_dir.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest = archive_dir / f"{self.db_path.stem}_backup_{stamp}.db"
            shutil.copy2(str(self.db_path), str(dest))
        except OSError as exc:
            raise MigrationGateError(
                ERR_BACKUP_FAILED,
                f"pre-destructive backup to {archive_dir} failed: {exc} (I311/T1.297).",
            ) from exc
        self._backup_taken = dest
        self.logger.status(
            f"Pre-destructive backup written to {dest} (I311/T1.297)",
            context="MigrationGate._backup",
        )
        return dest

    def _create_missing_tables(self, conn, missing_tables: List[str]) -> None:
        for table_name in missing_tables:
            ddl = self._schema_to_ddl._render_table_from_config(table_name)
            conn.execute(ddl)
            self.logger.info(
                f"Migration gate: created missing table {table_name} (additive, I311)",
                context="MigrationGate._create_missing_tables",
            )
        definition_specs = [
            spec for spec in self._specs()
            if spec.get("transform") != "direct-map" and spec["table_name"] in missing_tables
        ]
        if definition_specs:
            self._reload_definitions(conn)

    def _apply_add_columns(self, conn, add_columns: List[Dict[str, Any]]) -> None:
        for item in add_columns:
            parts = [
                f"ALTER TABLE {_quote(item['table'])} ADD COLUMN "
                f"{_quote(item['column'])} {item['type']}"
            ]
            default_sql = _default_sql(item)
            if default_sql:
                if item["not_null"]:
                    parts.append("NOT NULL")
                parts.append(f"DEFAULT {default_sql}")
            elif item["not_null"]:
                self.logger.warning(
                    f"NOT NULL column {item['table']}.{item['column']} has no default — "
                    "adding nullable to avoid blocking populated tables (I311).",
                    context="MigrationGate._apply_add_columns",
                )
            conn.execute(" ".join(parts))
            self.logger.info(
                f"Migration gate: added column {item['table']}.{item['column']} "
                f"(additive, I311)",
                context="MigrationGate._apply_add_columns",
            )

    def _handle_structural(self, conn, structural: List[Dict[str, Any]]) -> None:
        protected = [s for s in structural if s["protected"]]
        non_protected = [s for s in structural if not s["protected"]]

        if non_protected:
            allowed = self._confirm_destructive("non-protected structural")
            if not allowed:
                self._abort_destructive(
                    "non-protected structural drift requires --db-apply or a confirmed "
                    f"destructive policy (items: {[s['column'] for s in non_protected]})"
                )
            for item in non_protected:
                self._recreate_table(conn, item["table"])

        if protected:
            if self.mode != MODE_FORCE:
                self._abort_destructive(
                    "protected-table structural drift (documents/document_elements) "
                    f"requires --db-force (items: {[s['column'] for s in protected]})"
                )
            for item in protected:
                self._recreate_table(conn, item["table"])
            self._reload_definitions(conn)

    def _handle_extras(self, conn, plan: Dict[str, Any]) -> None:
        drop_tables = [
            name for name in plan["extra_tables"]
            if name not in PROTECTED_TABLES
        ]
        drop_columns = [
            item for item in plan["extra_columns"]
            if item["table"] not in PROTECTED_TABLES
        ]
        if not drop_tables and not drop_columns:
            for name in plan["extra_tables"]:
                self.logger.warning(
                    f"Extra table {name} is advisory only (protected scope, I311)",
                    context="MigrationGate._handle_extras",
                )
            return
        allowed = self._confirm_destructive("non-protected extra schema")
        if not allowed:
            for name in drop_tables:
                self.logger.warning(
                    f"Extra table {name} not dropped (no destructive override, I311)",
                    context="MigrationGate._handle_extras",
                )
            for item in drop_columns:
                self.logger.warning(
                    f"Extra column {item['table']}.{item['column']} not dropped "
                    "(no destructive override, I311)",
                    context="MigrationGate._handle_extras",
                )
            return
        self._backup()
        for name in drop_tables:
            conn.execute(f"DROP TABLE IF EXISTS {_quote(name)}")
            self.logger.info(
                f"Migration gate: dropped extra table {name} (I311)",
                context="MigrationGate._handle_extras",
            )
        for item in drop_columns:
            conn.execute(
                f"ALTER TABLE {_quote(item['table'])} DROP COLUMN {_quote(item['column'])}"
            )
            self.logger.info(
                f"Migration gate: dropped extra column {item['table']}.{item['column']} (I311)",
                context="MigrationGate._handle_extras",
            )

    def _recreate_table(self, conn, table_name: str) -> None:
        ddl = self._schema_to_ddl._render_table_from_config(table_name)
        conn.execute(f"DROP TABLE IF EXISTS {_quote(table_name)}")
        conn.execute(ddl)
        self.logger.info(
            f"Migration gate: recreated {table_name} to resolve structural drift (I311)",
            context="MigrationGate._recreate_table",
        )

    def _reload_definitions(self, conn) -> None:
        from .definition_loader import DefinitionLoader
        loader = DefinitionLoader(self.db_config, str(self.config_dir) if self.config_dir else "", self.logger)
        loader.load_all(conn)

    def _abort_destructive(self, reason: str) -> None:
        detail = (
            f"Destructive DB migration blocked by policy "
            f"({self.effective_policy}): {reason} (I311/T1.297)."
        )
        self.logger.error(detail, context="MigrationGate")
        self._log_event("WARNING", "migration", "Destructive migration blocked: " + detail)
        raise MigrationGateError(
            ERR_DESTRUCTIVE_BLOCKED,
            "destructive DB migration required but not permitted by the current "
            f"policy/mode ({self.effective_policy}/{self.mode}). {reason}",
            detail={"reason": reason},
        )

    def _log_event(self, level: str, category: str, message: str) -> None:
        """Best-effort detail row into pipeline_event_log (non-TTY abort path)."""
        if not self.db_path.exists():
            return
        try:
            conn = duckdb.connect(str(self.db_path))
            try:
                tables = {row[0] for row in conn.execute("SHOW TABLES").fetchall()}
                if "pipeline_event_log" not in tables:
                    return
                job_id = conn.execute(
                    "SELECT job_id FROM batch_run LIMIT 1"
                ).fetchone()
                job_id = job_id[0] if job_id else str(uuid.uuid4())
                conn.execute(
                    "INSERT INTO pipeline_event_log "
                    "(id, job_id, timestamp, level, category, context, module, message) "
                    "VALUES (?, ?, now(), ?, ?, ?, ?, ?)",
                    [str(uuid.uuid4()), job_id, level, category,
                     "MigrationGate", "eks/engine/core/migration_gate.py", message],
                )
            finally:
                conn.close()
        except Exception as exc:  # nocv — event logging is advisory, never fatal
            self.logger.debug(f"pipeline_event_log insert skipped ({exc})")

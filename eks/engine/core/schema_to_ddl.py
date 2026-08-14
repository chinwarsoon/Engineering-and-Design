"""
Schema-to-DDL for EKS - Auto-generate SQL DDL from JSON schema definitions.
T1.36: Replaces hard-coded DDL in registry.py with schema-driven generation.

Revision: 1.4
Date: 2026-08-12
Author: opencode
Summary: 1.4: I310 (T1.292/T1.296) — exclude schema-def DDL tables,
          exclude self-referencing physical FKs, and reference registered
          DB-layer error codes.
1.3: I310 (T1.292) — added all-table DB config rendering, selective
          physical FK eligibility, and reserved-identifier quoting.
1.2: I307 (T1.279) — re-homed the 7 runtime-table DDL generators
          (batch_run, health_score, health_batch, document_reference,
          pipeline_checkpoint, pipeline_event_log, export_artifact) from
          hardcoded column literals into eks_db_config.json. Added
          load_db_config() + _render_table_from_config() so the generators
          emit DDL from the schema-driven config (single column source for
          all 53 tables; no code/config split). Physical FKs and JSON
          columns are declared in eks_db_config.json foreign_keys[]/columns[]
          and rendered when present.
1.1: T1.256/T1.257/T1.258 (I293/I294/I295) — added runtime-table DDL
          generators generate_batch_run_ddl(), generate_health_score_ddl(),
          generate_health_batch_ddl(), generate_document_reference_ddl()
          (GROUP 11 pipeline-execution tables).
1.0: T1.254 (I291) — generate_document_elements_ddl() emits `id VARCHAR PRIMARY
          KEY` + `created_at TIMESTAMP NOT NULL DEFAULT now()` (+ optional element_seq);
          generate_migration_ddl() skips the id PK (DuckDB cannot ALTER-add a PK) but
          adds `created_at TIMESTAMP NOT NULL DEFAULT now()`.
"""
import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from ..logging.logger import EKSLogger, log_depth


JSON_TO_SQL_TYPE_MAP = {
    "string": "VARCHAR",
    "boolean": "BOOLEAN",
    "integer": "INTEGER",
    "number": "DOUBLE",
    "array": "JSON",
    "object": "JSON",
}

SQLITE_DEFAULT_MAP = {
    "VARCHAR": "'{default}'",
    "BOOLEAN": "{default}",
    "INTEGER": "{default}",
    "DOUBLE": "{default}",
    "JSON": "'{default}'",
}

# I310/T1.296: registered DB-layer error codes (eks_error_config.json v1.8.0).
ERR_DB_TABLE_SPEC = "S-C-S-0309"        # system — invalid table spec
ERR_DB_FK_SPEC = "S-C-S-0310"           # system — invalid FK spec
ERR_DB_MATERIALIZATION = "S-R-S-0411"   # system — DDL materialization failed
# I308/T1.282: registered view-config error code.
ERR_VIEW_CONFIG = "S-C-S-0312"          # system — export view config missing/unreadable

# I312/T1.303: SSOT set of always-nullable project-metadata columns. Used by both
# the DDL generators and the migration gate's I196 NOT NULL advisory check so the
# two never diverge (AGENTS.md §10 SSOT). Last synced from I196 (T1.99.164).
ALWAYS_NULLABLE_COLUMNS = frozenset(
    {"project_title", "project_number", "area", "discipline", "department", "project_code"}
)


class SchemaToDDL:
    """
    Generates SQL DDL (CREATE TABLE, ALTER TABLE) from JSON schema definitions.
    Reads document_metadata_def, project_metadata_def, document_element_def
    from eks_doc_base_schema.json.
    """

    def __init__(self, doc_base_schema: Dict[str, Any], logger: Optional[EKSLogger] = None,
                 db_config: Optional[Dict[str, Any]] = None):
        self.schema = doc_base_schema
        self.definitions = doc_base_schema.get("definitions", {})
        self.logger = logger or EKSLogger("SchemaToDDL", level=2)
        # I307 (T1.279): schema-driven runtime-table column source. If not supplied,
        # lazily loaded by load_db_config() on first runtime-table DDL call.
        self.db_config = db_config
        self._db_config_dir: Optional[Path] = None

    @log_depth
    def generate_documents_ddl(self) -> str:
        """
        Generate CREATE TABLE DDL for the documents table by merging
        project_metadata_def and document_metadata_def properties.
        The 'id' column is always PRIMARY KEY (document identifier).
        Project metadata fields (project_title, project_number) are always
        nullable for backward compatibility — documents can be registered
        before project metadata is known.
        """
        self.logger.status("Generating documents table DDL from schema definitions")

        project_props = self.definitions.get("project_metadata_def", {}).get("properties", {})
        document_props = self.definitions.get("document_metadata_def", {}).get("properties", {})

        all_props = {}
        all_props.update(project_props)
        all_props.update(document_props)

        required_fields = set()
        for def_name in ["project_metadata_def", "document_metadata_def"]:
            req = self.definitions.get(def_name, {}).get("required", [])
            required_fields.update(req)

        always_nullable = ALWAYS_NULLABLE_COLUMNS

        # T1.99.150 (I186): id is a UUID (stored as VARCHAR in DuckDB, system-generated)
        columns = ["id VARCHAR PRIMARY KEY"]
        for col_name, col_schema in all_props.items():
            effective_required = required_fields - always_nullable
            col_def = self._resolve_column(col_name, col_schema, effective_required)
            columns.append(col_def)

        col_lines = ",\n                ".join(columns)
        ddl = f"""
            CREATE TABLE IF NOT EXISTS documents (
                {col_lines}
            )"""
        return ddl

    @log_depth
    def generate_document_elements_ddl(self) -> str:
        """
        Generate CREATE TABLE DDL for the document_elements table from
        document_element_def.
        I291 (T1.254): id UUID PRIMARY KEY + created_at TIMESTAMP NOT NULL
        DEFAULT now() (+ optional element_seq) via a schema-driven ruleset.
        """
        self.logger.status("Generating document_elements table DDL from schema definition")

        el_def = self.definitions.get("document_element_def", {})
        props = el_def.get("properties", {})
        required_fields = set(el_def.get("required", []))

        columns = ["id VARCHAR PRIMARY KEY"]
        for col_name, col_schema in props.items():
            if col_name == "id":
                continue  # PK already emitted above (surrogate UUID)
            if col_name == "created_at":
                # I291 (T1.254): runtime timestamp, schema format date-time.
                columns.append("created_at TIMESTAMP NOT NULL DEFAULT now()")
                continue
            col_def = self._resolve_column(col_name, col_schema, required_fields)
            columns.append(col_def)

        col_lines = ",\n                ".join(columns)
        ddl = f"""
            CREATE TABLE IF NOT EXISTS document_elements (
                {col_lines}
            )"""
        return ddl

    @log_depth
    def generate_batch_run_ddl(self) -> str:
        """
        Generate CREATE TABLE DDL for the runtime `batch_run` table (GROUP 11).

        I293 (T1.256): pipeline-execution table — one row per run. Column set
        covers the 6 definition-layer columns plus the 8 stage-statistics
        columns (job_id, data_dir, current_stage, phase_a_discovered,
        phase_a_valid, phase_b_total, phase_b_success, phase_b_failed,
        phase_c_flagged). Runtime-generated (no base-schema definition).

        I307 (T1.279): column definitions re-homed from this hardcoded string
        into eks_db_config.json — the renderer emits DDL from config (single
        column source, no code/config split).
        """
        return self._render_table_from_config("batch_run")

    @log_depth
    def generate_health_score_ddl(self) -> str:
        """
        Generate CREATE TABLE DDL for the runtime `health_score` table (GROUP 8/11).

        I294 (T1.257): per-document health result, one row per doc per run.
        `document_id` is the registry UUID (declared_only FK → documents.id,
        enforced at validation layer — no physical FK DDL per I290 precedent).

        I307 (T1.279): column definitions re-homed from hardcoded string into
        eks_db_config.json; rendered from config.
        """
        return self._render_table_from_config("health_score")

    @log_depth
    def generate_health_batch_ddl(self) -> str:
        """
        Generate CREATE TABLE DDL for the runtime `health_batch` table (GROUP 8/11).

        I294 (T1.257): per-run aggregate produced by ``HealthScorer.score_batch()``.
        I307 (T1.279): column definitions re-homed from hardcoded string into
        eks_db_config.json; rendered from config.
        """
        return self._render_table_from_config("health_batch")

    @log_depth
    def generate_document_reference_ddl(self) -> str:
        """
        Generate CREATE TABLE DDL for the runtime `document_reference` junction
        (GROUP 11).

        I295 (T1.258): M:N relationships between registry documents. Both
        endpoints are declared_only FKs → documents.id (validation-layer
        enforcement; no physical FK DDL per I290 precedent).

        I307 (T1.279): column definitions re-homed from hardcoded string into
        eks_db_config.json; rendered from config.
        """
        return self._render_table_from_config("document_reference")

    @log_depth
    def generate_pipeline_checkpoint_ddl(self) -> str:
        """
        Generate CREATE TABLE DDL for the runtime `pipeline_checkpoint` table
        (GROUP 12).

        I298 (T1.261): persists pipeline phase-state snapshots for restore/audit
        alongside filesystem JSON. job_id + phase is the natural unique key.
        I307 (T1.279): column definitions re-homed from hardcoded string into
        eks_db_config.json; rendered from config.
        """
        return self._render_table_from_config("pipeline_checkpoint")

    @log_depth
    def generate_pipeline_event_log_ddl(self) -> str:
        """
        Generate CREATE TABLE DDL for the runtime `pipeline_event_log` table
        (GROUP 12).

        I299 (T1.262): structured event/debug log for cross-run querying
        (replaces filesystem-only debug_log.json).
        I307 (T1.279): column definitions re-homed from hardcoded string into
        eks_db_config.json; rendered from config.
        """
        return self._render_table_from_config("pipeline_event_log")

    @log_depth
    def generate_export_artifact_ddl(self) -> str:
        """
        Generate CREATE TABLE DDL for the runtime `export_artifact` table
        (GROUP 12).

        I301 (T1.264): tracks pipeline export artifacts (CSV/XLSX) linking
        jobs to output files.
        I307 (T1.279): column definitions re-homed from hardcoded string into
        eks_db_config.json; rendered from config.
        """
        return self._render_table_from_config("export_artifact")

    @staticmethod
    def load_db_config(config_dir: Optional[Path] = None) -> Dict[str, Any]:
        """Load eks_db_config.json from the schemas directory.

        I307 (T1.277/T1.279): the schema-driven DB-layer table config is the
        single source of column definitions for all 53 tables. Search order:
        config_dir/schemas/eks_db_config.json, then config_dir/eks_db_config.json,
        then the standard eks config/schemas/ layout relative to this module.
        """
        candidates = []
        if config_dir is not None:
            candidates += [Path(config_dir) / "schemas" / "eks_db_config.json",
                           Path(config_dir) / "eks_db_config.json"]
        # Module-relative fallback: eks/engine/core/schema_to_ddl.py -> eks/config/schemas/
        module_dir = Path(__file__).resolve()
        candidates.append(module_dir.parent.parent.parent / "config" / "schemas" / "eks_db_config.json")
        candidates.append(module_dir.parent.parent.parent / "config" / "eks_db_config.json")
        for path in candidates:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
        raise FileNotFoundError(
            "eks_db_config.json not found. Searched: "
            + "; ".join(str(c) for c in candidates)
            + " — the schema-driven DB-layer config is required since I307 (T1.279)."
        )

    @staticmethod
    def load_view_config(config_dir: Optional[Path] = None) -> Dict[str, Any]:
        """Load eks_export_view_config.json from the schemas directory.

        I308 (T1.282): the schema-driven export-view config is the single source
        of view definitions (view_id, source_table, filter, columns). Search order
        mirrors load_db_config(): config_dir/schemas/, config_dir/, then the
        standard eks config/schemas/ layout relative to this module.

        Raises:
            FileNotFoundError: if the config cannot be located anywhere.
        """
        candidates = []
        if config_dir is not None:
            candidates += [Path(config_dir) / "schemas" / "eks_export_view_config.json",
                           Path(config_dir) / "eks_export_view_config.json"]
        module_dir = Path(__file__).resolve()
        candidates.append(module_dir.parent.parent.parent / "config" / "schemas" / "eks_export_view_config.json")
        candidates.append(module_dir.parent.parent.parent / "config" / "eks_export_view_config.json")
        for path in candidates:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
        raise FileNotFoundError(
            "eks_export_view_config.json not found. Searched: "
            + "; ".join(str(c) for c in candidates)
            + " — the schema-driven export-view config is required since I308 (T1.282)."
        )

    def _get_db_config(self) -> Dict[str, Any]:
        """Return the loaded eks_db_config.json, lazily loading if needed."""
        if self.db_config is None:
            self.db_config = self.load_db_config(self._db_config_dir)
        return self.db_config

    def _render_table_from_config(
        self, table_name: str, include_fk: bool | set[str] = False
    ) -> str:
        """Render CREATE TABLE DDL for a table spec from eks_db_config.json.

        I307 (T1.279): emits `CREATE TABLE IF NOT EXISTS {name}` with columns
        (name + DuckDB type + NOT NULL + UNIQUE + PRIMARY KEY + DEFAULT). The
        surrogate `id` column carries the PRIMARY KEY marker.

        Physical FK constraints are declared in eks_db_config.json foreign_keys[]
        (I306 Q1) but emitted only when ``include_fk`` is True — the current
        runtime registry (11 tables) does not yet materialize every FK target,
        so FK DDL emission is deferred to I310/T1.292 (full 53-table renderer).
        DuckDB supports only NO ACTION / RESTRICT for ON DELETE.
        """
        cfg = self._get_db_config()
        tables = cfg.get("db_tables", [])
        spec = next((t for t in tables if t.get("table_name") == table_name), None)
        if spec is None:
            raise KeyError(
                f"[{ERR_DB_TABLE_SPEC}] table '{table_name}' not declared in "
                f"eks_db_config.json db_tables[] — cannot render DDL (I307/T1.279)."
            )
        cols = spec.get("columns", [])
        if not cols:
            raise ValueError(
                f"[{ERR_DB_TABLE_SPEC}] table '{table_name}' has no columns "
                "in eks_db_config.json."
            )

        lines = []
        for c in cols:
            parts = [self._quote_identifier(c["name"]), c["column_type"]]
            if c.get("is_primary"):
                parts.append("PRIMARY KEY")
            if c.get("unique"):
                parts.append("UNIQUE")
            if c.get("nullable") is False:
                parts.append("NOT NULL")
            if c.get("default") is not None:
                default = c["default"]
                if c["column_type"] == "BOOLEAN":
                    parts.append(f"DEFAULT {'TRUE' if default else 'FALSE'}")
                elif c["column_type"] in ("INTEGER", "DOUBLE"):
                    parts.append(f"DEFAULT {default}")
                elif c["column_type"] == "TIMESTAMP" and str(default).lower() == "now()":
                    # DuckDB keyword default — emitted unquoted.
                    parts.append("DEFAULT now()")
                else:
                    parts.append(f"DEFAULT '{default}'")
            lines.append("    " + " ".join(parts))

        if include_fk:
            for fk_spec in spec.get("foreign_keys", []):
                if isinstance(include_fk, set) and fk_spec.get("fk_name") not in include_fk:
                    continue
                fk_clause = (
                    "    CONSTRAINT {fk} FOREIGN KEY ({col}) REFERENCES {tbl}({tcol})"
                    .format(
                        fk=self._quote_identifier(fk_spec["fk_name"]),
                        col=self._quote_identifier(fk_spec["column"]),
                        tbl=self._quote_identifier(fk_spec["target_table"]),
                        tcol=self._quote_identifier(fk_spec["target_column"]),
                    )
                )
                if fk_spec.get("on_delete"):
                    fk_clause += f" ON DELETE {fk_spec['on_delete']}"
                lines.append(fk_clause)

        col_lines = ",\n".join(lines)
        return f"CREATE TABLE IF NOT EXISTS {self._quote_identifier(table_name)} (\n{col_lines}\n)"

    @staticmethod
    def _quote_identifier(identifier: str) -> str:
        """Quote a DuckDB identifier supplied by schema configuration."""
        if identifier.lower() not in {"symmetric"}:
            return identifier
        return '"' + identifier.replace('"', '""') + '"'

    def generate_db_tables_ddl(
        self,
        physical_fk_tables: Optional[set[str]] = None,
        exclude_tables: Optional[set[str]] = None,
    ) -> List[str]:
        """Render DDL for every table declared in ``eks_db_config.json``.

        I310/T1.292: the DB configuration is the single source for table DDL.
        Physical foreign keys are emitted only when their target column is
        primary or unique in the same configuration and the target is a
        runtime (direct-map) table; self-referencing links and definition
        targets are retained for the post-load relationship validator.
        ``exclude_tables`` omits schema-def DDL tables (documents,
        document_elements) that keep their own generated shape.
        """
        config = self._get_db_config()
        table_specs = config.get("db_tables", [])
        table_names = {spec.get("table_name") for spec in table_specs}
        direct_map_tables = {
            spec.get("table_name")
            for spec in table_specs
            if spec.get("transform") == "direct-map"
        }
        unique_targets = {
            (spec.get("table_name"), column.get("name"))
            for spec in table_specs
            for column in spec.get("columns", [])
            if column.get("is_primary") or column.get("unique")
        }
        ddl_statements = []
        for spec in table_specs:
            table_name = spec.get("table_name")
            if not table_name:
                raise ValueError(
                    f"[{ERR_DB_TABLE_SPEC}] DB table specification is missing "
                    "table_name (I310/T1.292)."
                )
            if table_name not in table_names:
                raise ValueError(
                    f"[{ERR_DB_TABLE_SPEC}] Unknown DB table specification: "
                    f"{table_name} (I310/T1.292)."
                )
            if exclude_tables and table_name in exclude_tables:
                continue
            physical_fks = {
                fk.get("fk_name")
                for fk in spec.get("foreign_keys", [])
                if fk.get("target_table") in table_names
                and fk.get("target_table") in direct_map_tables
                and fk.get("target_table") != table_name
                and (fk.get("target_table"), fk.get("target_column")) in unique_targets
            }
            if physical_fk_tables is not None and table_name not in physical_fk_tables:
                physical_fks = set()
            ddl_statements.append(
                self._render_table_from_config(table_name, include_fk=physical_fks)
            )
        return ddl_statements

    @log_depth
    def generate_view_ddl(
        self,
        view_config: Optional[Dict[str, Any]] = None,
        config_dir: Optional[Path] = None,
    ) -> List[str]:
        """Render persistent CREATE OR REPLACE VIEW DDL from the view config SSOT.

        I308 (T1.283): each views[] entry in eks_export_view_config.json becomes
        a persistent DuckDB view named ``v_<view_id>``. The SELECT list is the
        entry's ordered ``columns[]`` and the optional ``filter`` (column/value)
        is rendered as a WHERE clause (e.g. is_latest = TRUE) so only the latest
        document revision flows into exports. Views are created with
        CREATE OR REPLACE VIEW so re-initialization is idempotent.

        Args:
            view_config: Optional pre-loaded view config dict. If omitted, it is
                         loaded via load_view_config(config_dir).
            config_dir:  Optional config dir used to locate the view config.

        Returns:
            List of CREATE OR REPLACE VIEW statements (one per view).

        Raises:
            RuntimeError: FAIL_FAST [S-C-S-0312] if the config is missing,
                          unreadable, or a view entry is malformed.
        """
        if view_config is None:
            try:
                view_config = self.load_view_config(config_dir)
            except FileNotFoundError as exc:
                raise RuntimeError(
                    f"FAIL_FAST [{ERR_VIEW_CONFIG}]: export view config not found — {exc}"
                ) from exc

        views = view_config.get("views")
        if not isinstance(views, list) or not views:
            raise RuntimeError(
                f"FAIL_FAST [{ERR_VIEW_CONFIG}]: export view config has no views[] entries"
            )

        stmts = []
        for view in views:
            view_id = view.get("view_id")
            source_table = view.get("source_table")
            columns = view.get("columns")
            if not view_id or not source_table or not isinstance(columns, list) or not columns:
                raise RuntimeError(
                    f"FAIL_FAST [{ERR_VIEW_CONFIG}]: malformed view entry — "
                    f"view_id/source_table/columns[] required: {view}"
                )
            col_list = ", ".join(self._quote_identifier(c) for c in columns)
            where_clause = ""
            filt = view.get("filter")
            if filt:
                fcol = filt.get("column")
                fval = filt.get("value")
                if not fcol:
                    raise RuntimeError(
                        f"FAIL_FAST [{ERR_VIEW_CONFIG}]: view '{view_id}' filter "
                        "missing 'column'"
                    )
                if isinstance(fval, bool):
                    fval_sql = "TRUE" if fval else "FALSE"
                elif isinstance(fval, (int, float)):
                    fval_sql = str(fval)
                else:
                    fval_sql = "'" + str(fval).replace("'", "''") + "'"
                where_clause = f" WHERE {self._quote_identifier(fcol)} = {fval_sql}"
            stmts.append(
                f"CREATE OR REPLACE VIEW v_{view_id} AS "
                f"SELECT {col_list} FROM {self._quote_identifier(source_table)}{where_clause}"
            )
        return stmts

    @log_depth
    def generate_indexes(self) -> List[str]:
        """Generate index creation statements for documents and document_elements."""
        # T1.99.150 (I186): Composite index on business key for fast lookup
        # since id is now UUID and (document_number, revision) is no longer unique.
        return [
            "CREATE INDEX IF NOT EXISTS idx_doc_business_key ON documents(document_number, revision)",
            "CREATE INDEX IF NOT EXISTS idx_elements_doc_id ON document_elements(doc_id)",
            "CREATE INDEX IF NOT EXISTS idx_elements_type ON document_elements(element_type)",
        ]

    @log_depth
    def registry_relations(self) -> List[Dict[str, Any]]:
        """
        Return the schema-declared FK relationships for the runtime `documents`
        registry (GROUP 11).

        I290 (T1.253): FK relationships are declared as schema metadata in
        eks_doc_base_schema.json#/registry_relations (SSOT, AGENTS.md §16).
        Runtime ENTITY does NOT emit physical DuckDB FOREIGN KEY constraints:
          (a) definition-layer targets (project_doc_type, discipline, file_type,
              project_definition) are not materialized in the runtime registry DB —
              DuckDB rejects FK DDL referencing a missing table;
          (b) self-FKs (supersedes/superseded_by) would block PK UPDATEs performed
              by _migrate_ids_to_uuid (DuckDB reports the referenced key still
              referenced by a FK in the same session).
        Referential integrity is enforced by the validation layer instead.
        """
        relations = self.schema.get("registry_relations", [])
        return relations or []

    @log_depth
    def generate_relations_manifest_ddl(self) -> List[str]:
        """
        Generate the `_eks_table_relations` manifest table (one row per declared
        FK relationship) plus its INSERT statements.

        I290 (T1.253): the manifest makes the schema-declared relationships
        queryable at runtime (which FKs exist, their candidate-key shape, and
        whether they are declared-only), and mirrors ``registry_relations``
        exactly so the docs and the DB cannot drift.

        I311 (T1.297): the manifest table shape is rendered from
        ``eks_db_config.json`` (SSOT) so `id` is the PRIMARY KEY and
        ``relation_name`` is UNIQUE — matching the I307 schema-driven config
        instead of the legacy I290 ``relation_name``-primary shape. Every
        manifest row's `id` is derived with the config ``id_strategy``
        (uuid5 of the namespace + natural key), mirroring DefinitionLoader.
        """
        relations = self.registry_relations()
        if not relations:
            return []
        stmts = [
            self._render_table_from_config("_eks_table_relations", include_fk=False)
        ]
        import json as _json

        def _sql(strlit):
            return "'" + str(strlit).replace("'", "''") + "'"

        # I311: id derived exactly like DefinitionLoader (uuid5 namespace +
        # natural-key join) so the config id_strategy is the single source.
        cfg = self._get_db_config()
        spec = next(
            (t for t in cfg.get("db_tables", [])
             if t.get("table_name") == "_eks_table_relations"),
            {},
        )
        strategy = spec.get("id_strategy", {}) or {}
        ns = uuid.uuid5(
            uuid.NAMESPACE_URL,
            strategy.get("namespace", "eks:_eks_table_relations"),
        )
        natural_keys = strategy.get("natural_key_columns") or ["relation_name"]

        for rel in relations:
            natural = "|".join(
                str(rel.get(name, "")) for name in natural_keys
            )
            row_id = str(uuid.uuid5(ns, natural))
            columns = [
                "id", "relation_name", "source_table", "source_columns",
                "target_table", "target_columns", "relation_type",
                "declared_only", "description",
            ]
            values = [
                _sql(row_id),
                _sql(rel.get("relation_name")),
                _sql(rel.get("source_table", "documents")),
                _sql(_json.dumps(rel.get("source_columns", []))),
                _sql(rel.get("target_table")),
                _sql(_json.dumps(rel.get("target_columns", []))),
                _sql(rel.get("relation_type", "simple")),
                "TRUE" if rel.get("declared_only", True) else "FALSE",
                _sql(rel.get("description", "")),
            ]
            # I311: id PK + relation_name UNIQUE make `INSERT OR REPLACE`
            # ambiguous in DuckDB — an explicit conflict target is required.
            update_cols = ", ".join(
                f"{col} = EXCLUDED.{col}" for col in columns[1:]
            )
            stmts.append(
                "INSERT INTO _eks_table_relations "
                f"({', '.join(columns)}) VALUES ({', '.join(values)}) "
                f"ON CONFLICT (id) DO UPDATE SET {update_cols}"
            )
        return stmts

    @log_depth
    def generate_migration_ddl(self, table_name: str, existing_columns: set) -> List[str]:
        """
        Generate ALTER TABLE ADD COLUMN statements for columns that exist
        in the schema but are missing from the database.
        """
        self.logger.info(f"Checking schema drift for table '{table_name}'")

        if table_name == "documents":
            project_props = self.definitions.get("project_metadata_def", {}).get("properties", {})
            document_props = self.definitions.get("document_metadata_def", {}).get("properties", {})
            all_props = {}
            all_props.update(project_props)
            all_props.update(document_props)
            required_fields = set()
            for def_name in ["project_metadata_def", "document_metadata_def"]:
                req = self.definitions.get(def_name, {}).get("required", [])
                required_fields.update(req)
            # T1.99.164 (I196): Apply always_nullable override for migration DDL
            # — matches generate_documents_ddl() behavior so that columns added
            # via ALTER TABLE get the same nullability as columns created via
            # CREATE TABLE. SSOT = ALWAYS_NULLABLE_COLUMNS (I312/T1.303).
            required_fields = required_fields - ALWAYS_NULLABLE_COLUMNS
        elif table_name == "document_elements":
            el_def = self.definitions.get("document_element_def", {})
            all_props = el_def.get("properties", {})
            required_fields = set(el_def.get("required", []))
        else:
            return []

        stmts = []
        for col_name, col_schema in all_props.items():
            if col_name not in existing_columns:
                if col_name == "id":
                    # I291 (T1.254): id is the surrogate UUID PK — a DuckDB
                    # ALTER TABLE ADD COLUMN cannot add a PRIMARY KEY constraint
                    # to a populated table; existing rows get it only on
                    # re-CREATE. Skip for migration (PK is create-time only).
                    continue
                if col_name == "created_at":
                    # I291 (T1.254): match CREATE-TABLE nullability/default.
                    stmts.append(
                        "ALTER TABLE document_elements ADD COLUMN "
                        "created_at TIMESTAMP NOT NULL DEFAULT now()"
                    )
                    continue
                col_def = self._resolve_column(col_name, col_schema, required_fields)
                stmts.append(f"ALTER TABLE {table_name} ADD COLUMN {col_def}")
                self.logger.info(f"Migration: Adding column '{col_name}' to {table_name}")

        return stmts

    def _resolve_column(self, col_name: str, col_schema: Dict[str, Any],
                        required_fields: set) -> str:
        """
        Resolve a JSON schema property to a SQL column definition string.
        Handles $ref resolution, type mapping, defaults, nullability,
        and format-based type overrides (e.g., date-time → TIMESTAMP).
        """
        resolved = self._resolve_ref(col_schema)
        json_type = resolved.get("type", "string")
        if isinstance(json_type, list):
            # I308/T1.283: multi-type unions (e.g. ["string", "null"]) —
            # take the first non-null member for the SQL type mapping.
            json_type = next((t for t in json_type if t != "null"), "string")
        fmt = resolved.get("format", "")

        if fmt == "date-time":
            sql_type = "TIMESTAMP"
        elif json_type == "string" and col_name == "ingested_at":
            sql_type = "TIMESTAMP"
        else:
            sql_type = JSON_TO_SQL_TYPE_MAP.get(json_type, "VARCHAR")

        parts = [col_name, sql_type]

        if col_name == "ingested_at" and sql_type == "TIMESTAMP":
            parts.append("DEFAULT CURRENT_TIMESTAMP")
        else:
            default = resolved.get("default")
            if default is not None:
                if sql_type == "BOOLEAN":
                    sql_val = "TRUE" if default else "FALSE"
                    parts.append(f"DEFAULT {sql_val}")
                elif sql_type in ("INTEGER", "DOUBLE"):
                    parts.append(f"DEFAULT {default}")
                else:
                    parts.append(f"DEFAULT '{default}'")

        # DuckDB: columns are NULL by default — only emit NOT NULL constraints
        if col_name in required_fields:
            parts.append("NOT NULL")

        return " ".join(parts)

    def _resolve_ref(self, schema_fragment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve $ref references in a schema fragment. Follows one level of
        $ref to extract type, default, and enum information.
        """
        if "$ref" in schema_fragment:
            ref_path = schema_fragment["$ref"]
            ref_def = self._lookup_ref(ref_path)
            if ref_def:
                return ref_def
        return schema_fragment

    def _lookup_ref(self, ref_path: str) -> Optional[Dict[str, Any]]:
        """
        Look up a $ref path (e.g., '#/definitions/document_type_code' or
        'eks_doc_base_schema.json#/definitions/file_type_code').
        """
        if ref_path.startswith("#/definitions/"):
            def_name = ref_path.split("/")[-1]
            return self.definitions.get(def_name)
        elif "#/definitions/" in ref_path:
            def_name = ref_path.split("/")[-1]
            return self.definitions.get(def_name)
        return None

    @staticmethod
    def load_doc_base_schema(config_dir: Path) -> Dict[str, Any]:
        """Load eks_doc_base_schema.json from config_dir/schemas/ or config_dir/."""
        schema_path = config_dir / "schemas" / "eks_doc_base_schema.json"
        if not schema_path.exists():
            schema_path = config_dir / "eks_doc_base_schema.json"
        if not schema_path.exists():
            raise FileNotFoundError(
                f"eks_doc_base_schema.json not found in {config_dir} or its schemas/ subdirectory"
            )
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)


def generate_all_ddl(config_dir: Path) -> Tuple[str, str, List[str]]:
    """
    Convenience function: load schema and generate all DDL.
    Returns (documents_ddl, document_elements_ddl, index_statements).
    """
    schema = SchemaToDDL.load_doc_base_schema(config_dir)
    gen = SchemaToDDL(schema)
    docs_ddl = gen.generate_documents_ddl()
    els_ddl = gen.generate_document_elements_ddl()
    indexes = gen.generate_indexes()
    return docs_ddl, els_ddl, indexes

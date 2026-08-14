"""
Document Registry for EKS - Metadata DB CRUD interface using DuckDB.
DDL is auto-generated from JSON schema definitions via SchemaToDDL (T1.36).

Revision: 1.7
Date: 2026-08-14
Author: opencode
Summary: 1.7: I312 (T1.301–T1.303) — retired _ensure_schema_version() and
          _migrate_schema(); added _refresh_manifest() which writes the
          schema-driven db_manifest provenance table (replaces _eks_schema_meta).
          I196 NOT NULL advisory check ported into migration_gate.py (SOFT warn);
          gate skips structural validation on db_manifest (metadata table).
1.6: I308 (T1.283) — persistent v_* export views now created by
          _create_export_views() AFTER _run_migration_gate() so additive
          migrations (e.g. flag_reason on a stale registry) are applied
          before the views referencing them are created.
1.5: I311 (T1.297) — migration gate replaces the silent
          _migrate_schema() call; added migration_policy/migration_mode/
          migration_archive_dir constructor params + _run_migration_gate().
1.4: I310 (T1.296) â€” _eks_table_relations keeps legacy manifest
          shape (relation_name PK) for I290 population.
1.3: I310 (T1.294/T1.296) â€” documents/document_elements keep
          schema-def DDL; health CRUD preserves runtime batch references.
1.2: I310 (T1.292â€“T1.295) â€” materialize all configured tables,
          load definition data through DefinitionLoader, and validate
          relationships after loading.
1.1: T1.256/T1.257/T1.258 (I293/I294/I295) â€” added GROUP 11 runtime
          table CRUD: insert_batch()/update_batch()/get_batch() (batch_run stage
          stats); store_health_score()/store_health_batch()/get_health_scores()
          (health_score/health_batch with document_id UUID); store_document_reference()/
          list_document_references()/delete_document_references()/get_document_by_id()
          (document_reference junction). _init_db() now creates the 4 runtime tables.
1.0: T1.254 (I291) â€” store_elements() now injects surrogate UUID `id`, validates
          element_type against the 11-code enum (ValueError otherwise) via new cached
          _element_type_codes(), and validates doc_id existence (declared_only
          fk_element_doc enforcement); _element_type_codes() reads valid codes from the
          schema-driven element_type registry.
0.9: T1.200/T1.201 (I274) -- removed hardcoded COLUMN_ALLOWLIST fallback;
          _get_column_allowlist() now resolves doc base schema via schema-driven
          paths (CWD-independent) and raises a descriptive error on absence.
0.8: T1.99.191 (I225) â€” added pre_generated_ddl param to reuse bootstrap
          DDL; _ensure_schema_version() retired in I312 (T1.303) — db_manifest now holds provenance.
0.7: T1.106 (I232) â€” added get_document_by_file_path() for SSOT doc_id lookup.
          0.6: T1.99.153 (I189/F1) â€” added optional db_path parameter for test-isolated databases.
         0.5: T1.99.148 (I187) â€” migrated synthetic key generation to common.library.utility.synthetic_key.
          Removed ad-hoc hashlib usage for key generation.
          T1.99.150 (I186) â€” changed id from business-key to pure UUID, INSERT OR REPLACE â†’ INSERT.
          T1.99.152 (I184) â€” added diff logging to update_document_status().
          Prior: T1.99.141â€“T1.99.146 â€” document metadata completeness.
"""
import duckdb
import hashlib
import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from common.library.utility.synthetic_key import generate_synthetic_key
from common.library.utility.change_detector import detect_changes
from common.library.utility.file_hash import compute_file_hash
from .config_registry import ConfigRegistry
from .schema_to_ddl import SchemaToDDL
from .definition_loader import DefinitionLoader
from .flag_utils import compute_flag_reason
from ..logging.logger import EKSLogger, log_depth

class DocumentRegistry:
    """
    Manages document metadata storage and retrieval.
    Backed by DuckDB (or PostgreSQL if configured).
    DDL is auto-generated from JSON schema definitions via SchemaToDDL (T1.36).
    """

    _SCHEMA_DERIVED_ALLOWLIST: Optional[set] = None

    # T1.99.165 (I196): SSOT fallback â€” the authoritative source is
    # eks_doc_config.json â†’ document_title_config â†’ boilerplate_prefixes.
    # This constant is used only when that config cannot be loaded.
    _BOILERPLATE_PREFIXES_FALLBACK = (
        "Microsoft Word", "AutoCAD Drawing", "Microsoft Excel"
    )

    @classmethod
    def _resolve_doc_base_config_dir(cls) -> Path:
        """Resolve the config dir holding ``eks_doc_base_schema.json`` from any CWD.

        T1.201 (I274): replaces the hardcoded ``Path("eks/config")`` literal.
        Resolution order (AGENTS.md Â§15 - no hardcoded path literals):
          1. The already-resolved ``SchemaLoader.config_dir`` from the
             ConfigRegistry singleton (bootstrap path - CWD-independent once
             bootstrapped).
          2. Anchor-based discovery: ``default_base_path`` locates the project
             root, then schema-driven ``resolve_paths()`` (global_paths) derives
             the config dir - works from any working directory.
        Raises a descriptive ``FileNotFoundError`` when the config dir cannot be
        resolved - there is NO silent fallback (AGENTS.md Â§16).
        """
        from .config_registry import ConfigRegistry
        from common.library.paths.root_discovery import default_base_path
        from common.library.paths import resolve_paths

        # Priority 1: already-resolved bootstrap config dir.
        loader = getattr(ConfigRegistry._instance, "_loader", None)
        if loader is not None and getattr(loader, "config_dir", None):
            cfg = Path(loader.config_dir)
            if (cfg / "schemas" / "eks_doc_base_schema.json").exists() or \
                    (cfg / "eks_doc_base_schema.json").exists():
                return cfg

        # Priority 2: anchor-based discovery + schema-driven global_paths.
        project_root = default_base_path("eks", reference=__file__)
        config = {}
        for candidate in (
            project_root / "eks" / "config" / "schemas" / "eks_config.json",
            project_root / "eks" / "config" / "eks_config.json",
            project_root / "config" / "eks_config.json",
        ):
            if candidate.exists():
                with open(candidate, "r", encoding="utf-8") as fh:
                    config = json.load(fh)
                break
        if not config.get("global_paths"):
            raise FileNotFoundError(
                "Could not resolve the EKS config dir: no eks_config.json with "
                "global_paths found under the anchor-discovered project root "
                f"{project_root}. Run from within the project tree or pass "
                "--base-path/--config-dir (I274/T1.201)."
            )
        resolved = resolve_paths(project_root, config).resolve(project_root)
        return Path(resolved["config_dir"])

    @classmethod
    def _get_column_allowlist(cls) -> set:
        """
        Derive COLUMN_ALLOWLIST from JSON schema definitions (sole source).

        T1.200 (I274): the schema-derived set is the ONLY source - no hardcoded
        fallback list. On genuine schema absence, a descriptive error is raised
        instead of silently degrading (AGENTS.md Â§16).
        """
        if cls._SCHEMA_DERIVED_ALLOWLIST is not None:
            return cls._SCHEMA_DERIVED_ALLOWLIST
        from .schema_to_ddl import SchemaToDDL
        config_dir = cls._resolve_doc_base_config_dir()
        schema = SchemaToDDL.load_doc_base_schema(config_dir)
        gen = SchemaToDDL(schema)
        project_props = gen.definitions.get("project_metadata_def", {}).get("properties", {})
        document_props = gen.definitions.get("document_metadata_def", {}).get("properties", {})
        all_cols = set(project_props.keys()) | set(document_props.keys())
        all_cols.add("id")
        cls._SCHEMA_DERIVED_ALLOWLIST = all_cols
        return all_cols

    @property
    def COLUMN_ALLOWLIST(self) -> set:
        return self._get_column_allowlist()

    # T1.99.152 (I184): Fields tracked for before/after diff on status update
    DIFF_TRACK_FIELDS: set = {
        "embedded_title", "page_count", "extraction_confidence",
        "file_hash", "document_title", "lifecycle_stage",
        "revision_description",
    }

    def __init__(self, logger: Optional[EKSLogger] = None, db_path: Optional[str] = None,
                 pre_generated_ddl: Optional[Dict[str, Any]] = None,
                 migration_policy: Optional[str] = None,
                 migration_mode: Optional[str] = None,
                 migration_archive_dir: Optional[str] = None):
        """
        Initialize the DocumentRegistry.

        Args:
            logger: Optional EKSLogger instance.
            db_path: Optional explicit database file path. When provided, used
                directly (bypassing config). Enables test-isolated databases
                (I189/F1).
            pre_generated_ddl: Optional pre-generated DDL from bootstrap P7
                SchemaToDDL pre-flight. When provided, schema-to-ddl loading
                is skipped and the pre-generated DDL is used directly for
                table creation and migration. Keys: documents_ddl, elements_ddl,
                indexes, definitions.
            migration_policy: Optional override for the I311 gate policy
                ('additive' non-destructive | 'destructive'). Defaults to the
                schema-driven ``system_parameters.migration_policy``.
            migration_mode: Optional I311 gate mode ('check' | 'apply' | 'force').
                'check' builds a plan only (callers short-circuit pre-construction);
                'apply' (= --db-apply/--yes) permits non-protected destructive;
                'force' (= --db-force) is the TOTAL override incl. protected
                tables (documents/document_elements) with a mandatory timestamped
                backup to output/archive/ before any destructive change.
            migration_archive_dir: Optional archive dir for the mandatory
                pre-destructive .db backup (default: <eks>/archive).
        """
        self.config = ConfigRegistry()
        self._migration_policy = migration_policy
        self._migration_mode = migration_mode
        self._migration_archive_dir = Path(migration_archive_dir) if migration_archive_dir else None
        if db_path is not None:
            self.db_path = Path(db_path)
        else:
            settings = self.config.registry_settings
            conn_str = settings.get("connection_string", "output/eks_registry.db")
            # Resolve relative paths relative to config directory
            loader = getattr(self.config, '_loader', None)
            if loader and hasattr(loader, 'config_dir'):
                config_dir = Path(loader.config_dir)
                self.db_path = (config_dir.parent / conn_str).resolve()
            else:
                self.db_path = Path(conn_str)
        self.retry_count = max(1, int(self.config.get_system_param("retry_count", 3)))
        self.retry_delay = float(self.config.get_system_param("retry_delay", 0.5))
        self.db_timeout = int(self.config.get_system_param("db_timeout", 30))
        self.logger = logger or EKSLogger("Registry", level=1)
        # T1.99.191 (I225): Store pre-generated DDL for schema-version tracking
        self._pre_generated_ddl = pre_generated_ddl
        # T1.256 (I293): cached SchemaToDDL for runtime GROUP 11 table DDL
        self._schema_to_ddl: Optional[SchemaToDDL] = None
        self._init_db()
        # I311 (T1.297): the schema-driven migration gate replaces the narrow
        # silent `_migrate_schema()` retired in I312/T1.303 (replaced by the migration gate).
        # it alongside `_eks_schema_meta`, T1.301â€“T1.303).
        self._run_migration_gate()
        # I308 (T1.283): persistent export views are created AFTER the migration
        # gate â€” a stale registry first gets additive columns (e.g. flag_reason)
        # so the v_* views never reference a column the gate still has to add.
        self._create_export_views()
        self._refresh_manifest()

    @log_depth
    def _init_db(self):
        """Initialize the metadata database tables with DDL auto-generated from JSON schema.
        
        T1.99.191 (I225): Uses pre-generated DDL from bootstrap if available,
        skipping schema re-loading from disk.
        """
        self.logger.status(f"Initializing Document Registry at {self.db_path}")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        if self._pre_generated_ddl:
            docs_ddl = self._pre_generated_ddl["documents_ddl"]
            els_ddl = self._pre_generated_ddl["elements_ddl"]
            indexes = self._pre_generated_ddl["indexes"]
            self.logger.info(
                "Using pre-generated DDL from bootstrap (I225)",
                context="DocumentRegistry._init_db",
            )
        else:
            loader = getattr(self.config, '_loader', None)
            if loader and hasattr(loader, 'doc_base_schema') and loader.doc_base_schema:
                schema_to_ddl = SchemaToDDL(loader.doc_base_schema, self.logger)
                docs_ddl = schema_to_ddl.generate_documents_ddl()
                els_ddl = schema_to_ddl.generate_document_elements_ddl()
                indexes = schema_to_ddl.generate_indexes()
            else:
                docs_ddl = SchemaToDDL(self._load_doc_schema()).generate_documents_ddl()
                els_ddl = SchemaToDDL(self._load_doc_schema()).generate_document_elements_ddl()
                indexes = SchemaToDDL(self._load_doc_schema()).generate_indexes()

        # T1.256/T1.257/T1.258 (I293/I294/I295): runtime GROUP 11 tables â€”
        # batch_run, health_score, health_batch, document_reference. These are
        # pipeline-execution tables with no base-schema definition; DDL is
        # generated by SchemaToDDL and created unconditionally (IF NOT EXISTS).
        sddl_from_cache = getattr(self, '_schema_to_ddl', None)
        if sddl_from_cache is None:
            loader = getattr(self.config, '_loader', None)
            if loader and hasattr(loader, 'doc_base_schema') and loader.doc_base_schema:
                sddl_from_cache = SchemaToDDL(loader.doc_base_schema, self.logger)
            else:
                sddl_from_cache = SchemaToDDL(self._load_doc_schema())
            self._schema_to_ddl = sddl_from_cache

        db_config = getattr(getattr(self.config, "_loader", None), "db_config", None)
        if not db_config:
            db_config = SchemaToDDL.load_db_config(
                Path(getattr(getattr(self.config, "_loader", None), "config_dir", ""))
            )
        schema_to_ddl = SchemaToDDL(
            getattr(getattr(self.config, "_loader", None), "doc_base_schema", {}),
            self.logger,
            db_config=db_config,
        )
        runtime_tables = {
            spec["table_name"]
            for spec in db_config.get("db_tables", [])
            if spec.get("transform") == "direct-map"
        }
        # I310/T1.294: documents/document_elements keep their schema-def DDL
        # shape (full merged metadata + lifecycle defaults) and are excluded
        # here. I311 (T1.297): _eks_table_relations is no longer excluded â€”
        # its manifest DDL is rendered from eks_db_config.json (SSOT) with an
        # `id` PRIMARY KEY, so config pre-creation governs its shape and the
        # migration gate sees no drift.
        db_ddls = schema_to_ddl.generate_db_tables_ddl(
            physical_fk_tables=runtime_tables,
            exclude_tables={"documents", "document_elements"},
        )

        conn = duckdb.connect(str(self.db_path))
        try:
            # Schema-def DDL first so documents/document_elements (and their
            # FKs) exist before config tables reference them (I310/T1.294).
            conn.execute(docs_ddl)
            conn.execute(els_ddl)
            for idx_stmt in indexes:
                conn.execute(idx_stmt)
            for table_ddl in db_ddls:
                conn.execute(table_ddl)
            # I310/T1.295: retain the relationship table as a derived audit.
            self._create_relations_manifest(conn)
            definition_loader = DefinitionLoader(
                db_config,
                getattr(getattr(self.config, "_loader", None), "config_dir", ""),
                self.logger,
            )
            definition_loader.load_all(conn)
            relationship_violations = definition_loader.validate_relationships(conn)
            if relationship_violations:
                self.logger.warning(
                    f"Definition relationship validation found "
                    f"{len(relationship_violations)} violations",
                    context="DocumentRegistry._init_db",
                )
        finally:
            conn.close()

    @log_depth
    def _create_export_views(self) -> None:
        """I308/T1.283: persist the v_* export views from the
        eks_export_view_config.json SSOT (is_latest=TRUE renders the WHERE clause).

        Runs after ``_run_migration_gate()`` so that additive migrations
        (e.g. ``flag_reason`` on a stale registry) are applied before the views
        referencing them are created. ``CREATE OR REPLACE VIEW`` keeps this
        idempotent across runs.
        """
        config_dir = Path(getattr(getattr(self.config, "_loader", None), "config_dir", ""))
        sddl = getattr(self, "_schema_to_ddl", None)
        if sddl is None:
            # Should not happen â€” _init_db() sets it â€” but keep a safe fallback.
            loader = getattr(self.config, "_loader", None)
            if loader and hasattr(loader, "doc_base_schema") and loader.doc_base_schema:
                sddl = SchemaToDDL(loader.doc_base_schema, self.logger)
            else:
                sddl = SchemaToDDL(self._load_doc_schema())
            self._schema_to_ddl = sddl
        try:
            view_ddls = sddl.generate_view_ddl(config_dir=config_dir)
        except Exception as exc:
            self.logger.error(
                f"Failed to generate export view DDL: {exc}",
                context="DocumentRegistry._create_export_views",
            )
            raise
        conn = duckdb.connect(str(self.db_path))
        try:
            for view_ddl in view_ddls:
                conn.execute(view_ddl)
            self.logger.info(
                f"Created {len(view_ddls)} persistent export views (I308)",
                context="DocumentRegistry._create_export_views",
            )
        except Exception as exc:
            self.logger.error(
                f"Failed to create export views: {exc}",
                context="DocumentRegistry._create_export_views",
            )
            raise
        finally:
            conn.close()

    @log_depth
    def _run_migration_gate(self) -> None:
        """Run the I311 schema-driven migration gate after ``_init_db()``.

        Reads the schema-driven ``system_parameters.migration_policy`` (with an
        explicit ``migration_policy`` constructor override taking precedence) and
        hands the DB over to :class:`MigrationGate`. Default policy (``additive``)
        auto-applies missing tables/columns; structural drift raises
        ``P1-R-P-0004`` unless a destructive override (``--db-apply``/``--db-force``)
        was transferred in via ``migration_mode``.
        """
        from .migration_gate import MigrationGate

        policy = self._migration_policy
        if not policy:
            try:
                policy = self.config.get_system_param("migration_policy", "additive")
            except Exception:  # nocv â€” config may not be bootstrapped yet
                policy = "additive"
        if policy not in ("additive", "destructive"):
            policy = "additive"
            self.logger.warning(
                "Invalid migration_policy in config â€” falling back to 'additive' "
                "(S-C-S-0311, I311/T1.297)",
                context="DocumentRegistry._run_migration_gate",
            )

        self._migration_gate = MigrationGate(
            db_path=self.db_path,
            config_dir=self._gate_config_dir(),
            logger=self.logger,
            policy=policy,
            mode=self._migration_mode,
            archive_dir=self._migration_archive_dir,
        )
        self._migration_plan = self._migration_gate.run(
            include_drift=(self._migration_mode == "check")
        )
        # I312/T1.303: capture gate-side validation outcomes (I196 NOT NULL etc.)
        # so the manifest can record them without re-running validation.
        self._last_gate_not_null = self._migration_plan.get("not_null_warnings", []) or []
        if self._migration_mode == "check":
            self.logger.status(
                self._migration_gate.render_report(self._migration_plan),
                context="DocumentRegistry._run_migration_gate",
            )

    @log_depth
    def _refresh_manifest(self) -> None:
        """I312/T1.302â€“T1.303: refresh the schema-driven ``db_manifest`` provenance table.

        Replaces the retired ``_ensure_schema_version()`` (and the retired
        ``_eks_schema_meta`` table). The manifest is a regenerated projection of
        the config SSOT (AGENTS.md Â§16); it is written transactionally with a
        retried UPSERT on the natural key. Gate validation outcomes (I196 NOT
        NULL warnings) are recorded into the manifest by the writer.
        """
        from .manifest import DBManifestWriter

        loader = getattr(self.config, "_loader", None)
        db_config = getattr(loader, "db_config", None) if loader else None
        if not db_config:
            self.logger.warning(
                "db_manifest refresh skipped â€” db_config not available",
                context="DocumentRegistry._refresh_manifest",
            )
            return
        config_dir = getattr(loader, "config_dir", None) if loader else None
        writer = DBManifestWriter(db_config, config_dir, self.logger)
        try:
            self._with_retry(
                lambda: writer.refresh(
                    self.db_path, validation={"not_null": self._last_gate_not_null}
                )
            )
        except Exception as exc:  # nocv â€” manifest is advisory, never fatal
            self.logger.warning(
                f"db_manifest refresh failed ({exc})",
                context="DocumentRegistry._refresh_manifest",
            )

    @log_depth
    def _gate_config_dir(self) -> str:
        """Resolve the config dir for the migration gate (bootstrap-first, SSOT)."""
        loader = getattr(self.config, '_loader', None)
        if loader is not None and getattr(loader, "config_dir", None):
            return str(Path(loader.config_dir))
        return str(self._resolve_doc_base_config_dir())

    @log_depth
    def _create_relations_manifest(self, conn) -> None:
        """
        Persist the schema-declared FK relationships (`registry_relations`) into
        the `_eks_table_relations` manifest table.

        I290 (T1.253): FK definitions live in
        eks_doc_base_schema.json#/registry_relations (SSOT, AGENTS.md Â§16).
        The runtime DuckDB registry does NOT emit physical FOREIGN KEY
        constraints (targets are definition-layer tables that are not
        materialized here; self-FKs would block the UUID migration). Instead
        the relationships are materialized as rows of `_eks_table_relations`,
        making the FK model queryable and keeping docs and DB in lockstep.
        """
        from .schema_to_ddl import SchemaToDDL
        try:
            if self._pre_generated_ddl and "doc_base_schema" in self._pre_generated_ddl:
                ddl_gen = SchemaToDDL(self._pre_generated_ddl["doc_base_schema"], self.logger)
            else:
                loader = getattr(self.config, '_loader', None)
                if loader and hasattr(loader, 'doc_base_schema') and loader.doc_base_schema:
                    ddl_gen = SchemaToDDL(loader.doc_base_schema, self.logger)
                else:
                    ddl_gen = SchemaToDDL(self._load_doc_schema())
            stmts = ddl_gen.generate_relations_manifest_ddl()
            for stmt in stmts:
                conn.execute(stmt)
            count = ddl_gen.registry_relations()
            if count:
                self.logger.info(
                    f"Relations manifest: {len(count)} declared FK relationships "
                    f"persisted to _eks_table_relations (I290/T1.253)",
                    context="DocumentRegistry._create_relations_manifest",
                )
        except Exception as exc:  # nocv â€” manifest is advisory, never fatal
            self.logger.warning(
                f"FK relations manifest skipped ({exc})",
                context="DocumentRegistry._create_relations_manifest",
            )


    @log_depth
    def _migrate_ids_to_uuid(self, conn):
        """
        Convert existing business-key-derived ids (e.g. 'DWG-001-A')
        to pure UUIDs.  Also updates FK references in document_elements.

        T1.99.150 (I186): One-time migration â€” idempotent (only runs on rows
        whose id does not already match UUID format).
        """
        import uuid as _uuid
        # Check if any ids are not UUID-format (UUIDs are 36 chars with hyphens)
        sample = conn.execute(
            "SELECT COUNT(*) FROM documents WHERE length(id) != 36 OR id NOT LIKE '%-%-%-%-%'"
        ).fetchone()
        if not sample or sample[0] == 0:
            return  # Already UUIDs â€” nothing to migrate

        count = sample[0]
        self.logger.status(
            f"Migrating {count} document ids from business-key to UUID format (I186)"
        )

        # Step 1: Create temporary old_id column, populate with current ids
        conn.execute("ALTER TABLE documents ADD COLUMN IF NOT EXISTS _old_id VARCHAR")
        conn.execute("UPDATE documents SET _old_id = id WHERE _old_id IS NULL")

        # Step 2: Replace ids with UUIDs
        rows = conn.execute(
            "SELECT id, _old_id FROM documents WHERE length(id) != 36 OR id NOT LIKE '%-%-%-%-%'"
        ).fetchall()
        old_to_new = {}
        for row in rows:
            new_id = str(_uuid.uuid4())
            old_to_new[row[1]] = new_id
            conn.execute("UPDATE documents SET id = ? WHERE _old_id = ?", [new_id, row[1]])

        # Step 3: Update FK references in document_elements
        for old_id, new_id in old_to_new.items():
            conn.execute(
                "UPDATE document_elements SET doc_id = ? WHERE doc_id = ?",
                [new_id, old_id],
            )

        # Step 4: Drop temporary column
        conn.execute("ALTER TABLE documents DROP COLUMN _old_id")

        self.logger.status(f"ID migration complete: {count} rows converted to UUID")
        # Also ensure the composite index exists (added in I186)
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_doc_business_key ON documents(document_number, revision)"
        )

    def _load_doc_schema(self) -> Dict[str, Any]:
        """Load eks_doc_base_schema.json as fallback when loader is unavailable."""
        loader = getattr(self.config, '_loader', None)
        if loader and hasattr(loader, 'config_dir'):
            config_dir = Path(loader.config_dir)
        else:
            config_dir = self._resolve_doc_base_config_dir()
        return SchemaToDDL.load_doc_base_schema(config_dir)

    def _get_boilerplate_prefixes(self) -> tuple:
        """
        Read boilerplate title prefixes from eks_doc_config.json
        â†’ document_title_config â†’ boilerplate_prefixes (SSOT).
        Falls back to class-level _BOILERPLATE_PREFIXES_FALLBACK.

        T1.99.165 (I196): Replaces hardcoded in-function list per SSOT rule.
        """
        try:
            loader = getattr(self.config, '_loader', None)
            if loader and hasattr(loader, 'config_dir'):
                config_dir = Path(loader.config_dir)
            else:
                config_dir = self._resolve_doc_base_config_dir()
            doc_config_path = config_dir / "schemas" / "eks_doc_config.json"
            if not doc_config_path.exists():
                doc_config_path = config_dir / "eks_doc_config.json"
            if doc_config_path.exists():
                with open(doc_config_path, "r", encoding="utf-8") as f:
                    doc_cfg = json.load(f)
                prefixes = doc_cfg.get("document_title_config", {}).get("boilerplate_prefixes", [])
                if prefixes:
                    return tuple(prefixes)
        except Exception:
            pass
        return self._BOILERPLATE_PREFIXES_FALLBACK

    @log_depth
    def sync_schema(self) -> Dict[str, Any]:
        """
        Synchronize database schema with JSON schema definitions.
        Compares current DB columns against schema and applies any missing
        columns via ALTER TABLE ADD COLUMN.

        Returns a summary dict with keys:
            - documents_added: list of column names added to documents
            - document_elements_added: list of column names added to document_elements
            - indexes_created: list of index names created
        """
        self.logger.status("Syncing database schema with JSON schema definitions")
        summary = {"documents_added": [], "document_elements_added": [], "indexes_created": []}

        conn = duckdb.connect(str(self.db_path))
        try:
            if self._pre_generated_ddl and "doc_base_schema" in self._pre_generated_ddl:
                ddl_gen = SchemaToDDL(
                    self._pre_generated_ddl["doc_base_schema"], self.logger
                )
            else:
                loader = getattr(self.config, '_loader', None)
                if loader and hasattr(loader, 'doc_base_schema') and loader.doc_base_schema:
                    ddl_gen = SchemaToDDL(loader.doc_base_schema, self.logger)
                else:
                    ddl_gen = SchemaToDDL(self._load_doc_schema())

            for table_name, key in [("documents", "documents_added"), ("document_elements", "document_elements_added")]:
                res = conn.execute(f"PRAGMA table_info('{table_name}')").fetchall()
                existing_cols = {row[1] for row in res}
                migration_stmts = ddl_gen.generate_migration_ddl(table_name, existing_cols)
                for stmt in migration_stmts:
                    conn.execute(stmt)
                    col_name = stmt.split("ADD COLUMN ")[1].split()[0]
                    summary[key].append(col_name)

            for idx_stmt in ddl_gen.generate_indexes():
                idx_name = idx_stmt.split("IF NOT EXISTS ")[1].split()[0]
                res = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='index' AND name=?", [idx_name]
                ).fetchone()
                if not res:
                    conn.execute(idx_stmt)
                    summary["indexes_created"].append(idx_name)

        finally:
            conn.close()

        total = sum(len(v) for v in summary.values())
        self.logger.status(f"Schema sync complete: {total} changes applied")
        return summary

    @log_depth
    def store_elements(self, doc_id: str, elements: List[Dict[str, Any]]) -> int:
        """
        Insert structural elements for a document. Returns count inserted.
        I291 (T1.254): (a) surrogate UUID id injected per element;
        (b) element_type validated against the 11-code enum
        (fk_element_type declared_only â€” validation-layer enforcement, no
        physical DuckDB FK); (c) doc_id existence enforced (fk_element_doc
        declared_only â€” writes to unknown documents are rejected).
        """
        valid_types = self._element_type_codes()
        conn = duckdb.connect(str(self.db_path))
        try:
            count = 0
            for el in elements:
                el_type = el.get("element_type", "unknown")
                if el_type not in valid_types:
                    raise ValueError(
                        f"Unknown element_type '{el_type}' for document {doc_id} â€” "
                        f"expected one of {sorted(valid_types)} (I291/T1.254)"
                    )
                exists = conn.execute(
                    "SELECT COUNT(*) FROM documents WHERE id = ?", [doc_id]
                ).fetchone()[0]
                if not exists:
                    raise ValueError(
                        f"Cannot store elements: document {doc_id} not found in "
                        f"documents table (fk_element_doc declared_only, I291/T1.254)"
                    )
                conn.execute("""
                    INSERT INTO document_elements
                    (id, doc_id, element_type, element_id, title, content, confidence, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, [
                    str(uuid.uuid4()),
                    doc_id,
                    el_type,
                    el.get("element_id"),
                    el.get("title"),
                    el.get("content"),
                    el.get("confidence"),
                    el.get("source", "heuristic"),
                ])
                count += 1
            self.logger.info(f"Stored {count} elements for {doc_id}", context="DocumentRegistry.store_elements")
            return count
        finally:
            conn.close()

    def _element_type_codes(self) -> set:
        """Cached set of valid element_type codes (I291/T1.254, fk_element_type)."""
        if getattr(self, "_element_type_codes_cache", None) is not None:
            return self._element_type_codes_cache
        try:
            schema = SchemaToDDL.load_doc_base_schema(self._resolve_doc_base_config_dir())
            codes = set(schema["definitions"]["element_type_code"]["enum"])
        except Exception:
            loader = getattr(self.config, '_loader', None)
            if loader and hasattr(loader, "doc_base_schema"):
                codes = set(
                    loader.doc_base_schema.get("definitions", {}).get(
                        "element_type_code", {}
                    ).get("enum", [])
                )
            else:
                codes = set()
        self._element_type_codes_cache = codes
        return codes

    @log_depth
    def get_elements(self, doc_id: str) -> List[Dict[str, Any]]:
        """Retrieve all structural elements for a document."""
        conn = duckdb.connect(str(self.db_path))
        try:
            res = conn.execute(
                "SELECT * FROM document_elements WHERE doc_id = ? ORDER BY doc_id, element_type", [doc_id]
            ).fetchall()
            cols = [d[0] for d in conn.description]
            return [dict(zip(cols, row)) for row in res]
        finally:
            conn.close()

    @log_depth
    def get_elements_by_type(self, doc_id: str, element_type: str) -> List[Dict[str, Any]]:
        """Retrieve structural elements of a specific type for a document."""
        conn = duckdb.connect(str(self.db_path))
        try:
            res = conn.execute(
                "SELECT * FROM document_elements WHERE doc_id = ? AND element_type = ? ORDER BY doc_id",
                [doc_id, element_type]
            ).fetchall()
            cols = [d[0] for d in conn.description]
            return [dict(zip(cols, row)) for row in res]
        finally:
            conn.close()

    @log_depth
    def delete_elements(self, doc_id: str) -> int:
        """Delete all structural elements for a document. Returns count deleted."""
        conn = duckdb.connect(str(self.db_path))
        try:
            before = conn.execute("SELECT COUNT(*) FROM document_elements WHERE doc_id = ?", [doc_id]).fetchone()[0]
            conn.execute("DELETE FROM document_elements WHERE doc_id = ?", [doc_id])
            self.logger.info(f"Deleted {before} elements for {doc_id}", context="DocumentRegistry.delete_elements")
            return before
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # T1.256 (I293): batch_run runtime table CRUD
    # ------------------------------------------------------------------

    @log_depth
    def insert_batch(self, run_id: str, *, project_code: Optional[str] = None,
                     job_id: Optional[str] = None, data_dir: Optional[str] = None,
                     status: str = "running", started_at: Optional[str] = None) -> str:
        """
        Create a new batch_run row at pipeline start (Phase A).
        I293 (T1.256): `batch_run` is a GROUP 11 runtime table (no base-schema
        definition); one row per run. Stage stats are zero-initialized and
        populated by ``update_batch()`` at each phase boundary.
        """
        if not run_id:
            run_id = str(uuid.uuid4())
        started_at = started_at or datetime.now().isoformat()
        conn = duckdb.connect(str(self.db_path))
        try:
            conn.execute(
                "INSERT INTO batch_run (run_id, job_id, project_code, data_dir, "
                "current_stage, phase_a_discovered, phase_a_valid, phase_b_total, "
                "phase_b_success, phase_b_failed, phase_c_flagged, started_at, status, doc_count) "
                "VALUES (?, ?, ?, ?, 'A', 0, 0, 0, 0, 0, 0, ?, ?, 0)",
                [run_id, job_id, project_code, data_dir, started_at, status],
            )
            self.logger.info(f"Batch run {run_id} created (status={status})", context="DocumentRegistry.insert_batch")
        finally:
            conn.close()
        return run_id

    @log_depth
    def update_batch(self, run_id: str, *, current_stage: Optional[str] = None,
                     phase_a_discovered: Optional[int] = None, phase_a_valid: Optional[int] = None,
                     phase_b_total: Optional[int] = None, phase_b_success: Optional[int] = None,
                     phase_b_failed: Optional[int] = None, phase_c_flagged: Optional[int] = None,
                     status: Optional[str] = None, finished_at: Optional[str] = None,
                     doc_count: Optional[int] = None) -> None:
        """
        Update stage statistics on an existing batch_run row (called at each
        phase boundary). I293 (T1.256) â€” only non-None fields are updated; the
        row is created by ``insert_batch()``.
        """
        fields: Dict[str, Any] = {
            "current_stage": current_stage,
            "phase_a_discovered": phase_a_discovered,
            "phase_a_valid": phase_a_valid,
            "phase_b_total": phase_b_total,
            "phase_b_success": phase_b_success,
            "phase_b_failed": phase_b_failed,
            "phase_c_flagged": phase_c_flagged,
            "status": status,
            "finished_at": finished_at or (datetime.now().isoformat() if status and status != "running" else None),
            "doc_count": doc_count,
        }
        sets = [k for k, v in fields.items() if v is not None]
        if not sets:
            self.logger.warning(
                f"update_batch({run_id}): no fields to update", context="DocumentRegistry.update_batch"
            )
            return
        conn = duckdb.connect(str(self.db_path))
        try:
            assigns = ", ".join(f"{k} = ?" for k in sets)
            params = [fields[k] for k in sets] + [run_id]
            conn.execute(f"UPDATE batch_run SET {assigns} WHERE run_id = ?", params)
            self.logger.info(
                f"Batch run {run_id} updated: {', '.join(sets)}",
                context="DocumentRegistry.update_batch",
            )
        finally:
            conn.close()

    @log_depth
    def get_batch(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a single batch_run row by run_id."""
        conn = duckdb.connect(str(self.db_path))
        try:
            res = conn.execute("SELECT * FROM batch_run WHERE run_id = ?", [run_id]).fetchall()
            if not res:
                return None
            cols = [d[0] for d in conn.description]
            return dict(zip(cols, res[0]))
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # I298 (T1.261): pipeline_checkpoint runtime table CRUD
    # ------------------------------------------------------------------

    @log_depth
    def insert_checkpoint(self, job_id: str, phase: str, state_json: str) -> str:
        """
        Persist pipeline checkpoint state snapshot to DB.
        I298 (T1.261): written alongside filesystem JSON for SQL-queryable restore/audit.
        """
        checkpoint_id = str(uuid.uuid4())
        conn = duckdb.connect(str(self.db_path))
        try:
            conn.execute(
                "INSERT INTO pipeline_checkpoint (id, job_id, phase, state) "
                "VALUES (?, ?, ?, ?)",
                [checkpoint_id, job_id, phase, state_json],
            )
            self.logger.debug(
                f"Checkpoint {checkpoint_id} saved for job={job_id} phase={phase}",
                context="DocumentRegistry.insert_checkpoint",
            )
        finally:
            conn.close()
        return checkpoint_id

    @log_depth
    def get_checkpoint(self, job_id: str, phase: str) -> Optional[Dict[str, Any]]:
        """Fetch latest checkpoint for job+phase."""
        conn = duckdb.connect(str(self.db_path))
        try:
            res = conn.execute(
                "SELECT * FROM pipeline_checkpoint WHERE job_id = ? AND phase = ? "
                "ORDER BY created_at DESC LIMIT 1",
                [job_id, phase],
            ).fetchall()
            if not res:
                return None
            cols = [d[0] for d in conn.description]
            return dict(zip(cols, res[0]))
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # I299 (T1.262): pipeline_event_log runtime table CRUD
    # ------------------------------------------------------------------

    @log_depth
    def insert_events(self, job_id: str, events: list) -> None:
        """
        Batch-insert pipeline event/debug log entries.
        I299 (T1.262): flushes _LogCapture buffer to DB at pipeline completion.
        Each event is a dict with keys: timestamp, level, category, context, module, message.
        """
        if not events:
            return
        conn = duckdb.connect(str(self.db_path))
        try:
            for ev in events:
                ev_id = str(uuid.uuid4())
                conn.execute(
                    "INSERT INTO pipeline_event_log (id, job_id, timestamp, level, "
                    "category, context, module, message) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    [
                        ev_id, job_id,
                        ev.get("timestamp", datetime.now().isoformat()),
                        ev.get("level", "INFO"),
                        ev.get("category", ""),
                        ev.get("context", ""),
                        ev.get("module", ""),
                        ev.get("message", ""),
                    ],
                )
            self.logger.debug(
                f"{len(events)} events saved for job={job_id}",
                context="DocumentRegistry.insert_events",
            )
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # I301 (T1.264): export_artifact runtime table CRUD
    # ------------------------------------------------------------------

    @log_depth
    def insert_artifact(self, job_id: str, artifact_type: str,
                        file_path: str, row_count: int = 0) -> str:
        """
        Track a pipeline export artifact (CSV/XLSX).
        I301 (T1.264): written after each export file generation in _handle_export().
        """
        artifact_id = str(uuid.uuid4())
        conn = duckdb.connect(str(self.db_path))
        try:
            conn.execute(
                "INSERT INTO export_artifact (id, job_id, artifact_type, "
                "file_path, row_count) VALUES (?, ?, ?, ?, ?)",
                [artifact_id, job_id, artifact_type, str(file_path), row_count],
            )
            self.logger.debug(
                f"Artifact {artifact_id} recorded for job={job_id} type={artifact_type}",
                context="DocumentRegistry.insert_artifact",
            )
        finally:
            conn.close()
        return artifact_id

    # ------------------------------------------------------------------
    # T1.257 (I294): health_score / health_batch runtime table CRUD
    # ------------------------------------------------------------------

    @log_depth
    def store_health_score(self, run_id: str, document_id: str, score_row: Dict[str, Any]) -> str:
        """
        Persist one per-document health score row (GROUP 8/11).
        I294 (T1.257): `document_id` is the registry UUID (declared_only FK â†’
        documents.id enforced at the validation layer â€” no physical FK DDL).
        If a row for ``(run_id, document_id)`` already exists it is replaced.
        """
        import json as _json
        row_id = str(uuid.uuid4())
        scored_at = score_row.get("scored_at") or datetime.now().isoformat()
        dims = score_row.get("dimensions", {})
        conn = duckdb.connect(str(self.db_path))
        try:
            # I310/T1.295: materialized health rows may arrive before the
            # pipeline writes batch metadata; preserve that runtime contract.
            conn.execute(
                "INSERT INTO batch_run (run_id) VALUES (?) ON CONFLICT (run_id) DO NOTHING",
                [run_id],
            )
            conn.execute(
                "DELETE FROM health_score WHERE run_id = ? AND document_id = ?",
                [run_id, document_id],
            )
            conn.execute(
                "INSERT INTO health_score (id, run_id, document_id, class_id, template_id, "
                "health_score, extract_status, dim_completeness, dim_extraction, dim_structural, "
                "dim_source, dim_xref, dim_consistency, missing_columns, tier1_populated, "
                "tier1_total, scored_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    row_id, run_id, document_id,
                    score_row.get("class_id"), score_row.get("template_id"),
                    float(score_row.get("health_score", 0.0)),
                    score_row.get("extract_status"),
                    dims.get("completeness"), dims.get("extraction_confidence"),
                    dims.get("structural_completeness"), dims.get("source_quality"),
                    dims.get("xref_quality"), dims.get("consistency"),
                    _json.dumps(score_row.get("missing_columns", [])),
                    score_row.get("tier1_populated"), score_row.get("tier1_total"),
                    scored_at,
                ],
            )
            self.logger.info(
                f"Health score for doc {document_id}: {score_row.get('health_score')}",
                context="DocumentRegistry.store_health_score",
            )
        finally:
            conn.close()
        return row_id

    @log_depth
    def store_health_batch(self, run_id: str, batch_row: Dict[str, Any]) -> None:
        """Persist the health_batch aggregate row for a run (GROUP 8/11)."""
        by_status = batch_row.get("by_status", {})
        conn = duckdb.connect(str(self.db_path))
        try:
            conn.execute(
                "INSERT INTO batch_run (run_id) VALUES (?) ON CONFLICT (run_id) DO NOTHING",
                [run_id],
            )
            conn.execute(
                "INSERT INTO health_batch (run_id, avg_document_health, total_documents, "
                "status_success, status_partial, status_failed) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                [
                    run_id,
                    float(batch_row.get("avg_document_health", 0.0)),
                    int(batch_row.get("total_documents", 0)),
                    int(by_status.get("success", 0)),
                    int(by_status.get("partial", 0)),
                    int(by_status.get("failed", 0)),
                ],
            )
            self.logger.info(
                f"Health batch {run_id}: {batch_row.get('total_documents')} docs, "
                f"avg={batch_row.get('avg_document_health')}",
                context="DocumentRegistry.store_health_batch",
            )
        finally:
            conn.close()

    @log_depth
    def get_health_scores(self, run_id: str) -> List[Dict[str, Any]]:
        """Fetch all health_score rows for a run."""
        conn = duckdb.connect(str(self.db_path))
        try:
            res = conn.execute(
                "SELECT * FROM health_score WHERE run_id = ? ORDER BY scored_at", [run_id]
            ).fetchall()
            cols = [d[0] for d in conn.description]
            return [dict(zip(cols, row)) for row in res]
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # T1.258 (I295): document_reference junction CRUD
    # ------------------------------------------------------------------

    _DOCUMENT_RELATION_TYPES = {
        "produced_from", "validated_by", "references", "implements", "supersedes",
        "derived_from", "contains", "linked_to", "verified_against", "governs",
    }

    @log_depth
    def store_document_reference(self, source_doc_id: str, target_doc_id: str,
                                 relation_type: str) -> str:
        """
        Insert a single document_reference junction row.
        I295 (T1.258): both endpoints are declared_only FKs â†’ documents.id;
        relation_type must be one of the 10 document-level relationship types
        (Appendix B Â§B2.1 Â§5). Validates doc_id existence and relation_type.
        """
        if relation_type not in self._DOCUMENT_RELATION_TYPES:
            raise ValueError(
                f"Unknown relation_type '{relation_type}'. Must be one of: "
                f"{sorted(self._DOCUMENT_RELATION_TYPES)}"
            )
        for d in (source_doc_id, target_doc_id):
            if not self.get_document_by_id(d):
                raise ValueError(f"document_reference endpoint not found in registry: {d}")
        row_id = str(uuid.uuid4())
        conn = duckdb.connect(str(self.db_path))
        try:
            conn.execute(
                "INSERT INTO document_reference (id, source_doc_id, target_doc_id, relation_type) "
                "VALUES (?, ?, ?, ?)",
                [row_id, source_doc_id, target_doc_id, relation_type],
            )
        finally:
            conn.close()
        return row_id

    @log_depth
    def list_document_references(self, doc_id: str) -> List[Dict[str, Any]]:
        """List all references where ``doc_id`` is the source or the target."""
        conn = duckdb.connect(str(self.db_path))
        try:
            res = conn.execute(
                "SELECT * FROM document_reference WHERE source_doc_id = ? OR target_doc_id = ? "
                "ORDER BY created_at",
                [doc_id, doc_id],
            ).fetchall()
            cols = [d[0] for d in conn.description]
            return [dict(zip(cols, row)) for row in res]
        finally:
            conn.close()

    @log_depth
    def delete_document_references(self, doc_id: str) -> int:
        """Delete all reference rows where ``doc_id`` is source or target. Returns count."""
        conn = duckdb.connect(str(self.db_path))
        try:
            before = conn.execute(
                "SELECT COUNT(*) FROM document_reference WHERE source_doc_id = ? OR target_doc_id = ?",
                [doc_id, doc_id],
            ).fetchone()[0]
            conn.execute(
                "DELETE FROM document_reference WHERE source_doc_id = ? OR target_doc_id = ?",
                [doc_id, doc_id],
            )
            return before
        finally:
            conn.close()

    @log_depth
    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a registry document by its UUID id (used by reference validation)."""
        conn = duckdb.connect(str(self.db_path))
        try:
            res = conn.execute("SELECT * FROM documents WHERE id = ?", [doc_id]).fetchall()
            if not res:
                return None
            cols = [d[0] for d in conn.description]
            return dict(zip(cols, res[0]))
        finally:
            conn.close()

    @log_depth
    def register_document(self, metadata: Dict[str, Any]) -> str:
        """
        Register a new document revision in the registry.
        Handles 'is_latest' flag update and JSON serialization for complex fields.

        T1.99.120: L3 null-tolerant â€” generates synthetic UNRESOLVED-{hash} key
        instead of raising KeyError when document_number is missing.
        """
        doc_number = metadata.get("document_number")
        revision = metadata.get("revision", "00")

        # T1.99.148 (I187): L3 â€” generate synthetic key via common library
        if not doc_number:
            file_path = metadata.get("file_path", "")
            synthetic_key = generate_synthetic_key(file_path)
            self.logger.warning(
                f"document_number missing â€” generating synthetic key {synthetic_key}",
                context="DocumentRegistry.register_document"
            )
            metadata["document_number"] = synthetic_key
            doc_number = synthetic_key
            if not revision:
                revision = "00"
                metadata["revision"] = revision

        # T1.99.150 (I186): id is now a pure UUID â€” business-key derived id is retired
        doc_id = str(uuid.uuid4())
        
        self.logger.debug(f"Registering document: {doc_id}", context="DocumentRegistry.register_document")
        
        # Serialize asset_tags if provided as list
        tags = metadata.get("asset_tags")
        if isinstance(tags, list):
            tags_json = json.dumps(tags)
        else:
            tags_json = tags

        # T1.99.145: Serialize references_documents if provided as list
        refs = metadata.get("references_documents")
        if isinstance(refs, list):
            refs_json = json.dumps(refs)
        else:
            refs_json = json.dumps([])  # default empty array

        # T1.99.142: Derive document_title
        doc_title = metadata.get("document_title")
        if not doc_title:
            embedded_title = metadata.get("embedded_title")
            # T1.99.165 (I196): Schema-driven boilerplate prefix check (SSOT)
            boilerplate_prefixes = self._get_boilerplate_prefixes()
            if embedded_title and embedded_title.strip() and not embedded_title.strip().startswith(boilerplate_prefixes):
                doc_title = embedded_title.strip()
            else:
                # Fallback: filename stem
                file_path = metadata.get("file_path", "")
                if file_path:
                    doc_title = Path(file_path).stem
                else:
                    doc_title = doc_number

        # T1.99.146: Set total_sheets default from page_count
        total_sheets = metadata.get("total_sheets")
        if total_sheets is None:
            total_sheets = metadata.get("page_count")

        conn = duckdb.connect(str(self.db_path))
        try:
            # 1. Clear 'is_latest' for older revisions of the same document number
            #    and capture the previously-latest for supersedes chain (T1.99.141)
            prev = conn.execute(
                "SELECT id FROM documents WHERE document_number = ? AND is_latest = TRUE",
                [doc_number]
            ).fetchone()
            prev_doc_id = prev[0] if prev else None
            conn.execute("UPDATE documents SET is_latest = FALSE WHERE document_number = ?", [doc_number])
            
            # 2. Build dynamic INSERT from metadata keys that match allowed columns
            #    T1.99.136: Dynamic column builder replaces hardcoded 24-column INSERT.
            allowlist = self.COLUMN_ALLOWLIST
            core_meta = {
                "id": doc_id,
                "source_type": metadata.get("source_type", "ingested"),
                "project_title": metadata.get("project_title"),
                "project_number": metadata.get("project_number"),
                "area": metadata.get("area"),
                "discipline": metadata.get("discipline"),
                "department": metadata.get("department"),
                "document_type": metadata.get("document_type"),
                "document_number": doc_number,
                "revision": revision,
                "status": metadata.get("status"),
                "is_latest": True,
                "file_path": metadata.get("file_path"),
                "file_type": metadata.get("file_type"),
                "asset_tags": tags_json,
                "extract_status": metadata.get("extract_status", "pending"),
                "extraction_confidence": metadata.get("extraction_confidence"),
                "extraction_notes": metadata.get("extraction_notes"),
                # I308/T1.283: materialize flag_reason at ingest (single source of
                # truth = core.flag_utils.compute_flag_reason). Explicit caller
                # value wins; otherwise computed so v_review_flags is a pure
                # projection (no SQL CASE duplication).
                "flag_reason": metadata.get("flag_reason")
                if metadata.get("flag_reason")
                else compute_flag_reason(
                    metadata.get("extract_status", "pending"),
                    metadata.get("extraction_confidence"),
                ),
                # T1.99.145: Cross-reference column
                "references_documents": refs_json,
                # T1.99.142: Human-readable title
                "document_title": doc_title,
                # T1.99.146: Language default
                "language": metadata.get("language", "en"),
                # T1.99.146: Total sheets default to page_count
                "total_sheets": total_sheets,
            }
            # T1.99.141: Set supersedes chain from captured previous-latest
            if prev_doc_id and prev_doc_id != doc_id:
                core_meta["supersedes"] = prev_doc_id

            # Merge metadata extras (new property columns pass through here)
            for key, value in metadata.items():
                if key not in core_meta and key in allowlist:
                    core_meta[key] = value

            # Build column/value lists
            columns = [k for k in core_meta.keys() if k in allowlist]
            placeholders = ", ".join(["?" for _ in columns])
            values = [core_meta[col] for col in columns]
            col_list = ", ".join(columns)

            # T1.99.150 (I186): Pure INSERT â€” every call creates a new row unconditionally.
            # I185 (three-tier check) is the sole gatekeeper that decides whether to call this.
            conn.execute(
                f"INSERT INTO documents ({col_list}) VALUES ({placeholders})",
                values,
            )

            # T1.99.141: Update previous document's superseded_by to point to this new revision
            if prev_doc_id and prev_doc_id != doc_id:
                conn.execute(
                    "UPDATE documents SET superseded_by = ? WHERE id = ?",
                    [doc_id, prev_doc_id],
                )
                self.logger.debug(
                    f"Revision chain: {doc_id} supersedes {prev_doc_id}",
                    context="DocumentRegistry.register_document",
                )

            self.logger.debug(f"Document {doc_id} registered successfully.")
            return doc_id
        finally:
            conn.close()

    @log_depth
    def get_document(self, doc_number: str, revision: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieve metadata for a specific document revision."""
        conn = duckdb.connect(str(self.db_path))
        try:
            if revision:
                res = conn.execute("SELECT * FROM documents WHERE document_number = ? AND revision = ?", [doc_number, revision]).fetchone()
            else:
                res = conn.execute("SELECT * FROM documents WHERE document_number = ? AND is_latest = TRUE", [doc_number]).fetchone()
            
            if not res:
                return None
            
            # Convert to dict
            cols = [d[0] for d in conn.description]
            return dict(zip(cols, res))
        finally:
            conn.close()

    @log_depth
    def get_document_by_file_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Retrieve the latest (is_latest=TRUE) document by its file_path.

        T1.106 (I232): SSOT lookup that avoids filename-parse divergence.
        Phase A registered every file with its absolute file_path, so this
        always returns the correct doc_id regardless of filename parseability.
        """
        conn = duckdb.connect(str(self.db_path))
        try:
            res = conn.execute(
                "SELECT * FROM documents WHERE file_path = ? AND is_latest = TRUE",
                [file_path],
            ).fetchone()
            if not res:
                return None
            cols = [d[0] for d in conn.description]
            return dict(zip(cols, res))
        finally:
            conn.close()

    @log_depth
    def get_latest_by_key(self, doc_number: str, revision: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve the most-recently-registered (is_latest=TRUE) row for a given
        (document_number, revision) pair.

        T1.99.150 (I186): Introduced alongside UUID-based id to provide the
        authoritative "current" row when multiple rows share the same
        (document_number, revision) due to content changes.

        Returns None if no row exists for this composite key.
        """
        conn = duckdb.connect(str(self.db_path))
        try:
            res = conn.execute(
                "SELECT * FROM documents WHERE document_number = ? AND revision = ? AND is_latest = TRUE",
                [doc_number, revision],
            ).fetchone()

            if not res:
                return None

            cols = [d[0] for d in conn.description]
            return dict(zip(cols, res))
        finally:
            conn.close()

    def _with_retry(self, fn, retries: Optional[int] = None, delay: Optional[float] = None):
        """Execute *fn* with retries on IOError (DuckDB locking contention)."""
        retries = self.retry_count if retries is None else retries
        delay = self.retry_delay if delay is None else delay
        for attempt in range(retries):
            try:
                return fn()
            except (IOError, OSError) as e:
                if attempt < retries - 1:
                    if hasattr(fn, '__self__') and hasattr(fn.__self__, 'logger'):
                        fn.__self__.logger.warning(
                            f"DB lock contention (attempt {attempt+1}/{retries}): {e}",
                            context="DocumentRegistry._with_retry"
                        )
                    time.sleep(delay)
                else:
                    raise

    @log_depth
    def update_document_status(self, doc_id: str, status: str,
                               confidence: Optional[float] = None,
                               notes: Optional[str] = None,
                               extra_properties: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update document extraction status using the registry singleton connection.
        Uses _with_retry for safe concurrent access.

        T1.99.136: Accepts extra_properties dict to update additional registry
        columns (e.g. file_size, file_hash, embedded_title from FilePropertyExtractor).
        Only keys present in COLUMN_ALLOWLIST are applied.

        T1.99.152 (I184): Before executing UPDATE, queries current row and
        compares extraction-related fields.  Any changes are serialized as
        ``[DIFF] {"field": {"old": ..., "new": ...}}`` and prepended to
        extraction_notes.

        Returns True if exactly one row was updated.
        """
        def _action():
            conn = duckdb.connect(str(self.db_path))
            try:
                # T1.99.152 (I184): Query current row for diff logging
                current = conn.execute(
                    "SELECT * FROM documents WHERE id = ?", [doc_id]
                ).fetchone()
                current_dict: Dict[str, Any] = {}
                if current:
                    cols = [d[0] for d in conn.description]
                    current_dict = dict(zip(cols, current))

                # Build SET clause dynamically
                allowlist = self.COLUMN_ALLOWLIST

                # --- T1.99.152 (I184): compute diff before setting final notes ---
                effective_notes = notes
                if current_dict and extra_properties:
                    # Build the proposed new-values dict for diff comparison
                    new_values: Dict[str, Any] = {**extra_properties}
                    new_values["extraction_confidence"] = confidence
                    diffs = detect_changes(
                        old_dict=current_dict,
                        new_dict=new_values,
                        track_fields=self.DIFF_TRACK_FIELDS,
                    )
                    if diffs:
                        diff_payload = json.dumps(
                            {d.field: {"old": d.old_value, "new": d.new_value} for d in diffs}
                        )
                        diff_header = f"[DIFF] {diff_payload}"
                        existing = (notes or "").strip()
                        effective_notes = f"{diff_header}\n{existing}" if existing else diff_header
                        self.logger.warning(
                            f"Field changes detected on update for {doc_id}: {diff_payload}",
                            context="DocumentRegistry.update_document_status",
                        )

                set_parts = ["extract_status = ?", "extraction_confidence = ?", "extraction_notes = ?"]
                params: List[Any] = [status, confidence, effective_notes]

                if extra_properties:
                    for key, value in extra_properties.items():
                        if key in allowlist:
                            set_parts.append(f"{key} = ?")
                            params.append(value)

                params.append(doc_id)
                set_clause = ", ".join(set_parts)
                conn.execute(
                    f"UPDATE documents SET {set_clause} WHERE id = ?",
                    params,
                )
                # Check affected rows via a SELECT COUNT after UPDATE
                affected = conn.execute(
                    "SELECT COUNT(*) FROM documents WHERE id = ? AND extract_status = ?",
                    [doc_id, status]
                ).fetchone()
                count = affected[0] if affected else 0
                if count > 0:
                    self.logger.info(f"Updated status for {doc_id}: {status} (conf={confidence})",
                                     context="DocumentRegistry.update_document_status")
                    return True
                self.logger.warning(f"Document not found for status update: {doc_id}",
                                   context="DocumentRegistry.update_document_status")
                return False
            finally:
                conn.close()

        try:
            return self._with_retry(_action)
        except Exception as e:
            self.logger.error(f"Failed to update document status for {doc_id}: {e}",
                              context="DocumentRegistry.update_document_status")
            return False

    @log_depth
    def list_documents(self, 
                       filters: Optional[Dict[str, Any]] = None, 
                       latest_only: bool = True,
                       order_by: Optional[str] = None) -> List[Dict[str, Any]]:
        """List documents with optional filtering and SQL-level sorting."""
        conn = duckdb.connect(str(self.db_path))
        try:
            query = "SELECT * FROM documents WHERE 1=1"
            params = []
            
            if latest_only:
                query += " AND is_latest = TRUE"
            
            if filters:
                for k, v in filters.items():
                    if k not in self.COLUMN_ALLOWLIST:
                        self.logger.warning(f"Ignored untrusted filter column: {k}", context="DocumentRegistry.list_documents")
                        continue
                    query += f" AND {k} = ?"
                    params.append(v)
            
            if order_by:
                # Basic validation for order_by - expect "column_name" or "column_name DESC"
                base_col = order_by.split()[0].lower()
                if base_col in self.COLUMN_ALLOWLIST:
                    query += f" ORDER BY {order_by}"
                else:
                    self.logger.warning(f"Ignored untrusted order_by column: {base_col}", context="DocumentRegistry.list_documents")
            
            res = conn.execute(query, params).fetchall()
            cols = [d[0] for d in conn.description]
            return [dict(zip(cols, row)) for row in res]
        finally:
            conn.close()

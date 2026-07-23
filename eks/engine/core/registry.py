"""
Document Registry for EKS - Metadata DB CRUD interface using DuckDB.
DDL is auto-generated from JSON schema definitions via SchemaToDDL (T1.36).

Revision: 0.7
Date: 2026-07-23
Author: CodeBuddy
Summary: 0.7: T1.106 (I232) — added get_document_by_file_path() for SSOT doc_id lookup.
         0.6: T1.99.153 (I189/F1) — added optional db_path parameter for test-isolated databases.
         0.5: T1.99.148 (I187) — migrated synthetic key generation to common.library.utility.synthetic_key.
          Removed ad-hoc hashlib usage for key generation.
          T1.99.150 (I186) — changed id from business-key to pure UUID, INSERT OR REPLACE → INSERT.
          T1.99.152 (I184) — added diff logging to update_document_status().
          Prior: T1.99.141–T1.99.146 — document metadata completeness.
"""
import duckdb
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
from ..logging.logger import EKSLogger, log_depth

class DocumentRegistry:
    """
    Manages document metadata storage and retrieval.
    Backed by DuckDB (or PostgreSQL if configured).
    DDL is auto-generated from JSON schema definitions via SchemaToDDL (T1.36).
    """

    _SCHEMA_DERIVED_ALLOWLIST: Optional[set] = None

    # T1.99.165 (I196): SSOT fallback — the authoritative source is
    # eks_doc_config.json → document_title_config → boilerplate_prefixes.
    # This constant is used only when that config cannot be loaded.
    _BOILERPLATE_PREFIXES_FALLBACK = (
        "Microsoft Word", "AutoCAD Drawing", "Microsoft Excel"
    )

    @classmethod
    def _get_column_allowlist(cls) -> set:
        """
        Derive COLUMN_ALLOWLIST from JSON schema definitions.
        Falls back to static set if schema is unavailable.
        """
        if cls._SCHEMA_DERIVED_ALLOWLIST is not None:
            return cls._SCHEMA_DERIVED_ALLOWLIST
        try:
            from .schema_to_ddl import SchemaToDDL
            config_dir = Path("eks/config")
            schema = SchemaToDDL.load_doc_base_schema(config_dir)
            gen = SchemaToDDL(schema)
            project_props = gen.definitions.get("project_metadata_def", {}).get("properties", {})
            document_props = gen.definitions.get("document_metadata_def", {}).get("properties", {})
            all_cols = set(project_props.keys()) | set(document_props.keys())
            all_cols.add("id")
            cls._SCHEMA_DERIVED_ALLOWLIST = all_cols
            return all_cols
        except Exception:
            return {
                "id", "project_title", "project_number", "area", "discipline",
                "department", "document_type", "document_number", "revision",
                "status", "is_latest", "file_path", "ingested_at", "source_type",
                "created_by", "checked_by", "approved_by", "originator_company",
                "security_class", "asset_tags", "page_count", "extract_status",
                "extraction_confidence", "extraction_notes", "verified_by",
                "file_size", "file_created_at", "file_modified_at", "file_hash",
                "embedded_title", "embedded_subject", "embedded_created_date",
                "embedded_modified_date", "embedded_creator_app", "embedded_producer",
                "embedded_last_modified_by", "embedded_keywords", "embedded_sheet_count",
                # T1.99.141–T1.99.146: 15 new metadata columns
                "supersedes", "superseded_by", "document_title",
                "lifecycle_stage", "revision_date", "revision_description",
                "embedded_revision_number", "references_documents",
                "project_phase", "contract_package", "issued_date",
                "responsible_engineer", "total_sheets", "language", "vendor_name",
            }

    @property
    def COLUMN_ALLOWLIST(self) -> set:
        return self._get_column_allowlist()

    # T1.99.152 (I184): Fields tracked for before/after diff on status update
    DIFF_TRACK_FIELDS: set = {
        "embedded_title", "page_count", "extraction_confidence",
        "file_hash", "document_title", "lifecycle_stage",
        "revision_description",
    }

    def __init__(self, logger: Optional[EKSLogger] = None, db_path: Optional[str] = None):
        """
        Initialize the DocumentRegistry.

        Args:
            logger: Optional EKSLogger instance.
            db_path: Optional explicit database file path. When provided, used
                directly (bypassing config). Enables test-isolated databases
                (I189/F1).
        """
        self.config = ConfigRegistry()
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
        self._init_db()
        self._migrate_schema()

    @log_depth
    def _init_db(self):
        """Initialize the metadata database tables with DDL auto-generated from JSON schema."""
        self.logger.status(f"Initializing Document Registry at {self.db_path}")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

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

        conn = duckdb.connect(str(self.db_path))
        try:
            conn.execute(docs_ddl)
            conn.execute(els_ddl)
            for idx_stmt in indexes:
                conn.execute(idx_stmt)
        finally:
            conn.close()

    @log_depth
    def _migrate_schema(self):
        """Handle schema evolution by adding missing columns via SchemaToDDL."""
        conn = duckdb.connect(str(self.db_path))
        try:
            for table_name in ["documents", "document_elements"]:
                res = conn.execute(f"PRAGMA table_info('{table_name}')").fetchall()
                existing_cols = {row[1] for row in res}

                loader = getattr(self.config, '_loader', None)
                if loader and hasattr(loader, 'doc_base_schema') and loader.doc_base_schema:
                    ddl_gen = SchemaToDDL(loader.doc_base_schema, self.logger)
                else:
                    ddl_gen = SchemaToDDL(self._load_doc_schema())

                migration_stmts = ddl_gen.generate_migration_ddl(table_name, existing_cols)
                for stmt in migration_stmts:
                    conn.execute(stmt)

            # T1.99.166 (I196): Diagnose misapplied NOT NULL constraints on
            # project-metadata columns.  These columns should be nullable
            # (always_nullable set in SchemaToDDL) but old DDL may have
            # applied NOT NULL.  Pragma NOTNULL check is advisory only —
            # DuckDB does not support ALTER COLUMN DROP NOT NULL.
            always_nullable_cols = {"project_title", "project_number", "area", "discipline", "department"}
            null_check = conn.execute(
                "SELECT name FROM pragma_table_info('documents') WHERE \"notnull\" = 1"
            ).fetchall()
            bogus_notnull = [row[0] for row in null_check if row[0] in always_nullable_cols]
            if bogus_notnull:
                self.logger.warning(
                    f"Schema drift: {len(bogus_notnull)} project-metadata column(s) "
                    f"have NOT NULL constraint but should be nullable: {bogus_notnull}. "
                    f"Delete eks_registry.db and re-run to rebuild with correct DDL.",
                    context="DocumentRegistry._migrate_schema",
                )

            # T1.99.150 (I186): Migrate existing business-key ids to UUIDs
            self._migrate_ids_to_uuid(conn)
        finally:
            conn.close()

    @log_depth
    def _migrate_ids_to_uuid(self, conn):
        """
        Convert existing business-key-derived ids (e.g. 'DWG-001-A')
        to pure UUIDs.  Also updates FK references in document_elements.

        T1.99.150 (I186): One-time migration — idempotent (only runs on rows
        whose id does not already match UUID format).
        """
        import uuid as _uuid
        # Check if any ids are not UUID-format (UUIDs are 36 chars with hyphens)
        sample = conn.execute(
            "SELECT COUNT(*) FROM documents WHERE length(id) != 36 OR id NOT LIKE '%-%-%-%-%'"
        ).fetchone()
        if not sample or sample[0] == 0:
            return  # Already UUIDs — nothing to migrate

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
            config_dir = Path("eks/config")
        return SchemaToDDL.load_doc_base_schema(config_dir)

    def _get_boilerplate_prefixes(self) -> tuple:
        """
        Read boilerplate title prefixes from eks_doc_config.json
        → document_title_config → boilerplate_prefixes (SSOT).
        Falls back to class-level _BOILERPLATE_PREFIXES_FALLBACK.

        T1.99.165 (I196): Replaces hardcoded in-function list per SSOT rule.
        """
        try:
            loader = getattr(self.config, '_loader', None)
            if loader and hasattr(loader, 'config_dir'):
                config_dir = Path(loader.config_dir)
            else:
                config_dir = Path("eks/config")
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
        """Insert structural elements for a document. Returns count inserted."""
        conn = duckdb.connect(str(self.db_path))
        try:
            count = 0
            for el in elements:
                conn.execute("""
                    INSERT INTO document_elements
                    (doc_id, element_type, element_id, title, content, confidence, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, [
                    doc_id,
                    el.get("element_type", "unknown"),
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

    @log_depth
    def register_document(self, metadata: Dict[str, Any]) -> str:
        """
        Register a new document revision in the registry.
        Handles 'is_latest' flag update and JSON serialization for complex fields.

        T1.99.120: L3 null-tolerant — generates synthetic UNRESOLVED-{hash} key
        instead of raising KeyError when document_number is missing.
        """
        doc_number = metadata.get("document_number")
        revision = metadata.get("revision", "00")

        # T1.99.148 (I187): L3 — generate synthetic key via common library
        if not doc_number:
            file_path = metadata.get("file_path", "")
            synthetic_key = generate_synthetic_key(file_path)
            self.logger.warning(
                f"document_number missing — generating synthetic key {synthetic_key}",
                context="DocumentRegistry.register_document"
            )
            metadata["document_number"] = synthetic_key
            doc_number = synthetic_key
            if not revision:
                revision = "00"
                metadata["revision"] = revision

        # T1.99.150 (I186): id is now a pure UUID — business-key derived id is retired
        doc_id = str(uuid.uuid4())
        
        self.logger.info(f"Registering document: {doc_id}", context="DocumentRegistry.register_document")
        
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

            # T1.99.150 (I186): Pure INSERT — every call creates a new row unconditionally.
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
                self.logger.info(
                    f"Revision chain: {doc_id} supersedes {prev_doc_id}",
                    context="DocumentRegistry.register_document",
                )

            self.logger.status(f"Document {doc_id} registered successfully.")
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

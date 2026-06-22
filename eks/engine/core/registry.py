"""
Document Registry for EKS - Metadata DB CRUD interface using DuckDB.
DDL is auto-generated from JSON schema definitions via SchemaToDDL (T1.36).
"""
import duckdb
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
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
                "extraction_confidence", "extraction_notes", "verified_by"
            }

    @property
    def COLUMN_ALLOWLIST(self) -> set:
        return self._get_column_allowlist()

    def __init__(self, logger: Optional[EKSLogger] = None):
        self.config = ConfigRegistry()
        settings = self.config.registry_settings
        conn_str = settings.get("connection_string", "output/eks_registry.db")
        # Resolve relative paths relative to config directory
        loader = getattr(self.config, '_loader', None)
        if loader and hasattr(loader, 'config_dir'):
            config_dir = Path(loader.config_dir)
            self.db_path = (config_dir.parent / conn_str).resolve()
        else:
            self.db_path = Path(conn_str)
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
        finally:
            conn.close()

    def _load_doc_schema(self) -> Dict[str, Any]:
        """Load eks_doc_base_schema.json as fallback when loader is unavailable."""
        loader = getattr(self.config, '_loader', None)
        if loader and hasattr(loader, 'config_dir'):
            config_dir = Path(loader.config_dir)
        else:
            config_dir = Path("eks/config")
        return SchemaToDDL.load_doc_base_schema(config_dir)

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
        """
        doc_number = metadata["document_number"]
        revision = metadata["revision"]
        doc_id = f"{doc_number}-{revision}"
        
        self.logger.info(f"Registering document: {doc_id}", context="DocumentRegistry.register_document")
        
        # Serialize asset_tags if provided as list
        tags = metadata.get("asset_tags")
        if isinstance(tags, list):
            tags_json = json.dumps(tags)
        else:
            tags_json = tags

        conn = duckdb.connect(str(self.db_path))
        try:
            # 1. Clear 'is_latest' for older revisions of the same document number
            conn.execute("UPDATE documents SET is_latest = FALSE WHERE document_number = ?", [doc_number])
            
            # 2. Insert new revision
            conn.execute("""
                INSERT OR REPLACE INTO documents 
                (id, source_type, project_title, project_number, area, discipline, department, 
                 document_type, document_number, revision, status, is_latest, file_path, file_type,
                 created_by, checked_by, approved_by, originator_company, security_class,
                 asset_tags, page_count, extract_status, extraction_confidence, 
                 extraction_notes, verified_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                doc_id,
                metadata.get("source_type", "ingested"),
                metadata.get("project_title"),
                metadata.get("project_number"),
                metadata.get("area"),
                metadata.get("discipline"),
                metadata.get("department"),
                metadata.get("document_type"),
                doc_number,
                revision,
                metadata.get("status"),
                True,
                metadata.get("file_path"),
                metadata.get("file_type"),
                metadata.get("created_by"),
                metadata.get("checked_by"),
                metadata.get("approved_by"),
                metadata.get("originator_company"),
                metadata.get("security_class"),
                tags_json,
                metadata.get("page_count"),
                metadata.get("extract_status", "pending"),
                metadata.get("extraction_confidence"),
                metadata.get("extraction_notes"),
                metadata.get("verified_by")
            ])
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

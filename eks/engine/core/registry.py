"""
Document Registry for EKS - Metadata DB CRUD interface using DuckDB.
"""
import duckdb
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
from .config_registry import ConfigRegistry
from ..logging.logger import EKSLogger, log_depth

class DocumentRegistry:
    """
    Manages document metadata storage and retrieval.
    Backed by DuckDB (or PostgreSQL if configured).
    """
    COLUMN_ALLOWLIST = {
        "id", "project_title", "project_number", "area", "discipline", 
        "department", "document_type", "document_number", "revision", 
        "status", "is_latest", "file_path", "ingested_at", "source_type",
        "created_by", "checked_by", "approved_by", "originator_company",
        "security_class", "asset_tags", "page_count", "extract_status",
        "extraction_confidence", "extraction_notes", "verified_by"
    }

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
        """Initialize the metadata database table with the full extended schema."""
        self.logger.status(f"Initializing Document Registry at {self.db_path}")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = duckdb.connect(str(self.db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id VARCHAR PRIMARY KEY,
                source_type VARCHAR DEFAULT 'ingested',
                project_title VARCHAR,
                project_number VARCHAR,
                area VARCHAR,
                discipline VARCHAR,
                department VARCHAR,
                document_type VARCHAR,
                document_number VARCHAR,
                revision VARCHAR,
                status VARCHAR,
                is_latest BOOLEAN DEFAULT TRUE,
                file_path VARCHAR,
                ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by VARCHAR,
                checked_by VARCHAR,
                approved_by VARCHAR,
                originator_company VARCHAR,
                security_class VARCHAR,
                asset_tags JSON,
                page_count INTEGER,
                extract_status VARCHAR DEFAULT 'pending',
                extraction_confidence DOUBLE,
                extraction_notes TEXT,
                verified_by VARCHAR
            )
        """)
        conn.close()

    @log_depth
    def _migrate_schema(self):
        """Handle schema evolution by adding missing columns to existing tables."""
        conn = duckdb.connect(str(self.db_path))
        try:
            # Get existing columns
            res = conn.execute("PRAGMA table_info('documents')").fetchall()
            existing_cols = {row[1] for row in res}
            
            # Map of column to type (subset of full schema)
            new_cols = {
                "created_by": "VARCHAR",
                "checked_by": "VARCHAR",
                "approved_by": "VARCHAR",
                "originator_company": "VARCHAR",
                "security_class": "VARCHAR",
                "asset_tags": "JSON",
                "page_count": "INTEGER",
                "extract_status": "VARCHAR DEFAULT 'pending'",
                "extraction_confidence": "DOUBLE",
                "extraction_notes": "TEXT",
                "verified_by": "VARCHAR"
            }
            
            for col, col_type in new_cols.items():
                if col not in existing_cols:
                    self.logger.info(f"Migrating schema: Adding column '{col}' to documents table.")
                    conn.execute(f"ALTER TABLE documents ADD COLUMN {col} {col_type}")
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
                 document_type, document_number, revision, status, is_latest, file_path,
                 created_by, checked_by, approved_by, originator_company, security_class,
                 asset_tags, page_count, extract_status, extraction_confidence, 
                 extraction_notes, verified_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

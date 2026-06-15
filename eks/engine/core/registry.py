"""
Document Registry for EKS - Metadata DB CRUD interface using DuckDB.
"""
import duckdb
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
    def __init__(self, logger: Optional[EKSLogger] = None):
        self.config = ConfigRegistry()
        settings = self.config.registry_settings
        self.db_path = Path(settings.get("connection_string", "data/eks_registry.db"))
        self.logger = logger or EKSLogger("Registry", level=1)
        self._init_db()

    @log_depth
    def _init_db(self):
        """Initialize the metadata database table."""
        self.logger.status(f"Initializing Document Registry at {self.db_path}")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = duckdb.connect(str(self.db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id VARCHAR PRIMARY KEY,
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
                ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.close()

    @log_depth
    def register_document(self, metadata: Dict[str, Any]) -> str:
        """
        Register a new document revision in the registry.
        Handles 'is_latest' flag update for previous revisions.
        """
        doc_number = metadata["document_number"]
        revision = metadata["revision"]
        doc_id = f"{doc_number}-{revision}"
        
        self.logger.info(f"Registering document: {doc_id}", context="DocumentRegistry.register_document")
        
        conn = duckdb.connect(str(self.db_path))
        try:
            # 1. Clear 'is_latest' for older revisions of the same document number
            conn.execute("UPDATE documents SET is_latest = FALSE WHERE document_number = ?", [doc_number])
            
            # 2. Insert new revision
            conn.execute("""
                INSERT OR REPLACE INTO documents 
                (id, project_title, project_number, area, discipline, department, 
                 document_type, document_number, revision, status, is_latest, file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                doc_id,
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
                metadata.get("file_path")
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
    def list_documents(self, filters: Optional[Dict[str, Any]] = None, latest_only: bool = True) -> List[Dict[str, Any]]:
        """List documents with optional filtering."""
        conn = duckdb.connect(str(self.db_path))
        try:
            query = "SELECT * FROM documents WHERE 1=1"
            params = []
            
            if latest_only:
                query += " AND is_latest = TRUE"
            
            if filters:
                for k, v in filters.items():
                    query += f" AND {k} = ?"
                    params.append(v)
            
            res = conn.execute(query, params).fetchall()
            cols = [d[0] for d in conn.description]
            return [dict(zip(cols, row)) for row in res]
        finally:
            conn.close()

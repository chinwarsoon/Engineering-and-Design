"""
Revision Management for EKS - Logic for tracking and filtering document revisions.
"""
from typing import Any, Dict, List, Optional
from .registry import DocumentRegistry
from ..logging.logger import EKSLogger, log_depth

class RevisionManager:
    """
    Orchestrates revision-specific logic, such as finding the latest version
    or retrieving the full history of a document.
    """
    def __init__(self, registry: DocumentRegistry, logger: Optional[EKSLogger] = None):
        self.registry = registry
        self.logger = logger or EKSLogger("RevisionManager", level=1)

    @log_depth
    def get_latest_revision(self, document_number: str) -> Optional[Dict[str, Any]]:
        """Find the most recent revision for a document number."""
        return self.registry.get_document(document_number, revision=None)

    @log_depth
    def get_revision_history(self, document_number: str) -> List[Dict[str, Any]]:
        """Retrieve all revisions of a document, sorted by ingested_at."""
        all_revs = self.registry.list_documents(filters={"document_number": document_number}, latest_only=False)
        # DuckDB sort might be better, but we can sort in Python too
        return sorted(all_revs, key=lambda x: x.get("ingested_at", ""), reverse=True)

    @log_depth
    def is_latest(self, document_number: str, revision: str) -> bool:
        """Check if a specific revision is the current latest."""
        doc = self.registry.get_document(document_number, revision=revision)
        return doc.get("is_latest", False) if doc else False

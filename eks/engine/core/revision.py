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
        """Retrieve all revisions of a document, sorted by ingested_at DESC via SQL."""
        return self.registry.list_documents(
            filters={"document_number": document_number}, 
            latest_only=False,
            order_by="ingested_at DESC"
        )

    @log_depth
    def is_latest(self, document_number: str, revision: str) -> bool:
        """Check if a specific revision is the current latest."""
        doc = self.registry.get_document(document_number, revision=revision)
        return doc.get("is_latest", False) if doc else False

    @log_depth
    def _compare_revisions(self, rev_a: str, rev_b: str) -> int:
        """
        Compare two revision strings.
        Returns -1 if a < b, 0 if equal, 1 if a > b.
        Handles numeric, alphabetic, and mixed revision formats.
        """
        try:
            return (int(rev_a) > int(rev_b)) - (int(rev_a) < int(rev_b))
        except ValueError:
            pass
        a = rev_a.strip().upper()
        b = rev_b.strip().upper()
        if len(a) == 1 and len(b) == 1 and a.isalpha() and b.isalpha():
            return (a > b) - (a < b)
        return (a > b) - (a < b)

    @log_depth
    def detect_supersession(self, document_number: str, revision: str) -> Dict[str, Any]:
        """
        Detect supersession relationships for a (document_number, revision) pair.

        Queries the registry for existing documents with the same document_number,
        identifies the current is_latest revision, and determines if the given
        revision supersedes any existing document or is itself superseded.

        Returns:
            dict with keys:
                - has_supersession: bool — True if any existing document is affected
                - current_latest: Optional[Dict] — the current is_latest document (if any)
                - latest_revision: Optional[str] — revision number of current latest
                - supersedes: Optional[str] — doc_id of the document this revision supersedes
                - superseded_by: Optional[str] — doc_id that supersedes this revision
                - is_newer: bool — True if this revision is newer than current latest
                - is_same: bool — True if this revision matches current latest exactly
        """
        result: Dict[str, Any] = {
            "has_supersession": False,
            "current_latest": None,
            "latest_revision": None,
            "supersedes": None,
            "superseded_by": None,
            "is_newer": False,
            "is_same": False,
        }

        docs = self.registry.list_documents(
            filters={"document_number": document_number},
            latest_only=False,
        )
        if not docs:
            self.logger.info(
                f"No existing documents for {document_number} — no supersession",
                context="RevisionManager.detect_supersession",
            )
            return result

        current_latest = None
        for doc in docs:
            if doc.get("is_latest"):
                current_latest = doc
                break

        if not current_latest:
            self.logger.warning(
                f"No is_latest document found for {document_number} — cannot determine supersession",
                context="RevisionManager.detect_supersession",
            )
            return result

        result["current_latest"] = current_latest
        result["latest_revision"] = current_latest.get("revision", "00")

        cmp = self._compare_revisions(revision, current_latest.get("revision", "00"))

        if cmp > 0:
            result["has_supersession"] = True
            result["supersedes"] = current_latest["id"]
            result["is_newer"] = True
            self.logger.info(
                f"Revision {revision} supersedes {current_latest.get('revision', '00')} "
                f"for {document_number} (doc_id: {current_latest['id']})",
                context="RevisionManager.detect_supersession",
            )
        elif cmp == 0:
            result["is_same"] = True
            self.logger.info(
                f"Revision {revision} for {document_number} matches current latest — no change",
                context="RevisionManager.detect_supersession",
            )
        else:
            result["has_supersession"] = True
            result["superseded_by"] = current_latest["id"]
            self.logger.warning(
                f"Revision {revision} for {document_number} is superseded by "
                f"revision {current_latest.get('revision', '00')} (doc_id: {current_latest['id']})",
                context="RevisionManager.detect_supersession",
            )

        return result

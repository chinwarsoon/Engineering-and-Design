"""
Manual Review Manager for EKS - Review surface for flagged documents.
T1.40: Phase C manual review workflow.
"""
from typing import Any, Dict, List, Optional
from ..logging.logger import EKSLogger, log_depth
from .health_scorer import HealthScorer
from .structure_detector import StructureDetector


class ManualReviewManager:
    """
    Manages the manual review workflow for documents flagged by Phase C.
    Supports: querying flagged docs, metadata correction, element confirmation,
    score recalculation, and document locking.
    """

    def __init__(self, registry: Any, doc_config: Optional[Dict[str, Any]] = None,
                 logger: Optional[EKSLogger] = None):
        self.registry = registry
        self.doc_config = doc_config or {}
        self.logger = logger or EKSLogger("ManualReview", level=1)
        self.scorer = HealthScorer(logger=self.logger)
        self.detector = StructureDetector(logger=self.logger)

    @log_depth
    def get_flagged_documents(self, confidence_threshold: float = 0.70) -> List[Dict[str, Any]]:
        """
        Query documents where extract_status != 'success' or
        extraction_confidence < confidence_threshold.

        Returns list of document metadata dicts.
        """
        all_docs = self.registry.list_documents(latest_only=False)
        flagged = []
        for doc in all_docs:
            needs_review = False
            if doc.get("extract_status") != "success":
                needs_review = True
            conf = doc.get("extraction_confidence")
            if conf is not None and conf < confidence_threshold:
                needs_review = True
            if needs_review:
                flagged.append(doc)

        self.logger.info(
            f"Found {len(flagged)} flagged documents (threshold={confidence_threshold})",
            context="ManualReviewManager.get_flagged_documents"
        )
        return flagged

    @log_depth
    def correct_metadata(self, doc_id: str, updates: Dict[str, Any]) -> bool:
        """
        Correct document metadata fields.
        Allowed fields: project_title, project_number, area, discipline, department,
        document_type, status, created_by, checked_by, approved_by, originator_company,
        security_class, asset_tags, verified_by.

        Returns True if update succeeded.
        """
        allowed_fields = {
            "project_title", "project_number", "area", "discipline", "department",
            "document_type", "status", "created_by", "checked_by", "approved_by",
            "originator_company", "security_class", "asset_tags", "verified_by",
        }
        filtered = {k: v for k, v in updates.items() if k in allowed_fields}
        if not filtered:
            self.logger.warning(
                f"No valid fields to update for {doc_id}",
                context="ManualReviewManager.correct_metadata"
            )
            return False

        import duckdb, json
        conn = duckdb.connect(str(self.registry.db_path))
        try:
            set_parts = []
            params = []
            for k, v in filtered.items():
                if k == "asset_tags" and isinstance(v, list):
                    v = json.dumps(v)
                set_parts.append(f"{k} = ?")
                params.append(v)
            params.append(doc_id)
            sql = f"UPDATE documents SET {', '.join(set_parts)} WHERE id = ?"
            conn.execute(sql, params)
            self.logger.info(
                f"Updated metadata for {doc_id}: {list(filtered.keys())}",
                context="ManualReviewManager.correct_metadata"
            )
            return True
        except Exception as e:
            self.logger.error(
                f"Failed to update metadata for {doc_id}: {e}",
                context="ManualReviewManager.correct_metadata"
            )
            return False
        finally:
            conn.close()

    @log_depth
    def confirm_elements(self, doc_id: str, elements: List[Dict[str, Any]]) -> int:
        """
        Confirm and store structural elements for a document.
        Replaces any existing elements for this doc_id.
        Returns count of elements stored.
        """
        self.registry.delete_elements(doc_id)
        count = self.registry.store_elements(doc_id, elements)
        self.logger.info(
            f"Confirmed {count} elements for {doc_id}",
            context="ManualReviewManager.confirm_elements"
        )
        return count

    @log_depth
    def recalculate_score(self, doc_id: str, elements: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Recalculate health score for a document.
        If elements not provided, retrieves from registry.
        Returns score dict.
        """
        doc = self.registry.get_document(doc_id.rsplit("-", 1)[0], revision=doc_id.rsplit("-", 1)[1])
        if not doc:
            self.logger.warning(f"Document not found: {doc_id}", context="ManualReviewManager.recalculate_score")
            return {}

        if elements is None:
            elements = self.registry.get_elements(doc_id)

        score = self.scorer.score(doc, elements)
        self.logger.info(
            f"Recalculated score for {doc_id}: {score.get('overall', 'N/A')}",
            context="ManualReviewManager.recalculate_score"
        )
        return score

    @log_depth
    def lock_document(self, doc_id: str, verified_by: str) -> bool:
        """
        Lock a document by setting verified_by and extract_status to 'success'.
        This marks the document as reviewed and ready for Phase 2.
        Returns True if lock succeeded.
        """
        import duckdb
        conn = duckdb.connect(str(self.registry.db_path))
        try:
            conn.execute(
                "UPDATE documents SET verified_by = ?, extract_status = 'success' WHERE id = ?",
                [verified_by, doc_id]
            )
            self.logger.status(f"Document {doc_id} locked by {verified_by}")
            return True
        except Exception as e:
            self.logger.error(
                f"Failed to lock {doc_id}: {e}",
                context="ManualReviewManager.lock_document"
            )
            return False
        finally:
            conn.close()

    @log_depth
    def get_review_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the review status across all documents.
        Returns dict with counts by extract_status.
        """
        import duckdb
        conn = duckdb.connect(str(self.registry.db_path))
        try:
            res = conn.execute(
                "SELECT extract_status, COUNT(*) FROM documents GROUP BY extract_status"
            ).fetchall()
            status_counts = {row[0]: row[1] for row in res}

            total = sum(status_counts.values())
            flagged = sum(v for k, v in status_counts.items() if k != "success")

            return {
                "total": total,
                "status_counts": status_counts,
                "flagged": flagged,
                "reviewed": status_counts.get("success", 0),
            }
        finally:
            conn.close()

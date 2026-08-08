"""
Manual Review Manager for EKS - Review surface for flagged documents.
T1.40: Phase C manual review workflow.

Revision: 0.2
Date: 2026-08-08
Author: opencode
Summary: I286 (T1.237) - schema-driven correct_metadata: allowed_fields derived
from doc_config.column_processing (no hardcoded set, AGENTS.md §16); manual
source classification via manual_review marker; JSON serialization for
json_column list values; enum (lifecycle_stage_code) / ISO date / json list
value validation rejecting bad values; unknown/control column names rejected.
Revision 0.1: initial T1.40 implementation.
"""
from typing import Any, Dict, List, Optional, Set
from datetime import datetime, date
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
                 base_schema: Optional[Dict[str, Any]] = None,
                 logger: Optional[EKSLogger] = None):
        self.registry = registry
        self.doc_config = doc_config or {}
        self.base_schema = base_schema or {}
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

        I286 (T1.237): schema-driven. The set of allowed fields is derived from
        ``doc_config.column_processing`` (SSOT, AGENTS.md §16) — never a
        hardcoded list. Column entries carrying ``manual_review: true`` mark
        Manual-source columns (Appendix B §B4); derivable columns remain
        review-allowed. Values are validated per column type: ``json_column``
        values must be lists (serialized via ``json.dumps``), ``date_column``
        values must parse as ISO dates, ``code_column`` entries with an
        ``enum_reference`` (e.g. ``lifecycle_stage_code``) must be in the enum.
        Unknown/control column names are rejected outright.

        Returns True if update succeeded.
        """
        import duckdb, json

        col_proc = self._column_processing()
        allowed_fields = set(col_proc.keys())
        unknown = [k for k in updates if k not in allowed_fields]
        if unknown:
            self.logger.warning(
                f"Rejected unknown/control fields for {doc_id}: {sorted(unknown)}",
                context="ManualReviewManager.correct_metadata"
            )
            return False

        filtered = {k: v for k, v in updates.items() if k in allowed_fields}
        if not filtered:
            self.logger.warning(
                f"No valid fields to update for {doc_id}",
                context="ManualReviewManager.correct_metadata"
            )
            return False

        # Value validation + serialization (reject bad values, generalize asset_tags)
        prepared: Dict[str, Any] = {}
        for k, v in filtered.items():
            entry = col_proc.get(k, {})
            if not self._validate_field_value(k, v, entry):
                self.logger.warning(
                    f"Rejected invalid value for '{k}' on {doc_id}: {v!r}",
                    context="ManualReviewManager.correct_metadata"
                )
                return False
            if isinstance(v, list):
                prepared[k] = json.dumps(v)
            else:
                prepared[k] = v

        conn = duckdb.connect(str(self.registry.db_path))
        try:
            set_parts = []
            params = []
            for k, v in prepared.items():
                set_parts.append(f"{k} = ?")
                params.append(v)
            params.append(doc_id)
            sql = f"UPDATE documents SET {', '.join(set_parts)} WHERE id = ?"
            conn.execute(sql, params)
            self.logger.info(
                f"Updated metadata for {doc_id}: {list(prepared.keys())}",
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

    def _column_processing(self) -> Dict[str, Any]:
        """Return the schema-driven column_processing map.

        Raises a descriptive error if ``doc_config.column_processing`` is absent
        — the review allowlist is derived from it and must never fall back to a
        second source of truth (AGENTS.md §16).
        """
        cp = self.doc_config.get("column_processing") if isinstance(self.doc_config, dict) else None
        if not isinstance(cp, dict) or not cp:
            raise ValueError(
                "ManualReviewManager.correct_metadata requires "
                "doc_config['column_processing'] (schema-driven SSOT, AGENTS.md §16). "
                "No hardcoded allowlist fallback."
            )
        return cp

    def _validate_field_value(self, name: str, value: Any, entry: Dict[str, Any]) -> bool:
        """Validate a single review update value against its column config.

        Rules (I286):
        - ``json_column`` must receive a list (serialized by caller).
        - ``date_column`` must parse as an ISO date.
        - ``code_column`` with an ``enum_reference`` (e.g. lifecycle_stage_code)
          must be a member of the referenced enum.
        - all other text/numeric columns accept the raw value.
        """
        if isinstance(value, list):
            return entry.get("column_type") == "json_column"
        col_type = entry.get("column_type")
        if col_type == "json_column":
            return False
        if col_type == "date_column":
            return self._is_iso_date(value)
        if col_type == "code_column":
            enum_name = self._enum_reference_for(entry)
            if not enum_name:
                return True
            return self._is_in_enum(value, enum_name)
        return True

    @staticmethod
    def _is_iso_date(value: Any) -> bool:
        """True when *value* is a date/datetime or an ISO-8601 date string."""
        if isinstance(value, (datetime, date)):
            return True
        if not isinstance(value, str):
            return False
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
            return True
        except ValueError:
            return False

    def _enum_reference_for(self, entry: Dict[str, Any]) -> Optional[str]:
        """Return the enum name referenced by a code_column entry, if any."""
        validation = entry.get("validation")
        if isinstance(validation, list):
            for rule in validation:
                if isinstance(rule, dict) and rule.get("type") == "enum_reference":
                    ref = rule.get("reference") or rule.get("ref")
                    if isinstance(ref, str):
                        return ref
        schema_ref = entry.get("schema_ref")
        if isinstance(schema_ref, str) and schema_ref:
            return schema_ref
        return None

    def _enum_values(self, enum_name: str) -> Optional[List[Any]]:
        """Resolve enum values from the base schema definitions (SSOT)."""
        defs = self.base_schema.get("definitions", {}) if isinstance(self.base_schema, dict) else {}
        entry = defs.get(enum_name)
        if isinstance(entry, dict) and isinstance(entry.get("enum"), list):
            return entry["enum"]
        return None

    def _is_in_enum(self, value: Any, enum_name: str) -> bool:
        """True when *value* is in the named enum (schema-driven, no hardcode)."""
        enum_vals = self._enum_values(enum_name)
        if enum_vals is None:
            return True
        return value in enum_vals

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

        score = self.scorer.score(doc, structural_elements=elements)
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

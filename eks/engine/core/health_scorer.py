"""
EKS Health Scorer - 6-dimension per-document health scoring.

Revision: 0.2
Date: 2026-07-19
Author: CodeBuddy
Summary: 0.2: T1.99.187 (I214) — added score_from_input(HealthInput) → HealthOutput
         contract method for Appendix F compliance. score() unchanged for backward
         compatibility.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from ..logging.logger import EKSLogger, log_depth

TIER_1_COLUMNS = {"project_number", "discipline", "document_type", "document_number", "revision", "asset_tags"}
TIER_2_COLUMNS = {"project_title", "area", "status", "created_by", "checked_by", "approved_by", "originator_company", "page_count",
                   "document_title", "lifecycle_stage", "revision_date", "project_phase",
                   "contract_package", "issued_date", "responsible_engineer", "total_sheets",
                   "supersedes", "superseded_by", "file_type"}
TIER_3_COLUMNS = {"department", "security_class", "verified_by",
                   "file_size", "file_hash", "embedded_title", "embedded_subject",
                   "embedded_creator_app", "embedded_producer",
                   "revision_description", "embedded_revision_number",
                   "references_documents", "language", "vendor_name"}
ALL_SCOABLE = TIER_1_COLUMNS | TIER_2_COLUMNS | TIER_3_COLUMNS

TIER_1_WEIGHT = 2.0
TIER_2_WEIGHT = 1.0
TIER_3_WEIGHT = 0.5

COMPLETENESS_WEIGHT = 0.20
CONFIDENCE_WEIGHT = 0.20
STRUCTURAL_WEIGHT = 0.20
SOURCE_WEIGHT = 0.15
XREF_WEIGHT = 0.15
CONSISTENCY_WEIGHT = 0.10

COVER_TYPE_SOURCE_SCORES = {
    "A": 1.0,
    "B": 0.7,
    "C": 0.3,
    "D": 0.9,
    "E": 0.8,
    "F": 0.0,
}

EXPECTED_ELEMENTS_BY_TYPE = {
    "A": {"cover_page", "revision_table", "sections", "image", "table"},
    "B": {"cover_page", "revision_table", "sections", "image", "table"},
    "C": set(),
    "D": {"cover_page", "sections"},
    "E": {"cover_page", "sections", "table"},
}


class HealthScorer:
    """
    Per-document 6-dimension health scoring engine.
    Dimensions: completeness, extraction confidence, structural completeness,
                source quality, cross-reference quality, consistency.
    """

    def __init__(self, logger: Optional[EKSLogger] = None):
        self.logger = logger or EKSLogger("HealthScorer", level=2)

    @log_depth
    def score(self, metadata: Dict[str, Any],
              extraction_results: Optional[Dict[str, Any]] = None,
              structural_elements: Optional[List[Dict[str, Any]]] = None,
              cover_type: Optional[str] = None,
              xref_results: Optional[Dict[str, Any]] = None,
              consistency_violations: int = 0,
              _tampering_checks: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Compute the full 6-dimension health score for a single document.

        Parameters
        ----------
        metadata : dict
            Document metadata dict with all registry columns.
        extraction_results : dict, optional
            Per-field extraction confidence scores {field: score}.
        structural_elements : list of dict, optional
            Detected structural elements from structure_detector.
        cover_type : str, optional
            Cover sheet type letter (A, B, C, D, E).
        xref_results : dict, optional
            Cross-reference results with 'checks_passed' and 'checks_total'.
        consistency_violations : int
            Number of cross-field consistency violations.

        Returns
        -------
        dict with keys: health_score, dimensions, missing_columns,
                        tier1_fields, extract_status
        """
        completeness = self._score_completeness(metadata)
        extraction_conf = self._score_extraction_confidence(metadata, extraction_results)
        structural = self._score_structural(structural_elements, cover_type)
        source = self._score_source_quality(cover_type, metadata=metadata)
        xref = self._score_xref_quality(xref_results)
        consistency_mod = self._score_consistency(consistency_violations,
                                                   metadata=metadata,
                                                   tampering_checks=_tampering_checks)

        health_score = (
            completeness["score"] * COMPLETENESS_WEIGHT +
            extraction_conf["score"] * CONFIDENCE_WEIGHT +
            structural["score"] * STRUCTURAL_WEIGHT +
            source["score"] * SOURCE_WEIGHT +
            xref["score"] * XREF_WEIGHT +
            1.0 * CONSISTENCY_WEIGHT
        ) * consistency_mod

        health_score = max(0.0, min(1.0, health_score))

        if health_score >= 0.90:
            extract_status = "success"
        elif health_score >= 0.70:
            extract_status = "success"
        elif health_score >= 0.50:
            extract_status = "partial"
        elif health_score >= 0.20:
            extract_status = "partial"
        else:
            extract_status = "failed"

        populated = sum(1 for col in ALL_SCOABLE if metadata.get(col) not in (None, "", "NA"))
        tier1_populated = sum(1 for col in TIER_1_COLUMNS if metadata.get(col) not in (None, "", "NA"))

        return {
            "health_score": round(health_score, 4),
            "extract_status": extract_status,
            "dimensions": {
                "completeness": completeness,
                "extraction_confidence": extraction_conf,
                "structural_completeness": structural,
                "source_quality": source,
                "xref_quality": xref,
                "consistency": {"score": round(consistency_mod, 4), "violations": consistency_violations},
            },
            "missing_columns": [col for col in ALL_SCOABLE if metadata.get(col) in (None, "", "NA")],
            "tier1_fields": {"populated": tier1_populated, "total": len(TIER_1_COLUMNS)},
        }

    def _score_completeness(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Dimension 1: fraction of scorable columns populated."""
        populated = sum(1 for col in ALL_SCOABLE if metadata.get(col) not in (None, "", "NA"))
        total = len(ALL_SCOABLE)
        score = populated / total if total > 0 else 0.0
        return {"score": round(score, 4), "populated": populated, "total": total}

    def _score_extraction_confidence(self, metadata: Dict[str, Any],
                                      extraction_results: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Dimension 2: per-column match quality weighted by tier."""
        if extraction_results is None:
            extraction_results = {}

        def field_score(col: str) -> float:
            if col in extraction_results:
                return extraction_results[col]
            val = metadata.get(col)
            if val not in (None, "", "NA"):
                return 1.0
            return 0.0

        def tier_average(cols: Set[str], weight: float) -> float:
            scores = [field_score(c) for c in cols]
            return sum(scores) * weight / (len(cols) * weight) if cols else 0.0

        t1_avg = tier_average(TIER_1_COLUMNS, TIER_1_WEIGHT)
        t2_avg = tier_average(TIER_2_COLUMNS, TIER_2_WEIGHT)
        t3_avg = tier_average(TIER_3_COLUMNS, TIER_3_WEIGHT)

        max_possible = (
            len(TIER_1_COLUMNS) * 1.0 * TIER_1_WEIGHT +
            len(TIER_2_COLUMNS) * 1.0 * TIER_2_WEIGHT +
            len(TIER_3_COLUMNS) * 1.0 * TIER_3_WEIGHT
        )
        actual = (
            sum(field_score(c) * TIER_1_WEIGHT for c in TIER_1_COLUMNS) +
            sum(field_score(c) * TIER_2_WEIGHT for c in TIER_2_COLUMNS) +
            sum(field_score(c) * TIER_3_WEIGHT for c in TIER_3_COLUMNS)
        )
        score = actual / max_possible if max_possible > 0 else 0.0
        return {
            "score": round(score, 4),
            "tier1_avg": round(t1_avg, 4),
            "tier2_avg": round(t2_avg, 4),
            "tier3_avg": round(t3_avg, 4),
        }

    def _score_structural(self, structural_elements: Optional[List[Dict[str, Any]]],
                           cover_type: Optional[str]) -> Dict[str, Any]:
        """Dimension 3: fraction of expected structural elements detected."""
        cover = cover_type or "C"
        expected = EXPECTED_ELEMENTS_BY_TYPE.get(cover, set())
        if not expected:
            return {"score": 1.0, "detected": 0, "expected": 0, "elements": []}

        detected_elements = set()
        if structural_elements:
            for el in structural_elements:
                detected_elements.add(el.get("element_type", ""))
        detected = detected_elements & expected
        score = len(detected) / len(expected) if expected else 1.0
        return {"score": round(score, 4), "detected": len(detected), "expected": len(expected), "elements": sorted(detected)}

    def _score_source_quality(self, cover_type: Optional[str],
                               metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Dimension 4: cover sheet type quality baseline + file property bonus.

        T1.99.137: If embedded_creator_app is non-null, add +0.05 bonus
        (confirms the file was generated by a known authoring tool).
        """
        score = COVER_TYPE_SOURCE_SCORES.get(cover_type, 0.3) if cover_type else 0.3
        bonus = 0.0
        detail = {"type": cover_type or "unknown", "bonus": bonus, "bonus_reason": None}

        if metadata and metadata.get("embedded_creator_app") not in (None, "", "NA"):
            bonus = 0.05
            detail["bonus"] = bonus
            detail["bonus_reason"] = f"embedded_creator_app: {metadata['embedded_creator_app']}"

        final_score = min(1.0, score + bonus)
        detail["score"] = final_score
        return detail

    def _score_xref_quality(self, xref_results: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Dimension 5: cross-reference validation quality."""
        if not xref_results:
            return {"score": 1.0, "checks_passed": 0, "checks_total": 0}
        passed = xref_results.get("checks_passed", 0)
        total = xref_results.get("checks_total", 0)
        score = passed / total if total > 0 else 1.0
        return {"score": round(score, 4), "checks_passed": passed, "checks_total": total}

    def _score_consistency(self, violations: int,
                            metadata: Optional[Dict[str, Any]] = None,
                            tampering_checks: Optional[Dict[str, Any]] = None) -> float:
        """Consistency modifier: penalty per violation + file timestamp drift check.

        T1.99.137: If both file_modified_at (OS) and embedded_modified_date are
        non-null, compute time delta; if |delta| > 24 hours, add +1 violation
        (possible tampering or stale file copy).
        """
        total_violations = violations
        if metadata:
            os_mod_str = metadata.get("file_modified_at")
            emb_mod_str = metadata.get("embedded_modified_date")
            if os_mod_str and emb_mod_str:
                try:
                    os_mod = datetime.fromisoformat(os_mod_str.replace("Z", "+00:00"))
                    emb_mod = datetime.fromisoformat(emb_mod_str.replace("Z", "+00:00"))
                    delta = abs((os_mod - emb_mod).total_seconds())
                    if delta > 86400:  # 24 hours in seconds
                        total_violations += 1
                except (ValueError, TypeError):
                    pass  # Unparseable date strings are ignored — not a violation

        if tampering_checks:
            total_violations += tampering_checks.get("count", 0)

        return round(max(0.0, 1.0 - 0.1 * total_violations), 4)

    @log_depth
    def format_notes(self, result: Dict[str, Any]) -> str:
        """Format the health scoring result as a JSON string for extraction_notes."""
        import json
        return json.dumps({
            "health_score": result["health_score"],
            "dimensions": result["dimensions"],
            "missing_columns": result["missing_columns"],
            "tier1_fields": result["tier1_fields"],
        }, default=str)

    @log_depth
    def score_from_input(self, health_input: "HealthInput") -> "HealthOutput":
        """T1.99.187 (I214): Score from a HealthInput contract → HealthOutput.

        Wraps the existing ``score()`` method in the Appendix F HealthInput/
        HealthOutput contract pattern. Lazy-imports HealthOutput to avoid
        circular dependencies.

        Args:
            health_input: HealthInput with document, elements, etc.

        Returns:
            HealthOutput with overall score and per-dimension breakdown.
        """
        from .io_contracts import HealthOutput
        doc = health_input.document or {}
        result = self.score(
            doc,
            structural_elements=health_input.elements or None,
        )
        return HealthOutput(
            run_id=health_input.run_id,
            status="SUCCESS",
            overall=result.get("health_score", 0.0),
            dimensions={
                k: v.get("score", v) if isinstance(v, dict) else v
                for k, v in result.get("dimensions", {}).items()
            },
            metadata=result,
        )

    @log_depth
    def score_batch(self, documents: List[Dict[str, Any]],
                     extraction_results: Optional[Dict[str, Any]] = None,
                     cover_types: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Score multiple documents and compute pipeline-level metrics.
        """
        if cover_types is None:
            cover_types = {}
        doc_scores = []
        for doc in documents:
            doc_id = doc.get("id") or doc.get("document_number", "?")
            score_result = self.score(
                doc,
                extraction_results=extraction_results,
                structural_elements=doc.get("_elements"),
                cover_type=cover_types.get(doc_id),
                consistency_violations=doc.get("_consistency_violations", 0),
            )
            doc_scores.append(score_result)

        avg_health = sum(s["health_score"] for s in doc_scores) / len(doc_scores) if doc_scores else 0.0
        return {
            "avg_document_health": round(avg_health, 4),
            "total_documents": len(doc_scores),
            "by_status": {
                "success": sum(1 for s in doc_scores if s["extract_status"] == "success"),
                "partial": sum(1 for s in doc_scores if s["extract_status"] == "partial"),
                "failed": sum(1 for s in doc_scores if s["extract_status"] == "failed"),
            },
        }

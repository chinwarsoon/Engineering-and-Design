"""
EKS Health Scorer - 6-dimension per-document health scoring.

Revision: 0.3
Date: 2026-08-07
Author: CodeBuddy
Summary: 0.3: I284 — schema-driven type-aware health scoring. Tier sets and
         weights are read from column_processing (scoring_tier) and
         health_scoring.weight_tiers instead of module-level hardcoded
         frozensets. COVER_TYPE_SOURCE_SCORES migrated to
         document_templates[].source_quality_score with a schema default
         (health_scoring.default_source_quality_scores) fallback. The scorer
         is now class-aware (class_id) and template-aware (template_id).
         0.2: T1.99.187 (I214) — added score_from_input(HealthInput) → HealthOutput
         contract method for Appendix F compliance. score() unchanged for backward
         compatibility.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple

from ..logging.logger import EKSLogger, log_depth

# ---------------------------------------------------------------------------
# I284: config-less fallback (legacy literals).
#
# These are retained ONLY for callers that construct HealthScorer without a
# schema-driven column_config (e.g. the standalone health_cli.py and
# review_manager.py). The primary pipeline path always supplies
# column_config / weight_tiers / default_source_quality_scores loaded from
# eks_doc_config.json, so no scoring-policy constant is hardcoded there.
# ---------------------------------------------------------------------------
_FALLBACK_TIER_1 = {"project_number", "discipline", "document_type", "document_number", "revision", "asset_tags"}
_FALLBACK_TIER_2 = {"project_title", "area", "status", "created_by", "checked_by", "approved_by", "originator_company", "page_count",
                    "document_title", "lifecycle_stage", "revision_date", "project_phase",
                    "contract_package", "issued_date", "responsible_engineer", "total_sheets",
                    "supersedes", "superseded_by", "file_type"}
_FALLBACK_TIER_3 = {"department", "security_class", "verified_by",
                    "file_size", "file_hash", "embedded_title", "embedded_subject",
                    "embedded_creator_app", "embedded_producer",
                    "revision_description", "embedded_revision_number",
                    "references_documents", "language", "vendor_name"}

_FALLBACK_WEIGHT_TIERS = {"tier1": 2.0, "tier2": 1.0, "tier3": 0.5}
_FALLBACK_SOURCE_SCORES = {"A": 1.0, "B": 0.7, "C": 0.3, "D": 0.9, "E": 0.8, "F": 0.0}

COMPLETENESS_WEIGHT = 0.20
CONFIDENCE_WEIGHT = 0.20
STRUCTURAL_WEIGHT = 0.20
SOURCE_WEIGHT = 0.15
XREF_WEIGHT = 0.15
CONSISTENCY_WEIGHT = 0.10

# I279 (T1.213): EXPECTED_ELEMENTS_BY_TYPE is derived from the template
# registry (document_templates) when available, instead of being hardcoded.
# The legacy literal below is retained only as a scoring-policy fallback for
# callers that construct HealthScorer without a template registry.
_EXPECTED_ELEMENTS_BY_TYPE_FALLBACK = {
    "A": {"cover_page", "revision_table", "section", "image", "table"},
    "B": {"cover_page", "revision_table", "section", "image", "table"},
    "C": set(),
    "D": {"cover_page", "section"},
    "E": {"cover_page", "section", "table"},
}


class HealthScorer:
    """
    Per-document 6-dimension health scoring engine.

    Dimensions: completeness, extraction confidence, structural completeness,
                source quality, cross-reference quality, consistency.

    I284: type-aware and template-aware. Tier sets are derived per document
    class from column_config (column_processing.scoring_tier +
    applies_to_document_types); source quality reads
    document_templates[].source_quality_score with a schema default fallback.
    """

    def __init__(self, logger: Optional[EKSLogger] = None,
                 document_templates: Optional[Dict[str, Any]] = None,
                 column_config: Optional[Dict[str, Any]] = None,
                 weight_tiers: Optional[Dict[str, float]] = None,
                 default_source_quality_scores: Optional[Dict[str, float]] = None):
        self.logger = logger or EKSLogger("HealthScorer", level=2)
        self.document_templates = document_templates or {}
        # I284: schema-driven column/tier/weight configuration. When omitted,
        # fall back to the legacy literals above (config-less callers only).
        self._column_config = column_config or {}
        self._weight_tiers = dict(weight_tiers or _FALLBACK_WEIGHT_TIERS)
        self._default_source_quality_scores = dict(
            default_source_quality_scores or _FALLBACK_SOURCE_SCORES)
        self._expected_elements_by_type = self._build_expected_elements_map()
        self._template_source_quality = self._build_template_source_quality_map()

    # ------------------------------------------------------------------
    # I284: schema-driven helpers
    # ------------------------------------------------------------------
    def _build_template_source_quality_map(self) -> Dict[str, Dict[str, float]]:
        """Build {template_id: {cover_type: score}} from document_templates."""
        result: Dict[str, Dict[str, float]] = {}
        for tpl_id, tpl in self.document_templates.items():
            sq = tpl.get("source_quality_score") if isinstance(tpl, dict) else None
            if isinstance(sq, dict):
                result[tpl_id] = sq
        return result

    def _column_tier(self, col: str, class_id: Optional[str]) -> Optional[str]:
        """Return the effective tier for a column under a document class.

        Returns None when the column is excluded or not claimed by the class,
        i.e. it produces no score. When column_config is absent, returns the
        legacy fallback tier (config-less caller path).
        """
        if not self._column_config:
            if col in _FALLBACK_TIER_1:
                return "tier1"
            if col in _FALLBACK_TIER_2:
                return "tier2"
            if col in _FALLBACK_TIER_3:
                return "tier3"
            return None
        cfg = self._column_config.get(col)
        if not isinstance(cfg, dict):
            return None
        tier = cfg.get("scoring_tier")
        if tier == "excluded":
            return None
        claimed = cfg.get("applies_to_document_types")
        if claimed is not None and class_id not in claimed:
            return None
        return tier if tier in ("tier1", "tier2", "tier3") else None

    def _column_required(self, col: str, class_id: Optional[str]) -> bool:
        """Whether a column is REQUIRED (missing penalises) for the class.

        Only meaningful for non-excluded, claimed columns. When column_config
        is absent, treat all fallback-scorable columns as required to preserve
        legacy behaviour (config-less caller path).
        """
        if not self._column_config:
            return True
        cfg = self._column_config.get(col)
        if not isinstance(cfg, dict):
            return False
        return bool(cfg.get("required", False))

    def _resolve_tiers_for_class(self, class_id: Optional[str]) -> Tuple[Set[str], Set[str], Set[str]]:
        """Resolve (tier1, tier2, tier3) column sets for a document class.

        Only claimed, non-excluded columns participate. Optional (required=false)
        columns are excluded from the scorable sets because their weight is 0.
        """
        t1: Set[str] = set()
        t2: Set[str] = set()
        t3: Set[str] = set()
        if not self._column_config:
            return set(_FALLBACK_TIER_1), set(_FALLBACK_TIER_2), set(_FALLBACK_TIER_3)
        for col, cfg in self._column_config.items():
            if not isinstance(cfg, dict):
                continue
            tier = cfg.get("scoring_tier")
            if tier == "excluded":
                continue
            claimed = cfg.get("applies_to_document_types")
            if claimed is not None and class_id not in claimed:
                continue
            if not cfg.get("required", False):
                continue  # I284: required=false → weight 0, not scored
            if tier == "tier1":
                t1.add(col)
            elif tier == "tier2":
                t2.add(col)
            elif tier == "tier3":
                t3.add(col)
        return t1, t2, t3

    def _scorable_columns(self, class_id: Optional[str]) -> Set[str]:
        """Union of claimed, non-excluded, required columns for the class."""
        t1, t2, t3 = self._resolve_tiers_for_class(class_id)
        return t1 | t2 | t3

    # ------------------------------------------------------------------
    # I279: structural element expectations (unchanged from 0.2)
    # ------------------------------------------------------------------
    def _build_expected_elements_map(self) -> Dict[str, Set[str]]:
        """Derive cover-type → expected elements from the template registry."""
        if not self.document_templates:
            return {k: set(v) for k, v in _EXPECTED_ELEMENTS_BY_TYPE_FALLBACK.items()}
        result: Dict[str, Set[str]] = {}
        for tpl in self.document_templates.values():
            if not isinstance(tpl, dict):
                continue
            cover = tpl.get("cover_type", "C")
            elements = set(tpl.get("expected_elements", []))
            result.setdefault(cover, set()).update(elements)
        return result

    # ------------------------------------------------------------------
    # Public scoring entry points
    # ------------------------------------------------------------------
    @log_depth
    def score(self, metadata: Dict[str, Any],
              extraction_results: Optional[Dict[str, Any]] = None,
              structural_elements: Optional[List[Dict[str, Any]]] = None,
              cover_type: Optional[str] = None,
              xref_results: Optional[Dict[str, Any]] = None,
              consistency_violations: int = 0,
              _tampering_checks: Optional[Dict[str, Any]] = None,
              class_id: Optional[str] = None,
              template_id: Optional[str] = None) -> Dict[str, Any]:
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
        class_id : str, optional
            I284: resolved document class id for type-aware tier scoring.
        template_id : str, optional
            I284: resolved template id for template-scoped source quality.

        Returns
        -------
        dict with keys: health_score, dimensions, missing_columns,
                        tier1_fields, extract_status
        """
        class_id = class_id or metadata.get("class_id") or metadata.get("document_class")
        template_id = template_id or metadata.get("template_id")

        completeness = self._score_completeness(metadata, class_id)
        extraction_conf = self._score_extraction_confidence(metadata, extraction_results, class_id)
        structural = self._score_structural(structural_elements, cover_type)
        source = self._score_source_quality(cover_type, metadata=metadata, template_id=template_id)
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

        if health_score >= 0.70:
            extract_status = "success"
        elif health_score >= 0.50:
            extract_status = "partial"
        elif health_score >= 0.20:
            extract_status = "partial"
        else:
            extract_status = "failed"

        scorable = self._scorable_columns(class_id)
        t1, _, _ = self._resolve_tiers_for_class(class_id)
        populated = sum(1 for col in scorable if metadata.get(col) not in (None, "", "NA"))
        tier1_populated = sum(1 for col in t1 if metadata.get(col) not in (None, "", "NA"))

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
            "missing_columns": [col for col in scorable if metadata.get(col) in (None, "", "NA")],
            "tier1_fields": {"populated": tier1_populated, "total": len(t1)},
        }

    # ------------------------------------------------------------------
    # Dimension scorers
    # ------------------------------------------------------------------
    def _score_completeness(self, metadata: Dict[str, Any],
                            class_id: Optional[str] = None) -> Dict[str, Any]:
        """Dimension 1: fraction of required scorable columns populated.

        I284: only claimed, non-excluded, required columns are scorable.
        Optional columns (weight 0) do not participate.
        """
        scorable = self._scorable_columns(class_id)
        populated = sum(1 for col in scorable if metadata.get(col) not in (None, "", "NA"))
        total = len(scorable)
        score = populated / total if total > 0 else 0.0
        return {"score": round(score, 4), "populated": populated, "total": total}

    def _score_extraction_confidence(self, metadata: Dict[str, Any],
                                     extraction_results: Optional[Dict[str, Any]] = None,
                                     class_id: Optional[str] = None) -> Dict[str, Any]:
        """Dimension 2: per-column match quality weighted by tier.

        I284: tier sets and weights are class/schema-driven. Only required
        columns participate (optional → weight 0 → no contribution).
        """
        if extraction_results is None:
            extraction_results = {}

        def field_score(col: str) -> float:
            if col in extraction_results:
                return extraction_results[col]
            val = metadata.get(col)
            if val not in (None, "", "NA"):
                return 1.0
            return 0.0

        t1, t2, t3 = self._resolve_tiers_for_class(class_id)
        w1 = self._weight_tiers.get("tier1", 2.0)
        w2 = self._weight_tiers.get("tier2", 1.0)
        w3 = self._weight_tiers.get("tier3", 0.5)

        max_possible = (
            len(t1) * 1.0 * w1 +
            len(t2) * 1.0 * w2 +
            len(t3) * 1.0 * w3
        )
        actual = (
            sum(field_score(c) * w1 for c in t1) +
            sum(field_score(c) * w2 for c in t2) +
            sum(field_score(c) * w3 for c in t3)
        )
        score = actual / max_possible if max_possible > 0 else 0.0
        return {"score": round(score, 4), "tier1_avg": self._tier_average(field_score, t1, w1),
                "tier2_avg": self._tier_average(field_score, t2, w2),
                "tier3_avg": self._tier_average(field_score, t3, w3)}

    @staticmethod
    def _tier_average(field_score, cols: Set[str], weight: float) -> float:
        if not cols:
            return 0.0
        return round(sum(field_score(c) for c in cols) / len(cols), 4)

    def _score_structural(self, structural_elements: Optional[List[Dict[str, Any]]],
                           cover_type: Optional[str]) -> Dict[str, Any]:
        """Dimension 3: fraction of expected structural elements detected."""
        cover = cover_type or "C"
        expected = self._expected_elements_by_type.get(cover, set())
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
                              metadata: Optional[Dict[str, Any]] = None,
                              template_id: Optional[str] = None) -> Dict[str, Any]:
        """Dimension 4: cover sheet type quality baseline + file property bonus.

        I284: source quality is template-scoped. Resolution order:
          1. document_templates[template_id].source_quality_score map
          2. health_scoring.default_source_quality_scores (schema default)
          3. legacy fallback constant (config-less caller)
        """
        template_map = self._template_source_quality.get(template_id) if template_id else None
        if template_map and cover_type:
            base = template_map.get(cover_type)
        else:
            base = self._default_source_quality_scores.get(cover_type) if cover_type else None
        score = float(base) if base is not None else 0.3

        bonus = 0.0
        detail = {"type": cover_type or "unknown", "bonus": bonus, "bonus_reason": None,
                  "source": "template" if (template_map and cover_type) else "default"}

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
        """Consistency modifier: penalty per violation + file timestamp drift check."""
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
        """T1.99.187 (I214): Score from a HealthInput contract → HealthOutput."""
        from .io_contracts import HealthOutput
        doc = health_input.document or {}
        class_id = getattr(health_input, "class_id", None) or doc.get("class_id") or doc.get("document_class")
        template_id = getattr(health_input, "template_id", None) or doc.get("template_id")
        result = self.score(
            doc,
            structural_elements=health_input.elements or None,
            cover_type=getattr(health_input, "cover_type", None),
            class_id=class_id,
            template_id=template_id,
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
                class_id=doc.get("class_id") or doc.get("document_class"),
                template_id=doc.get("template_id"),
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

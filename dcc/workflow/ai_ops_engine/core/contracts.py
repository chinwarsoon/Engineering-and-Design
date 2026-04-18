"""
AI Ops Engine — Typed I/O Contracts

Defines all request/response dataclasses used across the engine.
Breadcrumb: consumed by context_builder, analyzers, providers, persistence.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid


@dataclass
class RiskItem:
    """
    A single risk finding with evidence.

    Args:
        title: Short risk title
        description: Detailed description
        severity: CRITICAL / HIGH / MEDIUM / LOW
        affected_rows: Number of rows affected
        error_codes: Related error codes
        columns: Affected columns
        recommendation: Suggested action
    """
    title: str
    description: str
    severity: str
    affected_rows: int
    error_codes: List[str] = field(default_factory=list)
    columns: List[str] = field(default_factory=list)
    recommendation: str = ""


@dataclass
class TrendItem:
    """
    A recurring issue pattern.

    Args:
        pattern: Pattern description
        frequency: Number of occurrences
        error_code: Primary error code
        phases: Pipeline phases where it appears
    """
    pattern: str
    frequency: int
    error_code: str
    phases: List[str] = field(default_factory=list)


@dataclass
class AiContext:
    """
    Model-ready context assembled from pipeline outputs.

    Args:
        run_id: UUID for this pipeline run
        timestamp: ISO timestamp
        total_rows: Total rows processed
        health_score: Data health score (0-100)
        health_grade: Letter grade (A+/A/B/C/F)
        error_summary: Summary dict from error_dashboard_data.json
        phase_breakdown: Errors by phase
        top_columns: Top columns by error count
        top_error_codes: Top error codes by frequency
        dataset_sample: CSV string of first 200 rows
        processing_summary: Full processing_summary.txt text
    """
    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    total_rows: int = 0
    health_score: float = 0.0
    health_grade: str = "F"
    error_summary: Dict[str, Any] = field(default_factory=dict)
    phase_breakdown: List[Dict] = field(default_factory=list)
    top_columns: List[Dict] = field(default_factory=list)
    top_error_codes: List[Dict] = field(default_factory=list)
    dataset_sample: str = ""
    processing_summary: str = ""


@dataclass
class AiInsight:
    """
    Structured AI insight output for a pipeline run.

    Args:
        run_id: Matches AiContext.run_id
        timestamp: ISO timestamp
        risk_level: Overall risk level (CRITICAL/HIGH/MEDIUM/LOW)
        executive_summary: 2-3 sentence plain-language summary
        top_risks: Ranked list of risk findings
        trends: Recurring issue patterns
        recommendations: Actionable improvement items
        evidence_links: Row/column/phase/error_code traceability
        model_used: LLM model name
        provider: Provider name (ollama / rule_based)
        fallback_used: True if rule-based fallback was used
    """
    run_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    risk_level: str = "LOW"
    executive_summary: str = ""
    top_risks: List[RiskItem] = field(default_factory=list)
    trends: List[TrendItem] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    evidence_links: List[Dict] = field(default_factory=list)
    model_used: str = ""
    provider: str = ""
    fallback_used: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to JSON-safe dict."""
        return {
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "risk_level": self.risk_level,
            "executive_summary": self.executive_summary,
            "top_risks": [
                {
                    "title": r.title,
                    "description": r.description,
                    "severity": r.severity,
                    "affected_rows": r.affected_rows,
                    "error_codes": r.error_codes,
                    "columns": r.columns,
                    "recommendation": r.recommendation,
                }
                for r in self.top_risks
            ],
            "trends": [
                {
                    "pattern": t.pattern,
                    "frequency": t.frequency,
                    "error_code": t.error_code,
                    "phases": t.phases,
                }
                for t in self.trends
            ],
            "recommendations": self.recommendations,
            "evidence_links": self.evidence_links,
            "model_used": self.model_used,
            "provider": self.provider,
            "fallback_used": self.fallback_used,
        }


@dataclass
class PipelineRunRecord:
    """
    Persisted run metadata for DuckDB storage.

    Args:
        run_id: UUID
        timestamp: ISO timestamp
        input_file: Source Excel path
        total_rows: Rows processed
        health_score: Data health score
        health_grade: Letter grade
        error_count: Total errors
        ai_risk_level: AI-assessed risk level
        output_csv: CSV output path
        output_excel: Excel output path
        schema_version: Schema file path
    """
    run_id: str
    timestamp: str
    input_file: str
    total_rows: int
    health_score: float
    health_grade: str
    error_count: int
    ai_risk_level: str
    output_csv: str
    output_excel: str
    schema_version: str

# Phase 5 I/O Contract — AI Ops Engine

**Date:** 2026-04-19

---

## Inputs

| Input | Source | Format | Required |
|-------|--------|--------|----------|
| Error dashboard telemetry | `output/error_dashboard_data.json` | JSON | YES |
| Processing summary | `output/processing_summary.txt` | Text | YES |
| Processed dataset sample | `output/processed_dcc_universal.csv` | CSV (top 200 rows) | YES |
| Schema metadata | `config/schemas/dcc_register_config.json` | JSON | NO |

## Outputs

| Output | Location | Format | Description |
|--------|----------|--------|-------------|
| AI insight summary | `output/ai_insight_summary.json` | JSON | Structured insight payload |
| AI insight report | `output/ai_insight_report.md` | Markdown | Human-readable summary |
| AI insight trace | `output/ai_insight_trace.json` | JSON | Evidence traceability map |
| Run record | DuckDB `pipeline_runs` table | DuckDB | Persisted run metadata |

## AiContext Schema

```python
@dataclass
class AiContext:
    run_id: str                    # UUID for this run
    timestamp: str                 # ISO timestamp
    total_rows: int
    health_score: float
    health_grade: str
    error_summary: dict            # from error_dashboard_data.json summary
    phase_breakdown: list          # errors by phase
    top_columns: list              # top 10 columns by error count
    top_error_codes: list          # top 10 error codes
    dataset_sample: str            # CSV string of top 200 rows
    processing_summary: str        # full processing_summary.txt text
```

## AiInsight Schema

```python
@dataclass
class AiInsight:
    run_id: str
    timestamp: str
    risk_level: str                # CRITICAL / HIGH / MEDIUM / LOW
    executive_summary: str         # 2-3 sentence summary
    top_risks: list[RiskItem]      # ranked risk findings
    trends: list[TrendItem]        # recurring patterns
    recommendations: list[str]     # actionable items
    evidence_links: list[dict]     # row/column/phase/error_code links
    model_used: str
    provider: str
    fallback_used: bool
```

## SSE Event Schema

```json
{
  "event": "pipeline_step",
  "data": {
    "step": "step4_document_processing",
    "status": "running | complete | error",
    "message": "Processing 11099 rows...",
    "timestamp": "2026-04-19T10:00:00"
  }
}
```

"""
AI Ops Engine — Context Builder

Assembles a model-ready AiContext from pipeline output files.
Breadcrumb: called by engine.py before provider invocation.
"""

from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

from .contracts import AiContext

logger = logging.getLogger(__name__)

# Max rows of processed CSV to include in context (keeps prompt size manageable)
_SAMPLE_ROWS = 200


def build_ai_context(
    output_dir: Path,
    run_id: Optional[str] = None,
) -> AiContext:
    """
    Build AiContext from pipeline output files.

    Reads error_dashboard_data.json, processing_summary.txt, and
    processed_dcc_universal.csv from output_dir.

    Args:
        output_dir: Path to dcc/output/ directory
        run_id: Optional run UUID; generated if not provided

    Returns:
        Populated AiContext ready for provider consumption
    """
    ctx = AiContext()
    if run_id:
        ctx.run_id = run_id

    # --- error_dashboard_data.json ---
    dashboard_path = output_dir / "error_dashboard_data.json"
    if dashboard_path.exists():
        try:
            with dashboard_path.open(encoding="utf-8") as f:
                dash = json.load(f)
            summary = dash.get("summary", {})
            kpi = summary.get("health_kpi", {})
            ctx.total_rows = dash.get("metadata", {}).get("total_rows", 0)
            ctx.health_score = kpi.get("score", 0.0)
            ctx.health_grade = kpi.get("grade", "F")
            ctx.error_summary = summary
            ctx.phase_breakdown = dash.get("phase_breakdown", [])
            ctx.top_columns = dash.get("column_health", [])[:10]
            ctx.top_error_codes = dash.get("error_types", [])[:10]
            logger.info(f"[context_builder] Loaded dashboard: {ctx.total_rows} rows, score={ctx.health_score}")
        except Exception as exc:
            logger.warning(f"[context_builder] Failed to load dashboard JSON: {exc}")
    else:
        logger.warning(f"[context_builder] Dashboard JSON not found: {dashboard_path}")

    # --- processing_summary.txt ---
    summary_path = output_dir / "processing_summary.txt"
    if summary_path.exists():
        try:
            ctx.processing_summary = summary_path.read_text(encoding="utf-8")
        except Exception as exc:
            logger.warning(f"[context_builder] Failed to read summary: {exc}")

    # --- processed_dcc_universal.csv (sample) ---
    csv_path = output_dir / "processed_dcc_universal.csv"
    if csv_path.exists():
        try:
            df = pd.read_csv(csv_path, nrows=_SAMPLE_ROWS, low_memory=False)
            ctx.dataset_sample = df.to_csv(index=False)
            logger.info(f"[context_builder] Loaded CSV sample: {len(df)} rows × {len(df.columns)} cols")
        except Exception as exc:
            logger.warning(f"[context_builder] Failed to load CSV sample: {exc}")

    return ctx


def format_context_for_prompt(ctx: AiContext) -> str:
    """
    Format AiContext into a structured prompt string for the LLM.

    Args:
        ctx: Populated AiContext

    Returns:
        Formatted prompt string
    """
    top_errors = "\n".join(
        f"  - [{e.get('code','?')}] {e.get('count',0)} occurrences (severity: {e.get('severity','?')})"
        for e in ctx.top_error_codes
    )
    top_cols = "\n".join(
        f"  - {c.get('column','?')}: {c.get('error_count',0)} errors"
        for c in ctx.top_columns
    )
    phases = "\n".join(
        f"  - Phase {p.get('Phase','?')}: {p.get('Total',0)} total "
        f"(HIGH:{p.get('High',0)}, MEDIUM:{p.get('Medium',0)}, WARN:{p.get('Warning/Info',0)})"
        for p in ctx.phase_breakdown
    )

    return f"""You are a data quality analyst reviewing a DCC (Document Control Centre) register pipeline run.

## Run Summary
- Total rows processed: {ctx.total_rows}
- Data Health Score: {ctx.health_score:.1f}% (Grade {ctx.health_grade})
- Total errors: {ctx.error_summary.get('total_errors', 0)}
- Affected rows: {ctx.error_summary.get('affected_rows', 0)}

## Error Distribution by Phase
{phases}

## Top Columns by Error Count
{top_cols}

## Top Error Codes
{top_errors}

## Processing Summary
{ctx.processing_summary[:1500]}

## Dataset Sample (first {_SAMPLE_ROWS} rows, key columns)
{ctx.dataset_sample[:3000]}

---

Based on the above, provide a structured analysis with:
1. Overall risk level (CRITICAL/HIGH/MEDIUM/LOW)
2. Executive summary (2-3 sentences)
3. Top 3-5 specific risks with affected row counts and recommendations
4. Recurring patterns or trends
5. Top 3 actionable recommendations

Respond in JSON format matching this schema:
{{
  "risk_level": "HIGH",
  "executive_summary": "...",
  "top_risks": [
    {{"title": "...", "description": "...", "severity": "HIGH", "affected_rows": 0, "error_codes": [], "columns": [], "recommendation": "..."}}
  ],
  "trends": [
    {{"pattern": "...", "frequency": 0, "error_code": "...", "phases": []}}
  ],
  "recommendations": ["...", "...", "..."]
}}"""

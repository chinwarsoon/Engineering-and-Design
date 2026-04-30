"""
AI Ops Engine — Main Orchestrator

Coordinates context building, provider invocation, analysis, evidence
linking, persistence, and output generation for one pipeline run.
Breadcrumb: run_ai_ops() → AiOpsEngine.run() → AiInsight + output files
"""

from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from core_engine.context import PipelineContext

from .contracts import AiContext, AiInsight, PipelineRunRecord
from .context_builder import build_ai_context
from .evidence import attach_evidence_links
from ..providers.ollama_provider import OllamaProvider
from ..providers.base import RuleBasedProvider
from ..analyzers.risk_analyzer import RiskAnalyzer
from ..analyzers.trend_analyzer import TrendAnalyzer
from ..analyzers.summary_generator import SummaryGenerator
from ..persistence.run_store import RunStore
from ..streaming.event_stream import emit_pipeline_status, emit_pipeline_artifact
from ..utils.serializers import dumps_safe

logger = logging.getLogger(__name__)


class AiOpsEngine:
    """
    Main orchestrator for the AI Operations Engine.

    Runs the full AI analysis pipeline:
    1. Build context from pipeline outputs
    2. Run deterministic analyzers (risk + trend)
    3. Call LLM provider (Ollama or fallback)
    4. Attach evidence links
    5. Generate output files
    6. Persist run record to DuckDB

    Args:
        output_dir: Path to dcc/output/ directory
        db_path: Path to DuckDB file for persistence
        model: Ollama model name
        use_ollama: Whether to attempt Ollama (True by default)
    """

    def __init__(
        self,
        output_dir: Path,
        db_path: Optional[Path] = None,
        model: str = "llama3.1:8b",
        use_ollama: bool = True,
        effective_parameters: Optional[Dict[str, Any]] = None,
    ):
        self.output_dir = Path(output_dir)
        self.db_path = db_path or (self.output_dir / "dcc_runs.duckdb")
        self.model = model
        self.use_ollama = use_ollama
        self.effective_parameters = effective_parameters or {}

        self._risk_analyzer = RiskAnalyzer()
        self._trend_analyzer = TrendAnalyzer()
        self._summary_generator = SummaryGenerator()
        self._run_store = RunStore(self.db_path)

    def run(
        self,
        pipeline_results: Dict[str, Any],
        run_id: Optional[str] = None,
    ) -> AiInsight:
        """
        Execute the full AI operations pipeline for one run.

        Args:
            pipeline_results: Results dict from run_engine_pipeline()
            run_id: Optional run UUID; generated if not provided

        Returns:
            Populated AiInsight
        """
        emit_pipeline_status("step7_ai_ops", "running", "Building AI context...")
        logger.info("[ai_ops_engine] Starting AI operations run")

        # Step 1: Build context with schema-driven filenames
        ctx = build_ai_context(
            self.output_dir, 
            run_id=run_id,
            effective_parameters=self.effective_parameters,
        )
        logger.info(f"[ai_ops_engine] Context built: run_id={ctx.run_id}, rows={ctx.total_rows}")

        # Step 2: Deterministic analysis
        det_risks = self._risk_analyzer.analyze(ctx)
        det_trends = self._trend_analyzer.analyze(ctx)
        overall_risk = self._risk_analyzer.compute_overall_risk(ctx)
        logger.info(f"[ai_ops_engine] Deterministic: {len(det_risks)} risks, {len(det_trends)} trends, risk={overall_risk}")

        # Step 3: LLM provider
        emit_pipeline_status("step7_ai_ops", "running", "Generating AI insights...")
        insight = self._run_provider(ctx)

        # Merge deterministic findings if LLM fallback was used or risks are empty
        if insight.fallback_used or not insight.top_risks:
            insight.top_risks = det_risks
            insight.trends = det_trends
            insight.risk_level = overall_risk

        # Step 4: Attach evidence links
        dashboard_path = self.output_dir / "error_dashboard_data.json"
        if dashboard_path.exists():
            try:
                with dashboard_path.open(encoding="utf-8") as f:
                    dashboard_data = json.load(f)
                insight = attach_evidence_links(insight, dashboard_data)
            except Exception as exc:
                logger.warning(f"[ai_ops_engine] Evidence linking failed: {exc}")

        # Step 5: Generate output files
        self._write_outputs(insight)

        # Step 6: Persist run record
        self._persist_run(insight, pipeline_results, ctx)

        emit_pipeline_status("step7_ai_ops", "complete", f"AI analysis complete — risk={insight.risk_level}")
        logger.info(f"[ai_ops_engine] Run complete: risk={insight.risk_level}, fallback={insight.fallback_used}")
        return insight

    def _run_provider(self, ctx: AiContext) -> AiInsight:
        """
        Select and run the appropriate provider.

        Tries Ollama first; falls back to RuleBasedProvider.

        Args:
            ctx: Populated AiContext

        Returns:
            AiInsight from provider
        """
        if self.use_ollama:
            provider = OllamaProvider(model=self.model)
            if provider.is_available():
                logger.info(f"[ai_ops_engine] Using Ollama provider: {self.model}")
                return provider.generate(ctx)
            else:
                logger.info("[ai_ops_engine] Ollama unavailable, using rule-based fallback")

        fallback = RuleBasedProvider()
        return fallback.generate(ctx)

    def _write_outputs(self, insight: AiInsight) -> None:
        """
        Write all AI output files to output_dir using schema-driven filenames.

        Uses effective_parameters for:
        - ai_insight_summary_filename (default: ai_insight_summary.json)
        - ai_insight_report_filename (default: ai_insight_report.md)
        - ai_insight_trace_filename (default: ai_insight_trace.json)

        Args:
            insight: Populated AiInsight
        """
        # Get schema-driven filenames with defaults
        summary_filename = self.effective_parameters.get("ai_insight_summary_filename", "ai_insight_summary.json")
        report_filename = self.effective_parameters.get("ai_insight_report_filename", "ai_insight_report.md")
        trace_filename = self.effective_parameters.get("ai_insight_trace_filename", "ai_insight_trace.json")

        # JSON summary
        json_path = self.output_dir / summary_filename
        self._summary_generator.generate_json_summary(insight, json_path)
        emit_pipeline_artifact("ai_insight", str(json_path))

        # Markdown report
        md_path = self.output_dir / report_filename
        self._summary_generator.generate_markdown_report(insight, md_path)
        emit_pipeline_artifact("ai_report", str(md_path))

        # Trace
        trace_path = self.output_dir / trace_filename
        self._summary_generator.generate_trace(insight, trace_path)
        emit_pipeline_artifact("ai_trace", str(trace_path))

        logger.info(f"[ai_ops_engine] Outputs written to {self.output_dir}")

    def _persist_run(
        self,
        insight: AiInsight,
        pipeline_results: Dict[str, Any],
        ctx: AiContext,
    ) -> None:
        """
        Persist run record and insight to DuckDB.

        Args:
            insight: Populated AiInsight
            pipeline_results: Pipeline results dict
            ctx: AiContext with run metadata
        """
        record = PipelineRunRecord(
            run_id=ctx.run_id,
            timestamp=ctx.timestamp,
            input_file=pipeline_results.get("excel_path", ""),
            total_rows=ctx.total_rows,
            health_score=ctx.health_score,
            health_grade=ctx.health_grade,
            error_count=ctx.error_summary.get("total_errors", 0),
            ai_risk_level=insight.risk_level,
            output_csv=pipeline_results.get("csv_output_path", ""),
            output_excel=pipeline_results.get("excel_output_path", ""),
            schema_version=pipeline_results.get("schema_path", ""),
        )
        self._run_store.save_run(record)
        self._run_store.save_insight(insight)


def run_ai_ops(
    context: PipelineContext,
    model: str = "llama3.1:8b",
    effective_parameters: Optional[Dict[str, Any]] = None,
) -> Optional[AiInsight]:
    """
    Convenience entry point for running AI ops from the pipeline.

    Creates engine, runs analysis, and returns insight.

    Args:
        context: PipelineContext with paths and state
        model: Ollama model to use
        effective_parameters: Optional dict with schema-driven filename configuration

    Returns:
        AiInsight or None if AI ops failed
    """
    try:
        engine = AiOpsEngine(
            output_dir=context.paths.csv_output_path.parent, 
            model=model,
            effective_parameters=effective_parameters,
        )
        pipeline_results = {
            "excel_path": str(context.paths.excel_path),
            "csv_output_path": str(context.paths.csv_output_path),
            "excel_output_path": str(context.paths.excel_output_path),
            "schema_path": str(context.paths.schema_path),
        }
        return engine.run(pipeline_results)
    except Exception as exc:
        logger.warning(f"[ai_ops_engine] AI operations failed (non-blocking): {exc}")
        
        # Record error in context as non-blocking system error
        if hasattr(context, 'add_system_error'):
            context.add_system_error(
                code="S-A-S-0501",
                message=f"AI operations failed: {exc}",
                details=str(exc),
                engine="ai_ops_engine",
                phase="ai_analysis",
                severity="medium",
                fatal=False  # Non-blocking as per R11
            )
        
        # Also print to stderr for user visibility (preserved behavior)
        try:
            from utility_engine.errors import system_error_print
            system_error_print("S-A-S-0501", detail=str(exc), fatal=False)
        except Exception:
            pass
        return None

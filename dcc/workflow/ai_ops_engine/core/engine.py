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
from typing import Any, Dict, List, Optional, Tuple

from core_engine.context.context_pipeline import PipelineContext

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


def _get_available_ram_gb() -> float:
    """
    Return currently available system RAM in GB.

    Uses psutil (already in requirements.txt). Degrades to a conservative
    fallback (1.0 GB) if psutil is unavailable so the selector still
    returns the smallest pool entry rather than crashing.

    Returns:
        Available RAM in GB (float, always > 0).
    """
    try:
        import psutil
        return psutil.virtual_memory().available / (1024 ** 3)
    except Exception:
        logger.warning("[ai_ops_engine] psutil unavailable; assuming 1.0 GB free")
        return 1.0


def _select_model_by_memory(
    model_pool: List[Dict[str, Any]],
    headroom_gb: float,
) -> Tuple[Optional[str], Optional[Dict[str, Any]], str, float, float]:
    """
    Pick the first enabled pool entry that fits available RAM.

    All metadata (name, size_gb, ram_multiplier, enabled) comes from
    schema-resolved parameters — no hardcoded sizes or names in code
    (per agent_rule.md §4.4 schema-driven design).

    Args:
        model_pool: List of model_entry dicts (schema-driven).
        headroom_gb: GB reserved for OS + Python + Ollama overhead.

    Returns:
        Tuple of:
            - model_name: Selected name, or None if no fit.
            - selected_entry: The full entry dict, or None.
            - selection_reason: One of
                "schema_default", "explicit_override", "no_model_fits".
            - free_ram_gb: Available RAM at decision time.
            - required_gb: RAM required by selected model (0 if no fit).
    """
    free_ram_gb = _get_available_ram_gb()

    for entry in model_pool or []:
        if not isinstance(entry, dict):
            continue
        if not entry.get("enabled", True):
            continue
        size_gb = float(entry.get("size_gb", 0))
        mult = float(entry.get("ram_multiplier", 1.5))
        required_gb = size_gb * mult
        if required_gb + headroom_gb <= free_ram_gb:
            return entry.get("name"), entry, "schema_default", free_ram_gb, required_gb

    return None, None, "no_model_fits", free_ram_gb, 0.0


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
        model: Ollama model name (used only as a final fallback if
            effective_parameters contains no model_pool)
        use_ollama: Whether to attempt Ollama (True by default)
        effective_parameters: Schema-resolved parameters (must contain
            model_pool, model_memory_headroom_gb, and optionally ai_model)
    """

    def __init__(
        self,
        output_dir: Path,
        db_path: Optional[Path] = None,
        model: str = "",
        use_ollama: bool = True,
        effective_parameters: Optional[Dict[str, Any]] = None,
    ):
        self.output_dir = Path(output_dir)
        self.effective_parameters = effective_parameters or {}

        # Task B5d: Use filename from parameters if available (SSOT)
        db_filename = self.effective_parameters.get('ai_runs_db_filename', 'dcc_runs.duckdb')
        self.db_path = db_path or (self.output_dir / db_filename)

        self.use_ollama = use_ollama

        # Phase 5.6: Model selection is schema-driven. Resolve at init
        # time so the chosen model + reason are available to _run_provider
        # and to persistence. The hardcoded `model` parameter is preserved
        # as a last-resort fallback only when no model_pool is provided.
        self.selected_model = ""
        self.selected_entry: Optional[Dict[str, Any]] = None
        self.selection_reason: str = "no_model_pool"
        self.free_ram_mb: int = 0
        self.required_ram_mb: int = 0
        self._resolve_model_selection(model)

        self._risk_analyzer = RiskAnalyzer()
        self._trend_analyzer = TrendAnalyzer()
        self._summary_generator = SummaryGenerator()
        self._run_store = RunStore(self.db_path)

    def _resolve_model_selection(self, fallback_model: str) -> None:
        """
        Resolve which Ollama model to use for this run.

        Precedence (per agent_rule.md §4.4):
        1. Explicit ai_model override in effective_parameters
           (only honored if its entry in model_pool is enabled and fits).
        2. First enabled model_pool entry that fits available RAM.
        3. Hardcoded `fallback_model` (last resort; legacy CLI compat).
        """
        params = self.effective_parameters
        model_pool = params.get("model_pool") or []
        headroom_gb = float(params.get("model_memory_headroom_gb", 2.0))

        chosen, entry, reason, free_gb, req_gb = _select_model_by_memory(
            model_pool, headroom_gb
        )

        # Try explicit override against the resolved pool first
        explicit = params.get("ai_model")
        if explicit and model_pool:
            explicit_entry = next(
                (m for m in model_pool if isinstance(m, dict) and m.get("name") == explicit),
                None,
            )
            if explicit_entry and explicit_entry.get("enabled", True):
                size_gb = float(explicit_entry.get("size_gb", 0))
                mult = float(explicit_entry.get("ram_multiplier", 1.5))
                required_gb = size_gb * mult
                if required_gb + headroom_gb <= free_gb:
                    self.selected_model = explicit
                    self.selected_entry = explicit_entry
                    self.selection_reason = "explicit_override"
                    self.free_ram_mb = int(free_gb * 1024)
                    self.required_ram_mb = int(required_gb * 1024)
                    logger.info(
                        f"[ai_ops_engine] Explicit override honored: model={explicit}, "
                        f"required={required_gb:.2f}GB, free={free_gb:.2f}GB"
                    )
                    return

        if chosen:
            self.selected_model = chosen
            self.selected_entry = entry
            self.selection_reason = reason
            self.free_ram_mb = int(free_gb * 1024)
            self.required_ram_mb = int(req_gb * 1024)
            logger.info(
                f"[ai_ops_engine] Memory-aware selector picked: model={chosen}, "
                f"required={req_gb:.2f}GB, free={free_gb:.2f}GB"
            )
            return

        # Last resort: hardcoded fallback (only when no model_pool exists)
        if not model_pool and fallback_model:
            self.selected_model = fallback_model
            self.selection_reason = "no_model_pool"
            self.free_ram_mb = int(free_gb * 1024)
            self.required_ram_mb = 0
            logger.warning(
                f"[ai_ops_engine] No model_pool in schema; using hardcoded "
                f"fallback: model={fallback_model}"
            )
            return

        self.selected_model = ""
        self.selection_reason = reason
        self.free_ram_mb = int(free_gb * 1024)
        self.required_ram_mb = 0
        logger.warning(
            f"[ai_ops_engine] No model fits free RAM "
            f"({free_gb:.2f}GB); will fall back to rule-based provider"
        )

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

        # Phase 5.6: annotate insight with model selection telemetry
        # (engine selection state was resolved at __init__ time).
        insight.model_family = (
            self.selected_entry.get("family", "") if self.selected_entry else ""
        )
        insight.model_capability = (
            self.selected_entry.get("capability", "") if self.selected_entry else ""
        )
        insight.free_ram_mb = self.free_ram_mb
        insight.required_ram_mb = self.required_ram_mb
        insight.selection_reason = self.selection_reason

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
                # C3: Pass error catalog from pipeline_results as SSOT for phase mapping
                error_catalog = pipeline_results.get("error_catalog", {})
                insight = attach_evidence_links(insight, dashboard_data, error_catalog=error_catalog)
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

        Phase 5.6: model is resolved at init time from schema-driven
        model_pool + memory check (see _resolve_model_selection).
        If no model fits, falls back to RuleBasedProvider.

        Args:
            ctx: Populated AiContext

        Returns:
            AiInsight from provider
        """
        if self.use_ollama and self.selected_model:
            provider = OllamaProvider(
                model=self.selected_model,
                model_metadata=self.selected_entry,
            )
            if provider.is_available():
                logger.info(
                    f"[ai_ops_engine] Using Ollama provider: {self.selected_model} "
                    f"(reason={self.selection_reason})"
                )
                return provider.generate(ctx)
            else:
                logger.info(
                    "[ai_ops_engine] Ollama provider reports unavailable; "
                    "using rule-based fallback"
                )

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
    model: str = "",
    effective_parameters: Optional[Dict[str, Any]] = None,
) -> Optional[AiInsight]:
    """
    Convenience entry point for running AI ops from the pipeline.

    Phase 5.6: model selection is delegated to AiOpsEngine which reads
    model_pool + model_memory_headroom_gb from effective_parameters.
    The `model` parameter is preserved as a legacy last-resort fallback
    when no model_pool is present in the resolved schema.

    Args:
        context: PipelineContext with paths and state
        model: Ollama model to use (legacy fallback; usually empty)
        effective_parameters: Schema-resolved parameters (must include
            model_pool and model_memory_headroom_gb for schema-driven mode)

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

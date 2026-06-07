#!/usr/bin/env python3
"""
DCC Engine Pipeline - Modular workflow using four engine folders:
1. initiation_engine - Project setup validation
2. schema_engine - Schema validation and dependency resolution
3. mapper_engine - Column mapping and fuzzy matching
4. processor_engine - Document processing and calculations
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

# Insert workflow path for engine imports
workflow_path = Path(__file__).parent
if str(workflow_path) not in sys.path:
    sys.path.insert(0, str(workflow_path))

# Engine imports
from ai_ops_engine import run_ai_ops
from core_engine.context.context_pipeline import (
    PipelineContext,
)
from core_engine.errors.error_manager import (
    handle_system_error,
    validate_schema_ready,
    validate_setup_ready,
    wrap_engine_execution,
)
from core_engine.errors.pipeline_result_handler import (
    handle_pipeline_error,
    handle_pipeline_results,
)
from core_engine.io import load_excel_data
from core_engine.logging import (
    DEBUG_LEVEL,
    save_debug_log,
    set_debug_level,
    setup_logger,
)
from core_engine.paths import (
    resolve_pipeline_base_path,
)
from initiation_engine import (
    ProjectSetupValidator,
)
from initiation_engine import (
    format_report as format_setup_report,
)
from mapper_engine import ColumnMapperEngine
from processor_engine import (
    # Phase 2 DI: Import factories for dependency injection
    SchemaProcessorFactory,
    create_calculation_engine,
)
from reporting_engine import (
    write_processing_summary,
)
from schema_engine import (
    SchemaValidator,
    write_validation_status,
)
from utility_engine.bootstrap.boot_pipeline import BootstrapError, BootstrapManager
from utility_engine.cli import (
    VERBOSE_LEVELS,
    parse_cli_args,
)
from utility_engine.console import (
    create_progress_bar,
    create_progress_spinner,
    milestone_print,
    print_framework_banner,
    status_print,
)


@dataclass(frozen=True)
class PipelineStep:
    """Registered pipeline step with standardized execution metadata."""

    engine_name: str
    phase: str
    runner: Callable[[PipelineContext], Any]


def _run_initiation(context: PipelineContext) -> Dict[str, Any]:
    setup_validator = ProjectSetupValidator(context)
    setup_results = setup_validator.run()
    context.state.setup_results = setup_results

    if not validate_setup_ready(
        context, setup_results, engine="initiation_engine", phase="step1_initiation"
    ):
        if context.should_fail_fast("system"):
            raise ValueError(format_setup_report(setup_results))
    else:
        total_folders = setup_validator.get_total_folders(setup_results)
        total_files = setup_validator.get_total_files(setup_results)
        milestone_print(
            "MILESTONE_SETUP_VALIDATED", f"{total_folders} folders, {total_files} files"
        )

    return setup_results


def _run_schema(context: PipelineContext) -> Dict[str, Any]:
    schema_path = context.paths.schema_path
    status_print("STATUS_MAIN_SCHEMA", path=schema_path, min_level=3)

    if not handle_system_error(
        context=context,
        condition=schema_path.exists(),
        code="S-F-S-0204",
        message=f"Schema file not found: {schema_path}",
        details=str(schema_path),
        engine="schema_engine",
        phase="step2_schema_validation",
        severity="critical",
        fatal=True,
    ):
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    schema_validator = SchemaValidator(context)

    # Stage 1: BEFORE
    status_print("STATUS_SCHEMA_VAL_START")

    # Stage 2: DURING - Progress indicator for schema validation
    with create_progress_spinner("PROGRESS_SCHEMA_VAL") as spinner:
        schema_results = schema_validator.run()
        spinner.update(1)

    context.state.schema_results = schema_results
    write_validation_status(schema_results)

    if not validate_schema_ready(
        context, schema_results, engine="schema_engine", phase="step2_schema_validation"
    ):
        if context.should_fail_fast("system"):
            raise ValueError(json.dumps(schema_results, indent=2))

    schema_validator.build_blueprint(context)

    # Stage 3: AFTER
    total_columns = schema_validator.get_total_columns(schema_results)
    total_refs = schema_validator.get_total_references(schema_results)
    milestone_print(
        "MILESTONE_SCHEMA_LOADED", f"{total_columns} columns, {total_refs} references"
    )
    return schema_results


def _run_mapper(context: PipelineContext) -> Dict[str, Any]:
    excel_path = context.paths.excel_path
    if not handle_system_error(
        context=context,
        condition=excel_path.exists(),
        code="S-F-S-0201",
        message=f"Input file not found: {excel_path}",
        details=str(excel_path),
        engine="mapper_engine",
        phase="step3_column_mapping",
        severity="critical",
        fatal=True,
    ):
        raise FileNotFoundError(f"Input file not found: {excel_path}")

    context.data.df_raw = load_excel_data(
        excel_path,
        context.parameters,
        nrows=context.nrows,
        verbose=DEBUG_LEVEL >= 2,
        context=context,
    )

    # Phase 2: Progress indicator for column mapping
    total_headers = len(context.data.df_raw.columns)

    # Stage 1: BEFORE
    status_print("STATUS_MAPPER_START", count=total_headers)

    # Stage 2: DURING
    with create_progress_spinner("PROGRESS_COLUMN_MAP") as spinner:
        mapper = ColumnMapperEngine(context)
        result = mapper.run()
        spinner.update(1)

    # Stage 3: AFTER
    mapping_result = context.state.mapping_result
    milestone_print(
        "MILESTONE_COLUMNS_MAPPED",
        f"{mapping_result['matched_count']:.0f} / {mapping_result['total_headers']:.0f}  ({mapping_result['match_rate']:.0%})",
    )
    return result


def _write_summary(context: PipelineContext, df_processed: Any) -> None:
    write_processing_summary(
        summary_path=context.paths.summary_path,
        input_file=context.paths.excel_path,
        main_schema_path=context.paths.schema_path,
        schema_results=context.state.schema_results,
        raw_columns=list(context.data.df_raw.columns),
        mapped_columns=list(context.data.df_mapped.columns),
        processed_columns=list(df_processed.columns),
        raw_shape=context.data.df_raw.shape,
        mapped_shape=context.data.df_mapped.shape,
        processed_shape=df_processed.shape,
        df_raw=context.data.df_raw,
        df_mapped=context.data.df_mapped,
        df_processed=df_processed,
        mapping_result=context.state.mapping_result,
        schema_reference_count=len(
            context.state.resolved_schema.get("schema_references", {})
        ),
        csv_path=context.paths.csv_output_path,
        excel_path=context.paths.excel_output_path,
        upload_sheet_name=context.parameters.get("upload_sheet_name"),
        header_row_index=context.parameters.get("header_row_index"),
    )


def _run_processor(context: PipelineContext) -> Dict[str, Any]:
    processor = create_calculation_engine(
        context=context,
        schema_data=context.state.resolved_schema,
    )
    status_print("STATUS_DI_ENGINE", engine="CalculationEngine", min_level=3)

    try:
        result = processor.run()
        df_processed = context.data.df_processed

        status_print("STATUS_HEALTH_DIAG")
        context.state.error_summary = processor.get_error_summary()
        dashboard_json_path = processor.error_reporter.export_dashboard_json(
            len(df_processed), context=context
        )
        status_print("STATUS_DASHBOARD_EXPORT", path=dashboard_json_path, min_level=3)
        return result
    except Exception:
        if context.should_fail_fast("data"):
            status_print("STATUS_DIAG_REPORT")
            context.state.error_summary = processor.get_error_summary()
            processor.error_reporter.export_dashboard_json(
                len(context.data.df_mapped), context=context
            )
            _write_summary(context, context.data.df_mapped)
        raise


def _run_reorder(context: PipelineContext) -> Dict[str, Any]:
    schema_processor = SchemaProcessorFactory.create(
        context.state.resolved_schema, context=context
    )
    context.data.df_processed = schema_processor.reorder_dataframe(
        context.data.df_processed,
        status_print_fn=status_print,
    )
    return {
        "processed_columns": len(context.data.df_processed.columns),
    }


def _run_export(context: PipelineContext) -> Dict[str, Any]:
    df_processed = context.data.df_processed

    # Phase 2: Progress indicators for export operations
    export_steps = [
        (
            "Excel",
            lambda: df_processed.to_excel(context.paths.excel_output_path, index=False),
        ),
        (
            "CSV",
            lambda: df_processed.to_csv(context.paths.csv_output_path, index=False),
        ),
        ("Summary", lambda: _write_summary(context, df_processed)),
        (
            "Debug Log",
            lambda: save_debug_log(output_path=context.paths.debug_log_path),
        ),
    ]

    for step_name, step_func in export_steps:
        # Stage 1: BEFORE
        status_print("STATUS_EXPORT_START", name=step_name)

        # Stage 2: DURING
        with create_progress_spinner("PROGRESS_EXPORT", name=step_name) as spinner:
            step_func()
            spinner.update(1)

    status_print("STATUS_PROC_COMPLETE")
    status_print("STATUS_CSV_PATH", name=context.paths.csv_output_path.name)
    status_print("STATUS_EXCEL_PATH", name=context.paths.excel_output_path.name)
    return {
        "csv_output_path": str(context.paths.csv_output_path),
        "excel_output_path": str(context.paths.excel_output_path),
    }


def _run_ai(context: PipelineContext) -> Dict[str, Any]:
    # Stage 1: BEFORE
    status_print("STATUS_AI_START")

    # Stage 2: DURING - Progress indicator for AI operations
    with create_progress_spinner("PROGRESS_AI_ANALYSIS") as spinner:
        ai_insight = run_ai_ops(
            context=context,
            effective_parameters=context.parameters,
        )
        spinner.update(1)

    # Stage 3: AFTER
    if ai_insight:
        milestone_print(
            "MILESTONE_AI_COMPLETE",
            f"Risk: {ai_insight.risk_level}, Provider: {ai_insight.provider}",
        )
        ai_summary_filename = context.parameters.get(
            "ai_insight_summary_filename", "ai_insight_summary.json"
        )
        status_print(
            "STATUS_AI_INSIGHT",
            path=context.paths.csv_output_path.parent / ai_summary_filename,
        )
        return {
            "risk_level": ai_insight.risk_level,
            "provider": ai_insight.provider,
        }

    status_print("STATUS_AI_SKIP")
    return {"skipped": True}


PIPELINE_STEPS: Tuple[PipelineStep, ...] = (
    PipelineStep("initiation_engine", "step1_initiation", _run_initiation),
    PipelineStep("schema_engine", "step2_schema_validation", _run_schema),
    PipelineStep("mapper_engine", "step3_column_mapping", _run_mapper),
    PipelineStep("processor_engine", "step4_document_processing", _run_processor),
    PipelineStep("reorder_engine", "step5_column_reorder", _run_reorder),
    PipelineStep("export_engine", "step6_export", _run_export),
    PipelineStep("ai_ops_engine", "step7_ai_ops", _run_ai),
)


def _build_pipeline_results(context: PipelineContext) -> Dict[str, Any]:
    return {
        "base_path": str(context.paths.base_path),
        "schema_path": str(context.paths.schema_path),
        "excel_path": str(context.paths.excel_path),
        "output_path": str(context.paths.csv_output_path),
        "csv_output_path": str(context.paths.csv_output_path),
        "excel_output_path": str(context.paths.excel_output_path),
        "summary_path": str(context.paths.summary_path),
        "raw_shape": list(context.data.df_raw.shape),
        "mapped_shape": list(context.data.df_mapped.shape),
        "processed_shape": list(context.data.df_processed.shape),
        "matched_count": context.state.mapping_result["matched_count"],
        "total_headers": context.state.mapping_result["total_headers"],
        "match_rate": context.state.mapping_result["match_rate"],
        "missing_required": context.state.mapping_result.get("missing_required", []),
        "ready": True,
        "telemetry": context.telemetry.execution_times,
        "environment": context.state.environment,
    }


def run_engine_pipeline(context: PipelineContext) -> Dict[str, Any]:
    """Run the registered DCC engine pipeline steps."""
    # Execute each registered pipeline step in sequence.
    # Steps are defined in PIPELINE_STEPS and run in order: initiation -> schema -> mapper -> processor -> reorder -> export -> ai_ops.
    # wrap_engine_execution handles error capture, telemetry, and fail-fast logic per step.
    # The lambda captures the current step's runner to avoid the classic loop-closure variable binding issue.
    for step in PIPELINE_STEPS:
        wrap_engine_execution(
            context,
            step.engine_name,
            lambda runner=step.runner: runner(context),
            phase=step.phase,
        )
    return _build_pipeline_results(context)


def run_engine_pipeline_with_ui(
    base_path: Path,
    upload_file_name: str,
    output_folder: str = "output",
    schema_file_name: Optional[str] = None,
    debug_mode: bool = False,
    nrows: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Run pipeline with UI-selected paths and parameters using BootstrapManager.

    Breadcrumb: UI params -> BootstrapManager -> bootstrap_for_ui() -> to_pipeline_context() -> run_engine_pipeline()

    Simplified UI mode initialization using BootstrapManager instead of manual contracts.

    Precedence (highest to lowest):
        1. UI Overrides (this function - passed to BootstrapManager)
        2. Schema Configuration
        3. Native Defaults

    Args:
        base_path: Base directory selected by user (contains data/ folder)
        upload_file_name: Excel file name selected by user
        output_folder: Output subfolder name (default: "output")
        schema_file_name: Optional custom schema file
        debug_mode: Enable debug logging
        nrows: Optional row limit for testing

    Returns:
        Pipeline execution results dictionary

    Example:
        >>> result = run_engine_pipeline_with_ui(
        ...     base_path=Path("/home/user/dcc"),
        ...     upload_file_name="project.xlsx",
        ...     debug_mode=True,
        ...     nrows=500
        ... )
    """
    try:
        # Bootstrap all initialization phases for UI mode
        manager = BootstrapManager(base_path).bootstrap_for_ui(
            upload_file_name=upload_file_name,
            output_folder=output_folder,
            schema_file_name=schema_file_name,
            debug_mode=debug_mode,
            nrows=nrows,
        )

        # Convert to PipelineContext
        context = manager.to_pipeline_context()
        context.nrows = nrows or 0
        context.debug_mode = debug_mode

        # Run pipeline
        status_print("STATUS_UI_PIPELINE", name=upload_file_name)
        status_print("STATUS_BASE_PATH", path=base_path)
        status_print("STATUS_DEBUG_MODE", mode=debug_mode, rows=nrows or "ALL")

        return run_engine_pipeline(context)

    except BootstrapError as e:
        # Handle bootstrap failures
        code, message = e.to_system_error()
        raise ValueError(f"Bootstrap failed [{code}]: {message}")
    except Exception as exc:
        # Handle unexpected errors
        raise ValueError(f"Pipeline initialization failed: {exc}")


def main() -> int:
    """
    Main entry point for DCC Engine Pipeline using BootstrapManager.

    Breadcrumb: sys.argv -> resolve_pipeline_base_path() -> parse_cli_args() -> BootstrapManager -> bootstrap_all() -> to_pipeline_context() -> run_engine_pipeline()

    The pipeline start position is determined by:
        1. --base-path CLI argument (explicit)
        2. Current working directory (execution context)

    Simplified from ~400 lines to ~50 lines using BootstrapManager for initialization.
    """
    # Resolve pipeline start position before parsing CLI args
    # This ensures all path operations use the correct execution context
    # pipeline must rest in "workflow" folder
    pipeline_dir = "workflow"

    # return actual pipeline start position
    pipeline_start = resolve_pipeline_base_path()

    # if pipeline started in "workflow" folder, need to strip the "workflow" folder from the pipeline_start path. this will
    # allow the pipeline to start in the "workflow" folder.
    # pipeline base path will be the parent of the "workflow" folder.
    if pipeline_start.name == pipeline_dir:
        pipeline_start = pipeline_start.parent

    # Parse CLI args using the resolved pipeline start position and expected pipeline directory
    # args: parsed Namespace with typed fields (base_path, verbose, nrows, json, etc.)
    # cli_args: raw dict of CLI-provided values for downstream precedence resolution
    # cli_overrides_provided: bool flag indicating whether any CLI overrides were explicitly passed
    args, cli_args, cli_overrides_provided = parse_cli_args(
        pipeline_start, pipeline_dir
    )

    # Setup logger early with verbose level from CLI (before any bootstrap operations)
    setup_logger()
    verbose_level = VERBOSE_LEVELS.get(args.verbose, 1)
    set_debug_level(verbose_level)

    try:
        # Bootstrap all initialization phases in one call
        # Bootstrap will load schema, validate paths, resolve parameters per precedence of CLI > config > defaults
        # Bootsrap will return a BootstrapManager instance with all initialized components
        # if any error, Bootstrap will raise BootstrapError

        manager = BootstrapManager(Path(args.base_path)).bootstrap_all(cli_args)

        # Convert to PipelineContext (this also builds postload trace via Phase P3)
        context = manager.to_pipeline_context()
        context.nrows = args.nrows

        # Update debug mode based on DEBUG_LEVEL
        context.debug_mode = DEBUG_LEVEL >= 2

        # Phase P3: Attach preload and postload traces from BootstrapManager to the pipeline context.
        # Preload trace captures the parameter resolution state before schema/config loading (always present).
        # Postload trace captures the state after schema and config are fully loaded (may be None if schema loading was skipped or failed).
        # These traces are used downstream for diagnostics, audit logging, and parameter precedence reporting.
        context.set_preload_state(manager.preload_trace)
        if manager.postload_trace:
            context.set_postload_state(manager.postload_trace)

        # Print banner after bootstrap (now that we have effective_parameters)
        # Use dynamic bootstrap summary for status display
        summary = manager.bootstrap_summary
        print_framework_banner(
            base_path=manager.base_path,
            input_file=manager.effective_parameters.get("upload_file_name"),
            output_dir=manager.effective_parameters.get("download_file_path"),
            cli_overrides=cli_args if cli_overrides_provided else None,
            bootstrap_status=summary["status"],
            bootstrap_phases=summary["completed_count"],
        )

        # Run pipeline
        milestone_print("MILESTONE_PIPELINE_START")
        results = run_engine_pipeline(context)

    except BootstrapError as exc:
        return handle_pipeline_error(exc, json_output=args.json)
    except Exception as exc:
        return handle_pipeline_error(exc, json_output=args.json)

    results["environment"] = manager.environment
    results["effective_parameters"] = manager.effective_parameters
    handle_pipeline_results(context, results, json_output=args.json)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

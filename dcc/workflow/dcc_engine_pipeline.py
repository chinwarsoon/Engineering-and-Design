#!/usr/bin/env python3
"""
DCC Engine Pipeline - Modular workflow using four engine folders:
1. initiation_engine - Project setup validation
2. schema_engine - Schema validation and dependency resolution
3. mapper_engine - Column mapping and fuzzy matching
4. processor_engine - Document processing and calculations
"""

from __future__ import annotations

import argparse
import builtins
import importlib
import json
import os
import platform
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Insert workflow path for engine imports
workflow_path = Path(__file__).parent
if str(workflow_path) not in sys.path:
    sys.path.insert(0, str(workflow_path))

# Engine imports
from core_engine.context import (
    PipelineContext,
    PipelinePaths,
    PipelineState,
    PipelineData,
    ContextTraceItem,
)
from core_engine.paths import (
    resolve_pipeline_base_path,
    get_homedir,
    resolve_platform_paths,
    resolve_output_paths,
    validate_export_paths,
)
from utility_engine.paths import safe_resolve
from core_engine.logging import (
    setup_logger,
    set_debug_mode,
    set_debug_level,
    log_context,
    log_error,
    save_debug_log,
    get_verbose_mode,
    DEBUG_LEVEL,
)
from core_engine.system import test_environment
from core_engine.io import load_excel_data

# Phase 4: UI Contract imports for path and parameter overrides
from initiation_engine.overrides import (
    PathSelectionContract,
    ParameterOverrideContract,
    UIContractBundle,
    get_available_files,
    suggest_base_paths,
    validate_and_resolve,
)
from core_engine.ui_contract import UIContractManager, UIRequest, UIResponse

from utility_engine.console import (
    status_print,
    milestone_print,
    debug_print,
    print_framework_banner,
)
from utility_engine.cli import (
    parse_cli_args,
    build_native_defaults,
    resolve_effective_parameters,
    get_registry_for_cli,
    VERBOSE_LEVELS,
)
from utility_engine.errors import system_error_print
from utility_engine.bootstrap import BootstrapManager, BootstrapError
from initiation_engine.error_handling import get_system_error_message
from core_engine.error_handling import handle_system_error, validate_setup_ready, validate_schema_ready, generate_error_report

from initiation_engine import (
    ProjectSetupValidator,
    format_report as format_setup_report,
)
from schema_engine import (
    SchemaValidator,
    write_validation_status,
    default_schema_path,
    load_schema_parameters,
)
from mapper_engine import ColumnMapperEngine
from processor_engine import (
    CalculationEngine,
    SchemaProcessor,
    # Phase 2 DI: Import factories for dependency injection
    CalculationEngineFactory,
    SchemaProcessorFactory,
    create_calculation_engine,
)
from reporting_engine import (
    write_processing_summary,
    print_summary,
)
from ai_ops_engine import run_ai_ops

# Phase 2 DI Configuration: Set to True to use dependency injection
# Set to False for legacy direct instantiation (backward compatibility)
_USE_DI_MODE = True  # Toggle this to switch between DI and legacy mode


def run_engine_pipeline(context: PipelineContext) -> Dict[str, Any]:
    """
    Run the four-engine pipeline:
    1. initiation_engine - Project setup validation
    2. schema_engine - Schema validation
    3. mapper_engine - Column mapping
    4. processor_engine - Document processing
    """
    excel_path = context.paths.excel_path
    schema_path = context.paths.schema_path
    base_path = context.paths.base_path
    export_paths = {
        "csv_path": context.paths.csv_output_path,
        "excel_path": context.paths.excel_output_path,
        "summary_path": context.paths.summary_path,
    }
    
    # Get effective_parameters from context for schema-driven filenames
    effective_parameters = getattr(context, 'parameters', {}) or {}

    # Step 1: Initiation Engine - Project Setup Validation
    # this step will check if all required files and folders are present.
    try:
        start_time = time.time()
        with log_context("pipeline", "step1_initiation"):
            setup_validator = ProjectSetupValidator(context)
            # return setup_results which includes a "ready" boolean and details on missing/invalid items if not ready, like number of files/folders found, missing files/folders, etc
            # if ready is True, return a summary of the setup validation, like number of files/folders found, etc
            # if ready is False, log a system error with code S-C-S-0305 and include the details in the log, then raise a ValueError with the details
            setup_results = setup_validator.validate()
            context.state.setup_results = setup_results
            
            # Record engine status
            context.state.engine_status["initiation_engine"] = "running"
            
            # Use context-based error handling
            if not validate_setup_ready(context, setup_results, engine="initiation_engine", phase="step1_initiation"):
                if context.should_fail_fast("system"):
                    raise ValueError(format_setup_report(setup_results))
            else:
                total_folders = setup_validator.get_total_folders(setup_results)
                total_files = setup_validator.get_total_files(setup_results)
                milestone_print("Setup validated", f"{total_folders} folders, {total_files} files")
                context.state.engine_status["initiation_engine"] = "completed"
        
        context.telemetry.execution_times["initiation_engine"] = time.time() - start_time
    except ValueError:
        context.record_engine_failure("initiation_engine", "step1_initiation")
        raise
    except Exception as exc:
        context.capture_exception(code="S-R-S-0401", exception=exc, engine="initiation_engine", phase="step1_initiation")
        raise

    # Step 2: Schema Engine - Schema Validation
    try:
        start_time = time.time()
        with log_context("pipeline", "step2_schema_validation"):
            status_print(f"Main schema: {schema_path}", min_level=3)
            
            # Record engine status
            context.state.engine_status["schema_engine"] = "running"
            
            # Validate schema file exists using context-based error handling
            if not handle_system_error(
                context=context,
                condition=schema_path.exists(),
                code="S-F-S-0204",
                message=f"Schema file not found: {schema_path}",
                details=str(schema_path),
                engine="schema_engine",
                phase="step2_schema_validation",
                severity="critical",
                fatal=True
            ):
                raise FileNotFoundError(f"Schema file not found: {schema_path}")
            
            schema_validator = SchemaValidator(context)
            status_print("Validating schema and resolving dependencies...", min_level=3)
            schema_results = schema_validator.validate()
            context.state.schema_results = schema_results
            write_validation_status(schema_results)
            
            # Use context-based error handling for schema validation
            if not validate_schema_ready(context, schema_results, engine="schema_engine", phase="step2_schema_validation"):
                if context.should_fail_fast("system"):
                    raise ValueError(json.dumps(schema_results, indent=2))
            
            # Populate Blueprint (SSOT)
            resolved_schema = schema_validator.load_resolved_schema()
            context.state.resolved_schema = resolved_schema
            
            _schema_root = resolved_schema if "columns" in resolved_schema else resolved_schema.get("enhanced_schema", {})
            context.blueprint.columns = _schema_root.get("columns", {})
            context.blueprint.validation_rules = resolved_schema.get("parameters", {})
            
            # Pre-calculate phase map for Phase 6
            column_sequence = _schema_root.get("column_sequence", [])
            phase_map = {"P1": [], "P2": [], "P2.5": [], "P3": []}
            for col_name in column_sequence:
                if col_name in context.blueprint.columns:
                    phase = context.blueprint.columns[col_name].get("processing_phase", "P3")
                    if phase in phase_map:
                        phase_map[phase].append(col_name)
            context.blueprint.phase_map = phase_map
            
            # Load Error Catalog into Blueprint
            error_config_path = context.paths.schema_paths.data_error_config
            if error_config_path.exists():
                try:
                    with open(error_config_path, "r", encoding="utf-8") as f:
                        context.blueprint.error_catalog = json.load(f).get("data_logic_errors", {})
                except Exception as e:
                    msg = get_system_error_message("S-C-S-0311").format(detail=str(e))
                    context.add_system_error(
                        code="S-C-S-0311",
                        message=msg,
                        details=str(e),
                        engine="schema_engine",
                        phase="step2_schema_validation",
                        severity="medium",
                        fatal=False
                    )

            total_columns = schema_validator.get_total_columns(schema_results)
            total_refs = schema_validator.get_total_references(schema_results)
            milestone_print("Schema loaded", f"{total_columns} columns, {total_refs} references")
            context.state.engine_status["schema_engine"] = "completed"
        
        context.telemetry.execution_times["schema_engine"] = time.time() - start_time
    except (ValueError, FileNotFoundError):
        context.record_engine_failure("schema_engine", "step2_schema_validation")
        raise
    except json.JSONDecodeError as exc:
        context.capture_exception(code="S-C-S-0302", exception=exc, engine="schema_engine", phase="step2_schema_validation")
        raise
    except Exception as exc:
        context.capture_exception(code="S-R-S-0404", exception=exc, engine="schema_engine", phase="step2_schema_validation")
        raise

    # Step 3: Mapper Engine - Column Mapping
    try:
        start_time = time.time()
        with log_context("pipeline", "step3_column_mapping"):
            # Record engine status
            context.state.engine_status["mapper_engine"] = "running"
            
            # Validate excel file exists using context-based error handling
            if not handle_system_error(
                context=context,
                condition=excel_path.exists(),
                code="S-F-S-0201",
                message=f"Input file not found: {excel_path}",
                details=str(excel_path),
                engine="mapper_engine",
                phase="step3_column_mapping",
                severity="critical",
                fatal=True
            ):
                raise FileNotFoundError(f"Input file not found: {excel_path}")
            
            df_raw = load_excel_data(excel_path, context.parameters, nrows=context.nrows, verbose=DEBUG_LEVEL >= 2, context=context)
            
            # resolved_schema is already in context.state.resolved_schema from step 2
            
            mapper = ColumnMapperEngine(context)
            mapping_out = mapper.map_dataframe()
            mapping_result = context.state.mapping_result
            df_mapped = context.data.df_mapped
            milestone_print("Columns mapped", f"{mapping_result['matched_count']:.0f} / {mapping_result['total_headers']:.0f}  ({mapping_result['match_rate']:.0%})")
            context.state.engine_status["mapper_engine"] = "completed"
        
        context.telemetry.execution_times["mapper_engine"] = time.time() - start_time
    except FileNotFoundError:
        context.record_engine_failure("mapper_engine", "step3_column_mapping")
        raise
    except PermissionError as exc:
        context.capture_exception(code="S-F-S-0202", exception=exc, engine="mapper_engine", phase="step3_column_mapping")
        raise
    except Exception as exc:
        context.capture_exception(code="S-R-S-0405", exception=exc, engine="mapper_engine", phase="step3_column_mapping")
        raise

    # Step 4: Processor Engine - Document Processing
    try:
        start_time = time.time()
        with log_context("pipeline", "step4_document_processing"):
            # Record engine status
            context.state.engine_status["processor_engine"] = "running"
            
            # Phase 2 DI: Use factory for dependency injection (or legacy mode for compatibility)
            if _USE_DI_MODE:
                processor = create_calculation_engine(
                    context=context,
                    schema_data=context.state.resolved_schema,
                    # Dependencies are auto-created if not provided
                    # For custom injection, pass explicit dependencies:
                    # error_reporter=custom_reporter,
                    # error_aggregator=custom_aggregator,
                    # etc.
                )
                status_print("Using DI-enabled CalculationEngine", min_level=3)
            else:
                # Legacy mode: Direct instantiation (backward compatibility)
                processor = CalculationEngine(context, context.state.resolved_schema)
                status_print("Using legacy CalculationEngine", min_level=3)
            
            processor.process_data()
            df_processed = context.data.df_processed
            
            status_print("Generating data health diagnostics...", min_level=2)
            context.state.error_summary = processor.get_error_summary()
            schema_results["error_summary"] = context.state.error_summary
            processor.error_reporter.output_dir = export_paths["csv_path"].parent
            processor.error_reporter.effective_parameters = effective_parameters  # Schema-driven filenames
            dashboard_json_path = processor.error_reporter.export_dashboard_json(len(df_processed))
            status_print(f"✓ Dashboard JSON exported: {dashboard_json_path}", min_level=3)
            context.state.engine_status["processor_engine"] = "completed"
        
        context.telemetry.execution_times["processor_engine"] = time.time() - start_time
    except MemoryError as exc:
        context.capture_exception(code="S-R-S-0403", exception=exc, engine="processor_engine", phase="step4_document_processing")
        raise
    except Exception as exc:
        # Replace legacy "FAIL FAST" string detection with context-based fail-fast
        context.capture_exception(code="S-R-S-0402", exception=exc, engine="processor_engine", phase="step4_document_processing")
        
        if context.should_fail_fast("data"):
            status_print("Generating diagnostic report for captured errors...")
            context.state.error_summary = processor.get_error_summary()
            schema_results["error_summary"] = context.state.error_summary
            processor.error_reporter.output_dir = export_paths["csv_path"].parent
            processor.error_reporter.effective_parameters = effective_parameters  # Schema-driven filenames
            processor.error_reporter.export_dashboard_json(len(df_mapped))
            schema_reference_count = len(resolved_schema.get("schema_references", {}))
            write_processing_summary(
                summary_path=export_paths["summary_path"],
                input_file=excel_path,
                main_schema_path=schema_path,
                schema_results=schema_results,
                raw_columns=list(df_raw.columns),
                mapped_columns=list(df_mapped.columns),
                processed_columns=list(df_mapped.columns),
                raw_shape=df_raw.shape,
                mapped_shape=df_mapped.shape,
                processed_shape=df_mapped.shape,
                df_raw=df_raw,
                df_mapped=df_mapped,
                df_processed=df_mapped,
                mapping_result=mapping_result,
                schema_reference_count=schema_reference_count,
                csv_path=export_paths["csv_path"],
                excel_path=export_paths["excel_path"],
            )
        else:
            context.capture_exception(code="S-R-S-0406", exception=exc, engine="processor_engine", phase="step4_document_processing")
        raise

    # Step 5: Reorder columns per schema column_sequence
    with log_context("pipeline", "step5_column_reorder"):
        start_time = time.time()
        # Phase 2 DI: Use factory for SchemaProcessor creation
        if _USE_DI_MODE:
            schema_processor = SchemaProcessorFactory.create(resolved_schema)
        else:
            # Legacy mode
            schema_processor = SchemaProcessor(resolved_schema)
        df_processed = schema_processor.reorder_dataframe(df_processed, status_print_fn=status_print)
        context.data.df_processed = df_processed
        context.telemetry.execution_times["reorder_engine"] = time.time() - start_time

    # Export results
    with log_context("pipeline", "step6_export"):
        start_time = time.time()
        df_processed.to_excel(export_paths["excel_path"], index=False)
        df_processed.to_csv(export_paths["csv_path"], index=False)

        # Write processing summary
        schema_reference_count = len(resolved_schema.get("schema_references", {}))
        write_processing_summary(
            summary_path=export_paths["summary_path"],
            input_file=excel_path,
            main_schema_path=schema_path,
            schema_results=schema_results,
            raw_columns=list(df_raw.columns),
            mapped_columns=list(df_mapped.columns),
            processed_columns=list(df_processed.columns),
            raw_shape=df_raw.shape,
            mapped_shape=df_mapped.shape,
            processed_shape=df_processed.shape,
            df_raw=df_raw,
            df_mapped=df_mapped,
            df_processed=df_processed,
            mapping_result=mapping_result,
            schema_reference_count=schema_reference_count,
            csv_path=export_paths["csv_path"],
            excel_path=export_paths["excel_path"],
        )

        # Save debug log to same output folder as CSV
        debug_log_path = context.paths.debug_log_path
        save_debug_log(output_path=debug_log_path)
        context.telemetry.execution_times["export_engine"] = time.time() - start_time

        # Get error summary for display from processor
        error_summary = context.state.error_summary
        total_errors = error_summary.get("total_errors", 0)

        status_print(f"✓ Processing complete")
        status_print(f"CSV: {export_paths['csv_path'].name}")
        status_print(f"Excel: {export_paths['excel_path'].name}")
        
        if total_errors > 0:
            # Show abbreviated error summary
            health_kpi = error_summary.get("health_kpi", {})
            affected = error_summary.get("affected_rows", 0)
            status_print(f"⚠ Validation: {total_errors} errors ({health_kpi.get('critical_errors',0)} critical, {health_kpi.get('high_errors',0)} high, {health_kpi.get('medium_errors',0)} medium) — {affected} rows affected")
            # Use schema-driven dashboard filename for error details reference
            dashboard_filename = effective_parameters.get("error_dashboard_filename", "error_dashboard_data.json")
            status_print(f"  Details: {export_paths['csv_path'].parent.name}/{dashboard_filename}")
            status_print(f"  Run with --verbose debug for full error list")
        else:
            status_print(f"✓ Validation: No errors detected")

    # Step 7: AI Operations (non-blocking)
    with log_context("pipeline", "step7_ai_ops"):
        start_time = time.time()
        status_print("Running AI operations analysis...")
        ai_insight = run_ai_ops(
            context=context,
            effective_parameters=effective_parameters,  # Pass schema-driven filenames
        )
        if ai_insight:
            status_print(f"✓ AI analysis complete — Risk: {ai_insight.risk_level}, Provider: {ai_insight.provider}")
            # Use schema-driven filename for status message
            ai_summary_filename = effective_parameters.get("ai_insight_summary_filename", "ai_insight_summary.json")
            status_print(f"AI Insight: {export_paths['csv_path'].parent / ai_summary_filename}")
        else:
            status_print("⚠ AI analysis skipped or failed (non-blocking)")
        context.telemetry.execution_times["ai_ops_engine"] = time.time() - start_time

    return {
        "base_path": str(base_path),
        "schema_path": str(schema_path),
        "excel_path": str(excel_path),
        "output_path": str(export_paths["csv_path"]),
        "csv_output_path": str(export_paths["csv_path"]),
        "excel_output_path": str(export_paths["excel_path"]),
        "summary_path": str(export_paths["summary_path"]),
        "raw_shape": list(df_raw.shape),
        "mapped_shape": list(df_mapped.shape),
        "processed_shape": list(df_processed.shape),
        "matched_count": mapping_result["matched_count"],
        "total_headers": mapping_result["total_headers"],
        "match_rate": mapping_result["match_rate"],
        "missing_required": mapping_result.get("missing_required", []),
        "ready": True,
        "telemetry": context.telemetry.execution_times,
        "environment": context.state.environment,
    }


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
            nrows=nrows
        )
        
        # Convert to PipelineContext
        context = manager.to_pipeline_context()
        context.nrows = nrows or 0
        context.debug_mode = debug_mode
        
        # Run pipeline
        status_print(f"🚀 UI Pipeline: {upload_file_name}")
        status_print(f"   Base: {base_path}")
        status_print(f"   Debug: {debug_mode} | Rows: {nrows or 'ALL'}")
        
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
    
    # Parse CLI args with resolved base_path, raise error if pipeline is not in "workflow" folder
    args, cli_args, cli_overrides_provided = parse_cli_args(pipeline_start, pipeline_dir)
    
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
        context.debug_mode = (DEBUG_LEVEL >= 2)
        
        # Phase P3: Set preload/postload traces from BootstrapManager
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
            bootstrap_phases=summary["completed_count"]
        )
        
        # Run pipeline
        milestone_print("Pipeline Execution", "Starting engine pipeline")
        results = run_engine_pipeline(context)
        
    except BootstrapError as e:
        # Handle bootstrap failures with structured error codes
        code, message = e.to_system_error()
        if args.json:
            print(json.dumps({
                "ready": False,
                "error": message,
                "code": code,
                "phase": e.phase,
                "timestamp": datetime.now().isoformat()
            }, indent=2))
        else:
            system_error_print(code, detail=message)
        return 1
    except Exception as exc:
        # Handle unexpected errors
        if args.json:
            print(json.dumps({
                "ready": False,
                "error": str(exc),
                "timestamp": datetime.now().isoformat()
            }, indent=2))
        else:
            system_error_print("S-R-S-0401", detail=str(exc))
        return 1
    
    # Generate final error report for successful completion
    error_report = generate_error_report(context)
    
    results["environment"] = manager.environment
    results["effective_parameters"] = manager.effective_parameters
    results["timestamp"] = datetime.now().isoformat()
    results["error_report"] = error_report
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_summary(results, status_print_fn=status_print)
        
        # Print error summary for non-JSON output
        if error_report['error_summary']['total_errors'] > 0:
            print("\n=== Error Summary ===")
            print(f"Total errors: {error_report['error_summary']['total_errors']}")
            print(f"Fatal errors: {error_report['error_summary']['fatal_errors']}")
            if error_report['error_summary']['by_domain']:
                print("By domain:", error_report['error_summary']['by_domain'])
            if error_report['error_summary']['by_severity']:
                print("By severity:", error_report['error_summary']['by_severity'])
            
            # Show system vs data error separation
            system_errors = error_report['system_status_errors']['errors']
            data_errors = error_report['data_handling_errors']['errors']
            
            if system_errors:
                print(f"\nSystem-status errors ({len(system_errors)}):")
                for error in system_errors[:3]:
                    print(f"  - [{error['code']}] {error['message']}")
                if len(system_errors) > 3:
                    print(f"  ... and {len(system_errors) - 3} more")
            
            if data_errors:
                print(f"\nData-handling errors ({len(data_errors)}):")
                for error in data_errors[:3]:
                    print(f"  - [{error['code']}] {error['message']}")
                if len(data_errors) > 3:
                    print(f"  ... and {len(data_errors) - 3} more")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

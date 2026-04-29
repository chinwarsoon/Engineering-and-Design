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
    default_base_path,
    get_homedir,
    resolve_platform_paths,
    resolve_output_paths,
    validate_export_paths,
)
from utility_engine.paths import safe_resolve
from core_engine.logging import (
    setup_logger,
    set_debug_mode,
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
)
from utility_engine.errors import system_error_print
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


def _build_preload_context_data(
    *,
    base_path: Path,
    schema_path: Path,
    input_file_path: Path,
    export_paths: Dict[str, Path],
    effective_parameters: Dict[str, Any],
) -> Dict[str, ContextTraceItem]:
    """Build preload trace from raw resolved values before context creation."""
    return {
        "base_path": ContextTraceItem("base_path", str(base_path), "resolved", "directory", True),
        "schema_path": ContextTraceItem("schema_path", str(schema_path), "resolved", "file", True),
        "upload_file_name": ContextTraceItem(
            "upload_file_name",
            effective_parameters.get("upload_file_name"),
            "effective_parameters",
            "file",
            bool(effective_parameters.get("upload_file_name")),
        ),
        "download_file_path": ContextTraceItem(
            "download_file_path",
            effective_parameters.get("download_file_path"),
            "effective_parameters",
            "directory",
            bool(effective_parameters.get("download_file_path")),
        ),
        "csv_output_path": ContextTraceItem("csv_output_path", str(export_paths["csv_path"]), "resolved", "file", True),
        "excel_output_path": ContextTraceItem("excel_output_path", str(export_paths["excel_path"]), "resolved", "file", True),
        "summary_path": ContextTraceItem("summary_path", str(export_paths["summary_path"]), "resolved", "file", True),
        "parameters": ContextTraceItem("parameters", effective_parameters, "effective_parameters", "dict", isinstance(effective_parameters, dict)),
    }


def _validate_pre_context_gate(
    preload_data: Dict[str, ContextTraceItem],
    validation_result: Any,
) -> None:
    """Fail fast if preload trace or validation state is not ready for context construction."""
    invalid_items = [item.key for item in preload_data.values() if not item.validated]
    if invalid_items:
        raise ValueError(f"Pre-context validation gate failed: invalid preload fields: {', '.join(invalid_items)}")
    if validation_result.has_errors:
        raise ValueError(
            f"Pre-context validation gate failed: {'; '.join(validation_result.errors)}"
        )


def _build_postload_context_data(
    *,
    pipeline_paths: PipelinePaths,
    effective_parameters: Dict[str, Any],
) -> Dict[str, ContextTraceItem]:
    """Build postload trace from context-ready values after context construction."""
    return {
        "base_path": ContextTraceItem("base_path", str(pipeline_paths.base_path), "context.paths", "directory", True, "ready"),
        "schema_path": ContextTraceItem("schema_path", str(pipeline_paths.schema_path), "context.paths", "file", True, "ready"),
        "excel_path": ContextTraceItem("excel_path", str(pipeline_paths.excel_path), "context.paths", "file", True, "ready"),
        "csv_output_path": ContextTraceItem("csv_output_path", str(pipeline_paths.csv_output_path), "context.paths", "file", True, "ready"),
        "excel_output_path": ContextTraceItem("excel_output_path", str(pipeline_paths.excel_output_path), "context.paths", "file", True, "ready"),
        "summary_path": ContextTraceItem("summary_path", str(pipeline_paths.summary_path), "context.paths", "file", True, "ready"),
        "parameters": ContextTraceItem("parameters", effective_parameters, "context.parameters", "dict", isinstance(effective_parameters, dict), "ready"),
    }


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
                    context.add_system_error(
                        code="E-SCH-CATALOG-LOAD",
                        message=f"Failed to load error catalog: {e}",
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
            status_print(f"  Details: {export_paths['csv_path'].parent.name}/error_diagnostic_log.csv")
            status_print(f"  Run with --verbose debug for full error list")
        else:
            status_print(f"✓ Validation: No errors detected")

    # Step 7: AI Operations (non-blocking)
    with log_context("pipeline", "step7_ai_ops"):
        start_time = time.time()
        status_print("Running AI operations analysis...")
        ai_insight = run_ai_ops(
            context=context,
        )
        if ai_insight:
            status_print(f"✓ AI analysis complete — Risk: {ai_insight.risk_level}, Provider: {ai_insight.provider}")
            status_print(f"AI Insight: {export_paths['csv_path'].parent / 'ai_insight_summary.json'}")
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
    Phase 4: Run pipeline with UI-selected paths and parameters.
    
    This function provides a UI-friendly interface for pipeline execution
    using PathSelectionContract and ParameterOverrideContract.
    
    Precedence (highest to lowest):
        1. CLI Arguments (handled by main())
        2. UI Overrides (this function)
        3. Schema Configuration
        4. Hardcoded Defaults
    
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
    # Phase 4: Create path selection contract
    path_contract = PathSelectionContract(
        base_path=base_path,
        upload_file_name=upload_file_name,
        output_folder=output_folder,
        schema_file_name=schema_file_name
    )
    
    # Phase 4: Validate before running
    validation = path_contract.validate()
    if not validation["valid"]:
        raise ValueError(f"Path validation failed: {validation['errors']}")
    
    # Phase 4: Create parameter override contract
    param_contract = ParameterOverrideContract(
        debug_mode=debug_mode,
        nrows=nrows
    )
    
    # Phase 4: Apply parameter warnings
    param_validation = param_contract.validate()
    if param_validation.get("warnings"):
        for warning in param_validation["warnings"]:
            status_print(f"⚠ {warning}")
    
    # Phase 4: Resolve to PipelinePaths
    paths = path_contract.to_paths()
    
    # Phase 4: Create context with overrides
    context = PipelineContext(
        paths=paths,
        parameters={},
        nrows=nrows or 0,
        debug_mode=debug_mode
    )
    
    # Phase 4: Apply parameter overrides to context
    param_contract.apply_to_context(context)
    
    # Phase 4: Run main pipeline
    status_print(f"🚀 Phase 4 UI Pipeline: {upload_file_name}")
    status_print(f"   Base: {base_path}")
    status_print(f"   Debug: {debug_mode} | Rows: {nrows or 'ALL'}")
    
    return run_engine_pipeline(context)


def main() -> int:
    """Main entry point for DCC Engine Pipeline."""
    
    # 1. Parse CLI args (this also sets debug level via --verbose)
    # milestone print for CLI args parsed to be shown in banner
    args, cli_args, cli_overrides_provided = parse_cli_args()
    
    # 2. Configure Python logging based on DEBUG_LEVEL (suppresses INFO at level 0-1)
    # milestone print for logging configured to be shown in banner
    setup_logger()
    
    # 3. Resolve base path early for banner using centralized validation
    from utility_engine.validation import ValidationManager
    
    validator = ValidationManager()
    base_path_validation = validator.validate_path_with_system_context(
        path_input=Path(args.base_path),
        path_type="directory",
        name="Base Directory",
        required=True,
        base_path=None  # Base path resolution for base path itself
    )
    
    if base_path_validation.status.name == "FAIL":
        raise ValueError(f"Base path validation failed: {base_path_validation.message}")
    
    base_path = base_path_validation.path
    
    # 4. Handle Windows HOME env issues using centralized validation
    home_dir_validation = validator.validate_home_directory()
    
    if home_dir_validation.status.name == "FAIL":
        milestone_print("Warning", f"Home directory validation failed: {home_dir_validation.message}")
    else:
        # milestone print for home directory resolved
        milestone_print("Home Directory", f"Resolved: {home_dir_validation.path}")
    
    # 5. Build parameters using the central base_path
    native_defaults = build_native_defaults(base_path)
    # milestone print for native defaults built, and count of native defaults
    milestone_print("Native Defaults", f"Built from base_path ({len(native_defaults)} defaults)")
    
    # 5.5. Validate native defaults folders and files conditionally (only when not available from CLI or schema)
    from utility_engine.validation import ValidationStatus
    milestone_print("Native Defaults Validation", "Checking fallback parameter availability")
    
    # Extract file and folder paths from native defaults for validation
    native_files_to_validate = []
    native_dirs_to_validate = []
    
    # Conditionally validate native default input file (only if not provided by CLI or schema)
    cli_upload_file = cli_args.get("upload_file_name")
    schema_upload_file = effective_parameters.get("upload_file_name") if "effective_parameters" in locals() else None
    native_upload_file = native_defaults.get("upload_file_name")
    
    if not cli_upload_file and (not schema_upload_file or schema_upload_file == native_upload_file):
        if native_upload_file:
            native_files_to_validate.append((
                Path(native_upload_file),
                "Native Default Input File",
                False,  # Native defaults are fallbacks, not required
                False   # create_parent parameter (not used for files)
            ))
    
    # Conditionally validate native default output directory (only if not provided by CLI or schema)
    cli_output_path = cli_args.get("download_file_path")
    schema_output_path = effective_parameters.get("download_file_path") if "effective_parameters" in locals() else None
    native_output_path = native_defaults.get("download_file_path")
    
    if not cli_output_path and (not schema_output_path or schema_output_path == native_output_path):
        if native_output_path:
            native_dirs_to_validate.append((
                Path(native_output_path),
                "Native Default Output Directory",
                False,  # Native defaults are fallbacks, not required
                False   # create_if_missing parameter (False for native defaults)
            ))
    
    # Always validate common directories (data, config) as they're infrastructure directories
    data_dir = base_path / "data"
    native_dirs_to_validate.append((
        data_dir,
        "Native Default Data Directory",
        False,  # Optional directory
        False   # create_if_missing parameter (False for native defaults)
    ))
    
    config_dir = base_path / "config"
    native_dirs_to_validate.append((
        config_dir,
        "Native Default Config Directory",
        False,  # Optional directory
        False   # create_if_missing parameter (False for native defaults)
    ))
    
    # Validate native defaults using ValidationManager (only if we have items to validate)
    if native_files_to_validate or native_dirs_to_validate:
        milestone_print("Native Defaults Validation", f"Validating {len(native_files_to_validate) + len(native_dirs_to_validate)} fallback items")
        
        native_validation_result = validator.validate_paths_and_parameters(
            files=native_files_to_validate,
            directories=native_dirs_to_validate
        )
        
        if native_validation_result.has_errors:
            error_messages = "\n".join(native_validation_result.errors)
            milestone_print("Native Defaults Validation", f"Native defaults validation failed:\n{error_messages}")
        elif native_validation_result.has_warnings:
            warning_messages = "\n".join(native_validation_result.warnings)
            milestone_print("Native Defaults Validation", f"Native defaults validation completed with warnings:\n{warning_messages}")
        else:
            milestone_print("Native Defaults Validation", "All native defaults validated successfully")
        
        # Show native defaults validation summary
        total_native_items = len(native_files_to_validate) + len(native_dirs_to_validate)
        passed_native = len([item for item in native_validation_result.items if item.status == ValidationStatus.PASS])
        failed_native = len([item for item in native_validation_result.items if item.status == ValidationStatus.FAIL])
        warnings_native = len([item for item in native_validation_result.items if item.status == ValidationStatus.WARNING])
        
        milestone_print("Native Defaults Summary", f"Total: {total_native_items}, Passed: {passed_native}, Failed: {failed_native}, Warnings: {warnings_native}")
    else:
        milestone_print("Native Defaults Validation", "No fallback validation needed (CLI or schema values available)")

    # 7. Test environment using central base_path
    environment = test_environment(base_path=base_path)
    if not environment["ready"]:
        payload = {
            "ready": False,
            "error": "Environment test failed",
            "environment": environment,
            "timestamp": datetime.now().isoformat(),
        }
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            missing = ", ".join(environment.get("missing_packages", [])) or "see output above"
            system_error_print("S-E-S-0103", detail=missing)
        return 1
    else:
        milestone_print("Environment ready", "Required dependencies available")

    # 8. Resolve the main schema path using centralized validation
    schema_path_input = cli_args.get("schema_register_file", native_defaults["schema_register_file"])
    schema_path_validation = validator.validate_path_with_system_context(
        path_input=Path(schema_path_input),
        path_type="file",
        name="Schema File",
        required=True,
        base_path=base_path
    )
    
    if schema_path_validation.status.name == "FAIL":
        raise ValueError(f"Schema path validation failed: {schema_path_validation.message}")
    
    schema_path = schema_path_validation.path
    milestone_print("Schema resolved", f"Using: {schema_path}")

    # 8. Resolve effective parameters
    effective_parameters = resolve_effective_parameters(
        schema_path, 
        cli_args, 
        native_defaults,
        load_schema_params_fn=load_schema_parameters
    )
    effective_parameters = resolve_platform_paths(effective_parameters, base_path, status_print)
    
    # Generate export paths and validate them before building PipelineContext
    export_paths = resolve_output_paths(base_path, effective_parameters, safe_resolve, status_print)
    validate_export_paths(export_paths, bool(effective_parameters.get("overwrite_existing_downloads", True)))
    
   # milestone print for number of parameters resolved from cli args, schema, and native defaults
    total_params = len(effective_parameters)
    cli_params = len(cli_args)
    schema_params = len(load_schema_parameters(schema_path))
    native_params = len(native_defaults)
    milestone_print("Parameters resolved", f"Precedence: {total_params} total (CLI: {cli_params}, Schema: {schema_params}, Defaults: {native_params})")

    # 9.5. Print framework banner (visible at ALL levels) with input_file (output_dir to be resolved after project_config loading)
    input_file = effective_parameters.get("upload_file_name", native_defaults.get("upload_file_name"))
    print_framework_banner(base_path=base_path, input_file=input_file, output_dir="pending resolution", cli_overrides=cli_args if cli_overrides_provided else None)

    # 11.Validate paths and parameters using universal validation functions
    milestone_print("Validation", "Validating paths and parameters using universal validation functions")
    
    # Import universal validation utilities
    from utility_engine.validation import ValidationStatus
    
    # Resolve input file path using centralized validation
    input_file_validation = validator.validate_path_with_system_context(
        path_input=Path(effective_parameters["upload_file_name"]),
        path_type="file",
        name="Input Excel File",
        required=True,
        base_path=base_path
    )
    
    if input_file_validation.status.name == "FAIL":
        raise ValueError(f"Input file validation failed: {input_file_validation.message}")
    
    input_file_path = input_file_validation.path
    
    # Load project_config for folder creation configuration
    project_config_path = base_path / "config" / "schemas" / "project_config.json"
    project_config = {}
    if project_config_path.exists():
        try:
            with open(project_config_path, "r", encoding="utf-8") as f:
                project_config = json.load(f)
        except Exception as e:
            milestone_print("Warning", f"Could not load project_config.json: {e}")
    
    # 12.5. Resolve output directory using proper precedence and centralized validation
    output_dir_input = effective_parameters.get("download_file_path", native_defaults.get("download_file_path"))
    
    # Update validator with folder creation config
    if project_config and "folder_creation" in project_config:
        validator.folder_creation_config = project_config["folder_creation"]
    
    output_dir_validation = validator.validate_path_with_system_context(
        path_input=Path(output_dir_input),
        path_type="directory",
        name="Output Directory",
        required=True,
        base_path=base_path
    )
    
    if output_dir_validation.status.name == "FAIL":
        raise ValueError(f"Output directory validation failed: {output_dir_validation.message}")
    
    output_dir = output_dir_validation.path
    milestone_print("Output Directory", f"Resolved and validated: {output_dir}")

    # 13. Validate all pipeline prerequisites using universal validation with schema-controlled folder creation
    validation_result = validator.validate_pipeline_prerequisites(
        base_path=base_path,
        schema_path=schema_path,
        input_file_path=input_file_path,
        export_paths=export_paths,
        effective_parameters=effective_parameters,
        project_config=project_config
    )
    
    # Check validation results
    if validation_result.has_errors:
        error_messages = "\n".join(validation_result.errors)
        raise ValueError(f"Pipeline validation failed:\n{error_messages}")
    
    if validation_result.has_warnings:
        warning_messages = "\n".join(validation_result.warnings)
        milestone_print("Validation Warnings", f"Validation completed with warnings:\n{warning_messages}")
    else:
        milestone_print("Validation", "All paths and parameters validated successfully")
    
    # Log validation summary
    summary = validation_result.summary
    milestone_print("Validation Summary", 
                   f"Total: {summary['total_items']}, "
                   f"Passed: {summary['passed']}, "
                   f"Failed: {summary['failed']}, "
                   f"Warnings: {summary['warnings']}")
    
    # Set debug log path for context
    debug_log_path = export_paths["csv_path"].parent / "debug_log.json"

    # 14. Build preload context trace and enforce pre-context validation gate
    preload_context_data = _build_preload_context_data(
        base_path=base_path,
        schema_path=schema_path,
        input_file_path=input_file_path,
        export_paths=export_paths,
        effective_parameters=effective_parameters,
    )
    _validate_pre_context_gate(preload_context_data, validation_result)

    # 15. Build PipelineContext
    pipeline_paths = PipelinePaths(
        base_path=base_path,
        schema_path=schema_path,
        excel_path=input_file_path,
        csv_output_path=export_paths["csv_path"],
        excel_output_path=export_paths["excel_path"],
        summary_path=export_paths["summary_path"],
        debug_log_path=debug_log_path
    )
    
    context = PipelineContext(
        paths=pipeline_paths,
        parameters=effective_parameters,
        nrows=args.nrows,
        debug_mode=(DEBUG_LEVEL >= 2)
    )
    context.set_preload_state(preload_context_data)
    context.set_postload_state(
        _build_postload_context_data(
            pipeline_paths=pipeline_paths,
            effective_parameters=effective_parameters,
        )
    )
    context.state.environment = environment
    # milestone print for pipeline context built, this is preloaded with all parameters and paths
    milestone_print("Pipeline Context", "Built with validated preload/postload trace data")

    
    # 16. Run the engine pipeline
    try:
        # milestone print for pipeline execution started
        milestone_print("Pipeline Execution", "Starting engine pipeline")
        results = run_engine_pipeline(context)
    except Exception as exc:
        # Capture exception in context before failing
        context.capture_exception(code="S-R-S-0401", exception=exc, engine="orchestrator", phase="main_execution")
        
        # Generate error report
        error_report = generate_error_report(context)
        
        payload = {
            "ready": False,
            "error": str(exc),
            "environment": environment,
            "effective_parameters": effective_parameters,
            "timestamp": datetime.now().isoformat(),
            "error_report": error_report
        }
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            system_error_print("S-R-S-0401", detail=str(exc))
            # Print error summary
            print("\n=== Error Summary ===")
            print(f"Total errors: {error_report['error_summary']['total_errors']}")
            print(f"Fatal errors: {error_report['error_summary']['fatal_errors']}")
            if error_report['error_summary']['by_domain']:
                print("By domain:", error_report['error_summary']['by_domain'])
            if error_report['error_summary']['by_severity']:
                print("By severity:", error_report['error_summary']['by_severity'])
        return 1
    
    # Generate final error report for successful completion
    error_report = generate_error_report(context)
    
    results["environment"] = environment
    results["effective_parameters"] = effective_parameters
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
                for error in system_errors[:3]:  # Show first 3
                    print(f"  - [{error['code']}] {error['message']}")
                if len(system_errors) > 3:
                    print(f"  ... and {len(system_errors) - 3} more")
            
            if data_errors:
                print(f"\nData-handling errors ({len(data_errors)}):")
                for error in data_errors[:3]:  # Show first 3
                    print(f"  - [{error['code']}] {error['message']}")
                if len(data_errors) > 3:
                    print(f"  ... and {len(data_errors) - 3} more")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

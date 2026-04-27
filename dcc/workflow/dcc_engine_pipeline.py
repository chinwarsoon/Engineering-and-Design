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
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Insert workflow path for engine imports
workflow_path = Path(__file__).parent
if str(workflow_path) not in sys.path:
    sys.path.insert(0, str(workflow_path))

# Engine imports
from core_engine.context import PipelineContext, PipelinePaths, PipelineState, PipelineData
from core_engine.paths import (
    default_base_path,
    get_homedir,
    resolve_platform_paths,
    resolve_output_paths,
    validate_export_paths,
    safe_resolve,
)
from core_engine.logging import (
    setup_logger,
    set_debug_mode,
    log_context,
    log_error,
    save_debug_log,
    get_verbose_mode,
    DEBUG_LEVEL,
)
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

from initiation_engine import (
    ProjectSetupValidator,
    format_report as format_setup_report,
    test_environment,
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
    load_excel_data,
)
from reporting_engine import (
    write_processing_summary,
    print_summary,
)
from ai_ops_engine import run_ai_ops


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
    try:
        with log_context("pipeline", "step1_initiation"):
            setup_validator = ProjectSetupValidator(context)
            setup_results = setup_validator.validate()
            context.state.setup_results = setup_results
            if not setup_results.get("ready"):
                system_error_print("S-C-S-0305", detail=format_setup_report(setup_results))
                raise ValueError(format_setup_report(setup_results))
            total_folders = setup_validator.get_total_folders(setup_results)
            total_files = setup_validator.get_total_files(setup_results)
            milestone_print("Setup validated", f"{total_folders} folders, {total_files} files")
    except ValueError:
        raise
    except Exception as exc:
        system_error_print("S-R-S-0401", detail=str(exc))
        raise

    # Step 2: Schema Engine - Schema Validation
    try:
        with log_context("pipeline", "step2_schema_validation"):
            status_print(f"Main schema: {schema_path}", min_level=3)
            if not schema_path.exists():
                system_error_print("S-F-S-0204", detail=str(schema_path))
                raise FileNotFoundError(f"Schema file not found: {schema_path}")
            schema_validator = SchemaValidator(context)
            status_print("Validating schema and resolving dependencies...", min_level=3)
            schema_results = schema_validator.validate()
            context.state.schema_results = schema_results
            write_validation_status(schema_results)
            if not schema_results.get("ready"):
                system_error_print("S-C-S-0303", detail=str(schema_path))
                raise ValueError(json.dumps(schema_results, indent=2))
            
            total_columns = schema_validator.get_total_columns(schema_results)
            total_refs = schema_validator.get_total_references(schema_results)
            milestone_print("Schema loaded", f"{total_columns} columns, {total_refs} references")
    except (ValueError, FileNotFoundError):
        raise
    except json.JSONDecodeError as exc:
        system_error_print("S-C-S-0302", detail=f"{schema_path}: {exc}")
        raise
    except Exception as exc:
        system_error_print("S-R-S-0404", detail=str(exc))
        raise

    # Step 3: Mapper Engine - Column Mapping
    try:
        with log_context("pipeline", "step3_column_mapping"):
            if not excel_path.exists():
                system_error_print("S-F-S-0201", detail=str(excel_path))
                raise FileNotFoundError(f"Input file not found: {excel_path}")
            df_raw = load_excel_data(excel_path, context.parameters, nrows=context.nrows, verbose=DEBUG_LEVEL >= 2)
            context.data.df_raw = df_raw
            
            resolved_schema = schema_validator.load_resolved_schema()
            context.state.resolved_schema = resolved_schema
            
            mapper = ColumnMapperEngine(context)
            mapping_out = mapper.map_dataframe()
            mapping_result = context.state.mapping_result
            df_mapped = context.data.df_mapped
            milestone_print("Columns mapped", f"{mapping_result['matched_count']:.0f} / {mapping_result['total_headers']:.0f}  ({mapping_result['match_rate']:.0%})")
    except FileNotFoundError:
        raise
    except PermissionError as exc:
        system_error_print("S-F-S-0202", detail=str(excel_path))
        raise
    except Exception as exc:
        system_error_print("S-R-S-0405", detail=str(exc))
        raise

    # Step 4: Processor Engine - Document Processing
    try:
        with log_context("pipeline", "step4_document_processing"):
            processor = CalculationEngine(context, context.state.resolved_schema)
            processor.process_data()
            df_processed = context.data.df_processed
            
            status_print("Generating data health diagnostics...", min_level=2)
            context.state.error_summary = processor.get_error_summary()
            schema_results["error_summary"] = context.state.error_summary
            processor.error_reporter.output_dir = export_paths["csv_path"].parent
            dashboard_json_path = processor.error_reporter.export_dashboard_json(len(df_processed))
            status_print(f"✓ Dashboard JSON exported: {dashboard_json_path}", min_level=3)
    except MemoryError as exc:
        system_error_print("S-R-S-0403", detail=str(exc))
        raise
    except Exception as exc:
        is_fail_fast = "FAIL FAST" in str(exc)
        if is_fail_fast:
            system_error_print("S-R-S-0402", detail=str(exc))
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
            system_error_print("S-R-S-0406", detail=str(exc))
        raise

    # Step 5: Reorder columns per schema column_sequence
    with log_context("pipeline", "step5_column_reorder"):
        schema_processor = SchemaProcessor(resolved_schema)
        df_processed = schema_processor.reorder_dataframe(df_processed, status_print_fn=status_print)
        context.data.df_processed = df_processed

    # Export results
    with log_context("pipeline", "step6_export"):
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
        status_print("Running AI operations analysis...")
        ai_insight = run_ai_ops(
            context=context,
        )
        if ai_insight:
            status_print(f"✓ AI analysis complete — Risk: {ai_insight.risk_level}, Provider: {ai_insight.provider}")
            status_print(f"AI Insight: {export_paths['csv_path'].parent / 'ai_insight_summary.json'}")
        else:
            status_print("⚠ AI analysis skipped or failed (non-blocking)")

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
    }


def main() -> int:
    """Main entry point for DCC Engine Pipeline."""
    
    # 1. Parse CLI args (this also sets debug level via --verbose)
    args, cli_args, cli_overrides_provided = parse_cli_args()
    
    # 1.5 Configure Python logging based on DEBUG_LEVEL (suppresses INFO at level 0-1)
    setup_logger()
    
    # 2. Print framework banner (visible at ALL levels)
    input_file = cli_args.get("upload_file_name", "Submittal and RFI Tracker Lists.xlsx")
    base_path = safe_resolve(Path(args.base_path))
    output_dir = base_path / "output"
    print_framework_banner(base_path=base_path, input_file=input_file, output_dir=str(output_dir), cli_overrides=cli_args if cli_overrides_provided else None)
    
    # 3. Handle Windows HOME env issues
    local_home = get_homedir()
    if get_verbose_mode() in ["debug", "trace"]:
        status_print(f"  Resolved home directory: {local_home}")
    
    # 4. Build parameters using the central base_path
    native_defaults = build_native_defaults(base_path)

    # 5. Test environment using central base_path
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
    milestone_print("Environment ready", "Required dependencies available")

    # 4. Resolve the main schema path
    schema_path = safe_resolve(
        Path(cli_args.get("schema_register_file", native_defaults["schema_register_file"]))
    )

    # 5. Resolve effective parameters
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
    
    # Build PipelineContext
    pipeline_paths = PipelinePaths(
        base_path=base_path,
        schema_path=schema_path,
        excel_path=safe_resolve(Path(effective_parameters["upload_file_name"])),
        csv_output_path=export_paths["csv_path"],
        excel_output_path=export_paths["excel_path"],
        summary_path=export_paths["summary_path"],
        debug_log_path=export_paths["csv_path"].parent / "debug_log.json"
    )
    
    context = PipelineContext(
        paths=pipeline_paths,
        parameters=effective_parameters,
        nrows=args.nrows,
        debug_mode=(DEBUG_LEVEL >= 2)
    )

    # milestone print for number of parameters resolved from cli args, schema, and native defaults
    total_params = len(effective_parameters)
    cli_params = len(cli_args)
    schema_params = len(load_schema_parameters(schema_path))
    native_params = len(native_defaults)
    milestone_print("Parameters resolved", f"Precedence: {total_params} total (CLI: {cli_params}, Schema: {schema_params}, Defaults: {native_params})")

    # 6. Run the engine pipeline
    try:
        results = run_engine_pipeline(context)
    except Exception as exc:
        payload = {
            "ready": False,
            "error": str(exc),
            "environment": environment,
            "effective_parameters": effective_parameters,
            "timestamp": datetime.now().isoformat(),
        }
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            system_error_print("S-R-S-0401", detail=str(exc))
        return 1
    
    results["environment"] = environment
    results["effective_parameters"] = effective_parameters
    results["timestamp"] = datetime.now().isoformat()
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_summary(results, status_print_fn=status_print)
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

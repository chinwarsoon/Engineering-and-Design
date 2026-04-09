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

print("DCC Register Universal Processing Pipeline")
print("=" * 80)
print("Enhanced Features:")
print("- Universal Column Mapper: Fuzzy header detection with schema integration")
print("- Universal Document Processor: Schema-driven calculations and null handling")
print("- Enhanced Schema System: Modular configuration with external references")
print("- Multi-format Export: Excel, CSV, JSON with comprehensive reporting")
print("=" * 80)

# Insert workflow path for engine imports
workflow_path = Path(__file__).parent
if str(workflow_path) not in sys.path:
    sys.path.insert(0, str(workflow_path))

# Engine imports
from initiation_engine.engine import (
    ProjectSetupValidator,
    format_report as format_setup_report,
    default_base_path,
    get_homedir,
    parse_cli_args,
    status_print,
    debug_print,
    setup_logger,
    set_debug_mode,
    test_environment,
    resolve_platform_paths,
    resolve_output_paths,
    validate_export_paths,
    log_context,
    save_debug_log,
)
from schema_engine.engine import (
    SchemaValidator,
    write_validation_status,
    safe_resolve,
    default_schema_path,
    load_schema_parameters,
)
from mapper_engine.engine import ColumnMapperEngine
from processor_engine.engine import (
    CalculationEngine,
    SchemaProcessor,
    load_excel_data,
)
from reporting_engine.engine import write_processing_summary


def build_native_defaults(base_path: Path) -> Dict[str, Any]:
    """
    Build native default parameters for the DCC processing pipeline.
    Precedence: CLI args → Schema params → Native defaults
    """
    status_print("Building native default parameters...")
    return {
        "debug_dev_mode": False,
        "overwrite_existing_downloads": True,
        "start_col": "P",
        "end_col": "AP",
        "header_row_index": 4,
        "upload_sheet_name": "Prolog Submittals ",
        "schema_register_file": str(default_schema_path(base_path)),
        # Windows network drive paths
        "win_upload_file": r"K:\J Submission\Submittal and RFI Tracker Lists.xlsx",
        "win_download_path": r"K:\J Submission\AI Tools and Report\data_output",
        # Windows fallback paths
        "win_upload_file_fallback": str(base_path / "data" / "Submittal and RFI Tracker Lists.xlsx"),
        "win_download_path_fallback": str(base_path / "output"),
        # Linux/Colab paths
        "linux_upload_file": str(base_path / "data" / "Submittal and RFI Tracker Lists.xlsx"),
        "linux_download_path": str(base_path / "output"),
        "colab_upload_file": "/content/sample_data/Submittal and RFI Tracker Lists.xlsx",
        "colab_download_path": "/content/output",
        # Active paths (resolved by resolve_platform_paths)
        "upload_file_name": str(base_path / "data" / "Submittal and RFI Tracker Lists.xlsx"),
        "download_file_path": str(base_path / "output"),
    }


def resolve_effective_parameters(
    schema_path: Path,
    cli_args: Dict[str, Any],
    native_defaults: Dict[str, Any],
) -> Dict[str, Any]:
    """  Resolve effective parameters with precedence: CLI → Schema → Native."""
    status_print("Resolving effective parameters...")
    effective_parameters = native_defaults.copy()
    
    try:
        schema_parameters = load_schema_parameters(schema_path)
        effective_parameters.update(schema_parameters)
        status_print(f"Loaded schema parameters from {schema_path}")
    except Exception as exc:
        status_print(f"WARNING: Could not load schema parameters: {exc}")
    
    effective_parameters.update(cli_args)
    effective_parameters["schema_register_file"] = str(schema_path)
    debug_print(f"Effective parameters: {effective_parameters}")
    return effective_parameters


def run_engine_pipeline(
    base_path: Path,
    schema_path: Path,
    effective_parameters: Dict[str, Any],
    nrows: int | None = None,
    debug_mode: bool = False,
) -> Dict[str, Any]:
    """
    Run the four-engine pipeline:
    1. initiation_engine - Project setup validation
    2. schema_engine - Schema validation
    3. mapper_engine - Column mapping
    4. processor_engine - Document processing
    """
    excel_path = safe_resolve(Path(effective_parameters["upload_file_name"]))
    export_paths = resolve_output_paths(base_path, effective_parameters, safe_resolve)
    validate_export_paths(export_paths, bool(effective_parameters.get("overwrite_existing_downloads", True)))

    # Step 1: Initiation Engine - Project Setup Validation
    with log_context("pipeline", "step1_initiation"):
        setup_validator = ProjectSetupValidator(base_path=base_path)
        setup_results = setup_validator.validate()
        if not setup_results.get("ready"):
            raise ValueError(format_setup_report(setup_results))
        status_print("✓ Project setup validation passed")

    # Step 2: Schema Engine - Schema Validation
    with log_context("pipeline", "step2_schema_validation"):
        status_print(f"Main schema: {schema_path}")

        schema_validator = SchemaValidator(schema_path)
        status_print("Validating schema and resolving dependencies...")
        schema_results = schema_validator.validate()
        write_validation_status(schema_results)
        if not schema_results.get("ready"):
            raise ValueError(json.dumps(schema_results, indent=2))
        status_print("✓ Schema validation passed")
        # Store schema_results for summary generation
        pipeline_schema_results = schema_results

    # Step 3: Mapper Engine - Column Mapping
    with log_context("pipeline", "step3_column_mapping"):
        df_raw = load_excel_data(excel_path, effective_parameters, nrows=nrows)

        # Flatten MultiIndex/tuple columns
        import pandas as pd
        if isinstance(df_raw.columns, pd.MultiIndex):
            status_print("⚠️  Flattening MultiIndex columns before mapping")
            df_raw.columns = ['_'.join(str(level) for level in levels).strip('_') for levels in df_raw.columns]
        elif len(df_raw.columns) > 0 and isinstance(df_raw.columns[0], tuple):
            status_print("⚠️  Converting tuple columns to strings")
            df_raw.columns = ['_'.join(str(level) for level in levels).strip('_') for levels in df_raw.columns]

        # Use mapper engine
        resolved_schema = schema_validator.load_resolved_schema()
        mapper = ColumnMapperEngine()
        mapper.resolved_schema = resolved_schema
        mapping_result = mapper.detect_columns(df_raw.columns.tolist())
        df_mapped = mapper.rename_dataframe_columns(df_raw, mapping_result)
        status_print(f"✓ Column mapping complete: {mapping_result['match_rate']:.1%} match rate")

    # Step 4: Processor Engine - Document Processing
    with log_context("pipeline", "step4_document_processing"):
        processor = CalculationEngine(resolved_schema)
        df_processed = processor.process_data(df_mapped)

    # Step 5: Reorder columns per schema column_sequence
    with log_context("pipeline", "step5_column_reorder"):
        schema_processor = SchemaProcessor(resolved_schema)
        ordered_columns = schema_processor.get_ordered_columns()

        # Build ordered column list: only columns that exist in processed DataFrame
        ordered_col_names = [col for col in ordered_columns.keys() if col in df_processed.columns]

        # Append any columns in DataFrame but not in schema sequence
        extra_cols = [col for col in df_processed.columns if col not in ordered_col_names]
        final_col_order = ordered_col_names + extra_cols

        if extra_cols:
            status_print(f"Warning: {len(extra_cols)} column(s) not in column_sequence: {extra_cols}")

        # Reorder DataFrame
        df_processed = df_processed[final_col_order]
        status_print(f"Columns reordered: {len(ordered_col_names)} columns in schema order")
        status_print(f"Total columns: {len(df_processed.columns)}")

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
            schema_results=pipeline_schema_results,
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
        debug_log_path = export_paths["csv_path"].parent / "debug_log.json"
        save_debug_log(output_path=debug_log_path)

        status_print(f"✓ Processing complete")
        status_print(f"CSV: {export_paths['csv_path']}")
        status_print(f"Excel: {export_paths['excel_path']}")
        status_print(f"Summary: {export_paths['summary_path']}")
        status_print(f"Debug Log: {debug_log_path}")

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


def print_summary(results: Dict[str, Any]) -> None:
    """Print processing summary."""
    status_print("\n" + "=" * 72)
    status_print("DCC ENGINE PIPELINE - PROCESSING COMPLETE")
    status_print("=" * 72)
    status_print(f"Base Path: {results['base_path']}")
    status_print(f"Schema File: {results['schema_path']}")
    status_print(f"Excel File: {results['excel_path']}")
    status_print(f"CSV Output: {results['csv_output_path']}")
    status_print(f"Excel Output: {results['excel_output_path']}")
    status_print(f"Raw Shape: {tuple(results['raw_shape'])}")
    status_print(f"Mapped Shape: {tuple(results['mapped_shape'])}")
    status_print(f"Processed Shape: {tuple(results['processed_shape'])}")
    status_print(f"Matched Headers: {results['matched_count']} / {results['total_headers']}")
    status_print(f"Match Rate: {results['match_rate']:.1%}")
    if results["missing_required"]:
        status_print(f"Missing Required Columns: {results['missing_required']}")
    status_print("Ready: YES")


def main() -> int:
    """Main entry point for DCC Engine Pipeline."""
    
    # 1. Centrally manage base_path
    args, cli_args = parse_cli_args() # default_base_path is called inside parse_cli_args if not provided
    base_path = safe_resolve(Path(args.base_path))
    status_print(f"  Project root path: {base_path}")
    
    # Handle Windows HOME env issues
    local_home = get_homedir()
    status_print(f"  Resolved home directory: {local_home}")
    
    # 2. Build parameters using the central base_path
    native_defaults = build_native_defaults(base_path)

    # Set debug mode
    debug_mode = bool(cli_args.get("debug_dev_mode", native_defaults.get("debug_dev_mode", False)))
    status_print(f"Debug mode: {debug_mode}")
    set_debug_mode(debug_mode)

    # 3. Test environment using central base_path
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
            status_print("Environment test failed.")
        return 1

    # 4. Resolve the main schema path
    schema_path = safe_resolve(
        Path(cli_args.get("schema_register_file", native_defaults["schema_register_file"]))
    )

    # 5. Resolve effective parameters
    effective_parameters = resolve_effective_parameters(schema_path, cli_args, native_defaults)
    effective_parameters = resolve_platform_paths(effective_parameters, base_path, status_print)

    # 6. Run the engine pipeline
    try:
        results = run_engine_pipeline(
            base_path=base_path,
            schema_path=schema_path,
            effective_parameters=effective_parameters,
            nrows=args.nrows,
            debug_mode=debug_mode,
        )
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
            status_print(f"PIPELINE ERROR: {exc}")
            import traceback
            if debug_mode:
                traceback.print_exc()
        return 1
    
    results["environment"] = environment
    results["effective_parameters"] = effective_parameters
    results["timestamp"] = datetime.now().isoformat()
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_summary(results)
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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
)
from schema_engine.engine import (
    SchemaValidator, 
    write_validation_status,
    safe_resolve,
    default_schema_path,
)
from mapper_engine.engine import ColumnMapperEngine
from processor_engine.engine import (
    CalculationEngine,
    load_excel_data,
)


DEBUG_DEV_MODE = False


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





def resolve_platform_paths(
    effective_parameters: Dict[str, Any],
    base_path: Path,
) -> Dict[str, Any]:
    """
    Resolve platform-specific paths from merged effective parameters.
    Precedence: CLI → Schema → Native defaults
    """
    status_print("Resolving platform paths...")
    params = effective_parameters.copy()
    system_name = platform.system().lower()
    
    if system_name == "windows":
        win_upload = params.get("win_upload_file", "")
        win_download = params.get("win_download_path", "")
        if win_upload and Path(win_upload).exists():
            params["upload_file_name"] = win_upload
            if win_download:
                params["download_file_path"] = win_download
            status_print(f"Using Windows path: {win_upload}")
    else:
        linux_upload = params.get("linux_upload_file", "")
        linux_download = params.get("linux_download_path", "")
        if linux_upload:
            lp = Path(linux_upload)
            if not lp.is_absolute():
                lp = base_path / lp
            if lp.exists():
                params["upload_file_name"] = str(lp)
                if linux_download:
                    ld = Path(linux_download)
                    if not ld.is_absolute():
                        ld = base_path / ld
                    params["download_file_path"] = str(ld)
                status_print(f"Using Linux path: {lp}")
    
    # Resolve any remaining relative paths
    active_upload = Path(params.get("upload_file_name", ""))
    active_download = Path(params.get("download_file_path", ""))
    if not active_upload.is_absolute():
        params["upload_file_name"] = str(base_path / active_upload)
    if not active_download.is_absolute():
        params["download_file_path"] = str(base_path / active_download)
    
    Path(params["download_file_path"]).mkdir(parents=True, exist_ok=True)
    status_print(f"Current system detected: {system_name}")
    return params





def load_schema_parameters(schema_path: Path) -> Dict[str, Any]:
    """Load parameters section from schema file."""
    with schema_path.open("r", encoding="utf-8") as handle:
        return json.load(handle).get("parameters", {})


def resolve_effective_parameters(
    schema_path: Path,
    cli_args: Dict[str, Any],
    native_defaults: Dict[str, Any],
) -> Dict[str, Any]:
    """Resolve effective parameters with precedence: CLI → Schema → Native."""
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


def resolve_output_paths(base_path: Path, effective_parameters: Dict[str, Any]) -> Dict[str, Path]:
    """Resolve output file paths."""
    explicit_output = effective_parameters.get("output_file")
    if explicit_output:
        base_output = safe_resolve(Path(explicit_output))
    else:
        output_dir = safe_resolve(Path(effective_parameters.get("download_file_path", str(base_path / "output"))))
        base_output = output_dir / "processed_dcc_universal.csv"
    
    output_dir = base_output.parent
    stem = base_output.stem or "processed_dcc_universal"
    
    return {
        "output_dir": output_dir,
        "csv_path": output_dir / f"{stem}.csv",
        "excel_path": output_dir / f"{stem}.xlsx",
        "summary_path": output_dir / "processing_summary.txt",
    }


def validate_export_paths(export_paths: Dict[str, Path], overwrite_existing: bool) -> None:
    """Validate output paths and check for existing files."""
    export_paths["output_dir"].mkdir(parents=True, exist_ok=True)
    if not overwrite_existing:
        for file_key in ("csv_path", "excel_path", "summary_path"):
            target_path = export_paths[file_key]
            if target_path.exists():
                raise FileExistsError(f"Output file exists: {target_path}. Use --overwrite True.")


def run_engine_pipeline(
    base_path: Path,
    schema_path: Path,
    effective_parameters: Dict[str, Any],
    nrows: int | None = None,
) -> Dict[str, Any]:
    """
    Run the four-engine pipeline:
    1. initiation_engine - Project setup validation
    2. schema_engine - Schema validation
    3. mapper_engine - Column mapping
    4. processor_engine - Document processing
    """
    excel_path = safe_resolve(Path(effective_parameters["upload_file_name"]))
    export_paths = resolve_output_paths(base_path, effective_parameters)
    validate_export_paths(export_paths, bool(effective_parameters.get("overwrite_existing_downloads", True)))
    
    # Step 1: Initiation Engine - Project Setup Validation
    status_print("=" * 72)
    status_print("STEP 1: Initiation Engine - Project Setup Validation")
    status_print("=" * 72)
    setup_validator = ProjectSetupValidator(base_path=base_path)
    setup_results = setup_validator.validate()
    if not setup_results.get("ready"):
        raise ValueError(format_setup_report(setup_results))
    status_print("✓ Project setup validation passed")
    
    # Step 2: Schema Engine - Schema Validation
    status_print("\n" + "=" * 72)
    status_print("STEP 2: Schema Engine - Schema Validation")
    status_print("=" * 72)
    schema_validator = SchemaValidator(schema_path)
    schema_results = schema_validator.validate()
    write_validation_status(schema_results)
    if not schema_results.get("ready"):
        raise ValueError(json.dumps(schema_results, indent=2))
    status_print("✓ Schema validation passed")
    
    # Step 3: Mapper Engine - Column Mapping
    status_print("\n" + "=" * 72)
    status_print("STEP 3: Mapper Engine - Column Mapping")
    status_print("=" * 72)
    df_raw = load_excel_data(excel_path, effective_parameters, nrows=nrows)
    
    # Flatten MultiIndex/tuple columns
    import pandas as pd
    if isinstance(df_raw.columns, pd.MultiIndex):
        status_print("   ⚠️  Flattening MultiIndex columns before mapping")
        df_raw.columns = ['_'.join(str(level) for level in levels).strip('_') for levels in df_raw.columns]
    elif len(df_raw.columns) > 0 and isinstance(df_raw.columns[0], tuple):
        status_print("   ⚠️  Converting tuple columns to strings")
        df_raw.columns = ['_'.join(str(level) for level in levels).strip('_') for levels in df_raw.columns]
    
    # Use mapper engine
    mapper = ColumnMapperEngine(schema_file=str(schema_path))
    mapping_result = mapper.detect_columns(df_raw.columns.tolist())
    df_mapped = mapper.rename_dataframe_columns(df_raw, mapping_result)
    status_print(f"✓ Column mapping complete: {mapping_result['match_rate']:.1%} match rate")
    
    # Step 4: Processor Engine - Document Processing
    status_print("\n" + "=" * 72)
    status_print("STEP 4: Processor Engine - Document Processing")
    status_print("=" * 72)
    processor = CalculationEngine(schema_file=str(schema_path))
    df_processed = processor.process_data(df_mapped)
    
    # Export results
    df_processed.to_excel(export_paths["excel_path"], index=False)
    df_processed.to_csv(export_paths["csv_path"], index=False)
    
    status_print(f"✓ Processing complete")
    status_print(f"   CSV: {export_paths['csv_path']}")
    status_print(f"   Excel: {export_paths['excel_path']}")
    
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
    base_path = default_base_path()

    status_print(f"Project root path: {base_path}")
    
    # Handle Windows HOME env issues
    local_home = get_homedir()
    status_print(f"Resolved home directory: {local_home}")
    
    # load local defaults and parse CLI args
    native_defaults = build_native_defaults(base_path)
    args, cli_args = parse_cli_args(base_path)
    
    global DEBUG_DEV_MODE
    DEBUG_DEV_MODE = bool(cli_args.get("debug_dev_mode", native_defaults.get("debug_dev_mode", False)))
    
    # Test environment
    environment = test_environment()
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
    
    base_path = safe_resolve(Path(args.base_path))
    native_defaults = build_native_defaults(base_path)
    
    # Load schema parameters early for path resolution
    schema_path = safe_resolve(
        Path(cli_args.get("schema_register_file", native_defaults["schema_register_file"]))
    )
    try:
        schema_parameters = load_schema_parameters(schema_path)
        debug_print(f"Loaded schema parameters early: {schema_path}")
    except Exception as exc:
        debug_print(f"Could not load schema parameters early: {exc}")
        schema_parameters = {}
    
    # Merge parameters and resolve platform paths
    effective_parameters = native_defaults.copy()
    effective_parameters.update(schema_parameters)
    effective_parameters.update(cli_args)
    effective_parameters["schema_register_file"] = str(schema_path)
    effective_parameters = resolve_platform_paths(effective_parameters, base_path)
    
    # Run the engine pipeline
    try:
        results = run_engine_pipeline(
            base_path=base_path,
            schema_path=schema_path,
            effective_parameters=effective_parameters,
            nrows=args.nrows,
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
            status_print(str(exc))
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

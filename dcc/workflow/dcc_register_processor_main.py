#!/usr/bin/env python3
"""
Main DCC processing pipeline:
1. project_setup_validation
2. schema_validation
3. universal_column_mapper
4. universal_document_processor
"""

from __future__ import annotations

import argparse
import builtins
import importlib
import json
import platform
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pandas as pd

from project_setup_validation import ProjectSetupValidator
from schema_validation import SchemaValidator, write_validation_status
from universal_column_mapper import UniversalColumnMapper
from universal_document_processor import UniversalDocumentProcessor


DEBUG_DEV_MODE = False


def status_print(*args: Any, **kwargs: Any) -> None:
    builtins.print(*args, **kwargs)


def debug_print(*args: Any, **kwargs: Any) -> None:
    if DEBUG_DEV_MODE:
        builtins.print(*args, **kwargs)


def _default_base_path() -> Path:
    script_dir = Path(__file__).resolve().parent
    return script_dir.parent if script_dir.name.lower() == "workflow" else script_dir


def _default_schema_path(base_path: Path) -> Path:
    return base_path / "config" / "schemas" / "dcc_register_enhanced.json"


def _build_native_defaults(base_path: Path) -> Dict[str, Any]:
    return {
        "debug_dev_mode": False,
        "overwrite_existing_downloads": True,
        "start_col": "P",
        "end_col": "AP",
        "header_row_index": 4,
        "upload_sheet_name": "Prolog Submittals ",
        "schema_register_file": str(_default_schema_path(base_path)),
        "win_upload_file": r"K:\J Submission\Submittal and RFI Tracker Lists.xlsx",
        "win_download_path": r"K:\J Submission\AI Tools and Report",
        "linux_upload_file": str(base_path / "data" / "Submittal and RFI Tracker Lists.xlsx"),
        "linux_download_path": str(base_path / "output"),
        "upload_file_name": str(base_path / "data" / "Submittal and RFI Tracker Lists.xlsx"),
        "download_file_path": str(base_path / "output"),
    }


def _test_environment() -> Dict[str, Any]:
    status_print("Testing environment and required libraries...")
    required_modules = [
        "argparse",
        "json",
        "pathlib",
        "pandas",
        "numpy",
        "openpyxl",
    ]
    optional_modules = [
        "duckdb",
        "matplotlib",
    ]

    results: Dict[str, Any] = {
        "python_version": platform.python_version(),
        "platform": platform.system(),
        "required_modules": {},
        "optional_modules": {},
        "errors": [],
        "ready": True,
    }

    for module_name in required_modules:
        try:
            importlib.import_module(module_name)
            results["required_modules"][module_name] = "ok"
        except Exception as exc:
            results["required_modules"][module_name] = f"error: {exc}"
            results["errors"].append(f"{module_name}: {exc}")

    for module_name in optional_modules:
        try:
            importlib.import_module(module_name)
            results["optional_modules"][module_name] = "ok"
        except Exception as exc:
            results["optional_modules"][module_name] = f"warning: {exc}"

    results["ready"] = not results["errors"]
    if results["ready"]:
        status_print("Environment test passed.")
    else:
        status_print("Environment test failed.")
    debug_print(f"Environment details: {results}")
    return results


def _resolve_native_paths(native_defaults: Dict[str, Any]) -> Dict[str, Any]:
    status_print("Resolving platform paths...")
    resolved = native_defaults.copy()
    system_name = platform.system().lower()

    if system_name == "windows" and Path(native_defaults["win_upload_file"]).exists():
        resolved["upload_file_name"] = native_defaults["win_upload_file"]
        resolved["download_file_path"] = native_defaults["win_download_path"]
        debug_print("Windows path selection succeeded.")
    else:
        resolved["upload_file_name"] = native_defaults["linux_upload_file"]
        resolved["download_file_path"] = native_defaults["linux_download_path"]
        debug_print(f"Using non-Windows defaults for {system_name}.")

    Path(resolved["download_file_path"]).mkdir(parents=True, exist_ok=True)
    status_print(f"Current system detected: {system_name}")
    return resolved


def _create_parser(base_path: Path) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="DCC Universal Processing main pipeline.")
    parser.add_argument("--base-path", default=str(base_path), help="Project root path.")
    parser.add_argument("--schema-file", default=None, help="Alternative schema register JSON file.")
    parser.add_argument("--excel-file", default=None, help="Input Excel file.")
    parser.add_argument("--upload-sheet", default=None, help="Input Excel sheet name.")
    parser.add_argument("--output-file", default=None, help="Final CSV output file path.")
    parser.add_argument("--start-col", default=None, help="Input Excel start column.")
    parser.add_argument("--end-col", default=None, help="Input Excel end column.")
    parser.add_argument("--header-row", type=int, default=None, help="Header row index.")
    parser.add_argument("--overwrite", choices=["True", "False"], default=None, help="Overwrite output file if it exists.")
    parser.add_argument("--debug-mode", choices=["True", "False"], default=None, help="Enable debug print output.")
    parser.add_argument("--nrows", type=int, default=None, help="Optional row limit.")
    parser.add_argument("--json", action="store_true", help="Print final result as JSON.")
    return parser


def _parse_cli_args(base_path: Path) -> tuple[argparse.Namespace, Dict[str, Any]]:
    status_print("Reading CLI arguments...")
    parser = _create_parser(base_path)
    args, unknown_args = parser.parse_known_args()

    cli_args: Dict[str, Any] = {}
    if args.schema_file:
        cli_args["schema_register_file"] = args.schema_file
    if args.excel_file:
        cli_args["upload_file_name"] = args.excel_file
    if args.upload_sheet:
        cli_args["upload_sheet_name"] = args.upload_sheet
    if args.output_file:
        cli_args["output_file"] = args.output_file
        cli_args["download_file_path"] = str(Path(args.output_file).expanduser().resolve().parent)
    if args.start_col:
        cli_args["start_col"] = args.start_col
    if args.end_col:
        cli_args["end_col"] = args.end_col
    if args.header_row is not None:
        cli_args["header_row_index"] = args.header_row
    if args.overwrite:
        cli_args["overwrite_existing_downloads"] = args.overwrite == "True"
    if args.debug_mode:
        cli_args["debug_dev_mode"] = args.debug_mode == "True"

    if unknown_args:
        debug_print(f"Ignoring unknown CLI arguments: {unknown_args}")

    if cli_args:
        status_print("CLI overrides detected.")
        debug_print(f"CLI values: {cli_args}")
    else:
        status_print("No CLI overrides provided.")

    return args, cli_args


def _load_schema_parameters(schema_path: Path) -> Dict[str, Any]:
    with schema_path.open("r", encoding="utf-8") as handle:
        return json.load(handle).get("parameters", {})


def _resolve_effective_parameters(
    schema_path: Path,
    cli_args: Dict[str, Any],
    native_defaults: Dict[str, Any],
) -> Dict[str, Any]:
    status_print("Resolving effective parameters...")
    effective_parameters = native_defaults.copy()

    try:
        schema_parameters = _load_schema_parameters(schema_path)
        effective_parameters.update(schema_parameters)
        status_print(f"Loaded schema parameters from {schema_path}")
    except Exception as exc:
        status_print(f"WARNING: Could not load schema parameters from {schema_path}: {exc}")

    effective_parameters.update(cli_args)
    effective_parameters["schema_register_file"] = str(schema_path)
    debug_print(f"Effective parameters: {effective_parameters}")
    return effective_parameters


def _resolve_output_path(base_path: Path, effective_parameters: Dict[str, Any]) -> Path:
    explicit_output = effective_parameters.get("output_file")
    if explicit_output:
        return Path(explicit_output).expanduser().resolve()
    output_dir = Path(effective_parameters.get("download_file_path", base_path / "output")).expanduser().resolve()
    return output_dir / "processed_dcc_universal.csv"


def _load_excel_data(excel_path: Path, effective_parameters: Dict[str, Any], nrows: int | None = None) -> pd.DataFrame:
    sheet_name = effective_parameters.get("upload_sheet_name", "Prolog Submittals ")
    header_row = effective_parameters.get("header_row_index", 4)
    start_col = effective_parameters.get("start_col", "P")
    end_col = effective_parameters.get("end_col", "AP")
    usecols = f"{start_col}:{end_col}"

    status_print(f"Loading Excel file: {excel_path}")
    debug_print(
        f"Excel settings: sheet={sheet_name}, header_row={header_row}, usecols={usecols}, nrows={nrows}"
    )
    return pd.read_excel(
        excel_path,
        sheet_name=sheet_name,
        header=header_row,
        usecols=usecols,
        nrows=nrows,
    )


def _validate_output_path(output_path: Path, overwrite_existing: bool) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists() and not overwrite_existing:
        raise FileExistsError(
            f"Output file already exists: {output_path}. Use --overwrite True or choose another output file."
        )


def run_pipeline(
    base_path: Path,
    schema_path: Path,
    effective_parameters: Dict[str, Any],
    nrows: int | None = None,
) -> Dict[str, Any]:
    excel_path = Path(effective_parameters["upload_file_name"]).expanduser().resolve()
    output_path = _resolve_output_path(base_path, effective_parameters)
    _validate_output_path(output_path, bool(effective_parameters.get("overwrite_existing_downloads", True)))

    status_print("Step 1: Project setup validation")
    setup_validator = ProjectSetupValidator(base_path=base_path)
    setup_results = setup_validator.validate()
    if not setup_results.get("ready"):
        raise ValueError(setup_validator.format_report(setup_results))

    status_print("Step 2: Schema validation")
    schema_validator = SchemaValidator(schema_path)
    schema_results = schema_validator.validate()
    write_validation_status(schema_results)
    if not schema_results.get("ready"):
        raise ValueError(json.dumps(schema_results, indent=2))

    status_print("Step 3: Universal column mapping")
    df_raw = _load_excel_data(excel_path, effective_parameters, nrows=nrows)
    mapper = UniversalColumnMapper(schema_file=str(schema_path))
    mapping_result = mapper.detect_columns(df_raw.columns.tolist())
    df_mapped = mapper.rename_dataframe_columns(df_raw, mapping_result)

    status_print("Step 4: Universal document processing")
    processor = UniversalDocumentProcessor(schema_file=str(schema_path))
    df_processed = processor.process_data(df_mapped)
    df_processed.to_csv(output_path, index=False)

    return {
        "base_path": str(base_path),
        "schema_path": str(schema_path),
        "excel_path": str(excel_path),
        "output_path": str(output_path),
        "raw_shape": list(df_raw.shape),
        "mapped_shape": list(df_mapped.shape),
        "processed_shape": list(df_processed.shape),
        "matched_count": mapping_result["matched_count"],
        "total_headers": mapping_result["total_headers"],
        "match_rate": mapping_result["match_rate"],
        "missing_required": mapping_result["missing_required"],
        "ready": True,
    }


def _print_summary(results: Dict[str, Any]) -> None:
    status_print("DCC REGISTER PROCESSOR PIPELINE")
    status_print("=" * 72)
    status_print(f"Base Path: {results['base_path']}")
    status_print(f"Schema File: {results['schema_path']}")
    status_print(f"Excel File: {results['excel_path']}")
    status_print(f"Output File: {results['output_path']}")
    status_print(f"Raw Shape: {tuple(results['raw_shape'])}")
    status_print(f"Mapped Shape: {tuple(results['mapped_shape'])}")
    status_print(f"Processed Shape: {tuple(results['processed_shape'])}")
    status_print(f"Matched Headers: {results['matched_count']} / {results['total_headers']}")
    status_print(f"Match Rate: {results['match_rate']:.1%}")
    if results["missing_required"]:
        status_print(f"Missing Required Columns: {results['missing_required']}")
    status_print("Ready: YES")


def main() -> int:
    base_path = _default_base_path()
    native_defaults = _resolve_native_paths(_build_native_defaults(base_path))
    args, cli_args = _parse_cli_args(base_path)

    global DEBUG_DEV_MODE
    DEBUG_DEV_MODE = bool(cli_args.get("debug_dev_mode", native_defaults.get("debug_dev_mode", False)))

    environment = _test_environment()
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

    base_path = Path(args.base_path).expanduser().resolve()
    schema_path = Path(cli_args.get("schema_register_file", native_defaults["schema_register_file"])).expanduser().resolve()
    effective_parameters = _resolve_effective_parameters(schema_path, cli_args, native_defaults)

    try:
        results = run_pipeline(
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
        _print_summary(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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
import os
import platform
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


DEBUG_DEV_MODE = False


def status_print(*args: Any, **kwargs: Any) -> None:
    kwargs.setdefault("flush", True)
    builtins.print(*args, **kwargs)


def debug_print(*args: Any, **kwargs: Any) -> None:
    if DEBUG_DEV_MODE:
        kwargs.setdefault("flush", True)
        builtins.print(*args, **kwargs)


def _safe_resolve(path: Path) -> Path:
    """Return an absolute path without filesystem I/O (no resolve, no expanduser)."""
    return Path(path).absolute()


def _default_base_path() -> Path:
    # Use script directory directly. Do NOT use resolve() or cwd,
    # which inject restricted network paths on Windows UNC shares.
    script_dir = Path(__file__).parent
    if script_dir.name.lower() == "workflow":
        script_dir = script_dir.parent
    return Path(script_dir).absolute()


def _default_schema_path(base_path: Path) -> Path:
    return base_path / "config" / "schemas" / "dcc_register_enhanced.json"


def _build_native_defaults(base_path: Path) -> Dict[str, Any]:
    """
    Build native default parameters for the DCC processing pipeline.

    These are the lowest-priority defaults in the parameter precedence chain:
    1. CLI arguments (highest) → 2. Schema parameters → 3. Native defaults (lowest)

    Paths are defined here, not in mapper or processor files.
    """
    return {
        "debug_dev_mode": False,
        "overwrite_existing_downloads": True,
        "start_col": "P",
        "end_col": "AP",
        "header_row_index": 4,
        "upload_sheet_name": "Prolog Submittals ",
        "schema_register_file": str(_default_schema_path(base_path)),
        # Windows network drive paths (primary if K: exists)
        "win_upload_file": r"K:\J Submission\Submittal and RFI Tracker Lists.xlsx",
        "win_download_path": r"K:\J Submission\AI Tools and Report",
        # Windows fallback paths (relative to base_path)
        "win_upload_file_fallback": str(base_path / "data" / "Submittal and RFI Tracker Lists.xlsx"),
        "win_download_path_fallback": str(base_path / "output"),
        # Linux/Colab paths
        "linux_upload_file": str(base_path / "data" / "Submittal and RFI Tracker Lists.xlsx"),
        "linux_download_path": str(base_path / "output"),
        "colab_upload_file": "/content/sample_data/Submittal and RFI Tracker Lists.xlsx",
        "colab_download_path": "/content/output",
        # Active paths (resolved by _resolve_native_paths)
        "upload_file_name": str(base_path / "data" / "Submittal and RFI Tracker Lists.xlsx"),
        "download_file_path": str(base_path / "output"),
    }


def _import_dependency(module_name: str, attribute_names: list[str] | None = None) -> tuple[Any, str | None]:
    """Import a module and optional attributes with clear failure reporting."""
    try:
        module = importlib.import_module(module_name)
        if not attribute_names:
            return module, None
        values = [getattr(module, name) for name in attribute_names]
        if len(values) == 1:
            return values[0], None
        return tuple(values), None
    except ModuleNotFoundError as exc:
        return None, f"Missing module '{module_name}': {exc}"
    except AttributeError as exc:
        return None, f"Module '{module_name}' is missing expected logic: {exc}"
    except Exception as exc:
        return None, f"Failed to import '{module_name}': {exc}"


def _load_pipeline_dependencies() -> Dict[str, Any]:
    """Load local pipeline modules lazily so startup can fail gracefully."""
    dependencies: Dict[str, Any] = {}
    imports = {
        "project_setup_validator_cls": ("project_setup_validation", ["ProjectSetupValidator"]),
        "schema_validation_imports": ("schema_validation", ["SchemaValidator", "write_validation_status"]),
        "universal_column_mapper_cls": ("universal_column_mapper", ["UniversalColumnMapper"]),
        "universal_document_processor_cls": ("universal_document_processor", ["UniversalDocumentProcessor"]),
    }

    for dependency_name, (module_name, attribute_names) in imports.items():
        imported_value, error = _import_dependency(module_name, attribute_names)
        if error is not None:
            raise ImportError(error)
        dependencies[dependency_name] = imported_value

    return dependencies


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
    local_dependencies = {
        "project_setup_validation": ["ProjectSetupValidator"],
        "schema_validation": ["SchemaValidator", "write_validation_status"],
        "universal_column_mapper": ["UniversalColumnMapper"],
        "universal_document_processor": ["UniversalDocumentProcessor"],
    }

    results: Dict[str, Any] = {
        "python_version": platform.python_version(),
        "platform": platform.system(),
        "required_modules": {},
        "optional_modules": {},
        "local_dependencies": {},
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

    for module_name, attribute_names in local_dependencies.items():
        _, error = _import_dependency(module_name, attribute_names)
        if error is None:
            results["local_dependencies"][module_name] = "ok"
        else:
            results["local_dependencies"][module_name] = f"error: {error}"
            results["errors"].append(error)

    results["ready"] = not results["errors"]
    if results["ready"]:
        status_print("Environment test passed.")
    else:
        status_print("Environment test failed.")
    debug_print(f"Environment details: {results}")
    return results


def _resolve_native_paths(native_defaults: Dict[str, Any], base_path: Path) -> Dict[str, Any]:
    """
    Resolve platform-specific paths from native defaults.

    On Windows: tries K: network drive first, falls back to relative paths if not found.
    On Linux/Mac: uses the linux_upload_file and linux_download_path, resolving relative paths against base_path.
    Also resolves upload_file_name and download_file_path if they are relative.
    """
    status_print("Resolving platform paths...")
    resolved = native_defaults.copy()
    system_name = platform.system().lower()

    if system_name == "windows":
        if Path(native_defaults["win_upload_file"]).exists():
            resolved["upload_file_name"] = native_defaults["win_upload_file"]
            resolved["download_file_path"] = native_defaults["win_download_path"]
            debug_print("Windows network drive (K:) path selection succeeded.")
        else:
            resolved["upload_file_name"] = native_defaults["win_upload_file_fallback"]
            resolved["download_file_path"] = native_defaults["win_download_path_fallback"]
            debug_print("Windows network drive (K:) not found, using relative paths.")
    else:
        # Resolve relative paths against base_path for Linux/Mac
        upload_path = Path(native_defaults["linux_upload_file"])
        download_path = Path(native_defaults["linux_download_path"])
        
        if not upload_path.is_absolute():
            upload_path = base_path / upload_path
        if not download_path.is_absolute():
            download_path = base_path / download_path
            
        resolved["upload_file_name"] = str(upload_path)
        resolved["download_file_path"] = str(download_path)
        debug_print(f"Using non-Windows defaults for {system_name} (resolved against base_path).")

    # Also resolve upload_file_name and download_file_path if they're relative paths
    # (These may come from schema parameters and should be resolved against base_path or home folder)
    active_upload = Path(resolved.get("upload_file_name", ""))
    active_download = Path(resolved.get("download_file_path", ""))
    
    if not active_upload.is_absolute():
        # Resolve relative paths against base_path
        resolved["upload_file_name"] = str(base_path / active_upload)
        debug_print(f"Resolved upload_file_name against base_path: {resolved['upload_file_name']}")
    
    if not active_download.is_absolute():
        # Resolve relative paths against base_path
        resolved["download_file_path"] = str(base_path / active_download)
        debug_print(f"Resolved download_file_path against base_path: {resolved['download_file_path']}")

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
        cli_args["download_file_path"] = str(_safe_resolve(Path(args.output_file)).parent)
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
        return _safe_resolve(Path(explicit_output))
    output_dir = _safe_resolve(Path(effective_parameters.get("download_file_path", str(base_path / "output"))))
    return output_dir / "processed_dcc_universal.csv"


def _resolve_export_paths(base_path: Path, effective_parameters: Dict[str, Any]) -> Dict[str, Path]:
    base_output_path = _resolve_output_path(base_path, effective_parameters)
    output_dir = base_output_path.parent
    stem = base_output_path.stem or "processed_dcc_universal"
    return {
        "output_dir": output_dir,
        "csv_path": output_dir / f"{stem}.csv",
        "excel_path": output_dir / f"{stem}.xlsx",
        "summary_path": output_dir / "processing_summary.txt",
    }


def _load_excel_data(excel_path: Path, effective_parameters: Dict[str, Any], nrows: int | None = None) -> Any:
    pd_module, error = _import_dependency("pandas")
    if error is not None:
        raise ImportError(f"Failed to import pandas for Excel loading: {error}")

    sheet_name = effective_parameters.get("upload_sheet_name", "Prolog Submittals ")
    header_row = effective_parameters.get("header_row_index", 4)
    start_col = effective_parameters.get("start_col", "P")
    end_col = effective_parameters.get("end_col", "AP")
    usecols = f"{start_col}:{end_col}"

    status_print(f"📁 Loading Excel file: {excel_path}")
    status_print(f"   Sheet: '{sheet_name}'")
    status_print(f"   Header row: {header_row + 1} (0-indexed: {header_row})")
    status_print(f"   Column range: {start_col}:{end_col}")
    status_print(f"   Row limit: {nrows if nrows else 'all'}")
    
    debug_print(
        f"Excel settings: sheet={sheet_name}, header_row={header_row}, usecols={usecols}, nrows={nrows}"
    )
    
    # Read Excel with explicit parameters to ensure correct header and column range
    df = pd_module.read_excel(
        excel_path,
        sheet_name=sheet_name,
        header=header_row,
        usecols=usecols,
        nrows=nrows,
    )
    
    # DEBUG: Log raw DataFrame state immediately after loading
    import logging
    raw_logger = logging.getLogger('excel_loader')
    raw_logger.info(f"[DEBUG] Raw DataFrame after Excel load - shape: {df.shape}")
    raw_logger.info(f"[DEBUG] Raw DataFrame columns type: {type(df.columns)}")
    raw_logger.info(f"[DEBUG] Raw DataFrame first 10 columns: {list(df.columns)[:10]}")
    has_tuples = any(isinstance(c, tuple) for c in df.columns)
    raw_logger.info(f"[DEBUG] Has tuple columns: {has_tuples}")
    if has_tuples:
        tuple_cols = [c for c in df.columns if isinstance(c, tuple)]
        raw_logger.warning(f"[DEBUG] Tuple columns: {tuple_cols}")
    
    # Validate that columns were loaded successfully
    if len(df.columns) == 0:
        raise ValueError(
            f"No columns loaded from Excel file. "
            f"Check if header_row_index={header_row} and column range {start_col}:{end_col} are correct."
        )
    
    # Flatten MultiIndex columns if present (can happen with merged cells in Excel)
    if hasattr(pd_module, 'MultiIndex') and isinstance(df.columns, pd_module.MultiIndex):
        status_print("   ⚠️  Flattening MultiIndex columns from Excel header")
        df.columns = ['_'.join(str(level) for level in levels).strip('_') 
                      for levels in df.columns]
    
    # Remove any fully empty columns that might have been created
    df = df.dropna(axis=1, how='all')
    
    status_print(f"   ✓ Loaded {len(df)} rows × {len(df.columns)} columns")
    
    return df


def _validate_output_path(output_path: Path, overwrite_existing: bool) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists() and not overwrite_existing:
        raise FileExistsError(
            f"Output file already exists: {output_path}. Use --overwrite True or choose another output file."
        )


def _validate_export_paths(export_paths: Dict[str, Path], overwrite_existing: bool) -> None:
    export_paths["output_dir"].mkdir(parents=True, exist_ok=True)
    if overwrite_existing:
        return

    for file_key in ("csv_path", "excel_path", "summary_path"):
        target_path = export_paths[file_key]
        if target_path.exists():
            raise FileExistsError(
                f"Output file already exists: {target_path}. Use --overwrite True or choose another output file."
            )


def _write_processing_summary(
    summary_path: Path,
    input_file: Path,
    main_schema_path: Path,
    schema_results: Dict[str, Any],
    raw_columns: list[str],
    mapped_columns: list[str],
    processed_columns: list[str],
    raw_shape: tuple[int, int],
    mapped_shape: tuple[int, int],
    processed_shape: tuple[int, int],
    raw_null_counts: Dict[str, int],
    mapped_null_counts: Dict[str, int],
    processed_null_counts: Dict[str, int],
    mapping_result: Dict[str, Any],
    schema_reference_count: int,
    csv_path: Path,
    excel_path: Path,
) -> None:
    detected_columns = mapping_result.get("detected_columns", {})
    unmatched_headers = mapping_result.get("unmatched_headers", [])
    missing_required = mapping_result.get("missing_required", [])
    processed_added_columns = [column for column in processed_columns if column not in mapped_columns]
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    schema_files = [str(main_schema_path)]
    schema_files.extend(
        item.get("resolved_path")
        for item in schema_results.get("references", [])
        if item.get("resolved_path")
    )
    schema_files = list(dict.fromkeys(schema_files))

    warnings: list[str] = []
    warnings.extend(f"Missing required mapped column: {column}" for column in missing_required)
    warnings.extend(f"Unmatched input header: {header}" for header in unmatched_headers)
    warnings.extend(f"Column created during processing: {column}" for column in processed_added_columns)
    warnings.extend(schema_results.get("errors", []))

    with summary_path.open("w", encoding="utf-8") as handle:
        handle.write("Universal Document Processing Summary\n")
        handle.write("=" * 50 + "\n\n")
        handle.write(f"Processing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        handle.write("Input and Output Files:\n")
        handle.write(f"  Input Data File: {input_file}\n")
        handle.write(f"  CSV Export: {csv_path}\n")
        handle.write(f"  Excel Export: {excel_path}\n")
        handle.write(f"  Summary Report: {summary_path}\n\n")

        handle.write("Schema Files Used:\n")
        for schema_file in schema_files:
            handle.write(f"  - {schema_file}\n")
        handle.write("\n")

        handle.write("Dataset Shapes:\n")
        handle.write(f"  Raw Input Shape: {raw_shape}\n")
        handle.write(f"  Mapped Data Shape: {mapped_shape}\n")
        handle.write(f"  Processed Data Shape: {processed_shape}\n\n")

        handle.write("Column Overview:\n")
        handle.write(f"  Column Mapping Success Rate: {mapping_result['match_rate']:.1%}\n")
        handle.write(f"  Matched Headers: {mapping_result['matched_count']} / {mapping_result['total_headers']}\n")
        handle.write(f"  Missing Required Columns: {len(mapping_result['missing_required'])}\n")
        handle.write(f"  Schema References Loaded: {schema_reference_count}\n\n")

        handle.write("Columns Read From Input:\n")
        for index, column_name in enumerate(raw_columns, start=1):
            handle.write(f"  {index:02d}. {column_name}\n")
        handle.write("\n")

        handle.write("Column Mapping Details:\n")
        for original_header in raw_columns:
            if original_header in detected_columns:
                mapped_column = detected_columns[original_header]["mapped_column"]
                matched_alias = detected_columns[original_header].get("matched_alias", "")
                match_score = detected_columns[original_header].get("match_score", 0.0)
                handle.write(
                    f"  - {original_header} -> {mapped_column} "
                    f"(alias='{matched_alias}', score={match_score:.2f})\n"
                )
            else:
                handle.write(f"  - {original_header} -> NOT MAPPED\n")
        handle.write("\n")

        handle.write("Mapped Columns After Rename:\n")
        for index, column_name in enumerate(mapped_columns, start=1):
            handle.write(f"  {index:02d}. {column_name}\n")
        handle.write("\n")

        handle.write("Processed Columns:\n")
        for index, column_name in enumerate(processed_columns, start=1):
            marker = " [ADDED DURING PROCESSING]" if column_name in processed_added_columns else ""
            handle.write(f"  {index:02d}. {column_name}{marker}\n")
        handle.write("\n")

        handle.write("Null Summary:\n")
        handle.write("  Raw Input Columns With Nulls:\n")
        raw_null_items = [(column, count) for column, count in raw_null_counts.items() if count > 0]
        if raw_null_items:
            for column_name, count in sorted(raw_null_items, key=lambda item: (-item[1], item[0])):
                handle.write(f"    - {column_name}: {count}\n")
        else:
            handle.write("    - None\n")

        handle.write("  Mapped Columns With Nulls:\n")
        mapped_null_items = [(column, count) for column, count in mapped_null_counts.items() if count > 0]
        if mapped_null_items:
            for column_name, count in sorted(mapped_null_items, key=lambda item: (-item[1], item[0])):
                handle.write(f"    - {column_name}: {count}\n")
        else:
            handle.write("    - None\n")

        handle.write("  Processed Columns With Nulls:\n")
        processed_null_items = [(column, count) for column, count in processed_null_counts.items() if count > 0]
        if processed_null_items:
            for column_name, count in sorted(processed_null_items, key=lambda item: (-item[1], item[0])):
                handle.write(f"    - {column_name}: {count}\n")
        else:
            handle.write("    - None\n")
        handle.write("\n")

        handle.write("Warnings and Potential Issues:\n")
        if warnings:
            for warning in warnings:
                handle.write(f"  - {warning}\n")
        else:
            handle.write("  - None\n")


def run_pipeline(
    base_path: Path,
    schema_path: Path,
    effective_parameters: Dict[str, Any],
    nrows: int | None = None,
) -> Dict[str, Any]:
    dependencies = _load_pipeline_dependencies()
    project_setup_validator_cls = dependencies["project_setup_validator_cls"]
    schema_validator_cls, write_validation_status_fn = dependencies["schema_validation_imports"]
    universal_column_mapper_cls = dependencies["universal_column_mapper_cls"]
    universal_document_processor_cls = dependencies["universal_document_processor_cls"]

    excel_path = _safe_resolve(Path(effective_parameters["upload_file_name"]))
    export_paths = _resolve_export_paths(base_path, effective_parameters)
    _validate_export_paths(export_paths, bool(effective_parameters.get("overwrite_existing_downloads", True)))

    status_print("Step 1: Project setup validation")
    setup_validator = project_setup_validator_cls(base_path=base_path)
    setup_results = setup_validator.validate()
    if not setup_results.get("ready"):
        raise ValueError(setup_validator.format_report(setup_results))
    status_print("Step 1 complete")

    status_print("Step 2: Schema validation")
    schema_validator = schema_validator_cls(schema_path)
    schema_results = schema_validator.validate()
    write_validation_status_fn(schema_results)
    if not schema_results.get("ready"):
        raise ValueError(json.dumps(schema_results, indent=2))
    status_print("Step 2 complete")

    status_print("Step 3: Universal column mapping")
    df_raw = _load_excel_data(excel_path, effective_parameters, nrows=nrows)
    
    # Safeguard: Ensure DataFrame columns are strings, not tuples (from Excel MultiIndex)
    pd_module = __import__('pandas')
    if hasattr(pd_module, 'MultiIndex') and isinstance(df_raw.columns, pd_module.MultiIndex):
        status_print("   ⚠️  Flattening MultiIndex columns before mapping")
        df_raw.columns = ['_'.join(str(level) for level in levels).strip('_') 
                          for levels in df_raw.columns]
    elif len(df_raw.columns) > 0 and isinstance(df_raw.columns[0], tuple):
        status_print("   ⚠️  Converting tuple columns to strings before mapping")
        df_raw.columns = ['_'.join(str(level) for level in levels).strip('_') 
                          for levels in df_raw.columns]

    mapper = universal_column_mapper_cls(schema_file=str(schema_path))
    mapping_result = mapper.detect_columns(df_raw.columns.tolist())
    df_mapped = mapper.rename_dataframe_columns(df_raw, mapping_result)
    status_print("Step 3 complete")

    status_print("Step 4: Universal document processing")
    processor = universal_document_processor_cls(schema_file=str(schema_path))
    df_processed = processor.process_data(df_mapped)
    df_processed.to_excel(export_paths["excel_path"], index=False)
    df_processed.to_csv(export_paths["csv_path"], index=False)
    schema_reference_count = len(getattr(processor, "schema_data", {}).get("schema_references", {}))
    _write_processing_summary(
        summary_path=export_paths["summary_path"],
        input_file=excel_path,
        main_schema_path=schema_path,
        schema_results=schema_results,
        raw_columns=df_raw.columns.tolist(),
        mapped_columns=df_mapped.columns.tolist(),
        processed_columns=df_processed.columns.tolist(),
        raw_shape=tuple(df_raw.shape),
        mapped_shape=tuple(df_mapped.shape),
        processed_shape=tuple(df_processed.shape),
        raw_null_counts={column: int(count) for column, count in df_raw.isna().sum().items()},
        mapped_null_counts={column: int(count) for column, count in df_mapped.isna().sum().items()},
        processed_null_counts={column: int(count) for column, count in df_processed.isna().sum().items()},
        mapping_result=mapping_result,
        schema_reference_count=schema_reference_count,
        csv_path=export_paths["csv_path"],
        excel_path=export_paths["excel_path"],
    )
    status_print(
        "Step 4 complete: output written to "
        f"{export_paths['csv_path']}, {export_paths['excel_path']}, and {export_paths['summary_path']}"
    )

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
        "missing_required": mapping_result["missing_required"],
        "ready": True,
    }


def _print_summary(results: Dict[str, Any]) -> None:
    status_print("DCC REGISTER PROCESSOR PIPELINE")
    status_print("=" * 72)
    status_print(f"Base Path: {results['base_path']}")
    status_print(f"Schema File: {results['schema_path']}")
    status_print(f"Excel File: {results['excel_path']}")
    status_print(f"CSV Output: {results['csv_output_path']}")
    status_print(f"Excel Output: {results['excel_output_path']}")
    status_print(f"Summary File: {results['summary_path']}")
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

    # On Windows with mapped network drives, clean HOME env if it points
    # to a non-existent network path (e.g., K:\home from cloud dev env).
    if platform.system() == "Windows":
        home = os.environ.get("HOME", "")
        if home:
            try:
                home_exists = Path(home).exists()
            except (OSError, PermissionError):
                home_exists = False
            if not home_exists:
                # Fall back to LOCALAPPDATA (always local on Windows)
                local_home = os.environ.get("LOCALAPPDATA", "")
                if local_home:
                    os.environ["HOME"] = local_home
                else:
                    os.environ.pop("HOME", None)

    # Ensure working directory is always accessible.
    # If the shell's cwd points to an inaccessible network share, switch to the script's directory.
    try:
        os.chdir(base_path)
    except (OSError, PermissionError):
        pass

    native_defaults = _build_native_defaults(base_path)
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

    base_path = _safe_resolve(Path(args.base_path))
    native_defaults = _resolve_native_paths(_build_native_defaults(base_path), base_path)
    schema_path = _safe_resolve(Path(cli_args.get("schema_register_file", native_defaults["schema_register_file"])))
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

"""
CLI argument parsing and parameter resolution for the DCC pipeline.
"""
import argparse
import sys
from pathlib import Path
from typing import Tuple, Dict, Any

from core_engine.logging import set_debug_level
from utility_engine.console import status_print, debug_print
from core_engine.paths import default_base_path, default_schema_path

VERBOSE_LEVELS = {
    "quiet": 0,
    "normal": 1,
    "debug": 2,
    "trace": 3,
}

def create_parser(base_path: Path) -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(description="DCC Engine Pipeline - Modular processing workflow.")
    parser.add_argument("--base-path", default=str(base_path), help="Project root path.")
    parser.add_argument("--schema-file", default=None, help="Alternative schema register JSON file.")
    parser.add_argument("--excel-file", default=None, help="Input Excel file.")
    parser.add_argument("--upload-sheet", default=None, help="Input Excel sheet name.")
    parser.add_argument("--output-file", default=None, help="Final CSV output file path.")
    parser.add_argument("--start-col", default=None, help="Input Excel start column.")
    parser.add_argument("--end-col", default=None, help="Input Excel end column.")
    parser.add_argument("--header-row", type=int, default=None, help="Header row index.")
    parser.add_argument("--overwrite", choices=["True", "False"], default=None, help="Overwrite output file.")
    parser.add_argument("--verbose", "-v", choices=["quiet", "normal", "debug", "trace"], default="normal", help="Output verbosity level.")
    parser.add_argument("--debug-mode", choices=["True", "False"], default=None, help="(DEPRECATED) Use --verbose debug instead.")
    parser.add_argument("--nrows", type=int, default=None, help="Optional row limit.")
    parser.add_argument("--json", action="store_true", help="Print final result as JSON.")
    return parser


def parse_cli_args(base_path: Path | None = None) -> Tuple[argparse.Namespace, Dict[str, Any], bool]:
    """Parse CLI arguments and return the namespace, override dict, and a status boolean."""
    if base_path is None:
        base_path = default_base_path()
        
    parser = create_parser(base_path)
    args, unknown_args = parser.parse_known_args()
    
    verbose_level = VERBOSE_LEVELS.get(args.verbose, 1)
    set_debug_level(verbose_level)
    
    raw_argv = sys.argv[1:]
    verbose_explicitly_set = "--verbose" in raw_argv or "-v" in raw_argv

    cli_args: Dict[str, Any] = {}

    if verbose_explicitly_set:
        cli_args["verbose_level"] = args.verbose
    if args.schema_file:
        cli_args["schema_register_file"] = args.schema_file
    if args.excel_file:
        cli_args["upload_file_name"] = args.excel_file
    if args.upload_sheet:
        cli_args["upload_sheet_name"] = args.upload_sheet
    if args.output_file:
        cli_args["output_file"] = args.output_file
        cli_args["download_file_path"] = str(Path(args.output_file).resolve().parent)
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
    
    cli_overrides_provided = bool(cli_args)

    return args, cli_args, cli_overrides_provided


def build_native_defaults(base_path: Path) -> Dict[str, Any]:
    """
    Build native default parameters for DCC processing pipeline.
    Precedence: CLI args → Schema params → Native defaults
    
    Standardized parameter keys across CLI, schema, and native defaults:
    - upload_file_name: Input Excel file path
    - download_file_path: Output directory path
    - schema_register_file: Schema file path
    - upload_sheet_name: Excel sheet name
    - start_col: Start column for processing
    - end_col: End column for processing
    - header_row_index: Header row index
    """
    status_print("Building native default parameters...", min_level=3)
    
    # Platform-specific defaults (for reference, not used in precedence)
    platform_defaults = {
        "win_upload_file": r"K:\J Submission\Submittal and RFI Tracker Lists.xlsx",
        "win_download_path": r"K:\J Submission\AI Tools and Report\data_output",
        "linux_upload_file": str(base_path / "data" / "Submittal and RFI Tracker Lists.xlsx"),
        "linux_download_path": str(base_path / "output"),
        "colab_upload_file": "/content/sample_data/Submittal and RFI Tracker Lists.xlsx",
        "colab_download_path": "/content/output",
    }
    
    # Standardized native defaults using consistent keys
    return {
        # Core processing parameters (consistent with CLI and schema)
        "debug_dev_mode": False,
        "overwrite_existing_downloads": True,
        "start_col": "P",
        "end_col": "AP",
        "header_row_index": 4,
        "upload_sheet_name": "Prolog Submittals ",
        "schema_register_file": str(default_schema_path(base_path)),
        "upload_file_name": str(base_path / "data" / "Submittal and RFI Tracker Lists.xlsx"),
        "download_file_path": str(base_path / "output"),
        
        # Platform-specific defaults (kept for reference, not used in precedence)
        "platform_defaults": platform_defaults,
        
        # Legacy fallback keys (for backward compatibility)
        "win_upload_file_fallback": str(base_path / "data" / "Submittal and RFI Tracker Lists.xlsx"),
        "win_download_path_fallback": str(base_path / "output"),
    }


def resolve_effective_parameters(
    schema_path: Path,
    cli_args: Dict[str, Any],
    native_defaults: Dict[str, Any],
    load_schema_params_fn: Any = None,
) -> Dict[str, Any]:
    """
    Resolve effective parameters with precedence: CLI → Schema → Native.
    """
    status_print("Resolving effective parameters...", min_level=3)
    effective_parameters = native_defaults.copy()
    
    if load_schema_params_fn:
        try:
            schema_parameters = load_schema_params_fn(schema_path)
            effective_parameters.update(schema_parameters)
            status_print(f"Loaded schema parameters from {schema_path}", min_level=3)
        except Exception as exc:
            status_print(f"WARNING: Could not load schema parameters: {exc}", min_level=2)
    
    effective_parameters.update(cli_args)
    effective_parameters["schema_register_file"] = str(schema_path)
    debug_print(f"Effective parameters: {effective_parameters}")
    return effective_parameters

"""
CLI argument parsing functions.
"""
import argparse
import sys
from pathlib import Path
from typing import Tuple, Dict, Any

from core_engine.logging import set_debug_level
from utility_engine.console import status_print, debug_print
from core_engine.paths import default_base_path, default_schema_path
from utility_engine.validation import (
    ParameterTypeRegistry,
    ParameterValidator,
    get_parameter_registry,
)


VERBOSE_LEVELS = {
    "quiet": 0,
    "normal": 1,
    "debug": 2,
    "trace": 3,
}


def create_parser(base_path: Path) -> argparse.ArgumentParser:
    """
    Create CLI argument parser.

    Breadcrumb: base_path -> create ArgumentParser -> add arguments from schema

    Note: Argument names should match global_parameters.json schema definitions.
    For schema-driven CLI, use create_parser_from_registry() instead.

    Args:
        base_path: Project root path for defaults

    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(description="DCC Engine Pipeline - Modular processing workflow.")
    parser.add_argument("--base-path", default=str(base_path), help="Project root path.")
    parser.add_argument("--schema-file", default=None, help="Alternative schema register JSON file.")
    parser.add_argument("--excel-file", "-e", default=None, help="Input Excel file (maps to upload_file_name).")
    parser.add_argument("--upload-sheet", default=None, help="Input Excel sheet name (maps to upload_sheet_name).")
    parser.add_argument("--output-path", default=None, help="Output directory path (maps to download_file_path).")
    parser.add_argument("--output-file", default=None, help="Final output file name (not full path).")
    parser.add_argument("--start-col", default=None, help="Input Excel start column.")
    parser.add_argument("--end-col", default=None, help="Input Excel end column.")
    parser.add_argument("--header-row", type=int, default=None, help="Header row index (maps to header_row_index).")
    parser.add_argument("--overwrite", choices=["True", "False"], default=None, help="Overwrite existing output (maps to overwrite_existing_downloads).")
    parser.add_argument("--verbose", "-v", choices=["quiet", "normal", "debug", "trace"], default="normal", help="Output verbosity level.")
    parser.add_argument("--nrows", type=int, default=None, help="Optional row limit.")
    parser.add_argument("--json", action="store_true", help="Print final result as JSON.")
    return parser


def parse_cli_args(base_path: Path | None = None, pipeline_dir: str = "workflow") -> Tuple[argparse.Namespace, Dict[str, Any], bool]:
    """Parse CLI arguments and return the namespace, override dict, and a status boolean."""
    if base_path is None:
        base_path = default_base_path(pipeline_dir)

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
    # Handle output path (directory) from schema
    if args.output_path:
        cli_args["download_file_path"] = args.output_path
    # Handle output file name from schema (separate from directory)
    if args.output_file:
        cli_args["output_file"] = args.output_file
        # Only derive download_file_path from output_file if output_path not explicitly set
        if not args.output_path:
            cli_args["download_file_path"] = str(Path(args.output_file).resolve().parent)
    if args.start_col:
        cli_args["start_col"] = args.start_col
    if args.end_col:
        cli_args["end_col"] = args.end_col
    if args.header_row is not None:
        cli_args["header_row_index"] = args.header_row
    if args.overwrite:
        cli_args["overwrite_existing_downloads"] = args.overwrite == "True"
    if unknown_args:
        debug_print(f"Ignoring unknown CLI arguments: {unknown_args}")

    cli_overrides_provided = bool(cli_args)

    return args, cli_args, cli_overrides_provided

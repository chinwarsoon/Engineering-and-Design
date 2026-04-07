import argparse
from pathlib import Path
from typing import Tuple, Dict, Any

# Assuming these are your custom logger functions
# Use relative imports since it's inside the package
from .logging import status_print, debug_print 

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
    parser.add_argument("--debug-mode", choices=["True", "False"], default=None, help="Enable debug output.")
    parser.add_argument("--nrows", type=int, default=None, help="Optional row limit.")
    parser.add_argument("--json", action="store_true", help="Print final result as JSON.")
    return parser


def parse_cli_args(base_path: Path) -> Tuple[argparse.Namespace, Dict[str, Any]]:
    """Parse CLI arguments and return as dictionary."""
    status_print("Reading CLI arguments...")
    parser = create_parser(base_path)
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
        cli_args["download_file_path"] = str(safe_resolve(Path(args.output_file)).parent)
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
        status_print(f"CLI overrides detected. CLI values: {cli_args}")
    else:
        status_print("No CLI overrides provided.")
    
    return args, cli_args
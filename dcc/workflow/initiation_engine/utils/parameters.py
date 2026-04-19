"""
Parameter resolution and default configuration for the DCC processing pipeline.
"""

from pathlib import Path
from typing import Any, Dict

from .logging import status_print, debug_print
from .paths import default_schema_path

def build_native_defaults(base_path: Path) -> Dict[str, Any]:
    """
    Build native default parameters for the DCC processing pipeline.
    Precedence: CLI args → Schema params → Native defaults
    """
    status_print("Building native default parameters...", min_level=3)
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
    load_schema_params_fn: Any = None,
) -> Dict[str, Any]:
    """
    Resolve effective parameters with precedence: CLI → Schema → Native.
    
    Args:
        schema_path: Path to the schema file.
        cli_args: Dictionary of CLI arguments.
        native_defaults: Dictionary of native default parameters.
        load_schema_params_fn: Function to load schema parameters (optional).
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

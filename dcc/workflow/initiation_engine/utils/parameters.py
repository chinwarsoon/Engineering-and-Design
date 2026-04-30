"""
Parameter resolution and default configuration for the DCC processing pipeline.
"""

from pathlib import Path
from typing import Any, Dict, Optional

from .logging import status_print, debug_print
from .paths import default_schema_path

def build_native_defaults(base_path: Path, registry: Optional[Any] = None) -> Dict[str, Any]:
    """
    Build native default parameters for the DCC processing pipeline.
    Precedence: CLI args → Schema params → Native defaults
    
    Uses schema-driven parameter keys from registry when available.
    """
    status_print("Building native default parameters...", min_level=3)
    
    # Helper to get canonical key from registry or use fallback
    def key(param_name: str) -> str:
        if registry and hasattr(registry, 'get_canonical_key'):
            return registry.get_canonical_key(param_name)
        return param_name
    
    return {
        key("debug_dev_mode"): False,
        key("overwrite_existing_downloads"): True,
        key("start_col"): "P",
        key("end_col"): "AP",
        key("header_row_index"): 4,
        key("upload_sheet_name"): "Prolog Submittals ",
        key("schema_register_file"): str(default_schema_path(base_path)),
        # Windows network drive paths
        key("win_upload_file"): r"K:\J Submission\Submittal and RFI Tracker Lists.xlsx",
        key("win_download_path"): r"K:\J Submission\AI Tools and Report\data_output",
        # Windows fallback paths
        key("win_upload_file_fallback"): str(base_path / "data" / "Submittal and RFI Tracker Lists.xlsx"),
        key("win_download_path_fallback"): str(base_path / "output"),
        # Linux/Colab paths
        key("linux_upload_file"): str(base_path / "data" / "Submittal and RFI Tracker Lists.xlsx"),
        key("linux_download_path"): str(base_path / "output"),
        key("colab_upload_file"): "/content/sample_data/Submittal and RFI Tracker Lists.xlsx",
        key("colab_download_path"): "/content/output",
        # Active paths (resolved by resolve_platform_paths)
        key("upload_file_name"): str(base_path / "data" / "Submittal and RFI Tracker Lists.xlsx"),
        key("download_file_path"): str(base_path / "output"),
    }


def resolve_effective_parameters(
    schema_path: Path,
    cli_args: Dict[str, Any],
    native_defaults: Dict[str, Any],
    load_schema_params_fn: Any = None,
    registry: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Resolve effective parameters with precedence: CLI → Schema → Native.
    
    Args:
        schema_path: Path to the schema file.
        cli_args: Dictionary of CLI arguments.
        native_defaults: Dictionary of native default parameters.
        load_schema_params_fn: Function to load schema parameters (optional).
        registry: Parameter registry for schema-driven key lookups (optional).
    """
    status_print("Resolving effective parameters...", min_level=3)
    effective_parameters = native_defaults.copy()
    
    # Helper to get canonical key from registry or use fallback
    def key(param_name: str) -> str:
        if registry and hasattr(registry, 'get_canonical_key'):
            return registry.get_canonical_key(param_name)
        return param_name
    
    if load_schema_params_fn:
        try:
            schema_parameters = load_schema_params_fn(schema_path)
            effective_parameters.update(schema_parameters)
            status_print(f"Loaded schema parameters from {schema_path}", min_level=3)
        except Exception as exc:
            status_print(f"WARNING: Could not load schema parameters: {exc}", min_level=2)
    
    effective_parameters.update(cli_args)
    effective_parameters[key("schema_register_file")] = str(schema_path)
    debug_print(f"Effective parameters: {effective_parameters}")
    return effective_parameters

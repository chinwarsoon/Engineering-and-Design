"""
Native defaults building for CLI parameters.
"""
from pathlib import Path
from typing import Dict, Any, Optional

from core_engine.paths import default_schema_path
from utility_engine.console import status_print


def build_native_defaults(base_path: Path, registry: Optional[Any] = None) -> Dict[str, Any]:
    """
    Build native default parameters for DCC processing pipeline.
    Precedence: CLI args → Schema params → Native defaults

    Uses schema-driven parameter keys from registry when available.
    """
    status_print("Building native default parameters...", min_level=3)

    # Helper to get canonical key from registry or use fallback
    def key(param_name: str) -> str:
        if registry and hasattr(registry, 'get_canonical_key'):
            return registry.get_canonical_key(param_name)
        return param_name

    # Platform-specific defaults (for reference, not used in precedence)
    platform_defaults = {
        key("win_upload_file"): r"K:\J Submission\Submittal and RFI Tracker Lists.xlsx",
        key("win_download_path"): r"K:\J Submission\AI Tools and Report\data_output",
        key("linux_upload_file"): str(base_path / "data" / "Submittal and RFI Tracker Lists.xlsx"),
        key("linux_download_path"): str(base_path / "output"),
        key("colab_upload_file"): "/content/sample_data/Submittal and RFI Tracker Lists.xlsx",
        key("colab_download_path"): "/content/output",
    }

    # Standardized native defaults using schema-driven keys
    return {
        # Core processing parameters (consistent with CLI and schema)
        key("debug_dev_mode"): False,
        key("overwrite_existing_downloads"): True,
        key("start_col"): "P",
        key("end_col"): "AP",
        key("header_row_index"): 4,
        key("upload_sheet_name"): "Prolog Submittals ",
        key("schema_register_file"): str(default_schema_path(base_path)),
        key("upload_file_name"): str(base_path / "data" / "Submittal and RFI Tracker Lists.xlsx"),
        key("download_file_path"): str(base_path / "output"),

        # Infrastructure directory parameters (schema-driven, not hardcoded)
        key("data_dir"): "data",
        key("config_dir"): "config",
        key("schema_dir"): "schemas",

        # Platform-specific defaults (kept for reference, not used in precedence)
        key("platform_defaults"): platform_defaults,

        # Legacy fallback keys (for backward compatibility)
        key("win_upload_file_fallback"): str(base_path / "data" / "Submittal and RFI Tracker Lists.xlsx"),
        key("win_download_path_fallback"): str(base_path / "output"),
    }

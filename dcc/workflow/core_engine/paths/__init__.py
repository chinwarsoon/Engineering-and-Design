"""
Foundation path utilities for safe file system operations, OS detection, and path resolution.
"""
import os
import platform
from pathlib import Path
from typing import Any, Dict


# --- OS Detection ---

def detect_os() -> Dict[str, str]:
    """Detect operating system and return normalized info."""
    system_name = platform.system().strip() or "Unknown"
    normalized_name = {
        "Windows": "windows",
        "Linux": "linux",
        "Darwin": "macos",
    }.get(system_name, system_name.lower())
    return {
        "system": system_name,
        "normalized": normalized_name,
    }


def should_auto_create_folders(os_info: Dict[str, str]) -> bool:
    """Check if folders should be auto-created on this OS."""
    return os_info["normalized"] in {"windows", "linux", "macos"}


# --- Basic Path Resolvers ---

def safe_resolve(path: Path) -> Path:
    """Return an absolute path without filesystem I/O (no resolve, no expanduser)."""
    return Path(path).absolute()


def normalize_path(value: str | Path) -> Path:
    """Normalize a path to absolute form."""
    return safe_resolve(Path(value))


def safe_cwd() -> Path:
    """Get current working directory safely, falling back if inaccessible."""
    try:
        return Path.cwd().absolute()
    except (OSError, PermissionError):
        pass
    try:
        return Path(os.getcwd())
    except (OSError, PermissionError):
        pass
    return Path(__file__).parent.absolute()


def get_homedir() -> Path:
    """Return a validated home directory, with special Windows handling."""
    home_str = os.environ.get("HOME", "")

    if platform.system() == "Windows":
        home_exists = False
        if home_str:
            try:
                home_exists = Path(home_str).exists()
            except (OSError, PermissionError):
                home_exists = False

        if not home_exists:
            local_home = os.environ.get("LOCALAPPDATA", "")
            if local_home:
                os.environ["HOME"] = local_home
                home_str = local_home
            else:
                os.environ.pop("HOME", None)
                home_str = ""

    if home_str:
        return Path(home_str)
    return Path.home()


def default_base_path() -> Path:
    """Return default base path for project by finding 'workflow' parent."""
    for parent in Path(__file__).parents:
        if parent.name.lower() == "workflow":
            return parent.parent
    return Path(__file__).parent


def get_schema_path(base_path: Path) -> Path:
    """Return default project setup schema path."""
    from core_engine.schema_paths import get_schema_paths
    return get_schema_paths(base_path).project_setup_schema


def default_schema_path(base_path: Path | None = None) -> Path:
    """Return default data register schema path."""
    if base_path is None:
        for parent in Path(__file__).parents:
            if parent.name.lower() == "workflow":
                base_path = parent.parent
                break
        else:
            base_path = Path(__file__).parent
    from core_engine.schema_paths import get_schema_paths
    return get_schema_paths(base_path).dcc_register_config


# --- Pipeline Path Resolvers ---

def resolve_platform_paths(
    effective_parameters: Dict[str, Any],
    base_path: Path,
    status_print_fn: Any = print,
) -> Dict[str, Any]:
    """Resolve platform-specific paths from merged effective parameters."""
    status_print_fn("Resolving platform paths...", min_level=3)
    params = effective_parameters.copy()
    system_name = platform.system().lower()
    
    if system_name == "windows":
        win_upload = params.get("win_upload_file", "")
        win_download = params.get("win_download_path", "")
        if win_upload and Path(win_upload).exists():
            params["upload_file_name"] = win_upload
            if win_download:
                params["download_file_path"] = win_download
            status_print_fn(f"Using Windows path: {win_upload}", min_level=3)
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
                status_print_fn(f"Using Linux path: {lp}", min_level=3)
    
    active_upload = Path(params.get("upload_file_name", ""))
    active_download = Path(params.get("download_file_path", ""))
    if not active_upload.is_absolute():
        params["upload_file_name"] = str(base_path / active_upload)
    if not active_download.is_absolute():
        params["download_file_path"] = str(base_path / active_download)
    
    Path(params["download_file_path"]).mkdir(parents=True, exist_ok=True)
    status_print_fn(f"Current system detected: {system_name}", min_level=3)
    return params


def resolve_output_paths(
    base_path: Path,
    effective_parameters: Dict[str, Any],
    safe_resolve_fn: Any = None,
    status_print_fn: Any = print,
) -> Dict[str, Path]:
    """
    Resolve output file paths for processed data using schema-driven filenames.
    
    Breadcrumb: effective_parameters -> schema-driven filename resolution
    
    Uses global_parameters.json for:
    - output_file: Explicit output filename (if provided)
    - output_filename_pattern: Default filename stem (default: processed_dcc_universal)
    - summary_filename: Summary file name (default: processing_summary.txt)
    
    Args:
        base_path: Project base path
        effective_parameters: Resolved parameters (should include schema values)
        safe_resolve_fn: Optional path resolution function
        status_print_fn: Status printing function
        
    Returns:
        Dictionary with resolved output paths (output_dir, csv_path, excel_path, summary_path)
    """
    explicit_output = effective_parameters.get("output_file")
    if explicit_output:
        base_output = Path(explicit_output)
        if safe_resolve_fn:
            base_output = safe_resolve_fn(base_output)
    else:
        output_dir_str = effective_parameters.get("download_file_path", str(base_path / "output"))
        output_dir = Path(output_dir_str)
        if safe_resolve_fn:
            output_dir = safe_resolve_fn(output_dir)
        # Use schema-driven filename pattern (not hardcoded)
        filename_pattern = effective_parameters.get("output_filename_pattern", "processed_dcc_universal")
        base_output = output_dir / f"{filename_pattern}.csv"
    
    output_dir = base_output.parent
    stem = base_output.stem or effective_parameters.get("output_filename_pattern", "processed_dcc_universal")

    # Use schema-driven summary filename (not hardcoded)
    summary_filename = effective_parameters.get("summary_filename", "processing_summary.txt")

    status_print_fn(f"Output directory: {output_dir}", min_level=3)
    status_print_fn(f"CSV path: {output_dir / f'{stem}.csv'}", min_level=3)
    status_print_fn(f"Excel path: {output_dir / f'{stem}.xlsx'}", min_level=3)
    status_print_fn(f"Summary path: {output_dir / summary_filename}", min_level=3)
    
    return {
        "output_dir": output_dir,
        "csv_path": output_dir / f"{stem}.csv",
        "excel_path": output_dir / f"{stem}.xlsx",
        "summary_path": output_dir / summary_filename,
    }


def validate_export_paths(export_paths: Dict[str, Path], overwrite_existing: bool) -> None:
    """Validate output paths and check for existing files."""
    export_paths["output_dir"].mkdir(parents=True, exist_ok=True)
    if not overwrite_existing:
        for file_key in ("csv_path", "excel_path", "summary_path"):
            target_path = export_paths[file_key]
            if target_path.exists():
                raise FileExistsError(f"Output file exists: {target_path}. Use --overwrite True.")

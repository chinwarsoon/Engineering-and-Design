"""
Path utilities for project setup validation.
Extracted from project_setup_validation.py path functions.
"""

import os
import platform
from pathlib import Path
from typing import Any, Dict, List, Callable  # Add Any here

from ..utils.logging import status_print



# check and get "HOME" directory, with special handling for Windows network drive issues
def get_homedir() -> Path:
    """
    Return a validated home directory.

    On Windows, it fixes broken/network HOME paths by falling back to LOCALAPPDATA.
    Uses environment variables and Path.home() as fallback.

    Returns:
        Path object pointing to the validated home directory.

    Breadcrumb Comments:
        - Reads HOME environment variable first.
        - On Windows, validates path exists (not a dead network drive).
        - Falls back to LOCALAPPDATA on Windows if HOME is broken.
        - Final fallback is Path.home() if no valid path found.
        - Used for resolving user-specific paths in the project.
    """
    # Start with the standard HOME environment variable
    home_str = os.environ.get("HOME", "")

    if platform.system() == "Windows":
        home_exists = False
        
        if home_str:
            try:
                # Check if the path is actually reachable (not a dead network drive)
                home_exists = Path(home_str).exists()
            except (OSError, PermissionError):
                home_exists = False

        # If HOME is missing or broken, switch to a guaranteed local path
        if not home_exists:
            local_home = os.environ.get("LOCALAPPDATA", "")
            if local_home:
                # Update the environment so other libraries can find it too
                os.environ["HOME"] = local_home
                home_str = local_home
            else:
                # If everything fails, remove the broken HOME entry
                os.environ.pop("HOME", None)
                home_str = ""

    # If we still have a string, return it as a Path object
    if home_str:
        return Path(home_str)
    
    # Absolute fallback: use Python's built-in home locator
    return Path.home()


def normalize_path(value: str | Path) -> Path:
    """
    Normalize a path to absolute form.

    Args:
        value: Path as string or Path object to normalize.

    Returns:
        Absolute Path object.

    Breadcrumb Comments:
        - value: Received from __init__ for base_path and schema_path.
                 Modified here by Path(value).absolute() to ensure absolute path.
                 Consumed as base_path for all path resolution operations.
    """
    return Path(value).absolute()


def default_base_path() -> Path:
    """
    Return default base path for project.

    Uses script directory directly without resolve() to avoid
    injecting restricted network paths on Windows UNC shares.
    Traverses parent directories to find the "workflow" folder,
    then returns its parent as the project root.

    Returns:
        Path object pointing to the project root directory.

    Breadcrumb Comments:
        - Traverses Path(__file__).parents to find "workflow" directory.
        - Returns parent of workflow folder as project base.
        - If workflow not found, returns script parent directory.
        - Consumed by __init__ when base_path is not provided.
    """
    # go through each parent to check if "workflow" is in the path, if so, return the parent of "workflow"
    for parent in Path(__file__).parents:
        if parent.name.lower() == "workflow":
            return parent.parent
    else:        # if "workflow" is not found in any parent, return the script directory
        script_parent = Path(__file__).parent
        return script_parent


def get_schema_path(base_path: Path) -> Path:
    """
    Return default schema path based on base path.

    Args:
        base_path: Project root directory.

    Returns:
        Path to project_setup.json schema file.

    Breadcrumb Comments:
        - base_path: Initialized in __init__ via normalize_path().
                     Used here to construct schema path.
                     Returns base_path / "config" / "schemas" / "project_setup.json".
    """
    return base_path / "config" / "schemas" / "project_setup.json"


def resolve_platform_paths(
    effective_parameters: dict[str, Any],
    base_path: Path,
    status_print_fn: Any = print,
) -> dict[str, Any]:
    """
    Resolve platform-specific paths from merged effective parameters.

    Resolves upload and download file paths based on the operating system.
    Precedence: CLI → Schema → Native defaults

    Args:
        effective_parameters: Merged parameters dictionary containing
            win_upload_file, win_download_path, linux_upload_file,
            linux_download_path, upload_file_name, download_file_path.
        base_path: Base path for resolving relative paths.
        status_print_fn: Function to print status messages (default: print).

    Returns:
        Updated parameters dictionary with resolved paths.

    Breadcrumb Comments:
        - effective_parameters: Initialized in build_effective_parameters()
                                 from CLI args and schema defaults.
                                 Modified here to set upload_file_name
                                 and download_file_path based on OS.
        - base_path: Initialized in __init__ via normalize_path().
                     Used here to resolve relative Linux paths.
        - Parameters consumed: win_upload_file, win_download_path,
          linux_upload_file, linux_download_path.
        - Parameters modified: upload_file_name, download_file_path.
    """
    from typing import Dict, Any
    
    status_print_fn("Resolving platform paths...")
    params = effective_parameters.copy()
    system_name = platform.system().lower()
    
    if system_name == "windows":
        win_upload = params.get("win_upload_file", "")
        win_download = params.get("win_download_path", "")
        if win_upload and Path(win_upload).exists():
            params["upload_file_name"] = win_upload
            if win_download:
                params["download_file_path"] = win_download
            status_print_fn(f"Using Windows path: {win_upload}")
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
                status_print_fn(f"Using Linux path: {lp}")
    
    # Resolve any remaining relative paths
    active_upload = Path(params.get("upload_file_name", ""))
    active_download = Path(params.get("download_file_path", ""))
    if not active_upload.is_absolute():
        params["upload_file_name"] = str(base_path / active_upload)
    if not active_download.is_absolute():
        params["download_file_path"] = str(base_path / active_download)
    
    Path(params["download_file_path"]).mkdir(parents=True, exist_ok=True)
    status_print_fn(f"Current system detected: {system_name}")
    return params


def resolve_output_paths(
    base_path: Path,
    effective_parameters: dict[str, Any],
    safe_resolve_fn: Any = None,
) -> dict[str, Path]:
    """
    Resolve output file paths for processed data.

    Determines output directory and file paths based on effective_parameters.
    Creates output directory if it doesn't exist.

    Args:
        base_path: Base path for the project.
        effective_parameters: Dictionary containing output_file or
            download_file_path for determining output location.
        safe_resolve_fn: Optional path resolution function (defaults to Path resolution).

    Returns:
        Dictionary with keys: output_dir, csv_path, excel_path, summary_path.

    Breadcrumb Comments:
        - effective_parameters: Initialized in build_effective_parameters().
                                 Consumes output_file or download_file_path
                                 to determine output_dir.
        - base_path: Used as fallback if no explicit output path provided.
        - Returns dictionary consumed by run_engine_pipeline() and
          validate_export_paths() for writing output files.
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
        base_output = output_dir / "processed_dcc_universal.csv"
    
    output_dir = base_output.parent
    stem = base_output.stem or "processed_dcc_universal"

    status_print(f"Output directory: {output_dir}")
    status_print(f"CSV path: {output_dir / f'{stem}.csv'}")
    status_print(f"Excel path: {output_dir / f'{stem}.xlsx'}")
    status_print(f"Summary path: {output_dir / 'processing_summary.txt'}")
    
    return {
        "output_dir": output_dir,
        "csv_path": output_dir / f"{stem}.csv",
        "excel_path": output_dir / f"{stem}.xlsx",
        "summary_path": output_dir / "processing_summary.txt",
    }


def validate_export_paths(export_paths: dict[str, Path], overwrite_existing: bool) -> None:
    """
    Validate output paths and check for existing files.

    Creates output directory if needed. Raises error if output files
    already exist and overwrite is not enabled.

    Args:
        export_paths: Dictionary with keys: output_dir, csv_path, excel_path, summary_path.
        overwrite_existing: If True, allow overwriting existing files.

    Raises:
        FileExistsError: If output files exist and overwrite_existing is False.

    Breadcrumb Comments:
        - export_paths: Initialized in resolve_output_paths().
                        Consumes output_dir for directory creation.
                        Checks csv_path, excel_path, summary_path for existence.
        - overwrite_existing: Passed from effective_parameters via CLI args.
                              If False and files exist, raises FileExistsError.
    """
    export_paths["output_dir"].mkdir(parents=True, exist_ok=True)
    if not overwrite_existing:
        for file_key in ("csv_path", "excel_path", "summary_path"):
            target_path = export_paths[file_key]
            if target_path.exists():
                raise FileExistsError(f"Output file exists: {target_path}. Use --overwrite True.")

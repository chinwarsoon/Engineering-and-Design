"""
Core path utilities for OS detection and basic path operations.
"""
import os
import platform
from pathlib import Path
from typing import Dict


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


def default_base_path(pipeline_dir: str = "workflow") -> Path:
    """
    Return default base path for project by finding pipeline_dir parent.

    Raises:
        FileNotFoundError: If pipeline_dir is not found in parent hierarchy
    """
    for parent in Path(__file__).parents:
        if parent.name.lower() == pipeline_dir:
            return parent.parent

    raise FileNotFoundError(
        f"Pipeline directory '{pipeline_dir}' not found in parent hierarchy. "
        f"Ensure pipeline is executed from within '{pipeline_dir}' folder structure, "
        f"or specify project root explicitly using --base-path argument."
    )

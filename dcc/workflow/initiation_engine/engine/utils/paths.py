"""
Path utilities for project setup validation.
Extracted from project_setup_validation.py path functions.
"""

import os
import platform
from pathlib import Path

from pathlib import Path


# check and get "HOME" directory, with special handling for Windows network drive issues
def get_homedir() -> Path:
    """
    Returns a validated home directory. 
    On Windows, it fixes broken/network HOME paths by falling back to LOCALAPPDATA.
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
    """Normalize a path to absolute form."""
    return Path(value).absolute()


def default_base_path() -> Path:
    """
    Return default base path for project.
    Uses script directory directly. Does NOT use resolve(),
    which injects restricted network paths on Windows UNC shares.
    """
    # go through each parent to check if "workflow" is in the path, if so, return the parent of "workflow"
    for parent in Path(__file__).parents:
        if parent.name.lower() == "workflow":
            return parent.parent
    else:        # if "workflow" is not found in any parent, return the script directory
        script_parent = Path(__file__).parent
        return script_parent


def get_schema_path(base_path: Path) -> Path:
    """Return default schema path based on base path."""
    return base_path / "config" / "schemas" / "project_setup.json"

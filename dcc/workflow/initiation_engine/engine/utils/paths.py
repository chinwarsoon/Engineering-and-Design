"""
Path utilities for project setup validation.
Extracted from project_setup_validation.py path functions.
"""

from pathlib import Path


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

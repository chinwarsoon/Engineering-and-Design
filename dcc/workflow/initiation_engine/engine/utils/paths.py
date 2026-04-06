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
    script_parent = Path(__file__).parent
    if script_parent.name.lower() == "workflow":
        return script_parent.parent
    return script_parent


def get_schema_path(base_path: Path) -> Path:
    """Return default schema path based on base path."""
    return base_path / "config" / "schemas" / "project_setup.json"

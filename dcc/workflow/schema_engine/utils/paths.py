"""
Path utilities for safe file system operations.
Extracted from schema_validation.py path functions.
"""

import os
from pathlib import Path


def safe_resolve(path: Path) -> Path:
    """Return an absolute path without filesystem I/O (no resolve, no expanduser)."""
    return Path(path).absolute()


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
    # Final fallback: script directory (guaranteed to exist since script is running)
    return Path(__file__).parent.absolute()


def get_default_schema_path() -> Path:
    """Return the default schema path relative to this module."""
    return safe_resolve(Path(__file__).parent.parent.parent / "config" / "schemas" / "dcc_register_enhanced.json")


def default_schema_path(base_path: Path | None = None) -> Path:
    """
    Return default schema register path.
    
    Args:
        base_path: Optional base path. If not provided, uses workflow root.
        
    Returns:
        Path to dcc_register_enhanced.json schema file.
    """
    if base_path is None:
        # Infer from this file's location
        base_path = safe_resolve(Path(__file__).parent.parent.parent.parent)
    return base_path / "config" / "schemas" / "dcc_register_enhanced.json"

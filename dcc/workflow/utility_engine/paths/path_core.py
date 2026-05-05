"""
Core path utilities for system context and normalization.
"""
import os
import platform
from pathlib import Path
from typing import Optional, Union


def get_system_context() -> str:
    """
    Get current system context for path resolution.

    Returns:
        System context string (windows, linux, macos)
    """
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "darwin":
        return "macos"
    elif system == "linux":
        return "linux"
    else:
        return "unknown"


def normalize_path_separators(path: Union[str, Path], system_context: str) -> str:
    """
    Normalize path separators based on system context.

    Args:
        path: Path to normalize
        system_context: Current system context

    Returns:
        Normalized path string
    """
    path_str = str(path)

    if system_context == "windows":
        # Convert forward slashes to backslashes on Windows
        path_str = path_str.replace("/", "\\")
        # Handle UNC paths
        if path_str.startswith("\\\\"):
            return path_str
        # Handle drive letters
        if len(path_str) > 1 and path_str[1] == ":":
            return path_str
    else:
        # Convert backslashes to forward slashes on Unix-like systems
        path_str = path_str.replace("\\", "/")

    return path_str


def resolve_relative_to_base(path: Union[str, Path], base_path: Optional[Path] = None) -> Path:
    """
    Resolve path relative to base path.

    Args:
        path: Path to resolve
        base_path: Base path for relative resolution

    Returns:
        Resolved absolute path
    """
    if base_path is None:
        # Default to current working directory
        base_path = Path.cwd()

    path_obj = Path(path)

    if path_obj.is_absolute():
        return path_obj
    else:
        return (base_path / path_obj).resolve()

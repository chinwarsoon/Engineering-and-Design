"""
Data models for path resolution.
"""
from pathlib import Path
from typing import Union
from dataclasses import dataclass


@dataclass
class PathResolutionResult:
    """Result of path resolution with system context."""
    resolved_path: Path
    original_path: Union[str, Path]
    system_context: str
    resolution_method: str
    is_absolute: bool
    exists: bool
    is_file: bool
    is_directory: bool
    errors: list[str]

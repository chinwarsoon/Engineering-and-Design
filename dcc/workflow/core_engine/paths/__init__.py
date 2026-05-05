"""
Foundation path utilities for safe file system operations, OS detection, and path resolution.

This module follows the barrel pattern - it re-exports functionality from submodules.
"""
from core_engine.paths.path_core import (
    detect_os,
    should_auto_create_folders,
    safe_resolve,
    normalize_path,
    safe_cwd,
    get_homedir,
    default_base_path,
)
from core_engine.paths.path_resolvers import (
    resolve_pipeline_base_path,
    get_schema_path,
    default_schema_path,
    resolve_platform_paths,
    resolve_output_paths,
    validate_export_paths,
)

__all__ = [
    # From path_core
    "detect_os",
    "should_auto_create_folders",
    "safe_resolve",
    "normalize_path",
    "safe_cwd",
    "get_homedir",
    "default_base_path",
    # From path_resolvers
    "resolve_pipeline_base_path",
    "get_schema_path",
    "default_schema_path",
    "resolve_platform_paths",
    "resolve_output_paths",
    "validate_export_paths",
]

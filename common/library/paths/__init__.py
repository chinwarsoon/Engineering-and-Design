"""Architecture-aligned paths package for shared pipeline libraries.

Revision: 1.0
Date: 2026-07-11
Author: opencode
Summary: T1.98.2 — export the universal PathResolver (resolve_paths, ResolvedPaths).
"""

from common.library.core.paths.path_utils import (
    detect_os,
    safe_posix,
    resolve_anchored,
    safe_cwd,
    get_homedir,
    should_auto_create_folders,
)
from common.library.paths.resolver import resolve_paths, ResolvedPaths
from common.library.paths.root_discovery import (
    discover_project_root,
    resolve_pipeline_base_path,
    default_base_path,
)

__all__ = [
    "detect_os",
    "safe_posix",
    "resolve_anchored",
    "safe_cwd",
    "get_homedir",
    "should_auto_create_folders",
    "resolve_paths",
    "ResolvedPaths",
    "discover_project_root",
    "resolve_pipeline_base_path",
    "default_base_path",
]

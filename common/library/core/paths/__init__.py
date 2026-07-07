"""
common.library.core.paths — OS detection and cross-platform path utilities.

Exports
-------
detect_os           L12  Detect OS and return normalized name dict
safe_posix          L12  Convert any path to forward-slash string (cross-platform safe)
resolve_anchored    L12  Resolve a relative path against a base, return absolute Path
safe_cwd            L12  Get CWD safely with fallback
get_homedir         L12  Resolve home directory with Windows LOCALAPPDATA fallback

Sources
-------
dcc: core_engine/paths/path_core.py        (detect_os, safe_resolve, safe_cwd, get_homedir)
     utility_engine/paths/path_core.py     (get_system_context, normalize_path_separators)
     core_engine/system/system_environment.py  (detect_os — duplicate, eliminated here)
eks: engine/core/context.py                (EKSPaths.to_dict — T1.74 gap fixed by safe_posix)
"""

from common.library.core.paths.path_utils import (
    detect_os,
    safe_posix,
    resolve_anchored,
    safe_cwd,
    get_homedir,
)

__all__ = ["detect_os", "safe_posix", "resolve_anchored", "safe_cwd", "get_homedir"]

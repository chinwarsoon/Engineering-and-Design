"""Architecture-aligned paths package for shared pipeline libraries.

Revision: 1.0
Date: 2026-07-11
Author: opencode
Summary: T1.98b — export the universal PathResolver (resolve_paths, ResolvedPaths).
"""

from common.library.core.paths.path_utils import detect_os, safe_posix, resolve_anchored, safe_cwd, get_homedir
from common.library.paths.resolver import resolve_paths, ResolvedPaths

__all__ = ["detect_os", "safe_posix", "resolve_anchored", "safe_cwd", "get_homedir", "resolve_paths", "ResolvedPaths"]

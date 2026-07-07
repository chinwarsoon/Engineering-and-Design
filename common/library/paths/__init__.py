"""Architecture-aligned paths package for shared pipeline libraries."""

from common.library.core.paths.path_utils import detect_os, safe_posix, resolve_anchored, safe_cwd, get_homedir

__all__ = ["detect_os", "safe_posix", "resolve_anchored", "safe_cwd", "get_homedir"]

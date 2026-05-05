"""
Universal Path Resolution Utilities - Function Model Design Approach

Provides reusable path resolution functions that consider current system context
and can be used across all pipeline components.

This module follows the barrel pattern - it re-exports functionality from submodules.
"""
# Models
from utility_engine.paths.path_models import PathResolutionResult

# Core functions
from utility_engine.paths.path_core import (
    get_system_context,
    normalize_path_separators,
    resolve_relative_to_base,
)

# Resolver functions
from utility_engine.paths.path_resolvers import (
    resolve_with_system_context,
    safe_resolve,
    safe_resolve_batch,
    validate_path_resolutions,
    get_path_info,
    safe_resolve_legacy,
)

__all__ = [
    # Models
    "PathResolutionResult",
    # Core
    "get_system_context",
    "normalize_path_separators",
    "resolve_relative_to_base",
    # Resolvers
    "resolve_with_system_context",
    "safe_resolve",
    "safe_resolve_batch",
    "validate_path_resolutions",
    "get_path_info",
    "safe_resolve_legacy",
]

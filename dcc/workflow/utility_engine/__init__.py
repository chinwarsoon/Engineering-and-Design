"""
Utility Engine - Shared utilities for the DCC workflow pipeline.

Provides validation, path resolution, error handling, CLI parsing, and
bootstrap management for pipeline initialization.

Breadcrumb: BootstrapManager -> validation -> paths -> console -> errors
"""

# Bootstrap submodule (Phase 1 implementation)
from utility_engine.bootstrap import BootstrapManager, BootstrapError

# Other submodules are imported from their respective packages
from utility_engine.console import status_print, milestone_print
from utility_engine.errors import system_error_print
from utility_engine.paths import safe_resolve
from utility_engine.validation import ValidationManager, ValidationStatus

__all__ = [
    # Bootstrap
    "BootstrapManager",
    "BootstrapError",
    # Console
    "status_print",
    "milestone_print",
    # Errors
    "system_error_print",
    # Paths
    "safe_resolve",
    # Validation
    "ValidationManager",
    "ValidationStatus",
]

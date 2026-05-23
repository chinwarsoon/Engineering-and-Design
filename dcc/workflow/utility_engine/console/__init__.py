"""
Console UI utilities for the DCC pipeline.
Provides standardized formatting for terminal output.

This module follows the barrel pattern - it re-exports functionality from submodules.
"""

from utility_engine.console.console_output import (
    debug_print,
    milestone_print,
    print_framework_banner,
    status_print,
)
from utility_engine.console.progress import (
    create_progress_bar,
    create_progress_callback,
    create_progress_spinner,
)

__all__ = [
    "status_print",
    "milestone_print",
    "debug_print",
    "print_framework_banner",
    "create_progress_bar",
    "create_progress_spinner",
    "create_progress_callback",
]

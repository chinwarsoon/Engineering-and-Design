"""
System Error Handling — utility_engine/errors/__init__.py

Provides system_error_print(): always-visible error output for pipeline
execution failures. Bypasses DEBUG_LEVEL entirely — system errors are
shown at all verbose levels including --verbose quiet.

This module follows the barrel pattern - it re-exports functionality from submodules.
"""
from utility_engine.errors.error_loader import (
    get_system_error,
    get_all_system_codes,
)
from utility_engine.errors.error_printer import (
    system_error_print,
)

__all__ = [
    "system_error_print",
    "get_system_error",
    "get_all_system_codes",
]

"""
initiation_engine/error_handling — System Error Handling Sub-Module

Provides always-visible system error output for pipeline execution failures.
System errors bypass DEBUG_LEVEL and are shown at all verbose levels.
"""

from .system_errors import system_error_print, get_system_error, get_all_system_codes, get_system_error_message

__all__ = [
    "system_error_print",
    "get_system_error",
    "get_all_system_codes",
    "get_system_error_message",
]

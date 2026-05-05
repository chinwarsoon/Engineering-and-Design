"""
Foundation system utilities for environment testing, OS detection, and dependency validation.

This module follows the barrel pattern - it re-exports functionality from submodules.
"""
from core_engine.system.system_environment import (
    detect_os,
    should_auto_create_folders,
    test_environment,
)

__all__ = [
    "detect_os",
    "should_auto_create_folders",
    "test_environment",
]

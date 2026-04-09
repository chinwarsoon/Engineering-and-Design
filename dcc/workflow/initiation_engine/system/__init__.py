"""
System detection utilities for the initiation engine.
"""

from .os_detect import (
    detect_os,
    should_auto_create_folders,
)

__all__ = [
    'detect_os',
    'should_auto_create_folders',
]

"""
System detection utilities for the initiation engine.
"""

from dcc.workflow.initiation_engine.engine.system.os_detect import (
    detect_os,
    should_auto_create_folders,
)

__all__ = [
    'detect_os',
    'should_auto_create_folders',
]

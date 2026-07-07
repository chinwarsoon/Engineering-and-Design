"""
L04 — System snapshot utility.

Returns a dict capturing OS, Python, CPU, memory, and CWD at call time.
Union of DCC _get_system_snapshot() and EKS EKSLogger._get_system_snapshot().

Sources
-------
dcc: core_engine/logging/log_state.py  (_get_system_snapshot)
eks: engine/logging/logger.py          (EKSLogger._get_system_snapshot)
"""

import os
import platform
import sys
from datetime import datetime
from typing import Any, Dict

import psutil


def get_system_snapshot() -> Dict[str, Any]:
    """
    Capture a system snapshot at call time.

    Returns the union of DCC and EKS snapshot fields:
        platform, platform_release, python_version, processor,
        hostname, cpu_count, memory_total_mb, cwd, timestamp
    """
    try:
        memory_total_mb = round(psutil.virtual_memory().total / (1024 * 1024), 1)
    except Exception:
        memory_total_mb = None

    return {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "python_version": platform.python_version(),
        "processor": platform.processor(),
        "hostname": platform.node(),
        "cpu_count": os.cpu_count(),
        "memory_total_mb": memory_total_mb,
        "cwd": os.getcwd(),
        "timestamp": datetime.now().isoformat(),
    }

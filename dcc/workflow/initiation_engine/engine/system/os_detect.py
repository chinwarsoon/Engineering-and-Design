"""
System detection utilities.
Extracted from project_setup_validation.py OS detection.
"""

import platform
from typing import Dict


def detect_os() -> Dict[str, str]:
    """
    Detect operating system and return normalized info.
    
    Returns:
        Dictionary with 'system' (raw) and 'normalized' (lowercase) OS names.
    """
    system_name = platform.system().strip() or "Unknown"
    normalized_name = {
        "Windows": "windows",
        "Linux": "linux",
        "Darwin": "macos",
    }.get(system_name, system_name.lower())
    return {
        "system": system_name,
        "normalized": normalized_name,
    }


def should_auto_create_folders(os_info: Dict[str, str]) -> bool:
    """Check if folders should be auto-created on this OS."""
    return os_info["normalized"] in {"windows", "linux", "macos"}

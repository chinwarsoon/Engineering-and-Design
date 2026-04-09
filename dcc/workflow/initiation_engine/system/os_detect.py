"""
System detection utilities.
Extracted from project_setup_validation.py OS detection.
"""

import platform
from typing import Dict


def detect_os() -> Dict[str, str]:
    """
    Detect operating system and return normalized info.

    Uses platform.system() to detect the OS and returns both raw and
    normalized names for consistent handling across the codebase.

    Returns:
        Dictionary with:
            - 'system': Raw OS name (e.g., 'Windows', 'Linux', 'Darwin')
            - 'normalized': Lowercase normalized name (e.g., 'windows', 'linux', 'macos')

    Breadcrumb Comments:
        - Called from ProjectSetupValidator.__init__() to set os_info attribute.
        - Consumed by validate_folders() via should_auto_create_folders() check.
        - Used to determine auto-creation capability based on OS.
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
    """
    Check if folders should be auto-created on this OS.

    Determines if the current operating system supports auto-creating
    folders during validation. Currently enabled for Windows, Linux, and macOS.

    Args:
        os_info: Dictionary containing 'normalized' OS name from detect_os().

    Returns:
        True if folders can be auto-created on this OS, False otherwise.

    Breadcrumb Comments:
        - os_info: Initialized in ProjectSetupValidator.__init__ via detect_os().
                   Passed from validate_folders() to check auto-creation eligibility.
        - Checks 'normalized' key for 'windows', 'linux', or 'macos'.
        - If True, validate_folders() calls ensure_folder() to create missing dirs.
    """
    return os_info["normalized"] in {"windows", "linux", "macos"}

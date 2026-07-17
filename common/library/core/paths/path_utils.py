"""
L12 — OS detection and cross-platform path normalization utilities.

Eliminates the verbatim duplication of detect_os() across:
  dcc/workflow/core_engine/paths/path_core.py
  dcc/workflow/core_engine/system/system_environment.py

Also provides safe_posix() which fixes the EKS T1.74 gap where
EKSPaths.to_dict() used str(Path) producing backslashes on Windows.

Added should_auto_create_folders() to remove the verbatim duplication of
that gate across DCC (path_core.py / system_environment.py) and to satisfy
L17 step 7 (OS-gated folder auto-create).

Revision: 1.1
Date: 2026-07-15
Author: opencode
Summary: T1.99.22/T1.99.25 (I098/L17) — added should_auto_create_folders(); de-duplicates
DCC's triple detect_os() and gates folder auto-create by OS (L17 step 7).

Sources
-------
dcc: core_engine/paths/path_core.py        (detect_os, safe_resolve, safe_cwd, get_homedir,
                                            should_auto_create_folders)
     utility_engine/paths/path_core.py     (get_system_context, normalize_path_separators,
                                            resolve_relative_to_base)
     core_engine/system/system_environment.py (detect_os, should_auto_create_folders)
eks: engine/core/context.py                (EKSPaths.to_dict — T1.74 gap)
"""

import os
import platform
from pathlib import Path
from typing import Dict, Union


def detect_os() -> Dict[str, str]:
    """
    Detect the current operating system.

    Returns
    -------
    dict with keys:
        system      : raw platform.system() value  e.g. "Windows"
        normalized  : lowercase canonical name      e.g. "windows" | "linux" | "macos"
    """
    system_name = platform.system().strip() or "Unknown"
    normalized = {
        "Windows": "windows",
        "Linux": "linux",
        "Darwin": "macos",
    }.get(system_name, system_name.lower())
    return {"system": system_name, "normalized": normalized}


def safe_posix(path: Union[str, Path]) -> str:
    """
    Convert a path to a forward-slash string regardless of OS.

    Use this instead of str(Path) when the result will be stored in JSON,
    sent over HTTP, or compared across platforms.

    Fixes EKS T1.74: EKSPaths.to_dict() used str() which produces
    backslashes on Windows.

    Examples
    --------
    safe_posix(Path("eks\\output"))   -> "eks/output"
    safe_posix("/abs/path/file.txt")  -> "/abs/path/file.txt"
    """
    return Path(path).as_posix()


def resolve_anchored(path: Union[str, Path], base: Union[str, Path, None] = None) -> Path:
    """
    Resolve a path relative to base (or CWD if base is None).

    Absolute paths are returned unchanged.
    Relative paths are joined to base and resolved to an absolute Path.

    Parameters
    ----------
    path : str | Path — path to resolve
    base : str | Path | None — anchor for relative resolution

    Returns
    -------
    Absolute Path object.
    """
    path_obj = Path(path)
    if path_obj.is_absolute():
        return path_obj
    anchor = Path(base) if base is not None else safe_cwd()
    return (anchor / path_obj).resolve()


def safe_cwd() -> Path:
    """
    Return the current working directory safely, with fallback.

    Falls back to os.getcwd(), then to the directory of this file,
    if the primary Path.cwd() raises an OSError (e.g. deleted CWD).
    """
    try:
        return Path.cwd().absolute()
    except (OSError, PermissionError):
        pass
    try:
        return Path(os.getcwd())
    except (OSError, PermissionError):
        pass
    return Path(__file__).parent.absolute()


def get_homedir() -> Path:
    """
    Resolve the user home directory with Windows LOCALAPPDATA fallback.

    On Windows, if $HOME is unset or points to a non-existent path,
    falls back to $LOCALAPPDATA so that Path.home() does not raise.

    Source: dcc/workflow/core_engine/paths/path_core.py (get_homedir)
    """
    home_str = os.environ.get("HOME", "")

    if platform.system() == "Windows":
        home_exists = False
        if home_str:
            try:
                home_exists = Path(home_str).exists()
            except (OSError, PermissionError):
                home_exists = False

        if not home_exists:
            local_home = os.environ.get("LOCALAPPDATA", "")
            if local_home:
                os.environ["HOME"] = local_home
                home_str = local_home
            else:
                os.environ.pop("HOME", None)
                home_str = ""

    return Path(home_str) if home_str else Path.home()


def should_auto_create_folders(os_info: Dict[str, str]) -> bool:
    """
    Check if folders should be auto-created on the detected OS (L17 step 7).

    De-duplicates DCC's verbatim ``should_auto_create_folders``
    (dcc/workflow/core_engine/paths/path_core.py:24 and
    dcc/workflow/core_engine/system/system_environment.py:30).

    Parameters
    ----------
    os_info : dict — output of :func:`detect_os` (keys ``system`` / ``normalized``)

    Returns
    -------
    True when auto-create is safe (windows / linux / macos), else False.
    """
    return os_info.get("normalized") in {"windows", "linux", "macos"}

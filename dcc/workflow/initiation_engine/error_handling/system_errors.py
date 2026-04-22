"""
System Error Handling — initiation_engine/error_handling/system_errors.py

Provides system_error_print(): always-visible error output for pipeline
execution failures. Bypasses DEBUG_LEVEL entirely — system errors are
shown at all verbose levels including --verbose quiet.

Breadcrumb: system_error_print() -> _load_messages() -> system_en.json
"""

from __future__ import annotations

import json
import sys
import builtins
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Message loading
# ---------------------------------------------------------------------------

_MESSAGES: dict = {}
_CODES: dict = {}
_LOADED = False

_CONFIG_DIR = Path(__file__).parent / "config"
_CODES_FILE = _CONFIG_DIR / "system_error_codes.json"
_MESSAGES_FILE = _CONFIG_DIR / "messages" / "system_en.json"


def _load() -> None:
    """Load system error codes and messages from JSON. Called once at import."""
    global _MESSAGES, _CODES, _LOADED
    if _LOADED:
        return
    try:
        _CODES = json.loads(_CODES_FILE.read_text(encoding="utf-8")).get("errors", {})
    except Exception:
        _CODES = {}
    try:
        _MESSAGES = json.loads(_MESSAGES_FILE.read_text(encoding="utf-8"))
    except Exception:
        _MESSAGES = {}
    _LOADED = True


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def system_error_print(
    code: str,
    detail: Optional[str] = None,
    fatal: bool = True,
) -> None:
    """
    Print a system error to stderr. Always visible regardless of DEBUG_LEVEL.

    Fatal errors (stops_pipeline=True) print a full bordered block.
    Warnings (stops_pipeline=False) print a compact single line.

    Args:
        code:   System error code, e.g. 'S-F-S-0201'
        detail: Optional detail string (file path, exception message, etc.)
        fatal:  True = full error block; False = compact warning line.
                Defaults to True. Overridden by stops_pipeline in JSON if loaded.

    Breadcrumb: system_error_print -> _load() -> system_en.json / system_error_codes.json
    """
    _load()

    # Determine fatal from JSON definition if available
    code_def = _CODES.get(code, {})
    if code_def:
        fatal = code_def.get("stops_pipeline", fatal)

    msg_def = _MESSAGES.get(code, {})
    title = msg_def.get("title", code_def.get("name", code))
    hint = msg_def.get("hint", "Run with --verbose trace for more detail.")

    # Substitute {detail} placeholder in hint if present
    if detail and "{detail}" in hint:
        hint = hint.replace("{detail}", detail)

    sep = "-" * 76

    if fatal:
        lines = [
            sep,
            f"  X  PIPELINE ERROR  [{code}]",
            f"     {title}",
        ]
        if detail:
            lines.append(f"     Detail: {detail}")
        hint_lines = hint.splitlines()
        lines.append(f"     Hint:   {hint_lines[0]}")
        for hl in hint_lines[1:]:
            lines.append(f"             {hl}")
        lines.append(sep)
        builtins.print("\n".join(lines), file=sys.stderr, flush=True)
    else:
        detail_str = f" - {detail}" if detail else ""
        builtins.print(
            f"  !  [{code}] {title}{detail_str}",
            file=sys.stderr,
            flush=True,
        )
        hint_lines = hint.splitlines()
        builtins.print(
            f"     Hint: {hint_lines[0]}",
            file=sys.stderr,
            flush=True,
        )


def get_system_error(code: str) -> dict:
    """
    Return the definition dict for a system error code.

    Args:
        code: System error code, e.g. 'S-F-S-0201'

    Returns:
        Dict with name, severity, category, stops_pipeline keys.
        Empty dict if code not found.
    """
    _load()
    return _CODES.get(code, {})


def get_all_system_codes() -> list[str]:
    """Return all registered system error codes."""
    _load()
    return list(_CODES.keys())

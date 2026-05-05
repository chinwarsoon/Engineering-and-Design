"""
Error message and code loading utilities.
"""
import json
from pathlib import Path
from typing import Dict

# ---------------------------------------------------------------------------
# Message loading
# ---------------------------------------------------------------------------

_MESSAGES: Dict = {}
_CODES: Dict = {}
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


def get_system_error(code: str) -> Dict:
    """Return the definition dict for a system error code."""
    _load()
    return _CODES.get(code, {})


def get_all_system_codes() -> list[str]:
    """Return all registered system error codes."""
    _load()
    return list(_CODES.keys())


def get_error_message(code: str) -> Dict:
    """Return the message dict for a system error code."""
    _load()
    return _MESSAGES.get(code, {})

"""
Console output utilities for the DCC pipeline.
Provides standardized formatting for terminal output using schema-driven message IDs.
"""
import builtins
import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from datetime import datetime

from core_engine.logging import log_status, log_warning, DEBUG_OBJECT, DEBUG_LEVEL

# Cache for pipeline messages
_MESSAGE_CATALOG: Optional[Dict[str, Any]] = None


def _load_message_catalog() -> Dict[str, Any]:
    """Load the pipeline message catalog from config/schemas/pipeline_message_config.json."""
    global _MESSAGE_CATALOG
    if _MESSAGE_CATALOG is not None:
        return _MESSAGE_CATALOG

    # Attempt to find the config file relative to this file
    # Path: workflow/utility_engine/console/console_output.py
    # Target: config/schemas/pipeline_message_config.json
    base_dir = Path(__file__).parents[3]
    config_path = base_dir / "config" / "schemas" / "pipeline_message_config.json"

    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                _MESSAGE_CATALOG = data.get("messages", {})
        except Exception as exc:
            # Fallback to empty if loading fails
            builtins.print(f"WARNING: Failed to load message catalog: {exc}")
            _MESSAGE_CATALOG = {}
    else:
        # Fallback for tests or missing file
        _MESSAGE_CATALOG = {}

    return _MESSAGE_CATALOG


def get_message(msg_id: str, **context) -> Tuple[str, int, str]:
    """
    Look up a message by ID and hydrate its template with context.
    Returns: (hydrated_message, min_level, icon)
    """
    catalog = _load_message_catalog()
    msg_def = catalog.get(msg_id)

    if not msg_def:
        # Fallback if ID is missing (treat ID as the message itself for safety)
        return msg_id, 1, ""

    template = msg_def.get("template", "")
    level = msg_def.get("level", 1)
    icon = msg_def.get("icon", "")

    try:
        hydrated = template.format(**context)
    except Exception:
        # If hydration fails, return raw template
        hydrated = template

    return hydrated, level, icon


def status_print(msg_id: str, **kwargs: Any) -> None:
    """
    Print a status message based on its ID.
    If msg_id is not in catalog, prints it as a literal string.
    """
    # Check if we should override the level from kwargs
    min_level_override = kwargs.pop("min_level", None)

    message, level, icon = get_message(msg_id, **kwargs)

    # Use override if provided, else use level from catalog
    min_level = min_level_override if min_level_override is not None else level

    # Prepend icon if present in catalog (status messages usually don't have icons in Phase 1-3,
    # but the schema allows it)
    full_message = f"{icon} {message}" if icon else message

    log_status(full_message, min_level=min_level)


def milestone_print(msg_id: str, detail: str = "", ok: bool = True, error_code: str = None, **kwargs: Any) -> None:
    """Print a clean pipeline milestone line using message ID."""
    message, level, icon_catalog = get_message(msg_id, **kwargs)

    if DEBUG_LEVEL >= level:
        # Use icon from catalog if present, else fallback to standard OK/X
        icon = icon_catalog if icon_catalog else ("✓" if ok else "✗")
        icon_display = icon if ok else "✗"

        code_str = f"  [{error_code}]" if (error_code and not ok) else ""
        builtins.print(f"  {icon_display}  {message:<22} {detail}{code_str}", flush=True)

    DEBUG_OBJECT["messages"].append({
        "level": level,
        "timestamp": datetime.now().isoformat(),
        "module": "milestone",
        "context": message,
        "message": detail,
    })


def debug_print(msg_id: str, **kwargs: Any) -> None:
    """Print a debug message (level 2)."""
    message, _, _ = get_message(msg_id, **kwargs)
    log_warning(message)


def print_framework_banner(
    base_path: Path = None,
    input_file: str = None,
    output_dir: str = None,
    version: str = "3.0",
    cli_overrides: Dict[str, Any] = None,
    bootstrap_status: str = "complete",
    bootstrap_phases: int = 8,
) -> None:
    """Print default framework banner."""
    mode = {0: "quiet", 1: "normal", 2: "debug", 3: "trace"}.get(DEBUG_LEVEL, "normal")

    input_name = Path(input_file).name if input_file else "stdin"
    output_name = Path(output_dir).name if output_dir else "output"

    banner_content = f"""  DCC Pipeline v{version}
  Mode: {mode}
  base_path: {base_path if base_path else 'N/A'}
  Input: {input_name}
  Output: {output_name}
  Bootstrap: {bootstrap_phases} phases {bootstrap_status.upper()}
  DEBUG {'ENABLED' if DEBUG_LEVEL >= 2 else 'DISABLED':<37}
  CLI Overrides: {json.dumps(cli_overrides) if cli_overrides else 'None'}  """

    content_width = max(len(line) for line in banner_content.splitlines())
    total_width = content_width + 6
    banner_border = "=" * total_width

    banner = f"{banner_border}\n"
    for line in banner_content.splitlines():
        banner += f"  {line.ljust(content_width)}  \n"
    banner += banner_border

    builtins.print(banner, flush=True)

"""
Console UI utilities for the DCC pipeline.
Provides standardized formatting for terminal output.
"""
import builtins
import json
from pathlib import Path
from typing import Any, Dict
from datetime import datetime

from core_engine.logging import log_status, log_warning, DEBUG_OBJECT, DEBUG_LEVEL


def status_print(*args: Any, **kwargs: Any) -> None:
    """Legacy status print - maps to level 1 logging."""
    message = " ".join(str(a) for a in args)
    min_level = kwargs.get("min_level", 1)
    log_status(message, min_level=min_level)


def milestone_print(step: str, detail: str, ok: bool = True, error_code: str = None) -> None:
    """Print a clean pipeline milestone line — always visible at level 1+."""
    if DEBUG_LEVEL >= 1:
        icon = "OK" if ok else "X"
        code_str = f"  [{error_code}]" if (error_code and not ok) else ""
        builtins.print(f"  {icon}  {step:<22} {detail}{code_str}", flush=True)
        
    DEBUG_OBJECT["messages"].append({
        "level": 1,
        "timestamp": datetime.now().isoformat(),
        "module": "milestone",
        "context": step,
        "message": detail,
    })


def debug_print(*args: Any, **kwargs: Any) -> None:
    """Legacy debug print - maps to level 2 logging."""
    message = " ".join(str(a) for a in args)
    log_warning(message)


def print_framework_banner(
    base_path: Path = None,
    input_file: str = None,
    output_dir: str = None,
    version: str = "3.0",
    cli_overrides: Dict[str, Any] = None,
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
  DEBUG {'ENABLED' if DEBUG_LEVEL >= 2 else 'DISABLED':<49}
  CLI Overrides: {json.dumps(cli_overrides) if cli_overrides else 'None'}  """
    
    content_width = max(len(line) for line in banner_content.splitlines())
    total_width = content_width + 6
    banner_border = "=" * total_width

    banner = f"{banner_border}\n"
    for line in banner_content.splitlines():
        banner += f"  {line.ljust(content_width)}  \n"
    banner += banner_border
    
    builtins.print(banner, flush=True)

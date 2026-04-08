
import logging
import sys
import builtins
from typing import Any

DEBUG_DEV_MODE = False

def set_debug_mode(enabled: bool):
    """
    Set the global debug mode flag.

    Args:
        enabled: True to enable debug mode, False to disable.

    Breadcrumb Comments:
        - DEBUG_DEV_MODE: Global flag modified here.
                         Consumed by debug_print() to conditionally output.
    """
    global DEBUG_DEV_MODE
    DEBUG_DEV_MODE = enabled

# Global debug mode flag
def setup_logger(debug_mode: bool = False):
    """
    Configure the global logging settings.

    Sets up basic logging configuration with timestamp, level, and message format.
    Log level is DEBUG if debug_mode is True, otherwise INFO.

    Args:
        debug_mode: If True, set log level to DEBUG. Default is INFO.

    Breadcrumb Comments:
        - debug_mode: Controls logging level passed to logging.basicConfig().
        - Format includes timestamp, level name, and message.
        - Output directed to sys.stdout.
    """
    level = logging.DEBUG if debug_mode else logging.INFO
    
    # Standard format: [TIME] LEVEL - MESSAGE
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout
    )

def status_print(*args: Any, **kwargs: Any) -> None:
    """
    Print status messages with automatic flush.

    Wrapper around print() that ensures output is flushed immediately.
    Used throughout the engine for real-time status updates.

    Args:
        *args: Variable arguments to print.
        **kwargs: Keyword arguments passed to print().

    Breadcrumb Comments:
        - Used by validate_folders(), resolve_output_paths(),
          and throughout pipeline for status messages.
        - Automatically sets flush=True for immediate output.
    """
    kwargs.setdefault("flush", True)
    builtins.print(*args, **kwargs)


def debug_print(*args: Any, **kwargs: Any) -> None:
    """
    Print debug messages only in dev mode.

    Conditionally prints messages only when DEBUG_DEV_MODE is True.
    Used for development and troubleshooting output.

    Args:
        *args: Variable arguments to print.
        **kwargs: Keyword arguments passed to print().

    Breadcrumb Comments:
        - DEBUG_DEV_MODE: Global flag set via set_debug_mode().
                         If True, prints with flush enabled.
                         If False, silently discards output.
    """
    if DEBUG_DEV_MODE:
        kwargs.setdefault("flush", True)
        builtins.print(*args, **kwargs)

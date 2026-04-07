
import logging
import sys
import builtins
from typing import Any

DEBUG_DEV_MODE = False

def set_debug_mode(enabled: bool):
    global DEBUG_DEV_MODE
    DEBUG_DEV_MODE = enabled

# Global debug mode flag
def setup_logger(debug_mode: bool = False):
    """
    Configures the global logging settings.
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
    """Print status messages with flush."""
    kwargs.setdefault("flush", True)
    builtins.print(*args, **kwargs)


def debug_print(*args: Any, **kwargs: Any) -> None:
    """Print debug messages only in dev mode."""
    if DEBUG_DEV_MODE:
        kwargs.setdefault("flush", True)
        builtins.print(*args, **kwargs)

"""
common.library.core.messages — BaseMessageManager and catalog loader.

Exports
-------
BaseMessageManager  L11  Abstract base: catalog loading, template hydration,
                         verbosity filtering, show() routing

Sources
-------
dcc: utility_engine/console/console_output.py  (_load_message_catalog, get_message, status_print)
eks: engine/core/message_manager.py            (MessageManager class — reference impl)
"""

from common.library.core.messages.message_manager import BaseMessageManager

__all__ = ["BaseMessageManager"]

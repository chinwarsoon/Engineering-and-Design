"""
common.library.column_processor.registry — HandlerRegistry for calculation type dispatch.

Exports:
    HandlerRegistry       — maps calculation.type strings to handler callables
    ColumnProcessorError  — base error for column processor exceptions

Revision: 0.1
Date: 2026-07-29
Author: opencode
Summary: Initial HandlerRegistry — register/lookup by calc type with callable guard.
"""

from typing import Any, Callable, Dict, List


class ColumnProcessorError(Exception):
    """Base error for column processor operations."""


class HandlerRegistry:
    """
    Maps calculation.type strings to handler callables.

    Handler signature::

        handler(column_config: dict, data: dict, context: dict) -> Any

    Where:
        column_config — the full column entry from the column_processing config
        data          — the document/data dict being processed
        context       — phase context (metadata, parsed content, etc.)

    Usage::

        registry = HandlerRegistry()
        registry.register("priority_chain", resolve_priority_chain)
        handler = registry.get("priority_chain")  # raises if missing
    """

    def __init__(self) -> None:
        self._handlers: Dict[str, Callable] = {}

    def register(self, calc_type: str, handler: Callable) -> None:
        if not callable(handler):
            raise ColumnProcessorError(
                f"Cannot register handler for '{calc_type}': object is not callable"
            )
        self._handlers[calc_type] = handler

    def get(self, calc_type: str) -> Callable:
        if calc_type not in self._handlers:
            raise ColumnProcessorError(
                f"No handler registered for calculation type: {calc_type}. "
                f"Registered: {', '.join(sorted(self._handlers)) or '(none)'}"
            )
        return self._handlers[calc_type]

    @property
    def registered_types(self) -> List[str]:
        return list(self._handlers.keys())

    def __contains__(self, calc_type: str) -> bool:
        return calc_type in self._handlers

"""
common.library.column_processor.base — BaseColumnProcessor generic orchestrator.

Exports:
    BaseColumnProcessor  — schema-driven phase dispatcher for column processing

Revision: 0.1
Date: 2026-07-29
Author: opencode
Summary: Initial BaseColumnProcessor — phase-filtered dispatch + handler invocation.
"""

from typing import Any, Dict

from .registry import HandlerRegistry, ColumnProcessorError


class BaseColumnProcessor:
    """
    Generic schema-driven phase dispatcher for column processing.

    Reads a ``column_processing`` config dict (keyed by column name), filters
    columns by ``processing_phase``, then dispatches each calculated column to
    the handler registered for its ``calculation.type``.

    Handler signature::

        handler(column_config: dict, data: dict, context: dict) -> Any

    Subclasses register project-specific handlers in their constructor, then
    call ``process(phase, data, context)`` for each document.

    Usage::

        registry = HandlerRegistry()
        registry.register("priority_chain", my_handler)
        proc = BaseColumnProcessor(column_config, registry)
        result = proc.process("B", {"doc_id": "..."}, {"metadata": {...}})
    """

    def __init__(self, column_config: Dict[str, Any], registry: HandlerRegistry) -> None:
        if not isinstance(column_config, dict):
            raise ColumnProcessorError("column_config must be a dict (column-name-keyed entries)")
        if not isinstance(registry, HandlerRegistry):
            raise ColumnProcessorError("registry must be a HandlerRegistry instance")
        self._column_config = column_config
        self._registry = registry

    def process(self, phase: str, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process all calculated columns assigned to *phase*.

        Iterates the column config, filtering by ``processing_phase``.
        For each calculated column, resolves the handler by ``calculation.type``,
        invokes it, and writes the returned value to *data*.

        Args:
            phase:   Pipeline phase identifier (e.g. ``"A"``, ``"B"``, ``"C"``)
            data:    Document/data dict (mutated in-place and returned)
            context: Phase context dict carrying handler-specific data
                     (parsed metadata, extracted elements, config references)

        Returns:
            The same dict as *data* (mutated in-place).
        """
        for col_name, col_entry in self._column_config.items():
            if col_entry.get("processing_phase") != phase:
                continue
            if not col_entry.get("is_calculated"):
                continue

            calc = col_entry.get("calculation")
            if not calc:
                continue

            handler = self._registry.get(calc["type"])
            value = handler(col_entry, data, context)
            if value is not None:
                data[col_name] = value
            elif calc.get("fallback") == "default_value":
                if "default" in col_entry:
                    data[col_name] = col_entry["default"]

        return data

    @property
    def column_config(self) -> Dict[str, Any]:
        return dict(self._column_config)

    @property
    def registered_types(self) -> list:
        return self._registry.registered_types

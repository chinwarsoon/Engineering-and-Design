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

            if not self._applies(col_name, col_entry, context):
                continue

            if not self._extraction_applies(col_name, col_entry, context):
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

    def _applies(self, col_name: str, col_entry: Dict[str, Any],
                 context: Dict[str, Any]) -> bool:
        """
        I275: document-type scope filter for a column.

        Resolves the current document's concept_id (from context
        ``"concept_id"``) and ``format_category`` (from context
        ``"format_category"``), then:

        1. If ``applies_to_document_types`` is present and does not contain the
           resolved ``concept_id``, the column is skipped.
        2. If ``native_only`` is true and the resolved ``format_category`` is
           ``"print"``, the column is skipped (PDF prints carry no embedded
           metadata).

        Absent scope keys mean "all" — a column with no ``applies_to_document_types``
        applies to every concept, and a column without ``native_only`` applies to
        both native and print delivery. A document whose concept cannot be resolved
        is treated as unrestricted (defaults to applying).
        """
        concept_id = context.get("concept_id")
        format_category = context.get("format_category")

        applies_to = col_entry.get("applies_to_document_types")
        if applies_to and concept_id is not None:
            if isinstance(applies_to, (list, tuple)) and concept_id not in applies_to:
                return False
            if isinstance(applies_to, str) and concept_id != applies_to:
                return False

        native_only = col_entry.get("native_only")
        if native_only and format_category == "print":
            return False

        return True

    def _extraction_applies(self, col_name: str, col_entry: Dict[str, Any],
                            context: Dict[str, Any]) -> bool:
        """
        I277: gate a column by the resolved extraction-method capability set.

        The context may carry ``"extraction_methods"`` — the set of methods
        admitted for this document (resolved by the project from the selected
        parsing profile's ``extraction_methods`` intersected with the binding
        ``format_category``). When absent, the column is unrestricted (defaults
        to applying) so existing callers that do not provide capability info
        behave exactly as before.

        Subclasses may override to derive the column's required method from its
        calculation config; the base implementation applies no gating.
        """
        extraction_methods = context.get("extraction_methods")
        if extraction_methods is None:
            return True
        required = self._required_extraction_method(col_name, col_entry, context)
        if not required:
            return True
        return required in extraction_methods

    def _required_extraction_method(self, col_name: str, col_entry: Dict[str, Any],
                                    context: Dict[str, Any]) -> Any:
        """
        I277: determine the extraction method a column requires.

        Subclasses may override. Returns the required method (or ``None`` for
        no requirement). The base implementation treats only the direct
        ``calculation.type`` as the requirement when it matches an extraction
        handler name.
        """
        calc = col_entry.get("calculation")
        if calc:
            return calc.get("type")
        return None

    @property
    def column_config(self) -> Dict[str, Any]:
        return dict(self._column_config)

    @property
    def registered_types(self) -> list:
        return self._registry.registered_types

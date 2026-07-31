"""
EKS Column Processor — schema-driven orchestrator for all 42 document registry columns.

EKSColumnProcessor wraps ``common.library.column_processor.BaseColumnProcessor`` with
EKS-specific handler registration and a factory method for instantiation from
doc_config.

Handlers (T1.186):
  - priority_chain         → resolve from ordered sources (cover_page > metadata > lookup > existing)
  - filename_segment       → read from already-parsed data dict or delegate to FilenameParser
  - file_property          → lookup from FilePropertyExtractor output
  - parser_metadata        → key lookup from parser metadata dict
  - cover_page_element     → extract field from cover_page structure detection element
  - code_to_title_lookup   → project_code → project_title from project_code_titles registry
  - health_score           → read from HealthScorer output
  - auto_increment         → UUID generation
  - existing_record        → preserve current data dict value

Revision: 0.3
Date: 2026-07-31
Author: opencode
Summary: 0.3: T1.194 (I265) — EKSColumnProcessor accepts an optional injected
          runtime_slice (Appendix L D1). _resolve_code_to_title() falls back to
          the slice's resolved project name when project_code_titles has no
          entry. Backward-compatible: from_doc_config() without a slice behaves
          exactly as before (L.14.7).
0.2: T1.186 — enhanced all 9 handlers with real pipeline logic.
0.1: T1.185 — initial handler stubs.
"""

import re
from typing import Any, Dict, Optional

from common.library.column_processor import (
    BaseColumnProcessor,
    HandlerRegistry,
    ColumnProcessorError,
)


def _resolve_priority_chain(column_config: Dict[str, Any], data: Dict[str, Any],
                             context: Dict[str, Any]) -> Optional[Any]:
    """
    Resolve column value from an ordered list of sources.
    First non-null value wins.

    Sources handled:
      - parser_metadata      → context.metadata[field]
      - cover_page_element   → elements[cover_page].content[field]
      - code_to_title_lookup → project_code_titles[project_number]
      - file_property        → context.file_properties[field]
      - existing_record      → data[field]

    Special: ``document_type`` keeps existing filename-derived value when
    parser metadata returns a plausible but different value (priority:
    cover sheet > filename > extension).
    """
    calc = column_config.get("calculation", {})
    sources = calc.get("sources", [])

    col_type = column_config.get("column_type", "")

    for source in sources:
        source_type = source.get("source")
        field = source.get("field")
        val = None

        if source_type == "parser_metadata":
            metadata = context.get("metadata", {})
            val = metadata.get(field)

        elif source_type == "cover_page_element":
            elements = context.get("elements", [])
            for el in elements:
                if el.get("element_type") == "cover_page":
                    content = el.get("content", {})
                    if isinstance(content, dict):
                        val = content.get(field)
                        break

        elif source_type == "code_to_title_lookup":
            key = data.get(field) or data.get("project_number")
            if key:
                titles = context.get("project_code_titles", {})
                val = titles.get(key)

        elif source_type == "file_property":
            val = context.get("file_properties", {}).get(field)

        elif source_type == "existing_record":
            val = data.get(field)

        if val is None:
            continue

        # document_type: keep filename-derived value if already set and parser disagrees
        if source_type == "parser_metadata" and field == "document_type":
            existing = data.get("document_type")
            if existing and existing not in ("UNKNOWN", None) and existing != val:
                continue

        # Type coercion: numeric_column from string source
        if col_type == "numeric_column" and isinstance(val, str):
            try:
                return int(val)
            except (ValueError, TypeError):
                try:
                    return float(val)
                except (ValueError, TypeError):
                    return val

        return val

    return None


def _resolve_filename_segment(column_config: Dict[str, Any], data: Dict[str, Any],
                               context: Dict[str, Any]) -> Optional[Any]:
    """
    Resolve column value from Phase A filename parsing.

    Phase A runs FilenameParser on every discovered file and stores results
    in the data dict. This handler reads the already-parsed value from the
    data dict by ``maps_to`` key.

    For revision columns: if not already parsed, attempt basic revision
    detection from filename suffix (``_revNN`` pattern).
    """
    calc = column_config.get("calculation", {})
    maps_to = calc.get("maps_to")

    if maps_to and maps_to in data and data[maps_to] is not None:
        return data[maps_to]

    # Fallback: revision detection from file_path suffix (Phase A may have missed it)
    if maps_to == "revision":
        file_path = data.get("file_path", "")
        stem = file_path.rsplit(".", 1)[0] if "." in file_path else file_path
        rev_match = re.search(r"_rev([A-Z0-9]+)$", stem)
        if rev_match:
            return rev_match.group(1)

    return None


def _resolve_file_property(column_config: Dict[str, Any], data: Dict[str, Any],
                            context: Dict[str, Any]) -> Optional[Any]:
    """
    Resolve column value from FilePropertyExtractor output.

    Reads from ``context.file_properties`` dict which contains keys like
    ``file_size``, ``file_created_at``, ``file_modified_at``, ``file_hash``.
    """
    calc = column_config.get("calculation", {})
    field = calc.get("maps_to") or calc.get("field")
    if field:
        fp = context.get("file_properties", {})
        return fp.get(field)
    return None


def _resolve_parser_metadata(column_config: Dict[str, Any], data: Dict[str, Any],
                              context: Dict[str, Any]) -> Optional[Any]:
    """
    Resolve column value directly from parser metadata dict.

    Handles type coercion: numeric fields (page_count, embedded_sheet_count)
    are converted to int if returned as string.
    """
    calc = column_config.get("calculation", {})
    field = calc.get("field") or calc.get("maps_to")
    if not field:
        return None
    metadata = context.get("metadata", {})
    val = metadata.get(field)

    if val is not None:
        col_type = column_config.get("column_type", "")
        if col_type == "numeric_column" and isinstance(val, str):
            try:
                return int(val)
            except (ValueError, TypeError):
                try:
                    return float(val)
                except (ValueError, TypeError):
                    return val
        return val

    return None


def _resolve_cover_page_element(column_config: Dict[str, Any], data: Dict[str, Any],
                                 context: Dict[str, Any]) -> Optional[Any]:
    """
    Resolve column value from cover page element content.

    Special: ``field == "asset_tags"`` returns a list by splitting on
    comma/space. Handles both dict and string-serialised content.
    """
    calc = column_config.get("calculation", {})
    field = calc.get("field")
    if not field:
        return None

    elements = context.get("elements", [])
    for el in elements:
        if el.get("element_type") != "cover_page":
            continue
        content = el.get("content", {})

        if isinstance(content, str):
            try:
                import ast
                content = ast.literal_eval(content)
            except (ValueError, SyntaxError):
                content = {}

        if not isinstance(content, dict):
            continue

        val = content.get(field)
        if val is None:
            continue

        # asset_tags: comma/space-split string → list of strings
        if field == "asset_tags" and isinstance(val, str):
            return [t.strip() for t in re.split(r"[,\s]+", str(val)) if t.strip()]

        return val

    return None


def _resolve_code_to_title(column_config: Dict[str, Any], data: Dict[str, Any],
                            context: Dict[str, Any]) -> Optional[Any]:
    """
    Look up project title from project_code_titles registry.

    Uses ``data[source_field]`` as the lookup key.
    Source field defaults to ``"project_number"`` (configurable via
    calculation.field).

    T1.194 (I265): When the titles registry has no entry, falls back to the
    injected ``config_slice`` resolved project name (Appendix L D1). The slice
    comes from Project Definition ``project_identity.project_name``.
    """
    calc = column_config.get("calculation", {})
    source_field = calc.get("field", "project_number")
    key = data.get(source_field)
    if key:
        titles = context.get("project_code_titles", {})
        title = titles.get(key)
        if title:
            return title
        # T1.194 (I265): Slice fallback — resolved project name from the
        # injected ProjectConfigurationRegistry slice.
        slice_ctx = context.get("config_slice", {})
        project_domain = slice_ctx.get("project")
        if project_domain is not None:
            title = getattr(project_domain, "project_name", None)
            if title:
                return title
    return None


def _resolve_health_score(column_config: Dict[str, Any], data: Dict[str, Any],
                           context: Dict[str, Any]) -> Optional[Any]:
    """
    Read health score from HealthScorer output.

    Expects ``context.score`` to contain an ``overall`` key or
    ``health_score`` key from the HealthScorer.
    """
    score = context.get("score", {})
    return score.get("health_score") or score.get("overall")


def _resolve_auto_increment(column_config: Dict[str, Any], data: Dict[str, Any],
                             context: Dict[str, Any]) -> Optional[Any]:
    """
    Generate auto-increment value (UUID for id column).
    """
    import uuid
    return str(uuid.uuid4())


def _resolve_existing_record(column_config: Dict[str, Any], data: Dict[str, Any],
                              context: Dict[str, Any]) -> Optional[Any]:
    """
    Preserve existing value from the current record.

    If the data dict already has a non-null value for the target field,
    return it (preserve existing). Otherwise return None.
    """
    calc = column_config.get("calculation", {})
    field = calc.get("field") or calc.get("maps_to")
    if field and field in data:
        return data[field]
    return None


class EKSColumnProcessor(BaseColumnProcessor):
    """
    EKS-specific column processor with all 9 handler types pre-registered.

    Usage::

        processor = EKSColumnProcessor.from_doc_config(
            doc_config, runtime_slice=cfg.slice_for("ColumnProcessor")
        )
        result = processor.process("B", document_dict, {
            "metadata": metadata,
            "elements": elements,
            "file_properties": file_properties,
            "project_code_titles": project_code_titles,
            "score": score,
            "config_slice": cfg.slice_for("ColumnProcessor"),
        })
    """

    HANDLER_TYPES = {
        "priority_chain": _resolve_priority_chain,
        "filename_segment": _resolve_filename_segment,
        "file_property": _resolve_file_property,
        "parser_metadata": _resolve_parser_metadata,
        "cover_page_element": _resolve_cover_page_element,
        "code_to_title_lookup": _resolve_code_to_title,
        "health_score": _resolve_health_score,
        "auto_increment": _resolve_auto_increment,
        "existing_record": _resolve_existing_record,
    }

    def __init__(self, column_config: Dict[str, Any],
                 runtime_slice: Optional[Dict[str, Any]] = None) -> None:
        registry = HandlerRegistry()
        for calc_type, handler_fn in self.HANDLER_TYPES.items():
            registry.register(calc_type, handler_fn)
        super().__init__(column_config, registry)
        # T1.194 (I265): Injected config slice (Appendix L D1). Handlers receive
        # the slice via the process() context; this copy is kept for traceability.
        self.runtime_slice = runtime_slice or {}

    @classmethod
    def from_doc_config(cls, doc_config: Dict[str, Any],
                        runtime_slice: Optional[Dict[str, Any]] = None) -> "EKSColumnProcessor":
        """
        Factory method: instantiate from EKS doc_config.

        Reads ``column_processing`` section and builds the processor.
        Raises ``ColumnProcessorError`` if ``column_processing`` is missing.

        T1.194 (I265): Optional ``runtime_slice`` (the resolved config slice for
        the module's project) is injected for handler consumption.
        """
        column_config = doc_config.get("column_processing")
        if not column_config:
            raise ColumnProcessorError(
                "doc_config missing 'column_processing' section — "
                "ensure eks_doc_config.json has column_processing entries"
            )
        return cls(column_config, runtime_slice=runtime_slice)

"""
Base processor class for all processing components.
"""
import logging
from typing import Dict, Any, Optional

from core_engine.context.context_pipeline import PipelineContext
from core_engine.logging import log_warning
from utility_engine.console import status_print

logger = logging.getLogger("core_engine.base")


class BaseProcessor:
    """
    Abstract base class containing shared properties and methods
    for all processing components.
    """

    def __init__(self, context: PipelineContext, schema_data: Dict[str, Any]):
        """
        Initialize with the global context and schema data.

        Args:
            context: The global pipeline context.
            schema_data: The full resolved schema containing definitions and reference data.
        """
        self.context = context
        self.schema_data = schema_data

    def _print_processing_step(self, phase: str, column_name: str, detail: str) -> None:
        """
        Standardized console and log output for tracking processing stages.
        """
        message = f"[{phase}] {column_name}: {detail}"
        status_print(message)
        logger.info(message)

    def _resolve_schema_reference(self, ref_config: Dict[str, Any]) -> Any:
        """
        Resolve a schema reference to its actual value using the current
        top-level schema architecture.

        The schema stores reference data as top-level lists keyed by domain
        (e.g. schema_data['approval_codes'], schema_data['departments']).
        The mapping from schema_name to top-level key is read from the schema's
        own 'schema_reference_map' section when present, with a built-in
        fallback for the standard DCC register schemas.

        Args:
            ref_config: Dict with 'schema', 'code', and 'field' keys.
                        Breadcrumb: column_def['calculation']['ref'] → here.

        Returns:
            Resolved value or None if not found.
        """
        schema_name = ref_config.get('schema')
        code = ref_config.get('code')
        field = ref_config.get('field')

        if not all([schema_name, code, field]):
            log_warning(f"Invalid schema reference: {ref_config}")
            return None

        # Prefer schema-driven reference map; fall back to built-in defaults
        reference_map: Dict[str, str] = self.schema_data.get('schema_reference_map', {
            'approval_code_schema': 'approval_codes',
            'department_schema':    'departments',
            'discipline_schema':    'disciplines',
            'facility_schema':      'facilities',
            'document_type_schema': 'document_types',
            'project_code_schema':  'projects',
        })

        top_level_key = reference_map.get(schema_name)
        if not top_level_key:
            log_warning(f"No reference map entry for schema '{schema_name}'")
            return None

        entries = self.schema_data.get(top_level_key)
        if not isinstance(entries, list):
            log_warning(f"Reference data '{top_level_key}' is missing or not a list")
            return None

        for entry in entries:
            if entry.get('code') == code:
                value = entry.get(field)
                if value is not None:
                    return value

        log_warning(f"Reference not found: {schema_name}[code={code}].{field}")
        return None

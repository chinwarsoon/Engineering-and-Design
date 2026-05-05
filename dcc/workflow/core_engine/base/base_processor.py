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
        Resolve a schema reference to its actual value.

        Supports both new architecture and legacy _data suffix keys.
        """
        schema_name = ref_config.get('schema')
        code = ref_config.get('code')
        field = ref_config.get('field')

        if not all([schema_name, code, field]):
            log_warning(f"Invalid schema reference: {ref_config}")
            return None

        data_section = ref_config.get('data_section', 'approval')

        # New architecture: map schema_name to top-level key
        _new_key_map = {
            'approval_code_schema': 'approval_codes',
            'department_schema':    'departments',
            'discipline_schema':    'disciplines',
            'facility_schema':      'facilities',
            'document_type_schema': 'document_types',
            'project_code_schema':  'projects',
        }
        top_level_key = _new_key_map.get(schema_name)
        entries = None

        if top_level_key and isinstance(self.schema_data.get(top_level_key), list):
            entries = self.schema_data[top_level_key]
        else:
            # Legacy fallback: schema_name_data.data_section
            ref_schema_data = self.schema_data.get(f'{schema_name}_data', {})
            entries = ref_schema_data.get(data_section, [])

        for entry in entries or []:
            if entry.get('code') == code:
                value = entry.get(field)
                if value is not None:
                    return value

        log_warning(f"Reference not found: {schema_name}[code={code}].{field}")
        return None

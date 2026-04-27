"""
Base classes for DCC engines and processors.
"""
import logging
from typing import Dict, Any, Optional

from ..context import PipelineContext

logger = logging.getLogger("dcc_core.base")


class BaseEngine:
    """
    Abstract base class for all domain-specific engines in the DCC pipeline.
    """
    def __init__(self, context: PipelineContext):
        """
        Initialize the engine with the global pipeline context.
        
        Args:
            context: The PipelineContext containing paths, parameters, and state.
        """
        self.context = context


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

    def _resolve_schema_reference(self, ref_config: Dict[str, Any]) -> Any:
        """
        Resolve a schema reference to its actual value.

        Supports two schema architectures:
        - New: top-level keys (e.g., schema_data['approval_codes'], schema_data['departments'])
        - Legacy: _data suffix keys (e.g., schema_data['approval_code_schema_data'])

        Args:
            ref_config: Dict with 'schema', 'code', and 'field' keys.

        Returns:
            Resolved value or None if not found.
        """
        schema_name = ref_config.get('schema')
        code = ref_config.get('code')
        field = ref_config.get('field')

        if not all([schema_name, code, field]):
            logger.warning(f"Invalid schema reference: {ref_config}")
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

        logger.warning(f"Reference not found: {schema_name}[code={code}].{field}")
        return None

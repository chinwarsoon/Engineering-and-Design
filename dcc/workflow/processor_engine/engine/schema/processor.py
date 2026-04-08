"""
The logic for _resolve_schema_reference, which maps internal schema codes to actual values (like looking up approval codes), belongs in this file.
"""

import logging
from typing import Dict, Any, Optional, List
from ..core.base import BaseProcessor

logger = logging.getLogger(__name__)

class SchemaProcessor(BaseProcessor):
    """
    Handles the translation of schema definitions into actionable 
    instructions for the CalculationEngine.
    """

    def __init__(self, schema_data: Dict[str, Any]):
        """
        Initialize the processor with the full schema.
        """
        super().__init__(schema_data)
        self.enhanced_schema = schema_data.get('enhanced_schema', {})
        self.column_definitions = self.enhanced_schema.get('columns', {})
        self.column_sequence = self.enhanced_schema.get('column_sequence', [])

    def get_ordered_columns(self) -> Dict[str, Dict]:
        """
        Returns the column definitions reordered according to the 
        schema's column_sequence.
        """
        if not self.column_sequence:
            return {
                name: defn for name, defn in self.column_definitions.items() 
                if isinstance(defn, dict)
            }

        ordered_cols = {
            name: self.column_definitions[name]
            for name in self.column_sequence
            if name in self.column_definitions and isinstance(self.column_definitions[name], dict)
        }

        # Append any columns present in definitions but missing from sequence
        for name, definition in self.column_definitions.items():
            if name not in ordered_cols and isinstance(definition, dict):
                ordered_cols[name] = definition
        
        return ordered_cols

    def resolve_reference(self, ref_config: Dict) -> Any:
        """
        Resolves a schema reference (e.g., $ref) to its actual value.
        
        Args:
            ref_config: Dict containing 'schema', 'code', and 'field' keys.
            
        Returns:
            The resolved value from the referenced schema data.
        """
        schema_name = ref_config.get('schema')
        code = ref_config.get('code')
        field = ref_config.get('field')
        
        if not all([schema_name, code, field]):
            logger.warning(f"Invalid schema reference configuration: {ref_config}")
            return None
        
        # Load the external data section (e.g., approval_code_schema_data)
        ref_schema_data = self.schema_data.get(f'{schema_name}_data', {})
        if not ref_schema_data:
            logger.warning(f"Referenced schema data not found: {schema_name}_data")
            return None
        
        # Search the data section for the matching code
        data_section = ref_config.get('data_section', 'approval')
        entries = ref_schema_data.get(data_section, [])
        
        for entry in entries:
            if entry.get('code') == code:
                value = entry.get(field)
                if value is not None:
                    logger.debug(f"Resolved reference: {schema_name}.{code}.{field} -> {value}")
                    return value
        
        logger.warning(f"Code '{code}' not found in {schema_name}.{data_section}")
        return None

    def get_calculation_config(self, column_name: str) -> Optional[Dict]:
        """
        Retrieves the specific calculation block for a given column.
        """
        col_def = self.column_definitions.get(column_name, {})
        return col_def.get('calculation') if col_def.get('is_calculated') else None
    
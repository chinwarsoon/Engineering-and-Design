"""
logging configuration and any base utility methods (like _print_processing_step)
will be placed here to be shared across the engine.
"""
import logging
from typing import Dict, Any, Optional

# Import hierarchical logging functions from initiation_engine (centralized)
from initiation_engine import status_print

# Standardized logging configuration used across the engine
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("document_processor")

class BaseProcessor:
    """
    Abstract base class containing shared properties and logging methods
    for all processing components.
    """

    def __init__(self, schema_data: Dict[str, Any]):
        """
        Initialize with the global schema data.

        Args:
            schema_data: The full resolved schema containing definitions and reference data.
        """
        self.schema_data = schema_data

    def _print_processing_step(self, phase: str, column_name: str, detail: str):
        """
        Standardized console and log output for tracking the execution
        of different processing stages.
        
        Uses hierarchical indentation based on call depth.
        """
        message = f"[{phase}] {column_name}: {detail}"
        status_print(message)
        logger.info(message)

    def _resolve_schema_reference(self, ref_config: Dict[str, Any]) -> Any:
        """
        Utility to resolve a schema reference (e.g., $ref) to its actual value 
        by looking it up in the loaded schema data.
        
        Args:
            ref_config: Dictionary containing 'schema', 'code', and 'field' keys.
            
        Returns:
            The resolved value from the reference, or None if not found.
        """
        schema_name = ref_config.get('schema')
        code = ref_config.get('code')
        field = ref_config.get('field')
        
        if not all([schema_name, code, field]):
            logger.warning(f"Invalid schema reference: {ref_config}")
            return None
        
        # Look up data in the corresponding data section (e.g., approval_code_schema_data)
        ref_schema_data = self.schema_data.get(f'{schema_name}_data', {})
        data_section = ref_config.get('data_section', 'approval')
        entries = ref_schema_data.get(data_section, [])
        
        for entry in entries:
            if entry.get('code') == code:
                value = entry.get(field)
                if value is not None:
                    return value
        
        logger.warning(f"Reference not found: {schema_name}.{data_section} for code {code}")
        return None
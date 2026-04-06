"""
Functions like _apply_mapping_calculation (for status-to-code conversions).
"""

import pandas as pd
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def apply_mapping_calculation(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Applies a mapping transformation to a column based on a source column 
    and a mapping dictionary defined in the schema.
    """
    source_column = calculation.get('source_column')
    mapping_dict = calculation.get('mapping', {})
    default_value = calculation.get('default_value')

    if not source_column or source_column not in df.columns:
        logger.warning(f"Mapping skipped for {column_name}: source column {source_column} not found.")
        return df

    engine._print_processing_step("Mapping", column_name, f"Mapping from {source_column}")

    # Use pandas map for efficiency
    # If a value isn't in the mapping, it uses the default_value or remains NaN
    df[column_name] = df[source_column].map(mapping_dict)
    
    if default_value is not None:
        df[column_name] = df[column_name].fillna(default_value)

    return df

def apply_status_to_code(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Specialized mapping that resolves schema references for codes.
    Often used when the 'mapping' values are stored in an external schema section.
    """
    source_column = calculation.get('source_column')
    reference_config = calculation.get('reference_config') # e.g., {'schema': 'approval', 'field': 'code'}

    if not source_column or source_column not in df.columns:
        return df

    engine._print_processing_step("Status-to-Code", column_name, f"Resolving codes via {source_column}")

    def resolve_row_code(val):
        if pd.isna(val):
            return None
        # Logic to find the code associated with the status value
        # This typically interacts with engine.schema_processor.resolve_reference
        return engine._resolve_schema_reference({
            **reference_config,
            'code': val
        })

    df[column_name] = df[source_column].apply(resolve_row_code)
    return df
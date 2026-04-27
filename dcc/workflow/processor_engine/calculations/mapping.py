"""
Mapping calculations: status-to-code conversions, value mapping with
external mapping references.
Extracted from UniversalDocumentProcessor._apply_mapping_calculation.
"""

import pandas as pd
from typing import Dict, Any

# Import hierarchical logging functions from dcc_utility
from dcc_utility.console import status_print, debug_print


def _get_preservation_mode(engine, column_name: str) -> str:
    """Get data preservation mode from engine strategy if available."""
    if hasattr(engine, 'get_column_strategy'):
        try:
            strategy = engine.get_column_strategy(column_name)
            if strategy:
                return strategy.preservation_mode.value
        except Exception:
            pass
    return "preserve_existing"


def apply_mapping_calculation(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Applies a mapping transformation to a column based on a source column
    and a mapping dictionary defined in the schema, with support for
    external mapping references.
    """
    source_column = calculation.get('source_column')
    mapping = calculation.get('mapping', {})
    mapping_ref = calculation.get('mapping_reference')
    default = calculation.get('default', 'PEN')

    # Load external mapping if reference provided
    if mapping_ref and not mapping:
        # New architecture: top-level 'approval_codes' list
        # Legacy architecture: '{mapping_ref}_data'.approval list
        _new_key_map = {
            'approval_code_schema': 'approval_codes',
        }
        top_key = _new_key_map.get(mapping_ref)
        if top_key and isinstance(engine.schema_data.get(top_key), list):
            approval_rows = engine.schema_data[top_key]
        else:
            ref_data = engine.schema_data.get(f'{mapping_ref}_data', {})
            approval_rows = ref_data.get('approval', [])

        for row in approval_rows:
            code = row.get('code')
            if not code:
                continue
            status = row.get('status')
            if status:
                mapping[status] = code
            for alias in row.get('aliases', []):
                mapping[alias] = code

    if source_column not in df.columns:
        engine._print_processing_step("Mapping", column_name, f"ERROR: Source column {source_column} not found")
        return df

    engine._print_processing_step("Mapping", column_name, f"Mapping from {source_column} ({len(mapping)} mappings)")

    # Respect strategy configuration
    preservation_mode = _get_preservation_mode(engine, column_name)
    
    if column_name not in df.columns:
        df[column_name] = None

    if preservation_mode == "overwrite_existing":
        # Strategy: Calculate for ALL rows
        engine._print_processing_step("Mapping", column_name, f"Strategy: overwrite_existing - mapping all {len(df)} rows")
        mapped_values = df[source_column].map(mapping)
        df[column_name] = mapped_values.fillna(default)
        engine._print_processing_step("Mapping", column_name, f"Applied to all rows (overwritten)")
    else:
        # Strategy: preserve_existing (default) - only map null values
        null_mask = df[column_name].isna()
        if null_mask.any():
            mapped_values = df.loc[null_mask, source_column].map(mapping)
            df.loc[null_mask, column_name] = mapped_values.fillna(default)
            engine._print_processing_step("Mapping", column_name, f"Applied to {null_mask.sum()} rows with null values")
        else:
            debug_print(f"Skipped mapping for {column_name}: all values already present")

    return df


def apply_status_to_code(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Specialized mapping that resolves schema references for codes.
    Often used when the 'mapping' values are stored in an external schema section.
    
    Respects strategy configuration for data preservation.
    """
    source_column = calculation.get('source_column')
    reference_config = calculation.get('reference_config')  # e.g., {'schema': 'approval', 'field': 'code'}
    default = calculation.get('default', 'PEN')

    if not source_column or source_column not in df.columns:
        return df

    engine._print_processing_step("Status-to-Code", column_name, f"Resolving codes via {source_column}")
    
    # Respect strategy configuration
    preservation_mode = _get_preservation_mode(engine, column_name)

    def resolve_row_code(val):
        if pd.isna(val):
            return default
        return engine._resolve_schema_reference({
            **reference_config,
            'code': val
        }) or default

    if preservation_mode == "overwrite_existing":
        # Strategy: Calculate for ALL rows
        engine._print_processing_step("Status-to-Code", column_name, f"Strategy: overwrite_existing - resolving all {len(df)} rows")
        df[column_name] = df[source_column].apply(resolve_row_code)
        engine._print_processing_step("Status-to-Code", column_name, f"Applied to all rows (overwritten)")
    else:
        # Strategy: preserve_existing (default) - only resolve null values
        null_mask = df[column_name].isna()
        if null_mask.any():
            df.loc[null_mask, column_name] = df.loc[null_mask, source_column].apply(resolve_row_code)
            engine._print_processing_step("Status-to-Code", column_name, f"Applied to {null_mask.sum()} rows with null values")
        else:
            debug_print(f"Skipped status-to-code for {column_name}: all values already present")

    return df

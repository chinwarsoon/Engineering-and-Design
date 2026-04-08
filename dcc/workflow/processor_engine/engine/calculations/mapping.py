"""
Mapping calculations: status-to-code conversions, value mapping with
external mapping references.
Extracted from UniversalDocumentProcessor._apply_mapping_calculation.
"""

import pandas as pd
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


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
        ref_data = engine.schema_data.get(f'{mapping_ref}_data', {})
        if ref_data:
            # approval_code_schema stores rows under approval[] with
            # {code, status, aliases}. Invert aliases/status to {text: code}.
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
        logger.warning(f"Mapping skipped for {column_name}: source column {source_column} not found.")
        return df

    engine._print_processing_step("Mapping", column_name, f"Mapping from {source_column} ({len(mapping)} mappings)")

    # Only calculate where target is null - preserve existing data
    if column_name not in df.columns:
        df[column_name] = None

    # Create mask for null values in target column
    null_mask = df[column_name].isna()
    if null_mask.any():
        # Only map values where target is null
        mapped_values = df.loc[null_mask, source_column].map(mapping)
        df.loc[null_mask, column_name] = mapped_values.fillna(default)
        logger.info(f"Applied mapping to {null_mask.sum()} rows with null values in {column_name}")
    else:
        logger.info(f"Skipped mapping for {column_name}: all values already present")

    return df


def apply_status_to_code(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Specialized mapping that resolves schema references for codes.
    Often used when the 'mapping' values are stored in an external schema section.
    """
    source_column = calculation.get('source_column')
    reference_config = calculation.get('reference_config')  # e.g., {'schema': 'approval', 'field': 'code'}
    default = calculation.get('default', 'PEN')

    if not source_column or source_column not in df.columns:
        return df

    engine._print_processing_step("Status-to-Code", column_name, f"Resolving codes via {source_column}")

    def resolve_row_code(val):
        if pd.isna(val):
            return default
        # Logic to find the code associated with the status value
        return engine._resolve_schema_reference({
            **reference_config,
            'code': val
        }) or default

    df[column_name] = df[source_column].apply(resolve_row_code)
    return df

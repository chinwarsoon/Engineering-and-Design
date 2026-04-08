"""
Column mapping logic for schema-driven header detection.
Extracted from UniversalColumnMapper detect_columns method.
"""

import logging
from typing import Dict, List, Set, Any
import pandas as pd

from ..matchers.fuzzy import fuzzy_match_column

logger = logging.getLogger(__name__)


def flatten_multiindex_headers(headers: List[Any]) -> List[str]:
    """
    Flatten tuple headers (from MultiIndex Excel loading) to strings.
    
    Args:
        headers: List of headers (may contain tuples from MultiIndex)
        
    Returns:
        List of flattened string headers
    """
    flattened = []
    for h in headers:
        if isinstance(h, tuple):
            flattened_name = '_'.join(str(level) for level in h).strip('_')
            flattened.append(flattened_name)
            logger.warning(f"Flattened tuple header {h} to '{flattened_name}'")
        elif isinstance(h, str):
            flattened.append(h)
        else:
            flattened.append(str(h))
    
    return flattened


def detect_columns(headers: List[str], columns: Dict[str, Dict], threshold: float = 0.6) -> Dict[str, Any]:
    """
    Detect and map input headers to schema columns.
    
    Args:
        headers: List of input headers (already flattened)
        columns: Schema columns dictionary
        threshold: Minimum similarity score for matching
        
    Returns:
        Dictionary with detected_columns, unmatched_headers, missing_required, etc.
    """
    detected = {}
    unmatched = []
    missing_required = []
    
    # Track which schema columns were matched
    matched_column_names: Set[str] = set()
    
    for header in headers:
        best_match = None
        best_score = 0.0
        best_column_name = None

        # Try to match against each column's aliases
        # NOTE: We match ALL columns (including calculated ones) to ensure proper renaming
        # Calculated columns may exist in the input data and need to be renamed to schema names
        for column_name, column_def in columns.items():
            if not isinstance(column_def, dict):
                continue
            aliases = column_def.get('aliases', [])
            match, score = fuzzy_match_column(header, aliases, threshold)

            if score > best_score:
                best_match = match
                best_score = score
                best_column_name = column_name

        if best_score >= threshold:
            detected[header] = {
                'mapped_column': best_column_name,
                'original_header': header,
                'match_score': best_score,
                'matched_alias': best_match,
                'column_definition': columns[best_column_name]
            }
            matched_column_names.add(best_column_name)
        else:
            unmatched.append(header)
    
    # Check for missing required columns (that are NOT calculated)
    for col_name, col_def in columns.items():
        is_required = col_def.get('required', False)
        is_calculated = col_def.get('is_calculated', False)
        if is_required and not is_calculated and col_name not in matched_column_names:
            missing_required.append(col_name)
            logger.warning(f"Required input column missing during mapping detection: {col_name}")
    
    return {
        'detected_columns': detected,
        'unmatched_headers': unmatched,
        'missing_required': missing_required,
        'total_headers': len(headers),
        'matched_count': len(detected),
        'match_rate': len(detected) / len(headers) if len(headers) > 0 else 0
    }


def extract_categorical_choices(detected_columns: Dict[str, Dict], resolved_schema: Dict) -> None:
    """
    Add schema choices for categorical columns in-place.
    
    Args:
        detected_columns: Dictionary of detected column mappings (modified in-place)
        resolved_schema: Resolved schema with all dependencies
    """
    for header, mapping in detected_columns.items():
        col_def = mapping['column_definition']
        if col_def.get('data_type') == 'categorical':
            schema_ref = col_def.get('schema_reference')
            if schema_ref:
                schema_data = resolved_schema.get(f'{schema_ref}_data')
                if schema_data:
                    # Find array key containing code/description objects
                    array_key = None
                    for key in schema_data.keys():
                        if isinstance(schema_data[key], list) and len(schema_data[key]) > 0:
                            if isinstance(schema_data[key][0], dict) and 'code' in schema_data[key][0]:
                                array_key = key
                                break
                    
                    if array_key:
                        # Handle new format: array with code/description objects
                        mapping['choices'] = [item.get('code') for item in schema_data[array_key] if item.get('code')]
                        mapping['choice_descriptions'] = {
                            item.get('code'): item.get('description')
                            for item in schema_data[array_key] if item.get('code')
                        }
                    # Handle old format: choices array
                    elif 'choices' in schema_data:
                        mapping['choices'] = schema_data.get('choices', [])


def rename_dataframe_columns(df: pd.DataFrame, mapping_result: Dict) -> pd.DataFrame:
    """
    Rename DataFrame columns based on detected mapping.
    
    Args:
        df: Input DataFrame with original column names
        mapping_result: Result from detect_columns() method
        
    Returns:
        DataFrame with columns renamed to schema names
    """
    df_renamed = df.copy()
    
    # Flatten MultiIndex/tuple columns if present
    if hasattr(pd, 'MultiIndex') and isinstance(df_renamed.columns, pd.MultiIndex):
        logger.warning("Flattening MultiIndex columns in rename_dataframe_columns")
        df_renamed.columns = ['_'.join(str(level) for level in levels).strip('_')
                              for levels in df_renamed.columns]
    elif len(df_renamed.columns) > 0 and isinstance(df_renamed.columns[0], tuple):
        logger.warning("Flattening tuple columns in rename_dataframe_columns")
        df_renamed.columns = ['_'.join(str(level) for level in levels).strip('_')
                              for levels in df_renamed.columns]
    
    # Create rename mapping
    rename_dict = {}
    for header, mapping in mapping_result['detected_columns'].items():
        schema_column = mapping['mapped_column']
        if header in df_renamed.columns:
            rename_dict[header] = schema_column

    # Apply renaming
    df_renamed = df_renamed.rename(columns=rename_dict)

    # Remove duplicate columns (keep first occurrence)
    # This can happen when multiple Excel headers map to the same schema column
    duplicate_mask = df_renamed.columns.duplicated(keep='first')
    if duplicate_mask.any():
        duplicate_cols = df_renamed.columns[duplicate_mask].tolist()
        logger.warning(f"Removing {len(duplicate_cols)} duplicate columns after rename: {duplicate_cols}")
        df_renamed = df_renamed.loc[:, ~df_renamed.columns.duplicated(keep='first')]

    logger.info(f"Renamed {len(rename_dict)} columns to schema names")
    logger.info(f"Final DataFrame: {len(df_renamed)} rows × {len(df_renamed.columns)} columns")

    return df_renamed

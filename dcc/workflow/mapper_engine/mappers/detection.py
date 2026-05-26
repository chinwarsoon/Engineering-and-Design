"""
Column mapping logic for schema-driven header detection.
Extracted from UniversalColumnMapper detect_columns method.
"""

import logging
from typing import Dict, List, Set, Any
import pandas as pd

from ..matchers.fuzzy import fuzzy_match_column

# Import hierarchical logging functions from utility_engine
from utility_engine.console import status_print, debug_print


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
            status_print("WARNING_FLATTEN_TUPLE", raw=h, name=flattened_name)
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
            status_print("WARNING_MISSING_REQUIRED", name=col_name)
    
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

    Reads reference data from the schema's top-level lists (e.g. resolved_schema['approval_codes']).
    The mapping from schema_reference name to top-level key is read from the schema's own
    'schema_reference_map' section when present, with a built-in fallback for standard DCC schemas.

    Args:
        detected_columns: Dictionary of detected column mappings (modified in-place).
                          Breadcrumb: mapper_engine.detect_columns() → here.
        resolved_schema: Resolved schema with all dependencies.
    """
    # Prefer schema-driven reference map; fall back to built-in defaults
    ref_key_map: Dict[str, str] = resolved_schema.get('schema_reference_map', {
        'approval_code_schema': 'approval_codes',
        'department_schema':    'departments',
        'discipline_schema':    'disciplines',
        'facility_schema':      'facilities',
        'document_type_schema': 'document_types',
        'project_code_schema':  'projects',
    })

    for header, mapping in detected_columns.items():
        col_def = mapping['column_definition']
        if col_def.get('data_type') != 'categorical':
            continue

        schema_ref = col_def.get('schema_reference')
        if not schema_ref:
            continue

        top_key = ref_key_map.get(schema_ref)
        if not top_key:
            continue

        entries = resolved_schema.get(top_key)
        if not isinstance(entries, list):
            continue

        # Facilities use 'prefix' as the code field; all others use 'code'
        code_field = 'prefix' if schema_ref == 'facility_schema' else 'code'
        mapping['choices'] = [
            item.get(code_field) for item in entries
            if isinstance(item, dict) and item.get(code_field)
        ]
        mapping['choice_descriptions'] = {
            item.get(code_field): item.get('description', item.get('building_description', ''))
            for item in entries
            if isinstance(item, dict) and item.get(code_field)
        }


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
        status_print("WARNING_FLATTEN_MULTIINDEX")
        df_renamed.columns = ['_'.join(str(level) for level in levels).strip('_')
                              for levels in df_renamed.columns]
    elif len(df_renamed.columns) > 0 and isinstance(df_renamed.columns[0], tuple):
        status_print("WARNING_FLATTEN_TUPLE_RENAME")
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
        status_print("WARNING_REMOVE_DUP_COLS", count=len(duplicate_cols), names=duplicate_cols)
        df_renamed = df_renamed.loc[:, ~df_renamed.columns.duplicated(keep='first')]

    status_print("STATUS_RENAMED_COLS", count=len(rename_dict))
    status_print("STATUS_FINAL_DF_SHAPE", rows=len(df_renamed), cols=len(df_renamed.columns))

    return df_renamed

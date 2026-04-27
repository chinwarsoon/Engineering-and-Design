"""
Null handling strategies for the document processor engine.
Extracted from UniversalDocumentProcessor null handling methods.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List

from utility_engine.console import status_print, debug_print


def _get_row_key(df: pd.DataFrame, idx: int) -> Dict[str, Any]:
    """
    Generate a stable row key for tracking purposes.
    Uses Document_ID and Submission_Date if available, falls back to index.
    """
    row_key = {'row_index': idx}
    
    if 'Document_ID' in df.columns and idx < len(df):
        row_key['Document_ID'] = str(df.iloc[idx].get('Document_ID', ''))
    
    if 'Submission_Date' in df.columns and idx < len(df):
        submission_date = df.iloc[idx].get('Submission_Date', '')
        if pd.notna(submission_date):
            row_key['Submission_Date'] = str(submission_date)
    
    if 'Submission_Session' in df.columns and idx < len(df):
        session = df.iloc[idx].get('Submission_Session', '')
        if pd.notna(session):
            row_key['Submission_Session'] = str(session)
    
    return row_key


def _record_fill_history(
    engine,
    operation_type: str,
    column: str,
    df: pd.DataFrame,
    filled_indices: List[int],
    group_by: List[str] = None,
    fill_value: Any = None,
    levels_applied: int = None,
    all_levels_failed: bool = False,
    default_applied: bool = False
):
    """
    Record fill operation to engine.fill_history for error detection.
    
    Args:
        engine: The processing engine with fill_history attribute
        operation_type: Type of fill (forward_fill, multi_level_fill, default_value, etc.)
        column: Target column being filled
        df: DataFrame for row key extraction
        filled_indices: List of row indices that were filled
        group_by: Grouping columns used (if any)
        fill_value: The value used to fill
        levels_applied: Number of levels tried (for multi-level fill)
        all_levels_failed: Whether all levels failed to find a value
        default_applied: Whether a default value was applied
    """
    # Initialize fill_history if not exists
    if not hasattr(engine, 'fill_history'):
        engine.fill_history = []
    
    if not filled_indices:
        return
    
    # Group consecutive filled indices to detect row jumps
    from_idx = None
    to_idx = None
    prev_idx = None
    
    for idx in sorted(filled_indices):
        if from_idx is None:
            from_idx = idx
            to_idx = idx
        elif idx == prev_idx + 1:
            # Consecutive - extend range
            to_idx = idx
        else:
            # Gap detected - record previous range and start new
            row_jump = to_idx - from_idx if to_idx > from_idx else 0
            
            # Check for session boundary crossing
            session_boundary_crossed = False
            source_session = None
            target_session = None
            
            if group_by and 'Submission_Session' in group_by:
                # With group_by, we don't cross sessions
                session_boundary_crossed = False
            elif from_idx < len(df) and to_idx < len(df):
                if 'Submission_Session' in df.columns:
                    source_session = str(df.iloc[from_idx].get('Submission_Session', ''))
                    target_session = str(df.iloc[to_idx].get('Submission_Session', ''))
                    session_boundary_crossed = source_session != target_session and source_session and target_session
            
            # Get row keys
            from_row_key = _get_row_key(df, from_idx)
            to_row_key = _get_row_key(df, to_idx)
            
            # Determine filled value for this range
            actual_fill_value = fill_value
            if to_idx < len(df) and column in df.columns:
                actual_fill_value = df.iloc[to_idx].get(column, fill_value)
            
            fill_record = {
                'operation_type': operation_type,
                'column': column,
                'from_row': from_row_key,
                'to_row': to_row_key,
                'row_jump': row_jump,
                'group_by': group_by or [],
                'filled_value': actual_fill_value,
                'session_boundary_crossed': session_boundary_crossed,
                'source_session': source_session,
                'target_session': target_session,
                'levels_applied': levels_applied,
                'all_levels_failed': all_levels_failed,
                'default_applied': default_applied,
                'timestamp': pd.Timestamp.now().isoformat()
            }
            
            engine.fill_history.append(fill_record)
            
            # Start new range
            from_idx = idx
            to_idx = idx
        
        prev_idx = idx
    
    # Record the last range
    if from_idx is not None:
        row_jump = to_idx - from_idx if to_idx > from_idx else 0
        
        # Check for session boundary crossing
        session_boundary_crossed = False
        source_session = None
        target_session = None
        
        if group_by and 'Submission_Session' in group_by:
            session_boundary_crossed = False
        elif from_idx < len(df) and to_idx < len(df):
            if 'Submission_Session' in df.columns:
                source_session = str(df.iloc[from_idx].get('Submission_Session', ''))
                target_session = str(df.iloc[to_idx].get('Submission_Session', ''))
                session_boundary_crossed = source_session != target_session and source_session and target_session
        
        from_row_key = _get_row_key(df, from_idx)
        to_row_key = _get_row_key(df, to_idx)
        
        actual_fill_value = fill_value
        if to_idx < len(df) and column in df.columns:
            actual_fill_value = df.iloc[to_idx].get(column, fill_value)
        
        fill_record = {
            'operation_type': operation_type,
            'column': column,
            'from_row': from_row_key,
            'to_row': to_row_key,
            'row_jump': row_jump,
            'group_by': group_by or [],
            'filled_value': actual_fill_value,
            'session_boundary_crossed': session_boundary_crossed,
            'source_session': source_session,
            'target_session': target_session,
            'levels_applied': levels_applied,
            'all_levels_failed': all_levels_failed,
            'default_applied': default_applied,
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        engine.fill_history.append(fill_record)


def apply_forward_fill(engine, df: pd.DataFrame, column_name: str, null_handling: Dict) -> pd.DataFrame:
    """
    Apply forward fill strategy - fills null values with the last non-null value.
    Supports group-based filling and zero-padding formatting.
    """
    group_by = null_handling.get('group_by', [])

    # Defensive check: ensure column_name is a string, not a tuple
    if not isinstance(column_name, str):
        debug_print(f"Invalid column_name type: {type(column_name)} - {column_name}")
        column_name = str(column_name) if isinstance(column_name, tuple) else column_name

    # Resolve fill_value from schema reference if specified
    fill_value_ref = null_handling.get('fill_value_reference')
    if fill_value_ref:
        fill_value = engine._resolve_schema_reference(fill_value_ref)
        if fill_value is None:
            fill_value = null_handling.get('fill_value', 'NA')
    else:
        fill_value = null_handling.get('fill_value', 'NA')

    na_fallback = null_handling.get('na_fallback', False)
    formatting = null_handling.get('formatting', {})
    zero_pad = formatting.get('zero_pad')

    # Validate that column exists in DataFrame
    if column_name not in df.columns:
        debug_print(f"Column '{column_name}' not found in DataFrame. Available columns: {list(df.columns)[:10]}...")
        return df

    # FIX: Always work on a local copy; never mutate the caller's DataFrame.
    df_copy = df.reset_index(drop=True).copy() if not isinstance(df.index, pd.RangeIndex) else df.copy()

    # Remove duplicate columns which cause df[col] to return a DataFrame
    if df_copy.columns.tolist().count(column_name) > 1:
        debug_print(f"DUPLICATE COLUMNS DETECTED: '{column_name}' appears {df_copy.columns.tolist().count(column_name)} times! Removing duplicates.")
        df_copy = df_copy.loc[:, ~df_copy.columns.duplicated()].copy()
        df_copy.index = pd.RangeIndex(len(df_copy))

    # Track which rows had nulls before fill (for history tracking)
    null_mask_before = df_copy[column_name].isna()
    
    if group_by:
        # Validate group_by columns exist
        valid_group_by = [col for col in group_by if col in df_copy.columns]
        if not valid_group_by:
            debug_print(f"None of the group_by columns {group_by} found in DataFrame. Skipping forward fill for {column_name}.")
            return df_copy

        # Cast group keys to str so NaN group keys don't silently split groups
        for col in valid_group_by:
            df_copy[col] = df_copy[col].astype(str)

        # FIX: assign ffill result directly - no mask+.values juggling.
        df_copy[column_name] = df_copy.groupby(valid_group_by, sort=False)[column_name].ffill()
        # Apply fill_value for any remaining NaN (groups that started with null)
        df_copy[column_name] = df_copy[column_name].fillna(fill_value)
    else:
        # FIX: assign ffill result directly - no mask+.values juggling.
        df_copy[column_name] = df_copy[column_name].ffill()
        # Apply fill_value for any remaining NaN at start of series
        df_copy[column_name] = df_copy[column_name].fillna(fill_value)
    
    # Track filled rows for error detection (Phase A: Fill History Tracking)
    null_mask_after = df_copy[column_name].isna()
    filled_mask = null_mask_before & ~null_mask_after
    filled_indices = df_copy[filled_mask].index.tolist()
    
    if filled_indices:
        _record_fill_history(
            engine=engine,
            operation_type='forward_fill',
            column=column_name,
            df=df_copy,
            filled_indices=filled_indices,
            group_by=group_by,
            fill_value=fill_value
        )

    if na_fallback:
        # Replace remaining NaN with 'NA' if fill_value was NaN
        df_copy[column_name] = df_copy[column_name].fillna('NA')

    # Apply zero-padding formatting if specified
    if zero_pad:
        try:
            df_copy[column_name] = df_copy[column_name].apply(
                lambda x: str(int(float(x))).zfill(zero_pad) if pd.notna(x) and x != 'NA' else x
            )
            debug_print(f"Applied zero-padding ({zero_pad} digits) for {column_name}")
        except Exception as e:
            debug_print(f"Could not apply zero-padding for {column_name}: {e}")

    debug_print(f"Applied forward fill for '{column_name}': group_by={group_by}")
    return df_copy


def apply_multi_level_forward_fill(engine, df: pd.DataFrame, column_name: str, null_handling: Dict) -> pd.DataFrame:
    """
    Apply multi-level forward fill strategy.
    Processes multiple grouping levels in sequence.
    """
    levels = null_handling.get('levels', [])
    final_fill = null_handling.get('final_fill')
    datetime_conversion = null_handling.get('datetime_conversion', {})

    # FIX: work on a single copy throughout; never write back into input df
    df_copy = df.copy()

    # Track which rows had nulls before fill
    null_mask_before = df_copy[column_name].isna()
    levels_applied = 0
    last_group_by = []

    # Optionally perform datetime conversion beforehand
    if datetime_conversion and column_name in df_copy.columns:
        errors = datetime_conversion.get('errors', 'coerce')
        df_copy[column_name] = pd.to_datetime(df_copy[column_name], errors=errors)

    for level in levels:
        group_by = level.get('group_by', [])
        if group_by:
            for col in group_by:
                if col in df_copy.columns:
                    df_copy[col] = df_copy[col].astype(str)

            # FIX: assign ffill result directly - no mask+.values juggling.
            df_copy[column_name] = df_copy.groupby(group_by, sort=False)[column_name].ffill()
            levels_applied += 1
            last_group_by = group_by

    # Check if final_fill was applied (all levels failed to fill remaining nulls)
    null_mask_after_levels = df_copy[column_name].isna()
    all_levels_failed = null_mask_after_levels.any()
    
    if final_fill is not None and column_name in df_copy.columns:
        df_copy[column_name] = df_copy[column_name].fillna(final_fill)
    
    # Track filled rows for error detection
    null_mask_after = df_copy[column_name].isna()
    filled_mask = null_mask_before & ~null_mask_after
    filled_indices = df_copy[filled_mask].index.tolist()
    
    if filled_indices:
        _record_fill_history(
            engine=engine,
            operation_type='multi_level_forward_fill',
            column=column_name,
            df=df_copy,
            filled_indices=filled_indices,
            group_by=last_group_by,
            fill_value=final_fill,
            levels_applied=levels_applied,
            all_levels_failed=all_levels_failed,
            default_applied=all_levels_failed and final_fill is not None
        )

    debug_print(f"Applied multi_level_forward_fill for {column_name}: levels={levels_applied}, final_fill_applied={all_levels_failed}")
    return df_copy


def apply_copy_from(engine, df: pd.DataFrame, column_name: str, null_handling: Dict) -> pd.DataFrame:
    """
    Apply copy from strategy.
    Copies values from a source column where the target column is null.
    """
    source_column = null_handling.get('source_column')
    fallback_value = null_handling.get('fallback_value', 'NA')

    # FIX: guard against missing or unconfigured source_column
    if not source_column:
        debug_print(f"_apply_copy_from: 'source_column' not specified in null_handling for '{column_name}'. Skipping.")
        return df
    if source_column not in df.columns:
        debug_print(f"_apply_copy_from: source column '{source_column}' not found in DataFrame for '{column_name}'. Skipping.")
        return df

    df = df.copy()

    # Copy from source column where target is null
    mask = df[column_name].isna()
    df.loc[mask, column_name] = df.loc[mask, source_column]

    # Apply fallback for remaining null values
    df[column_name] = df[column_name].fillna(fallback_value)

    debug_print(f"Applied copy from for {column_name}: source={source_column}, fallback={fallback_value}")
    return df


def apply_calculate_if_null(engine, df: pd.DataFrame, column_name: str, null_handling: Dict) -> pd.DataFrame:
    """
    Apply calculate if null strategy.

    Note: This method is deprecated for columns with is_calculated=true.
    Use null_handling.strategy: leave_null instead for calculated columns.
    Currently only handles legacy date_calculation and conditional calculations.
    """
    calculation = null_handling.get('calculation', {})
    calc_type = calculation.get('type')
    method = calculation.get('method')

    if calc_type == 'date_calculation' and method == 'add_working_days':
        df = _calculate_working_days(engine, df, column_name, calculation)
    elif calc_type == 'conditional' and method == 'status_based':
        df = _apply_conditional_calculation(engine, df, column_name, calculation)
    else:
        debug_print(
            f"Unsupported calculation type in calculate_if_null: {calc_type}/{method} for {column_name}. "
            f"Use is_calculated:true with appropriate calculation type instead."
        )

    return df


def _calculate_working_days(engine, df: pd.DataFrame, column_name: str, calculation: Dict) -> pd.DataFrame:
    """Calculate working days between dates."""
    source_column = calculation.get('source_column')
    parameters = calculation.get('parameters', {})
    days = parameters.get('days', 14)

    df = df.copy()

    # Convert date columns to datetime
    if source_column in df.columns:
        df[source_column] = pd.to_datetime(df[source_column], errors='coerce')

    # Calculate target date
    if column_name in df.columns:
        df[column_name] = pd.to_datetime(df[column_name], errors='coerce')

    # Add working days
    mask = df[column_name].notna() & df[source_column].notna()
    df.loc[mask, column_name] = df.loc[mask, source_column] + pd.Timedelta(days=days)

    debug_print(f"Calculated working days for {column_name}: +{days} days from {source_column}")
    return df


def _apply_conditional_calculation(engine, df: pd.DataFrame, column_name: str, calculation: Dict) -> pd.DataFrame:
    """Apply conditional calculation based on another column."""
    source_column = calculation.get('source_column')
    mapping = calculation.get('mapping', {})
    default_value = calculation.get('default', False)

    df = df.copy()

    if source_column in df.columns and column_name in df.columns:
        mask = df[column_name].isna()
        for value, result in mapping.items():
            df.loc[mask & (df[source_column] == value), column_name] = result

        # Apply default for remaining null values
        df[column_name] = df[column_name].fillna(default_value)

    debug_print(f"Applied conditional calculation for {column_name}: based on {source_column}")
    return df


def apply_default_value(engine, df: pd.DataFrame, column_name: str, null_handling: Dict) -> pd.DataFrame:
    """
    Apply default value strategy with formatting support.
    Handles text replacements, type conversion, and zero-padding.
    """
    default_value = null_handling.get('default_value', null_handling.get('default', 'NA'))
    text_replacements = null_handling.get('text_replacements', {})
    type_conversion = null_handling.get('type_conversion')
    formatting = null_handling.get('formatting', {})
    zero_pad = formatting.get('zero_pad')

    df = df.copy()

    # Track which rows had nulls before applying default
    null_mask_before = df[column_name].isna() if column_name in df.columns else pd.Series([False] * len(df), index=df.index)

    # FIX: Apply text replacements only on non-null values to avoid converting NaN
    # to the string "nan" which then escapes fillna() downstream.
    if text_replacements and column_name in df.columns:
        for old_text, new_text in text_replacements.items():
            # Exact-value replacement (non-destructive for NaN)
            df[column_name] = df[column_name].replace(old_text, new_text)
            # Substring replacement only on rows that are not null
            not_null_mask = df[column_name].notna()
            if not_null_mask.any():
                df.loc[not_null_mask, column_name] = (
                    df.loc[not_null_mask, column_name]
                    .astype(str)
                    .str.replace(old_text, new_text, regex=False)
                )

    # Apply type conversion if specified
    if type_conversion == 'string' and column_name in df.columns:
        # Convert only non-null values to string; leave nulls as pd.NA
        not_null_mask = df[column_name].notna()
        df[column_name] = df[column_name].where(~not_null_mask, df[column_name].astype(str))
        # Clean up any residual "nan" strings that may have slipped through
        df[column_name] = df[column_name].replace({'nan': pd.NA, 'NaN': pd.NA})

    # Fill null values with default
    if column_name in df.columns:
        df[column_name] = df[column_name].fillna(default_value)
    
    # Track which rows received the default value
    null_mask_after = df[column_name].isna() if column_name in df.columns else pd.Series([False] * len(df), index=df.index)
    filled_mask = null_mask_before & ~null_mask_after
    filled_indices = df[filled_mask].index.tolist()
    
    if filled_indices:
        _record_fill_history(
            engine=engine,
            operation_type='default_value',
            column=column_name,
            df=df,
            filled_indices=filled_indices,
            group_by=[],
            fill_value=default_value,
            default_applied=True
        )

    # Apply zero-padding formatting if specified
    if zero_pad and column_name in df.columns:
        try:
            def pad_if_numeric(x):
                if pd.isna(x) or x == 'NA':
                    return x
                # Try to convert to int and pad
                try:
                    num = int(float(str(x)))
                    return str(num).zfill(zero_pad)
                except (ValueError, TypeError):
                    # Not a number, return as-is
                    return x

            df[column_name] = df[column_name].apply(pad_if_numeric)
            debug_print(f"Applied zero-padding ({zero_pad} digits) for {column_name}")
        except Exception as e:
            debug_print(f"Could not apply zero-padding for {column_name}: {e}")

    debug_print(f"Applied default value for {column_name}: {default_value}")
    return df


def apply_lookup_if_null(engine, df: pd.DataFrame, column_name: str, null_handling: Dict) -> pd.DataFrame:
    """
    Apply lookup strategy for null values.
    Looks up values from grouped data based on a lookup key.
    """
    calculation = null_handling.get('calculation', {})
    lookup_key = calculation.get('lookup_key')
    source_column = calculation.get('source_column')
    fallback_value = calculation.get('fallback_value', 'NA')

    df = df.copy()

    if lookup_key and source_column and column_name in df.columns:
        mask = df[column_name].isna()

        # Group by lookup key and find first non-null value
        grouped = df.groupby(lookup_key, dropna=False)
        for key, group in grouped:
            # FIX: use .iloc[0] instead of .loc[non_null_mask.idxmax()] to safely get
            # the first non-null value regardless of the DataFrame index type.
            non_null_mask = group[source_column].notna()
            if non_null_mask.any():
                first_value = group.loc[non_null_mask, source_column].iloc[0]
                df.loc[mask & (df[lookup_key] == key), column_name] = first_value

        # Apply fallback for remaining null values
        df[column_name] = df[column_name].fillna(fallback_value)

    debug_print(f"Applied lookup if null for {column_name}: lookup_key={lookup_key}")
    return df

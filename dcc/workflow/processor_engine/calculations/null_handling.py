"""
Null handling strategies for the document processor engine.
Extracted from UniversalDocumentProcessor null handling methods.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List

from utility_engine.console import status_print, debug_print


def _get_row_key(engine, df: pd.DataFrame, idx: int) -> Dict[str, Any]:
    """
    Generate a stable row key for tracking purposes.
    Uses columns marked as is_row_key in schema if available.
    """
    row_key = {'row_index': idx}
    
    # Task A5: Read key columns from schema is_row_key: true flag
    if hasattr(engine, 'columns'):
        key_cols = [name for name, defn in engine.columns.items() if defn.get('is_row_key')]
        if key_cols:
            for col in key_cols:
                if col in df.columns and idx < len(df):
                    val = df.iloc[idx].get(col, '')
                    if pd.notna(val):
                        row_key[col] = str(val)
            return row_key
            
    # Fallback to legacy hardcoded keys if engine/schema not available
    legacy_keys = ['Document_ID', 'Submission_Date', 'Submission_Session']
    for col in legacy_keys:
        if col in df.columns and idx < len(df):
            val = df.iloc[idx].get(col, '')
            if pd.notna(val):
                row_key[col] = str(val)
    
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
    Optimized to handle large numbers of filled indices efficiently.
    """
    debug_print(f"[FILL-HISTORY] Recording fill for {column}, operation: {operation_type}, rows affected: {len(filled_indices)}")
    
    # Initialize fill_history if not exists
    if not hasattr(engine, 'fill_history'):
        engine.fill_history = []
    
    if not filled_indices:
        debug_print(f"[FILL-HISTORY] No filled indices, returning early")
        return
    
    # OPTIMIZATION: For large fills (>5000 rows), use a simplified history record
    # to avoid expensive sorting and iteration
    if len(filled_indices) > 5000:
        debug_print(f"[FILL-HISTORY] Large fill detected ({len(filled_indices)} rows), using simplified record")
        # Just record the range without iterating through all indices
        try:
            first_idx = filled_indices[0]
            last_idx = filled_indices[-1]
        except (IndexError, TypeError):
            debug_print(f"[FILL-HISTORY] Could not extract first/last index, aborting record")
            return
        
        row_jump = last_idx - first_idx if last_idx > first_idx else 0
        
        fill_record = {
            'operation_type': operation_type,
            'column': column,
            'from_row': {'row_index': first_idx},
            'to_row': {'row_index': last_idx},
            'row_jump': row_jump,
            'group_by': group_by or [],
            'filled_value': fill_value,
            'session_boundary_crossed': False,
            'source_session': None,
            'target_session': None,
            'levels_applied': levels_applied,
            'all_levels_failed': all_levels_failed,
            'default_applied': default_applied,
            'timestamp': pd.Timestamp.now().isoformat(),
            '_optimization_note': f'Large fill: {len(filled_indices)} rows, simplified record used'
        }
        
        engine.fill_history.append(fill_record)
        debug_print(f"[FILL-HISTORY] Recorded simplified history for {len(filled_indices)} rows")
        return
    
    # Original logic for smaller fills
    debug_print(f"[FILL-HISTORY] Processing {len(filled_indices)} indices with detailed tracking")
    
    # Group consecutive filled indices to detect row jumps
    from_idx = None
    to_idx = None
    prev_idx = None
    
    try:
        debug_print(f"[FILL-HISTORY] Sorting {len(filled_indices)} indices...")
        sorted_indices = sorted(filled_indices, key=lambda x: int(x) if not isinstance(x, int) else x)
        debug_print(f"[FILL-HISTORY] Sorted successfully, processing...")
    except Exception as e:
        debug_print(f"[FILL-HISTORY] Error during sorting: {e}, aborting detailed record")
        # Fallback to simple range record
        try:
            fill_record = {
                'operation_type': operation_type,
                'column': column,
                'group_by': group_by or [],
                'filled_value': fill_value,
                'levels_applied': levels_applied,
                'all_levels_failed': all_levels_failed,
                'default_applied': default_applied,
                'timestamp': pd.Timestamp.now().isoformat(),
                '_error_note': f'Could not sort indices: {str(e)}'
            }
            engine.fill_history.append(fill_record)
        except:
            pass
        return
    
    for idx in sorted_indices:
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
                session_boundary_crossed = False
            elif from_idx < len(df) and to_idx < len(df):
                if 'Submission_Session' in df.columns:
                    source_session = str(df.iloc[from_idx].get('Submission_Session', ''))
                    target_session = str(df.iloc[to_idx].get('Submission_Session', ''))
                    session_boundary_crossed = source_session != target_session and source_session and target_session
            
            # Get row keys
            from_row_key = _get_row_key(engine, df, from_idx)
            to_row_key = _get_row_key(engine, df, to_idx)
            
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
        
        from_row_key = _get_row_key(engine, df, from_idx)
        to_row_key = _get_row_key(engine, df, to_idx)
        
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
        debug_print(f"Column '{column_name}' not found in DataFrame.")
        return df

    # Work on a local copy; never mutate the caller's DataFrame.
    df_copy = df.copy()

    # Track which rows had nulls before fill
    null_mask_before = df_copy[column_name].isna()
    
    if group_by:
        # Validate group_by columns exist
        valid_group_by = [col for col in group_by if col in df_copy.columns]
        if not valid_group_by:
            debug_print(f"None of the group_by columns {group_by} found. Skipping forward fill.")
            return df_copy

        # Cast group keys to str
        for col in valid_group_by:
            df_copy[col] = df_copy[col].astype(str)

        df_copy[column_name] = df_copy.groupby(valid_group_by, sort=False)[column_name].ffill()
        df_copy[column_name] = df_copy[column_name].fillna(fill_value)
    else:
        df_copy[column_name] = df_copy[column_name].ffill()
        df_copy[column_name] = df_copy[column_name].fillna(fill_value)
    
    # Track filled rows for history
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
        df_copy[column_name] = df_copy[column_name].fillna('NA')

    # Apply zero-padding formatting
    if zero_pad:
        try:
            df_copy[column_name] = df_copy[column_name].apply(
                lambda x: str(int(float(x))).zfill(zero_pad) if pd.notna(x) and x != 'NA' else x
            )
        except Exception:
            pass

    return df_copy


def apply_multi_level_forward_fill(engine, df: pd.DataFrame, column_name: str, null_handling: Dict) -> pd.DataFrame:
    """
    Apply multi-level forward fill strategy.
    Tries multiple grouping levels sequentially until a value is found.
    """
    levels = null_handling.get('levels', [])
    fallback_value = null_handling.get('fill_value', 'NA')

    df_copy = df.copy()

    # Track indices that were originally null
    original_null_mask = df_copy[column_name].isna()
    original_null_indices = df_copy[original_null_mask].index.tolist()
    
    if not original_null_indices:
        return df_copy

    # Keep track of which rows were filled at which level
    filled_status = {idx: None for idx in original_null_indices}

    for i, level in enumerate(levels):
        group_by = level.get('group_by', [])
        available_group_by = [c for c in group_by if c in df_copy.columns]
        
        if not available_group_by:
            continue

        # For rows still null, try filling at this level
        current_null_mask = df_copy[column_name].isna()
        if not current_null_mask.any():
            break
            
        # Group-based ffill
        df_copy[column_name] = df_copy.groupby(available_group_by, group_keys=False)[column_name].ffill()
        
        # Mark rows filled at this level
        now_filled_mask = original_null_mask & df_copy[column_name].notna()
        for idx in df_copy[now_filled_mask].index:
            if filled_status[idx] is None:
                filled_status[idx] = i + 1

    # Record history by grouping indices by level
    for level_idx in range(1, len(levels) + 1):
        level_indices = [idx for idx, lvl in filled_status.items() if lvl == level_idx]
        if level_indices:
            _record_fill_history(
                engine, 
                "multi_level_fill", 
                column_name, 
                df_copy, 
                level_indices, 
                group_by=levels[level_idx-1].get('group_by'),
                levels_applied=level_idx
            )

    # Final fallback for remaining nulls
    remaining_null_mask = df_copy[column_name].isna()
    remaining_null_indices = df_copy[remaining_null_mask].index.tolist()
    if remaining_null_indices:
        df_copy[column_name] = df_copy[column_name].fillna(fallback_value)
        _record_fill_history(
            engine, 
            "multi_level_fill_fallback", 
            column_name, 
            df_copy, 
            remaining_null_indices, 
            fill_value=fallback_value,
            all_levels_failed=True,
            default_applied=True
        )

    return df_copy


def apply_copy_from(engine, df: pd.DataFrame, column_name: str, null_handling: Dict) -> pd.DataFrame:
    """
    Apply copy strategy: fills null values with values from another column.
    """
    source_column = null_handling.get('source_column')
    fallback_value = null_handling.get('fill_value', 'NA')

    if not source_column or source_column not in df.columns:
        return df

    df_copy = df.copy()

    # Track which rows had nulls
    null_mask_before = df_copy[column_name].isna()

    # Copy from source column where target is null
    df_copy[column_name] = df_copy[column_name].fillna(df_copy[source_column])
    
    # Record history
    null_mask_after = df_copy[column_name].isna()
    filled_indices = df_copy[null_mask_before & ~null_mask_after].index.tolist()
    if filled_indices:
        _record_fill_history(engine, "copy_from", column_name, df_copy, filled_indices, fill_value=f"from:{source_column}")

    # Apply fallback for remaining null values
    df_copy[column_name] = df_copy[column_name].fillna(fallback_value)

    return df_copy


def apply_calculate_if_null(engine, df: pd.DataFrame, column_name: str, null_handling: Dict) -> pd.DataFrame:
    """
    Apply calculate if null strategy. (Legacy/Deprecated)
    """
    calculation = null_handling.get('calculation', {})
    calc_type = calculation.get('type')
    
    if calc_type == 'date_calculation':
        from .date import calculate_working_days
        return calculate_working_days(engine, df, column_name, calculation)
    
    debug_print(f"Unsupported calculation type in calculate_if_null: {calc_type} for {column_name}")
    return df


def apply_default_value(engine, df: pd.DataFrame, column_name: str, null_handling: Dict) -> pd.DataFrame:
    """
    Apply simple default value to nulls.
    """
    default_value = null_handling.get('fill_value', 'NA')
    
    df_copy = df.copy()
    if column_name not in df_copy.columns:
        df_copy[column_name] = None
        
    null_indices = df_copy[df_copy[column_name].isna()].index.tolist()
    if null_indices:
        df_copy[column_name] = df_copy[column_name].fillna(default_value)
        _record_fill_history(engine, "default_value", column_name, df_copy, null_indices, fill_value=default_value, default_applied=True)
        
    return df_copy


def apply_lookup_if_null(engine, df: pd.DataFrame, column_name: str, null_handling: Dict) -> pd.DataFrame:
    """
    Apply lookup strategy for null values.
    """
    calculation = null_handling.get('calculation', {})
    lookup_key = calculation.get('lookup_key')
    source_column = calculation.get('source_column')
    fallback_value = calculation.get('fill_value', 'NA')

    df_copy = df.copy()
    if column_name not in df_copy.columns:
        df_copy[column_name] = None

    if lookup_key and source_column and source_column in df_copy.columns:
        null_mask = df_copy[column_name].isna()
        if null_mask.any():
            # Simple Document_ID based lookup
            first_value = df_copy.groupby(lookup_key)[column_name].transform('first')
            df_copy[column_name] = df_copy[column_name].fillna(first_value)
            
            # Record history
            now_filled_mask = null_mask & df_copy[column_name].notna()
            filled_indices = df_copy[now_filled_mask].index.tolist()
            if filled_indices:
                 _record_fill_history(engine, "lookup_if_null", column_name, df_copy, filled_indices, group_by=[lookup_key])
        
        # Apply fallback
        df_copy[column_name] = df_copy[column_name].fillna(fallback_value)

    return df_copy

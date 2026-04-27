"""
Aggregate calculations: standard grouping/aggregation, latest-by-date,
latest non-pending status, concatenate unique values, and date concatenation.
Extracted from UniversalDocumentProcessor._apply_aggregate_calculation and related methods.
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, Any, List

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


def apply_aggregate_calculation(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Performs standard grouping and aggregation (Min, Max, Sum, Count, Concatenate, etc.)
    """
    # Support both singular and plural source columns
    source_column = calculation.get('source_column')
    source_columns = calculation.get('source_columns', [])
    
    # If source_columns is provided but not source_column, use the first one as primary
    # (for methods that only support one) or all of them for concatenation
    if not source_column and source_columns:
        source_column = source_columns[0]
        
    method = calculation.get('method')
    group_by = calculation.get('group_by', [])
    sort_by = calculation.get('sort_by', [])
    separator = calculation.get('separator', ', ')

    if not source_column or source_column not in df.columns or not group_by:
        # Check if we have multiple valid source columns for concatenation
        if method not in ['concatenate_unique', 'concatenate_unique_quoted'] or not source_columns:
            return df
        
        # Ensure at least one source column exists
        valid_sources = [c for c in source_columns if c in df.columns]
        if not valid_sources:
            return df
        # Use first valid source as anchor for transformation
        source_column = valid_sources[0]

    engine._print_processing_step("Aggregate", column_name, f"{method} of {source_column if not source_columns else source_columns} grouped by {group_by}")

    # Initialize column if not exists
    if column_name not in df.columns:
        df[column_name] = None

    # Respect strategy configuration
    preservation_mode = _get_preservation_mode(engine, column_name)
    
    # Determine which rows to calculate for
    if preservation_mode == "overwrite_existing":
        # Calculate for all rows
        engine._print_processing_step("Aggregate", column_name, f"Strategy: overwrite_existing - calculating all rows")
        null_mask = pd.Series([True] * len(df), index=df.index)  # All rows
    else:
        # Calculate only for null values (default)
        existing_mask = df[column_name].notna()
        if existing_mask.any():
            engine._print_processing_step("Aggregate", column_name, f"Preserving {existing_mask.sum()} existing values")
        
        null_mask = df[column_name].isna()
        if not null_mask.any():
            debug_print(f"Skipped aggregate for {column_name}: all values present")
            return df

    # Calculate for target rows
    grouped = df.groupby(group_by, dropna=False)

    col_def = engine.columns.get(column_name, {})
    is_json = col_def.get('data_type') == 'json' or col_def.get('column_type') == 'json_column'

    if method == 'count':
        calculated = grouped[source_column].transform('count')
        df.loc[null_mask, column_name] = calculated[null_mask]
    elif method in ['min', 'max']:
        calculated = grouped[source_column].transform(method)
        df.loc[null_mask, column_name] = calculated[null_mask]
    elif method == 'concatenate_unique':
        # FIX: Use copy for sorting to avoid modifying original DataFrame index
        if sort_by:
            df_sorted = df.sort_values(sort_by).copy()
            grouped = df_sorted.groupby(group_by, dropna=False)
        else:
            grouped = df.groupby(group_by, dropna=False)

        def concat_unique(series):
            # If we're operating on multiple columns, we need a different approach
            # But transform() passes a Series. 
            # If we have source_columns, we should have used apply() or handled it differently.
            # For now, let's assume we want to concatenate values from ALL source_columns if provided.
            unique_vals = [str(val) for val in series.dropna().unique() if pd.notna(val)]
            try:
                sorted_vals = sorted(unique_vals, key=lambda x: float(x))
            except (ValueError, TypeError):
                sorted_vals = sorted(unique_vals)
            
            if is_json:
                return json.dumps(sorted_vals)
            return separator.join(sorted_vals)

        # If source_columns is plural, we need to handle it per group
        if len(source_columns) > 1:
            def group_concat_unique(group):
                all_vals = []
                for col in source_columns:
                    if col in group.columns:
                        all_vals.extend(group[col].dropna().unique())
                unique_vals = [str(val) for val in set(all_vals) if pd.notna(val)]
                try:
                    sorted_vals = sorted(unique_vals, key=lambda x: float(x))
                except (ValueError, TypeError):
                    sorted_vals = sorted(unique_vals)
                
                if is_json:
                    return json.dumps(sorted_vals)
                return separator.join(sorted_vals)
            
            # Map back to rows
            calculated_map = grouped.apply(group_concat_unique)
            df.loc[null_mask, column_name] = df.loc[null_mask, group_by].apply(
                lambda row: calculated_map.get(tuple(row) if len(group_by) > 1 else row[group_by[0]]), axis=1
            )
        else:
            calculated = grouped[source_column].transform(concat_unique)
            # FIX: Reindex to original DataFrame index to ensure proper alignment
            if sort_by:
                calculated = calculated.reindex(df.index)
            df.loc[null_mask, column_name] = calculated[null_mask]

    elif method == 'concatenate_unique_quoted':
        # FIX: Use copy for sorting to avoid modifying original DataFrame index
        if sort_by:
            df_sorted = df.sort_values(sort_by).copy()
            grouped = df_sorted.groupby(group_by, dropna=False)
        else:
            grouped = df.groupby(group_by, dropna=False)

        quote_each = calculation.get('quote_each', True)
        
        if len(source_columns) > 1:
            def group_concat_quoted(group):
                all_vals = []
                for col in source_columns:
                    if col in group.columns:
                        all_vals.extend(group[col].dropna().unique())
                unique_vals = [str(val) for val in set(all_vals) if pd.notna(val)]
                sorted_vals = sorted(unique_vals)
                
                if is_json:
                    return json.dumps(sorted_vals)
                
                if quote_each:
                    return separator.join(f'"{val}"' for val in sorted_vals)
                return separator.join(sorted_vals)
            
            calculated_map = grouped.apply(group_concat_quoted)
            df.loc[null_mask, column_name] = df.loc[null_mask, group_by].apply(
                lambda row: calculated_map.get(tuple(row) if len(group_by) > 1 else row[group_by[0]]), axis=1
            )
        else:
            def concat_unique_quoted(series):
                unique_vals = [str(val) for val in series.dropna().unique() if pd.notna(val)]
                sorted_vals = sorted(unique_vals)
                
                if is_json:
                    return json.dumps(sorted_vals)
                
                if quote_each:
                    return separator.join(f'"{val}"' for val in sorted_vals)
                return separator.join(sorted_vals)

            calculated = grouped[source_column].transform(concat_unique_quoted)
            # FIX: Reindex to original DataFrame index to ensure proper alignment
            if sort_by:
                calculated = calculated.reindex(df.index)
            df.loc[null_mask, column_name] = calculated[null_mask]

    elif method == 'concatenate_dates':
        # FIX: Use copy for sorting to avoid modifying original DataFrame index
        if sort_by:
            df_sorted = df.sort_values(sort_by).copy()
            grouped = df_sorted.groupby(group_by, dropna=False)
        else:
            grouped = df.groupby(group_by, dropna=False)

        date_fmt = calculation.get('date_format', 'YYYY-MM-DD')
        py_date_fmt = date_fmt.replace('YYYY', '%Y').replace('MM', '%m').replace('DD', '%d')

        def concat_dates(series):
            valid_dates = pd.to_datetime(series, errors='coerce').dropna()
            if valid_dates.empty:
                return "[]" if is_json else ""
            unique_sorted_dates = sorted(valid_dates.unique())
            formatted = [pd.Timestamp(d).strftime(py_date_fmt) for d in unique_sorted_dates]
            
            if is_json:
                return json.dumps(formatted)
            return separator.join(formatted)

        calculated = grouped[source_column].transform(concat_dates)
        # FIX: Reindex to original DataFrame index to ensure proper alignment
        if sort_by:
            calculated = calculated.reindex(df.index)
        df.loc[null_mask, column_name] = calculated[null_mask]

    if preservation_mode == "overwrite_existing":
        engine._print_processing_step("Aggregate", column_name, f"Applied {method} to all rows (overwritten)")
    else:
        engine._print_processing_step("Aggregate", column_name, f"Applied {method} to {null_mask.sum()} null rows")
    return df


def apply_latest_by_date_calculation(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Identifies the 'latest' value in a group based on a date column.
    Commonly used to find the 'Latest Review Status' for a document.
    """
    source_column = calculation.get('source_column')
    group_by = calculation.get('group_by', [])
    sort_by = calculation.get('sort_by', [])
    sort_dir = calculation.get('sort_direction', ['desc'])
    mapping = calculation.get('mapping', {})
    fallback = mapping.get('fallback_value', 'NA')

    if source_column not in df.columns or not group_by or not sort_by:
        return df

    # Initialize column if not exists
    if column_name not in df.columns:
        df[column_name] = None

    # Respect strategy configuration
    preservation_mode = _get_preservation_mode(engine, column_name)
    
    # Determine which rows to calculate for
    if preservation_mode == "overwrite_existing":
        engine._print_processing_step("Latest-By-Date", column_name, "Strategy: overwrite_existing - calculating all rows")
        null_mask = pd.Series([True] * len(df), index=df.index)
    else:
        # Calculate only for null values (default)
        existing_mask = df[column_name].notna()
        if existing_mask.any():
            engine._print_processing_step("Latest-By-Date", column_name, f"Preserving {existing_mask.sum()} existing values")
        
        null_mask = df[column_name].isna()
        if not null_mask.any():
            debug_print(f"Skipped latest_by_date for {column_name}: all values present")
            return df

    engine._print_processing_step("Latest-By-Date", column_name, f"Finding latest {source_column} via {sort_by}")

    filtered_df = df.copy()
    exclude = calculation.get('filter', {}).get('exclude_values', [])
    if exclude:
        filtered_df = filtered_df[~filtered_df[source_column].isin(exclude)]

    asc_flags = [d.lower() == 'asc' for d in sort_dir]
    if len(asc_flags) < len(sort_by):
        asc_flags.extend([False] * (len(sort_by) - len(asc_flags)))

    sorted_df = filtered_df.sort_values(sort_by, ascending=asc_flags)
    latest_vals = sorted_df.groupby(group_by)[source_column].first()

    # Map values back to original dataframe (only for null rows)
    if len(group_by) == 1:
        calculated = df.loc[null_mask, group_by[0]].map(latest_vals)
        df.loc[null_mask, column_name] = calculated.fillna(fallback)
    else:
        # Use a join that preserves the index
        subset = df.loc[null_mask, group_by].copy()
        # Merge by columns but keep index
        mapped = subset.merge(latest_vals, left_on=group_by, right_index=True, how='left')
        # Restore index alignment before assignment
        mapped.index = subset.index
        df.loc[null_mask, column_name] = mapped[source_column].fillna(fallback)

    engine._print_processing_step("Latest-By-Date", column_name, f"Applied to {null_mask.sum()} null rows")
    return df


def apply_latest_non_pending_status(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Specialized logic to find the latest status that is NOT 'Pending'.
    Used to determine the 'Effective Status' of a document sequence.
    """
    # Resolve pending_status parameter from schema
    parameters = engine.schema_data.get('parameters', {})
    pending_status_value = parameters.get('pending_status')

    # Fallback: try to resolve from approval_code_schema
    if pending_status_value is None or pending_status_value == 'pending_status':
        pending_status_value = engine._resolve_schema_reference({
            'schema': 'approval_code_schema',
            'code': 'PEN',
            'field': 'status'
        }) or "Awaiting S.O.'s response"

    source_column = calculation.get('source_column')
    group_by = calculation.get('group_by', ['Document_ID'])
    sort_by = calculation.get('sort_by', ['Submission_Date'])
    filter_config = calculation.get('filter', {})

    # Resolve exclude_values from schema reference if specified
    exclude_values_ref = filter_config.get('exclude_values_reference')
    if exclude_values_ref:
        exclude_values = engine._resolve_schema_reference(exclude_values_ref)
        if not isinstance(exclude_values, list):
            exclude_values = [exclude_values] if exclude_values else []
    else:
        exclude_values = filter_config.get('exclude_values', [])
        exclude_values = [pending_status_value if v == 'pending_status' else v for v in exclude_values]

    # Resolve fallback_value from schema reference if specified
    fallback_ref = calculation.get('fallback_value_reference')
    if fallback_ref:
        fallback_value = engine._resolve_schema_reference(fallback_ref)
    else:
        fallback_config = calculation.get('fallback_value', 'pending_status')
        fallback_value = pending_status_value if fallback_config == 'pending_status' else fallback_config

    preprocessing = calculation.get('preprocessing', {})

    if source_column not in df.columns:
        engine._print_processing_step("Aggregate", column_name, f"ERROR: Source column {source_column} not found")
        return df

    required_cols = group_by + sort_by + [source_column]
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        engine._print_processing_step("Aggregate", column_name, f"ERROR: Missing columns: {missing_cols}")
        return df

    engine._print_processing_step("Aggregate", column_name, "Finding latest non-pending status")

    # Initialize column if not exists
    if column_name not in df.columns:
        df[column_name] = None

    # Respect strategy configuration
    preservation_mode = _get_preservation_mode(engine, column_name)
    
    # Determine which rows to calculate for
    if preservation_mode == "overwrite_existing":
        engine._print_processing_step("Aggregate", column_name, "Strategy: overwrite_existing - calculating all rows")
        null_mask = pd.Series([True] * len(df), index=df.index)
    else:
        # Calculate only for null values (default)
        existing_mask = df[column_name].notna()
        if existing_mask.any():
            engine._print_processing_step("Aggregate", column_name, f"Preserving {existing_mask.sum()} existing values")
        
        null_mask = df[column_name].isna()
        if not null_mask.any():
            debug_print(f"Skipped latest_non_pending_status for {column_name}: all values present")
            return df

    # Filter to only null rows for calculation
    df_calc = df[null_mask].copy()

    # Apply preprocessing if configured
    df_copy = df_calc.copy()
    text_cleaning = preprocessing.get('text_cleaning', {})
    if text_cleaning:
        remove_patterns = text_cleaning.get('remove_patterns', [])
        if remove_patterns:
            for pattern in remove_patterns:
                df_copy[source_column] = df_copy[source_column].astype(str).str.replace(pattern, '', regex=True)
        if text_cleaning.get('strip_whitespace'):
            df_copy[source_column] = df_copy[source_column].astype(str).str.strip()

    def get_latest_non_pending(group_df):
        sorted_df = group_df.sort_values(by=sort_by[0], ascending=False)
        mask = ~sorted_df[source_column].isin(exclude_values)
        non_pending = sorted_df[mask]

        if len(non_pending) > 0:
            return non_pending.iloc[0][source_column]
        else:
            return fallback_value

    result = df_copy.groupby(group_by, group_keys=False).apply(get_latest_non_pending)

    # Merge back - only update null values
    if isinstance(result, pd.Series):
        result_df = result.reset_index()
        result_df.columns = group_by + [column_name]
        # Merge only for originally null rows
        df_merged = pd.merge(df_calc[group_by], result_df, on=group_by, how='left')
        # FIX: Ensure df_merged index matches df_calc index to avoid positional overwrite at top of DF
        df_merged.index = df_calc.index
        # Update only null positions
        if len(df_merged) > 0:
            df.loc[df_merged.index, column_name] = df_merged[column_name]
            if preservation_mode == "overwrite_existing":
                engine._print_processing_step("Aggregate", column_name, f"Applied to all rows (overwritten)")
            else:
                engine._print_processing_step("Aggregate", column_name, f"Applied to {len(df_merged)} null rows")
    else:
        df.loc[null_mask, column_name] = fallback_value
        if preservation_mode == "overwrite_existing":
            engine._print_processing_step("Aggregate", column_name, f"Applied fallback to all rows (overwritten)")
        else:
            engine._print_processing_step("Aggregate", column_name, f"Applied fallback to {null_mask.sum()} null rows")

    return df

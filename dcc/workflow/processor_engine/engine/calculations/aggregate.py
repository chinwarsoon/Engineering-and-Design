"""
Aggregate calculations: standard grouping/aggregation, latest-by-date,
latest non-pending status, concatenate unique values, and date concatenation.
Extracted from UniversalDocumentProcessor._apply_aggregate_calculation and related methods.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def apply_aggregate_calculation(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Performs standard grouping and aggregation (Min, Max, Sum, Count, Concatenate, etc.)
    """
    source_column = calculation.get('source_column')
    method = calculation.get('method')
    group_by = calculation.get('group_by', [])
    sort_by = calculation.get('sort_by', [])
    separator = calculation.get('separator', ', ')

    if not source_column or source_column not in df.columns or not group_by:
        return df

    engine._print_processing_step("Aggregate", column_name, f"{method} of {source_column} grouped by {group_by}")
    grouped = df.groupby(group_by, dropna=False)

    if method == 'count':
        df[column_name] = grouped[source_column].transform('count')
    elif method in ['min', 'max']:
        df[column_name] = grouped[source_column].transform(method)
    elif method == 'concatenate_unique':
        if sort_by:
            df_sorted = df.sort_values(sort_by)
            grouped = df_sorted.groupby(group_by, dropna=False)

        def concat_unique(series):
            unique_vals = [str(val) for val in series.dropna().unique() if pd.notna(val)]
            try:
                sorted_vals = sorted(unique_vals, key=lambda x: float(x))
            except (ValueError, TypeError):
                sorted_vals = sorted(unique_vals)
            return separator.join(sorted_vals)

        df[column_name] = grouped[source_column].transform(concat_unique)

    elif method == 'concatenate_unique_quoted':
        if sort_by:
            df_sorted = df.sort_values(sort_by)
            grouped = df_sorted.groupby(group_by, dropna=False)

        quote_each = calculation.get('quote_each', True)
        def concat_unique_quoted(series):
            unique_vals = [str(val) for val in series.dropna().unique() if pd.notna(val)]
            sorted_vals = sorted(unique_vals)
            if quote_each:
                return separator.join(f'"{val}"' for val in sorted_vals)
            return separator.join(sorted_vals)

        df[column_name] = grouped[source_column].transform(concat_unique_quoted)

    elif method == 'concatenate_dates':
        if sort_by:
            df_sorted = df.sort_values(sort_by)
            grouped = df_sorted.groupby(group_by, dropna=False)

        date_fmt = calculation.get('date_format', 'YYYY-MM-DD')
        py_date_fmt = date_fmt.replace('YYYY', '%Y').replace('MM', '%m').replace('DD', '%d')

        def concat_dates(series):
            valid_dates = pd.to_datetime(series, errors='coerce').dropna()
            if valid_dates.empty:
                return ""
            unique_sorted_dates = sorted(valid_dates.unique())
            formatted = [pd.Timestamp(d).strftime(py_date_fmt) for d in unique_sorted_dates]
            return separator.join(formatted)

        df[column_name] = grouped[source_column].transform(concat_dates)

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
        df[column_name] = fallback
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

    # Map values back to original dataframe
    if len(group_by) == 1:
        df[column_name] = df[group_by[0]].map(latest_vals).fillna(fallback)
    else:
        mapped = pd.merge(df[group_by], latest_vals, left_on=group_by, right_index=True, how='left')
        df[column_name] = mapped[source_column].fillna(fallback)

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
        logger.warning(f"Source column {source_column} not found for latest_non_pending_status")
        return df

    required_cols = group_by + sort_by + [source_column]
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        logger.warning(f"Missing columns for latest_non_pending_status: {missing_cols}")
        return df

    engine._print_processing_step("Aggregate", column_name, "Finding latest non-pending status")

    # Apply preprocessing if configured
    df_copy = df.copy()
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

    # Merge back
    if isinstance(result, pd.Series):
        result_df = result.reset_index()
        result_df.columns = group_by + [column_name]
        df = pd.merge(df, result_df, on=group_by, how='left')
    else:
        df[column_name] = fallback_value

    return df

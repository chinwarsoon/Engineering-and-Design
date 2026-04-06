"""
Null handling strategies for the document processor engine.
Extracted from UniversalDocumentProcessor null handling methods.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def apply_forward_fill(engine, df: pd.DataFrame, column_name: str, null_handling: Dict) -> pd.DataFrame:
    """
    Apply forward fill strategy - fills null values with the last non-null value.
    Supports group-based filling and zero-padding formatting.
    """
    group_by = null_handling.get('group_by', [])

    # Defensive check: ensure column_name is a string, not a tuple
    if not isinstance(column_name, str):
        logger.error(f"Invalid column_name type: {type(column_name)} - {column_name}")
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
        logger.error(f"Column '{column_name}' not found in DataFrame. Available columns: {list(df.columns)[:10]}...")
        return df

    # FIX: Always work on a local copy; never mutate the caller's DataFrame.
    df_copy = df.reset_index(drop=True).copy() if not isinstance(df.index, pd.RangeIndex) else df.copy()

    # Remove duplicate columns which cause df[col] to return a DataFrame
    if df_copy.columns.tolist().count(column_name) > 1:
        logger.error(f"DUPLICATE COLUMNS DETECTED: '{column_name}' appears {df_copy.columns.tolist().count(column_name)} times! Removing duplicates.")
        df_copy = df_copy.loc[:, ~df_copy.columns.duplicated()].copy()
        df_copy.index = pd.RangeIndex(len(df_copy))

    if group_by:
        # Validate group_by columns exist
        valid_group_by = [col for col in group_by if col in df_copy.columns]
        if not valid_group_by:
            logger.warning(f"None of the group_by columns {group_by} found in DataFrame. Skipping forward fill for {column_name}.")
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

    if na_fallback:
        # Replace remaining NaN with 'NA' if fill_value was NaN
        df_copy[column_name] = df_copy[column_name].fillna('NA')

    # Apply zero-padding formatting if specified
    if zero_pad:
        try:
            df_copy[column_name] = df_copy[column_name].apply(
                lambda x: str(int(float(x))).zfill(zero_pad) if pd.notna(x) and x != 'NA' else x
            )
            logger.info(f"Applied zero-padding ({zero_pad} digits) for {column_name}")
        except Exception as e:
            logger.warning(f"Could not apply zero-padding for {column_name}: {e}")

    logger.info(f"Applied forward fill for '{column_name}': group_by={group_by}")
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

    if final_fill is not None and column_name in df_copy.columns:
        df_copy[column_name] = df_copy[column_name].fillna(final_fill)

    logger.info(f"Applied multi_level_forward_fill for {column_name}")
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
        logger.error(f"_apply_copy_from: 'source_column' not specified in null_handling for '{column_name}'. Skipping.")
        return df
    if source_column not in df.columns:
        logger.error(f"_apply_copy_from: source column '{source_column}' not found in DataFrame for '{column_name}'. Skipping.")
        return df

    df = df.copy()

    # Copy from source column where target is null
    mask = df[column_name].isna()
    df.loc[mask, column_name] = df.loc[mask, source_column]

    # Apply fallback for remaining null values
    df[column_name] = df[column_name].fillna(fallback_value)

    logger.info(f"Applied copy from for {column_name}: source={source_column}, fallback={fallback_value}")
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
        logger.warning(
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

    logger.info(f"Calculated working days for {column_name}: +{days} days from {source_column}")
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

    logger.info(f"Applied conditional calculation for {column_name}: based on {source_column}")
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
            logger.info(f"Applied zero-padding ({zero_pad} digits) for {column_name}")
        except Exception as e:
            logger.warning(f"Could not apply zero-padding for {column_name}: {e}")

    logger.info(f"Applied default value for {column_name}: {default_value}")
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

    logger.info(f"Applied lookup if null for {column_name}: lookup_key={lookup_key}")
    return df

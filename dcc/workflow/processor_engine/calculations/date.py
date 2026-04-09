"""
Date calculations: working days, date differences, conditional dates,
resubmission plan dates, and business day calculations.
Extracted from UniversalDocumentProcessor._apply_date_calculation and related methods.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

# Import hierarchical logging functions from initiation_engine (centralized)
from initiation_engine import status_print, debug_print


def apply_date_calculation(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Standard date calculation dispatcher.
    Routes to specific methods based on calculation method.
    """
    method = calculation.get('method')
    parameters = calculation.get('parameters', {})

    if method == 'add_working_days':
        df = calculate_working_days(engine, df, column_name, calculation)
    elif method == 'date_difference':
        df = calculate_date_difference(engine, df, column_name, calculation)

    engine._print_processing_step("Date-Calc", column_name, f"method={method}")
    return df


def calculate_working_days(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Calculates a future date by adding a specific number of days to a source date.
    Only fills null values in target column.
    """
    source_column = calculation.get('source_column')
    parameters = calculation.get('parameters', {})
    days = parameters.get('days', 14)

    if source_column not in df.columns:
        return df

    # Initialize column if not exists
    if column_name not in df.columns:
        df[column_name] = pd.NaT

    # Get existing non-null values
    existing_mask = df[column_name].notna()
    if existing_mask.any():
        engine._print_processing_step("Working-Days", column_name, f"Preserving {existing_mask.sum()} existing values")

    engine._print_processing_step("Working-Days", column_name, f"+{days} days from {source_column}")

    # Convert columns to datetime for safety
    df[source_column] = pd.to_datetime(df[source_column], errors='coerce')

    # Calculate target date only for null values
    null_mask = df[column_name].isna()
    source_notna = df[source_column].notna()
    calc_mask = null_mask & source_notna
    if calc_mask.any():
        df.loc[calc_mask, column_name] = df.loc[calc_mask, source_column] + pd.Timedelta(days=days)
        engine._print_processing_step("Working-Days", column_name, f"Applied to {calc_mask.sum()} null rows")
    else:
        debug_print(f"Skipped working days for {column_name}: all values present or no source data")

    return df


def calculate_date_difference(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Calculate difference between two dates.
    Only fills null values in target column.
    """
    source_column = calculation.get('source_column')
    target_column = calculation.get('target_column', column_name)

    if source_column not in df.columns or target_column not in df.columns:
        return df

    # Initialize column if not exists
    if column_name not in df.columns:
        df[column_name] = None

    # Get existing non-null values
    existing_mask = df[column_name].notna()
    if existing_mask.any():
        engine._print_processing_step("Date-Diff", column_name, f"Preserving {existing_mask.sum()} existing values")

    engine._print_processing_step("Date-Diff", column_name, f"{source_column} to {target_column}")

    # Calculate only for null values
    null_mask = df[column_name].isna()
    if not null_mask.any():
        debug_print(f"Skipped date difference for {column_name}: all values present")
        return df

    # Convert to datetime
    df[source_column] = pd.to_datetime(df[source_column], errors='coerce')
    df[target_column] = pd.to_datetime(df[target_column], errors='coerce')

    # Calculate difference in days
    diff = (df[target_column] - df[source_column]).dt.days
    df.loc[null_mask, column_name] = diff[null_mask]

    engine._print_processing_step("Date-Diff", column_name, f"Applied to {null_mask.sum()} null rows")
    return df


def apply_resubmission_plan_date(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Calculate Resubmission_Plan_Date based on conditional logic.
    Important: When Submission_Closed is YES, always overwrite to null (NaT).
    """
    dependencies = calculation.get('dependencies', [])
    conditions = calculation.get('conditions', [])
    parameters = calculation.get('parameters', {})

    # Get parameters
    resubmission_duration = parameters.get('resubmission_duration', 14)
    first_review_duration = parameters.get('first_review_duration', 20)
    second_review_duration = parameters.get('second_review_duration', 14)
    duration_is_working_day = parameters.get('duration_is_working_day', True)

    # Get required columns
    submission_closed_col = 'Submission_Closed' if 'Submission_Closed' in df.columns else None
    review_return_date_col = 'Review_Return_Actual_Date' if 'Review_Return_Actual_Date' in df.columns else None
    latest_submission_date_col = 'Latest_Submission_Date' if 'Latest_Submission_Date' in df.columns else None
    submission_date_col = 'Submission_Date' if 'Submission_Date' in df.columns else None

    engine._print_processing_step("Resubmission-Plan", column_name, "Calculating based on submission state")

    # Initialize column if not exists
    if column_name not in df.columns:
        df[column_name] = pd.NaT

    # Get existing non-null values (will be preserved unless Submission_Closed=YES)
    existing_mask = df[column_name].notna()
    if existing_mask.any():
        engine._print_processing_step("Resubmission-Plan", column_name, f"Will preserve {existing_mask.sum()} existing values (except where Submission_Closed=YES)")

    # Track which rows have been determined - these skip remaining checks
    determined_mask = pd.Series([False] * len(df), index=df.index)

    # Condition 1: If Submission_Closed == 'YES', set to NaT (null) - ALWAYS OVERWRITES
    if submission_closed_col:
        mask_closed = df[submission_closed_col] == 'YES'
        df.loc[mask_closed, column_name] = pd.NaT
        determined_mask |= mask_closed
        if mask_closed.any():
            engine._print_processing_step("Resubmission-Plan", column_name, f"Overwrote {mask_closed.sum()} rows to null (Submission_Closed=YES)")

    # Condition 2: If Review_Return_Actual_Date is not null, add duration offset
    if review_return_date_col:
        df[review_return_date_col] = pd.to_datetime(df[review_return_date_col], errors='coerce')
        mask_has_return_date = df[review_return_date_col].notna() & ~determined_mask

        if duration_is_working_day:
            from pandas.tseries.offsets import BDay
            df.loc[mask_has_return_date, column_name] = df.loc[mask_has_return_date, review_return_date_col] + BDay(resubmission_duration)
        else:
            df.loc[mask_has_return_date, column_name] = df.loc[mask_has_return_date, review_return_date_col] + pd.Timedelta(days=resubmission_duration)

        determined_mask |= mask_has_return_date

    # Condition 3: If Latest_Submission_Date == Submission_Date (first submission)
    if latest_submission_date_col and submission_date_col:
        df[latest_submission_date_col] = pd.to_datetime(df[latest_submission_date_col], errors='coerce')
        df[submission_date_col] = pd.to_datetime(df[submission_date_col], errors='coerce')

        mask_first_submission = (df[latest_submission_date_col] == df[submission_date_col]) & ~determined_mask

        total_days = first_review_duration + resubmission_duration
        if duration_is_working_day:
            from pandas.tseries.offsets import BDay
            df.loc[mask_first_submission, column_name] = df.loc[mask_first_submission, submission_date_col] + BDay(total_days)
        else:
            df.loc[mask_first_submission, column_name] = df.loc[mask_first_submission, submission_date_col] + pd.Timedelta(days=total_days)

        determined_mask |= mask_first_submission

    # Condition 4: Else (subsequent submission)
    if submission_date_col:
        mask_subsequent = ~determined_mask
        total_days = second_review_duration + resubmission_duration
        if duration_is_working_day:
            from pandas.tseries.offsets import BDay
            df.loc[mask_subsequent, column_name] = df.loc[mask_subsequent, submission_date_col] + BDay(total_days)
        else:
            df.loc[mask_subsequent, column_name] = df.loc[mask_subsequent, submission_date_col] + pd.Timedelta(days=total_days)
        determined_mask |= mask_subsequent

    engine._print_processing_step("Resubmission-Plan", column_name, 
        f"Applied: {df[column_name].notna().sum()} rows with dates, {df[column_name].isna().sum()} rows null")
    return df


def apply_conditional_date_calculation(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Apply conditional date calculation based on previous submission existence.
    Only fills null values in target column.

    For Review_Return_Plan_Date:
    - First submission: Submission_Date + first_review_duration
    - Resubmission: Submission_Date + second_review_duration
    """
    doc_id_col = 'Document_ID'
    submission_date_col = 'Submission_Date'

    if doc_id_col not in df.columns or submission_date_col not in df.columns:
        engine._print_processing_step("Conditional-Date", column_name, f"ERROR: Missing required columns: {doc_id_col}, {submission_date_col}")
        return df

    # Initialize column if not exists
    if column_name not in df.columns:
        df[column_name] = pd.NaT

    # Get existing non-null values
    existing_mask = df[column_name].notna()
    if existing_mask.any():
        engine._print_processing_step("Conditional-Date", column_name, f"Preserving {existing_mask.sum()} existing values")

    # Calculate only for null values
    null_mask = df[column_name].isna()
    if not null_mask.any():
        debug_print(f"Skipped conditional date for {column_name}: all values present")
        return df

    first_duration = calculation.get('first_review_duration', 20)
    second_duration = calculation.get('second_review_duration', 14)

    engine._print_processing_step("Conditional-Date", column_name, f"first={first_duration}d, resub={second_duration}d")

    df[submission_date_col] = pd.to_datetime(df[submission_date_col], errors='coerce')

    # Vectorised: a row is a "first submission" if its date equals the minimum
    # submission date for that Document_ID group.
    min_dates = df.groupby(doc_id_col)[submission_date_col].transform('min')
    is_first = df[submission_date_col] == min_dates

    results = pd.Series(pd.NaT, index=df.index)
    valid = df[submission_date_col].notna() & null_mask

    results[valid & is_first] = df.loc[valid & is_first, submission_date_col] + pd.Timedelta(days=first_duration)
    results[valid & ~is_first] = df.loc[valid & ~is_first, submission_date_col] + pd.Timedelta(days=second_duration)

    df.loc[null_mask, column_name] = pd.to_datetime(results[null_mask])

    engine._print_processing_step("Conditional-Date", column_name, f"Applied to {null_mask.sum()} null rows")
    return df


def apply_conditional_business_day_calculation(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Apply conditional business day calculation.
    Only fills null values in target column.

    For Duration_of_Review:
    - Primary end date: Review_Return_Actual_Date
    - Fallback end date: current_date (today)
    - Calculate days between Submission_Date and end_date
    - Ensures non-negative values
    """
    end_date_logic = calculation.get('end_date_logic', {})
    primary_end = end_date_logic.get('primary', 'Review_Return_Actual_Date')
    fallback_end = end_date_logic.get('fallback', 'current_date')

    start_col = 'Submission_Date'

    if start_col not in df.columns:
        engine._print_processing_step("Business-Day", column_name, f"ERROR: Missing required column: {start_col}")
        return df

    # Initialize column if not exists
    if column_name not in df.columns:
        df[column_name] = None

    # Get existing non-null values
    existing_mask = df[column_name].notna()
    if existing_mask.any():
        engine._print_processing_step("Business-Day", column_name, f"Preserving {existing_mask.sum()} existing values")

    # Calculate only for null values
    null_mask = df[column_name].isna()
    if not null_mask.any():
        debug_print(f"Skipped business day calc for {column_name}: all values present")
        return df

    engine._print_processing_step("Business-Day", column_name, f"primary={primary_end}, fallback={fallback_end}")

    df[start_col] = pd.to_datetime(df[start_col], errors='coerce')
    today = pd.Timestamp.now().normalize()

    # Build end_date Series vectorially
    if primary_end in df.columns:
        primary_series = pd.to_datetime(df[primary_end], errors='coerce')
    else:
        primary_series = pd.Series(pd.NaT, index=df.index)

    if fallback_end == 'current_date':
        end_dates = primary_series.fillna(today)
    else:
        end_dates = primary_series  # no fallback; missing stays NaT

    # Calculate duration; enforce non-negative
    diff = (end_dates - df[start_col]).dt.days
    diff = diff.where(diff >= 0, other=np.nan)
    df.loc[null_mask, column_name] = diff[null_mask]

    engine._print_processing_step("Business-Day", column_name, f"Applied to {null_mask.sum()} null rows")
    return df

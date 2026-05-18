"""
Date calculations: working days, date differences, conditional dates,
resubmission plan dates, and business day calculations.
Extracted from UniversalDocumentProcessor._apply_date_calculation and related methods.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

# Import hierarchical logging functions from utility_engine
from utility_engine.console import status_print, debug_print


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
    Calculate Resubmission_Plan_Date using row-position-separated 5-priority logic.

    Row position (is_latest vs is_superseded) determines which priority applies,
    replacing the old flat 4-condition approach.

    Priority order:
    L1: is_latest + Resubmission_Required == NO             → NaT
    L2: is_latest + Resubmission_Required in [YES, PEN]     → calc A → B
    S1: is_superseded + Resubmission_Required == NO          → NaT
    S2: is_superseded + Resubmission_Required == RESUBMITTED
        + Review_Status_Code in [APP, VOID, INF]            → NaT
    S3: is_superseded + Resubmission_Required == RESUBMITTED
        + Review_Status_Code NOT in [APP, VOID, INF]        → calc A → C

    Sub-rules (calculate):
    A: Review_Return_Actual_Date not null → +resubmission_duration BDays
    B: Submission_Date + (first_review + resubmission) BDays (latest rows)
    C: Submission_Date + (second_review + resubmission) BDays (superseded rows)
    """
    dependencies = calculation.get('dependencies', [])
    parameters = calculation.get('parameters', {})

    resubmission_duration = parameters.get('resubmission_duration', 14)
    first_review_duration = parameters.get('first_review_duration', 20)
    second_review_duration = parameters.get('second_review_duration', 14)
    duration_is_working_day = parameters.get('duration_is_working_day', True)

    # New dependency order (Phase 5):
    # [0] Submission_Date, [1] Latest_Submission_Date, [2] Resubmission_Required,
    # [3] Review_Status_Code, [4] Review_Return_Actual_Date
    submission_date_col       = dependencies[0] if len(dependencies) > 0 else 'Submission_Date'
    latest_submission_date_col = dependencies[1] if len(dependencies) > 1 else 'Latest_Submission_Date'
    resubmission_required_col = dependencies[2] if len(dependencies) > 2 else 'Resubmission_Required'
    review_status_col         = dependencies[3] if len(dependencies) > 3 else 'Review_Status_Code'
    review_return_date_col    = dependencies[4] if len(dependencies) > 4 else 'Review_Return_Actual_Date'

    engine._print_processing_step("Resubmission-Plan", column_name,
        "Calculating based on row position and resubmission state")

    # Initialize column if not exists
    if column_name not in df.columns:
        df[column_name] = pd.NaT

    # Track which rows have been determined — these skip remaining checks
    determined_mask = pd.Series([False] * len(df), index=df.index)

    # Coerce date columns
    for col in [submission_date_col, latest_submission_date_col, review_return_date_col]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Determine row position: is_latest vs is_superseded
    has_position_cols = (submission_date_col in df.columns
                         and latest_submission_date_col in df.columns)
    if has_position_cols:
        is_latest_mask = df[submission_date_col] == df[latest_submission_date_col]
        is_superseded_mask = df[submission_date_col] != df[latest_submission_date_col]
    else:
        is_latest_mask = pd.Series([True] * len(df), index=df.index)
        is_superseded_mask = pd.Series([False] * len(df), index=df.index)
        engine._print_processing_step("Resubmission-Plan", column_name,
            "WARNING: Missing Submission_Date or Latest_Submission_Date — treating all as latest")

    # Get terminal codes from schema
    terminal_codes = ['APP', 'VOID', 'INF']
    if review_status_col in df.columns:
        approval_entries = engine.schema_data.get('approval_codes', [])
        terminal_statuses = ['Approved', 'Void', 'For Information']
        codes = [
            entry['code'] for entry in approval_entries
            if entry.get('status') in terminal_statuses
        ]
        if codes:
            terminal_codes = codes
    else:
        engine._print_processing_step("Resubmission-Plan", column_name,
            f"WARNING: {review_status_col} not found — terminal check uses fallback {terminal_codes}")

    # ===== L1: Latest + Resubmission_Required == NO → NaT =====
    # Latest submission row not requiring resubmission: no plan date needed
    if resubmission_required_col in df.columns and has_position_cols:
        mask_l1 = (
            is_latest_mask
            & (df[resubmission_required_col] == 'NO')
            & ~determined_mask
        )
        df.loc[mask_l1, column_name] = pd.NaT
        determined_mask |= mask_l1
        if mask_l1.any():
            engine._print_processing_step("Resubmission-Plan", column_name,
                f"L1: Set {mask_l1.sum()} latest-NO rows to NaT")

    # ===== L2: Latest + Resubmission_Required in [YES, PEN] → calc A → B =====
    # Latest row pending resubmission: calculate date via Review_Return_Actual_Date
    # or fall back to Submission_Date + first_review + resubmission
    if resubmission_required_col in df.columns and has_position_cols:
        mask_l2 = (
            is_latest_mask
            & df[resubmission_required_col].isin(['YES', 'PEN'])
            & ~determined_mask
        )
        if mask_l2.any():
            # Sub-rule A: Review_Return_Actual_Date not null → +resubmission_duration
            if review_return_date_col in df.columns:
                mask_a = mask_l2 & df[review_return_date_col].notna()
                if mask_a.any():
                    if duration_is_working_day:
                        from pandas.tseries.offsets import BDay
                        df.loc[mask_a, column_name] = (
                            df.loc[mask_a, review_return_date_col]
                            + BDay(resubmission_duration)
                        )
                    else:
                        df.loc[mask_a, column_name] = (
                            df.loc[mask_a, review_return_date_col]
                            + pd.Timedelta(days=resubmission_duration)
                        )
                    determined_mask |= mask_a

            # Sub-rule B: Submission_Date + (first_review + resubmission) BDays
            mask_b = mask_l2 & ~determined_mask
            if mask_b.any():
                total_days = first_review_duration + resubmission_duration
                if duration_is_working_day:
                    from pandas.tseries.offsets import BDay
                    df.loc[mask_b, column_name] = (
                        df.loc[mask_b, submission_date_col] + BDay(total_days)
                    )
                else:
                    df.loc[mask_b, column_name] = (
                        df.loc[mask_b, submission_date_col]
                        + pd.Timedelta(days=total_days)
                    )
                determined_mask |= mask_b

            engine._print_processing_step("Resubmission-Plan", column_name,
                f"L2: Set {mask_l2.sum()} latest-YES/PEN rows with plan dates")

    # ===== S1: Superseded + Resubmission_Required == NO → NaT =====
    # Superseded rows not requiring resubmission (older documents superseded by newer):
    # no plan date needed
    if resubmission_required_col in df.columns and has_position_cols:
        mask_s1 = (
            is_superseded_mask
            & (df[resubmission_required_col] == 'NO')
            & ~determined_mask
        )
        df.loc[mask_s1, column_name] = pd.NaT
        determined_mask |= mask_s1
        if mask_s1.any():
            engine._print_processing_step("Resubmission-Plan", column_name,
                f"S1: Set {mask_s1.sum()} superseded-NO rows to NaT")

    # ===== S2: Superseded + RESUBMITTED + terminal → NaT =====
    # Superseded rows with terminal review status (APP, VOID, INF): document is
    # terminally closed, no future resubmission
    if (resubmission_required_col in df.columns and review_status_col in df.columns
            and has_position_cols):
        mask_s2 = (
            is_superseded_mask
            & (df[resubmission_required_col] == 'RESUBMITTED')
            & df[review_status_col].isin(terminal_codes)
            & ~determined_mask
        )
        df.loc[mask_s2, column_name] = pd.NaT
        determined_mask |= mask_s2
        if mask_s2.any():
            engine._print_processing_step("Resubmission-Plan", column_name,
                f"S2: Set {mask_s2.sum()} superseded-RESUBMITTED-terminal rows to NaT")

    # ===== S3: Superseded + RESUBMITTED + non-terminal → calc A → C =====
    # Superseded rows that were resubmitted with non-terminal status (PEN, REJ, AWC, NAP):
    # calculate date via Review_Return_Actual_Date or fall back to
    # Submission_Date + second_review + resubmission
    if (resubmission_required_col in df.columns and review_status_col in df.columns
            and has_position_cols):
        mask_s3 = (
            is_superseded_mask
            & (df[resubmission_required_col] == 'RESUBMITTED')
            & ~df[review_status_col].isin(terminal_codes)
            & ~determined_mask
        )
        if mask_s3.any():
            # Sub-rule A: Review_Return_Actual_Date not null → +resubmission_duration
            if review_return_date_col in df.columns:
                mask_a = mask_s3 & df[review_return_date_col].notna()
                if mask_a.any():
                    if duration_is_working_day:
                        from pandas.tseries.offsets import BDay
                        df.loc[mask_a, column_name] = (
                            df.loc[mask_a, review_return_date_col]
                            + BDay(resubmission_duration)
                        )
                    else:
                        df.loc[mask_a, column_name] = (
                            df.loc[mask_a, review_return_date_col]
                            + pd.Timedelta(days=resubmission_duration)
                        )
                    determined_mask |= mask_a

            # Sub-rule C: Submission_Date + (second_review + resubmission) BDays
            mask_c = mask_s3 & ~determined_mask
            if mask_c.any():
                total_days = second_review_duration + resubmission_duration
                if duration_is_working_day:
                    from pandas.tseries.offsets import BDay
                    df.loc[mask_c, column_name] = (
                        df.loc[mask_c, submission_date_col] + BDay(total_days)
                    )
                else:
                    df.loc[mask_c, column_name] = (
                        df.loc[mask_c, submission_date_col]
                        + pd.Timedelta(days=total_days)
                    )
                determined_mask |= mask_c

            engine._print_processing_step("Resubmission-Plan", column_name,
                f"S3: Set {mask_s3.sum()} superseded-RESUBMITTED-non-terminal rows with plan dates")

    engine._print_processing_step("Resubmission-Plan", column_name,
        f"Applied: {df[column_name].notna().sum()} rows with dates, "
        f"{df[column_name].isna().sum()} rows null")
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

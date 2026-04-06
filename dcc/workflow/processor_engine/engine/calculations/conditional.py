"""
Conditional calculations: row-level conditionals, resubmission required,
submission closure status, and overdue status.
Extracted from UniversalDocumentProcessor._apply_conditional_calculation and related methods.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def apply_current_row_calculation(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Generic conditional logic based on other columns in the current row.
    """
    source_column = calculation.get('source_column')
    condition = calculation.get('condition')

    if source_column not in df.columns:
        return df

    engine._print_processing_step("Conditional", column_name, f"Evaluating {condition}")

    if condition == 'is_current_submission':
        df[column_name] = df[source_column]
    else:
        df[column_name] = df[source_column]

    return df


def apply_update_resubmission_required(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Logic for 'Update_Resubmission_Required'.
    Priority order (per schema):
    1. Keep NO if already NO
    2. Set to NO if submission is closed
    3. Set to RESUBMITTED if not the latest submission (resubmission already done)
    4. Set to PEN if latest submission and awaiting review return
    5. Default to YES for remaining rows
    """
    source_column = calculation.get('source_column', 'Resubmission_Required')

    # Get required columns
    submission_closed_col = 'Submission_Closed' if 'Submission_Closed' in df.columns else None
    document_id_col = 'Document_ID' if 'Document_ID' in df.columns else None
    submission_date_col = 'Submission_Date' if 'Submission_Date' in df.columns else None
    review_return_col = 'Review_Return_Actual_Date' if 'Review_Return_Actual_Date' in df.columns else None

    engine._print_processing_step("Conditional", column_name, f"Checking rejection/resubmission logic from {source_column}")

    # Initialize: start with default YES for all rows
    df[column_name] = 'YES'

    # Track which rows have been determined - these skip remaining checks
    determined_mask = pd.Series([False] * len(df), index=df.index)

    # Condition 1: Keep NO if already NO
    if source_column in df.columns:
        mask_already_no = df[source_column] == 'NO'
        df.loc[mask_already_no, column_name] = 'NO'
        determined_mask |= mask_already_no

    # Condition 2: Set to NO if submission is closed (skip rows already determined)
    if submission_closed_col:
        mask_closed = (df[submission_closed_col] == 'YES') & ~determined_mask
        df.loc[mask_closed, column_name] = 'NO'
        determined_mask |= mask_closed

    # Condition 3: Set to RESUBMITTED if not the latest submission (skip rows already determined)
    if document_id_col and submission_date_col:
        df[submission_date_col] = pd.to_datetime(df[submission_date_col], errors='coerce')
        latest_dates = df.groupby(document_id_col)[submission_date_col].transform('max')
        mask_not_latest = (df[submission_date_col] < latest_dates) & ~determined_mask
        df.loc[mask_not_latest, column_name] = 'RESUBMITTED'
        determined_mask |= mask_not_latest

    # Condition 4: Set to PEN if latest submission and awaiting review return
    if review_return_col and submission_date_col and document_id_col:
        df[review_return_col] = pd.to_datetime(df[review_return_col], errors='coerce')
        latest_dates = df.groupby(document_id_col)[submission_date_col].transform('max')
        mask_pending = (
            (df[submission_date_col] == latest_dates) &
            df[review_return_col].isna() &
            ~determined_mask
        )
        df.loc[mask_pending, column_name] = 'PEN'
        determined_mask |= mask_pending

    # Condition 5: Default YES - already set for all remaining undetermined rows

    logger.info(f"Applied update_resubmission_required for {column_name}: "
                f"{(df[column_name] == 'NO').sum()} NO, {(df[column_name] == 'RESUBMITTED').sum()} RESUBMITTED, "
                f"{(df[column_name] == 'PEN').sum()} PEN, {(df[column_name] == 'YES').sum()} YES")
    return df


def apply_submission_closure_status(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Determines if a submission sequence is 'Closed' or 'Open'.
    Priority order:
    1. Keep YES if already YES
    2. Set to YES if current submission is not the latest (superseded by newer submission)
    3. Set to YES if Latest_Approval_Code in ['APP', 'VOID']
    4. Default to NO for remaining rows

    Note: Does NOT depend on Resubmission_Required to avoid circular dependency.
    """
    source_column = calculation.get('source_column', 'Submission_Closed')

    # Get required columns
    latest_approval_col = 'Latest_Approval_Code' if 'Latest_Approval_Code' in df.columns else None
    document_id_col = 'Document_ID' if 'Document_ID' in df.columns else None
    submission_date_col = 'Submission_Date' if 'Submission_Date' in df.columns else None

    engine._print_processing_step("Conditional", column_name, "Evaluating closure status")

    # Preprocessing: convert to uppercase and fill nulls
    preprocessing = calculation.get('preprocessing', {})
    text_cleaning = preprocessing.get('text_cleaning', {})
    if text_cleaning.get('convert_to_uppercase') and source_column in df.columns:
        df[source_column] = df[source_column].str.upper()
    if text_cleaning.get('fill_nulls') and source_column in df.columns:
        df[source_column] = df[source_column].fillna(text_cleaning['fill_nulls'])

    # Initialize: start with default NO for all rows
    df[column_name] = 'NO'

    # Track which rows have been determined - these skip remaining checks
    determined_mask = pd.Series([False] * len(df), index=df.index)

    # Condition 1: Keep YES if already YES
    if source_column in df.columns:
        mask_already_yes = (df[source_column] == 'YES') & ~determined_mask
        df.loc[mask_already_yes, column_name] = 'YES'
        determined_mask |= mask_already_yes

    # Condition 2: Set to YES if current submission is not the latest (superseded)
    if document_id_col and submission_date_col:
        df[submission_date_col] = pd.to_datetime(df[submission_date_col], errors='coerce')
        latest_dates = df.groupby(document_id_col)[submission_date_col].transform('max')
        mask_not_latest = (df[submission_date_col] < latest_dates) & ~determined_mask
        df.loc[mask_not_latest, column_name] = 'YES'
        determined_mask |= mask_not_latest

    # Condition 3: Set to YES if Latest_Approval_Code is in approval list
    if latest_approval_col:
        approval_codes = ['APP', 'VOID']
        mask_approved = df[latest_approval_col].isin(approval_codes) & ~determined_mask
        df.loc[mask_approved, column_name] = 'YES'
        determined_mask |= mask_approved

    # Condition 4: Default NO - already set for all remaining undetermined rows

    return df


def apply_calculate_overdue_status(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Calculates if a document is overdue by comparing Resubmission_Plan_Date
    against current date.

    Logic:
    1. If Resubmission_Required == 'YES' AND Resubmission_Plan_Date is not null AND Resubmission_Plan_Date < current_date -> 'Overdue'
    2. Otherwise -> null
    """
    # Get required columns
    resubmission_required_col = 'Resubmission_Required' if 'Resubmission_Required' in df.columns else None
    resubmission_plan_date_col = 'Resubmission_Plan_Date' if 'Resubmission_Plan_Date' in df.columns else None

    engine._print_processing_step("Conditional", column_name, "Calculating Overdue/On-Track")

    # Initialize with pd.NA for consistent nullable dtype
    df[column_name] = pd.NA

    if resubmission_required_col and resubmission_plan_date_col:
        # Convert plan date to datetime
        df[resubmission_plan_date_col] = pd.to_datetime(df[resubmission_plan_date_col], errors='coerce')

        # Get current date
        current_date = pd.Timestamp.now().normalize()

        # Condition: Resubmission_Required == 'YES' AND plan date not null AND plan date < current_date
        mask_overdue = (
            (df[resubmission_required_col] == 'YES') &
            (df[resubmission_plan_date_col].notna()) &
            (df[resubmission_plan_date_col] < current_date)
        )

        df.loc[mask_overdue, column_name] = 'Overdue'

        logger.info(f"Applied calculate_overdue_status for {column_name}: "
                    f"{mask_overdue.sum()} rows Overdue, {(~mask_overdue).sum()} rows null")
    else:
        logger.warning(f"Cannot calculate overdue status: missing required columns")

    return df

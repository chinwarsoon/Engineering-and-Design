"""
Conditional calculations: row-level conditionals, resubmission required,
submission closure status, and overdue status.
Extracted from UniversalDocumentProcessor._apply_conditional_calculation and related methods.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

# Import hierarchical logging functions from utility_engine
from utility_engine.console import status_print, debug_print


def _coerce_date_col(df: pd.DataFrame, col: str) -> None:
    """
    Coerce a column to datetime in-place, safely handling mixed Timestamp/str types.
    Runs unconditionally — pd.to_datetime with errors='coerce' is idempotent on
    already-datetime values and converts strings/mixed types safely.
    """
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')


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


def apply_current_row_calculation(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Generic conditional logic based on other columns in the current row.
    Respects strategy configuration for data preservation.
    """
    source_column = calculation.get('source_column')
    condition = calculation.get('condition')

    if source_column not in df.columns:
        return df

    engine._print_processing_step("Conditional", column_name, f"Evaluating {condition}")

    # Respect strategy configuration
    preservation_mode = _get_preservation_mode(engine, column_name)

    if column_name not in df.columns:
        df[column_name] = None

    if preservation_mode == "overwrite_existing":
        # Strategy: Calculate for ALL rows
        engine._print_processing_step("Conditional", column_name, f"Strategy: overwrite_existing - calculating all {len(df)} rows")
        if condition == 'is_current_submission':
            df[column_name] = df[source_column]
        else:
            df[column_name] = df[source_column]
        engine._print_processing_step("Conditional", column_name, f"Applied to all rows (overwritten)")
    else:
        # Strategy: preserve_existing - only fill null values
        null_mask = df[column_name].isna()
        if null_mask.any():
            if condition == 'is_current_submission':
                df.loc[null_mask, column_name] = df.loc[null_mask, source_column]
            else:
                df.loc[null_mask, column_name] = df.loc[null_mask, source_column]
            debug_print(f"Applied current_row calculation to {null_mask.sum()} null rows in {column_name}")
        else:
            debug_print(f"Skipped current_row calculation for {column_name}: all values present")

    return df


def apply_update_resubmission_required(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Logic for 'Update_Resubmission_Required'.
    Priority order (per schema):
    1. Keep NO if already NO
    2. Set to NO if submission is closed
    3. Set to RESUBMITTED if not the latest submission (resubmission already done)
    4. Set to PENDING if latest submission and awaiting review return
    5. Default to YES for remaining rows
    
    Respects strategy configuration for data preservation.
    """
    source_column = calculation.get('source_column', 'Resubmission_Required')
    dependencies = calculation.get('dependencies', [])
    
    # Task A1: Read column dependencies from calculation instead of hardcoding
    # Dependency order: Submission_Closed, Document_ID, Submission_Date, Review_Return_Actual_Date, Latest_Submission_Date
    submission_closed_col = dependencies[0] if len(dependencies) > 0 else 'Submission_Closed'
    document_id_col = dependencies[1] if len(dependencies) > 1 else 'Document_ID'
    submission_date_col = dependencies[2] if len(dependencies) > 2 else 'Submission_Date'
    review_return_col = dependencies[3] if len(dependencies) > 3 else 'Review_Return_Actual_Date'
    latest_submission_date_col = dependencies[4] if len(dependencies) > 4 else 'Latest_Submission_Date'

    # Task A2: Read status values from schema allowed_values
    column_def = engine.columns.get(column_name, {})
    validation = column_def.get('validation', [])
    allowed_values = next((v.get('allowed_values', []) for v in validation if v.get('type') == 'allowed_values'), [])
    
    # Map status values from schema or use current defaults as fallback
    val_yes = allowed_values[0] if len(allowed_values) > 0 else 'YES'
    val_no = allowed_values[1] if len(allowed_values) > 1 else 'NO'
    val_resub = allowed_values[2] if len(allowed_values) > 2 else 'RESUBMITTED'
    val_pen = allowed_values[3] if len(allowed_values) > 3 else 'PEN'

    engine._print_processing_step("Conditional", column_name, f"Checking rejection/resubmission logic from {source_column}")

    # Respect strategy configuration
    preservation_mode = _get_preservation_mode(engine, column_name)

    if column_name not in df.columns:
        df[column_name] = None

    # Determine which rows to process
    if preservation_mode == "overwrite_existing":
        engine._print_processing_step("Conditional", column_name, f"Strategy: overwrite_existing - processing all {len(df)} rows")
        null_mask = pd.Series([True] * len(df), index=df.index)
    else:
        # Calculate only for null values (default)
        existing_mask = df[column_name].notna()
        if existing_mask.any():
            engine._print_processing_step("Conditional", column_name, f"Preserving {existing_mask.sum()} existing values")
        
        null_mask = df[column_name].isna()
        if not null_mask.any():
            debug_print(f"Skipped update_resubmission_required for {column_name}: all values present")
            return df
    
    # Initialize target values with default YES
    df.loc[null_mask, column_name] = val_yes

    # Track which rows have been determined - these skip remaining checks
    determined_mask = pd.Series([False] * len(df), index=df.index)

    # Condition 1: Keep NO if already NO
    if source_column in df.columns:
        mask_already_no = df[source_column] == val_no
        df.loc[mask_already_no, column_name] = val_no
        determined_mask |= mask_already_no

    # Condition 2: Set to NO if submission is closed (skip rows already determined)
    if submission_closed_col in df.columns:
        mask_closed = (df[submission_closed_col] == val_yes) & ~determined_mask
        df.loc[mask_closed, column_name] = val_no
        determined_mask |= mask_closed

    # Condition 3: Set to RESUBMITTED if not the latest submission (skip rows already determined)
    if document_id_col in df.columns and submission_date_col in df.columns:
        _coerce_date_col(df, submission_date_col)
        # Use Latest_Submission_Date column if available as dependency, otherwise calculate
        if latest_submission_date_col in df.columns:
            _coerce_date_col(df, latest_submission_date_col)
            latest_dates = df[latest_submission_date_col]
        else:
            latest_dates = df.groupby(document_id_col)[submission_date_col].transform('max')
            
        mask_not_latest = (df[submission_date_col] < latest_dates) & ~determined_mask
        df.loc[mask_not_latest, column_name] = val_resub
        determined_mask |= mask_not_latest

    # Condition 4: Set to PEN if latest submission and awaiting review return
    if review_return_col in df.columns and submission_date_col in df.columns and document_id_col in df.columns:
        _coerce_date_col(df, review_return_col)
        _coerce_date_col(df, submission_date_col)
        # Re-verify latest_dates
        if latest_submission_date_col in df.columns:
            _coerce_date_col(df, latest_submission_date_col)
            latest_dates = df[latest_submission_date_col]
        else:
            latest_dates = df.groupby(document_id_col)[submission_date_col].transform('max')
            
        mask_pending = (
            (df[submission_date_col] == latest_dates) &
            df[review_return_col].isna() &
            ~determined_mask
        )
        df.loc[mask_pending, column_name] = val_pen
        determined_mask |= mask_pending

    # Condition 5: Default YES - already set for all remaining undetermined rows

    engine._print_processing_step("Conditional", column_name, 
        f"Applied: {(df[column_name] == val_no).sum()} {val_no}, {(df[column_name] == val_resub).sum()} {val_resub}, "
        f"{(df[column_name] == val_pen).sum()} {val_pen}, {(df[column_name] == val_yes).sum()} {val_yes}")
    return df


def apply_submission_closure_status(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Determines if a submission sequence is 'Closed' or 'Open'.
    Priority order:
    1. Keep YES if already YES
    2. Set to YES if current submission is not the latest (superseded by newer submission)
    3. Set to YES if Latest_Approval_Code in approval list (terminal status)
    4. Default to NO for remaining rows

    Note: Does NOT depend on Resubmission_Required to avoid circular dependency.
    Respects strategy configuration for data preservation.
    """
    source_column = calculation.get('source_column', 'Submission_Closed')
    dependencies = calculation.get('dependencies', [])
    
    # Task A1: Read column dependencies
    # Dependency order: Latest_Approval_Code, Document_ID, Submission_Date, Latest_Submission_Date
    latest_approval_col = dependencies[0] if len(dependencies) > 0 else 'Latest_Approval_Code'
    document_id_col = dependencies[1] if len(dependencies) > 1 else 'Document_ID'
    submission_date_col = dependencies[2] if len(dependencies) > 2 else 'Submission_Date'
    latest_submission_date_col = dependencies[3] if len(dependencies) > 3 else 'Latest_Submission_Date'

    # Task A2: Read status values
    column_def = engine.columns.get(column_name, {})
    validation = column_def.get('validation', [])
    allowed_values = next((v.get('allowed_values', []) for v in validation if v.get('type') == 'allowed_values'), [])
    val_yes = allowed_values[0] if len(allowed_values) > 0 else 'YES'
    val_no = allowed_values[1] if len(allowed_values) > 1 else 'NO'

    engine._print_processing_step("Conditional", column_name, "Evaluating closure status")

    # Respect strategy configuration
    preservation_mode = _get_preservation_mode(engine, column_name)

    if column_name not in df.columns:
        df[column_name] = None

    # Determine which rows to process
    if preservation_mode == "overwrite_existing":
        engine._print_processing_step("Conditional", column_name, f"Strategy: overwrite_existing - processing all {len(df)} rows")
        null_mask = pd.Series([True] * len(df), index=df.index)
    else:
        # Calculate only for null values (default)
        existing_mask = df[column_name].notna()
        if existing_mask.any():
            engine._print_processing_step("Conditional", column_name, f"Preserving {existing_mask.sum()} existing values")
        
        null_mask = df[column_name].isna()
        if not null_mask.any():
            debug_print(f"Skipped submission_closure_status for {column_name}: all values present")
            return df

    # Preprocessing: convert to uppercase and fill nulls
    preprocessing = calculation.get('preprocessing', {})
    text_cleaning = preprocessing.get('text_cleaning', {})
    if text_cleaning.get('convert_to_uppercase') and source_column in df.columns:
        df[source_column] = df[source_column].str.upper()
    if text_cleaning.get('fill_nulls') and source_column in df.columns:
        df[source_column] = df[source_column].fillna(text_cleaning['fill_nulls'])

    # Initialize target values with default NO
    df.loc[null_mask, column_name] = val_no

    # Track which rows have been determined - these skip remaining checks
    determined_mask = pd.Series([False] * len(df), index=df.index)

    # Condition 1: Keep YES if already YES
    if source_column in df.columns:
        mask_already_yes = (df[source_column] == val_yes) & ~determined_mask
        df.loc[mask_already_yes, column_name] = val_yes
        determined_mask |= mask_already_yes

    # Condition 2: Set to YES if current submission is not the latest (superseded)
    if document_id_col in df.columns and submission_date_col in df.columns:
        _coerce_date_col(df, submission_date_col)
        if latest_submission_date_col in df.columns:
            _coerce_date_col(df, latest_submission_date_col)
            latest_dates = df[latest_submission_date_col]
        else:
            latest_dates = df.groupby(document_id_col)[submission_date_col].transform('max')
            
        mask_not_latest = (df[submission_date_col] < latest_dates) & ~determined_mask
        df.loc[mask_not_latest, column_name] = val_yes
        determined_mask |= mask_not_latest

    # Condition 3: Set to YES if Latest_Approval_Code is in terminal approval list
    if latest_approval_col in df.columns:
        # Task A3: Read from engine.schema_data['approval_codes'] filtered by status
        approval_entries = engine.schema_data.get('approval_codes', [])
        # Terminal status list (Approved, Void, For Information)
        terminal_statuses = ['Approved', 'Void', 'For Information']
        approval_codes = [
            entry['code'] for entry in approval_entries 
            if entry.get('status') in terminal_statuses
        ]
        if not approval_codes:
            approval_codes = ['APP', 'VOID', 'INF'] # Fallback
            
        mask_approved = df[latest_approval_col].isin(approval_codes) & ~determined_mask
        df.loc[mask_approved, column_name] = val_yes
        determined_mask |= mask_approved

    # Condition 4: Default NO - already set for all remaining undetermined rows

    return df


def apply_calculate_overdue_status(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Calculates if a document is overdue by comparing Resubmission_Plan_Date
    against current date.

    Expanded 5-value logic matrix (Phase 3):
    1. OVERDUE_RESUBMITTED: Required=RESUBMITTED and Plan_Date < today
    2. RESUBMITTED: Required=RESUBMITTED and Plan_Date >= today
    3. NO: Required=NO or Submission_Closed=YES
    4. OVERDUE: Required=YES and Plan_Date < today
    5. ON_TRACK: Required=YES and Plan_Date >= today
    
    Respects strategy configuration for data preservation.
    """
    dependencies = calculation.get('dependencies', [])
    
    # Dependency order: Resubmission_Required, Resubmission_Plan_Date, Submission_Closed
    resubmission_required_col = dependencies[0] if len(dependencies) > 0 else 'Resubmission_Required'
    resubmission_plan_date_col = dependencies[1] if len(dependencies) > 1 else 'Resubmission_Plan_Date'
    submission_closed_col = dependencies[2] if len(dependencies) > 2 else 'Submission_Closed'

    # Read status values from schema allowed_values
    column_def = engine.columns.get(column_name, {})
    validation = column_def.get('validation', [])
    allowed_values = next((v.get('allowed_values', []) for v in validation if v.get('type') == 'allowed_values'), [])
    
    # Map status values: [OVERDUE_RESUBMITTED, OVERDUE, RESUBMITTED, ON_TRACK, NO]
    val_overdue_resub = allowed_values[0] if len(allowed_values) > 0 else 'OVERDUE_RESUBMITTED'
    val_overdue = allowed_values[1] if len(allowed_values) > 1 else 'OVERDUE'
    val_resubmitted = allowed_values[2] if len(allowed_values) > 2 else 'RESUBMITTED'
    val_on_track = allowed_values[3] if len(allowed_values) > 3 else 'ON_TRACK'
    val_no = allowed_values[4] if len(allowed_values) > 4 else 'NO'

    engine._print_processing_step("Conditional", column_name, f"Calculating 5-value overdue matrix")

    # Respect strategy configuration
    preservation_mode = _get_preservation_mode(engine, column_name)

    if column_name not in df.columns:
        df[column_name] = pd.NA

    # Determine which rows to process
    if preservation_mode == "overwrite_existing":
        engine._print_processing_step("Conditional", column_name, f"Strategy: overwrite_existing - processing all {len(df)} rows")
        null_mask = pd.Series([True] * len(df), index=df.index)
    else:
        null_mask = df[column_name].isna()
        if not null_mask.any():
            debug_print(f"Skipped overdue calculation for {column_name}: all values present")
            return df

    if resubmission_required_col in df.columns and resubmission_plan_date_col in df.columns:
        # Ensure plan date is datetime
        _coerce_date_col(df, resubmission_plan_date_col)
        current_date = pd.Timestamp.now().normalize()

        # Build masks for conditions
        required = df[resubmission_required_col].astype(str).str.upper()
        plan_dates = df[resubmission_plan_date_col]
        closed = df[submission_closed_col].astype(str).str.upper() if submission_closed_col in df.columns else pd.Series(['NO'] * len(df), index=df.index)

        # 1. OVERDUE_RESUBMITTED: Required=RESUBMITTED and Plan_Date < today
        mask_overdue_resub = (required == 'RESUBMITTED') & (plan_dates.notna()) & (plan_dates < current_date)
        
        # 2. RESUBMITTED: Required=RESUBMITTED and Plan_Date >= today
        mask_resubmitted = (required == 'RESUBMITTED') & ((plan_dates.isna()) | (plan_dates >= current_date))
        
        # 3. NO: Required=NO or (Submission_Closed=YES AND Required != RESUBMITTED)
        # RESUBMITTED rows with Closed=YES are handled by conditions 1-2 (RESUBMITTED takes priority over Closed)
        mask_no = (required == 'NO') | ((closed == 'YES') & (required != 'RESUBMITTED'))
        
        # 4. OVERDUE: Required=YES and Plan_Date < today
        mask_overdue = (required == 'YES') & (plan_dates.notna()) & (plan_dates < current_date)
        
        # 5. ON_TRACK: Required=YES and (Plan_Date is null or Plan_Date >= today)
        # Note: If Required=YES but Plan_Date is null, we treat as ON_TRACK (waiting for plan)
        mask_on_track = (required == 'YES') & ((plan_dates.isna()) | (plan_dates >= current_date))

        # Apply values to null rows
        df.loc[null_mask & mask_overdue_resub, column_name] = val_overdue_resub
        df.loc[null_mask & mask_resubmitted, column_name] = val_resubmitted
        df.loc[null_mask & mask_no, column_name] = val_no
        df.loc[null_mask & mask_overdue, column_name] = val_overdue
        df.loc[null_mask & mask_on_track, column_name] = val_on_track
        
        # Final fallback for any remaining nulls in the null_mask
        df.loc[null_mask & df[column_name].isna(), column_name] = val_no

        engine._print_processing_step("Conditional", column_name, 
            f"Result: {(df[column_name] == val_overdue).sum()} {val_overdue}, "
            f"{(df[column_name] == val_on_track).sum()} {val_on_track}, "
            f"{(df[column_name] == val_resubmitted).sum()} {val_resubmitted}, "
            f"{(df[column_name] == val_overdue_resub).sum()} {val_overdue_resub}")
    else:
        engine._print_processing_step("Conditional", column_name, "Cannot calculate: missing dependencies")

    return df

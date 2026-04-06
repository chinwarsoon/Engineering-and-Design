"""
Logic that depends on row states, such as _apply_conditional_calculation,
_apply_update_resubmission_required, and _apply_submission_closure_status.
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
    engine._print_processing_step("Conditional", column_name, "Evaluating row-level logic")
    
    # Example: If Column A is X and Column B is Y, then Column C is Z
    # This is often implemented using np.select or a custom lambda
    return df

def apply_update_resubmission_required(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Logic for 'Update_Resubmission_Required'.
    Usually returns 'Yes' if Review_Status is 'Rejected' or 'Approved with Comments'.
    """
    status_col = calculation.get('source_column', 'Review_Status')
    
    if status_col not in df.columns:
        return df

    engine._print_processing_step("Conditional", column_name, f"Checking rejection status in {status_col}")

    # Define rejection-type statuses (can also be pulled from schema references)
    rejection_statuses = ['Rejected', 'Revise and Resubmit', 'Resubmit']
    
    df[column_name] = df[status_col].apply(
        lambda x: 'Yes' if str(x).strip() in rejection_statuses else 'No'
    )
    
    return df

def apply_submission_closure_status(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Determines if a submission sequence is 'Closed' or 'Open'.
    Logic: If the latest version is 'Approved', the status is 'Closed'.
    """
    status_col = calculation.get('source_column', 'Review_Status')
    
    if status_col not in df.columns:
        return df

    engine._print_processing_step("Conditional", column_name, "Evaluating closure status")

    df[column_name] = df[status_col].apply(
        lambda x: 'Closed' if str(x).strip() == 'Approved' else 'Open'
    )
    
    return df

def apply_calculate_overdue_status(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Calculates if a document is overdue by comparing a 'Planned Date' 
    against 'Today' or an 'Actual Date'.
    """
    planned_date_col = calculation.get('planned_date_column')
    actual_date_col = calculation.get('actual_date_column')
    
    if planned_date_col not in df.columns:
        return df

    engine._print_processing_step("Conditional", column_name, "Calculating Overdue/On-Track")

    today = pd.Timestamp.now().normalize()
    
    def evaluate_overdue(row):
        planned = pd.to_datetime(row.get(planned_date_col), errors='coerce')
        actual = pd.to_datetime(row.get(actual_date_col), errors='coerce') if actual_date_col in row else pd.NaT
        
        if pd.isna(planned):
            return "Pending"
        
        # If already submitted/returned
        if pd.notna(actual):
            return "Completed"
            
        # If planned date has passed and no actual date exists
        if planned < today:
            return "Overdue"
            
        return "On-Track"

    df[column_name] = df.apply(evaluate_overdue, axis=1)
    
    return df
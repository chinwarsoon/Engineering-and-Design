"""
Composite calculations: document ID building, row indexing, and complex lookups.
Extracted from UniversalDocumentProcessor composite and lookup methods.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

# Import hierarchical logging functions from utility_engine
from utility_engine.console import status_print, debug_print


def _get_preservation_mode(engine, column_name: str) -> str:
    """
    Get data preservation mode from engine strategy if available.
    Defaults to 'preserve_existing' for backward compatibility.
    """
    # Check if engine has strategy resolver (new strategy-aware engine)
    if hasattr(engine, 'get_column_strategy'):
        try:
            strategy = engine.get_column_strategy(column_name)
            if strategy:
                return strategy.preservation_mode.value
        except Exception:
            pass  # Fall back to default
    
    # Check if strategy is in column definition (passed via calculation dict)
    # This allows strategy to be passed through calculation config
    return "preserve_existing"  # Default behavior


def _identify_id_malformation(value: str) -> Optional[str]:
    """
    Identify specific malformation type for Document_ID.
    Returns the error code suffix or None if not specifically malformed.
    """
    if not value or pd.isna(value):
        return None
    
    # E: Reply/Comment reference
    if any(keyword in value.upper() for keyword in ["REPLY", "COMMENT", "RESPONSE"]):
        return "E"
    
    # F: Spaces in segments
    if " " in value.strip():
        return "F"
    
    # H: Special characters (dots, parentheses, etc.)
    if any(char in value for char in "().,;:+*#?!@%^&="):
        return "H"
        
    segments = value.split('-')
    # G: Wrong segment count
    if len(segments) != 5:
        # Check if it has an affix that was not stripped yet
        if '_' in value:
            base_part = value.split('_')[0]
            if len(base_part.split('-')) != 5:
                return "G"
        else:
            return "G"
            
    # D: NA segments
    if "NA" in segments:
        return "D"
        
    return None


def apply_composite_calculation(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Apply composite calculation using row-by-row formatting.
    Builds values by combining multiple source columns with a format string.
    
    Phase 2 Enhancements:
    - Pre-validation of source columns
    - Affix extraction for Document_ID
    - Specific error flagging for malformed IDs
    """
    source_columns = calculation.get('sources') or calculation.get('source_columns', [])
    format_string = calculation.get('format', '')

    if not format_string:
        engine._print_processing_step("Composite", column_name, "ERROR: No format string provided")
        return df

    # Verify which sources exist in df
    available_sources = [col for col in source_columns if col in df.columns]

    if not available_sources:
        engine._print_processing_step("Composite", column_name, "ERROR: No available source columns")
        return df

    engine._print_processing_step("Composite", column_name, f"Formatting with {len(available_sources)}/{len(source_columns)} sources")

    # Document_ID specific handling (Phase 2)
    is_doc_id = column_name == "Document_ID"
    affix_col = "Document_ID_Affixes"
    
    # Import affix extractor if needed
    extract_fn = None
    if is_doc_id:
        try:
            from .affix_extractor import extract_document_id_affixes
            extract_fn = extract_document_id_affixes
        except ImportError:
            pass

    def format_row(row):
        try:
            # Pre-validation (Phase 2): Check for malformed source data
            # If any source contains NA or invalid text, it will propagate to the formatted string
            values = {col: 'NA' if pd.isna(row.get(col)) or str(row.get(col)).strip() == '' else str(row[col]).strip() for col in available_sources}
            
            # Check for NA segments (Phase 2 Case 2)
            if is_doc_id and any(v == 'NA' for v in values.values()):
                # We still format it, but it will be flagged by identity detector later
                pass
                
            formatted = format_string.format(**values)
            
            # Affix Extraction (Phase 2 Case 1)
            if is_doc_id and extract_fn and '_' in formatted:
                base, affix = extract_fn(formatted)
                # Store affix in row if we had a way to return multiple values, 
                # but format_row only returns the column value. 
                # We handle storing affix in a separate vectorized step for efficiency.
                return base
                
            return formatted
        except Exception:
            return "ERR-COMPOSITE"

    df = df.copy()

    # Initialize column if not exists
    if column_name not in df.columns:
        df[column_name] = np.nan

    # Get preservation mode from strategy
    preservation_mode = _get_preservation_mode(engine, column_name)
    
    # Determine rows to calculate
    if preservation_mode == "overwrite_existing":
        calc_mask = pd.Series(True, index=df.index)
    else:
        calc_mask = df[column_name].isna()

    if calc_mask.any():
        df.loc[calc_mask, column_name] = df.loc[calc_mask, available_sources].apply(format_row, axis=1)
        
        # Post-process Document_ID to extract affixes (Phase 2 Case 1)
        if is_doc_id and extract_fn:
            if affix_col not in df.columns:
                df[affix_col] = ""
            
            # Vectorized affix extraction for the newly calculated rows
            # This ensures Document_ID is clean and Affixes are stored
            doc_ids = df.loc[calc_mask, column_name].astype(str)
            affix_results = doc_ids.apply(lambda x: extract_fn(x) if '_' in x else (x, ""))
            
            df.loc[calc_mask, column_name] = affix_results.apply(lambda x: x[0])
            # Only update affix if it was empty or we are in overwrite mode
            affix_update_mask = calc_mask & (df[affix_col].isna() | (df[affix_col] == ""))
            df.loc[affix_update_mask, affix_col] = affix_results.loc[affix_update_mask].apply(lambda x: x[1])

        engine._print_processing_step("Composite", column_name, f"Applied to {calc_mask.sum()} rows")

    return df


def apply_row_index(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Generate or preserve auto-increment row index starting from 1.

    This creates a unique index for each row in the imported data,
    useful for tracking original row positions.
    The Row_Index column is placed as the first column in the DataFrame.
    """
    df = df.copy()

    # Only generate row index where null - preserve existing values
    if column_name not in df.columns:
        df[column_name] = None

    null_mask = df[column_name].isna()
    if null_mask.any():
        df.loc[null_mask, column_name] = range(1, null_mask.sum() + 1)
        engine._print_processing_step("Row-Index", column_name, f"Applied to {null_mask.sum()} null rows")
    else:
        debug_print(f"Skipped row index for {column_name}: all values present")

    # Move column to front
    cols = df.columns.tolist()
    if column_name in cols:
        cols.remove(column_name)
        df = df[[column_name] + cols]

    return df


def apply_delay_of_resubmission(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Calculate Delay_of_Resubmission — delay is stored on the row whose plan was missed.

    For each submission row:
        delay = max(next_Submission_Date − current_Resubmission_Plan_Date, 0)

    Where "next submission" = the immediately following submission for the same Document_ID
    (sorted by Submission_Date ascending).

    Special case — latest row with no next submission yet (ISS-014):
        If Review_Return_Actual_Date is not null AND Resubmission_Plan_Date < today
        AND Submission_Closed != terminal:
            delay = max(today − Resubmission_Plan_Date, 0)
        Otherwise: 0

    Terminal closure override: Latest_Approval_Code in terminal codes (APP/VOID/INF) → 0.
    Superseded rows (closed only because a newer submission exists) still carry their delay.
    """
    dependencies = calculation.get('dependencies', [])

    # Dependency order: Submission_Closed, Document_ID, Submission_Date,
    #                   Resubmission_Plan_Date, Review_Return_Actual_Date, Latest_Submission_Date
    closed_col            = dependencies[0] if len(dependencies) > 0 else 'Submission_Closed'
    doc_id_col            = dependencies[1] if len(dependencies) > 1 else 'Document_ID'
    submission_date_col   = dependencies[2] if len(dependencies) > 2 else 'Submission_Date'
    plan_date_col         = dependencies[3] if len(dependencies) > 3 else 'Resubmission_Plan_Date'
    review_return_col     = dependencies[4] if len(dependencies) > 4 else 'Review_Return_Actual_Date'
    latest_submission_col = dependencies[5] if len(dependencies) > 5 else 'Latest_Submission_Date'

    required_cols = [doc_id_col, submission_date_col, plan_date_col, closed_col]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        engine._print_processing_step("Complex-Lookup", column_name, f"ERROR: Missing columns: {missing_cols}")
        df = df.copy()
        df[column_name] = 0
        return df

    engine._print_processing_step("Complex-Lookup", column_name,
        "Calculating delay — stored on the row whose plan was missed")

    df = df.copy()

    if column_name not in df.columns:
        df[column_name] = None

    # Always recalculate — overwrite_existing strategy
    # Delay values must reflect current pipeline state, not preserved from prior runs.
    existing_count = df[column_name].notna().sum()
    if existing_count:
        engine._print_processing_step("Complex-Lookup", column_name,
            f"Overwriting {existing_count} existing values (overwrite_existing strategy)")

    df[submission_date_col] = pd.to_datetime(df[submission_date_col], errors='coerce')
    df[plan_date_col] = pd.to_datetime(df[plan_date_col], errors='coerce')

    # ----------------------------------------------------------------
    # Path 1: Forward-looking — delay on the row whose plan was missed
    # For each row: next_Submission_Date − current_Resubmission_Plan_Date
    # Vectorised: sort by [Document_ID, Submission_Date], shift(-1) to get
    # the next row's Submission_Date within each group, then compute diff.
    # ----------------------------------------------------------------
    df_sorted = df[[doc_id_col, submission_date_col, plan_date_col]].copy()
    df_sorted = df_sorted.sort_values([doc_id_col, submission_date_col])

    # next_submission_date: the Submission_Date of the immediately following row
    # within the same Document_ID group. NaT for the last row in each group.
    df_sorted['_next_sub_date'] = (
        df_sorted.groupby(doc_id_col)[submission_date_col]
        .transform(lambda s: s.shift(-1))
    )

    next_sub_date = df_sorted['_next_sub_date'].reindex(df.index)

    # delay = next_Submission_Date − current_Resubmission_Plan_Date, clamp ≥ 0
    delay = (next_sub_date - df[plan_date_col]).dt.days.fillna(0).clip(lower=0).fillna(0).astype(int)

    # ----------------------------------------------------------------
    # Path 2: Latest row, active overdue — no next submission yet (ISS-014)
    # Review has been returned, plan date has passed, resubmission not made.
    # delay = max(today − Resubmission_Plan_Date, 0)
    # ----------------------------------------------------------------
    today = pd.Timestamp.now().normalize()

    if latest_submission_col in df.columns:
        df[latest_submission_col] = pd.to_datetime(df[latest_submission_col], errors='coerce')
        latest_dates = df[latest_submission_col]
    else:
        latest_dates = df.groupby(doc_id_col)[submission_date_col].transform('max')

    if review_return_col in df.columns:
        df[review_return_col] = pd.to_datetime(df[review_return_col], errors='coerce')
        has_review_return = df[review_return_col].notna()
    else:
        has_review_return = pd.Series(False, index=df.index)

    # Read schema YES value for Submission_Closed
    column_def = engine.columns.get(closed_col, {})
    validation = column_def.get('validation', [])
    allowed_values = next(
        (v.get('allowed_values', []) for v in validation if v.get('type') == 'allowed_values'), []
    )
    val_yes = allowed_values[0] if len(allowed_values) > 0 else 'YES'

    # Resolve terminal approval codes (same source as Resubmission_Plan_Date ISS-013)
    approval_entries = engine.schema_data.get('approval_codes', [])
    terminal_statuses = ['Approved', 'Void', 'For Information']
    terminal_codes = [
        entry['code'] for entry in approval_entries
        if entry.get('status') in terminal_statuses
    ]
    if not terminal_codes:
        terminal_codes = ['APP', 'VOID', 'INF']

    # Resolve Latest_Approval_Code for terminal check
    latest_approval_col = 'Latest_Approval_Code'
    if latest_approval_col in df.columns:
        is_terminal = df[latest_approval_col].isin(terminal_codes)
    else:
        is_terminal = pd.Series(False, index=df.index)

    # Path 2 mask: latest row, not terminally closed, review returned, plan date past
    mask_active_overdue = (
        (df[submission_date_col] == latest_dates)  # latest submission for this document
        & ~is_terminal                              # not terminally closed
        & has_review_return                         # review has been returned
        & df[plan_date_col].notna()                # plan date exists
        & (df[plan_date_col] < today)              # plan date has passed
    )

    if mask_active_overdue.any():
        active_delay = (today - df[plan_date_col]).dt.days.fillna(0).clip(lower=0).fillna(0).astype(int)
        delay[mask_active_overdue] = active_delay[mask_active_overdue]
        engine._print_processing_step(
            "Complex-Lookup", column_name,
            f"Path 2 (active overdue): {mask_active_overdue.sum()} rows — "
            f"delay = today − Resubmission_Plan_Date"
        )

    # ----------------------------------------------------------------
    # Terminal override: terminally closed rows → 0
    # Superseded rows (Submission_Closed=YES but not terminal) keep their delay.
    # ----------------------------------------------------------------
    delay[is_terminal] = 0

    # Apply to all rows (overwrite_existing strategy)
    df[column_name] = delay
    engine._print_processing_step(
        "Complex-Lookup", column_name,
        f"Applied to all {len(df)} rows: {(delay > 0).sum()} rows with positive delay"
    )

    return df


def apply_copy_calculation(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Apply direct copy calculation.
    Simply copies values from a source column to the target column.
    """
    source_column = calculation.get('source_column')

    if source_column not in df.columns:
        engine._print_processing_step("Copy", column_name, f"ERROR: Source column {source_column} not found")
        return df

    engine._print_processing_step("Copy", column_name, f"Copying from {source_column}")

    df = df.copy()

    # Initialize column if not exists
    if column_name not in df.columns:
        df[column_name] = None

    # Get existing non-null values
    existing_mask = df[column_name].notna()
    if existing_mask.any():
        engine._print_processing_step("Copy", column_name, f"Preserving {existing_mask.sum()} existing values")

    # Only copy to null values
    null_mask = df[column_name].isna()
    if null_mask.any():
        df.loc[null_mask, column_name] = df.loc[null_mask, source_column]
        engine._print_processing_step("Copy", column_name, f"Applied to {null_mask.sum()} null rows")
    else:
        debug_print(f"Skipped copy for {column_name}: all values present")

    return df


def apply_extract_affixes(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Extract affixes from Document_ID and store in Document_ID_Affixes column.
    
    Issue #16: Document_ID affix handling
    
    Reads schema parameters:
    - delimiter: from Document_ID.validation.derived_pattern.separator
    - sequence_length: from Document_Sequence_Number.validation.pattern
    
    Args:
        engine: The processing engine
        df: DataFrame with Document_ID column
        column_name: Target column (Document_ID_Affixes)
        calculation: Calculation configuration with source_column
        
    Returns:
        DataFrame with Document_ID_Affixes column populated
    """
    # Import affix extractor
    try:
        from .affix_extractor import extract_document_id_affixes
    except ImportError:
        engine._print_processing_step("Extract Affixes", column_name, "ERROR: affix_extractor not available")
        return df
    
    # Get source column (usually Document_ID)
    source_column = calculation.get('source_column', 'Document_ID')
    
    if source_column not in df.columns:
        engine._print_processing_step("Extract Affixes", column_name, f"ERROR: Source column {source_column} not found")
        return df
    
    # Get schema parameters
    delimiter = calculation.get('delimiter', '-')
    sequence_length = calculation.get('sequence_length', 4)
    
    # Extract affixes
    engine._print_processing_step("Extract Affixes", column_name, f"Extracting from {source_column}")
    
    df = df.copy()
    
    # Apply affix extraction to each row
    affix_results = df[source_column].apply(
        lambda x: extract_document_id_affixes(
            str(x) if pd.notna(x) else '',
            delimiter=delimiter,
            sequence_length=sequence_length
        ) if pd.notna(x) else ('', '')
    )
    
    # Extract affix part (second element of tuple)
    df[column_name] = affix_results.apply(lambda x: x[1])
    
    affix_count = df[column_name].ne('').sum()
    engine._print_processing_step("Extract Affixes", column_name, f"Extracted {affix_count} affixes")
    
    return df

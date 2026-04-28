"""
Data I/O utilities for loading Excel and other data sources.
"""
from pathlib import Path
from typing import Any, Dict, Callable

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


def load_excel_data(
    excel_path: Path,
    effective_parameters: Dict[str, Any],
    nrows: int | None = None,
    verbose: bool = True,
    status_print_fn: Callable = print,
    context: Any = None,
) -> Any:
    """
    Load Excel data with specified parameters.
    
    Args:
        excel_path: Path to Excel file
        effective_parameters: Dictionary containing upload_sheet_name, header_row_index,
                             start_col, end_col parameters
        nrows: Optional row limit
        verbose: Whether to print status messages
        status_print_fn: Function to print status messages (default: print)
        context: Optional PipelineContext to store raw data and telemetry
        
    Returns:
        pandas.DataFrame with loaded data
    """
    if not HAS_PANDAS:
        raise ImportError("pandas is required for load_excel_data")
    
    # Extract params from context if provided
    params = context.parameters if context else effective_parameters
    sheet_name = params.get("upload_sheet_name", "Prolog Submittals ")
    header_row = params.get("header_row_index", 4)
    start_col = params.get("start_col", "P")
    end_col = params.get("end_col", "AP")
    usecols = f"{start_col}:{end_col}"
    
    if verbose:
        status_print_fn(f"📁 Loading Excel file: {excel_path}")
        status_print_fn(f"   Sheet: '{sheet_name}'")
        status_print_fn(f"   Header row: {header_row + 1}")
        status_print_fn(f"   Column range: {start_col}:{end_col}")
    
    df = pd.read_excel(
        excel_path,
        sheet_name=sheet_name,
        header=header_row,
        usecols=usecols,
        nrows=nrows or (context.nrows if context else None),
    )
    
    if len(df.columns) == 0:
        raise ValueError(f"No columns loaded from {excel_path}")
    
    # Flatten columns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join(str(level) for level in levels).strip('_') for levels in df.columns]
    
    # Cleanup
    df = df.loc[:, ~df.columns.duplicated()].copy()
    df = df.dropna(axis=1, how='all')
    
    if verbose:
        status_print_fn(f"   ✓ Loaded {len(df)} rows × {len(df.columns)} columns")
    
    if context:
        context.data.df_raw = df
        if "rows_loaded" not in context.telemetry.data_metrics:
            context.telemetry.data_metrics["rows_loaded"] = len(df)
            
    return df

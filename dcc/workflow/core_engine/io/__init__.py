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
        
    Returns:
        pandas.DataFrame with loaded data
        
    Raises:
        ImportError: If pandas is not available
        ValueError: If no columns loaded or invalid parameters
    """
    if not HAS_PANDAS:
        raise ImportError("pandas is required for load_excel_data")
    
    sheet_name = effective_parameters.get("upload_sheet_name", "Prolog Submittals ")
    header_row = effective_parameters.get("header_row_index", 4)
    start_col = effective_parameters.get("start_col", "P")
    end_col = effective_parameters.get("end_col", "AP")
    usecols = f"{start_col}:{end_col}"
    
    if verbose:
        status_print_fn(f"📁 Loading Excel file: {excel_path}")
        status_print_fn(f"   Sheet: '{sheet_name}'")
        status_print_fn(f"   Header row: {header_row + 1} (0-indexed: {header_row})")
        status_print_fn(f"   Column range: {start_col}:{end_col}")
        status_print_fn(f"   Row limit: {nrows if nrows else 'all'}")
    
    df = pd.read_excel(
        excel_path,
        sheet_name=sheet_name,
        header=header_row,
        usecols=usecols,
        nrows=nrows,
    )
    
    # Validate columns loaded
    if len(df.columns) == 0:
        raise ValueError(f"No columns loaded. Check header_row_index={header_row} and range {start_col}:{end_col}")
    
    # Flatten MultiIndex columns if present
    if isinstance(df.columns, pd.MultiIndex):
        if verbose:
            status_print_fn("   ⚠️  Flattening MultiIndex columns")
        df.columns = ['_'.join(str(level) for level in levels).strip('_') for levels in df.columns]
    
    # Remove duplicate columns
    if df.columns.duplicated().any():
        dup_cols = df.columns[df.columns.duplicated()].tolist()
        if verbose:
            status_print_fn(f"   ⚠️  Removing {len(dup_cols)} duplicate columns")
        df = df.loc[:, ~df.columns.duplicated()].copy()
    
    # Remove empty columns
    df = df.dropna(axis=1, how='all')
    
    if verbose:
        status_print_fn(f"   ✓ Loaded {len(df)} rows × {len(df.columns)} columns")
    
    return df

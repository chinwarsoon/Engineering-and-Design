"""
Data I/O utilities for loading Excel and other data sources.

This module follows the barrel pattern - it re-exports functionality from submodules.
"""
from core_engine.io.io_excel import (
    load_excel_data,
    HAS_PANDAS,
)

__all__ = [
    "load_excel_data",
    "HAS_PANDAS",
]

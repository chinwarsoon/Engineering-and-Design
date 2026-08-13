"""
common.library.export — Universal DataExporter (L22).

Provides human-readable CSV and Excel export from ``list[dict]`` rows.
No pandas dependency — works with plain dictionaries. Reusable by EKS, DCC,
and future pipeline projects.

Exports:
    DataExporter          — primary class with export_to_csv / export_to_excel
    export_to_csv         — standalone convenience function
    export_to_excel       — standalone convenience function
    export_multi_sheet    — standalone convenience function (alias)
    export_to_workbook    — standalone workbook export with per-sheet columns

Revision: 0.2
Date: 2026-08-13
Author: opencode
Summary: v0.2 (I309 T1.288): export_to_workbook exported — single-workbook
         export with optional per-sheet column control (columns: Dict[sheet, cols]).
         v0.1 (2026-07-18): Initial L22 universal export module — CSV (stdlib
         csv.DictWriter) + Excel (openpyxl.Workbook) with auto-column-width,
         BOM, bold headers.
"""

from .exporter import (
    DataExporter,
    export_to_csv,
    export_to_excel,
    export_multi_sheet,
    export_to_workbook,
)

__version__ = "0.2"
__all__ = [
    "DataExporter",
    "export_to_csv",
    "export_to_excel",
    "export_multi_sheet",
    "export_to_workbook",
]

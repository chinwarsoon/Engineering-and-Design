"""
common.library.export — Universal DataExporter (L22).

Provides human-readable CSV and Excel export from ``list[dict]`` rows.
No pandas dependency — works with plain dictionaries. Reusable by EKS, DCC,
and future pipeline projects.

Exports:
    DataExporter          — primary class with export_to_csv / export_to_excel
    export_to_csv         — standalone convenience function
    export_to_excel       — standalone convenience function
    export_multi_sheet    — standalone convenience function

Revision: 0.1
Date: 2026-07-18
Author: opencode
Summary: Initial L22 universal export module — CSV (stdlib csv.DictWriter) +
         Excel (openpyxl.Workbook) with auto-column-width, BOM, bold headers.
"""

from .exporter import DataExporter, export_to_csv, export_to_excel, export_multi_sheet

__version__ = "0.1"
__all__ = ["DataExporter", "export_to_csv", "export_to_excel", "export_multi_sheet"]

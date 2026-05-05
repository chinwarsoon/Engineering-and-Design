"""Reporting Engine Core Module.

Provides summary report generation for DCC pipeline processing.
"""

from .core.report_summary import (
    write_processing_summary,
    print_summary,
)
from .core.report_health import (
    DataHealthKPI,
    HealthCalculator,
    calculate_row_health_series,
)
from .core.report_errors import (
    ErrorReporter,
)

__all__ = [
    "write_processing_summary",
    "print_summary",
    "DataHealthKPI",
    "HealthCalculator",
    "calculate_row_health_series",
    "ErrorReporter",
]

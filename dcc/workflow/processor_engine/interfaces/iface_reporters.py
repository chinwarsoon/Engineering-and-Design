"""
Error reporter interfaces for processor engine.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class ErrorReporterInterface(ABC):
    """Interface for error reporting implementations."""

    @abstractmethod
    def export_dashboard_json(
        self, total_rows: int, filename: Optional[str] = None, context: Optional[Any] = None
    ) -> str:
        """Export error summary as JSON dashboard."""
        pass

    @abstractmethod
    def set_output_dir(self, output_dir: Any) -> None:
        """Set the output directory for reports."""
        pass


# Alias for backward compatibility with existing code
IErrorReporter = ErrorReporterInterface


class IErrorAggregator(ABC):
    """Interface for error aggregation implementations."""

    @abstractmethod
    def get_error_summary(self) -> Dict[str, Any]:
        """Get aggregated error summary."""
        pass

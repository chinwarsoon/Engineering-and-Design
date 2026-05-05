"""
Core interfaces for processor engine.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Protocol
import pandas as pd


class ICalculationEngine(ABC):
    """Interface for the main calculation engine."""

    @abstractmethod
    def process_data(self) -> None:
        """Process the data through all calculations."""
        pass

    @abstractmethod
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary from processing."""
        pass


class ISchemaProcessor(ABC):
    """Interface for schema processing."""

    @abstractmethod
    def reorder_dataframe(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Reorder dataframe columns per schema."""
        pass


# Protocol versions for lightweight interfaces
class ErrorReporterProtocol(Protocol):
    """Protocol for error reporter implementations."""
    output_dir: Any

    def export_dashboard_json(self, total_rows: int) -> str: ...


class LoggerProtocol(Protocol):
    """Protocol for logger implementations."""
    def log(self, message: str, level: str = "info", **kwargs) -> None: ...

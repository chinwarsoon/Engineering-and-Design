"""
Dependency Injection Interfaces for Processor Engine

Defines abstract interfaces for all injectable dependencies,
enabling swappable implementations, simplified testing, and platform flexibility.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Protocol
import pandas as pd


class IErrorReporter(ABC):
    """Interface for error reporting implementations."""
    
    @abstractmethod
    def export_dashboard_json(self, total_rows: int) -> str:
        """Export error summary as JSON dashboard."""
        pass
    
    @abstractmethod
    def set_output_dir(self, output_dir: Any) -> None:
        """Set the output directory for reports."""
        pass


class IErrorAggregator(ABC):
    """Interface for error aggregation implementations."""
    
    @abstractmethod
    def get_error_summary(self) -> Dict[str, Any]:
        """Get aggregated error summary."""
        pass


class IStructuredLogger(ABC):
    """Interface for structured logging implementations."""
    
    @abstractmethod
    def log(self, message: str, level: str = "info", **kwargs) -> None:
        """Log a structured message."""
        pass


class IBusinessDetector(ABC):
    """Interface for business rule detection implementations."""
    
    @abstractmethod
    def detect(self, data: pd.DataFrame, phase: str) -> List[Dict]:
        """Detect business rule violations."""
        pass


class IStrategyResolver(ABC):
    """Interface for calculation strategy resolution."""
    
    @abstractmethod
    def resolve(self, column_name: str, column_def: Dict) -> Any:
        """Resolve calculation strategy for a column."""
        pass


class ICalculationStrategy(ABC):
    """Interface for individual calculation strategies."""
    
    @abstractmethod
    def execute(self, df: pd.DataFrame, context: Dict) -> pd.Series:
        """Execute the calculation strategy."""
        pass


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


__all__ = [
    'IErrorReporter',
    'IErrorAggregator',
    'IStructuredLogger',
    'IBusinessDetector',
    'IStrategyResolver',
    'ICalculationStrategy',
    'ICalculationEngine',
    'ISchemaProcessor',
    'ErrorReporterProtocol',
    'LoggerProtocol',
]

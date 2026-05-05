"""
Detector interfaces for processor engine.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any
import pandas as pd


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

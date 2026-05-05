"""
Logger interfaces for processor engine.
"""
from abc import ABC, abstractmethod


class IStructuredLogger(ABC):
    """Interface for structured logging implementations."""

    @abstractmethod
    def log(self, message: str, level: str = "info", **kwargs) -> None:
        """Log a structured message."""
        pass

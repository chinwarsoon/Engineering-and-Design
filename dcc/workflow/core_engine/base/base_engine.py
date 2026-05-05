"""
Base engine class for all domain-specific engines.
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from core_engine.context.context_pipeline import PipelineContext

logger = logging.getLogger("core_engine.base")


class BaseEngine(ABC):
    """
    Abstract base class for all domain-specific engines in the DCC pipeline.
    """
    def __init__(self, context: PipelineContext):
        """
        Initialize the engine with the global pipeline context.

        Args:
            context: The PipelineContext containing paths, parameters, and state.
        """
        self.context = context

    @abstractmethod
    def run(self) -> Dict[str, Any]:
        """
        Execute the engine's primary lifecycle action.

        Returns:
            Dictionary containing engine-specific result details.
        """
        raise NotImplementedError

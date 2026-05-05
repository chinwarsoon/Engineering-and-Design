"""
Base engine class for all domain-specific engines.
"""
import logging
from typing import Dict, Any, Optional

from core_engine.context import PipelineContext

logger = logging.getLogger("core_engine.base")


class BaseEngine:
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

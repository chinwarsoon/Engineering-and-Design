"""
Core engine components for the document processor.
"""

from .base import BaseProcessor
from .engine import CalculationEngine
from .registry import (
    get_null_handler,
    get_calculation_handler,
    register_null_handler,
    register_calculation_handler,
    list_registered_handlers,
    NULL_HANDLERS,
    CALCULATION_HANDLERS,
)

__all__ = [
    'BaseProcessor',
    'CalculationEngine',
    'get_null_handler',
    'get_calculation_handler',
    'register_null_handler',
    'register_calculation_handler',
    'list_registered_handlers',
    'NULL_HANDLERS',
    'CALCULATION_HANDLERS',
]

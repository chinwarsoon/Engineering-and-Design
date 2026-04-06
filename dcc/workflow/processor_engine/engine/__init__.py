"""
Document Processor Engine

A modular engine for processing documents with schema-driven calculations,
null handling, and validation.
"""

from dcc.workflow.processor_engine.engine.core import (
    BaseProcessor,
    CalculationEngine,
    get_null_handler,
    get_calculation_handler,
    register_null_handler,
    register_calculation_handler,
    list_registered_handlers,
)

from dcc.workflow.processor_engine.engine.utils import load_excel_data

__all__ = [
    'BaseProcessor',
    'CalculationEngine',
    'get_null_handler',
    'get_calculation_handler',
    'register_null_handler',
    'register_calculation_handler',
    'list_registered_handlers',
    'load_excel_data',
]

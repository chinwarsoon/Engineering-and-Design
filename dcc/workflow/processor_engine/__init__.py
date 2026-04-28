"""
Document Processor Engine

A modular engine for processing documents with schema-driven calculations,
null handling, and validation.

Phase 2 DI Update: Added dependency injection support via interfaces and factories.
"""

from .core import (
    BaseProcessor,
    CalculationEngine,
    get_null_handler,
    get_calculation_handler,
    register_null_handler,
    register_calculation_handler,
    list_registered_handlers,
)

from .schema import SchemaProcessor
from .utils import load_excel_data

# Phase 2 DI: Export DI components
from . import interfaces
from . import factories
from .factories import (
    DependencyContainer,
    get_container,
    set_container,
    CalculationEngineFactory,
    SchemaProcessorFactory,
    create_calculation_engine,
    create_calculation_engine_legacy,
)

__all__ = [
    'BaseProcessor',
    'CalculationEngine',
    'SchemaProcessor',
    'get_null_handler',
    'get_calculation_handler',
    'register_null_handler',
    'register_calculation_handler',
    'list_registered_handlers',
    'load_excel_data',
    # Phase 2 DI exports
    'interfaces',
    'factories',
    'DependencyContainer',
    'get_container',
    'set_container',
    'CalculationEngineFactory',
    'SchemaProcessorFactory',
    'create_calculation_engine',
    'create_calculation_engine_legacy',
]

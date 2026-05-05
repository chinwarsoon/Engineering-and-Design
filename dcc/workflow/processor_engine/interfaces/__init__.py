"""
Dependency Injection Interfaces for Processor Engine

Defines abstract interfaces for all injectable dependencies,
enabling swappable implementations, simplified testing, and platform flexibility.

This module follows the barrel pattern - it re-exports functionality from submodules.
"""
from processor_engine.interfaces.iface_reporters import (
    ErrorReporterInterface,
    IErrorReporter,
    IErrorAggregator,
)
from processor_engine.interfaces.iface_loggers import (
    IStructuredLogger,
)
from processor_engine.interfaces.iface_detectors import (
    IBusinessDetector,
    IStrategyResolver,
    ICalculationStrategy,
)
from processor_engine.interfaces.iface_base import (
    ICalculationEngine,
    ISchemaProcessor,
    ErrorReporterProtocol,
    LoggerProtocol,
)

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

"""
common.library.column_processor — Generic column processing orchestrator (L??).

Provides a schema-driven phase dispatcher and handler registry that can be
shared by EKS, DCC, and future pipeline projects. Project-specific handlers
are registered by each project's subclass.

Exports:
    BaseColumnProcessor   — generic phase-filtered column dispatch engine
    HandlerRegistry       — register/lookup handler callables by calculation.type
    ColumnProcessorError  — base exception for all column processor errors

Revision: 0.1
Date: 2026-07-29
Author: opencode
Summary: Initial release — BaseColumnProcessor + HandlerRegistry for schema-driven
         column processing. EKSColumnProcessor lives in eks/engine/core/.
"""

from .base import BaseColumnProcessor
from .registry import HandlerRegistry, ColumnProcessorError

__version__ = "0.1"
__all__ = [
    "BaseColumnProcessor",
    "HandlerRegistry",
    "ColumnProcessorError",
]

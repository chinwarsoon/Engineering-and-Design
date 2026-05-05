"""
Base classes for DCC engines and processors.

This module follows the barrel pattern - it re-exports functionality from submodules.
"""
from core_engine.base.base_engine import BaseEngine
from core_engine.base.base_processor import BaseProcessor

__all__ = [
    "BaseEngine",
    "BaseProcessor",
]

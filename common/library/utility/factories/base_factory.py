"""
L09 — Factory ABC

Abstract base for all config-driven factory classes.
Provides _get_config(key, default) and dynamic class loading via importlib.

Sources
-------
dcc: processor_engine/core/proc_factories.py  (direct-import factories)
eks: engine/core/factories.py                 (Factory ABC — reference impl)
"""

import importlib
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type


class Factory(ABC):
    """
    Abstract base class for all pipeline factories.

    Subclass usage
    --------------
    class ParserFactory(Factory):
        def create(self, file_type: str, **kwargs):
            class_path = self._mappings.get(file_type)
            return self._load_class(class_path)(**kwargs)
    """

    def __init__(self, config_registry: Optional[Dict[str, Any]] = None):
        self.config_registry: Dict[str, Any] = config_registry or {}

    @abstractmethod
    def create(self, **kwargs) -> Any:
        """Create and return a component instance."""

    def _get_config(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a value from config_registry by dot-separated key.
        Supports nested keys: _get_config("health_scoring.dimensions")
        """
        parts = key.split(".")
        node = self.config_registry
        for part in parts:
            if not isinstance(node, dict):
                return default
            node = node.get(part, default)
        return node

    @staticmethod
    def _load_class(class_path: str) -> Type:
        """
        Dynamically import and return a class from a dotted path string.
        e.g. "eks.engine.parsers.pdf_parser.PDFParser"
        """
        module_path, class_name = class_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        return getattr(module, class_name)

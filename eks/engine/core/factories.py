"""
Factories for Dependency Injection pattern.

This module implements factory classes for component creation per Appendix F,
providing config-driven instantiation for parsers, health scorers, and structure detectors.

Revision: 0.1
Date: 2026-06-30
Author: System
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type
from pathlib import Path
import importlib


class Factory(ABC):
    """Abstract base class for all factories."""
    
    def __init__(self, config_registry: Optional[Dict[str, Any]] = None):
        """
        Initialize factory.
        
        Args:
            config_registry: Configuration registry for factory settings
        """
        self.config_registry = config_registry or {}
    
    @abstractmethod
    def create(self, **kwargs) -> Any:
        """Create an instance of the component."""
        pass
    
    def _get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config_registry.get(key, default)


class ParserFactory(Factory):
    """
    Factory for creating parser instances.
    
    This factory implements the Dependency Injection pattern per Appendix F,
    providing config-driven parser instantiation based on file type.
    """
    
    def __init__(self, config_registry: Optional[Dict[str, Any]] = None):
        """
        Initialize parser factory.
        
        Args:
            config_registry: Configuration registry with parser mappings
        """
        super().__init__(config_registry)
        self._parser_map: Dict[str, Type] = {}
        self._load_parser_mappings()
    
    def _load_parser_mappings(self):
        """Load parser class mappings from configuration."""
        # Default parser mappings
        default_mappings = {
            ".pdf": "eks.engine.parsers.pdf_parser.PDFParser",
            ".docx": "eks.engine.parsers.docx_parser.DocxParser",
            ".xlsx": "eks.engine.parsers.xlsx_parser.XlsxParser",
            ".dwg": "eks.engine.parsers.dwg_parser.DWGParserStub",
            ".dgn": "eks.engine.parsers.dgn_parser.DGNParserStub"
        }
        
        # Override with config if provided
        config_mappings = self._get_config("parsers", {})
        self._parser_mappings = {**default_mappings, **config_mappings}
    
    def create(self, file_type: str, **kwargs) -> Any:
        """
        Create a parser instance for the given file type.
        
        Args:
            file_type: File extension (e.g., ".pdf", ".docx")
            **kwargs: Additional arguments for parser initialization
            
        Returns:
            Parser instance
            
        Raises:
            ValueError: If no parser is registered for the file type
        """
        parser_class_path = self._parser_mappings.get(file_type.lower())
        
        if not parser_class_path:
            raise ValueError(f"No parser registered for file type: {file_type}")
        
        # Dynamically import and instantiate parser class
        module_path, class_name = parser_class_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        parser_class = getattr(module, class_name)
        
        return parser_class(**kwargs)
    
    def register_parser(self, file_type: str, parser_class_path: str):
        """
        Register a parser for a file type.
        
        Args:
            file_type: File extension
            parser_class_path: Full class path (e.g., "eks.engine.parsers.pdf_parser.PDFParser")
        """
        self._parser_mappings[file_type.lower()] = parser_class_path
    
    def get_supported_types(self) -> list:
        """Get list of supported file types."""
        return list(self._parser_mappings.keys())


class HealthScorerFactory(Factory):
    """
    Factory for creating health scorer instances.
    
    This factory implements the Dependency Injection pattern per Appendix F,
    providing config-driven health scorer instantiation with custom dimensions.
    """
    
    def __init__(self, config_registry: Optional[Dict[str, Any]] = None):
        """
        Initialize health scorer factory.
        
        Args:
            config_registry: Configuration registry with health scoring settings
        """
        super().__init__(config_registry)
        self._default_dimensions = [
            "completeness",
            "confidence",
            "structural",
            "source",
            "xref",
            "consistency"
        ]
    
    def create(self, dimensions: Optional[list] = None, **kwargs) -> Any:
        """
        Create a health scorer instance.
        
        Args:
            dimensions: List of scoring dimensions (uses default if None)
            **kwargs: Additional arguments for health scorer initialization
            
        Returns:
            Health scorer instance
        """
        # Use config dimensions if provided, otherwise use default
        config_dimensions = self._get_config("health_scoring.dimensions")
        scoring_dimensions = dimensions or config_dimensions or self._default_dimensions
        
        # Import health scorer module
        from engine.core.health_scorer import HealthScorer
        
        # Create health scorer with dimensions
        return HealthScorer(dimensions=scoring_dimensions, **kwargs)
    
    def get_default_dimensions(self) -> list:
        """Get default scoring dimensions."""
        return self._default_dimensions.copy()
    
    def get_config_dimensions(self) -> list:
        """Get scoring dimensions from configuration."""
        return self._get_config("health_scoring.dimensions", self._default_dimensions)


class StructureDetectorFactory(Factory):
    """
    Factory for creating structure detector instances.
    
    This factory implements the Dependency Injection pattern per Appendix F,
    providing config-driven structure detector instantiation.
    """
    
    def __init__(self, config_registry: Optional[Dict[str, Any]] = None):
        """
        Initialize structure detector factory.
        
        Args:
            config_registry: Configuration registry with structure detection settings
        """
        super().__init__(config_registry)
        self._detector_class_path = self._get_config(
            "structure_detection.detector_class",
            "eks.engine.core.structure_detector.StructureDetector"
        )
    
    def create(self, **kwargs) -> Any:
        """
        Create a structure detector instance.
        
        Args:
            **kwargs: Additional arguments for structure detector initialization
            
        Returns:
            Structure detector instance
        """
        # Dynamically import and instantiate detector class
        module_path, class_name = self._detector_class_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        detector_class = getattr(module, class_name)
        
        return detector_class(**kwargs)
    
    def register_detector(self, detector_class_path: str):
        """
        Register a custom structure detector.
        
        Args:
            detector_class_path: Full class path
        """
        self._detector_class_path = detector_class_path


class EngineFactory(Factory):
    """
    Factory for creating engine instances.
    
    This factory provides a unified interface for creating any engine type.
    """
    
    def __init__(self, config_registry: Optional[Dict[str, Any]] = None):
        """
        Initialize engine factory.
        
        Args:
            config_registry: Configuration registry with engine settings
        """
        super().__init__(config_registry)
        self._engine_map: Dict[str, Type] = {}
        self._load_engine_mappings()
    
    def _load_engine_mappings(self):
        """Load engine class mappings from configuration."""
        # Default engine mappings
        default_mappings = {
            "parser": "eks.engine.parsers.parser_router.ParserRouter",
            "discovery": "eks.engine.core.file_scanner.FileScanner",
            "health": "eks.engine.core.health_scorer.HealthScorer"
        }
        
        # Override with config if provided
        config_mappings = self._get_config("engines", {})
        self._engine_mappings = {**default_mappings, **config_mappings}
    
    def create(self, engine_type: str, **kwargs) -> Any:
        """
        Create an engine instance.
        
        Args:
            engine_type: Type of engine (e.g., "parser", "discovery", "health")
            **kwargs: Additional arguments for engine initialization
            
        Returns:
            Engine instance
            
        Raises:
            ValueError: If no engine is registered for the type
        """
        engine_class_path = self._engine_mappings.get(engine_type.lower())
        
        if not engine_class_path:
            raise ValueError(f"No engine registered for type: {engine_type}")
        
        # Dynamically import and instantiate engine class
        module_path, class_name = engine_class_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        engine_class = getattr(module, class_name)
        
        return engine_class(**kwargs)
    
    def register_engine(self, engine_type: str, engine_class_path: str):
        """
        Register an engine type.
        
        Args:
            engine_type: Engine type identifier
            engine_class_path: Full class path
        """
        self._engine_mappings[engine_type.lower()] = engine_class_path
    
    def get_supported_engines(self) -> list:
        """Get list of supported engine types."""
        return list(self._engine_mappings.keys())

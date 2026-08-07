"""
Factories for Dependency Injection pattern.

This module implements factory classes for component creation per Appendix F,
providing config-driven instantiation for parsers and pipeline engines.

Revision: 0.4
Date: 2026-07-24
Author: CodeBuddy
Summary: 0.4: T1.99.198 — removed dead HealthScorerFactory and
         StructureDetectorFactory (superseded by EngineFactory).
         ParserFactory retained — actively used by ParserRouter.
0.3: T1.182.1-5 (I211) — removed duplicate Factory ABC; all 4 factory
         classes now inherit from common.library.utility.factories.base_factory.Factory;
         manual importlib replaced with self._load_class(); EngineFactory gains
         FileScanner/HealthScorer/StructureDetector mappings for DI compliance.
0.2: T1.99.183 (I211) — fixed broken import path in HealthScorerFactory
         (engine.core → eks.engine.core); added try/except guards with clear
         ImportError messages for all dynamic imports.
0.1: Initial factory implementation.
"""

from typing import Any, Dict, Optional
from common.library.utility.factories.base_factory import Factory


class ParserFactory(Factory):
    """
    Factory for creating parser instances.
    
    This factory implements the Dependency Injection pattern per Appendix F,
    providing config-driven parser instantiation based on file type.
    """
    
    def __init__(self, config_registry: Optional[Dict[str, Any]] = None,
                 processing_config: Optional[Dict[str, Any]] = None):
        """
        Initialize parser factory.

        Args:
            config_registry: Configuration registry with parser mappings
            processing_config: I287 (T1.242) — eks_processing_config.json values
                SSOT. Parser mappings are derived from extraction_profiles
                (parser_class + supported_extensions); the legacy config
                ``parsers`` key is retired.
        """
        super().__init__(config_registry)
        self.processing_config = processing_config or {}
        self._load_parser_mappings()

    def _load_parser_mappings(self):
        """Load parser class mappings from configuration.

        I287 (T1.242): single source is extraction_profiles in
        eks_processing_config.json — ``parser_class`` per profile bound to its
        ``supported_extensions``. Hardcoded default fallback removed (§16).
        """
        mappings: Dict[str, str] = {}
        for profile in self.processing_config.get("extraction_profiles", {}).values():
            parser_class = profile.get("parser_class", "")
            for ext in profile.get("supported_extensions", []):
                if ext and parser_class:
                    mappings[ext.lower()] = parser_class
        self._parser_mappings = mappings
    
    def create(self, file_type: str, **kwargs) -> Any:
        """
        Create a parser instance for the given file type.
        """
        if not file_type:
            raise ValueError(f"No file type provided")
        parser_class_path = self._parser_mappings.get(file_type.lower())
        if not parser_class_path:
            raise ValueError(f"No parser registered for file type: {file_type}")
        parser_class = self._load_class(parser_class_path)
        return parser_class(**kwargs)
    
    def register_parser(self, file_type: str, parser_class_path: str):
        """Register a parser for a file type."""
        self._parser_mappings[file_type.lower()] = parser_class_path
    
    def get_supported_types(self) -> list:
        """Get list of supported file types."""
        return list(self._parser_mappings.keys())


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
        self._load_engine_mappings()
    
    def _load_engine_mappings(self):
        """Load engine class mappings from configuration."""
        # Default engine mappings
        default_mappings = {
            "parser": "eks.engine.parsers.parser_router.ParserRouter",
            "discovery": "eks.engine.core.file_scanner.FileScanner",
            "health": "eks.engine.core.health_scorer.HealthScorer",
            "FileScanner": "eks.engine.core.file_scanner.FileScanner",
            "HealthScorer": "eks.engine.core.health_scorer.HealthScorer",
            "StructureDetector": "eks.engine.core.structure_detector.StructureDetector"
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
        engine_class_path = self._engine_mappings.get(engine_type)
        
        if not engine_class_path:
            raise ValueError(f"No engine registered for type: {engine_type}")
        
        engine_class = self._load_class(engine_class_path)
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

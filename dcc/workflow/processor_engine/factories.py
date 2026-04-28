"""
Dependency Factories for Processor Engine

Provides factory functions and dependency injection containers
for creating engine instances with configurable dependencies.
"""

from typing import Dict, Any, Optional, Type
from pathlib import Path

from .interfaces import (
    IErrorReporter,
    IErrorAggregator,
    IStructuredLogger,
    IBusinessDetector,
    IStrategyResolver,
    ICalculationEngine,
    ISchemaProcessor,
)


class DependencyContainer:
    """
    Container for managing dependency registrations and resolutions.
    Supports both explicit injection and default implementations.
    """
    
    def __init__(self):
        self._registrations: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}
    
    def register(self, interface: Type, implementation: Any, singleton: bool = False) -> None:
        """
        Register an implementation for an interface.
        
        Args:
            interface: The interface/class to register for
            implementation: The implementation class or instance
            singleton: If True, only create one instance
        """
        key = interface.__name__
        self._registrations[key] = {
            'implementation': implementation,
            'singleton': singleton,
            'is_class': isinstance(implementation, type)
        }
    
    def resolve(self, interface: Type, **kwargs) -> Any:
        """
        Resolve an implementation for the given interface.
        
        Args:
            interface: The interface to resolve
            **kwargs: Constructor arguments for creating instance
            
        Returns:
            The resolved implementation instance
        """
        key = interface.__name__
        
        if key not in self._registrations:
            # Return default implementation
            return self._create_default(interface, **kwargs)
        
        reg = self._registrations[key]
        
        # Handle singleton pattern
        if reg['singleton']:
            if key not in self._singletons:
                self._singletons[key] = self._create_instance(reg, **kwargs)
            return self._singletons[key]
        
        return self._create_instance(reg, **kwargs)
    
    def _create_instance(self, registration: Dict, **kwargs) -> Any:
        """Create an instance from registration."""
        impl = registration['implementation']
        if registration['is_class']:
            return impl(**kwargs)
        return impl
    
    def _create_default(self, interface: Type, **kwargs) -> Any:
        """Create default implementation for interface."""
        # Map interfaces to default implementations
        defaults = {
            'IErrorReporter': 'reporting_engine.error_reporter.ErrorReporter',
            'IErrorAggregator': 'processor_engine.error_handling.aggregator.ErrorAggregator',
            'IStructuredLogger': 'processor_engine.error_handling.core.logger.StructuredLogger',
            'IBusinessDetector': 'processor_engine.error_handling.detectors.business.BusinessDetector',
            'IStrategyResolver': 'processor_engine.core.calculation_strategy.StrategyResolver',
        }
        
        key = interface.__name__
        if key in defaults:
            module_path, class_name = defaults[key].rsplit('.', 1)
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            return cls(**kwargs)
        
        raise ValueError(f"No registration or default for {key}")


# Global container instance
_default_container: Optional[DependencyContainer] = None


def get_container() -> DependencyContainer:
    """Get the default dependency container (creates if needed)."""
    global _default_container
    if _default_container is None:
        _default_container = DependencyContainer()
    return _default_container


def set_container(container: DependencyContainer) -> None:
    """Set a custom dependency container."""
    global _default_container
    _default_container = container


class CalculationEngineFactory:
    """
    Factory for creating CalculationEngine instances with injectable dependencies.
    Supports both legacy direct creation and DI-based creation.
    """
    
    @staticmethod
    def create(
        context: Any,
        schema_data: Dict,
        error_reporter: Optional[IErrorReporter] = None,
        error_aggregator: Optional[IErrorAggregator] = None,
        structured_logger: Optional[IStructuredLogger] = None,
        business_detector: Optional[IBusinessDetector] = None,
        strategy_resolver: Optional[IStrategyResolver] = None,
        use_container: bool = False
    ) -> 'CalculationEngine':
        """
        Create a CalculationEngine with optional dependency injection.
        
        Args:
            context: Pipeline context
            schema_data: Resolved schema data
            error_reporter: Optional error reporter implementation
            error_aggregator: Optional error aggregator implementation
            structured_logger: Optional structured logger implementation
            business_detector: Optional business detector implementation
            strategy_resolver: Optional strategy resolver implementation
            use_container: If True, use DI container to resolve missing dependencies
            
        Returns:
            Configured CalculationEngine instance
        """
        from .core.engine import CalculationEngine
        
        if use_container:
            container = get_container()
            
            # Resolve missing dependencies from container
            if error_aggregator is None:
                error_aggregator = container.resolve(IErrorAggregator)
            if structured_logger is None:
                structured_logger = container.resolve(IStructuredLogger)
            if business_detector is None:
                parameters = schema_data.get('parameters', {})
                fail_fast = parameters.get('fail_fast', True)
                business_detector = container.resolve(
                    IBusinessDetector,
                    enable_fail_fast=fail_fast,
                    logger=structured_logger
                )
            if strategy_resolver is None:
                strategy_resolver = container.resolve(IStrategyResolver)
        
        # Create engine with explicit dependencies
        return CalculationEngine(
            context=context,
            schema_data=schema_data,
            error_reporter=error_reporter,
            error_aggregator=error_aggregator,
            structured_logger=structured_logger,
            business_detector=business_detector,
            strategy_resolver=strategy_resolver
        )
    
    @staticmethod
    def create_legacy(context: Any, schema_data: Dict) -> 'CalculationEngine':
        """
        Create a CalculationEngine using legacy direct instantiation.
        Maintains backward compatibility.
        """
        from .core.engine import CalculationEngine
        return CalculationEngine(context, schema_data)


class SchemaProcessorFactory:
    """Factory for creating SchemaProcessor instances."""
    
    @staticmethod
    def create(schema_data: Dict) -> 'SchemaProcessor':
        """Create a SchemaProcessor instance."""
        from .schema import SchemaProcessor
        return SchemaProcessor(schema_data)


# Convenience functions for direct use
def create_calculation_engine(
    context: Any,
    schema_data: Dict,
    **dependencies
) -> 'CalculationEngine':
    """
    Convenience function to create a CalculationEngine.
    
    Args:
        context: Pipeline context
        schema_data: Resolved schema data
        **dependencies: Optional dependency overrides
        
    Returns:
        Configured CalculationEngine instance
    """
    return CalculationEngineFactory.create(context, schema_data, **dependencies)


def create_calculation_engine_legacy(context: Any, schema_data: Dict) -> 'CalculationEngine':
    """
    Legacy compatibility function for creating CalculationEngine.
    """
    return CalculationEngineFactory.create_legacy(context, schema_data)


__all__ = [
    'DependencyContainer',
    'get_container',
    'set_container',
    'CalculationEngineFactory',
    'SchemaProcessorFactory',
    'create_calculation_engine',
    'create_calculation_engine_legacy',
]

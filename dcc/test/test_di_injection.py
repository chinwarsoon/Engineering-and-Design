"""
Integration Tests for Dependency Injection

Tests DI functionality in the processor_engine to ensure:
1. Dependencies can be injected successfully
2. Default implementations work when no dependencies provided
3. Behavior parity between DI and legacy modes
4. Factory functions work correctly
"""

import pytest
import pandas as pd
from pathlib import Path
from typing import Dict, Any
from unittest.mock import MagicMock, patch

# Insert workflow path for imports
import sys
workflow_path = Path(__file__).parent.parent / "workflow"
if str(workflow_path) not in sys.path:
    sys.path.insert(0, str(workflow_path))

from processor_engine import (
    CalculationEngine,
    CalculationEngineFactory,
    SchemaProcessorFactory,
    create_calculation_engine,
    create_calculation_engine_legacy,
    DependencyContainer,
    get_container,
    set_container,
)
from processor_engine.interfaces import (
    IErrorReporter,
    IErrorAggregator,
    IStructuredLogger,
    IBusinessDetector,
)


class MockErrorReporter(IErrorReporter):
    """Mock error reporter for testing."""
    
    def __init__(self):
        self.export_called = False
        self.output_dir = None
    
    def export_dashboard_json(self, total_rows: int) -> str:
        self.export_called = True
        return "/mock/path/dashboard.json"
    
    def set_output_dir(self, output_dir: Any) -> None:
        self.output_dir = output_dir


class MockErrorAggregator(IErrorAggregator):
    """Mock error aggregator for testing."""
    
    def __init__(self):
        self.errors = []
    
    def get_error_summary(self) -> Dict[str, Any]:
        return {
            "total_errors": len(self.errors),
            "health_kpi": {"health_score": 100.0},
            "affected_rows": 0,
        }


class MockStructuredLogger(IStructuredLogger):
    """Mock structured logger for testing."""
    
    def __init__(self):
        self.logs = []
    
    def log(self, message: str, level: str = "info", **kwargs) -> None:
        self.logs.append({"message": message, "level": level, **kwargs})


class MockBusinessDetector(IBusinessDetector):
    """Mock business detector for testing."""
    
    def __init__(self, enable_fail_fast: bool = True, logger=None):
        self.enable_fail_fast = enable_fail_fast
        self.logger = logger
        self.detections = []
    
    def detect(self, data: pd.DataFrame, phase: str):
        # Return empty list for mock
        return []


@pytest.fixture
def sample_schema_data():
    """Provide sample schema data for testing."""
    return {
        "columns": {
            "Document_ID": {
                "data_type": "string",
                "is_required": True,
            },
            "Status": {
                "data_type": "string",
                "is_calculated": False,
            },
        },
        "column_sequence": ["Document_ID", "Status"],
        "parameters": {
            "fail_fast": False,
        },
    }


@pytest.fixture
def mock_context():
    """Provide a mock pipeline context."""
    context = MagicMock()
    context.paths = MagicMock()
    context.data = MagicMock()
    context.state = MagicMock()
    context.parameters = {}
    context.blueprint = MagicMock()
    return context


class TestCalculationEngineFactory:
    """Test CalculationEngineFactory functionality."""
    
    def test_create_with_default_dependencies(self, mock_context, sample_schema_data):
        """Test creating engine with default (non-injected) dependencies."""
        engine = CalculationEngineFactory.create(
            context=mock_context,
            schema_data=sample_schema_data,
        )
        
        assert isinstance(engine, CalculationEngine)
        assert engine.context == mock_context
        # Verify default dependencies were created
        assert engine.error_reporter is not None
        assert engine.error_aggregator is not None
        assert engine.structured_logger is not None
        assert engine.business_detector is not None
    
    def test_create_with_injected_dependencies(self, mock_context, sample_schema_data):
        """Test creating engine with explicitly injected dependencies."""
        mock_reporter = MockErrorReporter()
        mock_aggregator = MockErrorAggregator()
        mock_logger = MockStructuredLogger()
        mock_detector = MockBusinessDetector()
        
        engine = CalculationEngineFactory.create(
            context=mock_context,
            schema_data=sample_schema_data,
            error_reporter=mock_reporter,
            error_aggregator=mock_aggregator,
            structured_logger=mock_logger,
            business_detector=mock_detector,
        )
        
        assert isinstance(engine, CalculationEngine)
        # Verify injected dependencies are used
        assert engine.error_reporter is mock_reporter
        assert engine.error_aggregator is mock_aggregator
        assert engine.structured_logger is mock_logger
        assert engine.business_detector is mock_detector
    
    def test_create_legacy_mode(self, mock_context, sample_schema_data):
        """Test legacy mode creates engine without DI."""
        engine = CalculationEngineFactory.create_legacy(
            context=mock_context,
            schema_data=sample_schema_data,
        )
        
        assert isinstance(engine, CalculationEngine)
        assert engine.context == mock_context
        # Legacy mode should have default dependencies
        assert engine.error_reporter is not None


class TestDependencyContainer:
    """Test DependencyContainer functionality."""
    
    def test_container_registration(self):
        """Test registering and resolving dependencies."""
        container = DependencyContainer()
        
        # Register mock implementations
        container.register(IErrorReporter, MockErrorReporter)
        container.register(IErrorAggregator, MockErrorAggregator)
        
        # Resolve them
        reporter = container.resolve(IErrorReporter)
        aggregator = container.resolve(IErrorAggregator)
        
        assert isinstance(reporter, MockErrorReporter)
        assert isinstance(aggregator, MockErrorAggregator)
    
    def test_container_singleton(self):
        """Test singleton pattern in container."""
        container = DependencyContainer()
        
        # Register as singleton
        container.register(IErrorReporter, MockErrorReporter, singleton=True)
        
        # Resolve twice
        reporter1 = container.resolve(IErrorReporter)
        reporter2 = container.resolve(IErrorReporter)
        
        # Should be the same instance
        assert reporter1 is reporter2
    
    def test_global_container(self):
        """Test global container getter/setter."""
        # Get default container
        container1 = get_container()
        assert isinstance(container1, DependencyContainer)
        
        # Set custom container
        custom_container = DependencyContainer()
        set_container(custom_container)
        
        # Get should return custom
        container2 = get_container()
        assert container2 is custom_container


class TestBehaviorParity:
    """Test behavior parity between DI and legacy modes."""
    
    def test_di_and_legacy_create_same_structure(self, mock_context, sample_schema_data):
        """Test that DI and legacy modes create engines with same internal structure."""
        di_engine = CalculationEngineFactory.create(
            context=mock_context,
            schema_data=sample_schema_data,
        )
        legacy_engine = CalculationEngineFactory.create_legacy(
            context=mock_context,
            schema_data=sample_schema_data,
        )
        
        # Both should have the same attributes
        assert hasattr(di_engine, 'error_reporter')
        assert hasattr(di_engine, 'error_aggregator')
        assert hasattr(di_engine, 'structured_logger')
        assert hasattr(di_engine, 'business_detector')
        assert hasattr(di_engine, 'strategy_resolver')
        
        assert hasattr(legacy_engine, 'error_reporter')
        assert hasattr(legacy_engine, 'error_aggregator')
        assert hasattr(legacy_engine, 'structured_logger')
        assert hasattr(legacy_engine, 'business_detector')
        assert hasattr(legacy_engine, 'strategy_resolver')
    
    def test_direct_instantiation_backward_compatible(self, mock_context, sample_schema_data):
        """Test that direct CalculationEngine instantiation still works."""
        # This is the legacy way (before DI)
        engine = CalculationEngine(
            context=mock_context,
            schema_data=sample_schema_data,
        )
        
        assert isinstance(engine, CalculationEngine)
        assert engine.context == mock_context
        # Should have default dependencies
        assert engine.error_reporter is not None


class TestSchemaProcessorFactory:
    """Test SchemaProcessorFactory functionality."""
    
    def test_create_schema_processor(self, sample_schema_data):
        """Test creating SchemaProcessor via factory."""
        from processor_engine.schema import SchemaProcessor
        
        processor = SchemaProcessorFactory.create(sample_schema_data)
        
        assert isinstance(processor, SchemaProcessor)
        assert processor.schema_data == sample_schema_data


class TestConvenienceFunctions:
    """Test convenience functions for DI."""
    
    def test_create_calculation_engine(self, mock_context, sample_schema_data):
        """Test the create_calculation_engine convenience function."""
        engine = create_calculation_engine(
            context=mock_context,
            schema_data=sample_schema_data,
        )
        
        assert isinstance(engine, CalculationEngine)
    
    def test_create_calculation_engine_legacy(self, mock_context, sample_schema_data):
        """Test the create_calculation_engine_legacy convenience function."""
        engine = create_calculation_engine_legacy(
            context=mock_context,
            schema_data=sample_schema_data,
        )
        
        assert isinstance(engine, CalculationEngine)


if __name__ == "__main__":
    # Run tests with pytest if available, otherwise basic assertions
    try:
        pytest.main([__file__, "-v"])
    except ImportError:
        print("pytest not available, running basic smoke tests...")
        
        # Basic smoke test
        container = DependencyContainer()
        print(f"✓ DependencyContainer created")
        
        factory = CalculationEngineFactory()
        print(f"✓ CalculationEngineFactory available")
        
        print("\nDI infrastructure ready for Phase 2.")

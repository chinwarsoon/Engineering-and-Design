"""
Error Handling Test Suite - Comprehensive validation of centralized error handling.

Tests the integration of PipelineContext error management across all pipeline components,
including domain separation, fail-fast behavior, and backward compatibility.
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from core_engine.context import (
    PipelineContext, 
    PipelineState, 
    PipelineBlueprint, 
    PipelinePaths,
    PipelineErrorEvent
)
from core_engine.error_handling import (
    handle_system_error,
    handle_data_error,
    wrap_engine_execution,
    generate_error_report,
    validate_setup_ready,
    validate_schema_ready
)


class TestPipelineContextErrorHandling:
    """Test PipelineContext error management capabilities."""

    def test_add_system_error(self):
        """Test adding system-status errors to context."""
        paths = PipelinePaths(
            base_path=Path("/test"),
            schema_path=Path("/test/schema.json"),
            excel_path=Path("/test/data.xlsx"),
            csv_output_path=Path("/test/output.csv"),
            excel_output_path=Path("/test/output.xlsx"),
            summary_path=Path("/test/summary.txt"),
            debug_log_path=Path("/test/debug.json")
        )
        context = PipelineContext(paths=paths, parameters={})
        
        # Add a system error
        context.add_system_error(
            code="S-F-S-0201",
            message="Test file not found",
            details="/test/file.txt",
            engine="test_engine",
            phase="test_phase",
            severity="critical",
            fatal=True
        )
        
        # Verify error was added
        assert len(context.state.system_status_errors) == 1
        error = context.state.system_status_errors[0]
        assert error.domain == "system"
        assert error.code == "S-F-S-0201"
        assert error.message == "Test file not found"
        assert error.engine == "test_engine"
        assert error.phase == "test_phase"
        assert error.severity == "critical"
        assert error.fatal is True

    def test_add_data_error(self):
        """Test adding data-handling errors to context."""
        paths = PipelinePaths(
            base_path=Path("/test"),
            schema_path=Path("/test/schema.json"),
            excel_path=Path("/test/data.xlsx"),
            csv_output_path=Path("/test/output.csv"),
            excel_output_path=Path("/test/output.xlsx"),
            summary_path=Path("/test/summary.txt"),
            debug_log_path=Path("/test/debug.json")
        )
        context = PipelineContext(paths=paths, parameters={})
        
        # Add a data error
        context.add_data_error(
            code="P1-A-P-0101",
            message="Validation failed",
            details="Row 5: Invalid value",
            engine="processor_engine",
            phase="data_validation",
            severity="medium",
            fatal=False
        )
        
        # Verify error was added
        assert len(context.state.system_status_errors) == 1
        error = context.state.system_status_errors[0]
        assert error.domain == "data"
        assert error.code == "P1-A-P-0101"
        assert error.message == "Validation failed"
        assert error.fatal is False

    def test_should_fail_fast_critical(self):
        """Test fail-fast behavior with critical errors."""
        paths = PipelinePaths(
            base_path=Path("/test"),
            schema_path=Path("/test/schema.json"),
            excel_path=Path("/test/data.xlsx"),
            csv_output_path=Path("/test/output.csv"),
            excel_output_path=Path("/test/output.xlsx"),
            summary_path=Path("/test/summary.txt"),
            debug_log_path=Path("/test/debug.json")
        )
        
        # Configure fail-fast for critical errors
        blueprint = PipelineBlueprint()
        blueprint.validation_rules = {
            "fail_fast_system": {
                "enabled": True,
                "severity_threshold": "critical"
            }
        }
        
        context = PipelineContext(paths=paths, parameters={}, blueprint=blueprint)
        
        # Add critical error
        context.add_system_error(
            code="S-F-S-0201",
            message="Critical error",
            severity="critical",
            fatal=True
        )
        
        # Should fail fast
        assert context.should_fail_fast("system") is True

    def test_should_fail_fast_disabled(self):
        """Test fail-fast behavior when disabled."""
        paths = PipelinePaths(
            base_path=Path("/test"),
            schema_path=Path("/test/schema.json"),
            excel_path=Path("/test/data.xlsx"),
            csv_output_path=Path("/test/output.csv"),
            excel_output_path=Path("/test/output.xlsx"),
            summary_path=Path("/test/summary.txt"),
            debug_log_path=Path("/test/debug.json")
        )
        
        # Disable fail-fast
        blueprint = PipelineBlueprint()
        blueprint.validation_rules = {
            "fail_fast_system": {
                "enabled": False,
                "severity_threshold": "critical"
            }
        }
        
        context = PipelineContext(paths=paths, parameters={}, blueprint=blueprint)
        
        # Add critical error
        context.add_system_error(
            code="S-F-S-0201",
            message="Critical error",
            severity="critical",
            fatal=True
        )
        
        # Should not fail fast
        assert context.should_fail_fast("system") is False

    def test_get_error_summary(self):
        """Test error summary generation."""
        paths = PipelinePaths(
            base_path=Path("/test"),
            schema_path=Path("/test/schema.json"),
            excel_path=Path("/test/data.xlsx"),
            csv_output_path=Path("/test/output.csv"),
            excel_output_path=Path("/test/output.xlsx"),
            summary_path=Path("/test/summary.txt"),
            debug_log_path=Path("/test/debug.json")
        )
        context = PipelineContext(paths=paths, parameters={})
        
        # Add multiple errors
        context.add_system_error(code="S-F-S-0201", message="File error", severity="critical", fatal=True)
        context.add_system_error(code="S-C-S-0301", message="Config error", severity="high", fatal=False)
        context.add_data_error(code="P1-A-P-0101", message="Data error", severity="medium", fatal=False)
        
        summary = context.get_error_summary()
        
        assert summary["total_errors"] == 3
        assert summary["by_domain"]["system"] == 2
        assert summary["by_domain"]["data"] == 1
        assert summary["by_severity"]["critical"] == 1
        assert summary["by_severity"]["high"] == 1
        assert summary["by_severity"]["medium"] == 1
        assert summary["fatal_errors"] == 1

    def test_get_system_status_errors(self):
        """Test filtering system-status errors."""
        paths = PipelinePaths(
            base_path=Path("/test"),
            schema_path=Path("/test/schema.json"),
            excel_path=Path("/test/data.xlsx"),
            csv_output_path=Path("/test/output.csv"),
            excel_output_path=Path("/test/output.xlsx"),
            summary_path=Path("/test/summary.txt"),
            debug_log_path=Path("/test/debug.json")
        )
        context = PipelineContext(paths=paths, parameters={})
        
        # Add mixed errors
        context.add_system_error(code="S-F-S-0201", message="System error", severity="critical")
        context.add_data_error(code="P1-A-P-0101", message="Data error", severity="medium")
        
        system_errors = context.get_system_status_errors()
        data_errors = context.get_data_handling_errors()
        
        assert len(system_errors) == 1
        assert len(data_errors) == 1
        assert system_errors[0]["code"] == "S-F-S-0201"
        assert data_errors[0]["code"] == "P1-A-P-0101"


class TestErrorHandlingUtilities:
    """Test standardized error handling utilities."""

    def test_handle_system_error_success(self):
        """Test handle_system_error with successful condition."""
        paths = PipelinePaths(
            base_path=Path("/test"),
            schema_path=Path("/test/schema.json"),
            excel_path=Path("/test/data.xlsx"),
            csv_output_path=Path("/test/output.csv"),
            excel_output_path=Path("/test/output.xlsx"),
            summary_path=Path("/test/summary.txt"),
            debug_log_path=Path("/test/debug.json")
        )
        context = PipelineContext(paths=paths, parameters={})
        
        # Test successful condition
        result = handle_system_error(
            context=context,
            condition=True,
            code="S-F-S-0201",
            message="Test error",
            engine="test_engine"
        )
        
        assert result is True
        assert len(context.state.system_status_errors) == 0

    def test_handle_system_error_failure(self):
        """Test handle_system_error with failed condition."""
        paths = PipelinePaths(
            base_path=Path("/test"),
            schema_path=Path("/test/schema.json"),
            excel_path=Path("/test/data.xlsx"),
            csv_output_path=Path("/test/output.csv"),
            excel_output_path=Path("/test/output.xlsx"),
            summary_path=Path("/test/summary.txt"),
            debug_log_path=Path("/test/debug.json")
        )
        context = PipelineContext(paths=paths, parameters={})
        
        # Test failed condition
        result = handle_system_error(
            context=context,
            condition=False,
            code="S-F-S-0201",
            message="Test error",
            details="Test details",
            engine="test_engine",
            phase="test_phase",
            severity="critical",
            fatal=True
        )
        
        assert result is False
        assert len(context.state.system_status_errors) == 1
        error = context.state.system_status_errors[0]
        assert error.code == "S-F-S-0201"
        assert error.message == "Test error"
        assert error.engine == "test_engine"

    def test_wrap_engine_execution_success(self):
        """Test wrap_engine_execution with successful execution."""
        paths = PipelinePaths(
            base_path=Path("/test"),
            schema_path=Path("/test/schema.json"),
            excel_path=Path("/test/data.xlsx"),
            csv_output_path=Path("/test/output.csv"),
            excel_output_path=Path("/test/output.xlsx"),
            summary_path=Path("/test/summary.txt"),
            debug_log_path=Path("/test/debug.json")
        )
        context = PipelineContext(paths=paths, parameters={})
        
        def successful_func():
            return "success"
        
        result = wrap_engine_execution(
            context=context,
            engine_name="test_engine",
            execution_func=successful_func
        )
        
        assert result == "success"
        assert context.state.engine_status["test_engine"] == "completed"

    def test_wrap_engine_execution_failure(self):
        """Test wrap_engine_execution with failed execution."""
        paths = PipelinePaths(
            base_path=Path("/test"),
            schema_path=Path("/test/schema.json"),
            excel_path=Path("/test/data.xlsx"),
            csv_output_path=Path("/test/output.csv"),
            excel_output_path=Path("/test/output.xlsx"),
            summary_path=Path("/test/summary.txt"),
            debug_log_path=Path("/test/debug.json")
        )
        context = PipelineContext(paths=paths, parameters={})
        
        def failing_func():
            raise ValueError("Test failure")
        
        with pytest.raises(ValueError, match="Test failure"):
            wrap_engine_execution(
                context=context,
                engine_name="test_engine",
                execution_func=failing_func
            )
        
        assert context.state.engine_status["test_engine"] == "failed"
        assert len(context.state.system_status_errors) == 1

    def test_generate_error_report(self):
        """Test comprehensive error report generation."""
        paths = PipelinePaths(
            base_path=Path("/test"),
            schema_path=Path("/test/schema.json"),
            excel_path=Path("/test/data.xlsx"),
            csv_output_path=Path("/test/output.csv"),
            excel_output_path=Path("/test/output.xlsx"),
            summary_path=Path("/test/summary.txt"),
            debug_log_path=Path("/test/debug.json")
        )
        context = PipelineContext(paths=paths, parameters={})
        
        # Add mixed errors
        context.add_system_error(code="S-F-S-0201", message="System error", severity="critical", fatal=True)
        context.add_data_error(code="P1-A-P-0101", message="Data error", severity="medium", fatal=False)
        
        report = generate_error_report(context)
        
        assert "pipeline_status" in report
        assert "error_summary" in report
        assert "system_status_errors" in report
        assert "data_handling_errors" in report
        assert "engine_status" in report
        assert "fail_fast_triggered" in report
        
        assert report["error_summary"]["total_errors"] == 2
        assert report["system_status_errors"]["count"] == 1
        assert report["data_handling_errors"]["count"] == 1


class TestFailFastBehavior:
    """Test fail-fast behavior configuration and execution."""

    def test_fail_fast_by_severity_threshold(self):
        """Test fail-fast based on severity threshold."""
        paths = PipelinePaths(
            base_path=Path("/test"),
            schema_path=Path("/test/schema.json"),
            excel_path=Path("/test/data.xlsx"),
            csv_output_path=Path("/test/output.csv"),
            excel_output_path=Path("/test/output.xlsx"),
            summary_path=Path("/test/summary.txt"),
            debug_log_path=Path("/test/debug.json")
        )
        
        # Configure fail-fast for high severity and above
        blueprint = PipelineBlueprint()
        blueprint.validation_rules = {
            "fail_fast_system": {
                "enabled": True,
                "severity_threshold": "high"
            }
        }
        
        context = PipelineContext(paths=paths, parameters={}, blueprint=blueprint)
        
        # Add medium error (should not fail fast)
        context.add_system_error(code="S-C-S-0301", message="Medium error", severity="medium", fatal=True)
        assert context.should_fail_fast("system") is False
        
        # Add high error (should fail fast)
        context.add_system_error(code="S-F-S-0201", message="High error", severity="high", fatal=True)
        assert context.should_fail_fast("system") is True

    def test_fail_fast_domain_specific(self):
        """Test domain-specific fail-fast configuration."""
        paths = PipelinePaths(
            base_path=Path("/test"),
            schema_path=Path("/test/schema.json"),
            excel_path=Path("/test/data.xlsx"),
            csv_output_path=Path("/test/output.csv"),
            excel_output_path=Path("/test/output.xlsx"),
            summary_path=Path("/test/summary.txt"),
            debug_log_path=Path("/test/debug.json")
        )
        
        # Configure different fail-fast settings for system vs data
        blueprint = PipelineBlueprint()
        blueprint.validation_rules = {
            "fail_fast_system": {
                "enabled": True,
                "severity_threshold": "critical"
            },
            "fail_fast_data": {
                "enabled": False,
                "severity_threshold": "critical"
            }
        }
        
        context = PipelineContext(paths=paths, parameters={}, blueprint=blueprint)
        
        # Add critical system error (should fail fast)
        context.add_system_error(code="S-F-S-0201", message="System error", severity="critical", fatal=True)
        assert context.should_fail_fast("system") is True
        assert context.should_fail_fast("data") is False
        
        # Add critical data error (should not fail fast due to disabled config)
        context.add_data_error(code="P1-A-P-0101", message="Data error", severity="critical", fatal=True)
        assert context.should_fail_fast("data") is False


class TestBackwardCompatibility:
    """Test backward compatibility with existing error handling."""

    def test_error_summary_preservation(self):
        """Test that existing error_summary is preserved."""
        paths = PipelinePaths(
            base_path=Path("/test"),
            schema_path=Path("/test/schema.json"),
            excel_path=Path("/test/data.xlsx"),
            csv_output_path=Path("/test/output.csv"),
            excel_output_path=Path("/test/output.xlsx"),
            summary_path=Path("/test/summary.txt"),
            debug_log_path=Path("/test/debug.json")
        )
        context = PipelineContext(paths=paths, parameters={})
        
        # Set existing error_summary (data-handling errors)
        context.state.error_summary = {
            "total_errors": 10,
            "health_kpi": 85.5,
            "affected_rows": 5
        }
        
        # Add system errors
        context.add_system_error(code="S-F-S-0201", message="System error", severity="critical")
        
        # Verify both are preserved
        summary = context.get_error_summary()
        assert summary["data_handling_summary"]["total_errors"] == 10
        assert summary["data_handling_summary"]["health_kpi"] == 85.5
        assert summary["total_errors"] == 1  # Only system errors counted here

    def test_context_methods_without_context(self):
        """Test graceful handling when context is not available."""
        # Test utility functions when context is None or missing methods
        result = handle_system_error(
            context=None,
            condition=False,
            code="S-F-S-0201",
            message="Test error"
        )
        
        # Should return False (error condition) without crashing
        assert result is False

    @patch('utility_engine.errors.system_error_print')
    def test_system_error_print_preservation(self, mock_print):
        """Test that system_error_print is still called for user visibility."""
        paths = PipelinePaths(
            base_path=Path("/test"),
            schema_path=Path("/test/schema.json"),
            excel_path=Path("/test/data.xlsx"),
            csv_output_path=Path("/test/output.csv"),
            excel_output_path=Path("/test/output.xlsx"),
            summary_path=Path("/test/summary.txt"),
            debug_log_path=Path("/test/debug.json")
        )
        context = PipelineContext(paths=paths, parameters={})
        
        # Handle system error with print_to_stderr=True (default)
        handle_system_error(
            context=context,
            condition=False,
            code="S-F-S-0201",
            message="Test error",
            print_to_stderr=True
        )
        
        # Verify system_error_print was called
        mock_print.assert_called_once_with("S-F-S-0201", detail=None)


class TestPerformanceValidation:
    """Test performance impact of error handling changes."""

    def test_error_recording_performance(self):
        """Test that error recording has minimal performance impact."""
        import time
        
        paths = PipelinePaths(
            base_path=Path("/test"),
            schema_path=Path("/test/schema.json"),
            excel_path=Path("/test/data.xlsx"),
            csv_output_path=Path("/test/output.csv"),
            excel_output_path=Path("/test/output.xlsx"),
            summary_path=Path("/test/summary.txt"),
            debug_log_path=Path("/test/debug.json")
        )
        context = PipelineContext(paths=paths, parameters={})
        
        # Measure time for 1000 error operations
        start_time = time.time()
        for i in range(1000):
            context.add_system_error(
                code=f"S-F-S-{i:04d}",
                message=f"Error {i}",
                engine="test_engine",
                phase="test_phase"
            )
        end_time = time.time()
        
        # Should complete quickly (<100ms for 1000 operations)
        duration = end_time - start_time
        assert duration < 0.1, f"Error recording too slow: {duration:.3f}s for 1000 operations"
        
        # Verify all errors were recorded
        assert len(context.state.system_status_errors) == 1000

    def test_error_summary_performance(self):
        """Test that error summary generation is performant."""
        import time
        
        paths = PipelinePaths(
            base_path=Path("/test"),
            schema_path=Path("/test/schema.json"),
            excel_path=Path("/test/data.xlsx"),
            csv_output_path=Path("/test/output.csv"),
            excel_output_path=Path("/test/output.xlsx"),
            summary_path=Path("/test/summary.txt"),
            debug_log_path=Path("/test/debug.json")
        )
        context = PipelineContext(paths=paths, parameters={})
        
        # Add many errors
        for i in range(100):
            context.add_system_error(
                code=f"S-F-S-{i:04d}",
                message=f"Error {i}",
                engine="test_engine",
                phase="test_phase",
                severity="critical" if i % 10 == 0 else "medium"
            )
        
        # Measure summary generation time
        start_time = time.time()
        summary = context.get_error_summary()
        end_time = time.time()
        
        # Should be very fast (<10ms)
        duration = end_time - start_time
        assert duration < 0.01, f"Error summary too slow: {duration:.3f}s"
        
        # Verify summary correctness
        assert summary["total_errors"] == 100
        assert summary["by_severity"]["critical"] == 10
        assert summary["by_severity"]["medium"] == 90


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

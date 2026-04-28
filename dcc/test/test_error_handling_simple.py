"""
Simple Error Handling Test Suite - Basic validation without pytest dependency.

Tests the core functionality of centralized error handling integration.
"""

import sys
import traceback
from pathlib import Path

# Add the workflow directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "workflow"))

def test_pipeline_context_error_handling():
    """Test basic PipelineContext error management."""
    print("Testing PipelineContext error handling...")
    
    try:
        from core_engine.context import (
            PipelineContext, 
            PipelineState, 
            PipelineBlueprint, 
            PipelinePaths,
            PipelineErrorEvent
        )
        
        # Create basic paths
        paths = PipelinePaths(
            base_path=Path("/test"),
            schema_path=Path("/test/schema.json"),
            excel_path=Path("/test/data.xlsx"),
            csv_output_path=Path("/test/output.csv"),
            excel_output_path=Path("/test/output.xlsx"),
            summary_path=Path("/test/summary.txt"),
            debug_log_path=Path("/test/debug.json")
        )
        
        # Test 1: Add system error
        print("  ✓ Testing system error addition...")
        context = PipelineContext(paths=paths, parameters={})
        context.add_system_error(
            code="S-F-S-0201",
            message="Test file not found",
            details="/test/file.txt",
            engine="test_engine",
            phase="test_phase",
            severity="critical",
            fatal=True
        )
        
        assert len(context.state.system_status_errors) == 1
        error = context.state.system_status_errors[0]
        assert error.domain == "system"
        assert error.code == "S-F-S-0201"
        assert error.message == "Test file not found"
        assert error.engine == "test_engine"
        assert error.phase == "test_phase"
        assert error.severity == "critical"
        assert error.fatal is True
        print("    ✓ System error added successfully")
        
        # Test 2: Add data error
        print("  ✓ Testing data error addition...")
        context.add_data_error(
            code="P1-A-P-0101",
            message="Validation failed",
            details="Row 5: Invalid value",
            engine="processor_engine",
            phase="data_validation",
            severity="medium",
            fatal=False
        )
        
        assert len(context.state.system_status_errors) == 2
        data_error = context.state.system_status_errors[1]
        assert data_error.domain == "data"
        assert data_error.code == "P1-A-P-0101"
        assert data_error.fatal is False
        print("    ✓ Data error added successfully")
        
        # Test 3: Error summary
        print("  ✓ Testing error summary...")
        summary = context.get_error_summary()
        assert summary["total_errors"] == 2
        assert summary["by_domain"]["system"] == 1
        assert summary["by_domain"]["data"] == 1
        assert summary["by_severity"]["critical"] == 1
        assert summary["by_severity"]["medium"] == 1
        assert summary["fatal_errors"] == 1
        print("    ✓ Error summary generated correctly")
        
        # Test 4: Domain filtering
        print("  ✓ Testing domain filtering...")
        system_errors = context.get_system_status_errors()
        data_errors = context.get_data_handling_errors()
        assert len(system_errors) == 1
        assert len(data_errors) == 1
        assert system_errors[0]["code"] == "S-F-S-0201"
        assert data_errors[0]["code"] == "P1-A-P-0101"
        print("    ✓ Domain filtering works correctly")
        
        print("✅ PipelineContext error handling tests passed")
        return True
        
    except Exception as e:
        print(f"❌ PipelineContext test failed: {e}")
        traceback.print_exc()
        return False


def test_error_handling_utilities():
    """Test error handling utility functions."""
    print("Testing error handling utilities...")
    
    try:
        from core_engine.error_handling import (
            handle_system_error,
            handle_data_error,
            generate_error_report
        )
        from core_engine.context import PipelineContext, PipelinePaths
        
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
        
        # Test 1: Handle system error (success case)
        print("  ✓ Testing handle_system_error (success)...")
        result = handle_system_error(
            context=context,
            condition=True,
            code="S-F-S-0201",
            message="Test error",
            engine="test_engine"
        )
        assert result is True
        assert len(context.state.system_status_errors) == 0
        print("    ✓ Success case handled correctly")
        
        # Test 2: Handle system error (failure case)
        print("  ✓ Testing handle_system_error (failure)...")
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
        print("    ✓ Failure case handled correctly")
        
        # Test 3: Generate error report
        print("  ✓ Testing error report generation...")
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
        print("    ✓ Error report generated correctly")
        
        print("✅ Error handling utilities tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Error handling utilities test failed: {e}")
        traceback.print_exc()
        return False


def test_fail_fast_behavior():
    """Test fail-fast behavior configuration."""
    print("Testing fail-fast behavior...")
    
    try:
        from core_engine.context import PipelineContext, PipelineBlueprint, PipelinePaths
        
        paths = PipelinePaths(
            base_path=Path("/test"),
            schema_path=Path("/test/schema.json"),
            excel_path=Path("/test/data.xlsx"),
            csv_output_path=Path("/test/output.csv"),
            excel_output_path=Path("/test/output.xlsx"),
            summary_path=Path("/test/summary.txt"),
            debug_log_path=Path("/test/debug.json")
        )
        
        # Test 1: Fail-fast enabled
        print("  ✓ Testing fail-fast enabled...")
        blueprint = PipelineBlueprint()
        blueprint.validation_rules = {
            "fail_fast_system": {
                "enabled": True,
                "severity_threshold": "critical"
            }
        }
        
        context = PipelineContext(paths=paths, parameters={}, blueprint=blueprint)
        context.add_system_error(
            code="S-F-S-0201",
            message="Critical error",
            severity="critical",
            fatal=True
        )
        
        assert context.should_fail_fast("system") is True
        print("    ✓ Fail-fast enabled correctly")
        
        # Test 2: Fail-fast disabled
        print("  ✓ Testing fail-fast disabled...")
        blueprint = PipelineBlueprint()
        blueprint.validation_rules = {
            "fail_fast_system": {
                "enabled": False,
                "severity_threshold": "critical"
            }
        }
        
        context = PipelineContext(paths=paths, parameters={}, blueprint=blueprint)
        context.add_system_error(
            code="S-F-S-0201",
            message="Critical error",
            severity="critical",
            fatal=True
        )
        
        assert context.should_fail_fast("system") is False
        print("    ✓ Fail-fast disabled correctly")
        
        # Test 3: Severity threshold
        print("  ✓ Testing severity threshold...")
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
        print("    ✓ Severity threshold working correctly")
        
        print("✅ Fail-fast behavior tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Fail-fast behavior test failed: {e}")
        traceback.print_exc()
        return False


def test_backward_compatibility():
    """Test backward compatibility with existing error handling."""
    print("Testing backward compatibility...")
    
    try:
        from core_engine.context import PipelineContext, PipelinePaths
        
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
        
        # Test 1: Error summary preservation
        print("  ✓ Testing error summary preservation...")
        context.state.error_summary = {
            "total_errors": 10,
            "health_kpi": 85.5,
            "affected_rows": 5
        }
        
        context.add_system_error(code="S-F-S-0201", message="System error", severity="critical")
        
        summary = context.get_error_summary()
        assert summary["data_handling_summary"]["total_errors"] == 10
        assert summary["data_handling_summary"]["health_kpi"] == 85.5
        assert summary["total_errors"] == 1  # Only system errors counted here
        print("    ✓ Error summary preserved correctly")
        
        # Test 2: Context methods without context
        print("  ✓ Testing graceful handling without context...")
        from core_engine.error_handling import handle_system_error
        
        result = handle_system_error(
            context=None,
            condition=False,
            code="S-F-S-0201",
            message="Test error"
        )
        
        assert result is False  # Should return False without crashing
        print("    ✓ Graceful handling without context works")
        
        print("✅ Backward compatibility tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Backward compatibility test failed: {e}")
        traceback.print_exc()
        return False


def test_performance_validation():
    """Test performance impact of error handling."""
    print("Testing performance validation...")
    
    try:
        import time
        from core_engine.context import PipelineContext, PipelinePaths
        
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
        
        # Test 1: Error recording performance
        print("  ✓ Testing error recording performance...")
        start_time = time.time()
        for i in range(100):  # Reduced from 1000 for faster testing
            context.add_system_error(
                code=f"S-F-S-{i:04d}",
                message=f"Error {i}",
                engine="test_engine",
                phase="test_phase"
            )
        end_time = time.time()
        
        duration = end_time - start_time
        assert duration < 0.05, f"Error recording too slow: {duration:.3f}s for 100 operations"
        assert len(context.state.system_status_errors) == 100
        print(f"    ✓ 100 error operations completed in {duration:.3f}s")
        
        # Test 2: Error summary performance
        print("  ✓ Testing error summary performance...")
        start_time = time.time()
        summary = context.get_error_summary()
        end_time = time.time()
        
        duration = end_time - start_time
        assert duration < 0.01, f"Error summary too slow: {duration:.3f}s"
        assert summary["total_errors"] == 100
        print(f"    ✓ Error summary generated in {duration:.3f}s")
        
        print("✅ Performance validation tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Performance validation test failed: {e}")
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all error handling tests."""
    print("=" * 60)
    print("ERROR HANDLING INTEGRATION TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_pipeline_context_error_handling,
        test_error_handling_utilities,
        test_fail_fast_behavior,
        test_backward_compatibility,
        test_performance_validation
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        print(f"\nRunning {test_func.__name__}...")
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_func.__name__} failed")
        except Exception as e:
            print(f"❌ {test_func.__name__} crashed: {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All tests passed! Error handling integration is working correctly.")
        return True
    else:
        print(f"⚠️  {total - passed} tests failed. Please review the implementation.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

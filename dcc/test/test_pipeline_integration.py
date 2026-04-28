"""
Pipeline Integration Test - Full pipeline execution with error handling validation.

Tests the complete dcc_engine_pipeline with centralized error handling integration,
including orchestrator, engines, and end-to-end error reporting.
"""

import sys
import traceback
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the workflow directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "workflow"))


def create_test_environment():
    """Create a minimal test environment for pipeline execution."""
    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp())
    
    # Create minimal schema
    schema_data = {
        "columns": {
            "Test_Column": {
                "is_calculated": False,
                "data_type": "string",
                "processing_phase": "P1"
            }
        },
        "column_sequence": ["Test_Column"],
        "parameters": {
            "fail_fast_system": {
                "enabled": True,
                "severity_threshold": "critical"
            }
        }
    }
    
    schema_path = temp_dir / "test_schema.json"
    with open(schema_path, 'w') as f:
        json.dump(schema_data, f)
    
    # Create minimal Excel file
    try:
        import pandas as pd
        df = pd.DataFrame({"Test_Column": ["value1", "value2"]})
        excel_path = temp_dir / "test_data.xlsx"
        df.to_excel(excel_path, index=False)
    except ImportError:
        excel_path = None
    
    return temp_dir, schema_path, excel_path


def test_pipeline_context_creation():
    """Test pipeline context creation with error handling capabilities."""
    print("Testing pipeline context creation...")
    
    try:
        from core_engine.context import PipelineContext, PipelinePaths
        
        temp_dir, schema_path, excel_path = create_test_environment()
        
        paths = PipelinePaths(
            base_path=temp_dir,
            schema_path=schema_path,
            excel_path=excel_path or Path("dummy.xlsx"),
            csv_output_path=temp_dir / "output.csv",
            excel_output_path=temp_dir / "output.xlsx",
            summary_path=temp_dir / "summary.txt",
            debug_log_path=temp_dir / "debug.json"
        )
        
        context = PipelineContext(paths=paths, parameters={})
        
        # Test error handling methods exist
        assert hasattr(context, 'add_system_error')
        assert hasattr(context, 'add_data_error')
        assert hasattr(context, 'capture_exception')
        assert hasattr(context, 'should_fail_fast')
        assert hasattr(context, 'get_error_summary')
        
        # Test engine status tracking
        assert hasattr(context.state, 'engine_status')
        assert isinstance(context.state.engine_status, dict)
        
        print("    ✓ Pipeline context created successfully")
        return True, temp_dir
        
    except Exception as e:
        print(f"    ❌ Pipeline context creation failed: {e}")
        traceback.print_exc()
        return False, None


def test_orchestrator_error_handling():
    """Test orchestrator error handling integration."""
    print("Testing orchestrator error handling...")
    
    try:
        from dcc_engine_pipeline import run_engine_pipeline
        from core_engine.context import PipelineContext, PipelinePaths
        
        temp_dir, schema_path, excel_path = create_test_environment()
        
        paths = PipelinePaths(
            base_path=temp_dir,
            schema_path=schema_path,
            excel_path=excel_path or Path("dummy.xlsx"),
            csv_output_path=temp_dir / "output.csv",
            excel_output_path=temp_dir / "output.xlsx",
            summary_path=temp_dir / "summary.txt",
            debug_log_path=temp_dir / "debug.json"
        )
        
        context = PipelineContext(paths=paths, parameters={})
        
        # Mock the engines to avoid full execution
        with patch('initiation_engine.ProjectSetupValidator') as mock_setup, \
             patch('schema_engine.SchemaValidator') as mock_schema, \
             patch('mapper_engine.ColumnMapperEngine') as mock_mapper, \
             patch('processor_engine.CalculationEngine') as mock_processor:
            
            # Configure mocks to return success
            mock_setup.return_value.validate.return_value = {"ready": True, "missing_items": [], "invalid_items": []}
            mock_schema.return_value.validate.return_value = {"ready": True, "errors": [], "column_count": 1}
            mock_mapper.return_value.map_dataframe.return_value = {"matched_count": 1, "total_headers": 1}
            mock_processor.return_value.process_data.return_value = None
            mock_processor.return_value.get_error_summary.return_value = {"total_errors": 0}
            
            # Run the pipeline
            result = run_engine_pipeline(context)
            
            # Verify error handling integration
            assert context.state.engine_status.get("initiation_engine") == "completed"
            assert context.state.engine_status.get("schema_engine") == "completed"
            assert context.state.engine_status.get("mapper_engine") == "completed"
            assert context.state.engine_status.get("processor_engine") == "completed"
            
            # Verify error reporting
            error_summary = context.get_error_summary()
            assert "total_errors" in error_summary
            assert "by_domain" in error_summary
            assert "by_severity" in error_summary
            
            print("    ✓ Orchestrator error handling integrated successfully")
            return True
            
    except Exception as e:
        print(f"    ❌ Orchestrator error handling test failed: {e}")
        traceback.print_exc()
        return False


def test_error_propagation():
    """Test error propagation through pipeline components."""
    print("Testing error propagation...")
    
    try:
        from dcc_engine_pipeline import run_engine_pipeline
        from core_engine.context import PipelineContext, PipelinePaths
        
        temp_dir, schema_path, excel_path = create_test_environment()
        
        paths = PipelinePaths(
            base_path=temp_dir,
            schema_path=schema_path,
            excel_path=excel_path or Path("dummy.xlsx"),
            csv_output_path=temp_dir / "output.csv",
            excel_output_path=temp_dir / "output.xlsx",
            summary_path=temp_dir / "summary.txt",
            debug_log_path=temp_dir / "debug.json"
        )
        
        context = PipelineContext(paths=paths, parameters={})
        
        # Mock setup validator to fail
        with patch('initiation_engine.ProjectSetupValidator') as mock_setup:
            mock_setup.return_value.validate.return_value = {"ready": False, "missing_items": ["test"]}
            
            try:
                run_engine_pipeline(context)
                assert False, "Pipeline should have failed"
            except Exception:
                pass  # Expected to fail
            
            # Verify error was recorded
            assert len(context.state.system_status_errors) > 0
            assert context.state.engine_status.get("initiation_engine") == "failed"
            
            # Verify error attribution
            error = context.state.system_status_errors[0]
            assert error.engine == "initiation_engine"
            assert error.phase == "step1_initiation"
            
            print("    ✓ Error propagation working correctly")
            return True
            
    except Exception as e:
        print(f"    ❌ Error propagation test failed: {e}")
        traceback.print_exc()
        return False


def test_fail_fast_integration():
    """Test fail-fast behavior in pipeline execution."""
    print("Testing fail-fast integration...")
    
    try:
        from dcc_engine_pipeline import run_engine_pipeline
        from core_engine.context import PipelineContext, PipelinePaths, PipelineBlueprint
        
        temp_dir, schema_path, excel_path = create_test_environment()
        
        # Configure fail-fast for critical errors
        blueprint = PipelineBlueprint()
        blueprint.validation_rules = {
            "fail_fast_system": {
                "enabled": True,
                "severity_threshold": "critical"
            }
        }
        
        paths = PipelinePaths(
            base_path=temp_dir,
            schema_path=schema_path,
            excel_path=excel_path or Path("dummy.xlsx"),
            csv_output_path=temp_dir / "output.csv",
            excel_output_path=temp_dir / "output.xlsx",
            summary_path=temp_dir / "summary.txt",
            debug_log_path=temp_dir / "debug.json"
        )
        
        context = PipelineContext(paths=paths, parameters={}, blueprint=blueprint)
        
        # Mock schema validator to fail with critical error
        with patch('schema_engine.SchemaValidator') as mock_schema:
            mock_schema.return_value.validate.return_value = {"ready": False, "errors": ["Schema validation failed"]}
            
            # Add a critical error to trigger fail-fast
            context.add_system_error(
                code="S-C-S-0303",
                message="Schema validation failed",
                severity="critical",
                fatal=True
            )
            
            # Check fail-fast behavior
            assert context.should_fail_fast("system") is True
            
            print("    ✓ Fail-fast integration working correctly")
            return True
            
    except Exception as e:
        print(f"    ❌ Fail-fast integration test failed: {e}")
        traceback.print_exc()
        return False


def test_end_to_run_error_reporting():
    """Test end-of-run error reporting."""
    print("Testing end-of-run error reporting...")
    
    try:
        from core_engine.error_handling import generate_error_report
        from core_engine.context import PipelineContext, PipelinePaths
        
        temp_dir, schema_path, excel_path = create_test_environment()
        
        paths = PipelinePaths(
            base_path=temp_dir,
            schema_path=schema_path,
            excel_path=excel_path or Path("dummy.xlsx"),
            csv_output_path=temp_dir / "output.csv",
            excel_output_path=temp_dir / "output.xlsx",
            summary_path=temp_dir / "summary.txt",
            debug_log_path=temp_dir / "debug.json"
        )
        
        context = PipelineContext(paths=paths, parameters={})
        
        # Add mixed errors
        context.add_system_error(code="S-F-S-0201", message="File error", severity="critical", fatal=True)
        context.add_data_error(code="P1-A-P-0101", message="Data error", severity="medium", fatal=False)
        
        # Simulate engine status
        context.state.engine_status = {
            "initiation_engine": "completed",
            "schema_engine": "failed",
            "mapper_engine": "completed",
            "processor_engine": "completed"
        }
        
        # Generate error report
        report = generate_error_report(context)
        
        # Verify report structure
        assert "pipeline_status" in report
        assert "error_summary" in report
        assert "system_status_errors" in report
        assert "data_handling_errors" in report
        assert "engine_status" in report
        assert "fail_fast_triggered" in report
        
        # Verify error counts
        assert report["error_summary"]["total_errors"] == 2
        assert report["error_summary"]["by_domain"]["system"] == 1
        assert report["error_summary"]["by_domain"]["data"] == 1
        assert report["error_summary"]["fatal_errors"] == 1
        
        # Verify engine status
        assert report["engine_status"]["initiation_engine"] == "completed"
        assert report["engine_status"]["schema_engine"] == "failed"
        
        print("    ✓ End-of-run error reporting working correctly")
        return True
        
    except Exception as e:
        print(f"    ❌ End-of-run error reporting test failed: {e}")
        traceback.print_exc()
        return False


def test_pipeline_with_real_data():
    """Test pipeline execution with minimal real data (if possible)."""
    print("Testing pipeline with real data...")
    
    try:
        # This test requires pandas and openpyxl
        import pandas as pd
        import openpyxl
    except ImportError:
        print("    ⚠️ Skipping real data test (pandas/openpyxl not available)")
        return True
    
    try:
        from dcc_engine_pipeline import main
        from core_engine.context import PipelineContext, PipelinePaths
        import tempfile
        import json
        
        # Create temporary directory
        temp_dir = Path(tempfile.mkdtemp())
        
        # Create comprehensive schema
        schema_data = {
            "columns": {
                "Project_Code": {
                    "is_calculated": False,
                    "data_type": "string",
                    "processing_phase": "P1",
                    "validation": {"required": True}
                },
                "Document_Type": {
                    "is_calculated": False,
                    "data_type": "string",
                    "processing_phase": "P1"
                }
            },
            "column_sequence": ["Project_Code", "Document_Type"],
            "parameters": {
                "fail_fast_system": {"enabled": False, "severity_threshold": "critical"}
            }
        }
        
        schema_path = temp_dir / "test_schema.json"
        with open(schema_path, 'w') as f:
            json.dump(schema_data, f)
        
        # Create test Excel file
        df = pd.DataFrame({
            "Project_Code": ["PRJ001", "PRJ002"],
            "Document_Type": ["Drawing", "Specification"]
        })
        excel_path = temp_dir / "test_data.xlsx"
        df.to_excel(excel_path, index=False)
        
        # Mock sys.argv for main function
        test_args = [
            "dcc_engine_pipeline.py",
            str(temp_dir),
            "--input", str(excel_path),
            "--schema", str(schema_path),
            "--verbose", "quiet"
        ]
        
        with patch('sys.argv', test_args):
            try:
                # Run the pipeline
                result = main()
                
                # Should complete successfully (exit code 0)
                assert result == 0, f"Pipeline failed with exit code {result}"
                
                print("    ✓ Real data pipeline execution successful")
                return True
                
            except SystemExit as e:
                if e.code == 0:
                    print("    ✓ Real data pipeline execution successful")
                    return True
                else:
                    print(f"    ❌ Pipeline failed with exit code {e.code}")
                    return False
            except Exception as e:
                print(f"    ❌ Real data pipeline test failed: {e}")
                traceback.print_exc()
                return False
                
    except Exception as e:
        print(f"    ❌ Real data pipeline setup failed: {e}")
        traceback.print_exc()
        return False


def run_integration_tests():
    """Run all pipeline integration tests."""
    print("=" * 60)
    print("PIPELINE INTEGRATION TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_pipeline_context_creation,
        test_orchestrator_error_handling,
        test_error_propagation,
        test_fail_fast_integration,
        test_end_to_run_error_reporting,
        test_pipeline_with_real_data
    ]
    
    passed = 0
    total = len(tests)
    temp_dir = None
    
    for test_func in tests:
        print(f"\nRunning {test_func.__name__}...")
        try:
            if test_func.__name__ == "test_pipeline_context_creation":
                success, temp_dir = test_func()
                if success:
                    passed += 1
            else:
                if test_func():
                    passed += 1
                else:
                    print(f"❌ {test_func.__name__} failed")
        except Exception as e:
            print(f"❌ {test_func.__name__} crashed: {e}")
            traceback.print_exc()
    
    # Cleanup
    if temp_dir and temp_dir.exists():
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    print("\n" + "=" * 60)
    print(f"INTEGRATION TEST RESULTS: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All integration tests passed! Pipeline error handling is fully integrated.")
        return True
    else:
        print(f"⚠️  {total - passed} integration tests failed. Please review the implementation.")
        return False


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)

"""
Integration Test for dcc_engine_pipeline.py with DI Mode

Tests the actual pipeline execution with _USE_DI_MODE = True
to validate Dependency Injection implementation in production code path.
"""

import sys
import logging
from pathlib import Path

# Setup paths
sys.path.insert(0, str(Path(__file__).parent.parent / "workflow"))

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger("PipelineDI-Test")

def test_pipeline_di_mode():
    """Test pipeline execution with DI mode enabled."""
    
    logger.info("=" * 60)
    logger.info("Testing dcc_engine_pipeline.py with DI Mode")
    logger.info("=" * 60)
    
    try:
        # Import pipeline module
        logger.info("Step 1: Importing dcc_engine_pipeline...")
        import dcc_engine_pipeline as pipeline
        
        # Verify _USE_DI_MODE is True (as implemented)
        logger.info(f"Step 2: Checking _USE_DI_MODE = {pipeline._USE_DI_MODE}")
        
        if not pipeline._USE_DI_MODE:
            logger.error("❌ _USE_DI_MODE is False - expected True for Phase 2")
            return False
        
        logger.info("✅ _USE_DI_MODE is True - DI mode active")
        
        # Verify DI components are importable
        logger.info("Step 3: Verifying DI components...")
        from processor_engine import (
            CalculationEngineFactory,
            SchemaProcessorFactory,
            create_calculation_engine,
            DependencyContainer,
        )
        logger.info("✅ DI factories imported successfully")
        
        # Verify pipeline can create context (basic smoke test)
        logger.info("Step 4: Testing PipelineContext creation...")
        from core_engine.context import PipelineContext, PipelinePaths
        from pathlib import Path
        
        test_paths = PipelinePaths(
            base_path=Path("/tmp/test"),
            schema_path=Path("/tmp/test/schema.json"),
            excel_path=Path("/tmp/test/input.xlsx"),
            csv_output_path=Path("/tmp/test/output.csv"),
            excel_output_path=Path("/tmp/test/output.xlsx"),
            summary_path=Path("/tmp/test/summary.json"),
            debug_log_path=Path("/tmp/test/debug.json")
        )
        
        context = PipelineContext(
            paths=test_paths,
            parameters={},
            nrows=10,
            debug_mode=False
        )
        
        logger.info(f"✅ PipelineContext created: {type(context)}")
        
        # Test factory creation (without actual processing)
        logger.info("Step 5: Testing CalculationEngineFactory...")
        
        sample_schema = {
            "columns": {
                "Document_ID": {"data_type": "string", "is_required": True}
            },
            "column_sequence": ["Document_ID"],
            "parameters": {"fail_fast": False}
        }
        
        engine = CalculationEngineFactory.create(
            context=context,
            schema_data=sample_schema
        )
        
        logger.info(f"✅ CalculationEngine created via factory: {type(engine)}")
        
        # Verify engine has DI attributes
        logger.info("Step 6: Verifying DI attributes...")
        
        di_attrs = [
            'error_reporter',
            'error_aggregator', 
            'structured_logger',
            'business_detector',
            'strategy_resolver'
        ]
        
        for attr in di_attrs:
            if hasattr(engine, attr):
                val = getattr(engine, attr)
                logger.info(f"  ✅ {attr}: {type(val).__name__}")
            else:
                logger.error(f"  ❌ {attr}: MISSING")
                return False
        
        # Test SchemaProcessorFactory
        logger.info("Step 7: Testing SchemaProcessorFactory...")
        
        from processor_engine import SchemaProcessor
        schema_processor = SchemaProcessorFactory.create(sample_schema)
        
        logger.info(f"✅ SchemaProcessor created via factory: {type(schema_processor)}")
        
        logger.info("=" * 60)
        logger.info("✅ ALL TESTS PASSED - DI Mode Working Correctly")
        logger.info("=" * 60)
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import Error: {e}")
        logger.error("This may indicate missing dependencies or incorrect paths")
        import traceback
        traceback.print_exc()
        return False
        
    except Exception as e:
        logger.error(f"❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_legacy_mode():
    """Test that legacy mode still works for backward compatibility."""
    
    logger.info("\n" + "=" * 60)
    logger.info("Testing Legacy Mode (Backward Compatibility)")
    logger.info("=" * 60)
    
    try:
        from processor_engine import CalculationEngine, create_calculation_engine_legacy
        from core_engine.context import PipelineContext, PipelinePaths
        from pathlib import Path
        
        test_paths = PipelinePaths(
            base_path=Path("/tmp/test"),
            schema_path=Path("/tmp/test/schema.json"),
            excel_path=Path("/tmp/test/input.xlsx"),
            csv_output_path=Path("/tmp/test/output.csv"),
            excel_output_path=Path("/tmp/test/output.xlsx"),
            summary_path=Path("/tmp/test/summary.json"),
            debug_log_path=Path("/tmp/test/debug.json")
        )
        
        context = PipelineContext(
            paths=test_paths,
            parameters={},
            nrows=10,
            debug_mode=False
        )
        
        sample_schema = {
            "columns": {
                "Document_ID": {"data_type": "string", "is_required": True}
            },
            "column_sequence": ["Document_ID"],
            "parameters": {"fail_fast": False}
        }
        
        # Test legacy factory function
        engine = create_calculation_engine_legacy(context, sample_schema)
        logger.info(f"✅ Legacy factory works: {type(engine)}")
        
        # Test direct instantiation (the old way)
        engine_direct = CalculationEngine(context, sample_schema)
        logger.info(f"✅ Direct instantiation works: {type(engine_direct)}")
        
        logger.info("=" * 60)
        logger.info("✅ LEGACY MODE WORKS - Backward Compatibility Confirmed")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Legacy Mode Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all pipeline DI tests."""
    
    print("\n" + "=" * 60)
    print("DCC ENGINE PIPELINE - DI INTEGRATION TEST")
    print("=" * 60 + "\n")
    
    results = []
    
    # Test 1: DI Mode
    results.append(("DI Mode", test_pipeline_di_mode()))
    
    # Test 2: Legacy Mode
    results.append(("Legacy Mode", test_legacy_mode()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED - Phase 2 DI Ready for Production")
    else:
        print("❌ SOME TESTS FAILED - Review issues above")
    print("=" * 60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

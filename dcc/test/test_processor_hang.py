#!/usr/bin/env python3
"""
Debug script to isolate and identify the processor engine hang issue.
"""
import sys
import pandas as pd
from pathlib import Path

# Add workflow to path
workflow_path = Path("dcc/workflow")
if str(workflow_path) not in sys.path:
    sys.path.insert(0, str(workflow_path))

# Set up simple logging
import logging
logging.basicConfig(level=logging.DEBUG, format='[%(name)s] %(message)s')

# Test 1: Can we import the processor engine?
print("\n=== TEST 1: Import Processor Engine ===")
try:
    from processor_engine.core.engine import CalculationEngine
    print("✓ CalculationEngine imported successfully")
except Exception as e:
    print(f"✗ Failed to import: {e}")
    sys.exit(1)

# Test 2: Can we create a minimal context?
print("\n=== TEST 2: Create Minimal Pipeline Context ===")
try:
    from core_engine.context.context_pipeline import PipelineContext, PipelinePaths, PipelineBlueprint, PipelineData
    from pathlib import Path
    
    base_path = Path("dcc")
    context = PipelineContext(
        paths=PipelinePaths(
            base_path=base_path,
            schema_path=base_path / "config/schemas/dcc_register_config.json",
            excel_path=base_path / "data/Submittal and RFI Tracker Lists.xlsx",
            csv_output_path=base_path / "output/processed.csv",
            excel_output_path=base_path / "output/processed.xlsx",
            summary_path=base_path / "output/summary.txt",
            debug_log_path=base_path / "output/debug.json"
        ),
        parameters={},
        blueprint=PipelineBlueprint()
    )
    print("✓ PipelineContext created")
except Exception as e:
    print(f"✗ Failed to create context: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Test apply_forward_fill directly
print("\n=== TEST 3: Test apply_forward_fill ===")
try:
    from processor_engine.calculations.null_handling import apply_forward_fill
    
    # Create a small test DataFrame
    df_test = pd.DataFrame({
        'col1': [1, None, None, 4, None],
        'col2': ['A', None, 'C', None, 'E']
    })
    
    print(f"Input DataFrame:\n{df_test}\n")
    
    # Create a mock engine
    class MockEngine:
        def __init__(self):
            self.columns = {
                'col1': {'null_handling': {'strategy': 'forward_fill'}},
                'col2': {'null_handling': {'strategy': 'forward_fill'}}
            }
            self.fill_history = []
        
        def _resolve_schema_reference(self, ref):
            return None
    
    engine = MockEngine()
    
    # Apply forward fill
    print("Applying forward_fill to col1...")
    df_result = apply_forward_fill(engine, df_test, 'col1', {'group_by': [], 'fill_value': 'NA'})
    print(f"Result:\n{df_result}\n")
    print("✓ apply_forward_fill works")
    
except Exception as e:
    print(f"✗ apply_forward_fill failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Test _apply_phase_null_handling with small dataset
print("\n=== TEST 4: Test _apply_phase_null_handling ===")
try:
    from processor_engine.core.engine import CalculationEngine
    
    # Create minimal engine with mock data
    engine = CalculationEngine(
        context=context,
        schema_data={
            'columns': {
                'col1': {'null_handling': {'strategy': 'forward_fill', 'fill_value': 'NA'}},
                'col2': {'null_handling': {'strategy': 'leave_null'}},
                'col3': {'null_handling': {'strategy': 'default_value', 'fill_value': '0'}}
            },
            'parameters': {}
        }
    )
    
    # Create small test DataFrame
    df_small = pd.DataFrame({
        'col1': [1, None, None, 4, None],
        'col2': ['A', None, 'C', None, 'E'],
        'col3': [10, 20, None, None, 50]
    })
    
    print(f"Input DataFrame (5 rows):\n{df_small}\n")
    
    # Test _apply_phase_null_handling
    print("Calling _apply_phase_null_handling for columns: ['col1', 'col3']...")
    df_result = engine._apply_phase_null_handling(df_small, ['col1', 'col3'])
    print(f"Result:\n{df_result}\n")
    print("✓ _apply_phase_null_handling works on small dataset")
    
except Exception as e:
    print(f"✗ _apply_phase_null_handling failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n=== ALL TESTS PASSED ===")

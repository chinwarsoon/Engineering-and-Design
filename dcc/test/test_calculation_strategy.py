"""
Test Calculation Strategy System

Verifies that the strategy resolver and executor work correctly
for different column types with different preservation modes.
"""

import sys
sys.path.insert(0, '/home/franklin/dsai/Engineering-and-Design/dcc/workflow')

import pandas as pd
import numpy as np
from processor_engine.core.calculation_strategy import (
    StrategyResolver,
    CalculationStrategy,
    PreservationMode,
    CalculationTiming,
    NullHandlingTiming,
    FallbackType,
    get_column_strategy,
    should_calculate_for_row
)


def test_document_id_strategy():
    """Test Document_ID gets correct preserve_existing strategy."""
    print("\n🧪 Testing Document_ID strategy...")
    
    column_def = {
        "is_calculated": True,
        "calculation": {
            "type": "composite",
            "method": "build_document_id",
            "source_columns": ["Project_Code", "Facility_Code", "Document_Type", "Discipline", "Document_Sequence_Number"]
        },
        "null_handling": {
            "strategy": "leave_null"
        }
    }
    
    strategy = get_column_strategy("Document_ID", column_def)
    
    assert strategy.preservation_mode == PreservationMode.PRESERVE_EXISTING
    assert strategy.null_handling_timing == NullHandlingTiming.LAST_DEFENSE
    assert strategy.fallback_type == FallbackType.LEAVE_NULL
    
    print(f"   ✓ Document_ID: {strategy}")
    return True


def test_submission_closed_strategy():
    """Test Submission_Closed gets built_in null handling strategy."""
    print("\n🧪 Testing Submission_Closed strategy...")
    
    column_def = {
        "is_calculated": True,
        "calculation": {
            "type": "conditional",
            "method": "submission_closure_status",
            "preprocessing": {
                "text_cleaning": {
                    "convert_to_uppercase": True,
                    "fill_nulls": "NO"
                }
            },
            "logic": {
                "conditions": [
                    {"if": "Submission_Closed == 'YES'", "then": "'YES'"},
                    {"else": "'NO'"}
                ]
            }
        },
        "null_handling": {
            "strategy": "default_value",  # Different from leave_null
            "default_value": "NO"
        }
    }
    
    strategy = get_column_strategy("Submission_Closed", column_def)
    
    # Should detect built-in fallback from else clause
    assert strategy.preservation_mode == PreservationMode.PRESERVE_EXISTING
    # With preprocessing and logic.else, should be BUILT_IN
    assert strategy.null_handling_timing == NullHandlingTiming.BUILT_IN
    assert strategy.fallback_type == FallbackType.CALCULATED_DEFAULT
    
    print(f"   ✓ Submission_Closed: {strategy}")
    return True


def test_validation_errors_strategy():
    """Test Validation_Errors gets overwrite strategy."""
    print("\n🧪 Testing Validation_Errors strategy...")
    
    column_def = {
        "is_calculated": True,
        "calculation": {
            "type": "error_tracking",
            "method": "aggregate_validation_errors"
        }
    }
    
    strategy = get_column_strategy("Validation_Errors", column_def)
    
    assert strategy.preservation_mode == PreservationMode.OVERWRITE_EXISTING
    assert strategy.null_handling_timing == NullHandlingTiming.SKIP
    assert strategy.fallback_type == FallbackType.DEFAULT_VALUE
    assert strategy.fallback_value == ""
    
    print(f"   ✓ Validation_Errors: {strategy}")
    return True


def test_row_index_strategy():
    """Test Row_Index gets auto_increment strategy."""
    print("\n🧪 Testing Row_Index strategy...")
    
    column_def = {
        "is_calculated": True,
        "calculation": {
            "type": "auto_increment",
            "method": "generate_row_index"
        }
    }
    
    strategy = get_column_strategy("Row_Index", column_def)
    
    assert strategy.preservation_mode == PreservationMode.PRESERVE_EXISTING
    assert strategy.fallback_type == FallbackType.AUTO_GENERATE
    
    print(f"   ✓ Row_Index: {strategy}")
    return True


def test_explicit_strategy_config():
    """Test explicit strategy configuration from schema."""
    print("\n🧪 Testing explicit strategy configuration...")
    
    column_def = {
        "is_calculated": True,
        "calculation": {"type": "test"},
        "strategy": {
            "data_preservation": {"mode": "conditional_overwrite"},
            "processing_sequence": {
                "calculation_timing": "last",
                "null_handling_timing": "before_calculation"
            },
            "fallback": {
                "type": "forward_fill",
                "value": "default"
            }
        }
    }
    
    strategy = get_column_strategy("TestColumn", column_def)
    
    assert strategy.preservation_mode == PreservationMode.CONDITIONAL_OVERWRITE
    assert strategy.calculation_timing == CalculationTiming.LAST
    assert strategy.null_handling_timing == NullHandlingTiming.BEFORE_CALCULATION
    assert strategy.fallback_type == FallbackType.FORWARD_FILL
    assert strategy.fallback_value == "default"
    
    print(f"   ✓ Explicit config: {strategy}")
    return True


def test_should_calculate_for_row():
    """Test row-level calculation decision logic."""
    print("\n🧪 Testing should_calculate_for_row...")
    
    # Test preserve_existing - only calculate for nulls
    strategy_preserve = CalculationStrategy(
        column_name="test",
        preservation_mode=PreservationMode.PRESERVE_EXISTING,
        calculation_timing=CalculationTiming.FIRST,
        null_handling_timing=NullHandlingTiming.LAST_DEFENSE,
        fallback_type=FallbackType.LEAVE_NULL
    )
    
    assert should_calculate_for_row(None, strategy_preserve) == True  # Null - calculate
    assert should_calculate_for_row(np.nan, strategy_preserve) == True  # NaN - calculate
    assert should_calculate_for_row("existing_value", strategy_preserve) == False  # Existing - skip
    
    # Test overwrite_existing - calculate for all
    strategy_overwrite = CalculationStrategy(
        column_name="test",
        preservation_mode=PreservationMode.OVERWRITE_EXISTING,
        calculation_timing=CalculationTiming.FIRST,
        null_handling_timing=NullHandlingTiming.SKIP,
        fallback_type=FallbackType.DEFAULT_VALUE,
        fallback_value=""
    )
    
    assert should_calculate_for_row("existing_value", strategy_overwrite) == True  # Overwrite all
    
    print("   ✓ Row-level calculation decisions correct")
    return True


def main():
    """Run all strategy tests."""
    print("=" * 60)
    print("Calculation Strategy System Tests")
    print("=" * 60)
    
    tests = [
        test_document_id_strategy,
        test_submission_closed_strategy,
        test_validation_errors_strategy,
        test_row_index_strategy,
        test_explicit_strategy_config,
        test_should_calculate_for_row,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            failed += 1
            print(f"   ❌ FAILED: {e}")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

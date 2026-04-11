"""
Calculation Strategy Handler

Provides centralized strategy resolution and execution for calculated columns.
Reads strategy configuration from schema and applies appropriate processing logic.
"""

import pandas as pd
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class PreservationMode(Enum):
    """Data preservation modes for calculated columns."""
    PRESERVE_EXISTING = "preserve_existing"
    OVERWRITE_EXISTING = "overwrite_existing"
    CONDITIONAL_OVERWRITE = "conditional_overwrite"


class CalculationTiming(Enum):
    """When to run calculation relative to null handling."""
    FIRST = "first"
    LAST = "last"
    CONDITIONAL = "conditional"


class NullHandlingTiming(Enum):
    """When to apply null handling."""
    LAST_DEFENSE = "last_defense"
    BEFORE_CALCULATION = "before_calculation"
    BUILT_IN = "built_in"
    SKIP = "skip"


class FallbackType(Enum):
    """Fallback strategies when calculation cannot determine a value."""
    LEAVE_NULL = "leave_null"
    DEFAULT_VALUE = "default_value"
    FORWARD_FILL = "forward_fill"
    CALCULATED_DEFAULT = "calculated_default"
    AUTO_GENERATE = "auto_generate"


@dataclass
class CalculationStrategy:
    """Complete strategy configuration for a calculated column."""
    column_name: str
    preservation_mode: PreservationMode
    calculation_timing: CalculationTiming
    null_handling_timing: NullHandlingTiming
    fallback_type: FallbackType
    fallback_value: Any = None
    fallback_value_source: Optional[str] = None
    
    def __str__(self) -> str:
        return (
            f"CalculationStrategy({self.column_name}: "
            f"{self.preservation_mode.value}, "
            f"calc={self.calculation_timing.value}, "
            f"null={self.null_handling_timing.value}, "
            f"fallback={self.fallback_type.value})"
        )


class StrategyResolver:
    """Resolves strategy from schema column definition."""
    
    @staticmethod
    def from_schema(column_name: str, column_def: Dict[str, Any]) -> CalculationStrategy:
        """
        Resolve calculation strategy from schema column definition.
        
        Uses explicit strategy config if present, otherwise infers from:
        - is_calculated
        - calculation type
        - null_handling config
        - column name patterns
        """
        # Check for explicit strategy config
        strategy_config = column_def.get("strategy")
        if strategy_config:
            return StrategyResolver._from_explicit_config(column_name, strategy_config)
        
        # Infer strategy from column properties
        return StrategyResolver._infer_strategy(column_name, column_def)
    
    @staticmethod
    def _from_explicit_config(column_name: str, config: Dict[str, Any]) -> CalculationStrategy:
        """Create strategy from explicit configuration."""
        data_preservation = config.get("data_preservation", {})
        processing_sequence = config.get("processing_sequence", {})
        fallback = config.get("fallback", {})
        
        return CalculationStrategy(
            column_name=column_name,
            preservation_mode=PreservationMode(data_preservation.get("mode", "preserve_existing")),
            calculation_timing=CalculationTiming(processing_sequence.get("calculation_timing", "first")),
            null_handling_timing=NullHandlingTiming(processing_sequence.get("null_handling_timing", "last_defense")),
            fallback_type=FallbackType(fallback.get("type", "leave_null")),
            fallback_value=fallback.get("value"),
            fallback_value_source=fallback.get("value_source")
        )
    
    @staticmethod
    def _infer_strategy(column_name: str, column_def: Dict[str, Any]) -> CalculationStrategy:
        """Infer strategy from column definition properties."""
        is_calculated = column_def.get("is_calculated", False)
        calculation = column_def.get("calculation", {})
        null_handling = column_def.get("null_handling", {})
        
        if not is_calculated:
            raise ValueError(f"Cannot resolve strategy for non-calculated column: {column_name}")
        
        # Special cases based on column name
        if column_name == "Validation_Errors":
            return CalculationStrategy(
                column_name=column_name,
                preservation_mode=PreservationMode.OVERWRITE_EXISTING,
                calculation_timing=CalculationTiming.FIRST,
                null_handling_timing=NullHandlingTiming.SKIP,
                fallback_type=FallbackType.DEFAULT_VALUE,
                fallback_value=""
            )
        
        # Check for built-in null handling in calculation
        calc_type = calculation.get("type", "")
        calc_method = calculation.get("method", "")
        has_preprocessing = "preprocessing" in calculation
        has_logic_else = any("else" in str(cond) for cond in calculation.get("logic", {}).get("conditions", []))
        
        # Built-in fallback detection
        if has_preprocessing and has_logic_else and null_handling.get("strategy") != "leave_null":
            # Has preprocessing and default logic - built-in fallback
            return CalculationStrategy(
                column_name=column_name,
                preservation_mode=PreservationMode.PRESERVE_EXISTING,
                calculation_timing=CalculationTiming.FIRST,
                null_handling_timing=NullHandlingTiming.BUILT_IN,
                fallback_type=FallbackType.CALCULATED_DEFAULT,
                fallback_value_source="calculation_logic"
            )
        
        # Standard preserve + last defense (most common)
        null_strategy = null_handling.get("strategy", "leave_null")
        fallback_type = FallbackType.LEAVE_NULL if null_strategy == "leave_null" else FallbackType.DEFAULT_VALUE
        
        return CalculationStrategy(
            column_name=column_name,
            preservation_mode=PreservationMode.PRESERVE_EXISTING,
            calculation_timing=CalculationTiming.FIRST,
            null_handling_timing=NullHandlingTiming.LAST_DEFENSE,
            fallback_type=fallback_type,
            fallback_value=null_handling.get("default_value")
        )


class StrategyExecutor:
    """Executes calculations according to resolved strategy."""
    
    def __init__(self, engine):
        self.engine = engine
    
    def apply_calculation_with_strategy(
        self,
        df: pd.DataFrame,
        column_name: str,
        calculation: Dict[str, Any],
        strategy: CalculationStrategy,
        calculation_handler: Callable
    ) -> pd.DataFrame:
        """
        Apply calculation respecting the column's strategy.
        
        Args:
            df: DataFrame to process
            column_name: Target column
            calculation: Calculation configuration from schema
            strategy: Resolved calculation strategy
            calculation_handler: The specific handler function for this calculation type
        
        Returns:
            DataFrame with calculation applied according to strategy
        """
        df_result = df.copy()
        
        # Check if column exists
        if column_name not in df_result.columns:
            df_result[column_name] = None
        
        # Apply data preservation mask
        if strategy.preservation_mode == PreservationMode.PRESERVE_EXISTING:
            existing_mask = df_result[column_name].notna()
            null_mask = df_result[column_name].isna()
            
            if existing_mask.any():
                self.engine._print_processing_step(
                    "Strategy", column_name,
                    f"Preserving {existing_mask.sum()} existing values per strategy"
                )
            
            # Only calculate for null values
            if null_mask.any():
                # Create temporary DataFrame with only null rows
                df_to_calc = df_result[null_mask].copy()
                df_calculated = calculation_handler(self.engine, df_to_calc, column_name, calculation)
                
                # Update only the null values
                df_result.loc[null_mask, column_name] = df_calculated.loc[null_mask, column_name]
            else:
                self.engine._print_processing_step(
                    "Strategy", column_name,
                    "Skipped calculation: all values present"
                )
                
        elif strategy.preservation_mode == PreservationMode.OVERWRITE_EXISTING:
            # Calculate for all rows
            df_result = calculation_handler(self.engine, df_result, column_name, calculation)
            
        elif strategy.preservation_mode == PreservationMode.CONDITIONAL_OVERWRITE:
            # Apply based on condition (future implementation)
            pass
        
        return df_result
    
    def apply_fallback(
        self,
        df: pd.DataFrame,
        column_name: str,
        strategy: CalculationStrategy,
        null_handling_config: Dict[str, Any]
    ) -> pd.DataFrame:
        """
        Apply fallback strategy for values that remain null after calculation.
        
        Only called if strategy.null_handling_timing is LAST_DEFENSE.
        """
        if strategy.null_handling_timing != NullHandlingTiming.LAST_DEFENSE:
            return df
        
        df_result = df.copy()
        null_mask = df_result[column_name].isna()
        
        if not null_mask.any():
            return df_result
        
        self.engine._print_processing_step(
            "Strategy-Fallback", column_name,
            f"Applying {strategy.fallback_type.value} to {null_mask.sum()} remaining nulls"
        )
        
        if strategy.fallback_type == FallbackType.LEAVE_NULL:
            # Do nothing - leave as null
            pass
            
        elif strategy.fallback_type == FallbackType.DEFAULT_VALUE:
            df_result.loc[null_mask, column_name] = strategy.fallback_value
            
        elif strategy.fallback_type == FallbackType.CALCULATED_DEFAULT:
            # Use value from calculation logic (already applied)
            pass
            
        elif strategy.fallback_type == FallbackType.FORWARD_FILL:
            from ..registry import get_null_handler
            handler = get_null_handler("forward_fill")
            if handler:
                df_result = handler(self.engine, df_result, column_name, null_handling_config)
        
        return df_result


def get_column_strategy(column_name: str, column_def: Dict[str, Any]) -> CalculationStrategy:
    """
    Public function to get strategy for a column.
    
    Usage:
        strategy = get_column_strategy("Document_ID", schema_columns["Document_ID"])
        print(strategy.preservation_mode)  # PreservationMode.PRESERVE_EXISTING
    """
    return StrategyResolver.from_schema(column_name, column_def)


def should_calculate_for_row(
    row_value: Any,
    strategy: CalculationStrategy
) -> bool:
    """
    Determine if calculation should run for a specific row value.
    
    Usage:
        if should_calculate_for_row(df.at[idx, "Document_ID"], strategy):
            # Run calculation
    """
    import pandas as pd
    
    is_null = pd.isna(row_value)
    
    if strategy.preservation_mode == PreservationMode.PRESERVE_EXISTING:
        return is_null  # Only calculate for nulls
    elif strategy.preservation_mode == PreservationMode.OVERWRITE_EXISTING:
        return True  # Calculate for all
    elif strategy.preservation_mode == PreservationMode.CONDITIONAL_OVERWRITE:
        # Future: check condition
        return True
    
    return is_null

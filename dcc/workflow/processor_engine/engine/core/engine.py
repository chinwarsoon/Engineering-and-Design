"""
House the CalculationEngine class itself, specifically the
  __init__ (initialization),
  _resolve_calculation_order (DAG sorting),
  apply_calculations,
  apply_null_handling entry points.
"""

import logging
import pandas as pd
from typing import Dict, List, Set, Optional

# Configure logging
logger = logging.getLogger(__name__)

from .base import BaseProcessor

# Import hierarchical logging functions from initiation_engine (centralized)
from initiation_engine.engine import log_context, status_print, debug_print

class CalculationEngine(BaseProcessor):
    """
    The orchestrator for the modular calculation engine.
    This class manages the sequence of null handling and calculation execution.
    """

    def __init__(self, schema_data: Dict):
        """
        Initialize the engine using the resolved schema.
        """
        super().__init__(schema_data)
        enhanced_schema = schema_data.get('enhanced_schema', {})
        raw_columns = enhanced_schema.get('columns', {})
        column_sequence = enhanced_schema.get('column_sequence', [])

        # Build the column definition dictionary based on schema sequence
        if column_sequence:
            self.columns = {
                name: raw_columns[name]
                for name in column_sequence
                if name in raw_columns and isinstance(raw_columns[name], dict)
            }
            # Append any remaining columns not in the explicit sequence
            for name, definition in raw_columns.items():
                if name not in self.columns and isinstance(definition, dict):
                    self.columns[name] = definition
        else:
            self.columns = {name: defn for name, defn in raw_columns.items() if isinstance(defn, dict)}

        # Determine the safe execution order for calculated columns
        from ..schema.dependency import resolve_calculation_order
        self.calculation_order = resolve_calculation_order(self.columns)

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        The main entry point for data transformation.
        """
        with log_context("processor", "process_data"):
            debug_print(f"Starting process_data with {len(df.columns)} columns")
            # 1. Apply Null Handling
            df = self.apply_null_handling(df)
            debug_print(f"Finished null handling, now has {len(df.columns)} columns")

            # 2. Apply Calculations
            df = self.apply_calculations(df)
            debug_print(f"Finished calculations, now has {len(df.columns)} columns")

            return df

    def apply_null_handling(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Iterates through the schema and applies the designated null-handling
        strategy to each column.
        """
        with log_context("processor", "apply_null_handling"):
            from ..utils.dateframe import prepare_dataframe_for_processing, initialize_missing_columns
            from .registry import get_null_handler

            debug_print(f"Entering apply_null_handling")
            df_processed = prepare_dataframe_for_processing(df)

            # Initialize missing columns from schema
            parameters = self.schema_data.get('parameters', {})
            df_processed = initialize_missing_columns(df_processed, self.columns, parameters)
            debug_print(f"DataFrame prepared and initialized, has {len(df_processed.columns)} columns")

            for column_name, column_def in self.columns.items():
                if column_name not in df_processed.columns:
                    continue

                null_handling = column_def.get('null_handling', {})
                strategy = null_handling.get('strategy')

                if strategy and strategy != 'leave_null':
                    handler = get_null_handler(strategy)
                    if handler:
                        # debug_print(f"Applying null strategy {strategy} to {column_name}")
                        df_processed = handler(self, df_processed, column_name, null_handling)

            return df_processed

    def apply_calculations(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Executes calculated columns in the validated dependency order.
        """
        with log_context("processor", "apply_calculations"):
            from .registry import get_calculation_handler

            debug_print(f"Entering apply_calculations, order: {self.calculation_order}")
            df_calculated = df.copy()

            for column_name in self.calculation_order:
                column_def = self.columns[column_name]
                calculation = column_def.get('calculation', {})
                calc_type = calculation.get('type')

                handler = get_calculation_handler(calc_type, calculation.get('method'))
                if handler:
                    debug_print(f"Applying {calc_type}/{calculation.get('method')} to {column_name}")
                    df_calculated = handler(self, df_calculated, column_name, calculation)
                else:
                    status_print(f"WARNING: No handler found for calculation type: {calc_type}")

            return df_calculated

    def _print_processing_step(self, phase: str, column_name: str, detail: str):
        """Standardized logging for processing progress."""
        message = f"[{phase}] {column_name}: {detail}"
        status_print(message)
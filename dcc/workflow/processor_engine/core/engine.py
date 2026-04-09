"""
House the CalculationEngine class itself, specifically the
  __init__ (initialization),
  _resolve_calculation_order (DAG sorting),
  apply_calculations,
  apply_null_handling entry points.
"""

import logging
import pandas as pd
from typing import Dict, List, Set, Optional, Any

# Configure logging
logger = logging.getLogger(__name__)

from .base import BaseProcessor

# Import hierarchical logging functions from initiation_engine (centralized)
from initiation_engine import log_context, status_print, debug_print

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
        Uses phased processing: P1 → P2 → P2.5 → P3
        For calculated columns (P2.5, P3): Calculations run FIRST, null handling as LAST DEFENSE
        """
        with log_context("processor", "process_data"):
            debug_print(f"Starting process_data with {len(df.columns)} columns")
            
            # Use phased processing (P1 → P2 → P2.5 → P3)
            df = self.apply_phased_processing(df)
            debug_print(f"Finished phased processing, now has {len(df.columns)} columns")

            return df

    def apply_phased_processing(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process columns by phase: P1 → P2 → P2.5 → P3
        
        Phase 1 (Meta Data): Null handling with bounded forward fill
        Phase 2 (Transactional): Forward fill if Manual Input = YES, then validate
        Phase 2.5 (Anomaly): Calculations FIRST, then null handling as last defense
        Phase 3 (Calculated): Calculations FIRST, then null handling as last defense
        
        Rule 11: If is_calculated = true, apply calculation FIRST, then null_handling as last defense
        Rule 12: If manual user input is allowed, forward fill with boundary is allowed
        Rule 13: Always respect sequence of columns in the schema
        """
        with log_context("processor", "apply_phased_processing"):
            from ..utils.dateframe import prepare_dataframe_for_processing, initialize_missing_columns
            
            # Initialize DataFrame
            df_processed = prepare_dataframe_for_processing(df)
            parameters = self.schema_data.get('parameters', {})
            df_processed = initialize_missing_columns(df_processed, self.columns, parameters)
            
            # Get column sequence from schema (Rule 13)
            enhanced_schema = self.schema_data.get('enhanced_schema', {})
            column_sequence = enhanced_schema.get('column_sequence', [])
            
            # Group columns by processing phase
            phase_columns = {'P1': [], 'P2': [], 'P2.5': [], 'P3': []}
            for col_name in column_sequence:
                if col_name in self.columns:
                    phase = self.columns[col_name].get('processing_phase', 'P3')
                    if phase in phase_columns:
                        phase_columns[phase].append(col_name)
            
            debug_print(f"Phase distribution: P1={len(phase_columns['P1'])}, P2={len(phase_columns['P2'])}, P2.5={len(phase_columns['P2.5'])}, P3={len(phase_columns['P3'])}")
            
            # Phase 1: Meta Data - Apply null handling (forward fill OK)
            if phase_columns['P1']:
                self._print_processing_step("Phase 1", "Meta Data", f"Processing {len(phase_columns['P1'])} columns")
                df_processed = self._apply_phase_null_handling(df_processed, phase_columns['P1'])
            
            # Phase 2: Transactional - Forward fill if Manual Input = YES, then validate
            if phase_columns['P2']:
                self._print_processing_step("Phase 2", "Transactional", f"Processing {len(phase_columns['P2'])} columns")
                df_processed = self._apply_phase_transactional(df_processed, phase_columns['P2'])
            
            # Phase 2.5: Anomaly - Calculations FIRST, then null handling
            if phase_columns['P2.5']:
                self._print_processing_step("Phase 2.5", "Anomaly", f"Processing {len(phase_columns['P2.5'])} columns")
                df_processed = self._apply_phase_calculated(df_processed, phase_columns['P2.5'])
            
            # Phase 3: Calculated - Calculations FIRST, then null handling (last defense)
            if phase_columns['P3']:
                self._print_processing_step("Phase 3", "Calculated", f"Processing {len(phase_columns['P3'])} columns")
                df_processed = self._apply_phase_calculated(df_processed, phase_columns['P3'])
            
            return df_processed

    def _apply_phase_null_handling(self, df: pd.DataFrame, column_names: List[str]) -> pd.DataFrame:
        """Apply null handling for a specific phase (P1 or P2)."""
        from .registry import get_null_handler
        
        df_result = df.copy()
        for column_name in column_names:
            if column_name not in df_result.columns:
                continue
                
            column_def = self.columns[column_name]
            null_handling = column_def.get('null_handling', {})
            strategy = null_handling.get('strategy')
            
            if strategy and strategy != 'leave_null':
                handler = get_null_handler(strategy)
                if handler:
                    df_result = handler(self, df_result, column_name, null_handling)
                    
        return df_result

    def _apply_phase_transactional(self, df: pd.DataFrame, column_names: List[str]) -> pd.DataFrame:
        """
        Apply Phase 2 transactional processing.
        Rule 12: If manual user input is allowed, forward fill with boundary is allowed.
        """
        from .registry import get_null_handler
        
        df_result = df.copy()
        
        for column_name in column_names:
            if column_name not in df_result.columns:
                continue
                
            column_def = self.columns[column_name]
            null_handling = column_def.get('null_handling', {})
            strategy = null_handling.get('strategy')
            
            # For P2 columns: Apply forward fill if strategy is defined
            if strategy and strategy != 'leave_null':
                handler = get_null_handler(strategy)
                if handler:
                    self._print_processing_step("P2-ForwardFill", column_name, f"Applying {strategy}")
                    df_result = handler(self, df_result, column_name, null_handling)
                    
        return df_result

    def _apply_phase_calculated(self, df: pd.DataFrame, column_names: List[str]) -> pd.DataFrame:
        """
        Apply Phase 2.5 or P3 calculated processing.
        Rule 11: Calculation FIRST, then null handling as LAST DEFENSE.
        """
        from .registry import get_calculation_handler, get_null_handler
        
        df_result = df.copy()
        
        # Step 1: Apply calculations FIRST
        for column_name in column_names:
            if column_name not in self.columns:
                continue
                
            column_def = self.columns[column_name]
            calculation = column_def.get('calculation', {})
            calc_type = calculation.get('type')
            
            if calc_type:
                handler = get_calculation_handler(calc_type, calculation.get('method'))
                if handler:
                    self._print_processing_step("Calculation", column_name, f"Applying {calc_type}/{calculation.get('method')}")
                    df_result = handler(self, df_result, column_name, calculation)
        
        # Step 2: Apply null handling as LAST DEFENSE (only for remaining nulls)
        for column_name in column_names:
            if column_name not in df_result.columns:
                continue
                
            column_def = self.columns[column_name]
            null_handling = column_def.get('null_handling', {})
            strategy = null_handling.get('strategy')
            
            # Only apply null handling if there are still nulls after calculation
            if strategy and strategy != 'leave_null' and df_result[column_name].isna().any():
                handler = get_null_handler(strategy)
                if handler:
                    self._print_processing_step("Last-Defense", column_name, f"Filling remaining nulls with {strategy}")
                    df_result = handler(self, df_result, column_name, null_handling)
                    
        return df_result

    def apply_null_handling(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        [DEPRECATED for direct use] - Use apply_phased_processing() instead.
        
        Iterates through the schema and applies the designated null-handling
        strategy to each column. This method is now used internally by
        apply_phased_processing() for P1 and P2 columns.
        
        For calculated columns (P2.5, P3), null handling is applied as LAST DEFENSE
        after calculations in _apply_phase_calculated().
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
        [DEPRECATED for direct use] - Use apply_phased_processing() instead.
        
        Executes calculated columns in the validated dependency order.
        This method is now used internally by _apply_phase_calculated()
        which runs calculations FIRST, then null handling as LAST DEFENSE.
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
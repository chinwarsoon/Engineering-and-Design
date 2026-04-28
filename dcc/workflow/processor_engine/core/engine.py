"""
House the CalculationEngine class itself, specifically the
  __init__ (initialization),
  _resolve_calculation_order (DAG sorting),
  apply_calculations,
  apply_null_handling entry points.

Phase 2 DI Update: Supports dependency injection for all components
while maintaining backward compatibility with legacy instantiation.
"""

import logging
import pandas as pd
from typing import Dict, List, Set, Optional, Any, TYPE_CHECKING

# Configure logging
logger = logging.getLogger(__name__)

from core_engine.base import BaseProcessor
from .calculation_strategy import (
    StrategyResolver,
    StrategyExecutor,
    CalculationStrategy,
    NullHandlingTiming,
    get_column_strategy
)

# Import hierarchical logging functions from utility_engine and core_engine
from utility_engine.console import status_print, debug_print
from core_engine.logging import log_context, DEBUG_LEVEL

# Phase 4: Import error handling components
from ..error_handling.detectors.business import ProcessingPhase

from core_engine.context import PipelineContext

# Phase 2 DI: Import interfaces for type hints
if TYPE_CHECKING:
    from ..interfaces import (
        IErrorReporter,
        IErrorAggregator,
        IStructuredLogger,
        IBusinessDetector,
        IStrategyResolver,
    )


class CalculationEngine(BaseProcessor):
    """
    The orchestrator for the modular calculation engine.
    This class manages the sequence of null handling and calculation execution.
    
    Phase 2 DI Update: Supports dependency injection for:
    - error_reporter: IErrorReporter implementation
    - error_aggregator: IErrorAggregator implementation
    - structured_logger: IStructuredLogger implementation
    - business_detector: IBusinessDetector implementation
    - strategy_resolver: IStrategyResolver implementation
    """

    def __init__(
        self,
        context: PipelineContext,
        schema_data: Dict,
        error_reporter: Optional['IErrorReporter'] = None,
        error_aggregator: Optional['IErrorAggregator'] = None,
        structured_logger: Optional['IStructuredLogger'] = None,
        business_detector: Optional['IBusinessDetector'] = None,
        strategy_resolver: Optional['IStrategyResolver'] = None,
    ):
        """
        Initialize the engine using the resolved schema.
        
        Args:
            context: Pipeline context with paths, parameters, and state
            schema_data: Resolved schema data with column definitions
            error_reporter: Optional error reporter implementation (DI)
            error_aggregator: Optional error aggregator implementation (DI)
            structured_logger: Optional structured logger implementation (DI)
            business_detector: Optional business detector implementation (DI)
            strategy_resolver: Optional strategy resolver implementation (DI)
            
        Note:
            If dependencies are not provided, they are created with default
            implementations for backward compatibility.
        """
        super().__init__(context, schema_data)
        
        # Phase 2 DI: Initialize dependencies (injected or default)
        parameters = schema_data.get('parameters', {})
        fail_fast = parameters.get('fail_fast', True)
        
        # Lazy imports to avoid circular dependencies
        if structured_logger is None:
            from ..error_handling.core.logger import StructuredLogger
            structured_logger = StructuredLogger()
        self.structured_logger = structured_logger
        
        if error_aggregator is None:
            from ..error_handling.aggregator import ErrorAggregator
            error_aggregator = ErrorAggregator()
        self.error_aggregator = error_aggregator
        
        if business_detector is None:
            from ..error_handling.detectors.business import BusinessDetector
            business_detector = BusinessDetector(
                enable_fail_fast=fail_fast,
                logger=self.structured_logger
            )
        self.business_detector = business_detector
        
        if error_reporter is None:
            from reporting_engine.error_reporter import ErrorReporter
            error_reporter = ErrorReporter(self.error_aggregator)
        self.error_reporter = error_reporter
        
        self._last_processed_rows = 0
        
        # Support new top-level 'columns' key and legacy 'enhanced_schema.columns'
        _schema_root = schema_data if 'columns' in schema_data else schema_data.get('enhanced_schema', {})
        raw_columns = _schema_root.get('columns', {})
        column_sequence = _schema_root.get('column_sequence', [])

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
        
        # Phase 2 DI: Initialize strategy resolver (injected or default)
        if strategy_resolver is None:
            strategy_resolver = StrategyResolver()
        self.strategy_resolver = strategy_resolver
        self._column_strategies = {}  # Cache resolved strategies
        self.strategy_executor = None  # Initialized on first use

    def get_column_strategy(self, column_name: str) -> Optional[CalculationStrategy]:
        """
        Get or resolve calculation strategy for a column.
        
        Args:
            column_name: Name of the column
            
        Returns:
            CalculationStrategy if column is calculated, None otherwise
        """
        # Return cached strategy if available
        if column_name in self._column_strategies:
            return self._column_strategies[column_name]
        
        # Get column definition
        if column_name not in self.columns:
            return None
            
        column_def = self.columns[column_name]
        
        # Only calculated columns have strategies
        if not column_def.get("is_calculated", False):
            return None
        
        # Resolve and cache strategy
        strategy = self.strategy_resolver.from_schema(column_name, column_def)
        self._column_strategies[column_name] = strategy
        
        status_print(f"Resolved strategy for {column_name}: {strategy}", min_level=3)
        
        return strategy

    def process_data(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        The main entry point for data transformation.
        Uses phased processing: P1 → P2 → P2.5 → P3
        For calculated columns (P2.5, P3): Calculations run FIRST, null handling as LAST DEFENSE
        
        Phase 3: Added telemetry heartbeat logging every 1,000 rows (R17)
        """
        if df is None:
            df = self.context.data.df_mapped
            if df is None:
                raise ValueError("No input DataFrame provided in context.data.df_mapped.")
                
        with log_context("processor", "process_data"):
            debug_print(f"Starting process_data with {len(df.columns)} columns")
            self._last_processed_rows = len(df)
            
            # Phase 3: Initialize telemetry heartbeat
            from core_engine.telemetry_heartbeat import TelemetryHeartbeat
            heartbeat = TelemetryHeartbeat(interval=1000)
            total_rows = len(df)
            status_print(f"🚀 Starting processing of {total_rows:,} rows...", min_level=1)
            
            # Use phased processing (P1 → P2 → P2.5 → P3)
            df = self.apply_phased_processing(df, heartbeat=heartbeat, total_rows=total_rows)
            
            # Phase 3: Emit final heartbeat summary
            final_payload = heartbeat.final_summary(total_rows, status_print_fn=status_print)
            self.context.telemetry.heartbeat_logs.append(final_payload.to_dict())
            
            debug_print(f"Finished phased processing, now has {len(df.columns)} columns")

            # Store in context
            self.context.data.df_processed = df

            return df

    def apply_phased_processing(
        self,
        df: pd.DataFrame,
        heartbeat: Optional[Any] = None,
        total_rows: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Process columns by phase: P1 → P2 → P2.5 → P3
        
        Phase 1 (Meta Data): Null handling with bounded forward fill
        Phase 2 (Transactional): Forward fill if Manual Input = YES, then validate
        Phase 2.5 (Anomaly): Calculations FIRST, then null handling as last defense
        Phase 3 (Calculated): Calculations FIRST, then null handling as last defense
        
        Phase 3: Added telemetry heartbeat tracking (R17)
        
        Rule 11: If is_calculated = true, apply calculation FIRST, then null_handling as last defense
        Rule 12: If manual user input is allowed, forward fill with boundary is allowed
        Rule 13: Always respect sequence of columns in the schema
        """
        with log_context("processor", "apply_phased_processing"):
            from core_engine.data import prepare_dataframe_for_processing, initialize_missing_columns
            
            # Phase 3: Helper to emit heartbeat and store in context
            def _emit_checkpoint(phase: str, rows_processed: int):
                if heartbeat and total_rows:
                    payload = heartbeat.tick(
                        current_row=rows_processed,
                        current_phase=phase,
                        total_rows=total_rows,
                        status_print_fn=status_print,
                    )
                    if payload and hasattr(self.context.telemetry, 'heartbeat_logs'):
                        self.context.telemetry.heartbeat_logs.append(payload.to_dict())
            
            # Initialize DataFrame
            df_processed = prepare_dataframe_for_processing(df)
            parameters = self.context.blueprint.validation_rules or self.schema_data.get('parameters', {})
            df_processed = initialize_missing_columns(df_processed, self.columns, parameters)
            
            # Get total rows for progress tracking
            total_rows = len(df_processed) if total_rows is None else total_rows
            current_rows = 0
            
            # Phase 1: Meta Data - Apply null handling (forward fill OK)
            p1_cols = self.context.blueprint.get_columns_by_phase('P1')
            if p1_cols:
                self._print_processing_step("Phase 1", "Meta Data", f"Processing {len(p1_cols)} columns")
                df_processed = self._apply_phase_null_handling(df_processed, p1_cols)
                current_rows = len(df_processed)
                _emit_checkpoint("P1", current_rows)
                # Phase 4: Run Phase 1 detection
                p1_results = self.business_detector.detect(
                    df_processed, 
                    context={"phase": "P1", "schema_data": self.schema_data}, 
                    phases=[ProcessingPhase.P1]
                )
                self.error_aggregator.add_errors(p1_results.get(ProcessingPhase.P1, []))
            
            # Phase 2: Transactional - Forward fill if Manual Input = YES, then validate
            # Phase C: Initialize fill history tracking for error detection
            self.fill_history = []
            
            p2_cols = self.context.blueprint.get_columns_by_phase('P2')
            if p2_cols:
                self._print_processing_step("Phase 2", "Transactional", f"Processing {len(p2_cols)} columns")
                df_processed = self._apply_phase_transactional(df_processed, p2_cols)
                current_rows = len(df_processed)
                _emit_checkpoint("P2", current_rows)
                # Phase 4: Run Phase 2 detection
                p2_results = self.business_detector.detect(
                    df_processed, 
                    context={"phase": "P2", "schema_data": self.schema_data}, 
                    phases=[ProcessingPhase.P2]
                )
                self.error_aggregator.add_errors(p2_results.get(ProcessingPhase.P2, []))
            
            # Phase 2.5: Anomaly - Calculations FIRST, then null handling
            p25_cols = self.context.blueprint.get_columns_by_phase('P2.5')
            if p25_cols:
                self._print_processing_step("Phase 2.5", "Anomaly", f"Processing {len(p25_cols)} columns")
                df_processed = self._apply_phase_calculated(df_processed, p25_cols)
                current_rows = len(df_processed)
                _emit_checkpoint("P2.5", current_rows)
                # Phase 4: Run Phase 2.5 detection
                # Phase C: Include fill_history in context for FillDetector
                p25_results = self.business_detector.detect(
                    df_processed, 
                    context={
                        "phase": "P2.5", 
                        "schema_data": self.schema_data,
                        "fill_history": getattr(self, 'fill_history', [])
                    }, 
                    phases=[ProcessingPhase.P2_5]
                )
                self.error_aggregator.add_errors(p25_results.get(ProcessingPhase.P2_5, []))
                # Phase C: Clear fill history after detection to prevent memory bloat
                self.fill_history = []
            
            # Phase 3: Calculated - Calculations FIRST, then null handling (last defense)
            p3_cols = self.context.blueprint.get_columns_by_phase('P3')
            if p3_cols:
                self._print_processing_step("Phase 3", "Calculated", f"Processing {len(p3_cols)} columns")
                df_processed = self._apply_phase_calculated(df_processed, p3_cols)
                current_rows = len(df_processed)
                _emit_checkpoint("P3", current_rows)
                # Phase 4: Run Phase 3 detection
                p3_results = self.business_detector.detect(
                    df_processed, 
                    context={"phase": "P3", "schema_data": self.schema_data}, 
                    phases=[ProcessingPhase.P3]
                )
                self.error_aggregator.add_errors(p3_results.get(ProcessingPhase.P3, []))
            
            # Phase 4: Validation - Apply schema validation rules
            self._print_processing_step("Phase 4", "Validation", "Applying all schema validation rules")
            from ..calculations.validation import apply_validation
            schema_data_full = self.schema_data
            df_processed = apply_validation(df_processed, self.columns, schema_data_full)

            # Phase 4: Row Validation - Cross-field business logic
            self._print_processing_step("Phase 4", "RowValidation", "Running row-level cross-field checks")
            from ..error_handling.detectors.row_validator import RowValidator
            row_validator = RowValidator(
                logger_inst=self.structured_logger,
                enable_fail_fast=False,
            )
            row_errors = row_validator.detect(
                df_processed,
                context={"phase": "P4", "schema_data": self.schema_data},
            )
            self.error_aggregator.add_errors(row_errors)
            status_print(
                f"✓ Row validation complete: {len(row_errors)} cross-field issues found", min_level=2
            )

            # Phase 4: Aggregation - Populate Validation_Errors column (Step 46)
            self._print_processing_step("Phase 4", "Aggregation", "Populating Validation_Errors column")
            df_processed["Validation_Errors"] = self.error_aggregator.format_validation_errors_column(len(df_processed))
            
            # Phase 5: Metrics (Layer 5) - Populate Data_Health_Score column (Step 48)
            self._print_processing_step("Phase 5", "Metrics", "Calculating Data_Health_Score")
            from reporting_engine.data_health import calculate_row_health_series
            df_processed["Data_Health_Score"] = calculate_row_health_series(df_processed, self.error_aggregator)
            
            return df_processed

    def get_error_summary(self) -> Dict[str, Any]:
        """Phase 5: Returns structured error summary for reporting."""
        return self.error_reporter.generate_summary_stats(self._last_processed_rows)

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
        Apply Phase 2.5 or P3 calculated processing with strategy support.
        Rule 11: If is_calculated = true, apply calculation FIRST, then null_handling as last defense.
        
        Strategy-aware processing allows each column to define its own:
        - Data preservation mode (preserve_existing, overwrite_existing)
        - Processing sequence (calculation timing, null handling timing)
        - Fallback behavior for values that cannot be calculated
        """
        from .registry import get_calculation_handler, get_null_handler
        
        # Initialize strategy executor on first use
        if self.strategy_executor is None:
            self.strategy_executor = StrategyExecutor(self)
        
        df_result = df.copy()
        
        # Step 1: Apply calculations FIRST (respecting each column's strategy)
        for column_name in column_names:
            if column_name not in self.columns:
                continue
                
            column_def = self.columns[column_name]
            calculation = column_def.get('calculation', {})
            calc_type = calculation.get('type')
            
            if not calc_type:
                continue
                
            # Get calculation handler
            handler = get_calculation_handler(calc_type, calculation.get('method'))
            if not handler:
                continue
            
            # Get or resolve strategy for this column
            strategy = self.get_column_strategy(column_name)
            
            if strategy:
                # Strategy-aware calculation
                self._print_processing_step(
                    "Strategy-Calc", column_name,
                    f"Applying {calc_type}/{calculation.get('method')} "
                    f"with {strategy.preservation_mode.value}"
                )
                df_result = self.strategy_executor.apply_calculation_with_strategy(
                    df_result, column_name, calculation, strategy, handler
                )
            else:
                # Legacy mode: apply handler directly
                self._print_processing_step("Calculation", column_name, f"Applying {calc_type}/{calculation.get('method')}")
                df_result = handler(self, df_result, column_name, calculation)
        
        # Step 2: Apply null handling as LAST DEFENSE (only for columns with last_defense timing)
        for column_name in column_names:
            if column_name not in df_result.columns:
                continue
                
            column_def = self.columns[column_name]
            null_handling = column_def.get('null_handling', {})
            
            # Get strategy to check null handling timing
            strategy = self.get_column_strategy(column_name)
            
            # Skip null handling if strategy says BUILT_IN or SKIP
            if strategy and strategy.null_handling_timing in (NullHandlingTiming.BUILT_IN, NullHandlingTiming.SKIP):
                self._print_processing_step(
                    "Strategy-Null", column_name,
                    f"Skipping null handling ({strategy.null_handling_timing.value})"
                )
                continue
            
            # Apply standard last-defense null handling
            strategy_name = null_handling.get('strategy')
            if strategy_name and strategy_name != 'leave_null' and df_result[column_name].isna().any():
                handler = get_null_handler(strategy_name)
                if handler:
                    self._print_processing_step("Last-Defense", column_name, f"Filling remaining nulls with {strategy_name}")
                    
                    # If strategy exists, use executor for consistency
                    if strategy:
                        df_result = self.strategy_executor.apply_fallback(
                            df_result, column_name, strategy, null_handling
                        )
                    else:
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
            from ..utils.dataframe import prepare_dataframe_for_processing, initialize_missing_columns
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
                    status_print(f"WARNING: No handler found for calculation type: {calc_type}", min_level=2)

            return df_calculated

    def _print_processing_step(self, phase: str, column_name: str, detail: str):
        """Standardized logging for processing progress.
        
        Suppresses ERROR messages at level 1 (default) - they appear in final summary.
        """
        # Suppress ERROR messages at default level (1)
        if detail.startswith("ERROR:") and DEBUG_LEVEL <= 1:
            return
        message = f"[{phase}] {column_name}: {detail}"
        status_print(message, min_level=3)
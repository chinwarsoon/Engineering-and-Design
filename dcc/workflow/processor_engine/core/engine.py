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
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, TYPE_CHECKING

# Configure logging
logger = logging.getLogger(__name__)

from core_engine.base import BaseProcessor
from core_engine.schema_utils import resolve_schema_root
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

from core_engine.context.context_pipeline import PipelineContext

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
            from reporting_engine.core.report_errors import ErrorReporter
            # Task A6: Pass output_dir and parameters at construction
            output_dir = getattr(self.context.paths, 'csv_output_path', Path("output")).parent
            error_reporter = ErrorReporter(
                aggregator=self.error_aggregator,
                output_dir=output_dir,
                effective_parameters=self.context.parameters
            )
        self.error_reporter = error_reporter
        
        self._last_processed_rows = 0
        
        # Use centralized schema root resolution
        _schema_root = resolve_schema_root(schema_data)
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

    def run(self) -> Dict[str, Any]:
        """Execute document processing through the uniform engine interface."""
        df_processed = self.process_data()
        return {
            "processed_rows": len(df_processed),
            "processed_columns": len(df_processed.columns),
        }

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
                error_msg = "No input DataFrame provided in context.data.df_mapped."
                # Record error in context
                if hasattr(self.context, 'add_system_error'):
                    self.context.add_system_error(
                        code="S-C-P-0101",
                        message=error_msg,
                        details="DataFrame must be provided either as parameter or in context.data.df_mapped",
                        engine="processor_engine",
                        phase="data_processing",
                        severity="critical",
                        fatal=True
                    )
                raise ValueError(error_msg)
                
        with log_context("processor", "process_data"):
            debug_print(f"Starting process_data with {len(df.columns)} columns")
            self._last_processed_rows = len(df)
            
            # Phase 3: Initialize telemetry heartbeat
            from core_engine.logging.log_telemetry import TelemetryHeartbeat
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
            
            # Get phase order from schema or use default
            phase_order = self.schema_data.get('processing_phase_order', ["P1", "P2", "P2.5", "P3"])
            
            # Configuration map for phased processing steps
            phase_config = {
                "P1": {"method": self._apply_phase_null_handling, "enum": ProcessingPhase.P1, "desc": "Meta Data"},
                "P2": {"method": self._apply_phase_transactional, "enum": ProcessingPhase.P2, "desc": "Transactional"},
                "P2.5": {"method": self._apply_phase_calculated, "enum": ProcessingPhase.P2_5, "desc": "Anomaly"},
                "P3": {"method": self._apply_phase_calculated, "enum": ProcessingPhase.P3, "desc": "Calculated"}
            }

            # Phase C: Initialize fill history tracking for error detection
            self.fill_history = []
            
            # Iterate through phases dynamically based on schema-driven order
            for phase_id in phase_order:
                config = phase_config.get(phase_id)
                if not config:
                    continue
                
                phase_cols = self.context.blueprint.get_columns_by_phase(phase_id)
                if not phase_cols:
                    continue
                
                self._print_processing_step(f"Phase {phase_id}", config["desc"], f"Processing {len(phase_cols)} columns")
                
                # Apply phase-specific processing
                df_processed = config["method"](df_processed, phase_cols)
                current_rows = len(df_processed)
                _emit_checkpoint(phase_id, current_rows)
                
                # Build detection context
                detection_context = {"phase": phase_id, "schema_data": self.schema_data}
                if phase_id == "P2.5":
                    # Phase C: Include fill_history in context for FillDetector
                    detection_context["fill_history"] = getattr(self, 'fill_history', [])
                
                # Run business detection for this phase
                phase_results = self.business_detector.detect(
                    df_processed, 
                    context=detection_context, 
                    phases=[config["enum"]]
                )
                self.error_aggregator.add_errors(phase_results.get(config["enum"], []))
                
                # Post-phase cleanup
                if phase_id == "P2.5":
                    # Phase C: Clear fill history after detection to prevent memory bloat
                    self.fill_history = []
            
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
            # Task A4: Resolve column names from blueprint (SSOT)
            validation_errors_col = next((c for c in p3_cols if self.columns.get(c, {}).get('calculation', {}).get('type') == 'error_tracking'), "Validation_Errors")
            self._print_processing_step("Phase 4", "Aggregation", f"Populating {validation_errors_col} column")
            df_processed[validation_errors_col] = self.error_aggregator.format_validation_errors_column(len(df_processed))
            
            # Phase 5: Metrics (Layer 5) - Populate Data_Health_Score column (Step 48)
            health_score_col = next((c for c in p3_cols if self.columns.get(c, {}).get('column_type') == 'score_column'), "Data_Health_Score")
            self._print_processing_step("Phase 5", "Metrics", f"Calculating {health_score_col}")
            from reporting_engine.core.report_health import calculate_row_health_series
            df_processed[health_score_col] = calculate_row_health_series(df_processed, self.error_aggregator)
            
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

    def _print_processing_step(self, phase: str, column_name: str, detail: str):
        """Standardized logging for processing progress.
        
        Suppresses ERROR messages at level 1 (default) - they appear in final summary.
        """
        # Suppress ERROR messages at default level (1)
        if detail.startswith("ERROR:") and DEBUG_LEVEL <= 1:
            return
        message = f"[{phase}] {column_name}: {detail}"
        status_print(message, min_level=3)

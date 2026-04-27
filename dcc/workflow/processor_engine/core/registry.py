"""
Registry module for mapping calculation types and null handling strategies
to their implementing functions in the processor engine.
"""

from typing import Callable, Dict, Optional

# Import null handling strategies
from ..calculations.null_handling import (
    apply_forward_fill,
    apply_multi_level_forward_fill,
    apply_copy_from,
    apply_calculate_if_null,
    apply_default_value,
    apply_lookup_if_null,
)

# Import calculation modules
from ..calculations import (
    aggregate,
    conditional,
    date,
    mapping,
    composite,
    error_tracking,
)

# Import hierarchical logging functions from dcc_utility
from dcc_utility.console import status_print, debug_print

# --- Registry for Null Handling ---

NULL_HANDLERS: Dict[str, Callable] = {
    "forward_fill": apply_forward_fill,
    "multi_level_forward_fill": apply_multi_level_forward_fill,
    "copy_from": apply_copy_from,
    "calculate_if_null": apply_calculate_if_null,
    "default_value": apply_default_value,
    "lookup_if_null": apply_lookup_if_null,
    "leave_null": None,  # No-op, handled specially
}

# --- Registry for Calculations ---

CALCULATION_HANDLERS: Dict[str, Dict[str, Callable]] = {
    "mapping": {
        "status_to_code": mapping.apply_mapping_calculation,
        "default": mapping.apply_mapping_calculation,
    },
    "aggregate": {
        "latest_by_date": aggregate.apply_latest_by_date_calculation,
        "concatenate_unique": aggregate.apply_aggregate_calculation,
        "concatenate_unique_quoted": aggregate.apply_aggregate_calculation,
        "concatenate_dates": aggregate.apply_aggregate_calculation,
        "count": aggregate.apply_aggregate_calculation,
        "min": aggregate.apply_aggregate_calculation,
        "max": aggregate.apply_aggregate_calculation,
        "default": aggregate.apply_aggregate_calculation,
    },
    "custom_aggregate": {
        "latest_non_pending_status": aggregate.apply_latest_non_pending_status,
        "default": aggregate.apply_latest_non_pending_status,
    },
    "copy": {
        "direct": composite.apply_copy_calculation,
        "default": composite.apply_copy_calculation,
    },
    "conditional": {
        "current_row": conditional.apply_current_row_calculation,
        "update_resubmission_required": conditional.apply_update_resubmission_required,
        "submission_closure_status": conditional.apply_submission_closure_status,
        "calculate_overdue_status": conditional.apply_calculate_overdue_status,
        "default": conditional.apply_current_row_calculation,
    },
    "date_calculation": {
        "add_working_days": date.calculate_working_days,
        "date_difference": date.calculate_date_difference,
        "default": date.apply_date_calculation,
    },
    "conditional_date_calculation": {
        "default": date.apply_conditional_date_calculation,
    },
    "conditional_business_day_calculation": {
        "default": date.apply_conditional_business_day_calculation,
    },
    "custom_conditional_date": {
        "calculate_resubmission_plan_date": date.apply_resubmission_plan_date,
        "default": date.apply_resubmission_plan_date,
    },
    "composite": {
        "build_document_id": composite.apply_composite_calculation,
        "default": composite.apply_composite_calculation,
    },
    "extract_affixes": {
        "extract_document_id_affixes": composite.apply_extract_affixes,
        "default": composite.apply_extract_affixes,
    },
    "auto_increment": {
        "generate_row_index": composite.apply_row_index,
        "default": composite.apply_row_index,
    },
    "complex_lookup": {
        "calculate_delay_of_resubmission": composite.apply_delay_of_resubmission,
        "default": composite.apply_delay_of_resubmission,
    },
    "error_tracking": {
        "aggregate_row_errors": error_tracking.apply_aggregate_row_errors,
        "default": error_tracking.apply_aggregate_row_errors,
    },
}

def get_null_handler(strategy: str) -> Optional[Callable]:
    """
    Retrieves the function associated with a null-handling strategy.

    Args:
        strategy: The null handling strategy name (e.g., 'forward_fill', 'default_value')

    Returns:
        The handler function or None if not found (or if strategy is 'leave_null')
    """
    handler = NULL_HANDLERS.get(strategy)
    if not handler and strategy != "leave_null":
        status_print(f"WARNING: No handler registered for null strategy: {strategy}", min_level=2)
    return handler

def get_calculation_handler(calc_type: str, method: str = "default") -> Optional[Callable]:
    """
    Retrieves the specific calculation function based on type and method.

    Args:
        calc_type: The calculation type (e.g., 'aggregate', 'conditional', 'mapping')
        method: The specific method within the type (e.g., 'latest_by_date', 'direct')

    Returns:
        The handler function or None if not found
    """
    type_map = CALCULATION_HANDLERS.get(calc_type, {})

    # If a specific method exists, use it.
    # Otherwise, check if there is a 'default' handler for that type.
    handler = type_map.get(method) or type_map.get("default")

    if not handler:
        status_print(f"WARNING: No handler registered for calculation type: {calc_type}/{method}", min_level=2)

    return handler

def register_null_handler(strategy: str, func: Callable):
    """
    Allows dynamic registration of new null handling strategies.

    Args:
        strategy: The strategy name to register
        func: The handler function
    """
    NULL_HANDLERS[strategy] = func
    status_print(f"Registered null handler for strategy: {strategy}", min_level=3)


def register_calculation_handler(calc_type: str, method: str, func: Callable):
    """
    Allows dynamic registration of new calculation handlers.

    Args:
        calc_type: The calculation type
        method: The specific method name
        func: The handler function
    """
    if calc_type not in CALCULATION_HANDLERS:
        CALCULATION_HANDLERS[calc_type] = {}
    CALCULATION_HANDLERS[calc_type][method] = func
    status_print(f"Registered calculation handler for {calc_type}/{method}", min_level=3)


def list_registered_handlers():
    """
    Returns a listing of all registered handlers for debugging/documentation.
    """
    return {
        "null_handlers": list(NULL_HANDLERS.keys()),
        "calculation_types": {
            calc_type: list(methods.keys())
            for calc_type, methods in CALCULATION_HANDLERS.items()
        }
    }
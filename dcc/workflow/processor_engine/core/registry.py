"""
define the mapping between the strings in your JSON (e.g., "forward_fill", "aggregate")
and the specific methods now located in the calculations/ directory.
"""

import logging
from typing import Callable, Dict, Optional

# Import the calculation modules (these will be created in the /calculations folder)
from engine.calculations import (
    mapping,
    aggregate,
    conditional,
    date,
    dataframe_utils  # For copy/direct actions
)

logger = logging.getLogger(__name__)

# --- Registry for Null Handling ---

NULL_HANDLERS: Dict[str, Callable] = {
    "forward_fill": None,  # Will be mapped to calculation methods
    "multi_level_forward_fill": None,
    "copy_from": None,
    "calculate_if_null": None,
    "default_value": None,
    "lookup_if_null": None,
}

# --- Registry for Calculations ---

CALCULATION_HANDLERS: Dict[str, Dict[str, Callable]] = {
    "mapping": {
        "status_to_code": mapping.apply_mapping_calculation,
    },
    "aggregate": {
        "latest_by_date": aggregate.apply_latest_by_date_calculation,
        "default": aggregate.apply_aggregate_calculation,
    },
    "copy": {
        "direct": dataframe_utils.apply_copy_calculation,
    },
    "conditional": {
        "current_row": conditional.apply_current_row_calculation,
        "update_resubmission_required": conditional.apply_update_resubmission_required,
        "submission_closure_status": conditional.apply_submission_closure_status,
        "calculate_overdue_status": conditional.apply_calculate_overdue_status,
    },
    "date_calculation": {
        "default": date.apply_date_calculation,
        "add_working_days": date.calculate_working_days,
    },
    "custom_conditional_date": {
        "calculate_resubmission_plan_date": date.apply_resubmission_plan_date,
    },
    "custom_aggregate": {
        "latest_non_pending_status": aggregate.apply_latest_non_pending_status,
    }
}

def get_null_handler(strategy: str) -> Optional[Callable]:
    """
    Retrieves the function associated with a null-handling strategy.
    """
    # Note: These are often internal engine methods (_apply_*) 
    # but can be registered here once the Engine class is initialized.
    handler = NULL_HANDLERS.get(strategy)
    if not handler:
        logger.debug(f"No external handler for null strategy: {strategy}")
    return handler

def get_calculation_handler(calc_type: str, method: str = "default") -> Optional[Callable]:
    """
    Retrieves the specific calculation function based on type and method.
    """
    type_map = CALCULATION_HANDLERS.get(calc_type, {})
    
    # If a specific method exists (e.g. status_to_code), use it.
    # Otherwise, check if there is a 'default' handler for that type.
    handler = type_map.get(method) or type_map.get("default")
    
    if not handler:
        logger.warning(f"No handler registered for {calc_type}/{method}")
    
    return handler

def register_null_handler(strategy: str, func: Callable):
    """Allows dynamic registration of new null handling strategies."""
    NULL_HANDLERS[strategy] = func
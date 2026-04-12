"""
Calculation modules for the document processor engine.
"""

# Aggregate calculations
from .aggregate import (
    apply_aggregate_calculation,
    apply_latest_by_date_calculation,
    apply_latest_non_pending_status,
)

# Conditional calculations
from .conditional import (
    apply_current_row_calculation,
    apply_update_resubmission_required,
    apply_submission_closure_status,
    apply_calculate_overdue_status,
)

# Date calculations
from .date import (
    apply_date_calculation,
    calculate_working_days,
    calculate_date_difference,
    apply_resubmission_plan_date,
    apply_conditional_date_calculation,
    apply_conditional_business_day_calculation,
)

# Mapping calculations
from .mapping import (
    apply_mapping_calculation,
    apply_status_to_code,
)

# Composite calculations
from .composite import (
    apply_composite_calculation,
    apply_row_index,
    apply_delay_of_resubmission,
    apply_copy_calculation,
)

# Null handling strategies
from .null_handling import (
    apply_forward_fill,
    apply_multi_level_forward_fill,
    apply_copy_from,
    apply_calculate_if_null,
    apply_default_value,
    apply_lookup_if_null,
)

# Validation
from .validation import (
    collect_raw_pattern_errors,
    apply_validation,
)

# Error tracking calculations
from .error_tracking import (
    apply_aggregate_row_errors,
)

__all__ = [
    'apply_aggregate_calculation',
    'apply_latest_by_date_calculation',
    'apply_latest_non_pending_status',
    'apply_current_row_calculation',
    'apply_update_resubmission_required',
    'apply_submission_closure_status',
    'apply_calculate_overdue_status',
    'apply_date_calculation',
    'calculate_working_days',
    'calculate_date_difference',
    'apply_resubmission_plan_date',
    'apply_conditional_date_calculation',
    'apply_conditional_business_day_calculation',
    'apply_mapping_calculation',
    'apply_status_to_code',
    'apply_composite_calculation',
    'apply_row_index',
    'apply_delay_of_resubmission',
    'apply_copy_calculation',
    'apply_forward_fill',
    'apply_multi_level_forward_fill',
    'apply_copy_from',
    'apply_calculate_if_null',
    'apply_default_value',
    'apply_lookup_if_null',
    'collect_raw_pattern_errors',
    'apply_validation',
    'apply_aggregate_row_errors',
]

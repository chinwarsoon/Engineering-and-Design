"""
Resolution Remediator Module

Applies remediation strategies to errors based on error type and context.
Implements 8 remediation strategies, decision matrix, and auto-remediation eligibility.

Complies with error_handling_module_workplan.md Phase: Resolution Module Implementation.
"""

from typing import Dict, Any, Optional, Callable
import re


class Remediator:
    """
    Applies remediation strategies to errors.
    
    Implements:
    - R001: AUTO_FIX (zero-pad, format corrections)
    - R002: MANUAL_FIX (flag for user correction)
    - R003: SUPPRESS (accept as-is with justification)
    - R004: ESCALATE (route to expert/team)
    - R005: DERIVE (calculate correct value)
    - R006: DEFAULT (apply default value)
    - R007: FILL_DOWN (forward fill from previous row)
    - R008: AGGREGATE (calculate from related rows)
    - Remediation decision matrix
    - Auto-remediation eligibility check
    """
    
    def __init__(self):
        """
        Initialize remediator with decision matrix.
        
        Breadcrumb: decision_matrix → strategy_handlers → auto_eligibility_map
        """
        self.decision_matrix = self._build_decision_matrix()
        self.strategy_handlers = self._build_strategy_handlers()
    
    def _build_decision_matrix(self) -> Dict[str, Dict[str, Any]]:
        """
        Build remediation decision matrix.
        
        Breadcrumb: error_codes → strategies → matrix
        
        Returns:
            Dict mapping error codes to remediation strategies
        """
        return {
            'P-C-P-0101': {  # NULL_ANCHOR
                'default_strategy': 'MANUAL_FIX',
                'auto_eligible': False,
                'escalation_required': True
            },
            'P-V-V-0501': {  # PATTERN_MISMATCH
                'default_strategy': 'AUTO_FIX',
                'auto_eligible': True,
                'auto_action': 'zero_pad',
                'fallback': 'MANUAL_FIX'
            },
            'F4-C-F-0401': {  # JUMP_LIMIT
                'default_strategy': 'SUPPRESS',
                'auto_eligible': True,
                'condition': 'jump_size < 50'
            },
            'P-C-C-0601': {  # CALCULATION_ERROR
                'default_strategy': 'DERIVE',
                'auto_eligible': True,
                'fallback': 'MANUAL_FIX'
            }
        }
    
    def _build_strategy_handlers(self) -> Dict[str, Callable]:
        """
        Build strategy handler functions.
        
        Breadcrumb: strategies → handler_functions → handlers_dict
        
        Returns:
            Dict mapping strategy codes to handler functions
        """
        return {
            'AUTO_FIX': self._strategy_auto_fix,
            'MANUAL_FIX': self._strategy_manual_fix,
            'SUPPRESS': self._strategy_suppress,
            'ESCALATE': self._strategy_escalate,
            'DERIVE': self._strategy_derive,
            'DEFAULT': self._strategy_default,
            'FILL_DOWN': self._strategy_fill_down,
            'AGGREGATE': self._strategy_aggregate
        }
    
    def remediate(self, error: Dict[str, Any], categorized: Dict[str, Any], 
                  strategy: Optional[str] = None) -> Dict[str, Any]:
        """
        Apply remediation to an error.
        
        Breadcrumb: error → categorized → strategy → handler → remediation_result
        
        Args:
            error: Error dict with error_code and context
            categorized: Categorized error from Categorizer
            strategy: Optional specific strategy to use (overrides default)
        
        Returns:
            Dict with remediation result and applied strategy
        """
        error_code = error.get('error_code', '')
        
        # Determine strategy
        if strategy:
            applied_strategy = strategy
        else:
            applied_strategy = self._get_default_strategy(error_code, categorized)
        
        # Get handler
        handler = self.strategy_handlers.get(applied_strategy)
        
        if not handler:
            return {
                'success': False,
                'error': f'Unknown remediation strategy: {applied_strategy}',
                'applied_strategy': None
            }
        
        try:
            # Apply remediation
            result = handler(error, categorized)
            
            return {
                'success': True,
                'applied_strategy': applied_strategy,
                'result': result,
                'auto_applied': self._is_auto_eligible(error_code, applied_strategy)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'applied_strategy': applied_strategy
            }
    
    def _get_default_strategy(self, error_code: str, categorized: Dict[str, Any]) -> str:
        """
        Get default remediation strategy for error code.
        
        Breadcrumb: error_code → decision_matrix → category → default_strategy
        
        Args:
            error_code: Error code
            categorized: Categorized error
        
        Returns:
            Default strategy code
        """
        # Check decision matrix for specific error code
        if error_code in self.decision_matrix:
            return self.decision_matrix[error_code]['default_strategy']
        
        # Use category-based default
        category = categorized.get('category', 'info')
        category_defaults = {
            'escalate': 'ESCALATE',
            'manual_fix': 'MANUAL_FIX',
            'auto_fix': 'AUTO_FIX',
            'suppress': 'SUPPRESS',
            'info': 'SUPPRESS'
        }
        
        return category_defaults.get(category, 'SUPPRESS')
    
    def _is_auto_eligible(self, error_code: str, strategy: str) -> bool:
        """
        Check if error is eligible for auto-remediation.
        
        Breadcrumb: error_code → strategy → decision_matrix → auto_eligible
        
        Args:
            error_code: Error code
            strategy: Strategy to apply
        
        Returns:
            True if auto-remediation eligible, False otherwise
        """
        if error_code in self.decision_matrix:
            return self.decision_matrix[error_code].get('auto_eligible', False)
        
        # Auto-eligible strategies
        auto_strategies = ['AUTO_FIX', 'DEFAULT', 'FILL_DOWN']
        return strategy in auto_strategies
    
    def _strategy_auto_fix(self, error: Dict[str, Any], categorized: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply AUTO_FIX strategy (zero-pad, format corrections).
        
        Breadcrumb: error → context → value → auto_fix → corrected_value
        
        Args:
            error: Error dict
            categorized: Categorized error
        
        Returns:
            Dict with remediation result
        """
        context = error.get('context', {})
        value = context.get('value')
        column = context.get('column')
        
        if not value or not column:
            return {'success': False, 'reason': 'Missing value or column in context'}
        
        # Auto-fix strategies based on column type
        if 'Sequence' in column or 'Session' in column:
            # Zero-pad numeric values
            if str(value).isdigit():
                # Determine padding length
                pad_length = 4 if 'Sequence' in column else 6
                corrected = str(value).zfill(pad_length)
                return {
                    'success': True,
                    'original_value': value,
                    'corrected_value': corrected,
                    'action': 'zero_pad'
                }
        
        return {'success': False, 'reason': 'No auto-fix applicable'}
    
    def _strategy_manual_fix(self, error: Dict[str, Any], categorized: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply MANUAL_FIX strategy (flag for user correction).
        
        Breadcrumb: error → context → manual_fix_flag → result
        
        Args:
            error: Error dict
            categorized: Categorized error
        
        Returns:
            Dict with remediation result
        """
        return {
            'success': True,
            'action': 'flag_for_manual_correction',
            'requires_user_action': True,
            'message': 'User must correct this error manually'
        }
    
    def _strategy_suppress(self, error: Dict[str, Any], categorized: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply SUPPRESS strategy (accept as-is with justification).
        
        Breadcrumb: error → categorized → suppress → result
        
        Args:
            error: Error dict
            categorized: Categorized error
        
        Returns:
            Dict with remediation result
        """
        return {
            'success': True,
            'action': 'suppress_error',
            'justification': 'Error accepted as-is',
            'severity_override': 'INFO'
        }
    
    def _strategy_escalate(self, error: Dict[str, Any], categorized: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply ESCALATE strategy (route to expert/team).
        
        Breadcrumb: error → categorized → escalate → result
        
        Args:
            error: Error dict
            categorized: Categorized error
        
        Returns:
            Dict with remediation result
        """
        return {
            'success': True,
            'action': 'escalate_to_expert',
            'requires_expert_review': True,
            'priority': 1
        }
    
    def _strategy_derive(self, error: Dict[str, Any], categorized: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply DERIVE strategy (calculate correct value).
        
        Breadcrumb: error → context → derive → calculated_value
        
        Args:
            error: Error dict
            categorized: Categorized error
        
        Returns:
            Dict with remediation result
        """
        context = error.get('context', {})
        
        # Example: Derive Document_ID from components
        if context.get('column') == 'Document_ID':
            components = [
                context.get('Project_Code'),
                context.get('Facility_Code'),
                context.get('Document_Type'),
                context.get('Discipline'),
                context.get('Document_Sequence_Number')
            ]
            if all(components):
                derived = '-'.join(str(c) for c in components)
                return {
                    'success': True,
                    'derived_value': derived,
                    'action': 'derive_from_components'
                }
        
        return {'success': False, 'reason': 'Cannot derive value'}
    
    def _strategy_default(self, error: Dict[str, Any], categorized: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply DEFAULT strategy (apply default value).
        
        Breadcrumb: error → context → default_value → result
        
        Args:
            error: Error dict
            categorized: Categorized error
        
        Returns:
            Dict with remediation result
        """
        context = error.get('context', {})
        column = context.get('column')
        
        # Default values by column type
        defaults = {
            'Review_Status': 'Pending',
            'Approval_Code': 'N/A',
            'Department': 'Unassigned'
        }
        
        default_value = defaults.get(column, 'N/A')
        
        return {
            'success': True,
            'default_value': default_value,
            'action': 'apply_default'
        }
    
    def _strategy_fill_down(self, error: Dict[str, Any], categorized: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply FILL_DOWN strategy (forward fill from previous row).
        
        Breadcrumb: error → context → fill_down → result
        
        Args:
            error: Error dict
            categorized: Categorized error
        
        Returns:
            Dict with remediation result
        """
        return {
            'success': True,
            'action': 'forward_fill',
            'message': 'Value will be filled from previous row'
        }
    
    def _strategy_aggregate(self, error: Dict[str, Any], categorized: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply AGGREGATE strategy (calculate from related rows).
        
        Breadcrumb: error → context → aggregate → calculated_value
        
        Args:
            error: Error dict
            categorized: Categorized error
        
        Returns:
            Dict with remediation result
        """
        context = error.get('context', {})
        column = context.get('column')
        
        # Example: Aggregate approval codes
        if column == 'All_Approval_Code':
            return {
                'success': True,
                'action': 'aggregate_approval_codes',
                'message': 'Aggregate from related submission rows'
            }
        
        return {'success': False, 'reason': 'Cannot aggregate value'}

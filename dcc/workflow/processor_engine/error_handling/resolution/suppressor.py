"""
Resolution Suppressor Module

Applies suppression rules to errors based on conditions.
Implements suppression rule matching, audit trail, and expiration checking.

Complies with error_handling_module_workplan.md Phase: Resolution Module Implementation.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json


class Suppressor:
    """
    Applies suppression rules to errors.
    
    Implements:
    - Suppression rule matching logic
    - Condition checking (project_code, submission_session, column, value)
    - Suppression types (GLOBAL, PROJECT, FILE, ROW, TEMPORARY)
    - Audit trail for suppression decisions
    - Expiration checking for temporary suppressions
    """
    
    def __init__(self, rules_path: Optional[str] = None):
        """
        Initialize suppressor with suppression rules.
        
        Breadcrumb: rules_path → load_rules → rule_index → audit_log
        
        Args:
            rules_path: Path to suppression_rules.json file
        """
        self.rules: List[Dict[str, Any]] = []
        self.audit_log: List[Dict[str, Any]] = []
        
        if rules_path:
            self.load_rules(rules_path)
    
    def load_rules(self, rules_path: str) -> None:
        """
        Load suppression rules from JSON file.
        
        Breadcrumb: rules_path → parse_json → rules_list
        
        Args:
            rules_path: Path to suppression_rules.json file
        """
        try:
            with open(rules_path, 'r') as f:
                data = json.load(f)
                self.rules = data.get('rules', [])
        except Exception as e:
            print(f"Failed to load suppression rules: {e}")
            self.rules = []
    
    def should_suppress(self, error_code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Check if error should be suppressed based on rules.
        
        Breadcrumb: error_code → context → match_rules → check_conditions → check_expiration → suppress_decision
        
        Args:
            error_code: Error code to check
            context: Additional context (project_code, submission_session, column, value, etc.)
        
        Returns:
            Dict with suppress decision, matching rule, and audit info
        """
        for rule in self.rules:
            if self._matches_rule(error_code, context, rule):
                # Check expiration
                if self._is_expired(rule):
                    continue
                
                # Log suppression decision
                audit_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'error_code': error_code,
                    'rule_id': rule.get('rule_id'),
                    'rule_name': rule.get('name'),
                    'context': context or {},
                    'suppressed': True,
                    'justification': rule.get('justification')
                }
                self.audit_log.append(audit_entry)
                
                return {
                    'suppressed': True,
                    'rule_id': rule.get('rule_id'),
                    'rule_name': rule.get('name'),
                    'justification': rule.get('justification'),
                    'severity_override': rule.get('severity_override'),
                    'audit_entry': audit_entry
                }
        
        return {
            'suppressed': False,
            'reason': 'No matching suppression rule'
        }
    
    def _matches_rule(self, error_code: str, context: Optional[Dict[str, Any]], rule: Dict[str, Any]) -> bool:
        """
        Check if error matches suppression rule.
        
        Breadcrumb: error_code → rule_error_codes → rule_conditions → context_match
        
        Args:
            error_code: Error code to check
            context: Additional context
            rule: Suppression rule to match against
        
        Returns:
            True if error matches rule, False otherwise
        """
        # Check error codes
        rule_error_codes = rule.get('error_codes', [])
        if rule_error_codes and error_code not in rule_error_codes:
            return False
        
        # Check conditions
        conditions = rule.get('conditions', {})
        if not conditions:
            return True
        
        if not context:
            return False
        
        # Check each condition
        for key, expected_value in conditions.items():
            actual_value = context.get(key)
            
            # Handle list of expected values
            if isinstance(expected_value, list):
                if actual_value not in expected_value:
                    return False
            # Handle comparison operators
            elif isinstance(expected_value, dict):
                if not self._check_condition(actual_value, expected_value):
                    return False
            # Handle exact match
            else:
                if actual_value != expected_value:
                    return False
        
        return True
    
    def _check_condition(self, actual: Any, condition: Dict[str, Any]) -> bool:
        """
        Check a condition with comparison operators.
        
        Breadcrumb: actual → condition_operator → expected → comparison_result
        
        Args:
            actual: Actual value
            condition: Condition dict with operator and value
        
        Returns:
            True if condition matches, False otherwise
        """
        operator = condition.get('operator', '==')
        expected = condition.get('value')
        
        if operator == '==':
            return actual == expected
        elif operator == '!=':
            return actual != expected
        elif operator == '<':
            return actual < expected
        elif operator == '<=':
            return actual <= expected
        elif operator == '>':
            return actual > expected
        elif operator == '>=':
            return actual >= expected
        elif operator == 'in':
            return actual in expected
        elif operator == 'not_in':
            return actual not in expected
        
        return False
    
    def _is_expired(self, rule: Dict[str, Any]) -> bool:
        """
        Check if suppression rule has expired.
        
        Breadcrumb: rule → expires_at → current_time → expired_check
        
        Args:
            rule: Suppression rule to check
        
        Returns:
            True if rule has expired, False otherwise
        """
        expires_at = rule.get('expires_at')
        if not expires_at:
            return False
        
        try:
            expiry_date = datetime.fromisoformat(expires_at)
            return datetime.now() > expiry_date
        except:
            return False
    
    def suppress(self, error_code: str, context: Optional[Dict[str, Any]] = None, 
                justification: Optional[str] = None, approved_by: Optional[str] = None,
                expires_at: Optional[str] = None) -> Dict[str, Any]:
        """
        Manually suppress an error with justification.
        
        Breadcrumb: error_code → context → manual_suppression → audit_log
        
        Args:
            error_code: Error code to suppress
            context: Additional context
            justification: Justification for suppression
            approved_by: User who approved suppression
            expires_at: Optional expiration date
        
        Returns:
            Dict with suppression result and audit info
        """
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'error_code': error_code,
            'rule_id': 'MANUAL',
            'rule_name': 'Manual Suppression',
            'context': context or {},
            'suppressed': True,
            'justification': justification,
            'approved_by': approved_by,
            'expires_at': expires_at
        }
        self.audit_log.append(audit_entry)
        
        return {
            'suppressed': True,
            'manual': True,
            'justification': justification,
            'approved_by': approved_by,
            'expires_at': expires_at,
            'audit_entry': audit_entry
        }
    
    def get_audit_log(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get suppression audit log.
        
        Breadcrumb: audit_log → limit → filtered_log
        
        Args:
            limit: Maximum number of entries to return (most recent first)
        
        Returns:
            List of audit entries
        """
        if limit:
            return self.audit_log[-limit:][::-1]
        return self.audit_log[::-1]
    
    def clear_audit_log(self) -> None:
        """Clear the suppression audit log."""
        self.audit_log = []

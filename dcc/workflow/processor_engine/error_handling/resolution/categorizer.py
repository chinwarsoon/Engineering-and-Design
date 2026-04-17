"""
Resolution Categorizer Module

Categorizes errors based on error code taxonomy, severity levels, and layer mapping.
Implements auto-categorization logic for routing to appropriate handlers.

Complies with error_handling_module_workplan.md Phase: Resolution Module Implementation.
"""

from typing import Dict, Any, List, Optional
from ..core.taxonomy_loader import TaxonomyLoader
from ..core.registry import ErrorRegistry


class Categorizer:
    """
    Categorizes errors for routing to appropriate handlers.
    
    Implements:
    - Auto-categorization based on error code taxonomy
    - Severity level mapping (Critical, High, Medium, Low, Info)
    - Layer mapping (L1, L2, L2.5, L3, L4, L5)
    - Business impact assessment
    """
    
    def __init__(self, taxonomy_loader: TaxonomyLoader, registry: ErrorRegistry):
        """
        Initialize categorizer with taxonomy and registry.
        
        Breadcrumb: taxonomy_loader → registry → severity_map → layer_map
        
        Args:
            taxonomy_loader: TaxonomyLoader instance for error code taxonomy
            registry: ErrorRegistry instance for error code definitions
        """
        self.taxonomy_loader = taxonomy_loader
        self.registry = registry
        self._build_severity_map()
        self._build_layer_map()
    
    def _build_severity_map(self) -> None:
        """Build severity level mapping based on error code patterns."""
        self.severity_map = {
            # Critical: Anchor and identity errors (P1xx, P2xx)
            'P1': 'Critical',
            'P2': 'Critical',
            # High: Schema and business logic errors (V5xx, B3xx)
            'V5': 'High',
            'B3': 'High',
            # Medium: Calculation and validation errors (C6xx, V4xx)
            'C6': 'Medium',
            'V4': 'Medium',
            # Low: Fill warnings (F4xx)
            'F4': 'Low',
            # Info: Base and logic errors
            'B4': 'Info',
        }
    
    def _build_layer_map(self) -> None:
        """Build layer mapping based on error code patterns."""
        self.layer_map = {
            # L1: Input validation (P1xx)
            'P1': 'L1',
            # L2: Schema validation (V5xx)
            'V5': 'L2',
            # L2.5: Historical lookup (P2xx)
            'P2': 'L2.5',
            # L3: Business logic (B3xx, C6xx)
            'B3': 'L3',
            'C6': 'L3',
            # L4: Approval hook (manual)
            'L4': 'L4',
            # L5: Metric aggregator (B4xx)
            'B4': 'L5',
            # L3: Fill warnings (F4xx)
            'F4': 'L3',
        }
    
    def categorize(self, error_code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Categorize an error based on error code and context.
        
        Breadcrumb: error_code → parse_code → severity → layer → business_impact → category
        
        Args:
            error_code: Error code in E-M-F-U format (e.g., P-C-P-0101)
            context: Additional context (column, row, value, etc.)
        
        Returns:
            Dict with category, severity, layer, business_impact, and routing_info
        """
        # Parse error code
        parsed = self._parse_error_code(error_code)
        
        # Determine severity
        severity = self._determine_severity(parsed)
        
        # Determine layer
        layer = self._determine_layer(parsed)
        
        # Assess business impact
        business_impact = self._assess_business_impact(parsed, context)
        
        # Determine routing category
        category = self._determine_category(parsed, severity, business_impact)
        
        return {
            'error_code': error_code,
            'parsed': parsed,
            'severity': severity,
            'layer': layer,
            'business_impact': business_impact,
            'category': category,
            'routing_info': self._get_routing_info(category, severity),
            'context': context or {}
        }
    
    def _parse_error_code(self, error_code: str) -> Dict[str, str]:
        """
        Parse error code in E-M-F-U format.
        
        Breadcrumb: error_code → split → engine_module_function_unique
        
        Args:
            error_code: Error code string
        
        Returns:
            Dict with engine, module, function, unique_id components
        """
        parts = error_code.split('-')
        if len(parts) >= 4:
            return {
                'engine': parts[0],
                'module': parts[1],
                'function': parts[2],
                'unique_id': parts[3]
            }
        return {'engine': '', 'module': '', 'function': '', 'unique_id': ''}
    
    def _determine_severity(self, parsed: Dict[str, str]) -> str:
        """
        Determine severity level based on error code pattern.
        
        Breadcrumb: parsed → function_code → severity_map → severity
        
        Args:
            parsed: Parsed error code components
        
        Returns:
            Severity level (Critical, High, Medium, Low, Info)
        """
        function_code = f"{parsed['engine']}{parsed['function']}"
        return self.severity_map.get(function_code, 'Medium')
    
    def _determine_layer(self, parsed: Dict[str, str]) -> str:
        """
        Determine validation layer based on error code pattern.
        
        Breadcrumb: parsed → function_code → layer_map → layer
        
        Args:
            parsed: Parsed error code components
        
        Returns:
            Layer identifier (L1, L2, L2.5, L3, L4, L5)
        """
        function_code = f"{parsed['engine']}{parsed['function']}"
        return self.layer_map.get(function_code, 'L3')
    
    def _assess_business_impact(self, parsed: Dict[str, str], context: Optional[Dict[str, Any]]) -> str:
        """
        Assess business impact based on error type and context.
        
        Breadcrumb: parsed → context → impact_rules → business_impact
        
        Args:
            parsed: Parsed error code components
            context: Additional context (column, row, value)
        
        Returns:
            Business impact level (Critical, High, Medium, Low)
        """
        severity = self._determine_severity(parsed)
        
        # Critical errors always have critical business impact
        if severity == 'Critical':
            return 'Critical'
        
        # High severity errors may have high or medium impact depending on context
        if severity == 'High':
            column = context.get('column', '') if context else ''
            # Schema errors in key columns have high impact
            if column in ['Document_ID', 'Project_Code', 'Submission_Date']:
                return 'High'
            return 'Medium'
        
        # Medium and below have corresponding impact
        return severity
    
    def _determine_category(self, parsed: Dict[str, str], severity: str, business_impact: str) -> str:
        """
        Determine routing category based on severity and business impact.
        
        Breadcrumb: severity → business_impact → category_rules → category
        
        Args:
            parsed: Parsed error code components
            severity: Severity level
            business_impact: Business impact level
        
        Returns:
            Routing category (auto_fix, manual_fix, suppress, escalate, info)
        """
        # Critical errors require escalation
        if business_impact == 'Critical':
            return 'escalate'
        
        # High impact errors require manual fix
        if business_impact == 'High':
            return 'manual_fix'
        
        # Medium impact may be auto-fixable
        if business_impact == 'Medium':
            return 'auto_fix'
        
        # Low impact can be suppressed or auto-fixed
        if business_impact == 'Low':
            return 'suppress'
        
        # Info errors are informational only
        return 'info'
    
    def _get_routing_info(self, category: str, severity: str) -> Dict[str, Any]:
        """
        Get routing information for the category.
        
        Breadcrumb: category → severity → routing_rules → routing_info
        
        Args:
            category: Routing category
            severity: Severity level
        
        Returns:
            Dict with handler, priority, and routing details
        """
        routing_map = {
            'escalate': {
                'handler': 'escalation_handler',
                'priority': 1,
                'requires_human': True,
                'timeout': None
            },
            'manual_fix': {
                'handler': 'manual_fix_handler',
                'priority': 2,
                'requires_human': True,
                'timeout': 3600  # 1 hour
            },
            'auto_fix': {
                'handler': 'auto_fix_handler',
                'priority': 3,
                'requires_human': False,
                'timeout': 30  # 30 seconds
            },
            'suppress': {
                'handler': 'suppression_handler',
                'priority': 4,
                'requires_human': False,
                'timeout': 10  # 10 seconds
            },
            'info': {
                'handler': 'info_handler',
                'priority': 5,
                'requires_human': False,
                'timeout': None
            }
        }
        
        return routing_map.get(category, routing_map['info'])
    
    def batch_categorize(self, errors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Categorize multiple errors in batch.
        
        Breadcrumb: errors → map_categorize → categorized_errors
        
        Args:
            errors: List of error dicts with error_code and context
        
        Returns:
            List of categorized error dicts
        """
        return [self.categorize(e['error_code'], e.get('context')) for e in errors]

"""
Error Handling Core Module - Phase 1 Implementation

Provides JSON-based configuration loading and core infrastructure
for the DCC Column Data Error Handling Module.

Exports:
    - ErrorRegistry: Load and query error codes from JSON
    - TaxonomyLoader: Load taxonomy definitions
    - StatusLoader: Load status lifecycle definitions
    - AnatomyLoader: Load and validate error code anatomy
    - RemediationLoader: Load remediation strategies
    - JSONSchemaValidator: Validate JSON against schemas
    - StructuredLogger: JSON structured logging
    - Interceptor: AOP-style decoration framework
"""

from .registry import ErrorRegistry
from .taxonomy_loader import TaxonomyLoader
from .status_loader import StatusLoader
from .anatomy_loader import AnatomyLoader
from .remediation_loader import RemediationLoader
from .validator import JSONSchemaValidator
from .logger import StructuredLogger
from .interceptor import Interceptor, intercept

__all__ = [
    "ErrorRegistry",
    "TaxonomyLoader",
    "StatusLoader",
    "AnatomyLoader",
    "RemediationLoader",
    "JSONSchemaValidator",
    "StructuredLogger",
    "Interceptor",
    "intercept",
]

__version__ = "1.0.0"

"""
Identity Detector Module (P2xx - Layer 3)

Validates P2 (Priority 2) identity columns:
- Document_ID, Document_Revision
- Document_Title
- Transmittal_Number

Error Codes:
- P2-I-P-0201: Document_ID uncertain (CRITICAL)
- P2-I-P-0202: Document_Revision missing (CRITICAL)
- P2-I-V-0203: Duplicate Transmittal_Number (HIGH)
- P2-I-V-0204: Document_ID format invalid (HIGH)
"""

import pandas as pd
import re
from typing import Dict, Any, List, Optional, Tuple

from .base import BaseDetector, DetectionResult

# Import derived pattern function for schema-driven validation
try:
    from ...calculations.validation import get_derived_pattern_regex
    HAS_DERIVED_PATTERN = True
except ImportError:
    HAS_DERIVED_PATTERN = False

# Import affix extractor for Document_ID affix handling (Issue #16)
try:
    from ...calculations.affix_extractor import extract_document_id_affixes
    HAS_AFFIX_EXTRACTOR = True
except ImportError:
    HAS_AFFIX_EXTRACTOR = False


class IdentityDetector(BaseDetector):
    """
    Detector for P2 identity column validation.
    
    P2 columns define document identity - critical for uniqueness
    and downstream processing.
    """
    
    # P2 identity columns
    IDENTITY_COLUMNS = [
        "Document_ID",
        "Document_Revision",
        "Document_Title",
        "Transmittal_Number"
    ]
    
    # Error codes
    ERROR_ID_UNCERTAIN = "P2-I-P-0201"
    ERROR_REV_MISSING = "P2-I-P-0202"
    ERROR_DUPLICATE_TRANS = "P2-I-V-0203"
    ERROR_ID_FORMAT_INVALID = "P2-I-V-0204"
    
    # Validation patterns
    # Document_ID: PROJECT-FACILITY-TYPE-DISCIPLINE-SEQUENCE (e.g., PRJ-FAC-DWG-ARC-0001)
    # Note: Now using schema-driven derived_pattern from dcc_register_enhanced.json
    # Fallback pattern kept for backward compatibility when schema not available
    DOC_ID_PATTERN = re.compile(
        r'^[A-Z0-9]{3,10}-[A-Z0-9]{2,10}-[A-Z0-9]{1,10}-[A-Z0-9]{1,10}-\d{4}(?:-[A-Z0-9.]+)?$'
    )
    
    def __init__(
        self,
        logger=None,
        enable_fail_fast: bool = True,
        required_identities: Optional[List[str]] = None
    ):
        """
        Initialize identity detector.
        
        Args:
            logger: StructuredLogger instance
            enable_fail_fast: Whether to raise on critical errors
            required_identities: Override default identity columns
        """
        super().__init__(
            layer="L3",
            logger=logger,
            enable_fail_fast=enable_fail_fast
        )
        self.required_identities = required_identities or self.IDENTITY_COLUMNS
    
    def detect(
        self,
        df: pd.DataFrame,
        context: Optional[Dict[str, Any]] = None
    ) -> List[DetectionResult]:
        """
        Run P2 identity validations for required columns.
        """
        self.clear_errors()
        
        if context:
            self.set_context(**context)
        
        # Run detection methods only for required columns
        if "Document_ID" in self.required_identities:
            self._detect_uncertain_document_id(df)
            self._detect_invalid_id_format(df)
            
        if "Document_Revision" in self.required_identities:
            self._detect_missing_revision(df)
            
        if "Transmittal_Number" in self.required_identities:
            self._detect_duplicate_transmittal(df)
        
        return self.get_errors()
    
    def _detect_uncertain_document_id(self, df: pd.DataFrame) -> None:
        """
        Detect uncertain/invalid Document_ID values.
        
        Uncertain indicators:
        - "NA", "N/A", "UNKNOWN", "TBD", "TO BE DETERMINED"
        - Empty or null values
        - Non-standard format
        
        Error: P2-I-P-0201 (CRITICAL - FAIL FAST)
        """
        id_col = "Document_ID"
        
        if id_col not in df.columns:
            return
        
        # Uncertain indicators
        uncertain_values = ['na', 'n/a', 'unknown', 'tbd', 'to be determined', 
                           'pending', 'draft', 'temp', 'temporary', '']
        
        for idx in df.index:
            value = str(df.at[idx, id_col]).strip().lower()
            
            # Check for uncertain values
            if value in uncertain_values or pd.isna(df.at[idx, id_col]):
                self.detect_error(
                    error_code=self.ERROR_ID_UNCERTAIN,
                    message=f"Document_ID uncertain at row {idx}: '{df.at[idx, id_col]}'",
                    row=idx,
                    column=id_col,
                    severity="CRITICAL",
                    fail_fast=True,
                    additional_context={
                        "actual_value": str(df.at[idx, id_col]),
                        "uncertain_type": "placeholder_value",
                        "suggestion": "Provide valid Document_ID"
                    }
                )
    
    def _detect_missing_revision(self, df: pd.DataFrame) -> None:
        """
        Detect missing Document_Revision values.
        
        Error: P2-I-P-0202 (CRITICAL - FAIL FAST)
        """
        rev_col = "Document_Revision"
        
        if rev_col not in df.columns:
            return
        
        # Check for nulls and empty strings
        null_mask = df[rev_col].isna() | (df[rev_col] == '')
        
        for idx in df[null_mask].index:
            self.detect_error(
                error_code=self.ERROR_REV_MISSING,
                message=f"Document_Revision missing at row {idx}",
                row=idx,
                column=rev_col,
                severity="CRITICAL",
                fail_fast=True,
                additional_context={
                    "suggestion": "Set default revision (e.g., '00' or 'A')"
                }
            )
    
    def _detect_duplicate_transmittal(self, df: pd.DataFrame) -> None:
        """
        Detect duplicate Transmittal_Number within session.
        
        Error: P2-I-V-0203 (HIGH)
        
        Note: Checks schema strategy configuration to skip validation for
        fact table attributes where duplicates are expected (e.g., one 
        transmittal containing multiple documents).
        """
        trans_col = "Transmittal_Number"
        session_col = "Submission_Session"
        
        if trans_col not in df.columns:
            return
        
        # Check schema strategy configuration
        context = self._context or {}
        schema_data = context.get('schema_data', {})
        columns_config = schema_data.get('enhanced_schema', {}).get('columns', {})
        transmittal_config = columns_config.get(trans_col, {})
        strategy = transmittal_config.get('strategy', {})
        validation_context = strategy.get('validation_context', {})
        
        # Skip duplicate check if configured in schema
        if validation_context.get('skip_duplicate_check', False):
            if self._logger:
                self._logger.info(
                    f"[{self.__class__.__name__}] Skipping duplicate check for {trans_col} "
                    f"(skip_duplicate_check: true in schema strategy)"
                )
            return
        
        # Group by session if available
        if session_col in df.columns:
            for session_id, group in df.groupby(session_col):
                duplicates = group[trans_col].duplicated(keep=False)
                
                for idx in group[duplicates].index:
                    self.detect_error(
                        error_code=self.ERROR_DUPLICATE_TRANS,
                        message=f"Duplicate Transmittal_Number in session {session_id}",
                        row=idx,
                        column=trans_col,
                        severity="HIGH",
                        fail_fast=False,
                        additional_context={
                            "session_id": str(session_id),
                            "transmittal_value": str(df.at[idx, trans_col]),
                            "duplicate_count": int(duplicates.sum()),
                            "suggestion": "Make Transmittal_Number unique per session"
                        }
                    )
        else:
            # Check across entire dataset
            duplicates = df[trans_col].duplicated(keep=False)
            
            for idx in df[duplicates].index:
                self.detect_error(
                    error_code=self.ERROR_DUPLICATE_TRANS,
                    message=f"Duplicate Transmittal_Number detected",
                    row=idx,
                    column=trans_col,
                    severity="HIGH",
                    fail_fast=False,
                    additional_context={
                        "transmittal_value": str(df.at[idx, trans_col]),
                        "suggestion": "Ensure Transmittal_Number uniqueness"
                    }
                )
    
    def _get_schema_pattern(self, context: Optional[Dict[str, Any]]) -> Optional[re.Pattern]:
        """
        Get schema-driven pattern from derived_pattern validation rule.
        
        Returns compiled regex pattern or None if schema not available.
        """
        if not HAS_DERIVED_PATTERN or not context:
            return None
        
        schema_data = context.get('schema_data', {})
        columns_config = schema_data.get('enhanced_schema', {}).get('columns', {})
        
        if 'Document_ID' not in columns_config:
            return None
        
        pattern_str = get_derived_pattern_regex(
            column_name='Document_ID',
            columns_schema=columns_config,
            schema_data=schema_data,
            separator='-'
        )
        
        if pattern_str:
            try:
                return re.compile(pattern_str)
            except re.error:
                return None
        
        return None
    
    def _get_affix_extraction_params(self, context: Optional[Dict[str, Any]]) -> Tuple[str, int]:
        """
        Get affix extraction parameters from schema.
        
        Reads:
        - delimiter: from Document_ID.validation.derived_pattern.separator
        - sequence_length: from Document_Sequence_Number.validation.pattern
        
        Returns:
            Tuple of (delimiter, sequence_length)
        """
        delimiter = '-'
        sequence_length = 4
        
        if not context:
            return (delimiter, sequence_length)
        
        schema_data = context.get('schema_data', {})
        columns_config = schema_data.get('enhanced_schema', {}).get('columns', {})
        
        # Get delimiter from Document_ID derived_pattern
        doc_id_config = columns_config.get('Document_ID', {})
        for validation in doc_id_config.get('validation', []):
            if validation.get('type') == 'derived_pattern':
                delimiter = validation.get('separator', '-')
                break
        
        # Get sequence_length from Document_Sequence_Number pattern
        seq_config = columns_config.get('Document_Sequence_Number', {})
        for validation in seq_config.get('validation', []):
            if validation.get('type') == 'pattern':
                pattern = validation.get('pattern', '')
                # Extract length from pattern like "^[0-9]{4}$"
                match = re.search(r'\{(\d+)\}', pattern)
                if match:
                    sequence_length = int(match.group(1))
                    break
        
        return (delimiter, sequence_length)
    
    def _detect_invalid_id_format(self, df: pd.DataFrame) -> None:
        """
        Detect Document_ID format violations.
        
        Uses schema-driven derived_pattern if available, falls back to hardcoded pattern.
        Extracts affixes before validation to prevent false positives for IDs with suffixes.
        
        Expected format: PROJECT-FACILITY-TYPE-DISCIPLINE-SEQUENCE
        Example: PRJ-FAC-DWG-ARC-0001
        
        Error: P2-I-V-0204 (HIGH)
        
        Related to Issue #16: Document_ID affix handling
        """
        id_col = "Document_ID"
        
        if id_col not in df.columns:
            return
        
        # Try to get schema-driven pattern first
        pattern = self._get_schema_pattern(self._context)
        if pattern:
            pattern_source = "schema_derived"
            if self._logger:
                self._logger.info(
                    f"[{self.__class__.__name__}] Using schema-derived pattern for {id_col} validation"
                )
        else:
            pattern = self.DOC_ID_PATTERN
            pattern_source = "fallback"
        
        # Get affix extraction parameters from schema (Issue #16)
        delimiter, sequence_length = self._get_affix_extraction_params(self._context)
        affix_extraction_enabled = HAS_AFFIX_EXTRACTOR
        
        for idx in df.index:
            value = str(df.at[idx, id_col])
            
            # Skip nulls (handled by _detect_uncertain_document_id)
            if pd.isna(df.at[idx, id_col]) or value.strip() == '':
                continue
            
            # Extract affix before validation (Issue #16)
            base_id = value
            affix = ""
            if affix_extraction_enabled:
                base_id, affix = extract_document_id_affixes(
                    value, 
                    delimiter=delimiter, 
                    sequence_length=sequence_length
                )
            
            # Validate base ID (without affix)
            if not pattern.match(base_id):
                error_context = {
                    "actual_value": value,
                    "expected_pattern": "PROJECT-FACILITY-TYPE-DISCIPLINE-SEQUENCE",
                    "example_valid": "PRJ-FAC-DWG-ARC-0001",
                    "suggestion": "Use format: PROJECT-FACILITY-TYPE-DISCIPLINE-0000",
                    "pattern_source": pattern_source
                }
                
                # Include affix info in error context (Issue #16)
                if affix_extraction_enabled and affix:
                    error_context.update({
                        "base_id": base_id,
                        "affix": affix,
                        "affix_extraction": "applied",
                        "note": "Validation performed on base ID after removing affix"
                    })
                
                self.detect_error(
                    error_code=self.ERROR_ID_FORMAT_INVALID,
                    message=f"Invalid Document_ID format: '{value}'",
                    row=idx,
                    column=id_col,
                    severity="HIGH",
                    fail_fast=False,
                    additional_context=error_context
                )
    
    def detect_P201_id_uncertain(
        self,
        df: pd.DataFrame
    ) -> List[Tuple[int, str]]:
        """
        Public API: Check for uncertain Document_ID values.
        
        Args:
            df: DataFrame
            
        Returns:
            List of (row_index, uncertain_value) tuples
        """
        id_col = "Document_ID"
        
        if id_col not in df.columns:
            return []
        
        uncertain_values = ['na', 'n/a', 'unknown', 'tbd', 'to be determined',
                           'pending', 'draft', 'temp', 'temporary', '']
        
        results = []
        for idx in df.index:
            value = str(df.at[idx, id_col]).strip().lower()
            if value in uncertain_values or pd.isna(df.at[idx, id_col]):
                results.append((idx, str(df.at[idx, id_col])))
        
        return results
    
    def detect_P202_rev_missing(
        self,
        df: pd.DataFrame
    ) -> List[int]:
        """
        Public API: Check for missing Document_Revision.
        
        Args:
            df: DataFrame
            
        Returns:
            List of row indices with missing revisions
        """
        rev_col = "Document_Revision"
        
        if rev_col not in df.columns:
            return []
        
        null_mask = df[rev_col].isna() | (df[rev_col] == '')
        return df[null_mask].index.tolist()
    
    def detect_P203_duplicate_trans(
        self,
        df: pd.DataFrame,
        group_by_session: bool = True
    ) -> Dict[str, List[int]]:
        """
        Public API: Find duplicate Transmittal_Numbers.
        
        Args:
            df: DataFrame
            group_by_session: Whether to check per session
            
        Returns:
            Dict of transmittal_value -> list of row indices
        """
        trans_col = "Transmittal_Number"
        
        if trans_col not in df.columns:
            return {}
        
        duplicates = {}
        
        if group_by_session and "Submission_Session" in df.columns:
            for session_id, group in df.groupby("Submission_Session"):
                dup_mask = group[trans_col].duplicated(keep=False)
                for idx in group[dup_mask].index:
                    value = str(df.at[idx, trans_col])
                    if value not in duplicates:
                        duplicates[value] = []
                    duplicates[value].append(idx)
        else:
            dup_mask = df[trans_col].duplicated(keep=False)
            for idx in df[dup_mask].index:
                value = str(df.at[idx, trans_col])
                if value not in duplicates:
                    duplicates[value] = []
                duplicates[value].append(idx)
        
        return duplicates

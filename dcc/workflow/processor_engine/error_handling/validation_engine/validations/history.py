"""
Historical Lookup Module (H2xx - Layer 2.5)

Validates data against historical records:
- Cross-session duplicate Document_ID detection
- Historical revision comparison
- Temporal consistency validation
- Previous submission reference validation

Error Codes:
- H2-V-H-0201: Cross-session duplicate Document_ID (CRITICAL)
- H2-V-H-0202: Revision regression vs history (HIGH)
- H2-V-H-0203: Temporal inconsistency across sessions (HIGH)
"""

import pandas as pd
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime


class HistoricalLookup:
    """
    Validates current data against historical records.
    
    Detects cross-session duplicates, revision regressions,
    and temporal inconsistencies.
    """
    
    # Error codes
    ERROR_CROSS_SESSION_DUPLICATE = "H2-V-H-0201"
    ERROR_REVISION_REGRESSION = "H2-V-H-0202"
    ERROR_TEMPORAL_INCONSISTENCY = "H2-V-H-0203"
    
    def __init__(self, historical_data: Optional[pd.DataFrame] = None):
        """
        Initialize historical lookup.
        
        Args:
            historical_data: DataFrame with historical records
        """
        self.historical_data = historical_data
        self._doc_id_index: Dict[str, List[Dict]] = {}
        
        if historical_data is not None:
            self._build_index()
    
    def _build_index(self) -> None:
        """Build Document_ID index from historical data."""
        if self.historical_data is None:
            return
        
        if "Document_ID" not in self.historical_data.columns:
            return
        
        for idx, row in self.historical_data.iterrows():
            doc_id = str(row.get("Document_ID", ""))
            if doc_id and doc_id.lower() not in ['nan', 'none', '']:
                if doc_id not in self._doc_id_index:
                    self._doc_id_index[doc_id] = []
                
                record = {
                    "row_index": idx,
                    "submission_date": row.get("Submission_Date"),
                    "document_revision": row.get("Document_Revision"),
                    "submission_session": row.get("Submission_Session"),
                    "review_status": row.get("Review_Status"),
                    "approval_code": row.get("Approval_Code")
                }
                self._doc_id_index[doc_id].append(record)
    
    def check_cross_session_duplicates(
        self,
        current_df: pd.DataFrame,
        id_column: str = "Document_ID",
        session_column: str = "Submission_Session"
    ) -> List[Tuple[int, str, str]]:
        """
        Check for Document_ID duplicates across different sessions.
        
        Args:
            current_df: Current session DataFrame
            id_column: Document ID column name
            session_column: Session column name
            
        Returns:
            List of (row_index, doc_id, duplicate_session) tuples
        """
        duplicates = []
        
        if id_column not in current_df.columns:
            return duplicates
        
        # Check within current data
        if session_column in current_df.columns:
            # Group by session and check for duplicates
            for doc_id, group in current_df.groupby(id_column):
                if len(group) > 1:
                    sessions = group[session_column].unique()
                    if len(sessions) > 1:
                        # Same ID in different sessions
                        for idx in group.index[1:]:  # Skip first occurrence
                            duplicates.append((
                                idx,
                                str(doc_id),
                                f"Multiple sessions: {', '.join(sessions)}"
                            ))
        
        # Check against historical data
        if self.historical_data is not None:
            for idx, row in current_df.iterrows():
                doc_id = str(row.get(id_column, ""))
                
                if doc_id in self._doc_id_index:
                    # Check if this is really a different session
                    current_session = str(row.get(session_column, ""))
                    
                    for hist_record in self._doc_id_index[doc_id]:
                        hist_session = str(hist_record.get("submission_session", ""))
                        
                        # Only report if different session
                        if hist_session and hist_session != current_session:
                            duplicates.append((
                                idx,
                                doc_id,
                                f"Historical session: {hist_session}"
                            ))
                            break  # Report once per row
        
        return duplicates
    
    def validate_revision_consistency(
        self,
        document_id: str,
        current_revision: str,
        current_date: Optional[datetime] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate revision consistency against history.
        
        Args:
            document_id: Document ID to check
            current_revision: Current revision value
            current_date: Current submission date (optional)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if document_id not in self._doc_id_index:
            return True, None  # New document, no history
        
        history = self._doc_id_index[document_id]
        
        if not history:
            return True, None
        
        # Get latest historical revision
        latest_hist = max(history, 
                         key=lambda x: self._parse_revision(x.get("document_revision", "0")))
        
        latest_rev = latest_hist.get("document_revision", "0")
        
        # Compare revisions
        try:
            current_rev_num = self._parse_revision(current_revision)
            latest_rev_num = self._parse_revision(latest_rev)
            
            if current_rev_num < latest_rev_num:
                return False, (
                    f"Revision regression: current {current_revision} < "
                    f"historical {latest_rev}"
                )
        except (ValueError, TypeError):
            # Can't parse revisions - assume valid
            pass
        
        return True, None
    
    def check_temporal_integrity(
        self,
        current_df: pd.DataFrame,
        date_column: str = "Submission_Date",
        id_column: str = "Document_ID"
    ) -> List[Dict[str, Any]]:
        """
        Check temporal consistency across sessions.
        
        Args:
            current_df: Current DataFrame
            date_column: Date column name
            id_column: ID column name
            
        Returns:
            List of temporal error dictionaries
        """
        errors = []
        
        if id_column not in current_df.columns or date_column not in current_df.columns:
            return errors
        
        for idx, row in current_df.iterrows():
            doc_id = str(row.get(id_column, ""))
            current_date = self._parse_date(row.get(date_column))
            
            if not doc_id or not current_date:
                continue
            
            # Check against history
            if doc_id in self._doc_id_index:
                for hist_record in self._doc_id_index[doc_id]:
                    hist_date = self._parse_date(hist_record.get("submission_date"))
                    
                    if hist_date and current_date < hist_date:
                        errors.append({
                            "row_index": idx,
                            "document_id": doc_id,
                            "current_date": current_date,
                            "historical_date": hist_date,
                            "error_type": "temporal_inconsistency",
                            "message": (
                                f"Current submission ({current_date}) is earlier "
                                f"than historical submission ({hist_date})"
                            )
                        })
                        break
        
        return errors
    
    def check_previous_references(
        self,
        current_df: pd.DataFrame,
        ref_column: str = "All_Submission_Sessions",
        session_column: str = "Submission_Session"
    ) -> List[Tuple[int, str, str]]:
        """
        Validate that previous submission references exist.
        
        Args:
            current_df: Current DataFrame
            ref_column: Column with previous session references
            session_column: Current session column
            
        Returns:
            List of (row_index, current_session, missing_refs) tuples
        """
        errors = []
        
        if ref_column not in current_df.columns:
            return errors
        
        # Build set of valid sessions
        valid_sessions: Set[str] = set()
        
        if session_column in current_df.columns:
            valid_sessions.update(str(s) for s in current_df[session_column].dropna().unique())
        
        if self.historical_data is not None:
            if "Submission_Session" in self.historical_data.columns:
                valid_sessions.update(
                    str(s) for s in self.historical_data["Submission_Session"].dropna().unique()
                )
        
        for idx, row in current_df.iterrows():
            ref_value = row.get(ref_column)
            
            if pd.isna(ref_value) or ref_value == '':
                continue
            
            # Parse reference sessions
            ref_sessions = str(ref_value).split(",")
            ref_sessions = [s.strip() for s in ref_sessions]
            
            # Check if all referenced sessions exist
            missing = [s for s in ref_sessions if s not in valid_sessions]
            
            if missing:
                current_session = str(row.get(session_column, "Unknown"))
                errors.append((
                    idx,
                    current_session,
                    ", ".join(missing)
                ))
        
        return errors
    
    def get_document_history(
        self,
        document_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get full history for a document.
        
        Args:
            document_id: Document ID to lookup
            
        Returns:
            List of historical records
        """
        return self._doc_id_index.get(document_id, [])
    
    def has_document(self, document_id: str) -> bool:
        """
        Check if document exists in history.
        
        Args:
            document_id: Document ID to check
            
        Returns:
            True if document exists
        """
        return document_id in self._doc_id_index
    
    def _parse_date(self, value: Any) -> Optional[datetime]:
        """
        Parse date from various formats.
        
        Args:
            value: Date value to parse
            
        Returns:
            Parsed datetime or None
        """
        if pd.isna(value) or value == '':
            return None
        
        if isinstance(value, datetime):
            return value
        
        if isinstance(value, pd.Timestamp):
            return value.to_pydatetime()
        
        formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%m-%d-%Y"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(str(value), fmt)
            except ValueError:
                continue
        
        return None
    
    def _parse_revision(self, value: str) -> float:
        """
        Parse revision string to number.
        
        Args:
            value: Revision string
            
        Returns:
            Numeric revision value
        """
        value = str(value).strip().upper()
        
        # Try numeric
        try:
            return float(value)
        except ValueError:
            pass
        
        # Try letter (A=1, B=2, etc.)
        if len(value) == 1 and value.isalpha():
            return ord(value) - ord('A') + 1
        
        # Try letter + number
        if len(value) >= 2 and value[0].isalpha():
            letter_val = ord(value[0]) - ord('A') + 1
            try:
                num_val = float(value[1:])
                return letter_val + num_val / 100
            except ValueError:
                pass
        
        # Fallback
        return hash(value) % 10000


def create_historical_lookup(
    historical_data: pd.DataFrame
) -> HistoricalLookup:
    """
    Factory function to create historical lookup.
    
    Args:
        historical_data: Historical records DataFrame
        
    Returns:
        Configured HistoricalLookup instance
    """
    return HistoricalLookup(historical_data)

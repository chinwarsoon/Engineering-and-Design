"""
Approval Hook Module (Layer 4)

Provides mechanisms for:
- Requesting manual approval for "wrong but acceptable" data
- Handling user-initiated suppression
- Maintaining an audit trail of approvals
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class ApprovalRequest:
    """Represents a request for manual data approval."""
    error_id: str
    row_index: int
    column: str
    value: Any
    error_code: str
    justification: str
    requested_by: str
    requested_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "PENDING" # PENDING, APPROVED, REJECTED
    approver: Optional[str] = None
    approved_at: Optional[datetime] = None
    approver_reason: Optional[str] = None
    project_code: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        d = asdict(self)
        d['requested_at'] = self.requested_at.isoformat()
        if self.approved_at:
            d['approved_at'] = self.approved_at.isoformat()
        return d

class ApprovalHook:
    """
    Manages the approval workflow for data errors.
    Supports Layer 4 validation where humans can overrule detected errors.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize approval hook.
        
        Args:
            storage_path: Path to approvals JSON file.
        """
        if storage_path is None:
            # Default path relative to this file
            base_dir = Path(__file__).parent.parent
            storage_path = base_dir / "config" / "approvals.json"
        
        self.storage_path = Path(storage_path)
        self._approvals: Dict[str, ApprovalRequest] = {}
        self._load_approvals()
        
    def _load_approvals(self) -> None:
        """Load approvals from disk."""
        if not self.storage_path.exists():
            return
            
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for aid, adict in data.items():
                    try:
                        # Convert ISO strings back to datetime objects
                        adict['requested_at'] = datetime.fromisoformat(adict['requested_at'])
                        if adict.get('approved_at'):
                            adict['approved_at'] = datetime.fromisoformat(adict['approved_at'])
                        self._approvals[aid] = ApprovalRequest(**adict)
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Failed to parse approval record {aid}: {e}")
        except Exception as e:
            logger.error(f"Failed to load approvals file: {e}")
            
    def _save_approvals(self) -> None:
        """Save approvals to disk."""
        try:
            # Ensure directory exists
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {aid: req.to_dict() for aid, req in self._approvals.items()}
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save approvals file: {e}")
            
    def request_approval(
        self,
        error_id: str,
        row_index: int,
        column: str,
        value: Any,
        error_code: str,
        justification: str,
        requested_by: str,
        project_code: Optional[str] = None
    ) -> ApprovalRequest:
        """
        Request approval for an error instance.
        
        Args:
            error_id: Unique identifier for this error instance
            row_index: Row index in dataset
            column: column name
            value: The problematic value
            error_code: The error code (taxonomy)
            justification: Reason why this should be approved
            requested_by: User ID of requestor
            project_code: Optional project identifier
            
        Returns:
            ApprovalRequest object
        """
        request = ApprovalRequest(
            error_id=error_id,
            row_index=row_index,
            column=column,
            value=value,
            error_code=error_code,
            justification=justification,
            requested_by=requested_by,
            project_code=project_code
        )
        self._approvals[error_id] = request
        self._save_approvals()
        return request
        
    def approve_error(
        self,
        error_id: str,
        approver: str,
        reason: Optional[str] = None
    ) -> bool:
        """
        Approve a pending error request.
        
        Args:
            error_id: Request ID
            approver: User ID of approver
            reason: Optional approval note
            
        Returns:
            True if approved successfully
        """
        if error_id not in self._approvals:
            return False
            
        request = self._approvals[error_id]
        if request.status != "PENDING":
            return False
            
        request.status = "APPROVED"
        request.approver = approver
        request.approved_at = datetime.utcnow()
        request.approver_reason = reason
        self._save_approvals()
        return True
        
    def reject_error(
        self,
        error_id: str,
        approver: str,
        reason: str
    ) -> bool:
        """
        Reject an approval request.
        
        Args:
            error_id: Request ID
            approver: User ID of rejector
            reason: Mandatory rejection reason
            
        Returns:
            True if rejected successfully
        """
        if error_id not in self._approvals:
            return False
            
        request = self._approvals[error_id]
        if request.status != "PENDING":
            return False
            
        request.status = "REJECTED"
        request.approver = approver
        request.approved_at = datetime.utcnow()
        request.approver_reason = reason
        self._save_approvals()
        return True
        
    def get_pending_approvals(self, project_code: Optional[str] = None) -> List[ApprovalRequest]:
        """
        Get all pending approval requests.
        
        Args:
            project_code: Optional filter by project
            
        Returns:
            List of pending ApprovalRequest objects
        """
        return [
            req for req in self._approvals.values()
            if req.status == "PENDING" and (project_code is None or req.project_code == project_code)
        ]
        
    def is_error_approved(self, error_code: str, row_index: int, column: str, value: Any) -> bool:
        """
        Check if a specific error instance has already been approved.
        Used during processing to suppress previously approved errors.
        """
        for req in self._approvals.values():
            if (req.status == "APPROVED" and 
                req.error_code == error_code and 
                req.row_index == row_index and 
                req.column == column and 
                str(req.value) == str(value)):
                return True
        return False

    def get_approval_history(self, error_id: str) -> List[Dict[str, Any]]:
        """Get history of a specific error approval."""
        if error_id not in self._approvals:
            return []
        # In this simple implementation, we only have the current state
        return [self._approvals[error_id].to_dict()]

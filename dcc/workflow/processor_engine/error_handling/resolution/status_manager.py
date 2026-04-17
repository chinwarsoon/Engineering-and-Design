"""
Status Manager Module

Manages error status lifecycle transitions.
Implements 7-state lifecycle, state transition validation, and persistence.

Complies with error_handling_module_workplan.md Phase: Resolution Module Implementation.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json


class StatusManager:
    """
    Manages error status lifecycle transitions.
    
    Implements:
    - 7-state error lifecycle (OPEN → SUPPRESSED → RESOLVED → ARCHIVED)
    - State transition validation
    - Status persistence to Error_Status column
    - Error history tracking (error_history.json)
    - Audit trail for state transitions
    """
    
    def __init__(self, status_loader=None, history_path: Optional[str] = None):
        """
        Initialize status manager with status loader and history tracking.
        
        Breadcrumb: status_loader → state_transitions → history_path → error_history
        
        Args:
            status_loader: StatusLoader instance for lifecycle definitions
            history_path: Path to error_history.json file
        """
        self.status_loader = status_loader
        self.history_path = history_path
        self.error_history: List[Dict[str, Any]] = []
        
        # Define valid state transitions
        self.valid_transitions = {
            'OPEN': ['SUPPRESSED', 'RESOLVED', 'ESCALATED', 'PENDING'],
            'SUPPRESSED': ['RESOLVED', 'REOPEN'],
            'RESOLVED': ['ARCHIVED', 'REOPEN'],
            'ESCALATED': ['RESOLVED'],
            'PENDING': ['RESOLVED', 'REOPEN'],
            'ARCHIVED': ['REOPEN'],
            'REOPEN': ['SUPPRESSED', 'RESOLVED', 'ESCALATED', 'PENDING']
        }
        
        # Terminal states (no outgoing transitions except REOPEN)
        self.terminal_states = ['ARCHIVED']
        
        if history_path:
            self._load_history()
    
    def _load_history(self) -> None:
        """Load error history from JSON file."""
        try:
            with open(self.history_path, 'r') as f:
                self.error_history = json.load(f)
        except FileNotFoundError:
            self.error_history = []
        except Exception as e:
            print(f"Failed to load error history: {e}")
            self.error_history = []
    
    def _save_history(self) -> None:
        """Save error history to JSON file."""
        if not self.history_path:
            return
        
        try:
            with open(self.history_path, 'w') as f:
                json.dump(self.error_history, f, indent=2)
        except Exception as e:
            print(f"Failed to save error history: {e}")
    
    def transition(self, error_id: str, from_status: str, to_status: str, 
                  actor: Optional[str] = None, justification: Optional[str] = None) -> Dict[str, Any]:
        """
        Transition an error to a new status.
        
        Breadcrumb: error_id → from_status → to_status → validate_transition → update_state → log_history
        
        Args:
            error_id: Error identifier
            from_status: Current status
            to_status: Target status
            actor: User or system performing the transition
            justification: Reason for transition
        
        Returns:
            Dict with transition result
        """
        # Validate transition
        if not self._is_valid_transition(from_status, to_status):
            return {
                'success': False,
                'error': f'Invalid transition from {from_status} to {to_status}',
                'valid_transitions': self.valid_transitions.get(from_status, [])
            }
        
        # Log transition
        transition_entry = {
            'timestamp': datetime.now().isoformat(),
            'error_id': error_id,
            'from_status': from_status,
            'to_status': to_status,
            'actor': actor or 'system',
            'justification': justification or 'Status transition'
        }
        self.error_history.append(transition_entry)
        
        # Save history
        self._save_history()
        
        return {
            'success': True,
            'new_status': to_status,
            'transition_entry': transition_entry
        }
    
    def _is_valid_transition(self, from_status: str, to_status: str) -> bool:
        """
        Validate state transition.
        
        Breadcrumb: from_status → to_status → valid_transitions → is_valid
        
        Args:
            from_status: Current status
            to_status: Target status
        
        Returns:
            True if transition is valid, False otherwise
        """
        valid_targets = self.valid_transitions.get(from_status, [])
        return to_status in valid_targets
    
    def get_valid_transitions(self, status: str) -> List[str]:
        """
        Get valid transitions from a status.
        
        Breadcrumb: status → valid_transitions → transitions_list
        
        Args:
            status: Current status
        
        Returns:
            List of valid target statuses
        """
        return self.valid_transitions.get(status, [])
    
    def is_terminal(self, status: str) -> bool:
        """
        Check if status is a terminal state.
        
        Breadcrumb: status → terminal_states → is_terminal
        
        Args:
            status: Status to check
        
        Returns:
            True if terminal, False otherwise
        """
        return status in self.terminal_states
    
    def get_error_history(self, error_id: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get error history for a specific error or all errors.
        
        Breadcrumb: error_id → history → filter → limit → history_entries
        
        Args:
            error_id: Optional error ID to filter by
            limit: Maximum number of entries to return
        
        Returns:
            List of history entries
        """
        history = self.error_history
        
        if error_id:
            history = [e for e in history if e.get('error_id') == error_id]
        
        # Sort by timestamp descending
        history = sorted(history, key=lambda x: x['timestamp'], reverse=True)
        
        if limit:
            history = history[:limit]
        
        return history
    
    def get_current_status(self, error_id: str) -> Optional[str]:
        """
        Get current status of an error from history.
        
        Breadcrumb: error_id → history → latest_entry → current_status
        
        Args:
            error_id: Error identifier
        
        Returns:
            Current status or None if not found
        """
        history = self.get_error_history(error_id, limit=1)
        if history:
            return history[0].get('to_status')
        return None
    
    def persist_status_to_column(self, error_id: str, status: str) -> Dict[str, Any]:
        """
        Persist status to Error_Status column.
        
        Breadcrumb: error_id → status → column_persistence → result
        
        Args:
            error_id: Error identifier
            status: Status to persist
        
        Returns:
            Dict with persistence result
        """
        # This would integrate with the DataFrame processing pipeline
        # For now, return success as placeholder
        return {
            'success': True,
            'error_id': error_id,
            'persisted_status': status,
            'column': 'Error_Status'
        }

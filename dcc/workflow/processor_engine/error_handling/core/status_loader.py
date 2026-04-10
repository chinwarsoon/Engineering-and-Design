"""
Status Lifecycle Loader Module

Loads and manages error status lifecycle definitions.
Provides state machine functionality for error status transitions.
"""

import json
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
from datetime import datetime


class StatusLoader:
    """
    Loads status lifecycle from config/status_lifecycle.json.
    
    Manages:
    - Status states and transitions
    - State descriptions and metadata
    - Workflow definitions
    - Permission rules
    - Notification configurations
    """
    
    _instance = None
    _status_data: Optional[Dict[str, Any]] = None
    
    def __new__(cls, config_path: Optional[str] = None):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize status loader."""
        if self._status_data is not None:
            return
            
        if config_path is None:
            base_dir = Path(__file__).parent.parent
            config_path = base_dir / "config" / "status_lifecycle.json"
        
        self.config_path = Path(config_path)
        self._load_status()
    
    def _load_status(self) -> None:
        """Load status lifecycle from JSON file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Status config not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._status_data = json.load(f)
        
        self.version = self._status_data.get("version", "unknown")
        self._states = self._status_data.get("states", [])
        self._transitions = self._status_data.get("transitions", {})
        self._descriptions = self._status_data.get("descriptions", {})
        self._workflows = self._status_data.get("workflows", {})
        self._permissions = self._status_data.get("permissions", {})
        self._notifications = self._status_data.get("notifications", {})
        
        self._initial_state = self._status_data.get("initial_state", "OPEN")
        self._terminal_states = set(self._status_data.get("terminal_states", ["ARCHIVED"]))
    
    def reload(self) -> None:
        """Reload status data from disk."""
        self._status_data = None
        self._load_status()
    
    def get_all_states(self) -> List[str]:
        """Get all valid status states."""
        return self._states.copy()
    
    def is_valid_state(self, state: str) -> bool:
        """Check if a state is valid."""
        return state in self._states
    
    def is_terminal_state(self, state: str) -> bool:
        """Check if a state is terminal (cannot transition out except reopen)."""
        return state in self._terminal_states
    
    def is_initial_state(self, state: str) -> bool:
        """Check if a state is the initial state."""
        return state == self._initial_state
    
    def get_initial_state(self) -> str:
        """Get the initial state for new errors."""
        return self._initial_state
    
    def get_valid_transitions(self, from_state: str) -> List[str]:
        """
        Get valid transition targets from a state.
        
        Args:
            from_state: Current state
        
        Returns:
            List of valid target states
        """
        transition = self._transitions.get(from_state, {})
        return transition.get("to", [])
    
    def can_transition(self, from_state: str, to_state: str) -> bool:
        """
        Check if a transition is valid.
        
        Args:
            from_state: Current state
            to_state: Target state
        
        Returns:
            True if transition is allowed
        """
        valid_targets = self.get_valid_transitions(from_state)
        return to_state in valid_targets
    
    def get_state_description(self, state: str) -> Optional[Dict[str, Any]]:
        """
        Get full description and metadata for a state.
        
        Returns:
            Dict with label, description, color, icon, etc.
        """
        return self._descriptions.get(state)
    
    def get_state_label(self, state: str) -> str:
        """Get human-readable label for a state."""
        desc = self._descriptions.get(state, {})
        return desc.get("label", state)
    
    def get_state_color(self, state: str) -> str:
        """Get color code for a state (for UI display)."""
        desc = self._descriptions.get(state, {})
        return desc.get("color", "#808080")
    
    def state_requires_action(self, state: str) -> bool:
        """Check if a state requires user action."""
        desc = self._descriptions.get(state, {})
        return desc.get("requires_action", False)
    
    def get_workflow(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """Get workflow definition by name."""
        return self._workflows.get(workflow_name)
    
    def get_all_workflows(self) -> Dict[str, Dict[str, Any]]:
        """Get all workflow definitions."""
        return self._workflows.copy()
    
    def get_workflow_path(self, workflow_name: str) -> List[str]:
        """
        Get the state path for a workflow.
        
        Returns:
            List of states in workflow order
        """
        workflow = self._workflows.get(workflow_name, {})
        return workflow.get("path", [])
    
    def get_permissions(self, state: str) -> Optional[Dict[str, Any]]:
        """Get permission rules for a state."""
        return self._permissions.get(state)
    
    def can_user_transition(self, state: str, user_role: str) -> bool:
        """
        Check if a user role can transition from a state.
        
        Args:
            state: Current state
            user_role: User role (analyst, reviewer, manager, admin, expert)
        
        Returns:
            True if user can transition
        """
        perms = self._permissions.get(state, {})
        allowed = perms.get("can_transition", [])
        return user_role in allowed
    
    def get_notifications(self, event: str) -> Optional[Dict[str, Any]]:
        """
        Get notification configuration for an event.
        
        Events: on_submit, on_approve, on_reject, on_escalate, on_timeout, on_reopen
        """
        return self._notifications.get(event)
    
    def get_transition_description(self, from_state: str, to_state: str) -> str:
        """Get description for a specific transition."""
        if not self.can_transition(from_state, to_state):
            return f"Invalid transition: {from_state} -> {to_state}"
        
        transition = self._transitions.get(from_state, {})
        return transition.get("description", f"Transition from {from_state} to {to_state}")
    
    def suggest_next_states(self, state: str, context: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Suggest next possible states with metadata.
        
        Args:
            state: Current state
            context: Optional context (error severity, user role, etc.)
        
        Returns:
            List of suggested next states with reasons
        """
        valid = self.get_valid_transitions(state)
        suggestions = []
        
        for target in valid:
            desc = self._descriptions.get(target, {})
            suggestion = {
                "state": target,
                "label": desc.get("label", target),
                "requires_action": desc.get("requires_action", False),
                "reason": self.get_transition_description(state, target)
            }
            
            # Add context-aware filtering
            if context:
                user_role = context.get("user_role")
                if user_role and not self.can_user_transition(state, user_role):
                    suggestion["allowed"] = False
                    suggestion["reason"] = f"Role '{user_role}' cannot transition to {target}"
                else:
                    suggestion["allowed"] = True
            else:
                suggestion["allowed"] = True
            
            suggestions.append(suggestion)
        
        return suggestions
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get status lifecycle statistics."""
        return {
            "total_states": len(self._states),
            "terminal_states": len(self._terminal_states),
            "workflows": len(self._workflows),
            "version": self.version,
            "initial_state": self._initial_state
        }

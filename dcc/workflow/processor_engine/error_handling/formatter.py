"""
Error Formatter Module

Handles formatting of error results for different outputs:
- UI (JSON)
- Logs (Text)
- Tooltips
- Localized reports
"""

from typing import List, Dict, Any, Optional
from .detectors.base import DetectionResult
from .localizer import Localizer
from .core.registry import ErrorRegistry

class ErrorFormatter:
    """
    Formats DetectionResult objects into user-friendly strings or structures.
    """
    
    def __init__(self, locale: str = "en"):
        self.localizer = Localizer(locale)
        self.registry = ErrorRegistry()
        
    def set_locale(self, locale: str) -> None:
        """Set the locale for formatting."""
        self.localizer.set_locale(locale)
        
    def format_for_ui(self, result: DetectionResult) -> Dict[str, Any]:
        """
        Formats error for UI display.
        
        Returns:
            Dict with localized message, action, and severity
        """
        error_def = self.registry.get_error(result.error_code) or {}
        message_key = error_def.get("message_key")
        action_key = error_def.get("action_key")
        
        # Build context for localization
        # DetectionResult.context might have some parameters, 
        # but we also need to include result properties
        loc_context = result.context.copy()
        loc_context.update({
            "row": result.row + 1 if result.row is not None else "Unknown",
            "column": result.column or "Unknown",
            "value": str(loc_context.get("value", "null"))
        })
        
        # Default to result message if localization fails
        localized_msg = result.message
        if message_key:
            localized_msg = self.localizer.get_message(message_key, **loc_context)
            
        localized_action = ""
        if action_key:
            localized_action = self.localizer.get_message(action_key)
            
        ui_severity = error_def.get("ui_severity", result.severity.lower())
        
        return {
            "error_code": result.error_code,
            "message": localized_msg,
            "action": localized_action,
            "severity": result.severity,
            "ui_severity": ui_severity,
            "row": result.row,
            "column": result.column,
            "detected_at": result.detected_at.isoformat() if result.detected_at else None
        }
        
    def format_for_log(self, result: DetectionResult) -> str:
        """
        Formats error for structured logging.
        """
        severity_tag = f"[{result.severity}]"
        code_tag = f"[{result.error_code}]"
        location = ""
        if result.row is not None:
            location += f" Row {result.row+1}"
        if result.column:
            location += f" Col {result.column}"
            
        return f"{severity_tag}{code_tag}{location}: {result.message}"
        
    def get_error_tooltip(self, result: DetectionResult) -> str:
        """
        Generates a localized tooltip string.
        """
        ui_data = self.format_for_ui(result)
        tooltip = f"{ui_data['message']}"
        if ui_data['action']:
            tooltip += f"\n\nAction: {ui_data['action']}"
        return tooltip
        
    def format_summary_for_ui(self, errors: List[DetectionResult]) -> List[Dict[str, Any]]:
        """Formats a list of errors for UI."""
        return [self.format_for_ui(e) for e in errors]

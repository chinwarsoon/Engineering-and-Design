"""
Localization Module

Handles loading and retrieving localized error messages from JSON files.
Supports parameter substitution and fallback to default locale.
"""

import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class Localizer:
    """
    Manages localization for error messages and user actions.
    """
    
    _instance = None
    _messages: Dict[str, Dict[str, Any]] = {}
    
    def __new__(cls, default_locale: str = "en"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.default_locale = default_locale
            cls._instance.current_locale = default_locale
        return cls._instance
    
    def __init__(self, default_locale: str = "en"):
        # Singleton init
        pass
        
    def set_locale(self, locale: str) -> None:
        """Set the current locale."""
        self.current_locale = locale
        if locale not in self._messages:
            self._load_locale(locale)
            
    def _load_locale(self, locale: str) -> None:
        """Load localization file for a specific locale."""
        # Fix: path should be relative to this file's location
        base_dir = Path(__file__).parent
        locale_path = base_dir / "config" / "messages" / f"{locale}.json"
        
        if not locale_path.exists():
            logger.warning(f"Locale file not found: {locale_path}")
            if locale == self.default_locale:
                self._messages[locale] = {} # Empty if default not found
                return
            # Fallback to default if locale file not found
            if self.default_locale not in self._messages:
                self._load_locale(self.default_locale)
            self._messages[locale] = self._messages.get(self.default_locale, {})
            return
            
        try:
            with open(locale_path, 'r', encoding='utf-8') as f:
                self._messages[locale] = json.load(f)
            logger.debug(f"Loaded locale: {locale} from {locale_path}")
        except Exception as e:
            logger.error(f"Failed to load locale {locale}: {e}")
            self._messages[locale] = {}
            
    def get_message(self, key: str, locale: Optional[str] = None, **kwargs) -> str:
        """
        Retrieve a localized message with parameter substitution.
        
        Args:
            key: Dot-separated key (e.g., 'error.anchor.null_project_code')
            locale: Override current locale
            **kwargs: Parameters for substitution in the message
            
        Returns:
            Localized and formatted message string
        """
        loc = locale or self.current_locale
        if loc not in self._messages:
            self._load_locale(loc)
            
        messages = self._messages.get(loc, {})
        
        # Traverse nested keys
        parts = key.split('.')
        current = messages
        found = True
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                found = False
                break
                
        if not found or not isinstance(current, str):
            # Key not found, fallback to default locale if not already using it
            if loc != self.default_locale:
                return self.get_message(key, self.default_locale, **kwargs)
            return key # Return key as last resort
            
        # Parameter substitution
        try:
            return current.format(**kwargs)
        except (KeyError, ValueError, IndexError) as e:
            logger.warning(f"Format error for key '{key}' in locale '{loc}': {e}")
            return current

    def get_user_action(self, action_key: str, locale: Optional[str] = None) -> str:
        """Retrieve localized user action."""
        if not action_key.startswith('action.'):
            action_key = f"action.{action_key}"
        return self.get_message(action_key, locale)

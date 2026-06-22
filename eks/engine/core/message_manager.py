"""
EKS Message Manager - catalog lookup, template hydration, verbosity control.
"""
import json
from pathlib import Path
from typing import Any, Dict, Optional
from ..logging.logger import EKSLogger, log_depth


class MessageManager:
    """
    Central message catalog for EKS pipeline.
    Loads message definitions from eks_message_config.json and provides
    template hydration with verbosity level filtering.
    """

    def __init__(self, config_dir: Optional[str | Path] = None, logger: Optional[EKSLogger] = None,
                 verbosity: int = 1):
        self.logger = logger or EKSLogger("MessageManager", level=1)
        self.config_dir = Path(config_dir) if config_dir else Path(__file__).parent.parent.parent / "config"
        self.verbosity = verbosity
        self._catalog: Dict[str, Any] = {}
        self.load_catalog()

    @log_depth
    def load_catalog(self) -> None:
        """Load the message catalog from the config directory."""
        catalog_path = self.config_dir / "schemas" / "eks_message_config.json"
        if not catalog_path.exists():
            self.logger.warning(f"Message catalog not found at {catalog_path}, using defaults")
            return
        try:
            with open(catalog_path, encoding="utf-8") as f:
                self._catalog = json.load(f)
            self.logger.status(f"Loaded message catalog: {self._catalog.get('metadata', {}).get('total_messages', '?')} messages")
        except Exception as e:
            self.logger.error(f"Failed to load message catalog: {e}")

    def get_message(self, msg_id: str) -> Optional[Dict[str, Any]]:
        """Look up a message definition by ID."""
        return self._catalog.get("messages", {}).get(msg_id)

    def get(self, msg_id: str, **kwargs: Any) -> Optional[str]:
        """
        Look up and hydrate a message template, respecting verbosity.
        Returns None if the message level exceeds current verbosity.
        """
        msg_def = self.get_message(msg_id)
        if not msg_def:
            return None
        if msg_def.get("level", 0) > self.verbosity:
            return None
        try:
            return msg_def["template"].format(**kwargs)
        except KeyError as e:
            return msg_def["template"]

    @log_depth
    def show(self, msg_id: str, **kwargs: Any) -> None:
        """
        Display a message via the logger if its verbosity level allows.
        Routes to the appropriate logger method based on message category.
        """
        msg_def = self.get_message(msg_id)
        if not msg_def:
            return
        if msg_def.get("level", 0) > self.verbosity:
            return

        try:
            text = msg_def["template"].format(**kwargs)
        except KeyError:
            text = msg_def["template"]

        category = msg_def.get("category", "status")

        if category == "milestone":
            self.logger.status(text, context=msg_id)
        elif category == "warning":
            self.logger.warning(text, context=msg_id)
        elif category == "error":
            self.logger.error(text, context=msg_id)
        elif category == "progress":
            self.logger.info(text, context=msg_id)
        else:
            self.logger.info(text, context=msg_id)

    def get_all_messages(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Get all messages, optionally filtered by category."""
        msgs = self._catalog.get("messages", {})
        if category:
            return {k: v for k, v in msgs.items() if v.get("category") == category}
        return msgs

    def set_verbosity(self, level: int) -> None:
        """Set the verbosity level (0=quiet, 1=normal, 2=debug, 3=trace)."""
        self.verbosity = level

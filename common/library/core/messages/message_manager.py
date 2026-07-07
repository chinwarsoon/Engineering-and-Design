"""
L11 — BaseMessageManager

Abstract base providing JSON catalog loading, template hydration via
str.format(**kwargs), verbosity filtering, and show() routing to a logger.

Projects extend this class and point _catalog_filename at their own
message config JSON (e.g. eks_message_config.json, pipeline_message_config.json).

Sources
-------
dcc: utility_engine/console/console_output.py  (module-level functions)
eks: engine/core/message_manager.py            (MessageManager class — reference impl)
"""

import json
from abc import ABC
from pathlib import Path
from typing import Any, Dict, Optional


class BaseMessageManager(ABC):
    """
    Base message manager for all pipeline projects.

    Subclass usage
    --------------
    class MyMessageManager(BaseMessageManager):
        _catalog_filename = "my_message_config.json"

    config_dir : Path — directory containing the catalog JSON
    logger     : optional logger instance (must have .status/.info/.warning/.error())
    verbosity  : int  — 0=silent, 1=normal, 2=debug, 3=trace
    """

    _catalog_filename: str = "message_config.json"

    def __init__(
        self,
        config_dir: Optional[str | Path] = None,
        logger=None,
        verbosity: int = 1,
    ):
        self._config_dir = Path(config_dir) if config_dir else Path(__file__).parents[5] / "config"
        self._logger = logger
        self.verbosity = verbosity
        self._catalog: Dict[str, Any] = {}
        self._load_catalog()

    # ------------------------------------------------------------------
    # Catalog loading
    # ------------------------------------------------------------------

    def _load_catalog(self) -> None:
        """Load the message catalog JSON from config_dir/schemas/<filename>."""
        catalog_path = self._config_dir / "schemas" / self._catalog_filename
        if not catalog_path.exists():
            return
        try:
            with open(catalog_path, encoding="utf-8") as f:
                data = json.load(f)
                self._catalog = data.get("messages", data)
        except Exception:
            self._catalog = {}

    def reload_catalog(self) -> None:
        """Force reload of the message catalog from disk."""
        self._catalog = {}
        self._load_catalog()

    # ------------------------------------------------------------------
    # Lookup and hydration
    # ------------------------------------------------------------------

    def get_message(self, msg_id: str) -> Optional[Dict[str, Any]]:
        """Return the raw message definition dict for msg_id, or None."""
        return self._catalog.get(msg_id)

    def get(self, msg_id: str, **kwargs: Any) -> Optional[str]:
        """
        Look up and hydrate a message template, respecting verbosity.

        Returns None if the message level exceeds current verbosity or
        if msg_id is not in the catalog.
        """
        msg_def = self.get_message(msg_id)
        if not msg_def:
            return None
        if msg_def.get("level", 0) > self.verbosity:
            return None
        try:
            return msg_def["template"].format(**kwargs)
        except KeyError:
            return msg_def.get("template", "")

    def show(self, msg_id: str, **kwargs: Any) -> None:
        """
        Hydrate and emit a message via the logger if verbosity allows.

        Routes to logger method based on message category:
            milestone → status
            warning   → warning
            error     → error
            progress/info/other → info
        """
        msg_def = self.get_message(msg_id)
        if not msg_def:
            return
        if msg_def.get("level", 0) > self.verbosity:
            return

        try:
            text = msg_def["template"].format(**kwargs)
        except KeyError:
            text = msg_def.get("template", "")

        if not self._logger:
            print(text)
            return

        category = msg_def.get("category", "info")
        if category == "milestone":
            self._logger.status(text, context=msg_id)
        elif category == "warning":
            self._logger.warning(text, context=msg_id)
        elif category == "error":
            self._logger.error(text, context=msg_id)
        else:
            self._logger.info(text, context=msg_id)

    def set_verbosity(self, level: int) -> None:
        """Set verbosity level (0–3)."""
        self.verbosity = max(0, min(3, level))

    def get_all_messages(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Return all messages, optionally filtered by category."""
        if category:
            return {k: v for k, v in self._catalog.items() if v.get("category") == category}
        return dict(self._catalog)

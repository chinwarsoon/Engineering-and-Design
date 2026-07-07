"""
L10 — BaseErrorManager

Abstract base providing JSON catalog loading, severity lookup,
system/data error handling, fail-fast, and error summary.

Projects extend this class and point _catalog_filename at their own
error config JSON (e.g. eks_error_config.json, dcc_error_config.json).

Sources
-------
dcc: core_engine/errors/error_manager.py  (functional helpers)
eks: engine/core/error_manager.py         (ErrorManager class — reference impl)
"""

import json
from abc import ABC
from pathlib import Path
from typing import Any, Dict, List, Optional


# Severity ordering: lower index = higher severity
_SEVERITY_ORDER = ["FATAL", "CRITICAL", "HIGH", "MEDIUM", "WARNING", "INFO"]
_SEVERITY_LEVELS = {s: i for i, s in enumerate(_SEVERITY_ORDER)}


class BaseErrorManager(ABC):
    """
    Base error manager for all pipeline projects.

    Subclass usage
    --------------
    class MyErrorManager(BaseErrorManager):
        _catalog_filename = "my_error_config.json"

    config_dir : Path — directory containing the catalog JSON
    logger     : optional logger instance (must have .warning() and .error())
    """

    _catalog_filename: str = "error_config.json"

    def __init__(
        self,
        config_dir: Optional[str | Path] = None,
        logger=None,
        fail_fast: bool = True,
    ):
        self._config_dir = Path(config_dir) if config_dir else Path(__file__).parents[5] / "config"
        self._logger = logger
        self._fail_fast_enabled = fail_fast
        self._catalog: Dict[str, Any] = {}
        self._errors: List[Dict[str, Any]] = []
        self._load_catalog()

    # ------------------------------------------------------------------
    # Catalog loading
    # ------------------------------------------------------------------

    def _load_catalog(self) -> None:
        """Load the error catalog JSON from config_dir/schemas/<filename>."""
        catalog_path = self._config_dir / "schemas" / self._catalog_filename
        if not catalog_path.exists():
            self._warn(f"Error catalog not found at {catalog_path}, using defaults")
            return
        try:
            with open(catalog_path, encoding="utf-8") as f:
                self._catalog = json.load(f)
        except Exception as exc:
            self._warn(f"Failed to load error catalog: {exc}")

    def reload_catalog(self) -> None:
        """Force reload of the error catalog from disk."""
        self._catalog = {}
        self._errors = []
        self._load_catalog()

    # ------------------------------------------------------------------
    # Catalog lookup
    # ------------------------------------------------------------------

    def get_system_error(self, code: str) -> Optional[Dict[str, Any]]:
        return self._catalog.get("system_errors", {}).get(code)

    def get_data_error(self, code: str) -> Optional[Dict[str, Any]]:
        return self._catalog.get("data_logic_errors", {}).get(code)

    def get_code_info(self, code: str) -> Optional[Dict[str, Any]]:
        return self.get_system_error(code) or self.get_data_error(code)

    # ------------------------------------------------------------------
    # Error handling
    # ------------------------------------------------------------------

    def handle_system_error(
        self,
        code: str,
        detail: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Handle a system-level error. Returns the error record."""
        entry = self.get_system_error(code) or {
            "code": code,
            "name": "UNKNOWN_SYSTEM_ERROR",
            "message": f"Unknown system error: {code}",
            "severity": "FATAL",
            "stops_pipeline": True,
        }
        msg = entry["message"]
        if detail:
            msg = f"{msg} — {detail}"

        record = {
            "code": code,
            "name": entry["name"],
            "message": msg,
            "severity": entry["severity"],
            "type": "system",
        }
        self._errors.append(record)

        if entry["severity"] in ("FATAL", "CRITICAL"):
            self._error(msg, context=f"system:{code}")
        else:
            self._warn(msg)

        if entry.get("stops_pipeline", False) and self._fail_fast_enabled:
            raise RuntimeError(f"FAIL_FAST [{code}]: {msg}")

        return record

    def handle_data_error(
        self,
        code: str,
        doc_id: Optional[str] = None,
        detail: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Handle a data-level error. Returns the error record."""
        entry = self.get_data_error(code) or {
            "code": code,
            "name": "UNKNOWN_DATA_ERROR",
            "message": f"Unknown data error: {code}",
            "severity": "WARNING",
            "health_score_impact": 0,
        }
        msg = entry["message"]
        if doc_id:
            msg = f"[{doc_id}] {msg}"
        if detail:
            msg = f"{msg} — {detail}"

        record = {
            "code": code,
            "name": entry["name"],
            "message": msg,
            "severity": entry["severity"],
            "type": "data",
            "doc_id": doc_id or "",
            "health_score_impact": entry.get("health_score_impact", 0),
        }
        self._errors.append(record)

        if entry["severity"] in ("FATAL", "CRITICAL"):
            self._error(msg, context=f"data:{code}")
        else:
            self._warn(msg)

        return record

    # ------------------------------------------------------------------
    # Fail-fast
    # ------------------------------------------------------------------

    def set_fail_fast(self, enabled: bool) -> None:
        self._fail_fast_enabled = enabled

    def should_fail_fast(self, severity_threshold: str = "CRITICAL") -> bool:
        """Return True if any recorded error meets or exceeds the threshold."""
        threshold_level = _SEVERITY_LEVELS.get(severity_threshold.upper(), 1)
        for err in self._errors:
            err_level = _SEVERITY_LEVELS.get(err.get("severity", "INFO").upper(), 99)
            if err_level <= threshold_level:
                return True
        return False

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def get_error_summary(self) -> Dict[str, Any]:
        if not self._errors:
            return {"total": 0, "system_errors": 0, "data_errors": 0, "by_severity": {}}
        severity_counts: Dict[str, int] = {}
        for err in self._errors:
            sev = err["severity"]
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        return {
            "total": len(self._errors),
            "system_errors": sum(1 for e in self._errors if e["type"] == "system"),
            "data_errors": sum(1 for e in self._errors if e["type"] == "data"),
            "by_severity": severity_counts,
            "errors": self._errors.copy(),
        }

    def get_health_impact(self, doc_id: Optional[str] = None) -> int:
        """Sum health score impacts, optionally filtered by doc_id."""
        return sum(
            e.get("health_score_impact", 0)
            for e in self._errors
            if e["type"] == "data" and (doc_id is None or e.get("doc_id") == doc_id)
        )

    def clear(self) -> None:
        self._errors.clear()

    # ------------------------------------------------------------------
    # Internal logging helpers
    # ------------------------------------------------------------------

    def _warn(self, msg: str, context: Optional[str] = None) -> None:
        if self._logger:
            self._logger.warning(msg, context=context)

    def _error(self, msg: str, context: Optional[str] = None) -> None:
        if self._logger:
            self._logger.error(msg, context=context)

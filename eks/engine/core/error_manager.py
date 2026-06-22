"""
EKS Error Manager - error code catalog, system/data error handling, fail-fast checks.
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from ..logging.logger import EKSLogger, log_depth


class ErrorManager:
    """
    Central error handling for EKS pipeline.
    Loads the error catalog from eks_error_config.json and provides
    system/data error handling, fail-fast checks, and error summaries.
    """

    def __init__(self, config_dir: Optional[str | Path] = None, logger: Optional[EKSLogger] = None):
        self.logger = logger or EKSLogger("ErrorManager", level=1)
        self.config_dir = Path(config_dir) if config_dir else Path(__file__).parent.parent.parent / "config"
        self._catalog: Dict[str, Any] = {}
        self._fail_fast_enabled = True
        self._errors: List[Dict[str, Any]] = []
        self.load_catalog()

    @log_depth
    def load_catalog(self) -> None:
        """Load the error code catalog from the config directory."""
        catalog_path = self.config_dir / "schemas" / "eks_error_config.json"
        if not catalog_path.exists():
            self.logger.warning(f"Error catalog not found at {catalog_path}, using defaults")
            return
        try:
            with open(catalog_path, encoding="utf-8") as f:
                self._catalog = json.load(f)
            self.logger.status(f"Loaded error catalog: {self._catalog.get('metadata', {}).get('total_codes', '?')} codes")
        except Exception as e:
            self.logger.error(f"Failed to load error catalog: {e}")

    def get_system_error(self, code: str) -> Optional[Dict[str, Any]]:
        """Look up a system error by code."""
        return self._catalog.get("system_errors", {}).get(code)

    def get_data_error(self, code: str) -> Optional[Dict[str, Any]]:
        """Look up a data error by code."""
        return self._catalog.get("data_logic_errors", {}).get(code)

    def get_code_info(self, code: str) -> Optional[Dict[str, Any]]:
        """Look up any error (system or data) by code."""
        return self.get_system_error(code) or self.get_data_error(code)

    @log_depth
    def handle_system_error(self, code: str, detail: Optional[str] = None) -> Dict[str, Any]:
        """Handle a system-level error, returning the error record."""
        entry = self.get_system_error(code)
        if not entry:
            entry = {
                "code": code, "name": "UNKNOWN_SYSTEM_ERROR",
                "message": f"Unknown system error: {code}", "severity": "FATAL",
                "stops_pipeline": True
            }
        msg = entry["message"]
        if detail:
            msg = f"{msg} — {detail}"

        self._errors.append({
            "code": code, "name": entry["name"], "message": msg,
            "severity": entry["severity"], "type": "system"
        })

        if entry["severity"] in ("FATAL", "CRITICAL"):
            self.logger.error(msg, context=f"system:{code}")
        else:
            self.logger.warning(msg, context=f"system:{code}")

        if entry.get("stops_pipeline", False) and self._fail_fast_enabled:
            self._fail_fast(code, msg)

        return {"code": code, "name": entry["name"], "message": msg, "severity": entry["severity"]}

    @log_depth
    def handle_data_error(self, code: str, doc_id: Optional[str] = None, detail: Optional[str] = None) -> Dict[str, Any]:
        """Handle a data-level error, returning the error record with health impact."""
        entry = self.get_data_error(code)
        if not entry:
            entry = {
                "code": code, "name": "UNKNOWN_DATA_ERROR",
                "message": f"Unknown data error: {code}", "severity": "WARNING",
                "health_score_impact": 0
            }
        msg = entry["message"]
        if doc_id:
            msg = f"[{doc_id}] {msg}"
        if detail:
            msg = f"{msg} — {detail}"

        self._errors.append({
            "code": code, "name": entry["name"], "message": msg,
            "severity": entry["severity"], "type": "data",
            "doc_id": doc_id or "",
            "health_score_impact": entry.get("health_score_impact", 0)
        })

        if entry["severity"] in ("FATAL", "CRITICAL"):
            self.logger.error(msg, context=f"data:{code}")
        elif entry["severity"] == "HIGH":
            self.logger.warning(msg, context=f"data:{code}")
        else:
            self.logger.info(msg, context=f"data:{code}")

        return {
            "code": code, "name": entry["name"], "message": msg,
            "severity": entry["severity"],
            "health_score_impact": entry.get("health_score_impact", 0)
        }

    @log_depth
    def _fail_fast(self, code: str, message: str) -> None:
        """Fail-fast: raise an exception with error details."""
        raise RuntimeError(f"FAIL_FAST [{code}]: {message}")

    def get_error_summary(self) -> Dict[str, Any]:
        """Return a summary of all errors encountered."""
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
            "errors": self._errors.copy()
        }

    def set_fail_fast(self, enabled: bool) -> None:
        """Enable or disable fail-fast behavior."""
        self._fail_fast_enabled = enabled

    def get_health_impact(self, doc_id: Optional[str] = None) -> int:
        """Sum health score impacts for all errors, optionally filtered by doc_id."""
        impact = 0
        for err in self._errors:
            if err["type"] == "data":
                if doc_id is None or err.get("doc_id") == doc_id:
                    impact += err.get("health_score_impact", 0)
        return impact

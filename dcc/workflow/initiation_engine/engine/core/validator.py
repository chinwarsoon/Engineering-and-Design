"""
Core orchestrator for project setup validation.
Refactored from project_setup_validation.py ProjectSetupValidator class.
"""

import json
from pathlib import Path
from typing import Dict, Any

from dcc.workflow.initiation_engine.engine.utils.paths import normalize_path, default_base_path, get_schema_path
from dcc.workflow.initiation_engine.engine.system.os_detect import detect_os
from dcc.workflow.initiation_engine.engine.validators.items import (
    validate_folders,
    validate_named_files,
    validate_environment,
    check_ready,
)
from dcc.workflow.initiation_engine.engine.core.reports import format_report


class ProjectSetupValidator:
    """Validate the DCC project structure from config/schemas/project_setup.json."""

    def __init__(self, base_path: str | Path | None = None, schema_path: str | Path | None = None):
        self.base_path = normalize_path(base_path) if base_path else default_base_path()
        self.schema_path = (
            normalize_path(schema_path)
            if schema_path
            else get_schema_path(self.base_path)
        )
        self.schema_document: Dict[str, Any] = {}
        self.project_setup: Dict[str, Any] = {}
        self.validation_rules: Dict[str, bool] = {}
        self.os_info = detect_os()

        if self.schema_path.is_file():
            self.schema_document = self._load_json(self.schema_path)
            self.project_setup = self._extract_project_setup(self.schema_document)
            self.validation_rules = {
                item.get("rule"): bool(item.get("enabled", True))
                for item in self.project_setup.get("validation_rules", [])
                if isinstance(item, dict) and item.get("rule")
            }

    def _load_json(self, path: Path) -> Dict[str, Any]:
        """Load JSON document from disk."""
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _extract_project_setup(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Extract project_setup configuration from schema document."""
        config = document.get("project_setup", [])
        if isinstance(config, list) and config:
            first_item = config[0]
            if isinstance(first_item, dict):
                return first_item
        return {}

    def _rule_enabled(self, rule_name: str) -> bool:
        """Check if a validation rule is enabled."""
        return self.validation_rules.get(rule_name, True)

    def validate(self) -> Dict[str, Any]:
        """Run full project setup validation."""
        results: Dict[str, Any] = {
            "base_path": str(self.base_path),
            "schema_path": str(self.schema_path),
            "os": self.os_info,
            "folders": [],
            "root_files": [],
            "schema_files": [],
            "workflow_files": [],
            "tool_files": [],
            "environment": [],
            "errors": [],
            "ready": True,
        }

        if not self.schema_path.is_file():
            results["errors"].append(f"Project setup schema not found: {self.schema_path}")
            results["ready"] = False
            return results

        if not self.project_setup:
            results["errors"].append("No project_setup configuration found in project_setup.json")
            results["ready"] = False
            return results

        if self._rule_enabled("check_folders"):
            validate_folders(
                results,
                self.project_setup.get("folders", []),
                self.base_path,
                self.os_info,
            )

        if self._rule_enabled("check_files"):
            validate_named_files(
                results,
                "root_files",
                self.project_setup.get("root_files", []),
                self.base_path,
                "name",
                "purpose",
            )
            validate_named_files(
                results,
                "schema_files",
                self.project_setup.get("schema_files", []),
                self.base_path / "config" / "schemas",
                "filename",
                "description",
            )
            validate_named_files(
                results,
                "workflow_files",
                self.project_setup.get("workflow_files", []),
                self.base_path / "workflow",
                "filename",
                "description",
            )
            validate_named_files(
                results,
                "tool_files",
                self.project_setup.get("tool_files", []),
                self.base_path / "tools",
                "filename",
                "description",
            )
            validate_environment(
                results,
                self.project_setup.get("environment", []),
                self.base_path,
            )

        results["ready"] = check_ready(results)
        return results

    def format_report(self, results: Dict[str, Any]) -> str:
        """Format validation results for terminal output."""
        return format_report(results)

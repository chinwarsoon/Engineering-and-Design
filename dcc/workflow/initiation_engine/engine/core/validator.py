"""
Core orchestrator for project setup validation.
Refactored from project_setup_validation.py ProjectSetupValidator class.
"""

import json
from pathlib import Path
from typing import Dict, Any

from ..utils.paths import normalize_path, default_base_path, get_schema_path
from ..system.os_detect import detect_os
from ..validators.items import (
    validate_folders,
    validate_named_files,
    validate_environment,
    check_ready,
)
from .reports import format_report
from ..utils.logging import status_print


class ProjectSetupValidator:
    """
    Validate the DCC project structure from config/schemas/project_setup.json.

    This class orchestrates the validation of project folders, files, environment
    specifications, and dependencies. It supports configurable validation rules
    and OS-specific behaviors like auto-folder creation.

    Attributes:
        base_path: Normalized absolute path to the project root.
        schema_path: Normalized absolute path to project_setup.json.
        schema_document: Raw parsed JSON document from schema_path.
        project_setup: Extracted project setup configuration dictionary.
        validation_rules: Dictionary mapping rule names to enabled status.
        os_info: OS detection results with 'system' and 'normalized' keys.
    """

    def __init__(self, base_path: str | Path | None = None, schema_path: str | Path | None = None):
        """
        Initialize the ProjectSetupValidator.

        Validates the DCC project structure by loading the project_setup.json schema
        and preparing validation rules. Detects OS and normalizes paths.

        Args:
            base_path: Project root directory. If None, uses default_base_path().
            schema_path: Path to project_setup.json. If None, uses get_schema_path().

        Breadcrumb Comments:
            - base_path: Initialized here via normalize_path() or default_base_path().
                         Consumed by validate_folders(), validate_named_files(),
                         validate_environment(), resolve_platform_paths().
            - schema_path: Initialized here via normalize_path() or get_schema_path().
                         Consumed by _load_json(), validate().
            - os_info: Initialized here via detect_os().
                      Consumed by validate_folders(), should_auto_create_folders().
            - validation_rules: Initialized here from _extract_project_setup().
                               Consumed by _rule_enabled(), validate().
        """
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
            status_print(f"Loading schema from: {self.schema_path} for validation")
            self.schema_document = self._load_json(self.schema_path)
            self.project_setup = self._extract_project_setup(self.schema_document)
            self.validation_rules = {
                item.get("rule"): bool(item.get("enabled", True))
                for item in self.project_setup.get("validation_rules", [])
                if isinstance(item, dict) and item.get("rule")
            }

    def _load_json(self, path: Path) -> Dict[str, Any]:
        """
        Load JSON document from disk.

        Args:
            path: Path to the JSON file.

        Returns:
            Parsed JSON document as a dictionary.

        Breadcrumb Comments:
            - path: Received from schema_path (initialized in __init__).
                    Consumed here to load schema_document.
        """
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _extract_project_setup(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract project_setup configuration from schema document.
        
        Handles two structures:
        1. "project_setup": [] - Array of projects, extracts first item
        2. "project_setup": {} - Direct object, returns as-is
        """
        config = document.get("project_setup", [])
        
        # Case 1: project_setup is a list/array
        if isinstance(config, list) and config:
            first_item = config[0]
            if isinstance(first_item, dict):
                return first_item
            return {}
        
        # Case 2: project_setup is a direct object/dict
        if isinstance(config, dict):
            return config
            
        return {}

    def _rule_enabled(self, rule_name: str) -> bool:
        """
        Check if a validation rule is enabled.

        Args:
            rule_name: Name of the validation rule to check.

        Returns:
            True if the rule is enabled or not explicitly disabled.

        Breadcrumb Comments:
            - rule_name: Passed from validate() for each check ("check_folders", "check_files").
            - validation_rules: Initialized in __init__ from _extract_project_setup().
                              Consumed here to determine if rule should run.
        """
        return self.validation_rules.get(rule_name, True)

    def validate(self) -> Dict[str, Any]:
        """
        Run full project setup validation.

        Executes all enabled validation rules against the project structure.
        Populates the results dictionary with validation outcomes.

        Returns:
            Dictionary containing validation results for all categories.

        Breadcrumb Comments:
            - results: Initialized here as empty accumulator.
                       Modified by validate_folders(), validate_named_files(),
                       validate_environment(), check_ready().
                       Consumed by format_report(), caller inspection.
            - project_setup: Loaded in __init__ via _extract_project_setup().
                            Consumed here for folders, root_files, schema_files,
                            workflow_files, tool_files, environment specs.
            - validation_rules: Checked via _rule_enabled() to conditionally run checks.
            - base_path: Passed to all validation functions for path resolution.
            - os_info: Passed to validate_folders() for auto-creation decisions.
        """
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
        """
        Format validation results for terminal output.

        Args:
            results: Validation results dictionary from validate().

        Returns:
            Formatted multi-line string for terminal display.

        Breadcrumb Comments:
            - results: Initialized in validate(), modified by all validators.
                       Passed here to generate human-readable report.
                       Contains folders, root_files, schema_files, workflow_files,
                       tool_files, environment sections with status indicators.
        """
        return format_report(results)

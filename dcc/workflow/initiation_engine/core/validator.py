"""
Core orchestrator for project setup validation.
Refactored from project_setup_validation.py ProjectSetupValidator class.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

from ..utils.paths import normalize_path, default_base_path, get_schema_path
from ..system.os_detect import detect_os
from ..validators.items import (
    validate_folders,
    validate_named_files,
    validate_environment,
    check_ready,
)
from .reports import format_report
from ..utils.logging import log_context, log_status, log_error, trace_parameter, status_print

# Import RefResolver for schema $ref resolution (Phase F)
from workflow.schema_engine.loader.ref_resolver import RefResolver, RefResolutionError


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
        self._ref_resolver: Optional[RefResolver] = None

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

    def _init_ref_resolver(self) -> Optional[RefResolver]:
        """
        Initialize RefResolver for schema $ref resolution.
        
        Breadcrumb: schema_path → ref_resolver → uri_resolution
        
        Returns:
            RefResolver instance or None if project_setup.json not available
            
        Complies with agent_rule.md Section 2.4: URI-based schema resolution.
        """
        if self._ref_resolver is not None:
            return self._ref_resolver
            
        try:
            # Find project_setup.json for strict registration
            project_setup_path = self.base_path / "config" / "schemas" / "project_setup.json"
            if not project_setup_path.exists():
                return None
                
            self._ref_resolver = RefResolver(
                project_setup_path=project_setup_path,
                schema_directories=[
                    self.base_path / "config" / "schemas"
                ]
            )
            return self._ref_resolver
        except Exception as exc:
            log_error(f"Failed to initialize RefResolver: {exc}", "validator", "_init_ref_resolver", fatal=False)
            return None

    def _extract_project_setup(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract project_setup configuration from schema document.
        
        Handles schema restructuring from Phase C (fragment pattern) and Phase F
        (master_registry.json integration):
        1. Old: "project_setup": {} - Direct configuration object
        2. New: JSON Schema with properties/$ref (extract defaults from schema)
        3. New: Resolve $ref to master_registry.json for configuration values
        
        Breadcrumb: document → schema_check → resolve_refs → extract_defaults → config
        
        Complies with:
        - agent_rule.md Section 2.3: project_setup.json as main entry point
        - agent_rule.md Section 2.4: URI-based schema resolution
        - agent_rule.md Section 2.5: Schema fragment pattern
        """
        # Case 1: Legacy format - direct project_setup object
        if "project_setup" in document:
            config = document["project_setup"]
            if isinstance(config, list) and config:
                first_item = config[0]
                if isinstance(first_item, dict):
                    return first_item
                return {}
            if isinstance(config, dict):
                return config
            return {}
        
        # Case 2: New schema format with $ref to registry (Phase F)
        if "$schema" in document and "registry" in document.get("properties", {}):
            resolver = self._init_ref_resolver()
            if resolver:
                try:
                    # Resolve registry $ref to get configuration from master_registry.json
                    registry_config = resolver.resolve(
                        {"$ref": "https://dcc-pipeline.internal/schemas/master-registry"},
                        document
                    )
                    if registry_config and "default" in registry_config:
                        defaults = registry_config["default"]
                        # Map project_structure to folders/root_files format
                        return self._map_registry_to_project_setup(defaults)
                except RefResolutionError as exc:
                    log_error(f"Failed to resolve registry $ref: {exc}", "validator", "_extract_project_setup", fatal=False)
        
        # Case 3: New schema format - JSON Schema with $schema key (extract defaults)
        if "$schema" in document:
            return self._extract_from_schema(document)
        
        # Case 4: Properties-based config (direct properties without $schema)
        if "properties" in document and isinstance(document["properties"], dict):
            return self._extract_from_schema(document)
            
        return {}
    
    def _map_registry_to_project_setup(self, registry_defaults: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map master_registry.json defaults to project_setup configuration format.
        
        Breadcrumb: registry_defaults → project_structure → folders/root_files
        
        Args:
            registry_defaults: Default values from master_registry.json
            
        Returns:
            Dictionary in project_setup format (folders, root_files, etc.)
        """
        config: Dict[str, Any] = {}
        
        # Extract project_structure for folders
        project_structure = registry_defaults.get("project_structure", {})
        if "required_folders" in project_structure:
            config["folders"] = [
                {
                    "name": folder.get("name", ""),
                    "required": folder.get("required", False),
                    "purpose": folder.get("purpose", ""),
                    "auto_created": False
                }
                for folder in project_structure["required_folders"]
            ]
        
        # Extract other configuration sections
        if "validation_rules" in registry_defaults:
            config["validation_rules"] = registry_defaults["validation_rules"]
        
        if "environment" in registry_defaults:
            config["environment"] = registry_defaults["environment"]
        
        if "dependencies" in registry_defaults:
            config["dependencies"] = registry_defaults["dependencies"]
            
        return config
    
    def _extract_from_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract configuration defaults from JSON Schema properties.
        
        Breadcrumb: schema → properties → defaults → config
        
        Args:
            schema: JSON Schema document with properties
            
        Returns:
            Dictionary with default values from schema properties
        """
        config = {}
        properties = schema.get("properties", {})
        definitions = schema.get("definitions", {})
        
        for key, prop_def in properties.items():
            # Handle $ref references by resolving to definition
            if "$ref" in prop_def:
                ref_path = prop_def["$ref"]
                # Check if it's a local definition reference
                if ref_path.startswith("#/definitions/"):
                    def_name = ref_path.replace("#/definitions/", "")
                    if def_name in definitions:
                        ref_def = definitions[def_name]
                        # Extract default from referenced definition
                        if "default" in ref_def:
                            config[key] = ref_def["default"]
                        elif "properties" in ref_def:
                            # Handle nested object definitions
                            config[key] = self._extract_from_schema(ref_def)
                continue
            
            # Extract default value if present
            if "default" in prop_def:
                config[key] = prop_def["default"]
            elif "properties" in prop_def and isinstance(prop_def["properties"], dict):
                # Nested object - extract recursively
                nested = self._extract_from_schema(prop_def)
                if nested:
                    config[key] = nested
            elif "type" in prop_def and prop_def["type"] == "array" and "default" in prop_def.get("items", {}):
                # Array with default items
                config[key] = prop_def["items"]["default"]
        
        return config

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
        with log_context("validator", "validate"):
            return self._do_validate()

    def _do_validate(self) -> Dict[str, Any]:
        """Internal validation implementation."""
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

        trace_parameter("schema_path", self.schema_path, "validator", "checking")
        if not self.schema_path.is_file():
            log_error(f"Schema not found: {self.schema_path}", "validator", "validate", fatal=False)
            results["errors"].append(f"Project setup schema not found: {self.schema_path}")
            results["ready"] = False
            return results

        if not self.project_setup:
            log_error("No project_setup configuration found", "validator", "validate", fatal=False)
            results["errors"].append("No project_setup configuration found in project_setup.json")
            results["ready"] = False
            return results

        log_status(f"OS: {self.os_info['system']} ({self.os_info['normalized']})", "validator")

        if self._rule_enabled("check_folders"):
            folders = self.project_setup.get("folders", [])
            log_status(f"Validating {len(folders)} folders...", "validator")
            validate_folders(
                results,
                folders,
                self.base_path,
                self.os_info,
            )
            log_status(f"Folders: {sum(1 for f in results['folders'] if f['exists'])} exist", "validator")

        if self._rule_enabled("check_files"):
            with log_context("validator", "validate_files"):
                root_files = self.project_setup.get("root_files", [])
                log_status(f"Validating {len(root_files)} root files...", "validator")
                validate_named_files(
                    results,
                    "root_files",
                    root_files,
                    self.base_path,
                    "name",
                    "purpose",
                )

                schema_files = self.project_setup.get("schema_files", [])
                log_status(f"Validating {len(schema_files)} schema files...", "validator")
                validate_named_files(
                    results,
                    "schema_files",
                    schema_files,
                    self.base_path / "config" / "schemas",
                    "filename",
                    "description",
                )

                workflow_files = self.project_setup.get("workflow_files", [])
                log_status(f"Validating {len(workflow_files)} workflow files...", "validator")
                validate_named_files(
                    results,
                    "workflow_files",
                    workflow_files,
                    self.base_path / "workflow",
                    "filename",
                    "description",
                )

                tool_files = self.project_setup.get("tool_files", [])
                log_status(f"Validating {len(tool_files)} tool files...", "validator")
                validate_named_files(
                    results,
                    "tool_files",
                    tool_files,
                    self.base_path / "tools",
                    "filename",
                    "description",
                )

                env_items = self.project_setup.get("environment", [])
                log_status(f"Validating {len(env_items)} environment items...", "validator")
                validate_environment(
                    results,
                    env_items,
                    self.base_path,
                )

        results["ready"] = check_ready(results)
        log_status(f"Ready: {'YES' if results['ready'] else 'NO'}", "validator")
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

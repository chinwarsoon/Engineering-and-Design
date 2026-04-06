#!/usr/bin/env python3
"""
Schema-driven validation for required DCC project folders and files.
"""

from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path
from typing import Any, Dict, Iterable, List


class ProjectSetupValidator:
    """Validate the DCC project structure from config/schemas/project_setup.json."""

    def __init__(self, base_path: str | Path | None = None, schema_path: str | Path | None = None):
        self.base_path = self._normalize_path(base_path) if base_path else self._default_base_path()
        self.schema_path = (
            self._normalize_path(schema_path)
            if schema_path
            else self.base_path / "config" / "schemas" / "project_setup.json"
        )
        self.schema_document: Dict[str, Any] = {}
        self.project_setup: Dict[str, Any] = {}
        self.validation_rules: Dict[str, bool] = {}
        self.os_info = self._detect_os()

        if self.schema_path.is_file():
            self.schema_document = self._load_json(self.schema_path)
            self.project_setup = self._extract_project_setup(self.schema_document)
            self.validation_rules = {
                item.get("rule"): bool(item.get("enabled", True))
                for item in self.project_setup.get("validation_rules", [])
                if isinstance(item, dict) and item.get("rule")
            }

    def _normalize_path(self, value: str | Path) -> Path:
        p = Path(value).expanduser()
        try:
            return p.resolve()
        except (OSError, PermissionError):
            return Path(p.absolute())

    def _default_base_path(self) -> Path:
        script_dir = Path(__file__).expanduser()
        try:
            script_dir = script_dir.resolve()
        except (OSError, PermissionError):
            pass
        return script_dir.parent if script_dir.name.lower() == "workflow" else script_dir

    def _load_json(self, path: Path) -> Dict[str, Any]:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _detect_os(self) -> Dict[str, str]:
        system_name = platform.system().strip() or "Unknown"
        normalized_name = {
            "Windows": "windows",
            "Linux": "linux",
            "Darwin": "macos",
        }.get(system_name, system_name.lower())
        return {
            "system": system_name,
            "normalized": normalized_name,
        }

    def _extract_project_setup(self, document: Dict[str, Any]) -> Dict[str, Any]:
        config = document.get("project_setup", [])
        if isinstance(config, list) and config:
            first_item = config[0]
            if isinstance(first_item, dict):
                return first_item
        return {}

    def _rule_enabled(self, rule_name: str) -> bool:
        return self.validation_rules.get(rule_name, True)

    def _record_path_check(
        self,
        results: Dict[str, Any],
        category: str,
        name: str,
        path: Path,
        required: bool,
        exists: bool,
        description: str,
        item_type: str,
    ) -> None:
        results[category].append(
            {
                "name": name,
                "path": str(path),
                "required": required,
                "exists": exists,
                "description": description,
                "item_type": item_type,
            }
        )

    def _should_auto_create_folders(self) -> bool:
        return self.os_info["normalized"] in {"windows", "linux", "macos"}

    def _ensure_folder(self, path: Path) -> bool:
        path.mkdir(parents=True, exist_ok=True)
        return path.is_dir()

    def _validate_folders(self, results: Dict[str, Any]) -> None:
        for folder in self.project_setup.get("folders", []):
            if not isinstance(folder, dict):
                continue
            name = folder.get("name", "")
            if not name:
                continue
            required = bool(folder.get("required", True))
            path = self.base_path / name
            exists = path.is_dir()
            auto_created = False
            if not exists and self._should_auto_create_folders():
                auto_created = self._ensure_folder(path)
                exists = path.is_dir()

            self._record_path_check(
                results,
                "folders",
                name,
                path,
                required,
                exists,
                folder.get("purpose", ""),
                "folder",
            )
            results["folders"][-1]["auto_created"] = auto_created
            results["folders"][-1]["schema_auto_created"] = bool(folder.get("auto_created", False))

    def _validate_named_files(
        self,
        results: Dict[str, Any],
        category: str,
        items: Iterable[Dict[str, Any]],
        parent_dir: Path,
        name_key: str,
        description_key: str,
    ) -> None:
        for item in items:
            if not isinstance(item, dict):
                continue
            name = item.get(name_key, "")
            if not name:
                continue
            required = bool(item.get("required", True))
            path = parent_dir / name
            self._record_path_check(
                results,
                category,
                name,
                path,
                required,
                path.is_file(),
                item.get(description_key, ""),
                "file",
            )

    def _validate_environment(self, results: Dict[str, Any]) -> None:
        for item in self.project_setup.get("environment", []):
            if not isinstance(item, dict):
                continue
            filename = item.get("file", "")
            if not filename:
                continue
            location = item.get("location", "root")
            if location == "root":
                path = self.base_path / filename
            else:
                path = self.base_path / location / filename

            results["environment"].append(
                {
                    "name": item.get("name", filename),
                    "path": str(path),
                    "required": bool(item.get("required", True)),
                    "exists": path.is_file(),
                    "location": location,
                    "setup_commands": item.get("setup_commands", []),
                    "key_dependencies": item.get("key_dependencies", []),
                }
            )

    def validate(self) -> Dict[str, Any]:
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
            self._validate_folders(results)

        if self._rule_enabled("check_files"):
            self._validate_named_files(
                results,
                "root_files",
                self.project_setup.get("root_files", []),
                self.base_path,
                "name",
                "purpose",
            )
            self._validate_named_files(
                results,
                "schema_files",
                self.project_setup.get("schema_files", []),
                self.base_path / "config" / "schemas",
                "filename",
                "description",
            )
            self._validate_named_files(
                results,
                "workflow_files",
                self.project_setup.get("workflow_files", []),
                self.base_path / "workflow",
                "filename",
                "description",
            )
            self._validate_named_files(
                results,
                "tool_files",
                self.project_setup.get("tool_files", []),
                self.base_path / "tools",
                "filename",
                "description",
            )
            self._validate_environment(results)

        results["ready"] = self._is_ready(results)
        return results

    def _is_ready(self, results: Dict[str, Any]) -> bool:
        if results["errors"]:
            return False

        required_sections = ["folders", "root_files", "schema_files", "workflow_files", "tool_files", "environment"]
        for section in required_sections:
            for item in results.get(section, []):
                if item.get("required") and not item.get("exists"):
                    return False

        return True

    def format_report(self, results: Dict[str, Any]) -> str:
        lines: List[str] = []
        lines.append("PROJECT SETUP VALIDATION")
        lines.append("=" * 72)
        lines.append(f"Base Path: {results['base_path']}")
        lines.append(f"Schema Path: {results['schema_path']}")
        lines.append(f"Operating System: {results['os']['system']} ({results['os']['normalized']})")

        if results["errors"]:
            lines.append("")
            lines.append("Errors:")
            for error in results["errors"]:
                lines.append(f"  - {error}")
            return "\n".join(lines)

        section_titles = {
            "folders": "Required Folders",
            "root_files": "Root Files",
            "schema_files": "Schema Files",
            "workflow_files": "Workflow Files",
            "tool_files": "Tool Files",
            "environment": "Environment Files",
        }

        for key, title in section_titles.items():
            entries = results.get(key, [])
            if not entries:
                continue
            lines.append("")
            lines.append(f"{title}:")
            for item in entries:
                status = "OK" if item["exists"] else ("MISS" if item["required"] else "WARN")
                required_text = "required" if item["required"] else "optional"
                auto_created_text = " [created]" if item.get("auto_created") else ""
                lines.append(
                    f"  [{status}] {item['name'] if 'name' in item else Path(item['path']).name} "
                    f"({required_text}) -> {item['path']}{auto_created_text}"
                )

        lines.append("")
        lines.append("Summary:")
        lines.append(f"  Ready: {'YES' if results['ready'] else 'NO'}")
        return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate required DCC project folders and files.")
    parser.add_argument(
        "--base-path",
        default=None,
        help="Project root to validate. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--schema-path",
        default=None,
        help="Override the project setup schema path. Defaults to <base-path>/config/schemas/project_setup.json.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the validation results as JSON instead of a text report.",
    )
    args = parser.parse_args()

    validator = ProjectSetupValidator(base_path=args.base_path, schema_path=args.schema_path)
    results = validator.validate()

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(validator.format_report(results))

    return 0 if results.get("ready") else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
Schema-driven validation for required DCC project folders and files.
"""

from __future__ import annotations

import argparse
import json
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

        if self.schema_path.is_file():
            self.schema_document = self._load_json(self.schema_path)
            self.project_setup = self._extract_project_setup(self.schema_document)
            self.validation_rules = {
                item.get("rule"): bool(item.get("enabled", True))
                for item in self.project_setup.get("validation_rules", [])
                if isinstance(item, dict) and item.get("rule")
            }

    def _normalize_path(self, value: str | Path) -> Path:
        return Path(value).expanduser().resolve()

    def _default_base_path(self) -> Path:
        cwd = Path.cwd().resolve()
        return cwd.parent if cwd.name.lower() == "workflow" else cwd

    def _load_json(self, path: Path) -> Dict[str, Any]:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

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

    def _validate_folders(self, results: Dict[str, Any]) -> None:
        for folder in self.project_setup.get("folders", []):
            if not isinstance(folder, dict):
                continue
            name = folder.get("name", "")
            if not name:
                continue
            required = bool(folder.get("required", True))
            path = self.base_path / name
            self._record_path_check(
                results,
                "folders",
                name,
                path,
                required,
                path.is_dir(),
                folder.get("purpose", ""),
                "folder",
            )

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

    def _validate_schema_references(self, results: Dict[str, Any]) -> None:
        main_schema = self.base_path / "config" / "schemas" / "dcc_register_enhanced.json"
        if not main_schema.is_file():
            results["schema_refs"].append(
                {
                    "source": str(main_schema),
                    "reference": None,
                    "resolved_path": None,
                    "exists": False,
                    "error": "Main schema file not found",
                }
            )
            return

        try:
            schema_data = self._load_json(main_schema)
        except Exception as exc:  # pragma: no cover - defensive
            results["schema_refs"].append(
                {
                    "source": str(main_schema),
                    "reference": None,
                    "resolved_path": None,
                    "exists": False,
                    "error": str(exc),
                }
            )
            return

        for ref_name, ref_path in schema_data.get("schema_references", {}).items():
            candidates = [
                (main_schema.parent / ref_path).resolve(),
                (self.base_path / ref_path).resolve(),
                (self.base_path / ref_path.replace("../", "")).resolve(),
            ]
            resolved_path = next((path for path in candidates if path.is_file()), candidates[0])
            results["schema_refs"].append(
                {
                    "source": str(main_schema),
                    "reference": ref_name,
                    "configured_path": ref_path,
                    "resolved_path": str(resolved_path),
                    "exists": resolved_path.is_file(),
                }
            )

    def validate(self) -> Dict[str, Any]:
        results: Dict[str, Any] = {
            "base_path": str(self.base_path),
            "schema_path": str(self.schema_path),
            "folders": [],
            "root_files": [],
            "schema_files": [],
            "workflow_files": [],
            "tool_files": [],
            "environment": [],
            "schema_refs": [],
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

        if self._rule_enabled("check_schema_refs"):
            self._validate_schema_references(results)

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

        for item in results.get("schema_refs", []):
            if not item.get("exists", False):
                return False

        return True

    def format_report(self, results: Dict[str, Any]) -> str:
        lines: List[str] = []
        lines.append("PROJECT SETUP VALIDATION")
        lines.append("=" * 72)
        lines.append(f"Base Path: {results['base_path']}")
        lines.append(f"Schema Path: {results['schema_path']}")

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
                lines.append(f"  [{status}] {item['name'] if 'name' in item else Path(item['path']).name} ({required_text}) -> {item['path']}")

        if results.get("schema_refs"):
            lines.append("")
            lines.append("Schema References:")
            for item in results["schema_refs"]:
                label = item.get("reference") or "schema_reference_check"
                status = "OK" if item["exists"] else "MISS"
                target = item.get("resolved_path") or item.get("error") or "unresolved"
                lines.append(f"  [{status}] {label} -> {target}")

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

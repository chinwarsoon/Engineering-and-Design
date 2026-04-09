"""
Report formatting for project setup validation results.
Extracted from project_setup_validation.py format_report method.
"""

from pathlib import Path
from typing import Dict, Any, List


def format_report(results: Dict[str, Any]) -> str:
    """
    Format validation results for terminal output.

    Generates a human-readable report showing the validation status of all
    project components including folders, files, environment settings, and
    dependencies. Shows [OK], [MISS], or [WARN] indicators for each item.

    Args:
        results: Validation results dictionary containing:
            - base_path: Project root directory path
            - schema_path: Path to project_setup.json
            - os: OS detection info with 'system' and 'normalized'
            - folders: List of folder validation results
            - root_files: List of root file validation results
            - schema_files: List of schema file validation results
            - workflow_files: List of workflow file validation results
            - tool_files: List of tool file validation results
            - environment: List of environment file validation results
            - errors: List of error messages
            - ready: Boolean indicating if all required items exist

    Returns:
        Formatted multi-line string suitable for terminal display.

    Breadcrumb Comments:
        - results: Initialized in ProjectSetupValidator.validate().
                   Modified by validate_folders(), validate_named_files(),
                   validate_environment(), check_ready().
                   Consumed here to generate human-readable report.
        - Each section (folders, root_files, etc.): Extracted from results
                  and formatted with status symbols [OK], [MISS], [WARN].
    """
    lines: List[str] = []
    lines.append("=" * 72)
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

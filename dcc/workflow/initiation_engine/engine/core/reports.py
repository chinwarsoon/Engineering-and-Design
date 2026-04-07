"""
Report formatting for project setup validation results.
Extracted from project_setup_validation.py format_report method.
"""

from pathlib import Path
from typing import Dict, Any, List


def format_report(results: Dict[str, Any]) -> str:
    """Format validation results for terminal output."""
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

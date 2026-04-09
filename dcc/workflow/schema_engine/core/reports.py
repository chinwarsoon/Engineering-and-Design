"""
Report formatting utilities for schema validation.
Extracted from schema_validation.py format_report function.
"""

from typing import Dict, Any, List


def format_report(results: Dict[str, Any]) -> str:
    """Format schema validation results for terminal output."""
    lines: List[str] = []
    lines.append("SCHEMA VALIDATION")
    lines.append("=" * 72)
    lines.append(f"Main Schema: {results['main_schema_path']}")

    if results.get("references"):
        lines.append("")
        lines.append("Schema References:")
        for item in results["references"]:
            status = "OK" if item.get("exists") else "MISS"
            label = item.get("reference") or "schema_reference"
            target = item.get("resolved_path") or item.get("error") or "unresolved"
            lines.append(f"  [{status}] {label} -> {target}")

    if results.get("dependency_cycle"):
        lines.append("")
        lines.append("Dependency Cycle:")
        lines.append(f"  {' -> '.join(results['dependency_cycle'])}")

    if results.get("errors"):
        lines.append("")
        lines.append("Errors:")
        for error in results["errors"]:
            lines.append(f"  - {error}")

    lines.append("")
    lines.append("Summary:")
    lines.append(f"  Ready: {'YES' if results.get('ready') else 'NO'}")
    return "\n".join(lines)

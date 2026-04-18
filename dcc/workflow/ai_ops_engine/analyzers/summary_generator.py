"""
AI Ops Engine — Summary Generator

Produces structured executive summaries and markdown reports
from AiInsight objects.
Breadcrumb: AiInsight → markdown string + JSON summary
"""

from __future__ import annotations
import json
import logging
from datetime import datetime
from pathlib import Path

from ..core.contracts import AiInsight

logger = logging.getLogger(__name__)


class SummaryGenerator:
    """
    Generates human-readable and machine-readable summaries from AiInsight.
    """

    def generate_markdown_report(self, insight: AiInsight, output_path: Path) -> Path:
        """
        Write a markdown insight report to disk.

        Args:
            insight: Populated AiInsight
            output_path: Target .md file path

        Returns:
            Path to written file
        """
        lines = [
            f"# AI Insight Report",
            f"",
            f"**Run ID:** {insight.run_id}  ",
            f"**Generated:** {insight.timestamp}  ",
            f"**Provider:** {insight.provider} (`{insight.model_used}`)  ",
            f"**Fallback Used:** {'Yes' if insight.fallback_used else 'No'}  ",
            f"",
            f"---",
            f"",
            f"## Overall Risk: {insight.risk_level}",
            f"",
            f"{insight.executive_summary}",
            f"",
            f"---",
            f"",
            f"## Top Risks",
            f"",
        ]

        for i, risk in enumerate(insight.top_risks, 1):
            lines += [
                f"### {i}. {risk.title} — {risk.severity}",
                f"",
                f"{risk.description}",
                f"",
                f"- **Affected rows:** {risk.affected_rows:,}",
                f"- **Error codes:** {', '.join(risk.error_codes) or 'N/A'}",
                f"- **Columns:** {', '.join(risk.columns) or 'N/A'}",
                f"- **Recommendation:** {risk.recommendation}",
                f"",
            ]

        lines += ["---", "", "## Trends", ""]
        for trend in insight.trends:
            lines.append(f"- **{trend.pattern}** (frequency: {trend.frequency:,})")
        if not insight.trends:
            lines.append("No significant trends detected.")

        lines += ["", "---", "", "## Recommendations", ""]
        for i, rec in enumerate(insight.recommendations, 1):
            lines.append(f"{i}. {rec}")

        lines += ["", "---", "", "## Evidence Links", ""]
        for link in insight.evidence_links[:10]:
            lines.append(
                f"- `{link.get('error_code','?')}` → Phase {link.get('phase','?')}, "
                f"{link.get('total_occurrences',0):,} occurrences"
            )
        if not insight.evidence_links:
            lines.append("No evidence links attached.")

        output_path.write_text("\n".join(lines), encoding="utf-8")
        logger.info(f"[summary_generator] Markdown report written: {output_path}")
        return output_path

    def generate_json_summary(self, insight: AiInsight, output_path: Path) -> Path:
        """
        Write structured JSON insight summary to disk.

        Args:
            insight: Populated AiInsight
            output_path: Target .json file path

        Returns:
            Path to written file
        """
        data = insight.to_dict()
        output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        logger.info(f"[summary_generator] JSON summary written: {output_path}")
        return output_path

    def generate_trace(self, insight: AiInsight, output_path: Path) -> Path:
        """
        Write evidence traceability map to disk.

        Args:
            insight: Populated AiInsight
            output_path: Target .json file path

        Returns:
            Path to written file
        """
        trace = {
            "run_id": insight.run_id,
            "generated_at": datetime.now().isoformat(),
            "evidence_count": len(insight.evidence_links),
            "evidence": insight.evidence_links,
        }
        output_path.write_text(json.dumps(trace, indent=2), encoding="utf-8")
        logger.info(f"[summary_generator] Trace written: {output_path}")
        return output_path

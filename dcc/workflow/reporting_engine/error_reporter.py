"""
Error Reporter Module

Generates specialized diagnostic reports and health summaries for the DCC pipeline.
Supports Excel/CSV export of error details and taxonomy-based analysis.
"""

import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from processor_engine.error_handling.aggregator import ErrorAggregator
from .data_health import HealthCalculator

class ErrorReporter:
    """
    Generates detailed error reports based on aggregated detection results.
    """
    
    def __init__(
        self, 
        aggregator: ErrorAggregator, 
        output_dir: Optional[Path] = None,
        effective_parameters: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize with an aggregator instance.
        
        Args:
            aggregator: ErrorAggregator instance
            output_dir: Output directory path
            effective_parameters: Optional dict with schema-driven filename configuration
        """
        self.aggregator = aggregator
        self.output_dir = output_dir or Path("output")
        self.effective_parameters = effective_parameters or {}
        
    def generate_summary_stats(self, total_rows: int) -> Dict[str, Any]:
        """
        Generate overall error statistics and Health KPIs.
        """
        # Sync with early-stage errors before calculating stats
        self.aggregator.sync_with_initiation_logging()
        
        errors = self.aggregator.get_all_errors()
        kpi = HealthCalculator.get_kpi(total_rows, errors)
        
        row_errors = self.aggregator.aggregate_row_errors()
        
        return {
            "health_kpi": kpi.to_dict(),
            "total_errors": len(errors),
            "unique_errors": len(self.aggregator.deduplicate_errors()),
            "affected_rows": len(row_errors),
            "clean_run": kpi.health_score == 100.0,
            "error_density": round(len(errors) / total_rows, 3) if total_rows > 0 else 0,
            "status": "PASS" if kpi.health_score >= 90.0 else "FAIL" if kpi.health_score < 60.0 else "WARNING"
        }
        
    def generate_diagnostic_summary(self) -> str:
        """
        Generates a human-readable text summary of all errors.
        """
        unique_errors = self.aggregator.deduplicate_errors()
        if not unique_errors:
            return "CHECK PASSED: No errors detected."
            
        lines = ["DIAGNOSTIC SUMMARY:"]
        lines.append("-" * 30)
        
        # Group by Error Code
        stats = {}
        for e in unique_errors:
            stats[e.error_code] = stats.get(e.error_code, 0) + 1
            
        for code, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"[{code}] : {count} occurrences")
            
        return "\n".join(lines)
        
    def generate_phase_breakdown(self) -> pd.DataFrame:
        """
        Generate a DataFrame showing error distribution across phases.
        """
        phase_errors = self.aggregator.aggregate_phase_errors()
        report_data = []
        
        for phase, errors in phase_errors.items():
            report_data.append({
                "Phase": phase,
                "Total": len(errors),
                "Critical": len([e for e in errors if e.severity == "CRITICAL"]),
                "High": len([e for e in errors if e.severity == "HIGH"]),
                "Medium": len([e for e in errors if e.severity == "MEDIUM"]),
                "Warning/Info": len([e for e in errors if e.severity in ["WARNING", "INFO"]])
            })
            
        return pd.DataFrame(report_data)
        
    def export_full_diagnostic_log(self, filename: str = "error_diagnostic_log.csv") -> Path:
        """
        Exports a detailed, per-instance error log to CSV for external analysis.
        """
        all_errors = self.aggregator.get_all_errors()
        export_data = []
        
        for e in all_errors:
            export_data.append({
                "timestamp": e.detected_at.isoformat(),
                "row": e.row + 1 if e.row is not None else "N/A",
                "column": e.column or "N/A",
                "code": e.error_code,
                "severity": e.severity,
                "message": e.message,
                "layer": e.layer,
                "phase": e.context.get("phase", "Unknown"),
                "value": str(e.context.get("value", "null"))
            })
            
        df = pd.DataFrame(export_data)
        
        output_path = self.output_dir / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        
        return output_path

    def export_dashboard_json(
        self, 
        total_rows: int, 
        filename: Optional[str] = None,
    ) -> Path:
        """
        Exports a rich JSON object containing all telemetry for the UI dashboard.
        
        Uses schema-driven filename from effective_parameters if available.
        
        Args:
            total_rows: Total number of rows processed
            filename: Optional override filename (uses schema default if not provided)
            
        Returns:
            Path to exported JSON file
        """
        # Use schema-driven filename with fallback to default
        if filename is None:
            filename = self.effective_parameters.get(
                "error_dashboard_filename", 
                "error_dashboard_data.json"
            )
        stats = self.generate_summary_stats(total_rows)
        unique_errors = self.aggregator.deduplicate_errors()
        phase_breakdown = self.generate_phase_breakdown().to_dict(orient="records")
        
        # Aggregate errors by column for column-health analysis
        column_stats = {}
        for e in self.aggregator.get_all_errors():
            if e.column:
                column_stats[e.column] = column_stats.get(e.column, 0) + 1
        
        dashboard_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_rows": total_rows,
                "dataset_name": "DCC Processing Report"
            },
            "summary": stats,
            "phase_breakdown": phase_breakdown,
            "column_health": [
                {"column": col, "error_count": count} 
                for col, count in sorted(column_stats.items(), key=lambda x: x[1], reverse=True)
            ],
            "error_types": [
                {
                    "code": code,
                    "count": len([e for e in unique_errors if e.error_code == code]),
                    "severity": next((e.severity for e in unique_errors if e.error_code == code), "INFO")
                }
                for code in sorted(list(set(e.error_code for e in unique_errors)))
            ],
            "recent_errors": [
                {
                    "row": e.row + 1 if e.row is not None else "Global",
                    "column": e.column,
                    "code": e.error_code,
                    "message": e.message,
                    "severity": e.severity
                }
                for e in unique_errors[:50] # Top 50 unique instances
            ]
        }
        
        output_path = self.output_dir / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        import json
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(dashboard_data, f, indent=2)
            
        return output_path

"""
Data Health KPI Module

Calculates data health scores and grades based on detected errors per row and per dataset.
"""

import pandas as pd
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class DataHealthKPI:
    """
    Structured Data Health KPI result.
    """
    total_rows: int
    critical_errors: int
    high_errors: int
    health_score: float  # 0-100%
    grade: str           # A+/A/B/C/D/F
    trend: str = "→"     # ↑ → ↓
    detailed_counts: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API/JSON output."""
        return {
            "score": self.health_score,
            "grade": self.grade,
            "trend": self.trend,
            "total_rows": self.total_rows,
            "critical_errors": self.critical_errors,
            "high_errors": self.high_errors,
            "detailed_counts": self.detailed_counts,
            "summary": f"{self.health_score:.1f}% ({self.grade}) - "
                       f"{self.critical_errors} critical, "
                       f"{self.high_errors} high errors"
        }

class HealthCalculator:
    """
    Orchestrator for calculating health metrics.
    """
    
    @staticmethod
    def calculate_dataset_score(total_rows: int, critical_errors: int, high_errors: int) -> float:
        """
        Calculates dataset-level health score.
        Formula: (TotalRows - Critical - High) / TotalRows * 100
        """
        if total_rows == 0:
            return 100.0
        
        # Deductions are weighted toward critical/high errors
        # In this implementation, each critical/high error affects one 'healthy' row
        deductions = critical_errors + high_errors
        score = max(0.0, (total_rows - deductions) / total_rows * 100.0)
        return round(score, 2)
        
    @staticmethod
    def get_grade(score: float) -> str:
        """
        Converts score to a letter grade based on industry standards.
        """
        if score >= 99.0: return "A+"
        if score >= 95.0: return "A"
        if score >= 90.0: return "A-"
        if score >= 85.0: return "B+"
        if score >= 80.0: return "B"
        if score >= 70.0: return "C"
        if score >= 60.0: return "D"
        return "F"
        
    @classmethod
    def get_kpi(cls, total_rows: int, errors: List[Any]) -> DataHealthKPI:
        """
        Calculate full KPI from a list of DetectionResult objects.
        """
        critical_count = len([e for e in errors if e.severity == "CRITICAL"])
        high_count = len([e for e in errors if e.severity == "HIGH"])
        
        detailed_counts = {
            "CRITICAL": critical_count,
            "HIGH": high_count,
            "MEDIUM": len([e for e in errors if e.severity == "MEDIUM"]),
            "WARNING": len([e for e in errors if e.severity == "WARNING"]),
            "INFO": len([e for e in errors if e.severity == "INFO"])
        }
        
        score = cls.calculate_dataset_score(total_rows, critical_count, high_count)
        grade = cls.get_grade(score)
        
        return DataHealthKPI(
            total_rows=total_rows,
            critical_errors=critical_count,
            high_errors=high_count,
            health_score=score,
            grade=grade,
            detailed_counts=detailed_counts
        )

def calculate_row_health_series(df: pd.DataFrame, error_aggregator: Any) -> pd.Series:
    """
    Calculates a health score series for each row (0-100).
    Adds to the 'Data_Health_Score' column.
    """
    num_rows = len(df)
    row_errors = error_aggregator.aggregate_row_errors()
    scores = []
    
    for i in range(num_rows):
        if i in row_errors:
            errors = row_errors[i]
            has_critical = any(e.severity == "CRITICAL" for e in errors)
            if has_critical:
                scores.append(0.0)
            else:
                # Deduction-based scoring for non-critical errors
                high_count = len([e for e in errors if e.severity == "HIGH"])
                other_count = len([e for e in errors if e.severity in ["MEDIUM", "WARNING", "INFO"]])
                
                # Each high error deducts 20%, others deduct 5%
                deduction = (high_count * 20.0) + (other_count * 5.0)
                scores.append(max(0.0, 100.0 - deduction))
        else:
            scores.append(100.0)
            
    return pd.Series(scores, index=df.index)

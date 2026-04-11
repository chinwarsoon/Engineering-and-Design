"""
Business Logic Detector Orchestrator (Layer 3)

Coordinates all business logic detectors across P1, P2, P2.5, and P3 phases.
Manages phase transitions, collects and routes errors.

This module serves as the main entry point for business logic validation,
integrating anchor, identity, logic, fill, and validation detectors.
"""

import pandas as pd
from typing import Dict, Any, List, Optional, Callable, Type
from enum import Enum

from .base import BaseDetector, DetectionResult, CompositeDetector, FailFastError
from .anchor import AnchorDetector
from .identity import IdentityDetector


class ProcessingPhase(Enum):
    """Processing phases for column calculation."""
    P1 = "P1"      # Anchor columns (Project, Facility, Type, Session)
    P2 = "P2"      # Identity columns (Document_ID, Revision)
    P2_5 = "P2.5"  # Cross-references (Reviewer, Department)
    P3 = "P3"      # Derived values (Dates, Status, Aggregations)


class BusinessDetector(BaseDetector):
    """
    Orchestrator for all business logic detectors.
    
    Manages:
    - Phase-based detection (P1 → P2 → P2.5 → P3)
    - Detector registration and execution
    - Error aggregation across phases
    - Fail-fast coordination
    """
    
    def __init__(
        self,
        logger=None,
        enable_fail_fast: bool = True,
        phases: Optional[List[ProcessingPhase]] = None
    ):
        """
        Initialize business detector orchestrator.
        
        Args:
            logger: StructuredLogger instance
            enable_fail_fast: Whether to stop on critical errors
            phases: Phases to run (default: all phases)
        """
        super().__init__(
            layer="L3",
            logger=logger,
            enable_fail_fast=enable_fail_fast
        )
        
        self.phases = phases or list(ProcessingPhase)
        self._phase_detectors: Dict[ProcessingPhase, List[BaseDetector]] = {
            phase: [] for phase in ProcessingPhase
        }
        self._phase_errors: Dict[ProcessingPhase, List[DetectionResult]] = {
            phase: [] for phase in ProcessingPhase
        }
        
        # Initialize default detectors
        self._init_default_detectors()
    
    def _init_default_detectors(self) -> None:
        """Initialize default detectors for each phase."""
        # P1: Anchor detector
        self.register_phase_detector(
            ProcessingPhase.P1,
            AnchorDetector(
                logger=self._logger,
                enable_fail_fast=self._enable_fail_fast
            )
        )
        
        # P2: Identity detector
        self.register_phase_detector(
            ProcessingPhase.P2,
            IdentityDetector(
                logger=self._logger,
                enable_fail_fast=self._enable_fail_fast
            )
        )
    
    def register_phase_detector(
        self,
        phase: ProcessingPhase,
        detector: BaseDetector
    ) -> None:
        """
        Register a detector for a specific phase.
        
        Args:
            phase: Processing phase
            detector: Detector instance
        """
        self._phase_detectors[phase].append(detector)
        
        if self._logger:
            self._logger.debug(
                f"Registered {detector.__class__.__name__} for phase {phase.value}"
            )
    
    def detect(
        self,
        df: pd.DataFrame,
        context: Optional[Dict[str, Any]] = None,
        stop_on_first_error: bool = False
    ) -> Dict[ProcessingPhase, List[DetectionResult]]:
        """
        Run all business logic validations across all phases.
        
        Args:
            df: DataFrame to validate
            context: Additional context
            stop_on_first_error: Stop after first error found
            
        Returns:
            Dict of phase -> list of detection results
        """
        self.clear_errors()
        self._phase_errors = {phase: [] for phase in ProcessingPhase}
        
        if context:
            self.set_context(**context)
        
        # Run phases in order
        for phase in self.phases:
            try:
                phase_errors = self._run_phase(phase, df, context)
                self._phase_errors[phase] = phase_errors
                
                # Check for fail-fast errors
                if self._enable_fail_fast:
                    critical_errors = [
                        e for e in phase_errors 
                        if e.severity == "CRITICAL" or e.fail_fast
                    ]
                    if critical_errors:
                        raise FailFastError(
                            critical_errors[0],
                            f"Critical error in phase {phase.value}"
                        )
                
                # Stop on first error if requested
                if stop_on_first_error and phase_errors:
                    break
                    
            except FailFastError:
                raise
            except Exception as e:
                if self._logger:
                    self._logger.error(
                        f"Error in phase {phase.value}: {str(e)}",
                        exc_info=True
                    )
                raise
        
        # Aggregate all errors
        all_errors = []
        for phase_errors in self._phase_errors.values():
            all_errors.extend(phase_errors)
        
        self._errors = all_errors
        return self._phase_errors
    
    def _run_phase(
        self,
        phase: ProcessingPhase,
        df: pd.DataFrame,
        context: Optional[Dict[str, Any]]
    ) -> List[DetectionResult]:
        """
        Run all detectors for a specific phase.
        
        Args:
            phase: Processing phase
            df: DataFrame to validate
            context: Additional context
            
        Returns:
            List of detection results for the phase
        """
        phase_errors = []
        detectors = self._phase_detectors.get(phase, [])
        
        if not detectors:
            if self._logger:
                self._logger.warning(f"No detectors registered for phase {phase.value}")
            return phase_errors
        
        if self._logger:
            self._logger.info(f"Running phase {phase.value} with {len(detectors)} detector(s)")
        
        for detector in detectors:
            try:
                errors = detector.detect(df, context)
                phase_errors.extend(errors)
                
                if self._logger:
                    self._logger.debug(
                        f"{detector.__class__.__name__} found {len(errors)} errors"
                    )
                    
            except FailFastError:
                raise
            except Exception as e:
                if self._logger:
                    self._logger.error(
                        f"Detector {detector.__class__.__name__} failed: {str(e)}",
                        exc_info=True
                    )
                raise
        
        if self._logger:
            self._logger.info(
                f"Phase {phase.value} complete: {len(phase_errors)} errors found"
            )
        
        return phase_errors
    
    def get_phase_errors(
        self,
        phase: ProcessingPhase
    ) -> List[DetectionResult]:
        """
        Get errors for a specific phase.
        
        Args:
            phase: Processing phase
            
        Returns:
            List of detection results
        """
        return self._phase_errors.get(phase, [])
    
    def get_errors_by_severity(
        self,
        severity: str
    ) -> List[DetectionResult]:
        """
        Get all errors of a specific severity across all phases.
        
        Args:
            severity: Severity level (CRITICAL, HIGH, MEDIUM, WARNING, INFO)
            
        Returns:
            List of matching detection results
        """
        all_errors = []
        for phase_errors in self._phase_errors.values():
            all_errors.extend([
                e for e in phase_errors 
                if e.severity == severity
            ])
        return all_errors
    
    def has_critical_errors(self) -> bool:
        """
        Check if any critical errors exist.
        
        Returns:
            True if critical errors found
        """
        return len(self.get_errors_by_severity("CRITICAL")) > 0
    
    def get_phase_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics for all phases.
        
        Returns:
            Summary dictionary
        """
        summary = {
            "phases_run": len(self.phases),
            "total_errors": 0,
            "errors_by_phase": {},
            "errors_by_severity": {
                "CRITICAL": 0,
                "HIGH": 0,
                "MEDIUM": 0,
                "WARNING": 0,
                "INFO": 0
            }
        }
        
        for phase, errors in self._phase_errors.items():
            error_count = len(errors)
            summary["errors_by_phase"][phase.value] = error_count
            summary["total_errors"] += error_count
            
            for error in errors:
                sev = error.severity
                if sev in summary["errors_by_severity"]:
                    summary["errors_by_severity"][sev] += 1
        
        return summary
    
    def validate_phase_transition(
        self,
        from_phase: ProcessingPhase,
        to_phase: ProcessingPhase
    ) -> bool:
        """
        Validate if phase transition is allowed.
        
        Args:
            from_phase: Source phase
            to_phase: Target phase
            
        Returns:
            True if transition is valid
        """
        # Define valid transitions
        valid_transitions = {
            ProcessingPhase.P1: [ProcessingPhase.P2],
            ProcessingPhase.P2: [ProcessingPhase.P2_5, ProcessingPhase.P3],
            ProcessingPhase.P2_5: [ProcessingPhase.P3],
            ProcessingPhase.P3: []
        }
        
        return to_phase in valid_transitions.get(from_phase, [])
    
    def can_proceed_to_phase(
        self,
        phase: ProcessingPhase
    ) -> bool:
        """
        Check if processing can proceed to a phase.
        
        Args:
            phase: Target phase
            
        Returns:
            True if no blocking errors in previous phases
        """
        # Get phases that must complete before target
        phase_order = list(ProcessingPhase)
        target_idx = phase_order.index(phase)
        
        # Check all previous phases for critical errors
        for prev_phase in phase_order[:target_idx]:
            errors = self._phase_errors.get(prev_phase, [])
            critical_count = len([e for e in errors if e.severity == "CRITICAL"])
            if critical_count > 0:
                return False
        
        return True


def create_business_detector(
    phases: Optional[List[str]] = None,
    enable_fail_fast: bool = True,
    logger=None
) -> BusinessDetector:
    """
    Factory function to create a business detector.
    
    Args:
        phases: List of phase names (e.g., ["P1", "P2"])
        enable_fail_fast: Whether to stop on critical errors
        logger: StructuredLogger instance
        
    Returns:
        Configured BusinessDetector instance
    """
    phase_enums = None
    if phases:
        phase_enums = [ProcessingPhase(p) for p in phases if p in [p.value for p in ProcessingPhase]]
    
    return BusinessDetector(
        logger=logger,
        enable_fail_fast=enable_fail_fast,
        phases=phase_enums
    )

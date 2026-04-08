"""Reporting Engine Core Module.

Provides summary report generation for DCC pipeline processing.
"""

from .summary import write_processing_summary

__all__ = ["write_processing_summary"]

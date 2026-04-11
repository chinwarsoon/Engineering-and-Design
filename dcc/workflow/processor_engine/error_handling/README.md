# DCC Error Handling & Health Diagnostics Module

This module provides a robust, 6-layer validation and error-tracking engine for the DCC processing pipeline.

## Features
- **Phased Detection**: Categorizes errors into P1 (Anchor), P2 (Identity), P2.5 (Anomaly), and P3 (Calculation).
- **Multi-Layer Validation**:
    - **L1/L2**: Input and Schema validation.
    - **L3**: Business logic validation.
    - **L4**: Approval/Manual override integration.
    - **L5**: Data Health KPI and Diagnostic reporting.
- **Fail-Fast**: Immediately halts processing on critical anchor errors to prevent data corruption.
- **Data Health KPI**: Calculates a weighted health score (0-100%) and letter grade (A-F) for the dataset.
- **Structured Logging**: Generates E-M-F-U coded JSON logs for machine-readability.
- **UI Dashboards**: Interactive tools for visualizing data health and exploring diagnostic logs.

## Architecture
- **Pure JSON Configuration**: All error codes, taxonomy, and localization are defined in `config/`.
- **Aggregator Pattern**: Centralized collection of all row-level errors.
- **Reporter Engine**: Generates human-readable `summary.txt` and machine-readable `dashboard_data.json`.

## Core Components
- `aggregator.py`: Collects and deduplicates errors.
- `detectors/`: Contains validation logic for each phase.
- `reporting_engine/data_health.py`: KPI calculation engine.
- `reporting_engine/error_reporter.py`: Telemetry exporter.

## Usage
The error handling system is automatically triggered during the `CalculationEngine.process_data()` call. It populates two specific columns in the output:
1. `Validation_Errors`: Comma-separated list of error codes (e.g., `P-C-P-0101`).
2. `Data_Health_Score`: Row-level data quality percentage.

## Diagnostic Tools
Located in `dcc/ui/`:
- `error_diagnostic_dashboard.html`: High-level health visualization.
- `log_explorer_pro.html`: Detailed log filtering and inspection.

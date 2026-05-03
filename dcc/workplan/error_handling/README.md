# DCC Error Handling — Workplans and Implementation Summary

**Last Updated:** 2026-05-03  
**Purpose:** Landing page for what’s implemented, key achievements, timelines, and links to the detailed workplans + phase reports.

---

## Folder Structure (this directory)

Each workplan lives in its own subfolder:
- `*/<workplan-title>.md`: the workplan document
- `*/reports/`: phase reports and completion reports
- `dcc/archive/workplan/error_handling/archive/`: archived phase artifacts (Phase 1–4) (not used anymore)

Shared reference docs remain at the top level (e.g., `error_handling_taxonomy.md`).

---

## Quick Links (by workplan)

- **Bootstrap error code standardization (in progress)**: `bootstrap_error_standardization/bootstrap_error_standardization_workplan.md`
  - Standardizes bootstrap B-XXXX-NNN codes and E-SCH-CATALOG-LOAD to S-C-S-XXXX format
  - Loads all error messages from schema (no hardcoding)
- **Error handling integration with `PipelineContext` (planned)**: `integration/error_handling_integration_workplan.md`
- **Processor data error handling module (implemented / wrapped up)**: `module/error_handling_module_workplan.md`
  - Report: `module/reports/resolution_module_implementation_report.md`
- **System error handling (implemented)**: `system_error_handling/system_error_handling_workplan.md`
  - Report: `system_error_handling/reports/system_error_handling_completion_report.md`
- **Data error handling (reference / implemented in processor subsystem)**: `data_error_handling/data_error_handling_workplan.md`
- **Pipeline messaging (implemented)**: `pipeline_messaging/pipeline_messaging_plan.md`
  - Report: `pipeline_messaging/reports/pipeline_messaging_plan_report.md`
- **Error catalog consolidation + standardization (implemented; Phase artifacts archived)**: `error_catalog_consolidation/error_catalog_consolidation_plan.md`
  - Reports:
    - `error_catalog_consolidation/reports/consolidated_implementation_report.md`
    - `error_catalog_consolidation/reports/phase4_consolidation_test_report.md`
  - Archive (Phase 1–4): `dcc/archive/workplan/error_handling/archive/`

Reference:
- **Error Handling Taxonomy (codes, ranges, naming rules)**: `error_handling_taxonomy.md`

---

## Object (high-level)

Provide a consistent, user-visible and machine-consumable error handling system for the DCC pipeline:
- **System-status errors**: environment, filesystem, configuration, runtime/orchestration failures (pipeline may not be able to run).
- **Data-handling errors**: validation and business-rule detection issues during processing (pipeline runs, output contains data health diagnostics).
- **Outputs**: readable CLI errors, structured dashboard artifacts, and stable contracts for reporting/AI/UI.

---

## What’s Implemented (high-signal achievements)

- **Standardized error code taxonomy and catalogs**
  - System codes (e.g., `S-E-S`, `S-F-S`, `S-C-S`, `S-R-S`, `S-A-S`)
  - Data/logic codes for phased detection and validation layers
  - Localization support (EN/ZH) where applicable

- **Processor data error handling module (AOP-style / interceptor pattern)**
  - Phased detection (P1 → P2 → P2.5 → P3 → validation)
  - Aggregation to `Validation_Errors` and data health KPI/dashboard exports
  - Resolution module framework (with minimal implementation where documented)

- **System error printing for always-visible failures**
  - Clear, code-driven fatal vs non-fatal output for runtime and environment issues

- **Pipeline messaging + reporting artifacts**
  - Standard messaging plan and report artifacts for consistent operator experience

- **Context integration (next step / planned)**
  - Workplan exists to integrate system-status errors and fail-fast policy into `PipelineContext` (without losing CLI visibility)

---

## Timelines (milestones)

- **2026-04-12**: Data error handling module workplan status marked core operational (`module/error_handling_module_workplan.md`)
- **2026-04-17 → 2026-04-25**: Messaging, system error handling completion report, consolidation reports produced (see links above)
- **2026-04-29**: Integration workplan updated to align with WP-PIPE-ARCH-001 and to explicitly separate system-status vs data-handling errors in `PipelineContext` (`integration/error_handling_integration_workplan.md`)
- **2026-05-03**: Bootstrap error standardization workplan created to address non-compliant B-XXXX-NNN codes and schema-based message loading (`bootstrap_error_standardization/bootstrap_error_standardization_workplan.md`)

---

## Scope Summary (this folder)

This folder’s workplans collectively cover:
- **Error code definition + consolidation** (catalogs, schema structure, archive artifacts)
- **System-status failure reporting** (CLI-facing, always visible)
- **Data-handling/validation error detection** (processor subsystem: detectors/aggregator/reporter)
- **Messaging and reporting contracts**
- **Planned**: end-to-end integration of error handling into `PipelineContext` (system-status recording + policy-driven fail-fast)

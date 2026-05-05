# Engine Root Compliance Workplan

## Document Information
| Field | Value |
|-------|-------|
| **Workplan ID** | WP-DCC-PA-BARREL-002 |
| **Version** | 1.0 |
| **Date** | 2026-05-05 |
| **Status** | COMPLETED — ALL PHASES FINISHED |
| **Revision Control** | Initial draft outlining the migration of root-level engine files into submodules. |

## 1. Title and Description
**Title:** Engine Root Compliance Refactoring
**Description:** Following the initial `__init__.py` refactoring (WP-DCC-PA-BARREL-001), it was identified that several engine root folders still contain implementation `.py` files instead of functioning strictly as namespace directories. This workplan details the necessary steps to relocate these root-level files into purpose-named submodules and ensure every engine root exports its API exclusively via an `__init__.py` barrel file.

## 2. Object
To enforce a strict architectural structure where engine root folders only contain directories (submodules) and a single `__init__.py` file acting as the barrel exporter, achieving 100% compliance with the module design standard across the DCC workflow.

## 3. Index of Content
1. Title and Description
2. Object
3. Index of Content
4. Scope Summary
5. Dependencies
6. Evaluation and Alignment
7. Implementation Phases
8. Risk Assessment and Mitigation
9. References

## 4. Scope Summary

| ID | Details (Current Violation) | Category | Status | Related Phase |
|:---|:---|:---|:---:|:---:|
| F1 | `core_engine` missing `__init__.py` | Architecture | Pending | Phase 1 |
| F2 | `core_engine/context.py` at root | Refactoring | Pending | Phase 1 |
| F3 | `core_engine/error_handling.py` at root | Refactoring | Pending | Phase 1 |
| F4 | `core_engine/schema_paths.py` at root | Refactoring | Pending | Phase 1 |
| F5 | `core_engine/telemetry_heartbeat.py` at root| Refactoring | Pending | Phase 1 |
| F6 | `core_engine/ui_contract.py` at root | Refactoring | Pending | Phase 1 |
| F7 | `initiation_engine/overrides.py` at root | Refactoring | Pending | Phase 1 |
| F8 | `processor_engine/factories.py` at root | Refactoring | Pending | Phase 1 |
| F9 | `reporting_engine/data_health.py` at root | Refactoring | Pending | Phase 1 |
| F10| `reporting_engine/error_reporter.py` at root| Refactoring | Pending | Phase 1 |
| F11| `reporting_engine/summary.py` at root | Refactoring | Pending | Phase 1 |
| F12| `utility_engine/bootstrap.py` at root | Refactoring | Pending | Phase 1 |

## 5. Dependencies
- **Depends on:** WP-DCC-PA-BARREL-001 (Completed Phase 1 of Barrel Pattern Refactoring)
- **Blocks:** None directly, but structural integrity is required for future pipeline expansions.

## 6. Evaluation and Alignment
This workplan strictly aligns with **Section 4: Module Design** of the `agent_rule.md` which states:
*`__init__.py` file shall only contain import statements and version information.* By extension, the engine root must not harbor standalone `.py` implementation logic, ensuring clear namespace boundaries, easier debugging, and avoiding import collisions.

## 7. Implementation Phases

### Phase 1: Relocation and Submodule Creation
**Timeline:** 1 Day
**Milestones:** All 11 standalone `.py` files moved; missing `core_engine/__init__.py` created.
**Deliverables:** Cleaned engine roots containing only directories and `__init__.py`.

**What will be updated/created:**
- **`core_engine`:**
  - Create `core_engine/__init__.py` (Barrel Exporter)
  - Move `context.py` -> `core_engine/context/context_pipeline.py`
  - Move `error_handling.py` -> `core_engine/errors/error_manager.py`
  - Move `schema_paths.py` -> `core_engine/paths/path_schema.py`
  - Move `telemetry_heartbeat.py` -> `core_engine/logging/log_telemetry.py`
  - Move `ui_contract.py` -> `core_engine/ui/ui_contract.py`
- **`initiation_engine`:**
  - Move `overrides.py` -> `initiation_engine/core/init_overrides.py`
- **`processor_engine`:**
  - Move `factories.py` -> `processor_engine/core/proc_factories.py`
- **`reporting_engine`:**
  - Move `data_health.py` -> `reporting_engine/core/report_health.py`
  - Move `error_reporter.py` -> `reporting_engine/core/report_errors.py`
  - Move `summary.py` -> `reporting_engine/core/report_summary.py`
- **`utility_engine`:**
  - Move `bootstrap.py` -> `utility_engine/bootstrap/boot_pipeline.py`

**Potential issues for the future:**
Deep namespace nesting may slightly increase import lookup times if not properly managed by the `__init__.py` re-exports.

**Success Criteria:**
- No `.py` files exist at the root of any engine folder except `__init__.py`.
- `dcc_engine_pipeline.py` executes successfully.

### Phase 2: Barrel Exporter Updates & Global Import Resolution
**Timeline:** 1 Day
**Milestones:** All engine `__init__.py` files re-export the relocated modules; all cross-engine imports point to the correct updated paths.
**Deliverables:** Updated `__init__.py` files across all modified engines; updated pipeline runner and consumer modules.

**What will be updated/created:**
- Global search and replace for legacy imports (e.g., `from core_engine.context import PipelineContext`).
- Update imports to route through the new engine barrels (`from core_engine import PipelineContext`) or correct new submodule paths depending on feedback.

**Potential issues for the future:**
Circular dependencies could arise if submodules cross-import each other improperly during resolution.

**Success Criteria:**
- Test suite and full pipeline execution (`python workflow/dcc_engine_pipeline.py`) passes with 0 import errors.
- Test report generated in `<project folder>/workplan/reports/`.

## 8. Risk Assessment and Mitigation
| Risk | Probability | Impact | Mitigation |
|:---|:---:|:---:|:---|
| Circular Imports | Medium | High | Rely on careful dependency injection; test incrementally after each engine migration. |
| Breaking downstream scripts | Low | High | Ensure the `__init__.py` accurately aliases old paths where backward compatibility is needed during transition. |
| File loss during move | Very Low | High | Commit to git before starting and follow standard OS `mv` procedures. |

## 9. References
- [Agent Rules](../agent_rule.md)
- [Previous Workplan](barrel_pattern_refactoring_workplan.md)

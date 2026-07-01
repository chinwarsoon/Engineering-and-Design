# EKS Phase 1 — Appendix F Architecture Integration

**Document ID**: WP-EKS-P1-APPENDIX-F-001  
**Current Version**: 0.1  
**Status**: 🔷 PLANNED  
**Last Updated**: 2026-06-30  
**Parent Workplan**: [phase_1_foundation_workplan.md](phase_1_foundation_workplan.md)  
**Phase Dependency**: Phase 1 Foundation (T1.1-T1.51) complete

---

## 1. Title and Description

Integrate universal pipeline architecture patterns defined in Appendix F into Phase 1 foundation. This workplan implements the core architecture patterns (PipelineContext, Dependency Injection, Telemetry Heartbeat, Standardized Engine I/O, Phase-Based Orchestration, Project Setup Validation) to establish a robust, modular, and testable foundation for all subsequent phases.

---

## 2. Revision Control & Version History

| Version | Date       | Author | Summary of Changes                            |
| :------ | :--------- | :----- | :-------------------------------------------- |
| 0.1     | 2026-06-30 | System | Initial workplan draft for Appendix F architecture integration tasks T1.52-T1.66 |

---

## 3. Objective

- Implement EKSPipelineContext for centralized state management
- Create BaseEngine abstract class with standard execution flow
- Implement TelemetryHeartbeat for progress and performance monitoring
- Implement Multi-Stage Validation (setup, schema, data, parser)
- Define Standardized Engine I/O Contracts
- Implement CLI Entry Points for independent engine execution
- Implement HTTP API Endpoints for independent engine execution
- Implement Checkpoint State Serialization for resume capability
- Implement Factories (ParserFactory, HealthScorerFactory, StructureDetectorFactory)
- Update Engines to Use Factories
- Enhance PipelineOrchestrator with Checkpoints and Phase Rollback
- Implement Project Setup Validator

---

## 4. Scope Summary

| ID | Details | Category | Status | Related Phase |
| :- | :------ | :------- | :----: | :----------- |
| R1 | EKSPipelineContext implementation | Foundation | 🔷 PLANNED | Phase 1 |
| R2 | BaseEngine abstract class | Foundation | 🔷 PLANNED | Phase 1 |
| R3 | TelemetryHeartbeat implementation | Telemetry | 🔷 PLANNED | Phase 1 |
| R4 | Multi-Stage Validation | Validation | 🔷 PLANNED | Phase 1 |
| R5 | Standardized Engine I/O Contracts | I/O | 🔷 PLANNED | Phase 1 |
| R6 | CLI Entry Points | Execution | 🔷 PLANNED | Phase 1 |
| R7 | HTTP API Endpoints | Execution | 🔷 PLANNED | Phase 1 |
| R8 | Checkpoint State Serialization | State Management | 🔷 PLANNED | Phase 1 |
| R9 | Factories (Parser, HealthScorer, StructureDetector) | Dependency Injection | 🔷 PLANNED | Phase 1 |
| R10 | Update Engines to Use Factories | Dependency Injection | 🔷 PLANNED | Phase 1 |
| R11 | PipelineOrchestrator Enhancements | Orchestration | 🔷 PLANNED | Phase 1 |
| R12 | Project Setup Validator | Validation | 🔷 PLANNED | Phase 1 |

---

## 5. Index of Content

- [1. Title and Description](#1-title-and-description)
- [2. Revision Control & Version History](#2-revision-control--version-history)
- [3. Objective](#3-objective)
- [4. Scope Summary](#4-scope-summary)
- [5. Index of Content](#5-index-of-content)
- [6. Dependencies with Other Tasks](#6-dependencies-with-other-tasks)
- [7. Evaluation and Alignment with Existing Architecture](#7-evaluation-and-align-with-existing-architecture)
- [8. Implementation Phases](#8-implementation-phases)
  - [Phase 1: Foundation Layer (T1.52-T1.55)](#phase-1-foundation-layer-t152-t155)
  - [Phase 2: I/O and Execution Layer (T1.56-T1.58)](#phase-2-io-and-execution-layer-t156-t158)
  - [Phase 3: Dependency Injection Layer (T1.59-T1.62)](#phase-3-dependency-injection-layer-t159-t162)
  - [Phase 4: Orchestration and Validation Layer (T1.63-T1.66)](#phase-4-orchestration-and-validation-layer-t163-t166)
- [9. Risks and Mitigation](#9-risks-and-mitigation)
- [10. Potential Future Issues](#10-potential-future-issues)
- [11. Success Criteria](#11-success-criteria)
- [12. Deliverables](#12-deliverables)
- [13. References](#13-references)

---

## 6. Dependencies with Other Tasks

| Dependency | Type | Description |
| :--------- | :--- | :---------- |
| Phase 1 Foundation (T1.1-T1.51) | Prerequisite | All Phase 1 foundation tasks must be complete |
| Appendix F Architecture Design | Reference | Architecture patterns defined in [appendix_f_pipeline_architecture_design.md](appendix_f_pipeline_architecture_design.md) |
| Phase 2-5 Workplans | Downstream | These phases will reference Phase 1.2 completion for base patterns |

---

## 7. Evaluation and Alignment with Existing Architecture

**Alignment with Appendix F:**
- All tasks directly implement patterns defined in Appendix F Section 3
- Follows the 3-layer schema pattern (base/setup/config) established in Phase 1
- Extends existing Phase 1 modules (core, parsers, health scoring)
- Maintains backward compatibility with legacy mode

**Architecture Impact:**
- Introduces centralized state management via EKSPipelineContext
- Enables independent engine execution via CLI and HTTP endpoints
- Provides factory pattern for component creation (Dependency Injection)
- Adds telemetry heartbeat for progress tracking
- Implements checkpoint/rollback for fault tolerance

---

## 8. Implementation Phases

### Phase 1: Foundation Layer (T1.52-T1.55)

**Timeline**: 2-3 days  
**Milestones**: EKSPipelineContext, BaseEngine, TelemetryHeartbeat, Multi-Stage Validation implemented

**Task Breakdown:**

| # | Task | Details | Status |
| :- | :--- | :------ | :----: |
| T1.52 | Implement EKSPipelineContext | Create `eks/engine/core/context.py` with nested dataclasses for centralized state management (paths, data, parameters, state, telemetry, schema_registry) per Appendix F | 🔷 PLANNED |
| T1.53 | Implement BaseEngine abstract class | Create `eks/engine/core/base.py` with standard execution flow (validate → execute → validate) per Appendix F | 🔷 PLANNED |
| T1.54 | Implement TelemetryHeartbeat | Create `eks/engine/core/telemetry.py` for document processing checkpoints per Appendix F | 🔷 PLANNED |
| T1.55 | Implement Multi-Stage Validation | Create `eks/engine/core/validator.py` with setup, schema, data, parser validation stages per Appendix F | 🔷 PLANNED |

**What will be updated/created:**
- `eks/engine/core/context.py` — EKSPipelineContext implementation
- `eks/engine/core/base.py` — BaseEngine, BaseProcessor abstract classes
- `eks/engine/core/telemetry.py` — TelemetryHeartbeat implementation
- `eks/engine/core/validator.py` — Multi-stage validation logic

**Risks and Mitigation:**
- **Risk**: Breaking changes to existing Phase 1 modules
- **Mitigation**: Maintain backward compatibility with legacy mode; add opt-in flag for new architecture

**Potential Future Issues:**
- Telemetry overhead may impact performance in large-scale processing
- Validation stages may add latency to pipeline execution

**Success Criteria:**
- ✅ EKSPipelineContext implemented with all required fields
- ✅ Base classes defined with clear interfaces
- ✅ Telemetry heartbeat emits at document processing checkpoints
- ✅ Multi-stage validation (setup, schema, data, parser) functional

**References:**
- Appendix F Section 3.1: PipelineContext
- Appendix F Section 3.2: BaseEngine
- Appendix F Section 3.3: TelemetryHeartbeat
- Appendix F Section 3.4: Multi-Stage Validation

---

### Phase 2: I/O and Execution Layer (T1.56-T1.58)

**Timeline**: 2-3 days  
**Milestones**: Standardized I/O contracts, CLI entry points, HTTP API endpoints implemented

**Task Breakdown:**

| # | Task | Details | Status |
| :- | :--- | :------ | :----: |
| T1.56 | Implement CLI Entry Points | Create `eks/engine/*/cli.py` for independent engine execution via command line per Appendix F | 🔷 PLANNED |
| T1.57 | Implement HTTP API Endpoints | Create `eks/ui/backend/engine_endpoints.py` for independent engine execution via HTTP per Appendix F | 🔷 PLANNED |
| T1.58 | Implement Checkpoint State Serialization | Add checkpoint state serialization/deserialization for resume capability per Appendix F | 🔷 PLANNED |

**What will be updated/created:**
- `eks/engine/discovery/cli.py` — CLI entry point for discovery engine
- `eks/engine/parsers/cli.py` — CLI entry point for parser engine
- `eks/engine/health/cli.py` — CLI entry point for health scorer
- `eks/ui/backend/engine_endpoints.py` — HTTP API endpoints
- Checkpoint state serialization logic in context.py

**Risks and Mitigation:**
- **Risk**: CLI/API endpoints may expose sensitive data
- **Mitigation**: Implement authentication and authorization in Phase 5

**Potential Future Issues:**
- Checkpoint state size may grow large for long-running pipelines
- CLI argument parsing complexity may increase

**Success Criteria:**
- ✅ CLI entry points for independent engine execution
- ✅ HTTP API endpoints for independent engine execution
- ✅ Checkpoint state serialization/deserialization working

**References:**
- Appendix F Section 3.5: Standardized Engine I/O
- Appendix F Section 3.6: Independent Execution

---

### Phase 3: Dependency Injection Layer (T1.59-T1.62)

**Timeline**: 2-3 days  
**Milestones**: Factories implemented, engines refactored to use factories

**Task Breakdown:**

| # | Task | Details | Status |
| :- | :--- | :------ | :----: |
| T1.59 | Implement ParserFactory | Create `eks/engine/core/factories.py` with file type routing per Appendix F | 🔷 PLANNED |
| T1.60 | Implement HealthScorerFactory | Factory with config-driven dimensions per Appendix F | 🔷 PLANNED |
| T1.61 | Implement StructureDetectorFactory | Factory for structure detector instantiation per Appendix F | 🔷 PLANNED |
| T1.62 | Update Engines to Use Factories | Refactor existing engines to use factories instead of direct instantiation per Appendix F | 🔷 PLANNED |

**What will be updated/created:**
- `eks/engine/core/factories.py` — Factory implementations
- Refactored parser_router.py to use ParserFactory
- Refactored health_scorer.py to use HealthScorerFactory
- Refactored structure_detector.py to use StructureDetectorFactory

**Risks and Mitigation:**
- **Risk**: Factory refactoring may introduce bugs
- **Mitigation**: Comprehensive unit tests for all factory methods; maintain legacy mode

**Potential Future Issues:**
- Factory pattern may add complexity for simple use cases
- Config-driven instantiation may be difficult to debug

**Success Criteria:**
- ✅ ParserFactory routes to correct parser based on file type
- ✅ HealthScorerFactory loads dimensions from config registry
- ✅ StructureDetectorFactory instantiates correct detector
- ✅ All existing engines use factories
- ✅ Backward compatibility maintained (legacy mode works)

**References:**
- Appendix F Section 3.7: Dependency Injection

---

### Phase 4: Orchestration and Validation Layer (T1.63-T1.66)

**Timeline**: 2-3 days  
**Milestones**: PipelineOrchestrator enhanced with checkpoints, Project Setup Validator implemented

**Task Breakdown:**

| # | Task | Details | Status |
| :- | :--- | :------ | :----: |
| T1.63 | Enhance PipelineOrchestrator with Checkpoints | Add 5 clear phases (A-E) with telemetry heartbeat integration per Appendix F | 🔷 PLANNED |
| T1.64 | Implement Phase Rollback Capability | Add checkpoint restoration mechanism for failed phases per Appendix F | 🔷 PLANNED |
| T1.65 | Implement Project Setup Validator | Create `eks/engine/core/setup_validator.py` with auto-creation of missing folders per Appendix F | 🔷 PLANNED |
| T1.66 | Create Project Setup Schema | Create `eks/config/schemas/project_setup.json` for setup validation per Appendix F | 🔷 PLANNED |

**What will be updated/created:**
- `eks/engine/core/pipeline_orchestrator.py` — Enhanced with checkpoints and rollback
- `eks/engine/core/setup_validator.py` — Setup validator
- `eks/config/schemas/project_setup.json` — Setup schema

**Risks and Mitigation:**
- **Risk**: Rollback mechanism may not restore state correctly
- **Mitigation**: Comprehensive testing of rollback scenarios; maintain checkpoint logs

**Potential Future Issues:**
- Phase rollback may be complex for stateful operations
- Setup validation may be too strict for some environments

**Success Criteria:**
- ✅ PipelineOrchestrator has 5 clear phases (A-E)
- ✅ Telemetry heartbeat emits at each phase checkpoint
- ✅ Progress reporting shows current phase and percent complete
- ✅ Phase rollback restores state to previous checkpoint
- ✅ EKSProjectSetupValidator validates required folders and files
- ✅ Missing folders auto-created with logging
- ✅ Environment validation checks for eks.yml
- ✅ Readiness status clearly reported (YES/NO with details)

**References:**
- Appendix F Section 3.8: Phase-Based Orchestration
- Appendix F Section 3.9: Project Setup Validation

---

## 9. Risks and Mitigation

| Risk | Likelihood | Impact | Mitigation |
| :--- | :--------: | :----: | :--------- |
| Breaking changes to existing Phase 1 modules | Medium | High | Maintain backward compatibility with legacy mode; add opt-in flag |
| Telemetry overhead impacts performance | Medium | Medium | Implement configurable telemetry levels; allow disable |
| Factory refactoring introduces bugs | Medium | High | Comprehensive unit tests; maintain legacy mode |
| Rollback mechanism fails to restore state | Low | High | Comprehensive testing of rollback scenarios; maintain checkpoint logs |
| Setup validation too strict | Low | Medium | Make validation warnings configurable; allow override |

---

## 10. Potential Future Issues

- Telemetry data volume may grow large for long-running pipelines
- Checkpoint state size may become unmanageable
- Factory pattern may add complexity for simple use cases
- Config-driven instantiation may be difficult to debug
- Phase rollback may be complex for stateful operations
- CLI argument parsing complexity may increase
- HTTP API endpoints may require authentication (deferred to Phase 5)

---

## 11. Success Criteria

**Phase 1 (Foundation Layer):**
- ✅ EKSPipelineContext implemented with all required fields
- ✅ Base classes defined with clear interfaces
- ✅ Telemetry heartbeat emits at document processing checkpoints
- ✅ Multi-stage validation (setup, schema, data, parser) functional

**Phase 2 (I/O and Execution Layer):**
- ✅ CLI entry points for independent engine execution
- ✅ HTTP API endpoints for independent engine execution
- ✅ Checkpoint state serialization/deserialization working

**Phase 3 (Dependency Injection Layer):**
- ✅ ParserFactory routes to correct parser based on file type
- ✅ HealthScorerFactory loads dimensions from config registry
- ✅ StructureDetectorFactory instantiates correct detector
- ✅ All existing engines use factories
- ✅ Backward compatibility maintained (legacy mode works)

**Phase 4 (Orchestration and Validation Layer):**
- ✅ PipelineOrchestrator has 5 clear phases (A-E)
- ✅ Telemetry heartbeat emits at each phase checkpoint
- ✅ Progress reporting shows current phase and percent complete
- ✅ Phase rollback restores state to previous checkpoint
- ✅ EKSProjectSetupValidator validates required folders and files
- ✅ Missing folders auto-created with logging
- ✅ Environment validation checks for eks.yml
- ✅ Readiness status clearly reported (YES/NO with details)

---

## 12. Deliverables

**Phase 1:**
- `eks/engine/core/context.py` — EKSPipelineContext implementation
- `eks/engine/core/base.py` — BaseEngine, BaseProcessor abstract classes
- `eks/engine/core/telemetry.py` — TelemetryHeartbeat implementation
- `eks/engine/core/validator.py` — Multi-stage validation logic

**Phase 2:**
- `eks/engine/discovery/cli.py` — CLI entry point for discovery engine
- `eks/engine/parsers/cli.py` — CLI entry point for parser engine
- `eks/engine/health/cli.py` — CLI entry point for health scorer
- `eks/ui/backend/engine_endpoints.py` — HTTP API endpoints
- Checkpoint state serialization logic

**Phase 3:**
- `eks/engine/core/factories.py` — Factory implementations
- Refactored engines using factories

**Phase 4:**
- `eks/engine/core/pipeline_orchestrator.py` — Enhanced with checkpoints and rollback
- `eks/engine/core/setup_validator.py` — Setup validator
- `eks/config/schemas/project_setup.json` — Setup schema

**Documentation:**
- Updated `phase_1_foundation_workplan.md` with task completion status
- Test report in `eks/workplan/reports/phase_1_appendix_f_report.md`
- Updated `eks/log/update_log.md` and `eks/log/issue_log.md`

---

## 13. References

1. [appendix_f_pipeline_architecture_design.md](appendix_f_pipeline_architecture_design.md) — Appendix F architecture patterns
2. [phase_1_foundation_workplan.md](phase_1_foundation_workplan.md) — Parent Phase 1 workplan
3. [AGENTS.md](../AGENTS.md) — Repository guidelines
4. [eks/config/schemas](../eks/config/schemas) — Schema pattern reference

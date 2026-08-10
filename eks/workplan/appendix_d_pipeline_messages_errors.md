# Appendix D — Pipeline Messages & Error Codes

**Version**: 2.3
**Last Updated**: 2026-08-10
**Phase**: 1 — Foundation (schema) / 3 (runtime)
**Status**: ✅ Tested — full re-sync with config v1.3.0 + code v1.2 (D1–D8); D9–D13 added to document output routing, verbosity, and debugging features found in implementation
**Source of Truth**:
- [`eks/config/schemas/eks_error_config.json`](../config/schemas/eks_error_config.json) v1.7.0 (75 system + 53 data = 128 codes)
- [`eks/config/schemas/eks_message_config.json`](../config/schemas/eks_message_config.json) v1.2.0 (52 messages)
- [`eks/engine/core/health_scorer.py`](../engine/core/health_scorer.py)
- [`eks/engine/core/pipeline_orchestrator.py`](../engine/core/pipeline_orchestrator.py)
- [`eks/engine/core/structure_detector.py`](../engine/core/structure_detector.py)
- [`eks/engine/core/filename_parser.py`](../engine/core/filename_parser.py)
- [`eks/engine/core/file_property_parser.py`](../engine/core/file_property_parser.py)
- [`eks/engine/eks_engine_pipeline.py`](../engine/eks_engine_pipeline.py)

### Revision History

| Revision | Date | Author | Summary |
| :------- | :--- | :----- | :------ |
| 0.1 | 2026-06-19 | opencode | Initial draft: D1–D10 |
| 0.2 | 2026-06-19 | opencode | Revised D7: 6-dimension health scoring |
| 0.3 | 2026-06-19 | opencode | Added D7.10 structural elements; 6-dimension composite |
| 0.4 | 2026-07-18 | opencode | I112: Added bootstrap (B) category, S-B codes, P1-BOOT-* format, B-* universal codes |
| **1.0** | **2026-07-19** | **CodeBuddy** | **Full re-sync to match config/code. D3: added A/AI category, F/D module codes, PROP function code, ERROR severity. D4: 61 real codes (replaced 45 fabricated). D5: 50 real codes (replaced 65 fabricated); P5 codes added. D6: 49 real messages (replaced 42 fabricated). D7: tiers updated (6/16/13), source quality bonus, timestamp drift. D8: Phase A/B/C states added. D9: new implementation files. D10: fixed duplicate references.** |
| **2.0** | **2026-07-27** | **opencode** | **Added output architecture, verbosity control, debugging, and known gaps (D9–D13). Updated D1 with 4-channel overview. Renumbered D9→D14, D10→D15.** |
| **2.1** | **2026-07-31** | **opencode** | **T1.195 (I265): Added S-C-S-0901–0904 Project Definition config system errors (D4), P1-C-V-0001–0003 data errors (D5), 4 PDEF messages (D6), updated error_config to v1.7.0 (128 codes), message_config to v1.2.0 (52 messages), and Config category ranges.** |
| **2.2** | **2026-08-08** | **opencode** | **I289 (T1.251): Retired legacy hybrid formats (`P1-BOOT-{reason}`, `P1-SETUP-{type}{id}`, `B-{module}-{id}`) from documentation — canonical-only `S-{cat}-S-{id4}` / `B-{cat}-S-{id4}` / `P{phase}-{module}-{id4}` per review directive 2026-08-08.** |
| **2.3** | **2026-08-10** | **opencode** | **I291 (T1.254): D7.10 `document_elements` schema enriched — added `id` (UUID PK), `created_at` (TIMESTAMP NOT NULL DEFAULT now()), `element_seq`; `doc_id`/`element_type` documented as declared_only FK relations (fk_element_doc → documents.id, fk_element_type → element_type.element_type); three element types added (title_block, grid, signature_block).** |

---

## Table of Contents

| # | Section | Title |
| :- | :------ | :---- |
| — | — | [Revision History](#revision-history) |
| D1 | [D1. Overview](#d1-overview) | Purpose, four-channel architecture, design principles, DCC alignment |
| D2 | [D2. Error Code Format](#d2-error-code-format) | Data, system, setup, bootstrap, universal formats |
| D3 | [D3. Error Code Taxonomy](#d3-error-code-taxonomy) | Phase/module/function codes, severity levels, system categories |
| D4 | [D4. System Error Catalog](#d4-system-error-catalog) | 75 codes across 9 categories |
| D5 | [D5. Data Error Catalog](#d5-data-error-catalog) | 53 codes across 7 phase/module groups |
| D6 | [D6. Pipeline Message Catalog](#d6-pipeline-message-catalog) | Message schema, 52 messages with templates |
| D7 | [D7. Health Scoring](#d7-health-scoring) | 6-dimension scoring, weight tiers, composite formula, worked examples |
| D8 | [D8. Status Lifecycle](#d8-status-lifecycle) | Phase A/B/C states, document states, extract status values |
| D9 | [D9. Output Architecture](#d9-output-architecture) | Four-channel design, logger implementations, dual telemetry, common library |
| D10 | [D10. Output Channels in Detail](#d10-output-channels-in-detail) | UniversalLogger, MessageManager, ErrorManager, Preload Print |
| D11 | [D11. Verbosity Control & Data Flow](#d11-verbosity-control--data-flow) | CLI flags, level matrix, data flow diagram, reconciliation gap |
| D12 | [D12. Debugging & Diagnostics](#d12-debugging--diagnostics) | Debug object schema, trace table, depth tracking, DCC shims |
| D13 | [D13. Known Gaps & Open Issues](#d13-known-gaps--open-issues) | I244–I248 with root cause and impact |
| D14 | [D14. Implementation Files](#d14-implementation-files) | Config files, engine modules, common library |
| D15 | [D15. References](#d15-references) | AGENTS.md, appendices, source files |

---

## D1. Overview

The EKS pipeline messaging and error system follows the DCC pattern (per AGENTS.md §19: "Each business logic must have an independent error code defined to trace related errors"). It consists of four independent output channels plus a health scoring subsystem:

### D1.1 Four-Channel Output Architecture

| Channel | Source Class | Gate | Destination | Purpose |
|:--------|:-------------|:----:|:------------|:--------|
| **A** — Direct Logging | `UniversalLogger` | Level 0–3 | `print()` + debug_object | General-purpose progress, warnings, diagnostics |
| **B** — Catalog Messages | `MessageManager` | Level 0–3 | `logger.status()/.info()/.warning()/.error()` | Schema-driven user-facing text with template hydration |
| **C** — Error Codes | `ErrorManager` | Severity | `logger.error()/.warning()/.info()` + fail-fast | Unique-by-business-logic error tracking with health impact |
| **D** — Preload Print | Pure stdlib | None (always) | `print(msg, file=sys.stderr)` | Bootstrap failure reporting before any logger exists |

All channels except D record entries in the logger's **debug object** for post-run diagnostics regardless of verbosity level (record-before-gate principle; see I249 for current implementation gap).

### D1.2 Components

1. **Error Codes** — Unique identifiers for every system and data error, enabling precise tracing (Channels C + D)
2. **Pipeline Messages** — Schema-driven user-facing status/milestone/warning messages (Channel B)
3. **Direct Logging** — Tiered console output with debug object persistence (Channel A)
4. **Preload Bootstrap** — Pure-stdlib failure reporting before infrastructure loads (Channel D)
5. **Health Scoring** — Per-document extraction confidence and pipeline-level quality metrics

### D1.3 Design Principles

| Principle | Description |
|-----------|-------------|
| **Schema-driven** | Error codes and messages defined in JSON config files, not hardcoded |
| **Two error domains** | System-status (pipeline execution) vs data-handling (quality/integrity) |
| **Unique per business logic** | Each distinct error condition gets its own code (AGENTS.md §19) |
| **Fail-fast metadata** | Critical errors stop the pipeline; warnings accumulate |
| **Traceable** | Every error links to its source module, function, and phase |
| **Health-aware** | Errors impact health scores; scores drive quality gates |
| **Level-gated** | All output respects a unified verbosity level (0–3) controlling visibility |

### D1.4 DCC Alignment

EKS adopts the DCC error code taxonomy pattern with domain-specific adaptations:

| Aspect | DCC | EKS |
|--------|-----|-----|
| Data error format | `LL-M-F-XXXX` | `P{phase}-{module}-{function}-{id}` |
| System error format | `S-C-S-XXXX` | `S-C-S-XXXX` (identical) |
| Error domains | System + Data | System + Data |
| Health scoring | Per-row (tabular) | Per-document (registry) |
| Status lifecycle | NEW → IN_PROGRESS → RESOLVED → CLOSED | NEW → EXTRACTED → REGISTERED → VERIFIED |
| Logger | DCC module-level functions + global singleton | UniversalLogger class per-component |

---

## D2. Error Code Format

### Data Errors

**Format**: `P{phase}-{module}-{function}-{id}`

```
P  3  -  E  -  E  -  0001
│  │     │     │     │
│  │     │     │     └── 4-5 digit sequential ID (0001–0019)
│  │     │     └──────── Function code (R/P/E/V/L/F/S/G/PROP)
│  │     └────────────── Module code (D/P/E/X/G/R/F)
│  └──────────────────── Phase number (1–5)
└─────────────────────── Prefix: P = Phase
```

**Example**: `P3-E-E-0001` = Phase 3, Extractor module, Extract function, error #1

### System Errors

**Format**: `S-{category}-S-{id4}`

```
S  -  F  -  S  -  0201
│     │     │     │
│     │     │     └── 4-digit sequential ID (0001–9999)
│     │     └──────── S = System
│     └────────────── Category (E/F/C/R/A/B)
└──────────────────── S = System prefix
```

**Example**: `S-F-S-0201` = System, File category, error #201

### Universal Bootstrap Format

**Format**: `B-{cat}-S-{id4}`

```
B  -  C  -  S  -  0001
│     │     │     │
│     │     │     └── 4-digit sequential ID
│     │     └──────── S = System
│     └────────────── Category letter (C/H/R/D/A/E/K/M/B/X/U)
└──────────────────── B = Bootstrap (universal)
```

**Example**: `B-C-S-0001` = Bootstrap, CLI category, System, error #1

**Note** (I289, review directive 2026-08-08): All error codes now follow the canonical `X-X-X-XXXX` pattern with 4-digit IDs. Retired hybrid formats: `P1-SETUP-{type}{id}`, `P1-BOOT-{reason}`, `B-{module}-{id}` (incl. dynamic `B-{phase_id}-ERR`), and `S-{cat}-S-{id}` (non-4-digit). Only `S-{cat}-S-{id4}`, `B-{cat}-S-{id4}`, and `P{phase}-{module}-{function}-{id4}` are permitted.

---

## D3. Error Code Taxonomy

### Phase Codes (Data Errors)

| Code | Phase | Description |
|------|-------|-------------|
| `P1` | Phase 1 — Foundation | File discovery, placeholder registration |
| `P2` | Phase 2 — Parsing | PDF/DOCX/DGN file parsing |
| `P3` | Phase 3 — Extraction & Graph | Metadata extraction, cross-reference, graph operations |
| `P4` | Phase 4 — Retrieval | Query, retrieval, scoring (future) |
| `P5` | Phase 5 — File Operations | Filename parsing, property extraction, pipeline file ops |

### Module Codes

| Code | Module | Phase(s) | Description |
|------|--------|----------|-------------|
| `D` | Discovery | 1 | File walk and placeholder registration |
| `P` | Parser | 2 | File parsing (PDF, DOCX, XLSX, DGN) |
| `E` | Extractor | 3 | Metadata extraction (cover sheet, filename) |
| `X` | CrossRef | 3 | Cross-reference (datadrop, asset tags) |
| `G` | Graph | 3 | Graph node/edge operations |
| `R` | Registry | 5 | Document registry lookup |
| `F` | File | 5 | File-level operations (filename parse, property extraction) |

### Function Codes

| Code | Function | Description |
|------|----------|-------------|
| `P` | Parse | File parsing, filename parsing, discovery operations |
| `E` | Extract | Metadata extraction operations |
| `V` | Validate | Validation operations (filename segment, file type) |
| `S` | System | System-level file operations |
| `G` | Graph | Graph node/edge/query operations |
| `X` | CrossRef | Cross-reference operations |
| `PROP` | Property | File property extraction (OS stat + embedded metadata) |

### Severity Levels

| Level | Description | Pipeline Impact |
|-------|-------------|-----------------|
| `FATAL` | Unrecoverable error, pipeline cannot continue | Stops execution immediately |
| `CRITICAL` | Major failure, requires intervention | Stops execution, allows cleanup |
| `ERROR` | Significant pipeline error, phase may fail | Phase may stop, file processing continues |
| `HIGH` | Significant issue, degraded output | Logs error, continues with fallback |
| `WARNING` | Moderate or minor issue, partial impact | Logs warning, continues |
| `INFO` | Informational, no error | Logs info, continues |

### System Error Categories

| Code | Category | Range | Description |
|------|----------|-------|-------------|
| `E` | Environment | `S-E-S-0100–0199` | Python, packages, DuckDB |
| `F` | File | `S-F-S-0200–0299` | File I/O, paths, schema files, config files |
| `C` | Config | `S-C-S-0300–0399`, `S-C-S-0901–0904` | Schema, config, parameters, registry |
| `R` | Runtime | `S-R-S-0400–0499` | Exceptions, memory, fail-fast, pipeline phase |
| `A` | AI | `S-A-S-0500–0599` | AI operations, embedding service, Ollama |
| `B` | Bootstrap | `S-B-S-0600–0699` | Bootstrap initialization, preload traces, readiness gates |

### Extended System Error Categories

| Category | Prefix Format | Count | Description |
|----------|---------------|:-----:|-------------|
| Bootstrap Universal | `B-{cat}-S-{id4}` | 15 | CLI, path, registry, defaults, fallback, env, schema, params, boot, context, unknown |

---

## D4. System Error Catalog

**Total: 75 codes** across 9 categories.

### S-E: Environment Errors (0101–0107)

| Code | Name | Severity | Description | Stops Pipeline |
|------|------|----------|-------------|:--------------:|
| `S-E-S-0101` | MISSING_PACKAGE | FATAL | Required Python package is not installed | Yes |
| `S-E-S-0102` | WRONG_PYTHON_VERSION | FATAL | Python version does not meet requirements | Yes |
| `S-E-S-0103` | IMPORT_ERROR | FATAL | Failed to import required module | Yes |
| `S-E-S-0104` | ENVIRONMENT_NOT_READY | FATAL | Environment validation failed | Yes |
| `S-E-S-0105` | DUCKDB_UNAVAILABLE | FATAL | DuckDB not available for pipeline execution | Yes |
| `S-E-S-0106` | MISSING_DEPENDENCY | WARNING | Required Python dependency not installed | No |
| `S-E-S-0107` | PYTHON_VERSION_MISMATCH | WARNING | Python version does not match expected version | No |

### S-F: File I/O Errors (0201–0210)

| Code | Name | Severity | Description | Stops Pipeline |
|------|------|----------|-------------|:--------------:|
| `S-F-S-0201` | INPUT_FILE_NOT_FOUND | FATAL | Input file not found at specified path | Yes |
| `S-F-S-0202` | FILE_UNREADABLE | FATAL | File exists but cannot be read | Yes |
| `S-F-S-0203` | OUTPUT_DIR_NOT_WRITABLE | FATAL | Output directory is not writable | Yes |
| `S-F-S-0204` | SCHEMA_FILE_NOT_FOUND | FATAL | Schema configuration file not found | Yes |
| `S-F-S-0205` | CONFIG_FILE_NOT_FOUND | FATAL | Configuration file not found | Yes |
| `S-F-S-0206` | OUTPUT_DIR_CREATION_FAILED | FATAL | Cannot create output directory | Yes |
| `S-F-S-0207` | MISSING_REQUIRED_FOLDER | FATAL | Required project folder does not exist | Yes |
| `S-F-S-0208` | MISSING_REQUIRED_FILE | FATAL | Required project file does not exist | Yes |
| `S-F-S-0209` | MISSING_EKS_YML | FATAL | eks/eks.yml environment file not found | Yes |
| `S-F-S-0210` | OUTPUT_PATH_NOT_WRITABLE | WARNING | Output directory is not writable | No |

### S-C: Config Errors (0301–0308)

| Code | Name | Severity | Description | Stops Pipeline |
|------|------|----------|-------------|:--------------:|
| `S-C-S-0301` | INVALID_PARAMETER | FATAL | Invalid parameter provided to pipeline | Yes |
| `S-C-S-0302` | SCHEMA_PARSE_ERROR | FATAL | Failed to parse schema JSON | Yes |
| `S-C-S-0303` | SCHEMA_VALIDATION_FAILED | FATAL | Schema validation failed against schema definition | Yes |
| `S-C-S-0304` | MISSING_REQUIRED_CONFIG | FATAL | Required configuration is missing | Yes |
| `S-C-S-0305` | ERROR_CATALOG_LOAD_FAILED | WARNING | Failed to load error catalog | No |
| `S-C-S-0306` | MESSAGE_CATALOG_LOAD_FAILED | WARNING | Failed to load message catalog | No |
| `S-C-S-0307` | REGISTRY_CONNECTION_FAILED | FATAL | Failed to connect to document registry | Yes |
| `S-C-S-0308` | SCHEMA_RESOLUTION_ERROR | FATAL | Schema resolution failed via $ref chain | Yes |

### S-C: Project Definition Config Errors (0901–0904) — I265 T1.195

Project Definition configuration validation errors (Appendix L §L.13). System errors hard-fail pipeline initialization via `resolver.errors` → bootstrap raises (V1 failure semantics). Both `S-C-S-09xx` codes extend the existing `S-C-S-XXXX` system format.

| Code | Name | Severity | Description | Stops Pipeline |
|------|------|----------|-------------|:--------------:|
| `S-C-S-0901` | PDEF_MISSING_MANDATORY_SECTION | FATAL | Project definition missing a mandatory section (project_identity, project_lifecycle, engineering_convention, engineering_standards, document_profile) or mandatory identity field | Yes |
| `S-C-S-0902` | PDEF_UNKNOWN_PROFILE_REF | FATAL | Unknown profile reference — a reusable profile (parsing/chunking/embedding/asset/ontology/retrieval/prompt/validation/document parser) or runtime profile (storage/vector_db/graph_db/messaging/cache) is not registered in the owning schema library | Yes |
| `S-C-S-0903` | PDEF_DUPLICATE_PROJECT_OR_PROFILE | FATAL | Duplicate project code or duplicate reusable profile id across owning schema registries | Yes |
| `S-C-S-0904` | PDEF_RUNTIME_CONSTRUCTION_FAILED | FATAL | RuntimeProjectConfiguration construction failed during resolution | Yes |

### P1-C: Project Definition Data Errors (0001–0003) — I265 T1.195

Project Definition configuration validation data errors (Appendix L §L.13.6/.7/.10). Data errors never block pipeline construction (V1) — they are logged via `resolver.data_errors`. Format `P{phase}-{module}-{function}-{id}` with layer `P1`, module `C` (Config), function `V` (Validate).

| Code | Name | Severity | Description | Health Impact |
|------|------|----------|-------------|:-------------:|
| `P1-C-V-0001` | PDEF_CAPABILITY_CONSISTENCY_FAILED | WARNING | Profile capability mismatch — resolved profile does not support the selected document profile, file extension, OCR requirement, or revision scheme (L.13.6, capability-driven V2) | −1 |
| `P1-C-V-0002` | PDEF_METADATA_POLICY_GAP | WARNING | Mandatory metadata field declared for a project has no inheritance rule under the selected metadata policy (L.13.7) | −1 |
| `P1-C-V-0003` | PDEF_UNUSED_PROFILE | INFO | Reusable profile registered in an owning schema library but never referenced by any project definition (L.13.10) | 0 |

### S-R: Runtime Errors (0401–0410)

| Code | Name | Severity | Description | Stops Pipeline |
|------|------|----------|-------------|:--------------:|
| `S-R-S-0401` | FAIL_FAST_TRIGGERED | FATAL | Fail-fast condition triggered — stopping pipeline | Yes |
| `S-R-S-0402` | PIPELINE_ABORTED | FATAL | Pipeline execution aborted by user or timeout | Yes |
| `S-R-S-0403` | MEMORY_ERROR | FATAL | Memory allocation failed during processing | Yes |
| `S-R-S-0404` | BATCH_PROCESSING_FAILED | FATAL | Batch processing encountered an unrecoverable error | Yes |
| `S-R-S-0405` | GRAPH_ENGINE_FAILED | HIGH | Graph engine operation failed | No |
| `S-R-S-0406` | PRE_PIPELINE_VALIDATION_FAILED | FATAL | Pre-pipeline validation failed | Yes |
| `S-R-S-0407` | FILE_PROCESSING_FAILED | ERROR | Unhandled error during per-file processing | No |
| `S-R-S-0408` | PIPELINE_PHASE_FAILED | ERROR | Pipeline phase execution failed | Yes |
| `S-R-S-0409` | PIPELINE_PROCESSING_FATAL | ERROR | Fatal error during pipeline processing | Yes |
| `S-R-S-0410` | SETUP_NOT_READY | FATAL | Project setup validation failed — readiness check not passed | Yes |

### S-A: AI / Optional Service Errors (0501–0503)

| Code | Name | Severity | Description | Stops Pipeline |
|------|------|----------|-------------|:--------------:|
| `S-A-S-0501` | AI_OPS_FAILED | WARNING | AI operations failed to complete | No |
| `S-A-S-0502` | EMBEDDING_SERVICE_FAILED | WARNING | Embedding service not available | No |
| `S-A-S-0503` | OLLAMA_UNAVAILABLE | WARNING | Ollama service is not available | No |

### S-B: Bootstrap Errors (0601–0618)

| Code | Name | Severity | Description | Stops Pipeline |
|------|------|----------|-------------|:--------------:|
| `S-B-S-0601` | BOOTSTRAP_NOT_COMPLETE | FATAL | Bootstrap must be completed before pipeline execution | Yes |
| `S-B-S-0602` | PHASE_DEPENDENCY_FAILED | FATAL | Required prior phase has not completed successfully | Yes |
| `S-B-S-0603` | BOOT_READINESS_FAILED | FATAL | Bootstrap readiness gate failed — project setup not ready | Yes |
| `S-B-S-0604` | BOOT_CONFIG_FAILED | FATAL | Bootstrap config loading failed — unable to load project configuration | Yes |
| `S-B-S-0605` | BOOT_PATHS_FAILED | FATAL | Bootstrap path resolution failed — invalid or missing project paths | Yes |
| `S-B-S-0606` | BOOT_OS_DETECTION_FAILED | FATAL | Bootstrap OS detection failed — unable to determine operating system | Yes |
| `S-B-S-0607` | BOOT_CONTEXT_FAILED | FATAL | Bootstrap context creation failed — must bootstrap before creating PipelineContext | Yes |
| `S-B-S-0608` | BOOT_ENVIRONMENT_FAILED | FATAL | Bootstrap environment check failed — required dependencies missing. Run: conda activate eks | Yes |
| `S-B-S-0609` | BOOT_CONFIG_DEGRADED | WARNING | Bootstrap config loaded in degraded mode — partial configuration | No |
| `S-B-S-0610` | BOOT_CONFIGREGISTRY_FAILED | WARNING | Bootstrap config registry construction degraded | No |
| `S-B-S-0611` | BOOT_SCCONFIG_DEGRADED | WARNING | Bootstrap schema/config load degraded — fallback used | No |
| `S-B-S-0612` | BOOT_ERRORMGR_TODICT_FAILED | WARNING | ErrorManager to_dict export failed | No |
| `S-B-S-0613` | BOOT_MSGMGR_TODICT_FAILED | WARNING | MessageManager to_dict export failed | No |
| `S-B-S-0614` | BOOT_ERRORMGR_CTX_FAILED | WARNING | ErrorManager context binding failed | No |
| `S-B-S-0615` | BOOT_MSGMGR_CTX_FAILED | WARNING | MessageManager context binding failed | No |
| `S-B-S-0616` | BOOT_SCHEMA_EMPTY | FATAL | Bootstrap schema registry loaded empty — no schemas available | Yes |
| `S-B-S-0617` | BOOT_SCHEMA_CROSSREF_FAILED | FATAL | Bootstrap schema cross-reference validation failed | Yes |
| `S-B-S-0618` | BOOT_SCHEMA_CONFORMANCE_FAILED | FATAL | Bootstrap schema conformance check failed | Yes |

### B-*: Universal Bootstrap Errors — Standardized Format (15 codes)

| Code | Name | Severity | Description | Stops Pipeline |
|------|------|----------|-------------|:--------------:|
| `B-C-S-0001` | BOOTSTRAP_CLI_PARSE_FAILED | FATAL | Bootstrap CLI parsing failed | Yes |
| `B-H-S-0001` | BOOTSTRAP_PROJECT_ROOT_MISSING | FATAL | Project root does not exist — cannot bootstrap | Yes |
| `B-H-S-0002` | BOOTSTRAP_PATH_VALIDATION_FAILED | FATAL | Bootstrap path validation failed | Yes |
| `B-R-S-0001` | BOOTSTRAP_REGISTRY_LOAD_FAILED | FATAL | Bootstrap registry / config loading failed | Yes |
| `B-D-S-0001` | BOOTSTRAP_DEFAULTS_BUILD_FAILED | FATAL | Bootstrap native defaults building failed | Yes |
| `B-A-S-0001` | BOOTSTRAP_FALLBACK_VALIDATION_FAILED | FATAL | Bootstrap fallback validation failed | Yes |
| `B-E-S-0001` | BOOTSTRAP_ENV_TESTING_FAILED | FATAL | Bootstrap environment testing failed | Yes |
| `B-E-S-0002` | BOOTSTRAP_DEPS_MISSING | FATAL | Required dependencies missing during bootstrap | Yes |
| `B-K-S-0001` | BOOTSTRAP_SCHEMA_RESOLUTION_FAILED | FATAL | Bootstrap schema resolution failed | Yes |
| `B-M-S-0001` | BOOTSTRAP_CLI_PARAMS_FAILED | FATAL | Bootstrap CLI parameters resolution failed | Yes |
| `B-M-S-0002` | BOOTSTRAP_UI_PARAMS_FAILED | FATAL | Bootstrap UI parameters resolution failed | Yes |
| `B-B-S-0001` | BOOTSTRAP_PRELOAD_NOT_READY | FATAL | Bootstrap must be completed before accessing preload trace | Yes |
| `B-X-S-0001` | BOOTSTRAP_CTX_NOT_READY | FATAL | Must bootstrap before creating PipelineContext | Yes |
| `B-U-S-0001` | BOOTSTRAP_UNHANDLED_CLI_ERROR | FATAL | Unexpected bootstrap error in CLI mode | Yes |
| `B-U-S-0002` | BOOTSTRAP_UNHANDLED_UI_ERROR | FATAL | Unexpected bootstrap error in UI mode | Yes |

---

## D5. Data Error Catalog

**Total: 53 codes** across 7 phase/module groups.

### Phase 1 — Discovery Errors (P1-D-P)

| Code | Name | Severity | Description | Source | Health Impact |
|------|------|----------|-------------|--------|:-------------:|
| `P1-D-P-0001` | FILE_DISCOVERY_FAILED | CRITICAL | File walk/discovery failed for target directory | `eks/engine/core/discovery.py` | -5 |
| `P1-D-P-0002` | DIRECTORY_NOT_FOUND | CRITICAL | Target directory does not exist or is inaccessible | `eks/engine/core/discovery.py` | -5 |
| `P1-D-P-0003` | REGISTRATION_FAILED | HIGH | Placeholder registration failed during file discovery | `eks/engine/core/pipeline_orchestrator.py` | -3 |

### Phase 1 — Project Definition Config Validation Errors (P1-C-V) — I265 T1.195

Project Definition configuration validation data errors (Appendix L §L.13.6/.7/.10). These never block pipeline construction (V1 failure semantics) — they are accumulated in `ProjectDefinitionResolver.data_errors` and logged during bootstrap.

| Code | Name | Severity | Description | Source | Health Impact |
|------|------|----------|-------------|--------|:-------------:|
| `P1-C-V-0001` | PDEF_CAPABILITY_CONSISTENCY_FAILED | WARNING | Resolved profile does not support the selected document profile, file extension, OCR requirement, or revision scheme (L.13.6 capability-driven V2) | `eks/engine/core/project_definition.py` | -1 |
| `P1-C-V-0002` | PDEF_METADATA_POLICY_GAP | WARNING | Mandatory metadata field declared for a project has no inheritance rule under the selected metadata policy (L.13.7) | `eks/engine/core/project_definition.py` | -1 |
| `P1-C-V-0003` | PDEF_UNUSED_PROFILE | INFO | Reusable profile registered in an owning schema library but never referenced by any project definition (L.13.10) | `eks/engine/core/project_definition.py` | 0 |

### Phase 2 — Parser Errors (P2-P-P)

| Code | Name | Severity | Description | Source | Health Impact |
|------|------|----------|-------------|--------|:-------------:|
| `P2-P-P-0001` | PDF_PARSE_OPEN_FAIL | HIGH | Failed to open PDF file for parsing | `eks/engine/parsers/pdf_parser.py` | -3 |
| `P2-P-P-0002` | PDF_PAGE_EXTRACT_FAIL | HIGH | Failed to extract a specific page from PDF | `eks/engine/parsers/pdf_parser.py` | -3 |
| `P2-P-P-0003` | PDF_NO_TEXT_LAYER | WARNING | PDF has no selectable text layer (scanned) | `eks/engine/parsers/pdf_parser.py` | -3 |
| `P2-P-P-0004` | PDF_ENCRYPTED | HIGH | PDF is password-protected or encrypted | `eks/engine/parsers/pdf_parser.py` | -3 |
| `P2-P-P-0005` | PDF_IMAGE_EXTRACT_FAIL | WARNING | Failed to extract image from PDF | `eks/engine/parsers/pdf_parser.py` | -2 |
| `P2-P-P-0006` | PDF_TABLE_EXTRACT_FAIL | WARNING | Failed to extract table from PDF page | `eks/engine/parsers/pdf_parser.py` | -2 |
| `P2-P-P-0007` | DOCX_PARSE_FAIL | HIGH | DOCX structure invalid or corrupt | `eks/engine/parsers/docx_parser.py` | -3 |
| `P2-P-P-0008` | DGN_UNSUPPORTED | HIGH | DGN file format not yet supported | `eks/engine/parsers/dgn_parser.py` | -3 |

### Phase 3 — Extraction Errors (P3-E-E)

| Code | Name | Severity | Description | Source | Health Impact |
|------|------|----------|-------------|--------|:-------------:|
| `P3-E-E-0001` | COVERSHEET_UNRECOGNIZED | WARNING | Cover sheet format not identified | `structure_detector.py` | -2 |
| `P3-E-E-0002` | DOC_NUMBER_EXTRACT_FAIL | WARNING | Could not extract document number | `extractor.py` | -2 |
| `P3-E-E-0003` | REVISION_EXTRACT_FAIL | WARNING | Could not extract revision | `extractor.py` | -2 |
| `P3-E-E-0004` | DISCIPLINE_EXTRACT_FAIL | WARNING | Could not extract discipline code | `extractor.py` | -1 |
| `P3-E-E-0005` | STATUS_EXTRACT_FAIL | WARNING | Could not extract approval status | `extractor.py` | -1 |
| `P3-E-E-0006` | CREATED_BY_EXTRACT_FAIL | INFO | Could not extract author | `extractor.py` | 0 |
| `P3-E-E-0007` | ORIGINATOR_EXTRACT_FAIL | INFO | Could not extract originator company | `extractor.py` | 0 |
| `P3-E-E-0008` | METADATA_INCOMPLETE | INFO | Some optional fields missing | `extractor.py` | 0 |
| `P3-E-E-0009` | CONFIDENCE_LOW | WARNING | Extraction confidence below threshold | `health_scorer.py` | -2 |
| `P3-E-E-0010` | COVER_PAGE_MISSING | WARNING | No cover page / title block detected | `structure_detector.py` | -3 |
| `P3-E-E-0011` | REVISION_TABLE_MISSING | WARNING | No revision history table detected | `structure_detector.py` | -2 |
| `P3-E-E-0012` | SECTIONS_MISSING | INFO | No section headings detected | `structure_detector.py` | 0 |
| `P3-E-E-0013` | TABLES_EMPTY | INFO | No data tables detected in body | `structure_detector.py` | 0 |
| `P3-E-E-0014` | IMAGES_DETECTED | INFO | Document contains images/charts | `structure_detector.py` | 0 |
| `P3-E-E-0015` | SCANNED_PAGES_FOUND | WARNING | Some pages have no text layer | `structure_detector.py` | -2 |
| `P3-E-E-0016` | ELEMENT_STORAGE_FAIL | WARNING | Detected element failed to store in DB | `registry.py` | -1 |
| `P3-E-E-0017` | STRUCTURE_LOW_SCORE | WARNING | Structural completeness below 0.5 | `health_scorer.py` | -2 |
| `P3-E-E-0018` | STRUCTURE_DETECTION_FAIL | WARNING | Structure detection failed for file | `pipeline_orchestrator.py` | -2 |
| `P3-E-E-0019` | HEALTH_SCORE_FAILED | WARNING | Health scoring computation failed | `pipeline_orchestrator.py` | -2 |

### Phase 3 — Cross-Reference Errors (P3-X-X)

| Code | Name | Severity | Description | Source | Health Impact |
|------|------|----------|-------------|--------|:-------------:|
| `P3-X-X-0001` | KEYTAG_NO_MATCH | WARNING | asset_tag has no matching datadrop keytag | `xref.py` | -1 |
| `P3-X-X-0002` | KEYTAG_AMBIGUOUS | WARNING | asset_tag matches multiple keytags | `xref.py` | -1 |
| `P3-X-X-0003` | KEYTAG_FORMAT_INVALID | WARNING | asset_tag format does not match expected pattern | `xref.py` | -1 |
| `P3-X-X-0004` | DATADROP_LOAD_FAIL | CRITICAL | Cannot load datadrop Excel file | `xref.py` | -5 |
| `P3-X-X-0005` | DATADROP_SHEET_MISSING | HIGH | Expected datadrop sheet not found | `xref.py` | -3 |

### Phase 3 — Graph Errors (P3-G-G)

| Code | Name | Severity | Description | Source | Health Impact |
|------|------|----------|-------------|--------|:-------------:|
| `P3-G-G-0001` | NODE_CREATION_FAILED | WARNING | Graph node creation failed | `graph_engine.py` | -2 |
| `P3-G-G-0002` | EDGE_CREATION_FAILED | WARNING | Graph edge creation failed | `graph_engine.py` | -2 |
| `P3-G-G-0003` | GRAPH_QUERY_FAILED | WARNING | Graph query execution failed | `graph_engine.py` | -2 |

### Phase 5 — File Operations Errors (P5-F-*)

#### File Validation (P5-F-V)

| Code | Name | Severity | Description | Source | Health Impact |
|------|------|----------|-------------|--------|:-------------:|
| `P5-F-V-0001` | FILE_TYPE_NOT_SUPPORTED | HIGH | File type not supported for processing | `pipeline_orchestrator.py` | -3 |
| `P5-F-V-0004` | TOO_FEW_FILENAME_SEGMENTS | WARNING | Filename has fewer segments than minimum required | `filename_parser.py` | -2 |
| `P5-F-V-0005` | TOO_MANY_FILENAME_SEGMENTS | WARNING | Filename has more segments than maximum allowed | `filename_parser.py` | -2 |
| `P5-F-V-0006` | SEGMENT_VALIDATION_FAILED | WARNING | Filename segment failed regex/schema validation | `filename_parser.py` | -1 |

#### File System (P5-F-S)

| Code | Name | Severity | Description | Source | Health Impact |
|------|------|----------|-------------|--------|:-------------:|
| `P5-F-S-0002` | FILE_NOT_FOUND | HIGH | File not found or unreadable during processing | `pipeline_orchestrator.py` | -3 |

#### Registry Lookup (P5-R-P)

| Code | Name | Severity | Description | Source | Health Impact |
|------|------|----------|-------------|--------|:-------------:|
| `P5-R-P-0003` | DOCUMENT_NOT_REGISTERED | WARNING | Document not found in registry during Phase B lookup | `pipeline_orchestrator.py` | -2 |

#### Filename Parse (P5-F-P)

| Code | Name | Severity | Description | Source | Health Impact |
|------|------|----------|-------------|--------|:-------------:|
| `P5-F-P-0007` | UNRESOLVABLE_FILENAME | WARNING | Filename cannot be resolved by any pattern — synthetic key generated | `filename_parser.py` | -2 |

#### File Property Extraction (P5-F-PROP)

| Code | Name | Severity | Description | Source | Health Impact |
|------|------|----------|-------------|--------|:-------------:|
| `P5-F-PROP-0001` | FILE_PROP_NOT_FOUND | CRITICAL | File not found during property extraction (Path.stat failed) | `file_property_parser.py` | -3 |
| `P5-F-PROP-0002` | FILE_PROP_STAT_FAILED | CRITICAL | OS stat failed during property extraction (OSError) | `file_property_parser.py` | -3 |
| `P5-F-PROP-0003` | FILE_PROP_NO_METADATA | WARNING | No parser metadata available for embedded property extraction | `file_property_parser.py` | -1 |
| `P5-F-PROP-0004` | FILE_PROP_MAPPING_FAILURE | WARNING | Property mapping failure — source_key not found in parser metadata | `file_property_parser.py` | -1 |
| `P5-F-PROP-0005` | FILE_PROP_HASH_FAILED | CRITICAL | Hash computation failed during file property extraction | `file_property_parser.py` | -2 |

---

## D6. Pipeline Message Catalog

**Total: 52 messages** across 7 categories.

### Message Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique message identifier (UPPER_SNAKE_CASE) |
| `category` | enum | `milestone`, `status`, `progress`, `warning`, `error` |
| `level` | integer | Verbosity: 0=error, 1=normal/status, 2=debug, 3=trace |
| `template` | string | Python-style template with `{placeholders}` |
| `icon` | string | Display icon (optional) |

### Milestone Messages

| ID | Category | Level | Template | Icon |
|----|----------|-------|----------|------|
| `MILESTONE_BOOTSTRAP_START` | milestone | 1 | `Starting EKS bootstrap initialization...` | ▶ |
| `MILESTONE_BOOTSTRAP_COMPLETE` | milestone | 1 | `Bootstrap complete: {completed_count}/{total_count} phases passed ({duration_ms:.0f}ms)` | ✓ |
| `MILESTONE_PIPELINE_START` | milestone | 1 | `Starting EKS pipeline for {target}` | — |
| `MILESTONE_FILE_DISCOVERY` | milestone | 1 | `Discovered {count} files in {target}` | — |
| `MILESTONE_PARSE_COMPLETE` | milestone | 1 | `Parsed {count} files ({success}/{failed} ok)` | — |
| `MILESTONE_EXTRACTION_COMPLETE` | milestone | 1 | `Extraction complete for {count} documents` | — |
| `MILESTONE_REGISTRATION_COMPLETE` | milestone | 1 | `Registered {count} documents in registry` | — |
| `MILESTONE_PHASE_COMPLETE` | milestone | 1 | `Phase {phase} complete — {summary}` | — |
| `MILESTONE_HEALTH_SCORED` | milestone | 1 | `Health scored {count} documents (avg: {avg_score})` | — |
| `MILESTONE_PIPELINE_DONE` | milestone | 1 | `EKS pipeline complete — {total} documents processed ({elapsed}s)` | — |

### Phase A/B/C Milestone Messages

| ID | Category | Level | Template | Icon |
|----|----------|-------|----------|------|
| `STATUS_PHASE_A_START` | milestone | 1 | `=== Phase {phase} Start: File Discovery ===` | ▶ |
| `STATUS_PHASE_A_COMPLETE` | milestone | 1 | `Phase A complete — {registered} files registered` | ✓ |
| `STATUS_PHASE_B_START` | milestone | 1 | `=== Phase {phase} Start: Parse + Detect + Score ===` | ▶ |
| `STATUS_PHASE_B_COMPLETE` | milestone | 1 | `Phase B complete — {success}/{total} success, {partial} partial, {failed} failed` | ✓ |
| `STATUS_PHASE_C_START` | milestone | 1 | `=== Phase {phase} Start: Review ===` | ▶ |
| `STATUS_PHASE_C_COMPLETE` | milestone | 1 | `Phase C complete — {flagged} documents flagged for review` | ✓ |
| `STATUS_PIPELINE_START` | milestone | 1 | `Starting EKS pipeline for {root_dir}` | ▶ |
| `STATUS_PIPELINE_COMPLETE` | milestone | 1 | `EKS pipeline complete` | ✓ |

### Status Messages

| ID | Category | Level | Template |
|----|----------|-------|----------|
| `STATUS_PARSING_FILE` | status | 1 | `Parsing: {filename}` |
| `STATUS_EXTRACTING` | status | 1 | `Extracting metadata from {filename}` |
| `STATUS_REGISTERING` | status | 1 | `Registering document: {doc_id}` |
| `STATUS_DETECTING_STRUCTURE` | status | 2 | `Detecting structural elements in {filename}` |
| `STATUS_STORING_ELEMENTS` | status | 2 | `Storing {count} elements for {doc_id}` |
| `STATUS_HEALTH_SCORE` | status | 2 | `Scoring {doc_id}: completeness={c:.2f} confidence={e:.2f} structural={s:.2f}` |
| `STATUS_XREF_CHECK` | status | 2 | `Cross-referencing {count} asset tags for {doc_id}` |
| `STATUS_BATCH_PROGRESS` | status | 1 | `Progress: [{current}/{total}] {percent}%` |
| `STATUS_CONFIG_LOADED` | status | 1 | `Config loaded: {config_count} keys, {path}` |
| `STATUS_PATHS_RESOLVED` | status | 2 | `Paths resolved: {count} paths from project root` |
| `STATUS_READINESS_PASSED` | status | 1 | `Readiness gate passed — project setup validated` |
| `STATUS_MANAGERS_INITIALIZED` | status | 2 | `Managers initialized: ErrorManager + MessageManager ready` |
| `PDEF_RESOLVE_START` | status | 1 | `Resolving {count} project definitions...` |
| `PDEF_RESOLVE_COMPLETE` | status | 1 | `Resolved {count} project definitions ({errors} errors, {data_errors} data warnings)` |

### Progress Messages

| ID | Category | Level | Template |
|----|----------|-------|----------|
| `PROGRESS_PARSING` | progress | 1 | `  {filename}` |
| `PROGRESS_EXTRACTION` | progress | 1 | `  Extracting fields from {filename}` |
| `PROGRESS_REGISTRATION` | progress | 1 | `  Registering {count} documents` |
| `PROGRESS_HEALTH_SCORE` | progress | 1 | `  Health scoring document {n}/{total}` |

### Warning Messages

| ID | Category | Level | Template |
|----|----------|-------|----------|
| `WARNING_SCANNED_PDF` | warning | 1 | `Scanned PDF detected (no text layer): {filename}` |
| `WARNING_LOW_CONFIDENCE` | warning | 1 | `Low extraction confidence ({score}%): {filename}` |
| `WARNING_NO_MATCH` | warning | 2 | `Asset tag "{tag}" has no datadrop match` |
| `WARNING_AMBIGUOUS_MATCH` | warning | 2 | `Asset tag "{tag}" matches {count} keytags: {matches}` |
| `WARNING_SKIPPED_FILE` | warning | 1 | `Skipped: {filename} — {reason}` |
| `WARNING_NO_COVER_PAGE` | warning | 1 | `No cover page detected: {filename}` |
| `WARNING_NO_REVISION_TABLE` | warning | 1 | `No revision history table: {filename}` |
| `WARNING_STRUCTURE_LOW` | warning | 1 | `Low structural completeness ({score}%): {filename}` |
| `WARNING_BOOTSTRAP_PHASE_FAILED` | warning | 0 | `Bootstrap phase {phase} failed: {detail}` |
| `PDEF_DATA_ERROR` | warning | 2 | `Project definition data warning ({code}): {detail}` |

### Error Messages

| ID | Category | Level | Template |
|----|----------|-------|----------|
| `ERROR_FILE_PROCESSING` | error | 0 | `Error processing {filename}: {detail}` |
| `ERROR_EXTRACTION_FAILED` | error | 0 | `Extraction failed for {filename}: {detail}` |
| `ERROR_REGISTRATION_FAILED` | error | 0 | `Registration failed for {doc_id}: {detail}` |
| `ERROR_GRAPH_FAILED` | error | 0 | `Graph operation failed: {detail}` |
| `ERROR_INGESTION_ABORTED` | error | 0 | `Ingestion aborted at [{current}/{total}]: {detail}` |
| `PDEF_SYSTEM_ERROR` | error | 0 | `Project definition system error ({code}): {detail}` |

---

## D7. Health Scoring

### D7.1 Column Classification — All 35 Scorable Registry Columns

Every registry column is classified as scorable or non-scorable, and assigned a weight tier.

| # | Group | Column | Scorable | Source | Tier |
|---|-------|--------|:--------:|--------|:----:|
| 1 | Identity | `id` | — | System (PK) | — |
| 2 | Identity | `source_type` | — | Config default | — |
| 3 | Project | `project_title` | ✓ | Cover sheet / config | T2 |
| 4 | Project | `project_number` | ✓ | Filename / cover sheet | T1 |
| 5 | Project | `area` | ✓ | Filename / cover sheet | T2 |
| 6 | Project | `discipline` | ✓ | Filename / cover sheet | T1 |
| 7 | Project | `department` | ✓ | Cover sheet | T3 |
| 8 | Document | `document_type` | ✓ | Filename / cover sheet | T1 |
| 9 | Document | `document_number` | ✓ | Filename / cover sheet | T1 |
| 10 | Document | `document_title` | ✓ | Cover sheet / embedded | T2 |
| 11 | Document | `revision` | ✓ | Cover sheet | T1 |
| 12 | Document | `revision_date` | ✓ | Cover sheet / revision table | T2 |
| 13 | Document | `revision_description` | ✓ | Revision table / embedded | T3 |
| 14 | Document | `lifecycle_stage` | ✓ | Cover sheet / config | T2 |
| 15 | Document | `status` | ✓ | Cover sheet revision table | T2 |
| 16 | Document | `is_latest` | — | System-generated | — |
| 17 | Document | `file_path` | — | System-generated | — |
| 18 | Document | `file_type` | — | System-generated | — |
| 19 | Document | `ingested_at` | — | System-generated | — |
| 20 | Document | `project_phase` | ✓ | Cover sheet / config | T2 |
| 21 | Document | `contract_package` | ✓ | Cover sheet / filename | T2 |
| 22 | Document | `issued_date` | ✓ | Cover sheet | T2 |
| 23 | Document | `supersedes` | ✓ | Cover sheet | T2 |
| 24 | Document | `superseded_by` | ✓ | Cover sheet | T2 |
| 25 | Document | `references_documents` | ✓ | Cover sheet / embedded | T3 |
| 26 | Document | `language` | ✓ | Embedded metadata | T3 |
| 27 | Account | `created_by` | ✓ | Cover sheet | T2 |
| 28 | Account | `checked_by` | ✓ | Cover sheet | T2 |
| 29 | Account | `approved_by` | ✓ | Cover sheet | T2 |
| 30 | Account | `responsible_engineer` | ✓ | Cover sheet | T2 |
| 31 | Origin | `originator_company` | ✓ | Cover sheet | T2 |
| 32 | Origin | `vendor_name` | ✓ | Cover sheet / embedded | T3 |
| 33 | Origin | `security_class` | ✓ | Manual (Phase 5) | T3 |
| 34 | Origin | `asset_tags` | ✓ | Regex / content extraction | T1 |
| 35 | Technical | `page_count` | ✓ | PDF metadata | T2 |
| 36 | Technical | `total_sheets` | ✓ | Cover sheet | T2 |
| 37 | File Props | `file_size` | ✓ | OS stat | T3 |
| 38 | File Props | `file_hash` | ✓ | SHA-256 hash | T3 |
| 39 | Embedded | `embedded_title` | ✓ | PDF/DOCX metadata | T3 |
| 40 | Embedded | `embedded_subject` | ✓ | PDF/DOCX metadata | T3 |
| 41 | Embedded | `embedded_creator_app` | ✓ | PDF/DOCX metadata | T3 |
| 42 | Embedded | `embedded_producer` | ✓ | PDF metadata | T3 |
| 43 | Embedded | `embedded_revision_number` | ✓ | PDF/DOCX metadata | T3 |
| 44 | Quality | `extract_status` | — | System-generated | — |
| 45 | Quality | `extraction_confidence` | — | Stores the score | — |
| 46 | Quality | `extraction_notes` | — | System-generated | — |
| 47 | Quality | `verified_by` | ✓ | Manual (Phase 5) | T3 |

**Summary**: 35 scorable columns, 12 non-scorable (system/meta).

### D7.2 Weight Tiers

| Tier | Columns | Count | Rationale |
|------|---------|:-----:|-----------|
| **T1 — Critical Identity** | `project_number`, `discipline`, `document_type`, `document_number`, `revision`, `asset_tags` | 6 | Must be correct for registry to function; wrong value = broken graph |
| **T2 — Important Context** | `project_title`, `area`, `document_title`, `lifecycle_stage`, `revision_date`, `status`, `project_phase`, `contract_package`, `issued_date`, `created_by`, `checked_by`, `approved_by`, `responsible_engineer`, `originator_company`, `page_count`, `total_sheets`, `supersedes`, `superseded_by` | 16 | Valuable for retrieval and display; missing reduces usefulness |
| **T3 — Optional / Manual / Derived** | `department`, `revision_description`, `references_documents`, `language`, `vendor_name`, `security_class`, `verified_by`, `file_size`, `file_hash`, `embedded_title`, `embedded_subject`, `embedded_creator_app`, `embedded_producer`, `embedded_revision_number` | 14 | Often null at extraction; filled during verification or derived from file metadata |

### D7.3 Scoring Dimensions (6)

#### Dimension 1: Completeness (20%)

What fraction of scorable columns are populated.

```
completeness = populated_scorable_columns / 35
```

| Population | Score |
|:----------:|:-----:|
| 35/35 | 1.00 |
| 28/35 | 0.80 |
| 18/35 | 0.51 |
| 9/35 | 0.26 |
| 0/35 | 0.00 |

#### Dimension 2: Extraction Confidence (20%)

Per-column regex/extraction match quality, weighted by tier.

**Per-field match scores**:

| Match Type | Score | Description |
|------------|:-----:|-------------|
| Exact regex match | 1.0 | Value matches expected pattern exactly |
| Fuzzy match | 0.8 | Minor format deviation (lowercase, extra space) |
| Heuristic match | 0.5 | Context-guessed value from surrounding text |
| No match / null | 0.0 | Field not extracted |

**Tier multipliers** (amplify critical fields):

| Tier | Multiplier | Rationale |
|------|:---------:|-----------|
| T1 | ×2.0 | Critical identity fields must be correct |
| T2 | ×1.0 | Standard weighting |
| T3 | ×0.5 | Optional fields, low penalty if null |

```
field_weighted_score = sum(field_score × tier_multiplier) / sum(tier_multiplier_for_all_fields)
```

#### Dimension 3: Source Quality (20%)

Reliability of the document format plus embedded metadata bonus.

| Type | Score | Description |
|------|:-----:|-------------|
| A | 1.0 | Standard drawing cover sheet — full field block |
| E | 0.8 | Specification doc — rich PDF metadata |
| D | 0.9 | Volume cover page — limited fields |
| B | 0.7 | Standard detail — partial fields |
| C | 0.3 | Scanned/vector-only — no text layer |
| F | 0.0 | Parse failed entirely |

**Embedded creator bonus**: If `embedded_creator_app` is non-null (file was generated by a known authoring tool), add **+0.05** bonus to the source quality score, capped at 1.0.

#### Dimension 4: Cross-Reference Quality (15%)

Validation of extracted values against known data and config.

| Check | Applies To | Score |
|-------|-----------|:-----:|
| `asset_tags` match datadrop keytags | `asset_tags` | matched/total |
| `project_number` matches config project | `project_number` | 1.0 or 0.0 |
| `discipline` in project discipline list | `discipline` | 1.0 or 0.0 |
| `document_number` format valid | `document_number` | 1.0 or 0.0 |
| `revision` matches project revision pattern | `revision` | 1.0 or 0.0 |

```
xref_score = sum(check_pass) / total_applicable_checks
```

If no checks are applicable, defaults to 1.0.

#### Dimension 5: Consistency (15%)

Cross-field agreement and logical checks. Violations apply a multiplicative modifier.

| Check | Violation | Deduction |
|-------|-----------|:---------:|
| `created_by` ≠ `checked_by` (if both present) | Same person reviewed and checked | -0.10 |
| `checked_by` ≠ `approved_by` (if both present) | Same person checked and approved | -0.10 |
| `page_count` > 0 for non-stub documents | Zero pages | -0.10 |
| `project_title` contains project context | Mismatch with `project_number` | -0.10 |
| `discipline` matches `document_type` category | Inconsistent classification | -0.10 |
| File timestamp drift (>24h) | \|`file_modified_at` − `embedded_modified_date`\| > 86400s | -0.10 |

```
consistency_modifier = 1.0 - (0.1 × violation_count)
```

### D7.4 Composite Health Score Formula

```
health_score = (
    completeness              × 0.20 +
    extraction_confidence     × 0.20 +
    structural_completeness   × 0.20 +
    source_quality            × 0.15 +
    xref_quality              × 0.15 +
    consistency_quality       × 0.10
) × consistency_modifier
```

Clamped to [0.0, 1.0].

**Dimension summary**:

| Dimension | Weight | Description |
|-----------|:------:|-------------|
| Completeness | 20% | Fraction of scorable columns populated |
| Extraction Confidence | 20% | Per-column regex/extraction match quality |
| Structural Completeness | 20% | Fraction of expected structural elements detected |
| Source Quality | 15% | Cover sheet type quality baseline + embedded bonus |
| Cross-Reference | 15% | Asset tag, datadrop, document number validation |
| Consistency | 10% | Cross-field validation checks + timestamp drift |

### D7.5 Score → Status Mapping

| Health Score | `extract_status` | `extraction_notes` | Pipeline Action |
|:------------:|:----------------:|:-------------------:|:----------------|
| ≥ 0.90 | `success` | Full breakdown | Auto-register |
| 0.70 – 0.89 | `success` | Full breakdown | Auto-register, optional review |
| 0.50 – 0.69 | `partial` | Full breakdown | Register, flag for review |
| 0.20 – 0.49 | `partial` | Full breakdown | Register, mandatory review |
| < 0.20 | `failed` | Full breakdown | Reject, manual entry required |

### D7.6 Extraction Notes Format

The `extraction_notes` field stores the full dimension breakdown as JSON:

```json
{
  "health_score": 0.87,
  "dimensions": {
    "completeness": {"score": 0.83, "populated": 29, "total": 35},
    "extraction_confidence": {
      "score": 0.91,
      "tier1_avg": 0.95,
      "tier2_avg": 0.88,
      "tier3_avg": 0.67
    },
    "structural_completeness": {"score": 0.80, "detected": 4, "expected": 5, "elements": ["cover_page", "revision_table", "sections", "image"]},
    "source_quality": {"score": 1.0, "type": "A"},
    "xref_quality": {"score": 0.80, "checks_passed": 4, "checks_total": 5},
    "consistency": {"score": 1.0, "violations": 0}
  },
  "missing_columns": ["department", "security_class", "verified_by"],
  "tier1_fields": {"populated": 5, "total": 6}
}
```

### D7.7 Pipeline Health Score (Batch Level)

Calculated per ingestion batch after all documents are processed.

**Formula**:

```
pipeline_health = (total_docs - critical_errors - high_errors) / total_docs × 100
```

**Grade thresholds**:

| Grade | Score | Meaning |
|-------|:-----:|---------|
| A+ | ≥ 99% | Excellent — near-perfect extraction |
| A | ≥ 95% | Good — minor issues only |
| A- | ≥ 90% | Acceptable — some warnings |
| B+ | ≥ 85% | Fair — several warnings |
| B | ≥ 80% | Marginal — needs attention |
| C | ≥ 70% | Poor — significant issues |
| D | ≥ 60% | Bad — major problems |
| F | < 60% | Failed — pipeline needs investigation |

**Secondary metric** — Average document health across batch:

```
avg_document_health = sum(health_scores) / total_docs
```

### D7.8 Health Score Impact per Error

Each data error code includes a `health_score_impact` value (see D5 tables). Impact is additive per document:

```
document_penalty = sum(health_score_impact for errors on this document)
adjusted_health = max(0.0, raw_health_score + document_penalty / 100.0)
```

### D7.9 Worked Examples

#### Example 1: Type A Document (High Score)

**Input**: `131101-WSW41-DR-C-0001.pdf` (standard cover sheet)

| Dimension | Calculation | Score |
|-----------|-------------|:-----:|
| Completeness | 29/35 (all T1+T2 fields populated, 2 T3) | 0.83 |
| Extraction Confidence | T1: 6/6×1.0×2.0=12.0, T2: 16/16×1.0×1.0=16.0, T3: 4/14×1.0×0.5=2.0 → 30.0/41.0 | 0.73 |
| Structural Completeness | 4/5 expected (cover, rev table, sections, image) — missing table | 0.80 |
| Source Quality | Type A + embedded_creator_app bonus | 1.0 |
| Cross-Reference | 5/5 checks pass | 1.0 |
| Consistency | 0 violations → modifier 1.0 | 1.0 |

```
health_score = (0.83×0.20 + 0.73×0.20 + 0.80×0.20 + 1.0×0.15 + 1.0×0.15 + 1.0×0.10) × 1.0
             = (0.166 + 0.146 + 0.160 + 0.15 + 0.15 + 0.10) = 0.872
```

**Result**: `extract_status = "success"`, flagged for optional review

#### Example 2: Type C Document (Low Score)

**Input**: `131101-WIL00-DR-E-7000.pdf` (scanned, no text layer)

| Dimension | Calculation | Score |
|-----------|-------------|:-----:|
| Completeness | 1/35 (discipline from filename only) | 0.03 |
| Extraction Confidence | T1: 1/6×1.0×2.0=2.0, T2: 0, T3: 0 → 2.0/41.0 | 0.05 |
| Structural Completeness | 0/0 expected (Type C: no structure expected) | 1.0 |
| Source Quality | Type C | 0.3 |
| Cross-Reference | 1/1 check pass | 1.0 |
| Consistency | 0 violations → modifier 1.0 | 1.0 |

```
health_score = (0.03×0.20 + 0.05×0.20 + 1.0×0.20 + 0.3×0.15 + 1.0×0.15 + 1.0×0.10)
             = (0.006 + 0.010 + 0.20 + 0.045 + 0.15 + 0.10) = 0.511
```

**Result**: `extract_status = "partial"`, flagged for review

---

### D7.10 Structural Elements Table (`document_elements`)

Each document in `document_registry` can have multiple structural elements stored in a separate table. This enables Phase 2 section-aware chunking, Phase 3 graph node creation, and Phase 4 structural queries.

**Table schema**:

| Column | Type | Nullable | Description |
|--------|------|:--------:|-------------|
| `id` | VARCHAR (UUID) | NO | I291 (T1.254): surrogate UUID primary key (system-generated at store time) |
| `doc_id` | VARCHAR (UUID) | NO | FK → `documents.id` (registry UUID PK; SSOT per I291 Q2 — D7.10 `document_registry.doc_id` and I294 health_score converge on it); declared_only relation `fk_element_doc` |
| `element_type` | VARCHAR | NO | FK → `element_type.element_type` (11-code enum; declared_only relation `fk_element_type`); validated by `store_elements()` |
| `element_id` | VARCHAR | YES | Page number or location identifier |
| `title` | VARCHAR | YES | Heading, field name, or section title |
| `content` | VARCHAR | YES | Raw text or JSON (for complex structures) |
| `confidence` | DOUBLE | YES | 0.0–1.0 extraction confidence |
| `source` | VARCHAR | NO | Extraction method: `regex`, `ocr`, `heuristic`, `manual` |
| `created_at` | TIMESTAMP | NO | I291 (T1.254): row creation timestamp, DEFAULT now() |
| `element_seq` | INTEGER | YES | I291 (T1.254): optional 0-based intra-document ordering |

**Element types**:

| `element_type` | Source | Content | Phase 2 Use | Phase 3 Use |
|----------------|--------|---------|:-----------:|:-----------:|
| `cover_page` | First page regex extraction | JSON: fields + values + confidence | Section anchor | Document-type node |
| `revision_table` | Table detection on page 1 | JSON: rows[{rev, date, by, desc}] | Change tracking | Revision nodes |
| `section` | Heading detection (regex `\d+\.\d+`) | Text of heading | Chunk boundary | Section nodes |
| `table` | `page.find_tables()` | HTML or Markdown | Context chunks | Table nodes |
| `image` | `page.get_images()` | Bounding box + page | Skip | Figure nodes |
| `link` | Regex on URLs/file paths | JSON: {url, text, type} | Skip | Reference edges |
| `legend` | Page location + heuristic | Text block | Skip | Legend nodes |
| `note` | Page 1 annotations | Text block | Skip | Annotation nodes |
| `title_block` | I283: drawing-frame title block detection | JSON fields | Frame anchor | Title-block nodes |
| `grid` | I283: drawing grid detection | Coordinates | Skip | Grid nodes |
| `signature_block` | I283: signature block detection | JSON fields | Skip | Signature nodes |

**CRUD operations** (in `registry.py`):

| Method | Description |
|--------|-------------|
| `store_elements(doc_id, elements: list[dict])` | Insert elements for a document |
| `get_elements(doc_id) -> list[dict]` | Retrieve all elements for a document |
| `get_elements_by_type(doc_id, element_type) -> list[dict]` | Filter by type |
| `delete_elements(doc_id)` | Remove all elements for a document |

**Structural completeness scoring**:

```
expected_elements = {cover_page, revision_table, sections, image, table}
detected_count = count(elements where element_type in expected_elements)
structural_completeness = detected_count / len(expected_elements)
```

Document type expectations:

| Document Type | Expected Elements | Threshold |
|---------------|-------------------|:---------:|
| Type A (standard drawing) | cover_page, revision_table, sections, image, table | 5 |
| Type B (standard detail) | cover_page, revision_table, sections, image, table | 5 |
| Type C (scanned) | (none expected) | 0 |
| Type D (volume cover) | cover_page, sections | 2 |
| Type E (specification) | cover_page, sections, table | 3 |

---

## D8. Status Lifecycle

### Pipeline Phase States

The Phase 1 pipeline operates in three phases (A/B/C), each tracked with IN_PROGRESS → COMPLETE transitions:

```
Phase A:  File Discovery      IN_PROGRESS ──► COMPLETE
Phase B:  Parse + Extract     IN_PROGRESS ──► COMPLETE
Phase C:  Review              IN_PROGRESS ──► COMPLETE
```

| Phase | Action | Description |
|-------|--------|-------------|
| **A** | File Discovery | Scan directory, validate file types, register placeholder documents |
| **B** | Parse + Detect + Score | Route files to parsers → detect structural elements → compute health scores → update registry |
| **C** | Review | Flag documents with `extract_status ≠ 'success'` or `extraction_confidence < 0.70` for manual review |

### Document Status States

Each document progresses through a lifecycle during ingestion:

```
NEW ──────► EXTRACTED ──────► REGISTERED ──────► VERIFIED
 │              │                   │                  │
 │ (discover)   │ (extract)         │ (register)       │ (human review)
 │              │                   │                  │
 ▼              ▼                   ▼                  ▼
pending      success/partial    success            verified_by set
```

| State | Meaning | Trigger | Next State |
|-------|---------|---------|------------|
| `NEW` | File discovered, not yet processed | File walk | EXTRACTED |
| `EXTRACTED` | Metadata extracted, not yet registered | Extraction pipeline | REGISTERED |
| `REGISTERED` | In document registry, not yet verified | `register_document()` | VERIFIED |
| `VERIFIED` | Human-validated, project-final | Manual verification (Phase 5) | — |

### Extract Status Values

Stored in `extract_status` column of document registry:

| Value | Meaning | Trigger |
|-------|---------|---------|
| `pending` | Not yet extracted (default) | `register_document()` |
| `success` | All auto-extractable fields populated | Extraction pipeline (score ≥ 0.70) |
| `partial` | Some fields extracted, some missing | Extraction pipeline (score 0.20–0.69) |
| `failed` | Extraction failed entirely | Extraction pipeline (score < 0.20) |

---

## D9. Output Architecture

### D9.1 Summary

The pipeline produces output through four independent channels. This section provides the high-level architecture; D10 describes each channel in detail, D11 covers verbosity control, and D12 covers debugging diagnostics.

```
                    ┌─────────────────────┐
                    │  CLI --level N      │
                    │  (0=silent, 1=norm, │
                    │   2=debug, 3=trace) │
                    └──────────┬──────────┘
                               │ feeds into
              ┌────────────────┼──────────────────┐
              ▼                ▼                  ▼
      ┌──────────────┐ ┌────────────┐ ┌────────────────┐
      │Universal     │ │Message     │ │ErrorManager    │
      │Logger        │ │Manager     │ │(severity→log)  │
      │(4 tiers)     │ │(catalog)   │ │+ fail-fast     │
      └──────┬───────┘ └─────┬──────┘ └───────┬────────┘
             │               │                │
             ▼               ▼                ▼
         print()          print()          print()
         +debug_obj       +icon prefix     +error code
```

**Preload Print (Channel D)** runs before this diagram — pure `print(file=stderr)`, no logger, no level gate.

### D9.2 Logger Implementations

Two logger implementations exist in the codebase. The pipeline uses **UniversalLogger** from the common library:

| Feature | EKSLogger (`eks/engine/`) | UniversalLogger (`common/library/`) |
|:--------|:-------------------------:|:-----------------------------------:|
| Production use | Legacy — not used by `main()` | **Active** — created in `eks_engine_pipeline.py` |
| Verbosity levels | 0–3 | 0–3 |
| `fatal` parameter on `error()` | No | Yes — raises `RuntimeError` |
| `global_parameters` tracking | No | Yes — `track_global_param()` |
| Module-level shim | No | Yes — `log_status()`, `log_error()` etc. |
| Shared depth counter with `log_context` | No | Yes — `depth.py` shares `_depth` |

### D9.3 Telemetry Dual-Channel Architecture

The `PipelineOrchestrator` wires **two** telemetry instances:

| Instance | Class | Scope | Created by |
|:---------|:------|:------|:-----------|
| Local | `eks/engine/core/telemetry.TelemetryHeartbeat` | Per-orchestrator document-level detail | `PipelineOrchestrator.__init__()` |
| External | `common.library.core.pipeline.TelemetryHeartbeat` | Pipeline-level checkpoints shared across components | `main()` — passed into orchestrator as `external_telemetry` |

Both instances receive the same `add_checkpoint()` calls via `_forward_telemetry()`, which forwards checkpoints to local + external. Failure in the external channel is silently caught to avoid blocking the pipeline.

### D9.4 Relationship to the Common Library

EKS output infrastructure is built on shared modules from `common/library/core/`:

| Module | L-Level | Provides |
|:-------|:-------:|:---------|
| `logging/logger.py` | L01 | `UniversalLogger` class |
| `logging/depth.py` | L02 | `log_depth` decorator, `log_context` manager |
| `logging/trace.py` | L03 | `trace_step()`, `track_global_param()` |
| `logging/snapshot.py` | L04 | `get_system_snapshot()` |
| `logging/__init__.py` | — | All four above as a consolidated API |
| `pipeline/heartbeat.py` | L05 | Universal `TelemetryHeartbeat` + `DocumentProcessingHeartbeat` |
| `core/messages/message_manager.py` | L11 | `BaseMessageManager` ABC with catalog loading, template hydration, verbosity gate |

---

## D10. Output Channels in Detail

### D10.1 UniversalLogger — Direct Console Logging (Channel A)

#### D10.1.1 Log Level Definitions

| Level | Name | Description | CLI Equivalent |
|:-----:|:-----|:------------|:---------------|
| 0 | Silent | Only fatal errors printed | `--level 0` |
| 1 | Normal | Milestones + high-level status (default) | `--level 1` |
| 2 | Debug | Warnings + internal state | `--level 2` / `--debug` |
| 3 | Trace | Deep technical info, raw JSON | `--level 3` / `--verbose` |

#### D10.1.2 Available Methods

| Method | Level | Category Tag | Purpose |
|:-------|:-----:|:-------------|:--------|
| `error(msg, context, fatal=False)` | 0 | `ERROR` | Always visible. If `fatal=True`, raises `RuntimeError` after printing. |
| `status(msg, context)` | 1 | `STATUS` | Milestone progress, high-level workflow status. |
| `info(msg, context)` | 1 | `INFO` | General informational messages. |
| `warning(msg, context)` | 2 | `WARNING` | Warnings, degraded quality, fallback paths. |
| `debug(msg, context)` | 2 | `DEBUG` | Variable values, path resolutions, internal state. |
| `trace(msg, context)` | 3 | `TRACE` | Deep technical detail (OS paths, raw extraction). |

#### D10.1.3 Output Format

```
{timestamp} | {category:7} | {name}[{context}] | {indent}{message}
```

Example output at level 1:
```
2026-07-27 14:30:01.234 | STATUS  | eks-pipeline | Phase A complete: 42 files registered
2026-07-27 14:30:01.456 | INFO    | eks-pipeline[data:P5-F-V-0001] | [file.pdf] File type not supported
```

Indentation is controlled by the global `_depth` counter, incremented by the `log_depth` decorator and `log_context` manager (see D12.3).

#### D10.1.4 Debug Object Accumulation

All log entries (regardless of level) **should** be appended to `logger.debug_object["logs"]` in memory — the design principle is **record-before-gate**: always save to the debug object, then gate only the console `print()` by verbosity level. This ensures post-run diagnostics can inspect suppressed messages even when running at `--level 0`. However, as of v2.0, `UniversalLogger._log()` gates recording + printing at the same point (I249). The fix is to reorder: record first, gate print second. The debug object is persisted to `debug_log.json` via `logger.save()` at pipeline completion.

At default `--level 1`, per-document messages are suppressed. The pipeline entry point prints a startup notice directing users to `--level 2` or `debug_log.json` for full diagnostics:

```
Per-document details suppressed at default level.
Use --level 2 (--debug) for per-file messages,
or check debug_log.json for full diagnostics.
```

### D10.2 MessageManager — Catalog-Driven Messages (Channel B)

Messages are defined in `eks_message_config.json` with this schema:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique message identifier (UPPER_SNAKE_CASE) |
| `category` | enum | `milestone`, `status`, `progress`, `warning`, `error` |
| `level` | integer | Verbosity: 0=error, 1=normal/status, 2=debug, 3=trace |
| `template` | string | Python-style template with `{placeholders}` |
| `icon` | string | Display icon (optional, e.g. ▶ ✓ ℹ ⚠) |

#### D10.2.1 Category-to-Logger Routing

When `MessageManager.show(msg_id, **kwargs)` is called, it looks up the message definition and routes to a logger method based on category:

| `category` | Logger method | Example |
|:-----------|:--------------|:--------|
| `milestone` | `logger.status()` | `=== Phase A Start: File Discovery ===` |
| `warning` | `logger.warning()` | `Scanned PDF detected (no text layer): {filename}` |
| `error` | `logger.error()` | `Error processing {filename}: {detail}` |
| `status` | `logger.info()` | `Parsing: {filename}` |
| `progress` | `logger.info()` | `  {filename}` (indented sub-step) |

If the message has an `icon` field, it is prepended: `{icon} {hydrated_template}`.

The level gate is `msg_def.level ≤ manager.verbosity`. If the level check fails, `show()` returns silently — no log entry is created.

### D10.3 ErrorManager — Error Code Output (Channel C)

The ErrorManager is an **orchestrator-level component**. It serves three purposes, all scoped to pipeline orchestration:

| Purpose | Description | Scope |
|:--------|:------------|:------|
| **Fail-fast** | Raise `RuntimeError` for unrecoverable errors (missing config, bootstrap failure) | Pipeline infrastructure — not per-document |
| **Health impact** | Accumulate `health_score_impact` per-document and adjust final health scores | Called after `HealthScorer.score()` in the orchestration loop |
| **Error summary** | Return counts of errors by severity for pipeline-level reporting | Pipeline completion |

Sub-modules (`filename_parser.py`, `file_property_parser.py`, parsers, etc.) use `logger.warning()` directly — not ErrorManager. This is by design: per-document validation warnings should never trigger fail-fast, their health impact is already captured by the completeness dimension in the health scorer, and all log entries are recorded in `debug_log.json` regardless of verbosity level. See D13.1 for the full rationale.

Error codes are defined in `eks_error_config.json` with two domains: system errors (`S-{cat}-S-{id}`) and data errors (`P{phase}-{module}-{function}-{id}`).

#### D10.3.1 Severity-to-Logger Routing

| Severity | handle_system_error | handle_data_error | Stops Pipeline? |
|:---------|:--------------------|:------------------|:---------------:|
| FATAL | `logger.error()` | `logger.error()` | Yes (fail-fast) |
| CRITICAL | `logger.error()` | `logger.error()` | Yes (fail-fast) |
| HIGH | `logger.warning()` | `logger.warning()` | No |
| WARNING | `logger.warning()` | `logger.info()` | No |
| INFO | `logger.warning()` | `logger.info()` | No |

**Note**: `handle_data_error` maps WARNING→`logger.info()` (level 1) while `handle_system_error` maps WARNING→`logger.warning()` (level 2). The three data errors that were problematic (P3-E-E-0018, P3-E-E-0019, P5-R-P-0003) were bumped from WARNING to HIGH severity (T1.135), routing them through `logger.warning()` at level 2 instead. Remaining WARNING-severity data errors at `logger.info()` are less impactful — they are INFO-level fields where missing data is expected (e.g., optional metadata).

#### D10.3.2 Fail-Fast Mechanism

When `error_manager._fail_fast_enabled` is `True` (default, read from `system_parameters.fail_fast`) and the error has `stops_pipeline: true`, the ErrorManager raises `RuntimeError(f"FAIL_FAST [{code}]: {message}")` after logging. This immediately stops the pipeline.

#### D10.3.3 Health Score Impact

Each data error has a `health_score_impact` field (−1 to −5). The ErrorManager accumulates these per-document:

```python
impact = sum(err["health_score_impact"] for err in errors if err["doc_id"] == target_doc)
adjusted_health = max(0.0, raw_health_score + impact / 100.0)
```

### D10.4 Preload Print — Pre-Bootstrap Output (Channel D)

Before any logger, message manager, or error manager exists, the pipeline entry point uses raw `print()` to stderr:

```python
print(f"FATAL: {err}", file=sys.stderr)
```

This is the **only** output channel during `_preload_infrastructure()`. It has:
- **No level gate** — always visible
- **No formatting** — raw plain text
- **No debug object** — not captured for diagnostics

Used for: missing `common.library` imports, Python version mismatch, project root not found.

---

## D11. Verbosity Control & Data Flow

### D11.1 CLI Flags

| Flag | Effect | Internal Level |
|:-----|:-------|:--------------:|
| `--level 0` | Silent — only fatal errors | 0 |
| `(default)` | Normal — milestones + info | 1 |
| `--level 2` / `--debug` | Debug — warnings + variable values | 2 |
| `--level 3` / `--verbose` | Trace — deep technical detail | 3 |

### D11.2 Verbosity Level Matrix

What fires at each level across all four channels. At default `--level 1`, the pipeline prints a startup notice:

```
Per-document details suppressed at default level.
Use --level 2 (--debug) for per-file messages,
or check debug_log.json for full diagnostics.
```

| Level | Logger (Ch A) | Messages (Ch B) | ErrorManager (Ch C) | Preload (Ch D) | Telemetry |
|:-----:|:--------------|:----------------|:--------------------|:---------------|:----------|
| **0** | `error()` only | Messages with `level: 0` (ERROR category) | FATAL / CRITICAL only | Always visible | Disabled |
| **1** | `error()` + `status()` + `info()` | Messages with `level ≤ 1` (milestones, status, progress, WARNING, ERROR) | All severities — but WARNING data→`info()` (level 1), HIGH system→`warning()` (level 2) | Always visible | Disabled |
| **2** | All except `trace()` | Messages with `level ≤ 2` (all categories) | All severities — HIGH/WARNING via `warning()` (level 2) | Always visible | **Enabled** |
| **3** | All methods including `trace()` | Messages with `level ≤ 3` (all) | All severities | Always visible | Enabled |

**Note**: At default level 1, WARNING-severity system errors (S-C-S-0305, S-C-S-0306, S-A-S-0501–0503) are suppressed because `handle_system_error` routes WARNING→`logger.warning()` (level 2). WARNING-severity data errors are visible because `handle_data_error` routes WARNING→`logger.info()` (level 1). The three problematic data errors (P3-E-E-0018, P3-E-E-0019, P5-R-P-0003) were bumped to HIGH severity (T1.135) so they route through `logger.warning()` at level 2.

### D11.3 Data Flow: `--level` Through the System

```
CLI args  ──►  _parse_early_verbosity()     [pure argparse, before bootstrap]
                    │
                    ▼
              early_level  ──►  UniversalLogger(level=early_level)
                           ──►  TelemetryHeartbeat(enabled=early_level >= 2)
                           ──►  EKSBootstrapManager(logger=logger)
                                    │
                                    ▼
                                bootstrap_all()
                                P2: CLI parse → resolved level from schema
                                    │
                                    ▼
                                mgr.effective_parameters["level"]
                                    │
                         ┌──────────┴──────────┐
                         ▼                     ▼
                   MessageManager           (logger stays at
                   .verbosity = level        early_level)
                         │
                         ▼
                   PipelineOrchestrator
                   (error_manager + message_manager injected)
                         │
                         ▼
                   run_phase_a/b/c()
                   em.handle_data_error(code, ...)
                   mm.show(msg_id, ...)
```

### D11.4 Known Gap: Verbosity Reconciliation

When bootstrap resolves a `level` different from `early_level` (e.g., a config file overrides the CLI default), the `TelemetryHeartbeat` is recreated with the new level, but **`UniversalLogger.level` is not updated** — it stays at `early_level`. This means:

- `logger.warning()` (level 2) may fire at the wrong threshold
- `message_manager.verbosity` is at default `1` — the resolved level is never passed to the MessageManager at all (hardcoded in `_eks_message_factory()`)

**Planned fixes**:
- T1.136: Add `mm.set_verbosity(level)` after level reconcile in `main()` so the MessageManager respects `--level 0/2/3`
- I249: Add `logger.set_level(level)` after reconcile and fix `UniversalLogger._log()` to record before gating print

---

## D12. Debugging & Diagnostics

### D12.1 Debug Object Schema

The `UniversalLogger` maintains a structured debug object in memory throughout the pipeline run. All log entries, errors, trace steps, and global parameters **should** be recorded regardless of verbosity level (record-before-gate principle, see I249 for current implementation gap).

```json
{
  "project": "eks-pipeline",
  "start_time": "2026-07-27T14:30:00",
  "end_time": "2026-07-27T14:35:12",
  "duration_ms": 312000,
  "system_snapshot": {
    "os": "win32",
    "python_version": "3.10.12",
    "cpu_count": 16,
    "memory_total": 34359738368,
    "cwd": "C:\\Users\\...\\EKS"
  },
  "trace_table": [
    {
      "timestamp": "2026-07-27T14:30:01",
      "step": "parse_filename",
      "parameter": "document_number",
      "value": "131101-WSW41-DR-C-0001",
      "source": "filename_parser.py",
      "status": "SUCCESS",
      "duration_ms": 2.5,
      "depth": 3
    }
  ],
  "global_parameters": {
    "level": {"post_cli": {"value": "1", "timestamp": "..."},
              "post_bootstrap": {"value": "1", "timestamp": "..."}},
    "data_dir": {"post_cli": {"value": "C:\\...\\data", "timestamp": "..."}}
  },
  "logs": [
    {
      "timestamp": "2026-07-27T14:30:01.234",
      "level": 1,
      "category": "STATUS",
      "context": null,
      "module": "eks-pipeline",
      "message": "Phase A complete: 42 files registered"
    }
  ],
  "errors": [
    {
      "timestamp": "2026-07-27T14:31:05",
      "context": "data:P5-F-V-0001",
      "message": "[file.pdf] File type not supported",
      "fatal": false
    }
  ]
}
```

### D12.2 Trace Table

The `trace_table` is populated via `logger.trace_step()` and the module-level `trace_step()` / `track_global_param()` functions from `common.library.core.logging.trace`. Each entry captures:

| Field | Description |
|:------|:------------|
| `step` | Logical step name (e.g. `"load_schema"`, `"parse_filename"`) |
| `parameter` | Variable or parameter name being traced |
| `value` | String value (truncated to 200 chars) |
| `source` | Origin module or function |
| `status` | `SUCCESS`, `FAIL`, `SKIP`, etc. |
| `duration_ms` | Elapsed time in milliseconds |
| `depth` | Call depth at recording time |

`track_global_param()` records a named parameter's value at a named pipeline stage, stored under `debug_object["global_parameters"][name][stage]`. This enables cross-phase parameter flow tracing.

### D12.3 Call Depth Tracking

Two forms share the global `_depth` counter:

| Form | Type | Usage |
|:-----|:-----|:------|
| `@log_depth` | Decorator | Applied to methods; auto-increments before call, decrements after |
| `log_context()` | Context manager | Wraps a `with` block; auto-increments on entry, decrements on exit, logs entry/exit with timing |

The depth counter controls indentation in the output format. Each level adds `"  "` (two spaces):

```
2026-07-27 14:30:01 | STATUS | PipelineOrchestrator | Phase B: Parsing files
2026-07-27 14:30:02 | INFO   | PipelineOrchestrator |   Parsing: 131101-WSW41-DR-C-0001.pdf
2026-07-27 14:30:03 | INFO   | PipelineOrchestrator |   Parsing: 131101-WIL00-DR-E-7000.pdf
```

### D12.4 Debug Log File Lifecycle

1. Logger is created with optional `debug_file` path
2. All entries accumulate in memory in `logger.debug_object`
3. At pipeline completion, `logger.save()` is called:
   - Sets `end_time` and `duration_ms`
   - Creates parent directories if needed
   - Writes `debug_log.json` with `json.dumps(indent=2)`
4. The file is a single overwrite — per-job accumulation is not supported (per I124)

### D12.5 DCC Backward-Compatibility Shims

For projects migrating from the DCC module-level API, `common.library.core.logging.logger` provides:

| Function | Delegates to |
|:---------|:-------------|
| `log_status(msg, module, context)` | `get_global_logger().status()` |
| `log_warning(msg, module, context)` | `get_global_logger().warning()` |
| `log_error(msg, module, context, fatal)` | `get_global_logger().error()` |
| `log_trace(msg, module, context)` | `get_global_logger().trace()` |

These access a process-wide `UniversalLogger` singleton via `get_global_logger()` / `set_global_logger()`.

---

## D13. Known Gaps & Open Issues

| Issue | Severity | Title | Status |
|:------|:--------:|:------|:-----:|
| I245 | 🟡 Medium | Sub-modules lack ErrorManager wiring — 44 data + 58 system codes catalog-only | ⛔ Won't Implement |
| I246 | 🟢 Low | Message catalog under-deployed — 39 of 49 messages never emitted | 🔴 Open |
| I247 | 🟢 Low | Config metadata miscount — `data_logic_codes: 48` should be `50` | 🔴 Open |
| I248 | 🟡 Medium | Pipeline batch health scoring not wired — `score_batch()` never called | 🔴 Open |
| I249 | 🟡 Medium | UniversalLogger level not reconciled after bootstrap; `_log()` gates record + print together | 🔴 Open |

### D13.1 Sub-module ErrorManager Wiring (I245)

**Decision**: ⛔ Won't Implement (I245). The current design is correct — ErrorManager is an orchestrator-level component, not a sub-module utility. Rationale:

1. **Fail-fast is for infrastructure errors, not per-document warnings** — A filename parsing warning or missing optional metadata should never stop the pipeline. Only orchestrator-level errors (missing config, bootstrap failure) warrant fail-fast.
2. **Health score impact is already captured by completeness dimension** — The health scorer measures 39 scorable columns. A missing field due to a parser error is automatically reflected in the completeness score. Wiring ErrorManager would add redundant double-counting.
3. **All `logger.warning()` calls are captured in `debug_log.json`** — The debug object records every log entry regardless of verbosity level (T1.138). Post-run diagnostics have full detail.
4. **Utility classes lack ErrorManager injection** — `filename_parser` and `file_property_parser` are schema-driven utility classes. Adding ErrorManager injection would add coupling without meaningful benefit.
5. **Bootstrap already uses the correct mechanism** — `BootstrapError` from `common.library.bootstrap` is the designed path for bootstrap-phase errors.

The error codes remain registered in `eks_error_config.json` for documentation, cross-reference, and searchability.

### D13.2 Message Catalog Under-Deployment (I246)

**Root cause**: Only `pipeline_orchestrator.py` calls `message_manager.show()`. No other module (bootstrap, scanners, parsers, extractors) emits catalog messages.

**Impact**: 39 of 49 registered messages are catalog-only. The message system works end-to-end only for Phase A/B/C milestones and one error message.

### D13.3 Verbosity Reconciliation Gap (I249 — partially resolved)

**Root cause**: Three independent gaps prevented verbosity level from being consistently applied.

**Resolved (T1.136)**: `logger.set_level(level)` and `mm.set_verbosity(level)` added after bootstrap reconcile in `main()`. Both Logger and MessageManager now respect `--level 0/2/3`. A startup message directs users to `--level 2` or `debug_log.json` for detailed diagnostics.

**Remaining**: Logger created with `early_level` still not updated if bootstrap resolves a different level — `logger.set_level(level)` runs, which updates the instance, so this is fully resolved.

### D13.4 Batch Health Scoring Not Wired (I248)

**Root cause**: `health_scorer.score_batch()` exists but is never called from any pipeline code. Appendix D §D7.7 defines pipeline-level health grades (A+ through F) with the formula `(total_docs - critical_errors - high_errors) / total_docs × 100` — none of this is executed.

**Impact**: Pipeline-level health metrics and grades are design artifacts only; no consumer exists.

### D13.5 UniversalLogger Record-Before-Gate (I249 — resolved)

**Root cause**: `UniversalLogger._log()` checked the level gate before appending to `debug_object["logs"]` — entries above verbosity were neither printed NOR saved.

**Resolution (T1.138)**: Reordered `_log()` to always append to `debug_object["logs"]` first, then gate only the `print()`. All log entries are now saved regardless of verbosity level. Post-run diagnostics at `--level 0` have complete `debug_object["logs"]` data.

## D14. Implementation Files

### Config Files

| File | Purpose |
|------|---------|
| `eks/config/schemas/eks_error_config.json` | Error code catalog — 111 codes (61 system + 50 data) |
| `eks/config/schemas/eks_message_config.json` | Message catalog — 49 pipeline messages |
| `eks/config/schemas/eks_doc_base_schema.json` | Document registry schema definitions + x_export flags |
| `eks/config/schemas/eks_doc_config.json` | Document config with filename_patterns + file_property_patterns |
| `eks/config/schemas/eks_config.json` | Pipeline configuration with global_paths + system_parameters |

### Engine Modules — Core Pipeline

| File | Purpose |
|------|---------|
| `eks/engine/eks_engine_pipeline.py` | **Main entry point** — CLI, bootstrap_pipeline(), run_pipeline(), _preload_infrastructure(), export helpers |
| `eks/engine/core/pipeline_orchestrator.py` | **Phase A/B/C orchestrator** — run_phase_a/b/c, run_full_pipeline, _process_file |
| `eks/engine/core/bootstrap.py` | EKSBootstrapManager — readiness gate, config loading, path resolution |
| `eks/engine/core/registry.py` | DocumentRegistry — CRUD, store_elements, get_elements, update_document_status |
| `eks/engine/core/health_scorer.py` | 6-dimension per-document health scoring engine |
| `eks/engine/core/structure_detector.py` | PDF structural element detection (cover page, revision table, sections, tables, images, links, legend, notes) |
| `eks/engine/core/review_manager.py` | ManualReviewManager — flagged docs, metadata correction, element confirmation, recalculation |
| `eks/engine/core/error_manager.py` | ErrorManager — handle_system_error, handle_data_error, get_health_impact |
| `eks/engine/core/message_manager.py` | MessageManager — catalog lookup, template hydration, verbosity control |
| `eks/engine/core/filename_parser.py` | FilenameParser — schema-driven filename-to-field extraction (Appendix I) |
| `eks/engine/core/file_property_parser.py` | FilePropertyExtractor — OS stat + embedded metadata extraction (Appendix J) |
| `eks/engine/core/context.py` | EKSPipelineContext + EKSPaths + EKSData |
| `eks/engine/core/file_scanner.py` | FileScanner — directory walk, file type validation, placeholder registration |
| `eks/engine/parsers/parser_router.py` | ParserRouter — route file to correct parser by type |

### Common Library — Universal Infrastructure

| File | Purpose |
|------|---------|
| `common/library/bootstrap/manager.py` | Universal L19 BootstrapManager (8-phase orchestrator) |
| `common/library/bootstrap/errors.py` | Universal BootstrapError (code/message/phase, to_system_error()) |
| `common/library/paths/root_discovery.py` | discover_project_root() — anchor-verified project root discovery |
| `common/library/paths/path_utils.py` | safe_posix(), should_auto_create_folders() |
| `common/library/cli/__init__.py` | build_parser_from_schema(), parse_cli_args() |
| `common/library/export/__init__.py` | DataExporter — CSV + Excel export |
| `common/library/utility/file_hash.py` | compute_file_hash() — SHA-256 chunked hash |

---

## D15. References

1. [AGENTS.md §19](../../AGENTS.md) — "Each business logic must have an independent error code defined"
2. [AGENTS.md §12](../../AGENTS.md) — Debugging: tiered logging, debug object, fail-fast
3. [AGENTS.md §8](../../AGENTS.md) — Messaging and errors: status, errors, warnings, data quality
4. [AGENTS.md §10](../../AGENTS.md) — SSOT: single source of truth for error/message codes
5. [Appendix B](appendix_b_document_registry.md) — Document registry schema
6. [DCC Error Code Pattern](../../dcc/config/schemas/error_code_base.json) — Reference for `P{phase}-{module}-{function}-{id}` format
7. [DCC Pipeline Messages](../../dcc/config/schemas/pipeline_message_base.json) — Reference for message catalog structure
8. [`eks/config/schemas/eks_error_config.json`](../config/schemas/eks_error_config.json) — Authoritative error code source (v1.3.0)
9. [`eks/config/schemas/eks_message_config.json`](../config/schemas/eks_message_config.json) — Authoritative message source (v1.1.0)
10. [`eks/engine/core/health_scorer.py`](../engine/core/health_scorer.py) — Health scoring implementation
11. [`eks/engine/eks_engine_pipeline.py`](../engine/eks_engine_pipeline.py) — Main pipeline entry point
12. [`common/library/bootstrap/manager.py`](../../common/library/bootstrap/manager.py) — Universal bootstrap manager
13. [`common/library/core/logging/logger.py`](../../common/library/core/logging/logger.py) — UniversalLogger implementation
14. [`common/library/core/logging/depth.py`](../../common/library/core/logging/depth.py) — log_depth / log_context
15. [`common/library/core/logging/trace.py`](../../common/library/core/logging/trace.py) — trace_step / track_global_param
16. [`common/library/core/pipeline/heartbeat.py`](../../common/library/core/pipeline/heartbeat.py) — Universal TelemetryHeartbeat
17. [`eks/engine/core/telemetry.py`](../engine/core/telemetry.py) — EKS TelemetryHeartbeat
18. [`eks/engine/logging/logger.py`](../engine/logging/logger.py) — Legacy EKSLogger
19. [`eks/log/issue_log.md`](../log/issue_log.md) — I244–I248 gap tracking

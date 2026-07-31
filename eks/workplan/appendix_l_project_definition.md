# Appendix L — Workplan: Project Definition Architecture Refactoring (Issue I265)

## L.1 Objective

Establish **`eks_project_definition_schema.json`** as the **Single Source of Truth (SSOT)** for all project-specific configuration.

The Project Definition shall consolidate all project-specific metadata, engineering settings, document processing policies, asset processing policies, ontology selection, pipeline behaviour, retrieval behaviour, security settings, and integration settings into a single authoritative schema.

Introduce **ProjectDefinitionResolver** as a common EKS pipeline component responsible for constructing an immutable **RuntimeProjectConfiguration**, which becomes the only runtime configuration object consumed by the EKS pipeline.

This work supersedes the earlier proposal to introduce `eks_project_rules_config.json`. Project-specific rules shall instead be integrated into the Project Definition.

> **Naming (T1.196/I269)**: The authoritative Project Definition is implemented as
> `eks_project_definition_config.json` (instance values) with its definitions in
> `eks_base_schema.json` (`project_definition_registry_def`,
> `project_definition_entry_def`). The proposed name `eks_project_definition_schema.json`
> is not a file on disk — references to it in I265 and the L.12 task rows denote this
> same Project Definition SSOT. `eks_project_rules_config.json` was retired in T1.196.

---

# L.2 Scope

This work extends the following completed architecture:

| Issue | Description                             |
| ----- | --------------------------------------- |
| I255  | Project code auto-detection             |
| I256  | Project configuration architecture      |
| I261  | SchemaLoader Stage 1–4 architecture     |
| I263  | Schema validation framework             |
| I264  | Column processing metadata architecture |

This work shall **extend** these implementations without redesigning or duplicating them.

---

# L.3 Problem Statement

Project-specific configuration is currently distributed across multiple configuration files.

Examples include:

* project metadata
* filename pattern mapping
* revision validation
* parser configuration
* project processing rules

This results in:

* duplicated project identifiers
* split configuration ownership
* duplicated configuration loading
* duplicated project registries
* inconsistent project onboarding
* SSOT violations

---

# L.4 Target Architecture

```text
                     Shared Framework
                  ┌──────────────────────┐
                  │     SchemaLoader     │
                  └──────────┬───────────┘
                             │
                   Raw validated schemas
                             │
                             ▼
                ProjectDefinitionResolver
                             │
                Resolve reusable profiles
                             │
                             ▼
               RuntimeProjectConfiguration
                             │
      ┌──────────────────────┼──────────────────────┐
      ▼                      ▼                      ▼
 FilenameParser      ColumnProcessor        Asset Loader
      ▼                      ▼                      ▼
  Retriever             Pipeline            Other Modules
```

---

# L.5 Architecture Principles

* Single Source of Truth (SSOT)
* Separation of Concerns
* Layered Architecture
* Immutable Runtime Configuration
* Configuration over Code
* Reusable Profile Libraries
* Backward Compatibility

---

# L.6 Configuration Ownership

The EKS configuration architecture separates **project-specific semantics**, **reusable configuration profiles**, and **deployment-specific infrastructure** into distinct ownership boundaries.

This separation ensures:

* Single Source of Truth (SSOT)
* Separation of Concerns
* Reusable configuration libraries
* Environment-independent project definitions
* Consistent runtime configuration assembly
* Simplified project onboarding

Only **ProjectDefinitionResolver** shall assemble these configuration sources into a fully resolved **RuntimeProjectConfiguration**.

---

## L.6.1 Project Definition

File

```text
eks_project_definition_schema.json
```

The Project Definition is the authoritative source for all configuration that is unique to a specific engineering project.

Each project definition shall describe the engineering semantics, processing behaviour, validation policies, and reusable profile selections required to process documents belonging to that project.

Typical sections include:

```text
Project Definition

├── project_identity
├── project_lifecycle
├── engineering_convention
├── engineering_standards
├── document_profile
├── parsing_profile
├── chunking_profile
├── embedding_profile
├── metadata_policy
├── asset_profile
├── ontology_profile
├── retrieval_profile
├── prompt_profile
├── validation_profile
├── security_profile
├── runtime_profiles
├── compatibility
└── fragment_required_fields
```

The Project Definition owns:

* project identity
* project lifecycle information
* engineering conventions
* engineering standards
* document processing profile selection
* parsing profile selection
* chunking profile selection
* embedding profile selection
* metadata inheritance policy
* ontology selection
* asset processing profile selection
* retrieval behaviour selection
* AI prompt profile selection
* validation policy selection
* security policy selection
* runtime profile references
* project-specific fragment requirements

The Project Definition shall not duplicate reusable profile definitions.

Instead, it shall reference reusable profiles by identifier.

Example

```text
document_profile

↓

technip_pdf
```

The referenced profile shall be resolved by ProjectDefinitionResolver during runtime initialization.

---

## L.6.2 Reusable Configuration Libraries

Reusable configuration libraries contain shared configuration definitions that may be referenced by multiple projects.

Examples include:

* `eks_doc_config.json`
* `eks_parser_profiles.json`
* `eks_chunking_profiles.json`
* `eks_embedding_profiles.json`
* `eks_asset_profiles.json`
* `eks_ontology_profiles.json`
* `eks_retrieval_profiles.json`
* `eks_prompt_profiles.json`
* `eks_validation_profiles.json`
* future reusable libraries

> **Implementation note (T1.195 V2 / T1.196 I271)**: reusable profile libraries are
> implemented as sections of `eks_doc_config.json` (e.g. `parsing_profiles`) rather
> than separate `eks_parser_profiles.json` files; `ProjectDefinitionResolver`
> resolves them by exact key (`_resolve_profile`) and compares capabilities
> generically. The chunking / embedding / asset / ontology / retrieval / prompt /
> validation profile sections are declared by this architecture but not yet
> populated — deferred to their consuming phases.

These libraries own reusable configuration only.

Typical reusable definitions include:

* filename patterns
* parser profiles
* OCR profiles
* title block profiles
* revision extraction profiles
* chunking strategies
* embedding models
* reranking strategies
* ontology definitions
* asset extraction rules
* retrieval configurations
* AI prompt templates
* validation policies

Reusable configuration libraries shall not contain:

* project codes
* client names
* project-specific document mappings
* project-specific engineering conventions
* project-specific validation rules

Reusable libraries shall remain completely independent of individual projects.

---

## L.6.3 Environment Configuration

Deployment-specific configuration shall be maintained separately from the Project Definition.

Typical environment configuration includes:

```text
Environment

├── storage
├── vector_database
├── graph_database
├── messaging
├── authentication
├── monitoring
└── logging
```

Examples include:

* Neo4j connection
* Qdrant connection
* PostgreSQL connection
* object storage location
* message broker
* API endpoints
* authentication credentials
* deployment settings

Environment configuration shall not contain project-specific engineering information.

The same Project Definition shall be deployable across Development, Test, Staging, and Production environments without modification.

---

## L.6.4 Runtime Configuration Assembly

ProjectDefinitionResolver is responsible for assembling the runtime configuration.

The configuration assembly process is illustrated below.

```text
Environment Configuration
                │
                ▼
Project Definition
                │
                ▼
Reusable Configuration Libraries
                │
                ▼
ProjectDefinitionResolver
                │
                ▼
RuntimeProjectConfiguration
```

ProjectDefinitionResolver shall:

* load `eks_project_definition_config.json`
* load every configured Project Definition
* resolve reusable configuration profile references
* apply runtime environment profiles
* merge project-specific and reusable configuration
* validate the complete resolved configuration
* construct a RuntimeProjectConfiguration for each project
* register every RuntimeProjectConfiguration in the Project Configuration Registry

After construction, RuntimeProjectConfiguration shall contain only fully resolved runtime configuration.

No reusable profile identifiers shall remain.

Runtime modules shall consume RuntimeProjectConfiguration exclusively and shall not load configuration files directly.

---

# L.7 Component Responsibilities

## L.7.1 SchemaLoader

SchemaLoader is a shared framework component responsible for loading and validating configuration schemas.

Responsibilities include:

* loading JSON schema documents;
* validating schema structure;
* caching loaded schemas;
* resolving generic schema references (`$ref`);
* providing validated schema objects to EKS components.

SchemaLoader shall remain independent of EKS business logic.

SchemaLoader shall not:

* interpret project semantics;
* resolve reusable configuration profiles;
* construct runtime configuration;
* determine project ownership.

---

## L.7.2 ProjectDefinitionResolver

ProjectDefinitionResolver is the configuration orchestration component for the EKS platform.

Its responsibility is to transform Project Definitions into validated runtime configuration that can be consumed by the document processing pipeline.

Unlike runtime modules, ProjectDefinitionResolver operates during pipeline initialization and configuration loading.

---

### Responsibilities

ProjectDefinitionResolver shall:

* load `eks_project_definition_config.json`;
* load every configured Project Definition;
* resolve reusable configuration profile references;
* apply runtime environment profiles;
* merge project-specific and reusable configuration;
* validate the complete resolved configuration;
* construct a RuntimeProjectConfiguration for each project;
* register every RuntimeProjectConfiguration in the Project Configuration Registry.

ProjectDefinitionResolver shall not:

* determine which project a document belongs to;
* parse engineering documents;
* extract metadata;
* execute pipeline processing;
* build knowledge graphs;
* generate embeddings;
* communicate with AI models.

---

### Configuration Resolution Workflow

ProjectDefinitionResolver performs the following workflow during pipeline initialization.

```text
eks_project_definition_config.json
                │
                ▼
Load Project Definitions
                │
                ▼
Resolve Reusable Profiles
                │
                ▼
Apply Environment Configuration
                │
                ▼
Merge Configuration
                │
                ▼
Validate Configuration
                │
                ▼
Construct RuntimeProjectConfiguration
                │
                ▼
Register Project Configuration
```

This process shall be completed before runtime modules are instantiated.

---

### Project Configuration Registry

ProjectDefinitionResolver shall maintain a Project Configuration Registry.

The registry contains one RuntimeProjectConfiguration for each configured project.

Example

```text
Project Configuration Registry
│
├── TECHNIP
│      └── RuntimeProjectConfiguration
│
├── JGC
│      └── RuntimeProjectConfiguration
│
├── SAMSUNG
│      └── RuntimeProjectConfiguration
│
└── SHELL
       └── RuntimeProjectConfiguration
```

The registry shall remain immutable after construction.

Runtime modules shall not modify registry contents.

---

### Project Selection

ProjectDefinitionResolver shall not determine the project associated with a document.

Project identification is a responsibility of the document processing pipeline.

During Phase 1, the pipeline scans and registers engineering documents without assigning a project.

Project identification may occur later using project-specific rules such as:

* filename conventions;
* document numbering;
* directory structure;
* title block metadata;
* engineering metadata.

Once a project has been identified, the corresponding RuntimeProjectConfiguration shall be retrieved from the Project Configuration Registry and supplied to downstream processing modules.

This separation allows configuration management and document classification to evolve independently.

---

### Runtime Configuration Access

Runtime modules shall obtain configuration exclusively from the Project Configuration Registry.

They shall not:

* reload Project Definitions;
* access reusable configuration libraries;
* resolve profile identifiers;
* reconstruct runtime configuration.

All runtime configuration shall originate from ProjectDefinitionResolver.

---

### Architectural Responsibilities

| Component | Responsibility |
|-----------|----------------|
| SchemaLoader | Load and validate schema documents |
| ProjectDefinitionResolver | Resolve configuration and construct the Project Configuration Registry |
| Project Configuration Registry | Store immutable RuntimeProjectConfiguration objects |
| Runtime Modules | Consume RuntimeProjectConfiguration and perform business processing |

Each architectural responsibility shall exist in only one component.

---

# L.8 RuntimeProjectConfiguration

## L.8.1 Overview

`RuntimeProjectConfiguration` is the immutable runtime representation of a resolved Project Definition.

It is produced by `ProjectDefinitionResolver` after:

* loading the Project Definition;
* resolving reusable configuration profiles;
* applying environment configuration;
* validating configuration consistency; and
* constructing strongly typed runtime configuration objects.

Each configured project shall have exactly one `RuntimeProjectConfiguration` registered within the Project Configuration Registry.

Runtime modules shall consume only `RuntimeProjectConfiguration`.

They shall never access Project Definitions directly.

---

## L.8.2 Design Principles

RuntimeProjectConfiguration shall satisfy the following principles.

| Principle | Description |
|-----------|-------------|
| Immutable | Cannot be modified after construction |
| Fully Resolved | Contains no unresolved profile references |
| Strongly Typed | Runtime objects instead of raw JSON |
| Self-Contained | Independent of Project Definition files |
| Deterministic | Identical configuration produces identical runtime configuration |
| Thread Safe | Safe for concurrent access |
| Extensible | New configuration domains can be added without breaking existing modules |

---

## L.8.3 Runtime Configuration Structure

RuntimeProjectConfiguration shall expose the following configuration domains.

```text
RuntimeProjectConfiguration
│
├── project
├── lifecycle
├── engineering
├── standards
├── document
├── parsing
├── chunking
├── embeddings
├── metadata
├── assets
├── ontology
├── retrieval
├── prompts
├── validation
├── security
├── runtime_profiles
└── runtime
```

Each configuration domain shall represent a single logical responsibility.

---

## L.8.4 Configuration Domains

| Configuration Domain | Responsibility |
|----------------------|----------------|
| project | Project identity and business context |
| lifecycle | Project lifecycle information |
| engineering | Engineering conventions |
| standards | Applicable engineering standards |
| document | Document processing rules |
| parsing | Parser and OCR configuration |
| chunking | Document fragmentation strategy |
| embeddings | Embedding generation configuration |
| metadata | Metadata extraction and inheritance |
| assets | Engineering asset extraction |
| ontology | Knowledge graph configuration |
| retrieval | Search and retrieval configuration |
| prompts | AI prompt templates and policies |
| validation | Validation policies |
| security | Security and access policies |
| runtime_profiles | Runtime infrastructure services |
| runtime | Runtime metadata |

---

## L.8.5 Runtime Metadata

The `runtime` configuration domain contains metadata generated during runtime configuration construction.

Typical metadata includes:

* configuration version;
* schema version;
* configuration checksum;
* build timestamp;
* resolved profile list;
* validation status.

Runtime metadata is intended for diagnostics and auditing.

It shall not be stored within Project Definitions.

---

## L.8.6 Runtime Object Requirements

Each configuration domain shall:

* be immutable;
* be fully validated before construction;
* contain only resolved runtime configuration;
* expose a stable public interface;
* remain independent of JSON schema implementation.

Runtime configuration objects shall not contain business processing logic.

---

## L.8.7 Registry Relationship

Each RuntimeProjectConfiguration is owned by exactly one Project Definition.

The Project Configuration Registry maintains the association between project identifiers and RuntimeProjectConfiguration instances.

Example

```text
Project Configuration Registry
│
├── TECHNIP
│      └── RuntimeProjectConfiguration
│
├── JGC
│      └── RuntimeProjectConfiguration
│
├── SAMSUNG
│      └── RuntimeProjectConfiguration
│
└── SHELL
       └── RuntimeProjectConfiguration
```

Runtime modules shall obtain RuntimeProjectConfiguration from the Project Configuration Registry.

They shall not construct or modify RuntimeProjectConfiguration instances.

---

## L.8.8 Lifecycle

RuntimeProjectConfiguration is created once during pipeline initialization.

The lifecycle consists of:

1. Construction by ProjectDefinitionResolver.
2. Registration in the Project Configuration Registry.
3. Retrieval by the document processing pipeline.
4. Injection into runtime modules.
5. Disposal when the application terminates or configuration is reloaded.

After construction, RuntimeProjectConfiguration shall remain immutable throughout its lifetime.

---

## L.8.9 Ownership Boundary

Configuration ownership is divided across distinct architectural components.

---

### SchemaLoader

Owns:

* schema loading;
* schema validation;
* schema caching;
* generic schema reference resolution.

SchemaLoader shall remain independent of EKS business logic.

---

### ProjectDefinitionResolver

Owns:

* loading `eks_project_definition_config.json`;
* loading every configured Project Definition;
* resolving reusable configuration profile references;
* applying runtime environment profiles;
* merging project-specific and reusable configuration;
* validating the complete resolved configuration;
* constructing a RuntimeProjectConfiguration for each project;
* registering every RuntimeProjectConfiguration in the Project Configuration Registry.

ProjectDefinitionResolver is the only component permitted to assemble runtime configuration.

---

### Project Configuration Registry

Owns:

* one RuntimeProjectConfiguration per configured project;
* immutable runtime configuration storage;
* runtime configuration lookup by project code.

The registry shall remain read-only after initialization.

---

### Runtime Modules

Own:

* document processing;
* metadata extraction;
* engineering validation;
* asset extraction;
* graph construction;
* retrieval;
* AI interaction.

Runtime modules shall never own configuration management.

---

### Ownership Summary

| Component | Owns |
|------------|------|
| SchemaLoader | Schema loading and validation |
| ProjectDefinitionResolver | Configuration resolution and Project Configuration Registry construction |
| Project Configuration Registry | Immutable RuntimeProjectConfiguration storage |
| Document Processing Pipeline | Project identification and pipeline orchestration |
| Runtime Modules | Business processing |

Each responsibility shall exist in only one architectural layer.

---

# L.9 Runtime Module Integration

## L.9.1 Overview

Runtime modules shall consume configuration exclusively through `RuntimeProjectConfiguration`.

Runtime modules shall remain independent of:

* Project Definitions;
* JSON schema documents;
* reusable configuration libraries;
* configuration resolution logic;
* environment configuration.

Configuration shall be supplied through dependency injection after the project associated with the document has been identified.

---

## L.9.2 Runtime Integration Architecture

The interaction between configuration management and runtime processing is illustrated below.

```text
Project Configuration Registry
            │
            ▼
Document Processing Pipeline
            │
            ▼
Project Identification
            │
            ▼
RuntimeProjectConfiguration
            │
            ├────────► FilenameParser
            ├────────► RevisionValidator
            ├────────► DocumentParser
            ├────────► OCRProcessor
            ├────────► MetadataExtractor
            ├────────► ColumnProcessor
            ├────────► AssetExtractor
            ├────────► GraphBuilder
            ├────────► Retriever
            ├────────► PromptEngine
            ├────────► ValidationEngine
            └────────► Pipeline Controller
```

The document processing pipeline shall retrieve the appropriate RuntimeProjectConfiguration from the Project Configuration Registry after the document's project has been determined.

---

## L.9.3 Phase 1 Processing

During Phase 1, the pipeline scans and registers engineering documents without assigning a project.

Typical Phase 1 activities include:

* scanning configured directories;
* registering document metadata;
* calculating checksums;
* recording file locations;
* recording file attributes.

Project-specific processing shall not occur during this phase.

RuntimeProjectConfiguration is therefore not required during initial file registration.

> **Wording amendment (T1.194 D2 / T1.197 alignment pass)**: Phase A keeps
> `FilenameParser` in auto-detect mode over `registry.project_codes` from the
> Project Configuration Registry — **no committed project assignment occurs in
> Phase A**. The caller (FileScanner / PipelineOrchestrator) resolves the project
> code (Phase A: auto-detect; Phase B: committed identity) and fetches the
> configuration slice for the module at call time. Authoritative project
> assignment is performed in Phase B only.

---

## L.9.4 Project Identification

Project identification is performed after document registration.

Project identification may use one or more project-specific characteristics including:

* filename conventions;
* document numbering;
* directory structure;
* title block metadata;
* engineering metadata;
* project-specific validation rules.

ProjectDefinitionResolver shall not participate in project identification.

Its responsibility ends after constructing the Project Configuration Registry.

---

## L.9.5 Runtime Configuration Injection

After a project has been identified, the corresponding RuntimeProjectConfiguration shall be retrieved from the Project Configuration Registry.

The runtime configuration shall then be supplied to downstream processing modules through dependency injection.

Example

```text
Document

↓

Project = TECHNIP

↓

Project Configuration Registry

↓

RuntimeProjectConfiguration

↓

MetadataExtractor

↓

AssetExtractor

↓

GraphBuilder

↓

Retriever
```

Runtime modules shall not retrieve configuration independently.

---

## L.9.6 Configuration Slice Principle

Runtime modules should receive only the configuration required for their responsibilities.

Examples include:

| Runtime Module | Required Configuration |
|----------------|------------------------|
| FilenameParser | project, engineering, document |
| RevisionValidator | engineering, document |
| DocumentParser | parsing |
| OCRProcessor | parsing |
| MetadataExtractor | metadata |
| ColumnProcessor | parsing |
| AssetExtractor | assets |
| GraphBuilder | ontology, metadata |
| Retriever | retrieval, embeddings, ontology |
| PromptEngine | prompts |
| ValidationEngine | validation |

Providing configuration slices reduces coupling while maintaining a consistent runtime configuration model.

---

## L.9.7 Runtime Module Responsibilities

Runtime modules shall:

* perform business processing;
* consume immutable runtime configuration;
* remain independent of configuration storage;
* remain independent of Project Definitions.

Runtime modules shall not:

* load configuration files;
* resolve reusable profiles;
* determine project identity;
* modify RuntimeProjectConfiguration;
* construct runtime configuration.

Configuration management remains the responsibility of ProjectDefinitionResolver.

---

## L.9.8 Future Extensibility

Future runtime modules shall integrate using the same configuration model.

Examples include:

* AI Agent
* Engineering Rule Engine
* Compliance Validator
* Workflow Orchestrator
* Engineering QA Engine

New runtime modules shall consume RuntimeProjectConfiguration through dependency injection without requiring changes to ProjectDefinitionResolver or the Project Configuration Registry.

---

# L.10 Ownership Boundary

## L.10.1 Overview

The EKS Project Definition Architecture adopts explicit ownership boundaries to ensure a clear separation of responsibilities between configuration management and runtime processing.

Each architectural component shall own a single responsibility.

Responsibilities shall not overlap.

---

## L.10.2 SchemaLoader

SchemaLoader is a reusable framework component responsible for schema management.

Responsibilities include:

* loading JSON schema documents;
* validating schema structure;
* resolving generic schema references (`$ref`);
* caching loaded schemas;
* providing validated schema objects.

SchemaLoader shall remain independent of EKS business logic.

SchemaLoader shall not:

* interpret project semantics;
* resolve project configuration;
* construct runtime configuration;
* determine project identity.

---

## L.10.3 ProjectDefinitionResolver

ProjectDefinitionResolver is responsible for configuration orchestration.

Responsibilities include:

* loading `eks_project_definition_config.json`;
* loading Project Definitions;
* resolving reusable configuration profiles;
* applying runtime environment configuration;
* validating resolved configuration;
* constructing RuntimeProjectConfiguration;
* maintaining the Project Configuration Registry.

ProjectDefinitionResolver owns the complete lifecycle of runtime configuration construction.

ProjectDefinitionResolver shall not:

* determine which project a document belongs to;
* perform document parsing;
* perform metadata extraction;
* execute business processing.

---

## L.10.4 Project Configuration Registry

The Project Configuration Registry is the authoritative repository of runtime configuration.

Responsibilities include:

* storing one RuntimeProjectConfiguration per configured project;
* providing immutable runtime configuration;
* supporting runtime configuration lookup.

The registry shall remain read-only after initialization.

Runtime modules shall never modify registry contents.

---

## L.10.5 Document Processing Pipeline

The document processing pipeline is responsible for document execution.

Responsibilities include:

* scanning engineering documents;
* registering files;
* identifying project ownership;
* retrieving RuntimeProjectConfiguration;
* coordinating downstream processing.

The pipeline shall not construct runtime configuration.

---

## L.10.6 Runtime Modules

Runtime modules perform business processing.

Examples include:

* FilenameParser
* ColumnProcessor
* RevisionValidator
* DocumentParser
* OCRProcessor
* MetadataExtractor
* AssetExtractor
* GraphBuilder
* Retriever
* PromptEngine
* ValidationEngine

Runtime modules shall:

* consume RuntimeProjectConfiguration;
* perform business logic only.

Runtime modules shall not:

* load configuration;
* resolve profiles;
* modify runtime configuration;
* access Project Definitions directly.

---

## L.10.7 Ownership Matrix

| Component | Primary Responsibility |
|-----------|------------------------|
| SchemaLoader | Schema loading and validation |
| ProjectDefinitionResolver | Configuration resolution and runtime configuration construction |
| Project Configuration Registry | Runtime configuration storage |
| Document Processing Pipeline | Project identification and pipeline orchestration |
| Runtime Modules | Business processing |

Each responsibility shall exist in only one architectural component.

No component shall duplicate the responsibility of another.

---

## L.10.8 Dependency Rules

Dependencies shall follow the architecture illustrated below.

```text
SchemaLoader
        │
        ▼
ProjectDefinitionResolver
        │
        ▼
Project Configuration Registry
        │
        ▼
Document Processing Pipeline
        │
        ▼
RuntimeProjectConfiguration
        │
        ▼
Runtime Modules
```

Dependencies shall be unidirectional.

Lower-level components shall not depend on higher-level components.

Runtime modules shall remain independent of configuration implementation details.

---

## L.10.9 Extensibility

Future components shall integrate without changing existing ownership boundaries.

Examples include:

* AI Agent
* Engineering QA Engine
* Compliance Validator
* Workflow Orchestrator
* Engineering Analytics

New components shall consume RuntimeProjectConfiguration through the existing runtime configuration model.

No changes to ProjectDefinitionResolver or SchemaLoader shall be required to support additional runtime modules.

---

# L.11 Migration Strategy

## Stage 1

Introduce `eks_project_definition_schema.json`.

Maintain compatibility with existing configuration.

---

## Stage 2

Introduce ProjectDefinitionResolver.

Construct RuntimeProjectConfiguration during pipeline bootstrap.

---

## Stage 3

Migrate runtime modules to RuntimeProjectConfiguration.

Replace direct schema access and multiple configuration dictionaries.

---

## Stage 4

Update all `$ref` consumers, including `eks_config.json`.

Retire `eks_project_rules_config.json`.

---

## Stage 5

Remove deprecated compatibility layer after all runtime modules have migrated.

---

# L.12 Implementation Tasks

| #          | Date       | Phase   | Task                                             | Description                                                                                                                                                                                                                                                                                                                                                                                                                          | Dependencies           | Author   |   Status   |
| :--------- | :--------- | :------ | :----------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------- | :------- | :--------: |
| **T1.189** | 2026-07-30 | Phase 1 | Define Project Definition Architecture           | Define architecture, ownership boundaries, runtime lifecycle, bootstrap sequence, RuntimeProjectConfiguration model, and interactions between SchemaLoader, ProjectDefinitionResolver, FilenameParser, ColumnProcessor, and runtime modules.                                                                                                                                                                                            | —                      | Franklin | 🔷 Planned |
| **T1.190** | 2026-07-30 | Phase 1 | Implement Project Definition Schema              | Create `eks_project_definition_schema.json`, consolidate all project-specific configuration, migrate project rules into the Project Definition, and define reusable profile references.                                                                                                                                                                                                                                              | T1.189                 | Franklin | 🔷 Planned |
| **T1.191** | 2026-07-30 | Phase 1 | Refactor Reusable Configuration Libraries        | Refactor `eks_doc_config.json` and related shared configuration libraries to retain only reusable profiles. Remove project-specific mappings while maintaining temporary compatibility for existing consumers.                                                                                                                                                                                                                       | T1.190                 | Franklin | 🔷 Planned |
| **T1.192** | 2026-07-30 | Phase 1 | Verify SchemaLoader Compatibility                | Verify that the SchemaLoader architecture introduced in I261/I263 fully supports ProjectDefinitionResolver. Implement only minimal generic enhancements if justified. Define the contract that SchemaLoader returns raw validated schema objects and does not assemble runtime configuration.                                                                                                                                        | I261, I263             | Franklin | 🔷 Planned |
| **T1.193** | 2026-07-30 | Phase 1 | Implement ProjectDefinitionResolver              | Implement the common EKS pipeline module that loads all Project Definitions from `eks_project_definition_config.json`, resolves reusable profile references, applies runtime environment profiles, validates each project configuration, merges configuration, constructs a RuntimeProjectConfiguration per project, and registers all in the Project Configuration Registry during pipeline bootstrap. The resolver shall not determine which project a document belongs to — project identification is a pipeline responsibility. | T1.190, T1.191, T1.192 | Franklin | 🔷 Planned |
| **T1.194** | 2026-07-31 | Phase 1 | Migrate Runtime Modules                          | Replace direct schema loading and multiple runtime configuration dictionaries with RuntimeProjectConfiguration across Phase 1 runtime modules. Preserve I255 auto-detection while replacing `project_code_registry` with Project Definition (`registry.project_codes`) as the authoritative project registry. **Approved design decisions (2026-07-31)**: **(D1 — Caller-injection contract)** Caller (FileScanner / PipelineOrchestrator) is constructed with the injected ProjectConfigurationRegistry; caller resolves the project code (Phase A: auto-detect; Phase B: committed identity) and fetches the config slice; caller passes `project_code` + resolved slice to the module at call time. Modules never hold the registry, self-fetch configuration, or identify projects (satisfies L.8.7 + L.9.5 + L.9.7). **(D2 — Phase A registration)** Phase A stays project-agnostic for assignment (L.9.3): FileScanner keeps FilenameParser in auto-detect mode over `registry.project_codes`; no committed project assignment in Phase A; authoritative assignment in Phase B. Requires L.9.3 wording amendment — recorded in T1.197 alignment pass. **Scope**: existing Phase 1 modules only — FileScanner, FilenameParser, PipelineOrchestrator (Pipeline), ColumnProcessor, FilePropertyParser, ParserRouter, RevisionManager. P3–P5 modules (AssetExtractor, GraphBuilder, Retriever, PromptEngine, OCRProcessor) deferred to their phases. **Backward-compat**: keep dict-based params as optional fallback per L.14.7 until T1.196 Stage 5 removal. **Tests**: TL029 — 21/21 slice-injection tests + full suite 413 passed (5 pre-existing). Update: U240. | T1.193, I255, I264     | Franklin | ✅ COMPLETE |
| **T1.195** | 2026-07-30 | Phase 1 | Implement Configuration Validation               | Validate project completeness, reusable profile references, project-to-profile mappings, duplicate definitions, unused profiles, schema consistency, and RuntimeProjectConfiguration construction during ProjectDefinitionResolver execution. **Approved design decisions (2026-07-31)**: **(V1 — Failure semantics)** System errors (schema violations, missing mandatory sections, unknown profile IDs, unknown runtime profiles, duplicate project codes/profiles, runtime construction failure) hard-fail pipeline initialization via `resolver.errors` → bootstrap raises. Data-related errors (L.13.6 capability consistency, L.13.7 metadata gaps, L.13.10 unused profiles) are logged via new `resolver.data_errors` and never fail the pipeline. **(V2 — Capability-driven consistency, no hardcode)** L.13.6 implemented with NO hardcoded pairs and NO central compatibility matrix: each profile declares its capabilities in its owning schema — `parsing_profile_def` with `supported_document_profiles`/`supported_extensions`/`requires_ocr` (doc schema set), chunking `supported_document_types`, embedding `supported_retrieval_strategies`, ontology `supported_asset_profiles`, validation `supported_engineering_conventions`; ProjectDefinitionResolver extracts these during `_resolve_profile()` (exact-key lookup, not substring match) and a single generic `_evaluate_capability_compat()` compares resolved profiles. Adds `parsing_profiles` section to `eks_doc_config.json`. **(V3 — Error codes)** System errors: `S-C-S-{id}` (category `Config` — e.g. `S-C-S-0901` missing mandatory section, `S-C-S-0902` unknown profile ref, `S-C-S-0903` duplicate project code, `S-C-S-0904` runtime construction failure). Data errors: `P1-C-V-{id}` (layer P1, module C=Config, function V=Validate — e.g. `P1-C-V-0001` capability consistency violation, `P1-C-V-0002` metadata-policy gap, `P1-C-V-0003` unused profile). Both patterns already satisfy `eks_error_code_base.json` regexes (system `S-[A-Z]-S-[0-9]{4}`, data `P[0-9]-[A-Z]-[A-Z]+-[0-9]{4}`) — registration only in `eks_error_config.json` (system + data sections) + `eks_message_config.json` + Appendix D + cross-source audit per §24. **Scope**: split `_validate_resolved()` into per-category validators (project completeness, profile refs, environment refs, capability consistency, metadata policy, duplicate detection, unused config, runtime module L.13.11, runtime constructible L.13.8); extend `validation_report` to L.13.12 content (resolved profiles, runtime profiles, checksum, schema version, RPC version); 30+ tests per category incl. ErrorManager code resolution. **Implementation (2026-07-31)**: schemas (doc base v1.10.0 `parsing_profile_def`, setup v1.9.0 `parsing_profiles`, config v1.8.0 profiles), error registry v1.7.0 (S-C-S-0901..0904, P1-C-V-0001..0003, 2 new ranges), message catalog v1.2.0 (4 PDEF messages), resolver rev 1.1.0 (V1 data_errors, V2 exact-key + `_evaluate_capability_compat`, L.13.3/.4/.5/.6/.7/.9/.10 validators, L.13.12 report, `_known_runtime_profiles`), bootstrap surfaces data_errors. **Tests**: TL030 — 75/75 (test_project_definition.py, 47 new) + 65/65 (test_t132_modules.py, 12 new); full suite 472 passed / 5 pre-existing. Update: U242. Appendix D v2.1 re-synced (D4 75/75, D5 53/53, D6 52/52). | T1.193                 | Franklin | ✅ COMPLETE |
| **T1.196** | 2026-07-30 | Phase 1 | Migrate Existing Configuration | **Scope (revised 2026-07-31 to cover I266–I272 — L.11 Stage 4 + Stage 5)**: **(1) $ref consumers (I267)** — remove `project_rules_registry` from `eks_setup_schema.json` (property + required) and `eks_config.json` ($ref); remove `project_rules_def` from `eks_base_schema.json`; archive `eks_project_rules_config.json`. **(2) Runtime consumers (I266)** — repoint `config_registry.py` `get_project_rules` / `get_fragment_required_fields` / `resolve_required_fields` to the Project Definition; expose `fragment_required_fields` via resolver / AssetExtractor slice. **(3) Stage 5 compat-layer removal (I268)** — drop the dead `legacy_project_rules` flag; remove `_validate_project_rules()` and the dead `revision_validation` reconstruction; keep the functional `filename_patterns` reconstruction (T1.191) until the filename_parser slice carries resolved patterns. **(4) Tests** — legacy assertions repointed to the Project Definition; regression tests with zero legacy presence. **(5) Cross-source audit (§24) + naming/doc alignment (I269–I272)** — naming reconciliation, L.6.2 note, L.13 V1/V2/V3 wording, L.10.6 ColumnProcessor, knowledge.json, eks_system_workplan, Appendix E. | T1.194, T1.195 | Franklin | ✅ COMPLETE |
| **T1.197** | 2026-07-30 | Phase 1 | Documentation, Traceability & Regression Testing | Update architecture documentation, Phase 1 implementation index, issue traceability, migration guide, runtime lifecycle documentation, and verify regression across document ingestion, metadata extraction, column processing, asset processing, graph construction, retrieval, and RAG workflows. **Implementation (2026-07-31)**: L.9.3 wording amendment (T1.194 D2); cross-workplan audit — P1.1 (project_definition_config + ProjectDefinitionResolver row), Appendix F/G/H (I265 alignment notes), knowledge.json; migration guide created (`docs/project_definition_migration_guide.md`); regression cleanup (test_config_version_bumped — 5→4 pre-existing failures); p1_task_log status summary recounted (396 total); I265 → 📐 Aligned. Tests: TL032 — full suite 474 passed / 4 pre-existing. Update: U246. | T1.196                 | Franklin | ✅ COMPLETE |

---

# L.13 Validation

# L.13 Validation

## L.13.1 Validation Objectives

ProjectDefinitionResolver shall validate the complete Project Definition before constructing RuntimeProjectConfiguration.

Validation ensures that:

* project configuration is complete;
* reusable profile references are valid;
* environment profile references are valid;
* configuration sections are internally consistent;
* runtime configuration can be constructed deterministically.

**Failure semantics (T1.195 V1/V3)**: System errors — schema violations, missing
mandatory sections (`S-C-S-0901`), unknown profile references (`S-C-S-0902`),
duplicate project codes/profiles (`S-C-S-0903`), and runtime construction failure
(`S-C-S-0904`) — fail pipeline initialization via `resolver.errors` → bootstrap
raises. Data-related issues — capability consistency (L.13.6, `P1-C-V-0001`),
metadata-policy gaps (L.13.7, `P1-C-V-0002`), unused profiles (L.13.10,
`P1-C-V-0003`) — are surfaced via `resolver.data_errors` and never block
initialization.

Pipeline initialization shall fail if any mandatory **system** validation fails.

No runtime module shall execute until RuntimeProjectConfiguration has been successfully validated and constructed.

---

## L.13.2 Validation Scope

Validation shall include the following categories.

| Category | Description |
|-----------|-------------|
| Schema Validation | JSON schema compliance |
| Project Validation | Project definition completeness |
| Profile Validation | Reusable profile resolution |
| Environment Validation | Runtime profile resolution |
| Cross-Reference Validation | Configuration consistency |
| Runtime Validation | RuntimeProjectConfiguration construction |
| Dependency Validation | Inter-profile compatibility |

Validation shall be performed during pipeline initialization.

---

## L.13.3 Project Definition Validation

ProjectDefinitionResolver shall verify:

* project exists;
* project code is unique;
* project identity is complete;
* lifecycle information is complete;
* engineering conventions are defined;
* engineering standards are specified;
* mandatory project sections exist.

Missing mandatory sections shall terminate initialization.

---

## L.13.4 Reusable Profile Validation

Every reusable profile reference shall exist.

Examples include:

* document profile;
* parsing profile;
* chunking profile;
* embedding profile;
* asset profile;
* ontology profile;
* retrieval profile;
* prompt profile;
* validation profile;
* security profile.

Resolver shall reject unknown profile identifiers.

Example

```text
Project Definition

↓

document_profile

↓

technip_pdf

↓

✓ Exists
```

or

```text
document_profile

↓

unknown_profile

↓

Validation Error
```

---

## L.13.5 Environment Profile Validation

Runtime profile references shall be validated.

Examples include:

* storage profile;
* vector database profile;
* graph database profile;
* messaging profile;
* cache profile.

ProjectDefinitionResolver shall verify that every referenced runtime profile exists.

Deployment-specific implementation details shall remain outside Project Definition.

---

## L.13.6 Configuration Consistency Validation

Configuration sections shall be mutually compatible.

Examples include:

* parser supports selected document profile;
* OCR profile supports parser;
* chunking strategy supports document type;
* embedding model supports retrieval strategy;
* ontology supports asset profile;
* validation profile supports engineering conventions.

Incompatible combinations are reported as non-blocking data errors
(`P1-C-V-0001` via `resolver.data_errors`, T1.195 V1) — they never terminate
initialization. Capability declarations are compared by the generic
`_evaluate_capability_compat()` using each profile's own schema-declared
capabilities (T1.195 V2 — no hardcoded compatibility matrix).

---

## L.13.7 Metadata Policy Validation

Metadata inheritance rules shall be verified.

Validation shall ensure:

* required metadata exists;
* mandatory inheritance rules are defined;
* metadata dependencies are satisfied;
* fragment metadata remains complete.

Example metadata includes:

* project code;
* revision;
* document number;
* sheet number;
* discipline;
* equipment tag;
* client;
* vendor.

---

## L.13.8 Runtime Configuration Validation

ProjectDefinitionResolver shall verify that RuntimeProjectConfiguration can be successfully constructed.

Validation includes:

* all runtime sections exist;
* configuration objects are complete;
* no unresolved profile identifiers remain;
* runtime object model is internally consistent;
* configuration is immutable.

Construction failures shall terminate pipeline initialization.

---

## L.13.9 Duplicate Detection

Validation shall detect duplicate definitions including:

* duplicate project codes;
* duplicate reusable profiles;
* duplicate runtime profile names;
* duplicate ontology entities;
* duplicate validation rules.

Duplicate definitions shall be reported as configuration errors.

---

## L.13.10 Unused Configuration Detection

Resolver shall report configuration that is never referenced.

Examples include:

* unused parser profiles;
* unused embedding profiles;
* unused ontology profiles;
* unused runtime profiles.

Unused configuration is surfaced via `resolver.data_errors` (`P1-C-V-0003`) and
never blocks the pipeline (T1.195 V1).

---

## L.13.11 Runtime Module Validation

Resolver shall verify that every runtime module receives compatible runtime configuration.

Examples

| Module | Required Configuration |
|----------|-----------------------|
| FilenameParser | project, engineering, document |
| DocumentParser | parsing |
| Retriever | retrieval, embeddings, ontology |
| GraphBuilder | ontology, metadata |
| PromptEngine | prompts |

Missing required runtime sections shall terminate initialization.

---

## L.13.12 Validation Report

ProjectDefinitionResolver shall generate a validation report.

Typical contents include:

* resolved project;
* resolved reusable profiles;
* resolved runtime profiles;
* validation results;
* warnings;
* errors;
* configuration checksum;
* schema version;
* RuntimeProjectConfiguration version.

The validation report shall be available for diagnostics and troubleshooting.

---

## L.13.13 Validation Success Criteria

RuntimeProjectConfiguration shall only be constructed when:

* every mandatory section exists;
* every reusable profile is resolved;
* every runtime profile is resolved;
* no unresolved references remain;
* no incompatible configuration exists;
* all runtime configuration objects are complete;
* validation completes without errors.

Only then may pipeline execution begin.

---

# L.14 Success Criteria

# L.14 Success Criteria

The Project Definition Architecture refactoring shall be considered complete when all of the following criteria are satisfied.

---

## L.14.1 Architecture

* `eks_project_definition_schema.json` is the Single Source of Truth (SSOT) for all project-specific configuration.
* SchemaLoader remains a reusable framework component independent of EKS business logic.
* ProjectDefinitionResolver is the only component responsible for runtime configuration assembly.
* RuntimeProjectConfiguration is the only runtime configuration consumed by pipeline modules.

---

## L.14.2 Configuration Ownership

Project-specific semantics shall reside exclusively within Project Definition.

Reusable behaviour shall reside exclusively within reusable configuration libraries.

Deployment-specific infrastructure shall reside exclusively within Environment Configuration.

No configuration ownership shall overlap.

---

## L.14.3 Runtime Configuration

RuntimeProjectConfiguration shall:

* be fully resolved;
* be immutable;
* be strongly typed;
* be reference-free;
* expose a stable runtime API;
* remain independent of JSON schema organization.

No runtime module shall access configuration schemas directly.

---

## L.14.4 Profile Resolution

ProjectDefinitionResolver shall successfully resolve:

* document profiles;
* parsing profiles;
* chunking profiles;
* embedding profiles;
* ontology profiles;
* asset profiles;
* retrieval profiles;
* prompt profiles;
* validation profiles;
* runtime profiles.

No unresolved profile identifiers shall remain.

---

## L.14.5 Runtime Module Integration

All runtime modules shall consume RuntimeProjectConfiguration through dependency injection.

Runtime modules shall not:

* load schemas;
* resolve profiles;
* merge configuration;
* determine project selection.

Business processing and configuration management shall remain separated.

---

## L.14.6 Validation

ProjectDefinitionResolver shall validate:

* project completeness;
* reusable profile references;
* runtime profile references;
* configuration consistency;
* RuntimeProjectConfiguration construction.

Pipeline initialization shall terminate if validation fails.

---

## L.14.7 Backward Compatibility

The implementation shall preserve compatibility with:

* I255 Project auto-detection;
* I256 Configuration Architecture;
* I261 SchemaLoader;
* I263 Schema Validation Framework;
* I264 Column Processing Architecture.

Existing document ingestion, metadata extraction, asset processing, graph construction, retrieval, and RAG workflows shall continue to operate without functional regression.

---

## L.14.8 Future Extensibility

The architecture shall support future enhancements without redesign.

Examples include:

* additional reusable profile libraries;
* AI agent configuration;
* engineering QA policies;
* workflow orchestration;
* compliance validation;
* multi-model retrieval;
* additional ontology domains.

Future extensions shall be introduced through configuration rather than source code modifications.

---

## L.14.9 Overall Completion Criteria

This work is complete when:

* Project Definition is the authoritative source for project semantics.
* RuntimeProjectConfiguration is the authoritative runtime configuration.
* Configuration ownership is clearly separated.
* Runtime configuration is deterministic, validated, and immutable.
* New projects can be onboarded through configuration only.
* Existing EKS pipelines continue to function without regression.

# Appendix M
# Runtime Configuration Architecture

---

# M.1 Objective

## M.1.1 Purpose

This appendix defines the Runtime Configuration Architecture for the Engineering Knowledge System (EKS).

It specifies how project-specific configuration is transformed into immutable runtime configuration used throughout the document processing pipeline.

This appendix complements Appendix L.

Appendix L defines:

- Project Definition
- configuration ownership
- reusable configuration libraries
- ProjectDefinitionResolver

This appendix defines:

- RuntimeProjectConfiguration
- runtime lifecycle
- runtime object model
- runtime module integration
- dependency injection
- runtime validation

Together these appendices establish the complete configuration architecture.

---

## M.1.2 Scope

This appendix applies to every runtime component within EKS including:

- ingestion pipeline
- metadata extraction
- document parsing
- asset extraction
- graph generation
- retrieval
- RAG services
- AI agents
- future runtime services

Every runtime component shall consume RuntimeProjectConfiguration.

---

## M.1.3 Objectives

The Runtime Configuration Architecture shall:

- establish a single runtime configuration model
- eliminate runtime configuration duplication
- isolate runtime modules from configuration storage
- support immutable runtime configuration
- provide deterministic runtime behavior
- simplify dependency injection
- support future configuration evolution

---

# M.2 Runtime Configuration Overview

## M.2.1 Runtime Configuration Philosophy

Project Definitions describe project semantics.

RuntimeProjectConfiguration represents those semantics after they have been resolved into executable runtime configuration.

Runtime modules shall never interpret Project Definitions directly.

Instead they consume RuntimeProjectConfiguration.

This separation provides:

- stable runtime APIs
- reusable configuration libraries
- simplified testing
- deterministic execution
- reduced coupling

---

## M.2.2 Runtime Configuration Lifecycle

Runtime configuration is created during pipeline initialization.

```text
Project Definition
        │
        ▼
ProjectDefinitionResolver
        │
Resolve Profiles
        │
Merge Configuration
        │
Validate
        │
        ▼
RuntimeProjectConfiguration
        │
Dependency Injection
        │
        ▼
Runtime Modules
```

RuntimeProjectConfiguration remains immutable throughout pipeline execution.

---

## M.2.3 Configuration Resolution

ProjectDefinitionResolver performs the following tasks.

1. Load Project Definition

2. Resolve reusable profile references

3. Load reusable profile definitions

4. Merge configuration

5. Apply environment configuration

6. Validate complete configuration

7. Construct RuntimeProjectConfiguration

Runtime modules are not involved in any configuration resolution.

---

# M.3 Runtime Lifecycle

Runtime configuration progresses through four stages.

---

## Stage 1 — Configuration Loading

SchemaLoader loads:

- Project Definition
- reusable configuration libraries
- environment configuration

All configuration shall be validated before use.

Output:

Validated schema objects.

---

## Stage 2 — Configuration Resolution

ProjectDefinitionResolver:

- resolves reusable profiles
- resolves runtime profiles
- merges configuration
- validates dependencies

Output:

Resolved runtime configuration.

---

## Stage 3 — Runtime Construction

ProjectDefinitionResolver constructs RuntimeProjectConfiguration.

Construction shall:

- resolve every profile
- eliminate configuration references
- produce immutable runtime objects

Construction shall fail if validation fails.

---

## Stage 4 — Runtime Execution

RuntimeProjectConfiguration is injected into runtime modules.

Example

```text
RuntimeProjectConfiguration

        │

        ├────────► FilenameParser

        ├────────► DocumentParser

        ├────────► MetadataExtractor

        ├────────► AssetLoader

        ├────────► GraphBuilder

        ├────────► Retriever

        ├────────► PromptEngine

        └────────► Pipeline
```

No runtime module shall modify RuntimeProjectConfiguration.

---

## M.3.1 Runtime Characteristics

RuntimeProjectConfiguration shall satisfy the following characteristics.

| Characteristic | Description |
|----------------|-------------|
| Immutable | Cannot be modified after construction |
| Fully Resolved | No unresolved profile references |
| Strongly Typed | Structured runtime objects |
| Reference-Free | Profile identifiers removed |
| Deterministic | Same configuration always produces identical runtime configuration |
| Self-Contained | Independent of configuration files |
| Serializable | Can be exported for diagnostics |
| Thread-Safe | Safe for concurrent runtime access |

---

## M.3.2 Runtime Contract

RuntimeProjectConfiguration establishes the contract between the configuration subsystem and runtime modules.

Runtime modules shall depend only on this contract.

They shall remain independent of:

- JSON schemas
- Project Definition
- reusable libraries
- environment configuration
- configuration loading
- profile resolution

This guarantees runtime stability even when configuration schemas evolve.

# M.4 RuntimeProjectConfiguration

## M.4.1 Purpose

`RuntimeProjectConfiguration` is the immutable runtime configuration model for the Engineering Knowledge System (EKS).

It represents the fully resolved runtime configuration produced by `ProjectDefinitionResolver` after:

- loading the Project Definition;
- resolving reusable profile references;
- applying environment configuration;
- validating configuration consistency; and
- constructing the runtime object model.

`RuntimeProjectConfiguration` is the only runtime configuration object that shall be consumed by runtime modules.

---

## M.4.2 Design Principles

RuntimeProjectConfiguration shall satisfy the following principles.

| Principle | Description |
|-----------|-------------|
| Single Runtime Contract | One configuration object for the entire platform |
| Immutable | Read-only after construction |
| Fully Resolved | No profile identifiers remain |
| Strongly Typed | Runtime objects instead of raw JSON |
| Reference-Free | Independent of configuration libraries |
| Deterministic | Same input always produces identical runtime configuration |
| Self-Contained | No dependency on configuration files |
| Extensible | New configuration domains can be added without breaking existing modules |

---

## M.4.3 Runtime Object Hierarchy

RuntimeProjectConfiguration shall expose the following runtime object hierarchy.

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

Each top-level object represents a distinct runtime configuration domain.

Runtime modules shall consume these objects through dependency injection.

---

## M.4.4 Runtime Object Requirements

Each runtime object shall:

- be immutable;
- be validated before construction;
- expose a stable public interface;
- be independent of JSON schema implementation;
- contain only resolved runtime configuration.

Runtime objects shall not perform business processing.

---

## M.4.5 Runtime Metadata

The runtime section contains metadata generated during configuration assembly.

Typical runtime metadata includes:

- schema version;
- RuntimeProjectConfiguration version;
- configuration checksum;
- build timestamp;
- resolved profile list;
- validation status.

Runtime metadata is generated during initialization and shall not be persisted within Project Definitions.

---

# M.5 Runtime Configuration Objects

## M.5.1 Overview

RuntimeProjectConfiguration is composed of a collection of immutable runtime configuration objects.

Each object owns a specific configuration domain and provides a stable interface for runtime modules.

---

## M.5.2 Runtime Configuration Domains

RuntimeProjectConfiguration
│
├── ProjectContext
│   ├── project
│   ├── lifecycle
│   ├── engineering
│   └── standards
│
├── ProcessingConfiguration
│   ├── document
│   ├── parsing
│   ├── chunking
│   ├── embeddings
│   ├── metadata
│   ├── assets
│   ├── ontology
│   ├── retrieval
│   ├── prompts
│   ├── validation
│   └── security
│
├── RuntimeServices
│   └── runtime_profiles
│
└── RuntimeMetadata
    └── runtime

---

## M.5.3 Object Responsibilities

### project

Defines the identity of the active engineering project.

Typical information includes:

- project code;
- project name;
- client;
- contractor;
- execution centre;
- project type.

---

### lifecycle

Defines the execution status of the project.

Typical information includes:

- project phase;
- engineering stage;
- issue status;
- baseline revision.

---

### engineering

Defines engineering conventions including:

- document numbering;
- tag naming;
- revision scheme;
- engineering units;
- discipline conventions.

---

### standards

Defines engineering standards applicable to the project.

Examples include:

- ASME;
- API;
- IEC;
- ISO;
- ISA;
- ASTM;
- AWS.

---

### document

Defines document-specific processing rules.

Typical responsibilities include:

- filename interpretation;
- title block rules;
- revision extraction;
- document numbering;
- metadata extraction.

---

### parsing

Defines parser behavior.

Typical configuration includes:

- parser implementation;
- OCR strategy;
- rotated page detection;
- table extraction;
- multi-column handling.

---

### chunking

Defines fragment generation policies.

Typical configuration includes:

- chunk size;
- overlap;
- semantic chunking;
- table chunking;
- drawing chunking.

---

### embeddings

Defines vector generation policies.

Typical configuration includes:

- embedding model;
- vector dimension;
- normalization;
- similarity metric;
- reranking strategy.

---

### metadata

Defines metadata enrichment and inheritance policies.

Typical metadata includes:

- project;
- document number;
- revision;
- discipline;
- equipment tag;
- client;
- vendor;
- package.

---

### assets

Defines engineering asset extraction.

Typical asset categories include:

- equipment;
- piping;
- instruments;
- valves;
- cables;
- packages.

---

### ontology

Defines knowledge graph behavior.

Typical configuration includes:

- entity definitions;
- relationship definitions;
- graph constraints;
- ontology mappings.

---

### retrieval

Defines runtime retrieval behavior.

Typical configuration includes:

- hybrid search;
- metadata filters;
- graph expansion;
- reranking;
- Top-K defaults.

---

### prompts

Defines AI prompt behavior.

Typical configuration includes:

- assistant prompts;
- citation policy;
- formatting rules;
- reasoning constraints;
- hallucination mitigation.

---

### validation

Defines runtime validation policies.

Typical responsibilities include:

- metadata validation;
- revision validation;
- ontology validation;
- asset validation;
- configuration consistency.

---

### security

Defines project security policies.

Typical responsibilities include:

- document classification;
- access control;
- redaction;
- audit;
- export policy.

---

### runtime_profiles

Defines resolved runtime infrastructure services.

Examples include:

- object storage;
- vector database;
- graph database;
- cache;
- messaging.

Only resolved runtime services shall appear in RuntimeProjectConfiguration.

---

### runtime

Contains runtime-generated metadata describing the constructed runtime configuration.

This object is intended for diagnostics, auditing and troubleshooting.

---

## M.5.4 Design Constraints

All runtime configuration objects shall satisfy the following constraints.

- Fully validated before construction.
- Immutable after construction.
- Strongly typed.
- Independent of JSON schema organization.
- Independent of reusable profile identifiers.
- Safe for concurrent access.
- Stable across future schema evolution.

Runtime modules shall consume only these runtime objects and shall never depend directly on Project Definitions or reusable configuration libraries.
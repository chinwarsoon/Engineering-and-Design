# Appendix F: EKS Pipeline Architecture Design

**Document ID**: WP-EKS-APPENDIX-F-001  
**Current Version**: 1.6  
**Status**: 📋 Proposed for Review  
**Last Updated**: 2026-06-29  
**Parent Workplan**: [Universal Pipeline Architecture Design](../../common/universal_pipeline_architecture_design.md)

---

## Revision History

| Revision | Date | Author | Summary |
| :--- | :--- | :--- | :--- |
| 1.6 | 2026-06-29 | Cascade | Consolidated implementation-related sections (2, 4, 5, 8, 10) into new Section 6 (Implementation Evaluation) at end of document for evaluating current status. Renumbered remaining sections accordingly. Updated index of content. |
| 1.5 | 2026-06-29 | Cascade | Added Index of Content section with links to all sections and subsections per AGENTS.md Section 14 (Documentation). |
| 1.4 | 2026-06-29 | Cascade | Removed Section 3.3.6 (Implementation Tasks) to ensure Appendix F contains only high-level architecture design. Task-level details moved to phase_1_foundation_workplan.md Section 16. |
| 1.3 | 2026-06-26 | Cascade | Restructured Appendix F to focus on high-level pipeline architecture design only. Removed detailed Phase 1.2.x implementation roadmap (moved to phase_1_foundation_workplan.md). Added Section 4: Implementation Guidance with cross-references to phase workplans. |
| 1.2 | 2026-06-26 | Cascade | Added Section 3.4: Engine I/O Analysis with comprehensive tabulation of all 60 engines across all 5 phases, documenting input/output types, database operations, and file operations. |
| 1.1 | 2026-06-26 | Cascade | Added Section 3.3: Standardized Engine I/O for Independent Execution. Updated Phase 1.2.1 tasks and deliverables to include I/O contracts, CLI entry points, and HTTP API endpoints. |
| 1.0 | 2026-06-26 | Cascade | Initial version with EKS-specific application of universal pipeline architecture patterns, including current state assessment, proposed architecture enhancement, and 6-phase implementation roadmap. |

---

## Index of Content

- [Revision History](#revision-history)
- [1. Executive Summary](#1-executive-summary)
- [2. Proposed Architecture Enhancement](#2-proposed-architecture-enhancement)
  - [2.1 Target Architecture](#21-target-architecture)
  - [2.2 EKSPipelineContext Structure](#22-ekspipelinecontext-structure)
  - [2.3 Standardized Engine I/O for Independent Execution](#23-standardized-engine-io-for-independent-execution)
    - [2.3.1 Standard Input/Output Contract](#231-standard-inputoutput-contract)
    - [2.3.2 Engine-Specific I/O Contracts](#232-engine-specific-io-contracts)
    - [2.3.3 Independent Execution Modes](#233-independent-execution-modes)
    - [2.3.4 Engine Chaining and Orchestration](#234-engine-chaining-and-orchestration)
    - [2.3.5 Benefits of Standardized I/O](#235-benefits-of-standardized-io)
  - [2.4 Engine I/O Analysis](#24-engine-io-analysis)
    - [Phase 1 Engines (Foundation)](#phase-1-engines-foundation)
    - [Phase 2 Engines (Chunking & Embedding)](#phase-2-engines-chunking--embedding)
    - [Phase 3 Engines (Knowledge Graph)](#phase-3-engines-knowledge-graph)
    - [Phase 4 Engines (Retrieval Pipeline)](#phase-4-engines-retrieval-pipeline)
    - [Phase 5 Engines (UI Integration)](#phase-5-engines-ui-integration)
    - [I/O Pattern Summary](#io-pattern-summary)
- [3. Benefits](#3-benefits)
  - [3.1 Maintainability](#31-maintainability)
  - [3.2 Testability](#32-testability)
  - [3.3 Observability](#33-observability)
  - [3.4 Flexibility](#34-flexibility)
  - [3.5 User Experience](#35-user-experience)
- [4. Risks and Mitigation](#4-risks-and-mitigation)
- [5. References](#5-references)
  - [5.1 Universal Architecture](#51-universal-architecture)
  - [5.2 EKS Documents](#52-eks-documents)
  - [5.3 DCC Reference Implementations](#53-dcc-reference-implementations)
- [6. Implementation Evaluation](#6-implementation-evaluation)
  - [6.1 Current State Assessment (Phase 1)](#61-current-state-assessment-phase-1)
    - [Completed Components](#completed-components)
    - [Architecture Gaps](#architecture-gaps)
  - [6.2 Implementation Guidance](#62-implementation-guidance)
  - [6.3 Architecture Comparison](#63-architecture-comparison)
  - [6.4 Success Criteria](#64-success-criteria)
  - [6.5 Next Steps](#65-next-steps)

---

## 1. Executive Summary

This appendix defines the EKS-specific application of universal pipeline architecture patterns documented in the Universal Pipeline Architecture Design. It provides a high-level architecture design for applying these patterns to the Engineering Knowledge System (EKS) pipeline, building on the completed Phase 1 foundation.

---

---

## 2. Proposed Architecture Enhancement

### 2.1 Target Architecture

```
eks/
├── engine/
│   ├── core/              # Foundation: logging, paths, IO, context, base classes
│   │   ├── context.py     # EKSPipelineContext
│   │   ├── base.py        # BaseEngine, BaseProcessor
│   │   ├── telemetry.py   # EKSTelemetryHeartbeat
│   │   ├── validator.py   # EKSValidator
│   │   ├── factories.py   # ParserFactory, HealthScorerFactory
│   │   └── orchestrator.py # PipelineOrchestrator (enhanced)
│   ├── parsers/           # Domain: document parsers
│   ├── discovery/         # Domain: file scanner
│   ├── router/            # Domain: parser router
│   ├── registry/          # Domain: document registry
│   ├── revision/          # Domain: revision manager
│   ├── health/            # Domain: health scorer
│   └── structure/         # Domain: structure detector
└── ui/
    ├── backend/           # Interface: HTTP server, API contracts
    │   ├── contracts.py   # DocumentSelectionContract, PipelineConfigContract
    │   ├── contract_manager.py # UIContractManager
    │   └── server.py      # HTTP server
    └── frontend/          # Interface: HTML/CSS/JavaScript
        ├── index.html
        ├── eks.css
        └── eks.js
```

### 2.2 EKSPipelineContext Structure

```python
@dataclass
class EKSPipelineContext:
    paths: EKSPaths                  # Document paths, schema paths, output paths
    data: EKSData                    # Document metadata, extracted content
    parameters: Dict[str, Any]       # Parser options, health thresholds
    state: EKSState                  # Processing status, document counts
    telemetry: EKSTelemetry          # Performance metrics, memory usage
    schema_registry: SchemaRegistry  # Loaded schema definitions
    config_registry: ConfigRegistry  # Global configuration SSOT
```

---

### 2.3 Standardized Engine I/O for Independent Execution

**Purpose**: Each engine can be run independently with standardized input/output contracts, enabling modular testing, debugging, and reusability.

#### 2.3.1 Standard Input/Output Contract

All engines must implement a standardized I/O contract:

```python
@dataclass
class EngineInput:
    """Standard input contract for all EKS engines"""
    run_id: str                      # Unique identifier for this execution
    data_dir: Path                   # Input data directory
    config_file: Path                # Configuration file path
    schema_dir: Path                 # Schema directory
    output_dir: Path                # Output directory
    parameters: Dict[str, Any]       # Engine-specific parameters
    checkpoint_state: Optional[Dict[str, Any]] = None  # For resume capability

@dataclass
class EngineOutput:
    """Standard output contract for all EKS engines"""
    run_id: str                      # Matches input run_id
    status: str                      # SUCCESS, PARTIAL, FAILED
    output_files: List[Path]         # Generated output files
    metadata: Dict[str, Any]        # Execution metadata
    errors: List[ErrorRecord]        # Any errors encountered
    checkpoint_state: Dict[str, Any] # State for next engine or resume
    telemetry: Dict[str, Any]        # Performance metrics

class BaseEngine(ABC):
    """Abstract base class for all EKS engines"""
    
    @abstractmethod
    def validate_input(self, input_data: EngineInput) -> ValidationResult:
        """Validate input before processing"""
        pass
    
    @abstractmethod
    def execute(self, input_data: EngineInput) -> EngineOutput:
        """Execute the engine logic"""
        pass
    
    @abstractmethod
    def validate_output(self, output: EngineOutput) -> ValidationResult:
        """Validate output before returning"""
        pass
    
    def run(self, input_data: EngineInput) -> EngineOutput:
        """Standard execution flow"""
        # 1. Validate input
        input_validation = self.validate_input(input_data)
        if not input_validation.is_valid:
            return EngineOutput(
                run_id=input_data.run_id,
                status="FAILED",
                output_files=[],
                metadata={},
                errors=[input_validation.to_error()],
                checkpoint_state={},
                telemetry={}
            )
        
        # 2. Execute
        output = self.execute(input_data)
        
        # 3. Validate output
        output_validation = self.validate_output(output)
        if not output_validation.is_valid:
            output.status = "FAILED"
            output.errors.append(output_validation.to_error())
        
        return output
```

#### 2.3.2 Engine-Specific I/O Contracts

Each engine extends the base contract with engine-specific fields:

**Discovery Engine I/O**:
```python
@dataclass
class DiscoveryInput(EngineInput):
    file_types: List[str]            # File types to discover
    include_subfolders: bool         # Recursive scan
    exclude_patterns: List[str]      # Glob patterns to exclude

@dataclass
class DiscoveryOutput(EngineOutput):
    discovered_files: List[FileInfo] # Discovered file metadata
    total_count: int                 # Total files found
```

**Parser Engine I/O**:
```python
@dataclass
class ParserInput(EngineInput):
    files_to_parse: List[Path]       # Files to process
    parser_options: Dict[str, Any]   # Parser-specific options

@dataclass
class ParserOutput(EngineOutput):
    parsed_documents: List[DocumentMetadata] # Parsed document metadata
    failed_files: List[Path]         # Files that failed to parse
```

**Health Scoring Engine I/O**:
```python
@dataclass
class HealthScorerInput(EngineInput):
    documents: List[DocumentMetadata] # Documents to score
    scoring_dimensions: Dict[str, Any] # Scoring configuration

@dataclass
class HealthScorerOutput(EngineOutput):
    scored_documents: List[DocumentMetadata] # Documents with health scores
    score_distribution: Dict[str, int] # Score tier distribution
```

#### 2.3.3 Independent Execution Modes

Engines can be executed independently through multiple interfaces:

**1. Command-Line Interface (CLI)**:
```bash
# Run discovery engine independently
python -m eks.engine.discovery.cli \
    --run-id discovery-001 \
    --data-dir ./data/twrp \
    --config-file ./config/schemas/eks_config.json \
    --output-dir ./output/discovery \
    --file-types pdf,docx \
    --include-subfolders

# Run parser engine independently
python -m eks.engine.parsers.cli \
    --run-id parser-001 \
    --input-file ./output/discovery/discovered_files.json \
    --config-file ./config/schemas/eks_config.json \
    --output-dir ./output/parsed
```

**2. Python API**:
```python
from eks.engine.discovery import DiscoveryEngine
from eks.engine.parsers import ParserEngine

# Run discovery independently
discovery = DiscoveryEngine()
discovery_input = DiscoveryInput(
    run_id="discovery-001",
    data_dir=Path("./data/twrp"),
    config_file=Path("./config/schemas/eks_config.json"),
    schema_dir=Path("./config/schemas"),
    output_dir=Path("./output/discovery"),
    parameters={},
    file_types=["pdf", "docx"],
    include_subfolders=True
)
discovery_output = discovery.run(discovery_input)

# Run parser independently using discovery output
parser = ParserEngine()
parser_input = ParserInput(
    run_id="parser-001",
    data_dir=Path("./data/twrp"),
    config_file=Path("./config/schemas/eks_config.json"),
    schema_dir=Path("./config/schemas"),
    output_dir=Path("./output/parsed"),
    parameters={},
    checkpoint_state=discovery_output.checkpoint_state,
    files_to_parse=[f.path for f in discovery_output.discovered_files]
)
parser_output = parser.run(parser_input)
```

**3. HTTP API**:
```python
# REST API endpoint for independent engine execution
POST /api/v1/engines/discovery
{
    "run_id": "discovery-001",
    "data_dir": "./data/twrp",
    "config_file": "./config/schemas/eks_config.json",
    "schema_dir": "./config/schemas",
    "output_dir": "./output/discovery",
    "parameters": {},
    "file_types": ["pdf", "docx"],
    "include_subfolders": true
}

# Response
{
    "run_id": "discovery-001",
    "status": "SUCCESS",
    "output_files": ["./output/discovery/discovered_files.json"],
    "metadata": {"total_count": 150, "duration_seconds": 2.3},
    "errors": [],
    "checkpoint_state": {...},
    "telemetry": {"memory_mb": 45.2, "cpu_percent": 12.5}
}
```

#### 2.3.4 Engine Chaining and Orchestration

The orchestrator chains engines by passing checkpoint state:

```python
class PipelineOrchestrator:
    def run_pipeline(self, context: EKSPipelineContext) -> EngineOutput:
        final_output = None
        checkpoint_state = {}
        
        # Phase A: Discovery
        discovery_input = DiscoveryInput(
            run_id=context.state.run_id,
            data_dir=context.paths.data_dir,
            config_file=context.paths.config_file,
            schema_dir=context.paths.schema_dir,
            output_dir=context.paths.output_dir / "discovery",
            parameters=context.parameters,
            file_types=context.parameters.get("file_types", ["pdf"]),
            include_subfolders=True
        )
        discovery_output = self.discovery_engine.run(discovery_input)
        checkpoint_state = discovery_output.checkpoint_state
        
        # Phase B: Parsing (uses discovery checkpoint)
        parser_input = ParserInput(
            run_id=context.state.run_id,
            data_dir=context.paths.data_dir,
            config_file=context.paths.config_file,
            schema_dir=context.paths.schema_dir,
            output_dir=context.paths.output_dir / "parsed",
            parameters=context.parameters,
            checkpoint_state=checkpoint_state,
            files_to_parse=[f.path for f in discovery_output.discovered_files]
        )
        parser_output = self.parser_engine.run(parser_input)
        checkpoint_state = parser_output.checkpoint_state
        
        # ... continue with other phases
        
        return final_output
```

#### 2.3.5 Benefits of Standardized I/O

- **Independent Testing**: Each engine can be tested in isolation
- **Modular Debugging**: Failed engines can be re-run without reprocessing entire pipeline
- **Reusability**: Engines can be reused in different pipelines or workflows
- **Parallel Execution**: Independent engines can run in parallel where possible
- **Clear Contracts**: Input/output validation ensures data quality between engines
- **Resume Capability**: Checkpoint state enables resumption from any phase

### 2.4 Engine I/O Analysis

This section provides a high-level analysis of engine I/O patterns across all EKS phases, documenting the distribution of input/output types, database operations, and file operations. This analysis informs the standardized I/O contract design.

**Summary**: 60 engines across 5 phases, with 50% involving database operations (DuckDB, Neo4j, Qdrant, Redis), 25% involving file operations (mostly read-only), and 15% being pure in-memory transformations. Phase 3 has the most database operations (22 engines touching Neo4j).

#### Phase 1 Engines (Foundation)

| Engine | Input Type | Output Type | Database Operations | File Operations | Description |
|--------|-----------|------------|-------------------|----------------|-------------|
| Schema Loader | JSON files (schema/config) | In-memory (loaded schemas) | None | Read: `eks/config/schemas/*.json` | Loads and validates 3-layer schema definitions |
| Config Registry | JSON config files | In-memory (config dict) | None | Read: `eks_config.json` | SSOT global parameter access |
| Document Registry | In-memory (metadata dict) | DuckDB (documents table) | CRUD: DuckDB `documents` table | None | Document metadata storage with revision flags |
| Revision Manager | In-memory (revision data) | DuckDB (revision fields) | Read/Update: DuckDB | None | Revision management logic |
| File Scanner | File system (directory walk) | In-memory (file list) + DuckDB (placeholder rows) | Insert: DuckDB `documents` table | Read: Scan `data/` directory | Walks project directory, validates extensions |
| Parser Router | In-memory (file path) | In-memory (parser instance) | None | Read: File content | Routes file_type → parser class |
| PDF Parser | File (PDF) | In-memory (content + metadata) | None | Read: `.pdf` files | Parses PDF documents |
| DOCX Parser | File (DOCX) | In-memory (content + metadata) | None | Read: `.docx` files | Parses Word documents |
| XLSX Parser | File (XLSX) | In-memory (content + metadata) | None | Read: `.xlsx` files | Parses Excel spreadsheets |
| DGN Parser (stub) | File (DGN) | In-memory (stub response) | None | Read: `.dgn` files | CAD parser stub (deferred) |
| DWG Parser (stub) | File (DWG) | In-memory (stub response) | None | Read: `.dwg` files | CAD parser stub (deferred) |
| Health Scorer | In-memory (document data) | DuckDB (health_score field) | Update: DuckDB `documents` table | None | 6-dimension health scoring |
| Structure Detector | In-memory (parsed content) | DuckDB (document_elements table) | Insert: DuckDB `document_elements` table | None | Detects structural elements |
| Pipeline Orchestrator | In-memory (orchestration state) | DuckDB (multiple tables) | Multiple: DuckDB tables | None | Coordinates scan→register→route→parse→detect→score→update |
| Manual Review Manager | In-memory (review data) | DuckDB (extract_status field) | Update: DuckDB `documents` table | None | Manual review workflow |
| Error Manager | In-memory (error data) | DuckDB (error logging) | Insert: DuckDB error tables | Write: `eks/log/issue_log.md` | Error catalog management |
| Message Manager | In-memory (message data) | In-memory (message dict) | None | Write: `eks/log/` | Pipeline message catalog |

#### Phase 2 Engines (Chunking & Embedding)

| Engine | Input Type | Output Type | Database Operations | File Operations | Description |
|--------|-----------|------------|-------------------|----------------|-------------|
| Chunker (size-based) | In-memory (document text) | In-memory (chunks) | None | None | Fixed token/character window chunking |
| Chunker (section-aware) | In-memory (document text + structure) | In-memory (chunks) | None | None | Section-aware chunking |
| Chunk Registry | In-memory (chunk metadata) | DuckDB (chunk_registry table) | CRUD: DuckDB `chunk_registry` table | None | Parent-child chunk management |
| Asset Chunk Registry | In-memory (asset metadata) | DuckDB (asset_records table) | CRUD: DuckDB `asset_records` table | None | Asset record management (no parent-child) |
| OpenAI Embedder | In-memory (text) | In-memory (vector) | None | None | OpenAI embeddings API |
| Ollama Embedder | In-memory (text) | In-memory (vector) | None | None | Ollama local embeddings |
| Hybrid Strategy | In-memory (text + metadata) | In-memory (header + text) | None | None | Contextual header construction |
| Qdrant Store (chunks) | In-memory (vectors + payload) | Qdrant (eks_chunks collection) | Upsert/Search: Qdrant | None | Vector storage for document chunks |
| Qdrant Store (assets) | In-memory (vectors + payload) | Qdrant (eks_assets collection) | Upsert/Search: Qdrant | None | Vector storage for asset summaries |
| Asset Text Builder | In-memory (asset data) | In-memory (contextual text) | None | None | Builds asset contextual summaries |

#### Phase 3 Engines (Knowledge Graph)

| Engine | Input Type | Output Type | Database Operations | File Operations | Description |
|--------|-----------|------------|-------------------|----------------|-------------|
| Neo4j Store | In-memory (node/edge data) | Neo4j (graph DB) | CRUD: Neo4j nodes/relationships | None | Neo4j graph store implementation |
| Graph Schema | In-memory (schema definitions) | In-memory (node/label types) | None | None | Node label and relationship definitions |
| Document Node Builder | In-memory (document metadata) | Neo4j (Document nodes) | Insert: Neo4j | None | Creates document nodes |
| Chunk Node Builder | In-memory (chunk metadata) | Neo4j (Chunk nodes) | Insert: Neo4j | None | Creates chunk nodes |
| Base Asset Loader | File (Excel datadrop) | In-memory (asset data) | None | Read: Excel datadrop sheets | Reads sheet data by tag_type |
| Equipment Loader | File (Excel) | In-memory (equipment data) | None | Read: Equipment sheet | Loads AT_EQUIP, AT_EQPMP, etc. |
| Instrument Loader | File (Excel) | In-memory (instrument data) | None | Read: Instrument sheet | Loads AT_INST_, AT_INST_CS, etc. |
| Valve Loader | File (Excel) | In-memory (valve data) | None | Read: Valve sheet | Loads AT_CVALVE, AT_PSV, AT_HVALVE |
| Pipeline Loader | File (Excel) | In-memory (pipeline data) | None | Read: Pipeline sheet | Loads AT_PROCESS + CONNECTS_TO edges |
| Motor Loader | File (Excel) | In-memory (motor data) | None | Read: Motor sheet | Loads AT_MOTOR |
| Inline Component Loader | File (Excel) | In-memory (inline data) | None | Read: Inline sheet | Loads AT_INCOMP |
| Sheet Orchestrator | File (Excel) | Neo4j + Qdrant | Insert: Neo4j, Upsert: Qdrant | Read: Excel sheets | Orchestrates sheet-by-sheet loading |
| Relationship Builders | In-memory (relationship data) | Neo4j (edges) | Insert: Neo4j relationships | None | Doc-to-doc, doc-to-asset, asset-to-asset edges |
| Asset Embed Trigger | In-memory (asset data) | Qdrant (eks_assets) | Upsert: Qdrant | None | Triggers asset embedding after Neo4j load |
| P&ID-to-Asset Linker | In-memory (P&ID data) | Neo4j (REFERENCED_BY_DWG edges) | Insert: Neo4j | None | Links P&ID to assets |
| Unit/Service Grouping | In-memory (unit/service data) | Neo4j (Unit/Service nodes) | Insert: Neo4j | None | Creates unit/service grouping nodes |
| Pipeline-to-Component Linker | In-memory (pipeline data) | Neo4j (CONNECTS_TO edges) | Insert: Neo4j | None | Creates pipeline-to-component edges |
| Automated Metadata Extractor | File (document) | In-memory (extended metadata) | None | Read: Document cover sheets | Extracts 11 extended fields |
| Ontology Node Loader | In-memory (ontology config) | Neo4j (OntologyClass nodes) | Insert: Neo4j | None | Loads T-Box classes |
| IS_A Relationship Builder | In-memory (mapping data) | Neo4j (IS_A edges) | Insert: Neo4j | None | Links assets to ontology classes |
| Dynamic Ontology Mapper | In-memory (AT_ codes) | In-memory (ontology classes) | None | None | Maps AT_ codes to ontology classes |
| PhysicalObject Builder | In-memory (serial data) | Neo4j (PhysicalObject nodes) | Insert: Neo4j | None | Creates PhysicalObject nodes |
| SHACL Validator | Neo4j (graph) | In-memory (violations) | Read: Neo4j | Write: `eks/log/issue_log.md` | Post-load constraint validation |
| Directional Flow Builder | In-memory (TO_COMPONENT data) | Neo4j (FLOWS_TO edges) | Insert: Neo4j | None | Creates directional flow edges |
| Electrical & Control Linker | In-memory (MCC/PLC data) | Neo4j (power/control edges) | Insert: Neo4j | None | Creates power and control edges |
| Governance Resolver | In-memory (design specs) | Neo4j (GOVERNED_BY edges) | Insert: Neo4j | None | Links assets to engineering standards |
| Set Point Linker | In-memory (set point data) | Neo4j (SET_POINT_IN edges) | Insert: Neo4j | None | Links set points to documents |
| Document Revision Graph Builder | In-memory (revision data) | Neo4j (SUPERSEDES edges) | Insert: Neo4j | None | Creates revision chains |
| Cross-Doc Reference Extractor | In-memory (document content) | Neo4j (REFERENCES_DOC edges) | Insert: Neo4j | None | Finds document references in text |
| Asset Tag Linker | In-memory (asset_tags JSON) | Neo4j (REFERENCES_ASSET edges) | Insert: Neo4j | None | Links documents to assets |

#### Phase 4 Engines (Retrieval Pipeline)

| Engine | Input Type | Output Type | Database Operations | File Operations | Description |
|--------|-----------|------------|-------------------|----------------|-------------|
| Metadata Filter | In-memory (query + filters) | In-memory (candidate set) | Read: DuckDB, Neo4j | None | Filters by doc + asset attributes |
| Revision-Aware Filter | In-memory (revision filter) | In-memory (filtered set) | Read: DuckDB | None | Applies latest/specific revision filter |
| Graph Expander | In-memory (candidate set) | In-memory (expanded set) | Read: Neo4j | None | Expands via graph relationships |
| Vector Search | In-memory (query embedding) | In-memory (vector results) | Search: Qdrant | None | Qdrant similarity search |
| Keyword Search | In-memory (query text) | In-memory (keyword results) | Search: DuckDB | None | BM25/full-text search |
| Hybrid Search Merger | In-memory (vector + keyword results) | In-memory (merged results) | None | None | Merges and deduplicates results |
| Scorer | In-memory (candidates) | In-memory (scored candidates) | None | None | Scores by relevance |
| Reranker | In-memory (top-k candidates) | In-memory (reranked candidates) | None | None | Cross-encoder or rule-based reranking |
| Context Assembler | In-memory (top-k chunks) | In-memory (context window) | None | None | Selects and orders chunks |
| OpenAI LLM | In-memory (prompt + context) | In-memory (answer + citations) | None | None | OpenAI chat completions |
| Ollama LLM | In-memory (prompt + context) | In-memory (answer + citations) | None | None | Ollama local chat |
| Pipeline Orchestrator | In-memory (query) | In-memory (final answer) | Read: DuckDB, Neo4j, Qdrant | None | End-to-end query execution |
| Asset Query Handler | In-memory (asset query) | In-memory (asset card data) | Read: Neo4j, Qdrant | None | Asset card details + P&ID links |
| Dual-Collection Merger | In-memory (eks_chunks + eks_assets) | In-memory (merged results) | None | None | Merges dual Qdrant collections |
| Ontology Resolver | In-memory (user label) | In-memory (AT_ codes) | Read: Neo4j | None | Resolves ontology classes |
| CONTROLS/FEEDS_FROM Traverser | In-memory (asset node) | In-memory (related assets) | Read: Neo4j | None | Traverses control relationships |
| PhysicalObject Lookup | In-memory (tag node) | In-memory (physical equipment) | Read: Neo4j | None | INSTALLED_AT reverse traversal |

#### Phase 5 Engines (UI Integration)

| Engine | Input Type | Output Type | Database Operations | File Operations | Description |
|--------|-----------|------------|-------------------|----------------|-------------|
| Retrieval Cache (memory) | In-memory (query hash) | In-memory (cached result) | None | None | In-memory LRU cache |
| Retrieval Cache (Redis) | In-memory (query hash) | Redis (cached result) | Read/Write: Redis | None | Redis-backed cache |
| Backend API (FastAPI) | HTTP request | HTTP response | Read: DuckDB, Neo4j, Qdrant | None | API endpoints |
| Query Route | HTTP (query + filters) | HTTP (answer + citations) | Read: All DBs | None | `/query` endpoint |
| Ingest Route | HTTP (file upload) | HTTP (ingestion status) | Write: All DBs | Read: Uploaded file | `/ingest` endpoint |
| Assets Route | HTTP (asset filters) | HTTP (asset cards) | Read: Neo4j, Qdrant | None | `/assets` endpoint |
| Status Route | HTTP (status request) | HTTP (system status) | Read: All DBs | None | `/status`, `/health` endpoints |
| Ontology Classes Route | HTTP (class request) | HTTP (class hierarchy) | Read: Neo4j | None | `/ontology/classes` endpoint |
| Frontend UI | HTTP (user interaction) | HTTP (API calls) | None | Read: Static assets | React SPA / HTML/JS |

#### I/O Pattern Summary

| I/O Type | Count | Percentage |
|----------|-------|------------|
| **File Operations (Read)** | 12 | ~20% |
| **File Operations (Write)** | 3 | ~5% |
| **DuckDB Operations** | 8 | ~13% |
| **Neo4j Operations** | 22 | ~37% |
| **Qdrant Operations** | 5 | ~8% |
| **Redis Operations** | 1 | ~2% |
| **In-Memory Only** | 9 | ~15% |
| **Total Engines** | 60 | 100% |

**Key Observations:**
- **Database-heavy**: 50% of engines involve database operations (DuckDB, Neo4j, Qdrant, Redis)
- **File-light**: Only 25% involve file operations (mostly read-only)
- **In-memory significant**: 15% are pure in-memory transformations
- **Neo4j dominant**: Phase 3 has the most database operations (22 engines touching Neo4j)

---

---

## 6. Implementation Evaluation

This section consolidates implementation-related information for evaluating current status and planning future work.

### 6.1 Current State Assessment (Phase 1)

#### Completed Components

- ✅ Schema Loader (`eks/engine/core/schema_loader.py`)
- ✅ Config Registry (`eks/engine/core/config_registry.py`)
- ✅ Document Registry (`eks/engine/core/registry.py`)
- ✅ Revision Manager (`eks/engine/core/revision.py`)
- ✅ File Scanner (`eks/engine/core/discovery.py`)
- ✅ Parser Router (`eks/engine/core/router.py`)
- ✅ Health Scorer (`eks/engine/core/health_scorer.py`)
- ✅ Parsers (PDF, DOCX, XLSX, DGN, DWG)
- ✅ Schema Files (eks/config/schemas/)

#### Architecture Gaps

| Pattern | Current State | Gap Description |
| :--- | :--- | :--- |
| PipelineContext | ❌ Not implemented | Loose variable passing between components |
| Dependency Injection | ❌ Not implemented | Direct instantiation of parsers and scorers |
| Phase-Based Orchestration | ⚠️ Partial | PipelineOrchestrator exists but lacks clear checkpoints |
| Telemetry Heartbeat | ❌ Not implemented | No progress tracking or performance monitoring |
| Schema-Driven Config | ✅ Implemented | JSON-based configuration exists |
| Multi-Stage Validation | ⚠️ Partial | Schema validation only, no project setup validation |
| Error Catalog | ✅ Implemented | Hierarchical error codes exist |
| UI Contracts | ❌ Not implemented | No backend contracts for UI integration |
| Project Setup Validation | ❌ Not implemented | No automated project structure verification |
| Foundation/Utility Separation | ⚠️ Partial | engine/ exists but not separated into core/domain |

### 6.2 Implementation Guidance

The detailed implementation tasks for applying universal pipeline architecture patterns to EKS are documented in the respective phase workplans:

- **Phase 1 Foundation Enhancement**: See [phase_1_foundation_workplan.md](phase_1_foundation_workplan.md) for detailed tasks on PipelineContext, Dependency Injection, Phase-Based Orchestration, Telemetry Heartbeat, UI Contracts, Project Setup Validation, and Standardized Engine I/O.
- **Phase 2–5**: Future phases will incorporate these patterns as they are implemented, following the architecture defined in this appendix.

### 6.3 Architecture Comparison

| Aspect | EKS (Current) | EKS (Proposed) | Universal Pattern |
| :--- | :--- | :--- | :--- |
| Context Management | ❌ Loose variables | ✅ EKSPipelineContext | PipelineContext Pattern |
| Dependency Injection | ❌ Direct instantiation | ✅ Factory Pattern | Dependency Injection Pattern |
| Phase Orchestration | ⚠️ Partial | ✅ 5 Phases (A-E) | Phase-Based Orchestration Pattern |
| Telemetry | ❌ None | ✅ Heartbeat System | Telemetry Heartbeat Pattern |
| Schema-Driven Config | ✅ JSON-based | ✅ JSON-based + Pipeline Config | Schema-Driven Configuration Pattern |
| Validation | ⚠️ Schema only | ✅ Multi-Stage | Multi-Stage Validation Pattern |
| Error Catalog | ✅ Hierarchical | ✅ Hierarchical + Pipeline Errors | Standardized Error Catalog Pattern |
| UI Contracts | ❌ None | ✅ Defined | UI Contract Pattern |
| Project Setup | ❌ None | ✅ Validator | Project Setup Validation Pattern |
| Foundation Separation | ⚠️ Partial | ✅ core/domain | Foundation/Utility Separation Pattern |

---

## 3. Benefits

### 3.1 Maintainability

- **Reduced Complexity**: Centralized context management reduces function signature complexity (5-7 parameters → 1-2)
- **Clear Separation**: Foundation/utility separation makes code easier to navigate
- **Consistent Patterns**: Uniform patterns across components reduce cognitive load

### 3.2 Testability

- **Dependency Injection**: Easy mocking for unit tests
- **Phase-Based Testing**: Each phase can be tested independently
- **Contract Validation**: UI contracts enable automated API testing

### 3.3 Observability

- **Telemetry**: Real-time progress tracking and performance monitoring
- **Error Catalog**: Structured error tracking with resolution guidance
- **Validation**: Multi-stage validation provides early error detection

### 3.4 Flexibility

- **Swappable Components**: Factory pattern enables easy component replacement
- **Schema-Driven**: Configuration changes without code modifications
- **Platform Independence**: Cross-platform path handling

### 3.5 User Experience

- **Progress Visibility**: Heartbeat system provides real-time feedback
- **Clear Errors**: Standardized error codes with resolution guidance
- **Setup Validation**: Automated project setup verification

---

## 4. Risks and Mitigation

| Risk | Likelihood | Impact | Mitigation |
| :--- | :---: | :---: | :--- |
| Refactoring breaks existing functionality | Medium | High | Maintain backward compatibility layer; comprehensive testing |
| Performance overhead from new abstractions | Low | Medium | Performance monitoring; optimize hot paths |
| Context object becomes too large | Medium | Medium | Use nested dataclasses; validate context size |
| Factory pattern adds complexity | Low | Low | Document factories thoroughly; provide examples |
| Telemetry adds runtime overhead | Low | Low | Configurable heartbeat intervals; lightweight payload |

---

### 6.4 Success Criteria

- ✅ EKSPipelineContext implemented and integrated across all engines
- ✅ Dependency injection factories for parsers and health scorer
- ✅ Phase-based orchestration with telemetry heartbeat (5 phases A-E)
- ✅ UI contracts for document selection and pipeline config
- ✅ Project setup validator with auto-creation
- ✅ All existing Phase 1 functionality preserved
- ✅ Test coverage >90% for new components
- ✅ Performance impact <5% overhead
- ✅ Documentation updated with new patterns
- ✅ knowledge.json updated with new architecture

### 6.5 Next Steps

1. **Review and Approval**: Stakeholder review of this appendix
2. **Phase 1.2.1 Start**: Begin foundation layer enhancement
3. **Weekly Check-ins**: Progress review at end of each phase
4. **Integration Testing**: Validate new patterns with existing Phase 1 components
5. **Documentation Update**: Update knowledge.json with new architecture

---

## 5. References

### 5.1 Universal Architecture

- [Universal Pipeline Architecture Design](../../common/universal_pipeline_architecture_design.md) — Universal patterns and guidelines

### 5.2 EKS Documents

- [Phase 1 Foundation Workplan](phase_1_foundation_workplan.md) — Foundation module specification
- [Phase 1.2 Interactive UI Workplan](phase_1.2_interactive_ui_workplan.md) — UI and sub-pipeline workplan
- [knowledge.json](../knowledge.json) — Project knowledge base

### 5.3 DCC Reference Implementations

- [Pipeline Architecture Design Workplan](../../dcc/workplan/pipeline_architecture/pipeline_architecture_workplan/pipeline_architecture_design_workplan.md)
- [Lessons Learned and Best Practices](../../dcc/workplan/pipeline_architecture/pipeline_architecture_workplan/lessons_learned_best_practices.md)

---

---

**End of Appendix F**

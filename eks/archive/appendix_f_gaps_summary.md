# Appendix F Architecture Gaps Summary

**Document ID**: WP-EKS-APPENDIX-F-GAPS-001
**Current Version**: 1.0
**Status**: 📋 Review
**Date**: 2026-06-29
**Purpose**: Summarize gaps between Appendix F architecture patterns and current phase workplan implementations

---

## Executive Summary

Appendix F defines 8 universal pipeline architecture patterns to be applied across all EKS phases. Currently, only Phase 1 acknowledges these patterns (as future work in Section 16), while Phases 2-5 do not reference or plan for these patterns. This creates a significant architectural gap between the proposed design and actual implementation plans.

---

## Appendix F Architecture Patterns

The following 8 patterns are defined in Appendix F:

1. **PipelineContext** - Centralized state management via EKSPipelineContext dataclass
2. **Dependency Injection** - Factory pattern for parser, scorer, and component creation
3. **Phase-Based Orchestration** - Clear phase checkpoints (A-E) with telemetry heartbeat
4. **Telemetry Heartbeat** - Progress tracking and performance monitoring at checkpoints
5. **Standardized Engine I/O** - EngineInput/EngineOutput contracts for independent execution
6. **UI Contracts** - Backend contracts (DocumentSelectionContract, PipelineConfigContract)
7. **Project Setup Validation** - Automated project structure verification
8. **Foundation/Utility Separation** - core/ domain separation in engine/ package

---

## Phase-by-Phase Gap Analysis

### Phase 1 Foundation (Status: ✅ COMPLETE)

**Current Implementation:**
- Has basic foundation components: schema loader, config registry, document registry, revision manager, file scanner, parser router, health scorer, parsers
- Schema-driven configuration via JSON (eks_config.json)
- Error catalog with hierarchical error codes
- Pipeline orchestrator exists (partial implementation)

**Gaps:**
- ❌ PipelineContext not implemented - loose variable passing between components
- ❌ Dependency Injection not implemented - direct instantiation of parsers and scorers
- ⚠️ Phase-Based Orchestration partial - PipelineOrchestrator lacks clear checkpoints
- ❌ Telemetry Heartbeat not implemented - no progress tracking or performance monitoring
- ⚠️ Multi-Stage Validation partial - schema validation only, no project setup validation
- ❌ UI Contracts not implemented - no backend contracts for UI integration
- ❌ Project Setup Validation not implemented - no automated project structure verification
- ⚠️ Foundation/Utility Separation partial - engine/ exists but not separated into core/domain

**Acknowledgment:**
- Section 16 (Phase 1.2 Foundation Enhancement) documents 19 tasks to implement these patterns
- Status: 🔷 PLANNED (future work)
- This indicates Phase 1 is aware of the gaps but has not implemented them yet

---

### Phase 2 Chunking & Embedding (Status: 🔵 DRAFT)

**Current Implementation:**
- Status: DRAFT - PENDING APPROVAL
- Focus: chunking, embedding, vector storage (Qdrant)
- Parent-child chunk registry with metadata
- Hybrid embedding strategy
- Plug-in embedding providers (OpenAI, Ollama)

**Gaps:**
- ❌ No mention of PipelineContext for state management
- ❌ No mention of Dependency Injection for chunker/embedder factories
- ❌ No mention of Phase-Based Orchestration with checkpoints
- ❌ No mention of Telemetry Heartbeat for progress tracking
- ❌ No mention of Standardized Engine I/O contracts (ChunkerInput/ChunkerOutput, EmbedderInput/EmbedderOutput)
- ❌ No mention of UI Contracts (though UI is not the focus of this phase)
- ❌ No mention of Project Setup Validation
- ❌ No mention of Foundation/Utility Separation (chunkers/embedders placement)

**Recommendation:**
- Add standardized I/O contracts for chunkers and embedders per Appendix F Section 2.3
- Consider factory pattern for embedding provider selection
- Add telemetry checkpoints for chunking progress

---

### Phase 3 Knowledge Graph (Status: 🔵 DRAFT)

**Current Implementation:**
- Status: DRAFT - PENDING APPROVAL
- Focus: Neo4j knowledge graph, asset loaders, ontology integration
- Structured asset loaders from Excel datadrop
- Dynamic ontology ingestion
- SHACL constraint validation

**Gaps:**
- ❌ No mention of PipelineContext for graph state management
- ❌ No mention of Dependency Injection for asset loader factories
- ❌ No mention of Phase-Based Orchestration with graph loading checkpoints
- ❌ No mention of Telemetry Heartbeat for batch loading progress
- ❌ No mention of Standardized Engine I/O contracts (AssetLoaderInput/AssetLoaderOutput, GraphStoreInput/GraphStoreOutput)
- ❌ No mention of UI Contracts (though UI is not the focus of this phase)
- ❌ No mention of Project Setup Validation
- ❌ No mention of Foundation/Utility Separation (asset loaders/graph store placement)

**Recommendation:**
- Add standardized I/O contracts for asset loaders and graph operations per Appendix F Section 2.3
- Consider factory pattern for asset loader instantiation (already has zero-code extensibility via config)
- Add telemetry checkpoints for batch loading progress (7,681 items across 7 categories)
- This phase has the most database operations (22 engines touching Neo4j) - would benefit most from standardized I/O

---

### Phase 4 Retrieval Pipeline (Status: 🔵 DRAFT)

**Current Implementation:**
- Status: DRAFT - PENDING APPROVAL
- Focus: hybrid retrieval, scoring, reranking, LLM answering
- Metadata filtering, graph expansion, vector search
- Revision-aware and asset-aware retrieval

**Gaps:**
- ❌ No mention of PipelineContext for retrieval state management
- ❌ No mention of Dependency Injection for LLM provider factories
- ❌ No mention of Phase-Based Orchestration with retrieval pipeline checkpoints
- ❌ No mention of Telemetry Heartbeat for retrieval progress tracking
- ❌ No mention of Standardized Engine I/O contracts (RetrieverInput/RetrieverOutput, ScorerInput/ScorerOutput, LLMInput/LLMOutput)
- ❌ No mention of UI Contracts (though this phase feeds into Phase 5 UI)
- ❌ No mention of Project Setup Validation
- ❌ No mention of Foundation/Utility Separation (retrieval components placement)

**Recommendation:**
- Add standardized I/O contracts for retrieval pipeline stages per Appendix F Section 2.3
- Consider factory pattern for LLM provider selection (OpenAI, Ollama)
- Add telemetry checkpoints for multi-stage retrieval pipeline
- Define UI contracts for query/response interface to Phase 5

---

### Phase 5 UI Integration (Status: 🔵 DRAFT)

**Current Implementation:**
- Status: DRAFT - PENDING APPROVAL
- Focus: web UI, retrieval cache, system integration
- Asset browsing and filtering
- Ontology-driven UI facets

**Gaps:**
- ❌ No mention of PipelineContext for UI state management
- ❌ No mention of Dependency Injection for cache provider factories
- ❌ No mention of Phase-Based Orchestration with UI interaction checkpoints
- ❌ No mention of Telemetry Heartbeat for UI performance monitoring
- ❌ No mention of Standardized Engine I/O contracts (UIInput/UIOutput, CacheInput/CacheOutput)
- ❌ **Critical Gap**: No mention of UI Contracts (DocumentSelectionContract, PipelineConfigContract) despite being the UI phase
- ❌ No mention of Project Setup Validation
- ❌ No mention of Foundation/Utility Separation (UI components placement)

**Recommendation:**
- **Priority**: Implement UI Contracts per Appendix F Section 3.1 (DocumentSelectionContract, PipelineConfigContract)
- Add standardized I/O contracts for cache operations per Appendix F Section 2.3
- Consider factory pattern for cache provider selection (Redis, in-memory)
- Add telemetry for UI response times and cache hit rates

---

## Cross-Phase Architecture Pattern Gaps

### Pattern 1: PipelineContext
- **Status**: ❌ Not implemented in any phase
- **Impact**: Loose variable passing, difficult state management across phases
- **Recommendation**: Implement in Phase 1.2 (already planned), then integrate into Phases 2-5

### Pattern 2: Dependency Injection
- **Status**: ❌ Not implemented in any phase
- **Impact**: Direct instantiation, difficult testing and component swapping
- **Recommendation**: Implement factories in Phase 1.2 (already planned), then use in Phases 2-5 for:
  - Phase 2: EmbedderFactory, ChunkerFactory
  - Phase 3: AssetLoaderFactory, GraphStoreFactory
  - Phase 4: LLMProviderFactory, RerankerFactory
  - Phase 5: CacheProviderFactory

### Pattern 3: Phase-Based Orchestration
- **Status**: ⚠️ Partial (Phase 1 only)
- **Impact**: No clear checkpoints, difficult progress tracking and rollback
- **Recommendation**: Enhance PipelineOrchestrator with 5 phases (A-E) and telemetry heartbeat in Phase 1.2, then apply to all phases

### Pattern 4: Telemetry Heartbeat
- **Status**: ❌ Not implemented in any phase
- **Impact**: No progress tracking, no performance monitoring
- **Recommendation**: Implement in Phase 1.2 (already planned), then add checkpoints in:
  - Phase 2: Chunking progress, embedding progress
  - Phase 3: Batch loading progress (7,681 items)
  - Phase 4: Retrieval pipeline stages
  - Phase 5: UI response times, cache metrics

### Pattern 5: Standardized Engine I/O
- **Status**: ❌ Not implemented in any phase
- **Impact**: No independent engine execution, difficult testing and debugging
- **Recommendation**: Implement base contracts in Phase 1.2 (already planned), then create domain-specific contracts:
  - Phase 2: ChunkerInput/Output, EmbedderInput/Output
  - Phase 3: AssetLoaderInput/Output, GraphStoreInput/Output
  - Phase 4: RetrieverInput/Output, ScorerInput/Output, LLMInput/Output
  - Phase 5: UIInput/Output, CacheInput/Output

### Pattern 6: UI Contracts
- **Status**: ❌ Not implemented in any phase
- **Impact**: No backend contracts for UI integration, potential API inconsistencies
- **Recommendation**: Implement in Phase 1.2 (already planned), then use in Phase 5:
  - DocumentSelectionContract for document selection UI
  - PipelineConfigContract for pipeline configuration UI
  - AssetQueryContract for asset browsing UI

### Pattern 7: Project Setup Validation
- **Status**: ❌ Not implemented in any phase
- **Impact**: No automated project structure verification, potential setup errors
- **Recommendation**: Implement in Phase 1.2 (already planned), then validate before each phase execution

### Pattern 8: Foundation/Utility Separation
- **Status**: ⚠️ Partial (Phase 1 only)
- **Impact**: engine/ not separated into core/domain, unclear code organization
- **Recommendation**: Restructure engine/ package in Phase 1.2 (already planned):
  - core/: context, base, telemetry, validator, factories, orchestrator
  - parsers/: document parsers
  - discovery/: file scanner
  - router/: parser router
  - registry/: document registry
  - revision/: revision manager
  - health/: health scorer
  - structure/: structure detector

---

## Summary Table

| Pattern | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Phase 5 | Overall |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| PipelineContext | 🔷 PLANNED | ❌ | ❌ | ❌ | ❌ | 🔷 PLANNED |
| Dependency Injection | 🔷 PLANNED | ❌ | ❌ | ❌ | ❌ | 🔷 PLANNED |
| Phase-Based Orchestration | ⚠️ Partial | ❌ | ❌ | ❌ | ❌ | ⚠️ Partial |
| Telemetry Heartbeat | 🔷 PLANNED | ❌ | ❌ | ❌ | ❌ | 🔷 PLANNED |
| Standardized Engine I/O | 🔷 PLANNED | ❌ | ❌ | ❌ | ❌ | 🔷 PLANNED |
| UI Contracts | 🔷 PLANNED | ❌ | ❌ | ❌ | ❌ | 🔷 PLANNED |
| Project Setup Validation | 🔷 PLANNED | ❌ | ❌ | ❌ | ❌ | 🔷 PLANNED |
| Foundation/Utility Separation | ⚠️ Partial | ❌ | ❌ | ❌ | ❌ | ⚠️ Partial |

**Legend**: ✅ Implemented | ⚠️ Partial | ❌ Not Implemented | 🔷 PLANNED

---

## Recommendations

### Immediate Actions (Phase 1.2)
1. **Implement Phase 1.2 Foundation Enhancement** (19 tasks already documented in Phase 1 Section 16)
2. **Update Phase 2-5 workplans** to reference and integrate these patterns
3. **Add standardized I/O contracts** to each phase's task breakdown

### Phase-Specific Updates
1. **Phase 2**: Add ChunkerInput/Output, EmbedderInput/Output contracts; add telemetry for chunking/embedding progress
2. **Phase 3**: Add AssetLoaderInput/Output, GraphStoreInput/Output contracts; add telemetry for batch loading (7,681 items)
3. **Phase 4**: Add RetrieverInput/Output, ScorerInput/Output, LLMInput/Output contracts; add telemetry for retrieval pipeline stages; define UI contracts for query/response
4. **Phase 5**: Implement UI Contracts (DocumentSelectionContract, PipelineConfigContract); add UIInput/Output, CacheInput/Output contracts; add telemetry for UI performance

### Cross-Phase Coordination
1. **Create shared I/O contract library** in `eks/engine/core/io_contracts.py` (per Phase 1.2 T1.2.5)
2. **Create domain-specific contract modules** in each engine package (per Phase 1.2 T1.2.6)
3. **Add CLI entry points** for independent engine execution (per Phase 1.2 T1.2.7)
4. **Add HTTP API endpoints** for independent engine execution (per Phase 1.2 T1.2.8)

---

## Conclusion

Appendix F defines a comprehensive set of universal pipeline architecture patterns that are currently not implemented in Phases 2-5 and only planned for Phase 1.2. This creates a significant architectural gap between the proposed design and actual implementation. The recommended approach is to:

1. **Complete Phase 1.2 Foundation Enhancement** to establish the base patterns
2. **Update Phases 2-5 workplans** to integrate these patterns
3. **Add standardized I/O contracts** to enable independent engine execution
4. **Add telemetry checkpoints** for progress tracking and performance monitoring

This will ensure consistency across all phases and enable the benefits outlined in Appendix F: improved maintainability, testability, observability, and user experience.

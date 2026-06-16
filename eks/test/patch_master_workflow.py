with open('eks/workplan/eks_system_workplan.md', 'r', encoding='utf-8') as f:
    c = f.read()

# ── Version + date ────────────────────────────────────────────────────────────
c = c.replace('**Current Version**: 0.6  ', '**Current Version**: 0.7  ')
c = c.replace('**Last Updated**: 2026-06-18  \n\n---\n\n## 1.', '**Last Updated**: 2026-06-18  \n\n---\n\n## 1.')

# ── Revision entry ────────────────────────────────────────────────────────────
c = c.replace(
    '| 0.6     | 2026-06-18 | System | Phase 1 marked PASS: T1.20 complete, all success criteria met, test_phase1.py updated, logs and report updated. R36 and R39 status updated to PASS in master scope table. |',
    '| 0.6     | 2026-06-18 | System | Phase 1 marked PASS: T1.20 complete, all success criteria met, test_phase1.py updated, logs and report updated. R36 and R39 status updated to PASS in master scope table. |\n| 0.7     | 2026-06-18 | System | Added Section 10: EKS Pipeline Architecture — full workflow diagram covering ingestion, embedding, graph, retrieval, and UI across all 5 phases. Added R40 (Asset Embedding Strategy), R41 (Asset Chunk Registry Extension), R42 (Asset Vector Upsert) based on datadrop embedding analysis. Updated scope table, phase index, and index of content. |'
)

# ── R40–R42 scope rows ────────────────────────────────────────────────────────
c = c.replace(
    '| R39 | Schema               | Zero-Code Asset Extensibility            | `conditional_fragments` structure in `eks_asset_setup_schema.json` and `eks_asset_config.json` enables adding new AT_ tag types and conditional fragment rules without any code changes — config-only update | 🔶 PARTIAL | 1,3   |\n\n**Status Legend:**',
    '| R39 | Schema               | Zero-Code Asset Extensibility            | `conditional_fragments` structure in `eks_asset_setup_schema.json` and `eks_asset_config.json` enables adding new AT_ tag types and conditional fragment rules without any code changes — config-only update | 🔶 PARTIAL | 1,3   |\n| R40 | Embedding            | Asset Embedding Strategy                 | Define asset-to-text representation (contextual header + key field summary); store asset vectors in separate Qdrant collection `eks_assets`; prevent null/code pollution | 🔷 PLANNED | 2,3   |\n| R41 | Knowledge Base       | Asset Chunk Registry Extension           | Extend chunk registry to support asset records keyed on `keytag` (no parent-child); asset metadata schema: keytag, tag_type, unit, service, tag_no, p_and_id_file | 🔷 PLANNED | 2     |\n| R42 | Knowledge Base       | Asset Vector Upsert                      | When datadrop is re-exported, invalidate and re-embed affected asset vectors in `eks_assets` collection; align with Neo4j node upsert strategy | 🔷 PLANNED | 3     |\n\n**Status Legend:**'
)

# ── Gap Assessment update ─────────────────────────────────────────────────────
c = c.replace(
    '**Gap Assessment:**\n- 38 requirements identified (35 original + 3 asset data)\n- Full greenfield build — no prior EKS implementation exists',
    '**Gap Assessment:**\n- 42 requirements identified (35 original + 3 asset data + 1 schema extensibility + 3 asset embedding)\n- Full greenfield build — no prior EKS implementation exists'
)

# ── Index of Content — add Section 10 ────────────────────────────────────────
c = c.replace(
    '- [8. Phase Workplan Index](#8-phase-workplan-index)\n- [9. References](#9-references)',
    '- [8. Phase Workplan Index](#8-phase-workplan-index)\n- [9. References](#9-references)\n- [10. EKS Pipeline Architecture](#10-eks-pipeline-architecture)'
)

# ── Phase table — update R columns ───────────────────────────────────────────
c = c.replace(
    '| 2     | Chunking, Embedding & Vector Storage           | WP-EKS-P2-001 | 🔷 PLANNED | R03,R04,R10,R12–R15,R25,R28,R30 |',
    '| 2     | Chunking, Embedding & Vector Storage           | WP-EKS-P2-001 | 🔷 PLANNED | R03,R04,R10,R12–R15,R25,R28,R30,R40,R41 |'
)
c = c.replace(
    '| 3     | Knowledge Graph & Structured Asset Ingestion   | WP-EKS-P3-001 | 🔷 PLANNED | R05,R11,R23,R27,R31,R37 |',
    '| 3     | Knowledge Graph & Structured Asset Ingestion   | WP-EKS-P3-001 | 🔷 PLANNED | R05,R11,R23,R27,R31,R37,R39(loader),R40(asset embed),R42 |'
)
c = c.replace(
    '| 4     | Retrieval & Scoring Pipeline                   | WP-EKS-P4-001 | 🔷 PLANNED | R16–R20,R24,R38 |',
    '| 4     | Retrieval & Scoring Pipeline                   | WP-EKS-P4-001 | 🔷 PLANNED | R16–R20,R24,R38,R40(retrieval) |'
)

# ── Section 10 — append before ## 9. References ───────────────────────────────
SECTION_10 = '''
---

## 10. EKS Pipeline Architecture

Full end-to-end workflow across all 5 phases. Two parallel ingestion paths (documents and assets) converge at the retrieval stage.

```
╔═════════════════════════════════════════════════════════════════════════════════════╗
║                        EKS — FULL PIPELINE ARCHITECTURE                            ║
╚═════════════════════════════════════════════════════════════════════════════════════╝

 INPUT SOURCES
 ─────────────────────────────────────────────────────────────────────────────────────
  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────────────┐
  │  PDF Files  │  │ DOCX Files  │  │ XLSX Files  │  │   Datadrop Excel             │
  │ (drawings,  │  │ (specs,     │  │ (sheets,    │  │   7 sheets · 7,681 items     │
  │  reports)   │  │  procedures)│  │  registers) │  │   Equipment / Instrument /   │
  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  │   Valve / Pipeline / Motor   │
         └────────────────┴────────────────┘          └──────────────┬───────────────┘
                          │                                           │
               DOCUMENT PATH (Phase 1–2)               ASSET PATH (Phase 1,3)
                          │                                           │
 ════════════════════════════════════════════════════════════════════════════════════
  PHASE 1 — PARSE & REGISTER
 ════════════════════════════════════════════════════════════════════════════════════
                          │                                           │
                          ▼                                           ▼
            ┌─────────────────────────┐             ┌─────────────────────────────┐
            │   Plug-in Parser        │             │   Structured Asset Loader   │
            │   PDFParser             │             │                             │
            │   DOCXParser            │             │ 1. Read sheet + header row  │
            │   XLSXParser            │             │ 2. Apply column norm map    │
            │   DWGParserStub (P3)    │             │ 3. Lookup tag_type in       │
            │   DGNParserStub (P3)    │             │    asset_type_registry      │
            │                         │             │ 4. Evaluate conditional_    │
            │ Output:                 │             │    fragments rules (R39)    │
            │  raw text + structure   │             │ 5. Compose property dict    │
            │  doc-level metadata     │             │ 6. Deduplicate Pipeline     │
            └────────────┬────────────┘             │    KEYTAGs (merge rows)     │
                         │                          └──────────────┬──────────────┘
                         ▼                                         │
            ┌─────────────────────────┐                           │
            │   Document Registry     │                           │
            │   DuckDB                │                           │
            │                         │                           │
            │  doc_number, revision   │                           │
            │  discipline, doc_type   │                           │
            │  is_latest flag         │                           │
            │  file_path              │                           │
            └────────────┬────────────┘                           │
                         │                                        │
 ════════════════════════════════════════════════════════════════════════════════════
  PHASE 2 — CHUNK, EMBED & VECTOR STORAGE (Documents + Asset Records)
 ════════════════════════════════════════════════════════════════════════════════════
                         │                                        │
                         ▼                                        │
            ┌─────────────────────────┐                          │
            │   Chunker               │                          │
            │   section_chunker.py    │                          │
            │   chunker.py            │                          │
            │                         │                          │
            │  PDF/DOCX → section     │                          │
            │  XLSX     → row/table   │                          │
            │  size-based fallback    │                          │
            │                         │                          │
            │  Output per chunk:      │                          │
            │   chunk_id, parent_id   │                          │
            │   text, page, section   │                          │
            └────────────┬────────────┘                          │
                         │                                        │
                         ▼                                        ▼
            ┌─────────────────────────┐          ┌───────────────────────────────┐
            │   Chunk Registry        │          │   Asset Chunk Registry        │
            │   DuckDB                │          │   DuckDB (R41)                │
            │                         │          │                               │
            │  chunk_id → parent_id   │          │  keytag (primary key)         │
            │  doc_number, revision   │          │  tag_type, tag_no             │
            │  page, section          │          │  unit, service                │
            │  source_file            │          │  p_and_id_file                │
            └────────────┬────────────┘          └──────────────┬────────────────┘
                         │                                       │
                         ▼                                       ▼
            ┌─────────────────────────┐          ┌───────────────────────────────┐
            │   Hybrid Embedding      │          │   Asset Text Builder (R40)    │
            │   Strategy              │          │                               │
            │   hybrid_strategy.py    │          │  Build contextual summary:    │
            │                         │          │  "[{tag_type} | Unit {unit}   │
            │  Header prepended:      │          │   | Svc {service}]            │
            │  "[{discipline} |        │          │   {description}:             │
            │   {doc_type} |          │          │   {key property fields}"      │
            │   {doc_no} Rev {rev} |  │          │                               │
            │   p.{page} §{section}]" │          │  Full metadata stored         │
            │                         │          │  in asset chunk registry      │
            │  Full metadata stored   │          │  NOT embedded (R13)           │
            │  in chunk registry      │          └──────────────┬────────────────┘
            │  NOT embedded (R13)     │                         │
            └────────────┬────────────┘                         │
                         │                                       │
                         └─────────────────┬─────────────────────┘
                                           │
                                           ▼
                            ┌──────────────────────────┐
                            │   Embedding Provider     │
                            │   openai_embedder.py     │
                            │   ollama_embedder.py     │
                            │                          │
                            │  Input:  header + text   │
                            │  Output: vector [n-dim]  │
                            │  Batch:  supported       │
                            └──────────┬───────────────┘
                                       │
                         ┌─────────────┴─────────────┐
                         │                           │
                         ▼                           ▼
            ┌────────────────────────┐  ┌────────────────────────────┐
            │  Qdrant: eks_chunks    │  │  Qdrant: eks_assets (R40)  │
            │                        │  │                            │
            │  Payload:              │  │  Payload:                  │
            │  • chunk_id            │  │  • keytag, tag_no          │
            │  • doc_number, rev     │  │  • tag_type                │
            │  • page, section       │  │  • unit, service           │
            │  • project, discipline │  │  • p_and_id_file           │
            │  • source_file         │  │                            │
            │                        │  │  Enables semantic search   │
            │  Doc content search    │  │  over asset properties     │
            └────────────────────────┘  └────────────────────────────┘

 ════════════════════════════════════════════════════════════════════════════════════
  PHASE 3 — KNOWLEDGE GRAPH & ASSET INGESTION
 ════════════════════════════════════════════════════════════════════════════════════

                    Document nodes          Asset nodes (from loader)
                         │                          │
                         ▼                          ▼
            ┌──────────────────────────────────────────────────────────────┐
            │                    Neo4j Graph DB                            │
            │                                                              │
            │  Document nodes:     Asset nodes (14 AT_ types):            │
            │  • Document          • AT_EQPMP, AT_EQUIP, AT_EQTNK …       │
            │  • Revision          • AT_INST_, AT_INST_CS, AT_INST_FLO    │
            │  • Chunk             • AT_MOTOR, AT_CVALVE, AT_HVALVE …     │
            │                      • AT_PROCESS, AT_INCOMP, AT_PSV        │
            │  Relationships:                                              │
            │  REFERENCES          REFERENCED_BY_DWG   (asset → P&ID)    │
            │  SUPERSEDES          BELONGS_TO_UNIT      (asset → unit)    │
            │  CONTAINS            BELONGS_TO_SERVICE   (asset → svc)     │
            │  RELATES_TO          CONNECTS_TO          (pipeline → comp) │
            │                      HAS_ACTUATOR         (valve → act)     │
            └──────────────────────────────────────────────────────────────┘
                         │                          │
                         │    Asset vector upsert   │
                         │    on datadrop reload     │
                         │    (R42) ◄───────────────┘
                         │
 ════════════════════════════════════════════════════════════════════════════════════
  PHASE 4 — RETRIEVAL & SCORING PIPELINE
 ════════════════════════════════════════════════════════════════════════════════════

  User Query (natural language)
         │
         ▼
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │  STAGE 1 — Metadata Filter                                                   │
  │  Document: project, discipline, doc_type, is_latest, revision                │
  │  Asset:    unit, service, tag_type, pipeline_tag (R38)                       │
  └──────────────────────────────┬───────────────────────────────────────────────┘
                                 │
                                 ▼
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │  STAGE 2 — Graph Relationship Expansion                                      │
  │  Doc→Doc:   REFERENCES, SUPERSEDES                                           │
  │  Doc→Asset: REFERENCED_BY_DWG  ←  surface docs linked to matching assets    │
  │  Asset→Asset: CONNECTS_TO, HAS_ACTUATOR  ←  expand pipeline subgraphs       │
  └──────────────────────────────┬───────────────────────────────────────────────┘
                                 │
                     ┌───────────┴───────────┐
                     │                       │
                     ▼                       ▼
  ┌──────────────────────────┐  ┌───────────────────────────────────────────────┐
  │  STAGE 3a                │  │  STAGE 3b                                     │
  │  Hybrid Search           │  │  Asset Query (R38, R40)                       │
  │  (Documents)             │  │                                               │
  │                          │  │  Structured: Neo4j Cypher for exact tag,      │
  │  Vector: eks_chunks      │  │  unit, service, pipeline lookups              │
  │  BM25 keyword            │  │                                               │
  │  Merge + deduplicate     │  │  Semantic: eks_assets vector search for       │
  └──────────────┬───────────┘  │  fuzzy property queries (R40)                │
                 │              └───────────────────────────┬───────────────────┘
                 └──────────────────────┬────────────────────┘
                                        │
                                        ▼
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │  STAGE 4 — Scorer                                                            │
  │  cosine similarity score + keyword score + graph proximity boost             │
  └──────────────────────────────┬───────────────────────────────────────────────┘
                                 │
                                 ▼
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │  STAGE 5 — Reranker                                                          │
  │  Rule-based (default) or cross-encoder (sentence-transformers, optional)     │
  └──────────────────────────────┬───────────────────────────────────────────────┘
                                 │
                                 ▼
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │  STAGE 6 — Context Assembler                                                 │
  │  Select top-k chunks + asset records → fit LLM context window               │
  └──────────────────────────────┬───────────────────────────────────────────────┘
                                 │
                                 ▼
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │  STAGE 7 — LLM Answering                                                     │
  │  OpenAI / Ollama provider (plug-in)                                          │
  │  Response includes source citations:                                         │
  │  doc_number · revision · page · chunk_id · asset keytag                     │
  └──────────────────────────────┬───────────────────────────────────────────────┘
                                 │
 ════════════════════════════════════════════════════════════════════════════════════
  PHASE 5 — UI, CACHE & SYSTEM INTEGRATION
 ════════════════════════════════════════════════════════════════════════════════════
                                 │
                                 ▼
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │  Retrieval Cache (memory / Redis)                                            │
  │  Keyed on query hash + filter hash → skip pipeline on hit                   │
  └──────────────────────────────┬───────────────────────────────────────────────┘
                                 │
                                 ▼
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │  FastAPI Backend                                                             │
  │  /query   → full retrieval pipeline + LLM answer + citations                │
  │  /assets  → asset browse/filter (unit, service, tag_type, pipeline_tag)     │
  │  /ingest  → document upload + parse + chunk + embed trigger                 │
  │  /status  → system health                                                   │
  └──────────────────────────────┬───────────────────────────────────────────────┘
                                 │
                                 ▼
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │  Web UI                                                                      │
  │  • Query input + filter panel (doc + asset dimensions)                      │
  │  • Answer display with source citation cards                                 │
  │  • Asset browsing panel (attributes + linked P&ID documents)                │
  │  • Document ingestion upload                                                 │
  └──────────────────────────────────────────────────────────────────────────────┘
```

**Data store summary:**

| Store | Technology | Contents | Phase |
| :---- | :--------- | :------- | :---: |
| Document Registry | DuckDB | Document metadata, revision flags | 1 |
| Asset Chunk Registry | DuckDB | Asset record metadata (keytag, tag_type, unit, service) | 2 |
| Vector Store — Documents | Qdrant `eks_chunks` | Document chunk vectors + payload | 2 |
| Vector Store — Assets | Qdrant `eks_assets` | Asset contextual summary vectors + payload | 2/3 |
| Knowledge Graph | Neo4j | All nodes (docs, chunks, assets) + all relationships | 3 |
| Retrieval Cache | Memory / Redis | Query result cache keyed on query+filter hash | 5 |

'''

c = c.replace('\n## 9. References', SECTION_10 + '\n## 9. References')

with open('eks/workplan/eks_system_workplan.md', 'w', encoding='utf-8') as f:
    f.write(c)
print("eks_system_workplan.md updated with Section 10 + R40-R42")

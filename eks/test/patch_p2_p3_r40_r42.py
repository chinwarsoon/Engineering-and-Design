def patch(path, replacements):
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    for old, new in replacements:
        assert old in c, f"NOT FOUND in {path}:\n{old[:80]}"
        c = c.replace(old, new, 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    print(f"Patched: {path}")

# ── Phase 2 ───────────────────────────────────────────────────────────────────
patch('eks/workplan/phase_2_chunking_embedding_workplan.md', [
    # version + date
    ('**Current Version**: 0.2  ',
     '**Current Version**: 0.3  '),
    ('**Last Updated**: 2026-06-16  \n**Parent Workplan**',
     '**Last Updated**: 2026-06-18  \n**Parent Workplan**'),
    # revision
    ('| 0.2     | 2026-06-16 | System | Added Timestamp column to task breakdown table per agent_rule Section 8.8. Added CAD/DWG/DGN vector store gap note to Section 11: chunking pipeline has no ingestion path for CAD content; deferred to Phase 3 stubs only. |',
     '| 0.2     | 2026-06-16 | System | Added Timestamp column to task breakdown table per agent_rule Section 8.8. Added CAD/DWG/DGN vector store gap note to Section 11: chunking pipeline has no ingestion path for CAD content; deferred to Phase 3 stubs only. |\n| 0.3     | 2026-06-18 | System | Added R40 (Asset Embedding Strategy) and R41 (Asset Chunk Registry Extension) to scope and task breakdown. Asset text builder and dedicated Qdrant eks_assets collection added. Updated success criteria and deliverables. |'),
    # scope rows
    ('| R30 | Infrastructure       | Vector DB                      | Qdrant for vector storage                                            | 🔷 PLANNED |\n\n**Status Legend:**',
     '| R30 | Infrastructure       | Vector DB                      | Qdrant for vector storage                                            | 🔷 PLANNED |\n| R40 | Embedding            | Asset Embedding Strategy       | Contextual header + key field summary per asset; store vectors in `eks_assets` Qdrant collection; prevent null/code pollution per R13 | 🔷 PLANNED |\n| R41 | Knowledge Base       | Asset Chunk Registry Extension | Extend DuckDB chunk registry to support asset records keyed on `keytag`; metadata: keytag, tag_type, tag_no, unit, service, p_and_id_file | 🔷 PLANNED |\n\n**Status Legend:**'),
    # tasks
    ('| T2.15 | Update logs | `update_log.md`, `issue_log.md` under `eks/log/` | 🔷 | — |',
     '| T2.15 | Update logs | `update_log.md`, `issue_log.md` under `eks/log/` | 🔷 | — |\n| T2.16 | Extend chunk registry for asset records | Add `asset_records` table to DuckDB chunk registry: keytag (PK), tag_type, tag_no, unit, service, p_and_id_file, embedded_at; no parent-child fields needed | 🔷 | — |\n| T2.17 | Implement asset text builder | `asset_text_builder.py`: build contextual text representation per asset — "[{tag_type} \\| Unit {unit} \\| Svc {service}] {description}: {key properties summary}"; select fields by fragment type, skip nulls | 🔷 | — |\n| T2.18 | Add eks_assets Qdrant collection | Configure second Qdrant collection `eks_assets` in `eks_config.json`; same abstract vector store interface (R28); payload: keytag, tag_no, tag_type, unit, service, p_and_id_file | 🔷 | — |\n| T2.19 | Write tests for R40/R41 additions | Asset text builder output, asset chunk registry CRUD, eks_assets collection upsert | 🔷 | — |'),
    # files table
    ('| `eks/config/eks_config.json`                   | Update | Add chunk_size, overlap, embedding_provider, qdrant settings |',
     '| `eks/config/eks_config.json`                   | Update | Add chunk_size, overlap, embedding_provider, qdrant settings, eks_assets collection config |\n| `eks/engine/chunking/asset_text_builder.py`    | Create | Asset contextual text builder for embedding (R40) |\n| `eks/engine/vector_store/asset_store.py`       | Create | Qdrant collection management for eks_assets (R40, R28) |'),
    # success criteria
    ('- [ ] Integration tests passing for: chunk → embed → store pipeline\n- [ ] All unit tests passing for Phase 2 components',
     '- [ ] Integration tests passing for: chunk → embed → store pipeline\n- [ ] Asset text builder produces clean contextual summaries (no nulls, no raw codes)\n- [ ] Asset records stored in DuckDB chunk registry with correct metadata (R41)\n- [ ] Asset vectors stored in `eks_assets` Qdrant collection with keytag payload (R40)\n- [ ] All unit tests passing for Phase 2 components'),
    # deliverables
    ('- Report: `eks/workplan/reports/phase_2_chunking_embedding_report.md`',
     '- Asset embedding modules: `asset_text_builder.py`, `asset_store.py`\n- Report: `eks/workplan/reports/phase_2_chunking_embedding_report.md`'),
])

# ── Phase 3 ───────────────────────────────────────────────────────────────────
patch('eks/workplan/phase_3_knowledge_graph_workplan.md', [
    # version + date
    ('**Current Version**: 0.4  ',
     '**Current Version**: 0.5  '),
    ('**Last Updated**: 2026-06-17  \n**Parent Workplan**',
     '**Last Updated**: 2026-06-18  \n**Parent Workplan**'),
    # revision
    ('| 0.4     | 2026-06-17 | System | Added R39 to scope. Updated T3.9 base asset loader to read conditional_fragments from config and evaluate when/in conditions at runtime — zero code changes needed to add new asset types. Schema loader confirmed no update needed (file-agnostic). |',
     '| 0.4     | 2026-06-17 | System | Added R39 to scope. Updated T3.9 base asset loader to read conditional_fragments from config and evaluate when/in conditions at runtime — zero code changes needed to add new asset types. Schema loader confirmed no update needed (file-agnostic). |\n| 0.5     | 2026-06-18 | System | Added R40 (asset embedding trigger after Neo4j load) and R42 (asset vector upsert on datadrop reload) to scope and tasks. T3.15 sheet orchestrator updated to trigger Phase 2 asset text builder + Qdrant upsert after each node batch. |'),
    # scope rows
    ('| R39 | Schema               | Zero-Code Asset Extensibility  | Base asset loader reads `conditional_fragments` from config at runtime; no code changes needed to add new AT_ types or conditional fragment rules | 🔷 PLANNED |\n\n**Status Legend:**',
     '| R39 | Schema               | Zero-Code Asset Extensibility  | Base asset loader reads `conditional_fragments` from config at runtime; no code changes needed to add new AT_ types or conditional fragment rules | 🔷 PLANNED |\n| R40 | Embedding            | Asset Embedding Trigger        | After loading each asset batch to Neo4j, call asset text builder and upsert vectors into `eks_assets` Qdrant collection | 🔷 PLANNED |\n| R42 | Knowledge Base       | Asset Vector Upsert            | On datadrop reload: upsert Neo4j nodes + invalidate and re-embed corresponding `eks_assets` vectors for changed keytags | 🔷 PLANNED |\n\n**Status Legend:**'),
    # T3.15 updated + T3.20 added
    ('| T3.15 | Implement sheet-to-graph orchestrator | Read all 7 sheets, map each row to its tag_type fragment rules, batch-create nodes + relationships | 🔷 | — |',
     '| T3.15 | Implement sheet-to-graph orchestrator | Read all 7 sheets, map each row to its tag_type fragment rules, batch-create nodes + relationships; after each batch trigger asset text builder + `eks_assets` upsert (R40) | 🔷 | — |\n| T3.20 | Implement asset vector upsert on reload | On datadrop reload: identify changed/new keytags, upsert Neo4j nodes, call asset text builder for changed items, re-upsert `eks_assets` vectors; log stale vectors removed (R42) | 🔷 | — |'),
    # files
    ('| `eks/test/test_phase3.py`                           | Create | Integration tests for Phase 3 components                   |',
     '| `eks/test/test_phase3.py`                           | Create | Integration tests for Phase 3 components                   |\n| `eks/engine/extractors/asset_embed_trigger.py`      | Create | Calls asset text builder + Qdrant upsert after Neo4j batch load (R40, R42) |'),
    # success criteria
    ('- [ ] Zero-code extensibility verified: add a new AT_ type and conditional fragment rule to `eks_asset_config.json` only — confirm loader applies correct fragments without code change',
     '- [ ] Zero-code extensibility verified: add a new AT_ type and conditional fragment rule to `eks_asset_config.json` only — confirm loader applies correct fragments without code change\n- [ ] Asset embeddings upserted to `eks_assets` after each datadrop load batch (R40)\n- [ ] Asset vector upsert on reload: changed keytags re-embedded, stale vectors removed (R42)'),
    # deliverables
    ('- Report: `eks/workplan/reports/phase_3_knowledge_graph_report.md`',
     '- Asset embed trigger: `asset_embed_trigger.py`\n- Report: `eks/workplan/reports/phase_3_knowledge_graph_report.md`'),
])

print("All done")

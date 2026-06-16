def patch(path, replacements):
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    for old, new in replacements:
        assert old in c, f"NOT FOUND in {path}:\n{repr(old[:100])}"
        c = c.replace(old, new, 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    print(f"Patched: {path}")

# ── Phase 4 ───────────────────────────────────────────────────────────────────
patch('eks/workplan/phase_4_retrieval_pipeline_workplan.md', [
    ('**Current Version**: 0.2  ',
     '**Current Version**: 0.4  '),
    ('**Last Updated**: 2026-06-15  \n**Parent Workplan**',
     '**Last Updated**: 2026-06-18  \n**Parent Workplan**'),
    ('| 0.2     | 2026-06-15 | System | Added asset-aware metadata filtering (unit, service, tag_type) and asset relationship expansion (CONNECTS_TO pipeline-to-component, REFERENCED_BY_DWG P&ID links). Updated scope, tasks, success criteria for R38 |',
     '| 0.2     | 2026-06-15 | System | Added asset-aware metadata filtering (unit, service, tag_type) and asset relationship expansion (CONNECTS_TO pipeline-to-component, REFERENCED_BY_DWG P&ID links). Updated scope, tasks, success criteria for R38 |\n| 0.3     | 2026-06-16 | System | Added T4.18: asset query handler in pipeline.py to explicitly scope the asset query path required by Phase 5 /assets endpoint. Added reranker model guidance note to T4.8. Added Timestamp column to task breakdown table per agent_rule Section 8.8. |\n| 0.4     | 2026-06-18 | System | Added R40 to retrieval scope: Phase 4 vector search now queries both eks_chunks (documents) and eks_assets (asset semantic search) collections. T4.4 updated to search both collections. Added T4.19 for dual-collection merge logic. |'),
    # scope
    ('| R38 | Retrieval Pipeline | Asset-Aware Retrieval            | Filter and expand context by asset attributes and asset-to-document graph relationships | 🔷 PLANNED |\n\n**Status Legend:**',
     '| R38 | Retrieval Pipeline | Asset-Aware Retrieval            | Filter and expand context by asset attributes and asset-to-document graph relationships | 🔷 PLANNED |\n| R40 | Retrieval Pipeline | Asset Semantic Search            | Query `eks_assets` Qdrant collection for fuzzy/semantic asset property queries; merge with structured Neo4j asset query results before scoring | 🔷 PLANNED |\n\n**Status Legend:**'),
    # T4.4 updated + T4.19 added
    ('| T4.4 | Implement vector search | Similarity search via Qdrant using query embedding | 🔷 | — |',
     '| T4.4 | Implement vector search | Similarity search via Qdrant using query embedding — query `eks_chunks` for document content and `eks_assets` for asset semantic search (R40); collection selected by query context | 🔷 | — |\n| T4.19 | Implement dual-collection search merger | Merge results from `eks_chunks` and `eks_assets` Qdrant searches; normalise scores across collection types before passing to scorer | 🔷 | — |'),
    # success criteria
    ('- [ ] Asset query handler (`query_assets`) in `pipeline.py` operational for Phase 5 `/assets` endpoint',
     '- [ ] Asset query handler (`query_assets`) in `pipeline.py` operational for Phase 5 `/assets` endpoint\n- [ ] `eks_assets` Qdrant collection queried for semantic asset property searches (R40)\n- [ ] Dual-collection search results merged and scored consistently'),
    # phase 4 requirements cell in phase index (in this file's reference section)
    ('4. [phase_3_knowledge_graph_workplan.md](phase_3_knowledge_graph_workplan.md) — Phase 3 prerequisite',
     '4. [phase_3_knowledge_graph_workplan.md](phase_3_knowledge_graph_workplan.md) — Phase 3 prerequisite'),
])

# ── update_log ────────────────────────────────────────────────────────────────
patch('eks/log/update_log.md', [
    ('| U021 | 2026-06-18 | Phase 1 | — | Updated `phase_1_foundation_workplan.md` v0.9 to COMPLETE. Marked T1.20 ✅, all scope R-items ✅, all success criteria ✅. Updated `eks_system_workplan.md` v0.6: Phase 1 status back to PASS. Updated `phase_1_foundation_report.md` v0.2. | System | ✅ Done |',
     '| U021 | 2026-06-18 | Phase 1 | — | Updated `phase_1_foundation_workplan.md` v0.9 to COMPLETE. Marked T1.20 ✅, all scope R-items ✅, all success criteria ✅. Updated `eks_system_workplan.md` v0.6: Phase 1 status back to PASS. Updated `phase_1_foundation_report.md` v0.2. | System | ✅ Done |\n| U022 | 2026-06-18 | Planning | — | Added R40 (Asset Embedding Strategy), R41 (Asset Chunk Registry Extension), R42 (Asset Vector Upsert) to `eks_system_workplan.md` v0.7. Added Section 10: EKS Pipeline Architecture workflow diagram. Updated Phase 2, 3, 4 workplans with new tasks (T2.16–T2.19, T3.20, T4.19) and success criteria. | System | ✅ Done |'),
])

print("All done")

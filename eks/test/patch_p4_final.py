def patch(path, replacements):
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    for old, new in replacements:
        if old not in c:
            print(f"  SKIP (not found): {repr(old[:80])}")
            continue
        c = c.replace(old, new, 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    print(f"Patched: {path}")

patch('eks/workplan/phase_4_retrieval_pipeline_workplan.md', [
    ('**Current Version**: 0.2  ',
     '**Current Version**: 0.4  '),
    ('**Last Updated**: 2026-06-15  \r\n**Parent Workplan**',
     '**Last Updated**: 2026-06-18  \r\n**Parent Workplan**'),
    # revision entries — find end of existing 0.2 row and append
    ('| 0.2     | 2026-06-15 | System | Added asset-aware metadata filtering (unit, service, tag_type) and asset relationship expansion (CONNECTS_TO pipeline-to-component, REFERENCED_BY_DWG P&ID links). Updated scope, tasks, success criteria for R38 |',
     '| 0.2     | 2026-06-15 | System | Added asset-aware metadata filtering (unit, service, tag_type) and asset relationship expansion (CONNECTS_TO pipeline-to-component, REFERENCED_BY_DWG P&ID links). Updated scope, tasks, success criteria for R38 |\r\n| 0.3     | 2026-06-16 | System | Added T4.18 asset query handler, reranker model guidance, Timestamp column in task table. |\r\n| 0.4     | 2026-06-18 | System | Added R40 to scope: dual-collection vector search (eks_chunks + eks_assets). Added T4.19 dual-collection merger. Updated success criteria. |'),
    # scope row after R38
    ('| R38 | Retrieval Pipeline | Asset-Aware Retrieval            | Filter and expand context by asset attributes and asset-to-document graph relationships | 🔷 PLANNED |\r\n\r\n**Status Legend:**',
     '| R38 | Retrieval Pipeline | Asset-Aware Retrieval            | Filter and expand context by asset attributes and asset-to-document graph relationships | 🔷 PLANNED |\r\n| R40 | Retrieval Pipeline | Asset Semantic Search            | Query `eks_assets` Qdrant collection for fuzzy/semantic asset property queries; merge with Neo4j structured results before scoring | 🔷 PLANNED |\r\n\r\n**Status Legend:**'),
    # T4.4 task row (no timestamp column in original)
    ('| T4.4 | Implement vector search | Similarity search via Qdrant using query embedding | 🔷 |',
     '| T4.4 | Implement vector search | Similarity search via Qdrant using query embedding — query `eks_chunks` (documents) and `eks_assets` (asset semantic search, R40); collection selected by query context | 🔷 |'),
    # T4.19 inserted after T4.18
    ('| T4.18 | Implement asset query handler in pipeline | Add `query_assets(filters)` method to `pipeline.py`: accepts unit, service, tag_type, pipeline_tag filters → queries Neo4j asset nodes + returns asset attributes and linked document references. Required by Phase 5 `/assets` endpoint. | 🔷 | — |',
     '| T4.18 | Implement asset query handler in pipeline | Add `query_assets(filters)` method to `pipeline.py`: accepts unit, service, tag_type, pipeline_tag filters → queries Neo4j asset nodes + returns asset attributes and linked document references. Required by Phase 5 `/assets` endpoint. | 🔷 | — |\r\n| T4.19 | Implement dual-collection search merger | Merge and normalise scores from `eks_chunks` and `eks_assets` Qdrant queries; tag each result with `source_type` (document / asset) before passing to scorer | 🔷 | — |'),
    # success criteria
    ('- [ ] Asset query handler (`query_assets`) in `pipeline.py` operational for Phase 5 `/assets` endpoint',
     '- [ ] Asset query handler (`query_assets`) in `pipeline.py` operational for Phase 5 `/assets` endpoint\r\n- [ ] `eks_assets` Qdrant collection queried for semantic asset property searches (R40)\r\n- [ ] Dual-collection search results merged and scored consistently'),
])

patch('eks/log/update_log.md', [
    ('| U021 | 2026-06-18 | Phase 1 | — | Updated `phase_1_foundation_workplan.md` v0.9 to COMPLETE. Marked T1.20 ✅, all scope R-items ✅, all success criteria ✅. Updated `eks_system_workplan.md` v0.6: Phase 1 status back to PASS. Updated `phase_1_foundation_report.md` v0.2. | System | ✅ Done |',
     '| U021 | 2026-06-18 | Phase 1 | — | Updated `phase_1_foundation_workplan.md` v0.9 to COMPLETE. Marked T1.20 ✅, all scope R-items ✅, all success criteria ✅. Updated `eks_system_workplan.md` v0.6: Phase 1 status back to PASS. Updated `phase_1_foundation_report.md` v0.2. | System | ✅ Done |\n| U022 | 2026-06-18 | Planning | — | Added R40 (Asset Embedding Strategy), R41 (Asset Chunk Registry Extension), R42 (Asset Vector Upsert) to `eks_system_workplan.md` v0.7. Added Section 10: EKS Pipeline Architecture workflow diagram. Updated Phase 2 v0.3 (T2.16–T2.19), Phase 3 v0.5 (T3.20), Phase 4 v0.4 (T4.19) workplans with new tasks and success criteria. | System | ✅ Done |'),
])

print("All done")

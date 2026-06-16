import re

# ── Phase 1 ───────────────────────────────────────────────────────────────────
with open('eks/workplan/phase_1_foundation_workplan.md', 'r', encoding='utf-8') as f:
    c = f.read()

# version bump + revision entry
c = c.replace(
    '**Current Version**: 0.6  ',
    '**Current Version**: 0.7  '
)
c = c.replace(
    '**Last Updated**: 2026-06-15  \n**Parent Workplan**',
    '**Last Updated**: 2026-06-16  \n**Parent Workplan**'
)
c = c.replace(
    '| 0.6     | 2026-06-15 | opencode | Created and validated actual schema files: `eks_asset_base_schema.json` (11 fragment $defs), `eks_asset_setup_schema.json` (registry + normalization declarations), `eks_asset_config.json` (14 AT_ mappings + 7-sheet column map). Appendix A extracted to stand-alone file. Fixed "10 fragments"\u2192"11 fragments" in 4 locations. |',
    '| 0.6     | 2026-06-15 | opencode | Created and validated actual schema files: `eks_asset_base_schema.json` (11 fragment $defs), `eks_asset_setup_schema.json` (registry + normalization declarations), `eks_asset_config.json` (14 AT_ mappings + 7-sheet column map). Appendix A extracted to stand-alone file. Fixed "10 fragments"\u2192"11 fragments" in 4 locations. |\n| 0.7     | 2026-06-16 | System | Gap analysis against actual datadrop Excel. Added 2 new fragments: `specialist_equipment` (A2.12) and `motor_control` (A2.13). Expanded `actuator` fragment with full actuator manufacturer+lifecycle block. Fragment count: 11 \u2192 13. Updated T1.17, success criteria, and deliverables accordingly. |'
)

# T1.17 task row
c = c.replace(
    'T1.17 | Design asset schema \u2014 fragment definitions | Add 11 reusable asset fragments to `eks_base_schema.json` (item_core, process_conditions, manufacturer, asset_lifecycle, control_system, piping_connection, valve_internals, actuator, rotating_equipment, instrumentation, pipeline_route) | \u2705 |',
    'T1.17 | Design asset schema \u2014 fragment definitions | Add 13 reusable asset fragments to `eks_asset_base_schema.json` (item_core, process_conditions, manufacturer, asset_lifecycle, control_system, piping_connection, valve_internals, actuator, rotating_equipment, instrumentation, pipeline_route, specialist_equipment, motor_control) | \u2705 |'
)

# success criteria
c = c.replace(
    '- [x] Universal plant item schema designed: 11 fragments in `eks_asset_base_schema.json` covering all 7 datadrop categories',
    '- [x] Universal plant item schema designed: 13 fragments in `eks_asset_base_schema.json` covering all 7 datadrop categories (added `specialist_equipment` A2.12 and `motor_control` A2.13 per gap analysis against actual datadrop)'
)

with open('eks/workplan/phase_1_foundation_workplan.md', 'w', encoding='utf-8') as f:
    f.write(c)
print("phase_1 patched")

# ── Phase 3 ───────────────────────────────────────────────────────────────────
with open('eks/workplan/phase_3_knowledge_graph_workplan.md', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace(
    '- **Phase 1 asset schema**: 11 reusable fragments define all asset properties; the `asset_type_registry` maps each AT_ tag_type to its fragment composition',
    '- **Phase 1 asset schema**: 13 fragments define all asset properties; the `asset_type_registry` maps each AT_ tag_type to its fragment composition (includes `specialist_equipment` A2.12 for UV/filtration/conveyor and `motor_control` A2.13 for motor electrical fields)'
)

# Also add pipeline deduplication note to T3.13
c = c.replace(
    '| T3.13 | Implement Pipeline loader | Load Pipeline sheet rows into AT_PROCESS nodes with pipeline_route fragment; create CONNECTS_TO edges from FROM/TO_COMPONENT | \ud83d\udd37 | \u2014 |',
    '| T3.13 | Implement Pipeline loader | Load Pipeline sheet rows into AT_PROCESS nodes with pipeline_route fragment; deduplicate 612 multi-row KEYTAGs by merging non-null fields and collecting all DOC_FNAME values; create CONNECTS_TO edges from FROM/TO_COMPONENT when populated | \ud83d\udd37 | \u2014 |'
)

# Add pipeline dedup risk to risks table
c = c.replace(
    '| Pipeline-to-component CONNECTS_TO edges may be incomplete | Medium | Medium | Log missing FROM/TO_COMPONENT; support incremental updates |',
    '| Pipeline-to-component CONNECTS_TO edges may be incomplete | Medium | Medium | Log missing FROM/TO_COMPONENT; support incremental updates |\n| Pipeline sheet has 612 duplicate KEYTAG rows (same tag on multiple P&ID sheets) | High | Medium | Deduplicate on load: merge rows by keytag, collect all DOC_FNAME as list for REFERENCED_BY_DWG edges |'
)

with open('eks/workplan/phase_3_knowledge_graph_workplan.md', 'w', encoding='utf-8') as f:
    f.write(c)
print("phase_3 patched")
print("All done")

with open('eks/workplan/eks_system_workplan.md', 'r', encoding='utf-8') as f:
    c = f.read()

# version bump
c = c.replace('**Current Version**: 0.4  ', '**Current Version**: 0.5  ')
c = c.replace('**Last Updated**: 2026-06-16  \n\n---\n\n## 1.', '**Last Updated**: 2026-06-17  \n\n---\n\n## 1.')

# revision entry
c = c.replace(
    '| 0.4     | 2026-06-16 | System | Fixed R36 status: corrected from 🔷 PLANNED to ✅ PASS (delivered in Phase 1 v0.6). Fixed fragment count in Section 6: corrected "10 reusable fragments" to "13 fragments" per gap analysis against actual datadrop (added specialist_equipment A2.12 and motor_control A2.13). |',
    '| 0.4     | 2026-06-16 | System | Fixed R36 status: corrected from 🔷 PLANNED to ✅ PASS (delivered in Phase 1 v0.6). Fixed fragment count in Section 6: corrected "10 reusable fragments" to "13 fragments" per gap analysis against actual datadrop (added specialist_equipment A2.12 and motor_control A2.13). |\n| 0.5     | 2026-06-17 | System | Added R39: Zero-code asset extensibility — conditional_fragments structure in schema enables adding new plant asset types/sub-types without code changes. Assigned to Phase 1 (schema) and Phase 3 (loader). |'
)

# R39 row after R38
c = c.replace(
    '| R38 | Retrieval Pipeline   | Asset-Aware Retrieval                    | Filter and expand context by asset attributes (unit, service, tag_type, pipeline) and asset-to-document relationships | 🔷 PLANNED | 4     |\n\n**Status Legend:**',
    '| R38 | Retrieval Pipeline   | Asset-Aware Retrieval                    | Filter and expand context by asset attributes (unit, service, tag_type, pipeline) and asset-to-document relationships | 🔷 PLANNED | 4     |\n| R39 | Schema               | Zero-Code Asset Extensibility            | `conditional_fragments` structure in `eks_asset_setup_schema.json` and `eks_asset_config.json` enables adding new AT_ tag types and conditional fragment rules without any code changes — config-only update | 🔷 PLANNED | 1,3   |\n\n**Status Legend:**'
)

# Phase 1 requirements cell — add R39
c = c.replace(
    '| 1     | Foundation — Project Structure, Schema & Registry | WP-EKS-P1-001 | ✅ PASS    | R01,R02,R06–R09,R21,R22,R26,R29,R33–R35,R36 |',
    '| 1     | Foundation — Project Structure, Schema & Registry | WP-EKS-P1-001 | 🔶 PARTIAL | R01,R02,R06–R09,R21,R22,R26,R29,R33–R35,R36,R39(schema) |'
)

with open('eks/workplan/eks_system_workplan.md', 'w', encoding='utf-8') as f:
    f.write(c)
print("eks_system_workplan.md patched")

# ── Phase 1 ───────────────────────────────────────────────────────────────────
with open('eks/workplan/phase_1_foundation_workplan.md', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('**Current Version**: 0.7  ', '**Current Version**: 0.8  ')
c = c.replace(
    '**Last Updated**: 2026-06-16  \n**Parent Workplan**: [eks_system_workplan.md]',
    '**Last Updated**: 2026-06-17  \n**Parent Workplan**: [eks_system_workplan.md]'
)
c = c.replace('**Status**: ✅ COMPLETE  ', '**Status**: 🔶 PARTIAL — R39 schema updates pending  ')

# revision entry
c = c.replace(
    '| 0.7     | 2026-06-16 | System | Gap analysis against actual datadrop Excel. Added 2 new fragments: `specialist_equipment` (A2.12) and `motor_control` (A2.13). Expanded `actuator` fragment with full actuator manufacturer+lifecycle block. Fragment count: 11 → 13. Updated T1.17, success criteria, and deliverables accordingly. |',
    '| 0.7     | 2026-06-16 | System | Gap analysis against actual datadrop Excel. Added 2 new fragments: `specialist_equipment` (A2.12) and `motor_control` (A2.13). Expanded `actuator` fragment with full actuator manufacturer+lifecycle block. Fragment count: 11 → 13. Updated T1.17, success criteria, and deliverables accordingly. |\n| 0.8     | 2026-06-17 | System | Added R39: zero-code asset extensibility. Added T1.20: update 3 asset schema files with gap analysis findings (13 fragments, expanded fields, conditional_fragments structure). Phase 1 status set to PARTIAL pending T1.20 completion. |'
)

# R39 scope row after R36
c = c.replace(
    '| R36 | Schema               | Universal Plant Item Schema              | Fragment-based asset schema covering Equipment, Inline Component, Instrument, Motor, Pipeline, Control Valve, Manual Valve | 🔷 PLANNED |\n\n**Status Legend:**',
    '| R36 | Schema               | Universal Plant Item Schema              | Fragment-based asset schema covering Equipment, Inline Component, Instrument, Motor, Pipeline, Control Valve, Manual Valve | 🔷 PLANNED |\n| R39 | Schema               | Zero-Code Asset Extensibility            | `conditional_fragments` in setup schema + config enables new AT_ types and conditional fragment rules with config-only changes; no code modification required | 🔷 PLANNED |\n\n**Status Legend:**'
)

# T1.20 task after T1.19
c = c.replace(
    '| T1.19 | Update config with asset source | Add project asset datadrop path and per-project config to `eks_config.json` | ✅ |',
    '| T1.19 | Update config with asset source | Add project asset datadrop path and per-project config to `eks_config.json` | ✅ |\n| T1.20 | Update asset schema files for R39 + gap analysis | (1) `eks_asset_base_schema.json`: add `specialist_equipment` and `motor_control` fragment `$defs`; expand `actuator`, `rotating_equipment`, `instrumentation`, `valve_internals` with gap analysis fields. (2) `eks_asset_setup_schema.json`: update fragment enum to 13 names; add `conditional_fragments` object structure to registry. (3) `eks_asset_config.json`: add `conditional_fragments` entries for AT_EQUIP and AT_MOTOR; add missing column normalization entries (manufacturer_fax, valve_internal_type, dual alarm TP columns) | 🔷 |'
)

# success criteria
c = c.replace(
    '- [x] Asset type registry mapped: all 14 AT_ categories composed from fragments in `eks_asset_config.json`',
    '- [x] Asset type registry mapped: all 14 AT_ categories composed from fragments in `eks_asset_config.json`\n- [ ] Zero-code extensibility: `conditional_fragments` structure declared in `eks_asset_setup_schema.json`; AT_EQUIP and AT_MOTOR entries include conditional fragment rules in `eks_asset_config.json`\n- [ ] All 13 fragment `$defs` present and correct in `eks_asset_base_schema.json` (includes gap analysis additions)'
)

# deliverables
c = c.replace(
    '- Asset schema files: `eks_asset_base_schema.json`, `eks_asset_setup_schema.json`, `eks_asset_config.json`',
    '- Asset schema files: `eks_asset_base_schema.json` (13 fragments), `eks_asset_setup_schema.json` (conditional_fragments structure), `eks_asset_config.json` (conditional rules + full column normalization)'
)

with open('eks/workplan/phase_1_foundation_workplan.md', 'w', encoding='utf-8') as f:
    f.write(c)
print("phase_1_foundation_workplan.md patched")

# ── Phase 3 ───────────────────────────────────────────────────────────────────
with open('eks/workplan/phase_3_knowledge_graph_workplan.md', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('**Current Version**: 0.3  ', '**Current Version**: 0.4  ')
c = c.replace(
    '**Last Updated**: 2026-06-16  \n**Parent Workplan**: [eks_system_workplan.md]',
    '**Last Updated**: 2026-06-17  \n**Parent Workplan**: [eks_system_workplan.md]'
)

# revision entry
c = c.replace(
    '| 0.3     | 2026-06-16 | System | Fixed fragment count in Section 6: corrected "10 reusable fragments" to "11 reusable fragments" to align with Phase 1 v0.6 delivery. Added Timestamp column to task breakdown table per agent_rule Section 8.8. |',
    '| 0.3     | 2026-06-16 | System | Fixed fragment count in Section 6: corrected "10 reusable fragments" to "11 reusable fragments" to align with Phase 1 v0.6 delivery. Added Timestamp column to task breakdown table per agent_rule Section 8.8. |\n| 0.4     | 2026-06-17 | System | Added R39 to scope. Updated T3.9 base asset loader to read conditional_fragments from config and evaluate when/in conditions at runtime — zero code changes needed to add new asset types. Schema loader confirmed no update needed (file-agnostic). |'
)

# R39 in scope table
c = c.replace(
    '| R37 | Knowledge Base       | Structured Asset Ingestion     | Load and index project asset data from Excel datadrop into knowledge graph       | 🔷 PLANNED |\n\n**Status Legend:**',
    '| R37 | Knowledge Base       | Structured Asset Ingestion     | Load and index project asset data from Excel datadrop into knowledge graph       | 🔷 PLANNED |\n| R39 | Schema               | Zero-Code Asset Extensibility  | Base asset loader reads `conditional_fragments` from config at runtime; no code changes needed to add new AT_ types or conditional fragment rules | 🔷 PLANNED |\n\n**Status Legend:**'
)

# T3.9 update
c = c.replace(
    '| T3.9 | Implement structured asset loader interface | `base_asset_loader.py`: load(sheet_data, tag_type) → create Neo4j node with fragment-composed properties | 🔷 | — |',
    '| T3.9 | Implement structured asset loader interface | `base_asset_loader.py`: load(sheet_data, tag_type) → (1) read `fragments` list from `asset_type_registry[tag_type]`; (2) read `conditional_fragments` list and evaluate each `when`/`in` condition against the row\'s field value; (3) merge all applicable fragment properties; (4) create Neo4j node. Adding a new AT_ type or conditional rule requires only a config update — zero code changes. | 🔷 | — |'
)

# success criteria
c = c.replace(
    '- [ ] Structured asset loaders operational for all 14 AT_ tag_types',
    '- [ ] Structured asset loaders operational for all 14 AT_ tag_types\n- [ ] Zero-code extensibility verified: add a new AT_ type and conditional fragment rule to `eks_asset_config.json` only — confirm loader applies correct fragments without code change'
)

with open('eks/workplan/phase_3_knowledge_graph_workplan.md', 'w', encoding='utf-8') as f:
    f.write(c)
print("phase_3_knowledge_graph_workplan.md patched")
print("All workplans done")

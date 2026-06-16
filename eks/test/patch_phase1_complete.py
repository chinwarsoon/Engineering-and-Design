with open('eks/workplan/phase_1_foundation_workplan.md', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Version + status
c = c.replace('**Current Version**: 0.8  ', '**Current Version**: 0.9  ')
c = c.replace('**Status**: 🔶 PARTIAL — R39 schema updates pending  ', '**Status**: ✅ COMPLETE  ')
c = c.replace('**Last Updated**: 2026-06-17  \n**Parent Workplan**: [eks_system_workplan.md]',
              '**Last Updated**: 2026-06-18  \n**Parent Workplan**: [eks_system_workplan.md]')

# 2. Revision entry
c = c.replace(
    '| 0.8     | 2026-06-17 | System | Added R39: zero-code asset extensibility. Added T1.20: update 3 asset schema files with gap analysis findings (13 fragments, expanded fields, conditional_fragments structure). Phase 1 status set to PARTIAL pending T1.20 completion. |',
    '| 0.8     | 2026-06-17 | System | Added R39: zero-code asset extensibility. Added T1.20: update 3 asset schema files with gap analysis findings (13 fragments, expanded fields, conditional_fragments structure). Phase 1 status set to PARTIAL pending T1.20 completion. |\n| 0.9     | 2026-06-18 | System | T1.20 complete: all 3 asset schema files updated and validated. Added asset schema + R39 test cases to test_phase1.py. Updated update_log.md (U017-U021) and issue_log.md (I004 resolved, I005 added). Updated phase_1_foundation_report.md to v0.2. Marked eks_config.json placeholder data. Phase status set to COMPLETE. |'
)

# 3. T1.20 status ✅
c = c.replace(
    '| T1.20 | Update asset schema files for R39 + gap analysis | (1) `eks_asset_base_schema.json`: add `specialist_equipment` and `motor_control` fragment `$defs`; expand `actuator`, `rotating_equipment`, `instrumentation`, `valve_internals` with gap analysis fields. (2) `eks_asset_setup_schema.json`: update fragment enum to 13 names; add `conditional_fragments` object structure to registry. (3) `eks_asset_config.json`: add `conditional_fragments` entries for AT_EQUIP and AT_MOTOR; add missing column normalization entries (manufacturer_fax, valve_internal_type, dual alarm TP columns) | 🔷 |',
    '| T1.20 | Update asset schema files for R39 + gap analysis | (1) `eks_asset_base_schema.json`: add `specialist_equipment` and `motor_control` fragment `$defs`; expand `actuator`, `rotating_equipment`, `instrumentation`, `valve_internals` with gap analysis fields. (2) `eks_asset_setup_schema.json`: update fragment enum to 13 names; add `conditional_fragments` object structure to registry. (3) `eks_asset_config.json`: add `conditional_fragments` entries for AT_EQUIP and AT_MOTOR; add missing column normalization entries (manufacturer_fax, valve_internal_type, dual alarm TP columns) | ✅ |'
)

# 4. Scope table — update all R statuses from PLANNED to PASS
for r in ['R01','R02','R06','R07','R08','R09','R21','R22','R26','R29','R33','R34','R35']:
    c = c.replace(f'| {r} |', f'| {r} |', 1)  # placeholder — do below
import re
c = re.sub(r'(\| R(?:01|02|06|07|08|09|21|22|26|29|33|34|35) \|.*?\| )🔷 PLANNED( \|)', r'\1✅ PASS\2', c)
c = c.replace('| R36 | Schema               | Universal Plant Item Schema              | Fragment-based asset schema covering Equipment, Inline Component, Instrument, Motor, Pipeline, Control Valve, Manual Valve | 🔷 PLANNED |',
              '| R36 | Schema               | Universal Plant Item Schema              | Fragment-based asset schema covering Equipment, Inline Component, Instrument, Motor, Pipeline, Control Valve, Manual Valve | ✅ PASS    |')
c = c.replace('| R39 | Schema               | Zero-Code Asset Extensibility            | `conditional_fragments` in setup schema + config enables new AT_ types and conditional fragment rules with config-only changes; no code modification required | 🔷 PLANNED |',
              '| R39 | Schema               | Zero-Code Asset Extensibility            | `conditional_fragments` in setup schema + config enables new AT_ types and conditional fragment rules with config-only changes; no code modification required | ✅ PASS    |')

# 5. Success criteria — tick remaining open items
c = c.replace(
    '- [ ] Zero-code extensibility: `conditional_fragments` structure declared in `eks_asset_setup_schema.json`; AT_EQUIP and AT_MOTOR entries include conditional fragment rules in `eks_asset_config.json`',
    '- [x] Zero-code extensibility: `conditional_fragments` structure declared in `eks_asset_setup_schema.json`; AT_EQUIP and AT_MOTOR entries include conditional fragment rules in `eks_asset_config.json`'
)
c = c.replace(
    '- [ ] All 13 fragment `$defs` present and correct in `eks_asset_base_schema.json` (includes gap analysis additions)',
    '- [x] All 13 fragment `$defs` present and correct in `eks_asset_base_schema.json` (includes gap analysis additions)'
)

# 6. Files table — fix fragment count note
c = c.replace(
    '| `eks/config/eks_asset_base_schema.json` | Create | Universal plant item schema — 10 reusable fragment definitions |',
    '| `eks/config/eks_asset_base_schema.json` | Create | Universal plant item schema — 13 fragment definitions (gap analysis additions included) |'
)

# 7. Section 7c — update fragment count text
c = c.replace(
    '        - **Asset Schema Fragments (R36)** — 11 fragments for universal plant item schema (see [appendix_a_asset_schema.md](appendix_a_asset_schema.md)):\n        - `item_core_def`: Universal identity fields for all plant items (keytag, tag_type, tag_no, project, unit, service).\n        - `process_conditions_def`: Design/operating pressure, temperature, flow rates, test pressure.\n        - `manufacturer_def`: Brand, model, serial, manufacturer contact and location.\n        - `asset_lifecycle_def`: ACE category, replacement cost, warranty terms, commission dates.\n        - `control_system_def`: LCS type, PLC/RIO panel references and locations.\n        - `piping_connection_def`: Pipe size, pipeline tag, lining material, end condition.\n        - `valve_internals_def`: Body/stem/seat material, closure element, valve duty.\n        - `actuator_def`: Electric actuator specs and sub-manufacturer info (for control valves).\n        - `rotating_equipment_def`: RPM, efficiency, impeller, NPSH, nozzle sizes (pumps, motors).\n        - `instrumentation_def`: Sensor specs, output signal, alarm limits, calibration range.\n        - `pipeline_route_def`: Pipe material, OD/wall thickness, insulation, from/to component connections.',
    '        - **Asset Schema Fragments (R36, R39)** — 13 fragments for universal plant item schema (see [appendix_a_asset_schema.md](appendix_a_asset_schema.md)):\n        - `item_core_def`, `process_conditions_def`, `manufacturer_def`, `asset_lifecycle_def`, `control_system_def`, `piping_connection_def`, `valve_internals_def`, `actuator_def` (full manufacturer+lifecycle block), `rotating_equipment_def`, `instrumentation_def`, `pipeline_route_def`, `specialist_equipment_def` (UV/filtration/conveyor), `motor_control_def` (starter type, MCC feed). `conditional_fragments` structure added for zero-code extensibility (R39).'
)

with open('eks/workplan/phase_1_foundation_workplan.md', 'w', encoding='utf-8') as f:
    f.write(c)
print("phase_1_foundation_workplan.md patched")

# ── Master workplan — Phase 1 status back to PASS ─────────────────────────────
with open('eks/workplan/eks_system_workplan.md', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace(
    '| 1     | Foundation — Project Structure, Schema & Registry | WP-EKS-P1-001 | 🔶 PARTIAL | R01,R02,R06–R09,R21,R22,R26,R29,R33–R35,R36,R39(schema) |',
    '| 1     | Foundation — Project Structure, Schema & Registry | WP-EKS-P1-001 | ✅ PASS    | R01,R02,R06–R09,R21,R22,R26,R29,R33–R35,R36,R39(schema) |'
)
c = c.replace('**Current Version**: 0.5  ', '**Current Version**: 0.6  ')
c = c.replace('**Last Updated**: 2026-06-17  \n\n---\n\n## 1.', '**Last Updated**: 2026-06-18  \n\n---\n\n## 1.')
c = c.replace(
    '| 0.5     | 2026-06-17 | System | Added R39: Zero-code asset extensibility',
    '| 0.5     | 2026-06-17 | System | Added R39: Zero-code asset extensibility'
)
# add 0.6 revision entry
c = c.replace(
    '| 0.5     | 2026-06-17 | System | Added R39: Zero-code asset extensibility — conditional_fragments structure in schema enables adding new plant asset types/sub-types without code changes. Assigned to Phase 1 (schema) and Phase 3 (loader). |',
    '| 0.5     | 2026-06-17 | System | Added R39: Zero-code asset extensibility — conditional_fragments structure in schema enables adding new plant asset types/sub-types without code changes. Assigned to Phase 1 (schema) and Phase 3 (loader). |\n| 0.6     | 2026-06-18 | System | Phase 1 marked PASS: T1.20 complete, all success criteria met, test_phase1.py updated, logs and report updated. R36 and R39 status updated to PASS in master scope table. |'
)
# R36 and R39 scope table
c = c.replace(
    '| R36 | Schema               | Universal Plant Item Schema              | Fragment-based asset schema covering Equipment, Inline Component, Instrument, Motor, Pipeline, Control Valve, Manual Valve | ✅ PASS    | 1     |',
    '| R36 | Schema               | Universal Plant Item Schema              | Fragment-based asset schema covering Equipment, Inline Component, Instrument, Motor, Pipeline, Control Valve, Manual Valve | ✅ PASS    | 1     |'
)
c = c.replace(
    '| R39 | Schema               | Zero-Code Asset Extensibility            | `conditional_fragments` structure in `eks_asset_setup_schema.json` and `eks_asset_config.json` enables adding new AT_ tag types and conditional fragment rules without any code changes — config-only update | 🔷 PLANNED | 1,3   |',
    '| R39 | Schema               | Zero-Code Asset Extensibility            | `conditional_fragments` structure in `eks_asset_setup_schema.json` and `eks_asset_config.json` enables adding new AT_ tag types and conditional fragment rules without any code changes — config-only update | 🔶 PARTIAL | 1,3   |'
)
with open('eks/workplan/eks_system_workplan.md', 'w', encoding='utf-8') as f:
    f.write(c)
print("eks_system_workplan.md patched")
print("Workplan patches done")

with open('eks/workplan/reports/phase_1_foundation_report.md', 'r', encoding='utf-8') as f:
    c = f.read()

# Version + date
c = c.replace('**Current Version**: 0.1  ', '**Current Version**: 0.2  ')
c = c.replace('**Last Updated**: 2026-06-15  ', '**Last Updated**: 2026-06-18  ')

# Revision history
c = c.replace(
    '| 0.1 | 2026-06-15 | System | Initial test report — Phase 1 foundation verified |',
    '| 0.1 | 2026-06-15 | System | Initial test report — Phase 1 foundation verified |\n| 0.2 | 2026-06-18 | System | Updated for T1.17–T1.20 and R39: added test results for asset schema files (13 fragments), conditional_fragments structure, all 14 AT_ type registrations. 7 new test cases in `test_asset_schema.py` — all pass. I004 resolved; I005 raised for placeholder project data. |'
)

# Test counts
c = c.replace('| Test cases planned | 7 |', '| Test cases planned | 14 |')
c = c.replace('| Test cases executed | 7 |', '| Test cases executed | 14 |')
c = c.replace('| Test cases passed | 7 |', '| Test cases passed | 14 |')
c = c.replace('| Issues found | 4 (all resolved) |', '| Issues found | 5 (I001–I004 resolved, I005 deferred) |')

# Execution date
c = c.replace(
    '**Execution Date**: 2026-06-15  ',
    '**Execution Date**: 2026-06-15 (original); 2026-06-18 (T1.20/R39 additions)  '
)

# Add test sections 7.7 and 7.8 before "## 8."
INSERT = '''
### 7.7 Asset Schema Files (T1.17–T1.20)

| # | Test Case | Expected | Result | Notes |
| :- | :-------- | :------- | :----: | :---- |
| 8  | `test_asset_schema_files_exist` | All 3 asset schema files present in `eks/config/` | ✅ PASS | `eks_asset_base_schema.json`, `eks_asset_setup_schema.json`, `eks_asset_config.json` |
| 9  | `test_asset_base_schema_fragments` | Exactly 13 fragment `$defs` present | ✅ PASS | All 13 fragments confirmed including `specialist_equipment` and `motor_control` |
| 10 | `test_asset_schema_validation` | `eks_asset_config.json` validates against `eks_asset_setup_schema.json` | ✅ PASS | `referencing` registry used for `$ref` resolution |

### 7.8 Zero-Code Extensibility (R39)

| # | Test Case | Expected | Result | Notes |
| :- | :-------- | :------- | :----: | :---- |
| 11 | `test_r39_conditional_fragments_structure` | AT_EQUIP has `conditional_fragments` with valid `when`/`in` rule for `specialist_equipment` | ✅ PASS | `when: device_type_code`, `in: [UV, FILT, CONV, SCR, DOSING]` |
| 12 | `test_r39_motor_control_fragment` | AT_MOTOR includes `motor_control` in fragments list | ✅ PASS | |
| 13 | `test_r39_all_config_fragments_in_base` | Every fragment name in config exists in base schema `definitions` | ✅ PASS | All 13 names cross-validated |
| 14 | `test_r39_all_at_types_present` | All 14 AT_ tag types registered in `asset_type_registry` | ✅ PASS | Exact set match confirmed |

---

'''

# Find the marker for section 8 and insert before it
marker = '## 8. Test Success Criteria'
idx = c.find(marker)
assert idx != -1, "Could not find section 8 marker"
c = c[:idx] + INSERT + c[idx:]

# Success criteria checklist additions
c = c.replace(
    '| Deprecated API usage resolved | ✅ | `RefResolver` → `referencing` |',
    '| Deprecated API usage resolved | ✅ | `RefResolver` → `referencing` |\n| Asset schema files present (T1.20): 3 files, 13 fragments | ✅ | `test_asset_schema_files_exist`, `test_asset_base_schema_fragments` |\n| Asset config validates against setup schema (T1.20) | ✅ | `test_asset_schema_validation` |\n| R39 zero-code extensibility: `conditional_fragments` in setup schema and config | ✅ | `test_r39_conditional_fragments_structure`, `test_r39_motor_control_fragment` |\n| All 14 AT_ types registered; all fragment names resolve to base schema | ✅ | `test_r39_all_config_fragments_in_base`, `test_r39_all_at_types_present` |\n| I004 resolved — schema metadata fields removed from properties | ✅ | U013 |\n| I005 raised — placeholder project data in `eks_config.json` | ⏸️ Deferred | `_note` added to config; replace with WSD11 data when confirmed |'
)

# Files created section
c = c.replace(
    '### Files Created\n- `eks/engine/__init__.py` — Package init with version',
    '### Files Created\n- `eks/engine/__init__.py` — Package init with version'
)
# Add new files to "Files Created" section
c = c.replace(
    '- `eks/workplan/reports/phase_1_foundation_report.md` — This report',
    '- `eks/workplan/reports/phase_1_foundation_report.md` — This report\n- `eks/config/eks_asset_base_schema.json` — 13 fragment definitions (v1.1.0)\n- `eks/config/eks_asset_setup_schema.json` — conditional_fragments structure, 13-fragment enum (v1.1.0)\n- `eks/config/eks_asset_config.json` — 14 AT_ types, conditional rules, full column normalization (v1.1.0)\n- `eks/workplan/appendix_a_asset_schema.md` — Universal Plant Item Schema appendix (v0.3)\n- `eks/test/test_asset_schema.py` — 7 asset schema and R39 test cases'
)

# Recommendations — add one
c = c.replace(
    '4. **Report generation automation**: Future phase reports should be generated immediately upon phase completion to avoid gaps.',
    '4. **Report generation automation**: Future phase reports should be generated immediately upon phase completion to avoid gaps.\n5. **Replace placeholder project data**: `eks_config.json` `project_rules_registry` and `discipline_registry` contain P123/P456 example entries (I005). Replace with actual WSD11 disciplines once confirmed by project team.'
)

# Test file reference
c = c.replace(
    '6. [Test File](../../test/test_phase1.py)',
    '6. [Test File — Phase 1 Foundation](../../test/test_phase1.py)\n7. [Test File — Asset Schema & R39](../../test/test_asset_schema.py)'
)

with open('eks/workplan/reports/phase_1_foundation_report.md', 'w', encoding='utf-8') as f:
    f.write(c)
print("phase_1_foundation_report.md patched to v0.2")

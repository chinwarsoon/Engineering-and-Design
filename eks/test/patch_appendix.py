with open('eks/workplan/appendix_a_asset_schema.md', 'r', encoding='utf-8') as f:
    content = f.read()

# ── A3 replacement ────────────────────────────────────────────────────────────
A3_OLD_START = '## A3. Type Composition Map'
A3_OLD_END   = '- Instruments include `piping_connection` for process tap details + `instrumentation` for sensor specs'

A3_NEW = '''## A3. Type Composition Map

Each `AT_` tag_type is composed of fragments. The composition is registered in `eks_asset_config.json` under `asset_type_registry`.

```
Legend:  ● = always included   ○ = conditional   — = not included

tag_type       Label                frag_core  proc_cond  mfr  lifecycle  ctrl_sys  piping  valve  actuator  rotating  instrum  pipeline_rt  specialist  motor_ctrl
──────         ─────                ────────   ────────   ───  ─────────  ────────  ──────  ─────  ────────  ────────  ───────  ───────────  ──────────  ──────────
AT_EQUIP       Equipment            ●          ●          ●    ●          ●         —       —      —         ●         —        —            ○           —
AT_EQPMP       Pump                 ●          ●          ●    ●          ●         —       —      —         ●         —        —            —           —
AT_EQTNK       Tank                 ●          ●          ●    ●          —         —       —      —         —         —        —            —           —
AT_EQVES       Vessel               ●          ●          ●    ●          —         —       —      —         —         —        —            —           —
AT_EQEXC       Heat Exchanger       ●          ●          ●    ●          —         —       —      —         —         —        —            —           —
AT_INCOMP      Inline Component     ●          ●          ●    ●          —         ●       —      —         —         —        —            —           —
AT_INST_       Instrument           ●          ●          ●    ●          ●         ●       —      —         —         ●        —            —           —
AT_INST_CS     Ctrl Sys Instrument  ●          ●          ●    ●          ●         ●       —      —         —         ●        —            —           —
AT_INST_FLO    Flow Instrument      ●          ●          ●    ●          ●         ●       —      —         —         ●        —            —           —
AT_MOTOR       Motor                ●          ●          ●    ●          ●         —       —      —         ●         —        —            —           ●
AT_PROCESS     Pipeline             ●          ●          —    —          —         ●       —      —         —         —        ●            —           —
AT_CVALVE      Control Valve        ●          ●          ●    ●          ●         ●       ●      ●         —         —        —            —           —
AT_PSV         Safety Valve         ●          ●          ●    ●          —         ●       ●      —         —         —        —            —           —
AT_HVALVE      Manual Valve         ●          ●          ●    ●          —         ●       ●      —         —         —        —            —           —
```

**Composition Rules:**
- All assets include `item_core` + `process_conditions`
- Rotating equipment (pumps, motors, general equipment) add `rotating_equipment`
- `AT_EQUIP` conditionally includes `specialist_equipment` (populated only for UV/filtration/conveyor types)
- Motors add `motor_control` for starter type, MCC feed, and equipment number linkage
- Control valves add `actuator` — which now contains the full second manufacturer+lifecycle block for the actuator sub-asset
- Pipelines are the only type without manufacturer or lifecycle data (pure routing)
- Instruments include `piping_connection` for process tap details + `instrumentation` for sensor specs
- **13 fragments total** (was 11 — added `specialist_equipment` A2.12 and `motor_control` A2.13)'''

idx_start = content.find(A3_OLD_START)
idx_end   = content.find(A3_OLD_END) + len(A3_OLD_END)
assert idx_start != -1, "A3 start not found"
assert idx_end   > idx_start, "A3 end not found"
content = content[:idx_start] + A3_NEW + content[idx_end:]
print("A3 replaced")

# ── A5 replacement ────────────────────────────────────────────────────────────
A5_OLD_START = '## A5. Column Normalization Map'
A5_OLD_END   = '   - Indexes on `keytag`, `tag_no`, `pipeline_tag_number`'

A5_NEW = '''## A5. Column Normalization Map

Multiple column names across sheets normalize to a single canonical field:

| Canonical Field | Equipment | Inline Component | Instrument | Motor | Pipeline | CONTROLVALVE | MANUALVALVE |
| :-------------- | :-------: | :--------------: | :--------: | :---: | :------: | :----------: | :---------: |
| `p_and_id_file` | PID NUMBER | P&ID FILE | DOC_FNAME | P&ID DRAWING | DOC_FNAME | P&ID FILENAME | DOC_FNAME |
| `unit` | UNIT | UNIT | UNIT_PROCESS_NO | UNIT | UNIT | UNIT | UNIT |
| `description` | DESCRIPTION | DESCRIPTION | DESCRIPTION | NAME | DESCRIPTION | NAME | DESCRIPTION |
| `short_description` | SHORT DESCR | SHORT DESCR | SHORT DESCR | SHORT DESCR | — | SHORT DESCR | SHORT DESCR |
| `pipe_size_nominal_mm` | — | PIPE SIZE - NOMINAL (MM) | PIPE SIZE - NOMINAL | — | DESIGN SIZE - NOMINAL (MM) | PIPE SIZE - NOMINAL (MM) | PIPE SIZE - NOMINAL (MM) |
| `ace_category` | PUB_ACE_CATEGORY | ACE CATEGORY | PUB_ACE_CATEGORY | ACE CATEGORY | — | ACE CATEGORY | ACE CATEGORY |
| `manufacturer_2d_file` | MANUFACTURER 2D MODEL FILE NAME | MANUFACTURER 2D MODEL FILE NAME | — | MANUFACTURER 2D MODEL FILE NAME | — | VALVE/ACTUATOR MANUFACTURER 2D | MANUFACTURER 2D MODEL FILE NAME |
| `manufacturer_3d_file` | MANUFACTURER 3D MODEL FILE NAME | MANUFACTURER 3D MODEL FILE NAME | — | MANUFACTURER 3D MODEL FILE NAME | — | MANUFACTURER 3D MODEL FILE NAME | MANUFACTURER 3D MODEL FILE NAME |
| `lining_material` | LINING_MATERIAL | — | LINING MATERIAL | — | LINING MATERIAL | LINING MATERIAL | LINING MATERIAL |
| `manufacturer_fax` | MANUFACTURER FAX | — | — | MANUFACTURER FAX | — | MANUFACTURER FAX | MANUFACTURER FAX |
| `valve_internal_type` | — | — | — | — | — | IINT1 | VINT1 |
| `alarm_limit_hh` | — | — | ALARM LIMIT HH / HIHI_ALARM_TP | — | — | — | — |
| `alarm_limit_h` | — | — | ALARM LIMIT H / HI_ALARM_TP | — | — | — | — |
| `alarm_limit_l` | — | — | ALARM LIMIT L / LO_ALARM_TP | — | — | — | — |
| `alarm_limit_ll` | — | — | ALARM LIMIT LL / LOLO_ALARM_TP | — | — | — | — |

**Notes on dual alarm columns (Instrument sheet):** The Instrument sheet contains two sets of alarm columns — `ALARM LIMIT HH/H/L/LL` (raw set points) and `HIHI_ALARM_TP / HI_ALARM_TP / LO_ALARM_TP / LOLO_ALARM_TP` (trip set points). The loader should prefer the `_TP` values when both are populated; store both if they differ.

**Ingestion Logic:**
1. Read each sheet → extract header row → map to canonical fields via column normalization table
2. Look up the row's `TAG_TYPE` in `asset_type_registry` → get fragment list
3. For each fragment, extract only the properties that belong to that fragment from the mapping
4. **Deduplicate Pipeline rows**: 612 KEYTAGs appear on multiple rows (same pipeline tag on multiple P&ID sheets). Strategy: group by `keytag`, merge rows by taking first non-null value per field, collect all distinct `DOC_FNAME` values as a list for `p_and_id_file` (produces multiple `REFERENCED_BY_DWG` edges)
5. Flatten to a single document per `keytag` with the fragment-namespaced properties
6. Write to Neo4j as a typed node with:
   - Node label = `TAG_TYPE` (e.g., `AT_EQPMP`)
   - Properties = all fragment fields flattened to top-level
   - Indexes on `keytag`, `tag_no`, `pipeline_tag_number`'''

idx_start = content.find(A5_OLD_START)
idx_end   = content.find(A5_OLD_END) + len(A5_OLD_END)
assert idx_start != -1, "A5 start not found"
assert idx_end   > idx_start, "A5 end not found"
content = content[:idx_start] + A5_NEW + content[idx_end:]
print("A5 replaced")

with open('eks/workplan/appendix_a_asset_schema.md', 'w', encoding='utf-8') as f:
    f.write(content)
print("File written successfully")

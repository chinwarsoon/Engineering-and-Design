# Appendix A — Universal Plant Item Schema

## A1. Overview

Project asset data represents structured engineering plant inventory — equipment, instruments, pipelines, valves, and motors — as a **relationship database**. Each plant item is uniquely identified by a `keytag` and typed by a `tag_type` code (e.g., `AT_EQPMP`, `AT_INST_`, `AT_CVALVE`). Items are connected to each other (pipeline → component, asset → P&ID document) and grouped by project hierarchy (project → unit → service).

The schema uses **fragment composition**: each tag_type is a set of property fragments. No inheritance hierarchy — just a registry mapping each type to its fragments. Adding a new asset type means adding a config entry, not changing code.

**Source**: Project datadrop Excel at `eks/data/twrp/datadrop/Datadrop Summary.xlsx`  
**Scale**: 7 sheets, 7,681 items, 447,867 fields, ~44% pending data entry  
**Project**: WSD11 (Contract C4B, Units 003/006/008/111/112)

---

## A2. Fragment Definitions

Each fragment is a reusable property group. Fragments with `(opt.)` are included only when data is present.

### A2.1 `item_core` — Universal Identity (every asset)
| Property | Type | Source Column(s) | Description |
| :------- | :--- | :--------------- | :---------- |
| `keytag` | string | KEYTAG | Unique system identifier |
| `tag_type` | string | TAG_TYPE | Category code (AT_EQUIP, AT_INST_, etc.) |
| `tag_no` | string | TAG_NO | Plant tag number, e.g. WSD11-003-P-0101 |
| `project_prefix` | string | PROJECT PREFIX | Project code (WSD11) |
| `unit` | string | UNIT, UNIT_PROCESS_NO | Process unit number |
| `service` | string | SERVICE | Fluid service code (G2D, THP, HS, IA, etc.) |
| `tag_loop_number` | string | TAG LOOP NUMBER | Loop/sequence identifier |
| `tag_suffix` | string | TAG SUFFIX | Optional suffix (A, B, C, D) |
| `description` | string | DESCRIPTION, NAME | Full item description |
| `short_description` | string | SHORT DESCR | Short description |
| `hazardous_zone` | string | HAZARDOUS ZONE | Zone classification |
| `contract_info` | string | CONTRACT INFO | Contract identifier |
| `device_type_code` | string | DEVICE TYPE CODE | Equipment/device type code |
| `p_and_id_file` | string | PID NUMBER, P&ID FILE, DOC_FNAME | Reference drawing filename |

### A2.2 `process_conditions` — Design & Operating Conditions
| Property | Type | Description |
| :------- | :--- | :---------- |
| `design_pressure` | number | Design pressure rating |
| `pressure_rating` | string | Pressure class (PN16, PN25, etc.) |
| `operating_pressure_normal` | number | Normal operating pressure |
| `operating_pressure_min` | number | Minimum operating pressure |
| `operating_pressure_max` | number | Maximum operating pressure |
| `operating_temperature_normal` | number | Normal operating temperature (°C) |
| `flow_rate_nominal` | number | Nominal design flow rate |
| `flow_rate_min` | number | Minimum flow rate |
| `flow_rate_max` | number | Maximum flow rate |
| `test_pressure` | number | Hydrostatic test pressure |

### A2.3 `manufacturer` — Manufacturer & Product Details
| Property | Type | Description |
| :------- | :--- | :---------- |
| `brand` | string | Product brand name |
| `model_number` | string | Model identifier |
| `serial_number` | string | Unit serial number |
| `manufacturer_name` | string | Manufacturer company name |
| `manufacturer_website` | string | Manufacturer URL |
| `manufacturer_phone` | string | Contact phone |
| `manufacturer_email` | string | Contact email |
| `manufacturer_location` | string | Manufacturing country/city |
| `lot_number` | string | Manufacturing lot/batch |
| `manufacture_date` | date | Date of manufacture |
| `model_2d_file` | string | 2D model/drawing file reference |
| `model_3d_file` | string | 3D model file reference |

### A2.4 `asset_lifecycle` — Asset Lifecycle & Financial (ACE)
| Property | Type | Description |
| :------- | :--- | :---------- |
| `ace_category` | string | ACE asset category code |
| `generic_equipment_type` | string | Generic equipment classification |
| `ace_asset_class` | string | ACE asset class |
| `life_span` | string | Expected service life |
| `supplier` | string | Supplier name |
| `cost_center` | string | Cost center code |
| `replacement_cost` | number | Estimated replacement cost |
| `wbs_element` | string | WBS element code |
| `est_replacement_date` | date | Estimated replacement year |
| `date_of_commission` | date | Commissioning date |
| `warranty_terms` | string | Warranty description |
| `warranty_start_date` | date | Warranty start |
| `warranty_expiry_date` | date | Warranty expiry |
| `product_certification` | string | Certification standard |
| `ace_asset_number` | string | ACE asset number |
| `ace_asset_sub_number` | string | ACE asset sub-number |

### A2.5 `control_system` — Control & I&C Interface
| Property | Type | Description |
| :------- | :--- | :---------- |
| `lcs_type` | string | Local control station type |
| `plc_panel` | string | PLC panel identifier |
| `plc_panel_location` | string | PLC panel physical location |
| `rio_panel` | string | Remote I/O panel identifier |
| `rio_panel_location` | string | RIO panel physical location |

### A2.6 `piping_connection` — Piping Interface
| Property | Type | Description |
| :------- | :--- | :---------- |
| `pipe_size_nominal_mm` | number | Nominal pipe size (mm) |
| `pipeline_tag_number` | string | Connected pipeline tag |
| `lining_material` | string | Internal lining material |
| `end_condition` | string | End preparation type (flanged, threaded, welded) |

### A2.7 `valve_internals` — Valve Trim & Body
| Property | Type | Description |
| :------- | :--- | :---------- |
| `valve_duty` | string | Duty/standby designation |
| `body_material` | string | Valve body material |
| `stem_material` | string | Stem material |
| `closure_element` | string | Closure element type (gate, ball, butterfly, plug) |
| `seat_material` | string | Seat/trim material |

### A2.8 `actuator` — Electric Actuator (Control Valves only)
| Property | Type | Description |
| :------- | :--- | :---------- |
| `actuator_tag_number` | string | Actuator tag reference |
| `actuator_rpm` | number | Actuator output speed |
| `actuator_torque_range` | string | Torque setting range |
| `actuator_rated_voltage` | number | Rated voltage (V) |
| `actuator_rated_frequency` | number | Rated frequency (Hz) |
| `actuator_rated_current` | number | Rated current (A) |
| `actuator_motor_rating_kw` | number | Motor power rating (kW) |
| `actuator_stem_direction` | string | Stem direction (linear, rotary) |
| `actuator_brand` | string | Actuator brand |
| `actuator_model` | string | Actuator model |
| `actuator_serial` | string | Actuator serial number |
| `actuator_manufacturer` | string | Actuator manufacturer |
| `actuator_ace_category` | string | Actuator ACE category |
| `actuator_ace_asset_class` | string | Actuator ACE class |
| `actuator_life_span` | string | Actuator life span |

### A2.9 `rotating_equipment` — Pumps, Motors, Compressors
| Property | Type | Description |
| :------- | :--- | :---------- |
| `rpm` | number | Rotational speed |
| `efficiency` | number | Design efficiency (%) |
| `impeller_type` | string | Impeller design type |
| `impeller_material` | string | Impeller material |
| `rotor_material` | string | Rotor material |
| `stator_material` | string | Stator material |
| `seal_type` | string | Mechanical seal / gland packing type |
| `npsh_min` | number | Minimum NPSH required (m) |
| `head_loss` | number | Head loss (m) |
| `suction_nozzle_size` | number | Suction nozzle diameter (mm) |
| `discharge_nozzle_size` | number | Discharge nozzle diameter (mm) |
| `design_capacity` | number | Design capacity |
| `design_capacity_unit` | string | Capacity unit (m³/h, kW, t/h, m³) |
| `duty_standby` | string | Duty or standby designation |
| `casing_material` | string | Casing/body material |
| `voltage` | number | Motor rated voltage (V) *(Motor only)* |
| `frequency` | number | Motor rated frequency (Hz) *(Motor only)* |
| `phase` | string | Motor phase (1, 3) *(Motor only)* |
| `motor_rating` | number | Motor power rating (kW) *(Motor only)* |

### A2.10 `instrumentation` — Sensors, Transmitters & Alarms
| Property | Type | Description |
| :------- | :--- | :---------- |
| `isa_instrument_id` | string | ISA instrument identifier (FAL, FE, etc.) |
| `measurement_principle` | string | Measurement technology (DP, magnetic, ultrasonic, etc.) |
| `sensor_model` | string | Sensor model number |
| `sensor_material` | string | Sensor wetted material |
| `sensor_ip_rating` | string | Ingress protection rating |
| `sensor_range` | string | Measurement range |
| `sensor_wetted_parts` | string | Wetted parts material |
| `output_signal` | string | Output type (4-20mA, HART, etc.) |
| `accuracy` | string | Measurement accuracy |
| `calibration_range` | string | Calibrated range |
| `supply_voltage` | string | Power supply voltage |
| `alarm_limit_hh` | number | High-high alarm set point |
| `alarm_limit_h` | number | High alarm set point |
| `alarm_limit_l` | number | Low alarm set point |
| `alarm_limit_ll` | number | Low-low alarm set point |
| `set_point` | number | Trip/set point (for switches) |
| `tube_material` | string | Impulse tube material |
| `tube_size` | string | Impulse tube size |

### A2.11 `pipeline_route` — Piping Geometry & Routing
| Property | Type | Description |
| :------- | :--- | :---------- |
| `pipe_material` | string | Pipe base material |
| `outside_diameter_mm` | number | Pipe outside diameter (mm) |
| `wall_thickness_mm` | number | Pipe wall thickness (mm) |
| `design_specification` | string | Design code / specification |
| `insulation_material` | string | Thermal insulation material |
| `insulation_thickness` | number | Insulation thickness (mm) |
| `from_component` | string | Source equipment/pipeline tag |
| `to_component` | string | Destination equipment/pipeline tag |

---

## A3. Type Composition Map

Each `AT_` tag_type is composed of fragments. The composition is registered in `eks_asset_config.json` under `asset_type_registry`.

```
Legend:  ● = always included   ○ = conditional   — = not included

tag_type          Label                 frag_core  proc_cond  mfr  lifecycle  ctrl_sys  piping  valve  actuator  rotating  instrum  pipeline_route
──────            ─────                 ────────   ────────   ───  ─────────  ────────  ──────  ─────  ────────  ────────  ───────  ──────────────
AT_EQUIP          Equipment             ●          ●          ●    ●          ●         —       —      —         ●         —        —
AT_EQPMP          Pump                  ●          ●          ●    ●          ●         —       —      —         ●         —        —
AT_EQTNK          Tank                  ●          ●          ●    ●          —         —       —      —         —         —        —
AT_EQVES          Vessel                ●          ●          ●    ●          —         —       —      —         —         —        —
AT_EQEXC          Heat Exchanger        ●          ●          ●    ●          —         —       —      —         —         —        —
AT_INCOMP         Inline Component      ●          ●          ●    ●          —         ●       —      —         —         —        —
AT_INST_          Instrument            ●          ●          ●    ●          ●         ●       —      —         —         ●        —
AT_INST_CS        Ctrl Sys Instrument   ●          ●          ●    ●          ●         ●       —      —         —         ●        —
AT_INST_FLO       Flow Instrument       ●          ●          ●    ●          ●         ●       —      —         —         ●        —
AT_MOTOR          Motor                 ●          ●          ●    ●          ●         —       —      —         ●         —        —
AT_PROCESS        Pipeline              ●          ●          —    —          —         ●       —      —         —         —        ●
AT_CVALVE         Control Valve         ●          ●          ●    ●          ●         ●       ●      ●         —         —        —
AT_PSV            Safety Valve          ●          ●          ●    ●          —         ●       ●      —         —         —        —
AT_HVALVE         Manual Valve          ●          ●          ●    ●          —         ●       ●      —         —         —        —
```

**Composition Rules:**
- All assets include `item_core` + `process_conditions`
- Rotating equipment (pumps, motors) add `rotating_equipment`
- Control valves add `actuator` with embedded manufacturer and ACE sub-fragments
- Pipelines are the only type without manufacturer or lifecycle data (pure routing)
- Instruments include `piping_connection` for process tap details + `instrumentation` for sensor specs

---

## A4. Relationship Graph

Asset data is a **relationship database** with the following entity-relationship model:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          PROJECT (WSD11)                                │
│                              │                                          │
│                    ┌─────────┴──────────┐                               │
│                    │                    │                               │
│              ┌─────┴─────┐      ┌──────┴──────┐                        │
│              │  CONTRACT  │      │    UNITS    │                        │
│              │   (C4B)    │      │ 003,006,111 │                        │
│              └───────────┘      └──────┬──────┘                        │
│                                        │                                │
│                              ┌─────────┴─────────┐                     │
│                              │                   │                     │
│                         ┌────┴────┐        ┌─────┴─────┐               │
│                         │ SERVICE │        │  P&ID DWG  │              │
│                         │ G2D,THP │        │(.dgn file) │              │
│                         └────┬────┘        └─────┬─────┘               │
│                              │                   │                     │
│         ┌────────────────────┼────────────────────┘                    │
│         │                    │                   ┌────────────────┐     │
│         │              ┌─────┴──────┐            │  MANUFACTURER  │     │
│         │              │   ASSET    │◄───────────│  (name, brand, │     │
│         │              │  (keytag)  │            │   model, ser)  │     │
│         │              └─────┬──────┘            └────────────────┘     │
│         │                    │                                           │
│         │      ┌─────────────┼──────────────┐                          │
│         │      │             │              │                          │
│         │  ┌───┴───┐   ┌────┴────┐   ┌─────┴─────┐                   │
│         │  │ UNIT  │   │ SERVICE │   │ TAG_TYPE  │                    │
│         │  │ 003   │   │  G2D    │   │ AT_EQPMP  │                    │
│         │  └───────┘   └─────────┘   └───────────┘                   │
│         │                                                            │
│         ▼                                                            │
│  ┌─────────────────────────────────────────────┐                     │
│  │          ASSET-TO-ASSET RELATIONSHIPS        │                    │
│  │                                             │                    │
│  │  PIPELINE ──CONNECTS_TO──▶ Inline Component │                    │
│  │  PIPELINE ──CONNECTS_TO──▶ Valve            │                    │
│  │  PIPELINE ──CONNECTS_TO──▶ Instrument       │                    │
│  │  PIPELINE ──CONNECTS_TO──▶ Equipment        │                    │
│  │  Asset ────REFERENCED_BY_DWG──▶ P&ID File   │                    │
│  │  Control Valve ──HAS_ACTUATOR──▶ Actuator   │                    │
│  │                                             │                    │
│  │  Source: FROM_COMPONENT / TO_COMPONENT      │                    │
│  │  in Pipeline sheet + P&ID filename in       │                    │
│  │  PID NUMBER / DOC_FNAME columns             │                    │
│  └─────────────────────────────────────────────┘                    │
└─────────────────────────────────────────────────────────────────────────┘
```

**Relationship Types:**
| Relationship | Source Node | Target Node | Cardinality | Origin Field |
| :----------- | :---------- | :---------- | :---------- | :----------- |
| `CONNECTS_TO` | Pipeline (AT_PROCESS) | Equipment / Valve / Instrument / Inline Component | M:N | FROM_COMPONENT / TO_COMPONENT |
| `REFERENCED_BY_DWG` | Asset (any) | Document (P&ID drawing) | M:N | PID NUMBER, P&ID FILE, DOC_FNAME |
| `HAS_ACTUATOR` | Control Valve (AT_CVALVE) | Actuator sub-asset | 1:1 | ACTUATOR TAG NUMBER |
| `BELONGS_TO_UNIT` | Asset (any) | Unit | M:1 | UNIT |
| `BELONGS_TO_SERVICE` | Asset (any) | Service | M:1 | SERVICE |
| `SUPERSEDES` | Document Revision | Document Revision | 1:1 | Revision chain |

---

## A5. Column Normalization Map

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
| `lining_material` | — | — | LINING MATERIAL | — | LINING MATERIAL | LINING MATERIAL | LINING MATERIAL |

**Ingestion Logic:**
1. Read each sheet → extract header row → map to canonical fields via column normalization table
2. Look up the row's `TAG_TYPE` in `asset_type_registry` → get fragment list
3. For each fragment, extract only the properties that belong to that fragment from the mapping
4. Flatten to a single document per `keytag` with the fragment-namespaced properties
5. Write to Neo4j as a typed node with:
   - Node label = `TAG_TYPE` (e.g., `AT_EQPMP`)
   - Properties = all fragment fields flattened to top-level
   - Indexes on `keytag`, `tag_no`, `pipeline_tag_number`

---

## A6. Schema File Structure

```
eks/config/
├── eks_asset_base_schema.json       # Fragment definitions (A2.1–A2.11)
├── eks_asset_setup_schema.json       # asset_type_registry declaration + column normalization rules
└── eks_asset_config.json             # Project-specific: type→fragment map, datadrop source path, column mappings
```

This follows the same base/setup/config inheritance pattern as the main EKS schema (Section 7c), ensuring SSOT compliance per agent_rule §4.

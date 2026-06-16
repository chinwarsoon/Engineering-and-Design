# Appendix A — Universal Plant Item Schema

**Version**: 0.3  
**Last Updated**: 2026-06-17  
**Summary of Changes**:  
v0.2 — Gap analysis against actual datadrop Excel. Added 14 unmapped Equipment columns (`specialist_equipment` fragment, A2.12), 10 Motor columns to `rotating_equipment` and new `motor_control` fragment (A2.13), full actuator manufacturer+lifecycle block to `actuator` fragment (A2.8), 12 Instrument columns to `instrumentation` fragment (A2.10), 3 MANUALVALVE columns to `valve_internals` (A2.7). Added pipeline duplicate KEYTAG ingestion rule (A5). Updated composition map (A3) and column normalization map (A5).  
v0.3 — Added A7: How to Add a New Plant Asset Type. Three scenarios covered (existing fragments only, conditional fragment, new fragment). Decision guide and validation step included. Supports R39 zero-code extensibility.

---

## A1. Overview

Project asset data represents structured engineering plant inventory — equipment, instruments, pipelines, valves, and motors — as a **relationship database**. Each plant item is uniquely identified by a `keytag` and typed by a `tag_type` code (e.g., `AT_EQPMP`, `AT_INST_`, `AT_CVALVE`). Items are connected to each other (pipeline → component, asset → P&ID document) and grouped by project hierarchy (project → unit → service).

The schema uses **fragment composition**: each tag_type is a set of property fragments. No inheritance hierarchy — just a registry mapping each type to its fragments. Adding a new asset type means adding a config entry, not changing code.

**Source**: Project datadrop Excel at `eks/data/twrp/datadrop/Datadrop Summary.xlsx`  
**Scale**: 7 sheets, 7,681 items, 447,867 fields, ~44% pending data entry  
**Project**: WSD11 (Contract C4B, Units 003/006/008/111/112)  
**Data quality note**: Pipeline sheet has 612 KEYTAGs with duplicate rows (same tag on multiple P&ID sheets — see ingestion rule in A5).

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
| Property | Type | Source Column(s) | Description |
| :------- | :--- | :--------------- | :---------- |
| `valve_duty` | string | VALVE - DUTY | Duty/standby designation |
| `body_material` | string | BODY MATERIAL | Valve body material |
| `stem_material` | string | STEM MATERIAL | Stem material |
| `closure_element` | string | VALVE CLOSURE ELEMENT | Closure element type (gate, ball, butterfly, disc, plug) |
| `seat_material` | string | SEAT MATERIAL | Seat/trim material |
| `locked_position` | string | LOCKED POSITION | Valve locked position (MANUALVALVE only: NO, OPEN, CLOSED) |
| `valve_internal_type` | string | VINT1 | Internal valve type code, e.g. BUTTERFLY_VALVE, KNIFE_GATE_CONTROL_VALVE (MANUALVALVE/CONTROLVALVE only) |

### A2.8 `actuator` — Actuator (Control Valves only)

The CONTROLVALVE sheet carries **two full manufacturer+lifecycle blocks** — one for the valve body and one for the actuator sub-asset (all columns suffixed `- ACTUATOR`). The `actuator` fragment captures all actuator-specific fields including its own manufacturer contact details and full ACE lifecycle data.

| Property | Type | Source Column(s) | Description |
| :------- | :--- | :--------------- | :---------- |
| `actuator_tag_number` | string | ACTUATOR TAG NUMBER | Actuator tag reference |
| `actuator_display_label` | string | ACTUATOR DISPLAY LABEL | Display label (e.g. "Cylinder Operator", "Diaphragm Actuator") |
| `actuator_internal_type` | string | A_ACT_DISPLAY, IINT1 | Internal actuator type code |
| `fail_mode` | string | FAIL MODE DISPLAY LABEL | Fail-safe position (CLOSE, OPEN, LAST) |
| `actuator_rpm` | number | ACTUATOR - RPM | Actuator output speed (RPM) |
| `actuator_motor_rpm` | number | ACTUATOR - MOTOR RPM | Internal motor speed (RPM) |
| `actuator_torque_range` | string | ACTUATOR - TORQUE SETTING RANGE | Torque setting range |
| `actuator_locked_rotor_torque` | number | ACTUATOR - LOCKED ROTOR TORQUE (NM) | Locked rotor torque (Nm) |
| `actuator_rated_voltage` | number | ACTUATOR - RATED VOLTAGE | Rated voltage (V) |
| `actuator_rated_frequency` | number | ACTUATOR - RATED FREQUENCY | Rated frequency (Hz) |
| `actuator_rated_current` | number | ACTUATOR - RATED CURRENT (AMPERE) | Rated current (A) |
| `actuator_rated_torque_current` | number | ACTUATOR - RATED TORQUE CURRENT (AMPERE) | Rated torque current (A) |
| `actuator_motor_rating_kw` | number | ACTUATOR - MOTOR RATING (KW) | Motor power rating (kW) |
| `actuator_stem_direction` | string | ACTUATOR - STEM DIRECTION | Stem direction (linear, rotary) |
| `actuator_brand` | string | BRAND - ACTUATOR | Actuator brand |
| `actuator_model` | string | MODEL NUMBER - ACTUATOR | Actuator model number |
| `actuator_serial` | string | SERIAL NUMBER - ACTUATOR | Actuator serial number |
| `actuator_manufacturer_name` | string | MANUFACTURER NAME - ACTUATOR | Actuator manufacturer name |
| `actuator_manufacturer_website` | string | MANUFACTURER WEBPAGE - ACTUATOR | Actuator manufacturer URL |
| `actuator_manufacturer_phone` | string | MANUFACTURER PHONE - ACTUATOR | Actuator manufacturer phone |
| `actuator_manufacturer_fax` | string | MANUFACTURER FAX - ACTUATOR | Actuator manufacturer fax |
| `actuator_manufacturer_email` | string | MANUFACTURER EMAIL - ACTUATOR | Actuator manufacturer email |
| `actuator_manufacturer_location` | string | MANUFACTURER LOCATION - ACTUATOR | Actuator manufacturer location |
| `actuator_model_3d_file` | string | MANUFACTURER 3D MODEL FILE NAME - ACTUATOR | Actuator 3D model file |
| `actuator_lot_number` | string | LOT NUMBER - ACTUATOR | Actuator lot/batch number |
| `actuator_manufacture_date` | date | MANUFACTURE DATE - ACTUATOR | Actuator manufacture date |
| `actuator_ace_category` | string | ACE CATEGORY - ACTUATOR | Actuator ACE category |
| `actuator_generic_equipment_type` | string | GENERIC EQUIPMENT TYPE - ACTUATOR | Actuator generic type |
| `actuator_ace_asset_class` | string | ACE ASSET CLASS - ACTUATOR | Actuator ACE class |
| `actuator_life_span` | string | LIFE SPAN - ACTUATOR | Actuator life span |
| `actuator_supplier` | string | SUPPLIER - ACTUATOR | Actuator supplier |
| `actuator_cost_center` | string | COST CENTER - ACTUATOR | Actuator cost center |
| `actuator_replacement_cost` | number | REPLACEMENT COST - ACTUATOR | Actuator replacement cost |
| `actuator_wbs_element` | string | WBS ELEMENT - ACTUATOR | Actuator WBS element |
| `actuator_est_replacement_date` | date | EST REPLACEMENT DATE - ACTUATOR | Actuator replacement date |
| `actuator_date_of_commission` | date | DATE OF COMMISSION - ACTUATOR | Actuator commissioning date |
| `actuator_warranty_terms` | string | WARRANTY TERMS - ACTUATOR | Actuator warranty description |
| `actuator_warranty_start_date` | date | WARRANTY START DATE - ACTUATOR | Actuator warranty start |
| `actuator_warranty_expiry_date` | date | WARRANTY EXPIRY DATE - ACTUATOR | Actuator warranty expiry |
| `actuator_product_certification` | string | PRODUCT CERTIFICATION - ACTUATOR | Actuator certification |
| `actuator_ace_asset_number` | string | ACE ASSET NUMBER - ACTUATOR | Actuator ACE asset number |
| `actuator_ace_asset_sub_number` | string | ACE ASSET SUB NUMBER - ACTUATOR | Actuator ACE sub-number |

### A2.9 `rotating_equipment` — Pumps, Motors, Compressors
| Property | Type | Source Column(s) | Description |
| :------- | :--- | :--------------- | :---------- |
| `rpm` | number | RPM, MOTOR - RPM | Rotational speed |
| `efficiency` | number | EFFICIENCY_DESIGN_CAP | Design efficiency (%) |
| `impeller_type` | string | IMPELLER_TYPE | Impeller design type |
| `impeller_material` | string | IMPELLER_MATERIAL | Impeller material |
| `impeller_wear_ring` | string | IMPELLER_WEAR_RING | Impeller wear ring material |
| `rotor_material` | string | ROTOR_MATERIAL | Rotor material |
| `stator_material` | string | STATOR_MATERIAL | Stator material |
| `casing_material` | string | ECASING_MTR | Casing/body material |
| `gearbox_material` | string | GEARBOX_MATERIAL | Gearbox material (if applicable) |
| `conveyor_hub_material` | string | CONVERYOR_HUB_MATERIAL | Conveyor hub material (specialty equipment) |
| `seal_type` | string | MECH SEAL/GLAND PACKAGING, SEAL_TYPE_MECH | Mechanical seal / gland packing type |
| `npsh_min` | number | NPSH - MIN | Minimum NPSH required (m) |
| `submergence_min` | number | SUBMERGENCE - MIN | Minimum submergence depth (m) |
| `head_loss` | number | HEAD LOSS | Head loss (m) |
| `suction_nozzle_size` | number | SUCTION NOZZLE SIZE | Suction nozzle diameter (mm) |
| `discharge_nozzle_size` | number | DISCHARGE NOZZLE SIZE | Discharge nozzle diameter (mm) |
| `design_capacity` | number | DESIGN CAPACITY | Design capacity |
| `design_capacity_unit` | string | DESIGN CAPACITY UNIT | Capacity unit (m³/h, kW, t/h, m³) |
| `duty_standby` | string | DUTY STAND BY | Duty or standby designation |
| `insulation_class` | string | EINS | Motor/equipment insulation class |
| `voltage` | number | MOTOR - VOLTAGE | Motor rated voltage (V) *(Motor only)* |
| `frequency` | number | MOTOR - HERTZ | Motor rated frequency (Hz) *(Motor only)* |
| `phase` | string | MOTOR - PHASE | Motor phase (THREE, SINGLE) *(Motor only)* |
| `motor_rating` | number | ACTUATOR - MOTOR RATING, RATED MOTOR | Motor power rating (kW) *(Motor only)* |
| `motor_speed_class` | string | M_SPEED_CLASS | Motor speed class *(Motor only)* |
| `motor_rated_current` | number | MOTOR - RATED CURRENT | Motor rated current (A) *(Motor only)* |
| `motor_torque_range` | string | MOTOR - TORQUE SETTING RANGE | Motor torque setting range *(Motor only)* |
| `motor_locked_rotor_torque` | number | MOTOR - LOCKED ROTOR TORQUE | Motor locked rotor torque *(Motor only)* |
| `motor_rated_torque_current` | number | MOTOR - RATED TORQUE CURRENT | Motor rated torque current (A) *(Motor only)* |

### A2.10 `instrumentation` — Sensors, Transmitters & Alarms
| Property | Type | Source Column(s) | Description |
| :------- | :--- | :--------------- | :---------- |
| `isa_instrument_id` | string | ISA INSTRUMENT ID | ISA instrument identifier (FAL, FE, etc.) |
| `instrument_function` | string | INSTRUMENT FUNCTION_CONTACT TYPE | Instrument function and contact type |
| `measurement_principle` | string | MEASUREMENT PRINCIPLE | Measurement technology (DP, magnetic, ultrasonic, etc.) |
| `measurement_sample_point` | string | MEASUREMENT/SAMPLE POINT | Measurement or sample point location |
| `operating_range` | string | OPERATING RANGE | Full operating range description |
| `sensor_model` | string | SENSOR MODEL | Sensor model number |
| `sensor_material` | string | SENSOR MATERIAL | Sensor wetted material |
| `sensor_ip_rating` | string | SENSOR IP RATING | Ingress protection rating |
| `sensor_range` | string | SENSOR RANGE | Measurement range |
| `sensor_wetted_parts` | string | SENSOR WETTED PARTS MATERIAL | Wetted parts material |
| `thermowell` | string | THERMOWELL_TEMPERATURE SENSOR ONLY | Thermowell specification (temperature instruments only) |
| `housing_material` | string | HOUSING MATERIAL | Instrument housing/enclosure material |
| `ingress_protection` | string | INGRESS PROTECTION | Housing IP rating |
| `lightning_arrestor` | string | LIGHTNING ARRESTOR | Lightning/surge arrestor fitted (Y/N/type) |
| `output_signal` | string | OUTPUT SIGNAL | Primary output type (4-20mA, HART, etc.) |
| `output_signal_2` | string | OUTPUT SIGNAL 2 | Secondary output signal type |
| `accuracy` | string | ACCURACY | Measurement accuracy |
| `calibration_range` | string | CALIBRATION RANGE | Calibrated range |
| `supply_voltage` | string | SUPPLY VOLTAGE | Power supply voltage |
| `alarm_limit_hh` | number | ALARM LIMIT HH, HIHI_ALARM_TP | High-high alarm set point |
| `alarm_limit_h` | number | ALARM LIMIT H, HI_ALARM_TP | High alarm set point |
| `alarm_limit_l` | number | ALARM LIMIT L, LO_ALARM_TP | Low alarm set point |
| `alarm_limit_ll` | number | ALARM LIMIT LL, LOLO_ALARM_TP | Low-low alarm set point |
| `set_point` | number | SET POINT | Trip/set point (for switches) |
| `tube_material` | string | TUBE MATERIAL | Impulse tube material |
| `tube_size` | string | TUBE SIZE | Impulse tube size |
| `ams_category` | string | PUB_AMS_CATEGORY | AMS asset management category |

### A2.11 `pipeline_route` — Piping Geometry & Routing
| Property | Type | Source Column(s) | Description |
| :------- | :--- | :--------------- | :---------- |
| `pipe_material` | string | PIPE MATERIAL | Pipe base material |
| `outside_diameter_mm` | number | OUTSIDE DIAMETER | Pipe outside diameter (mm) |
| `wall_thickness_mm` | number | WALL THICKNESS | Pipe wall thickness (mm) |
| `design_specification` | string | DESIGN SPECIFICATION | Design code / specification |
| `insulation_material` | string | INSULATION MATERIAL | Thermal insulation material |
| `insulation_thickness` | number | INSULATION THICKNESS | Insulation thickness (mm) |
| `from_component` | string | FROM_COMPONENT, FROM_COMPONENT1 | Source equipment/pipeline tag (null = pending data entry) |
| `to_component` | string | TO_COMPONENT, TO_COMPONENT1 | Destination equipment/pipeline tag (null = pending data entry) |

**Note on `from_component` / `to_component`**: The Pipeline sheet contains up to 4 connectivity columns (`TO_COMPONENT`, `FROM_COMPONENT`, `TO_COMPONENT1`, `FROM_COMPONENT1`). All are currently null in the datadrop. The loader must handle multi-value connectivity by creating one `CONNECTS_TO` edge per non-null value.

### A2.12 `specialist_equipment` — Specialty Equipment Properties *(Equipment sheet only)*

Equipment columns not covered by `rotating_equipment` that are specific to UV treatment, filtration, and conveyor equipment types.

| Property | Type | Source Column(s) | Description |
| :------- | :--- | :--------------- | :---------- |
| `aperture_size` | string | APERTURE SIZE | Screen/filter aperture size |
| `diaphragm_material` | string | DIAPHRM_MTRL | Diaphragm material |
| `lineshaft_type` | string | LINSHFT | Lineshaft type |
| `uv_lamp_type` | string | UV_LAMP_TYPE | UV lamp type (UV treatment equipment) |
| `removal_dosage` | number | REMOVAL_DOSAGE | UV/chemical removal dosage |
| `flux` | number | FLUX | UV flux value |
| `submergence_min` | number | SUBMERGENCE - MIN | Minimum submergence depth (m) — also in `rotating_equipment` for pumps |
| `manufacturer_fax` | string | MANUFACTURER FAX | Manufacturer fax number *(present across Equipment, Motor, CONTROLVALVE, MANUALVALVE)* |

**Note**: `manufacturer_fax` is present across 4 sheets but was omitted from the `manufacturer` fragment as it is rarely populated. It is captured here as an optional field. The column normalization map should include it universally.

### A2.13 `motor_control` — Motor Electrical & Control *(Motor sheet only)*

Motor-specific electrical and MCC control fields not covered by `rotating_equipment`.

| Property | Type | Source Column(s) | Description |
| :------- | :--- | :--------------- | :---------- |
| `starter_type` | string | M_STARTER_TYPE | Motor starter type (DOL, VFD, Soft Start, etc.) |
| `mcc_fed_from` | string | MCC FED FROM | MCC panel this motor is fed from |
| `equipment_number` | string | EQUIPMENT NUMBER | Associated mechanical equipment tag number |

---

## A3. Type Composition Map

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
- **13 fragments total** (was 11 — added `specialist_equipment` A2.12 and `motor_control` A2.13)

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

### A4.1 Concrete Example — Unit 003 / Service G2D Subgraph

The following is a **real-data example** drawn from the WSD11 datadrop showing three assets in Unit 003 / Service G2D (G2D Booster Pump system) all referenced on the same P&ID drawing.

#### Current State (as-populated in datadrop)

```
┌──────────────────────────────────────────────────────────────────┐
│                    131242-WSD11-DR-P-6200.dgn                     │
│                          (P&ID Drawing)                           │
└──────────────────────────────────────────────────────────────────┘
        │ REFERENCED_BY_DWG               │                         │
        ▼                                 ▼                         ▼
┌──────────────────┐        ┌──────────────────┐     ┌──────────────────────┐
│   AT_EQPMP       │        │   AT_HVALVE      │     │   AT_PROCESS         │
│  WSD11-003-P-0101│        │  WSD11-003-HV-0001│    │WSD11-003-G2D-00001… │
│ G2D BOOSTER PUMP │        │  (manual valve)   │    │ 300mm SS16 pipeline  │
└──────────────────┘        └──────────────────┘     └──────────────────────┘
        │ BELONGS_TO_UNIT           │                         │
        └────────────┬──────────────┴─────────────────────────┘
                     ▼
            ┌────────────────┐      ┌────────────────┐
            │   Unit 003     │      │  Service G2D   │
            └────────────────┘      └────────────────┘
                     ▲                         ▲
                     └─────────────┬───────────┘
                                   │ BELONGS_TO_SERVICE
                                   │ (all three assets)
```

**Key observations from current data:**
- P&ID file references are **universally populated** (3,368/3,368 pipelines; 336/337 equipment; 1,838/1,838 manual valves) — the `REFERENCED_BY_DWG` edges are immediately available
- Unit and Service fields are also fully populated — `BELONGS_TO_UNIT` and `BELONGS_TO_SERVICE` edges are ready
- `FROM_COMPONENT` / `TO_COMPONENT` are **entirely null** (~44% of datadrop fields are pending data entry) — `CONNECTS_TO` edges are not yet available

#### Future State (when FROM/TO data is entered)

Once the `FROM_COMPONENT` / `TO_COMPONENT` fields are populated, the graph gains the physical connectivity layer:

```
┌──────────────────────────────────────────────────────────────────────┐
│                     131242-WSD11-DR-P-6200.dgn                        │
│                           (P&ID Drawing)                              │
└──────────────────────────────────────────────────────────────────────┘
        │ REFERENCED_BY_DWG                       │
        ▼                                         ▼
┌─────────────────────┐             ┌─────────────────────────┐
│    AT_EQPMP         │             │    AT_HVALVE             │
│ WSD11-003-P-0101   │◄────────────│ WSD11-003-HV-0001       │
│ G2D BOOSTER PUMP A │  CONNECTS_TO│ (manual isolation valve) │
└─────────────────────┘   (from)   └─────────────────────────┘
        ▲                                        │
        │                                CONNECTS_TO (from)
        │                                        │
        │                              ┌─────────▼──────────────┐
        │                              │    AT_CVALVE            │
        │                              │ WSD11-003-FCV-0101    │
        │                              │ (control valve, unit   │
        │                              │  003/G2D, actuator     │
        │                              │  ref: ACT-003-001)     │
        │                              └─────────┬──────────────┘
        │                                        │
        │                                        ▼
        │                              ┌─────────────────────────┐
        │                              │    AT_PROCESS           │
        │                              │ WSD11-003-G2D-00001…  │
        │                              │ 300mm SS16 pipeline    │
        └──────────────────────────────┤   CONNECTS_TO          │
                  CONNECTS_TO (from)   │   → WSD11-003-P-0101   │
                                       │   → WSD11-003-HV-0001  │
                                       │   → WSD11-003-FCV-0101 │
                                       └─────────────────────────┘
```

**Neo4j query example (future state):**
```cypher
// Find all components connected to a given pipeline
MATCH (p:AT_PROCESS {tag_no: 'WSD11-003-G2D-00001-300-SS16'})
      -[:CONNECTS_TO]->(asset)
RETURN p.tag_no, asset.tag_no, asset.tag_type, asset.description

// Trace all assets on a P&ID drawing
MATCH (dwg:Document {filename: '131242-WSD11-DR-P-6200.dgn'})
      <-[:REFERENCED_BY_DWG]-(asset)
OPTIONAL MATCH (asset)-[:CONNECTS_TO]->(connected)
RETURN asset.tag_no, asset.tag_type, connected.tag_no

// Navigation: pipeline → connected assets → their P&ID
MATCH (p:AT_PROCESS {tag_no: 'WSD11-003-G2D-00001-300-SS16'})
      -[:CONNECTS_TO]->(asset)
      -[:REFERENCED_BY_DWG]->(dwg)
RETURN p.tag_no, asset.tag_no, dwg.filename
```

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
   - Indexes on `keytag`, `tag_no`, `pipeline_tag_number`

---

## A6. Schema File Structure

```
eks/config/
├── eks_asset_base_schema.json       # Fragment definitions (A2.1–A2.13)
├── eks_asset_setup_schema.json       # asset_type_registry declaration + column normalization rules
└── eks_asset_config.json             # Project-specific: type→fragment map, datadrop source path, column mappings
```

This follows the same base/setup/config inheritance pattern as the main EKS schema (Section 7c), ensuring SSOT compliance per agent_rule §4.

**Fragment count**: 13 total (A2.1 `item_core`, A2.2 `process_conditions`, A2.3 `manufacturer`, A2.4 `asset_lifecycle`, A2.5 `control_system`, A2.6 `piping_connection`, A2.7 `valve_internals`, A2.8 `actuator`, A2.9 `rotating_equipment`, A2.10 `instrumentation`, A2.11 `pipeline_route`, A2.12 `specialist_equipment` *(new)*, A2.13 `motor_control` *(new)*)

---

## A7. How to Add a New Plant Asset Type

The schema is designed for **zero-code extensibility** (R39). Adding a new plant asset type — or a new conditional sub-type — requires only config and schema file edits. No Python code changes.

There are three scenarios depending on what the new type needs.

---

### Scenario 1 — New type using existing fragments only

**When**: The new asset type's properties are fully covered by the 13 existing fragments.

**Steps** (config only — 1 file):

1. Open `eks/config/eks_asset_config.json`
2. Add a new entry under `asset_type_registry`:

```json
"AT_NEWTYPE": {
    "label": "My New Asset Type",
    "fragments": ["item_core", "process_conditions", "manufacturer", "asset_lifecycle"]
}
```

3. Add column normalization entries if the new type comes from a new sheet or uses different column names:

```json
"NewSheet": {
    "MY_PID_COL": "p_and_id_file",
    "MY_UNIT_COL": "unit"
}
```

That's it. The Phase 3 loader reads the registry at runtime and composes the node automatically.

---

### Scenario 2 — New type with a conditional fragment

**When**: The new type shares a base set of fragments, but certain rows within it need additional properties depending on a field value (e.g. `device_type_code`, `tag_type`, `service`).

**Steps** (config only — 1 file):

1. Open `eks/config/eks_asset_config.json`
2. Add the entry with a `conditional_fragments` array:

```json
"AT_NEWTYPE": {
    "label": "My New Asset Type",
    "fragments": ["item_core", "process_conditions", "manufacturer", "asset_lifecycle"],
    "conditional_fragments": [
        { "fragment": "specialist_equipment", "when": "device_type_code", "in": ["UV", "FILT"] }
    ]
}
```

The loader evaluates `when`/`in` against the row's field value at ingest time. If the condition matches, the fragment's properties are merged into the node. No code change needed.

---

### Scenario 3 — New type requiring a new property group (new fragment)

**When**: The new asset type has properties not covered by any existing fragment — e.g. a heat recovery unit with heat transfer coefficient and fouling factor fields.

**Steps** (3 files — schema + config):

**Step 1** — Define the new fragment in `eks/config/eks_asset_base_schema.json` under `definitions`:

```json
"heat_transfer": {
    "type": "object",
    "description": "Heat exchanger thermal performance data",
    "properties": {
        "heat_transfer_coefficient": { "type": "number" },
        "fouling_factor":            { "type": "number" },
        "heat_duty_kw":              { "type": "number" },
        "log_mean_temp_diff":        { "type": "number" }
    },
    "additionalProperties": false
}
```

**Step 2** — Register the new fragment name in `eks/config/eks_asset_setup_schema.json` by adding it to the `fragment_name` enum:

```json
"enum": [
    "item_core", "process_conditions", "manufacturer", "asset_lifecycle",
    "control_system", "piping_connection", "valve_internals", "actuator",
    "rotating_equipment", "instrumentation", "pipeline_route",
    "specialist_equipment", "motor_control",
    "heat_transfer"
]
```

**Step 3** — Add the new type to `eks/config/eks_asset_config.json` using the new fragment:

```json
"AT_HXUNIT": {
    "label": "Heat Recovery Unit",
    "fragments": ["item_core", "process_conditions", "manufacturer", "asset_lifecycle", "heat_transfer"]
}
```

Add column normalization entries for the new fragment's source columns if needed.

No loader code changes. The `base_asset_loader.py` dynamically resolves all fragment properties from config at runtime.

---

### Decision Guide

| What you need | Files to edit | Code changes? |
| :------------ | :------------ | :------------ |
| New tag_type, all properties exist in current 13 fragments | `eks_asset_config.json` only | ❌ None |
| New tag_type with conditional property group | `eks_asset_config.json` only | ❌ None |
| New tag_type with entirely new property group | `eks_asset_base_schema.json` + `eks_asset_setup_schema.json` + `eks_asset_config.json` | ❌ None |
| New Excel sheet as data source | `eks_asset_config.json` (column normalization) + new loader file | ✅ One new file |

---

### Validation after any schema change

Run the validation script to confirm all fragment names are consistent across the 3 files and the config validates against the setup schema:

```bash
python eks/test/validate_asset_schema.py
```

Expected output:
```
Fragment names in config not in base: NONE — OK
Schema validation: PASS
```

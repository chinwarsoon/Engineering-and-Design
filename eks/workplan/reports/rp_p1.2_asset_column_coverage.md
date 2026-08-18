# Asset Column-Coverage Pre-check (T1.311 / I020)

- Workbook: `C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\data\twrp\datadrop\Datadrop Summary.xlsx`
- Config map source: `column_normalization` + native item_core identity map
- Sheets analysed: 7

| Sheet | Config-mapped | Native-mapped | Unmapped |
|-------|--------------:|--------------:|---------:|
| CONTROLVALVE | 58 | 11 | 43 |
| Equipment | 39 | 10 | 32 |
| Inline Component | 23 | 10 | 23 |
| Instrument | 50 | 8 | 29 |
| MANUALVALVE | 28 | 10 | 26 |
| Motor | 46 | 11 | 16 |
| Pipeline | 9 | 6 | 18 |

## CONTROLVALVE

| Datadrop column | Canonical field |
|-----------------|-----------------|
| ACE ASSET CLASS | `ace_asset_class` |
| ACE ASSET CLASS - ACTUATOR | `actuator_ace_asset_class` |
| ACE ASSET NUMBER | `ace_asset_number` |
| ACE ASSET NUMBER - ACTUATOR | `actuator_ace_asset_number` |
| ACE ASSET SUB NUMBER | `ace_asset_sub_number` |
| ACE ASSET SUB NUMBER - ACTUATOR | `actuator_ace_asset_sub_number` |
| ACE CATEGORY | `ace_category` |
| ACE CATEGORY - ACTUATOR | `actuator_ace_category` |
| ACTUATOR DISPLAY LABEL | `actuator_display_label` |
| A_ACT_DISPLAY | `actuator_internal_type` |
| BRAND - ACTUATOR | `actuator_brand` |
| COST CENTER | `cost_center` |
| COST CENTER - ACTUATOR | `actuator_cost_center` |
| DATE OF COMMISSION | `date_of_commission` |
| DATE OF COMMISSION - ACTUATOR | `actuator_date_of_commission` |
| EST REPLACEMENT DATE | `est_replacement_date` |
| EST REPLACEMENT DATE - ACTUATOR | `actuator_est_replacement_date` |
| FAIL MODE DISPLAY LABEL | `fail_mode` |
| GENERIC EQUIPMENT TYPE | `generic_equipment_type` |
| GENERIC EQUIPMENT TYPE - ACTUATOR | `actuator_generic_equipment_type` |
| IINT1 | `valve_internal_type` |
| LIFE SPAN | `life_span` |
| LIFE SPAN - ACTUATOR | `actuator_life_span` |
| LINING MATERIAL | `lining_material` |
| LOT NUMBER - ACTUATOR | `actuator_lot_number` |
| MANUFACTURE DATE - ACTUATOR | `actuator_manufacture_date` |
| MANUFACTURER 3D MODEL FILE NAME | `model_3d_file` |
| MANUFACTURER 3D MODEL FILE NAME - ACTUATOR | `actuator_model_3d_file` |
| MANUFACTURER EMAIL - ACTUATOR | `actuator_manufacturer_email` |
| MANUFACTURER FAX | `manufacturer_fax` |
| MANUFACTURER FAX - ACTUATOR | `actuator_manufacturer_fax` |
| MANUFACTURER LOCATION - ACTUATOR | `actuator_manufacturer_location` |
| MANUFACTURER NAME - ACTUATOR | `actuator_manufacturer_name` |
| MANUFACTURER PHONE - ACTUATOR | `actuator_manufacturer_phone` |
| MANUFACTURER WEBPAGE - ACTUATOR | `actuator_manufacturer_website` |
| MODEL NUMBER - ACTUATOR | `actuator_model` |
| NAME | `description` |
| P&ID FILENAME | `p_and_id_file` |
| PIPE SIZE - NOMINAL (MM) | `pipe_size_nominal_mm` |
| PRODUCT CERTIFICATION | `product_certification` |
| PRODUCT CERTIFICATION - ACTUATOR | `actuator_product_certification` |
| REPLACEMENT COST | `replacement_cost` |
| REPLACEMENT COST - ACTUATOR | `actuator_replacement_cost` |
| SERIAL NUMBER - ACTUATOR | `actuator_serial` |
| SHORT DESCR | `short_description` |
| SUPPLIER | `supplier` |
| SUPPLIER - ACTUATOR | `actuator_supplier` |
| UNIT | `unit` |
| VALVE - DUTY | `valve_duty` |
| VALVE MANUFACTURER 2D MODEL FILE NAME | `model_2d_file` |
| WARRANTY EXPIRY DATE | `warranty_expiry_date` |
| WARRANTY EXPIRY DATE - ACTUATOR | `actuator_warranty_expiry_date` |
| WARRANTY START DATE | `warranty_start_date` |
| WARRANTY START DATE - ACTUATOR | `actuator_warranty_start_date` |
| WARRANTY TERMS | `warranty_terms` |
| WARRANTY TERMS - ACTUATOR | `actuator_warranty_terms` |
| WBS ELEMENT | `wbs_element` |
| WBS ELEMENT - ACTUATOR | `actuator_wbs_element` |

Native identity mapping (not yet in `column_normalization`):

| Datadrop column | Canonical field |
|-----------------|-----------------|
| CONTRACT INFO | `contract_info` |
| DESCRIPTION | `description` |
| DEVICE TYPE CODE | `device_type_code` |
| HAZARDOUS ZONE | `hazardous_zone` |
| KEYTAG | `keytag` |
| PROJECT PREFIX | `project_prefix` |
| SERVICE | `service` |
| TAG LOOP NUMBER | `tag_loop_number` |
| TAG SUFFIX | `tag_suffix` |
| TAG_NO | `tag_no` |
| TAG_TYPE | `tag_type` |

Unmapped columns (43):

- `ACTUATOR - LOCKED ROTOR TORQUE (NM)`
- `ACTUATOR - MOTOR RATING (KW)`
- `ACTUATOR - MOTOR RPM`
- `ACTUATOR - RATED CURRENT (AMPERE)`
- `ACTUATOR - RATED FREQUENCY`
- `ACTUATOR - RATED TORQUE CURRENT (AMPERE)`
- `ACTUATOR - RATED VOLTAGE`
- `ACTUATOR - RPM`
- `ACTUATOR - STEM DIRECTION`
- `ACTUATOR - TORQUE SETTING RANGE`
- `ACTUATOR MANUFACTURER 2D MODEL FILE NAME`
- `ACTUATOR TAG NUMBER`
- `BODY MATERIAL`
- `BRAND`
- `DESIGN PRESSURE`
- `END CONDITION`
- `FLOW RATE - MAX`
- `FLOW RATE - MIN`
- `FLOW RATE - NOMINAL`
- `LCS TYPE`
- `LOT NUMBER`
- `MANUFACTURE DATE`
- `MANUFACTURER EMAIL`
- `MANUFACTURER LOCATION`
- `MANUFACTURER NAME`
- `MANUFACTURER PHONE`
- `MANUFACTURER WEBPAGE`
- `MODEL NUMBER`
- `OPERATING PRESSURE - MAX`
- `OPERATING PRESSURE - MIN`
- `OPERATING PRESSURE - NORMAL`
- `OPERATING TEMPERATURE - NORMAL`
- `PIPELINE TAG NUMBER`
- `PLC PANEL`
- `PLC PANEL LOCATION`
- `PRESSURE RATING`
- `RIO PANEL`
- `RIO PANEL LOCATION`
- `SEAT MATERIAL`
- `SERIAL NUMBER`
- `STEM MATERIAL`
- `TEST PRESSURE`
- `VALVE CLOSURE ELEMENT`

## Equipment

| Datadrop column | Canonical field |
|-----------------|-----------------|
| ACE ASSET CLASS | `ace_asset_class` |
| APERTURE SIZE | `aperture_size` |
| CONVERYOR_HUB_MATERIAL | `conveyor_hub_material` |
| DESCRIPTION | `description` |
| DIAPHRM_MTRL | `diaphragm_material` |
| DUTY STAND BY | `duty_standby` |
| ECASING_MTR | `casing_material` |
| EFFICIENCY_DESIGN_CAP | `efficiency` |
| EINS | `insulation_class` |
| EQUIPMENT MATERIAL | `casing_material` |
| FLUX | `flux` |
| GEARBOX_MATERIAL | `gearbox_material` |
| IMPELLER_WEAR_RING | `impeller_wear_ring` |
| LINSHFT | `lineshaft_type` |
| MANUFACTURER 2D MODEL FILE NAME | `model_2d_file` |
| MANUFACTURER 3D MODEL FILE NAME | `model_3d_file` |
| MANUFACTURER FAX | `manufacturer_fax` |
| MECH SEAL/GLAND PACKAGING | `seal_type` |
| PID NUMBER | `p_and_id_file` |
| PUB_ACE_ASSET_NUMBER | `ace_asset_number` |
| PUB_ACE_ASSET_SUB_NUMBER | `ace_asset_sub_number` |
| PUB_ACE_CATEGORY | `ace_category` |
| PUB_COST_CENTER | `cost_center` |
| PUB_DATE_OF_COMMISSION | `date_of_commission` |
| PUB_EST_REPLACEMENT_DATE | `est_replacement_date` |
| PUB_GENERIC_EQUIPMENT_TYPE | `generic_equipment_type` |
| PUB_LIFE_SPAN | `life_span` |
| PUB_PRODUCT_CERTIFICATION | `product_certification` |
| PUB_REPLACEMENT_COST | `replacement_cost` |
| PUB_SUPPLIER | `supplier` |
| PUB_WARRANTY_EXPIRY_DATE | `warranty_expiry_date` |
| PUB_WARRANTY_START_DATE | `warranty_start_date` |
| PUB_WARRANTY_TERMS | `warranty_terms` |
| PUB_WBS_ELEMENT | `wbs_element` |
| REMOVAL_DOSAGE | `removal_dosage` |
| SHORT DESCR | `short_description` |
| SUBMERGENCE - MIN | `submergence_min` |
| UNIT | `unit` |
| UV_LAMP_TYPE | `uv_lamp_type` |

Native identity mapping (not yet in `column_normalization`):

| Datadrop column | Canonical field |
|-----------------|-----------------|
| CONTRACT INFO | `contract_info` |
| DEVICE TYPE CODE | `device_type_code` |
| HAZARDOUS ZONE | `hazardous_zone` |
| KEYTAG | `keytag` |
| PROJECT PREFIX | `project_prefix` |
| SERVICE | `service` |
| TAG LOOP NUMBER | `tag_loop_number` |
| TAG SUFFIX | `tag_suffix` |
| TAG_NO | `tag_no` |
| TAG_TYPE | `tag_type` |

Unmapped columns (32):

- `BRAND`
- `DESIGN CAPACITY`
- `DESIGN CAPACITY UNIT`
- `DISCHARGE NOZZLE SIZE`
- `HEAD LOSS`
- `IMPELLER_MATERIAL`
- `IMPELLER_TYPE`
- `LCS TYPE`
- `LINING_MATERIAL`
- `LOT NUMBER`
- `MANUFACTURE DATE`
- `MANUFACTURER EMAIL`
- `MANUFACTURER LOCATION`
- `MANUFACTURER NAME`
- `MANUFACTURER PHONE`
- `MANUFACTURER WEBPAGE`
- `MODEL NUMBER`
- `NPSH - MIN`
- `OPERATING PRESSURE - MAX`
- `OPERATING PRESSURE - MIN`
- `OPERATING PRESSURE - NORMAL`
- `OPERATING TEMPERATURE - NORMAL`
- `PLC PANEL`
- `PLC PANEL LOCATION`
- `RIO PANEL`
- `RIO PANEL LOCATION`
- `ROTOR_MATERIAL`
- `RPM`
- `SEAL_TYPE_MECH`
- `SERIAL NUMBER`
- `STATOR_MATERIAL`
- `SUCTION NOZZLE SIZE`

## Inline Component

| Datadrop column | Canonical field |
|-----------------|-----------------|
| ACE ASSET CLASS | `ace_asset_class` |
| ACE ASSET NUMBER | `ace_asset_number` |
| ACE ASSET SUB NUMBER | `ace_asset_sub_number` |
| ACE CATEGORY | `ace_category` |
| COST CENTER | `cost_center` |
| DATE OF COMMISSION | `date_of_commission` |
| DESCRIPTION | `description` |
| EST REPLACEMENT DATE | `est_replacement_date` |
| GENERIC EQUIPMENT TYPE | `generic_equipment_type` |
| LIFE SPAN | `life_span` |
| MANUFACTURER 2D MODEL FILE NAME | `model_2d_file` |
| MANUFACTURER 3D MODEL FILE NAME | `model_3d_file` |
| P&ID FILE | `p_and_id_file` |
| PIPE SIZE - NOMINAL (MM) | `pipe_size_nominal_mm` |
| PRODUCT CERTIFICATION | `product_certification` |
| REPLACEMENT COST | `replacement_cost` |
| SHORT DESCR | `short_description` |
| SUPPLIER | `supplier` |
| UNIT | `unit` |
| WARRANTY EXPIRY DATE | `warranty_expiry_date` |
| WARRANTY START DATE | `warranty_start_date` |
| WARRANTY TERMS | `warranty_terms` |
| WBS ELEMENT | `wbs_element` |

Native identity mapping (not yet in `column_normalization`):

| Datadrop column | Canonical field |
|-----------------|-----------------|
| CONTRACT INFO | `contract_info` |
| DEVICE TYPE CODE | `device_type_code` |
| HAZARDOUS ZONE | `hazardous_zone` |
| KEYTAG | `keytag` |
| PROJECT PREFIX | `project_prefix` |
| SERVICE | `service` |
| TAG LOOP NUMBER | `tag_loop_number` |
| TAG SUFFIX | `tag_suffix` |
| TAG_NO | `tag_no` |
| TAG_TYPE | `tag_type` |

Unmapped columns (23):

- `BRAND`
- `DESIGN PRESSURE`
- `FLOW RATE - MAX`
- `FLOW RATE - MIN`
- `FLOW RATE - NOMINAL`
- `LOT NUMBER`
- `MANUFACTURE DATE`
- `MANUFACTURER EMAIL`
- `MANUFACTURER FAX`
- `MANUFACTURER LOCATION`
- `MANUFACTURER NAME`
- `MANUFACTURER PHONE`
- `MANUFACTURER WEBPAGE`
- `MODEL NUMBER`
- `OPERATING PRESSURE - MAX`
- `OPERATING PRESSURE - MIN`
- `OPERATING PRESSURE - NORMAL`
- `OPERATING TEMPERATURE - NORMAL`
- `PIPELINE TAG NUMBER`
- `PRESSURE RATING`
- `SERIAL NUMBER`
- `TAG NAME`
- `TEST PRESSURE`

## Instrument

| Datadrop column | Canonical field |
|-----------------|-----------------|
| ALARM LIMIT H | `alarm_limit_h` |
| ALARM LIMIT HH | `alarm_limit_hh` |
| ALARM LIMIT L | `alarm_limit_l` |
| ALARM LIMIT LL | `alarm_limit_ll` |
| CONTTACT INFO | `contract_info` |
| DESCRIPTION | `description` |
| DOC_FNAME | `p_and_id_file` |
| HIHI_ALARM_TP | `alarm_limit_hh` |
| HI_ALARM_TP | `alarm_limit_h` |
| HOUSING MATERIAL | `housing_material` |
| INGRESS PROTECTION | `ingress_protection` |
| INSTRUMENT FUNCTION_CONTACT TYPE | `instrument_function` |
| LIGHTNING ARRESTOR | `lightning_arrestor` |
| LINING MATERIAL | `lining_material` |
| LOLO_ALARM_TP | `alarm_limit_ll` |
| LO_ALARM_TP | `alarm_limit_l` |
| MEASUREMENT/SAMPLE POINT | `measurement_sample_point` |
| OPERATING RANGE | `operating_range` |
| OUTPUT SIGNAL 2 | `output_signal_2` |
| PIPE SIZE - NOMINAL | `pipe_size_nominal_mm` |
| PUB_ACE_ASSET_NUMBER | `ace_asset_number` |
| PUB_ACE_ASSET_SUB_NUMBER | `ace_asset_sub_number` |
| PUB_ACE_CATEGORY | `ace_category` |
| PUB_AMS_CATEGORY | `ams_category` |
| PUB_BRAND | `brand` |
| PUB_COST_CENTER | `cost_center` |
| PUB_DATE_OF_COMMISSION | `date_of_commission` |
| PUB_EST_REPLACEMENT_DATE | `est_replacement_date` |
| PUB_GENERIC_EQUIPMENT_TYPE | `generic_equipment_type` |
| PUB_LIFE_SPAN | `life_span` |
| PUB_LOT_NUMBER | `lot_number` |
| PUB_MANUFACTURER_EMAIL | `manufacturer_email` |
| PUB_MANUFACTURER_FAX | `manufacturer_fax` |
| PUB_MANUFACTURER_LOCATION | `manufacturer_location` |
| PUB_MANUFACTURER_NAME | `manufacturer_name` |
| PUB_MANUFACTURER_PHONE | `manufacturer_phone` |
| PUB_MANUFACTURER_WEBPAGE | `manufacturer_website` |
| PUB_MANUFACTURE_DATE | `manufacture_date` |
| PUB_MODEL_NUMBER | `model_number` |
| PUB_PRODUCT_CERTIFICATION | `product_certification` |
| PUB_REPLACEMENT_COST | `replacement_cost` |
| PUB_SERIAL_NUMBER | `serial_number` |
| PUB_SUPPLIER | `supplier` |
| PUB_WARRANTY_EXPIRY_DATE | `warranty_expiry_date` |
| PUB_WARRANTY_START_DATE | `warranty_start_date` |
| PUB_WARRANTY_TERMS | `warranty_terms` |
| PUB_WBS_ELEMENT | `wbs_element` |
| SHORT DESCR | `short_description` |
| THERMOWELL_TEMPERATURE SENSOR ONLY | `thermowell` |
| UNIT_PROCESS_NO | `unit` |

Native identity mapping (not yet in `column_normalization`):

| Datadrop column | Canonical field |
|-----------------|-----------------|
| HAZARDOUS ZONE | `hazardous_zone` |
| KEYTAG | `keytag` |
| PROJECT PREFIX | `project_prefix` |
| SERVICE | `service` |
| TAG LOOP NUMBER | `tag_loop_number` |
| TAG SUFFIX | `tag_suffix` |
| TAG_NO | `tag_no` |
| TAG_TYPE | `tag_type` |

Unmapped columns (29):

- `ACCURACY`
- `CALIBRATION RANGE`
- `DESIGN PRESSURE`
- `FLOW RATE - MAX`
- `FLOW RATE - MIN`
- `FLOW RATE - NOMINAL`
- `ISA INSTRUMENT ID`
- `LCS TYPE`
- `MEASUREMENT PRINCIPLE`
- `OPERATING PRESSURE - MAX`
- `OPERATING PRESSURE - MIN`
- `OPERATING PRESSURE - NORMAL`
- `OPERATING TEMPERATURE - NORMAL`
- `OUTPUT SIGNAL`
- `PIPELINE TAG NUMBER`
- `PLC PANEL`
- `PLC PANEL LOCATION`
- `RIO PANEL`
- `RIO PANEL LOCATION`
- `SENSOR IP RATING`
- `SENSOR MATERIAL`
- `SENSOR MODEL`
- `SENSOR RANGE`
- `SENSOR WETTED PARTS MATERIAL`
- `SET POINT`
- `SUPPLY VOLTAGE`
- `TEST PRESSURE`
- `TUBE MATERIAL`
- `TUBE SIZE`

## MANUALVALVE

| Datadrop column | Canonical field |
|-----------------|-----------------|
| ACE ASSET CLASS | `ace_asset_class` |
| ACE ASSET NUMBER | `ace_asset_number` |
| ACE ASSET SUB NUMBER | `ace_asset_sub_number` |
| ACE CATEGORY | `ace_category` |
| COST CENTER | `cost_center` |
| DATE OF COMMISSION | `date_of_commission` |
| DESCRIPTION | `description` |
| DOC_FNAME | `p_and_id_file` |
| EST REPLACEMENT DATE | `est_replacement_date` |
| GENERIC EQUIPMENT TYPE | `generic_equipment_type` |
| LIFE SPAN | `life_span` |
| LINING MATERIAL | `lining_material` |
| LOCKED POSITION | `locked_position` |
| MANUFACTURER 2D MODEL FILE NAME | `model_2d_file` |
| MANUFACTURER 3D MODEL FILE NAME | `model_3d_file` |
| MANUFACTURER FAX | `manufacturer_fax` |
| PIPE SIZE - NOMINAL (MM) | `pipe_size_nominal_mm` |
| PRODUCT CERTIFICATION | `product_certification` |
| REPLACEMENT COST | `replacement_cost` |
| SHORT DESCR | `short_description` |
| SUPPLIER | `supplier` |
| UNIT | `unit` |
| VALVE - DUTY | `valve_duty` |
| VINT1 | `valve_internal_type` |
| WARRANTY EXPIRY DATE | `warranty_expiry_date` |
| WARRANTY START DATE | `warranty_start_date` |
| WARRANTY TERMS | `warranty_terms` |
| WBS ELEMENT | `wbs_element` |

Native identity mapping (not yet in `column_normalization`):

| Datadrop column | Canonical field |
|-----------------|-----------------|
| CONTRACT INFO | `contract_info` |
| DEVICE TYPE CODE | `device_type_code` |
| HAZARDOUS ZONE | `hazardous_zone` |
| KEYTAG | `keytag` |
| PROJECT PREFIX | `project_prefix` |
| SERVICE | `service` |
| TAG LOOP NUMBER | `tag_loop_number` |
| TAG SUFFIX | `tag_suffix` |
| TAG_NO | `tag_no` |
| TAG_TYPE | `tag_type` |

Unmapped columns (26):

- `BODY MATERIAL`
- `BRAND`
- `DESIGN PRESSURE`
- `END CONDITION`
- `FLOW RATE - MAX`
- `FLOW RATE - MIN`
- `FLOW RATE - NOMINAL`
- `LOT NUMBER`
- `MANUFACTURE DATE`
- `MANUFACTURER EMAIL`
- `MANUFACTURER LOCATION`
- `MANUFACTURER NAME`
- `MANUFACTURER PHONE`
- `MANUFACTURER WEBPAGE`
- `MODEL NUMBER`
- `OPERATING PRESSURE - MAX`
- `OPERATING PRESSURE - MIN`
- `OPERATING PRESSURE - NORMAL`
- `OPERATING TEMPERATURE - NORMAL`
- `PIPELINE TAG NUMBER`
- `PRESSURE RATING`
- `SEAT MATERIAL`
- `SERIAL NUMBER`
- `STEM MATERIAL`
- `TEST PRESSURE`
- `VALVE CLOSURE ELEMENT`

## Motor

| Datadrop column | Canonical field |
|-----------------|-----------------|
| ACE ASSET CLASS | `ace_asset_class` |
| ACE ASSET NUMBER | `ace_asset_number` |
| ACE ASSET SUB NUMBER | `ace_asset_sub_number` |
| ACE CATEGORY | `ace_category` |
| ACTUATOR - LOCKED ROTOR TORQUE | `actuator_locked_rotor_torque` |
| ACTUATOR - MOTOR RATING | `motor_rating` |
| ACTUATOR - MOTOR RPM | `actuator_motor_rpm` |
| ACTUATOR - RATED CURRENT | `actuator_rated_current` |
| ACTUATOR - RATED FREQUENCY | `actuator_rated_frequency` |
| ACTUATOR - RATED TORQUE CURRENT | `actuator_rated_torque_current` |
| ACTUATOR - RATED VOLTAGE | `actuator_rated_voltage` |
| ACTUATOR - RPM | `actuator_rpm` |
| ACTUATOR - STEM DIRECTION | `actuator_stem_direction` |
| ACTUATOR - TORQUE SETTING RANGE | `actuator_torque_range` |
| COST CENTER | `cost_center` |
| DATE OF COMMISSION | `date_of_commission` |
| EQUIPMENT NUMBER | `equipment_number` |
| EST REPLACEMENT DATE | `est_replacement_date` |
| GENERIC EQUIPMENT TYPE | `generic_equipment_type` |
| LIFE SPAN | `life_span` |
| MANUFACTURER 2D MODEL FILE NAME | `model_2d_file` |
| MANUFACTURER 3D MODEL FILE NAME | `model_3d_file` |
| MANUFACTURER FAX | `manufacturer_fax` |
| MCC FED FROM | `mcc_fed_from` |
| MOTOR - HERTZ | `frequency` |
| MOTOR - LOCKED ROTOR TORQUE | `motor_locked_rotor_torque` |
| MOTOR - PHASE | `phase` |
| MOTOR - RATED CURRENT | `motor_rated_current` |
| MOTOR - RATED TORQUE CURRENT | `motor_rated_torque_current` |
| MOTOR - RPM | `rpm` |
| MOTOR - TORQUE SETTING RANGE | `motor_torque_range` |
| MOTOR - VOLTAGE | `voltage` |
| M_SPEED_CLASS | `motor_speed_class` |
| M_STARTER_TYPE | `starter_type` |
| NAME | `description` |
| P&ID DRAWING | `p_and_id_file` |
| PRODUCT CERTIFICATION | `product_certification` |
| RATED MOTOR | `motor_rating` |
| REPLACEMENT COST | `replacement_cost` |
| SHORT DESCR | `short_description` |
| SUPPLIER | `supplier` |
| UNIT | `unit` |
| WARRANTY EXPIRY DATE | `warranty_expiry_date` |
| WARRANTY START DATE | `warranty_start_date` |
| WARRANTY TERMS | `warranty_terms` |
| WBS ELEMENT | `wbs_element` |

Native identity mapping (not yet in `column_normalization`):

| Datadrop column | Canonical field |
|-----------------|-----------------|
| CONTRACT INFO | `contract_info` |
| DESCRIPTION | `description` |
| DEVICE TYPE CODE | `device_type_code` |
| HAZARDOUS ZONE | `hazardous_zone` |
| KEYTAG | `keytag` |
| PROJECT PREFIX | `project_prefix` |
| SERVICE | `service` |
| TAG LOOP NUMBER | `tag_loop_number` |
| TAG SUFFIX | `tag_suffix` |
| TAG_NO | `tag_no` |
| TAG_TYPE | `tag_type` |

Unmapped columns (16):

- `BRAND`
- `LCS TYPE`
- `LOT NUMBER`
- `MANUFACTURE DATE`
- `MANUFACTURER EMAIL`
- `MANUFACTURER LOCATION`
- `MANUFACTURER NAME`
- `MANUFACTURER PHONE`
- `MANUFACTURER WEBPAGE`
- `MODEL NUMBER`
- `OPERATING TEMPERATURE - NORMAL`
- `PLC PANEL`
- `PLC PANEL LOCATION`
- `RIO PANEL`
- `RIO PANEL LOCATION`
- `SERIAL NUMBER`

## Pipeline

| Datadrop column | Canonical field |
|-----------------|-----------------|
| DESCRIPTION | `description` |
| DESIGN SIZE - NOMINAL (MM) | `pipe_size_nominal_mm` |
| DOC_FNAME | `p_and_id_file` |
| FROM_COMPONENT | `from_component` |
| FROM_COMPONENT1 | `from_component` |
| LINING MATERIAL | `lining_material` |
| TO_COMPONENT | `to_component` |
| TO_COMPONENT1 | `to_component` |
| UNIT | `unit` |

Native identity mapping (not yet in `column_normalization`):

| Datadrop column | Canonical field |
|-----------------|-----------------|
| KEYTAG | `keytag` |
| PROJECT PREFIX | `project_prefix` |
| SERVICE | `service` |
| TAG SUFFIX | `tag_suffix` |
| TAG_NO | `tag_no` |
| TAG_TYPE | `tag_type` |

Unmapped columns (18):

- `DESIGN PRESSURE`
- `DESIGN SPECIFICATION`
- `FLOW RATE - MAX`
- `FLOW RATE - MIN`
- `FLOW RATE - NOMINAL`
- `INSULATION MATERIAL`
- `INSULATION THICKNESS`
- `NUMBER`
- `OPERATING PRESSURE - MAX`
- `OPERATING PRESSURE - MIN`
- `OPERATING PRESSURE - NORMAL`
- `OPERATING TEMPERATURE - NORMAL`
- `OUTSIDE DIAMETER`
- `PIPE MATERIAL`
- `PRESSURE RATING`
- `PROCESS_USER_1`
- `TEST PRESSURE`
- `WALL THICKNESS`

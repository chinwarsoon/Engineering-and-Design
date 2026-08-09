# Appendix B.1 — Cross-Relationship Chart (Complete)

> **Parent:** [Appendix B — Document Registry](../appendix_b_document_registry.md)
> **Sibling:** [Appendix B.2 — DB Table Design](../appendix_b.2_db_table_design.md)

| Revision | Date | Author | Summary |
|:---------|:-----|:-------|:--------|
| 1.0 | 2026-08-09 | AI Assistant | Initial: entity relationship chart (10 layers) |
| 1.1 | 2026-08-09 | AI Assistant | Merged DB table relationship map, FK closure paths, and cross-document gap analysis |

```
================================================================================
                    EKS COMPLETE CROSS-RELATIONSHIP CHART
                              v1.1 / 2026-08-09
================================================================================
```


## PART I — DEFINITION ENTITY RELATIONSHIPS

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           1. CLASSIFICATION LAYER                             │
│                          (eks_document_type_schema.json)                      │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                    DOCUMENT CLASSES (8)                              │   │
│   │   Drawing │ Specification │ Datasheet │ Calculation │ Manual         │   │
│   │   Register │ Report │ Procedure                                     │   │
│   │                                                                     │   │
│   │   Each has: structural_profile, extraction_profile_ref,             │   │
│   │             ontology_class, common_rules                            │   │
│   └──────┬──────────────┬──────────────┬──────────────┬─────────────────┘   │
│          │              │              │              │                      │
│          ▼              ▼              ▼              ▼                      │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                    DOCUMENT TYPES (28)                               │   │
│   │   PID_DRAWING, PFD, PLOT_PLAN, GA_DRAWING, ISOMETRIC, LOOP_DRAWING, │   │
│   │   SLD, WIRING_DIAGRAM, CAUSE_EFFECT, PROCESS_SPEC, EQUIPMENT_SPEC,   │   │
│   │   MATERIAL_SPEC, INSTRUMENT_SPEC, ELECTRICAL_SPEC, CIVIL_SPEC,       │   │
│   │   PUMP_DATASHEET, VALVE_DATASHEET, INSTRUMENT_DATASHEET,             │   │
│   │   HEAT_EXCHANGER_DATASHEET, COMPRESSOR_DATASHEET, CALCULATION,       │   │
│   │   VENDOR_MANUAL, OPERATION_MANUAL, LINE_LIST, EQUIPMENT_LIST,        │   │
│   │   INSTRUMENT_INDEX, REPORT, PROCEDURE                                │   │
│   │                                                                     │   │
│   │   Each has: class_id ──► Document Class                             │   │
│   │             family_id ──► Document Family (nullable)                 │   │
│   │             structural_profile (inherits + overrides class)          │   │
│   └──────┬──────────────────────────────────────────────────────────────┘   │
│          │  family_id (22 of 28 = null)                                     │
│          ▼                                                                  │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                    DOCUMENT FAMILIES (4)                             │   │
│   │   Process Drawing │ Instrument Drawing │ Electrical Drawing          │   │
│   │   Mechanical Drawing (0 members — Phase 3 placeholder)               │   │
│   │                                                                     │   │
│   │   Each has: discipline (Process / Instrumentation / Electrical /     │   │
│   │             Mechanical)                                             │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```
```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      2. PROJECT BINDING LAYER                                │
│                  (eks_document_type_schema.json §project_document_types)      │
│                                                                              │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │  PROJECT 131101 (8 local codes)         PROJECT 131242 (7 codes)     │  │
│   │                                                                      │  │
│   │  local_code ──► class_id ──► template ──► format_category            │  │
│   │  DWG  → Drawing   → twrp_drawing    → print (pdf)                    │  │
│   │  SPC  → Spec      → twrp_spec_c     → print (pdf)                    │  │
│   │  DS   → Datasheet → twrp_datasheet_e→ print (pdf)                    │  │
│   │  MAN  → Manual    → twrp_manual_d   → print (pdf)                    │  │
│   │  RPT  → Report    → twrp_report_e   → print (pdf)                    │  │
│   │  CAD  → Drawing   → twrp_drawing    → native (dwg)                   │  │
│   │  ...                                                                │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```
```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      3. TEMPLATE → ELEMENT LAYER                             │
│          (eks_document_type_schema.json §document_templates                   │
│           + eks_doc_config.json §element_type_registry)                      │
│                                                                              │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │                    DOCUMENT TEMPLATES (6)                             │  │
│   │                                                                      │  │
│   │  twrp_drawing     cover=A  elements=8  threshold=5                   │  │
│   │  twrp_pandid      cover=B  elements=8  threshold=5                   │  │
│   │  twrp_spec_c      cover=C  elements=0  threshold=0  (skip detection) │  │
│   │  twrp_datasheet_e cover=E  elements=3  threshold=2                   │  │
│   │  twrp_manual_d    cover=D  elements=2  threshold=2                   │  │
│   │  twrp_report_e    cover=E  elements=3  threshold=2                   │  │
│   │                                                                      │  │
│   │  Each has: expected_elements[], source_quality_score{A..F},          │  │
│   │            detection{native, print}                                  │  │
│   └──────┬───────────────────────────────────────────────────────────────┘  │
│          │  expected_elements references                                    │
│          ▼                                                                  │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │                STRUCTURAL ELEMENTS (11)                               │  │
│   │                                                                      │  │
│   │  cover_page   │ revision_table │ section       │ table               │  │
│   │  image        │ link           │ legend        │ note                │  │
│   │  title_block  │ grid           │ signature_block                     │  │
│   │                                                                      │  │
│   │  Each has: source_method (regex|table|heuristic),                    │  │
│   │            expected_by_cover_types[],                                │  │
│   │            phase_2_use, phase_3_use                                  │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│   Detection chain:                                                           │
│   Template.expected_elements ──► StructureDetector.detect() gate             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  For each element in expected_elements:                             │   │
│   │    cover_page    → regex  (COVER_PAGE_PATTERNS)                      │   │
│   │    revision_table→ table  (REVISION_ROW_PATTERN)                     │   │
│   │    section       → regex  (SECTION_PATTERN)                          │   │
│   │    link          → regex  (LINK_PATTERN)          conf=0.9           │   │
│   │    note          → heuristic (keyword)            conf=0.7           │   │
│   │    title_block   → regex  (TITLE_BLOCK_PATTERN)                      │   │
│   │    grid          → regex  (GRID_PATTERN)                             │   │
│   │    signature_block→regex (SIGNATURE_PATTERN)                         │   │
│   │  Detected count >= threshold → structural score pass                │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```
```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      4. DATA COLUMN LAYER                                    │
│                  (eks_doc_config.json §column_processing)                     │
│                                                                              │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │  PHASE A (9 cols)                    PHASE B (33 cols)               │  │
│   │  ─────────────────                   ─────────────────               │  │
│   │  tier1: document_number    (1)       tier1: asset_tags         (1)   │  │
│   │         project_number     (2)              embedded_sheet_count(1)  │  │
│   │         document_type      (3)       tier2: project_title,           │  │
│   │         revision           (4)              document_title,           │  │
│   │  tier2: file_type          (1)              page_count, created_by,   │  │
│   │         area               (1)              checked_by, approved_by,  │  │
│   │  tier3: discipline         (1)              originator_company,       │  │
│   │         sequence_number    (1)              total_sheets,             │  │
│   │  ─────────────────                   lifecycle_stage,revision_date,│  │
│   │  Total: 9                             project_phase,contract_package│  │
│   │  Tier1: 4                             issued_date,responsible_eng, │  │
│   │  Tier2: 2                             file_modified_at        (14)  │  │
│   │  Tier3: 2                      tier3: discipline,seq_number,         │  │
│   │  Excluded: 1 (file_path)              file_size,file_created_at,     │  │
│   │                                       embedded_title/subject/        │  │
│   │                                       created_date/modified_date/    │  │
│   │                                       creator_app/producer/          │  │
│   │                                       last_modified_by/keywords/     │  │
│   │                                       revision_number,language,      │  │
│   │                                       references_documents,          │  │
│   │                                       vendor_name,                   │  │
│   │                                       revision_description    (13)   │  │
│   │                                excluded: file_hash,department,       │  │
│   │                                         status,security_class,       │  │
│   │                                         verified_by           (5)    │  │
│   │  ─────────────────                   ─────────────────               │  │
│   │                                       Total: 33                      │  │
│   │  GRAND TOTAL: 42 columns                                            │  │
│   │                                                                      │  │
│   │  Scoring: tier1(w=2.0), tier2(w=1.0), tier3(w=0.5), excluded(w=0)  │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```
```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      5. HEALTH SCORING LAYER                                 │
│            (eks_doc_config.json §health_scoring + health_scorer.py)           │
│                                                                              │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │                                                                      │  │
│   │   INPUTS                        6 DIMENSIONS           OUTPUT       │  │
│   │   ──────                        ────────────           ──────        │  │
│   │                                                                      │  │
│   │   metadata{}  ──────► completeness (0.20) ───┐                       │  │
│   │   extraction  ──────► extraction   (0.20) ───┤                       │  │
│   │   elements[]  ──────► structural   (0.20) ───┤                       │  │
│   │   cover_type  ──────► source_qual  (0.15) ───┼──► health_score      │  │
│   │   xref{}      ──────► xref_qual    (0.15) ───┤    [0.0 .. 1.0]     │  │
│   │   violations  ──────► consistency  (0.10) ───┘                      │  │
│   │                                                                      │  │
│   │   Each dimension uses:                                              │  │
│   │   • column_processing tiers (tier1/2/3 × class_id filter)           │  │
│   │   • weight_tiers {tier1_critical:2.0, tier2_standard:1.0,           │  │
│   │                    tier3_optional:0.5}                              │  │
│   │   • template source_quality_score{A..F} (template-scoped)           │  │
│   │   • template expected_elements (structural gate)                    │  │
│   │                                                                      │  │
│   │   ┌─────────────────────────────────────────────────────────────┐   │  │
│   │   │  SCORE → STATUS MAPPING                                     │   │  │
│   │   │                                                             │   │  │
│   │   │  SCHEMA (5-tier, action-based):                             │   │  │
│   │   │  0.90-1.00 → success   auto_register                        │   │  │
│   │   │  0.70-0.89 → success   optional_review                      │   │  │
│   │   │  0.50-0.69 → partial   flag_review                          │   │  │
│   │   │  0.20-0.49 → partial   mandatory_review                     │   │  │
│   │   │  0.00-0.19 → failed    manual_entry                         │   │  │
│   │   │                                                             │   │  │
│   │   │  CODE (3-level, status-based) — coarser for Phase 1:        │   │  │
│   │   │  >=0.70  → success                                          │   │  │
│   │   │  >=0.20  → partial                                          │   │  │
│   │   │  <0.20   → failed                                           │   │  │
│   │   │                                                             │   │  │
│   │   │  ⚠ 5-tier action routing is Phase 3 deferred               │   │  │
│   │   └─────────────────────────────────────────────────────────────┘   │  │
│   │                                                                      │  │
│   │   score_batch(): aggregates N documents → avg + by_status counts    │  │
│   │                                                                      │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```
```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      6. ONTOLOGY LAYER                                       │
│                  (eks_ontology_config.json + eks_doc_config.json              │
│                   §ontology_triggers)                                        │
│                                                                              │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │                    ONTOLOGY CLASSES (35)                              │  │
│   │                                                                      │  │
│   │   ISO15926_Entity (root)                                             │  │
│   │   ├── FunctionalObject ──► TaggedEquipment ──► TaggedRotating        │  │
│   │   │                       │                  ├── PumpTag  (AT_EQPMP) │  │
│   │   │                       │                  └── MotorTag (AT_MOTOR) │  │
│   │   │                       ├── TaggedStatic                          │  │
│   │   │                       │   ├── TankTag        (AT_EQTNK)          │  │
│   │   │                       │   ├── VesselTag      (AT_EQVES)          │  │
│   │   │                       │   └── HeatExchangerTag (AT_EQEXC)        │  │
│   │   │                       ├── TaggedPiping                           │  │
│   │   │                       │   ├── PipelineTag    (AT_PROCESS)        │  │
│   │   │                       │   ├── InlineComponentTag (AT_INCOMP)     │  │
│   │   │                       │   ├── ValveTag                           │  │
│   │   │                       │   │   ├── ControlValveTag (AT_CVALVE)    │  │
│   │   │                       │   │   ├── SafetyValveTag  (AT_PSV)       │  │
│   │   │                       │   │   └── ManualValveTag  (AT_HVALVE)    │  │
│   │   │                       └── TaggedInstrument                       │  │
│   │   │                           ├── ControlSystemInstrumentTag         │  │
│   │   │                           └── FlowInstrumentTag                  │  │
│   │   ├── PhysicalObject ──► PumpUnit, ValveUnit, MotorUnit, ...         │  │
│   │   ├── Document ──► Drawing ──► PID_Drawing, CAD_Drawing              │  │
│   │   │            ├── Specification (SPC)                               │  │
│   │   │            ├── Datasheet (DS)                                    │  │
│   │   │            ├── Calculation                                       │  │
│   │   │            ├── Manual (MAN) ──► OpsManual (OM)                   │  │
│   │   │            ├── Register                                          │  │
│   │   │            ├── Report (RPT)                                      │  │
│   │   │            └── Procedure                                         │  │
│   │   ├── InfrastructureObject ──► ElectricalPanel, ControlPanel         │  │
│   │   └── GovernanceObject ──► EngineeringStandard, Originator           │  │
│   │                                                                      │  │
│   │   Classes carry: fragments[] (asset schema composition),             │  │
│   │                  tag_type_mapping, tag_type_aliases,                 │  │
│   │                  document_type_mapping                               │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │                ONTOLOGY RELATIONSHIPS (15)                            │  │
│   │                                                                      │  │
│   │   SUBCLASS_OF │ IS_A │ CONNECTS_TO │ FLOWS_TO │ INSTALLED_AT         │  │
│   │   REFERENCED_BY_DWG │ CONTROLS │ ENERGIZED_BY │ GOVERNED_BY          │  │
│   │   SET_POINT_IN │ SUPERSEDES │ SUPPLEMENTS │ REFERENCES_DOC           │  │
│   │   PRODUCED_BY │ FEEDS_FROM                                           │  │
│   │                                                                      │  │
│   │   Each has: inverse, transitive (bool), symmetric (bool)             │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │          ONTOLOGY TRIGGERS (6)  ──  Data column binding              │  │
│   │                                                                      │  │
│   │   document_type      ──► IS_A           (tier1)                      │  │
│   │   document_number    ──► SUPERSEDES     (tier1)                      │  │
│   │   asset_tags         ──► REFERENCES_ASSET (tier1)                    │  │
│   │   originator_company ──► PRODUCED_BY    (tier2)                      │  │
│   │   file_type          ──► HAS_FORMAT     (tier2)                      │  │
│   │   references_documents──► REFERENCES_DOC (tier3)                     │  │
│   │                                                                      │  │
│   │   Key ontology signals are tier1; auxiliary links are tier2/tier3   │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```
```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      7. PROCESSING PROFILE LAYER                             │
│                  (eks_processing_config.json)                                 │
│                                                                              │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │                                                                      │  │
│   │   FILE ──► filename_profile ──► segments ──► column values           │  │
│   │   │        (twrp_standard)       0→project_number                    │  │
│   │   │        (default)             1→area                              │  │
│   │   │                              2→document_type                     │  │
│   │   │                              3→discipline                        │  │
│   │   │                              4→sequence_number                   │  │
│   │   │                                                                  │  │
│   │   ├──► file_property_profile ──► property_mapping ──► columns        │  │
│   │   │    (pdf_props)              author → created_by                  │  │
│   │   │    (docx_props)             title  → embedded_title              │  │
│   │   │    (xlsx_props)             ...                                  │  │
│   │   │    (dgn_props)  [stub]      (empty mapping)                      │  │
│   │   │    (dwg_props)  [stub]      (empty mapping)                      │  │
│   │   │                                                                  │  │
│   │   │    Each bound to: bound_extraction_profile                       │  │
│   │   │                                                                  │  │
│   │   └──► extraction_profile ──► parser_class                           │  │
│   │        (technip_pdf)   → PDFParser                                   │  │
│   │        (technip_docx)  → DOCXParser                                  │  │
│   │        (technip_xlsx)  → XLSXParser                                  │  │
│   │        (technip_dwg)   → DWGParserStub   [GAP-N4]                    │  │
│   │        (technip_dgn)   → DGNParserStub   [GAP-N4]                    │  │
│   │                                                                      │  │
│   │   os_properties: {file_size, fs_created, fs_modified, file_hash}    │  │
│   │                                                                      │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│   Processing chain:                                                          │
│   filename → name parser → columns                                          │
│   file     → property extractor → columns                                   │
│   file     → content parser → elements + metadata                           │
│   columns + elements → health scorer → scores                               │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```
```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      8. ERROR CODE & MESSAGE LAYER                           │
│          (eks_error_config.json + eks_message_config.json)                    │
│                                                                              │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │                                                                      │  │
│   │   SYSTEM ERRORS (75)                    DATA LOGIC ERRORS (53)       │  │
│   │   ─────────────────                     ─────────────────────        │  │
│   │                                                                      │  │
│   │   S-E-S-01xx  Environment   (7)         P0-F-P-xxxx  File      (10) │  │
│   │   S-F-S-02xx  File/IO       (10)        P1-F-V-xxxx  File Val  (8)  │  │
│   │   S-C-S-03xx  Config        (8)         P1-M-V-xxxx  Meta Val  (10) │  │
│   │   S-C-S-09xx  ProjDef       (4)         P1-I-P-xxxx  Integrity (4)  │  │
│   │   S-R-S-04xx  Runtime       (10)        P1-T-P-xxxx  Transform (6)  │  │
│   │   S-A-S-05xx  AI/Optional   (3)         P1-X-P-xxxx  XREF      (5)  │  │
│   │   S-B-S-06xx  Bootstrap     (18)        P2-C-P-xxxx  Content   (5)  │  │
│   │   S-B-S-07xx  Bootstrap     (7)         P3-O-P-xxxx  Ontology  (5)  │  │
│   │   S-B-S-08xx  Bootstrap     (8)                                     │  │
│   │                                                                      │  │
│   │   METADATA: total_codes=128, system=75, data=53  ✅ verified        │  │
│   │                                                                      │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │                      PIPELINE MESSAGES (52)                           │  │
│   │                                                                      │  │
│   │   MSG-SYS-xxx   System lifecycle           (~6)                      │  │
│   │   MSG-PH0-xxx   Phase 0: Discovery         (~10)                     │  │
│   │   MSG-PH1-xxx   Phase 1: Processing        (~20)                     │  │
│   │   MSG-PH2-xxx   Phase 2/3: Content+Onto    (~8)                      │  │
│   │   MSG-HLT-xxx   Health/Score summary       (~8)                      │  │
│   │                                                                      │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```
```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      9. PIPELINE EXECUTION FLOW                              │
│                                                                              │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌───────┐ │
│   │  PHASE 0 │───►│  PHASE 1 │───►│  PHASE 2 │───►│  PHASE 3 │───►│  DB   │ │
│   │ Discovery│    │ Process  │    │ Content  │    │ Ontology │    │Write  │ │
│   └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘    └───────┘ │
│        │               │               │               │                    │
│        ▼               ▼               ▼               ▼                    │
│   ┌─────────┐    ┌───────────┐   ┌──────────┐    ┌──────────┐              │
│   │ Scanner │    │ Parser    │   │ Chunk/   │    │ Graph    │              │
│   │ Discover│    │ Filename  │   │ Embed    │    │ Build    │              │
│   │ files   │    │ Property  │   │ AI       │    │ Connect  │              │
│   │         │    │ Cover pg  │   │          │    │          │              │
│   └─────────┘    │ Structure │   └──────────┘    └──────────┘              │
│                  │ Health    │                                             │
│                  │ Score!    │  ◄── score_batch() called here              │
│                  └───────────┘                                             │
│                                                                              │
│   Phase 0: file_path, file_type populated                                    │
│   Phase A: document_number, project_number, document_type, discipline,       │
│            sequence_number, revision, area (filename parse)                  │
│   Phase B: all 33 remaining columns (property + parser + cover page)         │
│   ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─     │
│   Health scoring runs at Phase B end (pipeline_orchestrator.py:608)         │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```
```
┌──────────────────────────────────────────────────────────────────────────────┐
│                  10. CROSS-REFERENCE VERIFICATION MATRIX                      │
│                                                                              │
│   ENTITY PAIR            │ STATUS │ VALIDATION                               │
│   ───────────────────────┼────────┼──────────────────────────────────────    │
│   Class ↔ Type           │   ✅   │ 8↔28, all .class_id values valid         │
│   Type ↔ Family          │   ✅   │ Sparse (22 null), Mechanical=0 members   │
│   Class ↔ Ontology       │   ✅   │ All 8 bidirectional, 2 missing code str  │
│   Template ↔ Class       │   ✅   │ 6 templates via project_document_types   │
│   Template ↔ Elements    │   ✅   │ All 11 in registry, gated by expected_   │
│   Columns ↔ Tiers        │   ⚠️   │ verified_by missing scoring_tier         │
│   Columns ↔ OntoTri      │   ✅   │ 6 triggers all map to existing columns   │
│   Schema Weights ↔ Code  │   ✅   │ Perfect 1.00 sum match                   │
│   Schema Tiers ↔ Code    │   ✅   │ 5→3 mapping known design (Phase 3)       │
│   Template Scores ↔ Code │   ✅   │ Template→default→fallback chain correct  │
│   Class ↔ StructProfile  │   ✅   │ Class default + type override working    │
│   Class ↔ Extraction     │   ✅   │ 8 bindings valid, DGN/DWG are stubs      │
│   File ↔ Profile Chain   │   ✅   │ Extension→property→extraction complete   │
│   Errors ↔ Phases        │   ✅   │ 128 codes, metadata counts match         │
│   Errors ↔ Messages      │   ✅   │ 52 messages across 5 categories          │
│   Fallback ↔ Schema      │   ⚠️   │ Tier1 fallback drift (config-less only)  │
│   OnTrig ↔ Consistency   │   ✅   │ Full chain verified                      │
│                                                                              │
│   LEGEND:  ✅ Verified  ⚠️ Minor observation (no issue needed)              │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

================================================================================
                        END OF PART I — DEFINITION ENTITIES
================================================================================


## PART II — DB TABLE RELATIONSHIP MAP

> Source: `appendix_b.2_db_table_design.md` — complete table relationship map extracted here
> for unified cross-reference. See Appendix B.2 for individual table column definitions.

### 11.1 SCHEMA OVERVIEW — 36 Definition Tables, 10 Junction Tables

```
                                    ┌─────────────┐
                                    │   project   │
                                    └──────┬──────┘
                                           │ 1:N
                    ┌──────────────────────┼──────────────────────┐
                    │                      │                      │
              ┌─────▼──────┐        ┌──────▼──────┐       ┌──────▼──────┐
              │project_doc │        │  pipeline   │       │  batch_run  │
              │  _type     │        │   _phase    │       │ (_runs)     │
              └─────┬──────┘        └──────┬──────┘       └──────┬──────┘
                    │                      │                      │
       ┌────────────┼──────────┐           │           ┌─────────┼─────────┐
       │            │          │           │           │         │         │
  ┌────▼───┐  ┌─────▼───┐ ┌───▼───┐  ┌────▼────┐ ┌───▼──┐ ┌───▼───┐ ┌───▼───┐
  │doc_    │  │document │ │doc_   │  │ error   │ │msg   │ │health │ │health │
  │class   │  │_type    │ │family │  │_code    │ │      │ │_score │ │_batch │
  └──┬──┬──┘  └────┬────┘ └───────┘  └─────────┘ └──────┘ └───┬───┘ └───────┘
     │  │           │                                           │
     │  │  ┌────────┼──────────────────────────────┐            │
     │  │  │        │                              │            │
     │  └──┤   ┌────▼────┐                   ┌─────▼─────┐      │
     │     │   │document │                   │  data_    │      │
     │     │   │_template│                   │  column   │◄─────┘
     │     │   └────┬────┘                   └─────┬─────┘
     │     │        │                              │
     │     │   ┌────▼──────────┐         ┌─────────┼─────────┐
     │     │   │template_      │         │         │         │
     │     │   │elements       │    ┌────▼────┐ ┌──▼───┐ ┌──▼──────┐
     │     │   │(junction)     │    │column_  │ │score │ │ontology │
     │     │   └───────┬───────┘    │class    │ │_tier │ │_trigger │
     │     │           │            │(junc)   │ │      │ │         │
     │     │      ┌────▼───┐        └─────────┘ └──────┘ └────┬────┘
     │     │      │element │                                    │
     │     │      │_type   │                              ┌─────▼──────┐
     │     │      └────────┘                              │ontology    │
     │     │                                              │_class      │
     │     │                                              └──┬─────┬───┘
     │     │                                                 │     │
     │     │                                           ┌─────▼┐ ┌──▼───────┐
     │     │                                           │onto  │ │onto_class│
     │     │                                           │_rel  │ │_fragment │
     │     │                                           │      │ │(junction)│
     │     │                                           └──────┘ └──────────┘
     │     │
     │     │  ┌──────────────────────────────────────────┐
     │     │  │           PROCESSING PROFILES              │
     │     └──┤                                          │
     │        │  ┌──────────┐  ┌──────────────┐  ┌──────▼──────┐
     │        │  │filename  │  │file_property │  │ extraction  │
     │        │  │_profile  │──┤_profile      ├──┤_profile     │
     │        │  └──────────┘  └──────┬───────┘  └──────┬──────┘
     │        │                      │                  │
     │        │                ┌─────▼──────┐    ┌──────▼──────┐
     │        │                │fp_property │    │  file_type  │
     │        │                │_mapping    │    └─────────────┘
     │        │                └────────────┘
     │        └──────────────────────────────────────────┘
     │
     └──────────────────────────────────────────────────┐
                                                        │
        ┌───────────────────────────────────────────────┘
        │
   ┌────▼────────┐
   │  class_     │
   │  structural │
   │  _profile   │
   └─────────────┘
```

### 11.2 COMPLETE TABLE RELATIONSHIP MAP (with FK connections)

```
                              ┌──────────────────────┐
                              │   REFERENCE LOOKUPS   │
                              │ discipline (8)        │
                              │ department (N) ──────►│ discipline
                              │ facility (6)          │
                              │ project_code (3)      │
                              └────────┬──────────────┘
                                       │
                          ┌────────────┼────────────┐
                          │N:1         │N:1         │N:1
                          ▼            ▼            ▼
                    ┌──────────┐ ┌──────────┐ ┌──────────┐
                    │ project  │ │ project  │ │ facility │
                    │ _code    │ │ (system) │ │          │
                    │  (3)     │ └────┬─────┘ └──────────┘
                    └────┬─────┘      │
                         │            │1:N
              ┌──────────┘            │
              │1:N                    │
              ▼                       ▼
      ┌───────────────┐       ┌───────────────┐
      │ project       │       │ project_doc   │
      │ _definition   │       │ _type  (15)   │
      └──┬───┬───┬───┘       └───┬───┬───┬──┘
         │   │   │               │   │   │
         │   │   │    ┌──────────┘   │   └─────────┐
         │   │   │    │N:1           │N:1          │N:1
         │   │   │    ▼             ▼             ▼
         │   │   │ ┌────────┐  ┌──────────┐  ┌────────┐
         │   │   │ │doc_    │  │document  │  │doc_    │
         │   │   │ │class(8)│  │_template │  │family  │
         │   │   │ └──┬──┬──┘  │  (6)     │  │ (4)    │
         │   │   │    │  │     └────┬─────┘  └────────┘
         │   │   │    │  │1:1       │1:N
         │   │   │    │  └───┐ ┌───▼──────────┐
         │   │   │    │      │ │template_      │
         │   │   │    │      │ │elements(M:N)  │
         │   │   │    │      │ └──────┬────────┘
         │   │   │    │      │        │N:1
         │   │   │    │      │   ┌────▼──────┐
         │   │   │    │      │   │ element    │
         │   │   │    │      │   │ _type (11) │
         │   │   │    │      │   └───────────┘
         │   │   │    │      │
         │   │   │    │      ▼1:N
         │   │   │    │ ┌──────────────┐
         │   │   │    │ │class_struct  │
         │   │   │    │ │_profile (8)  │
         │   │   │    │ └──────────────┘
         │   │   │    │
         │   │   │    │  M:N (via column_class junction)
         │   │   │    ├──────────────────────┐
         │   │   │    ▼                      ▼
         │   │   │ ┌─────────────┐   ┌──────────────┐
         │   │   │ │column_class │   │ data_column  │
         │   │   │ │  (junction) │   │    (42)      │
         │   │   │ └─────────────┘   └──┬───┬───┬──┘
         │   │   │                      │   │   │
         │   │   │            ┌─────────┘   │   └─────────┐
         │   │   │            │N:1          │N:1          │N:1
         │   │   │            ▼             ▼             ▼
         │   │   │    ┌───────────┐  ┌───────────┐  ┌───────────┐
         │   │   │    │ontology   │  │score_tier │  │  score    │
         │   │   │    │_trigger(6)│  │   (3)     │  │_weight(3) │
         │   │   │    └─────┬─────┘  └───────────┘  └───────────┘
         │   │   │          │
         │   │   │    ┌─────┴─────┐
         │   │   │    │           │
         │   │   │    ▼N:1        ▼N:1
         │   │   │ ┌──────────┐ ┌───────────┐
         │   │   │ │ontology  │ │ data_     │
         │   │   │ │_relation │ │ column    │
         │   │   │ │  (15)    │ │ (same)    │
         │   │   │ └──────────┘ └───────────┘
         │   │   │
         │   │   │  ┌─────────────────────────────────────┐
         │   │   │  │                                     │
         │   │   │  ▼N:1                                 ▼N:1
         │   │   │ ┌──────────────┐             ┌────────────────┐
         │   │   │ │ontology_class│             │ extraction     │
         │   │   │ │    (35)      │             │ _profile (5)   │
         │   │   │ └──┬───────┬───┘             └──────┬─────────┘
         │   │   │    │       │                        │
         │   │   │    │self-FK│N:N (fragments)         │1:1
         │   │   │    │       │                        │
         │   │   │    │  ┌────▼──────────┐    ┌───────▼──────────┐
         │   │   │    │  │onto_class     │    │ file_property    │
         │   │   │    │  │_fragment (M:N)│    │ _profile (5)     │
         │   │   │    │  └───────────────┘    └───────┬──────────┘
         │   │   │    │                               │
         │   │   │    └── subClassOf (self-ref)       │1:N
         │   │   │                                    │
         │   │   │                           ┌────────▼──────────┐
         │   │   │                           │ fp_property       │
         │   │   │                           │ _mapping (N)      │
         │   │   │                           └───────────────────┘
         │   │   │
         │   │   │  ┌────────────────────┐
         │   │   │  │                    │
         │   │   │  ▼                    ▼
         │   │   │ ┌──────────────┐ ┌──────────────┐
         │   │   │ │filename      │ │  file_type   │
         │   │   │ │_profile (2)  │ │    (5)       │
         │   │   │ └──────────────┘ └──────────────┘
         │   │   │
         │   │   │  ┌────────────────────────────────────────┐
         │   │   │  │                                        │
         │   │   │  ▼                                        ▼
         │   │   │ ┌──────────────┐                   ┌──────────────┐
         │   │   │ │  error_code  │◄──────────────────│  pipeline    │
         │   │   │ │    (128)     │   related_code    │  _message(52)│
         │   │   │ └──────────────┘   (nullable FK)   └──────────────┘
         │   │   │
         │   │   │  ╔══════════════════════════════════════════╗
         │   │   │  ║   GROUP 10: ASSET SYSTEM                 ║
         │   │   │  ╚══════════════════════════════════════════╝
         │   │   │
         │   │   │  ┌──────────────┐    ┌──────────────────┐
         │   │   │  │asset_fragment│    │ontology_class    │
         │   │   │  │   (14)       │    │   (35, above)    │
         │   │   │  └──┬───────┬──┘    └────────┬─────────┘
         │   │   │     │       │                 │
         │   │   │     │       │1:N (fields)     │N:1
         │   │   │     │  ┌────▼───────────┐     │
         │   │   │     │  │asset_fragment  │     │
         │   │   │     │  │_field (N)      │     │
         │   │   │     │  └────────────────┘     │
         │   │   │     │                         │
         │   │   │     │  ┌──────────────────────┘
         │   │   │     │  │
         │   │   │     │  ▼
         │   │   │     │ ┌─────────────┐
         │   │   │     │ │ asset_type  │──► ontology_class
         │   │   │     │ │   (14)      │
         │   │   │     │ └──┬───┬──────┘
         │   │   │     │    │   │
         │   │   │     │    │   │1:N
         │   │   │     │    │   └───────────────────────┐
         │   │   │     │    │                           │
         │   │   │     │    │M:N (via type_fragment)    │
         │   │   │     │    │                           │
         │   │   │     │    ▼                           ▼
         │   │   │     │ ┌────────────────────┐ ┌───────────────────┐
         │   │   │     │ │ asset_type_fragment│ │asset_column_      │
         │   │   │     │ │    (junction)      │ │normalization (N)  │
         │   │   │     │ └────────┬───────────┘ └───────────────────┘
         │   │   │     │          │
         │   │   │     │          │N:1
         │   │   │     │          ▼
         │   │   │     │    ┌──────────────┐   ┌──────────────┐
         │   │   │     │    │asset_fragment│   │asset_trigger │──► ontology_relation
         │   │   │     │    │  (above)     │   │   (N)        │
         │   │   │     │    └──────────────┘   └──────────────┘
         │   │   │     │
         │   │   │     └─────────────────────────── (asset_item +
         │   │   │                                   runtime tables
         │   │   │                                   populated by pipeline)
         │   │   │
         │   │   ▼
         │   │  ┌───────────────────────┐
         │   │  │ project_allowed       │──► discipline
         │   │  │ _discipline (junction)│
         │   │  └───────────────────────┘
         │   │
         │   ▼
         │  ┌───────────────────────┐
         │  │ project_engineering   │
         │  │ _standard (N)         │
         │  └───────────────────────┘
         │
         ▼
    ┌───────────────────────┐
    │ project_revision      │
    │ _pattern (N)          │
    └───────────────────────┘

 ┌──────────────────────────────────────────────────────────────┐
 │                     TEMPORAL / OUTPUT TABLES                   │
 │                                                               │
 │  batch_run ──► health_score ──► health_batch                  │
 │                                                               │
 │  (health_score and health_batch are populated at pipeline     │
 │   runtime; they reference doc_class, document_template,       │
 │   and batch_run via FKs)                                     │
 └──────────────────────────────────────────────────────────────┘
```

### 11.3 TABLE SUMMARY (39 Tables)

```
┌──────┬───────────────────────────────┬──────┬──────────────────────────────────┐
│  #   │ Table Name                    │ Rows │ Key Relationships                 │
├──────┼───────────────────────────────┼──────┼──────────────────────────────────┤
│ T01  │ project                       │   2  │ root table                        │
│ T02  │ project_doc_type              │  15  │ → project,doc_class,template      │
│ T03  │ batch_run                     │   N  │ → project                        │
│ T28  │ discipline                    │   8  │ standalone (reference)             │
│ T29  │ department                    │   N  │ → discipline (nullable)            │
│ T30  │ facility                      │   6  │ standalone (reference)             │
│ T31  │ project_code                  │   3  │ standalone (reference)             │
├──────┼───────────────────────────────┼──────┼──────────────────────────────────┤
│ T04  │ doc_class                     │   8  │ → ontology_class                  │
│ T05  │ document_type                 │  28  │ → doc_class, doc_family           │
│ T06  │ document_family               │   4  │ standalone                        │
│ T07  │ class_structural_profile      │   8  │ → doc_class (1:1)                 │
│ T08  │ type_structural_profile       │  28  │ → document_type (1:1)             │
├──────┼───────────────────────────────┼──────┼──────────────────────────────────┤
│ T09  │ document_template             │   6  │ standalone                        │
│ T10  │ template_source_quality       │  36  │ → document_template               │
│ T11  │ element_type                  │  11  │ standalone                        │
│ J01  │ template_elements             │  44  │ → template + element_type         │
│ J02  │ element_by_cover_type         │  33  │ → element_type                    │
├──────┼───────────────────────────────┼──────┼──────────────────────────────────┤
│ T12  │ data_column                   │  42  │ standalone                        │
│ J03  │ column_class                  │ 336  │ → data_column + doc_class         │
│ T13  │ score_dimension               │   6  │ standalone                        │
│ T14  │ score_tier                    │   5  │ standalone                        │
│ T15  │ score_weight_tier             │   3  │ standalone                        │
├──────┼───────────────────────────────┼──────┼──────────────────────────────────┤
│ T16  │ ontology_class                │  35  │ self-ref (subClassOf)             │
│ T17  │ ontology_relation             │  15  │ standalone                        │
│ J04  │ onto_class_fragment           │  12  │ → ontology_class                  │
│ T18  │ ontology_trigger              │   6  │ → data_column,ontology_relation   │
├──────┼───────────────────────────────┼──────┼──────────────────────────────────┤
│ T19  │ filename_profile              │   2  │ standalone                        │
│ T20  │ file_property_profile         │   5  │ → extraction_profile              │
│ T21  │ fp_property_mapping           │  30  │ → file_property_profile,          │
│      │                               │      │    data_column                    │
│ T22  │ extraction_profile            │   5  │ standalone                        │
│ T23  │ file_type                     │   5  │ standalone                        │
├──────┼───────────────────────────────┼──────┼──────────────────────────────────┤
│ T24  │ error_code                    │ 128  │ standalone                        │
│ T25  │ pipeline_message              │  52  │ → error_code (nullable)           │
├──────┼───────────────────────────────┼──────┼──────────────────────────────────┤
│ T26  │ health_score                  │   N  │ → batch_run,doc_class,template    │
│ T27  │ health_batch                  │   N  │ → batch_run                       │
├──────┼───────────────────────────────┼──────┼──────────────────────────────────┤
│ T32  │ project_definition            │   2  │ → project_code,discipline         │
│ T33  │ project_engineering_standard  │  10  │ → project_definition              │
│ J05  │ project_allowed_discipline    │  16  │ → project_definition,discipline   │
│ T34  │ project_revision_pattern      │   2  │ → project_definition              │
├──────┼───────────────────────────────┼──────┼──────────────────────────────────┤
│ T35  │ asset_fragment                │  14  │ standalone                        │
│ T36  │ asset_type                    │  14  │ → ontology_class (nullable)       │
│ J06  │ asset_type_fragment           │ 112  │ → asset_type,asset_fragment       │
│ T37  │ asset_fragment_field          │ 210  │ → asset_fragment                  │
│ T38  │ asset_column_normalization    │  80  │ → asset_type                      │
│ T39  │ asset_trigger                 │  18  │ → asset_type,ontology_relation    │
└──────┴───────────────────────────────┴──────┴──────────────────────────────────┘

                  39 Tables (36 definition + 10 junction + 2 output)
                  ~1,500 definition rows at rest
```


## PART III — KEY FOREIGN-KEY CLOSURE PATHS

> Source: `appendix_b.2_db_table_design.md`

```
1.  CLASSIFICATION CHAIN:
    project_doc_type.local_code
      → project_doc_type.class_id → doc_class.class_id
        → doc_class.ontology_class → ontology_class.name
      → project_doc_type.template_id → document_template.template_id
        → template_elements.element_name → element_type.element_name

2.  COLUMN-TO-SCORE CHAIN:
    data_column.column_name
      → column_class.class_id → doc_class.class_id
      → data_column.scoring_tier → score_weight_tier.tier_name
      → (at runtime) health_score uses class_id to resolve scorable columns

3.  ONTOLOGY CHAIN:
    ontology_trigger.column_name
      → data_column.column_name
      → column_class.class_id → doc_class.class_id
      → ontology_trigger.relation_name → ontology_relation.name

4.  FILE PROCESSING CHAIN:
    file_type.extension
      → file_property_profile.supported_extensions (filter match)
        → file_property_profile.bound_extraction_fk → extraction_profile.profile_id
          → extraction_profile.parser_class (dynamic import)
      → filename_profile (by project convention)

5.  ERROR HANDLING CHAIN:
    error_code.code
      → pipeline_message.related_code (nullable FK)
        → pipeline_message.triggers_on (event binding at runtime)

6.  PROJECT DEFINITION CHAIN:
    project_code.proj_code
      → project_definition.proj_code (1:1)
        → project_definition.discipline → discipline.discipline_code
        → project_allowed_discipline.disc_code → discipline.discipline_code
        → project_engineering_standard.proj_code → project_definition.proj_code
        → project_revision_pattern.proj_code → project_definition.proj_code

7.  ASSET TYPE CHAIN:
    asset_type.asset_type_id
      → asset_type.ontology_class → ontology_class.class_uri
      → asset_type_fragment.asset_type_id + fragment_id
          → asset_fragment.fragment_id
            → asset_fragment_field.fragment_id
      → asset_column_normalization.asset_type_id
      → asset_trigger.asset_type_id
        → asset_trigger.edge_type → ontology_relation.relation_uri
```


## PART IV — SCHEMA-TO-TABLE MASTER INDEX & LOAD ORDER

### Schema-to-Table Mapping

```
eks/config/schemas/
│
├── eks_doc_config.json ──────────────────────────────────────────────────────────
│   ├── file_type_registry{}          →  file_type             (5 rows)
│   ├── element_type_registry[]       →  element_type          (11 rows)
│   ├── element_type_registry[].      →  element_by_cover_type (junction)
│   │     expected_by_cover_types[]
│   ├── column_processing{}           →  data_column           (42 rows)
│   ├── column_processing.{col}.      →  column_class          (junction)
│   │     applies_to_document_types[]
│   ├── health_scoring.dimensions[]   →  score_dimension       (6 rows)
│   ├── health_scoring.score_tiers[]  →  score_tier            (5 rows)
│   ├── health_scoring.weight_tiers{} →  score_weight_tier     (3 rows)
│   └── ontology_triggers{}           →  ontology_trigger      (6 rows)
│
├── eks_document_type_schema.json ─────────────────────────────────────────────────
│   ├── document_classes[]            →  doc_class             (8 rows)
│   ├── document_classes[].           →  class_structural_     (8 rows)
│   │     structural_profile              profile
│   ├── document_types[]              →  document_type         (28 rows)
│   ├── document_types[].             →  type_structural_      (28 rows)
│   │     structural_profile              profile
│   ├── document_family[]             →  document_family       (4 rows)
│   ├── document_templates[]          →  document_template     (6 rows)
│   ├── document_templates[].         →  template_source_      (36 rows, 6x6)
│   │     source_quality_score            quality
│   ├── document_templates[].         →  template_elements     (junction)
│   │     expected_elements[]
│   └── project_document_types[]      →  project_doc_type      (15 rows)
│
├── eks_ontology_config.json ──────────────────────────────────────────────────────
│   ├── classes[]                     →  ontology_class        (35 rows)
│   ├── classes[].fragments[]         →  onto_class_fragment   (junction)
│   └── relationships[]               →  ontology_relation     (15 rows)
│
├── eks_processing_config.json ────────────────────────────────────────────────────
│   ├── filename_profiles[]           →  filename_profile      (2 rows)
│   ├── extraction_profiles[]         →  extraction_profile    (5 rows)
│   ├── file_property_profiles[]      →  file_property_profile (5 rows)
│   └── file_property_profiles[].     →  fp_property_mapping   (~30 rows)
│       property_mapping[]
│
├── eks_error_code_base.json          →  (validates eks_error_config.json only)
├── eks_error_config.json ─────────────────────────────────────────────────────────
│   └── error_codes{system,           →  error_code            (128 rows)
│       data_logic}
│
├── eks_message_base.json             →  (validates eks_message_config.json only)
├── eks_message_config.json ───────────────────────────────────────────────────────
│   └── messages{}                    →  pipeline_message      (52 rows)
│
├── eks_config.json ───────────────────────────────────────────────────────────────
│   └── project_metadata              →  project               (2 rows)
│
├── eks_discipline_schema.json ────────────────────────────────────────────────────
│   └── disciplines[]                 →  discipline            (8 rows)
│
├── eks_department_schema.json ─────────────────────────────────────────────────────
│   └── departments[]                 →  department            (~12 rows)
│                                       →  discipline.discipline_code (nullable FK)
│
├── eks_facility_schema.json ───────────────────────────────────────────────────────
│   └── facilities[]                  →  facility              (6 rows)
│
├── eks_project_code_schema.json ───────────────────────────────────────────────────
│   └── project_codes[]               →  project_code          (3 rows)
│
├── eks_project_definition_config.json ──────────────────────────────────────────────
│   ├── project_definition.{code}     →  project_definition    (2 rows)
│   ├── {project}.engineering_standards{} → project_engineering_standard (~10 rows)
│   ├── {project}.engineering_        →  project_allowed_discipline (junction, ~16)
│   │     convention.allowed_
│   │     disciplines[]
│   └── {project}.revision_validation →  project_revision_pattern (2 rows)
│
├── eks_asset_base_schema.json ─────────────────────────────────────────────────────
│   ├── $defs.<fragment_id>            →  asset_fragment        (14 rows, hdr only)
│   └── $defs.<fragment_id>.properties →  asset_fragment_field  (~210 rows)
│
├── eks_asset_setup_schema.json       →  (validates eks_asset_config.json only)
│
├── eks_asset_config.json ──────────────────────────────────────────────────────────
│   ├── asset_type_registry[]         →  asset_type            (14 rows)
│   ├── asset_type_registry[].        →  asset_type_fragment   (junction, ~112)
│   │     fragments[]
│   ├── column_normalization.<type>[] →  asset_column_normalization (~80 rows)
│   ├── relationship_triggers[]       →  asset_trigger         (~12 rows)
│   └── document_triggers[]           →  asset_trigger         (~6 rows)
│
└── (runtime only — no schema) ────────────────────────────────────────────────────
    └── health_scorer.py output       →  health_score          (N rows per run)
                                        →  health_batch        (1 row per run)
```

### Load Order (Dependency-Topological)

```
 1. project             (no FKs)
 2. discipline          (no FKs)
 3. department          (FK → discipline, nullable)
 4. facility            (no FKs)
 5. project_code        (no FKs)
 6. ontology_class      (self-ref FK, root classes have subclass_of=NULL)
 7. ontology_relation   (no FKs)
 8. doc_class           (FK → ontology_class)
 9. document_family     (no FKs)
10. document_type       (FK → doc_class, doc_family)
11. class_structural_profile   (FK → doc_class)
12. type_structural_profile    (FK → document_type)
13. element_type        (no FKs)
14. document_template   (no FKs)
15. template_source_quality     (FK → document_template)
16. template_elements           (FK → document_template, element_type)
17. element_by_cover_type       (FK → element_type)
18. file_type           (no FKs)
19. data_column         (no FKs)
20. column_class        (FK → data_column, doc_class)
21. score_dimension     (no FKs)
22. score_tier          (no FKs)
23. score_weight_tier   (no FKs)
24. ontology_trigger    (FK → data_column, ontology_relation)
25. onto_class_fragment (FK → ontology_class)
26. filename_profile    (no FKs)
27. extraction_profile  (no FKs)
28. file_property_profile       (FK → extraction_profile)
29. fp_property_mapping         (FK → file_property_profile, data_column)
30. project_doc_type    (FK → project, doc_class, document_template)
31. error_code          (no FKs)
32. pipeline_message    (FK → error_code, nullable)
33. project_definition  (FK → project_code, discipline)
34. project_engineering_standard (FK → project_definition)
35. project_allowed_discipline   (FK → project_definition, discipline)
36. project_revision_pattern     (FK → project_definition)
37. asset_fragment      (no FKs)
38. asset_fragment_field        (FK → asset_fragment)
39. asset_type          (FK → ontology_class, nullable)
40. asset_type_fragment (FK → asset_type, asset_fragment)
41. asset_column_normalization  (FK → asset_type)
42. asset_trigger       (FK → asset_type, ontology_relation)
--- runtime tables (populated during pipeline execution) ---
43. batch_run           (FK → project)
44. health_score        (FK → batch_run, doc_class, document_template)
45. health_batch        (FK → batch_run)
```


## PART V — CROSS-DOCUMENT GAP ANALYSIS

> **DB Table Design (Appendix B.2) vs Appendix B (Document Registry) vs Runtime Artifacts**
> Evaluation date: 2026-08-09

### 🔴 P0 — Blocking Defects

| ID | Title | Severity | Description |
|:---|:------|:---------|:------------|
| GAP-001 | `document_registry` core table missing | 🔴 P0 | Appendix B §B4 defines 54 columns across 11 groups in DuckDB `eks_registry.db`. All 48 tables in `db_table_design.md` have zero correspondence. 54 FK-capable fields (document_type → project_doc_type.local_code, file_type → file_type.extension, discipline → discipline.discipline_code, supersedes/superseded_by → self-ref FK) require explicit FK declaration on creation. |
| GAP-002 | `document_elements` runtime table missing | 🔴 P0 | Appendix B §B5.8–B5.11 defines full CRUD API (store, get, get_by_type, delete). Appendix D §D7.10 defines schema: doc_id, element_type, element_id, title, content, confidence, source. `element_type` table (GROUP 3, 11 types) exists — but no runtime data table to store actual detection results. |
| GAP-003 | Appendix B §B3.2 stale path + §B3.4 element_expectations alignment | 🔴 P0 | §B3.2 correctly records removal of `document_type_registry` from v1.9.0. §B3.4 references `eks_document_type_schema.json` → `document_templates[].expected_elements`. `element_by_cover_type` junction (GROUP 3, 33 rows: A/B/C/D/E/F × 11 elements) must match §B3.4 "Expected By Cover Type" column. |

### 🟡 P1 — Major Gaps

| ID | Title | Severity | Description |
|:---|:------|:---------|:------------|
| GAP-004 | `batch_run` missing stage statistics fields | 🟡 P1 | Current: run_id, project_code, started_at, finished_at, status, doc_count. Missing: job_id (UUID), data_dir, current_stage (A/B/C), phase_a_discovered, phase_a_valid, phase_b_total, phase_b_success, phase_b_failed, phase_c_flagged. These map to Appendix D §D8 phase states and `checkpoint_{job}_{phase}.json`. |
| GAP-005 | `health_score.document_id` missing FK | 🟡 P1 | Defined as "TEXT — doc number or UUID" with no FK constraint. After registry creation, must be FK → `document_registry.id` (UUID v4). Also present in Appendix B §B4 documents.id and §D7.10 document_elements.doc_id. |
| GAP-006 | JSON columns need junction tables | 🟡 P1 | `references_documents` (JSON array) → needs `document_reference` (M:N). `supersedes`/`superseded_by` (scalar self-ref) → FK or standalone. Appendix B §B2.1 §5 defines 10 document-level relationship types (produced_from, validated_by, references, implements, supersedes, derived_from, contains, linked_to, verified_against, governs) — not covered by current 15 ontology-level relations in `ontology_relation`. |
| GAP-007 | `page_count` multi-source SSOT conflict | 🟡 P1 | Present in: (a) Appendix B §B4 Asset Tags → "Auto from parser metadata", (b) GROUP 8 `health_score` via extraction_results.csv, (c) `total_sheets` defaults to `page_count`. No SSOT declaration. `document_registry.page_count` must be declared the SSOT. |
| GAP-008 | `SchemaToDDL` load order gap for new tables | 🟡 P1 | Appendix B §B7.2 step 1: "DDL auto-generated from JSON schema via SchemaToDDL" (DuckDB runtime). `db_table_design.md` load order (45 steps) does not include `document_registry` or `document_elements`. `document_registry` requires these to load first: doc_class, project_doc_type, document_template, element_type, file_type, discipline, project_code, project_definition. Suggested insertion: after step 42 (asset_trigger), before runtime tables. |

### 🟡 P2 — Observable Gaps

| ID | Title | Severity | Description |
|:---|:------|:---------|:------------|
| GAP-009 | Pipeline checkpoint no DB table | 🟡 P2 | Current `output/checkpoint_{job}_{phase}.json` is filesystem-only. Needs `pipeline_checkpoint` table: job_id, phase (A/B/C), state (JSON), created_at. Checkpoints are not SQL-queryable; recovery/audit relies on grep. |
| GAP-010 | Pipeline event log no DB table | 🟡 P2 | `output/debug_log.json` (~178KB/run) has structured logs per Appendix D §D12.1 debug_object schema (logs[], errors[], trace_table[]). Needs `pipeline_event_log`: job_id (FK), timestamp, level, category, context, module, message. |
| GAP-011 | `ontology_trigger` alignment with Appendix B §B4.1 | 🟡 P2 | §B4.1 defines 7 ontology trigger rules: document_type→IS_A, document_number→SUPERSEDES, asset_tags→REFERENCES_ASSET, originator_company→PRODUCED_BY, file_type→HAS_FORMAT, references_documents→REFERENCES_DOC, lifecycle_stage→HAS_STAGE. GROUP 5 `ontology_trigger` has 6 rows — needs per-row verification against all 7. Potential `column_name` PK collision between `document_number` mapped to SUPERSEDES vs REFERENCES_DOC. |

### 🟢 P3 — Refinement

| ID | Title | Severity | Description |
|:---|:------|:---------|:------------|
| GAP-012 | Export artifacts not tracked | 🟢 P3 | Appendix B §B6 step 6 generates 3 CSVs per job: discovery_inventory, extraction_results, review_flags → `output/{uuid}/`. Needs `export_artifact` table: job_id (FK), artifact_type, file_path, created_at, row_count. |
| GAP-013 | Version number consistency risk | 🟢 P3 | Appendix B §B4: "Schema source: eks_doc_base_schema.json v1.16.0 — 54 columns" ✅. §B3.2: "five-section runtime carrier v2.2.0". GROUP 2 `document_type` = 28 types — must match carrier v2.2.0 count. |
| GAP-014 | `template_source_quality` vs §B3.4 template count alignment | 🟢 P3 | GROUP 3: 6 templates × 6 cover types = 36 rows. `template_elements` = 44 rows (6 templates × varying expected_elements). Verify 44 matches carrier v2.3.0 actual expected_elements array entry count. |
| GAP-015 | `project_definition` missing `_setup_schema.json` | 🟢 P3 | DB design §GROUP 9 self-identifies: "eks_project_definition_config.json lacks a dedicated _setup_schema.json file." Per AGENTS.md §9 (3-tier compliance), every config file requires a corresponding setup schema. |

### Summary

| Priority | Count | New Tables Needed |
|:---------|:-----|:------------------|
| 🔴 P0 | 3 | `document_registry`, `document_element` |
| 🟡 P1 | 5 | expand `batch_run`, `document_reference` junction, `document_supersedes` junction |
| 🟡 P2 | 3 | `pipeline_checkpoint`, `pipeline_event_log` |
| 🟢 P3 | 4 | `export_artifact` + cross-source alignment verification |
| **Total** | **15** | **~8 new tables + batch_run expansion + FK migrations** |


================================================================================
                    END OF CROSS-RELATIONSHIP CHART
================================================================================
```

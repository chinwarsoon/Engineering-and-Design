# Appendix B.2 — DB Table Design

> **Parent:** [Appendix B — Document Registry](appendix_b_document_registry.md)
> **Sibling:** [Appendix B.1 — Cross-Relationship Chart](appendix_b.1_cross_relationship_chart.md)
>
> This document defines every DB table, its columns, types, constraints, and schema provenance. For the complete relationship map (all FK connections) and cross-document gap analysis, see **Appendix B.1**.

| Revision | Date | Author | Summary |
|:---------|:-----|:-------|:--------|
| 1.0 | 2026-08-09 | AI Assistant | Initial table layout, 27 tables with FK relationships |
| 1.1 | 2026-08-09 | AI Assistant | Added schema-to-table mapping, field provenance, SSOT compliance |
| 1.2 | 2026-08-09 | AI Assistant | Added project definition (GROUP 9), asset system (GROUP 10), reference tables (department/discipline/facility/project_code) |
| 1.3 | 2026-08-09 | AI Assistant | Renamed to Appendix B.2; relationship map + FK paths moved to B.1 |
| 1.6 | 2026-08-10 | AI Assistant | I300 (T1.263): ontology_relation 15→16 (HAS_STAGE added), ontology_trigger 6→7 (lifecycle_stage→HAS_STAGE), TABLE SUMMARY T17/T18 + schema-to-table counts updated; §24 follow-up noted for REFERENCES_ASSET/HAS_FORMAT drift |
| 1.7 | 2026-08-10 | AI Assistant | I298–I299, I301–I305 batch: (I302) version banners B.1 v1.1→v1.5, B.2 v1.2→v1.6; (I303) template_elements 44→27, twrp_spec_c populated [section,table,image], carrier v2.3.1; (I304) eks_project_definition_setup_schema.json v1.0.0 created, config $schema repointed; (I305) ontology relations 16→18 (REFERENCES_ASSET + HAS_FORMAT added, §24 drift resolved), T17 16→18; (I298/I299/I301) GROUP 12 pipeline runtime tables added (pipeline_checkpoint, pipeline_event_log, export_artifact), TABLE SUMMARY T40-T42, load order 48→51; GAP-011 §24 resolved, GAP-013–015 RESOLVED, GAP-012 promoted P3→P1 |
| 1.8 | 2026-08-13 | AI Assistant | I308 (T1.282–T1.286): new **EXPORT VIEW MODEL** section — persistent DuckDB views `v_discovery_inventory` / `v_extraction_results` / `v_review_flags` defined by `eks_export_view_config.json` v1.1.0 (source_table=documents, is_latest filter, ordered columns, file_base_name/sheet_name/formats); `generate_view_ddl()` renders `CREATE OR REPLACE VIEW` (idempotent, no hardcoded view SQL); `export_artifact.artifact_type` = view_id; `documents.flag_reason` materialized at ingest; version-control columns pruned from exports; missing view config → fail-fast S-C-S-0312; GAP-016 (two-tier gap) RESOLVED — DB is the materialized view, JSON-only definition layer language removed |
| 1.5 | 2026-08-10 | AI Assistant | I293/I294/I295 re-scoped 2026-08-10 against runtime code: `batch_run`/`health_score`/`health_batch` are CREATE tasks (tables don't exist in runtime DB — GROUP 11 mapping updated to "CREATE tracked by I293/T1.256, I294/T1.257"); `document_reference` junction added to GROUP 11 (I295/T1.258); supersedes self-ref already delivered as declared_only `fk_supersedes` (I290) — dropped from I295 scope |
| 1.4 | 2026-08-10 | AI Assistant | I291 (T1.254): added GROUP 11 "RUNTIME TABLES" family (documents, document_elements, batch_run, health_score, health_batch) with document_elements shape (id UUID PK, created_at DEFAULT now(), element_seq); load-order position 43/44 documented (renumber deferred to I297/T1.260) |

```
================================================================================
                 EKS DEFINITION DATABASE — FULL TABLE LAYOUT
                           v1.8 / 2026-08-13
================================================================================
```


## SCHEMA OVERVIEW — 36 Definition Tables, 10 Junction Tables

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


## SCHEMA-DRIVEN DESIGN PRINCIPLES

The database is a **materialized view of the SSOT schema JSON files**. Per AGENTS.md §9 (Schema
Pattern) and §5.15 (SSOT), no DB table stores data that can be derived from schema. The
relationship is:

```
  eks/config/schemas/
  ├── eks_document_type_schema.json   ──►  Group 2 (Classification) + Group 3 (Templates)
  ├── eks_doc_config.json             ──►  Group 3 (Elements) + Group 4 (Columns+Scoring) + Group 5 (Triggers)
  ├── eks_ontology_config.json        ──►  Group 5 (Ontology)
  ├── eks_processing_config.json      ──►  Group 6 (Processing Profiles)
  ├── eks_error_code_base.json        ──►  Group 7 (Error codes — pattern definitions)
  ├── eks_error_config.json           ──►  Group 7 (Error codes — actual values)
  ├── eks_message_base.json           ──►  Group 7 (Messages — format definitions)
  ├── eks_message_config.json         ──►  Group 7 (Messages — actual values)
  ├── eks_config.json                 ──►  Group 1 (project_metadata + system config)
  ├── eks_department_schema.json      ──►  Group 1 (Reference — department lookup)
  ├── eks_discipline_schema.json      ──►  Group 1 (Reference — discipline lookup)
  ├── eks_facility_schema.json        ──►  Group 1 (Reference — facility lookup)
  ├── eks_project_code_schema.json    ──►  Group 1 (Reference — project code lookup)
  ├── eks_project_definition_config.json ──►  Group 9 (Per-project engineering configuration)
  ├── eks_asset_base_schema.json      ──►  Group 10 (Asset definitions — fragment types)
  ├── eks_asset_setup_schema.json     ──►  Group 10 (Asset structure — validates config)
  └── eks_asset_config.json           ──►  Group 10 (Asset actual values — type registry, column normalization)
```

### Schema Layering (3-layer model per AGENTS.md §9)

```
  *_base_schema.json   ──  $id, definitions, shared types ($ref source)
  *_setup_schema.json  ──  properties, required, additionalProperties (structure)
  *_config.json        ──  actual values, instantiations (SSOT data)
```

The DB is loaded from `*_config.json` files. `_base` and `_setup` schemas validate the config
at load time but are not directly stored in DB tables (they govern structure, not data).

### Cross-Source Alignment Rule (AGENTS.md §5.13)

Every DB column that mirrors a schema field must be verified against all sources:

| Check | Rule |
|:------|:-----|
| Field name | DB column name = schema field name (snake_case) |
| Field type | DB type preserves schema type (string/number/boolean/array→JSON) |
| FK integrity | Every FK target must exist in the referenced schema's `$id` namespace |
| Cardinality | DB row count must equal schema array length for 1:1 tables |
| Enum values | DB CHECK constraints must match schema `enum` values exactly |

---

## TABLE DEFINITIONS

### GROUP 1: PROJECT, RUNTIME & REFERENCE (7 tables)

```
┌─────────────────────────────────────────────────┐
│                    project                       │
├──────────────┬──────────┬───────────────────────┤
│ project_code │ TEXT PK  │ "131101", "131242"     │
│ label        │ TEXT     │ Human-readable name    │
│ created_at   │ TEXT     │ ISO date               │
└──────────────┴──────────┴───────────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────────────────────────────────────┐
│                project_doc_type                  │
├──────────────────┬──────────┬───────────────────┤
│ id               │ INT PK   │ surrogate         │
│ project_code     │ TEXT FK  │ → project         │
│ local_code       │ TEXT     │ "DWG","SPC","DS"  │
│ class_id         │ TEXT FK  │ → doc_class       │
│ template_id      │ TEXT FK  │ → document_template│
│ format_category  │ TEXT     │ "print","native"  │
│ native_source    │ TEXT     │ "dwg","dgn" etc   │
│ expected_file_types│JSON    │ ["pdf","dwg"]     │
│ parsing_profile  │ TEXT     │ "technip_pdf"     │
│ project_rules    │ JSON     │ extra rules blob  │
└──────────────────┴──────────┴───────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────────────────────────────────────┐
│                  batch_run                       │
├──────────────┬──────────┬───────────────────────┤
│ run_id        │ TEXT PK  │ UUID                  │
│ project_code  │ TEXT FK  │ → project            │
│ started_at    │ TEXT     │ ISO datetime          │
│ finished_at   │ TEXT     │ ISO datetime          │
│ status        │ TEXT     │ running/success/failed│
│ doc_count     │ INT      │ documents processed   │
└──────────────┴──────────┴───────────────────────┘

                    -- Reference / Lookup Tables --

┌──────────────────────────────────────────────────────────────────┐
│                    discipline                                     │
├──────────────────┬──────────┬────────────────────────────────────┤
│ discipline_code  │ TEXT PK  │ "PI","EL","ME","CI","CS","IN"..   │
│ discipline_name  │ TEXT     │ "Piping","Electrical","Mechanical" │
│ description      │ TEXT     │ Full discipline description        │
└──────────────────┴──────────┴────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                    department                                     │
├──────────────────┬──────────┬────────────────────────────────────┤
│ department_code  │ TEXT PK  │ 2-character code (base schema def) │
│ department_name  │ TEXT     │ Department name                    │
│ description      │ TEXT     │ Department description             │
│ discipline_code  │ TEXT FK  │ → discipline.discipline_code (opt) │
└──────────────────┴──────────┴────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                    facility                                       │
├──────────────────┬──────────┬────────────────────────────────────┤
│ facility_code    │ TEXT PK  │ "GF","PF","MF" etc                 │
│ facility_name    │ TEXT     │ Facility/location name             │
│ facility_type    │ TEXT     │ plant/yard/site/office             │
│ description      │ TEXT     │ Facility description               │
└──────────────────┴──────────┴────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                    project_code                                   │
├──────────────────┬──────────┬────────────────────────────────────┤
│ proj_code        │ TEXT PK  │ "131101","131242" (6-digit)       │
│ project_name     │ TEXT     │ Full project name                  │
│ description      │ TEXT     │ Project scope/description          │
└──────────────────┴──────────┴────────────────────────────────────┘
```

### GROUP 1 SCHEMA SOURCE MAPPING

| DB Table | Schema File | Schema Path | Load Method |
|:---------|:------------|:------------|:------------|
| `project` | `eks_config.json` | `project_metadata` | direct field mapping |
| `project_doc_type` | `eks_document_type_schema.json` | `project_document_types[]` | array iteration with FK resolution (class_id, template_id must exist) |
| `batch_run` | *(no schema)* | runtime generated | populated by pipeline orchestrator at execution start |
| `discipline` | `eks_discipline_schema.json` | `disciplines[]` | array iteration; base def: `eks_base_schema.json#/definitions/discipline_entry_def` |
| `department` | `eks_department_schema.json` | `departments[]` | array iteration; base def: `eks_base_schema.json#/definitions/department_entry_def` |
| `facility` | `eks_facility_schema.json` | `facilities[]` | array iteration; base def: `eks_base_schema.json#/definitions/facility_entry_def` |
| `project_code` | `eks_project_code_schema.json` | `project_codes[]` | array iteration; base def: `eks_base_schema.json#/definitions/project_entry_def` |

**Field provenance — `project_doc_type`:**

| DB Column | Schema Field | Schema Section |
|:----------|:-------------|:---------------|
| project_code | project_code | project_document_types[] |
| local_code | local_code | project_document_types[] |
| class_id | class_id | project_document_types[] |
| template_id | template | project_document_types[] |
| format_category | format_category | project_document_types[] |
| native_source | native_source | project_document_types[] |
| expected_file_types | expected_file_types | project_document_types[] |
| parsing_profile | parsing_profile | project_document_types[] |
| project_rules | project_rules | project_document_types[] |

**Purpose:** Binds a project's local document code (e.g., "DWG", "SPC") to the global
class/template taxonomy. This is the bridge table that converts project-local conventions
into system-wide definitions. Schema SSOT: `eks_document_type_schema.json` §project_document_types.

**Field provenance — reference tables:**

| DB Column | Schema Field | Schema Source |
|:----------|:-------------|:-------------|
| discipline_code | code | `eks_discipline_schema.json` (via `eks_base_schema.json#/definitions/discipline_entry_def`) |
| discipline_name | name | (same) |
| department_code | code | `eks_department_schema.json` (via `eks_base_schema.json#/definitions/department_entry_def`) |
| department_name | name | (same) |
| facility_code | code | `eks_facility_schema.json` (via `eks_base_schema.json#/definitions/facility_entry_def`) |
| facility_type | facility_type | (same) |
| proj_code | project_code | `eks_project_code_schema.json` (via `eks_base_schema.json#/definitions/project_entry_def`) |
| project_name | project_name | (same) |

**Purpose:** These 4 lookup tables provide validation domains for FK fields throughout the
system (e.g., `project_definition.discipline` → `discipline.discipline_code`). They follow
the 2-tier pattern (standalone schema → values, no separate `_config.json`), with field
definitions sourced from `eks_base_schema.json` shared definitions.


### GROUP 2: CLASSIFICATION (3 tables + 2 junction tables)

```
┌──────────────────────────────────────────────────────────────┐
│                         doc_class                             │
├───────────────┬──────────┬───────────────────────────────────┤
│ class_id      │ TEXT PK  │ Drawing,Specification,Datasheet.. │
│ label         │ TEXT     │ "Engineering Drawing"             │
│ ontology_class│ TEXT FK  │ → ontology_class.name             │
│ extraction_pro│ TEXT     │ "technip_pdf" (profile FK)        │
│ cover_bearing │ BOOL     │ true/false                        │
│ common_rules  │ JSON     │ {requires_revision_table:true..}  │
└───────────────┴──────────┴───────────────────────────────────┘
         │                          │
         │ 1:N              ┌───────┘
         ▼                  ▼
┌─────────────────────┐  ┌──────────────────────────────────────┐
│    document_type    │  │        class_structural_profile       │
├──────────────┬──────┤  ├──────────────┬───────┬───────────────┤
│ type_id      │TXT PK│  │ class_id     │TXT FK │ → doc_class   │
│ label        │TXT   │  │ cover_page   │TXT    │required/opt.. │
│ class_id     │TXT FK│  │ revision_tbl │TXT    │               │
│ family_id    │TXT FK│  │ multi_sheet  │BOOL   │               │
│              │nullable│ │ drawing_based│BOOL   │               │
└──────────────┴──────┘  │ section_based│BOOL   │               │
         │                │ callouts     │BOOL   │               │
         │ 0..1:N         │ symbols      │BOOL   │               │
         ▼                │ title_block  │TXT    │               │
┌─────────────────────┐   │ legend       │TXT    │               │
│   document_family   │   │ grid         │TXT    │               │
├──────────────┬──────┤   │ signature_blk│TXT    │               │
│ family_id    │TXT PK│   └──────────────┴───────┴───────────────┘
│ label        │TXT   │
│ discipline   │TXT   │   -- same structure for type_structural_profile --
└──────────────┴──────┘
```

### GROUP 2 SCHEMA SOURCE MAPPING

| DB Table | Schema File | Schema Path | Load Method |
|:---------|:------------|:------------|:------------|
| `doc_class` | `eks_document_type_schema.json` | `document_classes[]` | array iteration, FK resolve ontology_class → `ontology_class.name` |
| `document_type` | `eks_document_type_schema.json` | `document_types[]` | array iteration, FK resolve class_id, family_id (nullable) |
| `document_family` | `eks_document_type_schema.json` | `document_family[]` | array iteration |
| `class_structural_profile` | `eks_document_type_schema.json` | `document_classes[].structural_profile` | 1:1 denormalization from class object |
| `type_structural_profile` | `eks_document_type_schema.json` | `document_types[].structural_profile` | 1:1 denormalization from type object |

**Field provenance — `doc_class`:**

| DB Column | Schema Field | Schema Section |
|:----------|:-------------|:---------------|
| class_id | class_id | document_classes[] |
| label | label | document_classes[] |
| ontology_class | ontology_class | document_classes[] |
| extraction_pro | extraction_profile_ref | document_classes[] |
| cover_bearing | cover_bearing | document_classes[] |
| common_rules | common_rules | document_classes[] |

**Field provenance — `class_structural_profile`:**

| DB Column | Schema Field | Schema Section |
|:----------|:-------------|:---------------|
| class_id | (parent class_id) | document_classes[] |
| cover_page | structural_profile.cover_page | document_classes[] |
| revision_tbl | structural_profile.revision_table | document_classes[] |
| multi_sheet | structural_profile.multi_sheet | document_classes[] |
| drawing_based | structural_profile.drawing_based | document_classes[] |
| section_based | structural_profile.section_based | document_classes[] |
| callouts | structural_profile.callouts | document_classes[] |
| symbols | structural_profile.symbols | document_classes[] |
| title_block | structural_profile.title_block | document_classes[] |
| legend | structural_profile.legend | document_classes[] |
| grid | structural_profile.grid | document_classes[] |
| signature_blk | structural_profile.signature_block | document_classes[] |

**Purpose:** The 4-level classification hierarchy (Class → Type → Family → StructuralProfile)
is the backbone of the system. Every document ingested resolves its class via `project_doc_type`,
then inherits rules, profiles, and element expectations from this group. Schema SSOT:
`eks_document_type_schema.json` §document_classes + §document_types + §document_family.

**Design note:** `type_structural_profile` inherits from `class_structural_profile` per
AGENTS.md §5.13 cross-source alignment — type overrides take precedence over class defaults.
The DB stores both levels; runtime resolution is type-first, class-fallback.


### GROUP 3: TEMPLATES & ELEMENTS (3 tables + 1 junction)

```
┌─────────────────────────────────────────────────────────────┐
│                     document_template                        │
├───────────────────┬──────────┬──────────────────────────────┤
│ template_id       │ TEXT PK  │ twrp_drawing,twrp_pandid..   │
│ label             │ TEXT     │ "TWRP Drawing Template"      │
│ cover_type        │ TEXT     │ A/B/C/D/E/F                  │
│ threshold         │ INT      │ 5 (min detected to pass)     │
│ detection_native  │ TEXT     │ "embedded_structure"         │
│ detection_print   │ TEXT     │ "page1_ocr"                  │
└───────────────────┴──────────┴──────────────────────────────┘
         │                          │
         │ 1:N              ┌───────┘ 1:N
         ▼                  ▼
┌─────────────────────┐  ┌──────────────────────────────────────────┐
│ template_source_    │  │          template_elements (junction)     │
│ quality_score       │  ├──────────────┬───────┬───────────────────┤
├──────────────┬──────┤  │ template_id  │TXT FK │→ document_template│
│ template_id  │TXT FK│  │ element_name │TXT FK │→ element_type.name│
│ cover_type   │TXT   │  │ is_expected  │BOOL   │ true              │
│ quality_score│REAL  │  │ added_in_ver │TEXT   │ "1.3.0"           │
└──────────────┴──────┘  └──────────────┴───────┴───────────────────┘
                                     │
                                     │ N:1
                                     ▼
                         ┌─────────────────────────────────────────┐
                         │             element_type                 │
                         ├──────────────┬──────┬───────────────────┤
                         │ element_name │TXT PK│ cover_page,link.. │
                         │ description  │TEXT  │                   │
                         │ source_method│TEXT  │ regex|table|heuristic│
                         │ phase_2_use  │TEXT  │ "Chunk boundary"  │
                         │ phase_3_use  │TEXT  │ "Section nodes"   │
                         └──────────────┴──────┴───────────────────┘

         ┌──────────────────────────────────────────────────────────┐
         │        element_by_cover_type (junction)                   │
         ├──────────────┬───────┬───────────────────────────────────┤
         │ element_name │TXT FK │ → element_type                    │
         │ cover_type   │TEXT   │ A/B/C/D/E/F                       │
         └──────────────┴───────┴───────────────────────────────────┘
```

**Note:** `expected_by_cover_types` denormalized into junction table for queryability.


### GROUP 3 SCHEMA SOURCE MAPPING

| DB Table | Schema File | Schema Path | Load Method |
|:---------|:------------|:------------|:------------|
| `document_template` | `eks_document_type_schema.json` | `document_templates[]` | array iteration |
| `template_source_quality` | `eks_document_type_schema.json` | `document_templates[].source_quality_score` | 6 rows per template (A..F each) |
| `element_type` | `eks_doc_config.json` | `element_type_registry[]` | array iteration |
| `template_elements` (J) | `eks_document_type_schema.json` | `document_templates[].expected_elements[]` | M:N junction from template.expected_elements |
| `element_by_cover_type` (J) | `eks_doc_config.json` | `element_type_registry[].expected_by_cover_types[]` | M:N junction from element.expected_by_cover_types |

**Field provenance — `document_template`:**

| DB Column | Schema Field | Schema Section |
|:----------|:-------------|:---------------|
| template_id | template_id | document_templates[] |
| label | label | document_templates[] |
| cover_type | cover_type | document_templates[] |
| threshold | detection.print.threshold | document_templates[].detection |

**Field provenance — `element_type`:**

| DB Column | Schema Field | Schema Section |
|:----------|:-------------|:---------------|
| element_name | element_name | element_type_registry[] |
| description | description | element_type_registry[] |
| source_method | source_method | element_type_registry[] |
| phase_2_use | phase_2_use | element_type_registry[] |
| phase_3_use | phase_3_use | element_type_registry[] |

**Purpose:** Templates define structural expectations per document blueprint. The
`expected_elements` list gates which detectors fire. Schema SSOT:
`eks_document_type_schema.json` §document_templates + `eks_doc_config.json` §element_type_registry.


### GROUP 4: DATA COLUMNS & SCORING (4 tables + 1 junction)

```
┌──────────────────────────────────────────────────────────────────┐
│                         data_column                               │
├──────────────────────┬──────────┬────────────────────────────────┤
│ column_name          │ TEXT PK  │ document_number, project_no..  │
│ column_type          │ TEXT     │ code_column, text_column..     │
│ is_calculated        │ BOOL     │ true/false                     │
│ calculation_config   │ JSON     │ {type:filename_segment,pos:0..}│
│ processing_phase     │ TEXT     │ A / B                          │
│ required             │ BOOL     │ true/false                     │
│ scoring_tier         │ TEXT     │ tier1/tier2/tier3/excluded/NULL│
│ native_only          │ BOOL     │ true/false (embedded fields)   │
│ manual_review        │ BOOL     │ true/false                     │
│ description          │ TEXT     │ Human-readable                  │
│ schema_ref           │ TEXT     │ document_type_registry (if any)│
│ validation_config    │ JSON     │ [{type:pattern,pattern:..}]    │
└──────────────────────┴──────────┴────────────────────────────────┘
         │
         │ M:N (which classes claim this column)
         ▼
┌──────────────────────────────────────────────────────────────────┐
│               column_class (junction)                             │
├──────────────┬──────────┬────────────────────────────────────────┤
│ column_name  │ TEXT FK  │ → data_column                          │
│ class_id     │ TEXT FK  │ → doc_class                            │
│ is_active    │ BOOL     │ true (column applies to this class)    │
└──────────────┴──────────┴────────────────────────────────────────┘


┌────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   score_dimension  │    │     score_tier        │    │  score_weight_tier  │
├───────────┬────────┤    ├───────────┬──────────┤    ├──────────┬──────────┤
│ dim_name  │TXT PK  │    │ tier_name │TXT PK    │    │ tier_name│TEXT PK   │
│ weight    │REAL    │    │ min_score │REAL      │    │ weight   │REAL      │
│ sort_order│INT     │    │ max_score │REAL      │    │ label    │TEXT      │
└───────────┴────────┘    │ status    │TEXT      │    └──────────┴──────────┘
                          │ action    │TEXT      │
                          │ sort_order│INT       │
                          └───────────┴──────────┘
```

### GROUP 4 SCHEMA SOURCE MAPPING

| DB Table | Schema File | Schema Path | Load Method |
|:---------|:------------|:------------|:------------|
| `data_column` | `eks_doc_config.json` | `column_processing{}` | object iteration over column names |
| `column_class` (J) | `eks_doc_config.json` | `column_processing.{col}.applies_to_document_types[]` | M:N junction from applies_to list |
| `score_dimension` | `eks_doc_config.json` | `health_scoring.dimensions[]` | array iteration |
| `score_tier` | `eks_doc_config.json` | `health_scoring.score_tiers[]` | array iteration |
| `score_weight_tier` | `eks_doc_config.json` | `health_scoring.weight_tiers{}` | object iteration (key→tier_name, value→weight) |

**Field provenance — `data_column`:**

| DB Column | Schema Field | Schema Section |
|:----------|:-------------|:---------------|
| column_name | (object key) | column_processing |
| column_type | column_type | column_processing.{col} |
| is_calculated | is_calculated | column_processing.{col} |
| calculation_config | calculation_config | column_processing.{col} |
| processing_phase | processing_phase | column_processing.{col} |
| required | required | column_processing.{col} |
| scoring_tier | scoring_tier | column_processing.{col} |
| native_only | native_only | column_processing.{col} |
| manual_review | manual_review | column_processing.{col} |
| description | description | column_processing.{col} |
| validation_config | validation | column_processing.{col} |

**Field provenance — `score_tier` (schema→code 3-level mapping):**

| DB Column | Schema Field | Schema Section |
|:----------|:-------------|:---------------|
| tier_name | name | health_scoring.score_tiers[] |
| min_score | range[0] | health_scoring.score_tiers[] |
| max_score | range[1] | health_scoring.score_tiers[] |
| status | action (first word) | health_scoring.score_tiers[].action |
| action | action (full) | health_scoring.score_tiers[].action |

**Purpose:** The `data_column` table is the central config hub — it defines what metadata
fields exist, which are scored, and which phases populate them. The `column_class` junction
provides class-scoped filtering so a Drawing-class document only expects Drawing-relevant
columns. Schema SSOT: `eks_doc_config.json` §column_processing + §health_scoring.

**Known gap:** `verified_by` column has no `scoring_tier` key → DB stores NULL → runtime treats
as excluded. This is an intentional placeholder (column not yet classified for scoring).


### GROUP 5: ONTOLOGY (4 tables + 1 junction)

```
┌──────────────────────────────────────────────────────────────────┐
│                     ontology_class                                │
├──────────────────┬──────────┬────────────────────────────────────┤
│ name             │ TEXT PK  │ ISO15926_Entity, PumpTag, Drawing..│
│ label            │ TEXT     │ "ISO 15926 Entity"                 │
│ subclass_of      │ TEXT FK  │ → ontology_class.name (nullable)   │
│ tag_type_mapping │ TEXT     │ "AT_EQPMP" (leaf classes only)     │
│ tag_type_aliases │ JSON     │ ["AT_PMP","AT_PUMP"]               │
│ document_type_map│ TEXT     │ "SPC", "DS", "DWG" (doc subclasses)│
│ layer            │ INT      │ 0=root, 1=FunctionalObj, 2=Tagged..│
└──────────────────┴──────────┴────────────────────────────────────┘
         │                          │
         │ N:N              ┌───────┘
         ▼                  ▼
┌─────────────────────┐  ┌──────────────────────────────────────────┐
│ ontology_relation   │  │      onto_class_fragment (junction)       │
├──────────────┬──────┤  ├──────────────┬───────┬───────────────────┤
│ name         │TXT PK│  │ class_name   │TXT FK │→ ontology_class   │
│ inverse      │TEXT   │  │ fragment_name│TEXT   │ item_core,        │
│ transitive   │BOOL   │  │              │       │ process_conditions│
│ symmetric    │BOOL   │  └──────────────┴───────┴───────────────────┘
│ description  │TEXT   │
└──────────────┴──────┘


┌──────────────────────────────────────────────────────────────────┐
│                    ontology_trigger                               │
├──────────────────┬──────────┬────────────────────────────────────┤
│ column_name      │ TEXT PK  │ document_type, asset_tags..        │
│ relation_name    │ TEXT FK  │ → ontology_relation                 │
│ column_fk        │ TEXT FK  │ → data_column                      │
│ priority         │ INT      │ 1=key, 2=auxiliary                  │
└──────────────────┴──────────┴────────────────────────────────────┘
```

### GROUP 5 SCHEMA SOURCE MAPPING

| DB Table | Schema File | Schema Path | Load Method |
|:---------|:------------|:------------|:------------|
| `ontology_class` | `eks_ontology_config.json` | `classes[]` | array iteration with self-ref FK (subclass_of) |
| `ontology_relation` | `eks_ontology_config.json` | `relationships[]` | array iteration |
| `onto_class_fragment` (J) | `eks_ontology_config.json` | `classes[].fragments[]` | M:N junction from class.fragments |
| `ontology_trigger` | `eks_doc_config.json` | `ontology_triggers{}` | object iteration (key→column_name, value.relation→relation_name) |

**Field provenance — `ontology_class`:**

| DB Column | Schema Field | Schema Section |
|:----------|:-------------|:---------------|
| name | name | classes[] |
| label | label | classes[] |
| subclass_of | subclass_of | classes[] |
| tag_type_mapping | tag_type_mapping | classes[] |
| tag_type_aliases | tag_type_aliases | classes[] |
| document_type_map | document_type_mapping | classes[] |
| layer | *(computed)* | derived from subclass_of depth |

**Field provenance — `ontology_trigger`:**

| DB Column | Schema Field | Schema Section |
|:----------|:-------------|:---------------|
| column_name | (object key) | ontology_triggers |
| relation_name | relation | ontology_triggers.{key} |
| priority | priority | ontology_triggers.{key} |

**Purpose:** The ontology layer maps ISO 15926 class hierarchy (35 classes, 18 relations)
into graph edges. Triggers bind ontology relations to data columns — when a column is
populated, the corresponding graph edge is created. Two-schema split: classes/relations in
`eks_ontology_config.json`, trigger bindings in `eks_doc_config.json` (because triggers need
column references). Schema SSOT: `eks_ontology_config.json` + `eks_doc_config.json`
§ontology_triggers. I300/T1.263: relationships 15→16 (added `HAS_STAGE`, inverse `STAGE_OF`,
binding `lifecycle_stage` — the 7th §B4.1 rule). I305/T1.268: relationships 16→18 (added 
`REFERENCES_ASSET`, inverse `REFERENCED_ASSET_BY`, and `HAS_FORMAT`, inverse `FORMAT_OF`);
all 7 §B4.1 trigger relation names now registered — §24 drift resolved.


### GROUP 6: PROCESSING PROFILES (4 tables)

```
┌──────────────────────────────────────────────────────────────────┐
│                    filename_profile                                │
├──────────────────┬──────────┬────────────────────────────────────┤
│ profile_id       │ TEXT PK  │ twrp_standard, default              │
│ profile_type     │ TEXT     │ "filename"                          │
│ description      │ TEXT     │                                     │
│ parser_type      │ TEXT     │ "delimited"                         │
│ separator        │ TEXT     │ "-"                                 │
│ min_segments     │ INT      │ 5                                   │
│ max_segments     │ INT      │ 5 (null=unlimited)                  │
│ rejoin_separator │ TEXT     │ "-"                                 │
│ strip_suffixes   │ JSON     │ ["_Add1","_Add2"]                   │
│ rev_separators   │ JSON     │ ["_rev"]                            │
│ dash_rev_max_len │ INT      │ 3                                   │
│ output_config    │ JSON     │ {document_number_source:..}         │
│ error_subcodes   │ JSON     │ {too_few_segments:"P5-F-V-0004"}    │
│ segment_config   │ JSON     │ [{position:0,maps_to:..}]           │
└──────────────────┴──────────┴────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────────┐
│                  file_property_profile                            │
├──────────────────────┬──────────┬────────────────────────────────┤
│ profile_id           │ TEXT PK  │ pdf_props, docx_props..        │
│ profile_type         │ TEXT     │ "file_property"                 │
│ description          │ TEXT     │                                  │
│ supported_extensions │ JSON     │ ["pdf"]                         │
│ bound_extraction_fk  │ TEXT FK  │ → extraction_profile.profile_id │
│ uses_os_properties   │ BOOL     │ true/false                      │
└──────────────────────┴──────────┴────────────────────────────────┘
         │
         │ 1:N
         ▼
┌──────────────────────────────────────────────────────────────────┐
│                fp_property_mapping                                │
├──────────────┬──────────┬────────────────────────────────────────┤
│ profile_id   │ TEXT FK  │ → file_property_profile                │
│ source_key   │ TEXT     │ author, title, subject..               │
│ maps_to      │ TEXT FK  │ → data_column.column_name              │
│ null_strategy│ TEXT     │ skip / default_value                   │
│ default_val  │ TEXT     │ (if strategy=default_value)            │
│ required     │ BOOL     │ true/false                             │
└──────────────┴──────────┴────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────────┐
│                   extraction_profile                              │
├──────────────────────┬──────────┬────────────────────────────────┤
│ profile_id           │ TEXT PK  │ technip_pdf, technip_docx..    │
│ profile_type         │ TEXT     │ "extraction"                    │
│ parser_class         │ TEXT     │ eks.engine.parsers.pdf_parser..│
│ description          │ TEXT     │                                  │
│ supported_extensions │ JSON     │ ["pdf"]                         │
│ supported_doc_profs  │ JSON     │ ["twrp_standard"]               │
│ requires_ocr         │ BOOL     │ true/false                      │
│ extraction_methods   │ JSON     │ ["parser_metadata",..]          │
└──────────────────────┴──────────┴────────────────────────────────┘


┌──────────────────────────────────────────────────────────────────┐
│                      file_type                                    │
├──────────────┬──────────┬────────────────────────────────────────┤
│ extension    │ TEXT PK  │ pdf, dgn, docx, xlsx, dwg              │
│ display_name │ TEXT     │ "PDF Document"                          │
│ description  │ TEXT     │                                          │
│ mime_type    │ TEXT     │ application/pdf                         │
│ format_cat   │ TEXT     │ print / native                          │
└──────────────┴──────────┴────────────────────────────────────────┘
```


### GROUP 6 SCHEMA SOURCE MAPPING

| DB Table | Schema File | Schema Path | Load Method |
|:---------|:------------|:------------|:------------|
| `filename_profile` | `eks_processing_config.json` | `filename_profiles[]` | array iteration |
| `file_property_profile` | `eks_processing_config.json` | `file_property_profiles[]` | array iteration |
| `fp_property_mapping` | `eks_processing_config.json` | `file_property_profiles[].property_mapping[]` | 1:N from profile |
| `extraction_profile` | `eks_processing_config.json` | `extraction_profiles[]` | array iteration |
| `file_type` | `eks_doc_config.json` | `file_type_registry{}` | object iteration |

**Key field mapping — `fp_property_mapping`:** source_key → maps_to → data_column.column_name.
The chain is: file extension → file_type → file_property_profile (via supported_extensions match) → fp_property_mapping → data_column. Schema SSOT: `eks_processing_config.json` for profiles + `eks_doc_config.json` §file_type_registry.

**Purpose:** Processing profiles define how raw files are parsed. The two sub-chains (filename parse + file property extraction) populate Phase A/B columns. `bound_extraction_fk` on `file_property_profile` links to `extraction_profile`, which specifies the parser class for content extraction.


### GROUP 7: ERRORS & MESSAGES (2 tables)

```
┌──────────────────────────────────────────────────────────────────┐
│                      error_code                                   │
├──────────────┬──────────┬────────────────────────────────────────┤
│ code         │ TEXT PK  │ S-E-S-0101, P1-F-V-0004..              │
│ category     │ TEXT     │ system / data_logic                     │
│ phase        │ TEXT     │ P0 / P1 / P2 / P3 / SYS                │
│ module       │ TEXT     │ File / Metadata / Bootstrap..          │
│ function     │ TEXT     │ Validation / Processing                 │
│ severity     │ TEXT     │ FATAL / ERROR / WARNING                 │
│ description  │ TEXT     │ Human-readable                          │
│ resolution   │ TEXT     │ Suggested fix                           │
│ schema_ref   │ TEXT     │ Related schema if any                   │
│ issue_id     │ TEXT     │ I001-I299 (if tracked)                  │
│ is_active    │ BOOL     │ true/false                              │
└──────────────┴──────────┴────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────────┐
│                    pipeline_message                               │
├──────────────┬──────────┬────────────────────────────────────────┤
│ message_code │ TEXT PK  │ MSG-SYS-001, MSG-PH1-015..             │
│ category     │ TEXT     │ system / phase0 / phase1 / health       │
│ severity     │ TEXT     │ INFO / WARN / ERROR                     │
│ template     │ TEXT     │ Message template with {placeholders}    │
│ triggers_on  │ TEXT     │ Event name that triggers this message   │
│ related_code │ TEXT FK  │ → error_code.code (nullable)            │
│ phase        │ TEXT     │ P0 / P1 / P2 / P3                      │
│ sort_order   │ INT      │ Display ordering                       │
└──────────────┴──────────┴────────────────────────────────────────┘
```

### GROUP 7 SCHEMA SOURCE MAPPING

| DB Table | Schema File | Schema Path | Load Method |
|:---------|:------------|:------------|:------------|
| `error_code` | `eks_error_config.json` | `error_codes{}` (system) + (data_logic) | object iteration over both categories |
| `pipeline_message` | `eks_message_config.json` | `messages{}` | object iteration, FK resolve related_code |

**Schema layering:**
- `eks_error_code_base.json` — defines pattern (S-E-S-01nn, P1-F-V-nnnn, etc.) and format rules. Validates `eks_error_config.json` at load time; not stored directly.
- `eks_error_config.json` — actual 128 codes with descriptions. SSOT for `error_code` table.
- `eks_message_base.json` — defines message format, category structure. Validates `eks_message_config.json`.
- `eks_message_config.json` — actual 52 messages. SSOT for `pipeline_message` table.

**Field provenance — `error_code`:**

| DB Column | Schema Field | Schema Section |
|:----------|:-------------|:---------------|
| code | (object key) | error_codes.system / error_codes.data_logic |
| category | *(derived from parent key)* | system or data_logic |
| phase | phase | error_codes.{category}.{code} |
| module | module | error_codes.{category}.{code} |
| function | function | error_codes.{category}.{code} |
| severity | severity | error_codes.{category}.{code} |
| description | description | error_codes.{category}.{code} |
| resolution | resolution | error_codes.{category}.{code} |
| schema_ref | schema_ref | error_codes.{category}.{code} |
| issue_id | issue_id | error_codes.{category}.{code} |

**Purpose:** Error codes and pipeline messages form the diagnostic subsystem. Each code is
phase-scoped (P0=file, P1=validation/transform, P2=content, P3=ontology, SYS=system).
Messages reference error codes via `related_code` (nullable — some messages are
informational and don't have an error counterpart). Schema SSOT: `eks_error_config.json` +
`eks_message_config.json`; format governance: `eks_error_code_base.json` + `eks_message_base.json`.


### GROUP 8: HEALTH SCORING OUTPUT (2 tables)

```
┌──────────────────────────────────────────────────────────────────┐
│                     health_score                                  │
│              (per-document, one row per run)                      │
├──────────────────────┬──────────┬────────────────────────────────┤
│ id                   │ INT PK   │ auto-increment                  │
│ run_id               │ TEXT FK  │ → batch_run                     │
│ document_id          │ TEXT     │ doc number or UUID              │
│ class_id             │ TEXT FK  │ → doc_class                     │
│ template_id          │ TEXT FK  │ → document_template             │
│ health_score         │ REAL     │ 0.0 - 1.0                       │
│ extract_status       │ TEXT     │ success / partial / failed      │
│ dim_completeness     │ REAL     │ per-dimension scores            │
│ dim_extraction       │ REAL     │                                  │
│ dim_structural       │ REAL     │                                  │
│ dim_source           │ REAL     │                                  │
│ dim_xref             │ REAL     │                                  │
│ dim_consistency      │ REAL     │                                  │
│ missing_columns      │ JSON     │ ["project_title","area"]        │
│ tier1_populated      │ INT      │ count of populated tier1 cols   │
│ tier1_total          │ INT      │ total tier1 cols expected       │
│ scored_at            │ TEXT     │ ISO datetime                    │
└──────────────────────┴──────────┴────────────────────────────────┘
         │
         │ N:1
         ▼
┌──────────────────────────────────────────────────────────────────┐
│                     health_batch                                  │
│                (aggregate per run)                                │
├──────────────────────┬──────────┬────────────────────────────────┤
│ run_id               │ TEXT FK  │ → batch_run                     │
│ avg_document_health  │ REAL     │ mean of all scores              │
│ total_documents      │ INT      │ count                           │
│ status_success       │ INT      │ >=0.70                          │
│ status_partial       │ INT      │ 0.20-0.69                       │
│ status_failed        │ INT      │ <0.20                           │
└──────────────────────┴──────────┴────────────────────────────────┘
```

### GROUP 8 SCHEMA SOURCE MAPPING

| DB Table | Schema Source | Load Method |
|:---------|:-------------|:------------|
| `health_score` | *(no schema)* | Runtime output — populated by `health_scorer.py` per document |
| `health_batch` | *(no schema)* | Runtime output — aggregated by `score_batch()` at pipeline_orchestrator.py:608 |

**Derivation chain (runtime, not schema-loaded):**

```
health_scorer.py loads:
  ├── column_processing (from data_column table)  → computes completeness
  ├── element detection results (from structure_detector) → computes structural_completeness
  ├── extraction confidence (from parser output) → computes extraction_confidence
  ├── template source_quality_score (from document_template) → computes source_quality
  ├── xref references (from cross-reference engine) → computes xref_quality
  └── consistency violations (from validation engine) → computes consistency

Each dimension × weight → health_score [0.0–1.0]
health_score → extract_status (success/partial/failed)
Multiple scores per run → health_batch aggregation
```

**Field provenance — `health_score` (all columns are computed at runtime):**

| DB Column | Source | How Computed |
|:----------|:-------|:-------------|
| health_score | 6 dimensions | weighted sum(dim_score × dim_weight) / sum(weights) |
| extract_status | score_tier table | mapped from health_score range via GROUP 4 score_tier thresholds |
| dim_completeness | data_column + metadata | populated columns / expected columns (by class_id, per tier weight) |
| dim_extraction | parser output | confidence score from extraction engine |
| dim_structural | structure_detector | detected_elements / expected_elements (threshold-gated) |
| dim_source | template_source_quality | lookup from GROUP 3 template_source_quality by template_id |
| dim_xref | cross-reference engine | ratio of resolved xrefs to detected xrefs |
| dim_consistency | validation engine | 1.0 - (violation_count / max_allowed) |
| missing_columns | data_column vs metadata | set difference expected_q - populated_q |
| tier1_populated | data_column + metadata | count of populated tier1 columns |

**Purpose:** Output tables capture per-document and per-batch health assessments. They reference
definition FKs (class_id, template_id, run_id) so scores can be joined back to classification
context for reporting. These tables are **not schema-loaded** — they are populated from the
pipeline run that reads schema-driven config at execution time.


------------------------------------------------------------------------

### GROUP 9: PROJECT DEFINITION (4 tables)

**3-Tier:** `eks_base_schema.json` (definitions) → `eks_project_definition_setup_schema.json` (v1.0.0, I304/T1.267) → `eks_project_definition_config.json` (values)

This group captures per-engineering-project configuration — distinct from GROUP 1's `project`
table which holds system-level runtime metadata. The project_definition stores engineering
conventions, standards, profiles, security policies, and runtime infrastructure bindings.

```
┌──────────────────────────────────────────────────────────────────┐
│                  project_definition (1:1 with project)            │
├────────────────────────────┬──────────┬──────────────────────────┤
│ proj_code                  │ TEXT PK  │ "131101" → project.proj..│
│ project_name               │ TEXT     │ Full engineering proj.   │
│ project_type               │ TEXT     │ "EPC","FEED","PMC"...    │
│ discipline                 │ TEXT FK  │ → discipline.disc_code    │
│ client                     │ TEXT     │ Client/owner name         │
│ contractor                 │ TEXT     │ EPC company name          │
│ region                     │ TEXT     │ Geographic region         │
│ execution_center           │ TEXT     │ Execution office          │
│ status                     │ TEXT     │ active/completed/on-hold  │
│ baseline_revision          │ TEXT     │ e.g. "01","02"            │
│ project_phase              │ TEXT     │ detail_design,procurement │
│ execution_stage            │ TEXT     │ stage-1/stage-2/stage-3   │
│ issue_status               │ TEXT     │ IFC/IFR/IFD               │
│ document_status            │ TEXT     │ ongoing/issued/completed  │
│ planned_completion         │ DATE     │ Target completion date    │
│ drawing_standard           │ TEXT     │ "ISO","ANSI","BS"         │
│ numbering_scheme           │ TEXT     │ "technip_2024" etc        │
│ revision_scheme            │ TEXT     │ "numeric","alpha"         │
│ tag_format                 │ TEXT     │ Tag format specification  │
│ engineering_units          │ TEXT     │ "metric","imperial"       │
│ security_policy            │ TEXT     │ Security policy ref       │
└────────────────────────────┴──────────┴──────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                project_engineering_standard                       │
├──────────────┬──────────┬────────────────────────────────────────┤
│ proj_code    │ TEXT FK  │ → project_definition.proj_code         │
│ standard_cat │ TEXT     │ piping/instrumentation/electrical/     │
│              │          │ mechanical/structural                  │
│ standard_ref │ TEXT     │ "ASME B31.3","IEC 61511"...            │
│ description  │ TEXT     │ Standard description                   │
│ PK: (proj_code, standard_cat)                                    │
└──────────────┴──────────┴────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                project_allowed_discipline                         │
├──────────────┬──────────┬────────────────────────────────────────┤
│ proj_code    │ TEXT FK  │ → project_definition.proj_code         │
│ disc_code    │ TEXT FK  │ → discipline.discipline_code           │
│ PK: (proj_code, disc_code)                                       │
└──────────────┴──────────┴────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                project_revision_pattern                           │
├──────────────┬──────────┬────────────────────────────────────────┤
│ proj_code    │ TEXT PK  │ → project_definition.proj_code         │
│ pattern      │ TEXT     │ Regex pattern for revision validation  │
│ description  │ TEXT     │ e.g. "Numeric 2-digit revision"        │
└──────────────┴──────────┴────────────────────────────────────────┘
```

**Profile references stored as JSON columns** on `project_definition` (not separate FK tables):

| JSON Column | Source Path | Contents |
|:------------|:------------|:---------|
| `document_profile` | `document_profile{}` | filename_pattern, parser, revision, ocr, column_processing |
| `parsing_profile` | `parsing_profile_ref` | Parser configuration pointer |
| `chunking_profile` | `chunking_profile_ref` | Chunking configuration pointer |
| `embedding_profile` | `embedding_profile_ref` | Embedding model/config pointer |
| `retrieval_profile` | `retrieval_profile_ref` | Retrieval strategy pointer |
| `prompt_profile` | `prompt_profile_ref` | LLM prompt configuration pointer |
| `validation_profile` | `validation_profile_ref` | Validation rules pointer |
| `asset_profile` | `asset_profile{}` | Per-project asset configuration |
| `ontology_profile` | `ontology_profile{}` | Per-project ontology configuration |
| `security_profile` | `security_profile{}` | document_classification, access_policy, redaction_policy |
| `runtime_profiles` | `runtime_profiles{}` | storage, vector_db, graph_db, messaging, cache |
| `fragment_required_fields` | `fragment_required_fields{}` | Per-asset-type required field overrides |

### GROUP 9 SCHEMA SOURCE MAPPING

| DB Table | Schema File | Schema Path | Load Method |
|:---------|:------------|:------------|:------------|
| `project_definition` | `eks_project_definition_config.json` | `project_definition.{code}` | per-project object iteration |
| `project_engineering_standard` | `eks_project_definition_config.json` | `project_definition.{code}.engineering_standards` | object key-value flattening |
| `project_allowed_discipline` | `eks_project_definition_config.json` | `project_definition.{code}.engineering_convention.allowed_disciplines[]` | array iteration |
| `project_revision_pattern` | `eks_project_definition_config.json` | `project_definition.{code}.revision_validation` | direct field mapping |

**3-Tier compliance note:** `eks_project_definition_config.json` lacks a dedicated `_setup_schema.json`
file. Its structure is validated by `$ref` calls into `eks_base_schema.json` definitions
(`project_definition_entry_def`, `project_lifecycle_def`, `engineering_convention_def`,
`engineering_standards_def`, `security_profile_def`, `runtime_profiles_def`). This is a
**compliance gap** — per AGENTS.md §9, every config file should have a corresponding
`_setup_schema.json` with `properties`, `required`, and `additionalProperties`.

**Purpose:** Captures all per-project engineering parameters that govern document processing
behavior, validation rules, standards references, and profile routing. One row per engineering
project (currently 131101, 131242). The `document_profile` JSON column stores filename patterns
and processing flags that link directly to GROUP 6 profile tables.

**Field provenance:**

| DB Column | Schema Field | Schema Source |
|:----------|:-------------|:-------------|
| proj_code | project_identity.project_code | `eks_project_definition_config.json` (base def: `eks_base_schema.json#/definitions/project_identity_def`) |
| project_name | project_identity.project_name | (same) |
| project_type | project_identity.project_type | (same) |
| discipline | project_identity.discipline | FK → `discipline.discipline_code` |
| client | project_identity.client | (same) |
| contractor | project_identity.contractor | (same) |
| region | project_identity.region | (same) |
| execution_center | project_identity.execution_center | (same) |
| status | project_identity.status | (same) |
| baseline_revision | project_lifecycle.baseline_revision | (same, base def: `project_lifecycle_def`) |
| project_phase | project_lifecycle.project_phase | (same) |
| execution_stage | project_lifecycle.execution_stage | (same) |
| issue_status | project_lifecycle.issue_status | (same) |
| document_status | project_lifecycle.document_status | (same) |
| planned_completion | project_lifecycle.planned_completion | (same) |
| drawing_standard | engineering_convention.drawing_standard | (same, base def: `engineering_convention_def`) |
| numbering_scheme | engineering_convention.numbering_scheme | (same) |
| revision_scheme | engineering_convention.revision_scheme | (same) |
| tag_format | engineering_convention.tag_format | (same) |
| engineering_units | engineering_convention.engineering_units | (same) |
| security_policy | engineering_convention.security_policy | (same) |


------------------------------------------------------------------------

### GROUP 10: ASSET SYSTEM (6 definition tables + 4 junction tables)

**3-Tier:** `eks_asset_base_schema.json` (14 fragment definitions + `$ref` source) → `eks_asset_setup_schema.json` (structure validation) → `eks_asset_config.json` (actual values)

The asset system defines the data model for engineering plant items (equipment, instruments,
valves, pipelines, etc.). The 3-tier design is fully compliant: `_base` defines reusable
fragments, `_setup` validates the config structure, `_config` holds the type registry and
column normalization maps.

**Definition-layer tables** (loaded from schema config, not runtime):

```
┌──────────────────────────────────────────────────────────────────┐
│                     asset_fragment                                │
├────────────────────┬──────────┬───────────────────────────────────┤
│ fragment_id        │ TEXT PK  │ "item_core","process_conditions" │
│ fragment_name      │ TEXT     │ "Item Core"                       │
│ category           │ TEXT     │ functional / physical             │
│ description        │ TEXT     │ What this fragment models          │
│ field_count        │ INT      │ Number of fields in fragment      │
│ base_def_key       │ TEXT     │ key in eks_asset_base_schema defs │
└────────────────────┴──────────┴───────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                     asset_type                                    │
├────────────────────┬──────────┬───────────────────────────────────┤
│ asset_type_id      │ TEXT PK  │ "centrifugal_pump","control_valve│
│ asset_name         │ TEXT     │ "Centrifugal Pump"                │
│ asset_category     │ TEXT     │ rotating_equipment/inline_comp.  │
│ ontology_class     │ TEXT FK  │ → ontology_class.class_uri (opt)  │
│ doc_template_ref   │ TEXT     │ Document template ref (opt)       │
│ icon_ref           │ TEXT     │ Icon/file reference               │
│ description        │ TEXT     │ Asset type description            │
└────────────────────┴──────────┴───────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 asset_type_fragment (junction)                    │
├────────────────────┬──────────┬───────────────────────────────────┤
│ asset_type_id      │ TEXT FK  │ → asset_type.asset_type_id        │
│ fragment_id        │ TEXT FK  │ → asset_fragment.fragment_id      │
│ is_required        │ BOOL     │ Minimum mandatory fragment        │
│ display_order      │ INT      │ UI display ordering               │
│ PK: (asset_type_id, fragment_id)                                  │
└────────────────────┴──────────┴───────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│              asset_fragment_field (from _base schema $defs)       │
├────────────────────────┬──────────┬───────────────────────────────┤
│ fragment_id            │ TEXT FK  │ → asset_fragment.fragment_id   │
│ field_name             │ TEXT     │ "keytag","design_pressure"..  │
│ field_type             │ TEXT     │ string/number/boolean/array   │
│ is_required            │ BOOL     │ From base schema "required"[] │
│ default_value          │ TEXT     │ JSON-encoded default (nullable)│
│ description            │ TEXT     │ Field purpose (from schema)    │
│ PK: (fragment_id, field_name)                                     │
└────────────────────────┴──────────┴───────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│            asset_column_normalization (from _config)              │
├────────────────────────┬──────────┬───────────────────────────────┤
│ asset_type_id          │ TEXT FK  │ → asset_type.asset_type_id    │
│ source_column_name     │ TEXT     │ Raw input column name (excel) │
│ target_field_path      │ TEXT     │ fragment.field nested path    │
│ transform_rule         │ TEXT     │ direct/case_lower/split..    │
│ pk_priority            │ INT      │ 1=primary, 2=secondary..      │
│ PK: (asset_type_id, source_column_name)                           │
└────────────────────────┴──────────┴───────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                asset_trigger (document + relationship triggers)   │
├──────────────┬──────────┬─────────────────────────────────────────┤
│ trigger_id   │ SERIAL PK│ Auto-increment                         │
│ asset_type_id│ TEXT FK  │ → asset_type.asset_type_id              │
│ trigger_type │ TEXT     │ "field_edge" / "doc_edge"               │
│ source_field │ TEXT     │ Field whose value triggers relationship │
│ edge_type    │ TEXT FK  │ → ontology_relation.relation_uri         │
│ target_type  │ TEXT     │ Target asset type (for field_edge)      │
│ doc_profile  │ TEXT     │ For doc_edge: document profile ref      │
└──────────────┴──────────┴─────────────────────────────────────────┘
```

### The 14 Fragments and Their Purposes

| # | fragment_id | Category | Fields | Models What |
|:--|:------------|:---------|:------:|:------------|
| 1 | `item_core` | functional | 17 | Keytag, tag_type, project_prefix, unit, service_code, description, status, etc. |
| 2 | `process_conditions` | functional | 10 | design_pressure, operating_temperature, flow_rate, test_pressure, etc. |
| 3 | `manufacturer` | physical | 15 | brand, model_number, serial_number, manufacturer company details |
| 4 | `asset_lifecycle` | functional | 19 | ACE fields (Asset Criticality Evaluation), life_span, cost_center, warranty dates |
| 5 | `control_system` | functional | 4 | LCS type, PLC panel, RIO panel |
| 6 | `piping_connection` | physical | 4 | pipe_size_nominal_mm, pipeline_tag_number, lining_material, end_condition |
| 7 | `valve_internals` | physical | 7 | valve_duty, body_material, stem_material, seat_material, locked_position |
| 8 | `actuator` | physical | 29 | Full actuator manufacturer + ACE lifecycle data |
| 9 | `rotating_equipment` | functional | 29 | RPM, efficiency, impeller details, motor electrical specs |
| 10 | `instrumentation` | functional | 30 | ISA instrument ID, sensor specs, alarms (HH/H/L/LL), AMS config |
| 11 | `pipeline_route` | physical | 8 | pipe_material, OD, wall_thickness, from_component, to_component |
| 12 | `specialist_equipment` | physical | 6 | UV lamp, filtration specs, conveyor equipment |
| 13 | `motor_control` | functional | 3 | starter_type, MCC_fed_from, equipment_number |
| 14 | `asset_context` | functional | 5 sub-obj | Project_context, location_hierarchy, system_hierarchy, asset_relationships (13 edge types), document_relationships (5 edge types), lifecycle_context (7 fields) |

### Asset Type Registry (14 registered types + fragment compositions)

| asset_type_id | Fragments (required marked with *) | Ontology Class |
|:--------------|:----------------------------------|:---------------|
| `centrifugal_pump` | item_core*, process_conditions*, manufacturer, asset_lifecycle, rotating_equipment, control_system, motor_control, asset_context | Centrifugal Pump |
| `reciprocating_pump` | item_core*, process_conditions*, manufacturer, asset_lifecycle, rotating_equipment, control_system, motor_control, asset_context | Reciprocating Pump |
| `in_line_instrument` | item_core*, process_conditions*, manufacturer, asset_lifecycle, instrumentation*, asset_context | In-line Instrument |
| `on_off_valve` | item_core*, process_conditions*, manufacturer, valve_internals*, asset_lifecycle, actuator, asset_context | On-Off Valve |
| `control_valve` | item_core*, process_conditions*, manufacturer, valve_internals*, asset_lifecycle, actuator, asset_context | Control Valve |
| `motor_operated_valve` | item_core*, process_conditions*, manufacturer, valve_internals*, asset_lifecycle, actuator, asset_context | Motor Operated Valve |
| `pressure_relief_device` | item_core*, process_conditions*, manufacturer, valve_internals*, asset_lifecycle, asset_context | Pressure Relief Device |
| `check_valve` | item_core*, process_conditions*, manufacturer, valve_internals*, asset_lifecycle, asset_context | Check Valve |
| `pressure_safety_valve` | item_core*, process_conditions*, manufacturer, valve_internals*, asset_lifecycle, asset_context | Pressure Safety Valve |
| `strainer` | item_core*, process_conditions*, manufacturer, piping_connection*, asset_lifecycle, asset_context | Strainer |
| `motor` | item_core*, manufacturer, asset_lifecycle*, rotating_equipment, motor_control, asset_context | Electric Motor |
| `package_unit` | item_core*, process_conditions*, manufacturer, asset_lifecycle, asset_context | Packaged Equipment |
| `pipeline_component` | item_core*, process_conditions*, manufacturer, piping_connection*, asset_lifecycle, asset_context | Pipeline Component |
| `specialist_item` | item_core*, process_conditions*, manufacturer, specialist_equipment*, asset_lifecycle, asset_context | Specialist Equipment |

### GROUP 10 SCHEMA SOURCE MAPPING

| DB Table | Schema File | Schema Path | Load Method |
|:---------|:------------|:------------|:------------|
| `asset_fragment` | `eks_asset_base_schema.json` + `eks_asset_config.json` | `$defs.*` + `fragment_category_registry{}` | Schema introspection (def keys) + config category lookup |
| `asset_type` | `eks_asset_config.json` | `asset_type_registry[]` | array iteration |
| `asset_type_fragment` | `eks_asset_config.json` | `asset_type_registry[].fragments[]` | junction from type-to-fragment arrays |
| `asset_fragment_field` | `eks_asset_base_schema.json` | `$defs.<fragment_id>.properties` | JSON Schema introspection of fragment definitions |
| `asset_column_normalization` | `eks_asset_config.json` | `column_normalization.<type>[]` | nested array iteration per asset type |
| `asset_trigger` | `eks_asset_config.json` | `relationship_triggers[]` + `document_triggers[]` | array iteration merging both trigger arrays |

**3-Tier compliance:** The asset system is the **most complete 3-tier implementation** in EKS:

```
definitions (reusable types)
  └── eks_asset_base_schema.json        →  $id, definitions (14 fragment $defs)
structural validation
  └── eks_asset_setup_schema.json       →  properties, required, additionalProperties
actual values (SSOT)
  └── eks_asset_config.json             →  asset_type_registry, column_normalization, triggers
```

**Purpose:** Provides the complete data model for physical engineering assets extracted from
P&IDs, instrument lists, equipment datasheets, and other plant engineering documents. The
fragment-composition pattern (14 reusable fragments combined into 14 asset types) mirrors a
component-based design, eliminating field duplication across asset types. Column normalization
maps raw Excel/CSV column names to the canonical fragment field paths.

**Runtime tables (NOT in schema, populated during pipeline):**
The following would be populated during pipeline execution and are not loaded from schema config:

| Runtime Table | Purpose |
|:--------------|:--------|
| `asset_item` | Actual equipment items discovered (keytag PK, asset_type_id FK, proj_code FK) |
| `asset_item_fragment_data` | JSON column storing per-fragment field values for each asset item |
| `asset_relationship_instance` | Materialized asset-to-asset relationships from asset_context edges |
| `asset_document_reference` | Links between asset items and source documents (P&IDs, datasheets) |

These are out of scope for the definition-layer table design but are noted for completeness.

### GROUP 11: RUNTIME TABLES (populated during pipeline execution)

I291 (T1.254): canonical family for tables created and populated **during pipeline execution** —
**not** loaded from schema config. Members: `documents`, `document_elements`, `batch_run`,
`health_score`, `health_batch`, `document_reference` (I295) (+ additions tracked by
I293/I294/I297/I298/I299/I301). RE-SCOPED 2026-08-10 (I293/I294/I295): `batch_run`,
`health_score`, `health_batch`, `document_reference` are CREATE tasks — none of these
runtime tables or their CRUD methods exist yet in the engine.

```
┌──────────────────────────────────────────────────────────────────┐
│                     documents (canonical registry)                │
│              (1 row per discovered + validated document)          │
├──────────────────────┬──────────┬────────────────────────────────┤
│ id                   │ VARCHAR  │ UUID PK (system-generated)      │
│ document_number      │ TEXT     │ NOT NULL natural key            │
│ project_code         │ TEXT FK* │ → project_doc_type (declared)   │
│ document_type        │ TEXT FK* │ composite (project_code,local)  │
│ ...54 registry cols  │          │ per Appendix B §B4              │
└──────────────────────┴──────────┴────────────────────────────────┘
         │ 1:N
         ▼
┌──────────────────────────────────────────────────────────────────┐
│                     document_elements                             │
│              (structural elements extracted per document)         │
├──────────────────────┬──────────┬────────────────────────────────┤
│ id                   │ VARCHAR  │ UUID PK (system-generated)      │
│ doc_id               │ VARCHAR  │ FK → documents.id (declared)    │
│ element_type         │ VARCHAR  │ FK → element_type (declared)    │
│ element_id           │ VARCHAR  │ page number or location         │
│ title                │ VARCHAR  │ heading/field/section title     │
│ content              │ TEXT     │ raw text or JSON                │
│ confidence           │ DOUBLE   │ 0.0–1.0                        │
│ source               │ VARCHAR  │ regex/ocr/heuristic/manual      │
│ element_seq          │ INTEGER  │ optional intra-doc order        │
│ created_at           │ TIMESTAMP│ NOT NULL DEFAULT now()          │
└──────────────────────┴──────────┴────────────────────────────────┘
```

**DDL source:** both `documents` and `document_elements` are auto-generated by
`SchemaToDDL` from `eks_doc_base_schema.json` definitions (AGENTS.md §16 — no hardcoded DDL).
Physical DuckDB FK constraints are deliberately **not** emitted (declared_only model, I290/I291):
FK relationships are declared in the schema `registry_relations` list and persisted to the
`_eks_table_relations` manifest (`fk_element_doc` doc_id→documents.id; `fk_element_type`
element_type→element_type.element_type). Enforced in the validation layer.

**GROUP 11 SCHEMA SOURCE MAPPING**

| DB Table | Schema Source | Load Method |
|:---------|:-------------|:------------|
| `documents` | `eks_doc_base_schema.json` → `document_metadata_def` + `project_metadata_def` | SchemaToDDL.generate_documents_ddl() — runtime ingest via register_document() |
| `document_elements` | `eks_doc_base_schema.json` → `document_element_def` | SchemaToDDL.generate_document_elements_ddl() — runtime ingest via store_elements() (StructureDetector.detect() output) |
| `document_reference` | *(no schema)* | Runtime — junction (source/target doc id, 10-type relation enum); CREATE tracked by I295/T1.258 |
| `batch_run` | *(no schema)* | Runtime — CREATE tracked by I293/T1.256 (stage-stat columns + insert_batch/update_batch CRUD) — RE-SCOPED 2026-08-10 |
| `health_score` | *(no schema)* | Runtime — CREATE tracked by I294/T1.257 (document_id UUID declared_only FK→documents.id) — RE-SCOPED 2026-08-10 |
| `health_batch` | *(no schema)* | Runtime — CREATE tracked by I294/T1.257 — `score_batch()` aggregation |


### GROUP 12: PIPELINE RUNTIME TABLES (checkpoint, events, export artifacts)

These tables persist pipeline execution metadata alongside the GROUP 11 tables.
They are created by `_init_db()` via SchemaToDDL and populated during pipeline runtime.

| DB Table | Schema Source | Load Method | Issue / Task |
|:---------|:-------------|:------------|:-------------|
| `pipeline_checkpoint` | *(no schema)* | Runtime — `insert_checkpoint()` at each phase boundary (I298/T1.261) | GROUP 12 |
| `pipeline_event_log` | *(no schema)* | Runtime — `insert_events()` flush at pipeline completion (I299/T1.262) | GROUP 12 |
| `export_artifact` | *(no schema)* | Runtime — `insert_artifact()` after each export file generation (I301/T1.264) | GROUP 12 |

**GROUP 12 SCHEMA SOURCE MAPPING**

| DB Table | Schema Source | Load Method |
|:---------|:-------------|:------------|
| `pipeline_checkpoint` | *(no schema)* | Runtime — `insert_checkpoint(job_id, phase, state_json)` at each phase boundary (see `run_full_pipeline._after()`) |
| `pipeline_event_log` | *(no schema)* | Runtime — `insert_events(job_id, events)` flush at pipeline completion (see `run_full_pipeline` → `_collect_pipeline_events()`) |
| `export_artifact` | *(no schema)* | Runtime — `insert_artifact(job_id, artifact_type, file_path, row_count)` after each export in `_handle_export()` |


## COMPLETE TABLE RELATIONSHIP MAP

> **Moved to [Appendix B.1 — Cross-Relationship Chart §11](appendix_b.1_cross_relationship_chart.md).**
> The full DB-level relationship map (all FK connections across all 42 tables) is maintained in Appendix B.1 as the single source of truth for cross-table relationships. This avoids duplication and drift between documents.


## TABLE SUMMARY

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
│ J01  │ template_elements             │  27  │ → template + element_type         │
│ J02  │ element_by_cover_type         │  30  │ → element_type                    │
├──────┼───────────────────────────────┼──────┼──────────────────────────────────┤
│ T12  │ data_column                   │  42  │ standalone                        │
│ J03  │ column_class                  │ 336  │ → data_column + doc_class         │
│ T13  │ score_dimension               │   6  │ standalone                        │
│ T14  │ score_tier                    │   5  │ standalone                        │
│ T15  │ score_weight_tier             │   3  │ standalone                        │
├──────┼───────────────────────────────┼──────┼──────────────────────────────────┤
│ T16  │ ontology_class                │  35  │ self-ref (subClassOf)             │
│ T17  │ ontology_relation             │  18  │ standalone                        │
│ J04  │ onto_class_fragment           │  12  │ → ontology_class                  │
│ T18  │ ontology_trigger              │   7  │ → data_column,ontology_relation   │
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
├──────┼───────────────────────────────┼──────┼──────────────────────────────────┤
│——    │ **GROUP 12 — PIPELINE RUNTIME** (I298/I299/I301)                  │
├──────┼───────────────────────────────┼──────┼──────────────────────────────────┤
│ T40  │ pipeline_checkpoint           │   N  │ → batch_run_(job_id)             │
│ T41  │ pipeline_event_log            │   N  │ → batch_run_(job_id)             │
│ T42  │ export_artifact              │   N  │ → batch_run_(job_id)             │
└──────┴───────────────────────────────┴──────┴──────────────────────────────────┘

                  42 Tables (39 definition + 3 pipeline runtime)
                  ~1,500 definition rows at rest
                  + 3 persistent export VIEWs (I308): v_discovery_inventory, v_extraction_results, v_review_flags
```


## EXPORT VIEW MODEL (I308)

> **SSOT:** `eks/config/schemas/eks_export_view_config.json` v1.1.0 (values) + `eks_setup_schema.json` `export_views` (shape). The 3 default views below are **persistent DuckDB VIEWs** created in `_init_db()` AFTER the I311 migration gate, rendered by `schema_to_ddl.generate_view_ddl()` (`CREATE OR REPLACE VIEW v_<view_id> AS SELECT <columns> FROM <source_table>` — idempotent, no hardcoded view SQL). View id, columns, order, source table, file base name, sheet name and formats all come from the view config — no literals in engine code.

| View ID (`view_id` = `export_artifact.artifact_type`) | Source Table | Filter | File Base Name (`file_base_name`) | Sheet Name (`sheet_name`) | Formats |
|:---|:---|:---|:---|:---|:---|
| `v_discovery_inventory` | `documents` | `is_latest = TRUE` | `discovery_inventory` | `Discovery` | csv, xlsx |
| `v_extraction_results` | `documents` | `is_latest = TRUE` | `extraction_results` | `Extraction` | csv, xlsx |
| `v_review_flags` | `documents` | `is_latest = TRUE` | `review_flags` | `Review Flags` | csv |

### I308 design resolutions (Q1–Q6)

| # | Resolution |
|:---|:---|
| Q1 | `v_review_flags` reads the **materialized** `documents.flag_reason` column (written by `core/flag_utils` at ingest) — pure projection, no SQL CASE duplication in view DDL. |
| Q2 | All views filter `is_latest = TRUE` via the schema-driven `filter` field (`filter.column` / `filter.value`) — no hardcoded WHERE clauses. |
| Q3 | Missing view config → **fail-fast** raise of registered error code `S-C-S-0312` (`eks_error_config.json`, covered by T1.285) — never silent fallback, never partial export (§16/I274/I276). |
| Q4 | Version-control columns (`is_latest`, `supersedes`, `superseded_by`) are intentionally **excluded** from exports (retained in `documents`); `export_artifact.artifact_type` = `view_id`. |
| Q5 | One `.xlsx` workbook per configured base name, **one worksheet per view** (sheet names = `sheet_name`); CSV per view uses `file_base_name` (I309). |
| Q6 | Each view has a **single source table** (`source_table` = `documents`) — no cross-table joins inside view DDL; column subset + order = `columns[]`. |

### Column provenance

- `discovery_inventory`: 46 ordered columns — project/meta fields first (project_title → verified_by), then file/embedded metadata (file_size → embedded_sheet_count), then document fields (document_title → vendor_name).
- `extraction_results`: 49 ordered columns — adds extraction fields (page_count, extract_status, extraction_confidence, extraction_notes) after asset_tags.
- `review_flags`: 12 ordered columns — review focus: project/doc identity + extract_status/extraction_confidence/extraction_notes + `flag_reason` + ingested_at.

### GAP-016 — two-tier gap RESOLVED

The "definition served JSON-only / DB is a mirror" two-tier interpretation is **closed as RESOLVED** (2026-08-13, I308/T1.272 re-scope): the DB **is** the materialized view — all 53 tables are materialized DuckDB objects driven by `eks_db_config.json`, and the persistent export views are projections over those materialized tables. No "JSON-only definition layer" language remains anywhere in the project (§24 grep clean).


## KEY FOREIGN-KEY CLOSURE PATHS

> **Moved to [Appendix B.1 — Cross-Relationship Chart §12](appendix_b.1_cross_relationship_chart.md).**
> All 7 FK closure path chains (Classification, Column-to-Score, Ontology, File Processing, Error Handling, Project Definition, Asset Type) are maintained in Appendix B.1 as the SSOT for closure path definitions.


## DESIGN NOTES

| Decision | Rationale |
|----------|-----------|
| JSON columns for arrays/configs | `segment_config`, `calculation_config`, `validation_config` etc. are variable-length and schema-defined — normalize only when query-time filtering is required |
| Junction tables for all M:N | `template_elements`, `column_class`, `element_by_cover_type`, `onto_class_fragment`, `asset_type_fragment`, `project_allowed_discipline` — avoids comma-sep strings in columns |
| `class_structural_profile` as 1:1 table | 11 boolean columns on doc_class would be wide; separate table keeps the class table clean and allows version-tracking per field |
| `template_source_quality` as separate table | 6 scores per template × 6 templates = 36 rows; normalized from nested JSON |
| Self-referencing FK on `ontology_class` | `subclass_of → name` — standard adjacency list for tree traversal. `layer` column is denormalized for fast depth queries |
| `health_score`/`health_batch` as output tables | These are populated at runtime, not definition data — but they reference definition FKs so queries can join score↔class↔template |
| `verified_by` scoring_tier = NULL | Treated as `excluded` by code — NULL allows DB-level distinction between "explicitly excluded" and "not yet classified" |
| `project_definition` as 1:1 extension of `project_code` | `project_code` is a simple lookup; `project_definition` holds all per-project engineering config (standards, conventions, profiles). One is a reference table, the other is a rich config entity |
| Profile refs as JSON columns on `project_definition` | 12 profile configurations (parsing, chunking, embedding, retrieval, asset, ontology, security, runtime, etc.) are variable-length nested objects with per-project overrides — JSON preserves the original schema structure |
| `asset_fragment_field` populated from base schema introspection | Field definitions live in `eks_asset_base_schema.json#/definitions` — the loader reads JSON Schema `properties` dicts and flattens them into rows |
| Asset runtime tables deferred | `asset_item`, `asset_item_fragment_data`, `asset_relationship_instance`, `asset_document_reference` are populated during pipeline execution from actual data sources, not from schema config |


## SCHEMA-TO-TABLE MASTER INDEX

One-to-one mapping from every schema JSON file to the DB tables it populates. This is the
loading sequence: schema files are processed in dependency order, loading definition tables
first, then junction tables (which require FK targets to exist).

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
│   └── ontology_triggers{}           →  ontology_trigger      (7 rows)
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
│   └── relationships[]               →  ontology_relation     (16 rows)
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
43. documents           (GROUP 11; FK → doc_class, project_doc_type, document_template, element_type, file_type, discipline, project_code, project_definition)  ← I290
44. document_elements   (GROUP 11; FK → documents.id, element_type)                                                                                            ← I291
45. document_reference  (GROUP 11; FK → documents.id × 2: source_doc_id, target_doc_id)                                                                       ← I295
46. batch_run           (FK → project)                                                                                                                         ← was 43
47. health_score        (FK → batch_run, doc_class, document_template, documents)                                                                              ← was 44
48. health_batch        (FK → batch_run)                                                                                                                       ← was 45
--- pipeline runtime tables (GROUP 12) ---
49. pipeline_checkpoint (GROUP 12; populated at phase boundaries by I298/T1.261)                                                                                   ← new
50. pipeline_event_log   (GROUP 12; flushed at pipeline completion by I299/T1.262)                                                                                  ← new
51. export_artifact      (GROUP 12; tracked after each export by I301/T1.264)                                                                                       ← new
```

> **Runtime Table load-order notes** (I297/T1.260 RESOLVED 2026-08-10): Load order expanded from 45→48 steps to include all GROUP 11 runtime tables. `documents` (I290) inserted at step 43 — all 8 FK targets (doc_class, project_doc_type, document_template, element_type, file_type, discipline, project_code, project_definition) verified loaded before registry. `document_elements` (I291) at step 44 — FK→documents+element_type satisfied. `document_reference` (I295) at step 45 — FK→documents (source_doc_id, target_doc_id) satisfied. Runtime group renumbered: batch_run 43→46, health_score 44→47, health_batch 45→48. **I298/I299/I301 (2026-08-10)**: GROUP 12 tables added at steps 49-51 — no FK dependencies, populated during pipeline execution. Load order 48→51, code execution in `registry.py _init_db()` already creates these tables. Documentation-only alignment.


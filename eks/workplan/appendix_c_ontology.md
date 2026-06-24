# Appendix C — Dynamic ISO 15926-Aligned Ontology

**Version**: 1.8  
**Status**: ✅ APPROVED & IMPLEMENTED  
**Last Updated**: 2026-06-22  

---

## C1. Revision Control & Version History

| Version | Date       | Author      | Summary of Changes                                                                 |
| :------ | :--------- | :---------- | :--------------------------------------------------------------------------------- |
| 1.0     | 2026-06-16 | System      | Initial draft proposing ISO 15926-aligned semantic model.                          |
| 1.1     | 2026-06-18 | Gemini CLI  | Approved & Implemented. Linked ontology classes to asset fragments.                |
| 1.2     | 2026-06-18 | Gemini CLI  | Exhaustive update: listed all classes, relationships, and sub-keys from config.    |
| 1.3     | 2026-06-18 | Gemini CLI  | Revised Class Taxonomy table into a hierarchical view with indentation.            |
| 1.4     | 2026-06-18 | Gemini CLI  | Corrected file structure and added C8: SSOT & Schema-Driven Design summary.        |
| 1.5     | 2026-06-18 | Gemini CLI  | Added specialized engineering relations (Flow, Power, Control, Governance, Set Points) and target classes per AGENTS.md Section 2 & 4. |
| 1.6     | 2026-06-18 | Gemini CLI  | Refined transitivity logic: Hierarchical/directional relations with inverses (CONTROLS, GOVERNED_BY) set to transitive; Physical connectivity (CONNECTS_TO) set to non-transitive. |
| 1.7     | 2026-06-18 | Gemini CLI  | Added Document Class Hierarchy and lifecycle relationships (SUPERSEDES, SUPPLEMENTS, REFERENCES_DOC). Linked Appendix B mapping triggers. |
| 1.8     | 2026-06-22 | opencode    | Added `DataSheet` (subClassOf Specification, document_type_mapping: DS) and `OpsManual` (subClassOf Manual, document_type_mapping: OM) to support T1.35 document type code alignment. Updated C4 class hierarchy table. |

---

## C2. Overview & Reference Model

The EKS Ontology provides a formal semantic model for the engineering knowledge base. It is modeled after the **ISO 15926 Part 2 conceptual model**, separating functional design requirements (topology, tag locations, and process parameters) from physical equipment characteristics (serial numbers, manufacturers, and physical components).

The system is fully dynamic: all classes, inheritance rules, and relationships are defined in `eks_ontology_config.json` and validated against the Triple-File schema library.

---

## C3. Ontology Configuration Metadata

| Sub-Key | Value | Description |
| :--- | :--- | :--- |
| `$schema` | `https://eks.engineering/schemas/eks_ontology_setup_schema.json` | Link to property declarations and inheritance. |
| `$id` | `https://eks.engineering/configs/eks_ontology_config.json` | Canonical URI for the config instance. |
| `version` | `1.6.0` | Current version of the ontology configuration. |
| `title` | `EKS ISO 15926-Aligned Dynamic Ontology` | Descriptive title. |
| `description` | `Dynamic ontology configuration for EKS classes...` | Scope and purpose statement. |

---

## C4. Ontology Class Hierarchy (T-Box)

The following table represents the class taxonomy and its associated fragments/mappings. Indentation in the **Class Name** column indicates inheritance.

| Class Name | Label | Parent Class | Associated Fragments / Tags |
| :--- | :--- | :--- | :--- |
| `ISO15926_Entity` | ISO 15926 Entity | — | Root entity |
| ├─ `FunctionalObject` | Functional Object (Tag) | `ISO15926_Entity` | `item_core`, `process_conditions` |
| │&nbsp;&nbsp;&nbsp;├─ `TaggedEquipment` | Tagged Equipment | `FunctionalObject` | — |
| │&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;└─ `TaggedRotating` | Tagged Rotating Equip | `TaggedEquipment` | `rotating_equipment` |
| │&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├─ `PumpTag` | Pump Tag | `TaggedRotating` | `AT_EQPMP` (Aliases: PMP, PUMP) |
| │&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─ `MotorTag` | Motor Tag | `TaggedRotating` | `AT_MOTOR`, `motor_control` |
| │&nbsp;&nbsp;&nbsp;├─ `TaggedStatic` | Tagged Static Equip | `TaggedEquipment` | — |
| │&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├─ `TankTag` | Tank Tag | `TaggedStatic` | `AT_EQTNK` (Alias: TANK) |
| │&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├─ `VesselTag` | Vessel Tag | `TaggedStatic` | `AT_EQVES` (Alias: VESSEL) |
| │&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─ `HeatExchangerTag` | Heat Exchanger Tag | `TaggedStatic` | `AT_EQEXC` (Aliases: HE_EX, HEAT_EXCHANGER) |
| │&nbsp;&nbsp;&nbsp;├─ `TaggedPiping` | Tagged Piping Component | `FunctionalObject` | `piping_connection` |
| │&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├─ `PipelineTag` | Pipeline Tag | `TaggedPiping` | `AT_PROCESS`, `pipeline_route` |
| │&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├─ `InlineComponentTag` | Inline Component Tag | `TaggedPiping` | `AT_INCOMP` |
| │&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─ `ValveTag` | Valve Tag | `TaggedPiping` | `valve_internals` |
| │&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├─ `ControlValveTag` | Control Valve Tag | `ValveTag` | `AT_CVALVE`, `actuator` |
| │&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├─ `SafetyValveTag` | Safety Valve Tag | `ValveTag` | `AT_PSV` |
| │&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─ `ManualValveTag` | Manual Valve Tag | `ValveTag` | `AT_HVALVE` |
| │&nbsp;&nbsp;&nbsp;├─ `TaggedInstrument` | Tagged Instrument | `FunctionalObject` | `instrumentation` |
| │&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├─ `ControlSystemInstrumentTag` | Control System Inst Tag | `TaggedInstrument` | `AT_INST_CS` |
| │&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─ `FlowInstrumentTag` | Flow Instrument Tag | `TaggedInstrument` | `AT_INST_FLO` |
| ├─ `PhysicalObject` | Physical Object (Equip) | `ISO15926_Entity` | `manufacturer`, `asset_lifecycle` |
| │&nbsp;&nbsp;&nbsp;├─ `PumpUnit` | Pump Unit | `PhysicalObject` | — |
| │&nbsp;&nbsp;&nbsp;├─ `ValveUnit` | Valve Unit | `PhysicalObject` | — |
| │&nbsp;&nbsp;&nbsp;├─ `MotorUnit` | Motor Unit | `PhysicalObject` | — |
| │&nbsp;&nbsp;&nbsp;├─ `InstrumentUnit` | Instrument Unit | `PhysicalObject` | — |
| │&nbsp;&nbsp;&nbsp;├─ `EquipmentUnit` | Equipment Unit | `PhysicalObject` | — |
| │&nbsp;&nbsp;&nbsp;└─ `ActuatorUnit` | Actuator Unit | `PhysicalObject` | — |
| ├─ `InfrastructureObject` | Infrastructure Object | `ISO15926_Entity` | — |
| │&nbsp;&nbsp;&nbsp;├─ `ElectricalPanel` | Electrical Panel (MCC) | `InfrastructureObject` | — |
| │&nbsp;&nbsp;&nbsp;└─ `ControlPanel` | Control Panel (PLC/RIO) | `InfrastructureObject` | — |
| ├─ `GovernanceObject` | Governance Object | `ISO15926_Entity` | — |
| │&nbsp;&nbsp;&nbsp;├─ `EngineeringStandard` | Engineering Standard/Spec | `GovernanceObject` | — |
| │&nbsp;&nbsp;&nbsp;└─ `Originator` | Document Originator (Company) | `GovernanceObject` | — |
| └─ `Document` | Document | `ISO15926_Entity` | — |
| &nbsp;&nbsp;&nbsp;├─ `Drawing` | Engineering Drawing | `Document` | `DWG` |
| &nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;└─ `PID_Drawing` | P&ID Drawing | `Drawing` | `PI-PID` |
| &nbsp;&nbsp;&nbsp;├─ `Specification` | Technical Specification | `Document` | `SPC` |
| &nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;└─ `DataSheet` | Equipment Data Sheet | `Specification` | `DS` |
| &nbsp;&nbsp;&nbsp;├─ `Manual` | Vendor O&M Manual | `Document` | `MAN` |
| &nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;└─ `OpsManual` | Operation Manual | `Manual` | `OM` |
| &nbsp;&nbsp;&nbsp;└─ `Report` | Technical Report | `Document` | `RPT` |

---

## C5. Object Relationships

| Relationship | Inverse | Transitive | Symmetric | Description |
| :--- | :--- | :---: | :---: | :--- |
| `SUBCLASS_OF` | `SUPERCLASS_OF` | ✅ | ❌ | Establishes class hierarchy. |
| `IS_A` | — | ❌ | ❌ | Links instance to its ontology class. |
| `CONNECTS_TO` | — | ❌ | ✅ | Generic physical connectivity (not transitive). |
| `FLOWS_TO` | `FLOWS_FROM` | ✅ | ❌ | Directional process flow (transitive). |
| `INSTALLED_AT` | `HAS_PHYSICAL` | ❌ | ❌ | Links equipment instance (SN) to its tag. |
| `REFERENCED_BY_DWG`| `REFERENCES_ASSET`| ❌ | ❌ | Document references a functional object. |
| `CONTROLS` | `CONTROLLED_BY` | ✅ | ❌ | Hierarchical control logic (transitive). |
| `ENERGIZED_BY` | `POWERS` | ✅ | ❌ | Electrical power distribution (transitive). |
| `GOVERNED_BY` | `VALIDATES_ASSET` | ✅ | ❌ | Hierarchical governance/standards (transitive). |
| `SET_POINT_IN` | `SPECIFIES_SET_POINT` | ❌ | ❌ | Links operating parameter to source doc. |
| `SUPERSEDES` | `SUPERSEDED_BY` | ✅ | ❌ | Links new revision to its predecessor. |
| `SUPPLEMENTS` | `SUPPLEMENTED_BY` | ✅ | ❌ | Links Annexes/Addendums to primary docs. |
| `REFERENCES_DOC` | `REFERENCED_BY_DOC` | ✅ | ❌ | Cross-reference found in document text. |
| `PRODUCED_BY` | `ORIGINATED` | ❌ | ❌ | Links document to Originating company. |
| `FEEDS_FROM` | — | ❌ | ❌ | Legacy material or energy feed relationship. |

---

## C6. Dynamic Mapping Sub-Keys

Each class entry in `eks_ontology_config.json` supports the following sub-keys for dynamic ingestion:

1.  **`name`** (String, Required): The unique identifier for the class in Neo4j.
2.  **`label`** (String, Required): The human-readable name used in UI and LLM headers.
3.  **`subClassOf`** (String, Optional): The parent class for taxonomy-based reasoning.
4.  **`tag_type_mapping`** (String, Optional): The primary AT_ code from the asset registry.
5.  **`document_type_mapping`** (String, Optional): The primary document type code from registry.
6.  **`tag_type_aliases`** (Array, Optional): List of alternative codes (e.g., `AT_PMP` for `AT_EQPMP`).
7.  **`fragments`** (Array, Optional): List of asset schema fragments required by instances of this class.

---

## C7. ISO 15926 Compliance Strategy

Compliance is enforced through the categorization of data into **Functional (Slot)** and **Physical (Unit)** entities.

1.  **A-Box Creation**: When a row in the datadrop contains both a Tag and a Serial Number, the Phase 3 loader creates *two* nodes:
    *   A `FunctionalObject` node (e.g., `PumpTag`) identified by the Tag.
    *   A `PhysicalObject` node (e.g., `PumpUnit`) identified by the Serial Number.
    *   An `INSTALLED_AT` relationship linking them.
2.  **Property Routing**: Properties are routed based on their fragment's category (defined in `eks_asset_config.json`).
    *   `rotating_equipment` properties go to the `FunctionalObject`.
    *   `manufacturer` properties go to the `PhysicalObject`.

This separation allows EKS to track the entire lifecycle of a design slot independently of the physical equipment currently residing in it.

----

## C8. SSOT & Schema-Driven Design (Zero-Code Extensibility)

The EKS architecture strictly adheres to the Single Source of Truth (SSOT) principle by isolating all domain knowledge within the configuration layer. This design ensures that the system can be expanded or modified without requiring updates to the Python source code.

### C8.1. Dynamic Discovery
*   **Agnostic Engine**: The core engine (SchemaLoader, Neo4j Importer) operates on generic `classes` and `relationships` arrays. It does not contain hardcoded strings for specific engineering types.
*   **Runtime Resolution**: Class inheritance, tag type aliases, and fragment associations are resolved at runtime. Adding a new specialized pump type or a new control relationship only requires a JSON entry in `eks_ontology_config.json`.

### C8.2. Automated Integrity
*   **Cross-Schema Validation**: The system automatically enforces consistency between the ontology and the asset schema. The loader verifies that every referenced fragment is defined in the base schema and every project mapping points to a valid ontology class.
*   **SHACL Integration**: Data quality rules (e.g., "every motor must have a starter type") are defined in the schema and validated post-ingestion, ensuring the knowledge graph remains semantically correct as it scales.

### C8.3. Future-Proofing
This configuration-driven approach allows for rapid adaptation to new project requirements:
1.  **New Asset Types**: Define the AT_ code and fragment composition in config.
2.  **New Taxonomy**: Add the ontology class and its `subClassOf` parent in config.
3.  **New Relationships**: Add the relationship name and its inverse logic in config.

The EKS engine will automatically recognize and process these new entities upon the next startup or data reload.

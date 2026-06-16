# Appendix C — Dynamic ISO 15926-Aligned Ontology

**Version**: 1.0  
**Status**: 🔵 PROPOSED — PENDING APPROVAL  
**Last Updated**: 2026-06-16  

---

## C1. Overview & Reference Model

The EKS Ontology provides a formal semantic model for the engineering knowledge base. It is modeled after the **ISO 15926 Part 2 conceptual model**, separating functional design requirements (topology, tag locations, and process parameters) from physical equipment characteristics (serial numbers, manufacturers, and physical components).

To ensure that the system is fully expandable without requiring code changes, the ontology is **database-driven** (schema-driven). All classes, properties, and relationships are defined in configuration files. The Python engine dynamically imports the taxonomy into the Neo4j Graph DB and resolves subclass hierarchies and connectivity paths at runtime by querying the database.

---

## C2. Conceptual Entities (ISO 15926 Part 2 Alignment)

Every node in EKS is classified under one of the following high-level ISO 15926 entities:

1.  **`FunctionalObject` (ClassOfFunctionalObject)**:
    *   **Concept**: Represents the design slot or piping/electrical node (e.g., tag `WSD11-003-P-0101`).
    *   **Focus**: *"What the plant design demands."*
    *   **Properties**: `tag_no`, `unit`, `service`, `design_pressure`, `flow_rate_nominal`.
    *   **Relationships**: Connects to other functional objects via `CONNECTS_TO`.
2.  **`PhysicalObject` (ClassOfPhysicalObject)**:
    *   **Concept**: Represents the physical product installed in a slot (e.g., Serial Number `SN-PUMP-98765`).
    *   **Focus**: *"What the manufacturer delivered."*
    *   **Properties**: `serial_number`, `brand`, `model_number`, `impeller_size`.
    *   **Relationships**: Linked to its tag slot via `INSTALLED_AT` (Tag $\leftarrow$ Physical).
3.  **`Document` (ClassOfInformationRepresentation)**:
    *   **Concept**: Any drawing, datasheet, standard, or procedure.
    *   **Focus**: *"How the information is represented."*
    *   **Properties**: `document_number`, `revision`, `file_path`.
    *   **Relationships**: Linked to tags via `REFERENCED_BY_DWG` or `APPLIES_TO`.

---

## C3. Class Taxonomy (T-Box)

The taxonomy defines the subclass relationships. All asset classes are subclasses of `FunctionalObject` (for tags) or `PhysicalObject` (for equipment units).

```
ISO15926_Entity
├── FunctionalObject (Tag Slots)
│   ├── TaggedEquipment
│   │   ├── TaggedRotating
│   │   │   ├── PumpTag (mapped to AT_EQPMP)
│   │   │   └── MotorTag (mapped to AT_MOTOR)
│   │   └── TaggedStatic
│   │       ├── TankTag (mapped to AT_EQTNK)
│   │       ├── VesselTag (mapped to AT_EQVES)
│   │       └── HeatExchangerTag (mapped to AT_EQEXC)
│   ├── TaggedPiping
│   │   ├── PipelineTag (mapped to AT_PROCESS)
│   │   ├── InlineComponentTag (mapped to AT_INCOMP)
│   │   └── ValveTag
│   │       ├── ControlValveTag (mapped to AT_CVALVE)
│   │       ├── SafetyValveTag (mapped to AT_PSV)
│   │       └── ManualValveTag (mapped to AT_HVALVE)
│   └── TaggedInstrument (mapped to AT_INST_)
│       ├── ControlSystemInstrumentTag (mapped to AT_INST_CS)
│       └── FlowInstrumentTag (mapped to AT_INST_FLO)
│
├── PhysicalObject (Equipment Instances)
│   ├── PumpUnit
│   ├── ValveUnit
│   └── MotorUnit
│
└── Document
    ├── EngineeringDocument (Specs, Procedures, Checklists)
    └── Drawing (P&ID Drawings, Isometric Drawings, Layouts)
        └── P_and_ID
```

---

## C4. Object Properties & Relationship Registry

Relations between entities are registered in `eks_ontology.json` and loaded as Neo4j relationship types.

| Relationship | Source Class (Domain) | Target Class (Range) | Characteristics | ISO 15926-2 Equivalent | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `SUBCLASS_OF` | `ISO15926_Entity` | `ISO15926_Entity` | Transitive | `Specialization` | Establishes class hierarchy. |
| `IS_A` | Instance Node | `OntologyClass` | Non-transitive | `Classification` | Links instance to its taxonomy class. |
| `CONNECTS_TO` | `FunctionalObject` | `FunctionalObject` | Transitive, Symmetric | `Connection` | Connectivity between tags (unlimited depth). |
| `INSTALLED_AT` | `PhysicalObject` | `FunctionalObject` | Functional | `Installation` | Links equipment unit (SN) to tag. |
| `REFERENCED_BY_DWG`| `FunctionalObject` | `Drawing` | Symmetric | `Representation` | Shows which drawing contains a tag. |
| `SUPERSEDES` | `Document` | `Document` | Transitive, Asymmetric | `Succession` | Document revision chain. |
| `CONTROLS` | `TaggedInstrument` | `FunctionalObject` | Non-transitive | `Control` | Signal control relationship. |

---

## C5. Schema-Driven Implementation (Zero-Code Extension)

To ensure new classes, properties, and relationships can be added without modifying Python code, EKS follows these design rules:

### C5.1 Schema Config Files
The ontology is defined in `eks/config/eks_ontology.json`, which validates against `eks/config/eks_ontology_schema.json` (created in Phase 1).

### C5.2 Ingestion (T-Box Importer)
At system startup, the Neo4j Graph Store runs `TBoxImporter` which:
1.  Clears old ontology class nodes: `MATCH (c:OntologyClass) DETACH DELETE c`.
2.  Creates nodes for all classes in `eks_ontology.json`: `CREATE (:OntologyClass {name: $name, label: $label})`.
3.  Creates subclass relationships: `MATCH (c:OntologyClass {name: $name}), (p:OntologyClass {name: $parent}) CREATE (c)-[:SUBCLASS_OF]->(p)`.

### C5.3 Dynamic Instance Mapping (A-Box)
When loading assets from Excel datadrop:
1.  The loader queries the class mapped to the row's `TAG_TYPE` (e.g. `AT_EQPMP` $\rightarrow$ `PumpTag`).
2.  The node is created using the dynamic class name as its Neo4j label: `CREATE (n:PumpTag {tag_no: $tag_no, ...})`.
3.  An instance-to-ontology relationship is created: `MATCH (n:PumpTag {tag_no: $tag_no}), (c:OntologyClass {name: 'PumpTag'}) CREATE (n)-[:IS_A]->(c)`.
4.  Physical objects are dynamically created and linked via `INSTALLED_AT` when serial numbers are present.

### C5.4 Dynamic Query Expansion (No Python Lists)
When executing query filters or relationship expansions, the retrieval engine queries the database to find subclasses dynamically:
```cypher
MATCH (parent:OntologyClass {name: $target_class})<-[:SUBCLASS_OF*0..10]-(subClass:OntologyClass)
RETURN collect(subClass.name) as sub_labels
```
The returned labels are used as target nodes in the subsequent instance search, guaranteeing that new subclasses added to the JSON config are immediately active in the query pipeline.

---

## C6. Unlimited Connectivity Traversal

Tracing physical flow paths is performed using the transitive `CONNECTS_TO` property at unlimited depth.

### C6.1 Unlimited Connectivity Query
```cypher
MATCH path = (start:FunctionalObject {tag_no: $tag_no})-[:CONNECTS_TO*]->(connected:FunctionalObject)
RETURN 
    [node in nodes(path) | node.tag_no] as flow_path,
    connected.tag_no as tag,
    labels(connected)[0] as type
```

### C6.2 Database Optimizations for Unlimited Traversals
To ensure performance:
1.  **Unique Constraints**: Unique constraint on `tag_no` guarantees fast index seeks at the root node.
2.  **Directional Edges**: A `direction` property on the `CONNECTS_TO` edge (e.g., `inlet`, `outlet`) or using incoming/outgoing edges enables pruning path traversals.
3.  **Cypher Cycle Check**: Neo4j automatically ensures relationships are not traversed twice within a single path, preventing infinite loops.

---

## C7. Ontology Configuration File (`eks_ontology.json`)

Located at `eks/config/eks_ontology.json`, this is the single source of truth for taxonomy and relationships.

```json
{
    "$schema": "https://eks.engineering/schemas/eks_ontology_schema.json",
    "$id": "https://eks.engineering/configs/eks_ontology.json",
    "version": "1.1.0",
    "title": "EKS ISO 15926-Aligned Dynamic Ontology",
    "classes": [
        { "name": "ISO15926_Entity", "label": "ISO 15926 Entity" },
        { "name": "FunctionalObject", "label": "Functional Object (Tag)", "subClassOf": "ISO15926_Entity" },
        { "name": "PhysicalObject", "label": "Physical Object (Equipment)", "subClassOf": "ISO15926_Entity" },
        { "name": "Document", "label": "Document", "subClassOf": "ISO15926_Entity" },
        
        { "name": "TaggedEquipment", "label": "Tagged Equipment", "subClassOf": "FunctionalObject" },
        { "name": "TaggedRotating", "label": "Tagged Rotating Equipment", "subClassOf": "TaggedEquipment" },
        { "name": "TaggedStatic", "label": "Tagged Static Equipment", "subClassOf": "TaggedEquipment" },
        
        { "name": "PumpTag", "label": "Pump Tag", "subClassOf": "TaggedRotating", "tag_type_mapping": "AT_EQPMP" },
        { "name": "MotorTag", "label": "Motor Tag", "subClassOf": "TaggedRotating", "tag_type_mapping": "AT_MOTOR" },
        { "name": "TankTag", "label": "Tank Tag", "subClassOf": "TaggedStatic", "tag_type_mapping": "AT_EQTNK" },
        { "name": "VesselTag", "label": "Vessel Tag", "subClassOf": "TaggedStatic", "tag_type_mapping": "AT_EQVES" },
        { "name": "HeatExchangerTag", "label": "Heat Exchanger Tag", "subClassOf": "TaggedStatic", "tag_type_mapping": "AT_EQEXC" },
        
        { "name": "TaggedPiping", "label": "Tagged Piping Component", "subClassOf": "FunctionalObject" },
        { "name": "PipelineTag", "label": "Pipeline Tag", "subClassOf": "TaggedPiping", "tag_type_mapping": "AT_PROCESS" },
        { "name": "InlineComponentTag", "label": "Inline Component Tag", "subClassOf": "TaggedPiping", "tag_type_mapping": "AT_INCOMP" },
        { "name": "ValveTag", "label": "Valve Tag", "subClassOf": "TaggedPiping" },
        { "name": "ControlValveTag", "label": "Control Valve Tag", "subClassOf": "ValveTag", "tag_type_mapping": "AT_CVALVE" },
        { "name": "SafetyValveTag", "label": "Safety Valve Tag", "subClassOf": "ValveTag", "tag_type_mapping": "AT_PSV" },
        { "name": "ManualValveTag", "label": "Manual Valve Tag", "subClassOf": "ValveTag", "tag_type_mapping": "AT_HVALVE" },
        
        { "name": "TaggedInstrument", "label": "Tagged Instrument", "subClassOf": "FunctionalObject", "tag_type_mapping": "AT_INST_" },
        { "name": "ControlSystemInstrumentTag", "label": "Control System Instrument Tag", "subClassOf": "TaggedInstrument", "tag_type_mapping": "AT_INST_CS" },
        { "name": "FlowInstrumentTag", "label": "Flow Instrument Tag", "subClassOf": "TaggedInstrument", "tag_type_mapping": "AT_INST_FLO" }
    ],
    "relationships": [
        { "name": "SUBCLASS_OF", "inverse": "SUPERCLASS_OF", "transitive": true },
        { "name": "IS_A", "transitive": false },
        { "name": "CONNECTS_TO", "symmetric": true, "transitive": true },
        { "name": "INSTALLED_AT", "inverse": "HAS_PHYSICAL", "transitive": false },
        { "name": "REFERENCED_BY_DWG", "symmetric": false, "inverse": "REFERENCES_ASSET" },
        { "name": "CONTROLS", "transitive": false },
        { "name": "FEEDS_FROM", "transitive": false }
    ]
}

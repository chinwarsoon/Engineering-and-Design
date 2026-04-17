# Guide: URI Registry & Naming

The DCC Pipeline uses a **Unified Schema Registry** (agent_rule.md Section 2.4). This system uses permanent URIs as "Digital IDs" for schemas, separating the schema's identity from its physical location on disk.

---

## The Base URI
All internal schemas must use the following base URI:
`https://dcc-pipeline.internal/schemas/`

---

## Naming Standards

To ensure successful recursive resolution, follow these naming conventions:

### 1. File Names
- **Format**: Use `snake_case` with underscores.
- **Suffix**: Always end with `.json`.
- **Example**: `department_schema.json`

### 2. Schema `$id`
- **Format**: The `$id` must match the file stem (filename without extension).
- **Format**: `https://dcc-pipeline.internal/schemas/{file_stem}`
- **Example**: `"$id": "https://dcc-pipeline.internal/schemas/department_schema"`

### 3. Cross-References (`$ref`)
- **Format**: Use the absolute URI of the target schema.
- **Example**: `{"$ref": "https://dcc-pipeline.internal/schemas/facility_schema"}`

---

## Why Use URIs instead of Paths?

| Feature | Using Paths | Using URIs |
| :--- | :--- | :--- |
| **Portability** | Fails if folders are moved. | Works regardless of location. |
| **Clarity** | Ambiguous (relative to what?). | Explicit and globally unique. |
| **Registry** | Requires complex lookup logic. | Handled automatically by `RefResolver`. |

---

## How URI Resolution Works

1.  **Scanning**: During initialization, the `RefResolver` scans all registered schema files.
2.  **Mapping**: It reads the `$id` field from each file and maps that URI to the physical file path.
3.  **Lookup**: When a `$ref` with a URI is encountered, the resolver checks its internal registry and loads the corresponding file.

---

## Handling Fragments and Pointers

The URI system supports standard JSON Pointers:

### Internal Definitions
```json
{"$ref": "https://dcc-pipeline.internal/schemas/project_setup_base#/definitions/file_entry"}
```

### Deep Property Access
```json
{"$ref": "https://dcc-pipeline.internal/schemas/dcc_register_config#/properties/parameters"}
```

---

## Maintenance

### Updating a URI
If you change the `$id` in a schema file:
1.  Search for all files referencing the old URI.
2.  Update them to the new URI.
3.  Clear the disk cache (`rm -rf dcc/.cache/schemas`).

### Adding a New Schema
1.  Choose a unique file name using `snake_case`.
2.  Set the `$id` to the matching internal URI.
3.  Register the file in `project_config.json`.

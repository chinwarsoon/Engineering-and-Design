# Architecture: Register Decoupling Strategy

Decoupling is an architectural pattern used to isolate schema fragments into specialized layers. This strategy ensures maintainability, reusability, and strict validation across the DCC Pipeline.

---

## 1. The Base/Setup/Config Pattern

Every major schema in the system (e.g., Project Setup, DCC Register) is split into three distinct files:

### Layer 1: Base (Definitions)
- **Purpose**: Contains reusable definitions (`definitions` or `$defs`).
- **Content**: Object structures, enum values, and validation patterns.
- **Example**: `dcc_register_base.json`.
- **Constraint**: Should not contain actual properties; only definitions to be referenced elsewhere.

### Layer 2: Setup (Properties)
- **Purpose**: Defines the schema structure (the "what").
- **Content**: Property names, types, and references to the Base layer.
- **Example**: `dcc_register_setup.json`.
- **Constraint**: Acts as the validator for the Config layer.

### Layer 3: Config (Data)
- **Purpose**: Contains the actual data (the "instance").
- **Content**: Real-world configuration values.
- **Example**: `dcc_register_config.json`.
- **Constraint**: Must reference its validator via the `$schema` key.

---

## 2. Benefits of Isolation

| Benefit | Description |
| :--- | :--- |
| **No Repetition** | Shared definitions (like `validation_rule_entry`) are defined once in a Base file and referenced by many Setup files. |
| **Version Control** | Data changes frequently (Config), while structures (Setup) and definitions (Base) remain stable. |
| **Validation Loops** | The `SchemaLoader` can recursively validate that a Config file matches its Setup schema, which in turn matches the Base definitions. |

---

## 3. Implementation in Schema Engine

The `RefResolver` supports this architecture by resolving the cross-file references required for decoupling:

1.  **URI Resolution**: Allows a Setup file to point to a Base file using an absolute internal URI.
2.  **Pointer Resolution**: Allows a Setup file to pull a specific definition from the Base file (e.g., `base_schema#/definitions/my_type`).
3.  **Recursive Load**: The `SchemaLoader` ensures that when a Setup schema is requested, its Base dependency is automatically pulled into the cache first.

---

## 4. Best Practices

- **Atomic Fragments**: Keep Base definitions small and focused.
- **One-to-One Matching**: Ensure every Config file has a corresponding Setup schema.
- **Relative Links**: Avoid them. Always use absolute `https://dcc-pipeline.internal/schemas/` URIs to link layers.
- **Circular Check**: Do not allow a Base file to reference its own Setup file (defines a cycle).

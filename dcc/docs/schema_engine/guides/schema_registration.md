# Guide: Schema Registration

Strict registration is a core engineering mandate (agent_rule.md Section 2.3). It ensures that the pipeline only uses authorized schemas and that all dependencies are explicitly managed.

---

## The Registration Source
All schemas must be registered in the **Project Configuration** file:
`dcc/config/schemas/project_config.json`

There are two ways to register a schema: **Explicit Listing** and **Auto-Discovery**.

---

## 1. Explicit Registration
Use this for core schemas that are foundational to the project.

### Format in `project_config.json`:
```json
"schema_files": [
    {
        "filename": "project_setup_base.json",
        "required": true,
        "description": "Base definitions",
        "category": "base_schema"
    }
]
```

### When to Use:
- The schema is required for the pipeline to start.
- The schema has a fixed, well-known filename.
- You want to enforce that the file **must exist** (via the `required` flag).

---

## 2. Auto-Discovery Rules
Use this for engine-specific schemas or categorized fragments that may grow in number.

### Format in `project_config.json`:
```json
"discovery_rules": [
    {
        "pattern": "*_schema.json",
        "directory": "config/schemas",
        "recursive": false,
        "auto_register": true,
        "category": "validation_schema"
    }
]
```

### How it Works:
The `RefResolver` scans the specified `directory` for files matching the `pattern`.
- **Recursive**: If `true`, it will walk through all subdirectories.
- **Auto-Register**: If `true`, any matching file is automatically added to the registry as if it were explicitly listed.
- **Exclude Patterns**: You can prevent certain files from being registered:
  `"exclude_patterns": ["**/backup/**"]`

### When to Use:
- You have many similar schemas (e.g., error codes for different modules).
- You want to add new schemas by simply dropping them into a folder without updating the config file.

---

## Registration Workflow

1.  **Creation**: Create your new JSON schema file.
2.  **Naming**: Use underscores (e.g., `my_new_schema.json`).
3.  **Discovery Check**: Check if your file matches an existing `discovery_rule`.
4.  **Manual Add**: If it doesn't match a rule, add it to the `schema_files` array.
5.  **Verification**: Run the audit tool to ensure registration is successful:
    ```bash
    python3 dcc/test/check_registration.py
    ```

---

## Troubleshooting Registration

### "Schema Not Registered" Error
If you get this error during a `load_recursive` call, it means:
1.  The file is not in `schema_files`.
2.  The file doesn't match any `discovery_rules`.
3.  The directory in the discovery rule is incorrect.

### Naming Mismatches
The registry uses the **file stem** (filename without `.json`) as the registration key.
- File: `facility_schema.json` -> Key: `facility_schema`
- Ensure your URIs match this key: `https://.../schemas/facility_schema`

---

## Agent Rule Compliance
- **Rule 2.3**: Mandatory cataloging.
- **Rule 2.8**: Use of pattern-based discovery for organization.

---
description: Schema design standards, inheritance patterns, and registry rules
mode: subagent
---

# Schema Rules
1. always check and ensure compliance with schema standard.
2. when create a schema, always consider a flat schema structure, use array of objects, and avoid using array of list.
3. use project_setup_base.json as base schema to store "definitions", project_setup.json to store "properties", and use project_config.json to store actual items. Similarly, 'definitions' will in base schema, 'properties' in setup schema, and actual values in config schema. always check one to one match in different schema files.
4. schema loader must support different types of $ref (string, object, nested object, recursive, etc.). also use Unified Schema Registry (URIs) giving every schema a unique, permanent "Digital ID" that the engine can find regardless of where the file actually sits on the drive.
5. adopt schema fragment pattern for better maintainability and reusability always.
6. implement inheritance (base + project) pattern for better maintainability and reusability always.
7. use 'Definitions' for repetitive objects.
8. use pattern-based discovery rule for organizing schema files.
9. set additional property false for important property control.
10. define 'required' for properties if applicable.

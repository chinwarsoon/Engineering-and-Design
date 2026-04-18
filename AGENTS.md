# Engineering-and-Design

## Run the App

```bash
cd dcc && python3 serve.py
# Serves on port 5000, serves ui/Excel Explorer Pro working.html at /
```

## Key Directories

- `dcc/` — Main application
- `dcc/workflow/` — Core processing logic (schema_engine, processor_engine, initiation_engine)
- `dcc/data/` — Excel datasets
- `dcc/config/schemas/` — JSON schemas
- `dcc/test/` — Test scripts
- `dcc/output/` — Processing outputs and logs
- `dcc/docs/` — Architecture documentation
- `dcc/workplan/` — Implementation plans and reports

## Testing

Tests are standalone Python scripts using unittest, not pytest:

```bash
cd dcc && python3 test/test_column_mapper.py
cd dcc && python3 test/test_schema_validation.py
cd dcc && python3 test/test_universal_document_processor_document_type_validation.py
```

All test files add `workflow/` to sys.path.

## Critical Conventions

1. **Always plan and wait for approval before making changes**
2. **Before deleting files, archive to respective archive folders first**
3. **When issues arise, log them and test before proceeding**

## Column Processing Priority

1. **Priority 1 (Metadata):** Project_Code, Project_Name, Project_Number, Department, Discipline, Section_Category, Submission_Session, Submission_Date — fill first, bounded forward fill
2. **Priority 2 (Transactional):** Document_ID, Document_Number, Document_Revision, Review_Return_Actual_Date — validate, no aggressive fill
3. **Priority 3 (Calculated):** Submission_Closed, Resubmission_Required, Days_Overdue — always recalculate, never manual

## Schema Standards

- Use flat schema structure with array of objects
- Use project_setup_base.json for definitions, project_setup.json for properties, project_config.json for values
- Schema loader must support $ref (string, object, nested, recursive)
- Use Unified Schema Registry (URIs) for permanent schema IDs

## Debug/Logging

- Tiered logging: level 0 (silent), level 1 (status), level 2 (warning), level 3 (trace)
- Use Debug Object, save to output/debug_log.json, pass to format_report
- Include function name in all print messages

## File Patterns to Ignore

- Backup folders (*/archive/*)
- Dot folders (.*)
- Dot files (.*)
- Test output files (*.txt in test folders)
- Markdown docs (*.md)

## Dependencies

Managed via `dcc.yml` (Conda format). Key packages: pandas, openpyxl, numpy, jsonschema, matplotlib, seaborn.
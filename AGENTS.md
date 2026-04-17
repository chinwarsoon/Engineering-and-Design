# Engineering-and-Design

## Run the App

```bash
python3 serve.py
# Serves on port 5000, serves dcc/Excel Explorer Pro working.html at /
```

## Key Directories

- `dcc/` — Main application
- `dcc/data/` — Excel datasets (document_type.xlsx, discipline_type.xlsx, etc.)
- `dcc/config/schemas/` — JSON schemas
- `dcc/tools/` — Python processing scripts
- `dcc/test/` — Test scripts and outputs

## Testing

```bash
# Run tests via pytest
cd dcc && python -m pytest test/ -v

# Or run specific test
python dcc/test/test_column_mapper.py
```

## Critical Conventions (from agent_rule.md)

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
- Use Debug Object, save to debug_log.json, pass to format_report
- Include function name in all print messages

## File Patterns to Ignore

- Backup folders (*/archive/*)
- Dot folders (.*)
- Dot files (.*)
- Test output files (*.txt in test folders)
- Markdown docs (*.md)
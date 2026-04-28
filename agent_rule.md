# Important:
1. always plan and wait for approval to make changes.
2. when delete any files, always archive them into respectie archive folders first.
3. whenever there is an issue, always log the issue, test, and update to logs under log folder.

# Project Folders:
1. `dcc folder` folder is for Document Control project.
2. `code_tracer` folder is for static and dynamic pyhton code tracing project.
3. `release` folder is for released versions for different packages.
4. Each project folder will have the followign subfolders:
- `archive` folder for archiving purpose
- `config` folder for configuration files, and schema files.
- `data` folder for data input files.
- `output` folder for data output files.
- `test` folder for testing purpose.
- `ui` folder for user interface files.
- `enginge` or `workflow` folder for code engines and modules.
- `log` folder for recording issues, updates and tests.
- `docs` folder for user and developer instructions and documentation.
- `workplan` folder for coding planning and reports.

# Section 1. data columns:
1. sort column is not allowed before forward fill.
2. forward fill shall not overwrite existing values.
3. always check if there are duplicate columns in data frame.
4. always check and define data column priority when processing data:
   - priority 1: meta data columns. These columns must be processed first because they define the "who" and "where" of the data. They are the only columns safe for broad null-handling (like global forward fills) because they represent static metadata that rarely changes within a session.
     - Project Identification: Project_Code, Project_Name, Project_Number.
     - Organizational Metadata: Department, Discipline, Section_Category.
     - Source Tracking: Submission_Session, Submission_Date.
     - Constraint: Null-handling for these columns must be "Bounded" (e.g., forward fill stops if the row index jumps significantly or a new file starts).
   - priority 2: Relational Keys & Transactional Data. These columns are the "Live" data points. They must be mapped and cleaned before any logic is applied, but they should not be subject to aggressive forward filling, as their values are unique to specific submission events.
     - Unique Identifiers: Document_ID, Document_Number, Document_Title.
     - Revision Control: Document_Revision, Submission_Session_Revision.
     - Workflow Dates: Review_Return_Actual_Date, Review_Due_Date.
     - Constraint: If Document_Revision is null, it should trigger a specific lookup against the database or be flagged as a validation error rather than being blindly filled.
   priority 3: Derived Logic & Status Flags (Calculations). These columns are processed last because they depend entirely on the values established in Priority 1 and 2. They are "is_calculated: true" fields.
     - Closing Logic: Submission_Closed (Depends on Latest_Approval_Code and Latest_Submission_Date).
     - Actionable Status: Resubmission_Required (Depends on whether Review_Return_Actual_Date is null and if the row is the latest revision).
     - Timeline Metrics: Review_Duration, Days_Overdue.
     - Constraint: These columns must never have manual data; they should be recalculated every time the pipeline runs to ensure the registry reflects the most recent submission history.
5. Processing Sequence
  - Impute Priority 1: Fill missing Project/Session info to "anchor" the rows.
  - Validate Priority 2: Ensure every document has an ID and a Revision.
  - Calculate Priority 3: Run the logic from submission_closed_schema.json to determine which rows are RESUBMITTED, PEN, or YES/NO.

# Section 2. Schema:
1. always check and enure compliance with schema standard.
2. when create a schema, alway consider a flat schema structure, use array of objects, and avoid using array of list.
3. use project_setup_base.json as base schema to store "definitions", project_setup.json to store "properties", and use project_config.json to store actual items. Similarly, 'definitions' will in base schema, 'properties' in setup schema, and actual values in config schema. always check one to one match in different schema files.
4. schema loader must support different types of $ref (string, object, nested object, recursive, etc.). also use Unified Schema Registry (URIs) giving every schema a unique, permanent "Digital ID" that the engine can find regardless of where the file actually sits on the drive.
5. adopt schema fragment pattern for better maintainability and reusability always.
6. implement inheritance (base + project) pattern for better maintainability and reusability always.
7. use 'Definitions' for repetitive objects.
8. use pattern-based discovery rule for organizing schema files.
9. set additional property false for important property control.
10. define 'required' for properties if applicable.


# Section 3. files and context:
1. ignore files under any backup folder.
2. ignore dot .folders and dot .files.
3. ignore md files.
4. ignore test folders

# Section 4. Moudle design:
1. always consider module design for functions and classes.

# Section 5. Function coding:
1. For each function, add standardized docstrings explianing the function, and breadcrumb comments tracing parameters.

# Section 6. Debug and logging:
1. Always use tiered logging strategy.
   - categorized logging for different severity levels
   - level 0: silent / only errors; level 1: status/info, level 2: warning, level 3: error
   - level 1: status/info; to show milestone progress / high-level workflow status
   - level 2: warning/debug; to show warnings / detailed information for debugging / variable values and path resolutions
   - level 3: trace; deep technical info, like OS specific path slashes, JSON raw extraction etc.
2. Use Debug Object, collect all debug info into a single results dictionary. Save it to a debug_log.json file. Pass it to format_report function. And print it at the end of the workflow.
3. Use structured trace table to track parameter flow, resolved values, soruce, and status. add timestamp or duration field for each step in the table.
4. Indent print messages per hierarchy level of calling functions. Use a global depth counter that increments when entering a function and decrements on exit.
5. Always include function name or module name, and calling context in warning/debug/trace print messages.
6. Trace global parameters, log the state before and after a major transformation.
7. Always implement fail-fast metadata in functions to stop execution on critical errors.
8. Record system snapshot for level 1 logging.

# section 7. documentation
1. overall summary
2. content index
3. key features
4. documentation map
5. quick start and mermaid workflow/chart
6. module/function structure
7. list of functions
8. I/O table
9. Global Parameter Trace Matrix
10. details of each function/module
11. debugging and troubleshooting
12. usage examples
13. best practice and pending issues
14. development test result
15. dependencies and environment
16. coding and programming engineering standard achieved

# Section 8. Workplan
1. always create workplan file for each given task. workplans will be generated in <project folder>/workplan/ folder.
2. workplan should consider the following:
   - Title and description
   - workplan document ID, revision control (summary of what updated in this workpan) and version history, status
   - object
   - scope summary
   - index of content with links
   - dependencies with other tasks
   - evaluation and alignment with existing architecture
   - implementation phase and task breakdown
     - timeline, milestones, and deliverables
     - what will be updated/created
     - risks and mitigation
     - potential issues to be addressed in the future
     - success criteria
     - references with links to other files, reports, and code files.
3. always update workplan file when there are changes or updates
4. always review related others workplan file before starting implementation
5. always log issues to issue_log.md file under the parent folder of workplan folder
6. always generate report for each phase in the subfolder reports which is under related workplan file folder
7. always update logs in log folder which is under parent folder of workplan folder

# Section 9. Reports for workplans
1. always conduct test after updates per workplan each phase. test reports for workplan phases will be generated in <project folder>/workplan/reports/ folder.
2. test report for workplan phases should include:
   - title and description for tests
   - report document ID, revision control (summary of what udpated in this test report) and version history, status
   - index of content with links
   - test objective, scope and execution summary
   - test methodology, environment, and tools
   - test phases, steps, cases, status, and detailed results
   - test success criteria and checklist
   - file archived, modified, and version controlled
   - recommendations for future actions
   - lessons learned
3. always log issues to issue_log.md file under the parent folder of workplan folder
4. always update update_log.md in <project folder>/log/ folder.
5. link reports to workplan files for cross reference.
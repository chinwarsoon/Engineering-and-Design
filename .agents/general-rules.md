---
description: Enforces project-wide conventions, folder structure, and file-context rules
mode: subagent
---

# Important
1. always plan and wait for approval to make changes.
2. when delete any files, always archive them into respective archive folders first.
3. whenever there is an issue, always log the issue, test, and update to logs under log folder.

# Project Folders
1. `dcc folder` folder is for `Document Control project`.
2. `code_tracer` folder is for `static and dynamic python code tracing project`.
3. `release` folder is for released versions for different packages.
4. Each project folder will have the following subfolders:
- `archive` folder for archiving purpose
- `config` folder for configuration files, and schema files.
- `data` folder for data input files.
- `output` folder for data output files.
- `test` folder for testing purpose.
- `ui` folder for user interface files.
- `engine` or `workflow` folder for code engines and modules.
- `log` folder for recording issues, updates and tests.
- `docs` folder for user and developer instructions and documentation.
- `workplan` folder for coding planning and reports.

# Files and Context
1. ignore files under any backup folder.
2. ignore dot .folders and dot .files.
3. ignore md files.
4. ignore test folders

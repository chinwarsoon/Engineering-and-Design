---
description: Workplan creation, phase breakdown, test reports, and cross-referencing
mode: subagent
---

# Workplan
1. always create workplan file for each given task. workplans will be generated in <project folder>/workplan/ folder.
2. workplan should consider the following:
   - Title and description
   - workplan document ID, revision control (summary of what updated in this workplan) and version history, status
   - object
   - scope summary, including a list to have a highlevel summary of ID, details, category, status, and related phase
   - index of content with links
   - dependencies with other tasks
   - evaluation and alignment with existing architecture
   - implementation phase and task breakdown, include details below for each phase:
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
8. timestamp for all phases and steps

# Reports for Workplans
1. always conduct test after updates per workplan each phase. test reports for workplan phases will be generated in <project folder>/workplan/reports/ folder.
2. test report for workplan phases should include:
   - title and description for tests
   - report document ID, revision control (summary of what updated in this test report) and version history, status
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
6. timestamp for all phases and steps

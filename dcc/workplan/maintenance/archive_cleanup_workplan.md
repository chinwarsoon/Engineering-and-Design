Requirements:
1. the purpose of cleanup and archive is to remove deprecated code and files that are no longer needed to <project folder>/archive folder. this will acheive:
- **schema file** - No dead or inconsistent schema files
- **Cleaner codebase** - No dead code paths
- **Faster loading** - No fallback checks for non-existent legacy formats
- **Less confusion** - New developers won't see dual-format support
- **Smaller repository** - Archive folder contains only truly legacy items
- **Clearer documentation** - No references to deprecated formats
2. the cleanup and archive process should be run on a regular basis
3. the cleanup and archive process should be documented and should be easy to understand and follow
4. the cleanup and archive process should be tested and should be working as expected
5. the cleanup and archive process should be reviewed and updated as needed
6. follow requirements for workplan and worplan phase test in agent_rule.md file
7. when check schema file:
- make sure to check for dead or inconsistent schema files. remove and archive unused or deprecated schema files to <project folder>/archive folder. resepect the folder structure and naming convention.
- validate values in schema files to ensure they are correct and consistent with current environment, folders, files, and code
- check $ref and $id to ensure they are correctly pointing to the right files
8. if there are any other achive folders instead of <project folder>/archive, make sure move the files to this project achive folder. deleted the empty folders after move. make sure any links to those achived files are updated to point to the new location.
9. when update readme file, user instructions, user guidelines, make sure to update them to reflect the current state of the project. final project documentation for readme, user instructions, user guidelines will be in <project folder>/docs folder.
10. after cleanup and archive, make sure to test the system to ensure everything is working as expected.
11. follow rules in agent_rule.md file to update this workplan, test reports, and logs.


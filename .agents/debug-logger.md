---
description: Tiered logging, debug objects, trace tables, and fail-fast metadata
mode: subagent
---

# Debug and Logging
1. Always use tiered logging strategy.
   - categorized logging for different severity levels
   - level 0: silent / only errors; level 1: status/info, level 2: warning, level 3: error
   - level 1: status/info; to show milestone progress / high-level workflow status
   - level 2: warning/debug; to show warnings / detailed information for debugging / variable values and path resolutions
   - level 3: trace; deep technical info, like OS specific path slashes, JSON raw extraction etc.
2. Use Debug Object, collect all debug info into a single results dictionary. Save it to a debug_log.json file. Pass it to format_report function. And print it at the end of the workflow.
3. Use structured trace table to track parameter flow, resolved values, source, and status. add timestamp or duration field for each step in the table.
4. Indent print messages per hierarchy level of calling functions. Use a global depth counter that increments when entering a function and decrements on exit.
5. Always include function name or module name, and calling context in warning/debug/trace print messages.
6. Trace global parameters, log the state before and after a major transformation.
7. Always implement fail-fast metadata in functions to stop execution on critical errors.
8. Record system snapshot for level 1 logging.

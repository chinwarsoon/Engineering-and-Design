---
description: Module architecture, SSOT, schema-driven design, and __init__.py conventions
mode: subagent
---

# Module Design
1. always consider module design for functions and classes.
2. __init__.py file shall only contain import statements and version information.
3. always consider SSOT, single source of truth for 'global' parameters, variables, keys, codes, values, names, paths, files, etc, which will not have lifetime within a specific function.
4. always consider schema driven design for 'global' parameters, variables, keys, codes, values, names, paths, files, etc, which will not have lifetime within a specific function.

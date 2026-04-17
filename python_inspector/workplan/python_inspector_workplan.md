# Phase 1: The Agnostic Extraction EngineGoal
Build a "Recursive Scanner" that handles any folder structure without knowing the business logic in advance.
- Recursive Crawler: Implement a scanner using pathlib that maps the entire directory tree, ignoring .git, __pycache__, and venv.
- Import Grapher: Use ast to parse import and from ... import statements. This builds the "edges" between different files in the repo.
- Global Signature Registry: Build a database of every function in the project, indexed by its "Fully Qualified Name" (e.g., module.submodule.function_name).
- Type Hint Harvesting: Extract PEP 484 type hints to understand what data types each function expects (Strings, Integers, DataFrames, or custom Pydantic models).

# Phase 2: Dynamic Workflow VisualizationGoal
Create a UI that adapts to the complexity of the project, from single-script utilities to multi-module packages.
- Multi-Level Graphing: Use Pyvis to allow "Drill-down" views.
  - Level 1: File-to-File dependencies (High-level architecture).
  - Level 2: Function-to-Function calls (Internal logic).
- Auto-Layout Engine: Use NetworkX to calculate the best visual hierarchy (top-down for pipelines, radial for libraries).
- Code Peek: Integrate a syntax-highlighted code viewer so that clicking a node reveals the source code in a side panel without leaving the tool.

# Phase 3: The Universal Mocking & API SandboxGoal
Create a "Data-Agnostic" testing interface.
- Generic Form Factory: Build a system that generates UI inputs based on the discovered type hints.
  - int $\rightarrow$ Slider/Number Input.
  - str $\rightarrow$ Text area.
  - bool $\rightarrow$ Toggle switch.
  - pd.DataFrame $\rightarrow$ CSV File Uploader.
- Sandboxed Execution: Use importlib to dynamically load the modules. Wrap the execution in a try/except block to capture errors and stack traces for the UI.
- The Global Tracer: Use sys.settrace or a decorator-based observer to capture the state of variables across file boundaries.

# Phase 4: Comparative Logic & Impact Analysis
Goal: Tools for debugging and understanding complex changes.
- The "What-Changed" Trace: Allow the user to run the same function with two different sets of mock data and visually compare which logic branches were hit in each case.
- State Snapshots: Store the "Local Variables" at every function step, allowing the user to "scroll" through the execution history.
- Exportable Test Cases: Allow the user to save a "Mock Data Set" as a JSON file, which can then be used for unit testing later.
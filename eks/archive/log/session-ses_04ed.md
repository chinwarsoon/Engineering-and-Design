# New session - 2026-07-30T03:51:50.708Z

**Session ID:** ses_04ed99d4cffeNYGms6v3vFgZlQ
**Created:** 30/07/2026, 11:51:50
**Updated:** 30/07/2026, 11:54:04

---

## User

hello

---

## Assistant (Build · DeepSeek V4 Flash Free · 8.1s)

_Thinking:_

The user is just saying hello. I'll respond with a brief greeting.

Hello! How can I help you today?

---

## User

refer to eks workplan appendix i, phase 1 issue log i265 and related tasks in task log, study current eks pipeline desing, check any gaps in workplan for review.

---

## Assistant (Build · DeepSeek V4 Flash Free · 7.4s)

_Thinking:_

The user wants me to:
1. Read the EKS workplan Appendix I (issue log) for issue I265
2. Check related tasks in the task log
3. Study the current EKS pipeline design
4. Check for gaps in the workplan for review

Let me start by finding the relevant files. I need to look at the EKS project structure first.

**Tool: glob**

**Input:**
```json
{
  "pattern": "eks/workplan/**/*.md"
}
```

**Output:**
```
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\appendix_h_bootstrap_module_design.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\appendix_g_interface_architecture.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\appendix_f_pipeline_architecture_design.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\appendix_e_schema_design.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\appendix_d_pipeline_messages_errors.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\appendix_c_ontology.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\appendix_b_document_registry.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\appendix_a_asset_schema.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\reports\rp_eks_p1_i255_filename_auto_detect.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\reports\rp_eks_p1_i254_path_doubling_fix.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\reports\phase_1_foundation_universal_cli_parser_report.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\reports\phase_1_foundation_report.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\reports\phase_1_foundation_entrypoint_discovery_report.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\reports\phase_1.2_report.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\phase_5_ui_integration_workplan.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\phase_4_retrieval_pipeline_workplan.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\phase_3_knowledge_graph_workplan.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\phase_2_chunking_embedding_workplan.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\phase_1_foundation_workplan.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\phase_1.2_interactive_ui_workplan.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\eks_system_workplan.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\appendix_p1.6_phase1_revision_history.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\appendix_p1.3_phase1_data_export.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\appendix_p1.2_phase1_scope.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\appendix_p1.1_phase1_architecture.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\appendix_l_project_definition.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\appendix_k_issue_management.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\appendix_j_file_property_parser.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\appendix_i_filename_parser.md
```

**Tool: glob**

**Input:**
```json
{
  "pattern": "eks/knowledge.json"
}
```

**Output:**
```
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\knowledge.json
```

**Tool: glob**

**Input:**
```json
{
  "pattern": "eks/engine/**/*.py"
}
```

**Output:**
```
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\__init__.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\review\__init__.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\pipeline_engine\__init__.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\pipeline_engine\runner.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\pipeline_engine\exporter.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\pipeline_engine\cli.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\parsers\__init__.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\parsers\xlsx_parser.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\parsers\pdf_parser.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\parsers\parser_router.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\parsers\io_contracts.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\parsers\dwg_parser.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\parsers\docx_parser.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\parsers\dgn_parser.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\parsers\base_parser.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\logging\__init__.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\logging\logger.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\health\__init__.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\eks_engine_pipeline.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\discovery\__init__.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\core\__init__.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\core\validator.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\core\ui_contracts.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\core\telemetry.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\core\structure_detector.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\core\setup_validator.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\core\schema_to_ddl.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\core\schema_loader.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\core\revision.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\core\review_manager.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\core\registry.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\core\pipeline_orchestrator.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\core\message_manager.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\core\io_contracts.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\core\health_scorer.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\core\health_cli.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\core\file_scanner.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\core\file_property_parser.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\core\filename_parser.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\core\factories.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\core\error_manager.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\core\discovery_cli.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\core\context.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\core\config_registry.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\core\column_processor.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\core\bootstrap.py
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\engine\core\base.py
```

**Tool: glob**

**Input:**
```json
{
  "pattern": "eks/config/**/*.json"
}
```

**Output:**
```
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\config\schemas\eks_setup_schema.json
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\config\schemas\eks_project_rules_config.json
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\config\schemas\eks_project_code_schema.json
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\config\schemas\eks_ontology_setup_schema.json
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\config\schemas\eks_ontology_config.json
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\config\schemas\eks_ontology_base_schema.json
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\config\schemas\eks_message_setup_schema.json
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\config\schemas\eks_message_config.json
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\config\schemas\eks_message_base.json
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\config\schemas\eks_facility_schema.json
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\config\schemas\eks_error_setup_schema.json
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\config\schemas\eks_error_config.json
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\config\schemas\eks_error_code_base.json
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\config\schemas\eks_doc_setup_schema.json
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\config\schemas\eks_doc_config.json
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\config\schemas\eks_doc_base_schema.json
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\config\schemas\eks_document_type_schema.json
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\config\schemas\eks_discipline_schema.json
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\config\schemas\eks_department_schema.json
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\config\schemas\eks_config.json
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\config\schemas\eks_base_schema.json
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\config\schemas\eks_asset_setup_schema.json
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\config\schemas\eks_asset_config.json
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\config\schemas\eks_asset_base_schema.json
```

---

## Assistant (Build · DeepSeek V4 Flash Free · 6.6s)

_Thinking:_

Now I need to look at the relevant files:

1. The issue log (issue_log.md) for I265
2. The task log (probably in log/ folder)
3. The workplan appendix I (filename parser)
4. The pipeline design documents

Let me read the key files. The issue log should be at `eks/log/issue_log.md`, and the workplan appendix I is `eks/workplan/appendix_i_filename_parser.md`.

**Tool: glob**

**Input:**
```json
{
  "pattern": "eks/log/*"
}
```

**Output:**
```
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\log\opencode.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\log\issue_log.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\log\gemini.md
```

**Tool: glob**

**Input:**
```json
{
  "pattern": "eks/workplan/task*"
}
```

**Output:**
```
No files found
```

**Tool: glob**

**Input:**
```json
{
  "pattern": "eks/workplan/appendix_i*"
}
```

**Output:**
```
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\appendix_i_filename_parser.md
```

---

## Assistant (Build · DeepSeek V4 Flash Free · 5.2s)

_Thinking:_

Let me read the issue log to find I265, the appendix I, and the task log / task table within the workplan.

**Tool: read**

**Input:**
```json
{
  "filePath": "C:\\Users\\franklin.song\\Desktop\\DSAI\\Engineering-and-Design\\eks\\log\\issue_log.md"
}
```

**Output:**
```
<path>C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\log\issue_log.md</path>
<type>file</type>
<content>
1: # EKS Issue Log — RETIRED
2: 
3: **Status**: ✅ Retired (2026-07-27)
4: **Archive**: `eks/archive/log/issue_log.md`
5: **Active source**: `eks/log/phase1/p1_issue_log.md` (Phase 1) + future `eks/log/phase{N}/p{N}_issue_log.md`
6: 
7: The consolidated issue log has been split into phase-specific logs. See the archive file for the full history (I001–I249).
8: 
9: **Revision**: 1.0 | **Date**: 2026-07-27 | **Author**: opencode | **Summary**: Retired in favour of phase-specific issue logs.

(End of file - total 9 lines)
</content>
```

**Tool: read**

**Input:**
```json
{
  "filePath": "C:\\Users\\franklin.song\\Desktop\\DSAI\\Engineering-and-Design\\eks\\workplan\\appendix_i_filename_parser.md"
}
```

**Output:**
```
<path>C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\appendix_i_filename_parser.md</path>
<type>file</type>
<content>
1: # Appendix I — Schema-Driven Filename Parser (Universal Class)
2: 
3: **Document ID**: WP-EKS-P1-APX-I  
4: **Version**: 0.3  
5: **Last Updated**: 2026-07-18  
6: **Phase**: 1 — Foundation  
7: **Status**: 📋 Proposed for Review  
8: **Parent Workplan**: [phase_1_foundation_workplan.md](phase_1_foundation_workplan.md) §20 (Document Registry & Revision Management)  
9: **Related Issues**: [I133](../log/issue_log.md), [I134](../log/issue_log.md), [I135](../log/issue_log.md), [I136](../log/issue_log.md), [I137](../log/issue_log.md)  
10: **Related Appendices**:
11: - [Appendix B — Document Registry](appendix_b_document_registry.md) — registry columns, SUPERSEDES chains, ontology triggers
12: - [Appendix D — Pipeline Messages & Errors](appendix_d_pipeline_messages_errors.md) — D5-PARSE-* error code taxonomy, D7.1 health scoring
13: - [Appendix F — Pipeline Architecture](appendix_f_pipeline_architecture_design.md) — Phase A/B orchestration flow
14: - [Appendix J — File Property Parser](appendix_j_file_property_parser.md) — OS-level + embedded property extraction, boundary definition
15: 
16: **Related Files**:
17: - [`eks/engine/core/file_scanner.py`](../engine/core/file_scanner.py) — current `_parse_filename()` (L145–174)
18: - [`eks/engine/core/pipeline_orchestrator.py`](../engine/core/pipeline_orchestrator.py) — inline duplicate extraction (L567, L645)
19: - [`eks/config/schemas/eks_doc_config.json`](../config/schemas/eks_doc_config.json) — target for `filename_patterns` block
20: - [`eks/config/schemas/eks_doc_setup_schema.json`](../config/schemas/eks_doc_setup_schema.json) — schema declarations
21: - [`eks/config/schemas/eks_doc_base_schema.json`](../config/schemas/eks_doc_base_schema.json) — shared definitions
22: - [`eks/config/schemas/eks_error_config.json`](../config/schemas/eks_error_config.json) — D5-PARSE-* error code registration
23: - [`eks/engine/core/registry.py`](../engine/core/registry.py) — `register_document()` / `get_document()`
24: - [`eks/ui/backend/phase1_server.py`](../ui/backend/phase1_server.py) — UI-side filename parsing
25: 
26: ### Revision History
27: 
28: | Revision | Date | Author | Summary |
29: | :------- | :--- | :----- | :------ |
30: | 0.3 | 2026-07-18 | CodeBuddy | Added §I1.1 boundary definition: explicit separation from FilePropertyExtractor (Appendix J), system-values breakdown table (3 categories, 3 sources), clean-architecture rationale |
31: | 0.2 | 2026-07-18 | CodeBuddy | Major redesign: universal class (`FilenameParser` + `FilenameParseResult`), segment-based field extraction aligned with Appendix B registry columns, 9-field output, full D5-PARSE-001–007 error taxonomy, cross-appendix alignment table |
32: | 0.1 | 2026-07-18 | CodeBuddy | Initial draft: I1–I10 (Overview, Problems, Filename Analysis, Schema Design, Algorithm, Shared Parser Module, Null-Tolerant Registration, Call-Site Migration, Per-Project Configuration, Implementation Plan) |
33: 
34: ---
35: 
36: ## I1. Overview
37: 
38: The filename parser extracts structured metadata from source filenames during Phase A (file discovery + registration) and Phase B (pipeline processing). Currently the logic is duplicated across 4 call sites using 2 divergent algorithms, with hardcoded rules that cannot be customized per project, extracts only 2 of 5 available fields, and has no support for null-registration when extraction fails.
39: 
40: This appendix defines a **schema-driven**, **universal-class**, **null-tolerant** filename parser that:
41: 
42: 1. Moves extraction rules into `eks_doc_config.json` as a `filename_patterns` block with segment-level field mapping (per-project, per I136)
43: 2. Consolidates all parsing logic into a single `FilenameParser` class in a shared module (per I135)
44: 3. Extracts all 7 filename-derived fields (`document_number`, `revision`, `project_number`, `area`, `document_type`, `discipline`, `sequence_number`) identified in Appendix B §B3
45: 4. Supports null returns when extraction genuinely fails, with pipeline layers relaxed to accept nulls (per I134)
46: 5. Eliminates the Phase A/Phase B algorithm divergence (root cause of I133/D5-PARSE-003)
47: 6. Registers error codes `D5-PARSE-001` through `D5-PARSE-007` in the formal error catalog (per I137)
48: 
49: ### Design Principles
50: 
51: | Principle | Description |
52: |-----------|-------------|
53: | **Schema-driven** | Per-project filename patterns + segment definitions in config JSON, not hardcoded in Python |
54: | **Universal class** | Single `FilenameParser` class shared by all call sites; one instantiation per project, reused across all files in a scan |
55: | **Fail-safe** | Never drop a file — return `parse_status: "unresolvable"` with synthetic keys; register with degraded quality markers |
56: | **Project hierarchy** | `{project_code}` pattern overrides `"*"` catch-all default |
57: | **Segment-aware** | Filename is decomposed into positional segments; each maps to a registry column per Appendix B |
58: | **Suffix-aware** | Strip known non-revision suffixes (`_AddN`, `_2-Stage`, `_HAC`) before segment/revision extraction |
59: | **Length-guarded** | Dash-suffix revision detection uses configurable `dash_revision_max_len` |
60: | **Backward compatible** | Default `"*"` pattern replicates current hardcoded behavior |
61: 
62: ### I1.1 Boundary: What the Filename Parser Does and Does NOT Handle
63: 
64: The filename parser is a **string-level operation only**. It operates on `Path.stem` — zero I/O, zero disk access. It does not verify file existence, does not open files, and does not depend on any parsing library.
65: 
66: The full set of "system-related" values that describe a file come from **3 distinct sources** with **3 distinct failure modes** and **3 distinct lifecycle stages**. Only Source A belongs in this class.
67: 
68: | Category | Source | Field Count | I/O Type | Pipeline Stage | Failure Domain | Handled By |
69: |:---|:---|:---:|:---|:---|:---|:---|
70: | **A. Filename-derived** | String parsing (`Path.stem`) | 7 | None — pure string operation | P0 (scan) | D5-PARSE-001..007 | **`FilenameParser`** (this appendix) |
71: | **B. OS-level** | `Path.stat()` / `hashlib` | 6 | Disk I/O, system calls | P0 / Phase B | D5-PROP-001, 002, 005 | **`FilePropertyExtractor`** (Appendix J) |
72: | **C. Embedded metadata** | Parser `extract_metadata()` | 11+ | File open, parsing libraries | Phase B | D5-PROP-003, 004 | **`FilePropertyExtractor`** (Appendix J) |
73: 
74: #### Why Categories B and C Must NOT Be in FilenameParser
75: 
76: **1. Different input type.** `FilenameParser.parse()` accepts a `str` — the filename. It does not need a real file to exist on disk:
77: 
78: ```python
79: parser.parse("131101-WSW41-SP-SG-0101.pdf")  # file need not exist
80: ```
81: 
82: OS properties and embedded metadata require a **real, accessible file path**:
83: 
84: ```python
85: Path.stat()           # requires OS permissions on a real file
86: pdfplumber.open()     # requires opening and parsing a real file on disk
87: ```
88: 
89: Adding these to `FilenameParser` would turn a pure string parser into a side-effect-producing I/O class — a fundamental change in its nature.
90: 
91: **2. Different pipeline timing.** In Phase A, the file has not yet been parsed — embedded metadata is unavailable. In Phase B, all three sources are available. If merged into one class, the same method would return different results depending on when it is called — a fragile pattern.
92: 
93: **3. Different error domains.** Naming-convention violations (D5-PARSE-*) have fundamentally different severity and recovery strategies than disk permission errors (D5-PROP-*). Mixing them would force a single `try/except` to handle both simultaneously.
94: 
95: **4. Different dependency profiles.** `FilenameParser` depends only on `re`, `dataclasses`, and `pathlib.Path` (only `.stem`). It is safe to import at PRESTART without any guards. `FilePropertyExtractor` requires `hashlib`, `datetime`, `os.stat`, and parser libraries — it needs `_preload_infrastructure()` guards for Python 3.13.
96: 
97: #### Clean Architecture Decision
98: 
99: | Concern | Handler | Rationale |
100: |:---|:---|:---|
101: | Extract structured fields from naming convention | `FilenameParser` | Pure string operation, testable without I/O |
102: | Collect filesystem timestamps, size, permissions | `FilePropertyExtractor` Layer 1 | Requires OS calls, unrelated to naming |
103: | Extract author, page count, title | `FilePropertyExtractor` Layer 2 | Requires parsed metadata, format-specific |
104: | Merge all into registry row | `PipelineOrchestrator` or `FileScanner` | Only the orchestrator sees the full picture |
105: 
106: **Integration point:** `PipelineOrchestrator._process_file()` calls both and merges the results:
107: 
108: ```python
109: # Phase A: FileScanner
110: parse_result = self._filename_parser.parse(file_name)     # string → 7 fields
111: os_props = self._prop_extractor.extract(file_path,        # disk → 6 fields
112:                file_type, parser_metadata=None)
113: metadata = {**parse_result.to_metadata_dict(),
114:             **os_props.to_registry_dict()}
115: 
116: # Phase B: PipelineOrchestrator
117: parse_result = self._filename_parser.parse(file_name)     # re-parse for consistency
118: parser_metadata = parser.extract_metadata()               # now available
119: full_props = self._prop_extractor.extract(file_path,      # OS + embedded
120:                 file_type, parser_metadata)
121: registry_update = {**parse_result.to_metadata_dict(),
122:                    **full_props.to_registry_dict()}
123: ```
124: 
125: **No third class needed. No merging needed.** The boundary is clean, coupling is low in both directions.
126: 
127: ### Design Decision: Class vs. Module-Level Function
128: 
129: | Factor | Module-Level Function | Universal Class | Decision |
130: |--------|----------------------|-----------------|----------|
131: | **Internal state** | None (stateless) | Caches compiled regex, resolved pattern, error list | **Class** — segment validation requires compiled patterns; caching avoids re-compile per file |
132: | **Return complexity** | Dict with 2 keys | `FilenameParseResult` dataclass with 9 fields + type safety | **Class** — IDE autocomplete, type checking, `.to_metadata_dict()` convenience |
133: | **Testability** | Parameterized function | Construct once, call `.parse(fname)` in loop | **Class** — natural for scan-loop usage; one instantiation, many calls |
134: | **Extensibility** | Add parameters → break signature | Add methods: `.parse_batch()`, `.generate_filename()` | **Class** — future methods fit naturally |
135: | **Call-site ergonomics** | `parse_filename(f, patterns, code)` | `parser = FilenameParser(patterns, code); parser.parse(f)` | **Class** — callers hold a reference; no repeated config passing |
136: 
137: **Conclusion**: The filename parser is implemented as a **universal class** (`FilenameParser`) in a standalone module (`eks/engine/core/filename_parser.py`). A module-level convenience function `parse_filename()` is also provided for one-shot usage.
138: 
139: ---
140: 
141: ## I2. Problem Analysis
142: 
143: ### I2.1 Current State — 4 Call Sites, 2 Algorithms
144: 
145: | # | Location | Algorithm | Length Guard | Output Fields |
146: |---|----------|-----------|--------------|---------------|
147: | **A** | `FileScanner._parse_filename()` L145–174 | 3-path: `_rev` split → `rsplit("-", 1)` only if `≤3` chars → fallback full stem | ✅ Yes | 2 (`doc_number`, `revision`) |
148: | **A** | `phase1_server.py` L393 | Calls `scanner.build_placeholder_metadata()` → uses algorithm A | ✅ Yes (via A) | 2 |
149: | **B** | `PipelineOrchestrator._process_file()` L567 | Inline: `stem.split("_rev")[0].rsplit("-", 1)[0]` | ❌ No | 1 (`doc_number` only) |
150: | **B** | `PipelineOrchestrator._update_doc_status()` L645 | Identical inline one-liner | ❌ No | 1 |
151: 
152: ### I2.2 Divergent Outputs — Root Cause of D5-PARSE-003
153: 
154: For file `131101-WSW41-SP-SP-0801_Add3.pdf`:
155: 
156: | Phase | Algorithm | Extracted `doc_number` | Reason |
157: |-------|-----------|------------------------|--------|
158: | **Phase A** (register) | A — `_parse_filename()` | `"131101-WSW41-SP-SP-0801_Add3"` | `_Add3` = 4 chars > 3 → falls through dash-split → full stem fallback |
159: | **Phase B** (lookup) | B — inline one-liner | `"131101-WSW41-SP-SP-0801"` | Unconditionally strips after last `-` → drops `-0801` → keeps parent |
160: 
161: Phase B looks up `"131101-WSW41-SP-SP-0801"` in the registry → not found (registered as `"131101-WSW41-SP-SP-0801_Add3"`) → **D5-PARSE-003**.
162: 
163: ### I2.3 Missing Field Extraction — Appendix B Gap
164: 
165: The registry (Appendix B §B3) defines 5 columns sourced from the filename. Only 2 are currently extracted:
166: 
167: | Registry Column | Source | Health Tier | Currently Extracted? |
168: |:---|:---|:---|:---|
169: | `project_number` | Filename segment 0 | T1 | ❌ No |
170: | `area` | Filename segment 1 | T2 | ❌ No |
171: | `document_type` | Filename segment 2 (→ ontology trigger) | T1 | ❌ No |
172: | `discipline` | Filename segment 3 | T1 | ❌ No |
173: | `document_number` | All segments rejoined | T1 | ✅ Yes |
174: | `revision` | Suffix | T1 | ✅ Yes |
175: 
176: Phase 3 (ontology) waits for `document_type` to assign classes. If it's in the filename, it should be extracted at Phase A.
177: 
178: ### I2.4 Gaps Mapped to Issues
179: 
180: | Gap | Issue | Severity |
181: |-----|-------|----------|
182: | Phase A/B algorithm divergence | I133 | 🟠 High |
183: | No null-registration support (3 layers) | I134 | 🟠 High |
184: | No shared parser module (4 call sites) | I135 | 🟡 Medium |
185: | Hardcoded patterns, no per-project config | I136 | 🟠 High |
186: | `D5-PARSE-003` not in error catalog | I137 | 🟢 Low |
187: | Only 2/5 filename-derived columns extracted | (this appendix) | 🟠 High |
188: 
189: ---
190: 
191: ## I3. TWRP Filename Analysis (Ground Truth)
192: 
193: Analysis of all 171 files under `eks/data/twrp/` reveals 3 filename families.
194: 
195: ### I3.1 Family A — Standard TenderSpec (project code 131101)
196: 
197: **Pattern**: `{project_code}-{contract}-{type_code}-{discipline}-{seq_number}[_{suffix}].{ext}`
198: 
199: **Segment-to-Column Mapping** (aligned with Appendix B §B3):
200: 
201: | Position | Segment | Example Value | `maps_to` Column | Appendix B Tier | Notes |
202: |:---------|:--------|:--------------|:-----------------|:----------------|:------|
203: | 0 | `project_code` | `131101` | `project_number` | T1 (Project) | 6-digit project ID |
204: | 1 | `contract` | `WSW41` | `area` | T2 (Project) | Contract/area code |
205: | 2 | `type_code` | `SP` | `document_type` | T1 (Document) | Maps to ontology class per B3.1: `SPC→Specification` |
206: | 3 | `discipline` | `SG` / `SP` | `discipline` | T1 (Project) | SG=General Works, SP=Specific Works |
207: | 4 | `seq_number` | `0101`–`1300` | *(no maps_to — rejoined)* | — | 4-digit sequence, used in `document_number` |
208: | — | `suffix` | `_Add1`, `_Add3`, `_2-Stage`, `_HAC` | *(stripped)* | — | Non-revision qualifier, stripped before parse |
209: 
210: **Subtypes**:
211: 
212: | Subtype | Pattern | Count | Example |
213: |---------|---------|-------|---------|
214: | A1 — Clean | `131101-WSW41-SP-SG-0101.pdf` | ~140 | Standard, no suffix |
215: | A2 — Addendum | `131101-WSW41-SP-SP-0801_Add3.pdf` | 4 | `_Add1`, `_Add3` |
216: | A3 — Two-stage | `131101-WSW41-SP-SP-0202_2-Stage.pdf` | 7 | `_2-Stage`, `_2-stage` |
217: | A4 — HAC | `131101-WSW41-SP-SP-0501_HAC.pdf` | 1 | `_HAC` suffix |
218: 
219: **Known suffixes for Family A (TWRP 131101)**:
220: 
221: | Suffix | Meaning | Is Revision? | Count |
222: |--------|---------|-------------|-------|
223: | `_Add1`, `_Add3` | Addendum 1, Addendum 3 | ❌ No | 4 |
224: | `_2-Stage`, `_2-stage` | Two-stage tender | ❌ No | 7 |
225: | `_HAC` | Unknown qualifier | ❌ No | 1 |
226: 
227: ### I3.2 Family B — Cover / Contents Pages
228: 
229: **Pattern**: `{prefix}_{descriptor}-{vol_info}[_{suffix}].{ext}`
230: 
231: | Subtype | Example | Count |
232: |---------|---------|-------|
233: | B1 — Cover | `00a_CoverPage_Vol2_C4B.pdf` | 3 |
234: | B2 — Contents | `00c_Contents - Vol 2_C4B.pdf` | 3 |
235: | B3 — Two-Stage Cover | `00a_Cover Page - Vol 3_C4B_2-Stage.pdf` | 4 |
236: 
237: **Parsing target**: No standard `{project_code}-{contract}-...` prefix. Fallback to full stem as `doc_number`, all segment fields `null`, `parse_status: "unresolvable"`.
238: 
239: ### I3.3 Family C — SOP / Preamble
240: 
241: **Pattern**: `{seq}_{TWRP}_{C4B}_{type}_{discipline}[_{qualifier}].{ext}`
242: 
243: | Example | Count |
244: |---------|-------|
245: | `02_TWRP_C4B_SOP1_PG_pwp.xlsx` | 8 |
246: | `17_TWRP_C4B_Preamble_FSOR _Work.pdf` | 2 |
247: 
248: **Parsing target**: Fallback to full stem as `doc_number`, all segment fields `null`, `parse_status: "unresolvable"`.
249: 
250: ### I3.4 Summary Distribution
251: 
252: | Family | Count | Segments extractable? | `revision` extractable? | `parse_status` |
253: |--------|-------|-----------------------|------------------------|----------------|
254: | A1 (clean) | ~140 | ✅ All 5 segments | ✅ null (no rev suffix) | `ok` |
255: | A2 (addendum) | 4 | ✅ After suffix strip | ✅ null | `ok` |
256: | A3 (two-stage) | 7 | ✅ After suffix strip | ✅ null | `ok` |
257: | A4 (HAC) | 1 | ✅ After suffix strip | ✅ null | `ok` |
258: | B (cover/contents) | ~10 | ❌ Fallback only | ❌ null | `unresolvable` |
259: | C (SOP/Preamble) | ~10 | ❌ Fallback only | ❌ null | `unresolvable` |
260: | **TOTAL** | **171** | — | — | — |
261: 
262: **Key finding**: No file in the TWRP dataset contains a genuine revision in the filename. All files use `revision = null` (per I134). The `revision_validation` regex (`^[A-Z0-9]{1,2}$`) applies to post-extraction validation, not filename parsing.
263: 
264: ---
265: 
266: ## I4. Schema Design — `filename_patterns` with Segments
267: 
268: ### I4.1 Location
269: 
270: New top-level key `filename_patterns` in `eks_doc_config.json`, sibling to `revision_validation`, `ontology_triggers`, etc.
271: 
272: ### I4.2 Structure — Full Config Block
273: 
274: ```json
275: "filename_patterns": {
276:     "131101": {
277:         "description": "TWRP WSD11 tenderspec naming: {project}-{area}-{type}-{disc}-{seq}[_suffix].ext",
278:         "parser_type": "delimited",
279:         "separator": "-",
280:         "min_segments": 5,
281:         "max_segments": 5,
282:         "segments": [
283:             {
284:                 "position": 0,
285:                 "maps_to": "project_number",
286:                 "label": "project_code",
287:                 "required": true,
288:                 "null_handling": { "strategy": "default_value", "default_value": "131101" },
289:                 "validation": { "type": "pattern", "pattern": "^\\d{6}$" }
290:             },
291:             {
292:                 "position": 1,
293:                 "maps_to": "area",
294:                 "label": "contract_or_area",
295:                 "required": true,
296:                 "null_handling": { "strategy": "default_value", "default_value": "UNKNOWN" },
297:                 "validation": { "type": "pattern", "pattern": "^[A-Z0-9]{3,6}$" }
298:             },
299:             {
300:                 "position": 2,
301:                 "maps_to": "document_type",
302:                 "label": "type_code",
303:                 "required": true,
304:                 "null_handling": { "strategy": "default_value", "default_value": "UNKNOWN" },
305:                 "validation": { "type": "schema_reference", "reference": "document_type_registry" }
306:             },
307:             {
308:                 "position": 3,
309:                 "maps_to": "discipline",
310:                 "label": "discipline_code",
311:                 "required": true,
312:                 "null_handling": { "strategy": "default_value", "default_value": "UNKNOWN" },
313:                 "validation": { "type": "pattern", "pattern": "^[A-Z]{2}$" }
314:             },
315:             {
316:                 "position": 4,
317:                 "maps_to": null,
318:                 "label": "sequence_number",
319:                 "required": true,
320:                 "null_handling": { "strategy": "default_value", "default_value": "0000" },
321:                 "validation": { "type": "pattern", "pattern": "^\\d{4}$" }
322:             }
323:         ],
324:         "rejoin_separator": "-",
325:         "strip_suffixes": ["_Add1", "_Add2", "_Add3", "_2-Stage", "_2-stage", "_HAC"],
326:         "revision_separators": ["_rev"],
327:         "dash_revision_max_len": 3,
328:         "output": {
329:             "document_number_source": "rejoin_segments",
330:             "fallback_doc_number": "full_stem",
331:             "fallback_revision": null,
332:             "preservation_mode": "overwrite_existing"
333:         },
334:         "error_subcodes": {
335:             "too_few_segments": "D5-PARSE-004",
336:             "too_many_segments": "D5-PARSE-005",
337:             "segment_validation_failed": "D5-PARSE-006",
338:             "unresolvable": "D5-PARSE-007"
339:         },
340:         "processing_phase": "P0"
341:     },
342:     "*": {
343:         "description": "Default: generic dash-suffix revision detection (backward compatible)",
344:         "parser_type": "delimited",
345:         "separator": "-",
346:         "min_segments": 1,
347:         "max_segments": null,
348:         "segments": [],
349:         "rejoin_separator": "-",
350:         "strip_suffixes": [],
351:         "revision_separators": ["_rev"],
352:         "dash_revision_max_len": 3,
353:         "output": {
354:             "document_number_source": "rejoin_segments",
355:             "fallback_doc_number": "full_stem",
356:             "fallback_revision": "00",
357:             "preservation_mode": "overwrite_existing"
358:         },
359:         "error_subcodes": {},
360:         "processing_phase": "P0"
361:     }
362: }
363: ```
364: 
365: ### I4.3 Field Definitions
366: 
367: #### Top-Level Pattern Fields
368: 
369: | Field | Type | Required | Description |
370: |-------|------|----------|-------------|
371: | `description` | `string` | Yes | Human-readable explanation of this project's naming convention |
372: | `parser_type` | `enum["delimited"]` | Yes | Parser strategy. Currently only `"delimited"` (split by separator). Future: `"regex"`, `"template"`. |
373: | `separator` | `string` | Yes | Character used to split the stem into segments |
374: | `min_segments` | `integer` | Yes | Minimum expected segment count. Fewer → `D5-PARSE-004`. |
375: | `max_segments` | `integer` or `null` | Yes | Maximum expected segment count. More → `D5-PARSE-005`. `null` = unlimited. |
376: | `segments` | `array[segment_def]` | Yes | Ordered segment definitions (see §I4.4). Empty array `[]` for fallback-only patterns. |
377: | `rejoin_separator` | `string` | Yes | Separator used when rejoining segments into `document_number` |
378: | `strip_suffixes` | `array[string]` | Yes | Suffixes to remove from stem **before** parsing. Applied in declaration order. Case-sensitive. |
379: | `revision_separators` | `array[string]` | Yes | Separators that indicate a revision follows (e.g., `["_rev"]`). |
380: | `dash_revision_max_len` | `integer` | Yes | Max length for trailing dash-segment to be considered revision. `0` = disabled. |
381: | `output` | `object` | Yes | Output control (see §I4.5) |
382: | `error_subcodes` | `object` | Yes | Maps error conditions to specific D5-PARSE-* codes |
383: | `processing_phase` | `enum["P0"]` | Yes | Phase when filename parsing runs. Always `"P0"` (pre-registration). |
384: 
385: #### I4.4 Segment Definition Fields
386: 
387: | Field | Type | Required | Description |
388: |-------|------|----------|-------------|
389: | `position` | `integer` | Yes | Zero-based index into the split stem parts |
390: | `maps_to` | `string` or `null` | Yes | Target registry column name (per Appendix B §B3). `null` = used in `document_number` rejoining only. |
391: | `label` | `string` | Yes | Human-readable segment name for logging/errors |
392: | `required` | `boolean` | Yes | Whether this segment must be present |
393: | `null_handling` | `object` | Yes | Strategy + fallback when segment is missing or invalid (see §I4.6) |
394: | `validation` | `object` | Yes | Validation rule for the segment value (see §I4.7) |
395: 
396: #### I4.5 Output Control Fields
397: 
398: | Field | Type | Description |
399: |-------|------|-------------|
400: | `document_number_source` | `enum["rejoin_segments"]` | How `document_number` is constructed. Currently `"rejoin_segments"` = join all split parts with `rejoin_separator`. |
401: | `fallback_doc_number` | `enum["full_stem"]` | Strategy when segment extraction fails entirely. `"full_stem"` = use the entire cleaned stem. |
402: | `fallback_revision` | `string` or `null` | Revision value when none extracted. `null` for I134 null-registration; `"00"` for backward compat. |
403: | `preservation_mode` | `enum["overwrite_existing"]` | How filename-derived values interact with existing registry values. Always `"overwrite_existing"` at P0. |
404: 
405: #### I4.6 Null-Handling Strategies
406: 
407: | Strategy | Behavior |
408: |----------|----------|
409: | `"default_value"` | Use `default_value` when segment missing or invalid |
410: | `"skip_segment"` | Omit from output (future) |
411: | `"raise_error"` | Treat as hard failure (future) |
412: 
413: #### I4.7 Validation Types
414: 
415: | Type | Fields | Description |
416: |------|--------|-------------|
417: | `"pattern"` | `pattern` (regex string) | Match segment value against regex. Fail → log `D5-PARSE-006`, use `null_handling`. |
418: | `"schema_reference"` | `reference` (config key) | Look up segment value in named registry (e.g., `document_type_registry`). Fail → log `D5-PARSE-006`, use `null_handling`. |
419: 
420: #### I4.8 `maps_to` ↔ Appendix B Registry Column Alignment
421: 
422: | `maps_to` Value | Registry Column (B3) | B3 Group | D7.1 Health Tier | Phase 3 Ontology Trigger |
423: |:---|:---|:---|:---|:---|
424: | `"project_number"` | `project_number` (VARCHAR) | Project | T1 | — |
425: | `"area"` | `area` (VARCHAR) | Project | T2 | — |
426: | `"document_type"` | `document_type` (VARCHAR) | Document | T1 | Class assignment (B3.1): `SPC→Specification`, `DWG→Drawing` |
427: | `"discipline"` | `discipline` (VARCHAR) | Project | T1 | — |
428: | `null` | *(only used in rejoined `document_number`)* | — | — | SUPERSEDES chains (B3.1) |
429: 
430: ### I4.9 Matching Priority
431: 
432: When the parser is invoked, it selects the pattern as follows:
433: 
434: ```
435: 1. If project_code is known → use filename_patterns[project_code]
436: 2. Else → use filename_patterns["*"]
437: 3. If filename_patterns is absent from config → use hardcoded defaults matching current "*"
438: ```
439: 
440: **Note on project_code discovery**: In Phase A, project_code is extracted from the data folder structure (`eks/data/twrp/` → project "TWRP" → code "131101"). A future task (beyond I136 scope) will implement formal `project_folder → project_code` mapping. Until then, the parser receives `project_code` as an optional parameter; when not provided, `"*"` is used.
441: 
442: ### I4.10 Schema Validation — Setup Schema Changes
443: 
444: In `eks_doc_setup_schema.json`, add to `properties`:
445: 
446: ```json
447: "filename_patterns": {
448:     "type": "object",
449:     "description": "Per-project filename parsing patterns with segment definitions. Keys are project codes or '*' for default. (Appendix I v0.2)",
450:     "propertyNames": {
451:         "pattern": "^(\\*|\\d{6})$"
452:     },
453:     "additionalProperties": {
454:         "type": "object",
455:         "properties": {
456:             "description": { "type": "string" },
457:             "parser_type": { "type": "string", "enum": ["delimited"] },
458:             "separator": { "type": "string", "minLength": 1 },
459:             "min_segments": { "type": "integer", "minimum": 1 },
460:             "max_segments": {
461:                 "oneOf": [
462:                     { "type": "integer", "minimum": 1 },
463:                     { "type": "null" }
464:                 ]
465:             },
466:             "segments": {
467:                 "type": "array",
468:                 "items": { "$ref": "#/definitions/filename_segment_def" }
469:             },
470:             "rejoin_separator": { "type": "string" },
471:             "strip_suffixes": {
472:                 "type": "array",
473:                 "items": { "type": "string" }
474:             },
475:             "revision_separators": {
476:                 "type": "array",
477:                 "items": { "type": "string" }
478:             },
479:             "dash_revision_max_len": { "type": "integer", "minimum": 0 },
480:             "output": {
481:                 "type": "object",
482:                 "properties": {
483:                     "document_number_source": { "type": "string", "enum": ["rejoin_segments"] },
484:                     "fallback_doc_number": { "type": "string", "enum": ["full_stem"] },
485:                     "fallback_revision": {
486:                         "oneOf": [
487:                             { "type": "string" },
488:                             { "type": "null" }
489:                         ]
490:                     },
491:                     "preservation_mode": { "type": "string", "enum": ["overwrite_existing"] }
492:                 },
493:                 "required": ["document_number_source", "fallback_doc_number", "fallback_revision", "preservation_mode"],
494:                 "additionalProperties": false
495:             },
496:             "error_subcodes": {
497:                 "type": "object",
498:                 "properties": {
499:                     "too_few_segments": { "type": "string" },
500:                     "too_many_segments": { "type": "string" },
501:                     "segment_validation_failed": { "type": "string" },
502:                     "unresolvable": { "type": "string" }
503:                 },
504:                 "additionalProperties": false
505:             },
506:             "processing_phase": { "type": "string", "enum": ["P0"] }
507:         },
508:         "required": ["description", "parser_type", "separator", "min_segments", "max_segments",
509:                      "segments", "rejoin_separator", "strip_suffixes", "revision_separators",
510:                      "dash_revision_max_len", "output", "error_subcodes", "processing_phase"],
511:         "additionalProperties": false
512:     },
513:     "minProperties": 1
514: }
515: ```
516: 
517: In `eks_doc_base_schema.json`, add the shared definitions:
518: 
519: ```json
520: "filename_pattern_def": {
521:     "type": "object",
522:     "description": "Per-project filename parsing pattern definition (Appendix I v0.2)",
523:     "properties": {
524:         "description": { "type": "string" },
525:         "parser_type": { "type": "string", "enum": ["delimited"] },
526:         "separator": { "type": "string", "minLength": 1 },
527:         "min_segments": { "type": "integer", "minimum": 1 },
528:         "max_segments": {
529:             "oneOf": [
530:                 { "type": "integer", "minimum": 1 },
531:                 { "type": "null" }
532:             ]
533:         },
534:         "segments": {
535:             "type": "array",
536:             "items": { "$ref": "#/definitions/filename_segment_def" }
537:         },
538:         "rejoin_separator": { "type": "string" },
539:         "strip_suffixes": { "type": "array", "items": { "type": "string" } },
540:         "revision_separators": { "type": "array", "items": { "type": "string" } },
541:         "dash_revision_max_len": { "type": "integer", "minimum": 0 },
542:         "output": { "$ref": "#/definitions/filename_output_def" },
543:         "error_subcodes": { "$ref": "#/definitions/filename_error_subcodes_def" },
544:         "processing_phase": { "type": "string", "enum": ["P0"] }
545:     },
546:     "required": ["description", "parser_type", "separator", "min_segments", "max_segments",
547:                  "segments", "rejoin_separator", "strip_suffixes", "revision_separators",
548:                  "dash_revision_max_len", "output", "error_subcodes", "processing_phase"],
549:     "additionalProperties": false
550: },
551: "filename_segment_def": {
552:     "type": "object",
553:     "description": "A positional segment extracted from a delimited filename (Appendix I v0.2)",
554:     "properties": {
555:         "position": { "type": "integer", "minimum": 0 },
556:         "maps_to": {
557:             "oneOf": [
558:                 { "type": "string" },
559:                 { "type": "null" }
560:             ]
561:         },
562:         "label": { "type": "string" },
563:         "required": { "type": "boolean" },
564:         "null_handling": {
565:             "type": "object",
566:             "properties": {
567:                 "strategy": { "type": "string", "enum": ["default_value", "skip_segment", "raise_error"] },
568:                 "default_value": { "type": "string" }
569:             },
570:             "required": ["strategy"],
571:             "additionalProperties": false
572:         },
573:         "validation": {
574:             "type": "object",
575:             "properties": {
576:                 "type": { "type": "string", "enum": ["pattern", "schema_reference"] },
577:                 "pattern": { "type": "string" },
578:                 "reference": { "type": "string" }
579:             },
580:             "required": ["type"],
581:             "additionalProperties": false
582:         }
583:     },
584:     "required": ["position", "maps_to", "label", "required", "null_handling", "validation"],
585:     "additionalProperties": false
586: },
587: "filename_output_def": {
588:     "type": "object",
589:     "description": "Output control for filename parsing (Appendix I v0.2)",
590:     "properties": {
591:         "document_number_source": { "type": "string", "enum": ["rejoin_segments"] },
592:         "fallback_doc_number": { "type": "string", "enum": ["full_stem"] },
593:         "fallback_revision": {
594:             "oneOf": [
595:                 { "type": "string" },
596:                 { "type": "null" }
597:             ]
598:         },
599:         "preservation_mode": { "type": "string", "enum": ["overwrite_existing"] }
600:     },
601:     "required": ["document_number_source", "fallback_doc_number", "fallback_revision", "preservation_mode"],
602:     "additionalProperties": false
603: },
604: "filename_error_subcodes_def": {
605:     "type": "object",
606:     "description": "Error subcode mapping for filename parsing failures (Appendix I v0.2)",
607:     "properties": {
608:         "too_few_segments": { "type": "string" },
609:         "too_many_segments": { "type": "string" },
610:         "segment_validation_failed": { "type": "string" },
611:         "unresolvable": { "type": "string" }
612:     },
613:     "additionalProperties": false
614: }
615: ```
616: 
617: ---
618: 
619: ## I5. Parsing Algorithm
620: 
621: ### I5.1 Class Design — `FilenameParser`
622: 
623: ```python
624: from dataclasses import dataclass, field
625: from pathlib import Path
626: from typing import Any, Dict, List, Optional, Tuple
627: import re
628: 
629: 
630: @dataclass
631: class FilenameParseResult:
632:     """
633:     Immutable result of parsing a single filename.
634: 
635:     All filename-derived fields are Optional[str] — null means
636:     "not extractable from this filename."  The Registry always
637:     receives a complete result; null fields trigger per-segment
638:     null_handling defaults downstream.
639: 
640:     Fields are ordered per Appendix B §B3 column priority.
641:     """
642:     document_number: Optional[str] = None
643:     revision: Optional[str] = None
644:     project_number: Optional[str] = None
645:     area: Optional[str] = None
646:     document_type: Optional[str] = None
647:     discipline: Optional[str] = None
648:     sequence_number: Optional[str] = None
649:     parse_status: str = "unresolvable"   # "ok" | "partial" | "unresolvable"
650:     parse_errors: List[str] = field(default_factory=list)
651: 
652:     def to_metadata_dict(self) -> Dict[str, Any]:
653:         """
654:         Convert to the flat dict expected by register_document().
655: 
656:         Excludes parse_status and parse_errors (internal fields).
657:         Excludes None-valued fields so the registry's schema defaults apply.
658:         """
659:         return {
660:             k: v for k, v in {
661:                 "document_number": self.document_number,
662:                 "revision": self.revision,
663:                 "project_number": self.project_number,
664:                 "area": self.area,
665:                 "document_type": self.document_type,
666:                 "discipline": self.discipline,
667:                 "sequence_number": self.sequence_number,
668:             }.items() if v is not None
669:         }
670: 
671: 
672: class FilenameParser:
673:     """
674:     Schema-driven filename parser — universal class shared by all EKS call sites.
675: 
676:     Design:
677:       - Instantiated once per project per pipeline run.
678:       - Caches compiled regex patterns and resolved schema references.
679:       - .parse(file_name) → FilenameParseResult (never raises).
680:       - Call sites: FileScanner (Phase A), PipelineOrchestrator (Phase B),
681:                     phase1_server.py (UI endpoint).
682: 
683:     Revision: 0.2
684:     Date: 2026-07-18
685:     Author: CodeBuddy
686:     Summary: Universal class with segment-based field extraction,
687:              FilenameParseResult dataclass, cached validators.
688:     """
689: 
690:     # Hardcoded default when no config is available (backward compat with v0.1)
691:     _HARDCODED_DEFAULT: Dict[str, Any] = {
692:         "description": "Hardcoded default (backward-compatible)",
693:         "parser_type": "delimited",
694:         "separator": "-",
695:         "min_segments": 1,
696:         "max_segments": None,
697:         "segments": [],
698:         "rejoin_separator": "-",
699:         "strip_suffixes": [],
700:         "revision_separators": ["_rev"],
701:         "dash_revision_max_len": 3,
702:         "output": {
703:             "document_number_source": "rejoin_segments",
704:             "fallback_doc_number": "full_stem",
705:             "fallback_revision": "00",
706:             "preservation_mode": "overwrite_existing",
707:         },
708:         "error_subcodes": {},
709:         "processing_phase": "P0",
710:     }
711: 
712:     def __init__(
713:         self,
714:         filename_patterns: Optional[Dict[str, Any]] = None,
715:         project_code: Optional[str] = None,
716:         document_type_registry: Optional[List[Dict[str, Any]]] = None,
717:     ):
718:         """
719:         Args:
720:             filename_patterns: The 'filename_patterns' block from eks_doc_config.json.
721:                                If None, use _HARDCODED_DEFAULT.
722:             project_code: Optional project code to select project-specific pattern.
723:                           Falls back to '*' pattern if not found.
724:             document_type_registry: Optional list of document type entries for
725:                                     schema_reference validation (maps_to: "document_type").
726:         """
727:         self._patterns = filename_patterns or {}
728:         self._project_code = project_code
729:         self._doc_type_registry = document_type_registry or []
730:         self._pattern = self._resolve_pattern()
731:         self._compiled_validators: Dict[int, re.Pattern] = {}
732:         self._doc_type_codes: Optional[set] = None
733:         self._precompile_validators()
734: 
735:     # ---- Pattern Resolution ----
736: 
737:     def _resolve_pattern(self) -> Dict[str, Any]:
738:         """Resolve the active pattern: project_code → '*' → hardcoded default."""
739:         if not self._patterns:
740:             return dict(self._HARDCODED_DEFAULT)
741:         pattern = self._patterns.get(self._project_code) if self._project_code else None
742:         if pattern is None:
743:             pattern = self._patterns.get("*", self._HARDCODED_DEFAULT)
744:         # Merge with hardcoded default for any missing keys
745:         merged = dict(self._HARDCODED_DEFAULT)
746:         merged.update(pattern)
747:         return merged
748: 
749:     def _precompile_validators(self) -> None:
750:         """Pre-compile regex patterns for segment validation to avoid re-compile per file."""
751:         for seg in self._pattern.get("segments", []):
752:             validation = seg.get("validation", {})
753:             if validation.get("type") == "pattern" and validation.get("pattern"):
754:                 self._compiled_validators[seg["position"]] = re.compile(validation["pattern"])
755:         # Pre-build document_type lookup set for schema_reference validation
756:         if self._doc_type_registry:
757:             self._doc_type_codes = {entry.get("code", "") for entry in self._doc_type_registry}
758: 
759:     # ---- Main Entry Point ----
760: 
761:     def parse(self, file_name: str) -> FilenameParseResult:
762:         """
763:         Parse a single filename into structured metadata.
764: 
765:         Never raises — always returns FilenameParseResult
766:         with parse_status indicating extraction quality.
767: 
768:         Args:
769:             file_name: Full filename (basename or path; Path.stem will be used).
770: 
771:         Returns:
772:             FilenameParseResult with all extractable fields populated.
773:         """
774:         result = FilenameParseResult()
775:         stem = Path(file_name).stem
776: 
777:         # Step 3: Strip known non-revision suffixes
778:         stem = self._strip_suffixes(stem)
779: 
780:         # Step 4: Revision separator split
781:         doc_stem, revision = self._extract_revision(stem)
782:         if revision is not None:
783:             result.revision = revision
784: 
785:         # Step 6: Segment extraction (on the stem after revision removal)
786:         segments_extracted = self._extract_segments(doc_stem, result)
787: 
788:         # Step 7: Construct document_number
789:         self._build_document_number(doc_stem, segments_extracted, result)
790: 
791:         # Finalize parse_status
792:         if not result.parse_errors:
793:             result.parse_status = "ok"
794:         elif result.parse_status == "unresolvable":
795:             pass  # keep unresolvable
796:         else:
797:             result.parse_status = "partial"
798: 
799:         return result
800: 
801:     # ---- Step 3: Suffix Stripping ----
802: 
803:     def _strip_suffixes(self, stem: str) -> str:
804:         """Strip the first matching non-revision suffix from the stem."""
805:         for suffix in self._pattern.get("strip_suffixes", []):
806:             if stem.endswith(suffix):
807:                 return stem[:-len(suffix)]
808:         return stem
809: 
810:     # ---- Step 4: Revision Extraction ----
811: 
812:     def _extract_revision(self, stem: str) -> Tuple[str, Optional[str]]:
813:         """
814:         Try to extract a revision from the stem.
815: 
816:         Returns (remaining_stem, revision_or_None).
817:         """
818:         # 4a: Check explicit revision separators
819:         for sep in self._pattern.get("revision_separators", []):
820:             if sep in stem:
821:                 parts = stem.split(sep, 1)
822:                 return parts[0], parts[1]
823: 
824:         # 4b: Dash-suffix revision detection
825:         max_len = self._pattern.get("dash_revision_max_len", 0)
826:         if max_len > 0:
827:             parts = stem.rsplit("-", 1)
828:             if len(parts) == 2 and len(parts[1]) <= max_len:
829:                 return parts[0], parts[1]
830: 
831:         return stem, None
832: 
833:     # ---- Step 6: Segment Extraction ----
834: 
835:     def _extract_segments(self, stem: str, result: FilenameParseResult) -> bool:
836:         """
837:         Split stem by separator and extract mapped fields into result.
838: 
839:         Returns True if at least one segment was successfully extracted.
840:         """
841:         segments = self._pattern.get("segments", [])
842:         if not segments:
843:             return False
844: 
845:         parts = stem.split(self._pattern.get("separator", "-"))
846: 
847:         # Check segment count bounds
848:         min_seg = self._pattern.get("min_segments", 1)
849:         max_seg = self._pattern.get("max_segments")
850: 
851:         if len(parts) < min_seg:
852:             err_code = self._pattern.get("error_subcodes", {}).get("too_few_segments", "D5-PARSE-004")
853:             result.parse_errors.append(
854:                 f"{err_code}: Expected >= {min_seg} segments, got {len(parts)} in '{stem}'"
855:             )
856:             result.parse_status = "partial"
857:             # Still try to extract what we have
858: 
859:         if max_seg is not None and len(parts) > max_seg:
860:             err_code = self._pattern.get("error_subcodes", {}).get("too_many_segments", "D5-PARSE-005")
861:             result.parse_errors.append(
862:                 f"{err_code}: Expected <= {max_seg} segments, got {len(parts)} in '{stem}'"
863:             )
864:             result.parse_status = "partial"
865: 
866:         any_extracted = False
867:         for seg_def in segments:
868:             pos = seg_def["position"]
869:             maps_to = seg_def.get("maps_to")
870:             label = seg_def.get("label", f"seg_{pos}")
871: 
872:             if pos >= len(parts):
873:                 # Segment not present — apply null_handling
874:                 self._apply_null_handling(seg_def, result, maps_to, label, reason="missing")
875:                 continue
876: 
877:             raw_value = parts[pos]
878: 
879:             # Validate
880:             if not self._validate_segment(seg_def, raw_value):
881:                 err_code = self._pattern.get("error_subcodes", {}).get(
882:                     "segment_validation_failed", "D5-PARSE-006"
883:                 )
884:                 result.parse_errors.append(
885:                     f"{err_code}: Segment validation failed at position {pos} "
886:                     f"('{label}' = '{raw_value}')"
887:                 )
888:                 result.parse_status = "partial"
889:                 self._apply_null_handling(seg_def, result, maps_to, label,
890:                                           reason=f"validation_failed:{raw_value}")
891:                 continue
892: 
893:             # Store the value
894:             if maps_to:
895:                 setattr(result, maps_to, raw_value)
896:                 any_extracted = True
897:             else:
898:                 # maps_to is null — value used only in rejoined document_number
899:                 # Store in sequence_number for reference
900:                 result.sequence_number = raw_value
901:                 any_extracted = True
902: 
903:         if not any_extracted:
904:             result.parse_status = "unresolvable"
905: 
906:         return any_extracted
907: 
908:     def _validate_segment(self, seg_def: Dict[str, Any], value: str) -> bool:
909:         """Validate a single segment value against its validation rule."""
910:         validation = seg_def.get("validation", {})
911:         vtype = validation.get("type")
912: 
913:         if vtype == "pattern":
914:             compiled = self._compiled_validators.get(seg_def["position"])
915:             if compiled:
916:                 return bool(compiled.match(value))
917:             # Fallback: compile on the fly
918:             pattern = validation.get("pattern", "")
919:             if pattern:
920:                 return bool(re.match(pattern, value))
921:             return True  # no pattern = no validation
922: 
923:         if vtype == "schema_reference":
924:             reference = validation.get("reference", "")
925:             if reference == "document_type_registry" and self._doc_type_codes is not None:
926:                 return value in self._doc_type_codes
927:             # If registry not available, skip validation (warn via parse_status = "partial")
928:             return True
929: 
930:         return True  # unknown validation type → pass
931: 
932:     def _apply_null_handling(
933:         self,
934:         seg_def: Dict[str, Any],
935:         result: FilenameParseResult,
936:         maps_to: Optional[str],
937:         label: str,
938:         reason: str,
939:     ) -> None:
940:         """Apply the segment's null_handling strategy."""
941:         nh = seg_def.get("null_handling", {})
942:         strategy = nh.get("strategy", "default_value")
943: 
944:         if strategy == "default_value":
945:             default = nh.get("default_value", "UNKNOWN")
946:             if maps_to:
947:                 setattr(result, maps_to, default)
948:         elif strategy == "skip_segment":
949:             pass  # leave field as None
950:         elif strategy == "raise_error":
951:             # Degrade gracefully — log as error but don't raise
952:             result.parse_errors.append(
953:                 f"raise_error strategy triggered for segment '{label}' ({reason})"
954:             )
955: 
956:     # ---- Step 7: Document Number Construction ----
957: 
958:     def _build_document_number(
959:         self, stem: str, segments_extracted: bool, result: FilenameParseResult
960:     ) -> None:
961:         """Build the final document_number from segments or fallback."""
962:         output = self._pattern.get("output", {})
963: 
964:         if segments_extracted and output.get("document_number_source") == "rejoin_segments":
965:             # Rejoin all parts of the stem (after suffix/revision stripping)
966:             separator = self._pattern.get("rejoin_separator", "-")
967:             # Use the stem as-is since it's already cleaned of suffixes and revisions
968:             result.document_number = stem
969:         else:
970:             # Fallback
971:             if output.get("fallback_doc_number") == "full_stem":
972:                 result.document_number = stem
973:             else:
974:                 result.document_number = None
975: 
976:         # Apply fallback revision if none extracted
977:         if result.revision is None:
978:             result.revision = output.get("fallback_revision")
979: 
980: 
981: # ---- Module-Level Convenience Function ----
982: 
983: def parse_filename(
984:     file_name: str,
985:     filename_patterns: Optional[Dict[str, Any]] = None,
986:     project_code: Optional[str] = None,
987:     document_type_registry: Optional[List[Dict[str, Any]]] = None,
988: ) -> FilenameParseResult:
989:     """
990:     One-shot convenience wrapper — instantiates FilenameParser per call.
991: 
992:     Prefer instantiating FilenameParser once and calling .parse() in a loop
993:     for batch operations (Phase A scan, pipeline processing).
994:     """
995:     parser = FilenameParser(filename_patterns, project_code, document_type_registry)
996:     return parser.parse(file_name)
997: ```
998: 
999: ### I5.2 Algorithm Steps (Detailed)
1000: 
1001: ```
1002: Input:  file_name, pattern (resolved at __init__)
1003: Output: FilenameParseResult
1004: 
1005: Step 1: [__init__]: Resolve pattern
1006:     pattern = patterns.get(project_code) or patterns.get("*") or _HARDCODED_DEFAULT
1007:     Pre-compile segment validation regex patterns
1008:     Pre-build document_type_registry lookup set
1009: 
1010: Step 2: [parse]: Extract stem
1011:     stem = Path(file_name).stem
1012: 
1013: Step 3: Strip known non-revision suffixes
1014:     for suffix in pattern["strip_suffixes"]:
1015:         if stem.endswith(suffix):
1016:             stem = stem[:-len(suffix)]
1017:             break
1018: 
1019: Step 4: Revision extraction
1020:     4a. Check revision_separators: split on first match
1021:         → left = doc_stem, right = revision
1022:     4b. If dash_revision_max_len > 0:
1023:         rsplit("-", 1); if suffix ≤ max_len → revision
1024:     If no revision found → revision = None
1025: 
1026: Step 5: doc_stem = stem after revision removal (for segment extraction)
1027: 
1028: Step 6: Segment extraction (if pattern.segments is non-empty)
1029:     6a. Split doc_stem by pattern.separator
1030:     6b. Check min/max segment counts → D5-PARSE-004 / D5-PARSE-005 if violated
1031:     6c. For each segment in pattern.segments:
1032:         - If position ≥ len(parts) → apply null_handling (default_value)
1033:         - Validate against segment.validation:
1034:             - "pattern": regex match → D5-PARSE-006 on failure
1035:             - "schema_reference": lookup in registry → D5-PARSE-006 on failure
1036:         - If maps_to is not null → set result.{maps_to} = value
1037:         - If maps_to is null → set result.sequence_number = value
1038:     6d. If no segments extracted → parse_status = "unresolvable"
1039: 
1040: Step 7: Document number construction
1041:     7a. If segments extracted → document_number = doc_stem (segments rejoined)
1042:     7b. Else → fallback_doc_number strategy (full_stem)
1043:     7c. If revision is still None → apply output.fallback_revision
1044: 
1045: Step 8: Finalize parse_status
1046:     - No errors → "ok"
1047:     - Errors but segments extracted → "partial"
1048:     - No segments extracted → "unresolvable"
1049: ```
1050: 
1051: ### I5.3 Worked Examples — TWRP (131101 Pattern)
1052: 
1053: #### Example 1: Clean Standard File
1054: 
1055: ```
1056: Input:  131101-WSW41-SP-SG-0101.pdf
1057: 
1058: Step 2: stem = "131101-WSW41-SP-SG-0101"
1059: Step 3: Strip suffixes → no match
1060: Step 4: _rev split → no _rev; dash-revision: "0101" = 4 chars > 3 → skip
1061: Step 5: doc_stem = "131101-WSW41-SP-SG-0101"
1062: Step 6: Split by "-" → ["131101", "WSW41", "SP", "SG", "0101"]
1063:   6b: count=5, min=5, max=5 → OK
1064:   6c: Segment[0]="131101" → pattern ^\d{6}$ → ✓ → project_number = "131101"
1065:       Segment[1]="WSW41"  → pattern ^[A-Z0-9]{3,6}$ → ✓ → area = "WSW41"
1066:       Segment[2]="SP"     → schema_ref document_type_registry → "SP" in registry? ✓ → document_type = "SP"
1067:       Segment[3]="SG"     → pattern ^[A-Z]{2}$ → ✓ → discipline = "SG"
1068:       Segment[4]="0101"   → pattern ^\d{4}$ → ✓ → sequence_number = "0101" (maps_to=null)
1069: Step 7: document_number = "131101-WSW41-SP-SG-0101", revision = null
1070: Step 8: 0 errors → parse_status = "ok"
1071: 
1072: Result:
1073:   FilenameParseResult(
1074:       document_number="131101-WSW41-SP-SG-0101",
1075:       revision=None,
1076:       project_number="131101",
1077:       area="WSW41",
1078:       document_type="SP",
1079:       discipline="SG",
1080:       sequence_number="0101",
1081:       parse_status="ok",
1082:       parse_errors=[]
1083:   )
1084: ```
1085: 
1086: #### Example 2: Addendum Suffix
1087: 
1088: ```
1089: Input:  131101-WSW41-SP-SP-0801_Add3.pdf
1090: 
1091: Step 2: stem = "131101-WSW41-SP-SP-0801_Add3"
1092: Step 3: Strip "_Add3" → stem = "131101-WSW41-SP-SP-0801"
1093: Step 4: No _rev; dash-revision: "0801" = 4 > 3 → skip
1094: Step 5: doc_stem = "131101-WSW41-SP-SP-0801"
1095: Step 6: Split("-") → ["131101", "WSW41", "SP", "SP", "0801"]
1096:   All 5 segments pass validation → same field mapping as Example 1
1097:   discipline = "SP", sequence_number = "0801"
1098: Step 7: document_number = "131101-WSW41-SP-SP-0801"  (Add3 stripped; stable across addenda)
1099: Step 8: parse_status = "ok"
1100: 
1101: Result:
1102:   FilenameParseResult(
1103:       document_number="131101-WSW41-SP-SP-0801",
1104:       revision=None,
1105:       project_number="131101",
1106:       area="WSW41",

(Output capped at 50 KB. Showing lines 1-1106. Use offset=1107 to continue.)
</content>
```

**Tool: read**

**Input:**
```json
{
  "filePath": "C:\\Users\\franklin.song\\Desktop\\DSAI\\Engineering-and-Design\\eks\\workplan\\phase_1_foundation_workplan.md"
}
```

**Output:**
```
<path>C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\phase_1_foundation_workplan.md</path>
<type>file</type>
<content>
1: # EKS Phase 1 — Foundation: Project Structure, Schema & Document Registry
2: 
3: - **Document ID**: WP-EKS-P1-001
4: - **Current Version**: 5.9
5: - **Status**: 🔷 IN PROGRESS — **v5.13**: §71 (I255 FilenameParser auto-pattern detection ✅). **v5.12**: §70 (I254 path doubling fix ✅). **v5.11**: §64 (I244 default-level verbosity noise — open). Full history in [Appendix P1.6](appendix_p1.6_phase1_revision_history.md).
6: - **Last Updated**: 2026-07-28 (v5.13 — §71 I255 FilenameParser auto-pattern detection ✅ complete)
7: - **Parent Workplan**: [eks_system_workplan.md](eks_system_workplan.md)
8: - **Phase Dependency**: None — first phase
9: 
10: ---
11: 
12: ## 1. Index of Content
13: 
14: - [1. Index of Content](#1-index-of-content)
15: - [2. Title and Description](#2-title-and-description)
16: - [3. Revision History → Appendix P1.6](#3-revision-history--appendix-p16)
17: - [4. Objective](#4-objective)
18: - [5. Evaluation and Alignment with Existing Architecture](#5-evaluation-and-alignment-with-existing-architecture)
19: - [6. Dependencies with Other Tasks](#6-dependencies-with-other-tasks)
20: - [7. Risks and Mitigation](#7-risks-and-mitigation)
21: - [8. Data Export — CSV/Excel Pipeline Output — ✅ COMPLETE](#8-data-export--csvexcel-pipeline-output--complete)
22: - [9. Success Criteria & Deliverables → SC Log + P1.2 §4](#9-success-criteria--deliverables)
23: - [10. Phase 1 Implementation Index](#10-phase-1-implementation-index)
24:   - [10.1 Design & Implementation](#101-design--implementation)
25:   - [10.2 Checklists & Deliverables](#102-checklists--deliverables)
26: - [11. References](#11-references)
27: 
28: ---
29: 
30: ## 2. Title and Description
31: 
32: Establish the EKS project foundation and the canonical, schema-driven pipeline substrate that all subsequent phases build upon. This phase creates the bedrock that all subsequent phases build upon.
33: 
34: Deliverables:
35: - AGENTS.md-compliant project folder structure and conda environment
36: - Canonical 3-layer schema design (base/setup/config) across core, asset, and ontology sets — including the universal plant-item asset schema with 13 reusable fragments and zero-code extensibility, ISO 15926 ontology integration, and the enhanced document schema v2 with type/file/element registries
37: - Schema-driven SSOT global parameters and universal system parameters (runtime behavior config)
38: - Document ingestion plug-ins for PDF/DOCX/XLSX plus a DuckDB-backed document registry with full CRUD and revision management (preserve-all revisions + latest-revision flag)
39: - Tiered logging (levels 0–3), debug object, and structured trace table, along with a schema-driven error/message catalog and per-document 6-dimension health scoring
40: - The end-to-end discovery → register → route → parse → detect → score → review pipeline (auto-DDL generation, file scanner, parser router, orchestrator with rollback, manual review workflow)
41: - Universal path resolution and a converged pipeline entry point (CLI + web + per-phase HTTP backend) funneling through a shared `run_pipeline(context)` / `bootstrap_pipeline()` helper
42: - Initiation integrity, config flattening, cross-cutting remediation, and architectural patterns (BaseEngine, Validator, factories, setup validation, data_dir traversal guard)
43: 
44: ---
45: 
46: ## 3. Revision History → Appendix P1.6
47: 
48: > **All revision history relocated to [Appendix P1.6](appendix_p1.6_phase1_revision_history.md)** — 102 revision entries from v0.1 (2026-06-11) through v5.3 (2026-07-20). Only the high-level eras summary is retained below.
49: 
50: ### Eras Summary
51: 
52: | Era | Versions | Dates | Theme |
53: |:----|:---------|:------|:------|
54: | **Foundation** | v0.1–v2.5 | 2026-06-11 to 2026-06-22 | Folder scaffolding, conda env, 3-layer schemas, document parsers, DuckDB registry, document schema v2 |
55: | **Pipeline Integration** | v3.0–v3.29 | 2026-06-22 to 2026-07-08 | Auto-DDL, file scanner, parser router, orchestrator, Phase 1.3 initiation harmonization, error/message catalog, 6-dim health scoring, project_setup integration, Appendix F architecture patterns |
56: | **Workplan Restructure** | v3.40–v3.52 | 2026-07-09 to 2026-07-11 | Initiation config flattening, schema discovery, system parameters SSOT, universal path resolution, workplan restructuring (Master Task Index), section resequence, canonical workplan promotion |
57: | **Bootstrap & Entry-Point Convergence** | v3.53–v3.87 | 2026-07-11 to 2026-07-20 | Universal BootstrapManager (L19), entry-point relocation (CLI + web + backend), anchor-folder path resolution, cross-platform discovery, universal CLI parser (L18), pre-bootstrap logger (I113), environment checks (I114), structured BootstrapError (I111), preload infrastructure guard (I117), lazy-import refactor |
58: | **Appendix Relocation** | v4.8–v5.0 | 2026-07-20 | §40–§50 defect deep-dives → P1.1; §43 file property extraction → Appendix J; §47 schema-driven export → P1.3; §3 full history → P1.6; 50→11 section collapse; §10 Implementation Index consolidates all appendix redirects |
59: | **Implementation Index Consolidation** | v5.1–v5.3 | 2026-07-20 | §10.1 table enhanced: added Tasks column (P1.4 cross-ref), Key Issues column (issue_log cross-ref), Status column (completion status per section); §10.3 merged into §10.1 as a single 36-row table |
60: | **CLI Default Pipeline Output** | v5.4 | 2026-07-24 | Added §57 row in §10.1 for I234 CLI default pipeline output (T1.112–T1.115); updated §8 to reference I234 default-on export; test_log TL014 added |
61: 
62: ---
63: 
64: ## 4. Objective
65: 
66: - Create the EKS project folder structure compliant with AGENTS.md
67: - Design and implement the canonical schema (base/setup/config pattern)
68: - Build the document registry (metadata DB) with full CRUD support
69: - Implement plug-in document parsers: PDF, DOCX, XLSX
70: - Implement revision management: preserve all revisions, latest revision flag
71: - Establish tiered logging (levels 0–3), debug object, and structured trace table
72: - Implement SSOT global parameter registry via schema-driven config
73: - Design the universal plant-item asset schema (13 reusable fragments, zero-code extensibility) following the canonical fragment pattern
74: - Integrate ISO 15926 ontology (dynamic, config-driven ontology schema with classes, properties, relationships)
75: - Implement the schema-driven error/message catalog and per-document 6-dimension health scoring with structural elements table
76: - Reorganize the document schema into the enhanced 3-layer Document Schema v2 with type/file/element registries
77: - Implement the end-to-end pipeline: auto-DDL generation, file scanner, parser router, pipeline orchestration (with rollback), and manual review workflow
78: - Establish universal path resolution and a converged pipeline entry point (CLI + web + per-phase HTTP backend) funneling through a shared `run_pipeline(context)` / `bootstrap_pipeline()` helper
79: - Deliver initiation integrity, config flattening, cross-cutting remediation, and architectural patterns (BaseEngine, Validator, factories, setup validation, data_dir traversal guard)
80: 
81: ---
82: 
83: ## 5. Evaluation and Alignment with Existing Architecture
84: 
85: - **Schema pattern**: Directly adopts `project_setup_base.json / project_setup.json / project_config.json` from `dcc/config/schemas`
86: - **Logging**: Directly adopts tiered logging and debug object from `dcc/workflow/core_engine/` patterns
87: - **Module design**: SSOT global parameters via schema-driven config per AGENTS.md Section 4
88: - **New**: Document registry with metadata DB is new to this workspace; no prior precedent in DCC
89: 
90: ---
91: 
92: ## 6. Dependencies with Other Tasks
93: 
94: 1. **AGENTS.md** — Governs all coding standards, module design, logging
95: 2. **dcc/config/schemas** — Schema base/setup/config pattern to replicate
96: 3. **External**: DuckDB (preferred for dev) or PostgreSQL for metadata DB
97: 4. **Next Phase**: Phase 2 depends on document registry and parsers from this phase
98: 
99: ---
100: 
101: ## 7. Risks and Mitigation
102: 
103: | Risk                                         | Likelihood | Impact | Mitigation                                                         |
104: | :------------------------------------------- | :--------: | :----: | :----------------------------------------------------------------- |
105: | DB schema changes cascade to downstream code | Medium     | High   | Schema-driven design isolates DB structure from processing logic   |
106: | PDF/DOCX parsing quality varies by doc type  | High       | Medium | Abstract parser interface allows per-format tuning; log errors     |
107: | DWG/DGN parsing requires CAD libraries       | High       | Low    | Deferred to Phase 3; stub plug-in interface stubbed in this phase  |
108: | Schema design diverges from dcc pattern      | Low        | Medium | Explicitly use dcc/config/schemas as template reference            |
109: | Metadata extraction accuracy is low          | Medium     | Medium | Implement Manual Verification workflow in Phase 5                  |
110: 
111: ---
112: 
113: ## 8. Data Export — CSV/Excel Pipeline Output — ✅ COMPLETE
114: 
115: > **Canonical Source**: [appendix_p1.3_phase1_data_export.md](appendix_p1.3_phase1_data_export.md) — full design, implementation, task breakdowns, success criteria, and post-implementation fixes (I188, I189, I192, I193). **I234**: CLI default pipeline output added — see [Task Log §30](../log/phase1/p1_task_log.md#30-cli-default-pipeline-output-i234-tasks).
116: 
117: **Summary**: Human-readable CSV/Excel export of Phase 1 pipeline results (discovery inventory, extraction results, review flags) via universal L22 `DataExporter` module in `common/library/export/`. Schema-driven column resolution (I193) replaces the original hardcoded 11-field subset with ~50 `x_export`-flagged fields. Three post-implementation fixes applied: I188 (empty files), I189 (stale output + test-DB pollution), I192 (root-level copies for user convenience). **I234**: `--export` now defaults to `"both"` (CSV+Excel) via schema-driven `export_default` in `eks_config.json`; CLI also writes `pipeline_output.json` and `debug_log.json` by default (5 output files total). All 6 issues (I126, I188, I189, I192, I193, I234) resolved. Detailed in [Appendix P1.3](appendix_p1.3_phase1_data_export.md) + [Task Log §30](../log/phase1/p1_task_log.md#30-cli-default-pipeline-output-i234-tasks).
118: 
119: ---
120: 
121: ## 9. Success Criteria & Deliverables
122: 
123: > **Success Criteria → [p1_sc_log.md](../log/phase1/p1_sc_log.md)** — 349 success criteria items with issue and task cross-references. Includes all 89 items from retired appendix P1.5 §33 plus per-section criteria, appendix F/I/J items, and Phase 1.2 workplan criteria.
124: >
125: > **Deliverables → [P1.2 §4](appendix_p1.2_phase1_scope.md#4-phase-1-deliverables-consolidated-from-34--37)** — Consolidated deliverable list merged from §34 + §37 of this workplan. Includes all artifacts from schema files through pipeline modules and common library components. Appendix P1.5 (source for SC checklist) is retired — archived at `eks/archive/workplan/appendix_p1.5_phase1_checklists.md`.
126: 
127: ---
128: 
129: ## 10. Phase 1 Implementation Index
130: 
131: > All detailed implementation specifications, task breakdowns, architecture diagrams, and defect analyses have been relocated to dedicated P1.x appendices. This section is a routing table — map from high-level topic to canonical source.
132: 
133: ### 10.1 Design & Implementation
134: 
135: | Original § | Topic | Tasks | Key Issues | Canonical Source |
136: | :---------- | :---- | :---- | :--------- | :--------------- |
137: | §5 | Scope Summary (R01–R100) | — (scoping doc) | — | [P1.2 §1](appendix_p1.2_phase1_scope.md#1-phase-1-scope-summary) |
138: | §8 | Master Task Index | T1.1–T1.99.203 (all 203+) | I001–I233 (all Phase 1) | [Task Log](../log/phase1/p1_task_log.md#status-summary) (§2–23) |
139: | §9 | Pipeline Architecture & 11 Function Tables | — (design doc) | I013, I215, I225, I229, I230 | [P1.1 §3](appendix_p1.1_phase1_architecture.md#3-phase-1-pipeline-architecture--function-tables) |
140: | §10 | Files & Modules to Create/Update | — (per-file index) | I024, I094 | [P1.2 §3](appendix_p1.2_phase1_scope.md#3-files-and-modules-to-createupdate) + [P1.1 §1.3](appendix_p1.1_phase1_architecture.md#13-module-inventory) |
141: | §11 | Project Folder Structure | T1.1 | — | [P1.1 §2](appendix_p1.1_phase1_architecture.md#2-phase-project-folder-structure) |
142: | §12 | Detailed Schema Design | T1.3–T1.5 (design); T1.42–T1.47, T1.50–T1.51 (fragments) | I004, I005, I010, I011, I194 | [Task Log §4](../log/phase1/p1_task_log.md#4-core-schema-suite-basesetupconfig-fragment-schemas-tasks) |
143: | §13 | Parser Module Architecture | T1.8–T1.11 (parsers); T1.9 (abstract base) | I015, I016, I024 | [P1.1 §5](appendix_p1.1_phase1_architecture.md#5-independent-parser-module-architecture) |
144: | §14 | Foundation & Compliance (R99) | T1.1–T1.2, T1.14–T1.16, T1.33, T1.48–T1.49, T1.52–T1.53, T1.55–T1.57, T1.65–T1.67, T1.70, T1.74 | I001, I002, I003, I010, I017–I020, I046, I093, I226, I227 | [Task Log §2](../log/phase1/p1_task_log.md#2-foundation-environment-compliance-r99-tasks) |
145: | §15 | Architectural Patterns — Context, Factories & Orchestration | T1.54, T1.58–T1.64 | I208–I225 (GAP-A1/A18), I230 | [Task Log §3](../log/phase1/p1_task_log.md#3-architectural-patterns-context-factories-orchestration-hardening-appendix-f-tasks) |
146: | §16 | Core Schema Suite (base/setup/config + fragments) | T1.3–T1.6, T1.42–T1.47, T1.50–T1.51 | I004, I005, I010, I011, I022–I023, I026–I027, I029–I031, I194 | [Task Log §4](../log/phase1/p1_task_log.md#4-core-schema-suite-basesetupconfig-fragment-schemas-tasks) + [P1.1 §6.2](appendix_p1.1_phase1_architecture.md#62-core-schema-suite) |
147: | §17 | Asset Schema — Universal Plant Item (R36/R39) | T1.17–T1.20 | I228, I021 | [Task Log §5](../log/phase1/p1_task_log.md#5-asset-schema-universal-plant-item-r36r39-tasks) + [P1.1 §6.3](appendix_p1.1_phase1_architecture.md#63-asset-schema--universal-plant-item) |
148: | §18 | Ontology Integration (R44, ISO 15926) | T1.23–T1.29 | I007, I008 | [Task Log §6](../log/phase1/p1_task_log.md#6-ontology-integration-r44-iso-15926-tasks) + [P1.1 §6.5](appendix_p1.1_phase1_architecture.md#65-ontology-integration-iso-15926) |
149: | §19 | Logging, Errors & Health Scoring (R33/R34/R51) | T1.13, T1.30–T1.32, T1.41, T1.68–T1.69, T1.71, T1.75–T1.76, T1.99.35–T1.99.39 | I014, I105, I195–I198, I199–I203, I204–I207 (GAP-D1/D13) | [Task Log §7](../log/phase1/p1_task_log.md#7-logging-errors-health-scoring-r33r34r51-tasks) + [P1.1 §6.6](appendix_p1.1_phase1_architecture.md#66-error--message-schemas) |
150: | §20 | Document Registry & Revision Management (R02/R21/R22/R29) | T1.7–T1.8, T1.21–T1.22 | I006, I131, I147–I162 (file properties), I184–I187 (registration/change), I212, I224 | [Task Log §8](../log/phase1/p1_task_log.md#8-document-registry-revision-management-r02r21r22r29-tasks) |
151: | §21 | Document Parsers — PDF/DOCX/XLSX (R01/R26) | T1.9–T1.12 | I015, I132, I024, I025, I133–I146, I155, I157, I163 (error codes + FilenameParser) | [Task Log §9](../log/phase1/p1_task_log.md#9-document-parsers-pdfdocxxlsx-r01r26-tasks) + [P1.1 §5](appendix_p1.1_phase1_architecture.md#5-independent-parser-module-architecture) |
152: | §22 | Document Schema v2 — 3-Layer Reorganization (R52/R53) | T1.34, T1.35.1–T1.35.6 | I012, I164–I168 (5 metadata gaps), I169–I175 (7-column bulk), I194 (cross-source) | [Task Log §10](../log/phase1/p1_task_log.md#10-document-schema-v2-3-layer-reorganization-r52r53-tasks) + [P1.1 §6.4](appendix_p1.1_phase1_architecture.md#64-document-schema-v2) |
153: | §23 | Pipeline Orchestration (R54–R58/R57) | T1.36–T1.40, T1.72–T1.73 | I013, I215, I225, I229 | [Task Log §11](../log/phase1/p1_task_log.md#11-pipeline-orchestration-r54r58r57-tasks) + [P1.1 §3,§4](appendix_p1.1_phase1_architecture.md#3-phase-1-pipeline-architecture--function-tables) |
154: | §24 | Initiation Integrity, Hardening & Harmonization | T1.77–T1.83 | I046, I100 | [Task Log §12](../log/phase1/p1_task_log.md#12-initiation-integrity-hardening-harmonization-t177t189-tasks) |
155: | §25 | Initiation Schema & Validation Harmonization | T1.84–T1.89 | I046 | [Task Log §13](../log/phase1/p1_task_log.md#13-initiation-schema-validation-harmonization-t184t189-tasks) |
156: | §26 | Initiation Config Flattening — DCC Pattern | T1.90–T1.95 | — | [Task Log §14](../log/phase1/p1_task_log.md#14-initiation-config-flattening-dcc-projectconfig-pattern-t190t195-tasks) |
157: | §27 | Schema Discovery & Registration — Discovery-Driven Loading | T1.96.1–T1.96.6 | — | [Task Log §15](../log/phase1/p1_task_log.md#15-schema-discovery-registration-discovery-driven-loading-t196-tasks) |
158: | §28 | System Parameters — SSOT Centralization | T1.97.1–T1.97.14 | I091 | [Task Log §16](../log/phase1/p1_task_log.md#16-system-parameters-ssot-centralization-t197-tasks) |
159: | §29 | Universal Path Resolution & Schema-Driven Init | T1.98.1–T1.98.8 | I089, I090, I130 | [Task Log §17](../log/phase1/p1_task_log.md#17-universal-path-resolution-schema-driven-initialization-i089-i090-tasks) |
160: | §30 | Pipeline Entry-Point & Sub-Pipeline Convergence (I092 / R60) | T1.99.1–T1.99.83 | I078, I092, I096–I100, I102–I107, I109–I117, I126, I188–I192, I233 | [Task Log §18](../log/phase1/p1_task_log.md#18-pipeline-entry-point-per-phase-sub-pipeline-convergence-i092-r60-tasks) |
161: | §39 | Bootstrap path-resolution rooting defect fix | — | I130 | [P1.1 §7](appendix_p1.1_phase1_architecture.md#7-issues--fixes--summary-with-cross-references) |
162: | §40 | KeyError: 'revision' in register_placeholders | — | I131 | [P1.1 §7](appendix_p1.1_phase1_architecture.md#7-issues--fixes--summary-with-cross-references) |
163: | §41 | .dwg file type orphan fix (Option B: CAD document type) | — | I132 | [P1.1 §7](appendix_p1.1_phase1_architecture.md#7-issues--fixes--summary-with-cross-references) |
164: | §42 | Unified P-prefix error codes + Appendix I FilenameParser | — | I133–I146, I155, I157, I163 | [P1.1 §7](appendix_p1.1_phase1_architecture.md#7-issues--fixes--summary-with-cross-references) |
165: | §43 | File property extraction — 14 issues, 13 registry columns | — | I147–I162 | [Appendix J §J14](appendix_j_file_property_parser.md#j14-implementation-record--complete) |
166: | §44 | Document metadata completeness — 5 schema gaps | — | I164–I168 | [P1.1 §7](appendix_p1.1_phase1_architecture.md#7-issues--fixes--summary-with-cross-references) |
167: | §45 | Remaining metadata schema gaps — 7-column bulk addition | — | I169–I175 | [P1.1 §7](appendix_p1.1_phase1_architecture.md#7-issues--fixes--summary-with-cross-references) |
168: | §46 | File registration, change detection & cross-project abstraction | — | I184–I187 | [P1.1 §7](appendix_p1.1_phase1_architecture.md#7-issues--fixes--summary-with-cross-references) |
169: | §47 | Schema-driven export columns (~50 fields, replaces 11-field subset) | — | I193 | [P1.3 §5.6](appendix_p1.3_phase1_data_export.md#56-detail-i193--schema-driven-export-columns-t199157-162) |
170: | §48 | Appendix D vs. actual pipeline cross-source audit (13 gaps) | — | I195–I207 | [P1.1 §7](appendix_p1.1_phase1_architecture.md#7-issues--fixes--summary-with-cross-references) |
171: | §49 | Appendix E+F vs. pipeline architecture cross-source audit (18 gaps) | — | I208–I225 | [P1.1 §7](appendix_p1.1_phase1_architecture.md#7-issues--fixes--summary-with-cross-references) |
172: | §50 | `str(5)` bug fix — restore exception messages (13 instances, 4 files) | — | I226 | [P1.1 §7](appendix_p1.1_phase1_architecture.md#7-issues--fixes--summary-with-cross-references) |
173: | §51 | Scan Redundancy — DuckDB SSOT eliminates Phase B re-scan | T1.100, T1.101 | I227 | [Task Log §24](../log/phase1/p1_task_log.md#24-scan-redundancy-eliminate-phase-b-re-scan-via-duckdb-ssot-i227-tasks) |
174: | §52 | Legacy doc_id fallback removal — file_path SSOT lookup, doc_id required | T1.106, T1.107 | I232 | [Task Log §27](../log/phase1/p1_task_log.md#27-legacy-doc_id-fallback-removal-i232-tasks) |
175: | §53 | Batch-level telemetry — per-file checkpoints replaced with 25%/50%/75%/100% milestones | T1.102 | I229 | [Task Log §25](../log/phase1/p1_task_log.md#25-phase-b-telemetry-batch-level-checkpoints-i229-tasks) |
176: | §54 | Cross-phase validation gates — A→B (registry non-empty) and B→C (scores exist) | T1.104 | I230 | [Task Log §26](../log/phase1/p1_task_log.md#26-cross-phase-validation-gates-i230-tasks) |
177: | §55 | Version SSOT — single `__version__` in `eks/__init__.py`; all subpackages import from `eks` | T1.108 | I231 | [Task Log §28](../log/phase1/p1_task_log.md#28-version-ssot-i231-tasks) |
178: | §56 | Pipeline monolith split — `pipeline_engine/` subfolder; entry-point shell (1,284 → 295 lines); zero module-level globals | T1.109–T1.111 | I233 | [Task Log §29](../log/phase1/p1_task_log.md#29-pipeline-monolith-split-i233-tasks) |
179: | §57 | CLI Default Pipeline Output — pipeline_output.json, debug_log.json, schema-driven --export default, 5 default output files | T1.112–T1.115 | I234 | [Task Log §30](../log/phase1/p1_task_log.md#30-cli-default-pipeline-output-i234-tasks) |
180: | §58 | Batch telemetry milestone ordering fix — 100% folded into BATCH_MILESTONES; single sorted loop eliminates out-of-order checkpoints | T1.103, T1.116, T1.117 | I235 | [Task Log §31](../log/phase1/p1_task_log.md#31-batch-telemetry-logic-order-fix-i235-tasks) |
181: | §59 | ERROR_FILE_PROCESSING kwarg mismatch fix — error= → detail= at call site; template kept as SSOT | T1.118, T1.119 | I236 | [Task Log §32](../log/phase1/p1_task_log.md#32-error_file_processing-kwarg-mismatch-fix-i236-tasks) |
182: | §60 | Schema-driven telemetry verbose — `telemetry_verbose` added to `system_parameters` schema chain (base v1.11.0 + config v1.9.0); PipelineOrchestrator passes to TelemetryHeartbeat; milestone prints/suppress verified | T1.120–T1.123 | I237 | [Task Log §33](../log/phase1/p1_task_log.md#33-schema-driven-telemetry-verbosity-i237-tasks) |
183: | §61 | Phase A batch milestones — downgrade per-document STATUS to INFO; add 25/50/75/100% milestone progress in registration loop matching Phase B pattern | T1.124–T1.126 | I238 | [Task Log §34](../log/phase1/p1_task_log.md#34-phase-a-batch-milestones-i238-tasks) |
184: | §62 | ERROR_FILE_PROCESSING level fix — change level from 0 to 1; suppress per-file errors in silent --level 0 mode | T1.127, T1.128 | I242 | [Task Log §35](../log/phase1/p1_task_log.md#35-error_file_processing-level-fix-i242-tasks) |
185: | §63 | STATUS_PHASE_B_COMPLETE kwarg fix — add missing total= to call site; hydrate template placeholders correctly | T1.129, T1.130 | I243 | [Task Log §36](../log/phase1/p1_task_log.md#36-status_phase_b_complete-kwarg-fix-i243-tasks) |
186: | §64 | Default-level verbosity noise — 7 per-document info calls, 3 WARNING codes misrouted to logger.info(), MessageManager verbosity hardcoded to 1 | TBD | I244 | [Issue Log §52](../log/issue_log.md#52--default-level-verbosity-noise-audit-i244) |
187: | §70 | Path doubling fix — strip `eks_root` prefix from relative CLI `--data-dir` in bootstrap path resolution; prevents `eks/eks/data` instead of `eks/data` | T1.156 | I254 | [Task Log §70](../log/phase1/p1_task_log.md#70-path-doubling-fix-i254) |
188: | §71 | FilenameParser auto-pattern detection — try all registered project code patterns per filename, use first match, fall back to `"*"` (0 segments). Unblocks I252 identity field extraction. | T1.157, T1.158 | I255 | [Task Log §71](../log/phase1/p1_task_log.md#71-filenameparser-auto-pattern-detection-i255) |
189: 
190: ### 10.2 Checklists & Deliverables
191: 
192: | Original § | Topic | Canonical Source |
193: | :---------- | :---- | :--------------- |
194: | §33, §36 | Success Criteria (349-item checklist) | [SC Log](../log/phase1/p1_sc_log.md) |
195: | §34 | Deliverables | [P1.2 §4](appendix_p1.2_phase1_scope.md#4-phase-1-deliverables-consolidated-from-34--37) |
196: 
197: ---
198: 
199: ## 11. References
200: 
201: 1. [AGENTS.md](../../AGENTS.md) — Repository guidelines
202: 2. [eks/readme.md](../readme.md) — EKS project overview
203: 3. [dcc/config/schemas](../../dcc/config/schemas) — Schema pattern reference
204: 4. [appendix_a_asset_schema.md](appendix_a_asset_schema.md) — Universal Plant Item Schema appendix
205: 5. [appendix_c_ontology.md](appendix_c_ontology.md) — Dynamic ISO 15926-Aligned Ontology
206: 6. [appendix_d_pipeline_messages_errors.md](appendix_d_pipeline_messages_errors.md) — Pipeline Messages & Error Codes (v0.3)
207: 7. [appendix_e_schema_design.md](appendix_e_schema_design.md) — EKS Schema Design (v0.1)
208: 
209: ### P1.x Appendices
210: 
211: | Appendix | File | Coverage |
212: | :------- | :--- | :------- |
213: | P1.1 | [appendix_p1.1_phase1_architecture.md](appendix_p1.1_phase1_architecture.md) | Architecture & design blueprints |
214: | P1.2 | [appendix_p1.2_phase1_scope.md](appendix_p1.2_phase1_scope.md) | Scope summary, files/modules, deliverables |
215: | P1.3 | [appendix_p1.3_phase1_data_export.md](appendix_p1.3_phase1_data_export.md) | Data export (CSV/Excel) design & implementation |
216: | P1.4 | [p1_task_log.md](../log/phase1/p1_task_log.md) | Task breakdown (replaces retired appendix_p1.4) |
217: | P1.5 | retired — archived at [eks/archive/workplan/](../archive/workplan/appendix_p1.5_phase1_checklists.md) | SC → [SC Log](../log/phase1/p1_sc_log.md); Deliverables → [P1.2 §4](appendix_p1.2_phase1_scope.md#4-phase-1-deliverables-consolidated-from-34--37) |
218: | P1.6 | [appendix_p1.6_phase1_revision_history.md](appendix_p1.6_phase1_revision_history.md) | Full revision history |

(End of file - total 218 lines)
</content>
```

---

## Assistant (Build · DeepSeek V4 Flash Free · 6.2s)

_Thinking:_

I can see that the issue log has been retired and split into phase-specific logs. The active issue log for Phase 1 is at `eks/log/phase1/p1_issue_log.md`. Let me look for I265 there, and also check the task log. I also need to read the phase-specific issue log.

**Tool: glob**

**Input:**
```json
{
  "pattern": "eks/log/phase1/*"
}
```

**Output:**
```
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\log\phase1\p1_update_log.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\log\phase1\p1_test_log.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\log\phase1\p1_task_log.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\log\phase1\p1_sc_log.md
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\log\phase1\p1_issue_log.md
```

**Tool: read**

**Input:**
```json
{
  "filePath": "C:\\Users\\franklin.song\\Desktop\\DSAI\\Engineering-and-Design\\eks\\workplan\\appendix_f_pipeline_architecture_design.md",
  "limit": 100
}
```

**Output:**
```
<path>C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\appendix_f_pipeline_architecture_design.md</path>
<type>file</type>
<content>
1: # Appendix F: EKS Pipeline Architecture Design
2: 
3: **Document ID**: WP-EKS-APPENDIX-F-001  
4: **Current Version**: 1.6  
5: **Status**: 📋 Proposed for Review  
6: **Last Updated**: 2026-06-29  
7: **Parent Workplan**: [Universal Pipeline Architecture Design](../../common/universal_pipeline_architecture_design.md)
8: 
9: ---
10: 
11: ## Revision History
12: 
13: | Revision | Date | Author | Summary |
14: | :--- | :--- | :--- | :--- |
15: | 1.6 | 2026-06-29 | Cascade | Consolidated implementation-related sections (2, 4, 5, 8, 10) into new Section 6 (Implementation Evaluation) at end of document for evaluating current status. Renumbered remaining sections accordingly. Updated index of content. |
16: | 1.5 | 2026-06-29 | Cascade | Added Index of Content section with links to all sections and subsections per AGENTS.md Section 14 (Documentation). |
17: | 1.4 | 2026-06-29 | Cascade | Removed Section 3.3.6 (Implementation Tasks) to ensure Appendix F contains only high-level architecture design. Task-level details moved to phase_1_foundation_workplan.md Section 16. |
18: | 1.3 | 2026-06-26 | Cascade | Restructured Appendix F to focus on high-level pipeline architecture design only. Removed detailed Phase 1.2.x implementation roadmap (moved to phase_1_foundation_workplan.md). Added Section 4: Implementation Guidance with cross-references to phase workplans. |
19: | 1.2 | 2026-06-26 | Cascade | Added Section 3.4: Engine I/O Analysis with comprehensive tabulation of all 60 engines across all 5 phases, documenting input/output types, database operations, and file operations. |
20: | 1.1 | 2026-06-26 | Cascade | Added Section 3.3: Standardized Engine I/O for Independent Execution. Updated Phase 1.2.1 tasks and deliverables to include I/O contracts, CLI entry points, and HTTP API endpoints. |
21: | 1.0 | 2026-06-26 | Cascade | Initial version with EKS-specific application of universal pipeline architecture patterns, including current state assessment, proposed architecture enhancement, and 6-phase implementation roadmap. |
22: 
23: ---
24: 
25: ## Index of Content
26: 
27: - [Revision History](#revision-history)
28: - [1. Executive Summary](#1-executive-summary)
29: - [2. Proposed Architecture Enhancement](#2-proposed-architecture-enhancement)
30:   - [2.1 Target Architecture](#21-target-architecture)
31:   - [2.2 EKSPipelineContext Structure](#22-ekspipelinecontext-structure)
32:   - [2.3 Standardized Engine I/O for Independent Execution](#23-standardized-engine-io-for-independent-execution)
33:     - [2.3.1 Standard Input/Output Contract](#231-standard-inputoutput-contract)
34:     - [2.3.2 Engine-Specific I/O Contracts](#232-engine-specific-io-contracts)
35:     - [2.3.3 Independent Execution Modes](#233-independent-execution-modes)
36:     - [2.3.4 Engine Chaining and Orchestration](#234-engine-chaining-and-orchestration)
37:     - [2.3.5 Benefits of Standardized I/O](#235-benefits-of-standardized-io)
38:   - [2.4 Engine I/O Analysis](#24-engine-io-analysis)
39:     - [Phase 1 Engines (Foundation)](#phase-1-engines-foundation)
40:     - [Phase 2 Engines (Chunking & Embedding)](#phase-2-engines-chunking--embedding)
41:     - [Phase 3 Engines (Knowledge Graph)](#phase-3-engines-knowledge-graph)
42:     - [Phase 4 Engines (Retrieval Pipeline)](#phase-4-engines-retrieval-pipeline)
43:     - [Phase 5 Engines (UI Integration)](#phase-5-engines-ui-integration)
44:     - [I/O Pattern Summary](#io-pattern-summary)
45: - [3. Benefits](#3-benefits)
46:   - [3.1 Maintainability](#31-maintainability)
47:   - [3.2 Testability](#32-testability)
48:   - [3.3 Observability](#33-observability)
49:   - [3.4 Flexibility](#34-flexibility)
50:   - [3.5 User Experience](#35-user-experience)
51: - [4. Risks and Mitigation](#4-risks-and-mitigation)
52: - [5. References](#5-references)
53:   - [5.1 Universal Architecture](#51-universal-architecture)
54:   - [5.2 EKS Documents](#52-eks-documents)
55:   - [5.3 DCC Reference Implementations](#53-dcc-reference-implementations)
56: - [6. Implementation Evaluation](#6-implementation-evaluation)
57:   - [6.1 Current State Assessment (Phase 1)](#61-current-state-assessment-phase-1)
58:     - [Completed Components](#completed-components)
59:     - [Architecture Gaps](#architecture-gaps)
60:   - [6.2 Implementation Guidance](#62-implementation-guidance)
61:   - [6.3 Architecture Comparison](#63-architecture-comparison)
62:   - [6.4 Success Criteria](#64-success-criteria)
63:   - [6.5 Next Steps](#65-next-steps)
64: 
65: ---
66: 
67: ## 1. Executive Summary
68: 
69: This appendix defines the EKS-specific application of universal pipeline architecture patterns documented in the Universal Pipeline Architecture Design. It provides a high-level architecture design for applying these patterns to the Engineering Knowledge System (EKS) pipeline, building on the completed Phase 1 foundation.
70: 
71: ---
72: 
73: ---
74: 
75: ## 2. Proposed Architecture Enhancement
76: 
77: ### 2.1 Target Architecture
78: 
79: ```
80: eks/
81: ├── engine/
82: │   ├── core/              # Foundation: logging, paths, IO, context, base classes
83: │   │   ├── context.py     # EKSPipelineContext
84: │   │   ├── base.py        # BaseEngine, BaseProcessor
85: │   │   ├── telemetry.py   # EKSTelemetryHeartbeat
86: │   │   ├── validator.py   # EKSValidator
87: │   │   ├── factories.py   # ParserFactory, HealthScorerFactory
88: │   │   └── orchestrator.py # PipelineOrchestrator (enhanced)
89: │   ├── parsers/           # Domain: document parsers
90: │   ├── discovery/         # Domain: file scanner
91: │   ├── router/            # Domain: parser router
92: │   ├── registry/          # Domain: document registry
93: │   ├── revision/          # Domain: revision manager
94: │   ├── health/            # Domain: health scorer
95: │   └── structure/         # Domain: structure detector
96: └── ui/
97:     ├── backend/           # Interface: HTTP server, API contracts
98:     │   ├── contracts.py   # DocumentSelectionContract, PipelineConfigContract
99:     │   ├── contract_manager.py # UIContractManager
100:     │   └── server.py      # HTTP server

(Showing lines 1-100 of 663. Use offset=101 to continue.)
</content>
```

**Tool: read**

**Input:**
```json
{
  "filePath": "C:\\Users\\franklin.song\\Desktop\\DSAI\\Engineering-and-Design\\eks\\knowledge.json",
  "limit": 100
}
```

**Output:**
```
<path>C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\knowledge.json</path>
<type>file</type>
<content>
1: {
2:   "$schema": "http://json-schema.org/draft-07/schema#",
3:   "$id": "https://eks.engineering/knowledge.json",
4:   "version": "2.7.0",
5:   "title": "EKS Project Knowledge Base",
6:   "description": "Engineering Knowledge System - machine-readable project blueprint and charter",
7:   "project_metadata": {
8:     "name": "Engineering Knowledge System (EKS)",
9:     "version": "2.6.0",
10:     "description": "Schema-driven document registry and knowledge graph system for engineering asset management",
11:     "purpose": "Ingest, extract, and cross-reference engineering documents to build a searchable knowledge graph",
12:     "status": "Phase 1 through I107/T1.99.45-49 — Bootstrap completeness achieved. bootstrap_pipeline() now handles all init (OS detection, CLI parse, config load once, log-level precedence, single path resolution, single MessageManager). EKSPipelineContext fully threaded through main()/run_pipeline()/orchestrator. Tests 23/23 on pipeline test suite (incl. 4 new I107 integration tests). Defect A (split path source) + Defect B (double MessageManager) fixed. Bugs found and fixed: 1) schema_cli.py anchor kwarg mismatch, 2) main() missing project_root to bootstrap_pipeline, 3) run_pipeline() args=None causing sys.argv bleed, 4) main() missing EKSPipelineContext import.",
13:     "last_updated": "2026-07-16"
14:   },
15:   "architecture_overview": {
16:     "key_modules": [
17:       "engine/core/ - Foundation: registry, revision, config, schema_loader, pipeline orchestration, context, base engine, telemetry, validator, factories, setup_validator",
18:       "engine/parsers/ - Plug-in document parsers (PDF, DOCX, XLSX, DGN, DWG) with parser_router",
19:       "engine/logging/ - Tiered logging infrastructure (levels 0-3)",
20:       "engine/discovery/ - CLI entry points for scheduling engines",
21:       "engine/health/ - CLI entry points for health scorer",
22:       "ui/backend/ - HTTP API endpoints for independent engine execution (12 endpoints + log streaming)",
23:       "ui/ - Interactive dashboard (phase1_ingestion.html, eks.css, eks.js, ui_help.json)",
24:       "config/schemas/ - 3-layer schema pattern (base/setup/config) for 6 schema sets + 4 fragments + project rules"
25:     ],
26:     "data_flows": [
27:       "File Scanner → Parser Router → Parser → Structure Detector → Health Scorer → Document Registry",
28:       "Schema Loader validates base/setup/config chain with $ref resolution",
29:       "ConfigRegistry provides SSOT access to global parameters",
30:       "common.library.config normalizes system_parameters across EKS flat-object and DCC array-entry config shapes"
31:     ],
32:     "integration_points": [
33:       "Main server (port 5000) proxies /api/* to Phase 1 backend (port 5001), serves static UI from eks/ui/",
34:     "DuckDB for document metadata storage",
35:       "Qdrant for vector embeddings (Phase 2)",
36:       "Neo4j for knowledge graph (Phase 3)",
37:       "OpenAI/Ollama for embeddings (Phase 2)"
38:     ]
39:   },
40:   "domain_concepts": {
41:     "core_entities": [
42:       "Document - engineering document with metadata, revisions, structural elements",
43:       "Asset - plant equipment/instrument with fragment-based schema",
44:       "Ontology - ISO 15926-aligned class and relationship definitions",
45:       "Project - WSD11 project codes (131101, 131242)",
46:       "Discipline - engineering disciplines (PI, EL, IN, CI, etc.)"
47:     ],
48:     "relationships": [
49:       "SUBCLASS_OF",
50:       "SUPERSEDES",
51:       "REFERENCES_ASSET",
52:       "PRODUCED_BY",
53:       "IS_A",
54:       "CONNECTS_TO",
55:       "FLOWS_TO",
56:       "INSTALLED_AT",
57:       "CONTROLS",
58:       "ENERGIZED_BY",
59:       "GOVERNED_BY",
60:       "SET_POINT_IN",
61:       "SUPPLEMENTS",
62:       "REFERENCED_BY_DOC",
63:       "FEEDS_FROM"
64:     ],
65:     "terminology": [
66:       "Fragment - reusable property group for asset schema composition",
67:       "3-layer pattern - Base (definitions) → Setup (properties) → Config (values)",
68:       "SSOT - Single Source of Truth for global parameters",
69:       "Health scoring - 6-dimension document quality assessment"
70:     ]
71:   },
72:     "key_schemas": [
73:       "config/schemas/eks_base_schema.json - Core pipeline definitions (v1.9.0, incl. DCC-aligned setup defs, system_parameters_def, workflow_file_entry_def, tool_file_entry_def)",
74:       "config/schemas/eks_setup_schema.json - Core property declarations (v1.7.0, incl. top-level setup values, system_parameters, workflow_files, tool_files)",
75:       "config/schemas/eks_config.json - Core config values (v1.7.0, incl. discovery_rules, system_parameters, workflow_files, tool_files)",
76:       "config/schemas/eks_asset_base_schema.json - Asset fragment definitions (v1.3.0, 14 fragments)",
77:       "config/schemas/eks_doc_base_schema.json - Document metadata definitions (v1.2.0, 8 defs)",
78:       "config/schemas/eks_ontology_base_schema.json - Ontology class/relationship definitions (v1.1.0, 2 defs)",
79:       "config/schemas/eks_error_code_base.json - Error code taxonomy (v1.1.0, 13 defs)",
80:       "config/schemas/eks_message_base.json - Pipeline message catalog (v1.1.0, 6 defs)",
81:       "config/schemas/eks_error_setup_schema.json - Error schema setup layer",
82:       "config/schemas/eks_message_setup_schema.json - Message schema setup layer",
83:       "config/schemas/eks_project_rules_config.json - Project rules SSOT",
84:       "config/schemas/eks_project_code_schema.json - WSD11 project codes fragment",
85:       "config/schemas/eks_discipline_schema.json - 21 discipline codes fragment",
86:       "config/schemas/eks_department_schema.json - 11 department codes fragment",
87:       "config/schemas/eks_facility_schema.json - 12 facility prefixes fragment"
88:     ],
89:     "total_schema_files": 23,
90:   "workflows": [
91:     {
92:       "name": "Document Ingestion Pipeline",
93:       "entry_point": "engine/core/pipeline_orchestrator.py",
94:       "phases": [
95:         "Phase A: File discovery and placeholder registration",
96:         "Phase B: Parse, detect structure, score health",
97:         "Phase C: Manual review and locking"
98:       ]
99:     },
100:     {

(Showing lines 1-100 of 295. Use offset=101 to continue.)
</content>
```

---

## Assistant (Build · DeepSeek V4 Flash Free · 5.6s)

_Thinking:_

Now I need to read the phase 1 issue log to find I265 and the task log. Let me read both.

**Tool: read**

**Input:**
```json
{
  "filePath": "C:\\Users\\franklin.song\\Desktop\\DSAI\\Engineering-and-Design\\eks\\log\\phase1\\p1_issue_log.md"
}
```

**Output:**
```
<path>C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\log\phase1\p1_issue_log.md</path>
<type>file</type>
<content>
1: # Phase 1 Issue Log
2: 
3: **Project**: Engineering Knowledge System (EKS)  
4: **Location**: `eks/log/phase1/p1_issue_log.md`  
5: **Last Updated**: 2026-07-29 — v46 (I264 ⏳ — T1.185 ✅, T1.186 ⏳; 242 total, 10 open, 1 in progress)
6: 
7: ## Legend
8: 
9: ### Status
10: 
11: | Marker | Status | Meaning |
12: |:------:|:-------|:--------|
13: | ✅ | Resolved | Fixed and verified; no remaining action |
14: | 🔴 | Open | Not yet addressed; active in queue |
15: | ⏳ | In Progress | Currently being worked on |
16: | ⏸️ | Deferred | Moved to a future phase |
17: | 🔷 | Deferred for further study | Marked resolved but has unresolved pending work |
18: | 🔷 | Deferred for further review | Requires debate/discussion before action can proceed |
19: | ⛔ | Won't Implement | Explicitly rejected or out of scope |
20: | 🔶 | Open (partial) | Open with partial progress or conditional resolution |
21: | 📐 | Aligned | Issue resolved AND workplan/docs updated to reflect the change |
22: | 🟢 | Approved | Tasks defined and approved; awaiting implementation |
23: 
24: ### Severity
25: 
26: | Marker | Severity | Meaning |
27: |:------:|:---------|:--------|
28: | 🔴 | Critical | Blocks phase completion |
29: | 🟠 | High | Significant impact; workaround needed |
30: | 🟡 | Medium | Moderate impact; can proceed |
31: | 🟢 | Low | Minor, cosmetic, or non-blocking |
32: | 🔷 | Deferred | Moved to future phase; not currently blocking |
33: 
34: ---
35: 
36: ### Status Summary
37: 
38: | Status | Marker | Count |
39: | :----- | :----: | ----: |
40: | Resolved | ✅ | 137 |
41: | Aligned | 📐 | 75 |
42: | Open | 🔴 | 10 |
43: | Approved | 🟢 | 0 |
44: | Deferred (study/review/planned) | 🔷 | 8 |
45: | Deferred | ⏸️ | 0 |
46: | In Progress | ⏳ | 1 |
47: | Won't Implement | ⛔ | 5 |
48: | Open (partial) | 🔶 | 0 |
49: | **Total** | | **242** |
50: 
51: ---
52: 
53: ## Priority Resolution Sequence
54: 
55: Issues below are ordered by resolution priority for Phase 1 completion. Each group should be resolved before moving to the next.
56: 
57: | Seq | Priority | Issue IDs | Count | Theme |
58: | :-: | :------: | :-------- | :---: | :---- |
59: | **1** | 🔵 P2 — Phase 1.2 UI | I064–I071 | 8 | **UI design system** — CSS tokens, theme picker, sidebar, KPI cards, sortable table, icon bar |
60: | **2** | 🔴 P5 — Phase 3 Dependency | I228 | 1 | **Asset schema pipeline gap** — Appendix A has zero runtime integration; risks Phase 3 being blocked |
61: | **3** | ⏳ In Progress | I264 | 1 | **Column processing metadata** — schema-driven ColumnProcessor orchestrator for all 42 document registry columns. T1.182–T1.184 ✅ |
62: | **4** | 🔷 P4 — Deferred | I124, I126, I213, I216, I217, I220, I223, I224 | 8 | **Deferred resolutions** — CLI output (I124/I126), ReviewManager write-back (I213/I224), checkpoint resume (I216), UI contracts (I217), ParserRouter location (I220), per-engine CLI (I223) |
63: 
64: > **Total: 18 outstanding issues** (0 critical, 1 high, 10 medium, 6 low, 1 in progress)
65: 
66: ---
67: 
68: ## Issue Log Table
69: 
70: | ID | Date | Phase | Severity | Title | Description | Status | Tasks | Resolution |
71: | :- | :--- | :---- | :------: | :---- | :---------- | :----: | :---- | :--------- |
72: | I001 | 2026-06-15 | Phase 1 | 🟠 High | Missing __init__.py files in engine packages | engine/__init__.py, engine/core/__init__.py, engine/parsers/__init__.py, engine/logging/__init__.py not created per agent_rule §4.2 and workplan Section 9. | ✅ Resolved | — | Updates: U011 — Close: Created 4 __init__.py files with import statements and version info — Approved: 2026-06-15 |
73: | I002 | 2026-06-15 | Phase 1 | 🟠 High | Missing Phase 1 test report | eks/workplan/reports/phase_1_foundation_report.md not created per workplan Section 13 and agent_rule §9. | ✅ Resolved | — | Updates: U014 — Close: Generated phase_1_foundation_report.md — Approved: 2026-06-15 |
74: | I003 | 2026-06-15 | Phase 1 | 🟡 Medium | Deprecated jsonschema.RefResolver API | schema_loader.py:7 and verify_schema_metadata.py:3 use deprecated RefResolver (deprecated since jsonschema v4.18.0). | ✅ Resolved | — | Updates: U012 — Close: Migrated to referencing library API — Approved: 2026-06-15 |
75: | I004 | 2026-06-15 | Phase 1 | 🟢 Low | Schema metadata fields in properties | eks_setup_schema.json lists $schema, $id, version, title, description as data properties. | ✅ Resolved | — | Updates: U013 — Close: Removed metadata fields from eks_setup_schema.json properties; config strips before validation — Approved: 2026-06-15 |
76: | I005 | 2026-06-18 | Phase 1 | 🟢 Low | eks_config.json contains placeholder project data | project_rules_registry and discipline_registry contain dummy entries (P123, P456). | ✅ Resolved | T1.46 | Close: Replaced P123/P456 with real WSD11 project codes (131101, 131242); added $ref to fragment schemas — Approved: 2026-06-18 |
77: | I006 | 2026-06-16 | Phase 1 | 🟠 High | Document Registry Technical Gaps (G1-G3) & Extended Metadata | Critical gaps identified: missing source_type (G1); SQL injection risk in filters (G2); Python-side sorting in get_revision_history (G3). Added 11 extended metadata fields. | ✅ Resolved | T1.21/T1.22 | Close: Added source_type, 11 extended fields to schema/DB; implemented COLUMN_ALLOWLIST; migrated sorting to SQL ORDER BY; added JSON array support for asset_tags — Approved: 2026-06-16 |
78: | I007 | 2026-06-18 | Phase 1 | 🟠 High | Ontology Schema Refactor to Triple-File Pattern | eks_ontology_schema.json did not follow the Base/Setup/Config pattern. | ✅ Resolved | — | Close: Split into eks_ontology_base_schema.json and eks_ontology_setup_schema.json with explicit allOf inheritance; updated SchemaLoader — Approved: 2026-06-18 |
79: | I008 | 2026-06-18 | Phase 1 | 🟡 Medium | Inconsistent Ontology Config Filename | eks_ontology.json name inconsistent with _config.json suffix. | ✅ Resolved | — | Close: Renamed to eks_ontology_config.json and updated all internal/external references — Approved: 2026-06-18 |
80: | I010 | 2026-06-22 | Phase 1 | 🟠 High | Schema files not consolidated under eks/config/schemas/ | Core, asset, and ontology schema/config files (9 JSON files) resided at eks/config/ root while only error/message schema files were in eks/config/schemas/. | 📐 Aligned | T1.33 | Updates: U051 — Close: Verified all 13 schema/config files in eks/config/schemas/; updated test_phase1.py — Workplan: phase_1_foundation_workplan.md — Approved: 2026-06-22 |
81: | I011 | 2026-06-22 | Phase 1 | 🟡 Medium | Document schema definitions mixed with pipeline config in eks_base_schema.json | document_metadata_def (11 fields) and project_metadata_def embedded with pipeline config definitions. | ✅ Resolved | T1.34 | Close: Created eks_doc_base_schema.json, eks_doc_setup_schema.json, eks_doc_config.json; removed doc defs from eks_base_schema.json — Approved: 2026-06-22 |
82: | I012 | 2026-06-22 | Phase 1 | 🟡 Medium | Document schema v1 lacks business logic enums and registries | Unset document_type, no file_type definition, no element_type enum. Missing registries. | ✅ Resolved | T1.35 | Close: Added document_type_code (7), file_type_code (5), element_type_code (8) enums with registries; refactored element_expectations keys; added 6 tests; created DGN/DWG parser stubs — Approved: 2026-06-22 |
83: | I013 | 2026-06-22 | Phase 1 | 🟠 High | No automated pipeline: database creation, parsing, scoring, and review are disconnected | Workflow: (1) registry.py creates DB with hard-coded DDL, (2) parsers run independently, (3) HealthScorer.score() not wired, (4) no file scanner, (5) no parser router, (6) no manual review workflow. | ✅ Resolved | T1.36–T1.40 | Close: SchemaToDDL auto-generates DDL; FileScanner walks directory; ParserRouter maps file_type; PipelineOrchestrator coordinates 3-phase pipeline; ManualReviewManager surfaces flagged docs. All 53 tests pass. — Approved: 2026-06-22 |
84: | I014 | 2026-06-22 | Phase 1 | 🟠 High | Error/message schemas missing 3-layer pattern — no setup layer | No eks_error_setup_schema.json or eks_message_setup_schema.json exist. Config files contain $schema/$id fields. | ✅ Resolved | T1.41 | Updates: U067 — Close: T1.41 — Created eks_error_setup_schema.json and eks_message_setup_schema.json; cleaned config files; updated SchemaLoader. All 53 tests pass. — Approved: 2026-06-22 |
85: | I017 | 2026-06-23 | Phase 1 | 🟢 Low | Mixed file types per submittal require per-file parser routing | Single submittals contain PDF+DOCX+XLSX+DGN files. ParserRouter correctly routes by file extension. | ✅ Resolved | T1.38 | Close: ParserRouter handles per-file routing via file_type_registry. Verified with twrp data patterns. — Approved: 2026-06-23 |
86: | I018 | 2026-06-23 | Phase 1 | 🟢 Low | Temp files (Thumbs.db, ~$ lock files) must be filtered | Thumbs.db found in 6 revision folders; MS Word lock file found. | ✅ Resolved | T1.37 | Close: FileScanner filters by file_type_registry extensions; Thumbs.db (.db), ~$ (temp), .zip, .msg, .lnk not registered. — Approved: 2026-06-23 |
87: | I022 | 2026-06-23 | Phase 1 | 🟡 Medium | Duplicate revision_id definition in base and doc base | revision_id defined identically in eks_base_schema.json and eks_doc_base_schema.json. | ✅ Resolved | T1.48 | Updates: U087 — Close: Removed revision_id from eks_base_schema.json; moved to eks_doc_base_schema.json — Approved: 2026-06-23 |
88: | I023 | 2026-06-23 | Phase 1 | 🟡 Medium | Duplicate discipline_code definition in base and doc base | discipline_code defined in both eks_base_schema.json and eks_doc_base_schema.json. | ✅ Resolved | T1.48 | Close: Removed from eks_base_schema.json. Doc base $ref now points to discipline_entry_def.properties/code. — Approved: 2026-06-23 |
89: | I024 | 2026-06-23 | Phase 1 | 🟠 High | Parser import path mismatch: engine.parsers.* vs eks.engine.parsers.* | eks_config.json uses engine.parsers.* while eks_doc_config.json uses eks.engine.parsers.* | ✅ Resolved | T1.48 | Close: Both configs now use eks.engine.parsers.* path. — Approved: 2026-06-23 |
90: | I025 | 2026-06-23 | Phase 1 | 🟡 Medium | Missing DGN/DWG parsers in eks_config.json | eks_config.json parsers only has 3 entries but file_type_registry has 5 file types. | ✅ Resolved | T1.48 | Close: Added DGN/DWG stub parsers to eks_config.json. — Approved: 2026-06-23 |
91: | I026 | 2026-06-23 | Phase 1 | 🟠 High | Missing $schema in eks_error_config.json and eks_message_config.json | Both config files lack $schema field to reference their setup schemas. Validation chain broken. | ✅ Resolved | T1.48 | Updates: U090 — Close: Added $schema field to both config files referencing respective setup schemas — Approved: 2026-06-23 |
92: | I027 | 2026-06-23 | Phase 1 | 🟢 Low | URI naming inconsistency in error/message base schemas | eks_error_code_base.json uses path-based URI vs filename-based URIs for all other schemas. | ✅ Resolved | T1.48 | Updates: U078 — Close: Aligned to filename-based pattern; updated all $ref and Registry().with_resources() calls — Approved: 2026-06-23 |
93: | I028 | 2026-06-23 | Phase 1 | 🟡 Medium | Config metadata fields break setup schema validation | T1.48 added $schema, $id, version, title, description to config files, violating additionalProperties: false. | ✅ Resolved | T1.48 | Updates: U077 — Close: Removed metadata fields from both config files. All 114 tests pass. — Approved: 2026-06-23 |
94: | I029 | 2026-06-24 | Phase 1 | 🟡 Medium | discipline_registry uses oneOf violating SSOT | discipline_registry can be either $ref or inline array — SSOT violation. | ✅ Resolved | — | Updates: U082 — Close: Removed oneOf, changed to $ref-only. eks_setup_schema.json v1.2.0→v1.2.1 — Approved: 2026-06-24 |
95: | I030 | 2026-06-24 | Phase 1 | 🟡 Medium | project_rules inline in config violates SSOT | eks_config.json contained inline project_rules values instead of dedicated fragment file. | ✅ Resolved | — | Updates: U083 — Close: Created eks_project_rules_config.json; updated eks_setup_schema.json and eks_config.json to $ref it — Approved: 2026-06-24 |
96: | I031 | 2026-06-24 | Phase 1 | 🟡 Medium | document_relationship_trigger_map base layer prescribes actual values | Base schema defines properties with enum values and required — these are mapping data, not structural constraints. | ✅ Resolved | T1.50 | Updates: U086 — Close: Stripped properties/required from base definition, keeping only shape. Config files now sole SSOT. — Approved: 2026-06-24 |
97: | I032 | 2026-06-24 | Phase 1 | 🟡 Medium | revision_id defined in base schema but only used by doc schema set | revision_id is consumed only by eks_doc_base_schema.json via $ref. Not a cross-cutting type. | ✅ Resolved | T1.50 | Updates: U087 — Close: Moved revision_id to eks_doc_base_schema.json; added revision_validation to doc setup+config — Approved: 2026-06-24 |
98: | I033 | 2026-06-25 | Docs | 🟡 Medium | Appendix E: eks_base_schema.json version stale (shows v1.3.1, actual v1.5.0) | E5.1 lists v1.3.1 but actual file is v1.5.0. | ✅ Resolved | — | Close: Updated E5.1 version to 1.5.0 in Appendix E v0.7. — Approved: 2026-06-25 |
99: | I034 | 2026-06-25 | Docs | 🟡 Medium | Appendix E: eks_setup_schema.json version stale (shows v1.2.0, actual v1.2.2) | E5.1 lists v1.2.0 but actual file is v1.2.2. | ✅ Resolved | — | Close: Updated E5.1 version to 1.2.2 in Appendix E v0.8. — Approved: 2026-06-25 |
100: | I035 | 2026-06-25 | Docs | 🟡 Medium | Appendix E: eks_doc_base_schema.json version stale (shows v1.1.2, actual v1.2.0) | E5.1 lists v1.1.2 but actual file is v1.2.0. | ✅ Resolved | — | Close: Updated E5.1 version to 1.2.0 in Appendix E v0.8. — Approved: 2026-06-25 |
101: | I036 | 2026-06-25 | Docs | 🟡 Medium | Appendix E: eks_doc_setup_schema.json version stale (shows v1.2.0, actual v1.3.0) | E5.1 lists v1.2.0 but actual file is v1.3.0. | ✅ Resolved | — | Close: Updated E5.1 version to 1.3.0 in Appendix E v0.8. — Approved: 2026-06-25 |
102: | I037 | 2026-06-25 | Docs | 🟡 Medium | Appendix E: eks_base_schema.json definition count wrong (shows 14, actual 13) | Since revision_id was moved to doc base, count is 13 not 14. | ✅ Resolved | — | Close: Updated count to 13 in Appendix E v0.8. — Approved: 2026-06-25 |
103: | I038 | 2026-06-25 | Docs | 🟡 Medium | Appendix E: revision_id still listed as Core Base definition in E5.1 | Following I032, revision_id lives exclusively in eks_doc_base_schema.json. | ✅ Resolved | — | Close: Removed revision_id from Core Base row in Appendix E v0.7. Updated E5.4 note 2. — Approved: 2026-06-25 |
104: | I039 | 2026-06-25 | Docs | 🟡 Medium | Appendix E: Document Setup missing revision_validation property | E5.1 shows 6 props, actual is 7 (including revision_validation). | ✅ Resolved | — | Close: Added revision_validation to Document Setup key content; updated count to 7 in Appendix E v0.8. — Approved: 2026-06-25 |
105: | I040 | 2026-06-25 | Docs | 🟡 Medium | Appendix E E5.3 Summary Matrix: Document Setup count wrong (shows 6, should be 7) | E5.3 Document row shows Setup: 6, correct is 7. | ✅ Resolved | — | Close: Updated Document Setup count from 6 to 7 in Appendix E v0.9. — Approved: 2026-06-25 |
106: | I041 | 2026-06-25 | Docs | 🟢 Low | Appendix E E11.4: Ontology relationship count wrong (shows 14, actual is 15) | E11.4 trace table says 14, actual eks_ontology_config.json has 15. | ✅ Resolved | — | Close: Updated E11.4 to 15 relationships in Appendix E v0.9. — Approved: 2026-06-25 |
107: | I042 | 2026-06-25 | Docs | 🟢 Low | Appendix E E5.1: Error Setup property count inconsistent (shows 5, actual is 6) | Actual properties are 6: metadata, system_error_ranges, system_errors, data_error_ranges, data_logic_errors, migration_log. | ✅ Resolved | — | Close: Updated Error Setup count to 6 in E5.1 in Appendix E v0.8. — Approved: 2026-06-25 |
108: | I043 | 2026-06-25 | Docs | 🟢 Low | Appendix E E12 Aggregate Summary: Document required count wrong (shows 3 req, should be 4) | revision_validation is in required array, making it 4 required properties. | ✅ Resolved | — | Close: Updated E12 Document row to (4 req) in Appendix E v0.9. — Approved: 2026-06-25 |
109: | I044 | 2026-06-25 | Docs | 🟢 Low | Appendix E: Internal inconsistency — E5.1 vs E11.1 setup schema version | E5.1 shows v1.2.0 while E11.1 correctly says v1.2.2. | ✅ Resolved | — | Close: Resolved when I034 was fixed in Appendix E v0.8. — Approved: 2026-06-25 |
110: | I045 | 2026-06-30 | Phase 1 | 🟠 High | $schema field re-introduced in error/message config files, breaking all phase 1 tests | Regression from I028 — metadata fields re-appeared violating additionalProperties: false. | ✅ Resolved | — | Close: Removed $schema from both config files. All 118 tests pass. — Approved: 2026-06-30 |
111: | I046 | 2026-06-30 | Phase 1 | 🟡 Medium | project_setup.json violates AGENTS.md §9 3-layer pattern | Standalone schema with 7 compliance violations: missing base/config, no allOf/$ref, inline defs, defaults in setup, never read by setup_validator.py. | 📐 Aligned | T1.66/T1.67 | Updates: U093 — Close: Added 4 defs to base v1.6.0, project_setup property to setup v1.3.0, values to config v1.4.0; archived project_setup.json; refactored setup_validator.py — Workplan: phase_1_foundation_workplan.md — Approved: 2026-06-30 |
112: | I047 | 2026-07-02 | Phase 1.2 | 🟠 High | eks/server.py routes GET / to static index.html — _build_index() not wired | do_GET calls _serve_static("index.html") at root. Dynamic tool-picker required by AGENTS.md not implemented. | ✅ Resolved | — | Close: Implemented _build_index() with SCAN_DIRS, EXCLUDE_DIRS, live search, card grid, status bar. — Approved: 2026-07-02 |
113: | I048 | 2026-07-02 | Phase 1.2 | 🟠 High | Phase 1 API endpoints lack /api/v1/ prefix | All 12 Phase 1 backend endpoints built without version prefix required by Appendix G. | ✅ Resolved | — | Close: All 13 endpoints migrated to /api/v1/ in phase1_server.py; all fetch() calls use /api/v1/. — Approved: 2026-07-02 |
114: | I049 | 2026-07-02 | All | 🟠 High | No port availability check | server.py binds to default port without checking if occupied. Corporate machines may block ports 5000–5002. | ✅ Resolved | — | Close: Added find_free_port() with socket.connect_ex() probe. Auto-increments up to 100 attempts. — Approved: 2026-07-02 |
115: | I050 | 2026-07-02 | Phase 1.2 | 🟡 Medium | CDN Chart.js fails on restricted networks | index.html loads Chart.js from CDN. Font stack missing system-ui. | ✅ Resolved | — | Close: Chart.js v4.4.4 self-hosted at static/chart.min.js. Font stack uses system-ui via --font-ui token. — Approved: 2026-07-02 |
116: | I051 | 2026-07-02 | All | 🟡 Medium | No backend readiness check | If conda env not activated, engine imports fail with bare ModuleNotFoundError. | ✅ Resolved | — | Close: All engine imports wrapped in try/except ImportError. Returns HTTP 503 with install guidance. — Approved: 2026-07-02 |
117: | I052 | 2026-07-02 | All | 🟡 Medium | Windows path normalization | Proxy constructs URLs using self.path directly. Static file traversal guard not implemented. | ✅ Resolved | — | Close: Path.is_relative_to() traversal guard returning 403. URL construction uses .as_posix(). — Approved: 2026-07-02 |
118: | I053 | 2026-07-02 | Phases 2–5 | 🟡 Medium | No DuckDB cross-process locking guidance | Multiple phase servers opening shared eks_registry.db may cause lock contention. | ✅ Resolved | — | Close: _with_retry() implemented with 3 retries, 0.5s delay. Phase 1 concurrency guard (HTTP 409). — Approved: 2026-07-02 |
119: | I055 | 2026-07-02 | Phase 1.2 | 🟡 Medium | No cache busting headers on any server response | Neither server overrides end_headers(). Polling endpoints return stale data. | ✅ Resolved | — | Close: Both servers override end_headers() to inject Cache-Control: no-cache, no-store, must-revalidate. — Approved: 2026-07-02 |
120: | I056 | 2026-07-02 | Phase 1.2 | 🟡 Medium | No urllib.parse.unquote() on path matching | Percent-encoded paths like DWG%20001 don't match route segments. | ✅ Resolved | — | Close: unquote() applied to all path matching in server.py and phase1_server.py. — Approved: 2026-07-02 |
121: | I057 | 2026-07-02 | Phase 1.2 | 🟢 Low | ConnectionResetError not suppressed | Neither server overrides handle_error(). Browser polling floods console with tracebacks. | ✅ Resolved | — | Close: Both servers override handle_error() to silently suppress ConnectionResetError. — Approved: 2026-07-02 |
122: | I058 | 2026-07-02 | Phase 1.2 | 🟡 Medium | Proxy timeout is 30s not 120s | server.py uses urlopen(req, timeout=30). Long pipelines need 120s. | ✅ Resolved | — | Close: API proxy uses timeout=120. Ollama proxy uses timeout=30 per design. — Approved: 2026-07-02 |
123: | I059 | 2026-07-02 | Phase 1.2 | 🔴 Critical | GET /api/files/load called but only POST exists | eks.js calls apiGet('/files/load') but only POST /api/files/load exists. File loading never works. | ✅ Resolved | — | Close: loadFiles() uses apiPost('/api/v1/files/load'). Wired to button and startup. — Approved: 2026-07-02 |
124: | I060 | 2026-07-02 | Phase 1.2 | 🔴 Critical | POST /api/review/submit called but backend only has PUT | eks.js calls apiPost('/review/submit'). Backend has PUT /api/review/{action} only. | ✅ Resolved | — | Close: eksSubmitReview() calls apiPut('/api/v1/review/lock', {...}). apiPut helper added. — Approved: 2026-07-02 |
125: | I061 | 2026-07-02 | Phase 1.2 | 🔴 Critical | Response format mismatch | Backend returns {discovered, files} but frontend expects {documents: [...]}. | ✅ Resolved | — | Close: After POST succeeds, loadFiles() calls GET /api/v1/documents to fetch document list. — Approved: 2026-07-02 |
126: | I062 | 2026-07-02 | Phase 1.2 | 🔴 Critical | Parameter name mismatch — frontend sends {dir: ...} but backend reads {data_dir: ...} | eks.js sends {dir: dir \|\| 'eks/data'}. Backend reads data.get("data_dir", "eks/data"). | ✅ Resolved | — | Close: loadFiles() sends {data_dir: path} matching backend's expected parameter name. — Approved: 2026-07-02 |
127: | I063 | 2026-07-02 | Phase 1.2 | 🔴 Critical | loadFiles() (correct POST) never wired to any UI element | Function defined but never referenced by any event listener. | ✅ Resolved | — | Close: loadFiles() wired to #btn-load-files, startup, and icon bar button. — Approved: 2026-07-02 |
128: | I064 | 2026-07-02 | Phase 1.2 | 🟡 Medium | eks.js Chart.js runtime fallback still uses CDN path | Runtime fallback loads from CDN when static tag fails. Must use self-hosted path. | 🔴 Open | T1.2.8.5 | Close: Fix in T1.2.8.5 expansion. |
129: | I065 | 2026-07-02 | Phase 1.2 | 🟡 Medium | CSS design tokens don't match AGENTS.md §18.3 required names | Uses --bg-primary, --bg-secondary instead of --surface, --surface2. 16 token groups missing. | 🔴 Open | T1.2.9.1 | Close: Fix in T1.2.9.1. |
130: | I066 | 2026-07-02 | Phase 1.2 | 🟢 Low | No theme transition CSS | body rule has no transition property. Theme switching is instant. | 🔴 Open | T1.2.9.1 | Close: Fix in T1.2.9.1. |
131: | I067 | 2026-07-02 | Phase 1.2 | 🟢 Low | Theme picker is a cycle button, not a dropdown menu | Cycles through 5 themes sequentially instead of dropdown menu with color dots. | 🔴 Open | T1.2.9.2 | Close: Fix in T1.2.9.2. |
132: | I068 | 2026-07-02 | Phase 1.2 | 🟡 Medium | Right sidebar only shows Document Detail — no Settings or Help views | AGENTS.md requires dual-purpose: Settings/Help/Detail context-sensitive views. | 🔴 Open | T1.2.9.3 | Close: Fix in T1.2.9.3. |
133: | I069 | 2026-07-02 | Phase 1.2 | 🟡 Medium | Dashboard has no KPI card grid or stage cards | Documents tab shows table instead of KPI tiles. Pipeline tab shows single progress bar. | 🔴 Open | T1.2.9.4 | Close: Fix in T1.2.9.4. |
134: | I070 | 2026-07-02 | Phase 1.2 | 🟡 Medium | Data table has no sortable columns, no row cap, no active highlight | No JS sort handler, no 50-row cap, no selected-row highlight. | 🔴 Open | T1.2.9.5 | Close: Fix in T1.2.9.5. |
135: | I071 | 2026-07-02 | Phase 1.2 | 🟢 Low | Icon bar 36px (should be 48px); multiple UI polish gaps | Icon bar width, drag-drop scope, sidebar persistence, file input, icons all need alignment with AGENTS.md. | 🔴 Open | T1.2.9.6 | Close: Fix in T1.2.9.6. |
136: | I072 | 2026-07-02 | Phase 1.2 | 🔴 Critical | /ui/ prefix stripped but ui/ directory not re-added | _serve_static(path[4:]) resolves to ROOT/index.html instead of ROOT/ui/index.html. | ✅ Resolved | — | Close: Fixed: prepend "ui/" — _serve_static("ui/" + path[4:]). All 28 tests pass. — Approved: 2026-07-02 |
137: | I073 | 2026-07-07 | Phase 1.2 | 🔴 Critical | #pipeline-progress element missing from HTML | document.getElementById('pipeline-progress') returns null. TypeError on every pipeline run. | ✅ Resolved | — | Close: Added div.progress-container with #pipeline-progress fill element. — Approved: 2026-07-07 |
138: | I074 | 2026-07-07 | Phase 1.2 | 🔴 Critical | hideHelp() called but never defined | hideHelp is never defined. Throws ReferenceError on help modal click. | ✅ Resolved | — | Close: Replaced hideHelp() with comUI.modal.close('help-modal'). — Approved: 2026-07-07 |
139: | I075 | 2026-07-07 | Phase 1.2 | 🔴 Critical | loadFiles() has no try/catch | Any network error silently swallowed — button appears to do nothing. | ✅ Resolved | — | Close: Wrapped in try/catch/finally with status bar update and toast notification. — Approved: 2026-07-07 |
140: | I076 | 2026-07-07 | Phase 1.2 | 🔴 Critical | Pipeline progress never updates mid-run — stays 0% until completion | _job_state progress only set to 100 on completion. Bar shows 0% then jumps to 100%. | ✅ Resolved | — | Close: Split run into sequential phase A/B/C calls. Progress: A=20%, B=75%, C=90%, done=100%. — Approved: 2026-07-07 |
141: | I077 | 2026-07-07 | Phase 1.2 | 🟠 High | Stage cards infer active stage from progress % — wrong mapping | Linear progress-to-stage mapping wrong for 3-phase orchestrator with unequal durations. | ✅ Resolved | — | Close: Added current_stage field; renderStageCards() reads data.current_stage instead of inferring. — Approved: 2026-07-07 |
142: | I079 | 2026-07-09 | Phase 1 | 🔴 Critical | Initiation readiness failure not wired to ErrorManager / error catalog | P1-SETUP-* error codes never attached to validate_all() results. Readiness raises generic RuntimeError. | ✅ Resolved | T1.78/T1.79 | Close: P1-SETUP-* codes attached to validation results; readiness raised through ErrorManager. setup_validator.py v0.4. — Approved: 2026-07-09 |
143: | I080 | 2026-07-09 | Phase 1 | 🟠 High | Hardcoded output/eks.yml paths in initiation violate schema-driven design | setup_validator.py hardcodes paths not backed by schema fields. | ✅ Resolved | T1.80 | Close: paths derived from config.global_paths.output_dir + required_files membership. — Approved: 2026-07-09 |
144: | I081 | 2026-07-09 | Phase 1 | 🟡 Medium | Hardcoded fallback lists duplicate eks_config.json (SSOT violation) | required_folders, required_engine_subfolders, required_files lists duplicate config values. 15-package dependency list also duplicates config. | ✅ Resolved | T1.81 | Close: Removed all 4 hardcoded fallback lists; raises ValueError if config absent. — Approved: 2026-07-09 |
145: | I082 | 2026-07-09 | Phase 1 | 🟡 Medium | Schema-driven validation_options.auto_create_folders ignored by readiness gate | phase1_server.py hardcodes auto_create=True, ignoring project_setup config value. | ✅ Resolved | T1.82 | Close: phase1_server.py passes config-driven value with fallback True. — Approved: 2026-07-09 |
146: | I083 | 2026-07-09 | Phase 1 | 🟢 Low | Hardcoded data_dir/global_paths defaults in server | Defaults data_dir to literal "eks/data" while config has "data". Hardcoded fallback global_paths dict. | ✅ Resolved | T1.82 | Close: defaults derived from config.global_paths. — Approved: 2026-07-09 |
147: | I084 | 2026-07-09 | Phase 1 | 🟢 Low | eks package root hardcoded 9× in phase1_server | All PRJ_DIR/"eks"/... literals for config/archive/log/schema dirs. | ✅ Resolved | T1.83 | Close: eks_root added to global_paths_def schema + config; all 10 PRJ_DIR/"eks" literals replaced. — Approved: 2026-07-09 |
148: | I085 | 2026-07-09 | Phase 1 | 🟡 Medium | EKS project_setup schema diverges from DCC's universal pattern | EKS uses flat string arrays; DCC uses rich object arrays with discovery_rules. | 📐 Aligned | T1.84–T1.89 | Close: Created shared ValidationManager; reshaped EKS to DCC object model; extracted eks_project_setup_config.json. 235/235 tests pass. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-09 |
149: | I086 | 2026-07-09 | Phase 1 | 🟡 Medium | Residual project_setup wrapper in eks_config.json contradicted DCC | EKS nested setup under project_setup subkey; DCC keeps top-level. | 📐 Aligned | T1.90–T1.95 | Close: Flattened eks_config.json to top-level; dropped wrapper in setup schema v1.5.0; deleted orphan. 236/236 tests pass. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-09 |
150: | I087 | 2026-07-10 | Phase 1 | 🟡 Medium | EKS config lacks discovery_rules (schema auto-discovery gap) | DCC project_config.json defines discovery_rules for automatic schema discovery. EKS has none. | 📐 Aligned | T1.96 | Close: Added 5 discovery_rules to eks_config.json. Extracted discover_schema_files() to common/library/. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-10 |
151: | I088 | 2026-07-10 | Phase 1 | 🟡 Medium | EKS config lacks system_parameters (loader/validator behavior flags) | log_level, retry, timeout, schema_cache_ttl spread across hardcoded values and separate configs. | 📐 Aligned | T1.97 | Close: Added universal config helpers, system_parameters_def in base schema, system_parameters in config. 243/243 pass. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-10 |
152: | I089 | 2026-07-10 | Phase 1 | 🟡 Medium | Path model mismatch: EKS global_paths vs DCC discovery-relative paths | EKS static paths vs DCC discovery-relative. Universal loader must normalize both. | 📐 Aligned | T1.98.1–T1.99.8 | Close: Adopted EKS global_paths as universal canonical path pattern; created common/library/paths/resolver.py. 252/252 tests pass. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-10 |
153: | I090 | 2026-07-10 | Phase 1 | 🟢 Low | EKS lacks workflow_files/tool_files/folder_creation from DCC | DCC validates workflow_files, tool_files, folder_creation. EKS has none. | 📐 Aligned | T1.98.6–T1.99.7 | Close: Added workflow_file_entry_def/tool_file_entry_def to base schema; workflow_files/tool_files to setup+config. 252/252 pass. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-10 |
154: | I091 | 2026-07-11 | Phase 1 | 🟡 Medium | system_parameters not defined as universal feature | config/ subpackage not listed as architecture-aligned, not imported, not documented. | 📐 Aligned | T1.97.10–T1.99.14 | Close: Registered config/ as architecture-aligned subpackage; added L15 to inventory; updated architecture doc. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-11 |
155: | I092 | 2026-07-11 | Phase 1 / Phases 2–5 | 🟡 Medium | EKS pipeline entry points do not converge on shared run_pipeline(context) | Only HTTP backend phase1_server._run works. No non-HTTP UI entry, no shared bootstrap/context helper. | 📐 Aligned | T1.99.1–7 | Close: Shared bootstrap_pipeline()/run_pipeline(context) added; unified eks-pipeline CLI; orphan engine_endpoints.py archived; canonical serve.py added. 257/257 green. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-11 |
156: | I093 | 2026-07-13 | Phase 1 | 🟡 Medium | CLI entry points for discovery and health-scorer engines are non-functional stubs | discovery_cli.py and health_cli.py returned placeholder EngineOutput(status="SUCCESS") only. | 📐 Aligned | T1.56.1–T1.56.5 | Updates: U146 — Close: Both CLIs now invoke real engines; tests added closing coverage gap. 264/264 green. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-13 |
157: | I094 | 2026-07-13 | Phase 1 | 🟢 Low | Pipeline architecture diagram (§9 Mermaid) incorrectly shows initialize_context inside Phase A | Mermaid diagram placed step 9 inside Phase A subgraph instead of standalone context setup. | 📐 Aligned | — | Close: Moved initialize_context() out of Phase A into standalone "Phase 1 Context Setup" subgraph. v3.56. — Workplan: phase_1_foundation_workplan.md v3.56 — Approved: 2026-07-13 |
158: | I095 | 2026-07-13 | Master | 🟢 Low | Master workplan high-level pipeline diagram (§10.1) omits bootstrap & entry-point convergence | Mermaid diagram started at raw file → SchemaToDDL, skipping bootstrap layer. | 📐 Aligned | — | Close: Added ENTRY subgraph (CLI/Web/HTTP converging on run_pipeline), BOOT subgraph, expanded PH3. v1.11. — Workplan: eks_system_workplan.md v1.11 — Approved: 2026-07-13 |
159: | I096 | 2026-07-14 | Phase 1 | 🟡 Medium | Main pipeline CLI entry misnamed/located; per-phase separability unsupported | eks/engine/parsers/cli.py name/location contradicts DCC convention. Cannot run single phases separately. | 📐 Aligned | — | Close: Created eks/engine/eks_engine_pipeline.py as single main entry; deleted parsers/cli.py; archived pipeline_runner.py. 264/264 green. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-14 |
160: | I097 | 2026-07-14 | Phase 1 | 🟡 Medium | EKS pipeline path resolution is brittle — hardcoded parent.parent.parent | No anchor-folder fallback, no schema-driven defaults, --data-dir required with no default. | 📐 Aligned | — | Updates: U149 — Close: Added resolve_pipeline_base_path() with engine/ anchor + CWD fallback; changed --data-dir to optional with schema-driven default. 271/271 green. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-14 |
161: | I098 | 2026-07-15 | Phase 1 / Master | 🟠 High | pipeline_dir anchor-folder discovery design not formalized | EKS anchor=engine forces hardcoded parent.parent.parent and per-path re-prefixing. | 📐 Aligned | — | Updates: U150–U156 — Close: Aligned with universal pattern; renamed to default_base_path("eks"); wired all sub-paths via resolve_paths(). — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-15 |
162: | I099 | 2026-07-15 | Phase 1 / Master | 🟡 Medium | EKS and DCC CLI arg parsers are not universal and not schema-driven | EKS build_parser() hardcoded + project-local; neither derives defaults from resolved schema. | 📐 Aligned | — | Close: Created common/library/cli/schema_cli.py with build_parser_from_schema() and parse_cli_args(). 15 new tests. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-15 |
163: | I100 | 2026-07-15 | Phase 1 | 🟡 Medium | EKS suite config drift — 15 pre-existing test failures | All fail inside ProjectSetupValidator.validate_all and ConfigRegistry. | 📐 Aligned | — | Updates: U160 — Close: _schema_config_candidates probes eks/config/schemas/; ConfigRegistry singleton promoted only after successful load_all(). 277/277 green. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-15 |
164: | I101 | 2026-07-15 | Phase 1 / Master | 🟡 Medium | DCC not yet wired to the universal L18 CLI parser (SSOT gap remains) | DCC still uses project-local parsers, duplicating parser logic across projects. | ⛔ Won't Implement | T1.99.30 | Close: Per user directive: DCC-related issues within the EKS pipeline are not to be implemented. |
165: | I102 | 2026-07-15 | Phase 1 / Master | 🟡 Medium | DEFAULT_PIPELINE_DIR = "engine" is hardcoded in common.library | EKS-specific value baked into universal shared library. | 📐 Aligned | — | Updates: U157 — Close: Removed from common.library; each pipeline entry defines its own pipeline_dir constant. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-15 |
166: | I103 | 2026-07-15 | Phase 1 / Master | 🟡 Medium | EKS main() delegates to a separate run() instead of containing pipeline steps | EKS main() = sys.exit(run()). DCC main() contains every step inline. | 📐 Aligned | T1.99.33 | Updates: U158 — Close: Merged run() into main(); deleted separate run(); if __name__ guard. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-15 |
167: | I104 | 2026-07-15 | Phase 1 / Master | 🟡 Medium | EKS main() does not declare anchor/pipeline_dir locally | EKS relied on module-level constants instead of local literals like DCC. | 📐 Aligned | T1.99.34 | Updates: U161 — Close: Declared anchor and pipeline_dir as local literals at top of main(); removed module-level constants. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-15 |
168: | I105 | 2026-07-16 | Phase 1 | 🟠 High | EKS pipeline messaging is duplicated and uses wrong catalog file | Two message-manager implementations. Entry-point uses default catalog "message_config.json" not "eks_message_config.json". | 📐 Aligned | T1.99.35–39 | Updates: U162 — Close: EKS MessageManager rewritten as thin subclass with correct catalog; fixed wrong-catalog bug; added icon support. 272/277 green. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-16 |
169: | I106 | 2026-07-16 | Phase 1 | 🟡 Medium | EKS pipeline context not threaded through main() | EKS main() never constructs or threads EKSPipelineContext. It lives only inside PipelineOrchestrator. | 📐 Aligned | T1.99.40–44 | Updates: U163 — Close: EKSPipelineContext extends BasePipelineContext; initialize_context() accepts bootstrap data; run_pipeline() accepts context param; main() builds context. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-16 |
170: | I107 | 2026-07-16 | Phase 1 | 🟡 Medium | EKS bootstrap incomplete vs DCC — init functions still outside bootstrap_pipeline() | OS detection, log-level precedence, path resolution split across main() and bootstrap. Split path-resolution source — cli.resolved_paths vs boot["resolved_paths"] can diverge. | 📐 Aligned | T1.99.45–48 | Updates: U165 — Close: bootstrap_pipeline() handles all init; main() delegates fully; single resolve_paths(); single MessageManager. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-16 |
171: | I108 | 2026-07-17 | Master | 🟠 High | Create universal BootstrapManager in common/library/bootstrap/ as L19 | common/library has individual building blocks but no shared bootstrap orchestrator. Every project must build its own. | 📐 Aligned | T1.99.50–55 | Updates: U167 — Close: Created common/library/bootstrap/ with 8-phase orchestrator, BootstrapError, phase registry, 37 tests. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-17 |
172: | I109 | 2026-07-17 | Phase 1 | 🟡 Medium | Refactor EKS bootstrap_pipeline() to delegate to universal BootstrapManager | Stateless function returning dict with ~13 keys. No phase tracking, no trace, no structured errors. | 📐 Aligned | T1.99.58/T1.99.59 | Updates: U167 — Close: Created EKSBootstrapManager; bootstrap_pipeline() refactored as thin wrapper; main() uses chain; backward-compat to_dict(). — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-17 |
173: | I110 | 2026-07-17 | Phase 1 | 🟡 Medium | Simplify EKS main() — delegate context construction to BootstrapManager | 30+ lines of manual context assembly that to_pipeline_context() handles in one call. | 📐 Aligned | T1.99.60/T1.99.61 | Updates: U167 — Close: Collapsed manual assembly into single ctx = mgr.to_pipeline_context(); EngineInput derived from ctx.paths. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-17 |
174: | I111 | 2026-07-17 | Phase 1 | 🟠 High | Structured BootstrapError + P1-BOOT-* error codes via shared error system | EKS bootstrap_pipeline() raises bare RuntimeError on readiness failure — no structured code, no phase attribution. | 📐 Aligned | T1.99.54/T1.99.62/T1.99.63 | Updates: U168 — Close: Created universal BootstrapError; registered 5 P1-BOOT-* codes; replaced RuntimeError; added 6 error-path tests. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-17 |
175: | I112 | 2026-07-17 | Phase 1 | 🟠 High | Bootstrap error codes misaligned with Appendix D pipeline message/error design | Cross-reference audit of 5 sources found 6 misalignments: P1-BOOT-* format not in Appendix D; S-B-S-06xx category B not documented; 14 universal B-* codes unregistered; no bootstrap messages; missing Appendix D bootstrap section. | 📐 Aligned | T1.99.64–69 | Updates: U181 — Close: Option B selected — keep P1-BOOT-* as documented hybrid format; EKSBootstrapManager overrides phases to use P1-BOOT-* codes; all 21 bootstrap error codes resolve via ErrorManager. Appendix D v0.4 updated. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-17 |
176: | I113 | 2026-07-17 | Phase 1 | 🟠 High | EKS main() creates logger + heartbeat after bootstrap; DCC creates before | DCC calls setup_logger() + set_debug_level() before BootstrapManager. EKS creates after bootstrap returns — phases P1–P8 run with no logger. CLI parsing happens inside bootstrap, so level unknown until completion. | 📐 Aligned | T1.99.70–T1.99.74 | Updates: U169 — Close: Added _parse_early_verbosity(); UniversalLogger created pre-bootstrap; TelemetryHeartbeat moved pre-bootstrap covering all 8 phases. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-17 |
177: | I114 | 2026-07-17 | Phase 1 | 🟠 High | No environment/dependency check in EKS bootstrap; top-level imports bypass any env check | DCC P6 calls test_environment() verifying all schema-driven dependencies. EKS _bootstrap_env() only does OS detection. Top-level module imports run before test_environment(). | 📐 Aligned | T1.99.75–80 | Updates: U173 — Close: Created universal test_environment(); wired EKSBootstrapManager; registered P1-BOOT-ENV; lazy-import refactor in main(). No bare ModuleNotFoundError. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-17 |
178: | I115 | 2026-07-17 | Phase 1 / Master | 🟡 Medium | universal_pipeline_architecture_design.md v1.9 gap-closure audit not tracked in issue log | Comprehensive gap-closure audit performed comparing architecture doc against common/library/. 5 major gaps resolved. Documentation update never logged as issue. | 📐 Aligned | — | Close: Retroactively logged as I115. 14 edits in doc revision history v1.9. Documentation-only. — Workplan: universal_pipeline_architecture_design.md v1.9 — Approved: 2026-07-17 |
179: | I116 | 2026-07-17 | Phase 1 / Master | 🟢 Low | universal_pipeline_architecture_design.md Document Index has incorrect § numbering sequence | §3.17–§3.22 listed as §17–§22. §3.1–§3.16 entirely missing from index. | ✅ Resolved | — | Close: Renumbered §17–§22 → §3.17–§3.22; added missing §3.1–§3.16 entries with correct anchor links. Index-only fix. — Approved: 2026-07-17 |
180: | I117 | 2026-07-17 | Phase 1 | 🟠 High | Pre-bootstrap common.library imports in main() are not error-guarded | main() imports common.library modules before bootstrap. If common.library not importable, bare ImportError hits user before any error infrastructure. | 📐 Aligned | T1.99.81 | Updates: U175 — Close: Created _preload_infrastructure() — pure-stdlib function guarding each import individually. Universal preload pattern §3.23. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-17 |
181: | I118 | 2026-07-17 | Phase 1 | 🟠 High | _preload_infrastructure() v1 had two critical defects | (a) Errors not printed to stderr at failure point — NameError crash possible. (b) Logger/heartbeat instantiated inside preload defeating pure-stdlib guarantee. | 📐 Aligned | T1.99.84 | Updates: U176 — Close: Every error prints immediately to stderr; all variables pre-bound; returns classes not instances. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-17 |
182: | I119 | 2026-07-17 | Phase 1 | 🟠 High | Runtime entry-point: stdlib sys.path not set for direct execution | Running python eks_engine_pipeline.py from eks/engine/ failed — sys.path lacked repo root. | 📐 Aligned | — | Updates: U177 — Close: Added _stdlib_find_repo_root() — walks up from __file__ to locate repo root, inserts into sys.path[0]. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-17 |
183: | I120 | 2026-07-17 | Phase 1 | 🟠 High | Runtime entry-point: absolute imports failed from subdirectory | Direct exec from eks/engine/ caused "from eks.engine.core import ..." to fail — eks resolved relative to CWD. | 📐 Aligned | — | Updates: U177 — Close: Converted entry-point to absolute imports gated on sys.path fix from I119. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-17 |
184: | I121 | 2026-07-17 | Phase 1 | 🟡 Medium | Runtime entry-point: EKSBootstrapManager import not guarded | Module-level import crashed with bare ImportError if eks.engine.core.bootstrap was unavailable. | 📐 Aligned | — | Updates: U177 — Close: Moved import inside try/except guard; returns structured error dict on failure. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-17 |
185: | I122 | 2026-07-17 | Phase 1 | 🟠 High | Stale eks/eks/ ghost directory causes B-REG-001 path-doubling bug | Bootstrap P3: B-REG-001 — root cause was empty eks/eks/ directory causing discover_project_root() to resolve one level too deep. | 📐 Aligned | — | Updates: U178 — Close: Archived stale eks/eks/ directory; root discovery now verifies anchor folder. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-17 |
186: | I123 | 2026-07-17 | Phase 1 | 🟠 High | P6 env check: pip distribution names != Python import names | test_environment() passed pip names (python-docx, rdflib) directly to importlib.import_module(). python-docx import must be docx; rdflib not installed. | ✅ Resolved | — | Updates: U179 — Close: Added pip→import name mapping dict; installed rdflib; added rdflib to eks.yml. — Approved: 2026-07-17 |
187: | I124 | 2026-07-17 | Phase 1 | 🟡 Medium | eks/output/ accumulates unbounded per-job JSON files | Each run wrote up to 10 JSON files. All write-only; data already in memory. | 🔷 Deferred for further study | T1.99.84–86 | Updates: U180 — Close: Collapsed into single overwrite pipeline_output.json (server only); CLI path never addressed. Deferred to I234 — CLI path needs pipeline_output.json + debug_log. |
188: | I125 | 2026-07-18 | Phase 1 | 🟢 Low | Phase 1 pipeline review: workplan documentation gaps | Workplan §9 Mermaid BOOT subgraph outdated, §8 task status not updated, §30 success criteria unchecked. | 📐 Aligned | — | Close: Fixed all 6 doc gaps; workplan v3.91. Documentation-only. — Workplan: phase_1_foundation_workplan.md v3.91 — Approved: 2026-07-18 |
189: | I126 | 2026-07-18 | Phase 1 | 🟠 High | No CSV/Excel export capability — pipeline results trapped in DB | Pipeline results only accessible via SQL queries on eks_registry.db. | 🔷 Deferred for further study | T1.99.87–94 | Updates: U183 — Close: Created common/library/export/ (L22) with DataExporter; --export CLI (opt-in, no default). Deferred to I234 — CLI exports should be default-on. |
190: | I127 | 2026-07-18 | Phase 1 | 🟠 High | Preload import gate audit: 6 bare imports in main() call chain not preload-guarded | EngineInput/EngineOutput, parse_cli_args, PipelineOrchestrator, DocumentRegistry, DataExporter imported bare. | 📐 Aligned | T1.99.95–100 | Updates: U185 — Close: All 6 added to _preload_infrastructure(); bare imports replaced with infra[key] references. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-18 |
191: | I128 | 2026-07-18 | Phase 1 | 🔴 Critical | Bootstrap P3: bootstrap_universal not in system_error_ranges schema | eks_error_setup_schema.json missing bootstrap_universal → P1-BOOT-CONFIG blocked every run. | 📐 Aligned | — | Updates: U186 — Close: Added bootstrap_universal to setup schema; added expanded format to base schema enum. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-18 |
192: | I129 | 2026-07-18 | Phase 1 | 🔴 Critical | FileScanner discovers 0 files — doc_config not loaded at bootstrap P3 | _bootstrap_registry() only loaded main config; doc_config stayed {} → file_type_registry empty → 0 files. | ✅ Resolved | — | Updates: U186 — Close: Modified EKSBootstrapManager to separately load doc_config from SchemaLoader. — Approved: 2026-07-18 |
193: | I130 | 2026-07-18 | Phase 1 | 🟠 High | Bootstrap path-resolution rooting defect — P2_paths calls resolve_paths() with empty config | 5-step defect chain: P2 runs before P3 → config={} → resolve_paths() falls to DCC branch→all paths anchor at repo root. | 📐 Aligned | T1.99.101–103 | Updates: U181 — Close: Added guard to skip resolver when config empty; cleaned stale root-level dirs. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-18 |
194: | I131 | 2026-07-18 | Phase 1 | 🟠 High | KeyError: 'revision' in register_placeholders | _parse_filename() fallback returns dict without revision key → register_document() direct access metadata["revision"] → KeyError. | ✅ Resolved | T1.99.104–107 | Updates: U181 — Close: 3-Level Layered Defense: L1 fallback returns revision="00"; L2 setdefault; L3 .get("revision", "00"). — Approved: 2026-07-18 |
195: | I132 | 2026-07-18 | Phase 1 | 🟡 Medium | .dwg file type orphan — registered in file_type_registry but no document type expected it | No document type listed .dwg in expected_file_types → files discovered as unknown and never registered. | 📐 Aligned | T1.99.108 | Updates: U181 — Close: Added "CAD" document type to enum, setup schema, and config entries. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-18 |
196: | I133 | 2026-07-18 | Phase 1 | 🟡 Medium | Option A2: Rename all 12 D5-prefix error codes to standard P-prefix format | D5-PARSE-001..007 and D5-PROP-001..005 were only non-conforming format. | 📐 Aligned | — | Updates: U189 — Close: All 12 codes renamed to P-prefix; call sites + tests updated. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-18 |
197: | I134 | 2026-07-18 | Phase 1 | 🟠 High | Null-tolerant registration — files with unparseable filenames silently dropped | Three pipeline layers rejected files that couldn't yield a document_number. | ✅ Resolved | T1.99.118–120 | Updates: U189 — Close: 3-layer relaxation: L1 allows None; L2 generates synthetic UNRESOLVED-{md5[:8]} key; L3 generates synthetic key. — Approved: 2026-07-18 |
198: | I135 | 2026-07-18 | Phase 1 | 🟡 Medium | No shared filename parser module — 4 call sites use brittle ad-hoc split() logic | PipelineOrchestrator, health_scorer.py, FileScanner, phase1_server.py each had independent filename parsing. | ✅ Resolved | T1.99.113–117 | Updates: U189 — Close: Created FilenameParser class; migrated all 4 call sites; deleted old ad-hoc code. — Approved: 2026-07-18 |

(Output capped at 50 KB. Showing lines 1-198. Use offset=199 to continue.)
</content>
```

**Tool: read**

**Input:**
```json
{
  "filePath": "C:\\Users\\franklin.song\\Desktop\\DSAI\\Engineering-and-Design\\eks\\log\\phase1\\p1_task_log.md",
  "limit": 200
}
```

**Output:**
```
<path>C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\log\phase1\p1_task_log.md</path>
<type>file</type>
<content>
1: # Phase 1 Task Log
2: 
3: **Project**: Engineering Knowledge System (EKS)  
4: **Location**: `eks/log/phase1/p1_task_log.md`  
5: **Last Updated**: 2026-07-29 (T1.188 ✅ COMPLETE — ColumnProcessor regression tests; §75: 295 complete, 34 planned)
6: 
7: ## Legend
8: 
9: ### Task Status
10: 
11: | Marker | Status | Meaning |
12: |:------:|:-------|:--------|
13: | ✅ | Complete | Task fully implemented and verified |
14: | ⏳ | In Progress | Task currently being implemented |
15: | 🔷 | Planned | Task defined but not yet implemented |
16: | ⛔ | Won't Implement | Explicitly rejected or out of scope |
17: 
18: ### Column Format
19: 
20: All tables use the standard 12-column enriched format:
21: 
22: `ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section`
23: 
24: ---
25: 
26: ## Status Summary
27: 
28: | Status | Marker | Count |
29: | :----- | :----: | ----: |
30: | Complete | ✅ | 295 |
31: | In Progress | ⏳ | 0 |
32: | Planned | 🔷 | 34 |
33: | Won't Implement | ⛔ | 0 |
34: | **Total** | | **329** |
35: 
36: ---
37: 
38: ## 2. Foundation, Environment & Compliance (R99) Tasks
39: 
40: > Source: [§14](phase_1_foundation_workplan.md#14)
41: 
42: ### Task Breakdown
43: 
44: | ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
45: | :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
46: | T1.1 | [Init] Create EKS folder structure | archive, config, data, output, engine, log, docs, workplan, test, ui | R99 | ✅ COMPLETE | — | — | folders | — | — | — | §14 |
47: | T1.2 | [Init] Create environment file `eks.yml` | Conda environment with all Phase 1–5 dependencies | R99 | ✅ COMPLETE | — | — | `eks/eks.yml` | — | — | — | §14 |
48: | T1.14 | [Code] Implement SSOT config registry | Global parameter access via schema-driven config; no hardcoding | R06, R35 | ✅ COMPLETE | — | — | `config_registry.py` | — | — | — | §14 |
49: | T1.15 | [Testing] Write unit tests | Schema loader, document registry, revision management, parsers, logger | R99 | ✅ COMPLETE | — | — | `test/` | — | — | — | §14 |
50: | T1.16 | [Docs] Create log files | `update_log.md`, `issue_log.md` under `eks/log/` | R99 | ✅ COMPLETE | — | — | `log/update_log.md`, `log/issue_log.md` | — | — | — | §14 |
51: | T1.33 | [Schema] Migrate EKS schemas to config/schemas/ | Move core/asset/ontology config & schema files to `eks/config/schemas/`; update SchemaLoader, ErrorManager, MessageManager, tests, and documentation | R06, R99 | ✅ COMPLETE | — | — | `config/schemas/`, `schema_loader.py` | — | — | — | §14 |
52: | T1.48 | [Schema] Schema audit — duplicates, inconsistencies, missing validations | Remove duplicate `revision_id` and `discipline_code`; Align parser import paths; Add dgn/dwg stub parsers; Log all issues (I022–I028). All 114 tests pass. | R06, R99 | ✅ COMPLETE | I022, I023, I024, I025, I026, I027, I028 | — | `eks_doc_base_schema.json`, `eks_config.json` | — | — | — | §14 |
53: | T1.49 | [Docs] Cross-cutting workplan remediation | Fix `agent_rule.md` references → `AGENTS.md`; convert Linux absolute paths to relative; update stale statuses; reorder §10/§25; fill Phase 3 placeholders; add reranker criteria. | R99 | ✅ COMPLETE | — | — | `phase_1_foundation_workplan.md` | — | — | — | §14 |
54: | T1.52 | [Code] Implement EKSPipelineContext | Create `eks/engine/core/context.py` with nested dataclasses for centralized state management per Appendix F | R57 | ✅ COMPLETE | — | — | `engine/core/context.py` | — | — | — | §14 |
55: | T1.53 | [Code] Implement BaseEngine abstract class | Create `eks/engine/core/base.py` with standard execution flow (validate → execute → validate) per Appendix F | R99 | ✅ COMPLETE | — | — | `engine/core/base.py` | — | — | — | §14 |
56: | T1.55 | [Code] Implement Multi-Stage Validation | Create `eks/engine/core/validator.py` with setup, schema, data, parser validation stages per Appendix F | R99 | ✅ COMPLETE | — | — | `engine/core/validator.py` | — | — | — | §14 |
57: | T1.56 | [Code] Implement CLI Entry Points | Discovery CLI and Health CLI both call real engines via `bootstrap_pipeline()` funnel. I093 resolved. | R99 | ✅ COMPLETE | I093 | — | `engine/core/discovery_cli.py`, `engine/core/health_cli.py` | — | — | — | §14 |
58: | T1.56.1 | [Code] Wire Discovery CLI to real engine (I093) | `discovery_cli.py` → `PipelineOrchestrator.run_phase_a()`; real `EngineOutput`. | R99 | ✅ COMPLETE | I093 | — | `engine/core/discovery_cli.py` | ← T1.56 | — | — | §14 |
59: | T1.56.2 | [Code] Wire Health Scorer CLI to real engine (I093) | `health_cli.py` → `HealthScorer.score()`/`score_batch()`; real scores/status. | R99 | ✅ COMPLETE | I093 | — | `engine/core/health_cli.py` | ← T1.56 | — | — | §14 |
60: | T1.56.3 | [Testing] Add pytest for discovery_cli (I093) | Happy path + failure/edge case; assert real `EngineOutput`. | R99 | ✅ COMPLETE | I093 | — | `test/` | ← T1.56.1 | — | — | §14 |
61: | T1.56.4 | [Testing] Add pytest for health_cli (I093) | Single + batch scoring + threshold boundary. | R99 | ✅ COMPLETE | I093 | — | `test/` | ← T1.56.2 | — | — | §14 |
62: | T1.56.5 | [Docs] Close I093 records & reclassify T1.56 | Mark I093 resolved; flip T1.56 status. | R99 | ✅ COMPLETE | I093 | — | `update_log.md`, `issue_log.md` | ← T1.56.3–4 | — | — | §14 |
63: | T1.57 | [Code] Implement HTTP API Endpoints | Delivered as `eks/ui/backend/phase1_server.py` (standalone `--port 5001`). | R99 | ✅ COMPLETE | — | — | `ui/backend/phase1_server.py` | — | — | — | §14 |
64: | T1.65 | [Code] Implement Project Setup Validator | Create `eks/engine/core/setup_validator.py` with auto-creation of missing folders per Appendix F | R99 | ✅ COMPLETE | — | — | `engine/core/setup_validator.py` | ← T1.66 | — | — | §14 |
65: | T1.66 | [Schema] Create Project Setup Schema | Create `eks/config/schemas/project_setup.json` for setup validation per Appendix F | R99 | ✅ COMPLETE | — | — | `config/schemas/project_setup.json` | — | — | — | §14 |
66: | T1.67 | [Schema] Integrate project_setup into core 3-layer schemas (I046) | Refactor content into `eks_base_schema.json`, `eks_setup_schema.json`, `eks_config.json`. Delete orphan `project_setup.json`. Resolves I046. | R99 | ✅ COMPLETE | I046 | — | `eks_base_schema.json`, `eks_setup_schema.json`, `eks_config.json`, `setup_validator.py` | ← T1.66 | — | — | §14 |
67: | T1.70 | [Code] Add data_dir traversal guard to phase1_server.py | Resolve `data_dir` against `PRJ_DIR`, check `is_relative_to(PRJ_DIR)` — return HTTP 403 if outside project root. | R99 | ✅ COMPLETE | — | — | `ui/backend/phase1_server.py` | — | — | — | §14 |
68: | T1.74 | [Code] Cross-platform path compatibility | Fix 4 cross-platform gaps in `phase1_server.py`, `context.py`. Resolves I078–I081. | R99 | ✅ COMPLETE | I078, I079, I080, I081 | — | `phase1_server.py`, `engine/core/context.py` | ← T1.69, T1.70 | — | — | §14 |
69: 
70: ---
71: 
72: ## 3. Architectural Patterns — Context, Factories & Orchestration Hardening (Appendix F) Tasks
73: 
74: > Source: [§15](phase_1_foundation_workplan.md#15)
75: 
76: ### Task Breakdown
77: 
78: | ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
79: | :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
80: | T1.54 | [Code] Implement TelemetryHeartbeat | Create `eks/engine/core/telemetry.py` for document processing checkpoints per Appendix F | R57 | ✅ COMPLETE | — | — | `engine/core/telemetry.py` | — | — | — | §15 |
81: | T1.58 | [Code] Implement Checkpoint State Serialization | Add checkpoint state serialization/deserialization for resume capability per Appendix F | R57 | ✅ COMPLETE | — | — | `engine/core/context.py` | — | — | — | §15 |
82: | T1.59 | [Code] Implement ParserFactory | Create `eks/engine/core/factories.py` with file type routing per Appendix F | R26 | ✅ COMPLETE | — | — | `engine/core/factories.py` | — | — | — | §15 |
83: | T1.60 | [Code] Implement HealthScorerFactory | Factory with config-driven dimensions per Appendix F | R51 | ✅ COMPLETE | — | — | `engine/core/factories.py` | — | — | — | §15 |
84: | T1.61 | [Code] Implement StructureDetectorFactory | Factory for structure detector instantiation per Appendix F | R99 | ✅ COMPLETE | — | — | `engine/core/factories.py` | — | — | — | §15 |
85: | T1.62 | [Code] Update Engines to Use Factories | Refactor existing engines to use factories instead of direct instantiation per Appendix F | R26 | ✅ COMPLETE | — | — | `engine/` | ← T1.59–61 | — | — | §15 |
86: | T1.63 | [Code] Enhance PipelineOrchestrator with Checkpoints | Add 5 clear phases (A-E) with telemetry heartbeat integration per Appendix F | R57 | ✅ COMPLETE | — | — | `pipeline_orchestrator.py` | — | — | — | §15 |
87: | T1.64 | [Code] Implement Phase Rollback Capability | Add checkpoint restoration mechanism for failed phases per Appendix F | R57 | ✅ COMPLETE | — | — | `pipeline_orchestrator.py` | ← T1.63 | — | — | §15 |
88: | T1.182.1 | [Code] Remove duplicate Factory base class from EKS factories.py | Remove lines 22-41 (duplicate Factory class); add import from common.library.utility.factories.base_factory | R99 | ✅ COMPLETE | I211 | TL010 | `engine/core/factories.py` | — | TL010 | U203 | §15 |
89: | T1.182.2 | [Code] Refactor ParserFactory to inherit from common.Factory | Ensure ParserFactory inherits from common.Factory; replace manual _load_class() with self._load_class(); verify _get_config() uses common version | R99 | ✅ COMPLETE | I211 | TL010 | `engine/core/factories.py` | ← T1.182.1 | TL010 | U203 | §15 |
90: | T1.182.3 | [Code] Refactor HealthScorerFactory to inherit from common.Factory | Ensure HealthScorerFactory inherits from common.Factory; replace manual import with self._load_class() if applicable; verify config access uses common._get_config() | R99 | ✅ COMPLETE | I211 | TL010 | `engine/core/factories.py` | ← T1.182.1 | TL010 | U203 | §15 |
91: | T1.182.4 | [Code] Refactor StructureDetectorFactory to inherit from common.Factory | Ensure StructureDetectorFactory inherits from common.Factory; replace manual _load_class() logic (lines 205-208) with self._load_class(); verify config access uses common._get_config() | R99 | ✅ COMPLETE | I211 | TL010 | `engine/core/factories.py` | ← T1.182.1 | TL010 | U203 | §15 |
92: | T1.182.5 | [Code] Refactor EngineFactory to inherit from common.Factory | Ensure EngineFactory inherits from common.Factory; replace manual _load_class() logic (lines 272-275) with self._load_class(); verify config access uses common._get_config() | R99 | ✅ COMPLETE | I211 | TL010 | `engine/core/factories.py` | ← T1.182.1 | TL010 | U203 | §15 |
93: | T1.182.6 | [Docs] Update factories.py revision metadata | Update revision header in factories.py to document SSOT compliance fix; reference I211 and T1.99.182 | R99 | ✅ COMPLETE | I211 | TL010 | `engine/core/factories.py` | ← T1.182.1–5 | TL010 | U203 | §15 |
94: | T1.182.7 | [Testing] Run EKS test suite for factory SSOT compliance | Run EKS test suite to verify no breaking changes; focus on tests that use factories; verify dynamic class loading still works | R99 | ✅ COMPLETE | I211 | TL010 | `test/` | ← T1.182.1–5 | TL010 | U203 | §15 |
95: | T1.182.8 | [Docs] Update I211 status in p1_issue_log.md | Update I211 resolution note to reflect completion; change status from "Deferred for further study" to "Resolved"; update last updated version | R99 | ✅ COMPLETE | I211 | TL010 | `log/phase1/p1_issue_log.md` | ← T1.182.1–7 | TL010 | U203 | §15 |
96: 
97: ---
98: 
99: ## 4. Core Schema Suite (base/setup/config + fragment schemas) Tasks
100: 
101: > Source: [§16](phase_1_foundation_workplan.md#16)
102: 
103: ### Task Breakdown
104: 
105: | ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
106: | :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
107: | T1.3 | [Schema] Design canonical schema — base | File: `eks_base_schema.json`. Layer: Definitions ($defs). 13 asset schema fragments + conditional_fragments for zero-code extensibility. | R06, R07, R08, R09 | ✅ COMPLETE | — | U006 | `eks_base_schema.json` | — | — | — | §16 |
108: | T1.4 | [Schema] Design canonical schema — setup | File: `eks_setup_schema.json`. Layer: Declarations (properties). One-to-one match with base via $ref. | R06, R07, R08, R09 | ✅ COMPLETE | — | U006 | `eks_setup_schema.json` | ← T1.3 | — | — | §16 |
109: | T1.5 | [Schema] Design canonical schema — config | File: `eks_config.json`. Layer: Config values. Validates strictly against setup schema. | R06, R07, R08, R09 | ✅ COMPLETE | — | U006 | `eks_config.json` | ← T1.4 | — | — | §16 |
110: | T1.6 | [Code] Implement schema loader | Load and resolve base/setup/config with $ref support (reuse DCC pattern) | R06 | ✅ COMPLETE | — | U008 | `schema_loader.py` | ← T1.5 | — | — | §16 |
111: | T1.42 | [Schema] Project code fragment schema | Create `eks_project_code_schema.json` with valid codes (131101, 131242, 999999). DCC fragment pattern. | R06 | ✅ COMPLETE | — | — | `eks_project_code_schema.json` | — | — | — | §16 |
112: | T1.43 | [Schema] Discipline fragment schema | Create `eks_discipline_schema.json` with 21 discipline codes (PI, EL, IN, ...). DCC fragment pattern. | R06 | ✅ COMPLETE | — | — | `eks_discipline_schema.json` | — | — | — | §16 |
113: | T1.44 | [Schema] Department fragment schema | Create `eks_department_schema.json` with 11 department codes (PRJ, QAQC, CNT, ...). DCC fragment pattern. | R06 | ✅ COMPLETE | — | — | `eks_department_schema.json` | — | — | — | §16 |
114: | T1.45 | [Schema] Facility fragment schema | Create `eks_facility_schema.json` with 12 facility prefixes (WSD11, WSW41, ...). DCC fragment pattern. | R06 | ✅ COMPLETE | — | — | `eks_facility_schema.json` | — | — | — | §16 |
115: | T1.46 | [Schema] Update base/config/setup for fragment integration | Add defs to base; replace P123/P456 with real WSD11 codes in config; add $ref to fragments. Resolve I005. | R06 | ✅ COMPLETE | I005 | — | `eks_base_schema.json`, `eks_config.json`, `eks_setup_schema.json` | ← T1.42–45 | — | — | §16 |
116: | T1.47 | [Testing] Add fragment schema validation tests | 6 new tests: fragment existence, base defs, required fields, no placeholders, config $ref, setup properties. | R06 | ✅ COMPLETE | — | — | `test/` | ← T1.46 | — | — | §16 |
117: | T1.50 | [Schema] Base schema SSOT enforcement | Strip trigger map to shape-only (I031); move revision_id to doc base (I032); update ConfigRegistry; update schema_inheritance_chain.md. 114/114 tests pass. | R06, R35 | ✅ COMPLETE | I031, I032 | — | `eks_base_schema.json`, `eks_doc_base_schema.json`, `ConfigRegistry` | — | — | — | §16 |
118: | T1.51 | [Schema] Asset Context Fragment — hierarchy + relationships | Extensible location/system hierarchy + asset/document relationships + lifecycle context for all 14 AT_ types. Version bumps: base 1.3.0, setup 1.3.0, config 1.4.0. | R36 | ✅ COMPLETE | — | — | `eks_asset_base_schema.json`, `eks_asset_setup_schema.json`, `eks_asset_config.json` | — | — | — | §16 |
119: 
120: ---
121: 
122: ## 5. Asset Schema — Universal Plant Item (R36/R39) Tasks
123: 
124: > Source: [§17](phase_1_foundation_workplan.md#17)
125: 
126: ### Task Breakdown
127: 
128: | ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
129: | :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
130: | T1.17 | [Schema] Design asset schema — fragment definitions | Add 13 reusable asset fragments to `eks_asset_base_schema.json` (item_core, process_conditions, manufacturer, ...) | R36 | ✅ COMPLETE | — | — | `eks_asset_base_schema.json` | — | — | — | §17 |
131: | T1.18 | [Schema] Design asset schema — type registry | Add `asset_type_registry` to setup schema; map all 14 AT_ categories to fragment compositions in config | R36 | ✅ COMPLETE | — | — | `eks_setup_schema.json`, `eks_config.json` | — | — | — | §17 |
132: | T1.19 | [Config] Update config with asset source | Add project asset datadrop path and per-project config to `eks_config.json` | R36 | ✅ COMPLETE | — | — | `eks_config.json` | — | — | — | §17 |
133: | T1.20 | [Schema] Update asset schema files for R39 + gap analysis | Add specialist_equipment/motor_control fragments; expand actuator/rotating/instrumentation/valve with gap fields; update fragment enum to 13; add conditional_fragments entries | R36, R39 | ✅ COMPLETE | — | — | `eks_asset_base_schema.json`, `eks_asset_setup_schema.json`, `eks_asset_config.json` | — | — | — | §17 |
134: 
135: ---
136: ## 6. Ontology Integration (R44, ISO 15926) Tasks
137: 
138: > Source: [§18](phase_1_foundation_workplan.md#18)
139: 
140: ### Task Breakdown
141: 
142: | ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
143: | :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
144: | T1.23 | [Schema] Design ontology schema | Validate classes, properties, and relationship types; SHACL constraint definitions for data quality rules | R44 | ✅ COMPLETE | — | — | `eks_ontology_schema.json` | — | — | — | §18 |
145: | T1.24 | [Config] Create ontology config | Define classes, inheritance, and relationship properties (ISO 15926 aligned) | R44 | ✅ COMPLETE | — | — | `eks_ontology_config.json` | — | — | — | §18 |
146: | T1.25 | [Code] Extend schema loader | Update `schema_loader.py` to validate and load the ontology registry dynamically at startup | R44 | ✅ COMPLETE | — | — | `schema_loader.py` | — | — | — | §18 |
147: | T1.26 | [Testing] Write ontology unit tests | Test ontology schema validation and loading in `test_phase1.py` | R44 | ✅ COMPLETE | — | — | `test/` | — | — | — | §18 |
148: | T1.27 | [Docs] Plan alias-aware ontology mapping | Define alias support and `ontology_class_map` design; document AT_ code-to-ontology mapping; hold schema/code updates pending approval | R44 | ✅ COMPLETE | — | — | `eks_asset_config.json` | — | — | — | §18 |
149: | T1.28 | [Schema] Embedded Relationship Metadata | Update base schema with relationship-triggering fields; update config with relationship_triggers mapping to graph edges | R44 | ✅ COMPLETE | — | — | `eks_asset_base_schema.json`, `eks_asset_config.json` | — | — | — | §18 |
150: | T1.29 | [Schema] Document Ontology & Mapping Metadata | Update ontology config with Document hierarchy + lifecycle relationships; update asset config with document_triggers | R44 | ✅ COMPLETE | — | — | `eks_ontology_config.json`, `eks_asset_config.json` | — | — | — | §18 |
151: 
152: ---
153: 
154: ## 7. Logging, Errors & Health Scoring (R33/R34/R51) Tasks
155: 
156: > Source: [§19](phase_1_foundation_workplan.md#19)
157: 
158: ### Task Breakdown
159: 
160: | ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
161: | :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
162: | T1.13 | [Code] Implement tiered logger | logger.py: levels 0–3, debug object, trace table, depth counter | R33, R34 | ✅ COMPLETE | — | — | `logger.py` | — | — | — | §19 |
163: | T1.30 | [Schema] Error Code Taxonomy Schema | Create error code base + config schemas with full system/data error catalog. Follow DCC pattern. | R51 | ✅ COMPLETE | — | — | `eks_error_code_base.json`, `eks_error_config.json` | — | — | — | §19 |
164: | T1.31 | [Schema] Pipeline Message Catalog Schema | Create message base + config schemas with milestone/status/progress/warning templates. Follow DCC pattern. | R51 | ✅ COMPLETE | — | — | `eks_message_base.json`, `eks_message_config.json` | — | — | — | §19 |
165: | T1.32 | [Code] Error & Message Manager Modules | Create error_manager.py, message_manager.py, health_scorer.py (6-dimension), structure_detector.py. Add document_elements table. | R51 | ✅ COMPLETE | — | — | `error_manager.py`, `message_manager.py`, `health_scorer.py`, `structure_detector.py` | — | — | — | §19 |
166: | T1.41 | [Schema] Fix error/message schemas 3-layer pattern | Create error/message setup schemas (allOf + $ref); clean config files; update SchemaLoader. Resolve I014. | R51 | ✅ COMPLETE | I014 | — | `eks_error_setup_schema.json`, `eks_message_setup_schema.json` | — | — | — | §19 |
167: | T1.68 | [Code] Wire ErrorManager/MessageManager into pipeline orchestrator | Emit D4/D5 error codes on phase failures; call MessageManager.format() for D6 milestone messages | R51 | ✅ COMPLETE | — | — | `pipeline_orchestrator.py` | ← T1.70, T1.72 | — | — | §19 |
168: | T1.69 | [Code] Add run_id correlation ID to EKSLogger and _LogCapture | Prepend [run_id] to all log entries; pass job_id as run_id from phase1_server | R33, R51 | ✅ COMPLETE | — | — | `logger.py`, `phase1_server.py` | ← T1.76 | — | — | §19 |
169: | T1.71 | [Code] Replace raw duckdb.connect in _update_doc_status | Route through registry.update_document_status() with _with_retry() wrapper | R02 | ✅ COMPLETE | — | — | `pipeline_orchestrator.py` | ← T1.68 | — | — | §19 |
170: | T1.75 | [Code] Activate ErrorManager/MessageManager in phase1_server | Construct and pass managers to PipelineOrchestrator (closes silent T1.68 gap) | R51, R99 | ✅ COMPLETE | — | — | `phase1_server.py` | ← T1.68, T1.76 | — | — | §19 |
171: | T1.76 | [Code] Persist debug/message/status JSON to eks/output | Generate debug_log.json, pipeline_status, pipeline_messages artifacts per AGENTS.md §7/§19 | R51, R99 | ✅ COMPLETE | — | — | `eks/output/` | ← T1.69, T1.75 | — | — | §19 |
172: | T1.99.35 | [Code] Harden universal BaseMessageManager as SSOT (I105) | Add optional icon support, print() fallback, verbosity clamp, _make_default_logger() hook. 10 new common tests pass. | R51, R99 | ✅ COMPLETE | I078, I105 | — | `common/library/core/messages/message_manager.py` | — | — | — | §19 |
173: | T1.99.36 | [Code] Make EKS MessageManager thin subclass (I105) | EKS MessageManager extends BaseMessageManager with _catalog_filename. Remove duplicated logic. All 7 EKS tests green. | R51, R99 | ✅ COMPLETE | I105 | — | `engine/core/message_manager.py` | ← T1.99.35 | — | — | §19 |
174: | T1.99.37 | [Fix] Fix eks_engine_pipeline.py:505 to use EKS subclass (I105) | Change BaseMessageManager → MessageManager. Fixes silent wrong-catalog bug. | R51, R99 | ✅ COMPLETE | I105 | — | `eks_engine_pipeline.py` | ← T1.99.36 | — | — | §19 |
175: | T1.99.38 | [Testing] Tests for universal message + EKS regression (I105) | Common BaseMessageManager subclass test + EKS suite green. 10+7 gap tests; 278/278 green. | R51, R99 | ✅ COMPLETE | — | — | `common/library/core/messages/tests/`, `test/` | ← T1.99.35–36 | — | — | §19 |
176: | T1.99.39 | [Docs] Knowledge base + logs update (I105) | Update knowledge.json, update_log.md (v3.74 recorded) | R51, R99 | ✅ COMPLETE | I105 | — | `knowledge.json`, `update_log.md` | ← T1.99.35–38 | — | — | §19 |
177: | T1.99.40 | [Code] Make EKSPipelineContext extend BasePipelineContext (L06) | Change class to extend common BasePipelineContext; add _from_dict() / _to_dict() | R99 | ✅ COMPLETE | I106 | — | `engine/core/context.py` | — | — | — | §19 |
178: | T1.99.41 | [Code] Populate context fields from EngineInput+bootstrap (I106) | initialize_context() accepts parameters, config_registry, schema_registry, checkpoint_state | R99 | ✅ COMPLETE | I106 | — | `pipeline_orchestrator.py` | ← T1.99.40 | — | — | §19 |
179: | T1.99.42 | [Code] Surface EKSPipelineContext through run_pipeline() (I106) | Accept optional context param; include context in return dict. Backward compat preserved. | R99 | ✅ COMPLETE | I106 | — | `eks_engine_pipeline.py` | ← T1.99.40–41 | — | — | §19 |
180: | T1.99.43 | [Code] main() builds + seeds EKSPipelineContext (I106) | Construct ctx from EngineInput; pass to run_pipeline(); extract EngineOutput from returned context | R99 | ✅ COMPLETE | I106 | — | `eks_engine_pipeline.py` | ← T1.99.42 | — | — | §19 |
181: | T1.99.44 | [Testing] Tests + knowledge base + logs for context threading (I106) | Integration test test_run_pipeline_surfaces_context(); update knowledge.json (U163), issue_log.md | R99 | ✅ COMPLETE | I106 | U163 | `test/`, `knowledge.json`, `update_log.md`, `issue_log.md` | ← T1.99.40–43 | — | — | §19 |
182: | T1.99.45 | [Code] Fold OS detection + params into bootstrap_pipeline() (I107) | Move detect_os(), CLI parse, log-level, eks_root into bootstrap_pipeline() | R99 | ✅ COMPLETE | I107 | — | `eks_engine_pipeline.py` | — | — | — | §19 |
183: | T1.99.46 | [Code] Fold CLI parse + data_dir precedence (I107) | Internal parse_eks_cli(); CLI>Schema>Native data_dir resolution | R99 | ✅ COMPLETE | I107 | — | `eks_engine_pipeline.py` | ← T1.99.45 | — | — | §19 |
184: | T1.99.47 | [Fix] Single path resolution source (I107 Defect A) | One resolved_paths dict; main() + EKSPipelineContext.paths both read from it | R99 | ✅ COMPLETE | I107 | — | `eks_engine_pipeline.py` | ← T1.99.45–46 | — | — | §19 |
185: | T1.99.48 | [Fix] Single MessageManager instance (I107 Defect B) | mm created once in bootstrap; main() reuses boot["mm"] | R99 | ✅ COMPLETE | I107 | — | `eks_engine_pipeline.py` | ← T1.99.47 | — | — | §19 |
186: | T1.99.49 | [Testing] Tests + knowledge base for bootstrap completeness (I107) | 4 integration tests (TestI107BootstrapCompleteness). 23/23 pass. knowledge.json v2.7.0, update_log U165. | R99 | ✅ COMPLETE | I107 | U165 | `test/`, `knowledge.json`, `update_log.md`, `issue_log.md` | ← T1.99.45–48 | — | — | §19 |
187: 
188: ---
189: 
190: ## 8. Document Registry & Revision Management (R02/R21/R22/R29) Tasks
191: 
192: > Source: [§20](phase_1_foundation_workplan.md#20)
193: 
194: ### Task Breakdown
195: 
196: | ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
197: | :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
198: | T1.7 | [Code] Implement document registry | CRUD interface for document metadata backed by DuckDB/PostgreSQL | R02, R29 | ✅ COMPLETE | — | — | `registry.py` | — | — | — | §20 |
199: | T1.8 | [Code] Implement revision management | Preserve all revisions; is_latest flag; revision chain lookup | R21, R22 | ✅ COMPLETE | — | — | `registry.py` | — | — | — | §20 |
200: | T1.21 | [Code] Document Registry Remediation (G1-G3) | Add source_type column; column allowlist for list_documents; SQL ORDER BY for revision history | R02 | ✅ COMPLETE | — | — | `registry.py` | — | — | — | §20 |

(Showing lines 1-200 of 951. Use offset=201 to continue.)
</content>
```

---

## Assistant (Build · DeepSeek V4 Flash Free · 6.7s)

_Thinking:_

I need to find I265 in the issue log. The issue log was cut off at line 198, and I need to continue reading to find I265. Let me also continue reading the task log to find related tasks. Let me search for I265 specifically.





**Tool: grep**

**Input:**
```json
{
  "pattern": "I265",
  "path": "C:\\Users\\franklin.song\\Desktop\\DSAI\\Engineering-and-Design\\eks\\log\\phase1"
}
```

**Output:**
```
No files found
```

**Tool: grep**

**Input:**
```json
{
  "pattern": "I265",
  "path": "C:\\Users\\franklin.song\\Desktop\\DSAI\\Engineering-and-Design\\eks",
  "include": "*.md"
}
```

**Output:**
```
Found 1 matches
C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\appendix_l_project_definition.md:
  Line 11: This workplan is related to issue I265.

```

---

## Assistant (Build · DeepSeek V4 Flash Free · 5.3s)

_Thinking:_

So I265 is referenced in the file `eks/workplan/appendix_l_project_definition.md`. Let me read that file.

**Tool: read**

**Input:**
```json
{
  "filePath": "C:\\Users\\franklin.song\\Desktop\\DSAI\\Engineering-and-Design\\eks\\workplan\\appendix_l_project_definition.md"
}
```

**Output:**
```
<path>C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\workplan\appendix_l_project_definition.md</path>
<type>file</type>
<content>
1: # Workplan – Project Definition Schema Refactoring
2: 
3: ## Objective
4: 
5: Establish **`eks_project_definition_schema.json`** as the **Single Source of Truth (SSOT)** for all project-specific configuration.
6: 
7: The Project Definition shall consolidate all project-specific metadata, engineering settings, document processing rules, asset processing rules, ontology selection, pipeline behavior, retrieval settings, security settings, and integration settings into a single authoritative schema.
8: 
9: A new common EKS pipeline module, **ProjectDefinitionResolver**, shall construct a validated immutable **RuntimeProjectDefinition** object that is consumed by every EKS pipeline component.
10: 
11: This workplan is related to issue I265.
12: 
13: ---
14: 
15: # Background
16: 
17: Project-specific configuration is currently distributed across multiple configuration files.
18: 
19: Examples include:
20: 
21: * project metadata
22: * filename pattern mapping
23: * revision validation
24: * project processing rules
25: 
26: This results in:
27: 
28: * duplicated project identifiers
29: * split configuration ownership
30: * duplicated parser definitions
31: * inconsistent project onboarding
32: * SSOT violations
33: 
34: The original proposal introduced **`eks_project_rules_config.json`**.
35: 
36: Following architectural review, this approach has been superseded.
37: 
38: Project-specific rules belong to the **Project Definition** itself and shall not be maintained in a separate configuration file.
39: 
40: ---
41: 
42: # Existing Architecture
43: 
44: ```text
45: Project Code
46: 
47: ├── eks_project_code_schema.json
48: ├── eks_doc_config.json
49: ├── filename_patterns
50: ├── revision_validation
51: └── runtime modules
52: ```
53: 
54: Project-specific configuration is distributed across multiple schemas.
55: 
56: ---
57: 
58: # Target Architecture
59: 
60: ```text
61:                      Shared Framework
62:                   ┌─────────────────────┐
63:                   │    SchemaLoader     │
64:                   └──────────┬──────────┘
65:                              │
66:                              ▼
67:           eks_project_definition_schema.json
68:                              │
69:                              ▼
70:              ProjectDefinitionResolver
71:                              │
72:                              ▼
73:               RuntimeProjectDefinition
74:                              │
75:       ┌──────────────────────┼──────────────────────┐
76:       ▼                      ▼                      ▼
77:  Document Pipeline      Asset Pipeline      Retrieval Pipeline
78: ```
79: 
80: Every EKS runtime component shall consume **RuntimeProjectDefinition** rather than loading schema files directly.
81: 
82: ---
83: 
84: # Architecture Principles
85: 
86: * Single Source of Truth (SSOT)
87: * Separation of Concerns
88: * Configuration over Code
89: * Reusable Configuration Profiles
90: * Immutable Runtime Configuration
91: * Layered Architecture
92: * Dependency Inversion
93: 
94: ---
95: 
96: # Configuration Ownership
97: 
98: ## Project Definition
99: 
100: **`eks_project_definition_schema.json`**
101: 
102: Owns all project-specific configuration.
103: 
104: Example sections
105: 
106: * project_info
107: * engineering
108: * document_processing
109: * asset_processing
110: * ontology
111: * pipeline
112: * retrieval
113: * security
114: * integration
115: 
116: ---
117: 
118: ## Reusable Configuration Libraries
119: 
120: Own reusable definitions only.
121: 
122: Examples
123: 
124: * filename_patterns
125: * parser_profiles
126: * OCR profiles
127: * document types
128: * ontology profiles
129: * asset profiles
130: * retrieval profiles
131: 
132: No project-specific configuration shall exist in reusable configuration libraries.
133: 
134: ---
135: 
136: # Runtime Configuration Flow
137: 
138: ```text
139: Project Code
140: 
141: ↓
142: 
143: SchemaLoader
144: 
145: ↓
146: 
147: ProjectDefinitionResolver
148: 
149: ↓
150: 
151: Resolve reusable profiles
152: 
153: ↓
154: 
155: Validate configuration
156: 
157: ↓
158: 
159: Merge configuration
160: 
161: ↓
162: 
163: RuntimeProjectDefinition
164: 
165: ↓
166: 
167: Pipeline Modules
168: ```
169: 
170: The RuntimeProjectDefinition shall be immutable after construction.
171: 
172: ---
173: 
174: # Component Responsibilities
175: 
176: ## SchemaLoader
177: 
178: Shared framework component.
179: 
180: Responsibilities
181: 
182: * load schemas
183: * cache schemas
184: * validate schema syntax
185: * resolve schema references
186: * provide generic schema access
187: 
188: SchemaLoader shall remain reusable and pipeline-independent.
189: 
190: ---
191: 
192: ## ProjectDefinitionResolver
193: 
194: Common EKS pipeline component.
195: 
196: Responsibilities
197: 
198: * load Project Definition
199: * resolve reusable profile references
200: * validate project completeness
201: * merge project-specific configuration
202: * construct RuntimeProjectDefinition
203: * expose RuntimeProjectDefinition to pipeline modules
204: 
205: ProjectDefinitionResolver shall contain all EKS-specific configuration resolution logic.
206: 
207: ---
208: 
209: # Implementation Tasks
210: 
211: | #      | Date       | Phase   | Task                                      | Description                                                                                                                                                                                                                                             | Author   |   Status   |
212: | :----- | :--------- | :------ | :---------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :------- | :--------: |
213: | T1.189 | 2026-07-30 | Phase 1 | Design Project Definition Architecture    | Define the Project Definition architecture, configuration ownership model, RuntimeProjectDefinition model, and interaction between SchemaLoader and ProjectDefinitionResolver.                                                                          | Franklin | 🔷 Planned |
214: | T1.190 | 2026-07-30 | Phase 1 | Implement Project Definition Schema       | Create `eks_project_definition_schema.json` and consolidate all project-specific configuration, including the functionality previously proposed for `eks_project_rules_config.json`.                                                                    | Franklin | 🔷 Planned |
215: | T1.191 | 2026-07-30 | Phase 1 | Refactor Reusable Configuration Libraries | Refactor `eks_doc_config.json` and related configuration schemas to contain only reusable profiles and shared definitions. Remove all project-specific mappings and rules.                                                                              | Franklin | 🔷 Planned |
216: | T1.192 | 2026-07-30 | Phase 1 | Enhance SchemaLoader                      | Extend SchemaLoader to support schema caching, dependency resolution, schema reference lookup, and generic cross-schema validation while remaining independent of EKS business logic.                                                                   | Franklin | 🔷 Planned |
217: | T1.193 | 2026-07-30 | Phase 1 | Implement ProjectDefinitionResolver       | Implement the common EKS pipeline module that loads Project Definitions, resolves reusable profiles, validates configuration, and constructs the immutable RuntimeProjectDefinition.                                                                    | Franklin | 🔷 Planned |
218: | T1.194 | 2026-07-30 | Phase 1 | Refactor EKS Runtime Modules              | Update FileScanner, FilenameParser, RevisionValidator, Asset Loader, Pipeline, Retriever, and future EKS modules to consume RuntimeProjectDefinition instead of reading configuration schemas directly.                                                 | Franklin | 🔷 Planned |
219: | T1.195 | 2026-07-30 | Phase 1 | Implement Configuration Validation        | Validate project completeness, reusable profile references, duplicate definitions, unused profiles, and configuration consistency during Project Definition resolution.                                                                                 | Franklin | 🔷 Planned |
220: | T1.196 | 2026-07-30 | Phase 1 | Migrate Existing Configuration            | Migrate all project-specific configuration into `eks_project_definition_schema.json`, retire `eks_project_rules_config.json`, convert project-keyed definitions into reusable profile references, and maintain backward compatibility during migration. | Franklin | 🔷 Planned |
221: | T1.197 | 2026-07-30 | Phase 1 | Documentation & Regression Testing        | Update architecture documentation, schema reference, migration guide, developer guide, and verify regression across document ingestion, metadata extraction, asset processing, graph construction, retrieval, and RAG workflows.                        | Franklin | 🔷 Planned |
222: 
223: ---
224: 
225: # Validation
226: 
227: The implementation shall verify
228: 
229: * every project exists in `eks_project_definition_schema.json`
230: * every referenced reusable profile exists
231: * project configuration is complete
232: * no duplicate reusable profiles exist
233: * unused reusable profiles are reported
234: * schema dependencies are valid
235: * RuntimeProjectDefinition is successfully constructed
236: 
237: ---
238: 
239: # Migration Strategy
240: 
241: ### Stage 1
242: 
243: Introduce `eks_project_definition_schema.json` while maintaining compatibility with the existing configuration.
244: 
245: ### Stage 2
246: 
247: Refactor EKS runtime modules to consume RuntimeProjectDefinition through ProjectDefinitionResolver.
248: 
249: ### Stage 3
250: 
251: Retire `eks_project_rules_config.json` and remove deprecated project-indexed configuration after all projects have been migrated.
252: 
253: ---
254: 
255: # Deliverables
256: 
257: * `eks_project_definition_schema.json`
258: * Refactored `eks_doc_config.json`
259: * Enhanced SchemaLoader
260: * ProjectDefinitionResolver
261: * RuntimeProjectDefinition model
262: * Updated runtime modules
263: * Cross-schema validation
264: * Configuration migration utility
265: * Updated documentation
266: * Unit tests
267: * Integration tests
268: 
269: ---
270: 
271: # Success Criteria
272: 
273: The implementation is complete when:
274: 
275: * `eks_project_definition_schema.json` is the authoritative source for all project-specific configuration.
276: * `eks_project_rules_config.json` has been retired.
277: * Reusable configuration libraries contain no project-specific settings.
278: * ProjectDefinitionResolver successfully constructs RuntimeProjectDefinition.
279: * Every EKS pipeline module consumes RuntimeProjectDefinition instead of loading schemas independently.
280: * SchemaLoader remains a reusable, pipeline-agnostic framework component.
281: * Multiple projects can share reusable profiles without configuration duplication.
282: * Existing document ingestion, asset processing, graph construction, retrieval, and RAG workflows remain fully backward compatible after migration.

(End of file - total 282 lines)
</content>
```




**Tool: read**

**Input:**
```json
{
  "filePath": "C:\\Users\\franklin.song\\Desktop\\DSAI\\Engineering-and-Design\\eks\\log\\phase1\\p1_issue_log.md",
  "offset": 199
}
```

**Output:**
```
<path>C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\log\phase1\p1_issue_log.md</path>
<type>file</type>
<content>
199: | I136 | 2026-07-18 | Phase 1 | 🟠 High | Hardcoded filename parsing patterns — no per-project configuration | All 4 call sites had hardcoded parsing rules with no schema-driven way to add new projects. | 📐 Aligned | T1.99.110–112 | Updates: U189 — Close: Added schema-driven filename_patterns config block with per-project entries. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-18 |
200: | I137 | 2026-07-18 | Phase 1 | 🟡 Medium | Appendix I: No universal filename parser | 4 call sites used ad-hoc split() — fragile, duplicated, untested. | ✅ Resolved | — | Updates: U189 — Close: Created FilenameParser class (schema-driven, 7 fields per Appendix B §B3). — Approved: 2026-07-18 |
201: | I138 | 2026-07-18 | Phase 1 | 🟡 Medium | Create filename_parser.py module | FilenameParseResult dataclass (9 fields) + FilenameParser class (schema-driven, 8-step algorithm, never raises). | ✅ Resolved | T1.99.113 | Updates: U189 — Close: Created eks/engine/core/filename_parser.py per Appendix I §I5.1. — Approved: 2026-07-18 |
202: | I139 | 2026-07-18 | Phase 1 | 🟡 Medium | Add filename_patterns config block to eks_doc_config.json | Config file needed 2 entries: 131101 TWRP pattern + "*" catch-all. | 📐 Aligned | T1.99.112 | Updates: U189 — Close: Populated eks_doc_config.json v1.3.0. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-18 |
203: | I140 | 2026-07-18 | Phase 1 | 🟡 Medium | Add 4 shared definitions to eks_doc_base_schema.json for filename parser | Missing: filename_pattern_def, filename_segment_def, filename_output_def, filename_error_subcodes_def. | 📐 Aligned | T1.99.111 | Updates: U189 — Close: Added 4 defs to eks_doc_base_schema.json v1.3.0. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-18 |
204: | I141 | 2026-07-18 | Phase 1 | 🟡 Medium | Call-site migration — remove old _parse_filename() from FileScanner | FileScanner.build_placeholder_metadata() used old method with hardcoded patterns. | ✅ Resolved | T1.99.115 | Updates: U189 — Close: Migrated FileScanner to self._parser.parse(); deleted old method. — Approved: 2026-07-18 |
205: | I142 | 2026-07-18 | Phase 1 | 🟡 Medium | Register 7 P5-F-* data error codes in eks_error_config.json | New filename parser needed dedicated error codes. 3 existed; 4 new needed. | 📐 Aligned | T1.99.121 | Updates: U189 — Close: Registered 7 codes + phase_5_file_ops range. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-18 |
206: | I143 | 2026-07-18 | Phase 1 | 🟡 Medium | L2 null-tolerant — register_placeholders() generates synthetic key instead of skipping | "if not doc_number: continue" — file silently dropped. | ✅ Resolved | T1.99.119 | Updates: U189 — Close: Both file_scanner.py and phase1_server.py generate synthetic UNRESOLVED keys. — Approved: 2026-07-18 |
207: | I144 | 2026-07-18 | Phase 1 | 🟡 Medium | L3 null-tolerant — register_document() generates synthetic key instead of KeyError | "raise KeyError("document_number is required")" — crashes pipeline. | ✅ Resolved | T1.99.120 | Updates: U189 — Close: registry.py generates synthetic key instead of raising. — Approved: 2026-07-18 |
208: | I145 | 2026-07-18 | Phase 1 | 🟢 Low | Export FilenameParser from eks/engine/core/__init__.py | New module not discoverable — missing from exports. | ✅ Resolved | T1.99.114 | Updates: U189 — Close: Added 3 exports to __init__.py. — Approved: 2026-07-18 |
209: | I146 | 2026-07-18 | Phase 1 | 🟡 Medium | PipelineOrchestrator uses inline filename parsing at 2 call sites | _process_file() and _update_doc_status() used ad-hoc split() — untested, fragile. | ✅ Resolved | T1.99.116 | Updates: U189 — Close: Replaced both with self._parser.parse(name). — Approved: 2026-07-18 |
210: | I147 | 2026-07-18 | Phase 1 | 🟠 High | Appendix J: No file property extraction — os.stat/hashlib never called in EKS | All 13 file-property columns in doc schema were null. First code to use os.stat/Path.stat/hashlib. | ✅ Resolved | T1.99.128–140 | Updates: U189 — Close: Created FilePropertyExtractor (two-layer: OS stat + per-type embedded mapping). 18 files changed. — Approved: 2026-07-18 |
211: | I148 | 2026-07-18 | Phase 1 | 🟡 Medium | OS-level property extraction — Path.stat() never called | file_size, fs_created, fs_modified, fs_accessed, file_mode — all null. | ✅ Resolved | T1.99.128 | Updates: U189 — Close: Layer 1 extraction via Path.stat() for all 5 file types. — Approved: 2026-07-18 |
212: | I149 | 2026-07-18 | Phase 1 | 🟡 Medium | File hash computation — hashlib never called | No file hash computed anywhere in EKS — impossible to detect duplicates. | ✅ Resolved | T1.99.131 | Updates: U189 — Close: file_hash computed at Layer 1 for all 5 file types. — Approved: 2026-07-18 |
213: | I150 | 2026-07-18 | Phase 1 | 🟡 Medium | Parser-metadata property mapping config — by_file_type entries | file_property_patterns config needed by_file_type entries mapping extension to extraction method. | 📐 Aligned | T1.99.130 | Updates: U189 — Close: 5 file-type entries in eks_doc_config.json. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-18 |
214: | I151 | 2026-07-18 | Phase 1 | 🟡 Medium | Embedded creator/producer extraction — PDF-specific metadata fields | creator_app and producer_lib from PDF metadata had no registry columns. | 📐 Aligned | T1.99.128 | Updates: U189 — Close: Added embedded_creator_app + embedded_producer columns to doc base schema. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-18 |
215: | I152 | 2026-07-18 | Phase 1 | 🟡 Medium | Embedded dates extraction — embedded_created_date + embedded_modified_date | PDF/DOCX/XLSX parsers extract timestamps but no registry columns existed. | 📐 Aligned | T1.99.128 | Updates: U189 — Close: Added embedded_created_date and embedded_modified_date columns. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-18 |
216: | I153 | 2026-07-18 | Phase 1 | 🟡 Medium | New registry columns for file properties — 13 columns needed in doc schema | Document registry had no storage for extracted file properties. | 📐 Aligned | T1.99.128 | Updates: U189 — Close: 13 optional columns in eks_doc_base_schema.json v1.4.0 — 6 OS-level + 7 embedded. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-18 |
217: | I154 | 2026-07-18 | Phase 1 | 🟡 Medium | Dynamic INSERT with extra_properties parameter | register_document() used static INSERT with fixed column list. | ✅ Resolved | T1.99.133 | Updates: U189 — Close: register_document() builds INSERT dynamically from extra_properties keys. — Approved: 2026-07-18 |
218: | I155 | 2026-07-18 | Phase 1 | 🟡 Medium | eks_doc_setup_schema.json missing filename_patterns property | Appendix I required filename_patterns; absent → blocker for schema-driven parser. | 📐 Aligned | T1.99.110 | Updates: U189 — Close: Added filename_patterns property block per Appendix I §I4.10. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-18 |
219: | I156 | 2026-07-18 | Phase 1 | 🟡 Medium | ALTER TABLE migration for existing DB instances with pre-v1.4.0 schema | Existing eks_registry.db instances lack 13 new columns. | ✅ Resolved | T1.99.134 | Updates: U189 — Close: SchemaToDDL auto-migrates missing columns on startup. — Approved: 2026-07-18 |
220: | I157 | 2026-07-18 | Phase 1 | 🟡 Medium | Error code format rename (Phase A of Option A2) | D5→P5 rename: update 12 error code definitions, all parser call sites, and test expectations. | 📐 Aligned | — | Updates: U189 — Close: All codes renamed; call sites + tests updated. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-18 |
221: | I158 | 2026-07-18 | Phase 1 | 🟢 Low | FilePropertyResult.to_registry_dict() mapping | FilePropertyResult dataclass (22 fields) needed field→column name mapping. | ✅ Resolved | T1.99.131 | Updates: U189 — Close: Full field-column mapping in .to_registry_dict(). — Approved: 2026-07-18 |
222: | I159 | 2026-07-18 | Phase 1 | 🟢 Low | File type capability matrix | No documentation of extraction capabilities per file type. 5-type × 13-property matrix needed. | ✅ Resolved | T1.99.131 | Updates: U189 — Close: Capability matrix in FilePropertyExtractor per Appendix J §J5. — Approved: 2026-07-18 |
223: | I160 | 2026-07-18 | Phase 1 | 🟢 Low | DGN/DWG stub support — os_only extraction mode | DGN/DWG parsers are stubs — only OS-level properties can be extracted. | ✅ Resolved | T1.99.130 | Updates: U189 — Close: DGN/DWG use os_only mode; embedded layer skipped. — Approved: 2026-07-18 |
224: | I161 | 2026-07-18 | Phase 1 | 🟢 Low | Unit tests for FilePropertyExtractor | No tests for file property extraction. All 5 file types + edge cases needed. | ✅ Resolved | T1.99.135 | Updates: U189 — Close: TestFilePropertyExtractor class in test_t132_modules.py. — Approved: 2026-07-18 |
225: | I162 | 2026-07-18 | Phase 1 | 🟡 Medium | Health scorer not consuming file property columns | file_size, file_hash etc. not in TIER_3_COLUMNS or ALL_SCOABLE. | ✅ Resolved | T1.99.137 | Updates: U189 — Close: Added 6 columns to health scorer; source-quality bonus; consistency violation. — Approved: 2026-07-18 |
226: | I163 | 2026-07-18 | Phase 1 | 🟡 Medium | Error code registration for filename parser errors | New FilenameParser needed dedicated P-prefix error codes for parse failures. | 📐 Aligned | — | Updates: U189 — Close: Registered P-prefix codes for all filename parser failure modes. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-18 |
227: | I164 | 2026-07-19 | Phase 1 | 🟠 High | Document Metadata Completeness: supersedes/superseded_by chain not implemented | No revision lineage tracking — impossible to trace document revision history. | 📐 Aligned | T1.99.141 | Updates: U190 — Close: Added bidirectional revision-chain columns with pre-INSERT query logic. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-19 |
228: | I165 | 2026-07-19 | Phase 1 | 🟡 Medium | Document Metadata Completeness: document_title derivation missing | No human-readable title column — only document_number. | 📐 Aligned | T1.99.142 | Updates: U190 — Close: Added title derivation chain: embedded_title → filename stem → explicit override. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-19 |
229: | I166 | 2026-07-19 | Phase 1 | 🟡 Medium | Document Metadata Completeness: lifecycle/revision fields missing | No lifecycle_stage, revision_date, revision_description columns. | 📐 Aligned | T1.99.143 | Updates: U190 — Close: Added lifecycle enum (6 stages), revision_date, revision_description. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-19 |
230: | I167 | 2026-07-19 | Phase 1 | 🟡 Medium | Document Metadata Completeness: embedded_revision_number + references_documents missing | DOCX revision metadata not extracted; cross-document refs had no storage. | 📐 Aligned | T1.99.144/T1.99.145 | Updates: U190 — Close: Added embedded_revision_number (DOCX mapping), references_documents (JSON + trigger). — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-19 |
231: | I168 | 2026-07-19 | Phase 1 | 🟡 Medium | Document Metadata Completeness: 7 contextual columns missing | project_phase, contract_package, issued_date, responsible_engineer, total_sheets, language, vendor_name absent. | 📐 Aligned | T1.99.146 | Updates: U190 — Close: Added all 7 columns (nullable). 15 total new columns across I164–I168. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-19 |
232: | I169 | 2026-07-19 | Phase 1 | 🟢 Low | Metadata gap (Phase 1, 1 of 7): project_phase column not in schema | Schema-only addition; nullable with config-level default. | 📐 Aligned | T1.99.146 | Updates: U192 — Close: Added via bulk schema extension (I169–I175). — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-19 |
233: | I170 | 2026-07-19 | Phase 1 | 🟢 Low | Metadata gap (Phase 1, 2 of 7): contract_package column not in schema | Schema-only addition; nullable with config-level default. | 📐 Aligned | T1.99.146 | Updates: U192 — Close: Added via bulk schema extension (I169–I175). — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-19 |
234: | I171 | 2026-07-19 | Phase 1 | 🟢 Low | Metadata gap (Phase 1, 3 of 7): issued_date column not in schema | Schema-only addition; nullable with config-level default. | 📐 Aligned | T1.99.146 | Updates: U192 — Close: Added via bulk schema extension (I169–I175). — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-19 |
235: | I172 | 2026-07-19 | Phase 1 | 🟢 Low | Metadata gap (Phase 1, 4 of 7): responsible_engineer column not in schema | Schema-only addition; nullable with config-level default. | 📐 Aligned | T1.99.146 | Updates: U192 — Close: Added via bulk schema extension (I169–I175). — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-19 |
236: | I173 | 2026-07-19 | Phase 1 | 🟢 Low | Metadata gap (Phase 1, 5 of 7): total_sheets column not in schema | Schema-only addition; defaults to page_count from PDF parser. | 📐 Aligned | T1.99.146 | Updates: U192 — Close: Added via bulk schema extension (I169–I175). — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-19 |
237: | I174 | 2026-07-19 | Phase 1 | 🟢 Low | Metadata gap (Phase 1, 6 of 7): language column not in schema | Schema-only addition; nullable with config-level default "en". | 📐 Aligned | T1.99.146 | Updates: U192 — Close: Added via bulk schema extension (I169–I175). — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-19 |
238: | I175 | 2026-07-19 | Phase 1 | 🟢 Low | Metadata gap (Phase 1, 7 of 7): vendor_name column not in schema | Last of 7 Phase 1 gaps. Schema-only addition; nullable config default. | 📐 Aligned | T1.99.146 | Updates: U192 — Close: Added via bulk schema extension (I169–I175). — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-19 |
239: | I188 | 2026-07-19 | Phase 1 | 🟠 High | CSV/Excel export generates empty files | discovery_inventory + review_flags always 0 rows. (1) filtered by wrong status. (2) used elif instead of else. | ✅ Resolved | T1.99.147–151 | Updates: U190 — Close: Removed status filter; changed to unconditional else: 3 CSV + 3 XLSX generate correctly. 36/36 green. — Approved: 2026-07-19 |
240: | I189 | 2026-07-19 | Phase 1 | 🟠 High | Stale output + test-production DB pollution (4 root causes) | (A) Shared output/ overwrites. (B) Tests call main() → production DB. (C) Export queries ALL docs. (D) test overwrites production exports. | ✅ Resolved | T1.99.153–156 | Updates: U191 — Close: F1 test-isolated DB; F2 pre-run capture; F3 per-run output/<run_id>/; F4 mock.patch temp DB. 36/36 green. — Approved: 2026-07-19 |
241: | I190 | 2026-07-19 | Phase 1 | 🟠 High | Issue log wiped — all 189 issues lost | eks/log/issue_log.md overwritten with empty 17-line header. Restored from git commit; reconstructed from update_log.md and workplan. | ✅ Resolved | — | Close: Restored from git; added eks/test_output/ to .gitignore. — Approved: 2026-07-19 |
242: | I191 | 2026-07-19 | Phase 1 | 🟠 High | Export generates zero files after first pipeline run | pre_doc_numbers filtering scoped exports to only new docs. After first run, all docs pre-existing → zero files. | ✅ Resolved | — | Close: Removed pre_doc_numbers filtering. Always exports all docs. Per-run UUID subdir prevents overwrites. — Approved: 2026-07-19 |
243: | I192 | 2026-07-19 | Phase 1 | 🟠 High | Users cannot identify latest CSV/Excel — UUID folder names meaningless | Per-run output/<uuid>/ directories — impossible to tell which has latest files. | ✅ Resolved | — | Close: After export, atomically copy 6 files to output/ root overwriting previous. Uses atomic dst_tmp.replace(). — Approved: 2026-07-19 |
244: | I193 | 2026-07-19 | Phase 1 | 🟠 High | Export CSV/Excel missing 43 of 54 columns — only 11 hardcoded fields exported | _build_export_rows() hardcodes 11 fields but list_documents() SELECTs * (54 columns). | ✅ Resolved | T1.99.157–160 | Close: Added x_export flags; created resolve_export_columns(); replaced hardcoded builders with schema-driven subsetting. 300/300 pass. — Approved: 2026-07-19 |
245: | I194 | 2026-07-19 | Phase 1 | 🟠 High | 11-gap closure sweep — Appendix B vs. codebase cross-source inconsistencies | Cross-source audit revealed 11 gaps across 6 modules: id format stale, CAD type missing, elements not persisted, DB nullability drift, scope inaccurate, asset_tags unwired, redundant re-parse, no exception isolation, boilerplate hardcoded, migration DDL missed override. [x] G1 id format — [x] G2 CAD type — [x] G3 elements persistence — [x] G4 nullability — [x] G5 scope — [x] G6 asset_tags — [x] G7/G10 re-parse — [x] G8 exception isolation — [x] G9 boilerplate — [x] G11 migration | 📐 Aligned | T1.99.161–167 | Updates: U193 — Close: All 11 gaps closed via edits to 6 files + Appendix B v0.9→1.0.0. 0 linter errors. — Workplan: phase_1_foundation_workplan.md — Approved: 2026-07-19 |
246: | I195 | 2026-07-19 | Phase 1 | 🔴 Critical | GAP-D1: HealthScorer.score() caller bug — structural elements misrouted | pipeline_orchestrator.py calls scorer.score(doc, elements) but signature is score(metadata, extraction_results=None, structural_elements=None). | ✅ Resolved | T1.99.163 | Updates: U194 — Close: Fixed score(doc, structural_elements=elements); updated review_manager.py and tests. — Approved: 2026-07-19 |
247: | I196 | 2026-07-19 | Phase 1 | 🔴 Critical | GAP-D2: 10 message IDs called in code do not exist in eks_message_config.json | Call sites reference STATUS_PHASE_A_START, STATUS_PHASE_A_COMPLETE, STATUS_PHASE_B_START, etc. None exist in config. | ✅ Resolved | T1.99.164 | Updates: U194 — Close: Added 10 message IDs to eks_message_config.json; total 39→49. — Approved: 2026-07-19 |
248: | I197 | 2026-07-19 | Phase 1 | 🟠 High | GAP-D3: 6 ad-hoc error codes used in code not registered in eks_error_config.json | Call sites use D5-REG-001, S-PIP-001/002, D5-DETECT-001, D5-SCORE-001, S-PIP-003. None registered. | ✅ Resolved | T1.99.165 | Updates: U194 — Close: Registered S-R-S-0407/0408/0409, P1-D-P-0003, P3-E-E-0018/0019; updated 6 call sites. 103→109 codes. — Approved: 2026-07-19 |
249: | I199 | 2026-07-19 | Phase 1 | 🟡 Medium | GAP-D5: 15+ new schema columns absent from HealthScorer.ALL_SCOABLE | Document schema grew from 25 to 54+ columns. ALL_SCOABLE omits 15 new columns. | ✅ Resolved | — | Updates: U194/U196 — Close: Added 14 columns to ALL_SCOABLE tier sets. Total scorable: 24→39. — Approved: 2026-07-19 |
250: | I200 | 2026-07-19 | Phase 1 | 🟡 Medium | GAP-D6: COVER_TYPE_SOURCE_SCORES missing Type F (0.0) | Appendix D: Type F → 0.0. Code fallback 0.3 inflates health by +0.045. | ✅ Resolved | — | Updates: U194 — Close: Added "F": 0.0 to COVER_TYPE_SOURCE_SCORES. — Approved: 2026-07-19 |
251: | I201 | 2026-07-19 | Phase 1 | 🟡 Medium | GAP-D7: health_score_impact from errors never applied | ErrorManager.get_health_impact() exists but never called during _process_file() or run_phase_b(). | ✅ Resolved | — | Updates: U194 — Close: Wired get_health_impact() after scoring; penalty via adjusted = max(0.0, raw + penalty/100.0). — Approved: 2026-07-19 |
252: | I202 | 2026-07-19 | Phase 1 | 🟡 Medium | GAP-D8: D7.10 expected elements formula differs between Appendix D and code | Appendix D: always 5 expected. Code: Type A/B expect 4 (no generic 'table'). | ✅ Resolved | — | Updates: U194 — Close: Added table to Type A/B EXPECTED_ELEMENTS_BY_TYPE (4→5). — Approved: 2026-07-19 |
253: | I209 | 2026-07-19 | Phase 1 | 🟠 High | GAP-A2: No EKS engine inherits from BaseEngine | FileScanner, HealthScorer, StructureDetector, ParserRouter, PipelineOrchestrator — none extend BaseEngine. | ✅ Resolved | T1.99.180 | Close: PipelineOrchestrator now inherits from BaseEngine; domain engines kept with direct interfaces. — Approved: 2026-07-19 |
254: | I210 | 2026-07-19 | Phase 1 | 🟡 Medium | GAP-A3: Dual EngineInput/EngineOutput — EKS versions unused | EKS engine/core/base.py versions sit unused; pipeline uses common.library versions. | ✅ Resolved | T1.99.181 | Close: EKS versions now extend common.library versions with graceful fallback. — Approved: 2026-07-19 |
255: | I211 | 2026-07-19 | Phase 1 | 🟡 Medium | GAP-A4: Dependency injection — factories exist but PipelineOrchestrator directly instantiates engines | Appendix F proposes Factory Pattern. PipelineOrchestrator directly instantiates FileScanner, HealthScorer, StructureDetector. | ✅ Resolved | T1.182.1–8 / T1.99.183 | Updates: U203 — Tests: TL010 — Close: Removed duplicate Factory ABC from factories.py; all 4 factories (ParserFactory, HealthScorerFactory, StructureDetectorFactory, EngineFactory) now inherit from common.Factory; manual importlib replaced with self._load_class() from common; EngineFactory gains FileScanner/HealthScorer/StructureDetector mappings; PipelineOrchestrator uses EngineFactory.create() for DI compliance. 114/114 test_phase1 + test_io_contracts tests pass. — Approved: 2026-07-24 by user |
256: | I212 | 2026-07-19 | Phase 1 | 🟠 High | GAP-A5: RevisionManager has no supersession detection logic | RevisionManager has get_latest_revision(), get_revision_history(), is_latest() but no detect_supersession(). Factory pattern evaluated and rejected — RevisionManager requires a live DocumentRegistry dependency, making it a poor fit for the _load_class() pattern. Direct instantiation in PipelineOrchestrator is correct. detect_supersession() now implemented with _compare_revisions() supporting numeric/alphabetic comparison, retroactive supersession detection in Phase B via parsed revision metadata. | ✅ Resolved | T1.99.179 | Updates: U205 — Tests: TL012 — Close: detect_supersession() added to revision.py with _compare_revisions() helper; wired into PipelineOrchestrator._process_file() after successful parse+score, using parsed revision from metadata (fallback to Phase A value). 5 tests covering no-existing, newer, same, older, numeric comparisons. 296/305 pass, 5 new tests, 0 regressions. — Approved: 2026-07-24 by user |
257: | I213 | 2026-07-19 | Phase 1 | 🟡 Medium | GAP-A6: ReviewManager exists but Phase C only flags docs — no review workflow triggered | engine/core/review_manager.py has ManualReviewManager with flag_for_review(), correct_field(), lock_document(), approve_document(). Phase C (run_phase_c()) queries flagged docs and exports review_flags.csv — but never calls any ReviewManager method. No mechanism to update review status back to registry. Phase C is effectively read-only. | 🔷 Deferred for further review | T1.99.187 | Close: ReviewManager initialized in orchestrator; auto-approved clean docs get recalculate_score(). Full interactive review workflow (correct_field, lock, approve) requires UI integration + review state machine. Deferred to Phase 5 (UI integration). Linked to I224. |
258: | I214 | 2026-07-19 | Phase 1 | 🟢 Low | GAP-A7: HealthInput/HealthOutput contracts defined but never used | io_contracts.py defines contracts. PipelineOrchestrator calls raw score() never constructing HealthInput. Factory assessment: DI is already covered via EngineFactory.create("HealthScorer") — no factory gap. Standalone HealthScorerFactory (factories.py:95-144) was dead code — now removed. Contract wiring via score_from_input() is now active in _process_file(). | ✅ Resolved | T1.99.187 / T1.99.198 / T1.99.199 | Updates: U204 — Tests: TL011 — Close: score_from_input() method added (U195). T1.99.198 removed dead HealthScorerFactory and StructureDetectorFactory. T1.99.199 wired HealthInput→score_from_input()→HealthOutput into _process_file(). 291/305 pass, no regressions. — Approved: 2026-07-24 by opencode |
259: | I215 | 2026-07-19 | Phase 1 | 🟡 Medium | GAP-A8: Dual telemetry — two parallel heartbeat systems unsynchronized | main() creates TelemetryHeartbeat; PipelineOrchestrator creates its own local one — no aggregation. | ✅ Resolved | T1.99.186 | Close: PipelineOrchestrator accepts external_telemetry param; _forward_telemetry() forwards to both. — Approved: 2026-07-19 |
260: | I216 | 2026-07-19 | Phase 1 | 🟡 Medium | GAP-A9: Checkpoint/resume — checkpoint writes restored; full resume capability still deferred | Per I124/T1.99.85, per-phase checkpoint writes were commented out. save_checkpoint() now writes per-phase checkpoints. EKSData.extracted_content is populated from checkpoint restore. However, --resume <run_id> CLI flag and cross-phase state restoration are not implemented — resume is partial (single-phase only). | 🔷 Deferred for further review | T1.99.187 | Close: Per-phase checkpoint writes restored. Full --resume <run_id> flag + cross-phase state restoration deferred. |
261: | I217 | 2026-07-19 | Phase 1 | 🟡 Medium | GAP-A10: UI contracts not implemented per Appendix F spec | Appendix F §2.3.3 proposes HTTP API endpoints for independent engine execution + DocumentSelectionContract / PipelineConfigContract. Current eks/ui/backend/ has contracts.py, contract_manager.py, phase1_server.py — but contracts are NOT implemented. UI backend is a thin Flask wrapper around bootstrap_pipeline() + run_pipeline(), not the independent engine endpoint model proposed. | 🔷 Deferred for further study | T1.99.192 | Close: Created UIRenderInput, UIRenderOutput, UIEvent, UIActionResponse stubs in eks/engine/core/ui_contracts.py. No DocumentSelectionContract, no PipelineConfigContract, no Flask endpoint wiring. Full implementation deferred to Phase 5 UI integration. |
262: | I218 | 2026-07-19 | Phase 1 | 🟢 Low | GAP-A11: ParserInput defaults use empty strings — not real values from context | _process_file() constructs ParserInput(config_file="", schema_dir="", output_dir=""). | ✅ Resolved | T1.99.189 | Close: ParserInput now receives context-resolved paths from self.context.paths. — Approved: 2026-07-19 |
263: | I219 | 2026-07-19 | Phase 1 | 🟢 Low | GAP-A12: EKSData.extracted_content populated from checkpoint but never written during execution | Context data store populated only on resume — never on fresh runs. | ✅ Resolved | T1.99.190 | Close: After successful parse, extraction result written to self.context.data.extracted_content. — Approved: 2026-07-19 |
264: | I220 | 2026-07-19 | Phase 1 | 🟢 Low | GAP-A13: ParserRouter lives in parsers/ not router/ per Appendix F | Appendix F §2.1 proposes engine/router/ for parser routing. Current code has ParserRouter at engine/parsers/parser_router.py. Tied to broader folder restructuring (I208). | 🔷 Deferred for further review | T1.99.190 | Close: ParserRouter relocation covered by I208 folder migration. No current import breakage. |
265: | I221 | 2026-07-19 | Phase 1 | 🟢 Low | GAP-A14: TelemetryHeartbeat depends on psutil — failure point on restricted systems | Unconditional import of psutil at module level for memory/CPU sampling. | ✅ Resolved | T1.99.191 | Close: psutil import guarded; _process set to None when unavailable; metrics return early. — Approved: 2026-07-19 |
266: | I222 | 2026-07-19 | Phase 1 | 🟢 Low | GAP-A15: Appendix E schema version freshness | Schema versions in E5.1 stale post-Phase 1 hardening (I164–I168). | ✅ Resolved | T1.99.193 | Close: Full version audit of all 23 schema files against E5.1. Appendix E v0.10. — Approved: 2026-07-19 |
267: | I223 | 2026-07-19 | Phase 1 | 🟢 Low | GAP-A16: No per-engine CLI entry points — Appendix F §2.3.3 not implemented | Appendix F proposes independent engine execution via CLI entry points (eks.engine.discovery.cli, eks.engine.parser.cli, etc.). No such entry points exist — only eks_engine_pipeline.py provides the unified --phase A/B/C/full flag. | 🔷 Deferred for further review | — | Close: Current --phase A/B/C provides equivalent per-phase isolation. Per-engine CLI would require 7 separate arg specs, help text, and tests. Deferred to Phase 2 re-evaluation. |
268: | I224 | 2026-07-19 | Phase 1 | 🟡 Medium | GAP-A17: Phase C is read-only — no mechanism to update review status back to registry | Phase C queries flagged docs and exports CSV/XLSX — but never writes review_status, reviewed_by, reviewed_at back to the registry. Review corrections made in exported files are lost on next pipeline run. review_manager.py has methods (correct_field(), approve_document()) but they're never called. | 🔷 Deferred for further review | T1.99.181 | Close: ManualReviewManager initialized in orchestrator; recalculate_score() used for auto-approved docs. Full write-back (review_status, reviewed_by, reviewed_at) requires UI integration + review state machine. Deferred to Phase 5 (UI integration). Linked to I213. |
269: | I225 | 2026-07-19 | Phase 1 | 🟢 Low | GAP-A18: SchemaToDDL exists but is not called during bootstrap or any pipeline phase | SchemaToDDL generates DDL but DDL never auto-generated at bootstrap; registry.py uses hardcoded CREATE TABLE. | ✅ Resolved | T1.99.191 | Updates: U206 — Tests: TL013 — Close: Bootstrap P7 stores pre-generated DDL; DocumentRegistry accepts pre_generated_ddl param, uses bootstrap DDL instead of re-loading schema; _ensure_schema_version() tracks DDL hash in _eks_schema_meta table; runner.py + CLI tools pass DDL through. |
270: | I226 | 2026-07-20 | Phase 1 | 🔴 Critical | str(5) replaces str(e) — 13 instances, all error info silently lost | 13 call sites use literal str(5) where str(e) was intended across pipeline_orchestrator.py, discovery_cli.py, phase1_server.py, serve.py. | ✅ Resolved | T1.99.194–197 | Close: All 13 str(5) replaced with str(e) across 4 files. Zero str(5) remaining per project-wide grep. — Approved: 2026-07-20 |
271: | I227 | 2026-07-20 | Phase 1 | 🟠 High | Scan redundancy — run_phase_b() re-scans entire directory tree | Phase A calls scanner.scan(root_dir). Phase B calls scanner.scan(root_dir) again — re-walks entire tree. | ✅ Resolved | T1.100, T1.101 | Updates: U198 — Tests: TL005 — Close: Phase B now reads file list from DuckDB (Phase A output) via _resolve_phase_b_files() with filesystem fallback. Approach B selected — DuckDB SSOT. 2 regression tests pass. — Approved: 2026-07-23 by CodeBuddy |
272: | I228 | 2026-07-20 | Phase 1 | 🟠 High | Asset schema (Appendix A) has zero runtime pipeline integration | Appendix A defines 13 fragments, 14 AT_ types, column normalisation mappings for 7 datadrop sheets. eks_asset_base/ setup/ config .json all exist and validate. But no pipeline phase loads asset data, applies fragment composition rules, or validates asset records against conditional fragments. R39 is marked PARTIAL (schema-only, no loader). | 🔴 Open | T3.9–T3.15 | Close: Phase 3 plans asset loaders but workplan status is 🔷 PLANNED. Tracks gap that Phase 1 has no asset extraction engine — risks Phase 3 being blocked on fundamental asset I/O patterns. |
273: | I229 | 2026-07-20 | Phase 1 | 🟡 Medium | Phase B telemetry too granular — file-level checkpoints for every document | run_phase_b() emits telemetry checkpoint for every file processed. 7000+ checkpoints overwhelm storage. | ✅ Resolved | T1.102, T1.103 | Updates: U200 — Tests: TL007 — Close: Replaced per-file telemetry with batch-level checkpoints at 25%/50%/75%/100% milestones. Batch constants defined; `last_milestone_pct` tracker prevents duplicate emission. Per-file ErrorManager logging preserved. 291/305 pass. — Approved: 2026-07-23 by opencode |
274: | I230 | 2026-07-20 | Phase 1 | 🟡 Medium | Multi-stage validation not implemented across phase boundaries | Missing: cross-phase data consistency checks, schema drift detection, data quality gates at A→B and B→C. | ✅ Resolved | T1.104, T1.105 | Updates: U200 — Tests: TL007 — Close: Added validate_phase_transition() to PipelineOrchestrator. A→B gate checks registry has documents with file_path; B→C gate checks extraction_confidence scores exist. Wired into run_full_pipeline() — non-blocking by default, results in summary["gates"]. 291/305 pass. — Approved: 2026-07-23 by opencode |
275: | I231 | 2026-07-20 | Phase 1 | 🟢 Low | Version inconsistency across project metadata | Three sources disagree: knowledge.json v2.6.0, __init__.py v1.4.0, bootstrap.py rev 0.3. | ✅ Resolved | T1.108 | Updates: U201 — Tests: TL008 — Close: eks/__init__.py declares __version__ = "2.6.0". All 8 subpackages (engine, engine.core, engine.parsers, config.schemas, test, ui, ui.backend, log.phase1) import __version__ from eks. pyproject.toml and knowledge.json already at 2.6.0. Full test suite: 291/305 pass. — Approved: 2026-07-23 by opencode |
276: | I232 | 2026-07-20 | Phase 1 | 🟡 Medium | Legacy doc_id fallback path conflicts with RevisionManager | _update_doc_status() legacy path falls back to filename-based lookup. _process_file() uses RevisionManager. Two paths can diverge. | 📐 Aligned | T1.106, T1.107 | Updates: U199 — Tests: TL006 — Close: Added registry.get_document_by_file_path(); _process_file() resolves doc_id once at entry via file_path lookup; _update_doc_status() now requires doc_id; legacy stem-based fallback removed. Workplan §52 added with T1.106/T1.107. 79/79 green. — Workplan: phase_1_foundation_workplan.md v3.x → v3.x+1 (added §52) — Approved: 2026-07-23 |
277: | I233 | 2026-07-23 | Phase 1 | 🟢 Low | eks_engine_pipeline.py approaching 1500+ lines — violates module size conventions | Single-file monolith mixes CLI parsing, bootstrap orchestration, pipeline running, export formatting, preload infrastructure. | 📐 Aligned | T1.109, T1.110, T1.111 | Updates: U202 — Tests: TL009 — Close: Split into pipeline_engine/cli.py, pipeline_engine/runner.py, pipeline_engine/exporter.py. eks_engine_pipeline.py reduced from 1,284 to 295 lines (thin shell). Zero module-level globals — all paths flow from main() via preload_infrastructure(). DCC-faithful *_engine/ convention. 291/305 pass (14 pre-existing rdflib failures). — Workplan: phase_1_foundation_workplan.md §56 added — Approved: 2026-07-23 by opencode |
278: | I234 | 2026-07-24 | Phase 1 | 🟡 Medium | CLI pipeline output gap — no default CSV/Excel export, no pipeline_output.json, no debug_log | eks_engine_pipeline.py (CLI path) generates only eks_registry.db by default. CSV/Excel exports require --export flag (hardcoded default="none" in cli.py). pipeline_output.json is server-only (phase1_server.py:635). debug_log.json was removed per U180/I124 consolidation — no equivalent in CLI path. Expected: CLI generates CSV/Excel (6 files), pipeline_output.json, and debug_log by default. --export default should be schema-driven (config value in eks_config.json) per §16 hardcoded fallback removal — CLI reads from config at runtime, falls back to "none" only when config unavailable. | 📐 Aligned | T1.112, T1.113, T1.114, T1.115 | Updates: U207 — Tests: TL014 — Close: Added export_default to system_parameters schema+config; CLI reads at runtime (schema-driven). CLI writes pipeline_output.json and debug_log.json. --export defaults to "both" via config. T1.115 verified: 5 output files generated by default. — Workplan: phase_1_foundation_workplan.md v5.3→v5.4 (added §57) — Approved: 2026-07-24 by opencode |
279: | I235 | 2026-07-24 | Phase 1 | 🟠 High | I229 batch telemetry logic order bug — 100% checkpoint fires before milestone loop, causing all intermediate milestones to also fire on last file | In run_phase_b() (pipeline_orchestrator.py lines 395–408), the pct >= 1.0 block emits the 100% telemetry checkpoint BEFORE the BATCH_MILESTONES loop executes. For any batch where the final file crosses 100% in the same tick (e.g. total=1, or last file jumps from <75% to 100%), the loop then evaluates last_milestone_pct < 0.25 <= 1.0 → True, last_milestone_pct < 0.50 <= 1.0 → True, last_milestone_pct < 0.75 <= 1.0 → True — all three intermediate milestones fire after 100% is already emitted. Result: up to 4 redundant checkpoint records in the same processing tick, defeating the purpose of I229. Additionally last_milestone_pct is never updated to 1.0 after the 100% block runs. T1.103 (dedicated milestone assertion test) was listed in task_log but not implemented — no test would catch this regression. | 📐 Aligned | T1.103, T1.116, T1.117 | Updates: U211 — Tests: TL015 — Close: Folded 1.0 into BATCH_MILESTONES, removed separate pct>=1.0 block, milestones now flow through single sorted loop in correct order. 3 regression tests (4-file, 1-file, 2-file) verify strict ascending order with no duplicates. 91/91 pass. — Workplan: phase_1_foundation_workplan.md v5.4→v5.5 (added §58) — Approved: 2026-07-27 by opencode |
280: | I236 | 2026-07-24 | Phase 1 | 🟡 Medium | ERROR_FILE_PROCESSING kwarg mismatch — call site passes error= but template expects {detail}, causing silent fallback to raw template literal | In run_phase_b() (pipeline_orchestrator.py line 378): mm.show("ERROR_FILE_PROCESSING", filename=file_path, error=str(e)). The eks_message_config.json template is: "Error processing {filename}: {detail}". The kwarg key is error but the placeholder is {detail}. BaseMessageManager.show() catches the KeyError silently (returns raw template string with unreplaced {detail}). Result: every file processing error prints the literal string "Error processing <path>: {detail}" instead of the actual exception message — error detail is completely invisible to the operator. Level=0 means this fires at all verbosity levels, so the broken output is always visible. | 📐 Aligned | T1.118, T1.119 | Updates: U212 — Tests: TL016 — Close: Changed error=str(e) → detail=str(e) at call site; template kept as SSOT. Grep confirmed sole occurrence of ERROR_FILE_PROCESSING and zero other show() calls with error= kwarg. 2 regression tests assert hydrated message contains actual exception text and does not contain literal {detail}. 142/142 pass. — Workplan: phase_1_foundation_workplan.md v5.5→v5.6 (added §59) — Approved: 2026-07-27 by opencode |
281: | I237 | 2026-07-27 | Phase 1 | 🟡 Medium | Phase B milestone progress (25/50/75/100%) never reaches CLI console at any debug level | TelemetryHeartbeat created with verbose=False in PipelineOrchestrator.__init__ (line 135). add_checkpoint() only prints when self.verbose=True (heartbeat.py:268). BATCH_MILESTONES loop (lines 394–405) calls only _forward_telemetry() — no logger.status() or mm.show() call accompanies. Result: milestones exist in-memory but invisible to CLI user at --level 0, 1, 2, or 3. **SSOT finding**: `verbose` parameter has zero schema/config backing — grep of all EKS schema and config JSON files finds no `telemetry` or `verbose` key. Archived `project_setup.json` had a `verbose` field (removed per I046). Hardcoded `verbose=False` at `pipeline_orchestrator.py:135` violates AGENTS.md §15 (path/param SSOT) and §16 (hardcoded fallback removal). Resolution: add `telemetry_verbose` to `system_parameters` schema chain (base+config), pass through bootstrap → runner → PipelineOrchestrator → TelemetryHeartbeat, default `true` so milestones visible at default --level 1. | 📐 Aligned | T1.120, T1.121, T1.122, T1.123 | Updates: U214 — Tests: TL017 — Close: Added telemetry_verbose to eks_base_schema.json v1.11.0 + eks_config.json v1.9.0; PipelineOrchestrator passes to TelemetryHeartbeat; 3 call sites in runner.py + discovery_cli.py updated; 2 regression tests verify milestone print/suppress at default level. 321/321 pass. — Workplan: phase_1_foundation_workplan.md v5.7 (added §60) — Approved: 2026-07-27 by opencode |
282: | I238 | 2026-07-27 | Phase 1 | 🟡 High | Phase A per-document STATUS floods CLI — needs batch milestones | Phase A register_placeholders() emits `logger.status("Document {doc_id} registered successfully.")` once per document via `registry.register_document()` (registry.py:629). For 42 registrations, this is 42 STATUS lines — noisy at default --level 1. Phase B solved the same problem via 4 batch milestones (25/50/75/100%) at STATUS level with per-file details at INFO only. Resolution: (T1.124) downgrade per-document STATUS to INFO in registry.register_document(); (T1.125) add batch milestone progress (25%/50%/75%/100%) in register_placeholders() loop matching Phase B pattern; (T1.126) add regression tests. | 📐 Aligned | T1.124, T1.125, T1.126 | Updates: U215 — Tests: TL018 — Close: registry.py:629 logger.status→logger.info; file_scanner.py added BATCH_MILESTONES loop in register_placeholders() emitting [TELEMETRY] A-registration at 25/50/75/100%; 2 regression tests verify milestone output and per-doc INFO level. 323/323 pass. — Workplan: phase_1_foundation_workplan.md v5.8 (added §61) — Approved: 2026-07-27 by user |
283: | I239 | 2026-07-27 | Phase 1 | 🟢 Low | STR_PHASE_B_MILESTONE template overflows | Template has both `{milestone}` and `{pct}` placeholders — `{pct}` stale from earlier template iteration. Fixed by removing `{pct}` placeholder from message config template string. | ✅ Resolved | — | Updates: U200 — Workplan: §58 (I235 batch) — Close: Removed stale `{pct}` placeholder from `STR_PHASE_B_MILESTONE` template; `{milestone}` is the sole placeholder. |
284: | I240 | 2026-07-27 | Phase 1 | 🟡 Medium | Phase B milestone always shows 100% | Milestone always 100% because milestone only fires on final file (100% complete). Was a misunderstanding of old milestone logic — actual cause was I235 (ordering: `_after` fired milestone BEFORE processing). | ⛔ Won't Implement | — | Close: Misunderstanding. Root cause was I235 ordering fix (T1.116/T1.117). Batch milestones (I238) provide correct per-batch progress. No additional work. |
285: | I241 | 2026-07-27 | Phase 1 | 🟡 Medium | Phase A milestone reports 100% at last file | Per-document STATUS showed 100% because last file had `last_milestone=100`. Was a misunderstanding of STATUS vs milestone distinction. | ⛔ Won't Implement | — | Close: Misunderstanding. Phase A per-document STATUS naturally shows 100% for last file in the loop. Batch milestones (I238) provide proper 25/50/75/100% progress across the full registration batch. No additional work. |
286: | I242 | 2026-07-27 | Phase 1 | 🟡 Medium | ERROR_FILE_PROCESSING level 0→2 fires at all verbosity levels | `eks_message_config.json` defined `"level": 0`, firing even at `--level 0` silent mode. With 738/753 Phase B file failures, produces ~740 visible error lines at default `--level 1`. First fix (U200): `0→1` — suppressed at `--level 0` but still visible at default. Second fix (U201): `1→2` — suppressed at `--level 0` and `--level 1`, visible at `--level 2+`. Also replaced bare `logger.error()` call at `pipeline_orchestrator.py:916` with `message_manager.show("ERROR_FILE_PROCESSING")` — routes through level 2 gate. | ✅ Resolved | T1.127, T1.128, T1.131 | Updates: U200, U201 — Tests: TL005 — Close: Level changed 0→2; bare `logger.error()`→MessageManager at L916. |
287: | I243 | 2026-07-27 | Phase 1 | 🟡 Medium | STATUS_PHASE_B_COMPLETE missing `total=` kwarg | Template `{success}/{total} success, {partial} partial, {failed} failed` has `{total}` but call site omits `total=`. `KeyError` caught silently — template literal `{success}/{total}` appears in output. Same bug pattern as I236. | ✅ Resolved | T1.129, T1.130 | Updates: U200 — Tests: TL005 — Close: Added `total=total` to `show()` call at `pipeline_orchestrator.py:438`. |
288: | I244 | 2026-07-27 | Phase 1 | 🟡 Medium | Default-level verbosity noise — per-document info messages and inconsistent severity-to-logger mapping | Post-I242 noise audit found 7 per-document `logger.info()` calls at level 1 and 4 design gaps. **Resolved**: 4 per-doc `info()`→`debug()`; S-R-S-0409 FATAL→HIGH; `file_scanner.py:222` info→debug; `mm.set_verbosity(level)` in `main()`; startup message directing users to debug_log.json; P3-E-E-0018/0019/P5-R-P-0003 severity WARNING→HIGH (T1.135); UniversalLogger `_log()` record-before-gate (T1.138). All 7 per-doc info calls at level 1 downgraded. Severity-to-logger asymmetry resolved — both handle_system_error and handle_data_error route HIGH→`warning()`. | ✅ Resolved | T1.132–T1.133, T1.135–T1.136, T1.138 | Updates: U201 — Tests: TL005 — Close: All default-level verbosity noise gaps closed. Per-doc messages suppressed at --level 1. Users directed to debug_log.json for details. |
289: | I245 | 2026-07-27 | Phase 1 | 🟡 Medium | Sub-modules lack ErrorManager wiring — 44 data codes and 58 system codes registered but never raised | 50 data + 61 system codes in `eks_error_config.json`. Only 6 data codes and 3 system codes are actually raised via ErrorManager — all from `pipeline_orchestrator.py`. Sub-modules use `logger.warning()` with error codes in message strings. Codes stay registered for documentation. ErrorManager scope remains on orchestrator-level errors. Health scoring completeness dimension already captures field quality — wiring ErrorManager into sub-modules would add redundant double-counting. | ⛔ Won't Implement | — | Close: Per-document validation warnings correctly use `logger.warning()` captured in `debug_log.json`. ErrorManager fail-fast is for infrastructure errors, not per-document issues. Utility classes (`filename_parser`, `file_property_parser`) lack ErrorManager injection. Bootstrap uses `BootstrapError` (correct mechanism). No meaningful benefit from wiring. |
290: | I246 | 2026-07-27 | Phase 1 | 🟢 Low | Message catalog under-deployed — 39 of 49 registered messages never emitted | Only 9 unique message IDs emitted via `message_manager.show()` — all from `pipeline_orchestrator.py`. The remaining 39 messages are catalog design artifacts. Sub-modules use inline `logger.X()` text equivalent to the catalog templates. WARNING message IDs (`WARNING_SCANNED_PDF`, etc.) have zero string references in engine code — the catalog was defined retrospectively. Same pattern and rationale as I245. | ⛔ Won't Implement | — | Close: Message catalog is a design reference documenting intended messages. Sub-modules use equivalent inline `logger.X()` text. The 9 phase-level messages (Phase A/B/C start/complete, pipeline start/complete, ERROR_FILE_PROCESSING) adequately cover pipeline lifecycle. Wiring sub-modules to MessageManager would add injection dependencies without changing user-visible behavior. |
291: | I247 | 2026-07-27 | Phase 1 | 🟢 Low | Config metadata miscount — data_logic_codes 48→50, total_codes 109→111 | `eks_error_config.json` metadata header had stale counts. **Resolution**: Fixed during I112 standardization (T1.143). `data_logic_codes` corrected from 48→50, `total_codes` from 109→111. All counts now match actual registered codes. | ✅ Resolved | T1.143 (via I112) | Close: Metadata counts corrected as part of I112 error code standardization. Config version 1.4.0. |
292: | I248 | 2026-07-27 | Phase 1 | 🟡 Medium | Pipeline batch health scoring not wired — `score_batch()` exists but never called; D7.7 health grades unimplemented | `health_scorer.score_batch()` exists but no pipeline code calls it. Appendix D §D7.7 pipeline health grades (A+≥99% through F<60%) with formula `(total_docs - critical_errors - high_errors) / total_docs × 100` and `avg_document_health` — none executed. **Resolution**: Wired `score_batch()` into `run_phase_b()` after the processing loop — queries registry, computes `avg_document_health` and status counts, appends to Phase B summary. Pipeline health grade from D7.7 deferred — `score_batch()` provides the numeric inputs needed. | ✅ Resolved | T1.148 | Updates: U216 — Close: `score_batch()` called at end of Phase B; `avg_document_health` and status breakdown added to summary. |
293: | I249 | 2026-07-27 | Phase 1 | 🟡 Medium | UniversalLogger level not reconciled after bootstrap; `_log()` gates record + print together | Two gaps: (1) Logger created with `early_level`; when bootstrap resolves different level, logger never updated — only TelemetryHeartbeat recreated. **Fixed**: `logger.set_level(level)` added after bootstrap reconcile (T1.136). (2) `UniversalLogger._log()` checks level gate before appending to `debug_object["logs"]` — entries above verbosity neither printed NOR saved. **Fixed**: Reordered to record before gate print (T1.138). All log entries now saved regardless of verbosity. | ✅ Resolved | T1.136, T1.138 | Close: Both gaps closed. Logger level reconciled after bootstrap. Record-before-gate implemented in UniversalLogger. |
294: | I250 | 2026-07-27 | Phase 1 | 🟡 Medium | Document type registry not extracted to standalone schema — inline in eks_doc_config.json violates SSOT | Current `document_type_registry` is embedded inline in `eks_doc_config.json` with no standalone schema validation. Must follow the facility/discipline/project/department pattern: add `document_type_entry_def` to `eks_doc_base_schema.json`, create `eks_document_type_schema.json` with all 15 valid codes (DWG, PI-PID, SPC, DS, MAN, OM, RPT, CAD, DR, SP, CL, BQ, VI, M3, QA), update `eks_doc_config.json` to `$ref` the new schema. This aligns with DCC's `document_type_schema.json` pattern. Created during T1.149. | ✅ Resolved | T1.149 | Close: `document_type_entry_def` added to `eks_doc_base_schema.json`. `eks_document_type_schema.json` created with 15 codes. `eks_doc_setup_schema.json` updated to `$ref` the new definition. |
295: | I251 | 2026-07-27 | Phase 1 | 🟡 Medium | Document type schema not wired into pipeline — SchemaLoader, FilenameParser, and dispatch use inline config not schema SSOT | After I250 creates the standalone schema, the pipeline must be updated to consume it. Three wiring points: (1) SchemaLoader — add `eks_document_type_schema.json` to its load chain so `$ref` resolution works. (2) `eks_doc_config.json` — replace inline `document_type_registry` array with `{"$ref": "..."}` to the new schema. (3) FilenameParser segment validation — currently uses `_doc_type_codes` set built from inline config; must derive from schema instead. | ✅ Resolved | T1.150, T1.151, T1.152 | Close: `eks_document_type_schema.json` registered in SchemaLoader `_SCHEMA_FILES` mapping. Validation now resolves through the schema chain. |

(Output capped at 50 KB. Showing lines 199-295. Use offset=296 to continue.)
</content>
```

---

## Assistant (Build · DeepSeek V4 Flash Free · 6.1s)

_Thinking:_

I need to continue reading the issue log to find I265. The issue log was cut off at line 295, and I265 isn't in that range. Let me continue reading.







**Tool: read**

**Input:**
```json
{
  "filePath": "C:\\Users\\franklin.song\\Desktop\\DSAI\\Engineering-and-Design\\eks\\log\\phase1\\p1_issue_log.md",
  "offset": 296
}
```

**Output:**
```
<path>C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\log\phase1\p1_issue_log.md</path>
<type>file</type>
<content>
296: | I252 | 2026-07-27 | Phase 1 | 🟡 Medium | Phase B never updates project_number, area, discipline, document_type in DB — identity fields frozen at Phase A values | Phase A writes these four fields once from filename parsing, but `_infer_doc_type()` may overwrite document_type with extension guess and discipline may fail validation. Phase B parses cover sheet metadata via PDFParser which could contain accurate values, reads FilePropertyExtractor for OS/embedded properties, but never extracts project_number/area/discipline/document_type from the parser output or cover sheet results. `_update_doc_status(extra_properties=registry_props)` only passes file property fields — these four identity fields are never included. PDF cover sheet extraction may yield better values than filename parsing (e.g., correct document_type from cover sheet title block), but they are silently discarded. | ✅ Resolved | T1.153, T1.154, T1.155 | Close: Identity fields extracted from parser metadata in `_process_file()` and written back via `extra_properties`. Document_type priority: cover sheet > filename segment > extension inference. `_infer_doc_type()` made conditional. COLUMN_ALLOWLIST already includes all four fields. |
297: | I253 | 2026-07-27 | Phase 1 | 🟠 High | Stale registry causes 795 pipeline failures — null file_type crashes parser factory | `eks_registry.db` had 795 rows from previous dev runs with null `file_type`. `ParserFactory.create()` at `factories.py:61` calls `file_type.lower()` without null guard → `'NoneType' object has no attribute 'lower'`. Also `_resolve_phase_b_files()` used `.get("file_type", "")` which returns None for SQL NULL. **Fix**: Deleted stale DB. Added null guard in `ParserFactory.create()`. Fixed `_resolve_phase_b_files()` to use `r.get("file_type") or ""`. Pipeline now runs clean — 0 failures. | ✅ Resolved | — | Close: Stale DB deleted. Null guard in factories.py:61. Null-to-empty conversion in _resolve_phase_b_files. |
298: | I254 | 2026-07-28 | Phase 1 | 🟠 High | Path doubling — --data-dir CLI argument and pipeline_root_dir combine to produce eks/eks/data instead of eks/data | `eks_engine_pipeline.py` hardcodes `pipeline_root_dir = "eks"` (line 116). Bootstrap `_bootstrap_params()` at `bootstrap.py:488` resolves relative CLI paths as `project_root / eks_root / cli_path`. When user passes `--data-dir eks/data`, this produces `.../eks/eks/data` (doubled). The correct path `.../eks/data` exists. **Fix applied**: Strip `eks_root` prefix from relative CLI `--data-dir` paths before combining. If `cli_str` starts with `"eks/"`, strip it; if equal to `"eks"`, use empty string. Absolute paths unchanged. 3 regression tests added. bootstrap.py rev 0.4→0.5. | ✅ Resolved | T1.156 | Updates: U221 — Tests: TL019 — Close: eks_root prefix stripped from relative CLI --data-dir in _bootstrap_params(); all 3 regression tests pass |
299: | I255 | 2026-07-28 | Phase 1 | 🟠 High | FilenameParser `_resolve_pattern()` always selects `"*"` pattern (0 segments) because `project_code=None` in all call sites — identity fields never extracted, rendering I252/I253 fixes ineffective | `FilenameParser.__init__()` receives `project_code=None` in both `FileScanner` (`file_scanner.py:36`) and `PipelineOrchestrator` (`pipeline_orchestrator.py:125`). `_resolve_pattern()` at `filename_parser.py:140` only attempts `self._patterns.get(self._project_code)` when `self._project_code` is truthy. Since `project_code=None`, it always falls to `self._patterns.get("*", self._HARDCODED_DEFAULT)` — the `"*"` pattern has `"segments": []` (empty), so `_extract_segments()` returns `False` immediately. Result: `to_metadata_dict()` excludes all four identity fields (`project_number`, `area`, `discipline`, `document_type`). The I252 Phase B write-back fix reads from PDF parser metadata which also has none of these fields. All pipeline output has NULL identity fields. `eks_project_code_schema.json` defines 3 valid project codes (`131101`, `131242`, `999999`) with corresponding patterns in `eks_doc_config.json:filename_patterns` — but none are ever tried. **Fix applied**: Removed `project_code` from `__init__`; added `project_code_registry: Optional[List[str]]`. New `_detect_pattern(stem)` method tries each registered code's pattern by checking first segment against code — returns matching pattern or `"*"` fallback. Called per-parse in `parse()`. Both call sites (`FileScanner`, `PipelineOrchestrator`) derive `project_code_registry` from `filename_patterns` keys (minus `"*"`). Also fixed pre-existing finalization bug in `parse()` where 0-segment `"*"` pattern produced `parse_status="ok"` instead of `"unresolvable"`. 2 regression tests added. `filename_parser.py` rev 1.0.0→1.1.0, `file_scanner.py` rev 1.5.0→1.6.0, `pipeline_orchestrator.py` rev 0.7→0.8. | ✅ Resolved | T1.157, T1.158 | Updates: U222 — Tests: TL020 — Close: FilenameParser a... (line truncated to 2000 chars)
300: | I256 | 2026-07-28 | Phase 1 | 🟡 Medium | project_title always NULL in registry — never populated despite project_number now being extracted (I255) and code→title mapping existing in eks_project_code_schema.json | **Fix applied — 4 tasks completed**: **T1.159 (§72)** — Registered `eks_project_code_schema` in `SchemaLoader._STEM_TO_ATTR` as `"project_code_schema"`. Post-load injects `project_code_titles` dict into `doc_config` from `projects[].code→description`. Updated `eks_doc_setup_schema.json` to allow the runtime-injected property. **T1.160 (§72)** — Added `project_title: Optional[str]` to `FilenameParseResult` + `to_metadata_dict()`. Added `project_code_titles` param to `FilenameParser.__init__()`. In `_extract_segments()`, looks up title from map when `project_number` extracted. All call sites updated: `FileScanner` (rev 1.6.0→1.7.0) and `PipelineOrchestrator` pass `project_code_titles` from `doc_config`. **T1.161 (§72)** — Extended I252 block with 3-tier priority: cover sheet metadata > code→title lookup > Phase A value. **T1.162 (§72)** — `test_filename_parser_populates_project_title` added with 3 sub-tests (known code→title, another code→title, fallback→null). All pass. Full suite: 327/332 pass (5 pre-existing unrelated failures). | ✅ Resolved | T1.159, T1.160, T1.161, T1.162 | Updates: U223–U227 — Tests: TL021 — Close: project_title now populated from project_code_titles mapping at parse time and Phase B write-back — Approved: 2026-07-28 by opencode |
301: | I257 | 2026-07-28 | Phase 1 | 🟡 Medium | Silent doc_config validation failure in _bootstrap_registry() — except Exception: pass swallows SchemaLoader errors; debug_log shows doc_config: 0 keys as normal INFO | In `bootstrap.py:300-306`, `_bootstrap_registry()` wraps `SchemaLoader.load_all()` in `try/except Exception: pass`. When `_validate_doc_config()` raises a `ValidationError`, the exception is silently swallowed. `doc_config` stays `{}` (default from `__init__`). The P3 completion message logs `doc_config: 0 keys` as a normal INFO — no ERROR, no WARNING, no trace of the actual validation failure is recorded in `debug_object["errors"]` or `debug_object["logs"]`. Diagnosis is impossible without source-code inspection. **Fix**: Registered `S-B-S-0609` `BOOT_CONFIG_DEGRADED` (WARNING, `stops_pipeline: false`) in `eks_error_config.json` v1.5.0. Replaced silent `pass` at bootstrap.py:305 with `self._log(f"doc_config schema validation failed — using empty defaults: {exc}", level=2)`. Fail-fast does NOT apply — the inner try/except is intentionally non-fatal. Pipeline continues with `doc_config = {}` (graceful degradation). Regression test `test_257_doc_config_failure_logged` verifies the log entry. T1.163 implemented the log; T1.164 added the test. | ✅ Resolved | T1.163, T1.164 | Updates: U228 — Tests: TL022 — Close: 7 silent bootstrap swallows replaced with logged WARNING entries; S-B-S-0609 registered — Approved: 2026-07-28 by opencode |
302: | I258 | 2026-07-28 | Phase 1 | 🟡 Medium | 6 additional silent exception swallows in EKSBootstrapManager — ConfigRegistry fallback, P7 doc_config, ErrorManager/MessageManager lazy-init all drop diagnostics | Post-I257 audit found 6 more sites where exceptions are caught and silently dropped with zero logging in `eks/engine/core/bootstrap.py`. **Site #1** (line 128): `_eks_config_loader()` — if `ConfigRegistry.__init__()` fails, silently falls back to raw `SchemaLoader` — pipeline runs with degraded config, no warning. **Site #2** (line 365): `_bootstrap_schema()` (P7) — same `except Exception: pass` pattern as I257 for doc_config load (duplicate). **Site #3** (line 568): `to_dict()` — `ErrorManager` lazy-init fails, silent `pass` — error handling goes dark. **Site #4** (line 576): `to_dict()` — `MessageManager` lazy-init fails — catalog goes dark. **Site #5** (line 650): `to_pipeline_context()` — `ErrorManager` lazy-init fails — pipeline context has `None` error manager. **Site #6** (line 659): `to_pipeline_context()` — `MessageManager` lazy-init fails — context has `None` message manager. All 6 sites share `except Exception: pass` pattern — no `_log()`, no `logger.warning()`, no `print(stderr)`. None of the failure paths are recorded in `debug_object["logs"]` or `debug_object["errors"]`. **Fix**: Registered 6 error codes `S-B-S-0610`–`S-B-S-0615` (WARNING, `stops_pipeline: false`) in `eks_error_config.json` v1.5.0. Bootstrap range end_id `0608`→`0615`, count `8`→`15`. Replaced each silent `pass` with `self._log(f"...failed: {exc}", level=2)`. Fail-fast does NOT apply to any — each is intentionally non-fatal. Regression tests added for all 6 paths. bootstrap.py rev 0.5→0.6. | ✅ Resolved | T1.165–T1.170 | Updates: U228 — Tests: TL022 — Close: 6 silent bootstrap swallows replaced with logged WARNING entries; S-B-S-0610–S-B-S-0615 registered — Approved: 2026-07-28 by opencode |
303: | I259 | 2026-07-29 | Phase 1 | 🔴 Critical | Tier 3 fallback scan missing in SchemaLoader — auxiliary schemas never loaded despite _STEM_TO_ATTR entries | load_all() only processes discover_schema_files() output (Tiers 1+2). 5 auxiliary schemas (eks_project_code_schema, eks_document_type_schema, eks_department_schema, eks_discipline_schema, eks_facility_schema) match no Tier 2 discovery pattern — only *_base_schema.json, *_base.json, *_setup_schema.json, *_config.json are defined. No *_schema.json (generic) pattern exists. No Tier 3 fallback scan catches them. **Impact**: I256 added project_code_titles extraction code in post-load setup, but self.project_code_schema defaults to {} because the source file is never loaded into the runtime attribute. project_code_titles is always empty at runtime. The original project_title NULL bug persists. **Fix**: Added discover_schema_files_tier3() to common/library/loader/schema_discovery.py (T1.171); wired in SchemaLoader.load_all() → _discover() (T1.172); tier3 regression test added (T1.173). schema_loader.py rev 1.1.0→1.2.0. | ✅ Resolved | T1.171, T1.172, T1.173 | Updates: U230 — Tests: TL023 — Close: Tier 3 fallback now scans _search_dirs for known _STEM_TO_ATTR stems not matched by glob patterns; _discover() injects results into registry before _load() runs — Approved: 2026-07-29 by opencode |
304: | I260 | 2026-07-29 | Phase 1 | 🟡 Medium | _STEM_TO_ATTR missing 3 auxiliary schema entries — department, discipline, facility schemas unmapped | 3 auxiliary schemas (eks_department_schema.json, eks_discipline_schema.json, eks_facility_schema.json) are referenced via $ref from eks_config.json but have no _STEM_TO_ATTR entry. Even with Tier 3 fallback, the load loop at line 139 would skip them to _extra_schemas because stem not in _STEM_TO_ATTR. No runtime key extraction can use their data (e.g., discipline code→description lookup). **Fix**: Added 3 entries to _STEM_TO_ATTR + corresponding self.*_schema: Dict = {} attributes in __init__ (T1.174). schema_loader.py rev 1.1.0→1.2.0. | ✅ Resolved | T1.174 | Updates: U230 — Tests: — Close: 3 _STEM_TO_ATTR entries (department_schema, discipline_schema, facility_schema) + matching __init__ attributes added — Approved: 2026-07-29 by opencode |
305: | I261 | 2026-07-29 | Phase 1 | 🟡 Medium | P7_schema bootstrap phase is a no-op stub — 4-stage lifecycle never invoked | BootstrapManager._bootstrap_schema() at manager.py:677 records phase complete with zero logic. E13.5 specifies discover→load→validate orchestration. No error codes for per-stage failures. **Fix**: Implemented _bootstrap_schema() with configurable schema_loader strategy hook (T1.175); added S-B-S-0616 (empty discovery) and S-B-S-0617 (cross-ref failure) to eks_error_config.json v1.6.0 (T1.176); added validate_schema_conformance() to ValidationManager (T1.177). manager.py rev 0.1→0.2. | ✅ Resolved | T1.175, T1.176, T1.177 | Updates: U230 — Tests: — Close: _bootstrap_schema() now invokes schema_loader hook, emits S-B-S-0616/S-B-S-0617 on failure; validate_schema_conformance() added to ValidationManager — Approved: 2026-07-29 by opencode |
306: | I262 | 2026-07-29 | Phase 1 | 🟢 Low | $id URI registry not shared via common/ — DCC ref_resolver not extracted | DCC’s ref_resolver._build_uri_registry() scans all .json files for $id URIs. EKS relies on jsonschema’s internal $ref resolution with no explicit URI registry. No cross-project reuse. **Fix**: Extracted _build_uri_registry() to new common/library/loader/ref_resolver.py with $id uniqueness validation (T1.178). | ✅ Resolved | T1.178 | Updates: U230 — Tests: — Close: build_uri_registry() extracted to common/library/loader/ref_resolver.py; exported from __init__.py — Approved: 2026-07-29 by opencode |
307: | I263 | 2026-07-29 | Phase 1 | 🟢 Low | 4 validation levels conflated in load_all() — no stage separation | E13.3 specifies 4 explicit validation levels (existence → conformance → cross-ref → key integrity). Current code mixes all into one load_all() method with no stage-separated methods. **Fix**: Added validate_schema_conformance() to ValidationManager (T1.179); refactored SchemaLoader.load_all() into 4 methods: _discover() → _load() → _validate() → _extract() (T1.180); registered S-B-S-0618 (conformance failure) in eks_error_config.json v1.6.0 (T1.181). schema_loader.py rev 1.1.0→1.2.0. | ✅ Resolved | T1.179, T1.180, T1.181 | Updates: U230 — Tests: — Close: load_all() refactored into 4 explicit stages; validate_schema_conformance() in ValidationManager; S-B-S-0618 registered — Approved: 2026-07-29 by opencode |
308: | I264 | 2026-07-29 | Phase 1 | 🟡 Medium | Column processing metadata not schema-driven — EKS doc registry columns lack processing phase, calculation, validation, and schema_ref metadata | DCC comparison review identified 5 missing column-processing features. EKS `eks_doc_base_schema.json` defines column structure (type, null, default) but not processing semantics. (a) no `is_calculated` flag — cannot distinguish source vs derived columns. (b) no `processing_phase` — no declarative mapping of populated-in-Phase-A vs Phase-B. (c) no per-column `validation` rules — all validation is hardcoded in 11 `_validate_*` methods. (d) no `calculation` strategy — project_title priority chain hardcoded in `pipeline_orchestrator.py:902-914`. (e) no `column_type` classification — no `code_column`/`id_column`/`date_column` role typing. **Design approved**: Single `ColumnProcessor` central orchestrator that reads `column_processing` config and dispatches each column to the appropriate handler module by `calculation.type`. All existing hardcoded column logic registers as handlers. Zero column logic outside schema config. **Refined per review**: BaseColumnProcessor + HandlerRegistry in common/library/column_processor/ (shared). EKSColumnProcessor subclass in eks/engine/core/. | ⏳ In Progress | T1.182–T1.188 | T1.186 ⏳ — enhancing 9 handler stubs with real logic. T1.185 ✅ — common/library/column_processor/ created (BaseColumnProcessor, HandlerRegistry) + EKSColumnProcessor with 9 stubs. T1.182 ✅ — 6 defs added to base schema (v1.9.0). T1.183 ✅ — column_processing property in setup schema (v1.7.0). T1.184 ✅ — 42 entries as DCC-aligned object keys in config (v1.6.0). — Approved: 2026-07-29 by user |
309: | **265** | 2026-07-30 | Phase 1 | 🟡 Medium | **Project Definition Schema Refactoring — Establish `eks_project_definition_schema.json` as the Project SSOT** | Project-specific configuration is currently distributed across multiple schemas, resulting in duplicated project identifiers, split configuration ownership, duplicated parser definitions, and SSOT violations. Refactor the architecture by introducing `eks_project_definition_schema.json` as the authoritative Project Definition containing all project-specific configuration. Reusable configuration (e.g., filename patterns, parser profiles, OCR profiles, ontology profiles) shall remain in shared configuration libraries and be referenced by the Project Definition. Introduce `ProjectDefinitionResolver` as a common EKS pipeline module to construct an immutable `RuntimeProjectDefinition` for all runtime components. Enhance `SchemaLoader` to provide generic schema loading, caching, dependency resolution, and cross-schema validation while remaining pipeline-agnostic. Retire `eks_project_rules_config.json` by integrating its project-specific rules into the Project Definition. | 🔷 Planned | **T1.189–T1.197** | **Architecture revised. Project Definition is the SSOT for all project-specific configuration. `eks_project_rules_config.json` is retired and replaced by `ProjectDefinitionResolver` + `RuntimeProjectDefinition`.** |
310: 

(End of file - total 310 lines)
</content>
```

**Tool: read**

**Input:**
```json
{
  "filePath": "C:\\Users\\franklin.song\\Desktop\\DSAI\\Engineering-and-Design\\eks\\log\\phase1\\p1_task_log.md",
  "offset": 850
}
```

**Output:**
```
<path>C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\log\phase1\p1_task_log.md</path>
<type>file</type>
<content>
850: | T1.142 | [Schema] Migrate 15 `B-*` → `B-{cat}-S-{id4}` with single-letter categories | Map CLI→C, PATH→H, REG→R, DEF→D, FALL→A, ENV→E, SCH→K, PAR→M, BOOT→B, CTX→X, UNK→U. Update codes and sequential IDs. | Config | ✅ COMPLETE | I112 | — | `eks/config/schemas/eks_error_config.json` | T1.140 | — | — | §65 |
851: | T1.143 | [Schema] Update `system_format` metadata + remove hybrid ranges | Remove `P1-SETUP-{type}{id}` and `P1-BOOT-{reason}` from `system_format`. Remove `setup_validation` and `bootstrap_p1` ranges. | Config | ✅ COMPLETE | I112 | — | `eks/config/schemas/eks_error_config.json` | T1.140–T1.142 | — | — | §65 |
852: | T1.144 | [Schema] Update `eks_error_setup_schema.json` ranges | Remove `setup_validation` and `bootstrap_p1` from `system_error_ranges.properties`. | Schema | ✅ COMPLETE | I112 | — | `eks/config/schemas/eks_error_setup_schema.json` | T1.143 | — | — | §65 |
853: | T1.145 | [Code] Update EKS call sites with new codes | Update `bootstrap.py` (40× `P1-BOOT-*` → `S-B-S-06xx`). Update `setup_validator.py` (18× `P1-SETUP-*` → `S-E`/`S-F`/`S-R`). | Code | ✅ COMPLETE | I112 | — | `eks/engine/core/bootstrap.py`, `eks/engine/core/setup_validator.py` | T1.140–T1.144 | — | — | §65 |
854: | T1.146 | [Docs] Update Appendix D — remove hybrid formats, document new codes | Remove `P1-SETUP-{type}{id}` and `P1-BOOT-{reason}` from D2 format table. Update D3/D4 ranges. | Docs | ✅ COMPLETE | I112 | — | `eks/workplan/appendix_d_pipeline_messages_errors.md` | T1.145 | — | — | §65 |
855: | T1.147 | [Testing] Full suite + grep for stale non-standard code references | Run project-wide grep for `P1-BOOT` and `P1-SETUP` — zero matches. Verify tests pass. | Test | ✅ COMPLETE | I112 | — | — | T1.145–T1.146 | — | — | §65 |
856: 
857: ### §66 — Pipeline Batch Health Scoring (I248)
858: 
859: | ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
860: | :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
861: | T1.148 | [Code] Wire `score_batch()` into `run_phase_b()` | After processing loop in `run_phase_b()`, query `registry.list_documents()` and call `self.scorer.score_batch(all_docs)`. Append `avg_document_health` and full `batch_health` dict to Phase B summary. Wrap in try/except with logger.warning on failure. | `eks/engine/core/pipeline_orchestrator.py` | ✅ COMPLETE | I248 | — | `eks/engine/core/pipeline_orchestrator.py` | — | — | — | §66 |
862: 
863: ### §67 — Document Type Schema Extraction (I250)
864: 
865: | ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
866: | :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
867: | T1.149 | [Schema] Extract document type registry to standalone schema | Follow facility/discipline/department pattern. Add `document_type_entry_def` to `eks_doc_base_schema.json`. Create `eks_document_type_schema.json` with 15 valid codes plus metadata (label, ontology_class, description, expected_file_types). Update `eks_doc_setup_schema.json` to validate against new definition. | Config + Schema | ✅ COMPLETE | I250 | — | `eks/config/schemas/eks_doc_base_schema.json`, `eks/config/schemas/eks_document_type_schema.json`, `eks/config/schemas/eks_doc_config.json`, `eks/config/schemas/eks_doc_setup_schema.json` | — | — | — | §67 |
868: 
869: ### §68 — Document Type Schema Pipeline Wiring (I251)
870: 
871: | ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
872: | :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
873: | T1.150 | [Schema] Register `eks_document_type_schema.json` in SchemaLoader load chain | Add the new schema file to `SchemaLoader.load_all()` so `$ref` resolution works. Register with `Registry().with_resources()`. | Schema | ✅ COMPLETE | I251 | — | `eks/engine/core/schema_loader.py` | T1.149 | — | — | §68 |
874: | T1.151 | [Config] Update `eks_doc_setup_schema.json` to `$ref` new definition | Replace inline item properties with `$ref` to `document_type_entry_def` from the base schema. | Config | ✅ COMPLETE | I251 | — | `eks/config/schemas/eks_doc_setup_schema.json` | T1.149 | — | — | §68 |
875: | T1.152 | [Code] Update FilenameParser `_doc_type_codes` to use schema-sourced registry | Currently `_doc_type_codes` is built from the inline config array. After I250, this will come from schema `$ref`. Ensure `FilenameParser._precompile_validators()` reads from the schema-resolved config. | Code | ✅ COMPLETE | I251 | — | `eks/engine/core/filename_parser.py` | T1.150–T1.151 | — | — | §68 |
876: 
877: ### §69 — Phase B Identity Field Write-Back (I252)
878: 
879: | ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
880: | :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
881: | T1.153 | [Code] Extract project_number, area, discipline, document_type from PDF parser metadata in Phase B | PDFParser returns `parse_result["metadata"]` which may contain cover sheet fields. Extract identity fields from this dict and pass them to `_update_doc_status()` via `extra_properties`. | Code | ✅ COMPLETE | I252 | — | `eks/engine/core/pipeline_orchestrator.py` | — | — | — | §69 |
882: | T1.154 | [Code] Add identity fields to `_update_doc_status()` extra_properties pass-through | Ensure `project_number`, `area`, `discipline`, `document_type` are included in the `extra_properties` dict passed to `registry.update_document_status()`. Verify COLUMN_ALLOWLIST in registry.py includes these four fields. | Code | ✅ COMPLETE | I252 | — | `eks/engine/core/pipeline_orchestrator.py`, `eks/engine/core/registry.py` | T1.153 | — | — | §69 |
883: | T1.155 | [Code] Add `document_type` priority chain: cover sheet > filename > extension inference | `_infer_doc_type()` previously unconditionally overrode filename-derived document_type. Made conditional. Phase B write-back uses priority: parser metadata > Phase A filename value > UNKNOWN. | Code | ✅ COMPLETE | I252 | — | `eks/engine/core/pipeline_orchestrator.py`, `eks/engine/core/file_scanner.py` | T1.153–T1.154 | — | — | §69 |
884: 
885: ### §70 — Path Doubling Fix (I254)
886: 
887: | ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
888: | :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
889: | T1.156 | [Fix] Strip `eks_root` prefix from relative CLI `--data-dir` in bootstrap path resolution | In `bootstrap.py:_bootstrap_params()` line 488, before combining `self.project_root / eks_root / cli_path`, strip the `eks_root` prefix from `cli_path` if present. E.g., `"eks/data"` → strip `"eks/"` → `"data"` → resolves to `.../eks/data` (correct). Absolute paths unchanged. 3 regression tests added (test_path_doubling_prevents_eks_eks_data_dir, test_path_doubling_handles_bare_data, test_path_doubling_handles_absolute_path). bootstrap.py rev 0.4→0.5. | Code | ✅ COMPLETE | I254 | TL019 | `eks/engine/core/bootstrap.py` | — | — | — | §70 |
890: 
891: ### §71 — FilenameParser Auto-Pattern Detection (I255)
892: 
893: | ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
894: | :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
895: | T1.157 | [Code] Make FilenameParser auto-detect project code pattern per filename — try all registered project codes, use first match, fall back to `"*"` (0 segments) | Removed `project_code` param from `FilenameParser.__init__()`. Added `project_code_registry: Optional[List[str]]` param. New `_detect_pattern(stem)` method: splits stem by common separator, iterates all registered codes, checks first segment against each code — uses matching pattern or returns `"*"` fallback. Called per-filename in `parse()`. Both call sites updated: `FileScanner` and `PipelineOrchestrator` derive `project_code_registry` from `filename_patterns` keys (excluding `"*"`). Also fixed pre-existing finalization bug in `parse()` where 0-segment `"*"` pattern resulted in `parse_status="ok"` instead of `"unresolvable"`. `filename_parser.py` rev 1.0.0→1.1.0, `file_scanner.py` rev 1.5.0→1.6.0, `pipeline_orchestrator.py` rev 0.7→0.8. | Code | ✅ COMPLETE | I255 | TL020 | `eks/engine/core/filename_parser.py`, `eks/engine/core/file_scanner.py`, `eks/engine/core/pipeline_orchestrator.py` | — | — | — | §71 |
896: | T1.158 | [Testing] Add regression tests for FilenameParser auto-pattern-detection: matching pattern case, non-matching pattern → `"*"` fallback | Added 2 tests in `eks/test/test_phase1.py`: (1) `test_filename_parser_auto_detects_131101_pattern` — supply `project_code_registry=["131101"]`, parse `"131101-AREA-SPC-CV-0001_rev01.pdf"`, assert `project_number="131101"`, `area="AREA"`, `document_type="SPC"`, `discipline="CV"`, `sequence_number="0001"`, `document_number="131101-AREA-SPC-CV-0001"`, `revision="01"`, `parse_status="ok"`. (2) `test_filename_parser_falls_back_to_star_pattern` — parse `"random_name.pdf"`, assert all 5 identity fields are `None`, `document_number="random_name"` (full_stem fallback), `revision="00"`, `parse_status="unresolvable"`. Both pass. | Testing | ✅ COMPLETE | I255 | TL020 | `eks/test/test_phase1.py` | T1.157 | — | — | §71 |
897: 
898: ### §72 — project_title Population from project_number (I256)
899: 
900: | ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
901: | :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
902: | T1.159 | [Schema] Register eks_project_code_schema.json in SchemaLoader._STEM_TO_ATTR | Option A implemented: Added `"eks_project_code_schema": "project_code_schema"` to `_STEM_TO_ATTR` in `schema_loader.py`. Added `self.project_code_schema` attribute. In post-load, injects `project_code_titles` dict into `doc_config` from `projects[].code→description`. Updated `eks_doc_setup_schema.json` `additionalProperties` to allow `project_code_titles`. | Schema | ✅ COMPLETE | I256 | U223 | `eks/engine/core/schema_loader.py`, `eks/config/schemas/eks_doc_setup_schema.json` | — | TL021 | U223 | §72 |
903: | T1.160 | [Code] Accept project_code→title mapping in FilenameParser; populate project_title in FilenameParseResult when project_number extracted | Added `project_title: Optional[str]` to `FilenameParseResult`. Added to `to_metadata_dict()`. Added `project_code_titles: Optional[Dict[str, str]]` to `__init__`. In `_extract_segments()`, after `setattr(result, "project_number", raw_value)`, looks up title from map. Call sites (`FileScanner`, `PipelineOrchestrator`) pass `project_code_titles` from `doc_config`. `parse_filename()` wrapper updated. | Code | ✅ COMPLETE | I256 | U224, U225, U226 | `eks/engine/core/filename_parser.py`, `eks/engine/core/file_scanner.py`, `eks/engine/core/pipeline_orchestrator.py` | T1.159 | TL021 | U224–U226 | §72 |
904: | T1.161 | [Code] Extend I252 Phase B identity write-back to include cover-sheet-derived project_title | Extended I252 block with 3-tier `project_title` priority: (1) cover sheet metadata → (2) code→title lookup from `project_code_titles` → (3) Phase A existing value. Added after existing `for id_field in ...` loop. | Code | ✅ COMPLETE | I256 | U226 | `eks/engine/core/pipeline_orchestrator.py` | T1.159 | — | U226 | §72 |
905: | T1.162 | [Testing] Add regression test: filename with known project_code → project_title populated correctly | Added `test_filename_parser_populates_project_title` in `test_phase1.py`. Three sub-tests: (1) `131101`→`WSD11 — Project Specifications`, (2) `999999`→`Unknown Project`, (3) fallback→`None`. All pass. | Testing | ✅ COMPLETE | I256 | U227 | `eks/test/test_phase1.py` | T1.160 | TL021 | U227 | §72 |
906: 
907: ### §73 — Silent doc_config Validation Failure (I257)
908: 
909: | ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
910: | :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
911: | T1.163 | [Code] Replace silent `except Exception: pass` with logged exception in `_bootstrap_registry()` using S-B-S-0609 | In `bootstrap.py:305`, change `except Exception: pass` to `except Exception as exc:` with `self._log(f"doc_config schema validation failed — using empty defaults: {exc}", level=2)`. Error code `S-B-S-0609` `BOOT_CONFIG_DEGRADED` (WARNING, `stops_pipeline: false`). Fail-fast does NOT apply — inner try/except is intentionally non-fatal; outer P3 handler catches fatal errors. Pipeline continues with `doc_config = {}`. | Code | ✅ COMPLETE | I257 | U228 | `eks/engine/core/bootstrap.py`, `eks/config/schemas/eks_error_config.json` | T1.165 | TL022 | U228 | §73 |
912: | T1.164 | [Testing] Add test verifying doc_config load failure produces WARNING entry with S-B-S-0609 | Add test case that injects a broken schema/config pair into a `SchemaLoader` instance, triggers `_bootstrap_registry()` path, and asserts `debug_object["logs"]` contains a WARNING-level entry mentioning the schema error and code S-B-S-0609. Implemented as `TestBootstrapDegradation.test_257_doc_config_failure_logged`. | Testing | ✅ COMPLETE | I257 | U228 | `eks/test/test_phase1.py` | T1.163 | TL022 | U228 | §73 |
913: 
914: ### §74 — Six Remaining Silent Bootstrap Swallows (I258)
915: 
916: | ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
917: | :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
918: | T1.165 | [Schema] Register 7 new error codes S-B-S-0609–S-B-S-0615 in eks_error_config.json (I257 + I258) | All WARNING severity, `stops_pipeline: false`. **S-B-S-0609** `BOOT_CONFIG_DEGRADED` — P3 doc_config validation failed (I257). **S-B-S-0610** `BOOT_CONFIGREGISTRY_FAILED` — ConfigRegistry init failed (I258#1). **S-B-S-0611** `BOOT_SCCONFIG_DEGRADED` — P7 doc_config load failed (I258#2). **S-B-S-0612** `BOOT_ERRORMGR_TODICT_FAILED` — ErrorManager in `to_dict()` (I258#3). **S-B-S-0613** `BOOT_MSGMGR_TODICT_FAILED` — MessageManager in `to_dict()` (I258#4). **S-B-S-0614** `BOOT_ERRORMGR_CTX_FAILED` — ErrorManager in `to_pipeline_context()` (I258#5). **S-B-S-0615** `BOOT_MSGMGR_CTX_FAILED` — MessageManager in `to_pipeline_context()` (I258#6). Update bootstrap range: end_id `S-B-S-0608`→`S-B-S-0615`, count `8`→`15`. Bump version to 1.5.0. | Schema | ✅ COMPLETE | I257, I258 | U228 | `eks/config/schemas/eks_error_config.json` | — | TL022 | U228 | §74 |
919: | T1.166 | [Code] Fix ConfigRegistry silent swallow in _eks_config_loader() (#1) using S-B-S-0610 | `bootstrap.py:128` — change `except Exception: pass` to `except Exception as exc: self._log(f"ConfigRegistry init failed, falling back to SchemaLoader: {exc}", level=2)` referencing code `S-B-S-0610`. Preserves graceful fallback to SchemaLoader. Fail-fast does NOT apply — inner try/except is non-fatal; phase outer handler catches fatals separately. | Code | ✅ COMPLETE | I258 | U228 | `eks/engine/core/bootstrap.py` | T1.165 | TL022 | U228 | §74 |
920: | T1.167 | [Code] Fix P7 SchemaLoader silent swallow in _bootstrap_schema() (#2) using S-B-S-0611 | `bootstrap.py:365` — same pattern as T1.163 (I257) but for the P7 duplicate site. Replace `except Exception: pass` with `self._log(f"Schema phase doc_config load failed — using empty defaults: {exc}", level=2)` using code `S-B-S-0611`. Non-fatal — SchemaToDDL pre-flight is skipped but schema validation proceeds. | Code | ✅ COMPLETE | I258 | U228 | `eks/engine/core/bootstrap.py` | T1.165 | TL022 | U228 | §74 |
921: | T1.168 | [Code] Fix ErrorManager/MessageManager silent swallows in to_dict() (#3, #4) using S-B-S-0612, S-B-S-0613 | `bootstrap.py:568,576` — replace both `except Exception: pass` with `self._log(f"ErrorManager/MessageManager lazy-init failed in to_dict(): {exc}", level=2)` using codes `S-B-S-0612`, `S-B-S-0613`. Both remain `None` — existing callers check for None and degrade gracefully (bare print/log). | Code | ✅ COMPLETE | I258 | U228 | `eks/engine/core/bootstrap.py` | T1.165 | TL022 | U228 | §74 |
922: | T1.169 | [Code] Fix ErrorManager/MessageManager silent swallows in to_pipeline_context() (#5, #6) using S-B-S-0614, S-B-S-0615 | `bootstrap.py:650,659` — same pattern as T1.168 using codes `S-B-S-0614`, `S-B-S-0615`. Pipeline context passes None managers; consumers degrade gracefully. | Code | ✅ COMPLETE | I258 | U228 | `eks/engine/core/bootstrap.py` | T1.165 | TL022 | U228 | §74 |
923: | T1.170 | [Testing] Add regression tests for all 7 logged bootstrap degradation paths (I257 + I258) | Add test cases to `test_phase1.py` that: (1) inject a broken schema/config pair triggering S-B-S-0609 (via I257 T1.163), (2) inject a broken config/registry triggering S-B-S-0610, (3) inject a broken schema for P7 triggering S-B-S-0611, (4–5) mock ErrorManager/MessageManager in to_dict() to raise and assert S-B-S-0612/S-B-S-0613 in logs, (6–7) same for to_pipeline_context() with S-B-S-0614/S-B-S-0615. Each test asserts the WARNING entry exists in `debug_object["logs"]` with the correct error code or descriptive text. Implemented as `class TestBootstrapDegradation` with 5 test methods covering all 7 paths. 105/106 pass (1 pre-existing unrelated failure). | Testing | ✅ COMPLETE | I257, I258 | U228 | `eks/test/test_phase1.py` | T1.163, T1.166–T1.169 | TL022 | U228 | §74 |
924: 
925: ### §75 — Tier 3 Discovery, Bootstrap Schema Strategy & 4-Stage Lifecycle (I259–I263)
926: 
927: | ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
928: | :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
929: | T1.171 | [Code] Add discover_schema_files_tier3() to common/library/loader/schema_discovery.py (I259) | Scans _search_dirs for known _STEM_TO_ATTR stems not matched by glob patterns. Returns dict of newly discovered entries. Exported from __init__.py. | Code | ✅ COMPLETE | I259 | 2026-07-29 | common/library/loader/schema_discovery.py, common/library/loader/__init__.py | — | TL024 | U230 | §75 |
930: | T1.172 | [Code] Wire Tier 3 fallback in SchemaLoader.load_all() → _discover() (I259) | Call discover_schema_files_tier3() inside _discover() with all _STEM_TO_ATTR keys and _search_dirs; merge results into registry before _load() iterates. | Code | ✅ COMPLETE | I259 | 2026-07-29 | eks/engine/core/schema_loader.py | T1.171 | TL024 | U230 | §75 |
931: | T1.173 | [Testing] Add Tier 3 fallback regression test (I259) | Test discover_schema_files_tier3() finds eks_project_code_schema.json when present in _search_dirs but not in existing registry. | Testing | ✅ COMPLETE | I259 | 2026-07-29 | eks/test/test_schema_discovery.py | T1.171 | TL023 | U230 | §75 |
932: | T1.174 | [Schema] Add 3 missing _STEM_TO_ATTR entries — department, discipline, facility (I260) | Add eks_department_schema, eks_discipline_schema, eks_facility_schema to _STEM_TO_ATTR mapping; add self.department_schema, self.discipline_schema, self.facility_schema to __init__. | Schema | ✅ COMPLETE | I260 | 2026-07-29 | eks/engine/core/schema_loader.py | — | TL024 | U230 | §75 |
933: | T1.175 | [Code] Implement _bootstrap_schema() with schema_loader strategy hook in BootstrapManager (I261) | Add SchemaLoader callable type; accept in __init__; invoke in _bootstrap_schema() during P7 phase. Raise S-B-S-0616 if empty, S-B-S-0617 on exception. | Code | ✅ COMPLETE | I261 | 2026-07-29 | common/library/bootstrap/manager.py | — | TL024 | U230 | §75 |
934: | T1.176 | [Schema] Register S-B-S-0616 (empty discovery) and S-B-S-0617 (cross-ref failure) in error config (I261) | Add both codes to eks_error_config.json system_errors; update bootstrap range count 15→18, end_id 0615→0618; bump version to 1.6.0. | Schema | ✅ COMPLETE | I261 | 2026-07-29 | eks/config/schemas/eks_error_config.json | — | TL024 | U230 | §75 |
935: | T1.177 | [Code] Add validate_schema_conformance() to ValidationManager (I261) | New method using jsonschema.validate() with optional $ref resolution via base_schemas dict. Returns ValidationItem PASS/FAIL. | Code | ✅ COMPLETE | I261 | 2026-07-29 | common/library/utility/validation/manager.py | — | TL024 | U230 | §75 |
936: | T1.178 | [Code] Extract build_uri_registry() to common/library/loader/ref_resolver.py (I262) | New file with build_uri_registry() function scanning directories for $id declarations with duplicate detection. Exported from __init__.py. | Code | ✅ COMPLETE | I262 | 2026-07-29 | common/library/loader/ref_resolver.py, common/library/loader/__init__.py | — | TL024 | U230 | §75 |
937: | T1.179 | [Code] Add validate_schema_conformance() to ValidationManager (I263) | Same as T1.177 — shared with I261. Added conformance validation with jsonschema. | Code | ✅ COMPLETE | I263 | 2026-07-29 | common/library/utility/validation/manager.py | — | TL024 | U230 | §75 |
938: | T1.180 | [Code] Refactor SchemaLoader.load_all() into 4 stage methods (I263) | Split into _discover() (bootstrap + Tier 1-3 discovery), _load() (schema loading from registry), _validate() (all validation calls), _extract() (post-load indexes). load_all() calls in sequence. | Code | ✅ COMPLETE | I263 | 2026-07-29 | eks/engine/core/schema_loader.py | — | TL024 | U230 | §75 |
939: | T1.181 | [Schema] Register S-B-S-0618 (conformance failure) in error config (I263) | Add code to eks_error_config.json v1.6.0. FATAL, stops_pipeline: true. | Schema | ✅ COMPLETE | I263 | 2026-07-29 | eks/config/schemas/eks_error_config.json | — | TL024 | U230 | §75 |
940: 
941: ## 39. Column Processing Metadata — Schema-Driven Registry Column Definitions (I264)
942: 
943: | ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
944: | :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
945: | T1.182 | [Schema] Add 6 column-processing definitions to eks_doc_base_schema.json | Add column_type_enum (12 role types), processing_phase_enum (A/B/C/D/bootstrap), calculation_strategy_def (priority_chain/filename_segment/file_property/parser_metadata/cover_page_element/code_to_title_lookup/health_score/auto_increment), handler_def (which module handles this calculation type), validation_rule_def (pattern/min_length/enum_reference/schema_reference_check), column_processing_entry_def (full entry schema referencing all above). | Schema | ✅ COMPLETE | I264 | 2026-07-29 | eks/config/schemas/eks_doc_base_schema.json | — | — | U232 | §75 |
946: | T1.183 | [Schema] Add column_processing property to eks_doc_setup_schema.json | New property: "column_processing" — object with additionalProperties pointing to column_processing_entry_def. propertyNames: ^[a-z_]+$. DCC-aligned key-as-name pattern per T1.184 review. | Schema | ✅ COMPLETE | I264 | 2026-07-29 | eks/config/schemas/eks_doc_setup_schema.json | T1.182 | — | U232 | §75 |
947: | T1.184 | [Config] Add column_processing entries for all 42 document registry columns to eks_doc_config.json | One entry per column in documents table, keyed by column name (DCC-aligned object pattern). Each: column_type, is_calculated, calculation, schema_ref, validation, processing_phase, required, description. 42 entries: 9 Phase A, 33 Phase B. | Config | ✅ COMPLETE | I264 | 2026-07-29 | eks/config/schemas/eks_doc_config.json | T1.183 | — | U232 | §75 |
948: | T1.185 | [Code] Build BaseColumnProcessor in common/library/ + EKSColumnProcessor | New package common/library/column_processor/ with HandlerRegistry + BaseColumnProcessor (generic phase dispatch). New class eks/engine/core/column_processor.py — EKSColumnProcessor(BaseColumnProcessor) with 9 pre-registered handler stubs: priority_chain, filename_segment, file_property, parser_metadata, cover_page_element, code_to_title_lookup, health_score, auto_increment, existing_record. Factory method from_doc_config(). | Code | ✅ COMPLETE | I264 | 2026-07-29 | common/library/column_processor/{__init__.py,base.py,registry.py}, eks/engine/core/column_processor.py | T1.184 | — | U233 | §75 |
949: | T1.186 | [Code] Wire EKSColumnProcessor handler stubs with real logic | Enhance 9 handler functions in eks/engine/core/column_processor.py: priority_chain (resolve project_title/document_title/total_sheets from cover_page → parser_metadata → code_to_title → existing_record), filename_segment (delegate to already-parsed data dict from Phase A FilenameParser), file_property (lookup from context.file_properties), parser_metadata (lookup from context.metadata), cover_page_element (extract field from cover_page content + asset_tags comma-split), code_to_title_lookup (project_code_titles registry), health_score (context.score), auto_increment (UUID), existing_record (preserve from data dict). | Code | ✅ COMPLETE | I264 | 2026-07-29 | eks/engine/core/column_processor.py | T1.185 | TL025 | U233 | §75 |
950: | T1.187 | [Code] Wire ColumnProcessor into PipelineOrchestrator phases | Replace hardcoded blocks in run_phase_a (filename identity fields), run_phase_b (project_title chain, identity write-back, file properties, elements, health score), and run_phase_c (review flags) with a single ColumnProcessor.process(phase) call per phase. Fix bare `doc_config` bug in _process_file. Fix `position` schema type (int→int null for separator-based revision). Fix `min_length` schema minimum (1→0 for zero-threshold). | Code | ✅ COMPLETE | I264 | 2026-07-29 | eks/engine/core/pipeline_orchestrator.py, eks/config/schemas/eks_doc_base_schema.json | T1.186 | TL026 | U234 | §75 |
951: | T1.188 | [Testing] Add regression tests for ColumnProcessor central orchestrator | Tests: (a) ColumnProcessor dispatches each calculation.type to correct handler, (b) priority_chain resolves project_title correctly across all 4 sources, (c) validation rules fire on mismatch, (d) fallback to leave_null works, (e) 42 column entries validate against setup schema, (f) end-to-end: ColumnProcessor.process("B") produces expected output. | Testing | ✅ COMPLETE | I264 | 2026-07-29 | eks/test/test_column_processing.py (new) | T1.187 | TL027 | U235 | §75 |

(End of file - total 951 lines)
</content>
```

---

## Assistant (Build · DeepSeek V4 Flash Free · 14.3s)

_Thinking:_

Now I have a comprehensive picture. Let me also read the rest of the task log to check if T1.189 (the one associated with I265) has been added.

Let me also check the existing pipeline design more directly by looking at the current state of key code files.

I have enough information now. Let me compile my findings and present them:

## I265 - Project Definition Schema Refactoring

Found in `eks/log/phase1/p1_issue_log.md:309`:
- **ID**: 265 (note: formatted as `**265**` not `I265`)
- **Date**: 2026-07-30
- **Phase**: Phase 1
- **Severity**: 🟡 Medium
- **Status**: 🔷 Planned
- **Tasks**: T1.189–T1.197
- **Description**: Project-specific configuration is distributed across multiple schemas. Need to create `eks_project_definition_schema.json` as SSOT for all project-specific config. Add `ProjectDefinitionResolver` to construct immutable `RuntimeProjectDefinition`. Retire `eks_project_rules_config.json`.

## Related Workplan: `eks/workplan/appendix_l_project_definition.md`

Key points from this workplan:
- Project Definition schema will consolidate: project_info, engineering, document_processing, asset_processing, ontology, pipeline, retrieval, security, integration
- Reusable config libraries will hold: filename_patterns, parser_profiles, OCR profiles, document types, ontology profiles, asset profiles, retrieval profiles
- RuntimeProjectDefinition will be immutable after construction
- Current architecture has project config spread across multiple files

## Task Log for I265 (T1.189–T1.197)
All tasks are **🔷 Planned**:
- T1.189: Design Project Definition Architecture
- T1.190: Implement Project Definition Schema
- T1.191: Refactor Reusable Configuration Libraries
- T1.192: Enhance SchemaLoader
- T1.193: Implement ProjectDefinitionResolver
- T1.194: Refactor EKS Runtime Modules
- T1.195: Implement Configuration Validation
- T1.196: Migrate Existing Configuration
- T1.197: Documentation & Regression Testing

## Current EKS Pipeline Design Summary
From what I've read across the codebase and docs:

1. **Schema-driven pipeline**: EKS follows a 3-layer schema pattern (base/setup/config)
2. **Pipeline phases**: Phase A (file discovery + registration), Phase B (parse, detect structure, score health), Phase C (manual review)
3. **Key modules**: FileScanner, ParserRouter, PipelineOrchestrator, DocumentRegistry, HealthScorer, RevisionManager, ManualReviewManager
4. **Datastore**: DuckDB-backed document registry
5. **Recent work**: I255 (auto-pattern detection for FilenameParser), I256 (project_title population), I264 (ColumnProcessor metadata)

Now let me think about gaps between I265's proposed design and the current state:

### Potential Gaps:

1. **Project Definition scope vs existing config**: I265 proposes consolidating all project-specific config into a single `eks_project_definition_schema.json`. Currently, project-specific config is spread across `eks_doc_config.json` (filename_patterns, revision_validation), `eks_config.json` (project rules), and `eks_project_rules_config.json`.

2. **FilenameParser auto-detection already implemented**: I255 already solved the project_code auto-detection problem. The `FilenameParser` now auto-detects patterns. I265's ProjectDefinitionResolver would need to integrate with this.

3. **Existing ColumnProcessor already handles 42 columns**: I264 has already implemented the ColumnProcessor. Any new Project Definition schema would need to align with column_processing definitions.

4. **SchemaLoader already has 4-stage lifecycle**: I261/I263 already refactored SchemaLoader with 4 stages (discover/load/validate/extract). I265's T1.192 (enhance SchemaLoader) may overlap.

5. **eks_project_rules_config.json status**: Already exists as a config fragment. I265 wants to retire it. The retirement plan needs cross-referencing with all consumers.

6. **Migration scope**: T1.196 describes migrating all existing project-specific config into the new schema. This is a significant refactoring task that touches many files.

7. **RuntimeProjectDefinition consumers**: T1.194 plans to update FileScanner, FilenameParser, RevisionValidator, Asset Loader, Pipeline, Retriever. This could be a large breaking change if not careful.

8. **Workplan appendix_l status**: It's a proposed workplan but not yet linked from the main phase_1_foundation_workplan.md. The issue I265 is 🔷 Planned, meaning it hasn't been approved yet.

Let me present this analysis to the user.

Based on my comprehensive analysis, here is the full picture of **I265**, its pipeline context, and the gaps I see.

---

## I265 — Project Definition Schema Refactoring

**Status**: 🔷 Planned (T1.189–T1.197 all planned)  
**File**: `eks/log/phase1/p1_issue_log.md:309`  
**Workplan**: `eks/workplan/appendix_l_project_definition.md`

**Goal**: Consolidate all project-specific config scattered across multiple schemas into a single `eks_project_definition_schema.json`, with a `ProjectDefinitionResolver` producing an immutable `RuntimeProjectDefinition` for all pipeline components.

---

## Current EKS Pipeline Design (relevant context)

| Area | Current State | Key Files |
|------|--------------|-----------|
| Schema pattern | 3-layer (base/setup/config) across 6 sets + 4 fragments | `eks/config/schemas/*.json` |
| Pipeline phases | A (discovery+register) → B (parse+score) → C (review) | `pipeline_orchestrator.py` |
| Filename parsing | Auto-detection per file (I255) — tries registered project codes | `filename_parser.py` |
| Column processing | Schema-driven ColumnProcessor with 42 entries (I264) | `column_processor.py` |
| SchemaLoader | 4-stage lifecycle: discover/load/validate/extract (I261/I263) | `schema_loader.py` |
| Config distribution | `eks_doc_config.json`, `eks_config.json`, `eks_project_rules_config.json`, fragment schemas | Multiple files |

---

## Gaps Identified Between I265 and Current Design

| # | Gap | Detail | Severity |
|:-:|------|--------|:--------:|
| 1 | **Overlap with existing SSOT work** | I261/I263 already refactored SchemaLoader into 4 stages. I255 already solved project_code auto-detection. I264 already added column_processing metadata. T1.192 (enhance SchemaLoader) and T1.194 (refactor modules) risk duplicating or conflicting with completed work. | 🟠 High |
| 2 | **No boundary definition with ColumnProcessor** | I265's `RuntimeProjectDefinition` would hold project config, but the ColumnProcessor (I264) already handles per-column processing metadata. Where does project definition end and column definition begin? Not defined. | 🟡 Medium |
| 3 | **`eks_project_rules_config.json` has existing consumers** | Grep shows this file is referenced via `$ref` in `eks_config.json`. T1.196 plans to retire it — all `$ref` consumers must be updated simultaneously. No migration strategy for backward compat. | 🟡 Medium |
| 4 | **appendix_l not linked from phase_1 workplan** | The workplan exists but is not listed in `phase_1_foundation_workplan.md` §10.1 Implementation Index. No cross-reference to I265 in the main workplan table. | 🟢 Low |
| 5 | **FilenameParser's `project_code_registry` vs Project Definition** | I255 added `project_code_registry` (list of codes) to FilenameParser. I265's ProjectDefinition would own project codes — but `FilenameParser` already derives them from `filename_patterns` keys. Dual SSOT risk. | 🟡 Medium |
| 6 | **No per-project override mechanism defined** | I255 uses auto-detection (try each code against filename). I265 proposes a resolver pattern. How the resolver selects the active project definition per file is unspecified. | 🟡 Medium |
| 7 | **Task table in appendix_l lacks issue cross-references** | T1.189–T1.197 have no Tests, UpdateRef, or Dependencies columns. Cannot trace which completed work (I255, I256, I259–I264) must be modified. | 🟢 Low |
| 8 | **Reusable config scope unclear** | Appendix §3 says "reusable" profiles stay in shared libs, but examples list `filename_patterns` and `parser_profiles` which currently ARE project-specific. The boundary between "reusable" and "project-specific" is not concretely defined. | 🟡 Medium |
| 9 | **No alignment with Appendix B registry columns** | The RuntimeProjectDefinition would be consumed by all pipeline modules, but Appendix B (document registry columns) and its 54 columns are not referenced in appendix_l. The mapping from project config → registry columns is missing. | 🟡 Medium |

---

## Summary

I265 is a well-scoped SSOT consolidation proposal, but **8 of 9 gaps** suggest it needs a pre-alignment review against recent I255–I264 work before implementation starts. The biggest risks are **(1) overlap with completed I261/I263 SchemaLoader refactoring** and **(2) undefined boundary with the I264 ColumnProcessor** — both of which would cause rework if not addressed in the workplan.

Would you like a workplan revision proposal that addresses these gaps?

---


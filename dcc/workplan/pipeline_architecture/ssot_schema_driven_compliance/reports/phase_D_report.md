# SSOT & Schema-Driven Compliance — Phase D Completion Report

**Workplan ID**: WP-SSOT-SD-001  
**Phase**: Phase D — Message Template Externalization  
**Status**: ✅ COMPLETE  
**Completion Date**: 2026-05-15  

---

## 1. Executive Summary

Phase D addressed a previously unaddressed violation category: error message text was hardcoded in 54 `detect_error()` calls across 9 detector files, while the `message` field in `data_error_config.json` existed as dead metadata — never read at runtime.

A `message_template` field was added to all 29 catalog entries. A new `BaseDetector._format_message(error_code, **kwargs)` method was added to `base.py` to read and format messages from the catalog. 54 of 63 hardcoded messages were replaced with catalog lookups. The remaining 9 (for 8 error codes not yet in catalog + 1 legacy string key) were deferred to Phase E.

---

## 2. Completed Tasks

| Task | Status | Details |
|:---|:---:|:---|
| D1 — Add `message_template` to all 29 catalog entries | ✅ | Each entry has a template with `{placeholder}` syntax matching the primary detector message |
| D2 — Add `_format_message()` to `BaseDetector` | ✅ | Method reads `message_template` from `error_catalog` in context; falls back to `message` field; catches `KeyError` gracefully |
| D3 — Update `anchor.py` (2 of 4 messages) | ✅ | P1-A-P-0101 messages replaced; P1-A-V-0102/0103 left as f-strings (not in catalog) |
| D4 — Update `identity.py` (1 of 5 messages) | ✅ | P2-I-V-0204 message replaced; P2-I-P-0201/0202, P2-I-V-0203 left as f-strings (not in catalog) |
| D5 — Update `row_validator.py` (9 of 10 messages) | ✅ | All standardized codes replaced; `GROUP_INCONSISTENT` legacy key left unchanged |
| D6 — Update `calculation.py` (9 messages) | ✅ | All C6xx messages replaced |
| D7 — Update `fill.py` (9 messages) | ✅ | All F4xx messages replaced |
| D8 — Update `input.py` (7 messages) | ✅ | All S1xx messages replaced |
| D9 — Update `logic.py` (5 messages) | ✅ | All L3xx messages replaced |
| D10 — Update `schema.py` (7 messages) | ✅ | All V5xx messages replaced |
| D11 — Update `validation.py` (5 of 7 messages) | ✅ | V5-I-V-0501/0502/0503/0504 replaced; V5-I-V-0505/0506 left as f-strings (not in catalog) |

---

## 3. Files Modified

| File | Change |
|:---|:---|
| `config/schemas/data_error_config.json` | Added `message_template` field to all 29 entries |
| `workflow/processor_engine/error_handling/detectors/base.py` | Added `_format_message(error_code, **kwargs)` method |
| `workflow/processor_engine/error_handling/detectors/anchor.py` | 2 messages replaced |
| `workflow/processor_engine/error_handling/detectors/identity.py` | 1 message replaced |
| `workflow/processor_engine/error_handling/detectors/row_validator.py` | 9 messages replaced |
| `workflow/processor_engine/error_handling/detectors/calculation.py` | 9 messages replaced |
| `workflow/processor_engine/error_handling/detectors/fill.py` | 9 messages replaced |
| `workflow/processor_engine/error_handling/detectors/input.py` | 7 messages replaced |
| `workflow/processor_engine/error_handling/detectors/logic.py` | 5 messages replaced |
| `workflow/processor_engine/error_handling/detectors/schema.py` | 7 messages replaced |
| `workflow/processor_engine/error_handling/detectors/validation.py` | 5 messages replaced |

---

## 4. Architecture

### `_format_message()` — Design

```python
def _format_message(self, error_code: str, **kwargs) -> str:
    catalog = self._context.get("error_catalog", {})
    entry = catalog.get(error_code, {})
    template = entry.get("message_template", entry.get("message", ""))
    if template and kwargs:
        try:
            return template.format(**kwargs)
        except KeyError:
            pass
    return template
```

**Pattern**: Parallel to `_get_severity()` — both read from the error catalog via context. Single-message codes use exact templates with kwargs. Multi-message codes use generic templates (later split in Phase E with affix notation).

### Template Convention

- Single-message codes: exact f-string template with `{placeholder}` for dynamic values  
  `"File not found: {file_path}"`

- Multi-message codes: canonical description from existing `message` field  
  `"Forward fill row jump exceeded limit"`

---

## 5. Verification

### Syntax Validation

All 11 modified files passed `ast.parse()` and `json.load()` validation:

```
  OK  config/schemas/data_error_config.json
  OK  base.py
  OK  anchor.py
  OK  identity.py
  OK  row_validator.py
  OK  calculation.py
  OK  fill.py
  OK  input.py
  OK  logic.py
  OK  schema.py
  OK  validation.py
```

### Success Criteria

| Criterion | Status |
|:---|:---:|
| All 29 catalog entries have `message_template` field | ✅ |
| `BaseDetector._format_message()` implemented | ✅ |
| 54 of 63 hardcoded messages replaced with catalog lookup | ✅ |
| All 11 modified files pass syntax check | ✅ |
| JSON schema file passes `json.load()` validation | ✅ |

---

## 6. Deferred Items (→ Phase E)

- 9 hardcoded messages remain for 8 error codes not yet in catalog (P2-I-P-0201, P2-I-P-0202, P2-I-V-0203, P1-A-V-0102, P1-A-V-0103, V5-I-V-0505, V5-I-V-0506) plus legacy `GROUP_INCONSISTENT` key
- 6 multi-semantic codes need affix splitting (P2-I-V-0204, S1-I-F-0805, F4-C-F-0401/0402/0403, C6-C-C-0605, L3-L-V-0303)
- Orphan code L3-L-V-0307 needs resolution

---

## 7. Lessons Learned

- The `message` field existed in the catalog for all 29 codes but was never connected to runtime code — it was dead metadata. This is a case of "schema has the data but code doesn't read it", the same anti-pattern that affected `severity` before Phase C.
- Multi-message codes (same code used for multiple detection scenarios) forced a choice between over-generic templates and per-variant templates. The affix split approach in Phase E is cleaner.

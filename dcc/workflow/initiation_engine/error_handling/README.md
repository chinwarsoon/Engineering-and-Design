# initiation_engine/error_handling

System-level error handling for the DCC pipeline.

## Purpose

Distinct from data error handling (`processor_engine/error_handling/`), this module handles failures in the pipeline's own execution: missing files, bad configuration, import errors, unexpected exceptions.

**Key property:** System errors are always visible — they bypass `DEBUG_LEVEL` and print to `stderr` at all verbose levels including `--verbose quiet`.

## Usage

```python
from initiation_engine.error_handling import system_error_print

# Fatal error — prints full block, pipeline should stop
system_error_print("S-F-S-0201", detail=str(path))

# Non-fatal warning — compact line, pipeline continues
system_error_print("S-A-S-0501", detail=str(exc), fatal=False)
```

## Error Code Format

```
S - <Category> - S - XXXX
│       │        │    │
│       │        │    └── 4-digit sequential ID
│       │        └─────── S = System (fixed)
│       └──────────────── E=Environment, F=File, C=Config, R=Runtime, A=AI
└──────────────────────── S = System namespace
```

## Files

| File | Purpose |
|------|---------|
| `system_errors.py` | `system_error_print()` implementation |
| `config/system_error_codes.json` | 20 error code definitions |
| `config/messages/system_en.json` | User-facing titles, descriptions, hints |

## Error Categories

| Category | Codes | Description |
|----------|-------|-------------|
| S-E | 0101–0104 | Environment & dependency failures |
| S-F | 0201–0205 | File & path errors |
| S-C | 0301–0305 | Configuration & parameter errors |
| S-R | 0401–0403 | Runtime & execution errors |
| S-A | 0501–0503 | AI ops warnings (non-fatal) |

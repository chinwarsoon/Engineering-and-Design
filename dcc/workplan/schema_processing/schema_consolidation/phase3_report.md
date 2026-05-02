# Phase 3 Report: Value File Restructuring

**Status:** ✅ COMPLETED  
**Date:** 2026-05-02  
**Duration:** ~15 minutes

---

## Summary

Successfully created new values-only file `dcc_global_parameters.json` with DCC processing parameters.

## Changes Made

### Created: dcc_global_parameters.json
**Location:** `dcc/config/schemas/dcc_global_parameters.json`

**Structure:**
- `$schema`: http://json-schema.org/draft-07/schema#
- `$id`: https://dcc-pipeline.internal/schemas/dcc_global_parameters
- `title`: DCC Global Processing Parameter Values
- `description`: Values-only file - definitions are in dcc_register_base#/definitions/dcc_parameter_entry
- `allOf`: References dcc_register_base

**Parameters (18 total):**
| Parameter | Type | Value |
|:---|:---|:---|
| `duration_is_working_day` | boolean | true |
| `start_col` | string | "P" |
| `end_col` | string | "AP" |
| `header_row_index` | integer | 4 |
| `first_review_duration` | integer | 20 |
| `second_review_duration` | integer | 14 |
| `resubmission_duration` | integer | 14 |
| `upload_sheet_name` | string | "Prolog Submittals " |
| `win_upload_file` | string | "data/Submittal and RFI Tracker Lists.xlsx" |
| `win_download_path` | string | "output" |
| `linux_upload_file` | string | "data/Submittal and RFI Tracker Lists.xlsx" |
| `linux_download_path` | string | "output" |
| `colab_upload_file` | string | "/content/sample_data/Submittal and RFI Tracker Lists.xlsx" |
| `colab_download_path` | string | "/content/output" |
| `upload_file_name` | string | "data/Submittal and RFI Tracker Lists.xlsx" |
| `download_file_path` | string | "output" |
| `pending_status` | object | {...} |
| `dynamic_column_creation` | object | {...} |

## Domain Separation

| Domain | Values File | Parameters |
|:---|:---|:---:|
| System | `project_config.json#/system_parameters` | 6 params (fail_fast, debug_dev_mode, is_colab, overwrite_existing_downloads, pc_name, progress_stage) |
| DCC | `dcc_global_parameters.json#/dcc_parameters` | 18 params (Excel paths, durations, etc.) |

## Next Phase

Phase 4: Config References Update

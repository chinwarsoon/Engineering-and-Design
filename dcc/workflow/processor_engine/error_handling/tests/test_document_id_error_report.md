# Document_ID Error Codes Test Report

**Test Date:** 2026-04-11T09:57:36.456580
**Data File:** /home/franklin/dsai/Engineering-and-Design/dcc/data/Submittal and RFI Tracker Lists.xlsx
**Schema File:** /home/franklin/dsai/Engineering-and-Design/dcc/config/schemas/dcc_register_enhanced.json

## Test Summary

- **Total Rows Analyzed:** 100
- **Total Errors Detected:** 209
- **Unique Error Codes:** 4

## Document_ID Pattern Analysis

- **Total Rows:** 100
- **Null Values:** 1
- **Empty Values:** 0
- **Unique IDs:** 99

### Pattern Distribution

- Standard (5-part): 99

### Invalid Format Samples

- No invalid formats detected

## Error Code Summary

| Error Code | Count | Description |
|------------|-------|-------------|
| P2-I-P-0201 | 2 | Document_ID uncertain/placeholder |
| P2-I-V-0204 | 198 | Document_ID format invalid |
| V5-I-V-0501 | 8 | Pattern mismatch |
| V5-I-V-0505 | 1 | Required field missing |

## Data Values with Error Codes

This section lists actual Document_ID values from the data that triggered error codes.

| Row | Document_ID Value | Error Code | Detector | Severity | Details |
|-----|-------------------|------------|----------|----------|---------|
| 85 | `NULL` | P2-I-P-0201 | IdentityDetector | CRITICAL | Document_ID uncertain at row 85: 'nan'... |
| 0 | `131242-WST00-PP-PM-0001-0` | P2-I-V-0204 | IdentityDetector | HIGH | Invalid Document_ID format: '131242-WST00-PP-PM-00... |
| 1 | `131242-WST00-PP-PM-0001-1` | P2-I-V-0204 | IdentityDetector | HIGH | Invalid Document_ID format: '131242-WST00-PP-PM-00... |
| 2 | `131242-WST00-PP-PC-0001-0` | P2-I-V-0204 | IdentityDetector | HIGH | Invalid Document_ID format: '131242-WST00-PP-PC-00... |
| 3 | `131242-WSW41-PP-PC-0001-1` | P2-I-V-0204 | IdentityDetector | HIGH | Invalid Document_ID format: '131242-WSW41-PP-PC-00... |
| 4 | `#000002.0_ Reply_2023 08 31-----` | P2-I-V-0204 | IdentityDetector | HIGH | Invalid Document_ID format: '#000002.0_ Reply_2023... |
| 5 | `131242-WSW41-PP-PC-0001-2` | P2-I-V-0204 | IdentityDetector | HIGH | Invalid Document_ID format: '131242-WSW41-PP-PC-00... |
| 6 | `#000002.0_ Reply_2023 09 13 (002)_CES...` | P2-I-V-0204 | IdentityDetector | HIGH | Invalid Document_ID format: '#000002.0_ Reply_2023... |
| 7 | `131242-WST00-PP-IM-0001-0` | P2-I-V-0204 | IdentityDetector | HIGH | Invalid Document_ID format: '131242-WST00-PP-IM-00... |
| 8 | `131242-WSW41-PP-IM-0001-1` | P2-I-V-0204 | IdentityDetector | HIGH | Invalid Document_ID format: '131242-WSW41-PP-IM-00... |
| 9 | `131242-WSW41-PP-IM-0001-2` | P2-I-V-0204 | IdentityDetector | HIGH | Invalid Document_ID format: '131242-WSW41-PP-IM-00... |
| 10 | `131242-WSW41-PP-IM-0001-3` | P2-I-V-0204 | IdentityDetector | HIGH | Invalid Document_ID format: '131242-WSW41-PP-IM-00... |
| 11 | `131242-WSW41-PP-IM-0001-4` | P2-I-V-0204 | IdentityDetector | HIGH | Invalid Document_ID format: '131242-WSW41-PP-IM-00... |
| 12 | `131242-WSW41-PP-IM-0001-5` | P2-I-V-0204 | IdentityDetector | HIGH | Invalid Document_ID format: '131242-WSW41-PP-IM-00... |
| 13 | `131242-WST00-PP-HS-0001-0` | P2-I-V-0204 | IdentityDetector | HIGH | Invalid Document_ID format: '131242-WST00-PP-HS-00... |
| 14 | `131242-WST00-PP-HS-0001-1` | P2-I-V-0204 | IdentityDetector | HIGH | Invalid Document_ID format: '131242-WST00-PP-HS-00... |
| 15 | `131242-WST00-PG-PC-0001-0` | P2-I-V-0204 | IdentityDetector | HIGH | Invalid Document_ID format: '131242-WST00-PG-PC-00... |
| 16 | `131242-WST00-PG-PC-0001-1` | P2-I-V-0204 | IdentityDetector | HIGH | Invalid Document_ID format: '131242-WST00-PG-PC-00... |
| 17 | `131242-WSW41-PG-PC-0001-2` | P2-I-V-0204 | IdentityDetector | HIGH | Invalid Document_ID format: '131242-WSW41-PG-PC-00... |
| 18 | `131242-WSW41-LT-PM-0003-0` | P2-I-V-0204 | IdentityDetector | HIGH | Invalid Document_ID format: '131242-WSW41-LT-PM-00... |
| 19 | `131242-WSW41-PG-PC-0001-3` | P2-I-V-0204 | IdentityDetector | HIGH | Invalid Document_ID format: '131242-WSW41-PG-PC-00... |
| 20 | `131242-WSW41-PG-PC-0001-4` | P2-I-V-0204 | IdentityDetector | HIGH | Invalid Document_ID format: '131242-WSW41-PG-PC-00... |
| 21 | `131242-WSW41-PG-PC-0001-5` | P2-I-V-0204 | IdentityDetector | HIGH | Invalid Document_ID format: '131242-WSW41-PG-PC-00... |
| 22 | `131242-WSW41-PG-PC-0001-5.1` | P2-I-V-0204 | IdentityDetector | HIGH | Invalid Document_ID format: '131242-WSW41-PG-PC-00... |
| 23 | `131242-WST00-VI-C-0001-0` | P2-I-V-0204 | IdentityDetector | HIGH | Invalid Document_ID format: '131242-WST00-VI-C-000... |
| 24 | `131242-WST00-VI-C-0001-1` | P2-I-V-0204 | IdentityDetector | HIGH | Invalid Document_ID format: '131242-WST00-VI-C-000... |
| 25 | `131242-WST00-PG-PC-0002-0` | P2-I-V-0204 | IdentityDetector | HIGH | Invalid Document_ID format: '131242-WST00-PG-PC-00... |
| 26 | `Reply to Comment Sheet_#000007-----` | P2-I-V-0204 | IdentityDetector | HIGH | Invalid Document_ID format: 'Reply to Comment Shee... |
| 27 | `131242-WST00-RG-Z-0001-0` | P2-I-V-0204 | IdentityDetector | HIGH | Invalid Document_ID format: '131242-WST00-RG-Z-000... |
| 28 | `131242-WST00-RG-Z-0001-1` | P2-I-V-0204 | IdentityDetector | HIGH | Invalid Document_ID format: '131242-WST00-RG-Z-000... |
| ... | ... | ... | ... | ... | _and 179 more_ |

## Detailed Error Log

### Error 1

- **Detector:** IdentityDetector
- **Error Code:** P2-I-P-0201
- **Message:** Document_ID uncertain at row 85: 'nan'
- **Row:** 85
- **Column:** Document_ID
- **Severity:** CRITICAL

### Error 2

- **Detector:** IdentityDetector
- **Error Code:** P2-I-V-0204
- **Message:** Invalid Document_ID format: '131242-WST00-PP-PM-0001-0'
- **Row:** 0
- **Column:** Document_ID
- **Severity:** HIGH

### Error 3

- **Detector:** IdentityDetector
- **Error Code:** P2-I-V-0204
- **Message:** Invalid Document_ID format: '131242-WST00-PP-PM-0001-1'
- **Row:** 1
- **Column:** Document_ID
- **Severity:** HIGH

### Error 4

- **Detector:** IdentityDetector
- **Error Code:** P2-I-V-0204
- **Message:** Invalid Document_ID format: '131242-WST00-PP-PC-0001-0'
- **Row:** 2
- **Column:** Document_ID
- **Severity:** HIGH

### Error 5

- **Detector:** IdentityDetector
- **Error Code:** P2-I-V-0204
- **Message:** Invalid Document_ID format: '131242-WSW41-PP-PC-0001-1'
- **Row:** 3
- **Column:** Document_ID
- **Severity:** HIGH

### Error 6

- **Detector:** IdentityDetector
- **Error Code:** P2-I-V-0204
- **Message:** Invalid Document_ID format: '#000002.0_ Reply_2023 08 31-----'
- **Row:** 4
- **Column:** Document_ID
- **Severity:** HIGH

### Error 7

- **Detector:** IdentityDetector
- **Error Code:** P2-I-V-0204
- **Message:** Invalid Document_ID format: '131242-WSW41-PP-PC-0001-2'
- **Row:** 5
- **Column:** Document_ID
- **Severity:** HIGH

### Error 8

- **Detector:** IdentityDetector
- **Error Code:** P2-I-V-0204
- **Message:** Invalid Document_ID format: '#000002.0_ Reply_2023 09 13 (002)_CES reply_20231025-----'
- **Row:** 6
- **Column:** Document_ID
- **Severity:** HIGH

### Error 9

- **Detector:** IdentityDetector
- **Error Code:** P2-I-V-0204
- **Message:** Invalid Document_ID format: '131242-WST00-PP-IM-0001-0'
- **Row:** 7
- **Column:** Document_ID
- **Severity:** HIGH

### Error 10

- **Detector:** IdentityDetector
- **Error Code:** P2-I-V-0204
- **Message:** Invalid Document_ID format: '131242-WSW41-PP-IM-0001-1'
- **Row:** 8
- **Column:** Document_ID
- **Severity:** HIGH

### Error 11

- **Detector:** IdentityDetector
- **Error Code:** P2-I-V-0204
- **Message:** Invalid Document_ID format: '131242-WSW41-PP-IM-0001-2'
- **Row:** 9
- **Column:** Document_ID
- **Severity:** HIGH

### Error 12

- **Detector:** IdentityDetector
- **Error Code:** P2-I-V-0204
- **Message:** Invalid Document_ID format: '131242-WSW41-PP-IM-0001-3'
- **Row:** 10
- **Column:** Document_ID
- **Severity:** HIGH

### Error 13

- **Detector:** IdentityDetector
- **Error Code:** P2-I-V-0204
- **Message:** Invalid Document_ID format: '131242-WSW41-PP-IM-0001-4'
- **Row:** 11
- **Column:** Document_ID
- **Severity:** HIGH

### Error 14

- **Detector:** IdentityDetector
- **Error Code:** P2-I-V-0204
- **Message:** Invalid Document_ID format: '131242-WSW41-PP-IM-0001-5'
- **Row:** 12
- **Column:** Document_ID
- **Severity:** HIGH

### Error 15

- **Detector:** IdentityDetector
- **Error Code:** P2-I-V-0204
- **Message:** Invalid Document_ID format: '131242-WST00-PP-HS-0001-0'
- **Row:** 13
- **Column:** Document_ID
- **Severity:** HIGH

### Error 16

- **Detector:** IdentityDetector
- **Error Code:** P2-I-V-0204
- **Message:** Invalid Document_ID format: '131242-WST00-PP-HS-0001-1'
- **Row:** 14
- **Column:** Document_ID
- **Severity:** HIGH

### Error 17

- **Detector:** IdentityDetector
- **Error Code:** P2-I-V-0204
- **Message:** Invalid Document_ID format: '131242-WST00-PG-PC-0001-0'
- **Row:** 15
- **Column:** Document_ID
- **Severity:** HIGH

### Error 18

- **Detector:** IdentityDetector
- **Error Code:** P2-I-V-0204
- **Message:** Invalid Document_ID format: '131242-WST00-PG-PC-0001-1'
- **Row:** 16
- **Column:** Document_ID
- **Severity:** HIGH

### Error 19

- **Detector:** IdentityDetector
- **Error Code:** P2-I-V-0204
- **Message:** Invalid Document_ID format: '131242-WSW41-PG-PC-0001-2'
- **Row:** 17
- **Column:** Document_ID
- **Severity:** HIGH

### Error 20

- **Detector:** IdentityDetector
- **Error Code:** P2-I-V-0204
- **Message:** Invalid Document_ID format: '131242-WSW41-LT-PM-0003-0'
- **Row:** 18
- **Column:** Document_ID
- **Severity:** HIGH

_... and 189 more errors_

## Conclusion

This test demonstrates the error handling module's ability to detect Document_ID issues
across multiple error code families (P2, V5, C6).

### Error Code Families Applied:

- **P2-I-xxx**: Identity validation errors
- **V5-I-V-xxxx**: Field validation errors
- **C6-C-C-xxxx**: Calculation/dependency errors

---
*Generated by DocumentIDErrorTest*
# Workplan - Submittal Dashboard KPI Label Update

| Field | Value |
|-------|-------|
| **Workplan ID** | WP-DCC-UI-004 |
| **Version** | 1.1 |
| **Date** | 2026-05-29 |
| **Status** | ✅ COMPLETED |
| **Type** | UI/UX Improvement |
| **Related** | [agent_rule.md](../../agent_rule.md) \| [html_design_rule.md](html_design_rule.md) |

## 1. Object
Update the subtitles for "Review > 30 Days" and "Delay > 30 Days" in the Submittal Dashboard to "MAX DURATION" and "MAX DELAY" to accurately reflect that the logic aggregates the maximum value across all historical revisions for each Document ID.

## 2. Scope Summary

### In Scope
- **KPI Subtitle Update**: 
  - Change "Review > 30 Days" subtitle to "MAX DURATION PER DOC ID (>30D)".
  - Change "Delay > 30 Days" subtitle to "MAX DELAY PER DOC ID (>30D)".
- **HTML Element IDs**: Add `id="subLongReview"` and `id="subDelay"` to the KPI cards.
- **Dynamic Title Logic**: Update `updateTitles` function to handle these new subtitles during data scope toggles.
- **Help Documentation**: Update the `buildSubmittalHelp` function to use the "MAX" terminology.

### Out of Scope
- Modifying the underlying data processing or aggregation logic.
- Changes to other dashboards or metrics.

## 3. Implementation Phases

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 1 | **HTML & Static Label Update**: Add IDs and update hardcoded subtitles in the KPI cards. | ✅ Complete |
| Phase 2 | **Dynamic Logic Update**: Update `updateTitles` to ensure subtitles persist correctly across data scopes. | ✅ Complete |
| Phase 3 | **Help Panel Update**: Synchronize the `buildSubmittalHelp` descriptions with "MAX" terminology. | ✅ Complete |
| Phase 4 | **Verification**: Ensure labels are consistent across all themes and data scopes. | ✅ Complete |

## 4. Evaluation & Alignment

### agent_rule.md Compliance
- Follows the mandate to accurately describe "Derived Logic & Status Flags" (Section 1.4, Priority 3).
- Ensures the UI explicitly reflects the "MAX" aggregation logic.

## 5. Success Criteria
- [x] KPI card for "Review > 30 Days" shows "MAX DURATION PER DOC ID" with dynamic "(>30D)" or "(INC. INVALID)" suffix.
- [x] KPI card for "Delay > 30 Days" shows "MAX DELAY PER DOC ID" with dynamic "(>30D)" or "(INC. INVALID)" suffix.
- [x] Only the **numerical values** (counts) turn red when "Include Invalid" is active; subtitles maintain default theme color.
- [x] Help panel documentation matches the new terminology.

## 6. References
- `ui/submittal_dashboard.html`
- `ui/ui_help.json`

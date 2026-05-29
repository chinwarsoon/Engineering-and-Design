# Workplan - Submittal Dashboard File Loading Panel Enhancement

| Field | Value |
|-------|-------|
| **Workplan ID** | WP-DCC-UI-003 |
| **Version** | 1.0 |
| **Date** | 2026-05-29 |
| **Status** | ✅ COMPLETED |
| **Type** | UI/UX Enhancement |
| **Related** | [agent_rule.md](../../agent_rule.md) \| [html_design_rule.md](html_design_rule.md) |

## 1. Object
Implement a dedicated, independent file loading panel in the Submittal Dashboard. This panel will provide a robust interface for manual file loading (local disk or pipeline) and will automatically prompt the user if the initial background data load fails.

## 2. Scope Summary

### In Scope
- **Independent Loading Panel (Rule 9)**: A new sidebar panel (`#fileSidebar`) accessible via the `📂` icon.
- **Icon Bar Realignment (Rule 10)**: Update filter icon to `🔍` and reserve `📂` for file loading.
- **Auto-Failure Prompt**: A centered UI overlay (`#loadingOverlay`) that appears if `processed_dcc_universal.csv` fails to load automatically.
- **Drag & Drop (Rule 9.3)**: Global and sidebar-specific drop zones for CSV files.
- **File Registry (Rule 9.2)**: Listing all files loaded during the session.
- **Status Bar Integration (Rule 9.4)**: Real-time update of the active file name.

### Out of Scope
- Modifying the underlying data processing logic.
- Changes to other dashboards.

## 3. Implementation Phases

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 1 | **Icon & Sidebar Refactoring**: Realignment of icon bar and creation of toggleable sidebar containers. | ✅ Complete |
| Phase 2 | **File Loading Panel**: Implementation of `#fileSidebar` with source toggle and loaded files list. | ✅ Complete |
| Phase 3 | **Failure Detection & Overlay**: Implementation of `#loadingOverlay` triggered by `loadFromPipeline` errors. | ✅ Complete |
| Phase 4 | **Drag & Drop Integration**: Global event listeners and sidebar drop zone logic. | ✅ Complete |
| Phase 5 | **Testing & Validation**: Verification of rule compliance and theme consistency. | ✅ Complete |

## 4. Evaluation & Alignment

### html_design_rule.md Compliance
- **Rule 9 (File Loading Panel)**: Implemented as a dedicated sidebar with history and drag-and-drop.
- **Rule 10 (Icons)**: Standardized icons used for all major functions (`📂`, `🔍`, `ℹ️`, `❓`, `⚙️`).
- **Layout (Rule 2/3)**: Maintained VS Code-inspired design system with multi-theme support.

## 5. Success Criteria
- [x] User is presented with a clear manual load option if auto-load fails.
- [x] File loading panel allows switching between "Pipeline" and "Local" files.
- [x] Icon bar uses 📂 specifically for the file panel.
- [x] Drag and drop functionality works as expected.
- [x] Status bar updates correctly with the loaded file name.

## 6. References
- `ui/submittal_dashboard.html`
- `workplan/ui_design/html_design_rule.md`

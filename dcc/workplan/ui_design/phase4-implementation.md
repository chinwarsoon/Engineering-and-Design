# Phase 4: Universal Web Interface Implementation
**Status:** In Progress | **Lead:** Franklin Song | **Updated:** 2026-04-18

## Overview
Build a cohesive suite of browser-based tools under `dcc/ui/` for data visualization, schema management, pipeline monitoring, and AI-assisted analysis. All tools share the unified DCC UI Design System.

---

## Design System Foundation (4.0) ✅ COMPLETED

### DCC UI Design System v1.0
**File:** `dcc/ui/dcc-design-system.css`

#### Color Themes Implemented
- **Dark** (default): GitHub-inspired dark theme
- **Light**: Professional light theme
- **Sky**: Cyan-blue theme
- **Ocean**: Teal-green theme
- **Presentation**: Purple-magenta theme

#### VS Code Layout Architecture
```
┌─────────────────────────────────────────────────────┐
│ Title Bar (36px) - Logo | Breadcrumb | Actions     │
├──────┬──────────────────────────────────────────────┤
│ Icon │ Sidebar (260px)  │ Content Area (flex)      │
│ Bar  │ - Sections       │ - Main content           │
│ 48px │ - Navigation     │ - Scrollable             │
│      │ - File tree      │                          │
├──────┴──────────────────────────────────────────────┤
│ Status Bar (22px) - Status | Info | Actions        │
└─────────────────────────────────────────────────────┘
```

#### Shared Components
- **Buttons**: Primary, secondary, ghost, danger, success variants
- **Form Controls**: Text inputs, selects, textareas with consistent styling
- **Cards & KPI Tiles**: Standardized padding, borders, typography
- **Tables**: Sticky headers, alternating rows, hover states
- **Badges & Pills**: Status indicators with color palette
- **Tabs**: Horizontal tab navigation with active state
- **Toolbar**: Flexible action bar with separators
- **Drop Zone**: File upload area with drag-and-drop
- **Toast**: Notification system

#### Typography
- **UI Font**: Inter (300, 400, 500, 600, 700)
- **Mono Font**: JetBrains Mono (300, 400, 500)

#### Spacing & Sizing
- Icon bar: 48px
- Sidebar: 260px
- Title bar: 36px
- Status bar: 22px
- Border radius: 4px (sm), 6px (md), 10px (lg)

---

## Tool Implementation Sequence

### 4.1 Pipeline Dashboard ⏳ PENDING
**File:** `dcc/ui/pipeline_dashboard.html`
**Purpose:** Central hub for pipeline execution monitoring and KPI display

**Features:**
- Pipeline execution status (6 stages with pass/fail)
- KPI tiles: rows processed, match rate, columns created, errors, health score
- Output file quick-links
- Data health gauge
- Last run timestamp
- Run Pipeline button

**Data Sources:**
- `output/error_dashboard_data.json`
- `output/processing_summary.txt`

**Implementation Notes:**
- Real-time status updates via EventSource or polling
- Responsive grid layout for KPI tiles
- Color-coded stage indicators

---

### 4.2 Excel Explorer Pro (Rebuild) ⏳ PENDING
**File:** `dcc/ui/excel_explorer_pro.html`
**Purpose:** Load and explore processed output with filtering and validation

**Features:**
- Drag-and-drop CSV/Excel loader
- Column visibility toggle
- Multi-column sort and filter
- Freeze first N columns
- Row validation error highlighting
- Data health score per row
- Export filtered view to CSV
- Column group tabs

**Data Sources:**
- `output/processed_dcc_universal.csv`
- `output/processed_dcc_universal.xlsx`

**Implementation Notes:**
- Use Papa Parse for CSV handling
- XLSX.js for Excel parsing
- Virtual scrolling for large datasets
- Column grouping by metadata

---

### 4.3 Error Diagnostic Dashboard (Rebuild) ⏳ PENDING
**File:** `dcc/ui/error_diagnostic_dashboard.html`
**Purpose:** Visualize validation errors and data health metrics

**Features:**
- Error summary by phase
- Error code frequency chart
- Per-column error heatmap
- Row-level error drill-down
- Data health distribution histogram
- Filter by error code, column, severity
- Export error report to CSV

**Data Sources:**
- `output/error_dashboard_data.json`

**Implementation Notes:**
- Chart.js for visualizations
- Heatmap using canvas or SVG
- Drill-down table with pagination

---

### 4.4 Schema Manager ⏳ PENDING
**File:** `dcc/ui/schema_manager.html`
**Purpose:** Browse, inspect, and edit schema files without raw JSON

**Features:**
- Schema file tree (left panel)
- Column definition viewer (table)
- Column detail panel (full definition)
- Schema reference viewer (resolved references)
- Global parameters editor
- JSON diff view
- Export modified schema

**Data Sources:**
- `config/schemas/*.json`
- `config/dcc_register_enhanced.json`

**Implementation Notes:**
- File tree with collapsible nodes
- Syntax highlighting for JSON
- Diff visualization
- Live validation

---

### 4.5 Log Explorer Pro (Rebuild) ⏳ PENDING
**File:** `dcc/ui/log_explorer_pro.html`
**Purpose:** Browse debug logs, issue logs, update logs, and test logs

**Features:**
- Log file selector
- JSON log tree viewer
- Markdown log renderer
- Search and filter
- Issue status filter
- Timeline view by date

**Data Sources:**
- `Log/debug_log.json`
- `Log/issue_log.md`
- `Log/update_log.md`
- `Log/test_log.md`

**Implementation Notes:**
- Markdown-it for rendering
- Collapsible tree for JSON
- Timeline component

---

### 4.6 Submittal Tracker Dashboard (Rebuild) ⏳ PENDING
**File:** `dcc/ui/submittal_dashboard.html`
**Purpose:** Visual analytics for processed DCC register data

**Features:**
- Summary KPI row
- Submission timeline chart
- Approval status donut chart
- Overdue resubmission list
- Document status by discipline
- Multi-filter support
- Load from processed CSV

**Data Sources:**
- `output/processed_dcc_universal.csv`

**Implementation Notes:**
- Chart.js for visualizations
- Responsive grid layout
- Real-time filtering

---

### 4.7 Common JSON Tools (Rebuild) ⏳ PENDING
**File:** `dcc/ui/common_json_tools.html`
**Purpose:** General-purpose JSON inspection and validation

**Features:**
- JSON paste/file load
- Tree view with collapsible nodes
- JSONPath query support
- Schema validation
- Format/minify/diff
- Copy to clipboard

**Data Sources:**
- User-provided JSON
- Schema files for validation

**Implementation Notes:**
- JSONPath library for queries
- Syntax highlighting
- Diff visualization

---

### 4.8 Excel → Schema Generator (Rebuild) ⏳ PENDING
**File:** `dcc/ui/excel_to_schema.html`
**Purpose:** Auto-generate schema JSON from Excel headers

**Features:**
- Excel drag-and-drop
- Sheet selector
- Header row selector
- Auto-detect column types
- Generate schema JSON
- Copy/download schema

**Data Sources:**
- User-provided Excel files

**Implementation Notes:**
- XLSX.js for parsing
- Type detection algorithm
- Schema template generation

---

## Implementation Checklist

### Design System (4.0)
- [x] CSS variables for all themes
- [x] VS Code layout components
- [x] Button variants
- [x] Form controls
- [x] Card and KPI styles
- [x] Table styling
- [x] Badge and pill styles
- [x] Tab navigation
- [x] Toolbar component
- [x] Drop zone styling
- [x] Toast notifications
- [x] Utility classes

### Tools (4.1-4.8)
- [ ] Pipeline Dashboard
- [ ] Excel Explorer Pro
- [ ] Error Diagnostic Dashboard
- [ ] Schema Manager
- [ ] Log Explorer Pro
- [ ] Submittal Tracker Dashboard
- [ ] Common JSON Tools
- [ ] Excel → Schema Generator

### Documentation
- [ ] Tool-specific user guides
- [ ] API documentation for data sources
- [ ] Troubleshooting guides
- [ ] Theme customization guide

---

## Technical Stack

### Libraries (CDN)
- **Chart.js**: Data visualization
- **Papa Parse**: CSV parsing
- **XLSX.js**: Excel parsing
- **Markdown-it**: Markdown rendering
- **JSONPath**: JSON querying
- **Diff-match-patch**: Text diffing

### Fonts (Google Fonts)
- **Inter**: UI typography
- **JetBrains Mono**: Code/data display

### Browser APIs
- **FileReader**: Local file access
- **Fetch**: Remote data loading
- **LocalStorage**: User preferences
- **EventSource**: Real-time updates

---

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────┐
│ DCC Pipeline (Python)                               │
│ - Processes Excel files                             │
│ - Generates output files                            │
└────────────────┬────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
┌──────────────┐  ┌──────────────────┐
│ CSV/Excel    │  │ JSON Logs        │
│ Output       │  │ - debug_log.json │
│              │  │ - issue_log.md   │
└──────┬───────┘  └────────┬─────────┘
       │                   │
       └───────┬───────────┘
               │
        ┌──────▼──────────┐
        │ DCC UI Tools    │
        │ (Browser-based) │
        │ - Load data     │
        │ - Visualize     │
        │ - Export        │
        └─────────────────┘
```

---

## Deployment Strategy

### Local Development
1. Open tool HTML file directly in browser
2. Use FileReader API to load local data files
3. Store preferences in localStorage

### Production Deployment
1. Host HTML files on static server
2. Serve data files via HTTP API
3. Implement authentication if needed
4. Add CORS headers for cross-origin requests

---

## Performance Considerations

- **Large Datasets**: Virtual scrolling for tables
- **Real-time Updates**: EventSource for streaming
- **File Parsing**: Web Workers for heavy computation
- **Caching**: LocalStorage for frequently accessed data
- **Lazy Loading**: Load data on demand

---

## Accessibility Standards

- WCAG 2.1 Level AA compliance
- Keyboard navigation support
- Screen reader friendly
- High contrast mode support
- Focus indicators

---

## Testing Strategy

### Unit Tests
- Component rendering
- Data parsing
- Calculations

### Integration Tests
- Data loading from files
- Filter and sort operations
- Export functionality

### E2E Tests
- Complete workflows
- Cross-browser compatibility
- Performance benchmarks

---

## Rollout Plan

### Phase 4.1: Foundation (Week 1)
- Design system finalization
- Pipeline Dashboard
- Excel Explorer Pro

### Phase 4.2: Analytics (Week 2)
- Error Diagnostic Dashboard
- Submittal Tracker Dashboard
- Log Explorer Pro

### Phase 4.3: Management (Week 3)
- Schema Manager
- Common JSON Tools
- Excel → Schema Generator

### Phase 4.4: Polish (Week 4)
- Documentation
- Testing
- Performance optimization
- User feedback integration

---

## Success Metrics

- [ ] All tools load and render correctly
- [ ] Data parsing accuracy > 99%
- [ ] Page load time < 2 seconds
- [ ] No console errors
- [ ] All filters and exports work
- [ ] Responsive on desktop/tablet
- [ ] Theme switching works smoothly
- [ ] Accessibility audit passes

---

*Last Updated: 2026-04-18*

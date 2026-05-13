# Phase 4 UI Tools - User Guide

## Overview
The DCC UI Tools suite provides a comprehensive set of browser-based applications for data visualization, schema management, pipeline monitoring, and analysis. All tools share a unified design system and can be accessed directly from the browser without requiring a server.

---

## 🎨 Design System

### Theme Support
All tools support 5 color themes:
- **Dark** (default): GitHub-inspired dark theme
- **Light**: Professional light theme
- **Sky**: Cyan-blue theme
- **Ocean**: Teal-green theme
- **Presentation**: Purple-magenta theme

Switch themes using the theme picker in the top-right corner of any tool.

### Layout Architecture
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

---

## 📊 Pipeline Dashboard

**File:** `pipeline_dashboard.html`

### Purpose
Central hub for monitoring pipeline execution, viewing KPIs, and accessing output files.

### Features

#### KPI Tiles
- **Rows Processed**: Total number of data rows processed
- **Match Rate**: Percentage of successful column mappings
- **Columns Created**: Number of output columns generated
- **Errors Found**: Count of validation errors
- **Data Health**: Overall data quality score (0-100%)

#### Pipeline Stages
Visual progress indicators for 6 processing stages:
1. File Upload
2. Sheet Selection
3. Column Mapping
4. Data Validation
5. Processing
6. Export

#### Output Files
Quick-access links to:
- CSV Export
- Excel Export
- Processing Summary
- Debug Log
- Error Dashboard Data
- Validation Report

#### Recent Activity
Timeline of pipeline events with status indicators.

### Usage
1. Open `pipeline_dashboard.html` in browser
2. View current pipeline status and KPIs
3. Click output file links to download or view
4. Use "Run Pipeline" button to trigger processing
5. Monitor stage progress in real-time

### Keyboard Shortcuts
- `Ctrl+R`: Refresh dashboard
- `Ctrl+S`: Save current view

---

## 📊 Excel Explorer Pro

**File:** `excel_explorer_pro.html`

### Purpose
Load and explore processed CSV/Excel data with advanced filtering, sorting, and validation highlighting.

### Features

#### File Loading
- Drag-and-drop CSV or Excel files
- Click to browse local files
- Automatic format detection

#### Column Management
- Toggle column visibility by group
- Groups: Document Info, Submission Info, Review Info, Metadata
- Freeze first N columns for horizontal scrolling

#### Data Filtering
- Search across all columns
- Filter by specific column
- Multi-column sort
- Reset filters to view all data

#### Validation Highlighting
- Red highlighting for validation errors
- Yellow highlighting for warnings
- Green highlighting for valid data
- Data health score per row

#### Export
- Export filtered view to CSV
- Preserves column visibility settings
- Includes all visible rows

### Usage
1. Open `excel_explorer_pro.html`
2. Drag-and-drop a CSV or Excel file
3. Use sidebar to toggle column visibility
4. Search or filter data using toolbar
5. Click "Export CSV" to download filtered view

### Tips
- Use column groups to organize large datasets
- Search is case-insensitive and searches all columns
- Filter by column for precise data selection
- Validation highlighting helps identify problem rows

---

## 🔍 Error Diagnostic Dashboard

**File:** `error_diagnostic_dashboard.html`

### Purpose
Visualize validation errors, data health metrics, and error analysis with interactive charts.

### Features

#### Summary KPIs
- Total Errors
- Warnings Count
- Data Health Score
- Affected Rows

#### Error Code Frequency Chart
Bar chart showing distribution of error codes across dataset.

#### Data Health Distribution
Line chart showing data health score distribution across rows.

#### Error Heatmap
Color-coded grid showing error frequency by column:
- Green: No errors
- Yellow: Few errors
- Red: Many errors

#### Error Details Table
Drill-down table with:
- Row number
- Column name
- Error code
- Error message
- Severity level

#### Phase Summary
Error summary by processing phase with pass/fail status.

### Filters
- Error Code: Filter by specific error code
- Column: Filter by affected column
- Severity: Filter by error severity (Critical/Warning/Info)

### Usage
1. Open `error_diagnostic_dashboard.html`
2. Load error data from `error_dashboard_data.json`
3. Use filters to narrow down errors
4. Click on chart elements to drill down
5. Export error report to CSV

### Interpretation
- **Critical Errors**: Must be fixed before processing
- **Warnings**: Should be reviewed but don't block processing
- **Info**: Informational messages for reference

---

## ⚙️ Schema Manager

**File:** `schema_manager.html`

### Purpose
Browse, inspect, and edit schema files without touching raw JSON.

### Features

#### Schema File Tree
- Browse all schema files in left panel
- Expand/collapse file structure
- View file metadata

#### Column Definition Viewer
Table showing all columns with:
- Column name
- Data type
- Required flag
- Null handling strategy

#### Column Detail Panel
Full definition for selected column:
- Data type
- Validation rules
- Calculation configuration
- Aliases
- Description

#### Schema References
View resolved schema references:
- Reference name
- Source file
- Resolution status

#### Global Parameters
Edit key schema parameters:
- Sheet name
- Header row number
- Data start row

#### JSON Diff View
Compare current schema vs archived version.

#### Export
Download modified schema as JSON file.

### Usage
1. Open `schema_manager.html`
2. Select schema file from left panel
3. View column definitions in table
4. Click column to see full details
5. Edit global parameters as needed
6. Export modified schema

### Best Practices
- Always backup schema before editing
- Validate schema after changes
- Use meaningful column names
- Document custom validation rules

---

## 📋 Log Explorer Pro

**File:** `log_explorer_pro.html`

### Purpose
Browse debug logs, issue logs, update logs, and test logs with search and filtering.

### Features

#### Log File Selection
- Debug Log (JSON format)
- Issue Log (Markdown format)
- Update Log (Markdown format)
- Test Log (Markdown format)

#### JSON Log Viewer
- Tree view with collapsible nodes
- Color-coded log levels
- Timestamp display
- Search and filter

#### Markdown Renderer
- Formatted markdown display
- Anchor navigation
- Code block highlighting
- List and table rendering

#### Search & Filter
- Search across log entries
- Filter by log level
- Filter by date range
- Filter by issue status

#### Timeline View
- Chronological log entry display
- Date-based grouping
- Event filtering

### Log Levels
- **Error** (Red): Critical issues
- **Warning** (Yellow): Potential problems
- **Info** (Blue): Informational messages
- **Success** (Green): Successful operations

### Usage
1. Open `log_explorer_pro.html`
2. Select log file from left panel
3. Use search to find specific entries
4. Filter by log level or date
5. Click entries to expand details
6. Export log report

### Tips
- Use search for quick issue identification
- Filter by severity to focus on problems
- Check timestamps for event correlation
- Export logs for external analysis

---

## 📤 Submittal Tracker Dashboard

**File:** `submittal_dashboard.html`

### Purpose
Visual analytics dashboard for processed DCC register data with charts and KPIs.

### Features

#### Summary KPIs
- Total Documents
- Open Submissions
- Overdue Resubmissions
- Approval Rate

#### Submission Timeline Chart
Line chart showing submission volume over time.

#### Approval Status Breakdown
Donut chart showing distribution of approval statuses:
- Approved
- Pending
- Rejected
- Resubmit

#### Document Status by Discipline
Bar chart showing document count by discipline:
- Structural
- Mechanical
- Electrical
- Plumbing

#### Submission Trend
Line chart showing approval rate trend over time.

#### Overdue Resubmissions Table
List of overdue submissions with:
- Document ID
- Discipline
- Due date
- Days overdue
- Status

#### Recent Activity
Timeline of recent document actions.

### Filters
- Project Code
- Facility Code
- Discipline
- Date Range

### Usage
1. Open `submittal_dashboard.html`
2. Load processed CSV data
3. Apply filters to narrow data
4. View charts and KPIs
5. Click chart elements to drill down
6. Export analytics report

### Insights
- Identify bottlenecks in approval process
- Track submission trends
- Monitor overdue items
- Analyze by discipline or facility

---

## { } Common JSON Tools

**File:** `common_json_tools.html`

### Purpose
General-purpose JSON inspection, formatting, validation, and manipulation.

### Features

#### Input Methods
- Paste JSON directly
- Load from file
- Load sample data

#### Tree View
- Collapsible tree structure
- Color-coded value types
- Expandable arrays and objects

#### Formatting
- Pretty-print JSON
- Minify JSON
- Copy to clipboard

#### JSONPath Query
- Execute JSONPath queries
- Extract specific data
- Filter results

#### Validation
- Validate JSON syntax
- Validate against schema
- Show validation errors

#### Supported Schemas
- DCC Register
- Department
- Discipline

### Usage
1. Open `common_json_tools.html`
2. Paste or load JSON
3. View tree structure
4. Use formatting tools
5. Execute JSONPath queries
6. Validate against schema

### JSONPath Examples
```
$.name                    # Get name property
$.columns[0]             # Get first column
$.columns[*].data_type   # Get all data types
$..required              # Find all required properties
```

### Tips
- Use tree view to understand structure
- Minify before sending over network
- Validate before processing
- Use JSONPath for data extraction

---

## 📊 Excel → Schema Generator

**File:** `excel_to_schema.html`

### Purpose
Auto-generate schema JSON from Excel file headers with type detection.

### Features

#### Step 1: Upload
- Drag-and-drop Excel file
- Click to browse

#### Step 2: Sheet Selection
- Select from available sheets
- View sheet metadata

#### Step 3: Column Detection
- Auto-detect column types
- Show sample values
- Mark required columns

#### Step 4: Schema Generation
- Generate schema JSON
- Preview generated schema
- Download or copy

#### Type Detection
- **String**: Text values
- **Number**: Numeric values
- **Date**: Date-formatted values
- **Boolean**: True/false values

#### Options
- Header row number
- Schema name and version
- Auto-detect required columns
- Auto-detect types
- Add column aliases

### Usage
1. Open `excel_to_schema.html`
2. Upload Excel file
3. Select sheet
4. Review detected columns
5. Adjust settings if needed
6. Download generated schema

### Tips
- Ensure headers are in first row
- Use consistent data types per column
- Review auto-detected types
- Add meaningful schema name
- Test schema before deployment

### Generated Schema Structure
```json
{
  "name": "Schema Name",
  "version": "1.0.0",
  "description": "Auto-generated schema",
  "columns": {
    "Column_Name": {
      "data_type": "string",
      "required": true,
      "allow_null": false,
      "aliases": ["column_name", "column name"],
      "description": "Column: Column_Name"
    }
  }
}
```

---

## 🔧 Troubleshooting

### File Loading Issues
**Problem**: File won't load
- **Solution**: Ensure file format is supported (CSV, XLSX, JSON)
- **Solution**: Check file size (max 50MB recommended)
- **Solution**: Try different browser

### Theme Not Saving
**Problem**: Theme resets on page reload
- **Solution**: Check browser localStorage is enabled
- **Solution**: Clear browser cache and try again

### Charts Not Displaying
**Problem**: Charts appear blank
- **Solution**: Ensure data is loaded
- **Solution**: Check browser console for errors
- **Solution**: Try different browser

### Export Not Working
**Problem**: Export button doesn't work
- **Solution**: Check browser download settings
- **Solution**: Ensure sufficient disk space
- **Solution**: Try different browser

### Performance Issues
**Problem**: Tool is slow with large files
- **Solution**: Use virtual scrolling for large tables
- **Solution**: Filter data before export
- **Solution**: Close other browser tabs

---

## 📱 Browser Compatibility

### Supported Browsers
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Required Features
- ES6 JavaScript support
- FileReader API
- LocalStorage
- Fetch API

---

## 🔐 Security & Privacy

### Data Handling
- All processing happens locally in browser
- No data sent to external servers
- Files stored only in browser memory
- LocalStorage used only for preferences

### Best Practices
- Don't share browser with sensitive data
- Clear browser cache after use
- Use HTTPS when accessing tools
- Validate data before processing

---

## 📞 Support

### Getting Help
1. Check this documentation
2. Review tool tooltips (hover over icons)
3. Check browser console for errors
4. Review project logs for issues

### Reporting Issues
Include:
- Browser and version
- Tool name
- Steps to reproduce
- Error message (if any)
- Screenshot (if applicable)

---

*Last Updated: 2026-04-18*

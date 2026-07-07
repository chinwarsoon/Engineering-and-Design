# Universal UI Design System

| Revision | Date       | Author | Summary                                      |
|----------|------------|--------|----------------------------------------------|
| 0.1      | 2026-07-07 | Dev    | Initial creation — shared CSS design tokens, layout, and components for DCC, EKS, and code_tracer |
| 0.2      | 2026-07-07 | Dev    | Added universal_ui_design.js — 8 reusable JS modules (theme, sidebar, layout, toast, modal, file, table, utils) under `comUI` namespace |

---

## 1. Overall Summary

The Universal UI Design System provides a single source of truth for all web UI components across the DCC, EKS, and code_tracer projects. It defines CSS custom properties (design tokens), a VS Code-inspired shell layout, reusable component classes prefixed with `com-` (common) and `sb-` (sidebar), and a shared JavaScript library under the `comUI` namespace. The system enforces consistent visual language, theming, interaction patterns, and JS logic across all project UIs.

**Purpose**: Eliminate duplicate CSS **and JS**, standardize component naming, and enable a unified look and feel across all tools.

---

## 2. Content Index

| #  | Section               | Description                                    |
|----|-----------------------|------------------------------------------------|
| 1  | Themes                | CSS custom properties for 5 color schemes      |
| 2  | Reset & Base          | Global reset, body, link, scrollbar styles     |
| 3  | Shell Layout          | Titlebar, iconbar, sidebar, content, statusbar |
| 4  | Sidebar Accordion     | Collapsible sidebar sections (`sb-section`)    |
| 5  | Buttons               | Primary, secondary, ghost, danger, success     |
| 6  | Badges                | Accent, success, warning, danger, info, muted  |
| 7  | Tables                | Sortable data tables with sticky headers       |
| 8  | Tabs & Navigation     | Content tabs and sidebar tabs                  |
| 9  | Forms                 | Labels, inputs, selects, textareas            |
| 10 | Cards & KPI Cards     | Metric tiles with grid layout                  |
| 11 | Stage Cards           | Pipeline stage indicators with progress bars   |
| 12 | Step Progress         | Pipeline step indicator (node + arrow)         |
| 13 | Modal                 | Overlay dialog with header/body/footer         |
| 14 | Toast                 | Fixed-position notification                    |
| 15 | Drop Zone             | File upload drag-and-drop area                 |
| 16 | Welcome Pane          | Empty-state landing page                       |
| 17 | Toolbar               | Horizontal action bar                          |
| 18 | Theme Picker          | Theme selector dropdown                        |
| 19 | Resizer               | Drag-to-resize sidebar handles                 |
| 20 | File Loading Panel    | Loaded files list                              |
| 21 | Data Table Viewer     | Multi-tab JSON/CSV viewer                      |
| 22 | Tree / Key Explorer   | JSON schema tree browser                        |
| 23 | Sidebar Panel         | Generic toggle panels                          |
| 24 | Content Panel         | Tab content area                               |
| 25 | Editor Components     | Monospace editor/text areas                    |
| 26 | Utilities             | Helper classes for layout, spacing, colors    |
| 27 | Animations            | Keyframe animations (fade, slide, spin)       |
| 28 | Health Gauge          | CSS gradient progress bar                      |
| 29 | Schema Map            | 3-tier flowchart for schema definitions       |
| 30 | JS: Theme             | `comUI.theme.apply()`, `comUI.theme.initPicker()` |
| 31 | JS: Sidebar           | `comUI.sidebar.resize()`, `comUI.sidebar.accordion()` |
| 32 | JS: Layout            | `comUI.layout.toggle()`                       |
| 33 | JS: Toast             | `comUI.toast.show()`                          |
| 34 | JS: Modal             | `comUI.modal.open/close/init()`               |
| 35 | JS: File              | `comUI.file.setupDropZone()`, `readFile*()`   |
| 36 | JS: Table             | `comUI.table.makeSortable()`                  |
| 37 | JS: Utils             | `comUI.utils.escHtml()`, `formatNum()`, `formatBytes()`, `setStatus()` |

---

## 3. Key Features

- **5 themes**: dark (default), light, sky, ocean, presentation – applied via `data-theme` attribute
- **VS Code shell model**: titlebar (36px) + iconbar (48px) + sidebars (resizable, collapsible) + content + statusbar (22px)
- **`com-` prefix**: all shared classes use `com-` to avoid naming collisions
- **`sb-` prefix**: sidebar-specific sub-components (accordion, tabs, items)
- **CSS custom properties**: all colors reference design tokens — never hardcoded hex
- **Theme transition**: smooth 0.25s color/background swap
- **Zero build step**: standalone CSS + JS files, no bundler required
- **Drag-to-resize sidebars**: min 120px, max 480px, persisted via `localStorage`
- **Collapsible panels**: sidebar accordion, sidebars collapse to 0 width
- **`comUI` JS namespace**: 8 reusable modules (theme, sidebar, layout, toast, modal, file, table, utils) — no framework dependency

---

## 4. Documentation Map

```
common/
├── universal_ui_design.css      # CSS design system (~842 lines, 29 sections)
├── universal_ui_design.js       # JS library (~350 lines, 8 modules)
└── universal_ui_design.md       # This documentation

Project folders reference:
  dcc/ui/dcc-design-system.css   → ancestor, now superseded by universal
  eks/ui/eks.css                 → should align to com- tokens
  code_tracer/ui/code-tracer.css → should align to com- tokens
  eks/ui/eks.js                  → should use comUI calls instead of inline code
  dcc/ui/*.html                  → should use comUI calls instead of inline code
```

---

## 5. Quick Start

### 5.1 Include the CSS

```html
<link rel="stylesheet" href="/common/universal_ui_design.css">
```

### 5.2 Set up the shell layout

```html
<body>
<div class="com-shell">
  <!-- Titlebar -->
  <header class="com-titlebar">
    <span class="com-titlebar-logo">📊 <span class="accent">My</span>App</span>
    <div class="com-titlebar-actions">
      <button class="com-theme-btn" id="themeBtn">🎨 <span class="com-theme-dot" style="background:var(--accent)"></span> Theme</button>
    </div>
  </header>

  <!-- Body -->
  <div class="com-body">
    <!-- Icon bar -->
    <nav class="com-iconbar">...</nav>
    <!-- Left sidebar -->
    <aside class="com-sidebar" id="leftSidebar">...</aside>
    <!-- Content -->
    <main class="com-content">...</main>
  </div>

  <!-- Status bar -->
  <footer class="com-statusbar">
    <span class="com-statusbar-left">Ready</span>
    <span class="com-statusbar-right">v1.0</span>
  </footer>
</div>
</body>
```

### 5.3 Apply a theme

```html
<!-- Default dark theme -->
<html data-theme="dark">
<!-- Or switch via JS: -->
<script>document.documentElement.setAttribute('data-theme', 'light');</script>
```

### 5.4 Use common components

```html
<button class="com-btn com-btn-primary">▶ Run Pipeline</button>
<span class="com-badge com-badge-success">✓ Pass</span>
<table class="com-table">...</table>
<div class="com-card">...</div>
```

### 5.5 Include the JS library and initialize

```html
<script src="/common/universal_ui_design.js"></script>
<script>
  // Theme picker (requires HTML structure: .com-theme-btn + .com-theme-menu + .com-theme-opt[data-theme])
  comUI.theme.initPicker('myapp-theme');

  // Sidebar resize (requires position:relative on sidebar + .com-resizer.left-resizer / .right-resizer)
  comUI.sidebar.resize('leftSidebar', 'leftResizer', { min: 120, max: 480, storageKey: 'myapp-sidebar-w' });
  comUI.sidebar.resize('rightSidebar', 'rightResizer', { min: 120, max: 480, storageKey: 'myapp-right-sidebar-w' });

  // Sidebar accordion (toggles .closed on click of .sb-section-header)
  comUI.sidebar.accordion();

  // Layout toggle button (cycles 🔲→📐→📦)
  comUI.layout.toggle('layoutBtn', { left: 'leftSidebar', right: 'rightSidebar', storageKey: 'myapp-layout' });

  // Toast notifications
  comUI.toast.show('Pipeline complete', 'success');
  comUI.toast.show('Connection failed', 'error', 5000);

  // Modal initialization
  comUI.modal.init('helpModal');

  // Sortable table
  comUI.table.makeSortable('docTable');

  // File drag-drop zone
  comUI.file.setupDropZone('dropZone', function(files) { console.log('Dropped', files.length, 'files'); });

  // Utility functions
  var safe = comUI.utils.escHtml(userInput);
  var pretty = comUI.utils.formatNum(1234567);  // "1.2M"
  var size = comUI.utils.formatBytes(2048);      // "2.0 KB"
  comUI.utils.setStatusBar('Documents loaded', 'v2.0');
</script>
```

---

## 6. Module/Function Structure

### CSS (29 sections)

Organized as a single flat file. Architecture dependency chain:

```
Themes (tokens) → Reset → Shell Layout → Sidebar → Components → Utilities → Animations
```

All components depend only on the CSS custom properties defined in themes. No component depends on another component's layout rules.

### JS (8 modules under `comUI` namespace)

Organized as a single IIFE file with `comUI` as the global namespace:

```
comUI.theme     → apply, initPicker
comUI.sidebar   → resize, accordion
comUI.layout    → toggle
comUI.toast     → show
comUI.modal     → open, close, init
comUI.file      → setupDropZone, readFileAsText, readFileAsJSON, readFileAsDataURL
comUI.table     → makeSortable
comUI.utils     → escHtml, formatNum, formatBytes, setStatus, setStatusBar
```

Each module is self-contained with no cross-module dependencies. Modules interact only with the DOM via CSS class names defined in the CSS design system (`.com-theme-btn`, `.com-theme-menu`, `.sb-section-header`, `.com-resizer`, `.com-toast`, etc.).

---

## 7. List of Component Groups

| Group              | Key Selectors                                      | Purpose                               |
|--------------------|----------------------------------------------------|---------------------------------------|
| Shell              | `.com-shell`, `.com-titlebar`, `.com-body`, `.com-iconbar`, `.com-sidebar`, `.com-content`, `.com-statusbar` | Page layout |
| Sidebar accordion  | `.sb-section`, `.sb-section-header`, `.sb-section-body`, `.sb-item` | Collapsible left sidebar |
| Buttons            | `.com-btn`, `.com-btn-primary`, `.com-btn-secondary`, `.com-btn-ghost`, `.com-btn-danger`, `.com-btn-success` | Action triggers |
| Badges             | `.com-badge`, `.com-badge-*`                       | Status labels |
| Tables             | `.com-table`, `.com-table-scroll`                  | Data display |
| Tabs               | `.com-tab-bar`, `.com-tab`, `.sb-tabs`, `.sb-tab`  | Navigation |
| Forms              | `.com-form-label`, `.com-input`, `.com-form-control` | Input fields |
| KPI Cards          | `.com-kpi-grid`, `.com-kpi-card`, `.com-kpi-value`, `.com-kpi-label` | Metrics dashboard |
| Stage Cards        | `.com-stage-card`, `.com-stage-status`, `.com-stage-progress` | Pipeline stages |
| Step Progress      | `.com-step-progress`, `.com-step-item`, `.com-step-node`, `.com-step-arrow` | Step indicators |
| Modal              | `.com-modal-overlay`, `.com-modal`, `.com-modal-header`, `.com-modal-body`, `.com-modal-footer` | Dialogs |
| Toast              | `.com-toast`, `.com-toast-*`                       | Notifications |
| Drop Zone          | `.com-drop-zone`, `.com-dz-*`                      | File upload |
| Welcome Pane       | `.com-welcome-pane`, `.com-welcome-*`              | Empty states |
| Toolbar            | `.com-toolbar`, `.com-toolbar-sep`, `.com-toolbar-spacer` | Action bars |
| Theme Picker       | `.com-theme-btn`, `.com-theme-menu`, `.com-theme-opt` | Theme switching |
| Resizer            | `.com-resizer`, `.com-resizer.left-resizer`, `.com-resizer.right-resizer` | Drag handles |
| Tree Explorer      | `.com-tree-container`, `.com-tree-node-inner`      | JSON schema browser |
| Animations         | `.com-spinner`, `@keyframes com*`                  | Loading/transition |

---

## 8. I/O Table

| Input (CSS Custom Property) | Affected Components             | Output Effect                    |
|-----------------------------|----------------------------------|----------------------------------|
| `--bg`                      | Body, content area              | Page background                  |
| `--surface`                 | Sidebar, card, modal, dropdown  | Surface background               |
| `--surface2`                | Hover state, secondary elements | Lighter/darker surface           |
| `--surface3`                | Input fields, tree areas        | Deepest surface                  |
| `--border`                  | All borders                     | Border color                     |
| `--text`                    | Body text, headings             | Primary text color               |
| `--text2`                   | Secondary labels, meta text     | Dimmed text                      |
| `--text3`                   | Placeholder, muted text         | Faint text                       |
| `--accent`                  | Primary button, links           | Accent color (blue default)      |
| `--accent-alt`              | Active tab, active sidebar      | Stronger accent                  |
| `--success`/`--warning`/`--danger`/`--info` | Badges, stage status, toast | Semantic colors   |
| `--radius`/`--radius-sm`/`--radius-lg`      | Cards, buttons, modals    | Border radius                    |
| `--font-ui`/`--font-mono`                      | All text / code blocks | Font family                      |
| `--sidebar-w`/`--right-sidebar-w`/`--icon-bar-w` | Shell layout dimensions | Widths          |

---

## 9. Global Parameter Trace Matrix

| Token Name             | Set In         | Used By (Sections)                       |
|------------------------|----------------|------------------------------------------|
| `--bg`                 | Theme :root    | 2 (body), 3 (com-content), 29           |
| `--surface`            | Theme :root    | 3 (titlebar, iconbar, sidebar, statusbar), 10 (card), 11 (stage), 13 (modal), 15 (welcome) |
| `--surface2`           | Theme :root    | 3 (toolbar), 4 (sb-section-header:hover), 5 (btn-secondary), 14 (toast), 18 (theme-opt:hover) |
| `--surface3`           | Theme :root    | 5 (btn-ghost:hover), 9 (input), 11 (stage-progress), 25 (editor-input) |
| `--border`             | Theme :root    | 3 (all borders), 4 (sb-section), 5 (btn-secondary), 7 (table), 8 (tab-bar), 13 (modal), 14 (toast), 15 (drop-zone), 17 (toolbar), 18 (theme-menu), 21 (dt-tab-bar) |
| `--text`               | Theme :root    | 2 (body), 4 (sb-section-header:hover), 5 (btn-ghost:hover), 7 (table td), 10 (card-title), 16 (welcome-title), 26 (utility text) |
| `--text2`              | Theme :root    | 3 (breadcrumb), 4 (sb-section-header), 5 (btn-secondary), 7 (table th), 10 (kpi-label), 11 (stage-meta), 16 (welcome-sub) |
| `--text3`              | Theme :root    | 3 (statusbar), 4 (chevron), 5 (btn-sm), 8 (sb-tab), 9 (form-label, placeholder), 22 (tree-title) |
| `--accent`             | Theme :root    | 5 (btn-primary), 6 (badge-accent), 12 (step-arrow), 22 (tree-node-inner.selected) |
| `--accent-alt`         | Theme :root    | 3 (iconbar-btn.active), 4 (sb-tab.active), 5 (btn-primary:hover), 7 (table th:hover), 8 (tab.active), 9 (input:focus), 10 (kpi-value), 12 (step-node.active), 14 (toast), 15 (drop-zone:hover), 18 (theme-opt.active), 21 (dt-tab.active) |
| `--success`/`--warning`/`--danger`/`--info` | Theme :root | 6 (badge), 11 (stage-status), 14 (toast border-left), 26 (text-*) |

---

## 10. Details of Each Component Group

### Section 1: Themes
Five color themes are defined via `[data-theme="..."]` selectors: `dark` (default), `light`, `sky`, `ocean`, `presentation`. Each defines 25+ CSS custom properties covering surfaces, borders, text, accent, semantic colors, tags, tables, dimensions, radii, and fonts. Properties cascade to all components.

### Section 2: Reset & Base
Universal box-sizing reset, full-height viewport, system font stack with antialiasing, link styling, custom 6px scrollbar.

### Section 3: Shell Layout
- `.com-shell`: flex column, full viewport height
- `.com-titlebar`: fixed 36px row — logo (left), breadcrumb (center), actions (right)
- `.com-body`: flex row with iconbar + sidebar(s) + content
- `.com-iconbar`: 48px column, top icons + bottom icons separated by 1px border
- `.com-sidebar`: collapsible via `.collapsed` → width 0
- `.com-content`: flex:1 column with scrollable body
- `.com-statusbar`: fixed 22px row — left info, right info

### Section 4: Sidebar Accordion
Collapsible sections within sidebars. Clicking `.sb-section-header` toggles `.closed` on parent `.sb-section`, rotating the chevron.

### Section 5: Buttons
6 variants: primary (accent fill), secondary (bordered), ghost (transparent), danger (red tint), success (green tint). 3 sizes: sm, default, lg. Icon-only variant.

### Section 6: Badges
Rounded pills with semantic color variants: accent, success, warning, danger, info, muted.

### Section 7: Tables
Sticky header, striped rows, hover highlight, sortable column headers with `▲`/`▼` indicators via `.sorted-asc`/`.sorted-desc`.

### Section 8: Tabs
Two tab patterns: `.com-tab-bar` (flex row with active underline + gradient) and `.sb-tabs` (full-width, uppercase, compact for sidebars).

### Section 9: Forms
Consistent input styling with focus accent border, select with custom arrow, monospace textarea.

### Section 10: Cards & KPI Cards
`.com-kpi-grid` auto-fits 140px+ columns. Each card clickable with accent border on hover.

### Section 11: Stage Cards
Pipeline stage card with icon, name, meta (truncated), status label (PENDING/RUNNING/PASS/FAIL), and 4px gradient progress bar.

### Section 12: Step Progress
Horizontal step indicator with circular nodes and connecting arrows. Supports active/done/fail states. Label below each node.

### Section 13: Modal
Fixed overlay with centered dialog. Header (title + close button), scrollable body, footer (right-aligned actions).

### Section 14: Toast
Fixed bottom-right notification with colored left border. Animates in.

### Section 15: Drop Zone
Dashed border area with file input overlay. Accent highlight on hover/drag-over.

### Section 16: Welcome Pane
Centered empty state with icon, title, subtitle, and optional step cards.

### Section 17: Toolbar
Flex row with title, separator, spacer, and actions.

### Section 18: Theme Picker
Button + dropdown menu. Each option has a color dot + label, active option marked.

### Section 19: Resizer
5px drag handles at sidebar edges. 2px × 32px center bar on hover.

### Section 20–25: Specialized panels
File list, data table viewer, tree explorer, toggle panels, content panels, and monospace editors.

### Section 26: Utilities
40+ helper classes for flex, spacing, colors, truncation, overflow.

### Section 27: Animations
`comFadeIn`, `comSlideUp`, `comToastIn`, `comSpin` keyframes. Spinner class for loading.

### Section 28: Health Gauge
4px gradient bar using danger→warning→success gradient.

### Section 29: Schema Map
3-tier flowchart layout for definitions → properties → values schema visualization.

---

## 11. Debugging and Troubleshooting

| Issue                        | Likely Cause                                  | Fix                                              |
|------------------------------|-----------------------------------------------|--------------------------------------------------|
| Theme not applying           | `data-theme` missing or typo                  | Set `<html data-theme="dark">`                   |
| Sidebar not collapsing       | `.collapsed` class missing or JS not hooked   | Add/remove `.collapsed` via JS                   |
| Com- class not working       | CSS file not loaded or path wrong             | Check `<link>` path; use root-relative path      |
| Colors look wrong            | CSS custom properties not defined             | Verify theme section loads before components     |
| Resizer not responding       | Missing position:relative on sidebar          | Ensure sidebar has `position: relative`          |
| Modal appears behind content | z-index conflict                              | `.com-modal-overlay` uses z-index: 10000         |
| KPI grid stacking            | Container too narrow                          | Minimum column width is 140px                     |
| Drag-and-drop not working    | File input opacity 0 but not covering zone    | Ensure `<input type="file">` has `inset: 0`      |

---

## 12. Usage Examples

### Full pipeline dashboard

```html
<div class="com-shell">
  <header class="com-titlebar">
    <span class="com-titlebar-logo">🔧 EKS Pipeline</span>
    <div class="com-titlebar-actions">
      <button class="com-btn com-btn-primary">▶ Run</button>
    </div>
  </header>
  <div class="com-body">
    <nav class="com-iconbar">
      <div class="com-iconbar-top">
        <button class="com-iconbar-btn active">📊</button>
        <button class="com-iconbar-btn">📂</button>
      </div>
      <div class="com-iconbar-bot">
        <button class="com-iconbar-btn">⚙️</button>
        <button class="com-iconbar-btn">❓</button>
      </div>
    </nav>
    <aside class="com-sidebar" id="leftSidebar" style="position:relative">
      <div class="sb-section">
        <div class="sb-section-header">📋 Stages <span class="chevron">▼</span></div>
        <div class="sb-section-body">
          <div class="sb-item active">📥 Ingestion</div>
          <div class="sb-item">🔄 Processing</div>
          <div class="sb-item">📤 Output</div>
        </div>
      </div>
      <div class="com-resizer left-resizer"></div>
    </aside>
    <main class="com-content">
      <div class="com-toolbar">
        <span class="com-toolbar-title">Ingestion Stage</span>
        <span class="com-toolbar-spacer"></span>
        <span class="com-badge com-badge-success">✓ Running</span>
      </div>
      <div class="com-content-body" style="padding:16px">
        <div class="com-kpi-grid">
          <div class="com-kpi-card">
            <span class="com-kpi-value">1,284</span>
            <span class="com-kpi-label">Records</span>
          </div>
          <div class="com-kpi-card">
            <span class="com-kpi-value">98.2%</span>
            <span class="com-kpi-label">Quality</span>
          </div>
        </div>
      </div>
    </main>
  </div>
  <footer class="com-statusbar">
    <span>Ready</span>
    <span class="com-statusbar-right">v1.0.0</span>
  </footer>
</div>
```

### Toast notification trigger

```javascript
function showToast(msg, type = 'info') {
  const t = document.getElementById('toast');
  t.className = 'com-toast com-toast-' + type + ' show';
  t.querySelector('.com-toast-icon').textContent = type === 'success' ? '✓' : '✗';
  t.appendChild(document.createTextNode(' ' + msg));
  setTimeout(() => t.classList.remove('show'), 3000);
}
```

---

## 13. Best Practices and Pending Issues

### Best Practices
- Always use `com-` prefixed classes in HTML; never apply raw CSS custom properties in inline styles
- Set `position: relative` on any container that hosts a `.com-resizer`
- Load `universal_ui_design.css` before any page-specific stylesheets
- Load `universal_ui_design.js` before page-specific JS files
- Use `.com-btn-icon` for icon-only buttons (28×28px)
- Use `.com-truncate` for single-line text overflow
- Persist sidebar widths and theme selection to `localStorage`
- Use `comUI.*` functions instead of duplicating theme/sidebar/layout/toast logic in each page
- Call `comUI.modal.init()` on DOMContentLoaded for each modal overlay that needs background-click-to-close
- Use `comUI.toast.show()` instead of creating ad-hoc notification elements

### Pending Issues
| #  | Issue | Priority | Status |
|----|-------|----------|--------|
| 1  | EKS `eks.css` still uses non-standard token names (`--bg-primary`, `--error` etc.) — needs alignment | High | 🔷 Planned |
| 2  | DCC `dcc-design-system.css` has overlapping classes (`dcc-table`, `dcc-toast`) that duplicate com- versions | Medium | 🔷 Planned |
| 3  | code_tracer `code-tracer.css` also uses `dcc-` prefix — needs migration | Medium | 🔷 Planned |
| 4  | ✅ RESOLVED — Shared JS library `universal_ui_design.js` created with 8 modules | — | ✅ Done |
| 5  | No automated visual regression tests | Low | 🔷 Planned |
| 6  | Responsive / mobile layout not defined | Low | 🔷 Planned |
| 7  | DCC/EKS inline JS blocks not yet migrated to `comUI.*` calls | High | 🔷 Planned |

---

## 14. Development Test Results

| Test                           | Method                                | Status |
|--------------------------------|---------------------------------------|--------|
| Theme variables load           | Inspect `computedStyle` in browser    | ✅ Pass |
| Shell layout renders 4 zones   | Visual check                          | ✅ Pass |
| Sidebar collapse/expand        | Add/remove `.collapsed` class         | ✅ Pass |
| Accordion toggle               | Click header, observe chevron         | ✅ Pass |
| Button variants                | Visual check + hover state            | ✅ Pass |
| Badge colors match semantic    | Visual check                          | ✅ Pass |
| Table sort indicators          | Add `.sorted-asc`/`.sorted-desc`      | ✅ Pass |
| Tab active state               | Add `.active` class                   | ✅ Pass |
| Modal open/close               | Add/remove `.open` on overlay         | ✅ Pass |
| Toast show/hide                | Add/remove `.show`                    | ✅ Pass |
| Drop zone hover state          | Hover + `.drag-over`                  | ✅ Pass |
| Step progress states           | Apply `.active`/`.done`/`.fail`       | ✅ Pass |
| Animations play                | Visual check                          | ✅ Pass |
| Spinner animation              | Visual check                          | ✅ Pass |

---

## 15. Dependencies and Environment

| Dependency      | Version/Details                         |
|-----------------|-----------------------------------------|
| CSS spec        | CSS Custom Properties (Level 1)         |
| JS spec         | ECMAScript 5+ (no transpilation needed) |
| Browsers        | Chrome 90+, Firefox 90+, Edge 90+       |
| Build tools     | None (standalone CSS + JS, no bundler)  |
| External fonts  | None (uses system-ui stack)             |
| CSS file size   | ~41 KB / ~842 lines                     |
| JS file size    | ~12 KB / ~350 lines                     |

No JavaScript framework dependency. All components work with HTML + CSS + vanilla JS. The JS library provides optional interactivity for theme picker, sidebar drag-resize, accordion toggle, toasts, modals, file loading, sortable tables, and utility functions. Pages that do not need interactivity can include only the CSS file.

---

## 16. Coding/Programming Engineering Standard Achieved

| Standard              | Implementation                                                      |
|-----------------------|----------------------------------------------------------------------|
| Modularity            | 29 CSS sections + 8 JS modules, each independently usable           |
| Naming convention     | `com-` CSS prefix, `comUI` JS namespace, `sb-` sidebar — BEM-like    |
| Single source of truth| All CSS tokens in `:root` custom properties; JS logic in `comUI` namespace |
| DRY                   | No repeated color values or JS patterns; all via shared modules      |
| Progressive enhancement | Base layout works without JS; JS adds interactivity and polish     |
| Accessibility         | Semantic HTML assumed, color contrast via theme tokens               |
| Performance           | Two files, no imports, no render-blocking external resources          |
| Maintainability       | Clear section headers, documented module boundaries, consistent API  |
| Portability           | Works in any HTML page, no framework dependency                      |
| Security              | No inline JS event handlers in CSS; no CDN fonts (corporate-firewall safe) |

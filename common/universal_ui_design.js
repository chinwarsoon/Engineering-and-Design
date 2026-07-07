/* ════════════════════════════════════════════════
   universal_ui_design.js — Shared UI JavaScript
   Revision: 1.0 | Date: 2026-07-07 | Author: Dev
   Summary: Reusable JS modules for DCC, EKS, and
   code_tracer projects. Namespace: comUI
   Depends on: universal_ui_design.css (design tokens)
   Zero external dependencies.
════════════════════════════════════════════════ */
var comUI = window.comUI || {};

/* ════════════════════════════════════════════════
   1. THEME — apply, initPicker
═════════════════════════════════════════════════ */
comUI.theme = (function() {
  var NAMES = ['dark', 'light', 'sky', 'ocean', 'presentation'];
  var LABELS = { dark: 'Dark', light: 'Light', sky: 'Sky', ocean: 'Ocean', presentation: 'Presentation' };
  var COLORS = {
    dark: '#0d1117', light: '#ffffff',
    sky: '#0b1a2e', ocean: '#0a1929', presentation: '#000000'
  };

  function apply(name, storageKey) {
    document.documentElement.setAttribute('data-theme', name);
    if (storageKey) { try { localStorage.setItem(storageKey, name); } catch (e) {} }
    // Update active state in any theme picker on the page
    var opts = document.querySelectorAll('.com-theme-opt');
    for (var i = 0; i < opts.length; i++) {
      var opt = opts[i];
      if (opt.getAttribute('data-theme') === name) { opt.classList.add('active'); }
      else { opt.classList.remove('active'); }
    }
    // Update theme button label
    var btn = document.querySelector('.com-theme-btn');
    if (btn) {
      var dot = btn.querySelector('.com-theme-dot');
      if (dot) { dot.style.background = COLORS[name] || COLORS.dark; }
      var text = btn.lastChild;
      if (text && text.nodeType === 3) { text.textContent = ' ' + (LABELS[name] || name); }
    }
  }

  function initPicker(storageKey) {
    storageKey = storageKey || 'com-theme';
    var btn = document.querySelector('.com-theme-btn');
    var menu = document.querySelector('.com-theme-menu');
    if (!btn || !menu) return;
    // Toggle menu on button click
    btn.addEventListener('click', function(e) {
      e.stopPropagation();
      menu.classList.toggle('open');
    });
    // Close menu on outside click
    document.addEventListener('click', function() { menu.classList.remove('open'); });
    menu.addEventListener('click', function(e) { e.stopPropagation(); });
    // Option click handler
    var opts = menu.querySelectorAll('.com-theme-opt');
    for (var i = 0; i < opts.length; i++) {
      (function(opt) {
        opt.addEventListener('click', function() {
          var theme = opt.getAttribute('data-theme');
          comUI.theme.apply(theme, storageKey);
          menu.classList.remove('open');
        });
      })(opts[i]);
    }
    // Restore saved theme
    var saved = null;
    try { saved = localStorage.getItem(storageKey); } catch (e) {}
    if (saved && NAMES.indexOf(saved) !== -1) {
      comUI.theme.apply(saved, storageKey);
    }
  }

  return { apply: apply, initPicker: initPicker, NAMES: NAMES, LABELS: LABELS, COLORS: COLORS };
})();


/* ════════════════════════════════════════════════
   2. SIDEBAR — resize, accordion
═════════════════════════════════════════════════ */
comUI.sidebar = (function() {

  function resize(sbId, handleId, opts) {
    opts = opts || {};
    var minW = opts.min || 120;
    var maxW = opts.max || 480;
    var storageKey = opts.storageKey || null;
    var sb = document.getElementById(sbId);
    var handle = document.getElementById(handleId);
    if (!sb || !handle) return;

    var startX, startW;

    function onDown(e) {
      startX = e.clientX;
      startW = sb.offsetWidth;
      handle.classList.add('active');
      document.addEventListener('mousemove', onMove);
      document.addEventListener('mouseup', onUp);
      e.preventDefault();
    }

    function onMove(e) {
      var dx = e.clientX - startX;
      var w = startW + dx;
      if (w < minW) w = minW;
      if (w > maxW) w = maxW;
      sb.style.width = w + 'px';
    }

    function onUp() {
      handle.classList.remove('active');
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
      if (storageKey) {
        try { localStorage.setItem(storageKey, sb.style.width); } catch (e) {}
      }
    }

    handle.addEventListener('mousedown', onDown);

    // Restore saved width
    if (storageKey) {
      try {
        var saved = localStorage.getItem(storageKey);
        if (saved) { sb.style.width = saved; }
      } catch (e) {}
    }
  }

  function accordion(scopeEl) {
    if (!scopeEl) scopeEl = document;
    scopeEl.addEventListener('click', function(e) {
      var header = e.target.closest('.sb-section-header');
      if (header) {
        var section = header.parentElement;
        if (section && section.classList.contains('sb-section')) {
          section.classList.toggle('closed');
        }
      }
    });
  }

  return { resize: resize, accordion: accordion };
})();


/* ════════════════════════════════════════════════
   3. LAYOUT — toggle between 1/2/3 column modes
═════════════════════════════════════════════════ */
comUI.layout = (function() {
  var ICONS = ['🔲', '📐', '📦'];

  function toggle(btnId, opts) {
    opts = opts || {};
    var leftId = opts.leftSidebar || opts.left || null;
    var rightId = opts.rightSidebar || opts.right || null;
    var storageKey = opts.storageKey || 'com-layout';
    var mode = 0;

    // Restore saved mode
    try {
      var saved = parseInt(localStorage.getItem(storageKey), 10);
      if (!isNaN(saved) && saved >= 0 && saved <= 2) mode = saved;
    } catch (e) {}

    function applyMode(m) {
      mode = m;
      var left = leftId ? document.getElementById(leftId) : null;
      var right = rightId ? document.getElementById(rightId) : null;
      // Mode 0: both visible
      // Mode 1: left collapsed
      // Mode 2: right collapsed
      if (left) {
        left.classList.toggle('collapsed', m === 1);
      }
      if (right) {
        right.classList.toggle('collapsed', m === 2);
      }
      var btn = document.getElementById(btnId);
      if (btn) { btn.textContent = ICONS[m] || ICONS[0]; }
      try { localStorage.setItem(storageKey, m); } catch (e) {}
    }

    // Wire button click
    var btnEl = document.getElementById(btnId);
    if (btnEl) {
      btnEl.addEventListener('click', function() {
        applyMode((mode + 1) % 3);
      });
    }

    applyMode(mode);
  }

  return { toggle: toggle };
})();


/* ════════════════════════════════════════════════
   4. TOAST — show notification
═════════════════════════════════════════════════ */
comUI.toast = (function() {
  var TYPES = {
    success: { icon: '✓', cls: 'com-toast-success' },
    error:   { icon: '✗', cls: 'com-toast-error' },
    warning: { icon: '⚠', cls: 'com-toast-warning' },
    info:    { icon: 'ℹ', cls: 'com-toast-info' }
  };
  var timer = null;

  function ensureEl() {
    var el = document.getElementById('com-toast');
    if (!el) {
      el = document.createElement('div');
      el.id = 'com-toast';
      el.className = 'com-toast';
      document.body.appendChild(el);
    }
    return el;
  }

  function show(msg, type, duration) {
    type = type || 'info';
    duration = duration || 3500;
    var t = TYPES[type] || TYPES.info;
    var el = ensureEl();
    if (timer) { clearTimeout(timer); timer = null; }
    el.className = 'com-toast show ' + (t.cls || '');
    el.innerHTML = '<span class="com-toast-icon">' + t.icon + '</span> ' + msg;
    timer = setTimeout(function() {
      el.classList.remove('show');
      timer = null;
    }, duration);
  }

  return { show: show };
})();


/* ════════════════════════════════════════════════
   5. MODAL — simple open/close overlay
═════════════════════════════════════════════════ */
comUI.modal = (function() {

  function open(modalId) {
    var el = document.getElementById(modalId);
    if (el) el.classList.add('open');
  }

  function close(modalId) {
    var el = document.getElementById(modalId);
    if (el) el.classList.remove('open');
  }

  function init(modalId) {
    var overlay = document.getElementById(modalId);
    if (!overlay) return;
    // Close on overlay click (background)
    overlay.addEventListener('click', function(e) {
      if (e.target === overlay) overlay.classList.remove('open');
    });
    // Close on X button
    var closeBtn = overlay.querySelector('.com-modal-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', function() { overlay.classList.remove('open'); });
    }
  }

  return { open: open, close: close, init: init };
})();


/* ════════════════════════════════════════════════
   6. FILE — drag-drop zone, FileReader helpers
═════════════════════════════════════════════════ */
comUI.file = (function() {

  function setupDropZone(zoneId, onFile) {
    var zone = document.getElementById(zoneId);
    if (!zone) return;

    function prevent(e) { e.preventDefault(); e.stopPropagation(); }

    zone.addEventListener('dragenter', prevent);
    zone.addEventListener('dragover', function(e) {
      prevent(e);
      zone.classList.add('drag-over');
    });
    zone.addEventListener('dragleave', function() {
      zone.classList.remove('drag-over');
    });
    zone.addEventListener('drop', function(e) {
      prevent(e);
      zone.classList.remove('drag-over');
      var files = e.dataTransfer.files;
      if (files && files.length > 0 && onFile) {
        onFile(files);
      }
    });
  }

  function readFileAsText(file) {
    return new Promise(function(resolve, reject) {
      var reader = new FileReader();
      reader.onload = function() { resolve(reader.result); };
      reader.onerror = function() { reject(reader.error); };
      reader.readAsText(file);
    });
  }

  function readFileAsJSON(file) {
    return readFileAsText(file).then(function(text) {
      return JSON.parse(text);
    });
  }

  function readFileAsDataURL(file) {
    return new Promise(function(resolve, reject) {
      var reader = new FileReader();
      reader.onload = function() { resolve(reader.result); };
      reader.onerror = function() { reject(reader.error); };
      reader.readAsDataURL(file);
    });
  }

  return { setupDropZone: setupDropZone, readFileAsText: readFileAsText, readFileAsJSON: readFileAsJSON, readFileAsDataURL: readFileAsDataURL };
})();


/* ════════════════════════════════════════════════
   7. TABLE — sortable columns
═════════════════════════════════════════════════ */
comUI.table = (function() {

  function makeSortable(tableId) {
    var table = document.getElementById(tableId);
    if (!table) return;
    var thead = table.querySelector('thead');
    if (!thead) return;
    var ths = thead.querySelectorAll('th');
    for (var i = 0; i < ths.length; i++) {
      (function(colIdx, th) {
        // Add sort arrow placeholder
        var arrow = th.querySelector('.sort-arrow');
        if (!arrow) {
          arrow = document.createElement('span');
          arrow.className = 'sort-arrow';
          th.appendChild(arrow);
        }
        th.style.cursor = 'pointer';
        th.addEventListener('click', function() {
          sortByColumn(table, colIdx, th);
        });
      })(i, ths[i]);
    }
  }

  function sortByColumn(table, colIdx, th) {
    var tbody = table.querySelector('tbody');
    if (!tbody) return;
    var rows = Array.prototype.slice.call(tbody.querySelectorAll('tr'));
    if (rows.length === 0) return;

    // Determine direction
    var isAsc = !th.classList.contains('sorted-asc');
    // Clear all sort indicators
    var allTh = table.querySelectorAll('thead th');
    for (var i = 0; i < allTh.length; i++) {
      allTh[i].classList.remove('sorted-asc', 'sorted-desc');
    }
    th.classList.add(isAsc ? 'sorted-asc' : 'sorted-desc');

    // Helper to get cell text
    function getCellText(row) {
      var cells = row.querySelectorAll('td');
      if (cells.length <= colIdx) return '';
      return cells[colIdx].textContent.trim();
    }

    // Detect numeric vs string
    var firstVal = getCellText(rows[0]);
    var isNumeric = firstVal !== '' && !isNaN(parseFloat(firstVal)) && isFinite(firstVal);

    rows.sort(function(a, b) {
      var va = getCellText(a);
      var vb = getCellText(b);
      if (isNumeric) {
        var na = parseFloat(va) || 0;
        var nb = parseFloat(vb) || 0;
        return isAsc ? na - nb : nb - na;
      }
      return isAsc ? va.localeCompare(vb) : vb.localeCompare(va);
    });

    // Re-append sorted rows
    for (var r = 0; r < rows.length; r++) {
      tbody.appendChild(rows[r]);
    }
  }

  return { makeSortable: makeSortable };
})();


/* ════════════════════════════════════════════════
   8. UTILS — escHtml, formatNum, formatBytes, setStatus
═════════════════════════════════════════════════ */
comUI.utils = (function() {

  function escHtml(s) {
    if (s == null) return '';
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function formatNum(n) {
    if (n == null || isNaN(n)) return '\u2014';
    if (n >= 1000000) { return (n / 1000000).toFixed(1) + 'M'; }
    if (n >= 1000) { return (n / 1000).toFixed(1) + 'K'; }
    return String(n);
  }

  function formatBytes(bytes) {
    if (bytes == null || isNaN(bytes)) return '\u2014';
    if (bytes === 0) return '0 B';
    var units = ['B', 'KB', 'MB', 'GB', 'TB'];
    var i = Math.floor(Math.log(bytes) / Math.log(1024));
    if (i >= units.length) i = units.length - 1;
    return (bytes / Math.pow(1024, i)).toFixed(i > 0 ? 1 : 0) + ' ' + units[i];
  }

  function setStatus(el, msg) {
    if (!el) return;
    if (typeof el === 'string') { el = document.getElementById(el); }
    if (el) { el.textContent = msg; }
  }

  function setStatusBar(leftMsg, rightMsg) {
    var left = document.querySelector('.com-statusbar-left');
    var right = document.querySelector('.com-statusbar-right');
    if (left && leftMsg != null) left.textContent = leftMsg;
    if (right && rightMsg != null) right.textContent = rightMsg;
  }

  return { escHtml: escHtml, formatNum: formatNum, formatBytes: formatBytes, setStatus: setStatus, setStatusBar: setStatusBar };
})();

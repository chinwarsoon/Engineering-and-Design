/* EKS Dashboard JavaScript — AGENTS.md §18 + G7 UI Contracts
   Revision: 2.0 | Date: 2026-07-07 | Author: Dev
   Summary: EKS business logic using comUI from common/universal_ui_design.js. */
(function () {
  'use strict';

  var PU = comUI.utils;

  const POLL_INTERVAL = 2000;

  /* ── State ── */
  const state = {
    docs: [],
    selectedDoc: null,
    jobId: null,
    pollTimer: null,
    logTimer: null,
    treeData: null,
    layout: localStorage.getItem('eks_layout') || 'triple',
    sidebarLeft: localStorage.getItem('eks_sidebar_left') !== 'false',
    sidebarRight: localStorage.getItem('eks_sidebar_right') !== 'false',
    paths: { data_dir: 'eks/data' },
  };

  /* ── Help Content ── */
  let helpData = null;

  async function loadHelp() {
    try {
      const r = await fetch('ui_help.json');
      helpData = await r.json();
    } catch (e) {
      helpData = { about: 'EKS Dashboard', help: {}, definitions: {} };
    }
  }

  function getHelp(key) {
    return helpData && helpData.help ? (helpData.help[key] || 'No help available.') : 'Loading...';
  }

  /* ── Config Paths ── */
  async function fetchPaths() {
    try {
      const data = await apiGet('/api/v1/config/paths');
      state.paths = {
        data_dir: data.data_dir || 'eks/data',
        global_paths: data.global_paths || {},
      };
      var pathInput = document.getElementById('folder-path');
      if (pathInput) pathInput.value = state.paths.data_dir;
    } catch (e) {
      state.paths = { data_dir: 'eks/data', global_paths: {} };
    }
  }

  /* ── Layout ── */
  function applyLayout(l) {
    var left = document.getElementById('left-sidebar');
    var right = document.getElementById('right-sidebar');
    left.classList.toggle('collapsed', l === 'single' || (l === 'dual' && !state.sidebarLeft));
    if (l === 'single') {
      left.classList.add('collapsed');
      right.classList.add('collapsed');
    } else if (l === 'dual') {
      left.classList.remove('collapsed');
      right.classList.add('collapsed');
    } else {
      left.classList.remove('collapsed');
      right.classList.remove('collapsed');
    }
    localStorage.setItem('eks_layout', l);
    state.layout = l;
    state.sidebarLeft = l !== 'single';
    state.sidebarRight = l === 'triple';
  }

  /* ── API helpers ── */
  async function apiGet(path) {
    const r = await fetch(path);
    if (!r.ok) {
      const body = await r.text();
      if (r.status === 503) {
        throw new Error('Phase 1 backend not running. Start it and refresh.\nCommand: python eks/ui/backend/phase1_server.py');
      }
      throw new Error(body);
    }
    return r.json();
  }

  async function apiPost(path, body) {
    const r = await fetch(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!r.ok) {
      const bodyText = await r.text();
      if (r.status === 503) {
        throw new Error('Phase 1 backend not running. Start it and refresh.\nCommand: python eks/ui/backend/phase1_server.py');
      }
      throw new Error(bodyText);
    }
    return r.json();
  }

  async function apiPut(path, body) {
    const r = await fetch(path, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!r.ok) {
      const bodyText = await r.text();
      if (r.status === 503) {
        throw new Error('Phase 1 backend not running. Start it and refresh.\nCommand: python eks/ui/backend/phase1_server.py');
      }
      throw new Error(bodyText);
    }
    return r.json();
  }

  async function apiDelete(path) {
    const r = await fetch(path, { method: 'DELETE' });
    if (!r.ok) {
      const bodyText = await r.text();
      if (r.status === 503) {
        throw new Error('Phase 1 backend not running. Start it and refresh.\nCommand: python eks/ui/backend/phase1_server.py');
      }
      throw new Error(bodyText);
    }
    return r.json();
  }

  /* ── File Load ── */
  async function loadFiles(dir) {
    const path = dir || getFolderPath();
    var pathInput = document.getElementById('folder-path');
    if (pathInput) pathInput.value = path;
    var btn = document.getElementById('btn-load-files');
    if (btn) { btn.disabled = true; btn.textContent = 'Loading...'; }
    PU.setStatus('status-text', 'Loading documents from ' + path + '...');
    try {
      await apiPost('/api/v1/files/load', { data_dir: path });
      const docData = await apiGet('/api/v1/documents');
      state.docs = docData.documents || [];
      renderDocTable(state.docs);
      renderKPICards(state.docs);
      buildTree(state.docs);
      PU.setStatus('status-text', 'Loaded ' + state.docs.length + ' documents');
      showLoadSummary(state.docs.length);
      updateStepProgress(2, [1]);
      hideAllTabs();
      showTab('documents');
    } catch (e) {
      PU.setStatus('status-text', 'Load error: ' + e.message);
      comUI.toast.show('Load failed: ' + e.message, 'error', 6000);
    } finally {
      if (btn) { btn.disabled = false; btn.textContent = '📂 Load Files'; }
    }
  }

  function showLoadSummary(count) {
    var el = document.getElementById('load-summary');
    var text = document.getElementById('load-summary-text');
    var proceed = document.getElementById('proceed-container');
    if (!el || !text) return;
    if (count > 0) {
      el.style.display = 'flex';
      text.textContent = count + ' documents loaded from ' + getFolderPath();
      if (proceed) proceed.style.display = 'block';
    } else {
      el.style.display = 'none';
      if (proceed) proceed.style.display = 'none';
    }
  }

  /* ── KPI Cards ── */
  function renderKPICards(docs) {
    var grid = document.getElementById('kpi-grid');
    if (!grid) return;
    if (!docs || docs.length === 0) { grid.style.display = 'none'; return; }
    var total = docs.length;
    var processed = docs.filter(function (d) { return d.extract_status === 'completed' || d.health_score; }).length;
    var flagged = docs.filter(function (d) { return d.flag_reason; }).length;
    var locked = docs.filter(function (d) { return d.locked; }).length;
    var avgScore = docs.reduce(function (s, d) { return s + (d.health_score || 0); }, 0) / total;
    grid.style.display = 'grid';
    grid.innerHTML = ''
      + '<div class="kpi-card" onclick="switchTab(\'documents\')"><div class="kpi-value">' + total + '</div><div class="kpi-label">Total Documents</div><div class="kpi-sublabel">Loaded</div><div class="kpi-gauge"></div></div>'
      + '<div class="kpi-card" onclick="switchTab(\'pipeline\')"><div class="kpi-value">' + processed + '</div><div class="kpi-label">Processed</div><div class="kpi-sublabel">' + Math.round(processed/total*100) + '% of total</div><div class="kpi-gauge"></div></div>'
      + '<div class="kpi-card" onclick="switchTab(\'review\')"><div class="kpi-value">' + flagged + '</div><div class="kpi-label">Flagged</div><div class="kpi-sublabel">Needs review</div><div class="kpi-gauge"></div></div>'
      + '<div class="kpi-card"><div class="kpi-value">' + locked + '</div><div class="kpi-label">Locked</div><div class="kpi-sublabel">Approved</div><div class="kpi-gauge"></div></div>'
      + '<div class="kpi-card" onclick="switchTab(\'health\')"><div class="kpi-value">' + (avgScore*100).toFixed(0) + '%</div><div class="kpi-label">Avg Health</div><div class="kpi-sublabel">Overall score</div><div class="kpi-gauge"></div></div>';
  }

  /* ── Stage Cards ── */
  var STAGES = [
    { key: 'scan',     icon: '🔍', name: 'Scan',     desc: 'Discover files in data folder' },
    { key: 'parse',    icon: '📄', name: 'Parse',    desc: 'Extract content from files' },
    { key: 'score',    icon: '📊', name: 'Score',    desc: 'Compute health scores' },
    { key: 'review',   icon: '📋', name: 'Review',   desc: 'Flag issues for review' },
    { key: 'register', icon: '💾', name: 'Register', desc: 'Save to document registry' },
  ];

  // Maps orchestrator stage key → index in STAGES array
  // Phase A=scan(0), Phase B=parse(1)+score(2), Phase C=review(3), done=register(4)
  var STAGE_IDX = { scan: 0, parse: 1, score: 2, review: 3, register: 4 };

  function renderStageCards(data) {
    var container = document.getElementById('stage-cards');
    if (!container) return;
    var overallStatus = data.status || 'pending';
    var activeIdx = STAGE_IDX[data.current_stage] ?? -1;
    var html = '';
    STAGES.forEach(function (s, i) {
      var cardStatus;
      if (overallStatus === 'completed') {
        cardStatus = 'pass';
      } else if (overallStatus === 'failed') {
        cardStatus = i < activeIdx ? 'pass' : (i === activeIdx ? 'fail' : 'pending');
      } else if (overallStatus === 'running') {
        cardStatus = i < activeIdx ? 'pass' : (i === activeIdx ? 'running' : 'pending');
      } else {
        cardStatus = 'pending';
      }
      html += '<div class="stage-card">'
        + '<span class="stage-icon">' + s.icon + '</span>'
        + '<div class="stage-info"><div class="stage-name">' + s.name + '</div><div class="stage-meta">' + s.desc + '</div></div>'
        + '<span class="stage-status ' + cardStatus + '">' + cardStatus.toUpperCase() + '</span>'
        + '<div class="stage-bar"><div class="stage-bar-fill ' + cardStatus + '" style="width:' + (cardStatus === 'pass' ? 100 : cardStatus === 'running' ? 50 : 0) + '%"></div></div>'
        + '</div>';
    });
    container.innerHTML = html;
  }

  /* ── Directory Tree Browse ── */
  async function toggleDirTree() {
    var tree = document.getElementById('dir-tree');
    if (!tree) return;
    var isOpen = tree.style.display === 'block';
    tree.style.display = isOpen ? 'none' : 'block';
    if (isOpen) return;
    var root = 'eks/data';
    var current = getFolderPath() || root;
    tree.innerHTML = '<div class="dir-tree-loading">Loading...</div>';
    try {
      var data = await apiGet('/api/v1/files/list-dirs?parent=' + encodeURIComponent(root));
      tree.innerHTML = buildDirTreeNodes(data.dirs, root);
      bindDirTreeEvents(tree);
      // Auto-expand the path from root to the currently selected folder
      if (current !== root) {
        autoExpandPath(tree, root, current);
      }
    } catch (e) {
      tree.innerHTML = '<div class="dir-tree-empty">Error: ' + PU.escHtml(e.message) + '</div>';
    }
  }

  async function autoExpandPath(tree, root, target) {
    var parts = target.replace(root + '/', '').split('/');
    var current = root;
    var container = tree;
    for (var i = 0; i < parts.length; i++) {
      if (!parts[i]) continue;
      current = current + '/' + parts[i];
      var node = container.querySelector('.dir-tree-node[data-path="' + PU.escHtml(current) + '"]');
      if (node) {
        var toggle = node.querySelector('.dir-tree-toggle');
        if (toggle && !toggle.classList.contains('empty')) {
          // Expand this node
          await toggleDirTreeNode(node, current);
          // After expanding, the children wrapper is the next sibling
          container = node.nextElementSibling;
        } else {
          break;
        }
      } else {
        break;
      }
    }
  }

  function buildDirTreeNodes(dirs, parent) {
    if (!dirs || dirs.length === 0) {
      return '<div class="dir-tree-empty">No subdirectories found</div>';
    }
    var html = '<div class="dir-tree-node selected" data-path="' + PU.escHtml(parent) + '">'
      + '<span class="dir-tree-toggle empty">▶</span>'
      + '<span class="dir-tree-icon">📁</span>'
      + '<span class="dir-tree-label">' + PU.escHtml(parent) + '</span>'
      + '</div>';
    dirs.forEach(function (d) {
      var label = d.split('/').pop();
      html += '<div class="dir-tree-node" data-path="' + PU.escHtml(d) + '" data-expandable="true">'
        + '<span class="dir-tree-toggle">▶</span>'
        + '<span class="dir-tree-icon">📁</span>'
        + '<span class="dir-tree-label">' + PU.escHtml(label) + '</span>'
        + '</div>';
    });
    return html;
  }

  function bindDirTreeEvents(root) {
    root.querySelectorAll('.dir-tree-node').forEach(function (node) {
      node.addEventListener('click', function (e) {
        e.stopPropagation();
        var path = node.dataset.path;
        var toggle = node.querySelector('.dir-tree-toggle');
        if (e.target === toggle || toggle && toggle.contains(e.target)) {
          if (toggle.classList.contains('empty')) return;
          toggleDirTreeNode(node, path);
        } else {
          selectDirTreeNode(node, path);
          var tree = document.getElementById('dir-tree');
          if (tree) tree.style.display = 'none';
        }
      });
    });
  }

  async function toggleDirTreeNode(node, path) {
    var toggle = node.querySelector('.dir-tree-toggle');
    var childrenContainer = node.nextElementSibling;
    if (childrenContainer && childrenContainer.classList.contains('dir-tree-children')) {
      childrenContainer.style.display = childrenContainer.style.display === 'none' ? 'block' : 'none';
      toggle.textContent = childrenContainer.style.display === 'block' ? '▼' : '▶';
      return;
    }
    toggle.textContent = '⏳';
    try {
      var data = await apiGet('/api/v1/files/list-dirs?parent=' + encodeURIComponent(path));
      var childHtml = '<div class="dir-tree-children">';
      if (data.dirs && data.dirs.length > 0) {
        data.dirs.forEach(function (d) {
          var label = d.split('/').pop();
          childHtml += '<div class="dir-tree-node" data-path="' + PU.escHtml(d) + '">'
            + '<span class="dir-tree-toggle">▶</span>'
            + '<span class="dir-tree-icon">📁</span>'
            + '<span class="dir-tree-label">' + PU.escHtml(label) + '</span>'
            + '</div>';
        });
      } else {
        childHtml += '<div class="dir-tree-empty">Empty</div>';
      }
      childHtml += '</div>';
      toggle.textContent = '▼';
      node.parentNode.insertBefore(htmlToElement(childHtml), node.nextSibling);
      bindDirTreeEvents(node.nextElementSibling);
    } catch (e) {
      toggle.textContent = '▶';
    }
  }

  function selectDirTreeNode(node, path) {
    var tree = document.getElementById('dir-tree');
    if (tree) {
      tree.querySelectorAll('.dir-tree-node.selected').forEach(function (n) {
        n.classList.remove('selected');
      });
    }
    node.classList.add('selected');
    var input = document.getElementById('folder-path');
    if (input) input.value = path;
    if (tree) tree.style.display = 'none';
  }

  function htmlToElement(html) {
    var div = document.createElement('div');
    div.innerHTML = html;
    return div.firstElementChild;
  }

  /* ── Doc Table with Sort + 50-row cap + Active Highlight ── */
  var _sortCol = null;
  var _sortDir = 'asc';
  var _showAll = false;

  function renderDocTable(docs) {
    var el = document.getElementById('doc-table-body');
    if (!docs || docs.length === 0) {
      el.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--text2);padding:20px;">No documents found</td></tr>';
      document.getElementById('doc-table-footer') && (document.getElementById('doc-table-footer').style.display = 'none');
      return;
    }
    // Sort in-place
    var sorted = [].concat(docs);
    if (_sortCol) {
      sorted.sort(function (a, b) {
        var av = String(a[_sortCol] || '');
        var bv = String(b[_sortCol] || '');
        var cmp = av.localeCompare(bv, undefined, { numeric: true });
        return _sortDir === 'asc' ? cmp : -cmp;
      });
    }
    // Apply 50-row cap
    var display = _showAll ? sorted : sorted.slice(0, 50);
    var html = display.map(function (d) {
      var score = d.health_score || 0;
      var cls = score >= 0.7 ? 'health-high' : score >= 0.4 ? 'health-medium' : 'health-low';
      return '<tr data-doc-id="' + PU.escHtml(d.document_number || d.file_path || '') + '">'
        + '<td>' + PU.escHtml(d.document_number || '-') + '</td>'
        + '<td>' + PU.escHtml(d.type || '-') + '</td>'
        + '<td>' + PU.escHtml(d.discipline || '-') + '</td>'
        + '<td>' + PU.escHtml(d.revision || '-') + '</td>'
        + '<td><span class="health-badge ' + cls + '">' + score.toFixed(2) + '</span></td>'
        + '</tr>';
    }).join('');
    el.innerHTML = html;
    // Row click → select + highlight
    el.querySelectorAll('tr').forEach(function (tr) {
      tr.addEventListener('click', function () {
        var id = tr.getAttribute('data-doc-id');
        // Remove active highlight from all rows
        el.querySelectorAll('tr.selected').forEach(function (r) { r.classList.remove('selected'); });
        tr.classList.add('selected');
        selectDocument(id);
      });
    });
    // Update sort indicators in header
    var ths = document.querySelectorAll('.doc-table th[data-col]');
    ths.forEach(function (th) {
      var col = th.getAttribute('data-col');
      th.innerHTML = th.getAttribute('data-label') + (col === _sortCol ? (_sortDir === 'asc' ? ' ▲' : ' ▼') : '');
    });
    // Update footer
    var footer = document.getElementById('doc-table-footer');
    if (footer) {
      if (docs.length > 50 && !_showAll) {
        footer.style.display = 'block';
        footer.innerHTML = 'Showing 50 of ' + docs.length + ' documents. <a href="#" onclick="return showAllDocs()" style="color:var(--accent);cursor:pointer;">Show all ' + docs.length + '</a>.';
      } else if (docs.length > 50 && _showAll) {
        footer.style.display = 'block';
        footer.innerHTML = 'Showing all ' + docs.length + ' documents. <a href="#" onclick="return showLimitedDocs()" style="color:var(--accent);cursor:pointer;">Show first 50</a>.';
      } else {
        footer.style.display = 'block';
        footer.innerHTML = docs.length + ' document(s)';
      }
    }
  }

  window.showAllDocs = function () { _showAll = true; renderDocTable(state.docs); return false; };
  window.showLimitedDocs = function () { _showAll = false; renderDocTable(state.docs); return false; };

  function initTableSort() {
    var ths = document.querySelectorAll('.doc-table th[data-col]');
    ths.forEach(function (th) {
      th.addEventListener('click', function () {
        var col = th.getAttribute('data-col');
        if (_sortCol === col) {
          _sortDir = _sortDir === 'asc' ? 'desc' : 'asc';
        } else {
          _sortCol = col;
          _sortDir = 'asc';
        }
        renderDocTable(state.docs);
      });
    });
  }

  function selectDocument(id) {
    var doc = state.docs.find(function (d) { return (d.document_number || d.file_path) === id; });
    if (!doc) return;
    state.selectedDoc = doc;
    // Switch to detail accordion view
    document.getElementById('sb-settings')?.classList.add('closed');
    document.getElementById('sb-help')?.classList.add('closed');
    document.getElementById('sb-detail')?.classList.remove('closed');
    document.getElementById('sb-title').textContent = 'Detail';
    document.getElementById('sb-back').style.display = 'none';
    showDetail(doc);
    document.getElementById('right-sidebar').classList.remove('collapsed');
    state.sidebarRight = true;
    localStorage.setItem('eks_sidebar_right', 'true');
  }

  function showDetail(doc) {
    var el = document.getElementById('detail-content');
    var score = doc.health_score || 0;
    var s = '<div class="detail-section">'
      + '<h4>Document Info</h4>'
      + '<div class="detail-row"><span class="detail-label">Number</span><span class="detail-value">' + PU.escHtml(doc.document_number || '-') + '</span></div>'
      + '<div class="detail-row"><span class="detail-label">Type</span><span class="detail-value">' + PU.escHtml(doc.type || '-') + '</span></div>'
      + '<div class="detail-row"><span class="detail-label">Discipline</span><span class="detail-value">' + PU.escHtml(doc.discipline || '-') + '</span></div>'
      + '<div class="detail-row"><span class="detail-label">Revision</span><span class="detail-value">' + PU.escHtml(doc.revision || '-') + '</span></div>'
      + '<div class="detail-row"><span class="detail-label">File</span><span class="detail-value">' + PU.escHtml(doc.file_path || '-') + '</span></div>'
      + '<div class="detail-row"><span class="detail-label">Status</span><span class="detail-value">' + PU.escHtml(doc.extract_status || 'pending') + '</span></div>'
      + '</div>'
      + '<div class="detail-section"><h4>Health Score</h4>'
      + '<div class="detail-row"><span class="detail-label">Overall</span><span class="detail-value"><span class="health-badge ' + (score>=0.7?'health-high':score>=0.4?'health-medium':'health-low') + '">' + score.toFixed(2) + '</span></span></div>'
      + renderScoreBar('Completeness', doc.completeness || score, '#4ec9b0')
      + renderScoreBar('Confidence', doc.confidence || score, '#9cdcfe')
      + renderScoreBar('Consistency', doc.consistency || score, '#dcdcaa')
      + renderScoreBar('Timeliness', doc.timeliness || score, '#ce9178')
      + renderScoreBar('Accessibility', doc.accessibility || score, '#c586c0')
      + renderScoreBar('Structural', doc.structural_completeness || score, '#6a9955')
      + '</div>';
    el.innerHTML = s;
  }

  function renderScoreBar(label, value, color) {
    var pct = Math.round((value || 0) * 100);
    return '<div class="score-bar"><span class="label">' + label + '</span><div class="bar-track"><div class="bar-fill" style="width:' + pct + '%;background:' + color + '"></div></div><span style="font-size:11px;color:var(--text2);">' + pct + '%</span></div>';
  }

  /* ── Tree ── */
  function buildTree(docs) {
    var tree = {};
    docs.forEach(function (d) {
      var disc = d.discipline || 'Unknown';
      var type = d.type || 'Unknown';
      if (!tree[disc]) tree[disc] = {};
      if (!tree[disc][type]) tree[disc][type] = [];
      tree[disc][type].push(d);
    });
    state.treeData = tree;
    renderTree(tree);
  }

  function renderTree(tree) {
    var el = document.getElementById('tree-content');
    if (!tree || Object.keys(tree).length === 0) {
      el.innerHTML = '<div class="empty-state"><p>No documents loaded</p></div>';
      return;
    }
    var html = '';
    Object.keys(tree).sort().forEach(function (disc) {
      html += '<div class="tree-node" data-expandable="true"><span class="toggle">▶</span>' + PU.escHtml(disc) + '<div class="tree-node children" style="display:none">';
      Object.keys(tree[disc]).sort().forEach(function (type) {
        html += '<div class="tree-node" data-expandable="true"><span class="toggle">▶</span>' + PU.escHtml(type) + '<div class="tree-node children" style="display:none">';
        tree[disc][type].forEach(function (d) {
          var id = d.document_number || d.file_path || '';
          html += '<div class="tree-node" data-doc-id="' + PU.escHtml(id) + '">' + PU.escHtml(d.document_number || d.file_path) + '</div>';
        });
        html += '</div></div>';
      });
      html += '</div></div>';
    });
    el.innerHTML = html;
    el.querySelectorAll('[data-expandable="true"]').forEach(function (node) {
      node.addEventListener('click', function (e) {
        e.stopPropagation();
        var children = node.querySelector(':scope > .children');
        var toggle = node.querySelector(':scope > .toggle');
        if (children) {
          var isHidden = children.style.display === 'none';
          children.style.display = isHidden ? 'block' : 'none';
          if (toggle) toggle.textContent = isHidden ? '▼' : '▶';
        }
      });
    });
    el.querySelectorAll('[data-doc-id]').forEach(function (node) {
      node.addEventListener('click', function () {
        selectDocument(node.getAttribute('data-doc-id'));
      });
    });
  }

  /* ── Pipeline ── */
  function getFolderPath() {
    var input = document.getElementById('folder-path');
    return input && input.value ? input.value : state.paths.data_dir;
  }

  async function startPipeline() {
    var btn = document.getElementById('btn-run-pipeline');
    btn.disabled = true;
    btn.textContent = 'Starting...';
    try {
      var result = await apiPost('/api/v1/pipeline/start', { data_dir: getFolderPath(), recursive: true });
      state.jobId = result.job_id;
      PU.setStatus('status-text', 'Pipeline started: ' + state.jobId);
      btn.textContent = 'Running...';
      updateStepProgress(2, [1]);
      showPipelineTab(state.jobId);
      startPolling(state.jobId);
      startLogPolling(state.jobId);
    } catch (e) {
      PU.setStatus('status-text', 'Pipeline error: ' + e.message);
      btn.disabled = false;
      btn.textContent = 'Run Pipeline';
    }
  }

  function startPolling(jobId) {
    if (state.pollTimer) clearInterval(state.pollTimer);
    state.pollTimer = setInterval(function () {
      apiGet('/api/v1/pipeline/status/' + jobId).then(function (data) {
        updatePipelineStatus(data);
        if (data.status === 'completed' || data.status === 'failed' || data.status === 'cancelled') {
          clearInterval(state.pollTimer);
          state.pollTimer = null;
          document.getElementById('btn-run-pipeline').disabled = false;
          document.getElementById('btn-run-pipeline').textContent = 'Run Pipeline';
          if (data.status === 'completed') {
            updateStepProgress(3, [1, 2]);
          }
        }
      }).catch(function () {});
    }, POLL_INTERVAL);
  }

  function startLogPolling(jobId) {
    if (state.logTimer) clearInterval(state.logTimer);
    state.logTimer = setInterval(function () {
      apiGet('/api/v1/pipeline/logs/' + jobId).then(function (data) {
        if (data.logs) renderLogs(data.logs);
      }).catch(function () {});
    }, POLL_INTERVAL);
  }

  function updatePipelineStatus(data) {
    var el = document.getElementById('pipeline-status');
    var label = data.status + ' (' + data.progress + '%)';
    if (data.status === 'failed' && data.error) label += ' — ' + data.error;
    el.textContent = 'Status: ' + label;
    document.getElementById('pipeline-progress').style.width = data.progress + '%';
    renderStageCards(data);
    if (data.summary) {
      document.getElementById('pipeline-summary').textContent = JSON.stringify(data.summary, null, 2);
    }
  }

  function renderLogs(logs) {
    var el = document.getElementById('pipeline-logs');
    el.innerHTML = logs.map(function (e) {
      var cls = 'log-' + e.level.toLowerCase();
      return '<div class="' + cls + '">[' + e.level + '] ' + PU.escHtml(e.message) + '</div>';
    }).join('');
    el.scrollTop = el.scrollHeight;
  }

  async function cancelPipeline() {
    if (!state.jobId) return;
    try {
      await apiDelete('/api/v1/pipeline/' + state.jobId);
      PU.setStatus('status-text', 'Pipeline cancelled');
    } catch (e) {
      PU.setStatus('status-text', 'Cancel error: ' + e.message);
    }
  }

  function showPipelineTab(jobId) {
    hideAllTabs();
    showTab('pipeline');
    document.getElementById('pipeline-status').textContent = 'Status: queued (0%)';
    document.getElementById('pipeline-progress').style.width = '0%';
    document.getElementById('pipeline-logs').innerHTML = '';
    document.getElementById('pipeline-summary').textContent = '';
    renderStageCards({ status: 'queued', progress: 0 });
  }

  /* ── Review ── */
  async function showReview() {
    try {
      var data = await apiGet('/api/v1/review/summary');
      updateStepProgress(3, [1, 2]);
      hideAllTabs();
      showTab('review');
      var el = document.getElementById('review-content');
      var flagged = data.flagged_documents || [];
      if (flagged.length === 0) {
        el.innerHTML = '<div class="empty-state"><p>No documents flagged for review</p></div>';
        return;
      }
      var html = '<h3 style="margin-bottom:8px;">Flagged Documents (' + flagged.length + ')</h3>';
      flagged.forEach(function (doc) {
        html += '<div class="detail-section" style="border:1px solid var(--border);border-radius:4px;padding:8px;margin-bottom:8px;">'
          + '<div class="detail-row"><span class="detail-label">Document</span><span class="detail-value">' + PU.escHtml(doc.document_number || '-') + '</span></div>'
          + '<div class="detail-row"><span class="detail-label">Reason</span><span class="detail-value">' + PU.escHtml(doc.flag_reason || 'Unknown') + '</span></div>'
          + '<div style="margin-top:8px;"><button class="com-btn com-btn-primary com-btn-sm" onclick="eksReviewDoc(\'' + PU.escHtml(doc.document_number || '') + '\')">Review</button></div>'
          + '</div>';
      });
      el.innerHTML = html;
    } catch (e) {
      PU.setStatus('status-text', 'Review error: ' + e.message);
    }
  }

  window.eksReviewDoc = function (docId) {
    document.getElementById('review-content').innerHTML = '<div class="review-form">'
      + '<h4>Review: ' + PU.escHtml(docId) + '</h4>'
      + '<label>Document Number</label><input id="rev-doc-number" value="' + PU.escHtml(docId) + '" />'
      + '<label>Revision</label><input id="rev-revision" placeholder="e.g., A, B, C" />'
      + '<label>Status</label><select id="rev-status"><option value="locked">Locked (Approved)</option><option value="flagged">Flagged (Needs Work)</option></select>'
      + '<label>Comments</label><textarea id="rev-comments" placeholder="Review comments..."></textarea>'
      + '<button onclick="eksSubmitReview()">Submit Review</button>'
      + '</div>';
  };

  window.eksSubmitReview = async function () {
    var docNumber = document.getElementById('rev-doc-number').value;
    var comments = document.getElementById('rev-comments').value;
    var status = document.getElementById('rev-status').value;
    try {
      await apiPut('/api/v1/review/lock', {
        doc_id: docNumber,
        verified_by: 'reviewer',
        comments: comments,
      });
      PU.setStatus('status-text', 'Review submitted for ' + docNumber);
      showReview();
    } catch (e) {
      PU.setStatus('status-text', 'Submit error: ' + e.message);
    }
  };

  /* ── Health Score Chart ── */
  function renderHealthChart() {
    var canvas = document.getElementById('health-chart-canvas');
    if (!canvas) return;
    var ctx = canvas.getContext('2d');
    if (typeof Chart === 'undefined') {
      var s = document.createElement('script');
      s.src = '/ui/static/chart.min.js';
      s.onload = function () { renderChart(ctx); };
      document.head.appendChild(s);
    } else {
      renderChart(ctx);
    }
  }

  function renderChart(ctx) {
    var scores = state.docs.length > 0 ? aggregateScores(state.docs) : { labels: ['No Data'], values: [0] };
    new Chart(ctx, {
      type: 'radar',
      data: {
        labels: ['Completeness', 'Confidence', 'Consistency', 'Timeliness', 'Accessibility', 'Structural'],
        datasets: [{
          label: 'Average Health Score',
          data: [scores.completeness || 0, scores.confidence || 0, scores.consistency || 0, scores.timeliness || 0, scores.accessibility || 0, scores.structural || 0],
          backgroundColor: 'rgba(55, 148, 255, 0.2)',
          borderColor: 'rgba(55, 148, 255, 1)',
          borderWidth: 2,
          pointBackgroundColor: 'rgba(55, 148, 255, 1)',
        }]
      },
      options: {
        responsive: true,
        scales: { r: { min: 0, max: 1, ticks: { stepSize: 0.2 } } },
        plugins: {
          legend: { display: false },
        }
      }
    });
    document.querySelector('#health-chart .empty-state')?.remove();
  }

  function aggregateScores(docs) {
    var total = docs.length;
    if (total === 0) return { completeness: 0, confidence: 0, consistency: 0, timeliness: 0, accessibility: 0, structural: 0 };
    var agg = { completeness: 0, confidence: 0, consistency: 0, timeliness: 0, accessibility: 0, structural: 0 };
    docs.forEach(function (d) {
      agg.completeness += d.completeness || d.health_score || 0;
      agg.confidence += d.confidence || d.health_score || 0;
      agg.consistency += d.consistency || d.health_score || 0;
      agg.timeliness += d.timeliness || d.health_score || 0;
      agg.accessibility += d.accessibility || d.health_score || 0;
      agg.structural += d.structural_completeness || d.health_score || 0;
    });
    Object.keys(agg).forEach(function (k) { agg[k] = agg[k] / total; });
    return agg;
  }

  /* ── Settings (renders in right sidebar) ── */
  function showSettings() {
    var sb = document.getElementById('right-sidebar');
    if (sb) sb.classList.remove('collapsed');
    state.sidebarRight = true;
    localStorage.setItem('eks_sidebar_right', 'true');
    document.getElementById('sb-back').style.display = '';
    // Expand settings section, collapse others
    document.getElementById('sb-detail')?.classList.add('closed');
    document.getElementById('sb-help')?.classList.add('closed');
    document.getElementById('sb-settings')?.classList.remove('closed');
    document.getElementById('sb-title').textContent = 'Settings';
    var theme = document.documentElement.getAttribute('data-theme') || 'dark';
    document.getElementById('sb-settings-content').innerHTML = ''
      + '<div class="setting-row"><label>Theme</label><select id="setting-theme" onchange="eksSetTheme(this.value)">'
      + '<option value="dark" ' + (theme === 'dark' ? 'selected' : '') + '>Dark</option>'
      + '<option value="light" ' + (theme === 'light' ? 'selected' : '') + '>Light</option>'
      + '<option value="sky" ' + (theme === 'sky' ? 'selected' : '') + '>Sky</option>'
      + '<option value="ocean" ' + (theme === 'ocean' ? 'selected' : '') + '>Ocean</option>'
      + '<option value="presentation" ' + (theme === 'presentation' ? 'selected' : '') + '>Presentation</option>'
      + '</select></div>'
      + '<div class="setting-row"><label>Layout</label><select id="setting-layout" onchange="eksSetLayout(this.value)">'
      + '<option value="single" ' + (state.layout === 'single' ? 'selected' : '') + '>Single</option>'
      + '<option value="dual" ' + (state.layout === 'dual' ? 'selected' : '') + '>Dual</option>'
      + '<option value="triple" ' + (state.layout === 'triple' ? 'selected' : '') + '>Triple</option>'
      + '</select></div>'
      + '<div class="setting-row"><label>Poll Interval (ms)</label><input type="number" id="setting-poll" value="' + POLL_INTERVAL + '" min="500" step="500" /></div>';
  }

  window.eksSetTheme = function (t) { comUI.theme.apply(t, 'eks-theme'); };
  window.eksSetLayout = function (l) { applyLayout(l); };

  /* ── Help (renders in right sidebar instead of modal) ── */
  function showHelp() {
    var sb = document.getElementById('right-sidebar');
    if (sb) sb.classList.remove('collapsed');
    state.sidebarRight = true;
    localStorage.setItem('eks_sidebar_right', 'true');
    document.getElementById('sb-back').style.display = '';
    document.getElementById('sb-detail')?.classList.add('closed');
    document.getElementById('sb-settings')?.classList.add('closed');
    document.getElementById('sb-help')?.classList.remove('closed');
    document.getElementById('sb-title').textContent = 'Help';
    var html = '<h4 style="font-size:12px;margin:0 0 4px;">About</h4><p style="font-size:11px;color:var(--text2);margin-bottom:8px;">' + (helpData ? PU.escHtml(helpData.about) : 'EKS Dashboard') + '</p>';
    html += '<h4 style="font-size:12px;margin:8px 0 4px;">Keyboard Shortcuts</h4>'
      + '<ul style="font-size:11px;padding-left:16px;margin:2px 0 8px;"><li><strong>F1</strong> — Toggle help</li>'
      + '<li><strong>Ctrl+Shift+L</strong> — Load files</li>'
      + '<li><strong>Ctrl+Shift+R</strong> — Run pipeline</li>'
      + '<li><strong>Ctrl+Shift+F</strong> — Focus search</li></ul>';
    html += '<h4 style="font-size:12px;margin:8px 0 4px;">Help Topics</h4>';
    if (helpData && helpData.help) {
      Object.keys(helpData.help).forEach(function (k) {
        html += '<p style="font-size:11px;margin:2px 0;"><strong>' + k.replace(/_/g, ' ') + ':</strong> ' + PU.escHtml(helpData.help[k]) + '</p>';
      });
    }
    html += '<h4 style="font-size:12px;margin:8px 0 4px;">Glossary</h4>';
    if (helpData && helpData.definitions) {
      Object.keys(helpData.definitions).forEach(function (k) {
        html += '<p style="font-size:11px;margin:2px 0;"><strong>' + PU.escHtml(k.replace(/_/g, ' ')) + '</strong>: ' + PU.escHtml(helpData.definitions[k]) + '</p>';
      });
    }
    document.getElementById('sb-help-content').innerHTML = html;
  }

  /* ── Step progress ── */
  function updateStepProgress(activeStep, completedSteps) {
    document.querySelectorAll('.step').forEach(function (step) {
      var num = parseInt(step.getAttribute('data-step'));
      step.classList.remove('active', 'completed');
      if (completedSteps && completedSteps.includes(num)) {
        step.classList.add('completed');
      } else if (num === activeStep) {
        step.classList.add('active');
      }
    });
  }

  /* ── Tab management ── */
  function hideAllTabs() {
    document.querySelectorAll('.tab-content').forEach(function (el) { el.style.display = 'none'; });
    document.querySelectorAll('.tab').forEach(function (el) { el.classList.remove('active'); });
  }

  function showTab(name) {
    var el = document.getElementById('tab-' + name);
    if (el) el.style.display = 'block';
    var tab = document.querySelector('.tab[data-tab="' + name + '"]');
    if (tab) tab.classList.add('active');
  }

  function switchTab(name) {
    hideAllTabs();
    showTab(name);
    var step = document.querySelector('.step[data-tab="' + name + '"]');
    if (step) {
      var num = parseInt(step.getAttribute('data-step'));
      var completed = [];
      document.querySelectorAll('.step.completed').forEach(function (s) {
        completed.push(parseInt(s.getAttribute('data-step')));
      });
      updateStepProgress(num, completed);
    }
  }

  /* ── Search ── */
  function searchDocs(query) {
    if (!query) { renderDocTable(state.docs); return; }
    var q = query.toLowerCase();
    var filtered = state.docs.filter(function (d) {
      return (d.document_number && d.document_number.toLowerCase().includes(q))
        || (d.type && d.type.toLowerCase().includes(q))
        || (d.discipline && d.discipline.toLowerCase().includes(q));
    });
    renderDocTable(filtered);
  }

  /* ── Resize (delegates to comUI for left sidebar, custom for right) ── */
  function initResize() {
    comUI.sidebar.resize('left-sidebar', 'left-resize', {
      storageKey: 'eks-left-sidebar-w', min: 200, max: 500,
    });
    // Right sidebar — reversed direction
    var sb = document.getElementById('right-sidebar');
    var handle = document.getElementById('right-resize');
    if (!sb || !handle) return;
    var startX, startW;
    handle.addEventListener('mousedown', function (e) {
      startX = e.clientX;
      startW = sb.offsetWidth;
      function onMove(ev) {
        var w = startW - (ev.clientX - startX);
        if (w < 200) w = 200;
        if (w > 500) w = 500;
        sb.style.width = w + 'px';
      }
      function onUp() {
        document.removeEventListener('mousemove', onMove);
        document.removeEventListener('mouseup', onUp);
      }
      document.addEventListener('mousemove', onMove);
      document.addEventListener('mouseup', onUp);
      e.preventDefault();
    });
  }

  /* ── Init ── */
  document.addEventListener('DOMContentLoaded', async function () {
    // Theme — picker and restore
    comUI.theme.initPicker('eks-theme');
    applyLayout(state.layout);

    await loadHelp();
    await fetchPaths();

    // Drag-and-drop on full page body (§18.7)
    document.addEventListener('dragover', function (e) { e.preventDefault(); });
    document.addEventListener('drop', function (e) {
      e.preventDefault();
      comUI.toast.show('Use the Browse &amp; Load Files button to select a server-side data folder.', 'info', 4000);
    });

    // Right sidebar accordion (§18.5)
    comUI.sidebar.accordion(document.getElementById('sb-content'));

    // Sidebar toggles
    document.getElementById('toggle-left')?.addEventListener('click', function () {
      state.sidebarLeft = !state.sidebarLeft;
      document.getElementById('left-sidebar').classList.toggle('collapsed', !state.sidebarLeft);
      localStorage.setItem('eks_sidebar_left', state.sidebarLeft);
    });
    document.getElementById('toggle-right')?.addEventListener('click', function () {
      state.sidebarRight = !state.sidebarRight;
      document.getElementById('right-sidebar').classList.toggle('collapsed', !state.sidebarRight);
      localStorage.setItem('eks_sidebar_right', state.sidebarRight);
    });
    // Back button — reopen detail view
    document.getElementById('sb-back')?.addEventListener('click', function () {
      document.getElementById('sb-settings')?.classList.add('closed');
      document.getElementById('sb-help')?.classList.add('closed');
      document.getElementById('sb-detail')?.classList.remove('closed');
      document.getElementById('sb-title').textContent = 'Detail';
      document.getElementById('sb-back').style.display = 'none';
      // Re-show the currently selected document
      if (state.selectedDoc) { showDetail(state.selectedDoc); }
    });

    // Layout toggle
    document.getElementById('btn-layout')?.addEventListener('click', function () {
      var layouts = ['triple', 'dual', 'single'];
      var idx = layouts.indexOf(state.layout);
      applyLayout(layouts[(idx + 1) % layouts.length]);
    });

    // Side icon bar buttons
    document.getElementById('icon-load')?.addEventListener('click', function () { loadFiles(); });
    document.getElementById('icon-refresh')?.addEventListener('click', function () {
      comUI.toast.show('Refreshing document list...', 'info', 2000);
      apiGet('/api/v1/documents').then(function (data) {
        state.docs = data.documents || [];
        renderDocTable(state.docs);
        buildTree(state.docs);
        PU.setStatus('status-text', 'Refreshed: ' + state.docs.length + ' documents');
      }).catch(function () {
        comUI.toast.show('Failed to refresh. Is the backend running?', 'warning', 3000);
      });
    });
    document.getElementById('icon-info')?.addEventListener('click', function () {
      var about = helpData ? helpData.about : 'EKS Engineering Knowledge System';
      var version = 'Phase 1 Ingestion Pipeline — v2.0';
      comUI.toast.show(about + ' — ' + version, 'info', 5000);
    });
    document.getElementById('icon-tree')?.addEventListener('click', function () {
      state.sidebarLeft = !state.sidebarLeft;
      document.getElementById('left-sidebar').classList.toggle('collapsed', !state.sidebarLeft);
      localStorage.setItem('eks_sidebar_left', state.sidebarLeft);
    });
    document.getElementById('icon-help')?.addEventListener('click', showHelp);
    document.getElementById('icon-settings')?.addEventListener('click', showSettings);

    // Tab action buttons (scoped per tab)
    document.getElementById('btn-load-files')?.addEventListener('click', function () { loadFiles(); });
    document.getElementById('btn-run-pipeline')?.addEventListener('click', startPipeline);
    document.getElementById('btn-cancel-pipeline')?.addEventListener('click', cancelPipeline);
    document.getElementById('btn-review')?.addEventListener('click', showReview);
    document.getElementById('btn-browse')?.addEventListener('click', toggleDirTree);
    document.getElementById('btn-proceed-process')?.addEventListener('click', function () {
      switchTab('pipeline');
      updateStepProgress(2, [1]);
    });
    // Close directory tree on outside click
    document.addEventListener('click', function (e) {
      var tree = document.getElementById('dir-tree');
      if (tree && !e.target.closest('#btn-browse') && !e.target.closest('#dir-tree')) {
        tree.style.display = 'none';
      }
    });

    // Step progress click — navigate to corresponding tab
    document.querySelectorAll('.step').forEach(function (step) {
      step.addEventListener('click', function () {
        var tab = step.getAttribute('data-tab');
        if (tab) switchTab(tab);
      });
    });

    // Global search
    var searchInput = document.getElementById('global-search');
    if (searchInput) {
      searchInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') searchDocs(searchInput.value);
      });
    }

    // Help modal (using comUI.modal)
    comUI.modal.init('help-modal');
    document.getElementById('help-modal')?.addEventListener('click', function (e) {
      if (e.target === this) comUI.modal.close('help-modal');
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', function (e) {
      if (e.key === 'F1') { e.preventDefault(); showHelp(); }
      if (e.ctrlKey && e.shiftKey && e.key === 'L') { e.preventDefault(); loadFiles(); }
      if (e.ctrlKey && e.shiftKey && e.key === 'R') { e.preventDefault(); startPipeline(); }
      if (e.ctrlKey && e.shiftKey && e.key === 'F') { e.preventDefault(); document.getElementById('global-search')?.focus(); }
    });

    // Table sort
    initTableSort();

    // Resize handles
    initResize();

    // Health chart tab visibility
    var chartTab = document.querySelector('.tab[data-tab="health"]');
    if (chartTab) {
      chartTab.addEventListener('click', function () {
        updateStepProgress(4, [1, 2, 3]);
        setTimeout(renderHealthChart, 100);
      });
    }

    // Auto-load on startup
    loadFiles();
  });

})();

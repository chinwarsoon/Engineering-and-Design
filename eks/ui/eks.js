/* EKS Dashboard JavaScript — AGENTS.md §18 + G7 UI Contracts */
(function () {
  'use strict';

  const API_BASE = '/api';
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
    theme: localStorage.getItem('eks_theme') || 'dark',
    sidebarLeft: localStorage.getItem('eks_sidebar_left') !== 'false',
    sidebarRight: localStorage.getItem('eks_sidebar_right') !== 'false',
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

  /* ── Theme ── */
  function applyTheme(t) {
    document.documentElement.setAttribute('data-theme', t);
    localStorage.setItem('eks_theme', t);
    state.theme = t;
  }

  /* ── Layout ── */
  function applyLayout(l) {
    document.getElementById('app-layout').className = 'layout-' + l;
    localStorage.setItem('eks_layout', l);
    state.layout = l;
    document.getElementById('left-sidebar').classList.toggle('open', state.sidebarLeft && l !== 'single');
    document.getElementById('right-sidebar').classList.toggle('right-open', state.sidebarRight && l === 'triple');
  }

  /* ── API helpers ── */
  async function apiGet(path) {
    const r = await fetch(API_BASE + path);
    if (!r.ok) throw new Error(await r.text());
    return r.json();
  }

  async function apiPost(path, body) {
    const r = await fetch(API_BASE + path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!r.ok) throw new Error(await r.text());
    return r.json();
  }

  async function apiDelete(path) {
    const r = await fetch(API_BASE + path, { method: 'DELETE' });
    if (!r.ok) throw new Error(await r.text());
    return r.json();
  }

  /* ── File Load ── */
  async function loadFiles(dir) {
    const data = await apiPost('/files/load', { dir: dir || 'eks/data' });
    state.docs = data.documents || [];
    renderDocTable(state.docs);
    buildTree(state.docs);
    setStatus('Loaded ' + state.docs.length + ' documents');
    hideAllTabs();
    showTab('documents');
  }

  async function loadFilesFromPicker() {
    const data = await apiGet('/files/load');
    state.docs = data.documents || [];
    renderDocTable(state.docs);
    buildTree(state.docs);
    setStatus('Loaded ' + state.docs.length + ' documents');
    hideAllTabs();
    showTab('documents');
  }

  /* ── Doc Table ── */
  function renderDocTable(docs) {
    const el = document.getElementById('doc-table-body');
    if (!docs || docs.length === 0) {
      el.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--text-secondary);padding:20px;">No documents found</td></tr>';
      return;
    }
    el.innerHTML = docs.map(function (d) {
      var score = d.health_score || 0;
      var cls = score >= 0.7 ? 'health-high' : score >= 0.4 ? 'health-medium' : 'health-low';
      return '<tr data-doc-id="' + esc(d.document_number || d.file_path || '') + '">'
        + '<td>' + esc(d.document_number || '-') + '</td>'
        + '<td>' + esc(d.type || '-') + '</td>'
        + '<td>' + esc(d.discipline || '-') + '</td>'
        + '<td>' + esc(d.revision || '-') + '</td>'
        + '<td><span class="health-badge ' + cls + '">' + score.toFixed(2) + '</span></td>'
        + '</tr>';
    }).join('');
    el.querySelectorAll('tr').forEach(function (tr) {
      tr.addEventListener('click', function () {
        var id = tr.getAttribute('data-doc-id');
        selectDocument(id);
      });
    });
  }

  function selectDocument(id) {
    var doc = state.docs.find(function (d) { return (d.document_number || d.file_path) === id; });
    if (!doc) return;
    state.selectedDoc = doc;
    showDetail(doc);
    if (state.layout === 'triple' || state.layout === 'dual') {
      document.getElementById('right-sidebar').classList.add('right-open');
      state.sidebarRight = true;
      localStorage.setItem('eks_sidebar_right', 'true');
    }
  }

  function showDetail(doc) {
    var el = document.getElementById('detail-content');
    var score = doc.health_score || 0;
    var s = '<div class="detail-section">'
      + '<h4>Document Info</h4>'
      + '<div class="detail-row"><span class="detail-label">Number</span><span class="detail-value">' + esc(doc.document_number || '-') + '</span></div>'
      + '<div class="detail-row"><span class="detail-label">Type</span><span class="detail-value">' + esc(doc.type || '-') + '</span></div>'
      + '<div class="detail-row"><span class="detail-label">Discipline</span><span class="detail-value">' + esc(doc.discipline || '-') + '</span></div>'
      + '<div class="detail-row"><span class="detail-label">Revision</span><span class="detail-value">' + esc(doc.revision || '-') + '</span></div>'
      + '<div class="detail-row"><span class="detail-label">File</span><span class="detail-value">' + esc(doc.file_path || '-') + '</span></div>'
      + '<div class="detail-row"><span class="detail-label">Status</span><span class="detail-value">' + esc(doc.extract_status || 'pending') + '</span></div>'
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
    return '<div class="score-bar"><span class="label">' + label + '</span><div class="bar-track"><div class="bar-fill" style="width:' + pct + '%;background:' + color + '"></div></div><span style="font-size:11px;color:var(--text-secondary);">' + pct + '%</span></div>';
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
      html += '<div class="tree-node" data-expandable="true"><span class="toggle">▶</span>' + esc(disc) + '<div class="tree-node children" style="display:none">';
      Object.keys(tree[disc]).sort().forEach(function (type) {
        html += '<div class="tree-node" data-expandable="true"><span class="toggle">▶</span>' + esc(type) + '<div class="tree-node children" style="display:none">';
        tree[disc][type].forEach(function (d) {
          var id = d.document_number || d.file_path || '';
          html += '<div class="tree-node" data-doc-id="' + esc(id) + '">' + esc(d.document_number || d.file_path) + '</div>';
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
  async function startPipeline() {
    var btn = document.getElementById('btn-run-pipeline');
    btn.disabled = true;
    btn.textContent = 'Starting...';
    try {
      var result = await apiPost('/pipeline/start', { data_dir: 'eks/data', recursive: true });
      state.jobId = result.job_id;
      setStatus('Pipeline started: ' + state.jobId);
      btn.textContent = 'Running...';
      showPipelineTab(state.jobId);
      startPolling(state.jobId);
      startLogPolling(state.jobId);
    } catch (e) {
      setStatus('Pipeline error: ' + e.message);
      btn.disabled = false;
      btn.textContent = 'Run Pipeline';
    }
  }

  function startPolling(jobId) {
    if (state.pollTimer) clearInterval(state.pollTimer);
    state.pollTimer = setInterval(function () {
      apiGet('/pipeline/status/' + jobId).then(function (data) {
        updatePipelineStatus(data);
        if (data.status === 'completed' || data.status === 'failed' || data.status === 'cancelled') {
          clearInterval(state.pollTimer);
          state.pollTimer = null;
          document.getElementById('btn-run-pipeline').disabled = false;
          document.getElementById('btn-run-pipeline').textContent = 'Run Pipeline';
        }
      }).catch(function () {});
    }, POLL_INTERVAL);
  }

  function startLogPolling(jobId) {
    if (state.logTimer) clearInterval(state.logTimer);
    state.logTimer = setInterval(function () {
      apiGet('/pipeline/logs/' + jobId).then(function (data) {
        if (data.logs) renderLogs(data.logs);
      }).catch(function () {});
    }, POLL_INTERVAL);
  }

  function updatePipelineStatus(data) {
    var el = document.getElementById('pipeline-status');
    el.textContent = 'Status: ' + data.status + ' (' + data.progress + '%)';
    document.getElementById('pipeline-progress').style.width = data.progress + '%';
    if (data.summary) {
      document.getElementById('pipeline-summary').textContent = JSON.stringify(data.summary, null, 2);
    }
  }

  function renderLogs(logs) {
    var el = document.getElementById('pipeline-logs');
    el.innerHTML = logs.map(function (e) {
      var cls = 'log-' + e.level.toLowerCase();
      return '<div class="' + cls + '">[' + e.level + '] ' + esc(e.message) + '</div>';
    }).join('');
    el.scrollTop = el.scrollHeight;
  }

  async function cancelPipeline() {
    if (!state.jobId) return;
    try {
      await apiDelete('/pipeline/' + state.jobId);
      setStatus('Pipeline cancelled');
    } catch (e) {
      setStatus('Cancel error: ' + e.message);
    }
  }

  function showPipelineTab(jobId) {
    hideAllTabs();
    showTab('pipeline');
    document.getElementById('pipeline-status').textContent = 'Status: queued (0%)';
    document.getElementById('pipeline-progress').style.width = '0%';
    document.getElementById('pipeline-logs').innerHTML = '';
    document.getElementById('pipeline-summary').textContent = '';
  }

  /* ── Review ── */
  async function showReview() {
    try {
      var data = await apiGet('/review/summary');
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
        html += '<div class="detail-section" style="border:1px solid var(--border-color);border-radius:4px;padding:8px;margin-bottom:8px;">'
          + '<div class="detail-row"><span class="detail-label">Document</span><span class="detail-value">' + esc(doc.document_number || '-') + '</span></div>'
          + '<div class="detail-row"><span class="detail-label">Reason</span><span class="detail-value">' + esc(doc.flag_reason || 'Unknown') + '</span></div>'
          + '<div style="margin-top:8px;"><button class="title-bar-btn" onclick="eksReviewDoc(\'' + esc(doc.document_number || '') + '\')">Review</button></div>'
          + '</div>';
      });
      el.innerHTML = html;
    } catch (e) {
      setStatus('Review error: ' + e.message);
    }
  }

  window.eksReviewDoc = function (docId) {
    document.getElementById('review-content').innerHTML = '<div class="review-form">'
      + '<h4>Review: ' + esc(docId) + '</h4>'
      + '<label>Document Number</label><input id="rev-doc-number" value="' + esc(docId) + '" />'
      + '<label>Revision</label><input id="rev-revision" placeholder="e.g., A, B, C" />'
      + '<label>Status</label><select id="rev-status"><option value="locked">Locked (Approved)</option><option value="flagged">Flagged (Needs Work)</option></select>'
      + '<label>Comments</label><textarea id="rev-comments" placeholder="Review comments..."></textarea>'
      + '<button onclick="eksSubmitReview()">Submit Review</button>'
      + '</div>';
  };

  window.eksSubmitReview = async function () {
    var docNumber = document.getElementById('rev-doc-number').value;
    var revision = document.getElementById('rev-revision').value;
    var status = document.getElementById('rev-status').value;
    var comments = document.getElementById('rev-comments').value;
    try {
      await apiPost('/review/submit', { document_number: docNumber, revision: revision, status: status, comments: comments });
      setStatus('Review submitted for ' + docNumber);
      showReview();
    } catch (e) {
      setStatus('Submit error: ' + e.message);
    }
  };

  /* ── Health Score Chart ── */
  function renderHealthChart() {
    var canvas = document.getElementById('health-chart-canvas');
    if (!canvas) return;
    var ctx = canvas.getContext('2d');
    // Chart.js loaded from CDN
    if (typeof Chart === 'undefined') {
      var s = document.createElement('script');
      s.src = 'https://cdn.jsdelivr.net/npm/chart.js';
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

  /* ── Settings ── */
  function showSettings() {
    hideAllTabs();
    showTab('settings');
    document.getElementById('settings-content').innerHTML = ''
      + '<div class="setting-row"><label>Theme</label><select id="setting-theme" onchange="eksSetTheme(this.value)">'
      + '<option value="dark" ' + (state.theme === 'dark' ? 'selected' : '') + '>Dark</option>'
      + '<option value="light" ' + (state.theme === 'light' ? 'selected' : '') + '>Light</option>'
      + '<option value="sky" ' + (state.theme === 'sky' ? 'selected' : '') + '>Sky</option>'
      + '<option value="ocean" ' + (state.theme === 'ocean' ? 'selected' : '') + '>Ocean</option>'
      + '<option value="presentation" ' + (state.theme === 'presentation' ? 'selected' : '') + '>Presentation</option>'
      + '</select></div>'
      + '<div class="setting-row"><label>Layout</label><select id="setting-layout" onchange="eksSetLayout(this.value)">'
      + '<option value="single" ' + (state.layout === 'single' ? 'selected' : '') + '>Single</option>'
      + '<option value="dual" ' + (state.layout === 'dual' ? 'selected' : '') + '>Dual</option>'
      + '<option value="triple" ' + (state.layout === 'triple' ? 'selected' : '') + '>Triple</option>'
      + '</select></div>'
      + '<div class="setting-row"><label>Poll Interval (ms)</label><input type="number" id="setting-poll" value="' + POLL_INTERVAL + '" min="500" step="500" /></div>';
  }

  window.eksSetTheme = function (t) { applyTheme(t); };
  window.eksSetLayout = function (l) { applyLayout(l); };

  /* ── Help Modal ── */
  function showHelp() {
    var modal = document.getElementById('help-modal');
    if (!modal) return;
    var body = document.getElementById('help-body');
    var html = '<h4>About</h4><p>' + (helpData ? esc(helpData.about) : 'EKS Dashboard') + '</p>';
    html += '<h4>Keyboard Shortcuts</h4>'
      + '<ul><li><strong>F1</strong> — Toggle this help</li>'
      + '<li><strong>Ctrl+Shift+L</strong> — Load files</li>'
      + '<li><strong>Ctrl+Shift+R</strong> — Run pipeline</li>'
      + '<li><strong>Ctrl+Shift+F</strong> — Focus search</li></ul>';
    html += '<h4>Help Topics</h4>';
    if (helpData && helpData.help) {
      Object.keys(helpData.help).forEach(function (k) {
        html += '<p><strong>' + k.replace(/_/g, ' ') + ':</strong> ' + esc(helpData.help[k]) + '</p>';
      });
    }
    html += '<h4>Glossary</h4><dl class="glossary">';
    if (helpData && helpData.definitions) {
      Object.keys(helpData.definitions).forEach(function (k) {
        html += '<dt>' + esc(k.replace(/_/g, ' ')) + '</dt><dd>' + esc(helpData.definitions[k]) + '</dd>';
      });
    }
    html += '</dl>';
    body.innerHTML = html;
    modal.classList.add('open');
  }

  function hideHelp() {
    var modal = document.getElementById('help-modal');
    if (modal) modal.classList.remove('open');
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

  /* ── Utils ── */
  function esc(s) {
    if (typeof s !== 'string') return String(s || '');
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function setStatus(msg) {
    var el = document.getElementById('status-text');
    if (el) el.textContent = msg;
  }

  /* ── Resize ── */
  function initResize(sidebarId, handleId, isRight) {
    var sidebar = document.getElementById(sidebarId);
    var handle = document.getElementById(handleId);
    if (!sidebar || !handle) return;
    var startX, startW;
    handle.addEventListener('mousedown', function (e) {
      startX = e.clientX;
      startW = sidebar.offsetWidth;
      function onMove(ev) {
        var dx = ev.clientX - startX;
        var w = isRight ? startW - dx : startW + dx;
        if (w >= 200 && w <= 500) sidebar.style.width = w + 'px';
      }
      function onUp() {
        document.removeEventListener('mousemove', onMove);
        document.removeEventListener('mouseup', onUp);
      }
      document.addEventListener('mousemove', onMove);
      document.addEventListener('mouseup', onUp);
    });
  }

  /* ── Init ── */
  document.addEventListener('DOMContentLoaded', async function () {
    applyTheme(state.theme);
    applyLayout(state.layout);

    await loadHelp();

    // Sidebar toggles
    document.getElementById('toggle-left')?.addEventListener('click', function () {
      state.sidebarLeft = !state.sidebarLeft;
      document.getElementById('left-sidebar').classList.toggle('open', state.sidebarLeft);
      localStorage.setItem('eks_sidebar_left', state.sidebarLeft);
    });
    document.getElementById('toggle-right')?.addEventListener('click', function () {
      state.sidebarRight = !state.sidebarRight;
      document.getElementById('right-sidebar').classList.toggle('right-open', state.sidebarRight && state.layout === 'triple');
      localStorage.setItem('eks_sidebar_right', state.sidebarRight);
    });

    // Theme toggle
    document.getElementById('btn-theme')?.addEventListener('click', function () {
      var themes = ['dark', 'light', 'sky', 'ocean', 'presentation'];
      var idx = themes.indexOf(state.theme);
      applyTheme(themes[(idx + 1) % themes.length]);
    });

    // Layout toggle
    document.getElementById('btn-layout')?.addEventListener('click', function () {
      var layouts = ['triple', 'dual', 'single'];
      var idx = layouts.indexOf(state.layout);
      applyLayout(layouts[(idx + 1) % layouts.length]);
      // Restore sidebar visibility
      document.getElementById('left-sidebar').classList.toggle('open', state.sidebarLeft && state.layout !== 'single');
      document.getElementById('right-sidebar').classList.toggle('right-open', state.sidebarRight && state.layout === 'triple');
    });

    // Side icon bar buttons
    document.getElementById('icon-load')?.addEventListener('click', loadFilesFromPicker);
    document.getElementById('icon-tree')?.addEventListener('click', function () {
      state.sidebarLeft = !state.sidebarLeft;
      document.getElementById('left-sidebar').classList.toggle('open', state.sidebarLeft);
      localStorage.setItem('eks_sidebar_left', state.sidebarLeft);
    });
    document.getElementById('icon-help')?.addEventListener('click', showHelp);
    document.getElementById('icon-settings')?.addEventListener('click', showSettings);

    // Toolbar buttons
    document.getElementById('btn-load-files')?.addEventListener('click', loadFilesFromPicker);
    document.getElementById('btn-run-pipeline')?.addEventListener('click', startPipeline);
    document.getElementById('btn-cancel-pipeline')?.addEventListener('click', cancelPipeline);
    document.getElementById('btn-review')?.addEventListener('click', showReview);

    // Tabs
    document.querySelectorAll('.tab[data-tab]').forEach(function (tab) {
      tab.addEventListener('click', function () { switchTab(tab.getAttribute('data-tab')); });
    });

    // Global search
    var searchInput = document.getElementById('global-search');
    if (searchInput) {
      searchInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') searchDocs(searchInput.value);
      });
    }

    // Help modal
    document.getElementById('help-close')?.addEventListener('click', hideHelp);
    document.getElementById('help-modal')?.addEventListener('click', function (e) {
      if (e.target === this) hideHelp();
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', function (e) {
      if (e.key === 'F1') { e.preventDefault(); showHelp(); }
      if (e.ctrlKey && e.shiftKey && e.key === 'L') { e.preventDefault(); loadFilesFromPicker(); }
      if (e.ctrlKey && e.shiftKey && e.key === 'R') { e.preventDefault(); startPipeline(); }
      if (e.ctrlKey && e.shiftKey && e.key === 'F') { e.preventDefault(); document.getElementById('global-search')?.focus(); }
    });

    // Resize handles
    initResize('left-sidebar', 'left-resize', false);
    initResize('right-sidebar', 'right-resize', true);

    // Health chart tab visibility
    var chartTab = document.querySelector('.tab[data-tab="health"]');
    if (chartTab) {
      chartTab.addEventListener('click', function () {
        setTimeout(renderHealthChart, 100);
      });
    }

    // File drop area
    var dropArea = document.getElementById('file-drop-area');
    if (dropArea) {
      dropArea.addEventListener('dragover', function (e) { e.preventDefault(); dropArea.classList.add('drag-over'); });
      dropArea.addEventListener('dragleave', function () { dropArea.classList.remove('drag-over'); });
      dropArea.addEventListener('drop', function (e) {
        e.preventDefault();
        dropArea.classList.remove('drag-over');
        // File drop not fully supported via API, just trigger load
        loadFilesFromPicker();
      });
    }

    // Auto-load on startup
    loadFilesFromPicker();
  });

})();

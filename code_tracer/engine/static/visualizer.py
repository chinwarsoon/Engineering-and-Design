"""
visualizer.py — Interactive HTML network generator for the static analysis module.
Uses pyvis (if available) to produce a self-contained draggable HTML graph.
Falls back to a plain JSON-driven HTML file when pyvis is not installed.

Public API:
    GraphVisualizer(call_graph)
        .render(output_path, complexity_filter)  -> Path
"""

import json
import logging
from pathlib import Path
from typing import Optional

from .graph import CallGraph

log = logging.getLogger(__name__)

# ── Colour helpers ────────────────────────────────────────────────────────────

def _complexity_colour(cc: int) -> str:
    """Map cyclomatic complexity to a hex colour for heatmap display.

    Breadcrumb: green (low) → yellow (medium) → red (high).
    Thresholds: 1-4 green, 5-9 yellow, 10-19 orange, 20+ red.

    Args:
        cc: Cyclomatic complexity integer.

    Returns:
        Hex colour string.
    """
    if cc <= 4:
        return "#3fb950"   # green  — low complexity
    if cc <= 9:
        return "#d29922"   # yellow — medium
    if cc <= 19:
        return "#f0883e"   # orange — high
    return "#f85149"       # red    — very high


def _node_size(cc: int) -> int:
    """Map complexity to node size (10–40px range)."""
    return min(10 + cc * 2, 40)


# ── Visualizer ────────────────────────────────────────────────────────────────

class GraphVisualizer:
    """Renders a CallGraph as an interactive HTML network.

    Args:
        call_graph: Built CallGraph instance.

    Usage::

        viz = GraphVisualizer(cg)
        viz.render("tracer/output/call_graph.html", complexity_filter=0)
    """

    def __init__(self, call_graph: CallGraph):
        # Breadcrumb: store reference to built graph
        self.cg = call_graph

    def render(
        self,
        output_path: str | Path,
        complexity_filter: int = 0,
    ) -> Path:
        """Generate the interactive HTML network and write to *output_path*.

        Breadcrumb: tries pyvis first; falls back to self-contained HTML+JS.

        Args:
            output_path: Destination .html file path.
            complexity_filter: Only include nodes with CC >= this value (0 = all).

        Returns:
            Resolved Path of the written HTML file.
        """
        out = Path(output_path).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)

        try:
            from pyvis.network import Network
            return self._render_pyvis(out, complexity_filter, Network)
        except ImportError:
            log.warning("[visualizer] pyvis not installed — using built-in HTML renderer")
            return self._render_builtin(out, complexity_filter)

    # ── pyvis renderer ────────────────────────────────────────────────────────

    def _render_pyvis(self, out: Path, cc_filter: int, Network) -> Path:
        """Render using pyvis.network.Network.

        Breadcrumb: nodes coloured by complexity, sized by complexity,
        entry points marked with a star shape.
        """
        net = Network(
            height="100%", width="100%",
            bgcolor="#0d1117", font_color="#e6edf3",
            directed=True,
            notebook=False,
        )
        net.set_options("""
        {
          "physics": {"stabilization": {"iterations": 150}},
          "edges": {"arrows": {"to": {"enabled": true, "scaleFactor": 0.5}},
                    "color": {"color": "#30363d", "highlight": "#58a6ff"},
                    "smooth": {"type": "dynamic"}},
          "nodes": {"borderWidth": 1, "borderWidthSelected": 2,
                    "font": {"size": 11, "face": "Inter, sans-serif"}}
        }
        """)

        graph_data = self.cg.to_json()
        entry_set = set(graph_data["entry_points"])

        # Add nodes
        for node in graph_data["nodes"]:
            cc = node["cyclomatic_complexity"]
            if cc < cc_filter:
                continue
            colour = _complexity_colour(cc)
            size = _node_size(cc)
            shape = "star" if node["id"] in entry_set else "dot"
            title = (
                f"<b>{node['label']}</b><br>"
                f"Module: {node['module']}<br>"
                f"Line: {node['start_line']}–{node['end_line']}<br>"
                f"CC: {cc} | Loops: {node['loop_count']} | Try/Except: {node['try_except_count']}<br>"
                f"Args: {node['arg_count']}"
            )
            net.add_node(
                node["id"], label=node["label"],
                color=colour, size=size, shape=shape, title=title,
            )

        # Add edges
        node_ids = {n["id"] for n in graph_data["nodes"] if n["cyclomatic_complexity"] >= cc_filter}
        for edge in graph_data["edges"]:
            if edge["source"] in node_ids and edge["target"] in node_ids:
                net.add_edge(edge["source"], edge["target"])

        net.save_graph(str(out))
        log.info("[visualizer] pyvis HTML → %s", out)
        return out

    # ── built-in HTML renderer ────────────────────────────────────────────────

    def _render_builtin(self, out: Path, cc_filter: int) -> Path:
        """Render a self-contained HTML file using vis-network CDN.

        Breadcrumb: embeds graph JSON inline; uses vis-network for layout.
        Styled with DCC design system colours.
        """
        graph_data = self.cg.to_json()
        entry_set = set(graph_data["entry_points"])

        vis_nodes = []
        for node in graph_data["nodes"]:
            cc = node["cyclomatic_complexity"]
            if cc < cc_filter:
                continue
            colour = _complexity_colour(cc)
            size = _node_size(cc)
            shape = "star" if node["id"] in entry_set else "dot"
            vis_nodes.append({
                "id": node["id"],
                "label": node["label"],
                "color": {"background": colour, "border": "#30363d",
                           "highlight": {"background": "#58a6ff", "border": "#2f81f7"}},
                "size": size,
                "shape": shape,
                "title": (
                    f"<b>{node['label']}</b><br>"
                    f"Module: {node['module']}<br>"
                    f"Line: {node['start_line']}–{node['end_line']}<br>"
                    f"CC: {cc} | Loops: {node['loop_count']} | "
                    f"Try/Except: {node['try_except_count']}<br>"
                    f"Args: {node['arg_count']}"
                ),
                "module": node["module"],
                "cc": cc,
            })

        node_id_set = {n["id"] for n in vis_nodes}
        vis_edges = [
            {"from": e["source"], "to": e["target"], "arrows": "to",
             "color": {"color": "#30363d", "highlight": "#58a6ff"}}
            for e in graph_data["edges"]
            if e["source"] in node_id_set and e["target"] in node_id_set
        ]

        stats = graph_data["stats"]
        nodes_json = json.dumps(vis_nodes)
        edges_json = json.dumps(vis_edges)
        entry_json = json.dumps(graph_data["entry_points"])
        hotspots_json = json.dumps(graph_data["hotspots"][:20])

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>DCC Static Analysis — Call Graph</title>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:'Inter',sans-serif;font-size:12px;background:#0d1117;color:#e6edf3;display:flex;flex-direction:column;height:100vh;overflow:hidden}}
  #titlebar{{height:36px;background:#161b22;border-bottom:1px solid #30363d;display:flex;align-items:center;padding:0 14px;gap:10px;flex-shrink:0}}
  #titlebar .logo{{font-weight:700;color:#58a6ff}}
  #titlebar .stats{{margin-left:auto;display:flex;gap:16px;font-size:11px;color:#8b949e}}
  #shell{{display:flex;flex:1;overflow:hidden}}
  #sidebar{{width:260px;background:#161b22;border-right:1px solid #30363d;display:flex;flex-direction:column;flex-shrink:0;overflow:hidden}}
  #sidebar-header{{padding:10px 14px 8px;font-size:10px;font-weight:700;color:#484f58;text-transform:uppercase;letter-spacing:.8px;border-bottom:1px solid #30363d}}
  #sidebar-body{{flex:1;overflow-y:auto;padding:12px}}
  .sb-label{{font-size:10px;font-weight:700;color:#484f58;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px;display:block}}
  .sb-input{{background:#2d333b;border:1px solid #30363d;border-radius:4px;padding:5px 9px;color:#e6edf3;font-size:11px;width:100%;outline:none;margin-bottom:10px}}
  .sb-input:focus{{border-color:#58a6ff}}
  .sb-btn{{display:block;width:100%;padding:5px 10px;background:#2f81f7;color:#fff;border:none;border-radius:4px;font-size:11px;cursor:pointer;margin-bottom:6px;text-align:center}}
  .sb-btn:hover{{background:#58a6ff}}
  .sb-btn.secondary{{background:#2d333b;color:#8b949e;border:1px solid #30363d}}
  .sb-btn.secondary:hover{{border-color:#58a6ff;color:#e6edf3}}
  .legend{{margin-top:12px}}
  .legend-item{{display:flex;align-items:center;gap:6px;margin-bottom:5px;font-size:11px;color:#8b949e}}
  .legend-dot{{width:10px;height:10px;border-radius:50%;flex-shrink:0}}
  #hotspot-list{{margin-top:8px}}
  .hotspot-row{{padding:5px 0;border-bottom:1px solid #21262d;font-size:10px;color:#8b949e}}
  .hotspot-row .fn{{color:#e6edf3;font-weight:500}}
  .hotspot-row .cc{{float:right;font-weight:700}}
  #content{{flex:1;display:flex;flex-direction:column;overflow:hidden}}
  #network{{flex:1}}
  #statusbar{{height:22px;background:#2f81f7;color:#fff;display:flex;align-items:center;padding:0 12px;font-size:11px;gap:16px;flex-shrink:0}}
  #detail-panel{{position:absolute;right:16px;top:52px;width:280px;background:#161b22;border:1px solid #30363d;border-radius:6px;padding:12px;display:none;z-index:100;font-size:11px}}
  #detail-panel h3{{font-size:12px;color:#58a6ff;margin-bottom:8px}}
  .dp-row{{display:grid;grid-template-columns:100px 1fr;gap:4px;margin-bottom:4px}}
  .dp-key{{color:#484f58}}
  .dp-val{{color:#e6edf3;word-break:break-all}}
  #close-detail{{float:right;cursor:pointer;color:#484f58;font-size:14px}}
  #close-detail:hover{{color:#e6edf3}}
</style>
</head>
<body>
<div id="titlebar">
  <span class="logo">⚙ DCC Static Analysis</span>
  <span style="color:#484f58">Call Graph</span>
  <div class="stats">
    <span>Functions: <b style="color:#e6edf3">{stats['total_functions']}</b></span>
    <span>Edges: <b style="color:#e6edf3">{stats['total_edges']}</b></span>
    <span>Entry Points: <b style="color:#e6edf3">{stats['entry_point_count']}</b></span>
    <span>Modules: <b style="color:#e6edf3">{stats['modules_analyzed']}</b></span>
  </div>
</div>
<div id="shell">
  <div id="sidebar">
    <div id="sidebar-header">Controls</div>
    <div id="sidebar-body">
      <label class="sb-label">Complexity Filter (min CC)</label>
      <input id="cc-filter" class="sb-input" type="number" value="{cc_filter}" min="0" max="50">
      <label class="sb-label">Search Function</label>
      <input id="search-input" class="sb-input" type="text" placeholder="function name...">
      <button class="sb-btn" onclick="applyFilter()">Apply Filter</button>
      <button class="sb-btn secondary" onclick="resetFilter()">Reset</button>
      <button class="sb-btn secondary" onclick="fitNetwork()">Fit View</button>

      <div class="legend" style="margin-top:16px">
        <span class="sb-label">Complexity Legend</span>
        <div class="legend-item"><div class="legend-dot" style="background:#3fb950"></div>CC 1–4 (Low)</div>
        <div class="legend-item"><div class="legend-dot" style="background:#d29922"></div>CC 5–9 (Medium)</div>
        <div class="legend-item"><div class="legend-dot" style="background:#f0883e"></div>CC 10–19 (High)</div>
        <div class="legend-item"><div class="legend-dot" style="background:#f85149"></div>CC 20+ (Very High)</div>
        <div class="legend-item"><div class="legend-dot" style="background:#58a6ff;clip-path:polygon(50% 0%,61% 35%,98% 35%,68% 57%,79% 91%,50% 70%,21% 91%,32% 57%,2% 35%,39% 35%)"></div>★ Entry Point</div>
      </div>

      <div style="margin-top:16px">
        <span class="sb-label">Top Hotspots</span>
        <div id="hotspot-list"></div>
      </div>
    </div>
  </div>

  <div id="content">
    <div id="network"></div>
  </div>
</div>

<div id="detail-panel">
  <span id="close-detail" onclick="document.getElementById('detail-panel').style.display='none'">✕</span>
  <h3 id="dp-title">Function Details</h3>
  <div id="dp-body"></div>
</div>

<div id="statusbar">
  <span id="status-text">Ready</span>
  <span style="margin-left:auto">DCC Static Analyser v1.0</span>
</div>

<script>
const ALL_NODES = {nodes_json};
const ALL_EDGES = {edges_json};
const ENTRY_POINTS = {entry_json};
const HOTSPOTS = {hotspots_json};

let network = null;
let nodesDS = null;
let edgesDS = null;

function buildNetwork(nodes, edges) {{
  const container = document.getElementById('network');
  nodesDS = new vis.DataSet(nodes);
  edgesDS = new vis.DataSet(edges);
  const options = {{
    physics: {{stabilization: {{iterations: 200}}, barnesHut: {{gravitationalConstant: -8000}}}},
    interaction: {{hover: true, tooltipDelay: 100}},
    layout: {{improvedLayout: true}},
  }};
  network = new vis.Network(container, {{nodes: nodesDS, edges: edgesDS}}, options);
  network.on('click', function(params) {{
    if (params.nodes.length > 0) showDetail(params.nodes[0]);
  }});
  document.getElementById('status-text').textContent =
    `Showing ${{nodes.length}} functions, ${{edges.length}} edges`;
}}

function showDetail(nodeId) {{
  const node = ALL_NODES.find(n => n.id === nodeId);
  if (!node) return;
  const panel = document.getElementById('detail-panel');
  document.getElementById('dp-title').textContent = node.label;
  const rows = [
    ['Module', node.module],
    ['File', node.id.split('::')[0]],
    ['Lines', `${{node.start_line || '?'}}–${{node.end_line || '?'}}`],
    ['Complexity', node.cc],
    ['Entry Point', ENTRY_POINTS.includes(node.id) ? '★ Yes' : 'No'],
  ];
  document.getElementById('dp-body').innerHTML = rows.map(([k,v]) =>
    `<div class="dp-row"><span class="dp-key">${{k}}</span><span class="dp-val">${{v}}</span></div>`
  ).join('');
  panel.style.display = 'block';
}}

function applyFilter() {{
  const minCC = parseInt(document.getElementById('cc-filter').value) || 0;
  const search = document.getElementById('search-input').value.toLowerCase();
  const filtered = ALL_NODES.filter(n =>
    n.cc >= minCC && (!search || n.label.toLowerCase().includes(search))
  );
  const ids = new Set(filtered.map(n => n.id));
  const filteredEdges = ALL_EDGES.filter(e => ids.has(e.from) && ids.has(e.to));
  buildNetwork(filtered, filteredEdges);
}}

function resetFilter() {{
  document.getElementById('cc-filter').value = '0';
  document.getElementById('search-input').value = '';
  buildNetwork(ALL_NODES, ALL_EDGES);
}}

function fitNetwork() {{
  if (network) network.fit();
}}

// Render hotspot list
const hotspotList = document.getElementById('hotspot-list');
HOTSPOTS.slice(0, 10).forEach(h => {{
  const div = document.createElement('div');
  div.className = 'hotspot-row';
  div.innerHTML = `<span class="fn">${{h.name}}</span><span class="cc" style="color:#f85149">CC ${{h.complexity}}</span><br><span style="color:#484f58">${{h.module}}</span>`;
  div.style.cursor = 'pointer';
  div.onclick = () => {{ if (network) network.focus(h.qualified_name, {{scale:1.5, animation:true}}); showDetail(h.qualified_name); }};
  hotspotList.appendChild(div);
}});

// Initial render
buildNetwork(ALL_NODES, ALL_EDGES);
</script>
</body>
</html>"""

        out.write_text(html, encoding="utf-8")
        log.info("[visualizer] Built-in HTML → %s", out)
        return out

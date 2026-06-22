let Graph3D;
let originalGraph = { nodes: [], links: [] };
let activeTypes = new Set();
let selectedNodeId = null;

const colors = {
  project: "#60a5fa",
  concept: "#34d399",
  entity: "#fbbf24",
  memory: "#a78bfa",
  rule: "#f87171",
  technology: "#38bdf8",
  pattern: "#fb7185",
  domain: "#c084fc",
  person: "#facc15",
  company: "#22c55e",
  default: "#94a3b8",
};

function nodeColor(type) {
  return colors[type] || colors.default;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

async function init() {
  if (typeof ForceGraph3D !== "function") {
    throw new Error("3d-force-graph failed to load from CDN.");
  }
  const response = await fetch("graph.json");
  const graph = await response.json();
  originalGraph = convertGraph(graph);
  activeTypes = new Set(Object.keys(graph.metadata.type_counts));
  renderTypeFilters(graph.metadata.type_counts);
  renderStats(graph.metadata);
  createGraph();
  bindControls();
  applyFilters();
}

function convertGraph(graph) {
  return {
    nodes: graph.elements.nodes.map(node => {
      const data = node.data;
      return {
        id: data.id,
        label: data.label,
        type: data.type,
        val: Math.max(2, Math.min(22, Number(data.mention_count || 1) + 2)),
        color: nodeColor(data.type),
        raw: data,
      };
    }),
    links: graph.elements.edges.map(edge => ({
      source: edge.data.source,
      target: edge.data.target,
      relation: edge.data.relation,
      weight: Number(edge.data.weight || 0),
      raw: edge.data,
    })),
  };
}

function renderStats(metadata) {
  document.getElementById("stats").textContent =
    `${metadata.node_count} nodes, ${metadata.edge_count} edges`;
}

function renderTypeFilters(typeCounts) {
  const root = document.getElementById("typeFilters");
  root.innerHTML = "";
  Object.entries(typeCounts)
    .sort((a, b) => b[1] - a[1])
    .forEach(([type, count]) => {
      const label = document.createElement("label");
      label.innerHTML = `
        <input type="checkbox" data-type="${escapeHtml(type)}" checked>
        <span><span class="pill">${escapeHtml(type)}</span>${count}</span>
      `;
      root.appendChild(label);
    });
}

function createGraph() {
  const container = document.getElementById("graph3d");
  Graph3D = ForceGraph3D()(container)
    .backgroundColor("#08111f")
    .nodeLabel(node => `${node.label} · ${node.type}`)
    .nodeColor(node => node.id === selectedNodeId ? "#ffffff" : node.color)
    .nodeVal(node => node.val)
    .linkColor(() => "rgba(148, 163, 184, 0.42)")
    .linkWidth(link => Math.max(0.5, Math.min(5, link.weight)))
    .linkDirectionalParticles(link => link.weight >= 4 ? 2 : 0)
    .linkDirectionalParticleWidth(1.2)
    .onNodeClick(node => {
      selectedNodeId = node.id;
      showDetails(node.raw);
      focusNode(node);
      Graph3D.nodeColor(n => n.id === selectedNodeId ? "#ffffff" : n.color);
    });
}

function bindControls() {
  document.getElementById("search").addEventListener("input", applyFilters);
  document.getElementById("weightFilter").addEventListener("input", event => {
    document.getElementById("weightValue").textContent = event.target.value;
    applyFilters();
  });
  document.getElementById("typeFilters").addEventListener("change", event => {
    if (!event.target.matches("input[type='checkbox']")) return;
    const type = event.target.dataset.type;
    if (event.target.checked) activeTypes.add(type);
    else activeTypes.delete(type);
    applyFilters();
  });
  document.getElementById("fit").addEventListener("click", () => Graph3D.zoomToFit(600, 80));
  document.getElementById("reheat").addEventListener("click", () => Graph3D.d3ReheatSimulation());
  document.getElementById("clearFocus").addEventListener("click", clearFocus);
  window.addEventListener("resize", () => {
    const container = document.getElementById("graph3d");
    Graph3D.width(container.clientWidth).height(container.clientHeight);
  });
}

function applyFilters() {
  const query = document.getElementById("search").value.trim().toLowerCase();
  const minWeight = Number(document.getElementById("weightFilter").value);
  const nodes = originalGraph.nodes.filter(node => {
    const raw = node.raw;
    if (!activeTypes.has(raw.type)) return false;
    if (!query) return true;
    return `${raw.label} ${raw.type} ${raw.content}`.toLowerCase().includes(query);
  });
  const nodeIds = new Set(nodes.map(node => node.id));
  const links = originalGraph.links.filter(link =>
    link.weight >= minWeight &&
    nodeIds.has(String(link.source.id || link.source)) &&
    nodeIds.has(String(link.target.id || link.target))
  );
  Graph3D.graphData({ nodes, links });
  selectedNodeId = null;
}

function focusNode(node) {
  const distance = 180;
  const distRatio = 1 + distance / Math.hypot(node.x || 1, node.y || 1, node.z || 1);
  Graph3D.cameraPosition(
    { x: (node.x || 0) * distRatio, y: (node.y || 0) * distRatio, z: (node.z || 0) * distRatio },
    node,
    900
  );
}

function clearFocus() {
  selectedNodeId = null;
  Graph3D.nodeColor(node => node.color);
  document.getElementById("details").textContent = "Select a node to inspect linked memories.";
}

function showDetails(data) {
  const memories = (data.knowledge || []).map(item => `
    <div class="memory">
      <strong>#${escapeHtml(item.id)} ${escapeHtml(item.type)} · ${escapeHtml(item.project)}</strong>
      <div class="meta">${escapeHtml(item.role)} · strength ${escapeHtml(item.strength)}</div>
      <div>${escapeHtml(item.summary)}</div>
    </div>
  `).join("");
  document.getElementById("details").innerHTML = `
    <div class="node-title">${escapeHtml(data.label)}</div>
    <div class="meta">${escapeHtml(data.type)} · mentions ${escapeHtml(data.mention_count)} · importance ${escapeHtml(data.importance)}</div>
    <div>${escapeHtml(data.content || "No node content.")}</div>
    <h2>Linked Memories</h2>
    ${memories || "<p>No linked memories in exported sample.</p>"}
  `;
}

init().catch(error => {
  document.getElementById("stats").textContent = "Failed to load 3D graph.";
  document.getElementById("details").textContent = String(error);
});

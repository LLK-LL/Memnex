import {
  buildEditIntent,
  convertGraphToGalaxy,
  filterGalaxy,
} from "./memory-galaxy-core.js";

let Graph3D;
let originalGraph = { nodes: [], links: [], metadata: {} };
let visibleGraph = { nodes: [], links: [], metadata: {} };
let activeTypes = new Set();
let activeLayers = new Set(["core", "active", "knowledge", "episode", "external"]);
let selectedNodeId = null;
let selectedNode = null;
let stagedIntents = [];

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
  originalGraph = convertGraphToGalaxy(graph);
  activeTypes = new Set(Object.keys(graph.metadata.type_counts));
  renderTypeFilters(graph.metadata.type_counts);
  renderLayerFilters();
  renderStats(graph.metadata);
  createGraph();
  bindControls();
  applyFilters();
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

function renderLayerFilters() {
  const root = document.getElementById("layerFilters");
  const layers = [
    ["core", "Core"],
    ["active", "Active"],
    ["knowledge", "Knowledge"],
    ["episode", "Episodes"],
    ["external", "External"],
  ];
  root.innerHTML = "";
  for (const [layer, labelText] of layers) {
    const label = document.createElement("label");
    label.innerHTML = `
      <input type="checkbox" data-layer="${escapeHtml(layer)}" checked>
      <span><span class="pill">${escapeHtml(labelText)}</span></span>
    `;
    root.appendChild(label);
  }
}

function createGraph() {
  const container = document.getElementById("graph3d");
  Graph3D = ForceGraph3D()(container)
    .backgroundColor("#050913")
    .nodeLabel(node => `${node.label} | ${node.type} | ${node.layer}`)
    .nodeColor(node => node.id === selectedNodeId ? "#ffffff" : node.color)
    .nodeVal(node => node.val)
    .nodeOpacity(0.94)
    .linkColor(link => relationColor(link.relation))
    .linkWidth(link => Math.max(0.35, Math.min(4, link.weight)))
    .linkOpacity(0.34)
    .linkDirectionalParticles(link => link.weight >= 4 ? 2 : 0)
    .linkDirectionalParticleWidth(1.1)
    .cooldownTicks(120)
    .onNodeClick(node => {
      selectedNodeId = node.id;
      selectedNode = node;
      showDetails(node.raw);
      focusNode(node);
      Graph3D.nodeColor(n => n.id === selectedNodeId ? "#ffffff" : n.color);
    });
}

function relationColor(relation) {
  if (relation === "contradicts") return "rgba(248, 113, 113, 0.75)";
  if (relation === "solution") return "rgba(34, 197, 94, 0.65)";
  if (relation === "causal") return "rgba(251, 191, 36, 0.65)";
  if (relation === "context") return "rgba(96, 165, 250, 0.55)";
  return "rgba(148, 163, 184, 0.42)";
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
  document.getElementById("layerFilters").addEventListener("change", event => {
    if (!event.target.matches("input[type='checkbox']")) return;
    const layer = event.target.dataset.layer;
    if (event.target.checked) activeLayers.add(layer);
    else activeLayers.delete(layer);
    applyFilters();
  });
  document.getElementById("timelineFilter").addEventListener("input", applyFilters);
  document.getElementById("fit").addEventListener("click", () => Graph3D.zoomToFit(600, 80));
  document.getElementById("reheat").addEventListener("click", () => Graph3D.d3ReheatSimulation());
  document.getElementById("clearFocus").addEventListener("click", clearFocus);
  document.getElementById("focusNeighborhood").addEventListener("click", showNeighborhoodOnly);
  document.getElementById("copySelection").addEventListener("click", copySelection);
  document.getElementById("stageIntent").addEventListener("click", stageSelectedIntent);
  window.addEventListener("resize", () => {
    const container = document.getElementById("graph3d");
    Graph3D.width(container.clientWidth).height(container.clientHeight);
  });
}

function applyFilters() {
  const timelineCutoff = timelineCutoffFromSlider();
  visibleGraph = filterGalaxy(originalGraph, {
    query: document.getElementById("search").value,
    activeTypes,
    activeLayers,
    minWeight: Number(document.getElementById("weightFilter").value),
    timelineCutoff,
  });
  Graph3D.graphData(visibleGraph);
  selectedNodeId = null;
  selectedNode = null;
}

function timelineCutoffFromSlider() {
  const slider = document.getElementById("timelineFilter");
  const value = Number(slider.value);
  const timeline = originalGraph.metadata.timeline || {};
  if (value >= 100 || !timeline.start || !timeline.end) {
    document.getElementById("timelineValue").textContent = "All time";
    return null;
  }
  const start = Date.parse(timeline.start);
  const end = Date.parse(timeline.end);
  if (!Number.isFinite(start) || !Number.isFinite(end) || end <= start) return null;
  const cutoff = new Date(start + ((end - start) * value / 100));
  document.getElementById("timelineValue").textContent = cutoff.toISOString().slice(0, 10);
  return cutoff.toISOString();
}

function showNeighborhoodOnly() {
  if (!selectedNode) return;
  const keep = new Set([selectedNode.id]);
  for (const link of originalGraph.links) {
    const source = String(link.source.id || link.source);
    const target = String(link.target.id || link.target);
    if (source === selectedNode.id) keep.add(target);
    if (target === selectedNode.id) keep.add(source);
  }
  const nodes = originalGraph.nodes.filter(node => keep.has(node.id));
  const links = originalGraph.links.filter(link =>
    keep.has(String(link.source.id || link.source)) &&
    keep.has(String(link.target.id || link.target))
  );
  visibleGraph = { nodes, links, metadata: originalGraph.metadata };
  Graph3D.graphData(visibleGraph);
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
  selectedNode = null;
  Graph3D.nodeColor(node => node.color);
  document.getElementById("details").textContent = "Select a node to inspect linked memories.";
}

async function copySelection() {
  if (!selectedNode) return;
  const text = `${selectedNode.label}\nType: ${selectedNode.type}\nLayer: ${selectedNode.layer}\n\n${selectedNode.raw.content || ""}`;
  await navigator.clipboard.writeText(text);
  flashDetails("Copied selection to clipboard.");
}

function stageSelectedIntent() {
  if (!selectedNode) return;
  const intent = buildEditIntent("inspect_or_edit_node", {
    node_id: selectedNode.id,
    label: selectedNode.label,
    type: selectedNode.type,
    layer: selectedNode.layer,
  });
  stagedIntents.push(intent);
  localStorage.setItem("memoryGalaxyIntents", JSON.stringify(stagedIntents, null, 2));
  flashDetails(`Staged intent ${stagedIntents.length}. Stored in localStorage.memoryGalaxyIntents.`);
}

function flashDetails(message) {
  const root = document.getElementById("details");
  const notice = document.createElement("div");
  notice.className = "notice";
  notice.textContent = message;
  root.prepend(notice);
  setTimeout(() => notice.remove(), 2600);
}

function showDetails(data) {
  const memories = (data.knowledge || []).map(item => `
    <div class="memory">
      <strong>#${escapeHtml(item.id)} ${escapeHtml(item.type)} | ${escapeHtml(item.project)}</strong>
      <div class="meta">${escapeHtml(item.role)} | strength ${escapeHtml(item.strength)}</div>
      <div>${escapeHtml(item.summary)}</div>
    </div>
  `).join("");
  document.getElementById("details").innerHTML = `
    <div class="node-title">${escapeHtml(data.label)}</div>
    <div class="meta">
      ${escapeHtml(data.type)} | ${escapeHtml(data.galaxy_layer || "external")}
      | mentions ${escapeHtml(data.mention_count)}
      | importance ${escapeHtml(data.importance)}
    </div>
    <div class="meta">
      last seen ${escapeHtml(data.last_seen_at || "unknown")}
      | source ${escapeHtml(data.source || "unknown")}
    </div>
    <div>${escapeHtml(data.content || "No node content.")}</div>
    <h2>Linked Memories</h2>
    ${memories || "<p>No linked memories in exported sample.</p>"}
  `;
}

init().catch(error => {
  document.getElementById("stats").textContent = "Failed to load galaxy.";
  document.getElementById("details").textContent = String(error);
});

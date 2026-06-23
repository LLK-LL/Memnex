import {
  buildEditIntent,
  buildExpandedGalaxy,
  buildFocusGalaxy,
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
let renderTimer = null;
let filteredGraph = { nodes: [], links: [], metadata: {} };
let expandedNodeIds = new Set();
let lastClick = { nodeId: null, at: 0 };
const focusLimit = 720;

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
  container.addEventListener("contextmenu", event => event.preventDefault());
  Graph3D = ForceGraph3D()(container)
    .backgroundColor("#050913")
    .nodeLabel(node => `${node.label} | ${node.type} | ${node.layer}`)
    .nodeColor(node => node.id === selectedNodeId ? "#facc15" : node.color)
    .nodeVal(node => node.id === selectedNodeId ? node.val + 10 : node.val)
    .nodeOpacity(0.94)
    .linkColor(link => relationColor(link.relation))
    .linkWidth(link => Math.max(0.2, Math.min(2.2, link.weight * 0.65)))
    .linkOpacity(0.22)
    .linkDirectionalParticles(link => selectedNodeId && touchesSelectedNode(link) ? 1 : 0)
    .linkDirectionalParticleWidth(1.1)
    .cooldownTicks(45)
    .d3AlphaDecay(0.08)
    .d3VelocityDecay(0.55)
    .onNodeClick(node => {
      const now = Date.now();
      const isDoubleClick = lastClick.nodeId === node.id && now - lastClick.at < 340;
      lastClick = { nodeId: node.id, at: now };
      selectNode(node);
      focusNode(node);
      if (isDoubleClick) expandNodeNeighborhood(node);
    })
    .onNodeRightClick(node => {
      selectNode(node);
      collapseNodeNeighborhood(node);
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
  document.getElementById("search").addEventListener("input", scheduleApplyFilters);
  document.getElementById("weightFilter").addEventListener("input", event => {
    document.getElementById("weightValue").textContent = event.target.value;
    scheduleApplyFilters();
  });
  document.getElementById("typeFilters").addEventListener("change", event => {
    if (!event.target.matches("input[type='checkbox']")) return;
    const type = event.target.dataset.type;
    if (event.target.checked) activeTypes.add(type);
    else activeTypes.delete(type);
    scheduleApplyFilters();
  });
  document.getElementById("layerFilters").addEventListener("change", event => {
    if (!event.target.matches("input[type='checkbox']")) return;
    const layer = event.target.dataset.layer;
    if (event.target.checked) activeLayers.add(layer);
    else activeLayers.delete(layer);
    scheduleApplyFilters();
  });
  document.getElementById("timelineFilter").addEventListener("input", scheduleApplyFilters);
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

function scheduleApplyFilters() {
  clearTimeout(renderTimer);
  renderTimer = setTimeout(applyFilters, 120);
}

function applyFilters() {
  expandedNodeIds = new Set();
  selectedNodeId = null;
  selectedNode = null;
  renderGalaxy();
}

function renderGalaxy() {
  filteredGraph = currentFilteredGalaxy();
  const focusGraph = buildFocusGalaxy(filteredGraph, { maxNodes: focusLimit });
  visibleGraph = buildExpandedGalaxy(filteredGraph, focusGraph, expandedNodeIds);
  Graph3D.graphData(visibleGraph);
  renderVisibleStats();
  refreshHighlight();
}

function currentFilteredGalaxy() {
  const timelineCutoff = timelineCutoffFromSlider();
  return filterGalaxy(originalGraph, {
    query: document.getElementById("search").value,
    activeTypes,
    activeLayers,
    minWeight: Number(document.getElementById("weightFilter").value),
    timelineCutoff,
  });
}

function renderVisibleStats() {
  renderStats({
    node_count: `${visibleGraph.nodes.length}/${originalGraph.nodes.length}`,
    edge_count: `${visibleGraph.links.length}/${originalGraph.links.length}`,
  });
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
  expandNodeNeighborhood(selectedNode);
}

function expandNodeNeighborhood(node) {
  expandedNodeIds.add(node.id);
  renderGalaxy();
  focusNode(findVisibleNode(node.id) || node);
  Graph3D.linkDirectionalParticles(link => touchesSelectedNode(link) ? 1 : 0);
}

function collapseNodeNeighborhood(node) {
  expandedNodeIds.delete(node.id);
  renderGalaxy();
  const stillVisible = visibleGraph.nodes.some(graphNode => graphNode.id === node.id);
  selectedNodeId = stillVisible ? node.id : null;
  selectedNode = stillVisible ? node : null;
  refreshHighlight();
  Graph3D.linkDirectionalParticles(() => 0);
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
  expandedNodeIds = new Set();
  refreshHighlight();
  Graph3D.linkDirectionalParticles(() => 0);
  document.getElementById("details").textContent = "Select a node to inspect linked memories.";
  renderGalaxy();
}

function selectNode(node) {
  selectedNodeId = node.id;
  selectedNode = node;
  showDetails(node.raw);
  refreshHighlight();
}

function findVisibleNode(nodeId) {
  return visibleGraph.nodes.find(graphNode => graphNode.id === nodeId);
}

function refreshHighlight() {
  if (!Graph3D) return;
  Graph3D.nodeColor(graphNode => graphNode.id === selectedNodeId ? "#facc15" : graphNode.color);
  Graph3D.nodeVal(graphNode => graphNode.id === selectedNodeId ? graphNode.val + 10 : graphNode.val);
}

function touchesSelectedNode(link) {
  const source = String(link.source.id || link.source);
  const target = String(link.target.id || link.target);
  return source === selectedNodeId || target === selectedNodeId;
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

import {
  buildEditIntent,
  buildExpandedGalaxy,
  buildFocusGalaxy,
  convertGraphToGalaxy,
  filterGalaxy,
} from "./memory-galaxy-core.js";

let Graph2D;
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
  if (typeof ForceGraph !== "function") {
    throw new Error("force-graph failed to load from CDN.");
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
  Graph2D = ForceGraph()(container)
    .backgroundColor("#050913")
    .nodeLabel(node => `${node.label} | ${node.type} | ${node.layer}`)
    .nodeCanvasObject(drawNode)
    .nodePointerAreaPaint(drawNodePointerArea)
    .linkColor(linkColor)
    .linkWidth(linkWidth)
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
      if (isDoubleClick) expandNodeNeighborhood(node);
      else focusNode(node);
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

function linkColor(link) {
  if (link.expansionParentId) return "rgba(248, 113, 113, 0.95)";
  if (selectedNodeId && touchesSelectedNode(link)) return "rgba(250, 204, 21, 0.9)";
  return relationColor(link.relation);
}

function linkWidth(link) {
  if (link.expansionParentId) return Math.max(2, Math.min(5, link.weight));
  if (selectedNodeId && touchesSelectedNode(link)) return Math.max(1.6, Math.min(4, link.weight));
  return Math.max(0.2, Math.min(2.2, link.weight * 0.65));
}

function nodeSize(node) {
  return node.id === selectedNodeId ? node.val + 10 : node.val;
}

function drawNode(node, ctx, globalScale) {
  const radius = Math.max(2.4, Math.sqrt(nodeSize(node)) * 1.45);
  if (node.id === selectedNodeId) {
    ctx.beginPath();
    ctx.arc(node.x, node.y, radius + 7, 0, 2 * Math.PI, false);
    ctx.strokeStyle = "#ff1f3d";
    ctx.lineWidth = Math.max(2.2, 3 / globalScale);
    ctx.shadowColor = "#ff1f3d";
    ctx.shadowBlur = 16;
    ctx.stroke();
    ctx.shadowBlur = 0;
  }
  ctx.beginPath();
  ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI, false);
  ctx.fillStyle = node.id === selectedNodeId ? "#ffffff" : node.color;
  ctx.fill();
  if (node.focusRing === 0) {
    ctx.strokeStyle = "rgba(255,255,255,0.65)";
    ctx.lineWidth = Math.max(0.8, 1.2 / globalScale);
    ctx.stroke();
  }
}

function drawNodePointerArea(node, color, ctx) {
  const radius = Math.max(6, Math.sqrt(nodeSize(node)) * 1.8);
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI, false);
  ctx.fill();
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
  document.getElementById("fit").addEventListener("click", () => Graph2D.zoomToFit(600, 80));
  document.getElementById("reheat").addEventListener("click", () => Graph2D.d3ReheatSimulation());
  document.getElementById("clearFocus").addEventListener("click", clearFocus);
  document.getElementById("focusNeighborhood").addEventListener("click", showNeighborhoodOnly);
  document.getElementById("copySelection").addEventListener("click", copySelection);
  document.getElementById("stageIntent").addEventListener("click", stageSelectedIntent);
  window.addEventListener("resize", () => {
    const container = document.getElementById("graph3d");
    Graph2D.width(container.clientWidth).height(container.clientHeight);
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
  Graph2D.graphData(toPlanarGraph(visibleGraph));
  renderVisibleStats();
  refreshHighlight();
}

function toPlanarGraph(graph) {
  return {
    ...graph,
    nodes: graph.nodes.map(node => ({
      ...node,
      x: node.x,
      y: node.z ?? node.y,
    })),
  };
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
  Graph2D.linkDirectionalParticles(link => touchesSelectedNode(link) ? 1 : 0);
}

function collapseNodeNeighborhood(node) {
  expandedNodeIds.delete(node.id);
  renderGalaxy();
  const stillVisible = visibleGraph.nodes.some(graphNode => graphNode.id === node.id);
  selectedNodeId = stillVisible ? node.id : null;
  selectedNode = stillVisible ? node : null;
  refreshHighlight();
  Graph2D.linkDirectionalParticles(() => 0);
}

function focusNode(node) {
  Graph2D.centerAt(node.x ?? 0, node.y ?? node.z ?? 0, 700);
  Graph2D.zoom(2.4, 700);
}

function clearFocus() {
  selectedNodeId = null;
  selectedNode = null;
  expandedNodeIds = new Set();
  refreshHighlight();
  Graph2D.linkDirectionalParticles(() => 0);
  document.getElementById("details").textContent = "Select a node to inspect linked memories.";
  renderGalaxy();
}

function selectNode(node) {
  selectedNodeId = node.id;
  selectedNode = node;
  showDetails(node.raw);
  refreshHighlight();
}

function refreshHighlight() {
  if (!Graph2D) return;
  Graph2D.nodeCanvasObject(drawNode);
  Graph2D.linkColor(linkColor);
  Graph2D.linkWidth(linkWidth);
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

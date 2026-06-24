import {
  buildClusterGalaxy2DLayout,
  buildFocusGalaxy,
  convertGraphToGalaxy,
  filterGalaxy,
  selectVisibleLabels,
  visibleLinksForSelection,
} from "./memory-galaxy-core.js";
import {
  createInteractionLog,
  createMemoryGalaxyEvent,
  suggestAgentPrompt,
} from "./memory-galaxy-events.js";
import {
  escapeHtml,
  formatNodeDetails,
  renderPromptText,
  timelineCutoffFromPercent,
} from "./viewer-shared.js";

const viewName = "2d-galaxy";
const focusLimit = 850;
const interactionLog = createInteractionLog();

let app;
let stageRoot;
let linkLayer;
let nodeLayer;
let labelLayer;
let originalGraph = { nodes: [], links: [], metadata: {} };
let visibleGraph = { nodes: [], links: [], metadata: {} };
let activeTypes = new Set();
let activeLayers = new Set(["core", "active", "knowledge", "episode", "external"]);
let selectedNodeId = null;
let hoveredNodeId = null;
let selectedNode = null;
let renderTimer = null;
let scale = 1;
let pan = { x: 0, y: 0 };
let dragState = null;

async function init() {
  if (!window.PIXI) throw new Error("PixiJS failed to load from CDN.");
  const response = await fetch("graph.json");
  const graph = await response.json();
  originalGraph = convertGraphToGalaxy(graph);
  activeTypes = new Set(Object.keys(graph.metadata.type_counts));
  renderTypeFilters(graph.metadata.type_counts);
  renderLayerFilters();
  renderStats(graph.metadata);
  await createPixi();
  bindControls();
  applyFilters();
}

async function createPixi() {
  const container = document.getElementById("galaxy2d");
  app = new PIXI.Application();
  await app.init({
    resizeTo: container,
    antialias: true,
    backgroundAlpha: 0,
    autoDensity: true,
    resolution: Math.min(window.devicePixelRatio || 1, 2),
  });
  container.appendChild(app.canvas);
  stageRoot = new PIXI.Container();
  linkLayer = new PIXI.Container();
  nodeLayer = new PIXI.Container();
  labelLayer = new PIXI.Container();
  stageRoot.addChild(linkLayer, nodeLayer, labelLayer);
  app.stage.addChild(stageRoot);
  stageRoot.eventMode = "static";
  app.stage.eventMode = "static";
  app.stage.hitArea = app.screen;
  app.stage.on("wheel", onWheel);
  app.stage.on("pointerdown", onStagePointerDown);
  app.stage.on("pointermove", onStagePointerMove);
  app.stage.on("pointerup", onStagePointerUp);
  app.stage.on("pointerupoutside", onStagePointerUp);
  window.addEventListener("resize", () => requestAnimationFrame(fitView));
}

function renderTypeFilters(typeCounts) {
  const root = document.getElementById("typeFilters");
  root.innerHTML = "";
  Object.entries(typeCounts).sort((a, b) => b[1] - a[1]).forEach(([type, count]) => {
    const label = document.createElement("label");
    label.innerHTML = `<input type="checkbox" data-type="${escapeHtml(type)}" checked><span><span class="pill">${escapeHtml(type)}</span>${count}</span>`;
    root.appendChild(label);
  });
}

function renderLayerFilters() {
  const root = document.getElementById("layerFilters");
  root.innerHTML = "";
  for (const [layer, labelText] of [["core", "Core"], ["active", "Active"], ["knowledge", "Knowledge"], ["episode", "Episodes"], ["external", "External"]]) {
    const label = document.createElement("label");
    label.innerHTML = `<input type="checkbox" data-layer="${escapeHtml(layer)}" checked><span><span class="pill">${escapeHtml(labelText)}</span></span>`;
    root.appendChild(label);
  }
}

function bindControls() {
  document.getElementById("search").addEventListener("input", scheduleApplyFilters);
  document.getElementById("weightFilter").addEventListener("input", event => {
    document.getElementById("weightValue").textContent = event.target.value;
    scheduleApplyFilters();
  });
  document.getElementById("timelineFilter").addEventListener("input", scheduleApplyFilters);
  document.getElementById("typeFilters").addEventListener("change", event => {
    if (!event.target.matches("input[type='checkbox']")) return;
    if (event.target.checked) activeTypes.add(event.target.dataset.type);
    else activeTypes.delete(event.target.dataset.type);
    scheduleApplyFilters();
  });
  document.getElementById("layerFilters").addEventListener("change", event => {
    if (!event.target.matches("input[type='checkbox']")) return;
    if (event.target.checked) activeLayers.add(event.target.dataset.layer);
    else activeLayers.delete(event.target.dataset.layer);
    scheduleApplyFilters();
  });
  document.getElementById("fit").addEventListener("click", fitView);
  document.getElementById("clearFocus").addEventListener("click", clearFocus);
  document.getElementById("focusNeighborhood").addEventListener("click", focusNeighborhood);
  document.getElementById("focusView").addEventListener("click", applyFilters);
}

function scheduleApplyFilters() {
  clearTimeout(renderTimer);
  renderTimer = setTimeout(applyFilters, 120);
}

function applyFilters() {
  const timelineCutoff = currentTimelineCutoff();
  const filtered = filterGalaxy(originalGraph, {
    query: document.getElementById("search").value,
    activeTypes,
    activeLayers,
    minWeight: Number(document.getElementById("weightFilter").value),
    timelineCutoff,
  });
  visibleGraph = buildClusterGalaxy2DLayout(filtered, { maxNodes: focusLimit, perNodeLimit: 4 });
  selectedNodeId = null;
  selectedNode = null;
  drawGalaxy();
  fitView();
  renderStats({ node_count: `${visibleGraph.nodes.length}/${originalGraph.nodes.length}`, edge_count: `${visibleGraph.links.length}/${originalGraph.links.length}` });
  emitEvent("view:filtered", null, { visible_nodes: visibleGraph.nodes.length });
}

function focusNeighborhood() {
  if (!selectedNode) return;
  visibleGraph = buildClusterGalaxy2DLayout(buildFocusGalaxy(originalGraph, {
    focusNodeId: selectedNode.id,
    maxNodes: 260,
    seedCount: 1,
    firstRingLimit: 160,
  }), { maxNodes: 260, focusNodeId: selectedNode.id });
  drawGalaxy();
  fitView();
  emitEvent("node:expanded", selectedNode, { visible_neighbors: visibleGraph.nodes.length - 1 });
}

function clearFocus() {
  selectedNodeId = null;
  selectedNode = null;
  document.getElementById("details").textContent = "Select a node to inspect linked memories.";
  document.getElementById("agentPrompt").textContent = "Select or drag a node to stage an agent prompt.";
  applyFilters();
  emitEvent("view:focus-cleared", null, {});
}

function drawGalaxy() {
  linkLayer.removeChildren();
  nodeLayer.removeChildren();
  labelLayer.removeChildren();
  const nodeById = new Map(visibleGraph.nodes.map(node => [node.id, node]));
  const linksToDraw = visibleLinksForSelection(visibleGraph.links, {
    selectedNodeId,
    hoveredNodeId,
    perNodeLimit: 4,
  });
  for (const link of linksToDraw) {
    const source = nodeById.get(String(link.source.id || link.source));
    const target = nodeById.get(String(link.target.id || link.target));
    if (!source || !target) continue;
    const line = new PIXI.Graphics();
    const selected = selectedNodeId && (source.id === selectedNodeId || target.id === selectedNodeId);
    line.moveTo(source.x, source.y).lineTo(target.x, target.y);
    line.stroke({ width: selected ? Math.max(2.2, Math.min(4.2, link.weight * 0.55)) : Math.max(0.25, Math.min(1.1, link.weight * 0.28)), color: selected ? 0xfacc15 : 0x31445f, alpha: selected ? 0.82 : 0.075 });
    linkLayer.addChild(line);
  }
  for (const node of visibleGraph.nodes) {
    const star = new PIXI.Graphics();
    star.eventMode = "static";
    star.cursor = "grab";
    star.memoryNode = node;
    drawStar(star, node);
    star.on("pointerdown", event => onNodePointerDown(event, node, star));
    star.on("pointerover", () => {
      hoveredNodeId = node.id;
      drawGalaxy();
      emitEvent("node:hovered", node, { layer: node.layer });
    });
    star.on("pointerout", () => {
      hoveredNodeId = null;
      drawGalaxy();
    });
    nodeLayer.addChild(star);
  }
  for (const node of selectVisibleLabels(visibleGraph.nodes, { zoom: scale, selectedNodeId, hoveredNodeId })) {
    const label = new PIXI.Text({ text: node.label, style: { fill: 0xe5f0ff, fontFamily: "Segoe UI, Microsoft YaHei, sans-serif", fontSize: 12, fontWeight: "600" } });
    label.x = node.x + node.renderRadius + 7;
    label.y = node.y - 8;
    label.alpha = node.id === selectedNodeId || node.id === hoveredNodeId ? 1 : 0.72;
    labelLayer.addChild(label);
  }
  updateTransform();
}

function drawStar(graphics, node) {
  const selected = node.id === selectedNodeId;
  const hovered = node.id === hoveredNodeId;
  graphics.clear();
  graphics.position.set(node.x, node.y);
  if (selected || hovered) {
    graphics.circle(0, 0, node.renderRadius + (selected ? 10 : 6));
    graphics.stroke({ width: selected ? 2.4 : 1.6, color: selected ? 0xfacc15 : 0x7dd3fc, alpha: 0.9 });
  }
  graphics.circle(0, 0, node.renderRadius);
  graphics.fill(parseColor(node.color));
}

function onNodePointerDown(event, node, star) {
  event.stopPropagation();
  selectedNodeId = node.id;
  selectedNode = node;
  showDetails(node);
  dragState = { node, star, start: event.global.clone(), origin: { x: node.x, y: node.y }, mode: "node" };
  star.cursor = "grabbing";
  emitEvent("node:selected", node, { layer: node.layer, visible_neighbors: countVisibleNeighbors(node.id) });
  emitEvent("node:drag-started", node, { layer: node.layer });
  drawGalaxy();
}

function onStagePointerDown(event) {
  dragState = { mode: "pan", start: event.global.clone(), origin: { ...pan } };
}

function onStagePointerMove(event) {
  if (!dragState) return;
  if (dragState.mode === "pan") {
    pan.x = dragState.origin.x + event.global.x - dragState.start.x;
    pan.y = dragState.origin.y + event.global.y - dragState.start.y;
    updateTransform();
    return;
  }
  const dx = (event.global.x - dragState.start.x) / scale;
  const dy = (event.global.y - dragState.start.y) / scale;
  dragState.node.x = dragState.origin.x + dx;
  dragState.node.y = dragState.origin.y + dy;
  emitEvent("node:dragged", dragState.node, { layer: dragState.node.layer });
  drawGalaxy();
}

function onStagePointerUp() {
  if (dragState?.mode === "node") {
    emitEvent("node:drag-ended", dragState.node, { layer: dragState.node.layer, visible_neighbors: countVisibleNeighbors(dragState.node.id) });
  }
  dragState = null;
}

function onWheel(event) {
  event.preventDefault();
  const factor = event.deltaY > 0 ? 0.9 : 1.1;
  scale = Math.max(0.25, Math.min(3.5, scale * factor));
  updateTransform();
  drawGalaxy();
}

function fitView() {
  if (!visibleGraph.nodes.length || !app) return;
  const bounds = visibleGraph.nodes.reduce((acc, node) => ({
    minX: Math.min(acc.minX, node.x),
    maxX: Math.max(acc.maxX, node.x),
    minY: Math.min(acc.minY, node.y),
    maxY: Math.max(acc.maxY, node.y),
  }), { minX: Infinity, maxX: -Infinity, minY: Infinity, maxY: -Infinity });
  const width = Math.max(1, bounds.maxX - bounds.minX);
  const height = Math.max(1, bounds.maxY - bounds.minY);
  scale = Math.min(app.screen.width / (width + 160), app.screen.height / (height + 160), 1.8);
  pan = {
    x: app.screen.width / 2 - ((bounds.minX + bounds.maxX) / 2) * scale,
    y: app.screen.height / 2 - ((bounds.minY + bounds.maxY) / 2) * scale,
  };
  updateTransform();
}

function updateTransform() {
  if (!stageRoot) return;
  stageRoot.scale.set(scale);
  stageRoot.position.set(pan.x, pan.y);
}

function showDetails(node) {
  document.getElementById("details").innerHTML = formatNodeDetails(node.raw);
}

function emitEvent(type, node, context) {
  const event = createMemoryGalaxyEvent(type, {
    node_id: node?.id,
    gesture: type.includes("drag") ? "drag" : type.includes("hover") ? "hover" : "click",
    view: viewName,
    context,
  });
  interactionLog.push(event);
  const prompt = suggestAgentPrompt(event, node?.raw || {});
  if (prompt) document.getElementById("agentPrompt").textContent = renderPromptText(prompt);
}

function currentTimelineCutoff() {
  const slider = document.getElementById("timelineFilter");
  const cutoff = timelineCutoffFromPercent(originalGraph.metadata.timeline || {}, Number(slider.value));
  document.getElementById("timelineValue").textContent = cutoff ? cutoff.slice(0, 10) : "All time";
  return cutoff;
}

function countVisibleNeighbors(nodeId) {
  return visibleGraph.links.filter(link => String(link.source.id || link.source) === nodeId || String(link.target.id || link.target) === nodeId).length;
}

function renderStats(metadata) {
  document.getElementById("stats").textContent = `${metadata.node_count} nodes, ${metadata.edge_count} edges`;
}

function parseColor(value) {
  return Number.parseInt(String(value || "#94a3b8").replace("#", ""), 16);
}

init().catch(error => {
  document.getElementById("stats").textContent = "Failed to load galaxy.";
  document.getElementById("details").textContent = String(error);
});

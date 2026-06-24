import {
  buildGalacticOrbital2DLayout,
  buildFocusGalaxy,
  convertGraphToGalaxy,
  filterGalaxy,
  labelAnchorForNode,
  selectVisibleLabels,
  springBackTarget,
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
const labelModeZoom = {
  minimal: 0.65,
  normal: 1,
  dense: 1.8,
};
const springProfiles = [
  { limit: 15, label: "Pinned", retainRatio: 0.08, stiffness: 0.045, damping: 0.62, neighborPull: 0.012 },
  { limit: 45, label: "Gentle", retainRatio: 0.14, stiffness: 0.06, damping: 0.68, neighborPull: 0.022 },
  { limit: 75, label: "Playful", retainRatio: 0.22, stiffness: 0.085, damping: 0.72, neighborPull: 0.038 },
  { limit: 101, label: "Elastic", retainRatio: 0.32, stiffness: 0.115, damping: 0.76, neighborPull: 0.056 },
];

let app;
let stageRoot;
let linkLayer;
let orbitLayer;
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
const springAnimations = new Map();
const dragOffsetByNodeId = new Map();

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
  orbitLayer = new PIXI.Container();
  linkLayer = new PIXI.Container();
  nodeLayer = new PIXI.Container();
  labelLayer = new PIXI.Container();
  stageRoot.addChild(orbitLayer, linkLayer, nodeLayer, labelLayer);
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
  app.ticker.add(tickSpringAnimations);
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
  document.getElementById("edgeDensity").addEventListener("input", event => {
    document.getElementById("edgeDensityValue").textContent = `${event.target.value} links / star`;
    scheduleApplyFilters();
  });
  document.getElementById("labelMode").addEventListener("change", drawGalaxy);
  document.getElementById("springStrength").addEventListener("input", event => {
    document.getElementById("springStrengthValue").textContent = currentSpringProfile().label;
  });
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
  const edgeDensity = currentEdgeDensity();
  const filtered = filterGalaxy(originalGraph, {
    query: document.getElementById("search").value,
    activeTypes,
    activeLayers,
    minWeight: Number(document.getElementById("weightFilter").value),
    timelineCutoff,
  });
  visibleGraph = buildGalacticOrbital2DLayout(filtered, { maxNodes: focusLimit, perNodeLimit: edgeDensity });
  for (const node of visibleGraph.nodes) {
    const offset = dragOffsetByNodeId.get(node.id);
    if (!offset) continue;
    node.x += offset.x;
    node.y += offset.y;
  }
  selectedNodeId = null;
  selectedNode = null;
  drawGalaxy();
  fitView();
  renderStats({ node_count: `${visibleGraph.nodes.length}/${originalGraph.nodes.length}`, edge_count: `${visibleGraph.links.length}/${originalGraph.links.length}` });
  emitEvent("view:filtered", null, { visible_nodes: visibleGraph.nodes.length });
}

function focusNeighborhood() {
  if (!selectedNode) return;
  visibleGraph = buildGalacticOrbital2DLayout(buildFocusGalaxy(originalGraph, {
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
  orbitLayer.removeChildren();
  linkLayer.removeChildren();
  nodeLayer.removeChildren();
  labelLayer.removeChildren();
  const nodeById = new Map(visibleGraph.nodes.map(node => [node.id, node]));
  drawSystemGuides();
  const linksToDraw = visibleLinksForSelection(visibleGraph.links, {
    selectedNodeId,
    hoveredNodeId,
    perNodeLimit: currentEdgeDensity(),
  });
  for (const link of linksToDraw) {
    const source = nodeById.get(String(link.source.id || link.source));
    const target = nodeById.get(String(link.target.id || link.target));
    if (!source || !target) continue;
    const line = new PIXI.Graphics();
    const selected = selectedNodeId && (source.id === selectedNodeId || target.id === selectedNodeId);
    const sameSystem = source.memorySystem && source.memorySystem === target.memorySystem;
    line.moveTo(source.x, source.y).lineTo(target.x, target.y);
    line.stroke({
      width: selected
        ? Math.max(2.4, Math.min(4.6, link.weight * 0.58))
        : sameSystem
          ? Math.max(0.35, Math.min(1.15, link.weight * 0.28))
          : Math.max(0.3, Math.min(0.9, link.weight * 0.18)),
      color: selected ? 0xfacc15 : sameSystem ? 0x3f6d8f : 0x6d5f9d,
      alpha: selected ? 0.84 : sameSystem ? 0.12 : 0.055,
    });
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
  const placedLabelBounds = [];
  for (const node of selectVisibleLabels(visibleGraph.nodes, { zoom: scale * currentLabelZoomBoost(), selectedNodeId, hoveredNodeId })) {
    drawNodeLabel(node, placedLabelBounds);
  }
  updateTransform();
}

function drawNodeLabel(node, placedLabelBounds) {
  const anchor = labelAnchorForNode(node);
  const isPinned = node.id === selectedNodeId || node.id === hoveredNodeId || node.orbitalRole === "star" || node.orbitalRole === "galactic-core";
  const fontSize = isPinned ? 13 : 11;
  const text = new PIXI.Text({
    text: node.label,
    resolution: 2,
    style: {
      fill: 0xf8fbff,
      fontFamily: "Segoe UI, Microsoft YaHei, sans-serif",
      fontSize,
      fontWeight: isPinned ? "700" : "600",
      lineJoin: "round",
      stroke: { color: 0x020617, width: 3, alpha: 0.75 },
    },
  });
  text.anchor.set(anchor.align === "left" ? 0 : 1, 0.5);
  text.x = anchor.x;
  text.y = anchor.y;
  const bounds = {
    x1: anchor.align === "left" ? text.x : text.x - text.width,
    y1: text.y - text.height / 2,
    x2: anchor.align === "left" ? text.x + text.width : text.x,
    y2: text.y + text.height / 2,
  };
  if (!isPinned && placedLabelBounds.some(item => boundsOverlap(bounds, item))) return;
  placedLabelBounds.push(bounds);
  const plate = new PIXI.Graphics();
  const padX = 7;
  const padY = 4;
  plate.roundRect(bounds.x1 - padX, bounds.y1 - padY, text.width + padX * 2, text.height + padY * 2, 7);
  plate.fill({ color: 0x020817, alpha: isPinned ? 0.74 : 0.46 });
  plate.stroke({ width: 1, color: isPinned ? 0x7dd3fc : 0x334155, alpha: isPinned ? 0.42 : 0.22 });
  labelLayer.addChild(plate);
  labelLayer.addChild(text);
}

function boundsOverlap(a, b) {
  return a.x1 < b.x2 && a.x2 > b.x1 && a.y1 < b.y2 && a.y2 > b.y1;
}

function drawSystemGuides() {
  if (!visibleGraph.systems) return;
  for (const system of visibleGraph.systems) {
    if (system.key === "router") continue;
    const guide = new PIXI.Graphics();
    guide.ellipse(system.x, system.y, system.orbitRadius, system.orbitRadius * 0.64);
    guide.stroke({ width: 1.2, color: 0x5b6f91, alpha: 0.16 });
    guide.ellipse(system.x, system.y, system.orbitRadius * 1.42, system.orbitRadius * 0.91);
    guide.stroke({ width: 0.8, color: 0x5b6f91, alpha: 0.08 });
    orbitLayer.addChild(guide);
  }
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
  springAnimations.delete(node.id);
  dragState = {
    node,
    star,
    start: event.global.clone(),
    origin: { x: node.x, y: node.y },
    home: { x: node.homeX ?? node.x, y: node.homeY ?? node.y },
    mode: "node",
  };
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
  applyNeighborGravity(dragState.node, dx, dy);
  emitEvent("node:dragged", dragState.node, { layer: dragState.node.layer });
  drawGalaxy();
}

function onStagePointerUp() {
  if (dragState?.mode === "node") {
    const spring = currentSpringProfile();
    const target = springBackTarget(dragState.node, { retainRatio: spring.retainRatio });
    springAnimations.set(dragState.node.id, {
      node: dragState.node,
      target,
      stiffness: spring.stiffness,
      damping: spring.damping,
      velocity: { x: 0, y: 0 },
    });
    dragOffsetByNodeId.set(dragState.node.id, {
      x: target.x - (dragState.node.homeX ?? target.x),
      y: target.y - (dragState.node.homeY ?? target.y),
    });
    emitEvent("node:drag-ended", dragState.node, { layer: dragState.node.layer, visible_neighbors: countVisibleNeighbors(dragState.node.id) });
  }
  dragState = null;
}

function tickSpringAnimations() {
  if (springAnimations.size === 0) return;
  let changed = false;
  for (const [nodeId, animation] of springAnimations) {
    const node = animation.node;
    const dx = animation.target.x - node.x;
    const dy = animation.target.y - node.y;
    animation.velocity.x = (animation.velocity.x + dx * animation.stiffness) * animation.damping;
    animation.velocity.y = (animation.velocity.y + dy * animation.stiffness) * animation.damping;
    node.x += animation.velocity.x;
    node.y += animation.velocity.y;
    if (Math.abs(dx) < 0.6 && Math.abs(dy) < 0.6 && Math.hypot(animation.velocity.x, animation.velocity.y) < 0.25) {
      node.x = animation.target.x;
      node.y = animation.target.y;
      springAnimations.delete(nodeId);
    }
    changed = true;
  }
  if (changed) drawGalaxy();
}

function applyNeighborGravity(node, dx, dy) {
  const neighborIds = new Set();
  for (const link of visibleGraph.links) {
    const source = String(link.source.id || link.source);
    const target = String(link.target.id || link.target);
    if (source === node.id) neighborIds.add(target);
    if (target === node.id) neighborIds.add(source);
  }
  for (const neighbor of visibleGraph.nodes) {
    if (!neighborIds.has(neighbor.id)) continue;
    const pull = currentSpringProfile().neighborPull;
    neighbor.x += dx * pull;
    neighbor.y += dy * pull;
  }
}

function currentEdgeDensity() {
  return Math.max(1, Math.min(8, Number(document.getElementById("edgeDensity")?.value || 4)));
}

function currentLabelZoomBoost() {
  const mode = document.getElementById("labelMode")?.value || "normal";
  return labelModeZoom[mode] || labelModeZoom.normal;
}

function currentSpringProfile() {
  const value = Number(document.getElementById("springStrength")?.value || 70);
  return springProfiles.find(profile => value < profile.limit) || springProfiles[2];
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

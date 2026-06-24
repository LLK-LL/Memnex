import { convertGraphToGalaxy, filterGalaxy } from "./memory-galaxy-core.js";
import { createInteractionLog, createMemoryGalaxyEvent, suggestAgentPrompt } from "./memory-galaxy-events.js";
import { buildCometOverlayLayout, buildGalaxyOverviewLayout, buildPlanetSatelliteLayout, buildSolarSystemLayout } from "./memory-galaxy-layouts.js";
import { createMemoryGalaxyRenderer } from "./memory-galaxy-renderer.js";
import { createGalaxyViewState, enterGalaxyView, enterPlanetView, enterSolarView, goBackView } from "./memory-galaxy-view-state.js";
import { escapeHtml, formatNodeDetails, renderPromptText, timelineCutoffFromPercent } from "./viewer-shared.js";

const viewName = "2d-memory-galaxy";
const focusLimit = 900;
const interactionLog = createInteractionLog();
const state = createGalaxyViewState();

let app;
let renderer;
let originalGraph = { nodes: [], links: [], metadata: {} };
let filteredGraph = { nodes: [], links: [], metadata: {} };
let currentLayout = null;
let activeTypes = new Set();
let activeLayers = new Set(["core", "active", "knowledge", "episode", "external"]);
let renderTimer = null;
let lastSystemTap = { key: null, time: 0 };

async function init() {
  if (!window.PIXI) throw new Error("PixiJS failed to load from CDN.");
  const response = await fetch("graph.json");
  const graph = await response.json();
  originalGraph = convertGraphToGalaxy(graph);
  activeTypes = new Set(Object.keys(graph.metadata.type_counts || {}));
  renderTypeFilters(graph.metadata.type_counts || {});
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
  renderer = createMemoryGalaxyRenderer({ PIXI: window.PIXI, app, stage: app.stage });
  window.addEventListener("resize", () => {
    if (currentLayout) requestAnimationFrame(() => renderer.fitToBounds(currentLayout.bounds));
  });
}

function bindControls() {
  document.getElementById("search")?.addEventListener("input", scheduleApplyFilters);
  document.getElementById("weightFilter")?.addEventListener("input", event => {
    document.getElementById("weightValue").textContent = event.target.value;
    scheduleApplyFilters();
  });
  document.getElementById("timelineFilter")?.addEventListener("input", scheduleApplyFilters);
  document.getElementById("typeFilters")?.addEventListener("change", event => {
    if (!event.target.matches("input[type='checkbox']")) return;
    if (event.target.checked) activeTypes.add(event.target.dataset.type);
    else activeTypes.delete(event.target.dataset.type);
    scheduleApplyFilters();
  });
  document.getElementById("layerFilters")?.addEventListener("change", event => {
    if (!event.target.matches("input[type='checkbox']")) return;
    if (event.target.checked) activeLayers.add(event.target.dataset.layer);
    else activeLayers.delete(event.target.dataset.layer);
    scheduleApplyFilters();
  });
  document.getElementById("labelMode")?.addEventListener("change", drawCurrentLayout);
  document.getElementById("nodeScale")?.addEventListener("input", event => {
    state.nodeScale = Number(event.target.value);
    document.getElementById("nodeScaleValue").textContent = state.nodeScale.toFixed(2);
    drawCurrentLayout();
  });
  document.getElementById("relationshipMode")?.addEventListener("change", event => {
    state.relationshipMode = event.target.value;
    drawCurrentLayout();
  });
  document.getElementById("fit")?.addEventListener("click", () => {
    if (currentLayout) renderer.fitToBounds(currentLayout.bounds);
  });
  document.getElementById("clearFocus")?.addEventListener("click", () => {
    enterGalaxyView(state);
    state.selectedNodeId = null;
    drawCurrentLayout();
  });
  document.getElementById("focusView")?.addEventListener("click", drawCurrentLayout);
  document.getElementById("backView")?.addEventListener("click", () => {
    goBackView(state);
    drawCurrentLayout();
  });
}

function scheduleApplyFilters() {
  clearTimeout(renderTimer);
  renderTimer = setTimeout(applyFilters, 120);
}

function applyFilters() {
  const timelineCutoff = currentTimelineCutoff();
  filteredGraph = filterGalaxy(originalGraph, {
    query: document.getElementById("search")?.value || "",
    activeTypes,
    activeLayers,
    minWeight: Number(document.getElementById("weightFilter")?.value || 0),
    timelineCutoff,
  });
  if (filteredGraph.nodes.length > focusLimit) {
    filteredGraph = {
      ...filteredGraph,
      nodes: filteredGraph.nodes.slice(0, focusLimit),
      links: filteredGraph.links.filter(link => {
        const visible = new Set(filteredGraph.nodes.slice(0, focusLimit).map(node => node.id));
        return visible.has(String(link.source.id || link.source)) && visible.has(String(link.target.id || link.target));
      }),
    };
  }
  drawCurrentLayout();
  renderStats({
    node_count: `${filteredGraph.nodes.length}/${originalGraph.nodes.length}`,
    edge_count: `${filteredGraph.links.length}/${originalGraph.links.length}`,
  });
  emitEvent("view:filtered", null, { visible_nodes: filteredGraph.nodes.length });
}

function drawCurrentLayout() {
  if (!renderer || !app) return;
  currentLayout = buildActiveLayout();
  renderer.draw(currentLayout, state, {
    onSystemClick: system => {
      if (state.view !== "galaxy" || system.key === "router") return;
      const now = Date.now();
      const doubleTap = lastSystemTap.key === system.key && now - lastSystemTap.time < 420;
      lastSystemTap = { key: system.key, time: now };
      state.selectedSystem = system.key;
      state.selectedNodeId = null;
      showSystemDetails(system);
      emitEvent("system:selected", null, { system: system.key });
      if (doubleTap) enterSolarView(state, system.key);
      drawCurrentLayout();
    },
    onSystemHover: system => {
      if (state.view !== "galaxy") return;
      drawCurrentLayout();
    },
    onCometTap: comet => {
      showCometDetails(comet);
      document.getElementById("agentPrompt").textContent = `彗星 ${comet.label} 正在影响 ${comet.influences.map(item => item.system).join(", ")}`;
    },
    onNodePointerDown: node => {
      state.selectedNodeId = node.id;
      showDetails(node);
      emitEvent("node:selected", node, { layer: node.raw?.galaxy_layer, system: node.memorySystem });
    },
    onNodeTap: node => {
      state.selectedNodeId = node.id;
      showDetails(node);
      if (state.view === "solar" && (node.orbitRole === "planet" || String(node.orbitalRole || "").includes("planet"))) {
        enterPlanetView(state, node.id);
      }
      emitEvent("node:selected", node, { layer: node.raw?.galaxy_layer, system: node.memorySystem });
      drawCurrentLayout();
    },
    onNodePointerOver: node => {
      state.hoveredNodeId = node.id;
      drawCurrentLayout();
    },
    onNodePointerOut: () => {
      state.hoveredNodeId = null;
      drawCurrentLayout();
    },
    onNodeDrag: node => {
      state.selectedNodeId = node.id;
      emitEvent("node:dragged", node, { system: node.memorySystem });
    },
    onNodeDragEnd: node => {
      state.selectedNodeId = node.id;
      emitEvent("node:drag-ended", node, { system: node.memorySystem });
    },
  });
  renderer.fitToBounds(currentLayout.bounds);
  updateViewBadge();
}

function buildActiveLayout() {
  const size = { width: app.screen.width, height: app.screen.height, nodeScale: state.nodeScale };
  if (state.view === "solar") {
    return buildSolarSystemLayout(filteredGraph, state.selectedSystem, size);
  }
  if (state.view === "planet") {
    return buildPlanetSatelliteLayout(filteredGraph, state.selectedSystem, state.selectedPlanet, size);
  }
  const layout = buildGalaxyOverviewLayout(filteredGraph, size);
  const overlay = buildCometOverlayLayout(layout, buildActiveComets());
  return { ...layout, comets: overlay.comets };
}

function buildActiveComets() {
  return [{
    id: "comet:active-memory-galaxy",
    label: "Active Memory Galaxy Work",
    comet_type: "active_task",
    trajectory: ["preference", "skill", "harness", "rule"],
    influenced_systems: [
      { system: "skill", weight: 0.92 },
      { system: "harness", weight: 0.84 },
      { system: "preference", weight: 0.78 },
      { system: "rule", weight: 0.55 },
    ],
  }, {
    id: "comet:verification-trail",
    label: "Verification Trail",
    comet_type: "verification",
    trajectory: ["harness", "source", "rule"],
    influenced_systems: [
      { system: "harness", weight: 0.86 },
      { system: "source", weight: 0.64 },
      { system: "rule", weight: 0.48 },
    ],
  }, {
    id: "comet:user-feedback",
    label: "User Feedback",
    comet_type: "feedback",
    trajectory: ["preference", "persona", "knowledge"],
    influenced_systems: [
      { system: "preference", weight: 0.9 },
      { system: "persona", weight: 0.58 },
      { system: "knowledge", weight: 0.5 },
    ],
  }];
}

function renderTypeFilters(typeCounts) {
  const root = document.getElementById("typeFilters");
  if (!root) return;
  root.innerHTML = "";
  Object.entries(typeCounts).sort((a, b) => b[1] - a[1]).forEach(([type, count]) => {
    const label = document.createElement("label");
    label.innerHTML = `<input type="checkbox" data-type="${escapeHtml(type)}" checked><span><span class="pill">${escapeHtml(type)}</span>${count}</span>`;
    root.appendChild(label);
  });
}

function renderLayerFilters() {
  const root = document.getElementById("layerFilters");
  if (!root) return;
  root.innerHTML = "";
  for (const [layer, labelText] of [["core", "Core"], ["active", "Active"], ["knowledge", "Knowledge"], ["episode", "Episodes"], ["external", "External"]]) {
    const label = document.createElement("label");
    label.innerHTML = `<input type="checkbox" data-layer="${escapeHtml(layer)}" checked><span><span class="pill">${escapeHtml(labelText)}</span></span>`;
    root.appendChild(label);
  }
}

function currentTimelineCutoff() {
  const slider = document.getElementById("timelineFilter");
  const cutoff = timelineCutoffFromPercent(originalGraph.metadata.timeline || {}, Number(slider?.value || 100));
  const label = document.getElementById("timelineValue");
  if (label) label.textContent = cutoff ? cutoff.slice(0, 10) : "All time";
  return cutoff;
}

function showDetails(node) {
  document.getElementById("details").innerHTML = formatNodeDetails(node.raw || node);
}

function showSystemDetails(system) {
  document.getElementById("details").innerHTML = `
    <div class="node-title">${escapeHtml(system.label)}</div>
    <div class="meta">Layer: ${escapeHtml(system.layer)} · Mini orbits: ${(system.miniOrbits || []).length}</div>
    <p>单击高亮整个太阳系；双击进入该太阳系内部视图。行星、卫星和证据轨道会在太阳系视图中展开。</p>
  `;
  document.getElementById("agentPrompt").textContent = `已选中 ${system.label}。要查看这个太阳系内部结构，可以双击它。`;
}

function showCometDetails(comet) {
  document.getElementById("details").innerHTML = `
    <div class="node-title">${escapeHtml(comet.label)}</div>
    <div class="meta">Comet type: ${escapeHtml(comet.cometType || "active_task")}</div>
    <p>Influenced systems: ${escapeHtml(comet.influences.map(item => `${item.system} ${Math.round(item.weight * 100)}%`).join(", "))}</p>
  `;
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

function updateViewBadge() {
  let badge = document.getElementById("viewBadge");
  if (!badge) {
    badge = document.createElement("div");
    badge.id = "viewBadge";
    badge.className = "view-badge";
    document.querySelector(".sidebar header")?.appendChild(badge);
  }
  badge.textContent = state.view === "galaxy"
    ? "Galaxy Overview"
    : state.view === "solar"
      ? `Solar Focus: ${state.selectedSystem}`
      : `Planet Focus: ${state.selectedPlanet}`;
}

function renderStats(metadata) {
  const stats = document.getElementById("stats");
  if (!stats) return;
  stats.textContent = `${metadata.node_count} nodes, ${metadata.edge_count} edges`;
}

init().catch(error => {
  document.getElementById("stats").textContent = "Failed to load galaxy.";
  document.getElementById("details").textContent = String(error);
});

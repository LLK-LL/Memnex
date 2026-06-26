import { convertGraphToGalaxy, filterGalaxy } from "./memory-galaxy-core.js";
import { createInteractionLog, createMemoryGalaxyEvent, suggestAgentPrompt } from "./memory-galaxy-events.js";
import { buildCometOverlayLayout, buildGalaxyOverviewLayout, buildPlanetSatelliteLayout, buildSolarSystemLayout } from "./memory-galaxy-layouts.js";
import { createMemoryGalaxyRenderer } from "./memory-galaxy-renderer.js";
import { memorySystemForData } from "./memory-galaxy-systems.js";
import { createGalaxyViewState, enterGalaxyView, enterPlanetView, enterSolarView, goBackView, selectGalaxySystem, selectSolarPlanet } from "./memory-galaxy-view-state.js";
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
let lastPlanetTap = { id: null, time: 0 };
window.__memoryGalaxyDebug = {
  getState: () => ({
    view: state.view,
    selectedSystem: state.selectedSystem,
    selectedPlanet: state.selectedPlanet,
    selectedNodeId: state.selectedNodeId,
    animationSpeed: state.animationSpeed,
  }),
  getLayout: () => currentLayout,
  getTransform: () => renderer?.getTransform?.() || null,
  getGraphSummary: () => ({
    original: summarizeSystems(originalGraph.nodes),
    filtered: summarizeSystems(filteredGraph.nodes),
    layout: summarizeSystems(currentLayout?.nodes || []),
    systems: (currentLayout?.systems || []).map(system => system.key),
  }),
};

function loadEmbeddedGraph() {
  const el = document.getElementById("graph-data");
  if (!el?.textContent) return null;
  return JSON.parse(el.textContent);
}

async function loadGraph() {
  const embedded = loadEmbeddedGraph();
  if (embedded) return embedded;
  const response = await fetch("graph.json");
  if (!response.ok) throw new Error(`graph.json load failed: ${response.status}`);
  return response.json();
}

async function init() {
  if (!window.PIXI) throw new Error("PixiJS failed to load from CDN.");
  const graph = await loadGraph();
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
  app.canvas.addEventListener("dblclick", handleCanvasDoubleClick);
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
  document.getElementById("animationSpeed")?.addEventListener("input", event => {
    state.animationSpeed = Number(event.target.value);
    document.getElementById("animationSpeedValue").textContent = `${state.animationSpeed.toFixed(2)}x`;
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
    const visibleNodes = capNodesBySystem(filteredGraph.nodes, focusLimit);
    const visible = new Set(visibleNodes.map(node => node.id));
    filteredGraph = {
      ...filteredGraph,
      nodes: visibleNodes,
      links: filteredGraph.links.filter(link =>
        visible.has(String(link.source.id || link.source)) && visible.has(String(link.target.id || link.target))
      ),
    };
  }
  drawCurrentLayout();
  renderStats({
    node_count: `${filteredGraph.nodes.length}/${originalGraph.nodes.length}`,
    edge_count: `${filteredGraph.links.length}/${originalGraph.links.length}`,
  });
  emitEvent("view:filtered", null, { visible_nodes: filteredGraph.nodes.length });
}

function capNodesBySystem(nodes, limit) {
  const selected = [];
  const selectedIds = new Set();
  const sorted = [...nodes].sort((a, b) => scoreVisibleNode(b) - scoreVisibleNode(a));
  const systems = [...new Set(sorted.map(node => visibleNodeSystem(node)).filter(Boolean))];

  for (const system of systems) {
    const representative = sorted.find(node => visibleNodeSystem(node) === system && !selectedIds.has(node.id));
    if (!representative) continue;
    selected.push(representative);
    selectedIds.add(representative.id);
    if (selected.length >= limit) return selected;
  }

  for (const node of sorted) {
    if (selectedIds.has(node.id)) continue;
    selected.push(node);
    selectedIds.add(node.id);
    if (selected.length >= limit) break;
  }
  return selected;
}

function visibleNodeSystem(node) {
  return node.memorySystem || memorySystemForData(node.raw || node);
}

function scoreVisibleNode(node) {
  const raw = node.raw || {};
  const layerScore = { core: 80, active: 50, knowledge: 25, episode: 10, external: 6 }[node.layer] || 0;
  return layerScore
    + Number(raw.importance || 0) * 10
    + Number(raw.activity || 0) * 5
    + Math.log1p(Number(raw.mention_count || 0)) * 3;
}

function summarizeSystems(nodes) {
  return (nodes || []).reduce((acc, node) => {
    const system = visibleNodeSystem(node);
    acc[system] = (acc[system] || 0) + 1;
    return acc;
  }, {});
}

function drawCurrentLayout() {
  if (!renderer || !app) return;
  currentLayout = buildActiveLayout();
  renderer.draw(currentLayout, state, {
    onSystemClick: (system, event) => {
      const result = selectGalaxySystem(state, system.key, {
        lastSystemTap,
        now: Date.now(),
        forceEnter: clickCount(event) >= 2,
      });
      lastSystemTap = result.lastSystemTap;
      showSystemDetails(system);
      emitEvent("system:selected", null, { system: system.key });
      drawCurrentLayout();
      if (clickCount(event) < 2) renderer.focusOn(system.x, system.y, 1.04);
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
    onNodeTap: (node, event) => {
      if (state.view === "galaxy") {
        const systemKey = node.systemKey || (node.memorySystem && node.memorySystem !== "router" ? node.memorySystem : null);
        const system = systemKey ? currentLayout?.systems?.find(item => item.key === systemKey) : null;
        if (system) {
          const result = selectGalaxySystem(state, system.key, {
            lastSystemTap,
            now: Date.now(),
            forceEnter: clickCount(event) >= 2,
          });
          lastSystemTap = result.lastSystemTap;
          state.selectedNodeId = node.id;
          showSystemDetails(system);
          emitEvent("system:selected", null, { system: system.key });
          drawCurrentLayout();
          if (clickCount(event) < 2) renderer.focusOn(system.x, system.y, 1.04);
          return;
        }
      }
      if (state.view === "solar") {
        const planetNode = resolveSolarPlanetNode(currentLayout, node);
        if (planetNode) {
          const result = selectSolarPlanet(state, planetNode.id, {
            lastPlanetTap,
            now: Date.now(),
            forceEnter: clickCount(event) >= 2,
          });
          lastPlanetTap = result.lastPlanetTap;
          state.selectedNodeId = planetNode.id;
          showDetails(planetNode);
          emitEvent("node:selected", planetNode, { layer: planetNode.raw?.galaxy_layer, system: planetNode.memorySystem });
          drawCurrentLayout();
          if (clickCount(event) < 2) renderer.focusOn(planetNode.x, planetNode.y, 1.06);
          return;
        }
      }
      state.selectedNodeId = node.id;
      showDetails(node);
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

function clickCount(event) {
  return Number(
    event?.detail
    ?? event?.nativeEvent?.detail
    ?? event?.originalEvent?.detail
    ?? 0,
  );
}

function handleCanvasDoubleClick(event) {
  if (!renderer || !currentLayout) return;
  const point = screenToWorldPoint(event);
  if (!point) return;

  if (state.view === "galaxy") {
    const system = (state.selectedSystem
      ? currentLayout?.systems?.find(item => item.key === state.selectedSystem)
      : null) || findGalaxySystemAt(point.x, point.y, currentLayout);
    if (!system) return;
    const result = selectGalaxySystem(state, system.key, {
      lastSystemTap,
      now: Date.now(),
      forceEnter: true,
    });
    lastSystemTap = result.lastSystemTap;
    showSystemDetails(system);
    emitEvent("system:selected", null, { system: system.key });
    drawCurrentLayout();
    return;
  }

  if (state.view === "solar") {
    const selectedNode = state.selectedNodeId
      ? currentLayout?.nodes?.find(node => node.id === state.selectedNodeId)
      : null;
    const planetNode = resolveSolarPlanetNode(currentLayout, selectedNode) || findSolarPlanetAt(point.x, point.y, currentLayout);
    if (!planetNode) return;
    const result = selectSolarPlanet(state, planetNode.id, {
      lastPlanetTap,
      now: Date.now(),
      forceEnter: true,
    });
    lastPlanetTap = result.lastPlanetTap;
    state.selectedNodeId = planetNode.id;
    showDetails(planetNode);
    emitEvent("node:selected", planetNode, { layer: planetNode.raw?.galaxy_layer, system: planetNode.memorySystem });
    drawCurrentLayout();
  }
}

function screenToWorldPoint(event) {
  const canvas = app?.canvas;
  const transform = renderer?.getTransform?.();
  if (!canvas || !transform) return null;
  const rect = canvas.getBoundingClientRect();
  return {
    x: (event.clientX - rect.left - transform.pan.x) / transform.scale,
    y: (event.clientY - rect.top - transform.pan.y) / transform.scale,
  };
}

function findGalaxySystemAt(x, y, layout) {
  return (layout?.systems || []).find(system => {
    if (system.key === "router") return false;
    return Math.hypot(x - system.x, y - system.y) <= Math.max(26, (system.radius || 60) * 0.72);
  }) || null;
}

function findSolarPlanetAt(x, y, layout) {
  const satelliteSystemByParent = new Map((layout?.satelliteSystems || []).map(system => [system.parentId, system]));
  return (layout?.nodes || []).find(node => {
    if (node.orbitalRole !== "planet") return false;
    const system = satelliteSystemByParent.get(node.id);
    const radius = Math.max(18, (system?.radius || 0) + 12, (node.renderRadius || 0) + 10);
    return Math.hypot(x - node.x, y - node.y) <= radius;
  }) || null;
}

function resolveSolarPlanetNode(layout, node) {
  if (!layout || !node) return null;
  if (node.orbitalRole === "planet") return node;
  if (!node.parentPlanetId) return null;
  return layout.nodes.find(item => item.id === node.parentPlanetId) || null;
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

import { convertGraphToGalaxy, filterGalaxy, groupNeighborRelations } from "./memory-galaxy-core.js";
import { createInteractionLog, createMemoryGalaxyEvent, suggestAgentPrompt } from "./memory-galaxy-events.js";
import { buildCometOverlayLayout, buildGalaxyOverviewLayout, buildPlanetSatelliteLayout, buildSolarSystemLayout } from "./memory-galaxy-layouts.js";
import { createMemoryGalaxyRenderer } from "./memory-galaxy-renderer.js";
import { memorySystemForData, systemColors } from "./memory-galaxy-systems.js";
import { createGalaxyViewState, enterGalaxyView, goBackView, selectGalaxySystem, selectSolarPlanet } from "./memory-galaxy-view-state.js";
import { copyableInline, escapeHtml, formatNodeDetails, renderInspectorList, renderMetricGrid, renderPromptText, renderTag, timelineCutoffFromPercent } from "./viewer-shared.js";

const viewName = "2d-memory-galaxy";
const focusLimit = 900;
const interactionLog = createInteractionLog();
const state = createGalaxyViewState();

state.relationshipMode = "all";
state.labelMode = "medium";
state.showComets = false;
state.showOrbitGuides = true;
state.motionEnabled = true;

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
let shouldAutoFit = true;
let activeInspectorTab = "overview";
let minimapDragActive = false;
let pendingFitBounds = null;

const PERF_SAMPLE_LIMIT = 36;
const PERF_SAMPLE_INTERVAL_MS = 1000;
const perfState = {
  frames: 0,
  frameTimeTotal: 0,
  lastSampleAt: performance.now(),
  samples: new Array(PERF_SAMPLE_LIMIT).fill(0),
  sampleIndex: 0,
  sampleCount: 0,
  bars: [],
  gpuRenderer: "",
  backendPerformance: null,
  backendPerformanceAt: 0,
  backendUnavailable: false,
  lastStats: {
    fps: 0,
    frameTime: 0,
    cpuLoad: 0,
    memory: "N/A",
    gpuEstimate: 0,
  },
};

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
  getPerformanceStats: () => ({
    ...perfState.lastStats,
    sampleCount: perfState.sampleCount,
    sampleLimit: PERF_SAMPLE_LIMIT,
  }),
};

function loadEmbeddedGraph() {
  const el = document.getElementById("graph-data");
  if (!el?.textContent) return null;
  return JSON.parse(el.textContent);
}

async function loadGraph() {
  const backendGraph = await loadBackendGraph();
  if (backendGraph) return backendGraph;
  const embedded = loadEmbeddedGraph();
  if (embedded) return embedded;
  const response = await fetch("graph.json");
  if (!response.ok) throw new Error(`graph.json load failed: ${response.status}`);
  return response.json();
}

async function loadBackendGraph() {
  try {
    const response = await fetch("/api/graph", { cache: "no-store" });
    if (!response.ok || !response.headers.get("content-type")?.includes("application/json")) return null;
    const graph = await response.json();
    return graph?.elements?.nodes && graph?.elements?.edges ? graph : null;
  } catch {
    return null;
  }
}

async function init() {
  if (!window.PIXI) throw new Error("PixiJS failed to load from CDN.");
  const graph = await loadGraph();
  originalGraph = convertGraphToGalaxy(graph);
  activeTypes = new Set(Object.keys(graph.metadata.type_counts || {}));
  renderTypeFilters(graph.metadata.type_counts || {});
  renderLayerFilters();
  renderStats(graph.metadata);
  renderOrbitLegend();
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
  initPerformancePanel();
  app.ticker.add(ticker => recordPerformanceFrame(Number(ticker.deltaMS || 16.67)));
  app.canvas.addEventListener("dblclick", handleCanvasDoubleClick);
  window.addEventListener("resize", () => {
    if (currentLayout) requestAnimationFrame(() => renderer.fitToBounds(currentLayout.bounds));
  });
}

function bindControls() {
  const search = document.getElementById("search");
  const stageSearch = document.getElementById("stageSearchMirror");
  search?.addEventListener("input", event => {
    if (stageSearch && stageSearch.value !== event.target.value) stageSearch.value = event.target.value;
    scheduleApplyFilters();
  });
  stageSearch?.addEventListener("input", event => {
    if (search) search.value = event.target.value;
    scheduleApplyFilters();
  });
  document.getElementById("weightFilter")?.addEventListener("input", event => {
    document.getElementById("weightValue").textContent = Number(event.target.value).toFixed(1);
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
  document.getElementById("selectAllTypes")?.addEventListener("click", () => {
    activeTypes = new Set(Object.keys(originalGraph.metadata.type_counts || {}));
    for (const input of document.querySelectorAll("#typeFilters input[type='checkbox']")) input.checked = true;
    scheduleApplyFilters();
  });

  bindSegmentedControl("relationModeButtons", "relationshipMode", value => {
    state.relationshipMode = value;
    drawCurrentLayout({ preserveView: true });
  });
  bindSegmentedControl("labelModeButtons", "labelMode", value => {
    state.labelMode = value;
    drawCurrentLayout({ preserveView: true });
  });

  document.querySelector(".inspector-tabs")?.addEventListener("click", event => {
    const button = event.target.closest("button[data-tab]");
    if (!button) return;
    activeInspectorTab = button.dataset.tab || "overview";
    updateInspectorTabs();
  });

  document.getElementById("nodeScale")?.addEventListener("input", event => {
    const uiValue = Number(event.target.value);
    state.nodeScale = 0.48 * uiValue;
    document.getElementById("nodeScaleValue").textContent = uiValue.toFixed(2);
    shouldAutoFit = true;
    drawCurrentLayout();
  });

  document.getElementById("animationSpeed")?.addEventListener("input", event => {
    state.animationSpeed = Number(event.target.value);
    document.getElementById("animationSpeedValue").textContent = `${state.animationSpeed.toFixed(2)}x`;
  });

  document.getElementById("motionToggle")?.addEventListener("change", event => {
    state.motionEnabled = event.target.checked;
    state.animationSpeed = state.motionEnabled ? 1 : 0;
    document.getElementById("animationSpeed").value = String(state.animationSpeed);
    document.getElementById("animationSpeedValue").textContent = `${state.animationSpeed.toFixed(2)}x`;
  });
  document.getElementById("motionButton")?.addEventListener("click", () => {
    const toggle = document.getElementById("motionToggle");
    if (!toggle) return;
    toggle.checked = !toggle.checked;
    toggle.dispatchEvent(new Event("change", { bubbles: true }));
  });

  document.getElementById("cometsToggle")?.addEventListener("change", event => {
    state.showComets = event.target.checked;
    drawCurrentLayout({ preserveView: true });
  });

  document.getElementById("orbitGuidesToggle")?.addEventListener("change", event => {
    state.showOrbitGuides = event.target.checked;
    drawCurrentLayout({ preserveView: true });
  });

  const fit = () => {
    shouldAutoFit = true;
    if (currentLayout) drawCurrentLayout();
  };
  document.getElementById("fit")?.addEventListener("click", fit);
  document.getElementById("fitTop")?.addEventListener("click", fit);

  document.getElementById("clearFocus")?.addEventListener("click", () => {
    enterGalaxyView(state);
    state.selectedNodeId = null;
    shouldAutoFit = true;
    drawCurrentLayout();
  });

  document.getElementById("backView")?.addEventListener("click", () => {
    goBackView(state);
    shouldAutoFit = true;
    drawCurrentLayout();
  });

  document.getElementById("resetView")?.addEventListener("click", () => {
    enterGalaxyView(state);
    state.selectedNodeId = null;
    state.hoveredNodeId = null;
    state.selectedSystem = null;
    state.selectedPlanet = null;
    shouldAutoFit = true;
    drawCurrentLayout();
  });

  document.getElementById("crumbGalaxy")?.addEventListener("click", () => {
    enterGalaxyView(state);
    state.selectedNodeId = null;
    shouldAutoFit = true;
    drawCurrentLayout();
  });

  document.getElementById("crumbSystem")?.addEventListener("click", () => {
    if (!state.selectedSystem || state.view === "galaxy") return;
    state.view = "solar";
    state.selectedPlanet = null;
    state.selectedNodeId = null;
    shouldAutoFit = true;
    drawCurrentLayout();
  });

  bindMinimapControls();
}

function bindSegmentedControl(groupId, selectId, onChange) {
  const group = document.getElementById(groupId);
  const select = document.getElementById(selectId);
  group?.addEventListener("click", event => {
    const button = event.target.closest("button[data-value]");
    if (!button) return;
    const value = button.dataset.value;
    select.value = value;
    for (const item of group.querySelectorAll("button[data-value]")) item.classList.toggle("is-active", item === button);
    onChange(value);
  });
}

function scheduleApplyFilters() {
  clearTimeout(renderTimer);
  renderTimer = setTimeout(applyFilters, 120);
}

function applyFilters() {
  const timelineCutoff = currentTimelineCutoff();
  const scopedGraph = filterGalaxy(originalGraph, {
    query: document.getElementById("search")?.value || "",
    activeTypes,
    activeLayers,
    minWeight: Number(document.getElementById("weightFilter")?.value || 0),
    timelineCutoff,
  });
  filteredGraph = scopedGraph;
  if (filteredGraph.nodes.length > focusLimit) {
    const visibleNodes = capNodesBySystem(filteredGraph.nodes, focusLimit);
    const visible = new Set(visibleNodes.map(node => node.id));
    filteredGraph = {
      ...filteredGraph,
      nodes: visibleNodes,
      links: filteredGraph.links.filter(link =>
        visible.has(String(link.source.id || link.source)) && visible.has(String(link.target.id || link.target)),
      ),
    };
  }
  shouldAutoFit = true;
  drawCurrentLayout();
  renderStats({
    node_count: scopedGraph.nodes.length,
    edge_count: scopedGraph.links.length,
    total_node_count: originalGraph.nodes.length,
    total_edge_count: originalGraph.links.length,
    visible_node_count: filteredGraph.nodes.length,
    visible_edge_count: filteredGraph.links.length,
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

function drawCurrentLayout(options = {}) {
  if (!renderer || !app) return;
  currentLayout = buildActiveLayout();
  if (shouldAutoFit && !options.preserveView && currentLayout.bounds) {
    const nextTransform = transformForBounds(currentLayout.bounds);
    if (nextTransform && renderer.setTransform) {
      renderer.setTransform(nextTransform);
      shouldAutoFit = false;
    } else {
      pendingFitBounds = currentLayout.bounds;
    }
  }
  renderer.draw(currentLayout, state, {
    onSystemClick: (system, event) => {
      const result = selectGalaxySystem(state, system.key, {
        lastSystemTap,
        now: Date.now(),
        forceEnter: clickCount(event) >= 2,
      });
      lastSystemTap = result.lastSystemTap;
      state.selectedNodeId = result.entered ? null : `system:${system.key}`;
      showSystemSelection(system.key);
      emitEvent("system:selected", null, { system: system.key });
      shouldAutoFit = clickCount(event) >= 2;
      drawCurrentLayout({ preserveView: clickCount(event) < 2 });
      if (clickCount(event) < 2) renderer.focusOn(system.x, system.y, 1.04);
    },
    onSystemHover: () => {},
    onCometTap: comet => {
      showCometSelection(comet);
      document.getElementById("agentPrompt").textContent = `Comet ${comet.label} influences ${comet.influences.map(item => item.system).join(", ")}`;
    },
    onNodePointerDown: node => {
      if (state.view === "solar" || state.view === "planet") return;
      state.selectedNodeId = node.id;
      showNodeSelection(node);
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
          state.selectedNodeId = result.entered ? null : node.id;
          if (result.entered) showSystemSelection(system.key);
          else showNodeSelection(node);
          emitEvent("system:selected", null, { system: system.key });
          shouldAutoFit = clickCount(event) >= 2;
          drawCurrentLayout({ preserveView: clickCount(event) < 2 });
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
          showNodeSelection(planetNode);
          emitEvent("node:selected", planetNode, { layer: planetNode.raw?.galaxy_layer, system: planetNode.memorySystem });
          if (clickCount(event) < 2) {
            state.selectedNodeId = planetNode.id;
            renderer.draw(currentLayout, state, activeRendererHandlers());
            renderer.focusOn(planetNode.x, planetNode.y, 1.06);
          } else {
            state.selectedNodeId = null;
            shouldAutoFit = true;
            drawCurrentLayout();
          }
          return;
        }
      }
      state.selectedNodeId = node.id;
      showNodeSelection(node);
      emitEvent("node:selected", node, { layer: node.raw?.galaxy_layer, system: node.memorySystem });
      drawCurrentLayout({ preserveView: true });
    },
    onNodePointerOver: node => {
      state.hoveredNodeId = node.id;
      renderer.draw(currentLayout, state, activeRendererHandlers());
    },
    onNodePointerOut: () => {
      state.hoveredNodeId = null;
      renderer.draw(currentLayout, state, activeRendererHandlers());
    },
    onNodeDrag: node => {
      state.selectedNodeId = node.id;
      emitEvent("node:dragged", node, { system: node.memorySystem });
    },
    onNodeDragEnd: node => {
      state.selectedNodeId = node.id;
      emitEvent("node:drag-ended", node, { system: node.memorySystem });
      showNodeSelection(node);
    },
  });
  if (pendingFitBounds) {
    renderer.fitToBounds(pendingFitBounds);
    pendingFitBounds = null;
    shouldAutoFit = false;
  }
  syncToolbarState();
  renderBreadcrumbs();
  renderMinimap(currentLayout);
  renderSelectionFromState();
}

function activeRendererHandlers() {
  return {
    onSystemClick: (system, event) => {
      const result = selectGalaxySystem(state, system.key, {
        lastSystemTap,
        now: Date.now(),
        forceEnter: clickCount(event) >= 2,
      });
      lastSystemTap = result.lastSystemTap;
      state.selectedNodeId = result.entered ? null : `system:${system.key}`;
      showSystemSelection(system.key);
      emitEvent("system:selected", null, { system: system.key });
      shouldAutoFit = clickCount(event) >= 2;
      drawCurrentLayout({ preserveView: clickCount(event) < 2 });
      if (clickCount(event) < 2) renderer.focusOn(system.x, system.y, 1.04);
    },
    onSystemHover: () => {},
    onCometTap: comet => {
      showCometSelection(comet);
      document.getElementById("agentPrompt").textContent = `Comet ${comet.label} influences ${comet.influences.map(item => item.system).join(", ")}`;
    },
    onNodePointerDown: node => {
      if (state.view === "solar" || state.view === "planet") return;
      state.selectedNodeId = node.id;
      showNodeSelection(node);
      emitEvent("node:selected", node, { layer: node.raw?.galaxy_layer, system: node.memorySystem });
    },
    onNodeTap: (node, event) => handleNodeTap(node, event),
    onNodePointerOver: node => {
      state.hoveredNodeId = node.id;
      renderer.draw(currentLayout, state, activeRendererHandlers());
    },
    onNodePointerOut: () => {
      state.hoveredNodeId = null;
      renderer.draw(currentLayout, state, activeRendererHandlers());
    },
    onNodeDrag: node => {
      state.selectedNodeId = node.id;
      emitEvent("node:dragged", node, { system: node.memorySystem });
    },
    onNodeDragEnd: node => {
      state.selectedNodeId = node.id;
      emitEvent("node:drag-ended", node, { system: node.memorySystem });
      showNodeSelection(node);
    },
  };
}

function handleNodeTap(node, event) {
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
      state.selectedNodeId = result.entered ? null : node.id;
      if (result.entered) showSystemSelection(system.key);
      else showNodeSelection(node);
      emitEvent("system:selected", null, { system: system.key });
      shouldAutoFit = clickCount(event) >= 2;
      drawCurrentLayout({ preserveView: clickCount(event) < 2 });
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
      showNodeSelection(planetNode);
      emitEvent("node:selected", planetNode, { layer: planetNode.raw?.galaxy_layer, system: planetNode.memorySystem });
      if (clickCount(event) < 2) {
        state.selectedNodeId = planetNode.id;
        renderer.draw(currentLayout, state, activeRendererHandlers());
        renderer.focusOn(planetNode.x, planetNode.y, 1.06);
      } else {
        state.selectedNodeId = null;
        shouldAutoFit = true;
        drawCurrentLayout();
      }
      return;
    }
  }
  state.selectedNodeId = node.id;
  showNodeSelection(node);
  emitEvent("node:selected", node, { layer: node.raw?.galaxy_layer, system: node.memorySystem });
  drawCurrentLayout({ preserveView: true });
}

function transformForBounds(bounds) {
  if (!bounds || !app?.screen?.width || !app?.screen?.height) return null;
  const width = Math.max(1, bounds.width || bounds.maxX - bounds.minX);
  const height = Math.max(1, bounds.height || bounds.maxY - bounds.minY);
  const scale = Math.min(app.screen.width / (width + 120), app.screen.height / (height + 120), 1.8);
  return {
    scale,
    pan: {
      x: app.screen.width / 2 - ((bounds.minX + bounds.maxX) / 2) * scale,
      y: app.screen.height / 2 - ((bounds.minY + bounds.maxY) / 2) * scale,
    },
  };
}

function buildActiveLayout() {
  const size = { width: app.screen.width, height: app.screen.height, nodeScale: state.nodeScale || 0.48 };
  if (state.view === "solar") {
    return buildSolarSystemLayout(filteredGraph, state.selectedSystem, size);
  }
  if (state.view === "planet") {
    return buildPlanetSatelliteLayout(filteredGraph, state.selectedSystem, state.selectedPlanet, size);
  }
  const layout = buildGalaxyOverviewLayout(filteredGraph, size);
  if (!state.showComets) return { ...layout, comets: [] };
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
  }];
}

function renderTypeFilters(typeCounts) {
  const root = document.getElementById("typeFilters");
  if (!root) return;
  root.innerHTML = "";
  Object.entries(typeCounts).sort((a, b) => b[1] - a[1]).forEach(([type, count]) => {
    const label = document.createElement("label");
    label.className = "filter-card";
    label.innerHTML = `
      <span><input type="checkbox" data-type="${escapeHtml(type)}" checked> ${escapeHtml(type)}</span>
      <span>${escapeHtml(count)}</span>
    `;
    root.appendChild(label);
  });
}

function renderLayerFilters() {
  const root = document.getElementById("layerFilters");
  if (!root) return;
  root.innerHTML = "";
  for (const [layer, labelText] of [["core", "Core"], ["active", "Active"], ["knowledge", "Knowledge"], ["episode", "Episodes"], ["external", "External"]]) {
    const label = document.createElement("label");
    label.className = "filter-pill";
    label.innerHTML = `<input type="checkbox" data-layer="${escapeHtml(layer)}" checked><span>${escapeHtml(labelText)}</span>`;
    root.appendChild(label);
  }
}

function renderOrbitLegend() {
  document.getElementById("orbitLegend").innerHTML = `
    <span class="legend-item"><i class="legend-dot" style="background:#4ea1ff;box-shadow:0 0 12px #4ea1ff"></i>System</span>
    <span class="legend-item"><i class="legend-dot" style="background:#63d7d6;box-shadow:0 0 12px #63d7d6"></i>Planet</span>
    <span class="legend-item"><i class="legend-dot" style="background:#ae8cff;box-shadow:0 0 12px #ae8cff"></i>Moon</span>
    <span class="legend-item"><i class="legend-diamond" style="color:#f2c14e"></i>Evidence</span>
    <span class="legend-item"><i class="legend-square" style="color:#b5c0d4"></i>External</span>
    <span class="legend-item"><i class="legend-line" style="color:#f4f7fb"></i>Direct Relation</span>
    <span class="legend-item"><i class="legend-line legend-line-dashed" style="color:#7f8da7"></i>Indirect Relation</span>
  `;
}

function renderMinimap(layout) {
  const root = document.getElementById("minimapDots");
  const windowEl = document.getElementById("minimapWindow");
  if (!root || !layout?.bounds) return;
  const viewport = minimapViewport(layout);
  const points = minimapPoints(layout);
  root.innerHTML = points.map(system => {
    const point = worldToMinimapPercent(system.x, system.y, layout);
    return `<span class="minimap-dot" style="left:${point.x.toFixed(2)}%;top:${point.y.toFixed(2)}%;background:${escapeHtml(system.color || viewerSystemColor(system.key || system.memorySystem))};color:${escapeHtml(system.color || viewerSystemColor(system.key || system.memorySystem))}"></span>`;
  }).join("");
  if (windowEl && viewport) {
    windowEl.style.left = `${viewport.left.toFixed(2)}%`;
    windowEl.style.top = `${viewport.top.toFixed(2)}%`;
    windowEl.style.width = `${viewport.width.toFixed(2)}%`;
    windowEl.style.height = `${viewport.height.toFixed(2)}%`;
  }
}

function bindMinimapControls() {
  const minimap = document.querySelector(".galaxy-minimap");
  if (!minimap) return;
  const navigate = event => {
    if (!currentLayout?.bounds || !renderer?.centerOn) return;
    const world = minimapEventToWorld(event, currentLayout);
    if (!world) return;
    renderer.centerOn(world.x, world.y);
    renderMinimap(currentLayout);
  };
  minimap.addEventListener("pointerdown", event => {
    minimapDragActive = true;
    minimap.setPointerCapture?.(event.pointerId);
    navigate(event);
  });
  minimap.addEventListener("pointermove", event => {
    if (!minimapDragActive) return;
    navigate(event);
  });
  minimap.addEventListener("pointerup", event => {
    minimapDragActive = false;
    minimap.releasePointerCapture?.(event.pointerId);
  });
  minimap.addEventListener("pointercancel", () => {
    minimapDragActive = false;
  });
}

function minimapPoints(layout) {
  if (layout.view === "galaxy") return (layout.systems || []).filter(system => system.key !== "router");
  const ranked = [...(layout.nodes || [])]
    .filter(node => node.orbitalRole !== "satellite" || Number(node.raw?.importance || 0) >= 0.5 || Number(node.raw?.mention_count || 0) >= 3)
    .sort((a, b) => scoreVisibleNode(b) - scoreVisibleNode(a))
    .slice(0, 80);
  return ranked.map(node => ({
    x: node.x,
    y: node.y,
    key: node.memorySystem,
    memorySystem: node.memorySystem,
    color: node.color || viewerSystemColor(node.memorySystem),
  }));
}

function minimapEventToWorld(event, layout) {
  const minimap = document.querySelector(".galaxy-minimap");
  if (!minimap || !layout?.bounds) return null;
  const rect = minimap.getBoundingClientRect();
  const xPercent = Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width));
  const yPercent = Math.max(0, Math.min(1, (event.clientY - rect.top) / rect.height));
  const bounds = paddedMinimapBounds(layout.bounds);
  return {
    x: bounds.minX + xPercent * bounds.width,
    y: bounds.minY + yPercent * bounds.height,
  };
}

function worldToMinimapPercent(x, y, layout) {
  const bounds = paddedMinimapBounds(layout.bounds);
  return {
    x: ((x - bounds.minX) / bounds.width) * 100,
    y: ((y - bounds.minY) / bounds.height) * 100,
  };
}

function minimapViewport(layout) {
  const transform = renderer?.getTransform?.();
  if (!transform || !app?.screen?.width || !layout?.bounds) return null;
  const bounds = paddedMinimapBounds(layout.bounds);
  const view = {
    minX: (0 - transform.pan.x) / transform.scale,
    minY: (0 - transform.pan.y) / transform.scale,
    maxX: (app.screen.width - transform.pan.x) / transform.scale,
    maxY: (app.screen.height - transform.pan.y) / transform.scale,
  };
  const left = clampPercent(((view.minX - bounds.minX) / bounds.width) * 100);
  const top = clampPercent(((view.minY - bounds.minY) / bounds.height) * 100);
  const right = clampPercent(((view.maxX - bounds.minX) / bounds.width) * 100);
  const bottom = clampPercent(((view.maxY - bounds.minY) / bounds.height) * 100);
  return {
    left,
    top,
    width: Math.max(3, right - left),
    height: Math.max(3, bottom - top),
  };
}

function paddedMinimapBounds(bounds) {
  const width = Math.max(1, bounds.width || bounds.maxX - bounds.minX);
  const height = Math.max(1, bounds.height || bounds.maxY - bounds.minY);
  const padX = width * 0.08;
  const padY = height * 0.08;
  return {
    minX: bounds.minX - padX,
    minY: bounds.minY - padY,
    width: width + padX * 2,
    height: height + padY * 2,
  };
}

function clampPercent(value) {
  return Math.max(0, Math.min(100, Number(value) || 0));
}

function renderBreadcrumbs() {
  const galaxy = document.getElementById("crumbGalaxy");
  const system = document.getElementById("crumbSystem");
  galaxy.classList.toggle("chip-active", state.view === "galaxy");
  system.classList.toggle("chip-active", state.view !== "galaxy" && !!state.selectedSystem);
  system.textContent = state.selectedSystem ? systemLabel(state.selectedSystem) : "No System";
}

function syncToolbarState() {
  const badge = document.getElementById("viewBadge");
  badge.textContent = state.view === "galaxy"
    ? "Galaxy Overview"
    : state.view === "solar"
      ? systemLabel(state.selectedSystem)
      : `Planet Focus: ${selectedNodeLabel(state.selectedPlanet)}`;
}

function currentTimelineCutoff() {
  const slider = document.getElementById("timelineFilter");
  const cutoff = timelineCutoffFromPercent(originalGraph.metadata.timeline || {}, Number(slider?.value || 100));
  const label = document.getElementById("timelineValue");
  if (label) label.textContent = cutoff ? cutoff.slice(0, 10) : "All Time";
  return cutoff;
}

function renderSelectionFromState() {
  if (state.selectedNodeId?.startsWith("system:") && state.selectedSystem) {
    showSystemSelection(state.selectedSystem);
    return;
  }
  if (state.selectedNodeId) {
    const node = (currentLayout?.nodes || []).find(item => item.id === state.selectedNodeId)
      || filteredGraph.nodes.find(item => item.id === state.selectedNodeId);
    if (node) {
      showNodeSelection(node);
      return;
    }
  }
  if (state.selectedSystem) {
    showSystemSelection(state.selectedSystem);
    return;
  }
  document.getElementById("selectionCard").innerHTML = '<div class="empty-state">Select a system or node to inspect it.</div>';
  document.getElementById("relationsPanel").innerHTML = '<div class="empty-state">Relations appear here when a node is selected.</div>';
  document.getElementById("systemSummary").innerHTML = '<div class="empty-state">System counts and top members appear here.</div>';
  document.getElementById("systemDetails").innerHTML = '<div class="empty-state">System details appear here when a system is selected.</div>';
  document.getElementById("nodesPanel").innerHTML = '<div class="empty-state">Memory nodes appear here when a system or node is selected.</div>';
  updateInspectorTabs();
}

function showNodeSelection(node) {
  const raw = node.raw || node;
  const system = node.memorySystem || visibleNodeSystem(node);
  const status = raw.galaxy_layer || node.layer || "knowledge";
  document.getElementById("systemDetails").innerHTML = '<div class="empty-state">Select a system to view breakdowns and activity.</div>';
  document.getElementById("selectionCard").innerHTML = `
    <div class="selection-title-row">
      <div class="selection-title">
        <span class="selection-glow" style="color:${escapeHtml(viewerSystemColor(system))}"></span>
        <div>
          <div class="selection-name">${escapeHtml(node.label || raw.label || raw.name || raw.id)}</div>
          <div class="meta-inline">${escapeHtml(raw.type || node.type)} in ${escapeHtml(systemLabel(system))}</div>
        </div>
      </div>
      <span class="status-badge">${escapeHtml(capitalize(status))}</span>
    </div>
    ${renderMetricGrid([
      { label: "Mentions", value: raw.mention_count ?? 0 },
      { label: "Importance", value: raw.importance ?? 0 },
      { label: "Layer", value: raw.galaxy_layer || node.layer || "unknown" },
      { label: "System", value: systemLabel(system) },
    ])}
    <div class="meta-stack">
      <div>${escapeHtml(raw.content || "No node content.")}</div>
      ${copyableInline("Node ID", raw.id || node.id)}
      ${copyableInline("Last seen", raw.last_seen_at || "unknown")}
    </div>
  `;
  renderRelationsForNode(node);
  renderNodesForNode(node);
  renderSystemSummary(system);
  updateInspectorTabs();
}

function showSystemSelection(systemKey) {
  const members = filteredGraph.nodes
    .filter(node => visibleNodeSystem(node) === systemKey)
    .sort((a, b) => scoreVisibleNode(b) - scoreVisibleNode(a));
  const systemLinks = linksForNodes(new Set(members.map(node => node.id)));
  const typeBreakdown = summarizeBy(members, node => node.raw?.type || node.type || "memory");
  const layerBreakdown = summarizeBy(members, node => node.raw?.galaxy_layer || node.layer || "unknown");
  const latest = latestNodeTimestamp(members);
  document.getElementById("selectionCard").innerHTML = `
    <div class="inspector-title-row">
      <div class="inspector-title-main">
        <span class="selection-glow" style="color:${escapeHtml(viewerSystemColor(systemKey))}"></span>
        <div>
          <div class="selection-name">${escapeHtml(systemLabel(systemKey))}</div>
          <div class="meta-inline">${escapeHtml(formatSystemMix(typeBreakdown, "types"))}</div>
          <div class="meta-inline">Latest memory: ${escapeHtml(formatShortDate(latest))}</div>
        </div>
      </div>
    </div>
    <div class="active-row"><span class="live-dot"></span><span>${escapeHtml(formatSystemMix(layerBreakdown, "layers"))}</span></div>
    <div class="meta-stack">
      <div>${escapeHtml(systemEvidenceSummary(members, systemLinks))}</div>
    </div>
  `;
  renderRelationsForSystem(systemKey);
  renderNodesForSystem(systemKey);
  renderSystemSummary(systemKey);
  updateInspectorTabs();
}

function showCometSelection(comet) {
  document.getElementById("selectionCard").innerHTML = `
    <div class="selection-title-row">
      <div class="selection-title">
        <span class="selection-glow" style="color:#f97316"></span>
        <div>
          <div class="selection-name">${escapeHtml(comet.label)}</div>
          <div class="meta-inline">Context overlay</div>
        </div>
      </div>
      <span class="status-badge">Overlay</span>
    </div>
    <div class="meta-stack">
      <div>${escapeHtml(comet.cometType || "active_task")}</div>
      <div>${escapeHtml(comet.influences.map(item => `${item.system} ${Math.round(item.weight * 100)}%`).join(", "))}</div>
    </div>
  `;
  document.getElementById("relationsPanel").innerHTML = '<div class="empty-state">Comet overlays summarize active context rather than graph edges.</div>';
  document.getElementById("nodesPanel").innerHTML = '<div class="empty-state">Comet overlays do not map to individual memory nodes.</div>';
  updateInspectorTabs();
}

function updateInspectorTabs() {
  for (const button of document.querySelectorAll(".inspector-tabs button[data-tab]")) {
    button.classList.toggle("is-active", button.dataset.tab === activeInspectorTab);
  }
  for (const panel of document.querySelectorAll(".inspector-tab-panel[data-panel]")) {
    panel.hidden = panel.dataset.panel !== activeInspectorTab;
  }
}

function renderNodesForSystem(systemKey) {
  const members = filteredGraph.nodes
    .filter(node => visibleNodeSystem(node) === systemKey)
    .sort((a, b) => scoreVisibleNode(b) - scoreVisibleNode(a));
  document.getElementById("nodesPanel").innerHTML = renderNodeList(
    members,
    `${systemLabel(systemKey)} Nodes`,
    `${formatCompactNumber(members.length)} visible memories from the current graph scope.`,
  );
}

function renderNodesForNode(node) {
  const neighborRelations = Object.values(groupNeighborRelations(filteredGraph, node.id)).flat();
  const nodeById = new Map(filteredGraph.nodes.map(item => [item.id, item]));
  const nodes = [
    nodeById.get(node.id) || node.raw || node,
    ...neighborRelations
      .map(item => nodeById.get(item.neighbor.id))
      .filter(Boolean)
      .sort((a, b) => scoreVisibleNode(b) - scoreVisibleNode(a)),
  ];
  document.getElementById("nodesPanel").innerHTML = renderNodeList(
    dedupeById(nodes),
    "Selected Node Neighborhood",
    `${formatCompactNumber(Math.max(0, nodes.length - 1))} linked visible memories from the current graph scope.`,
  );
}

function renderNodeList(nodes, title, subtitle) {
  const visibleNodes = nodes.slice(0, 36);
  return `
    <div class="inspector-list-head">
      <span>${escapeHtml(title)}</span>
      <strong>${escapeHtml(subtitle)}</strong>
    </div>
    ${visibleNodes.length ? visibleNodes.map(renderNodeListItem).join("") : '<div class="empty-state">No visible memory nodes in the current scope.</div>'}
  `;
}

function renderNodeListItem(node) {
  const raw = node.raw || node;
  const system = visibleNodeSystem(node);
  const title = node.label || raw.label || raw.name || raw.id || node.id;
  const content = raw.content || raw.summary || "";
  return `
    <article class="memory-node-item">
      <div class="memory-node-title">
        <span class="breakdown-dot" style="background:${escapeHtml(viewerSystemColor(system))}"></span>
        <strong>${escapeHtml(title)}</strong>
      </div>
      <div class="meta">${escapeHtml(raw.type || node.type || "memory")} · ${escapeHtml(systemLabel(system))} · ${escapeHtml(raw.galaxy_layer || node.layer || "unknown")}</div>
      <div class="node-facts">
        <span>importance ${escapeHtml(raw.importance ?? 0)}</span>
        <span>mentions ${escapeHtml(raw.mention_count ?? 0)}</span>
        <span>updated ${escapeHtml(formatShortDate(raw.last_seen_at || raw.updated_at || "unknown"))}</span>
      </div>
      ${content ? `<p>${escapeHtml(truncateText(content, 180))}</p>` : ""}
      ${copyableInline("Node ID", raw.id || node.id)}
    </article>
  `;
}

function renderRelationsForNode(node) {
  const groups = groupNeighborRelations(filteredGraph, node.id);
  const relationTypes = Object.entries(groups).sort((a, b) => b[1].length - a[1].length);
  document.getElementById("relationsPanel").innerHTML = relationTypes.length
    ? relationTypes.map(([relation, items]) => `
      <div class="relation-group">
        <div class="relation-group-title">${escapeHtml(relation)} (${items.length})</div>
        ${items.slice(0, 12).map(item => renderConnectionItem(item.link, node, item.neighbor, relation)).join("")}
      </div>
    `).join("")
    : formatNodeDetails(node.raw || node);
}

function renderRelationsForSystem(systemKey) {
  const groups = groupSystemRelations(systemKey);
  const entries = Object.entries(groups).sort((a, b) => b[1].items.length - a[1].items.length);
  document.getElementById("relationsPanel").innerHTML = entries.length
    ? entries.map(([relation, group]) => `
      <div class="relation-group">
        <div class="relation-group-title">${escapeHtml(relation)} (${group.items.length})</div>
        ${group.items.slice(0, 12).map(item => `
          <div class="connection-item">
            <div class="connection-line">
              <strong>${escapeHtml(systemLabel(systemKey))}</strong>
              <span>→</span>
              <strong>${escapeHtml(systemLabel(item.system))}</strong>
            </div>
            <div class="meta">${escapeHtml(relation)} · ${escapeHtml(formatCompactNumber(item.count))} links</div>
            <div class="connection-weight">
              <div class="progress-track"><span style="--bar:${Math.min(100, item.weight * 10).toFixed(1)}%"></span></div>
              <span class="weight-value">${item.weight.toFixed(2)}</span>
            </div>
          </div>
        `).join("")}
      </div>
    `).join("")
    : '<div class="empty-state">No cross-system relations are visible in the current scope.</div>';
}

function renderConnectionItem(link, sourceNode, targetNode, relation) {
  const source = filteredGraph.nodes.find(node => node.id === String(link.source?.id || link.source)) || sourceNode;
  const target = filteredGraph.nodes.find(node => node.id === String(link.target?.id || link.target)) || targetNode;
  const sourceLabel = source.label || source.raw?.label || source.id;
  const targetLabel = target.label || target.raw?.label || target.id;
  const weight = Number(link.weight || 0);
  return `
    <div class="connection-item">
      <div class="connection-line">
        <strong>${escapeHtml(sourceLabel)}</strong>
        <span>→</span>
        <strong>${escapeHtml(targetLabel)}</strong>
      </div>
      <div class="meta">${escapeHtml(systemLabel(visibleNodeSystem(source)))} → ${escapeHtml(systemLabel(visibleNodeSystem(target)))} · ${escapeHtml(relation || link.relation || "related")}</div>
      <div class="connection-weight">
        <div class="progress-track"><span style="--bar:${Math.min(100, weight * 10).toFixed(1)}%"></span></div>
        <span class="weight-value">${weight.toFixed(2)}</span>
      </div>
    </div>
  `;
}

function renderSystemSummary(systemKey) {
  const members = filteredGraph.nodes
    .filter(node => visibleNodeSystem(node) === systemKey)
    .sort((a, b) => scoreVisibleNode(b) - scoreVisibleNode(a));
  const solarLayout = buildSolarSystemLayout(filteredGraph, systemKey, { nodeScale: state.nodeScale || 0.48 });
  const memberIds = new Set(members.map(node => node.id));
  const systemLinks = linksForNodes(memberIds);
  const avgConnections = members.length ? systemLinks.length / members.length : 0;
  const density = members.length > 1 ? systemLinks.length / (members.length * (members.length - 1)) : 0;
  const latest = latestNodeTimestamp(members);
  const datedCount = members.filter(node => node.raw?.last_seen_at).length;
  const timestampCoverage = members.length ? datedCount / members.length : 0;
  const topPlanets = solarLayout.nodes
    .filter(node => node.orbitalRole === "planet")
    .slice(0, 5)
    .map(node => ({ label: node.label, value: Number(node.raw?.importance || 0).toFixed(2) }));
  const typeBreakdown = summarizeBy(members, node => node.raw?.type || node.type || "memory").slice(0, 5);
  const relationBreakdown = Object.entries(groupSystemRelations(systemKey))
    .map(([relation, group]) => ({ label: relation, value: group.items.reduce((sum, item) => sum + item.weight, 0) }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 5);
  document.getElementById("systemSummary").innerHTML = `
    <div class="overview-metrics">
      <div class="integrity-gauge" style="--value:${timestampCoverage.toFixed(3)}">
        <div><strong>${formatPercent(timestampCoverage * 100)}</strong><span>Dated</span></div>
      </div>
      <div class="metric-stack">
        <div class="hud-row"><span>Total Nodes</span><strong>${escapeHtml(formatCompactNumber(members.length))}</strong></div>
        <div class="hud-row"><span>Total Connections</span><strong>${escapeHtml(formatCompactNumber(systemLinks.length))}</strong></div>
        <div class="hud-row"><span>Avg. Connections</span><strong>${avgConnections.toFixed(2)}</strong></div>
        <div class="hud-row"><span>Density</span><strong>${density.toFixed(4)}</strong></div>
        <div class="hud-row"><span>Last Updated</span><strong>${escapeHtml(formatShortDate(latest))}</strong></div>
      </div>
    </div>
  `;
  document.getElementById("systemDetails").innerHTML = `
    ${renderBreakdownSection("NODE TYPE BREAKDOWN", typeBreakdown, members.length)}
    ${renderBreakdownSection("TOP CONNECTIONS", relationBreakdown, Math.max(1, relationBreakdown.reduce((sum, item) => sum + item.value, 0)))}
    <div class="breakdown-section">
      <div class="breakdown-head"><span>TOP PLANETS</span></div>
      ${renderInspectorList(topPlanets)}
    </div>
    ${renderActivityList(members)}
  `;
}

function linksForNodes(nodeIds) {
  return filteredGraph.links.filter(link =>
    nodeIds.has(String(link.source.id || link.source)) || nodeIds.has(String(link.target.id || link.target))
  );
}

function groupSystemRelations(systemKey) {
  const memberIds = new Set(filteredGraph.nodes.filter(node => visibleNodeSystem(node) === systemKey).map(node => node.id));
  const grouped = {};
  for (const link of filteredGraph.links) {
    const sourceId = String(link.source.id || link.source);
    const targetId = String(link.target.id || link.target);
    const sourceIn = memberIds.has(sourceId);
    const targetIn = memberIds.has(targetId);
    if (sourceIn === targetIn) continue;
    const neighborId = sourceIn ? targetId : sourceId;
    const neighbor = filteredGraph.nodes.find(node => node.id === neighborId);
    if (!neighbor) continue;
    const relation = link.relation || "related";
    const neighborSystem = visibleNodeSystem(neighbor);
    if (!grouped[relation]) grouped[relation] = { items: [], bySystem: new Map() };
    const current = grouped[relation].bySystem.get(neighborSystem) || { weight: 0, count: 0 };
    grouped[relation].bySystem.set(neighborSystem, {
      weight: current.weight + Number(link.weight || 0),
      count: current.count + 1,
    });
  }
  for (const relation of Object.keys(grouped)) {
    grouped[relation].items = [...grouped[relation].bySystem.entries()]
      .map(([system, value]) => ({ system, weight: value.weight, count: value.count }))
      .sort((a, b) => b.weight - a.weight);
  }
  return grouped;
}

function dedupeById(nodes) {
  const seen = new Set();
  return nodes.filter(node => {
    const id = node?.id || node?.raw?.id;
    if (!id || seen.has(id)) return false;
    seen.add(id);
    return true;
  });
}

function truncateText(value, maxLength) {
  const text = String(value || "").replace(/\s+/g, " ").trim();
  return text.length > maxLength ? `${text.slice(0, maxLength - 1)}...` : text;
}

function summarizeBy(items, getKey) {
  const counts = new Map();
  for (const item of items) {
    const key = String(getKey(item) || "Other");
    counts.set(key, (counts.get(key) || 0) + 1);
  }
  return [...counts.entries()]
    .map(([label, value]) => ({ label, value }))
    .sort((a, b) => b.value - a.value);
}

function renderBreakdownSection(title, items, total) {
  const palette = ["#4ea1ff", "#b36cff", "#f7c65a", "#55dce0", "#b6c2d7"];
  return `
    <div class="breakdown-section">
      <div class="breakdown-head"><span>${escapeHtml(title)}</span></div>
      ${items.length ? items.map((item, index) => {
        const percent = total ? (Number(item.value || 0) / total) * 100 : 0;
        const color = palette[index % palette.length];
        return `
          <div class="breakdown-row">
            <span class="breakdown-dot" style="background:${color}"></span>
            <span>${escapeHtml(item.label)}</span>
            <div class="progress-track"><span style="--bar:${Math.min(100, percent).toFixed(1)}%;background:${color}"></span></div>
            <strong>${escapeHtml(formatCompactNumber(item.value))}</strong>
          </div>
        `;
      }).join("") : '<div class="empty-state">No visible items in this scope.</div>'}
    </div>
  `;
}

function renderActivityList(members) {
  const recent = [...members]
    .filter(node => node.raw?.last_seen_at)
    .sort((a, b) => String(b.raw.last_seen_at).localeCompare(String(a.raw.last_seen_at)))
    .slice(0, 5);
  return `
    <div class="activity-list">
      <div class="breakdown-head"><span>RECENT ACTIVITY</span></div>
      ${recent.length ? recent.map(node => `
        <div class="activity-item">
          <span>${escapeHtml(node.label)}</span>
          <strong>${escapeHtml(formatShortDate(node.raw.last_seen_at))}</strong>
        </div>
      `).join("") : '<div class="empty-state">No timestamps in this scope.</div>'}
    </div>
  `;
}

function formatShortDate(value) {
  if (!value || value === "unknown") return "unknown";
  return String(value).slice(0, 10);
}

function latestNodeTimestamp(nodes) {
  return nodes.map(node => node.raw?.last_seen_at).filter(Boolean).sort().at(-1) || "unknown";
}

function summarizeOrbitRoles(nodes) {
  return nodes.reduce((acc, node) => {
    const role = orbitRoleForNode(node);
    acc[role] = (acc[role] || 0) + 1;
    acc.external = acc.external || 0;
    if (node.layer === "external" || visibleNodeSystem(node) === "source") acc.external += 1;
    return acc;
  }, { planet: 0, moon: 0, evidence: 0, external: 0 });
}

function summarizeSystemStructure(systemKey) {
  const layout = buildSolarSystemLayout(filteredGraph, systemKey, { nodeScale: state.nodeScale || 0.48 });
  return layout.nodes.reduce((acc, node) => {
    if (node.orbitalRole === "planet") acc.planet += 1;
    else if (node.orbitalRole === "satellite") acc.moon += 1;
    return acc;
  }, { planet: 0, moon: 0, evidence: 0, external: 0 });
}

function orbitRoleForNode(node) {
  if (node.orbitRole) return node.orbitRole;
  if (node.layer === "external" || node.layer === "episode" || visibleNodeSystem(node) === "source") return "evidence";
  if (Number(node.raw?.importance || 0) >= 0.9 || Number(node.raw?.mention_count || 0) >= 10) return "planet";
  return "moon";
}

function formatSystemMix(items, fallbackLabel) {
  if (!items.length) return `0 ${fallbackLabel}`;
  return items
    .slice(0, 3)
    .map(item => `${item.label} ${formatCompactNumber(item.value)}`)
    .join(" / ");
}

function systemEvidenceSummary(members, links) {
  const top = members.find(node => node.raw?.content || node.label);
  const content = top?.raw?.content || top?.label || "No memory content is visible in this filtered scope.";
  return `${formatCompactNumber(members.length)} memories and ${formatCompactNumber(links.length)} visible links. Top memory: ${truncateText(content, 150)}`;
}

function systemLabel(systemKey) {
  return `${capitalize(systemKey)} System`;
}

function viewerSystemColor(systemKey) {
  return systemColors[systemKey] || "#4ea1ff";
}

function selectedNodeLabel(nodeId) {
  const node = filteredGraph.nodes.find(item => item.id === nodeId) || currentLayout?.nodes?.find(item => item.id === nodeId);
  return node?.label || nodeId || "Node";
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
    state.selectedNodeId = null;
    shouldAutoFit = true;
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
    showNodeSelection(planetNode);
    state.selectedNodeId = null;
    shouldAutoFit = true;
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

function renderStats(metadata) {
  const stats = document.getElementById("stats");
  const totalNodes = Number(metadata.total_node_count ?? metadata.node_count ?? 0);
  const totalEdges = Number(metadata.total_edge_count ?? metadata.edge_count ?? 0);
  const filteredNodes = Number(metadata.node_count ?? totalNodes);
  const filteredEdges = Number(metadata.edge_count ?? totalEdges);
  const visibleNodes = Number(metadata.visible_node_count ?? filteredNodes);
  const visibleEdges = Number(metadata.visible_edge_count ?? filteredEdges);
  const visibleSuffix = visibleNodes !== filteredNodes || visibleEdges !== filteredEdges
    ? ` (${visibleNodes}/${visibleEdges} shown)`
    : "";
  if (stats) stats.textContent = `${filteredNodes}/${totalNodes} nodes / ${filteredEdges}/${totalEdges} edges${visibleSuffix}`;
  const liveRows = document.getElementById("liveHudRows");
  if (liveRows) {
    liveRows.innerHTML = [
      ["Systems", countVisibleSystems()],
      ["Nodes", visibleNodes],
      ["Connections", visibleEdges],
      ["Inferred Links", filteredEdges],
    ].map(([label, value]) => `
      <div class="hud-row"><span>${escapeHtml(label)}</span><strong>${escapeHtml(formatCompactNumber(value))}</strong></div>
    `).join("");
  }
  const perfNodes = document.getElementById("perfNodes");
  const perfEdges = document.getElementById("perfEdges");
  if (perfNodes) perfNodes.textContent = formatCompactNumber(visibleNodes);
  if (perfEdges) perfEdges.textContent = formatCompactNumber(visibleEdges);
}

function initPerformancePanel() {
  const sparkline = document.getElementById("perfSparkline");
  if (sparkline && !perfState.bars.length) {
    const fragment = document.createDocumentFragment();
    for (let index = 0; index < PERF_SAMPLE_LIMIT; index += 1) {
      const bar = document.createElement("span");
      bar.style.setProperty("--h", "8%");
      fragment.appendChild(bar);
      perfState.bars.push(bar);
    }
    sparkline.appendChild(fragment);
  }
  perfState.gpuRenderer = readGpuRenderer();
  const gpuRenderer = document.getElementById("perfGpuRenderer");
  if (gpuRenderer) gpuRenderer.textContent = perfState.gpuRenderer;
}

function recordPerformanceFrame(deltaMS) {
  const now = performance.now();
  const frameTime = Number.isFinite(deltaMS) && deltaMS > 0 ? deltaMS : 16.67;
  perfState.frames += 1;
  perfState.frameTimeTotal += frameTime;
  if (now - perfState.lastSampleAt < PERF_SAMPLE_INTERVAL_MS) return;

  const elapsedSeconds = Math.max((now - perfState.lastSampleAt) / 1000, 0.001);
  const avgFrameTime = perfState.frames ? perfState.frameTimeTotal / perfState.frames : frameTime;
  const fps = Math.round(perfState.frames / elapsedSeconds);
  const cpuLoad = Math.max(0, Math.min(100, (avgFrameTime / 16.67) * 100));
  const gpuEstimate = estimateGpuMemoryMB();
  refreshBackendPerformance();
  const backendPerf = recentBackendPerformance();
  perfState.lastStats = {
    fps,
    frameTime: avgFrameTime,
    cpuLoad: backendPerf?.cpu_percent ?? cpuLoad,
    memory: formatSystemMemory(backendPerf) || formatBrowserMemory(),
    gpuEstimate: backendPerf?.gpu?.memory_used_mb ?? gpuEstimate,
  };
  perfState.samples[perfState.sampleIndex] = Math.max(0, Math.min(100, fps));
  perfState.sampleIndex = (perfState.sampleIndex + 1) % PERF_SAMPLE_LIMIT;
  perfState.sampleCount = Math.min(PERF_SAMPLE_LIMIT, perfState.sampleCount + 1);
  renderPerformancePanel();
  perfState.frames = 0;
  perfState.frameTimeTotal = 0;
  perfState.lastSampleAt = now;
}

function renderPerformancePanel() {
  setText("perfFps", String(perfState.lastStats.fps));
  setText("perfFrameTime", `${perfState.lastStats.frameTime.toFixed(1)} ms`);
  setText("perfCpu", `${perfState.lastStats.cpuLoad.toFixed(1)}%`);
  setText("perfMemory", perfState.lastStats.memory);
  const backendGpu = recentBackendPerformance()?.gpu;
  const gpuText = backendGpu?.memory_total_mb
    ? `${Number(backendGpu.memory_used_mb || 0).toFixed(0)} / ${Number(backendGpu.memory_total_mb).toFixed(0)} MB`
    : `~${perfState.lastStats.gpuEstimate.toFixed(1)} MB`;
  setText("perfGpu", gpuText);
  renderPerformanceSparkline();
}

function refreshBackendPerformance() {
  if (perfState.backendUnavailable) return;
  fetch("/api/system/performance", { cache: "no-store" })
    .then(response => response.ok ? response.json() : null)
    .then(payload => {
      if (!payload?.source) {
        perfState.backendUnavailable = true;
        return;
      }
      perfState.backendPerformance = payload;
      perfState.backendPerformanceAt = performance.now();
    })
    .catch(() => {
      perfState.backendUnavailable = true;
    });
}

function recentBackendPerformance() {
  if (!perfState.backendPerformance) return null;
  if (performance.now() - perfState.backendPerformanceAt > PERF_SAMPLE_INTERVAL_MS * 2.5) return null;
  return perfState.backendPerformance;
}

function formatSystemMemory(backendPerf) {
  const memory = backendPerf?.memory;
  if (!memory?.used_mb || !memory?.total_mb) return "";
  return `${Number(memory.used_mb).toFixed(0)} MB / ${Number(memory.total_mb).toFixed(0)} MB`;
}

function renderPerformanceSparkline() {
  if (!perfState.bars.length) return;
  const maxValue = Math.max(60, ...perfState.samples);
  for (let index = 0; index < PERF_SAMPLE_LIMIT; index += 1) {
    const sampleOffset = (perfState.sampleIndex + index) % PERF_SAMPLE_LIMIT;
    const value = perfState.sampleCount < PERF_SAMPLE_LIMIT && index < PERF_SAMPLE_LIMIT - perfState.sampleCount
      ? 0
      : perfState.samples[sampleOffset];
    const height = Math.max(8, Math.round((value / maxValue) * 100));
    perfState.bars[index].style.setProperty("--h", `${height}%`);
  }
}

function readGpuRenderer() {
  const canvas = app?.canvas;
  let gl = null;
  try {
    gl = canvas?.getContext("webgl2") || canvas?.getContext("webgl");
  } catch {
    return "WebGL";
  }
  if (!gl) return "WebGL";
  const debugInfo = gl.getExtension("WEBGL_debug_renderer_info");
  const rendererName = debugInfo
    ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL)
    : gl.getParameter(gl.RENDERER);
  return String(rendererName || "WebGL").replace(/\s+/g, " ").trim();
}

function formatBrowserMemory() {
  const memory = performance.memory;
  if (!memory?.usedJSHeapSize) return "N/A";
  const used = memory.usedJSHeapSize / 1048576;
  if (!memory.jsHeapSizeLimit) return `${used.toFixed(1)} MB`;
  const limit = memory.jsHeapSizeLimit / 1048576;
  return `${used.toFixed(1)} MB / ${limit.toFixed(0)} MB`;
}

function estimateGpuMemoryMB() {
  const nodes = Number(currentLayout?.nodes?.length || 0);
  const links = Number(currentLayout?.links?.length || 0);
  const canvas = app?.canvas;
  const canvasPixels = Number(canvas?.width || 0) * Number(canvas?.height || 0);
  const framebufferBytes = canvasPixels * 4;
  const graphBytes = nodes * 384 + links * 128;
  return Math.max(0.1, (framebufferBytes + graphBytes) / 1048576);
}

function setText(id, value) {
  const element = document.getElementById(id);
  if (element) element.textContent = value;
}

function formatCompactNumber(value) {
  const number = Number(value || 0);
  if (number >= 1000000) return `${(number / 1000000).toFixed(1)}M`;
  if (number >= 1000) return `${(number / 1000).toFixed(number >= 10000 ? 0 : 1)}K`;
  return String(number);
}

function formatPercent(value) {
  return `${Math.max(0, Math.min(100, Number(value || 0))).toFixed(1)}%`;
}

function countVisibleSystems() {
  return new Set(filteredGraph.nodes.map(node => visibleNodeSystem(node)).filter(Boolean)).size;
}

function capitalize(value) {
  const text = String(value || "");
  return text ? text.charAt(0).toUpperCase() + text.slice(1) : "";
}

init().catch(error => {
  document.getElementById("stats").textContent = "Failed to load galaxy.";
  document.getElementById("selectionCard").textContent = String(error);
});

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
  renderer.draw(currentLayout, state, {
    onSystemClick: (system, event) => {
      const result = selectGalaxySystem(state, system.key, {
        lastSystemTap,
        now: Date.now(),
        forceEnter: clickCount(event) >= 2,
      });
      lastSystemTap = result.lastSystemTap;
      state.selectedNodeId = `system:${system.key}`;
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
          state.selectedNodeId = node.id;
          showNodeSelection(node);
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
          state.selectedNodeId = planetNode.id;
          showNodeSelection(planetNode);
          emitEvent("node:selected", planetNode, { layer: planetNode.raw?.galaxy_layer, system: planetNode.memorySystem });
          shouldAutoFit = clickCount(event) >= 2;
          drawCurrentLayout({ preserveView: clickCount(event) < 2 });
          if (clickCount(event) < 2) renderer.focusOn(planetNode.x, planetNode.y, 1.06);
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
      drawCurrentLayout({ preserveView: true });
    },
    onNodePointerOut: () => {
      state.hoveredNodeId = null;
      drawCurrentLayout({ preserveView: true });
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
  if (shouldAutoFit && !options.preserveView) {
    renderer.fitToBounds(currentLayout.bounds);
    shouldAutoFit = false;
  }
  syncToolbarState();
  renderBreadcrumbs();
  renderMinimap(currentLayout);
  renderSelectionFromState();
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
  if (!root || !layout?.bounds) return;
  const bounds = layout.bounds;
  const width = Math.max(1, bounds.width);
  const height = Math.max(1, bounds.height);
  const points = (layout.systems || []).filter(system => system.key !== "router");
  root.innerHTML = points.map(system => {
    const x = ((system.x - bounds.minX) / width) * 100;
    const y = ((system.y - bounds.minY) / height) * 100;
    return `<span class="minimap-dot" style="left:${x.toFixed(2)}%;top:${y.toFixed(2)}%;background:${escapeHtml(system.color || systemColor(system.key))};color:${escapeHtml(system.color || systemColor(system.key))}"></span>`;
  }).join("");
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
}

function showNodeSelection(node) {
  const raw = node.raw || node;
  const system = node.memorySystem || visibleNodeSystem(node);
  const status = raw.galaxy_layer || node.layer || "knowledge";
  document.getElementById("selectionCard").innerHTML = `
    <div class="selection-title-row">
      <div class="selection-title">
        <span class="selection-glow" style="color:${escapeHtml(systemColor(system))}"></span>
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
  renderSystemSummary(system);
}

function showSystemSelection(systemKey) {
  const members = filteredGraph.nodes.filter(node => visibleNodeSystem(node) === systemKey);
  const lead = members.sort((a, b) => scoreVisibleNode(b) - scoreVisibleNode(a))[0];
  document.getElementById("selectionCard").innerHTML = `
    <div class="inspector-title-row">
      <div class="inspector-title-main">
        <span class="selection-glow" style="color:${escapeHtml(systemColor(systemKey))}"></span>
        <div>
          <div class="selection-name">${escapeHtml(systemLabel(systemKey))}</div>
          <div class="meta-inline">${escapeHtml(systemLayerLabel(systemKey))}</div>
          <div class="meta-inline">System ID: ${escapeHtml(`sys_${systemKey}`)}</div>
        </div>
      </div>
      <button type="button" class="focus-button">Focus</button>
    </div>
    <div class="active-row"><span class="live-dot"></span><span>${escapeHtml(layerBadgeForSystem(members))}</span></div>
    <div class="meta-stack">
      <div>${escapeHtml(systemDescription(systemKey, lead))}</div>
    </div>
  `;
  renderRelationsForSystem(systemKey);
  renderSystemSummary(systemKey);
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
}

function renderRelationsForNode(node) {
  const groups = groupNeighborRelations(filteredGraph, node.id);
  const relationTypes = Object.entries(groups).sort((a, b) => b[1].length - a[1].length);
  document.getElementById("relationsPanel").innerHTML = relationTypes.length
    ? relationTypes.map(([relation, items]) => `
      <div class="relation-group">
        <div class="relation-group-title">${escapeHtml(relation)} (${items.length})</div>
        ${items.slice(0, 3).map(item => `
          <div class="relation-item">
            <strong>${escapeHtml(item.neighbor.label)}</strong>
            <div class="progress-track"><span style="--bar:${Math.min(100, Number(item.link.weight || 0) * 10).toFixed(1)}%"></span></div>
            <span class="weight-value">${Number(item.link.weight || 0).toFixed(2)}</span>
          </div>
        `).join("")}
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
        ${group.items.slice(0, 3).map(item => `
          <div class="relation-item">
            <strong>${escapeHtml(systemLabel(item.system))}</strong>
            <div class="progress-track"><span style="--bar:${Math.min(100, item.weight * 10).toFixed(1)}%"></span></div>
            <span class="weight-value">${item.weight.toFixed(2)}</span>
          </div>
        `).join("")}
      </div>
    `).join("")
    : '<div class="empty-state">No cross-system relations are visible in the current scope.</div>';
}

function renderSystemSummary(systemKey) {
  const members = filteredGraph.nodes
    .filter(node => visibleNodeSystem(node) === systemKey)
    .sort((a, b) => scoreVisibleNode(b) - scoreVisibleNode(a));
  const solarLayout = buildSolarSystemLayout(filteredGraph, systemKey, { nodeScale: state.nodeScale || 0.48 });
  const memberIds = new Set(members.map(node => node.id));
  const systemLinks = filteredGraph.links.filter(link =>
    memberIds.has(String(link.source.id || link.source)) || memberIds.has(String(link.target.id || link.target))
  );
  const avgConnections = members.length ? systemLinks.length / members.length : 0;
  const density = members.length > 1 ? systemLinks.length / (members.length * (members.length - 1)) : 0;
  const latest = members.map(node => node.raw?.last_seen_at).filter(Boolean).sort().at(-1) || "unknown";
  const integrity = members.length ? Math.min(0.987, 0.72 + Math.log1p(systemLinks.length) / 16) : 0;
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
      <div class="integrity-gauge" style="--value:${integrity.toFixed(3)}">
        <div><strong>${formatPercent(integrity * 100)}</strong><span>Excellent</span></div>
      </div>
      <div class="metric-stack">
        <div class="hud-row"><span>Total Nodes</span><strong>${escapeHtml(formatCompactNumber(members.length))}</strong></div>
        <div class="hud-row"><span>Total Connections</span><strong>${escapeHtml(formatCompactNumber(systemLinks.length))}</strong></div>
        <div class="hud-row"><span>Avg. Connections</span><strong>${avgConnections.toFixed(2)}</strong></div>
        <div class="hud-row"><span>Density</span><strong>${density.toFixed(4)}</strong></div>
        <div class="hud-row"><span>Last Updated</span><strong>${escapeHtml(formatShortDate(latest))}</strong></div>
      </div>
    </div>
    ${renderBreakdownSection("NODE TYPE BREAKDOWN", typeBreakdown, members.length)}
    ${renderBreakdownSection("TOP CONNECTIONS", relationBreakdown, Math.max(1, relationBreakdown.reduce((sum, item) => sum + item.value, 0)))}
    <div class="breakdown-section">
      <div class="breakdown-head"><span>TOP PLANETS</span><a class="view-link" href="#">View All</a></div>
      ${renderInspectorList(topPlanets)}
    </div>
    ${renderActivityList(members)}
  `;
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
    const current = grouped[relation].bySystem.get(neighborSystem) || 0;
    grouped[relation].bySystem.set(neighborSystem, current + Number(link.weight || 0));
  }
  for (const relation of Object.keys(grouped)) {
    grouped[relation].items = [...grouped[relation].bySystem.entries()]
      .map(([system, weight]) => ({ system, weight }))
      .sort((a, b) => b.weight - a.weight);
  }
  return grouped;
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
      <div class="breakdown-head"><span>${escapeHtml(title)}</span><a class="view-link" href="#">View All</a></div>
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
      <a class="view-link" href="#">View All Activity</a>
    </div>
  `;
}

function formatShortDate(value) {
  if (!value || value === "unknown") return "unknown";
  return String(value).slice(0, 10);
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

function layerBadgeForSystem(nodes) {
  if (nodes.some(node => node.layer === "core")) return "Core";
  if (nodes.some(node => node.layer === "active")) return "Active";
  if (nodes.some(node => node.layer === "knowledge")) return "Knowledge";
  if (nodes.some(node => node.layer === "episode")) return "Episodes";
  return "External";
}

function systemDescription(systemKey, lead) {
  const descriptions = {
    router: "Encapsulates global routing and top-level agent coordination.",
    rule: "Captures hard constraints, policies, and durable guardrails.",
    persona: "Represents tone, identity, and behavior-shaping traits.",
    skill: "Encapsulates executable capabilities, techniques, and procedural knowledge.",
    harness: "Contains tests, evaluation harnesses, and verification workflows.",
    preference: "Tracks stable user preferences and interaction choices.",
    project: "Holds active project context and local domain memory.",
    knowledge: "Stores reusable concepts and longer-lived contextual knowledge.",
    event: "Contains episodes, sessions, and time-bound observations.",
    source: "Groups provenance, citations, and external supporting evidence.",
  };
  return descriptions[systemKey] || lead?.raw?.content || "No system description available.";
}

function systemLayerLabel(systemKey) {
  if (["rule", "persona"].includes(systemKey)) return "Control Layer";
  if (["skill", "harness", "preference"].includes(systemKey)) return "Execution Layer";
  if (["project", "knowledge"].includes(systemKey)) return "Context Layer";
  if (["event", "source"].includes(systemKey)) return "Evidence Layer";
  return "Core Layer";
}

function systemLabel(systemKey) {
  return `${capitalize(systemKey)} System`;
}

function systemColor(systemKey) {
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
    state.selectedNodeId = `system:${system.key}`;
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
    state.selectedNodeId = planetNode.id;
    showNodeSelection(planetNode);
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

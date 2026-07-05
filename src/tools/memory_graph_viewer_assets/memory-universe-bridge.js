const bundlePath = "./memory-universe-3d/memory-universe-viewer.js?v=20260705-state3-shapes-camera";
const max3DNodes = 420;
const max3DEdges = 220;
const supportedMemoryCategories = new Set([
  "rule",
  "system_constraint",
  "project",
  "skill",
  "workflow",
  "decision",
  "plan",
  "session",
  "event",
  "supporting_context",
  "context",
  "concept",
  "pattern",
  "technology",
  "domain",
  "person",
  "company",
  "event_role",
  "process",
  "setting",
  "database",
  "unknown",
]);

export function initMemoryUniverse3DCoexistence(options) {
  const twoDStage = document.getElementById("galaxy2d");
  const threeDStage = document.getElementById("memoryUniverse3d");
  const twoDButton = document.getElementById("viewMode2d");
  const threeDButton = document.getElementById("viewMode3d");
  const observatoryButton = document.getElementById("universe3dObservatory");
  const spaceshipButton = document.getElementById("universe3dSpaceship");
  const resetButton = document.getElementById("universe3dReset");

  if (!twoDStage || !threeDStage || !twoDButton || !threeDButton) {
    return createUnavailableBridge("3D bridge controls are missing.");
  }

  let activeView = "2d";
  let viewer = null;
  let viewerModule = null;
  let latestGraph = convertGalaxyToMemoryUniverseGraph(options.getGraph());
  let hoverPreview = null;
  let canvasHost = null;
  let navigationPanel = null;
  let navigationSearchInput = null;
  let navigationResults = null;
  let minimapPanel = null;
  let minimapDots = null;
  let unavailableReason = null;
  let suppressSelectionCallback = false;
  let expandedTreeTargets = new Set();
  let navigationCollapsed = false;
  let minimapAnimationFrame = null;
  let lastMinimapSignature = "";

  sync3DGraphDiagnostics();
  twoDButton.addEventListener("click", () => setActiveView("2d"));
  threeDButton.addEventListener("click", () => setActiveView("3d"));
  observatoryButton?.addEventListener("click", () => {
    viewer?.dispatchIntent({ type: "switchMode", mode: "observatory" });
  });
  spaceshipButton?.addEventListener("click", () => {
    viewer?.dispatchIntent({ type: "switchMode", mode: "spaceship" });
  });
  resetButton?.addEventListener("click", () => {
    viewer?.dispatchIntent({ type: "clearFocus" });
    viewer?.dispatchIntent({ type: "clearSelection" });
    viewer?.dispatchIntent({ type: "switchMode", mode: "observatory" });
  });

  syncViewChrome();

  return {
    updateGraph(galaxyGraph) {
      threeDStage.dataset.memoryUniverseRawNodes = String(galaxyGraph?.nodes?.length || 0);
      threeDStage.dataset.memoryUniverseRawEdges = String(galaxyGraph?.links?.length || 0);
      latestGraph = convertGalaxyToMemoryUniverseGraph(galaxyGraph);
      sync3DGraphDiagnostics();
      if (viewer) {
        viewer.updateGraph(latestGraph);
        viewer.selectNode(readSelectedNodeId(options.getSelectedNodeId()));
        if (activeView === "3d") applyCurrent2DFocusTo3D();
        renderNavigationPanel();
        lastMinimapSignature = "";
        renderProjectedMinimap();
      }
    },
    selectNode(nodeId) {
      if (!viewer) return;
      suppressSelectionCallback = true;
      try {
        viewer.selectNode(readSelectedNodeId(nodeId));
      } finally {
        suppressSelectionCallback = false;
      }
    },
    getActiveView() {
      return activeView;
    },
    getUnavailableReason() {
      return unavailableReason;
    },
  };

  async function setActiveView(view) {
    activeView = view;
    if (view === "3d") {
      const mounted = await mount3D();
      if (!mounted) {
        activeView = "2d";
      } else {
        applyCurrent2DFocusTo3D();
      }
    }
    syncViewChrome();
  }

  async function mount3D() {
    if (viewer) {
      return true;
    }
    if (!canUseWebGL()) {
      unavailableReason = "3D Universe unavailable: WebGL or GPU support is not available.";
      renderUnavailable(unavailableReason);
      return false;
    }
    try {
      viewerModule = viewerModule || await import(bundlePath);
      threeDStage.replaceChildren();
      canvasHost = document.createElement("div");
      canvasHost.className = "memory-universe-canvas-host";
      navigationPanel = createNavigationPanel();
      minimapPanel = createProjectedMinimap();
      hoverPreview = document.createElement("div");
      hoverPreview.className = "memory-universe-hover";
      hoverPreview.hidden = true;
      threeDStage.append(canvasHost, navigationPanel, minimapPanel, hoverPreview);
      viewer = viewerModule.createMemoryUniverseViewer({
        container: canvasHost,
        graph: latestGraph,
        options: {
          initialMode: "observatory",
          initialFocus: resolveCurrent2DFocusTarget() || undefined,
        },
        onSelectNode(node) {
          if (suppressSelectionCallback) return;
          options.onSelectNode?.(node?.id || null);
        },
        onStateChange(state) {
          renderHoverPreview(state.hoverSummary, state.selectedObject);
          renderNavigationPanel(state);
          renderProjectedMinimap();
          syncModeButtons(state.mode);
        },
      });
      viewer.selectNode(readSelectedNodeId(options.getSelectedNodeId()));
      renderNavigationPanel();
      renderProjectedMinimap();
      syncModeButtons(viewer.getMode?.() || "observatory");
      unavailableReason = null;
      return true;
    } catch (error) {
      unavailableReason = `3D Universe unavailable: ${error instanceof Error ? error.message : String(error)}`;
      renderUnavailable(unavailableReason);
      viewer = null;
      return false;
    }
  }

  function syncViewChrome() {
    const in3D = activeView === "3d";
    twoDStage.hidden = in3D;
    threeDStage.hidden = !in3D;
    document.body.classList.toggle("memory-universe-active", in3D);
    twoDButton.classList.toggle("is-active", !in3D);
    threeDButton.classList.toggle("is-active", in3D);
    twoDButton.setAttribute("aria-current", in3D ? "false" : "page");
    threeDButton.setAttribute("aria-current", in3D ? "page" : "false");
    if (in3D) startProjectedMinimapLoop();
    else stopProjectedMinimapLoop();
    options.onActiveViewChange?.(activeView);
  }

  function syncModeButtons(mode) {
    observatoryButton?.classList.toggle("is-active", mode === "observatory");
    spaceshipButton?.classList.toggle("is-active", mode === "spaceship");
  }

  function sync3DGraphDiagnostics() {
    threeDStage.dataset.memoryUniverseNodes = String(latestGraph.nodes.length);
    threeDStage.dataset.memoryUniverseEdges = String(latestGraph.edges.length);
    threeDStage.dataset.memoryUniverseCategories = String(new Set(latestGraph.nodes.map(node => node.category)).size);
  }

  function applyCurrent2DFocusTo3D() {
    const focusTarget = resolveCurrent2DFocusTarget();
    if (focusTarget) viewer?.setFocusTarget(focusTarget);
  }

  function resolveCurrent2DFocusTarget() {
    const focusState = options.getFocusTarget?.();
    return normalizeFocusTarget(focusState) || focusTargetFrom2DState(focusState);
  }

  function normalizeFocusTarget(value) {
    if (!value || typeof value !== "object") return null;
    if (value.type === "node" && latestGraph.nodes.some(node => node.id === value.id)) return { type: "node", id: value.id };
    if (value.type === "solarSystem" && latestGraph.hierarchy.solarSystems.some(system => system.id === value.id)) return { type: "solarSystem", id: value.id };
    if (value.type === "planetarySystem" && latestGraph.hierarchy.planetarySystems.some(system => system.id === value.id)) return { type: "planetarySystem", id: value.id };
    if (value.type === "galaxy" && latestGraph.hierarchy.galaxies.some(galaxy => galaxy.id === value.id)) return { type: "galaxy", id: value.id };
    return null;
  }

  function focusTargetFrom2DState(state) {
    const selectedNodeId = readSelectedNodeId(state?.selectedNodeId);
    if (selectedNodeId && latestGraph.nodes.some(node => node.id === selectedNodeId)) return { type: "node", id: selectedNodeId };

    const selectedPlanetId = readSelectedNodeId(state?.selectedPlanet);
    if (selectedPlanetId) {
      const node = latestGraph.nodes.find(node => node.id === selectedPlanetId);
      if (node) return { type: "node", id: node.id };
      const planetarySystem = latestGraph.hierarchy.planetarySystems.find(system => system.id === selectedPlanetId);
      if (planetarySystem) return { type: "planetarySystem", id: planetarySystem.id };
    }

    const solarSystem = resolveSolarSystemFocus(state?.selectedSystem);
    return solarSystem ? { type: "solarSystem", id: solarSystem.id } : null;
  }

  function resolveSolarSystemFocus(systemKey) {
    if (!systemKey) return null;
    const rawKey = String(systemKey);
    const parts = rawKey.split(":").filter(Boolean);
    const system = stableId(parts.at(-1) || rawKey);
    const namespace = parts.length > 1 ? stableId(parts[0]) : "";
    const expectedId = namespace ? `agent:${namespace}:system:${system}` : "";
    if (expectedId) {
      const exact = latestGraph.hierarchy.solarSystems.find(item => item.id === expectedId);
      if (exact) return exact;
    }
    return latestGraph.hierarchy.solarSystems.find(item => item.id.endsWith(`:system:${system}`)) || null;
  }

  function renderHoverPreview(summary, selected) {
    if (!hoverPreview) return;
    if (!summary || selected) {
      hoverPreview.hidden = true;
      hoverPreview.textContent = "";
      return;
    }
    hoverPreview.hidden = false;
    hoverPreview.textContent = `${summary.label} · ${formatObjectType(summary.type)}`;
  }

  function renderUnavailable(message) {
    const panel = document.createElement("div");
    panel.className = "memory-universe-unavailable";
    panel.setAttribute("role", "status");
    panel.textContent = message;
    threeDStage.replaceChildren(panel);
  }

  function createNavigationPanel() {
    const panel = document.createElement("aside");
    panel.className = "memory-universe-nav-panel";
    panel.setAttribute("aria-label", "3D Jump Panel");
    panel.innerHTML = `
      <div class="memory-universe-nav-header">
        <button type="button" class="memory-universe-nav-collapse" aria-label="Collapse 3D Navigation" aria-expanded="true">-</button>
        <div>
          <span>Jump</span>
          <strong>3D Navigation</strong>
        </div>
      </div>
      <label class="memory-universe-nav-search">
        <span>Search targets</span>
        <input type="search" autocomplete="off">
      </label>
      <div class="memory-universe-nav-results" aria-live="polite"></div>
    `;
    navigationSearchInput = panel.querySelector("input");
    navigationResults = panel.querySelector(".memory-universe-nav-results");
    navigationSearchInput?.addEventListener("input", () => renderNavigationPanel());
    panel.addEventListener("click", event => {
      const collapseButton = event.target.closest(".memory-universe-nav-collapse");
      if (collapseButton) {
        navigationCollapsed = !navigationCollapsed;
        panel.classList.toggle("is-collapsed", navigationCollapsed);
        collapseButton.textContent = navigationCollapsed ? "+" : "-";
        collapseButton.setAttribute("aria-expanded", String(!navigationCollapsed));
        collapseButton.setAttribute("aria-label", navigationCollapsed ? "Expand 3D Navigation" : "Collapse 3D Navigation");
        return;
      }

      const treeButton = event.target.closest("button[data-tree-target-type]");
      if (!treeButton) return;
      const target = readTreeTargetFromButton(treeButton);
      if (!target) return;

      const key = treeTargetKey(target);
      if (target.type !== "planetarySystem") {
        if (expandedTreeTargets.has(key)) expandedTreeTargets.delete(key);
        else expandedTreeTargets.add(key);
        renderNavigationPanel();
      }

      viewer?.dispatchIntent({ type: "focus", target });
    });
    return panel;
  }

  function createProjectedMinimap() {
    const panel = document.createElement("aside");
    panel.className = "memory-universe-minimap";
    panel.setAttribute("aria-label", "3D projected minimap");
    panel.innerHTML = `
      <div class="minimap-dots"></div>
      <div class="minimap-window" aria-hidden="true"></div>
    `;
    minimapDots = panel.querySelector(".minimap-dots");
    return panel;
  }

  function startProjectedMinimapLoop() {
    if (minimapAnimationFrame !== null) return;
    const tick = () => {
      minimapAnimationFrame = null;
      renderProjectedMinimap();
      if (activeView === "3d") {
        minimapAnimationFrame = requestAnimationFrame(tick);
      }
    };
    minimapAnimationFrame = requestAnimationFrame(tick);
  }

  function stopProjectedMinimapLoop() {
    if (minimapAnimationFrame === null) return;
    cancelAnimationFrame(minimapAnimationFrame);
    minimapAnimationFrame = null;
  }

  function renderProjectedMinimap(force = false) {
    if (!viewer || !minimapDots) return;
    const layout = viewer.getLayout?.();
    const camera = viewer.getCameraSnapshot?.();
    if (!layout?.nodes?.size || !camera?.position) return;
    const bounds = projectedLayoutBounds(layout);
    if (!bounds) return;
    const signature = [
      latestGraph.nodes.length,
      roundForSignature(camera.position.x),
      roundForSignature(camera.position.z),
      roundForSignature(camera.rotation.x),
      roundForSignature(camera.rotation.y),
    ].join(":");
    if (!force && signature === lastMinimapSignature) return;
    lastMinimapSignature = signature;

    const nodeById = new Map(latestGraph.nodes.map(node => [node.id, node]));
    const nodeDots = [...layout.nodes.entries()].slice(0, 180).map(([id, item]) => {
      const node = nodeById.get(id);
      const point = projectToMinimap(item.position.x, item.position.z, bounds);
      const color = minimapColorForCategory(node?.category);
      return `<span class="minimap-dot" style="left:${point.x.toFixed(2)}%;top:${point.y.toFixed(2)}%;background:${color};color:${color}"></span>`;
    });
    const cameraPoint = projectToMinimap(camera.position.x, camera.position.z, bounds);
    nodeDots.push(
      `<span class="memory-universe-minimap-camera" style="left:${cameraPoint.x.toFixed(2)}%;top:${cameraPoint.y.toFixed(2)}%"></span>`,
    );
    minimapDots.innerHTML = nodeDots.join("");
  }

  function projectedLayoutBounds(layout) {
    const points = [...layout.nodes.values()].map(item => item.position);
    const camera = viewer?.getCameraSnapshot?.()?.position;
    if (camera) points.push(camera);
    if (!points.length) return null;
    let minX = Infinity;
    let maxX = -Infinity;
    let minZ = Infinity;
    let maxZ = -Infinity;
    for (const point of points) {
      minX = Math.min(minX, point.x);
      maxX = Math.max(maxX, point.x);
      minZ = Math.min(minZ, point.z);
      maxZ = Math.max(maxZ, point.z);
    }
    const width = Math.max(1, maxX - minX);
    const depth = Math.max(1, maxZ - minZ);
    const padX = width * 0.08;
    const padZ = depth * 0.08;
    return {
      minX: minX - padX,
      minZ: minZ - padZ,
      width: width + padX * 2,
      depth: depth + padZ * 2,
    };
  }

  function projectToMinimap(x, z, bounds) {
    return {
      x: clampPercent(((x - bounds.minX) / bounds.width) * 100),
      y: clampPercent(((z - bounds.minZ) / bounds.depth) * 100),
    };
  }

  function clampPercent(value) {
    if (!Number.isFinite(value)) return 50;
    return Math.max(0, Math.min(100, value));
  }

  function roundForSignature(value) {
    return Number(value || 0).toFixed(1);
  }

  function minimapColorForCategory(category) {
    const colors = {
      rule: "#55d6a0",
      system_constraint: "#55d6a0",
      project: "#4ea1ff",
      skill: "#55dce0",
      workflow: "#f7c65a",
      decision: "#b36cff",
      plan: "#f7c65a",
      session: "#8fb8ff",
      event: "#ef6b6b",
      supporting_context: "#b6c2d7",
      context: "#7fb8ff",
      concept: "#83d8ff",
      pattern: "#a9b3c2",
      technology: "#55dce0",
      domain: "#62b0ff",
      person: "#fff0a4",
      company: "#5bbd9d",
      event_role: "#c8a3ff",
      process: "#7ee0c2",
      setting: "#ffd36b",
      database: "#c6d0de",
      unknown: "#94a3b8",
    };
    return colors[category] || colors.unknown;
  }

  window.__memoryUniverse3DDebug = {
    refreshMinimap() {
      lastMinimapSignature = "";
      renderProjectedMinimap(true);
    },
  };

  function renderNavigationPanel() {
    if (!navigationResults || !viewer) return;
    const query = navigationSearchInput?.value?.trim() || "";
    if (query) {
      const results = viewer.searchTargets(query).slice(0, 12);
      navigationResults.innerHTML = results.length
        ? results.map(summary => renderSearchTargetButton(summary)).join("")
        : `<p class="memory-universe-nav-empty">No targets</p>`;
      return;
    }

    const rows = buildNavigationTreeRows();
    navigationResults.innerHTML = rows.length
      ? rows.map(renderTreeTargetButton).join("")
      : `<p class="memory-universe-nav-empty">No hierarchy targets</p>`;
    return;
    const results = query
      ? viewer.searchTargets(query).slice(0, 10)
      : defaultNavigationTargets(state).slice(0, 12);
    if (results.length === 0) {
      navigationResults.innerHTML = `<p class="memory-universe-nav-empty">No targets</p>`;
      return;
    }
    navigationResults.innerHTML = results.map(summary => `
      <button type="button" data-target-type="${escapeAttribute(summary.type)}" data-target-id="${escapeAttribute(summary.id || "")}">
        <span>${escapeHtml(summary.label)}</span>
        <small>${escapeHtml(formatObjectType(summary.type))} · ${escapeHtml(summary.hierarchyPath?.join(" / ") || "")}</small>
      </button>
    `).join("");
  }

  function defaultNavigationTargets(state) {
    const targets = [];
    if (state?.selectedObject) targets.push(state.selectedObject);
    if (state?.focusSummary) targets.push(state.focusSummary);
    for (const galaxy of latestGraph.hierarchy.galaxies) {
      targets.push(viewer.getObjectSummary({ type: "galaxy", id: galaxy.id }));
    }
    for (const system of latestGraph.hierarchy.solarSystems) {
      targets.push(viewer.getObjectSummary({ type: "solarSystem", id: system.id }));
    }
    return dedupeTargets(targets);
  }

  function buildNavigationTreeRows() {
    const rows = [];
    const solarSystemsByGalaxy = groupBy(latestGraph.hierarchy.solarSystems, system => system.galaxyId);
    const planetarySystemsBySolar = groupBy(latestGraph.hierarchy.planetarySystems, system => system.solarSystemId);

    for (const galaxy of latestGraph.hierarchy.galaxies) {
      const galaxyTarget = { type: "galaxy", id: galaxy.id };
      const galaxyKey = treeTargetKey(galaxyTarget);
      rows.push({
        depth: 0,
        target: galaxyTarget,
        label: galaxy.label,
        expanded: expandedTreeTargets.has(galaxyKey),
        childCount: solarSystemsByGalaxy.get(galaxy.id)?.length || 0,
      });

      if (!expandedTreeTargets.has(galaxyKey)) continue;
      for (const solarSystem of solarSystemsByGalaxy.get(galaxy.id) || []) {
        const solarTarget = { type: "solarSystem", id: solarSystem.id };
        const solarKey = treeTargetKey(solarTarget);
        rows.push({
          depth: 1,
          target: solarTarget,
          label: solarSystem.label,
          expanded: expandedTreeTargets.has(solarKey),
          childCount: planetarySystemsBySolar.get(solarSystem.id)?.length || 0,
        });

        if (!expandedTreeTargets.has(solarKey)) continue;
        for (const planetarySystem of planetarySystemsBySolar.get(solarSystem.id) || []) {
          rows.push({
            depth: 2,
            target: { type: "planetarySystem", id: planetarySystem.id },
            label: planetarySystem.label,
            expanded: false,
            childCount: 0,
          });
        }
      }
    }
    return rows;
  }

  function renderTreeTargetButton(row) {
    const expandedText = row.childCount > 0 ? (row.expanded ? "Collapse" : "Expand") : "Focus";
    return `
      <button type="button"
        class="memory-universe-tree-item"
        data-tree-depth="${row.depth}"
        data-tree-target-type="${escapeAttribute(row.target.type)}"
        data-tree-target-id="${escapeAttribute(row.target.id || "")}"
        aria-expanded="${row.childCount > 0 ? String(row.expanded) : "false"}"
        style="--tree-depth:${row.depth}">
        <span class="memory-universe-tree-caret" aria-hidden="true">${row.childCount > 0 ? (row.expanded ? "-" : "+") : ""}</span>
        <span>${escapeHtml(row.label)}</span>
        <small>${escapeHtml(expandedText)} ${escapeHtml(formatObjectType(row.target.type))}</small>
      </button>
    `;
  }

  function renderSearchTargetButton(summary) {
    return `
      <button type="button"
        class="memory-universe-tree-item"
        data-tree-depth="0"
        data-tree-target-type="${escapeAttribute(summary.type)}"
        data-tree-target-id="${escapeAttribute(summary.id || "")}">
        <span class="memory-universe-tree-caret" aria-hidden="true"></span>
        <span>${escapeHtml(summary.label)}</span>
        <small>${escapeHtml(formatObjectType(summary.type))} / ${escapeHtml(summary.hierarchyPath?.join(" / ") || "")}</small>
      </button>
    `;
  }

  function readTreeTargetFromButton(button) {
    const type = button.dataset.treeTargetType;
    const id = button.dataset.treeTargetId;
    if (!type || !id) return null;
    return { type, id };
  }

  function treeTargetKey(target) {
    return `${target.type}:${target.id || ""}`;
  }

  function groupBy(items, keyFn) {
    const grouped = new Map();
    for (const item of items) {
      const key = keyFn(item);
      const list = grouped.get(key) || [];
      list.push(item);
      grouped.set(key, list);
    }
    return grouped;
  }
}

function createUnavailableBridge(reason) {
  return {
    updateGraph() {},
    selectNode() {},
    getActiveView() {
      return "2d";
    },
    getUnavailableReason() {
      return reason;
    },
  };
}

function convertGalaxyToMemoryUniverseGraph(galaxy) {
  const galaxies = new Map();
  const solarSystems = new Map();
  const planetarySystems = new Map();
  const sourceNodes = [...(galaxy?.nodes || [])]
    .sort((left, right) => scoreNodeFor3D(right) - scoreNodeFor3D(left))
    .slice(0, max3DNodes);
  const nodes = [];

  for (const node of sourceNodes) {
    const raw = node.raw || {};
    const agentNamespace = String(node.agentNamespace || raw.agent_namespace || "codex");
    const agentLabel = String(node.agentLabel || raw.agent_label || labelize(agentNamespace));
    const memorySystem = String(node.memorySystem || raw.memory_system || "knowledge");
    const layer = String(node.layer || raw.galaxy_layer || "external");
    const nodeType = String(node.type || raw.type || "unknown");
    const category = normalizeMemoryUniverseCategory(nodeType);
    const galaxyId = `agent:${stableId(agentNamespace)}`;
    const solarSystemId = `${galaxyId}:system:${stableId(memorySystem)}`;
    const planetarySystemId = `${solarSystemId}:layer:${stableId(layer)}:type:${stableId(nodeType)}`;

    galaxies.set(galaxyId, { id: galaxyId, label: agentLabel });
    solarSystems.set(solarSystemId, { id: solarSystemId, galaxyId, label: labelize(memorySystem) });
    planetarySystems.set(planetarySystemId, {
      id: planetarySystemId,
      galaxyId,
      solarSystemId,
      label: `${labelize(layer)} / ${labelize(nodeType)}`,
    });

    nodes.push({
      id: String(node.id),
      label: String(node.label || raw.label || raw.name || node.id),
      category,
      importance: clamp01(Number(raw.importance ?? raw.activity ?? node.val / 28 ?? 0.5)),
      galaxyId,
      solarSystemId,
      planetarySystemId,
      createdAt: raw.first_seen_at || raw.created_at || raw.last_seen_at,
      summary: raw.content || raw.summary || "",
      production: {
        sourceNodeId: String(raw.source_id || node.id),
        agentNamespace,
        memorySystem,
        galaxyLayer: layer,
        nodeType,
      },
    });
  }

  const nodeIds = new Set(nodes.map(node => node.id));
  const edges = [];
  const sourceEdges = [...(galaxy?.links || [])]
    .filter(link => {
      const sourceNodeId = String(link.source?.id || link.source || "");
      const targetNodeId = String(link.target?.id || link.target || "");
      return nodeIds.has(sourceNodeId) && nodeIds.has(targetNodeId);
    })
    .sort((left, right) => scoreEdgeFor3D(right) - scoreEdgeFor3D(left))
    .slice(0, max3DEdges);
  for (const [index, link] of sourceEdges.entries()) {
    const sourceNodeId = String(link.source?.id || link.source || "");
    const targetNodeId = String(link.target?.id || link.target || "");
    if (!nodeIds.has(sourceNodeId) || !nodeIds.has(targetNodeId)) continue;
    edges.push({
      id: String(link.raw?.id || `${sourceNodeId}->${targetNodeId}:${index}`),
      sourceNodeId,
      targetNodeId,
      relation: String(link.relation || link.raw?.relation || "relates-to"),
    });
  }

  return {
    version: "memory-universe-graph/v1",
    seed: "total-agent-memory-live-viewer",
    hierarchy: {
      galaxies: [...galaxies.values()],
      solarSystems: [...solarSystems.values()],
      planetarySystems: [...planetarySystems.values()],
    },
    nodes,
    edges,
  };
}

function normalizeMemoryUniverseCategory(nodeType) {
  const rawType = String(nodeType || "unknown").toLowerCase();
  if (supportedMemoryCategories.has(rawType)) return rawType;
  if (/(rule|constraint|policy|setting|environment)/.test(rawType)) return "system_constraint";
  if (/(project|company|product|domain)/.test(rawType)) return "project";
  if (/(tool|skill|function|code|language|capability|presentation)/.test(rawType)) return "skill";
  if (/(workflow|process|protocol|technique|procedure)/.test(rawType)) return "workflow";
  if (/(decision|solution|choice|resolution)/.test(rawType)) return "decision";
  if (/(plan|issue|task|test_case|roadmap)/.test(rawType)) return "plan";
  if (/(session|episode|conversation)/.test(rawType)) return "session";
  if (/(event|date|timeline|role)/.test(rawType)) return "event";
  if (/(data|database|storage|document|reference|source)/.test(rawType)) return "supporting_context";
  if (/(concept|pattern|architecture|person|user|interface|design|technology)/.test(rawType)) return "context";
  if (rawType.includes("|")) {
    const parts = rawType.split("|").map(part => part.trim()).filter(Boolean);
    for (const part of parts) {
      const mapped = normalizeMemoryUniverseCategory(part);
      if (mapped !== "unknown") return mapped;
    }
  }
  return "unknown";
}

function scoreNodeFor3D(node) {
  const raw = node?.raw || {};
  const value = Number(raw.importance ?? raw.activity ?? raw.weight ?? node?.val ?? 0);
  return Number.isFinite(value) ? value : 0;
}

function scoreEdgeFor3D(edge) {
  const raw = edge?.raw || {};
  const value = Number(raw.weight ?? raw.score ?? raw.count ?? edge?.weight ?? edge?.value ?? 0);
  return Number.isFinite(value) ? value : 0;
}

function readTargetFromButton(button) {
  const type = button.dataset.targetType;
  const id = button.dataset.targetId;
  if (type === "universe") return { type: "universe" };
  if (!type || !id) return null;
  return { type, id };
}

function dedupeTargets(targets) {
  const seen = new Set();
  const result = [];
  for (const target of targets) {
    if (!target) continue;
    const key = `${target.type}:${target.id || ""}`;
    if (seen.has(key)) continue;
    seen.add(key);
    result.push(target);
  }
  return result;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function escapeAttribute(value) {
  return escapeHtml(value);
}

function readSelectedNodeId(nodeId) {
  const value = nodeId ? String(nodeId) : "";
  return value && !value.startsWith("system:") ? value : null;
}

function canUseWebGL() {
  const canvas = document.createElement("canvas");
  try {
    return Boolean(canvas.getContext("webgl2") || canvas.getContext("webgl"));
  } catch {
    return false;
  }
}

function formatObjectType(type) {
  if (type === "solarSystem") return "Solar System";
  if (type === "planetarySystem") return "Planetary System";
  return String(type || "Object");
}

function stableId(value) {
  return String(value || "unknown")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "") || "unknown";
}

function labelize(value) {
  return String(value || "Unknown")
    .replace(/[_-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/\b\w/g, letter => letter.toUpperCase()) || "Unknown";
}

function clamp01(value) {
  if (!Number.isFinite(value)) return 0.5;
  return Math.max(0, Math.min(1, value));
}

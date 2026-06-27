export function createMemoryGalaxyRenderer({ PIXI, app, stage }) {
  const root = new PIXI.Container();
  const orbitLayer = new PIXI.Container();
  const cometLayer = new PIXI.Container();
  const linkLayer = new PIXI.Container();
  const nodeLayer = new PIXI.Container();
  const labelLayer = new PIXI.Container();
  root.addChild(orbitLayer, cometLayer, linkLayer, nodeLayer, labelLayer);
  stage.addChild(root);

  let currentLayout = null;
  let currentState = null;
  let currentHandlers = {};
  let scale = 1;
  let pan = { x: 0, y: 0 };
  let panState = null;
  let dragState = null;
  let pressState = null;
  let lastTap = { kind: null, key: null, time: 0 };
  const nodeGraphicsById = new Map();
  const systemHitByKey = new Map();
  const systemOrbitGuidesByKey = new Map();
  const satelliteOrbitGuidesByParent = new Map();
  const labelsByNodeId = new Map();
  const dragThreshold = 5;

  stage.eventMode = "static";
  stage.hitArea = app.screen;
  stage.on("pointerdown", event => {
    if (!hasCtrlModifier(event) || !isPrimaryButton(event)) return;
    panState = {
      start: event.global.clone(),
      origin: { ...pan },
    };
  });
  stage.on("pointermove", event => {
    if (panState) {
      pan = {
        x: panState.origin.x + (event.global.x - panState.start.x),
        y: panState.origin.y + (event.global.y - panState.start.y),
      };
      applyTransform();
      return;
    }
    if (pressState) {
      const dxRaw = event.global.x - pressState.start.x;
      const dyRaw = event.global.y - pressState.start.y;
      if (!pressState.moved && Math.hypot(dxRaw, dyRaw) >= dragThreshold) pressState.moved = true;
    }
    if (!dragState || !pressState?.moved) return;
    const dx = (event.global.x - dragState.start.x) / scale;
    const dy = (event.global.y - dragState.start.y) / scale;
    dragState.node.x = dragState.origin.x + dx;
    dragState.node.y = dragState.origin.y + dy;
    dragState.graphic.position.set(dragState.node.x, dragState.node.y);
    currentHandlers.onNodeDrag?.(dragState.node);
  });
  stage.on("pointerup", endDrag);
  stage.on("pointerupoutside", endDrag);
  stage.on("wheel", event => {
    event.preventDefault();
    scale = Math.max(0.25, Math.min(3.5, scale * (event.deltaY > 0 ? 0.9 : 1.1)));
    applyTransform();
  });
  app.ticker.add(ticker => animateScene(Number(ticker.deltaMS || 16.67) / 1000));

  function draw(layout, state, handlers = {}) {
    currentLayout = layout;
    currentState = state;
    currentHandlers = handlers;
    clearLayer(orbitLayer);
    clearLayer(cometLayer);
    clearLayer(linkLayer);
    clearLayer(nodeLayer);
    clearLayer(labelLayer);
    nodeGraphicsById.clear();
    systemHitByKey.clear();
    systemOrbitGuidesByKey.clear();
    satelliteOrbitGuidesByParent.clear();
    labelsByNodeId.clear();
    drawOrbits(layout, state);
    drawLinks(layout, state);
    drawNodes(layout, state, handlers);
    drawComets(layout, state);
    drawLabels(layout, state);
    applyTransform();
  }

  function setTransform(nextTransform = {}) {
    if (Number.isFinite(nextTransform.scale)) scale = Math.max(0.25, Math.min(3.5, Number(nextTransform.scale)));
    if (nextTransform.pan) {
      pan = {
        x: Number(nextTransform.pan.x || 0),
        y: Number(nextTransform.pan.y || 0),
      };
    }
    applyTransform();
  }

  function fitToBounds(bounds) {
    if (!bounds) return;
    const width = Math.max(1, bounds.width || bounds.maxX - bounds.minX);
    const height = Math.max(1, bounds.height || bounds.maxY - bounds.minY);
    scale = Math.min(app.screen.width / (width + 120), app.screen.height / (height + 120), 1.8);
    pan = {
      x: app.screen.width / 2 - ((bounds.minX + bounds.maxX) / 2) * scale,
      y: app.screen.height / 2 - ((bounds.minY + bounds.maxY) / 2) * scale,
    };
    applyTransform();
  }

  function focusOn(x, y, zoomMultiplier = 1.15) {
    scale = Math.max(0.25, Math.min(3.5, scale * zoomMultiplier));
    pan = {
      x: app.screen.width / 2 - x * scale,
      y: app.screen.height / 2 - y * scale,
    };
    applyTransform();
  }

  function centerOn(x, y) {
    pan = {
      x: app.screen.width / 2 - x * scale,
      y: app.screen.height / 2 - y * scale,
    };
    applyTransform();
  }

  function drawOrbits(layout, state) {
    if (state?.showOrbitGuides === false) return;
    for (const orbit of layout.orbits || []) {
      const guide = new PIXI.Graphics();
      const radius = Number(orbit.radius || 0);
      const centerX = Number(orbit.centerX || 0);
      const centerY = Number(orbit.centerY || 0);
      guide.ellipse(centerX, centerY, radius, radius * Number(orbit.aspect || 0.62));
      guide.stroke({ width: 1.1, color: orbitColor(orbit.kind), alpha: 0.2 });
      orbitLayer.addChild(guide);
    }
    for (const system of layout.systems || []) {
      if (system.key === "router") continue;
      const guide = new PIXI.Graphics();
      drawSystemOrbitGuide(guide, system);
      systemOrbitGuidesByKey.set(system.key, guide);
      orbitLayer.addChild(guide);
    }
    for (const satelliteSystem of layout.satelliteSystems || []) {
      const guide = new PIXI.Graphics();
      drawSatelliteOrbitGuide(guide, satelliteSystem);
      satelliteOrbitGuidesByParent.set(satelliteSystem.parentId, guide);
      orbitLayer.addChild(guide);
    }
  }

  function drawLinks(layout, state) {
    const nodeById = new Map((layout.nodes || []).map(node => [node.id, node]));
    const selectedNode = state.selectedNodeId ? nodeById.get(String(state.selectedNodeId)) : null;
    const selectedSystem = selectedNode?.id?.startsWith("system:") ? selectedNode.memorySystem : null;
    const relationMode = String(state.relationshipMode || "all");
    for (const link of layout.links || []) {
      const source = nodeById.get(String(link.source?.id || link.source));
      const target = nodeById.get(String(link.target?.id || link.target));
      if (!source || !target) continue;
      const selected = state.selectedNodeId && (source.id === state.selectedNodeId || target.id === state.selectedNodeId);
      const selectedBySystem = selectedSystem && (source.memorySystem === selectedSystem || target.memorySystem === selectedSystem);
      if (!selected && !selectedBySystem) continue;
      if (relationMode === "direct" && !selected) continue;
      if (relationMode === "inbound" && String(link.target?.id || link.target) !== state.selectedNodeId) continue;
      if (relationMode === "outbound" && String(link.source?.id || link.source) !== state.selectedNodeId) continue;
      const line = new PIXI.Graphics();
      const midX = (source.x + target.x) / 2;
      const midY = (source.y + target.y) / 2;
      const dx = target.x - source.x;
      const dy = target.y - source.y;
      const distance = Math.hypot(dx, dy) || 1;
      const bend = Math.min(120, Math.max(26, distance * 0.16));
      const controlX = midX + (-dy / distance) * bend;
      const controlY = midY + (dx / distance) * bend;
      line.moveTo(source.x, source.y).quadraticCurveTo(controlX, controlY, target.x, target.y);
      line.stroke({
        width: selected ? 2.2 : 1.6,
        color: selected ? 0xfacc15 : 0x7dd3fc,
        alpha: selected ? 0.78 : 0.52,
      });
      linkLayer.addChild(line);
    }
  }

  function drawComets(layout, state) {
    if (state?.showComets === false) return;
    for (const comet of layout.comets || []) {
      const graphic = new PIXI.Graphics();
      const trailPoints = (comet.trailHistory || comet.tail || []).filter(point => Number(point.alpha || 0) > 0.02);
      let previous = comet.head;
      for (const point of trailPoints) {
        graphic.moveTo(previous.x, previous.y).lineTo(point.x, point.y);
        graphic.stroke({ width: 5, color: 0xf97316, alpha: point.alpha || 0.3 });
        previous = point;
      }
      for (const influence of comet.influences || []) {
        graphic.moveTo(comet.head.x, comet.head.y).lineTo(influence.x, influence.y);
        graphic.stroke({ width: Math.max(1, influence.weight * 3), color: 0xf97316, alpha: Math.max(0.18, influence.weight * 0.46) });
      }
      graphic.circle(comet.head.x, comet.head.y, 12);
      graphic.fill({ color: 0xf97316, alpha: 0.95 });
      cometLayer.addChild(graphic);

      const hit = new PIXI.Graphics();
      hit.eventMode = "static";
      hit.cursor = "pointer";
      hit.circle(comet.head.x, comet.head.y, comet.hitRadius || 24);
      hit.fill({ color: 0xffffff, alpha: 0.001 });
        hit.on("pointerdown", event => {
          event.stopPropagation();
          pressState = {
            kind: "comet",
            key: comet.id,
            comet,
            tapDetail: pointerDetail(event),
            start: event.global.clone(),
            moved: false,
          };
        });
      cometLayer.addChild(hit);
    }
  }

  function drawNodes(layout, state, handlers) {
    for (const node of layout.nodes || []) {
      const graphics = new PIXI.Graphics();
      graphics.eventMode = "static";
      graphics.cursor = "grab";
      graphics.position.set(node.x, node.y);
      drawNodeBody(graphics, node, state);
      nodeGraphicsById.set(node.id, graphics);
      graphics.on("pointerdown", event => {
        if (hasCtrlModifier(event)) return;
        event.stopPropagation();
        dragState = { node, graphic: graphics, start: event.global.clone(), origin: { x: node.x, y: node.y } };
        pressState = {
          kind: "node",
          key: node.id,
          node,
          tapDetail: pointerDetail(event),
          start: event.global.clone(),
          moved: false,
        };
        graphics.cursor = "grabbing";
        handlers.onNodePointerDown?.(node, event);
      });
      graphics.on("pointerover", () => handlers.onNodePointerOver?.(node));
      graphics.on("pointerout", () => handlers.onNodePointerOut?.(node));
      nodeLayer.addChild(graphics);
    }
    if (layout.view === "solar") {
      const satelliteSystemByParent = new Map((layout.satelliteSystems || []).map(system => [system.parentId, system]));
      for (const planet of layout.nodes || []) {
        if (planet.orbitalRole !== "planet") continue;
        const system = satelliteSystemByParent.get(planet.id);
        const radius = Math.max(18, (system?.radius || 0) + 12, (planet.renderRadius || 0) + 10);
        const hit = new PIXI.Graphics();
        hit.eventMode = "static";
        hit.cursor = "pointer";
        hit.circle(planet.x, planet.y, radius);
        hit.fill({ color: 0xffffff, alpha: 0.001 });
        hit.on("pointerup", event => {
          event.stopPropagation();
          handlers.onNodeTap?.(planet, { detail: pointerDetail(event) || 1 });
        });
        nodeLayer.addChild(hit);
      }
    }
    if (layout.view === "galaxy") {
      for (const system of layout.systems || []) {
        if (system.key === "router") continue;
        const hit = new PIXI.Graphics();
        hit.eventMode = "static";
        hit.cursor = "pointer";
        hit.circle(system.x, system.y, Math.max(26, (system.radius || 60) * 0.72));
        hit.fill({ color: 0xffffff, alpha: 0.001 });
        hit.on("pointerup", event => {
          event.stopPropagation();
          handlers.onSystemClick?.(system, { detail: pointerDetail(event) || 1 });
        });
        systemHitByKey.set(system.key, hit);
        nodeLayer.addChild(hit);
      }
    }
  }

  function drawLabels(layout, state) {
    const placed = [];
    for (const node of layout.nodes || []) {
      if (!shouldLabel(node, state)) continue;
      const anchor = dynamicLabelAnchor(node);
      const text = new PIXI.Text({
        text: node.label,
        resolution: 2,
        style: {
          fill: 0xf8fbff,
          fontFamily: "Segoe UI, Microsoft YaHei, sans-serif",
          fontSize: node.id === state.selectedNodeId || node.id === state.hoveredNodeId ? 15 : 13,
          fontWeight: node.orbitalRole?.includes("central") || node.orbitalRole === "star" ? "700" : "600",
          stroke: { color: 0x020617, width: 3, alpha: 0.82 },
        },
      });
      text.anchor.set(anchor.align === "right" ? 1 : 0, 0.5);
      text.x = anchor.x;
      text.y = anchor.y;
      const bounds = labelBounds(text, anchor.align);
      if (!isPinned(node, state) && placed.some(item => overlaps(item, bounds))) continue;
      placed.push(bounds);
      let leader = null;
      if (isPinned(node, state)) {
        leader = new PIXI.Graphics();
        leader.moveTo(node.x, node.y).lineTo(anchor.x, anchor.y);
        leader.stroke({ width: 0.8, color: 0xc8d8ff, alpha: 0.34 });
        labelLayer.addChild(leader);
      }
      labelLayer.addChild(text);
      labelsByNodeId.set(node.id, { text, leader });
    }
  }

  function endDrag() {
    if (panState) {
      panState = null;
      return;
    }
    const activePress = pressState;
    const activeDrag = dragState;
    if (activeDrag) {
      activeDrag.graphic.cursor = "grab";
      if (activePress?.moved) currentHandlers.onNodeDragEnd?.(activeDrag.node);
    }
    if (activePress && !activePress.moved) {
      const detail = Math.max(
        Number(activePress.tapDetail || 0),
        nextTapDetail(activePress.kind, activePress.key, lastTap),
      );
      const syntheticEvent = { detail };
      if (activePress.kind === "node") currentHandlers.onNodeTap?.(activePress.node, syntheticEvent);
      if (activePress.kind === "system") currentHandlers.onSystemClick?.(activePress.system, syntheticEvent);
      if (activePress.kind === "comet") currentHandlers.onCometTap?.(activePress.comet, syntheticEvent);
      lastTap = { kind: activePress.kind, key: activePress.key, time: Date.now() };
    }
    dragState = null;
    pressState = null;
    if (currentLayout && currentState) draw(currentLayout, currentState, currentHandlers);
  }

  function applyTransform() {
    root.scale.set(scale);
    root.position.set(pan.x, pan.y);
  }

  function animateScene(deltaSeconds) {
    if (!currentLayout || dragState) return;
    const changed = advanceGalaxyAnimationNodes(currentLayout, deltaSeconds, nodeGraphicsById, currentState?.animationSpeed ?? 1);
    if (!changed || !currentState) return;
    updateAnimatedSceneVisuals(currentLayout, currentState);
  }

  return {
    draw,
    fitToBounds,
    focusOn,
    centerOn,
    setTransform,
    getTransform: () => ({ scale, pan: { ...pan } }),
  };

  function updateSystemHitTargets(layout) {
    for (const system of layout.systems || []) {
      const hit = systemHitByKey.get(system.key);
      if (!hit?.clear) continue;
      hit.clear();
      hit.circle(system.x, system.y, Math.max(26, (system.radius || 60) * 0.72));
      hit.fill({ color: 0xffffff, alpha: 0.001 });
    }
  }

  function updateAnimatedSceneVisuals(layout, state) {
    updateSystemHitTargets(layout);
    for (const system of layout.systems || []) {
      const guide = systemOrbitGuidesByKey.get(system.key);
      if (guide) drawSystemOrbitGuide(guide, system);
    }
    for (const satelliteSystem of layout.satelliteSystems || []) {
      const guide = satelliteOrbitGuidesByParent.get(satelliteSystem.parentId);
      if (guide) drawSatelliteOrbitGuide(guide, satelliteSystem);
    }
    for (const node of layout.nodes || []) {
      const label = labelsByNodeId.get(node.id);
      if (!label) continue;
      const anchor = dynamicLabelAnchor(node);
      label.text.anchor?.set?.(anchor.align === "right" ? 1 : 0, 0.5);
      label.text.x = anchor.x;
      label.text.y = anchor.y;
      if (label.leader) {
        label.leader.clear();
        label.leader.moveTo(node.x, node.y).lineTo(anchor.x, anchor.y);
        label.leader.stroke({ width: 0.8, color: 0xc8d8ff, alpha: 0.34 });
      }
    }
  }
}

function drawSystemOrbitGuide(guide, system) {
  guide.clear();
  const aspect = Number(system.orbitAspect || 0.58);
  guide.ellipse(system.x, system.y, system.radius || 70, (system.radius || 70) * aspect);
  guide.stroke({ width: 1, color: parseColor(system.color || "#7dd3fc"), alpha: 0.18 });
  for (const miniOrbit of system.miniOrbits || []) {
    guide.ellipse(system.x, system.y, miniOrbit.radius, miniOrbit.radius * Number(miniOrbit.aspect || 0.62));
    guide.stroke({ width: 0.8, color: parseColor(system.color || "#7dd3fc"), alpha: 0.12 });
  }
}

function drawSatelliteOrbitGuide(guide, satelliteSystem) {
  guide.clear();
  guide.ellipse(satelliteSystem.x, satelliteSystem.y, satelliteSystem.radius, satelliteSystem.radius * Number(satelliteSystem.aspect || 0.62));
  guide.stroke({ width: 0.8, color: 0x94a3b8, alpha: 0.18 });
  for (const orbit of satelliteSystem.orbits || []) {
    guide.ellipse(satelliteSystem.x, satelliteSystem.y, orbit.radius, orbit.radius * Number(orbit.aspect || 0.62));
    guide.stroke({ width: 0.7, color: 0x64748b, alpha: 0.14 });
  }
}

export function advanceGalaxyAnimationNodes(layout, deltaSeconds, nodeGraphicsById = new Map(), speedMultiplier = 1) {
  if (!layout || !Number.isFinite(deltaSeconds) || deltaSeconds <= 0) return false;
  const speed = Math.max(0, Number.isFinite(speedMultiplier) ? speedMultiplier : 1);
  let changed = false;
  const systemsByKey = new Map((layout.systems || []).map(system => [system.key, system]));
  const nodesById = new Map((layout.nodes || []).map(node => [node.id, node]));
  for (const system of layout.systems || []) {
    const animation = system.animation;
    if (!animation || Number(animation.orbitSpeed || 0) === 0) continue;
    const phase = Number(animation.phase ?? animation.orbitAngle ?? 0) + Number(animation.orbitSpeed || 0) * deltaSeconds * speed;
    animation.phase = phase;
    system.x = Number(animation.orbitCenterX || 0) + Math.cos(phase) * Number(animation.orbitRadiusX || 0);
    system.y = Number(animation.orbitCenterY || 0) + Math.sin(phase) * Number(animation.orbitRadiusY || 0);
    changed = true;
  }
  for (const node of layout.nodes || []) {
    const animation = node.animation;
    if (!animation) continue;
    const orbitSpeed = Number(animation.orbitSpeed || 0);
    const graphic = nodeGraphicsById.get(node.id);

    // System star nodes follow their system's position directly
    if (node.isSystemNode && node.systemKey && systemsByKey.has(node.systemKey)) {
      const system = systemsByKey.get(node.systemKey);
      node.x = system.x;
      node.y = system.y;
      graphic?.position?.set?.(node.x, node.y);
      changed = true;
      continue;
    }

    // Nodes orbiting around their parent system (planets/moons/evidence in galaxy view)
    if (orbitSpeed !== 0 && !animation.parentNodeId) {
      const radiusX = Number(animation.orbitRadiusX || 0);
      const radiusY = Number(animation.orbitRadiusY || 0);
      if (radiusX >= 1 || radiusY >= 1) {
        // Get the updated system position as orbit center
        const centerSystem = animation.parentSystemKey ? systemsByKey.get(animation.parentSystemKey) : null;
        const centerX = centerSystem ? centerSystem.x : Number(animation.orbitCenterX || 0);
        const centerY = centerSystem ? centerSystem.y : Number(animation.orbitCenterY || 0);

        // Update the node's orbit phase and position
        const phase = Number(animation.phase ?? animation.orbitAngle ?? 0) + orbitSpeed * deltaSeconds * speed;
        animation.phase = phase;
        node.x = centerX + Math.cos(phase) * radiusX;
        node.y = centerY + Math.sin(phase) * radiusY;
        graphic?.position?.set?.(node.x, node.y);
        changed = true;
      }
    }

    if (graphic && Number(animation.spinSpeed || 0) !== 0) {
      graphic.rotation += Number(animation.spinSpeed || 0) * deltaSeconds * 60 * speed;
      changed = true;
    }
  }
  for (const node of layout.nodes || []) {
    const animation = node.animation;
    if (!animation || !animation.parentNodeId) continue;
    const parentNode = nodesById.get(animation.parentNodeId);
    const orbitSpeed = Number(animation.orbitSpeed || 0);
    const graphic = nodeGraphicsById.get(node.id);
    if (parentNode && orbitSpeed !== 0) {
      const radiusX = Number(animation.orbitRadiusX || 0);
      const radiusY = Number(animation.orbitRadiusY || 0);
      const phase = Number(animation.phase ?? animation.orbitAngle ?? 0) + orbitSpeed * deltaSeconds * speed;
      animation.phase = phase;
      node.x = parentNode.x + Math.cos(phase) * radiusX;
      node.y = parentNode.y + Math.sin(phase) * radiusY;
      graphic?.position?.set?.(node.x, node.y);
      changed = true;
    }
    if (graphic && Number(animation.spinSpeed || 0) !== 0) {
      graphic.rotation += Number(animation.spinSpeed || 0) * deltaSeconds * 60 * speed;
      changed = true;
    }
  }
  for (const satelliteSystem of layout.satelliteSystems || []) {
    const parentNode = nodesById.get(satelliteSystem.parentId);
    if (!parentNode) continue;
    satelliteSystem.x = parentNode.x;
    satelliteSystem.y = parentNode.y;
    changed = true;
  }
  for (const comet of layout.comets || []) {
    const animation = comet.animation;
    const path = Array.isArray(comet.path) ? comet.path : [];
    if (!animation || path.length < 2 || Number(animation.pathSpeed || 0) === 0) continue;
    const previousHead = { x: comet.head.x, y: comet.head.y };
    const span = path.length - 1;
    animation.pathProgress = Number(animation.pathProgress || 0) + Number(animation.pathSpeed || 0) * deltaSeconds * speed;
    while (animation.pathProgress >= span) animation.pathProgress -= span;
    const index = Math.floor(animation.pathProgress);
    const nextIndex = (index + 1) % path.length;
    const localT = animation.pathProgress - index;
    const from = path[index];
    const to = path[nextIndex];
    comet.head.x = from.x + (to.x - from.x) * localT;
    comet.head.y = from.y + (to.y - from.y) * localT;
    const trailHistory = Array.isArray(comet.trailHistory) ? comet.trailHistory : [];
    if (Math.hypot(previousHead.x - comet.head.x, previousHead.y - comet.head.y) >= 6) {
      trailHistory.unshift({ x: previousHead.x, y: previousHead.y, alpha: 0.72 });
    }
    comet.trailHistory = trailHistory
      .slice(0, 14)
      .map((point, idx) => ({
      x: point.x,
      y: point.y,
      alpha: Math.max(0, Number(point.alpha ?? 0.72) - 0.08 - idx * 0.01),
    }))
      .filter(point => point.alpha > 0.02);
    comet.tail = comet.trailHistory;
    changed = true;
  }
  return changed;
}

function drawNodeBody(graphics, node, state) {
  const selected = node.id === state.selectedNodeId;
  const hovered = node.id === state.hoveredNodeId;
  const color = parseColor(node.color || "#94a3b8");
  const radius = Number(node.renderRadius || 4);
  const systemLike = node.isSystemNode || ["galactic-core", "central-star", "star"].includes(node.orbitalRole);
  if (systemLike) {
    drawSystemBody(graphics, node, { selected, hovered, color, radius });
    return;
  }
  graphics.circle(0, 0, radius + 10);
  graphics.fill({ color, alpha: selected || hovered ? 0.22 : 0.12 });
  graphics.circle(0, 0, radius);
  graphics.fill({ color, alpha: 0.92 });
  graphics.circle(-radius * 0.28, -radius * 0.34, Math.max(1.2, radius * 0.22));
  graphics.fill({ color: 0xffffff, alpha: 0.36 });
  if (selected || hovered) {
    graphics.circle(0, 0, radius + 6);
    graphics.stroke({ width: selected ? 2.2 : 1.4, color: selected ? 0xfacc15 : 0x7dd3fc, alpha: 0.9 });
  }
}

function drawSystemBody(graphics, node, context) {
  const { selected, hovered, color, radius } = context;
  const glowRadius = Math.max(28, radius + 24);
  graphics.circle(0, 0, glowRadius);
  graphics.fill({ color, alpha: selected || hovered ? 0.26 : 0.16 });
  for (let index = 0; index < 5; index += 1) {
    const ring = radius + 12 + index * 8;
    graphics.ellipse(0, 0, ring * 1.55, ring * 0.58);
    graphics.stroke({ width: index === 0 ? 1.2 : 0.8, color, alpha: Math.max(0.08, 0.24 - index * 0.035) });
  }
  const particles = Math.max(16, Math.min(36, Math.round(radius * 1.4)));
  for (let index = 0; index < particles; index += 1) {
    const angle = (index / particles) * Math.PI * 2 + hashPhase(node.id) * 0.2;
    const ring = radius + 16 + (index % 5) * 7;
    const x = Math.cos(angle) * ring * (1.15 + (index % 3) * 0.18);
    const y = Math.sin(angle) * ring * 0.48;
    const dot = 1 + (index % 4 === 0 ? 1.4 : 0);
    graphics.circle(x, y, dot);
    graphics.fill({ color: index % 7 === 0 ? 0xffffff : color, alpha: index % 7 === 0 ? 0.72 : 0.58 });
  }
  graphics.ellipse(0, 0, radius * 2.2, radius * 0.62);
  graphics.fill({ color, alpha: 0.18 });
  graphics.circle(0, 0, radius + 3);
  graphics.fill({ color, alpha: 0.92 });
  graphics.circle(-radius * 0.22, -radius * 0.28, Math.max(2, radius * 0.26));
  graphics.fill({ color: 0xffffff, alpha: 0.55 });
  if (selected || hovered || node.orbitalRole === "galactic-core") {
    graphics.moveTo(-glowRadius * 1.35, -2).lineTo(glowRadius * 1.35, 2);
    graphics.stroke({ width: selected ? 2.2 : 1.4, color: selected ? 0xfacc15 : 0xe7f0ff, alpha: selected ? 0.72 : 0.38 });
    graphics.circle(0, 0, radius + 10);
    graphics.stroke({ width: selected ? 2.4 : 1.4, color: selected ? 0xfacc15 : 0x7dd3fc, alpha: 0.9 });
  }
}

function clearLayer(layer) {
  layer.removeChildren().forEach(child => child.destroy?.({ children: true }));
}

function parseColor(value) {
  return Number.parseInt(String(value || "#94a3b8").replace("#", ""), 16);
}

function hashPhase(value) {
  let hash = 0;
  for (const char of String(value || "")) {
    hash = ((hash << 5) - hash + char.charCodeAt(0)) | 0;
  }
  return (Math.abs(hash) % 6283) / 1000;
}

function orbitColor(kind) {
  return {
    core: 0x60a5fa,
    control: 0xfacc15,
    execution: 0x22d3ee,
    context: 0x2dd4bf,
    evidence: 0x94a3b8,
    archive: 0x64748b,
    category: 0xa78bfa,
    planet: 0x22d3ee,
    moon: 0x7dd3fc,
    external: 0x94a3b8,
  }[kind] || 0x7dd3fc;
}

function sameParent(source, target) {
  return source.memorySystem && source.memorySystem === target.memorySystem;
}

function shouldLabel(node, state) {
  const density = String(state.labelMode || "medium");
  if (density === "none") return false;
  if (node.id === state.selectedNodeId || node.id === state.hoveredNodeId) return true;
  if (density === "low") return ["galactic-core", "central-star", "star"].includes(node.orbitalRole);
  if (density === "medium") return ["galactic-core", "central-star", "central-planet", "star", "category"].includes(node.orbitalRole);
  return ["galactic-core", "central-star", "central-planet", "star", "category"].includes(node.orbitalRole)
    || Number(node.raw?.importance || 0) >= 0.9
    || Number(node.raw?.mention_count || 0) >= 5;
}

function isPinned(node, state) {
  return node.id === state.selectedNodeId || node.id === state.hoveredNodeId || ["galactic-core", "central-star", "central-planet", "star"].includes(node.orbitalRole);
}

function nextTapDetail(kind, key, lastTap) {
  return lastTap.kind === kind && lastTap.key === key && Date.now() - lastTap.time < 420 ? 2 : 1;
}

function pointerDetail(event) {
  return Number(
    event?.detail
    ?? event?.nativeEvent?.detail
    ?? event?.originalEvent?.detail
    ?? 0
  );
}

function hasCtrlModifier(event) {
  return Boolean(event?.ctrlKey ?? event?.nativeEvent?.ctrlKey ?? event?.originalEvent?.ctrlKey);
}

function isPrimaryButton(event) {
  return Number(event?.button ?? event?.nativeEvent?.button ?? event?.originalEvent?.button ?? 0) === 0;
}

function labelBounds(text, align) {
  const width = text.width;
  const height = text.height;
  return {
    x1: align === "right" ? text.x - width : text.x,
    y1: text.y - height / 2,
    x2: align === "right" ? text.x : text.x + width,
    y2: text.y + height / 2,
  };
}

function overlaps(a, b) {
  return a.x1 < b.x2 && a.x2 > b.x1 && a.y1 < b.y2 && a.y2 > b.y1;
}

function dynamicLabelAnchor(node) {
  const centerX = Number(node.animation?.orbitCenterX ?? 0);
  const centerY = Number(node.animation?.orbitCenterY ?? 0);
  const angle = Math.atan2(node.y - centerY || 0.0001, node.x - centerX || 0.0001);
  const align = Math.cos(angle) < 0 ? "right" : "left";
  const xOffset = (node.orbitalRole === "star" || node.orbitalRole === "central-star" ? 28 : 22);
  const yOffset = (node.orbitalRole === "star" || node.orbitalRole === "central-star" ? 18 : 14);
  return {
    x: node.x + Math.cos(angle) * xOffset,
    y: node.y + Math.sin(angle) * yOffset,
    align,
  };
}

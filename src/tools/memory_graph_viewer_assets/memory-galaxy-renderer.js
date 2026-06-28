export function createMemoryGalaxyRenderer({ PIXI, app, stage, onAnimationFrame }) {
  const root = new PIXI.Container();
  const backgroundLayer = new PIXI.Container();
  const orbitLayer = new PIXI.Container();
  const cometLayer = new PIXI.Container();
  const linkLayer = new PIXI.Container();
  const nodeLayer = new PIXI.Container();
  const labelLayer = new PIXI.Container();
  root.addChild(backgroundLayer, orbitLayer, cometLayer, linkLayer, nodeLayer, labelLayer);
  stage.addChild(root);

  let currentLayout = null;
  let currentState = null;
  let currentHandlers = {};
  let scale = 1;
  let pan = { x: 0, y: 0 };
  let panState = null;
  let dragState = null;
  let pressState = null;
  let blankPressState = null;
  let lastTap = { kind: null, key: null, time: 0 };
  const nodeGraphicsById = new Map();
  const systemHitByKey = new Map();
  const solarPlanetHitById = new Map();
  const systemOrbitGuidesByKey = new Map();
  const satelliteOrbitGuidesByParent = new Map();
  const labelsByNodeId = new Map();
  const dragThreshold = 5;
  const minScale = 0.08;
  const maxScale = 3.5;

  stage.eventMode = "static";
  stage.hitArea = app.screen;
  stage.on("pointerdown", event => {
    if (!isPrimaryButton(event)) return;
    if (hasCtrlModifier(event)) {
      panState = {
        start: event.global.clone(),
        origin: { ...pan },
      };
      return;
    }
    blankPressState = {
      start: event.global.clone(),
      moved: false,
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
    if (blankPressState) {
      const dxRaw = event.global.x - blankPressState.start.x;
      const dyRaw = event.global.y - blankPressState.start.y;
      if (!blankPressState.moved && Math.hypot(dxRaw, dyRaw) >= dragThreshold) blankPressState.moved = true;
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
    scale = Math.max(minScale, Math.min(maxScale, scale * (event.deltaY > 0 ? 0.9 : 1.1)));
    applyTransform();
  });
  app.ticker.add(ticker => animateScene(Number(ticker.deltaMS || 16.67) / 1000));

  function draw(layout, state, handlers = {}) {
    currentLayout = layout;
    currentState = state;
    currentHandlers = handlers;
    clearLayer(backgroundLayer);
    clearLayer(orbitLayer);
    clearLayer(cometLayer);
    clearLayer(linkLayer);
    clearLayer(nodeLayer);
    clearLayer(labelLayer);
    nodeGraphicsById.clear();
    systemHitByKey.clear();
    solarPlanetHitById.clear();
    systemOrbitGuidesByKey.clear();
    satelliteOrbitGuidesByParent.clear();
    labelsByNodeId.clear();
    drawBackground(layout, state);
    drawOrbits(layout, state);
    drawLinks(layout, state);
    drawNodes(layout, state, handlers);
    drawComets(layout, state);
    drawLabels(layout, state);
    applyTransform();
  }

  function setTransform(nextTransform = {}) {
    if (Number.isFinite(nextTransform.scale)) scale = Math.max(minScale, Math.min(maxScale, Number(nextTransform.scale)));
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
    scale = Math.max(minScale, Math.min(maxScale, scale * zoomMultiplier));
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

  function drawBackground(layout, state) {
    const bounds = expandedBounds(layout?.bounds);
    const nebula = new PIXI.Graphics();
    drawNebulaWisps(nebula, bounds);
    backgroundLayer.addChild(nebula);

    const stars = new PIXI.Graphics();
    const starCount = layout?.view === "galaxy" ? 260 : 170;
    const seed = `${layout?.view || "galaxy"}:${Math.round(bounds.width)}:${Math.round(bounds.height)}`;
    for (const star of buildDeterministicStarfield(seed, starCount, bounds)) {
      const color = star.warm ? 0xf7c65a : star.blue ? 0x93c5fd : 0xf8fbff;
      stars.circle(star.x, star.y, star.radius);
      stars.fill({ color, alpha: star.alpha });
      if (star.radius > 2.1) {
        stars.circle(star.x, star.y, star.radius * 3.4);
        stars.fill({ color, alpha: star.alpha * 0.12 });
      }
    }
    backgroundLayer.addChild(stars);
  }

  function drawNebulaWisps(graphics, bounds) {
    const width = bounds.maxX - bounds.minX;
    const height = bounds.maxY - bounds.minY;
    const centerX = (bounds.minX + bounds.maxX) / 2;
    const centerY = (bounds.minY + bounds.maxY) / 2;
    const palette = [0x2563eb, 0x0ea5e9, 0x7c3aed, 0xf59e0b];
    for (let index = 0; index < 11; index += 1) {
      const phase = index * 0.74;
      const x = centerX + Math.cos(phase) * width * (0.08 + index * 0.018);
      const y = centerY + Math.sin(phase * 1.41) * height * 0.24;
      const rx = width * (0.16 + (index % 3) * 0.035);
      const ry = height * (0.025 + (index % 4) * 0.012);
      graphics.ellipse(x, y, rx, ry);
      graphics.fill({ color: palette[index % palette.length], alpha: index % 4 === 3 ? 0.035 : 0.05 });
    }
  }

  function drawLinks(layout, state) {
    drawSystemArcs(layout, state);
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
      line.memoryGalaxyLink = {
        sourceId: String(link.source?.id || link.source),
        targetId: String(link.target?.id || link.target),
        selected,
      };
      drawNodeLinkLine(line, source, target, selected);
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
      for (const planet of layout.nodes || []) {
        if (planet.orbitalRole !== "planet") continue;
        const radius = Math.max(18, (planet.renderRadius || 0) + 12);
        const hit = new PIXI.Graphics();
        hit.eventMode = "static";
        hit.cursor = "pointer";
        hit.circle(planet.x, planet.y, radius);
        hit.fill({ color: 0xffffff, alpha: 0.001 });
        hit.on("pointerup", event => {
          event.stopPropagation();
          handlers.onNodeTap?.(planet, { detail: pointerDetail(event) || 1 });
        });
        solarPlanetHitById.set(planet.id, hit);
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
      const systemLike = isSystemLikeNode(node);
      const label = systemLike
        ? createSystemLabel(PIXI, node, anchor)
        : createNodeLabel(PIXI, node, state, anchor);
      const bounds = label.bounds;
      if (!isPinned(node, state) && placed.some(item => overlaps(item, bounds))) continue;
      placed.push(bounds);
      let leader = null;
      if (isPinned(node, state)) {
        leader = new PIXI.Graphics();
        drawLabelLeader(leader, node, anchor);
        labelLayer.addChild(leader);
      }
      for (const text of label.texts) labelLayer.addChild(text);
      labelsByNodeId.set(node.id, { ...label, leader });
    }
  }

  function drawSystemArcs(layout, state) {
    if (layout?.view !== "galaxy") return;
    const router = (layout.systems || []).find(system => system.key === "router");
    if (!router) return;
    for (const system of layout.systems || []) {
      if (system.key === "router") continue;
      const arc = new PIXI.Graphics();
      arc.memoryGalaxySystemArcKey = system.key;
      drawSystemArcLine(arc, router, system);
      linkLayer.addChild(arc);
    }
  }

  function endDrag() {
    if (panState) {
      panState = null;
      blankPressState = null;
      return;
    }
    const activePress = pressState;
    const activeDrag = dragState;
    const activeBlankPress = blankPressState;
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
    blankPressState = null;
    if (!activePress && !activeDrag && activeBlankPress && !activeBlankPress.moved) {
      currentHandlers.onBlankTap?.();
    }
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
    onAnimationFrame?.(currentLayout);
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

  function updateSolarPlanetHitTargets(layout) {
    if (layout?.view !== "solar") return;
    for (const planet of layout.nodes || []) {
      if (planet.orbitalRole !== "planet") continue;
      const hit = solarPlanetHitById.get(planet.id);
      if (!hit?.clear) continue;
      const radius = Math.max(18, (planet.renderRadius || 0) + 12);
      hit.clear();
      hit.circle(planet.x, planet.y, radius);
      hit.fill({ color: 0xffffff, alpha: 0.001 });
    }
  }

  function updateAnimatedSceneVisuals(layout, state) {
    updateSystemHitTargets(layout);
    updateSolarPlanetHitTargets(layout);
    updateLinkGraphics(layout);
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
      positionLabel(label, anchor);
      if (label.leader) {
        label.leader.clear();
        drawLabelLeader(label.leader, node, anchor);
      }
    }
  }

  function updateLinkGraphics(layout) {
    const systemsByKey = new Map((layout.systems || []).map(system => [system.key, system]));
    const router = systemsByKey.get("router");
    const nodesById = new Map((layout.nodes || []).map(node => [String(node.id), node]));
    for (const graphic of linkLayer.children || []) {
      if (graphic.memoryGalaxySystemArcKey) {
        const system = systemsByKey.get(graphic.memoryGalaxySystemArcKey);
        if (router && system) drawSystemArcLine(graphic, router, system);
        continue;
      }
      if (graphic.memoryGalaxyLink) {
        const source = nodesById.get(graphic.memoryGalaxyLink.sourceId);
        const target = nodesById.get(graphic.memoryGalaxyLink.targetId);
        if (source && target) drawNodeLinkLine(graphic, source, target, graphic.memoryGalaxyLink.selected);
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
  const color = parseColor(satelliteSystem.color || "#94a3b8");
  guide.ellipse(satelliteSystem.x, satelliteSystem.y, satelliteSystem.radius, satelliteSystem.radius * Number(satelliteSystem.aspect || 0.62));
  guide.stroke({ width: 0.8, color, alpha: 0.18 });
  for (const orbit of satelliteSystem.orbits || []) {
    guide.ellipse(satelliteSystem.x, satelliteSystem.y, orbit.radius, orbit.radius * Number(orbit.aspect || 0.62));
    guide.stroke({ width: 0.7, color, alpha: 0.14 });
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
  const systemLike = isSystemLikeNode(node);
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
  const isPlanetSystem = Boolean(node.isPlanetSystemNode);
  const visualAspect = Number(node.visualOrbitAspect || 0.56);
  const glowRadius = isPlanetSystem ? Math.max(22, radius + 18) : Math.max(38, radius + 36);
  graphics.circle(0, 0, glowRadius * 1.65);
  graphics.fill({ color, alpha: selected || hovered ? 0.12 : 0.07 });
  graphics.circle(0, 0, glowRadius);
  graphics.fill({ color, alpha: selected || hovered ? 0.24 : 0.15 });

  const ringCount = isPlanetSystem ? 5 : 7;
  for (let index = 0; index < ringCount; index += 1) {
    const ring = radius + (isPlanetSystem ? 7 : 12) + index * (isPlanetSystem ? 5.5 : 9);
    graphics.ellipse(0, 0, ring * (isPlanetSystem ? 1.55 : 1.72), ring * visualAspect);
    graphics.stroke({ width: index === 0 ? 1.5 : 0.85, color, alpha: Math.max(0.07, 0.28 - index * 0.032) });
  }

  const phase = hashPhase(node.id);
  const arms = node.orbitalRole === "galactic-core" ? 5 : 4;
  const particles = node.orbitalRole === "galactic-core" ? 150 : isPlanetSystem ? 46 : 92;
  for (let index = 0; index < particles; index += 1) {
    const arm = index % arms;
    const t = index / Math.max(1, particles - 1);
    const swirl = t * Math.PI * 4.8 + arm * (Math.PI * 2 / arms) + phase;
    const jitter = Math.sin((index + 1) * 12.989 + phase) * 0.18;
    const ring = radius * 0.9 + t * glowRadius * 1.28;
    const x = Math.cos(swirl + jitter) * ring * (1.18 + t * 0.58);
    const y = Math.sin(swirl + jitter) * ring * (isPlanetSystem ? visualAspect * (0.56 + t * 0.28) : 0.34 + t * 0.22);
    const dot = 0.85 + (index % 11 === 0 ? 1.55 : index % 5 === 0 ? 0.7 : 0);
    const dotColor = index % 13 === 0 ? 0xffffff : index % 9 === 0 ? 0x93c5fd : color;
    graphics.circle(x, y, dot);
    graphics.fill({ color: dotColor, alpha: index % 13 === 0 ? 0.84 : Math.max(0.18, 0.72 - t * 0.36) });
  }

  graphics.ellipse(0, 0, radius * (isPlanetSystem ? 2.65 : 3.45), radius * (isPlanetSystem ? visualAspect * 1.18 : 0.82));
  graphics.fill({ color, alpha: 0.16 });
  graphics.ellipse(0, 0, radius * (isPlanetSystem ? 1.75 : 2.15), radius * (isPlanetSystem ? visualAspect * 0.76 : 0.52));
  graphics.fill({ color: 0xe7f0ff, alpha: 0.08 });
  graphics.circle(0, 0, radius + 4);
  graphics.fill({ color, alpha: 0.95 });
  graphics.circle(0, 0, Math.max(3, radius * 0.42));
  graphics.fill({ color: 0xffffff, alpha: 0.72 });
  graphics.circle(-radius * 0.28, -radius * 0.33, Math.max(2, radius * 0.22));
  graphics.fill({ color: 0xffffff, alpha: 0.58 });
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

function drawNodeLinkLine(line, source, target, selected) {
  line.clear?.();
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
}

function drawSystemArcLine(arc, router, system) {
  arc.clear?.();
  const dx = system.x - router.x;
  const dy = system.y - router.y;
  const distance = Math.hypot(dx, dy) || 1;
  const bend = Math.min(190, Math.max(54, distance * 0.22));
  const direction = system.y >= router.y ? 1 : -1;
  const controlX = (router.x + system.x) / 2 + (-dy / distance) * bend * direction;
  const controlY = (router.y + system.y) / 2 + (dx / distance) * bend * direction;
  const color = parseColor(system.color || "#4ea1ff");
  arc.moveTo(router.x, router.y).quadraticCurveTo(controlX, controlY, system.x, system.y);
  arc.stroke({ width: 6.5, color, alpha: 0.045 });
  arc.moveTo(router.x, router.y).quadraticCurveTo(controlX, controlY, system.x, system.y);
  arc.stroke({ width: 2.4, color, alpha: 0.28 });
  arc.moveTo(router.x, router.y).quadraticCurveTo(controlX, controlY, system.x, system.y);
  arc.stroke({ width: 0.9, color: 0xe7f0ff, alpha: 0.22 });
}

function parseColor(value) {
  return Number.parseInt(String(value || "#94a3b8").replace("#", ""), 16);
}

function expandedBounds(bounds) {
  const source = bounds || { minX: -900, maxX: 900, minY: -560, maxY: 560 };
  const minX = Number.isFinite(source.minX) ? source.minX : -900;
  const maxX = Number.isFinite(source.maxX) ? source.maxX : 900;
  const minY = Number.isFinite(source.minY) ? source.minY : -560;
  const maxY = Number.isFinite(source.maxY) ? source.maxY : 560;
  const padX = Math.max(260, (maxX - minX) * 0.18);
  const padY = Math.max(180, (maxY - minY) * 0.22);
  return {
    minX: minX - padX,
    maxX: maxX + padX,
    minY: minY - padY,
    maxY: maxY + padY,
    width: maxX - minX + padX * 2,
    height: maxY - minY + padY * 2,
  };
}

export function buildDeterministicStarfield(seed = "memory-galaxy", count = 180, bounds = { minX: -900, maxX: 900, minY: -560, maxY: 560 }) {
  const points = [];
  let state = seededNumber(seed);
  for (let index = 0; index < count; index += 1) {
    state = lcg(state);
    const x = bounds.minX + (state / 0xffffffff) * (bounds.maxX - bounds.minX);
    state = lcg(state);
    const y = bounds.minY + (state / 0xffffffff) * (bounds.maxY - bounds.minY);
    state = lcg(state);
    const radius = 0.7 + (state / 0xffffffff) * 2.4;
    state = lcg(state);
    const alpha = 0.18 + (state / 0xffffffff) * 0.72;
    points.push({ x, y, radius, alpha, warm: index % 17 === 0, blue: index % 5 === 0 });
  }
  return points;
}

export function systemLabelLines(node) {
  const name = String(node.label || "Memory System").toUpperCase();
  const type = node.isPlanetSystemNode ? "Planet System" : systemTypeLabel(node.memorySystem || node.systemKey || "memory");
  const count = Number(node.raw?.memberCount ?? node.memberCount ?? node.childCount ?? 0);
  return [name, type, count > 0 ? `${count.toLocaleString()} memories` : ""].filter(Boolean);
}

function seededNumber(seed) {
  let value = 2166136261;
  for (const char of String(seed || "memory-galaxy")) {
    value ^= char.charCodeAt(0);
    value = Math.imul(value, 16777619);
  }
  return value >>> 0;
}

function lcg(value) {
  return (Math.imul(value, 1664525) + 1013904223) >>> 0;
}

function systemTypeLabel(system) {
  return {
    router: "Route System",
    rule: "Rule System",
    persona: "Persona System",
    skill: "Skill System",
    harness: "Harness System",
    preference: "Preference System",
    project: "Project System",
    knowledge: "Knowledge System",
    event: "Event System",
    source: "Source System",
    archive: "Archive System",
  }[system] || "Memory System";
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
  if (density === "low") return isSystemLikeNode(node);
  if (density === "medium") return isSystemLikeNode(node) || ["central-planet", "category"].includes(node.orbitalRole);
  return isSystemLikeNode(node) || ["central-planet", "category"].includes(node.orbitalRole)
    || Number(node.raw?.importance || 0) >= 0.9
    || Number(node.raw?.mention_count || 0) >= 5;
}

function isPinned(node, state) {
  return node.id === state.selectedNodeId || node.id === state.hoveredNodeId || isSystemLikeNode(node) || node.orbitalRole === "central-planet";
}

function isSystemLikeNode(node) {
  return Boolean(node.isSystemNode || node.isPlanetSystemNode || ["galactic-core", "central-star", "star"].includes(node.orbitalRole));
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

function createNodeLabel(PIXI, node, state, anchor) {
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
  const label = { kind: "single", texts: [text] };
  positionLabel(label, anchor);
  label.bounds = labelBounds(text, anchor.align);
  return label;
}

function createSystemLabel(PIXI, node, anchor) {
  const color = parseColor(node.color || "#7dd3fc");
  const lines = systemLabelLines(node);
  const prominentSolarLabel = Boolean(node.isPlanetSystemNode || node.isSolarCenterStar);
  const title = new PIXI.Text({
    text: lines[0],
    resolution: 2,
    style: {
      fill: 0xf8fbff,
      fontFamily: "Segoe UI, Microsoft YaHei, sans-serif",
      fontSize: node.orbitalRole === "galactic-core" ? 16 : prominentSolarLabel ? 36 : 14,
      fontWeight: "800",
      stroke: { color: 0x020617, width: prominentSolarLabel ? 7 : 4, alpha: 0.94 },
    },
  });
  const subtitle = new PIXI.Text({
    text: lines[1] || "",
    resolution: 2,
    style: {
      fill: color,
      fontFamily: "Segoe UI, Microsoft YaHei, sans-serif",
      fontSize: prominentSolarLabel ? 20 : 11,
      fontWeight: "700",
      stroke: { color: 0x020617, width: prominentSolarLabel ? 5 : 3, alpha: 0.9 },
    },
  });
  const count = new PIXI.Text({
    text: lines[2] || "",
    resolution: 2,
    style: {
      fill: 0xd8e4f7,
      fontFamily: "Segoe UI, Microsoft YaHei, sans-serif",
      fontSize: prominentSolarLabel ? 18 : 11,
      fontWeight: "500",
      stroke: { color: 0x020617, width: 3, alpha: 0.82 },
    },
  });
  const label = { kind: "system", texts: [title, subtitle, count].filter(text => text.text) };
  positionLabel(label, anchor);
  label.bounds = groupLabelBounds(label.texts, anchor.align);
  return label;
}

function positionLabel(label, anchor) {
  const alignAnchor = anchor.align === "right" ? 1 : 0;
  if (label.kind === "system") {
    const lineGap = label.texts.some(text => Number(text.style?.fontSize || 0) >= 20) ? 23 : 17;
    const yStart = label.texts.length > 2 ? -lineGap * 1.14 : -lineGap * 0.82;
    label.texts.forEach((text, index) => {
      text.anchor?.set?.(alignAnchor, 0);
      text.x = anchor.x;
      text.y = anchor.y + yStart + index * lineGap;
    });
    label.bounds = groupLabelBounds(label.texts, anchor.align);
    return;
  }
  const [text] = label.texts;
  text.anchor?.set?.(alignAnchor, 0.5);
  text.x = anchor.x;
  text.y = anchor.y;
  label.bounds = labelBounds(text, anchor.align);
}

function groupLabelBounds(texts, align) {
  if (!texts.length) return { x1: 0, y1: 0, x2: 0, y2: 0 };
  return texts.reduce((acc, text) => {
    const item = labelBounds(text, align);
    return {
      x1: Math.min(acc.x1, item.x1),
      y1: Math.min(acc.y1, item.y1),
      x2: Math.max(acc.x2, item.x2),
      y2: Math.max(acc.y2, item.y2),
    };
  }, { x1: Infinity, y1: Infinity, x2: -Infinity, y2: -Infinity });
}

function overlaps(a, b) {
  return a.x1 < b.x2 && a.x2 > b.x1 && a.y1 < b.y2 && a.y2 > b.y1;
}

function dynamicLabelAnchor(node) {
  const centerX = Number(node.animation?.orbitCenterX ?? 0);
  const centerY = Number(node.animation?.orbitCenterY ?? 0);
  const angle = Math.atan2(node.y - centerY || 0.0001, node.x - centerX || 0.0001);
  const align = Math.cos(angle) < 0 ? "right" : "left";
  if (node.isPlanetSystemNode || node.isSolarCenterStar) {
    const offset = node.isSolarCenterStar
      ? Math.min(190, Math.max(120, Number(node.renderRadius || 24) + 56))
      : Math.min(92, Math.max(58, Number(node.renderRadius || 12) + 30));
    const elbow = node.isSolarCenterStar ? 76 : 46;
    const sign = align === "right" ? -1 : 1;
    return {
      x: node.x + Math.cos(angle) * offset + sign * elbow,
      y: node.y + Math.sin(angle) * offset,
      align,
      elbowX: node.x + Math.cos(angle) * offset,
      elbowY: node.y + Math.sin(angle) * offset,
    };
  }
  const xOffset = (node.orbitalRole === "star" || node.orbitalRole === "central-star" ? 28 : 22);
  const yOffset = (node.orbitalRole === "star" || node.orbitalRole === "central-star" ? 18 : 14);
  return {
    x: node.x + Math.cos(angle) * xOffset,
    y: node.y + Math.sin(angle) * yOffset,
    align,
  };
}

function drawLabelLeader(leader, node, anchor) {
  const color = parseColor(node.color || "#c8d8ff");
  if ((node.isPlanetSystemNode || node.isSolarCenterStar) && Number.isFinite(anchor.elbowX) && Number.isFinite(anchor.elbowY)) {
    const angle = Math.atan2(anchor.elbowY - node.y || 0.0001, anchor.elbowX - node.x || 0.0001);
    const startRadius = Math.max(0, Number(node.renderRadius || 0) + 3);
    const startX = node.x + Math.cos(angle) * startRadius;
    const startY = node.y + Math.sin(angle) * startRadius;
    leader.moveTo(startX, startY).lineTo(anchor.elbowX, anchor.elbowY).lineTo(anchor.x, anchor.elbowY);
    leader.stroke({ width: node.isSolarCenterStar ? 3.2 : 2.4, color, alpha: 0.96 });
    return;
  }
  leader.moveTo(node.x, node.y).lineTo(anchor.x, anchor.y);
  leader.stroke({ width: 0.8, color: 0xc8d8ff, alpha: 0.34 });
}

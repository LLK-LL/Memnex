export function createMemoryGalaxyRenderer({ PIXI, app, stage }) {
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
  let dragState = null;
  let elapsed = 0;

  stage.eventMode = "static";
  stage.hitArea = app.screen;
  stage.on("pointermove", event => {
    if (!dragState) return;
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
    const factor = event.deltaY > 0 ? 0.9 : 1.1;
    scale = Math.max(0.25, Math.min(3.5, scale * factor));
    applyTransform();
  });
  app.ticker.add(ticker => {
    elapsed += ticker.deltaTime;
    animateScene();
  });

  function draw(layout, state, handlers = {}) {
    currentLayout = layout;
    currentState = state;
    currentHandlers = handlers;
    clearLayer(orbitLayer);
    clearLayer(cometLayer);
    clearLayer(linkLayer);
    clearLayer(nodeLayer);
    clearLayer(labelLayer);

    drawOrbits(layout);
    drawLinks(layout, state);
    drawNodes(layout, state, handlers);
    drawComets(layout);
    drawLabels(layout, state);
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

  function drawOrbits(layout) {
    for (const orbit of layout.orbits || []) {
      const guide = new PIXI.Graphics();
      const radius = Number(orbit.radius || 0);
      guide.ellipse(0, 0, radius, radius * 0.62);
      guide.stroke({ width: 1.1, color: orbitColor(orbit.kind), alpha: 0.20 });
      orbitLayer.addChild(guide);
    }
    for (const system of layout.systems || []) {
      if (system.key === "router") continue;
      const guide = new PIXI.Graphics();
      const selected = system.key === currentState?.selectedSystem;
      guide.ellipse(system.x, system.y, system.radius || 70, (system.radius || 70) * 0.62);
      guide.stroke({ width: selected ? 2.4 : 1, color: selected ? 0xfacc15 : parseColor(system.color || "#7dd3fc"), alpha: selected ? 0.82 : 0.18 });
      if (selected) {
        guide.ellipse(system.x, system.y, (system.radius || 70) + 18, ((system.radius || 70) + 18) * 0.62);
        guide.stroke({ width: 1.4, color: 0xfacc15, alpha: 0.38 });
      }
      for (const miniOrbit of system.miniOrbits || []) {
        guide.ellipse(system.x, system.y, miniOrbit.radius, miniOrbit.radius * 0.62);
        guide.stroke({ width: 0.8, color: parseColor(system.color || "#7dd3fc"), alpha: 0.12 });
      }
      orbitLayer.addChild(guide);
    }
    for (const satelliteSystem of layout.satelliteSystems || []) {
      const guide = new PIXI.Graphics();
      guide.ellipse(satelliteSystem.x, satelliteSystem.y, satelliteSystem.radius, satelliteSystem.radius * 0.62);
      guide.stroke({ width: 0.8, color: 0x94a3b8, alpha: 0.18 });
      orbitLayer.addChild(guide);
    }
  }

  function drawLinks(layout, state) {
    const nodeById = new Map((layout.nodes || []).map(node => [node.id, node]));
    for (const link of layout.links || []) {
      const source = nodeById.get(String(link.source?.id || link.source));
      const target = nodeById.get(String(link.target?.id || link.target));
      if (!source || !target) continue;
      const selected = state.selectedNodeId && (source.id === state.selectedNodeId || target.id === state.selectedNodeId);
      const hovered = state.hoveredNodeId && (source.id === state.hoveredNodeId || target.id === state.hoveredNodeId);
      const path = link.isPath === true;
      const visible = state.relationshipMode === "focus" ? selected || hovered : state.relationshipMode === "path" ? path : sameParent(source, target);
      const line = new PIXI.Graphics();
      line.moveTo(source.x, source.y).lineTo(target.x, target.y);
      line.stroke({
        width: selected || hovered || path ? 2.2 : 0.7,
        color: selected || hovered || path ? 0xfacc15 : 0x7dd3fc,
        alpha: selected || hovered || path ? 0.78 : visible ? 0.15 : 0.035,
      });
      linkLayer.addChild(line);
    }
  }

  function drawComets(layout) {
    for (const comet of layout.comets || []) {
      const trail = new PIXI.Graphics();
      let previous = comet.head;
      for (const point of comet.tail || []) {
        trail.moveTo(previous.x, previous.y).lineTo(point.x, point.y);
        trail.stroke({ width: 5, color: 0xf97316, alpha: point.alpha || 0.35 });
        previous = point;
      }
      for (const influence of comet.influences || []) {
        trail.moveTo(comet.head.x, comet.head.y).lineTo(influence.x, influence.y);
        trail.stroke({ width: Math.max(1, influence.weight * 3), color: 0xf97316, alpha: Math.max(0.18, influence.weight * 0.46) });
        trail.ellipse(influence.x, influence.y, influence.radius * (0.9 + influence.weight * 0.55), influence.radius * (0.56 + influence.weight * 0.35));
        trail.stroke({ width: 1.2, color: 0xf97316, alpha: influence.weight * 0.30 });
      }
      trail.circle(comet.head.x, comet.head.y, 12);
      trail.fill({ color: 0xf97316, alpha: 0.95 });
      cometLayer.addChild(trail);
      const hit = new PIXI.Graphics();
      hit.eventMode = "static";
      hit.cursor = "pointer";
      hit.circle(comet.head.x, comet.head.y, comet.hitRadius || 24);
      hit.fill({ color: 0xffffff, alpha: 0.001 });
      hit.on("pointertap", event => {
        event.stopPropagation();
        currentHandlers.onCometTap?.(comet, event);
      });
      cometLayer.addChild(hit);
    }
  }

  function drawNodes(layout, state, handlers) {
    for (const system of layout.systems || []) {
      if (system.key === "router") continue;
      const hit = new PIXI.Graphics();
      hit.eventMode = "static";
      hit.cursor = "pointer";
      hit.circle(system.x, system.y, Math.max(30, system.radius || 60));
      hit.fill({ color: 0xffffff, alpha: 0.001 });
      hit.on("pointertap", event => {
        event.stopPropagation();
        handlers.onSystemClick?.(system);
      });
      hit.on("pointerover", () => handlers.onSystemHover?.(system));
      hit.on("pointerout", () => handlers.onSystemHoverOut?.(system));
      nodeLayer.addChild(hit);
    }
    for (const node of layout.nodes || []) {
      const graphics = new PIXI.Graphics();
      graphics.eventMode = "static";
      graphics.cursor = "grab";
      graphics.position.set(node.x, node.y);
      drawNodeBody(graphics, node, state);
      graphics.on("pointerdown", event => {
        event.stopPropagation();
        dragState = {
          node,
          graphic: graphics,
          start: event.global.clone(),
          origin: { x: node.x, y: node.y },
        };
        graphics.cursor = "grabbing";
        handlers.onNodePointerDown?.(node, event);
      });
      graphics.on("pointertap", event => {
        event.stopPropagation();
        handlers.onNodeTap?.(node, event);
      });
      graphics.on("pointerover", () => handlers.onNodePointerOver?.(node));
      graphics.on("pointerout", () => handlers.onNodePointerOut?.(node));
      nodeLayer.addChild(graphics);
    }
  }

  function drawLabels(layout, state) {
    const placed = [];
    for (const node of layout.nodes || []) {
      if (!shouldLabel(node, state)) continue;
      const anchor = node.labelAnchor || { x: node.x + 24, y: node.y, align: "left" };
      const text = new PIXI.Text({
        text: node.label,
        resolution: 2,
        style: {
          fill: 0xf8fbff,
          fontFamily: "Segoe UI, Microsoft YaHei, sans-serif",
          fontSize: node.id === state.selectedNodeId || node.id === state.hoveredNodeId ? 13 : 11,
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
      const plate = new PIXI.Graphics();
      plate.roundRect(bounds.x1 - 7, bounds.y1 - 4, bounds.x2 - bounds.x1 + 14, bounds.y2 - bounds.y1 + 8, 7);
      plate.fill({ color: 0x020817, alpha: isPinned(node, state) ? 0.74 : 0.46 });
      plate.stroke({ width: 1, color: isPinned(node, state) ? 0x7dd3fc : 0x334155, alpha: isPinned(node, state) ? 0.42 : 0.22 });
      labelLayer.addChild(plate, text);
    }
  }

  function endDrag() {
    if (!dragState) return;
    dragState.graphic.cursor = "grab";
    currentHandlers.onNodeDragEnd?.(dragState.node);
    dragState = null;
    if (currentLayout && currentState) draw(currentLayout, currentState, currentHandlers);
  }

  function applyTransform() {
    root.scale.set(scale);
    root.position.set(pan.x, pan.y);
  }

  function animateScene() {
    if (!currentLayout || dragState) return;
    let changed = false;
    for (const node of currentLayout.nodes || []) {
      const animation = node.animation;
      if (!animation || animation.orbitSpeed === 0) continue;
      const radiusX = animation.orbitRadiusX;
      const radiusY = animation.orbitRadiusY;
      if (radiusX < 1 && radiusY < 1) continue;
      const angle = animation.orbitAngle + elapsed * animation.orbitSpeed * 0.016;
      node.x = animation.orbitCenterX + Math.cos(angle) * radiusX;
      node.y = animation.orbitCenterY + Math.sin(angle) * radiusY;
      changed = true;
    }
    if (changed && currentState) draw(currentLayout, currentState, currentHandlers);
  }

  return {
    draw,
    fitToBounds,
    getTransform: () => ({ scale, pan: { ...pan } }),
  };
}

function drawNodeBody(graphics, node, state) {
  const selected = node.id === state.selectedNodeId;
  const hovered = node.id === state.hoveredNodeId;
  const color = parseColor(node.color || "#94a3b8");
  const radius = Number(node.renderRadius || 4);
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

function clearLayer(layer) {
  layer.removeChildren().forEach(child => child.destroy?.({ children: true }));
}

function parseColor(value) {
  return Number.parseInt(String(value || "#94a3b8").replace("#", ""), 16);
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
  if (node.id === state.selectedNodeId || node.id === state.hoveredNodeId) return true;
  return ["galactic-core", "central-star", "central-planet", "star", "category"].includes(node.orbitalRole);
}

function isPinned(node, state) {
  return node.id === state.selectedNodeId || node.id === state.hoveredNodeId || ["galactic-core", "central-star", "central-planet", "star"].includes(node.orbitalRole);
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

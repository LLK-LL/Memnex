const layerOrbit = {
  core: 70,
  active: 130,
  knowledge: 210,
  episode: 290,
  external: 370,
};

const sphereShell = {
  core: 85,
  active: 155,
  knowledge: 245,
  episode: 330,
  external: 410,
};

const clusterCenters = {
  project: { x: -360, y: -150 },
  concept: { x: 0, y: -190 },
  technology: { x: 360, y: -120 },
  pattern: { x: -260, y: 190 },
  event: { x: 190, y: 210 },
  external: { x: 470, y: 150 },
};

const galacticSystemCenters = {
  router: { x: 0, y: 0, orbitRadius: 0, label: "Router Core" },
  rule: { x: -330, y: -150, orbitRadius: 128, label: "Rules" },
  persona: { x: 0, y: -250, orbitRadius: 126, label: "Persona" },
  skill: { x: 345, y: -120, orbitRadius: 142, label: "Skills" },
  harness: { x: 365, y: 185, orbitRadius: 122, label: "Harness" },
  preference: { x: -335, y: 185, orbitRadius: 112, label: "Preferences" },
  project: { x: 0, y: 265, orbitRadius: 126, label: "Projects" },
  knowledge: { x: -610, y: 35, orbitRadius: 118, label: "Knowledge" },
  event: { x: 610, y: 45, orbitRadius: 112, label: "Events" },
  source: { x: 0, y: 470, orbitRadius: 96, label: "Sources" },
};

const memorySystemPriority = {
  router: 56,
  persona: 48,
  skill: 44,
  harness: 40,
  rule: 38,
  preference: 30,
  project: 28,
  knowledge: 20,
  event: 14,
  source: 10,
};

const typeColors = {
  project: "#60a5fa",
  concept: "#34d399",
  entity: "#fbbf24",
  memory: "#a78bfa",
  rule: "#f87171",
  decision: "#fb7185",
  solution: "#22c55e",
  lesson: "#f97316",
  convention: "#38bdf8",
  technology: "#38bdf8",
  pattern: "#fb7185",
  domain: "#c084fc",
  person: "#facc15",
  company: "#22c55e",
  default: "#94a3b8",
};

export function nodeColor(type) {
  return typeColors[type] || typeColors.default;
}

export function convertGraphToGalaxy(graph) {
  const nodes = graph.elements.nodes.map((node, index) => {
    const data = node.data;
    const layer = data.galaxy_layer || inferLayer(data);
    const orbit = layerOrbit[layer] || layerOrbit.external;
    const angle = index * 2.399963229728653;
    const lift = ((index % 9) - 4) * 14;
    const galaxyNode = {
      id: String(data.id),
      label: data.label || data.name || String(data.id),
      type: data.type || "default",
      layer,
      orbit,
      val: Math.max(3, Math.min(28, 4 + Number(data.activity || 0) * 20 + Number(data.importance || 0) * 3)),
      color: nodeColor(data.type),
      x: Math.cos(angle) * orbit,
      y: lift,
      z: Math.sin(angle) * orbit,
      raw: data,
    };
    galaxyNode.memorySystem = memorySystemForNode(galaxyNode);
    return galaxyNode;
  });

  const links = graph.elements.edges.map(edge => ({
    source: String(edge.data.source),
    target: String(edge.data.target),
    relation: edge.data.relation || "related",
    weight: Number(edge.data.weight || 0),
    raw: edge.data,
  }));

  return {
    nodes,
    links,
    metadata: graph.metadata || {},
  };
}

export function filterGalaxy(galaxy, options) {
  const query = (options.query || "").trim().toLowerCase();
  const activeTypes = options.activeTypes || new Set();
  const activeLayers = options.activeLayers || new Set();
  const minWeight = Number(options.minWeight || 0);
  const cutoff = options.timelineCutoff ? Date.parse(options.timelineCutoff) : null;

  const nodes = galaxy.nodes.filter(node => {
    if (activeTypes.size > 0 && !activeTypes.has(node.type)) return false;
    if (activeLayers.size > 0 && !activeLayers.has(node.layer)) return false;
    if (cutoff && node.raw.last_seen_at && Date.parse(node.raw.last_seen_at) > cutoff) return false;
    if (!query) return true;
    return `${node.label} ${node.type} ${node.layer} ${node.raw.content || ""}`.toLowerCase().includes(query);
  });

  const nodeIds = new Set(nodes.map(node => node.id));
  const links = galaxy.links.filter(link =>
    link.weight >= minWeight &&
    nodeIds.has(String(link.source.id || link.source)) &&
    nodeIds.has(String(link.target.id || link.target))
  );

  return { nodes, links, metadata: galaxy.metadata };
}

export function buildFocusGalaxy(galaxy, options = {}) {
  const maxNodes = Number(options.maxNodes || 900);
  const seedCount = Number(options.seedCount || 36);
  const firstRingLimit = Number(options.firstRingLimit || Math.floor(maxNodes * 0.62));
  const focusNodeId = options.focusNodeId ? String(options.focusNodeId) : null;
  const byId = new Map(galaxy.nodes.map(node => [node.id, node]));
  const adjacency = buildAdjacency(galaxy.links);

  const seeds = focusNodeId && byId.has(focusNodeId)
    ? [byId.get(focusNodeId)]
    : galaxy.nodes
      .filter(node => node.layer === "core" || node.layer === "active" || node.type === "project")
      .sort((a, b) => nodeScore(b) - nodeScore(a))
      .slice(0, seedCount);

  if (galaxy.nodes.length <= maxNodes || seeds.length === 0) {
    return withFocusRings(galaxy, new Map(seeds.map(node => [node.id, 0])));
  }

  const keep = new Map(seeds.map(node => [node.id, 0]));
  const firstRingCandidates = rankedNeighbors(seeds, adjacency, byId, keep);
  for (const node of firstRingCandidates) {
    if (keep.size >= firstRingLimit) break;
    keep.set(node.id, 1);
  }

  const firstRingNodes = [...keep]
    .filter(([, ring]) => ring <= 1)
    .map(([id]) => byId.get(id))
    .filter(Boolean);
  const secondRingCandidates = rankedNeighbors(firstRingNodes, adjacency, byId, keep);
  for (const node of secondRingCandidates) {
    if (keep.size >= maxNodes) break;
    keep.set(node.id, 2);
  }

  const nodes = galaxy.nodes
    .filter(node => keep.has(node.id))
    .map(node => positionForFocusRing(node, keep.get(node.id)));
  const nodeIds = new Set(nodes.map(node => node.id));
  const links = galaxy.links.filter(link =>
    nodeIds.has(String(link.source.id || link.source)) &&
    nodeIds.has(String(link.target.id || link.target))
  );

  return { nodes, links, metadata: galaxy.metadata };
}

export function buildGalaxy2DLayout(galaxy, options = {}) {
  const focused = buildFocusGalaxy(galaxy, {
    maxNodes: Number(options.maxNodes || 850),
    seedCount: Number(options.seedCount || 42),
    firstRingLimit: Number(options.firstRingLimit || 520),
    focusNodeId: options.focusNodeId,
  });
  const nodes = focused.nodes.map((node, index) => {
    const angle = hashAngle(`${node.id}:2d`);
    const spiral = 1 + ((hashNumber(`${node.id}:spiral`) % 100) / 420);
    const baseRadius = layerOrbit[node.layer] || layerOrbit.external;
    const ringOffset = ((index % 11) - 5) * 7;
    const radius = baseRadius * spiral + ringOffset;
    return {
      ...node,
      x: Math.cos(angle) * radius,
      y: Math.sin(angle) * radius * 0.58,
      z: 0,
      renderRadius: Math.max(4, Math.sqrt(node.val) * 1.7),
      labelPriority: nodeScore(node),
    };
  });
  return { nodes, links: focused.links, metadata: focused.metadata };
}

export function buildClusterGalaxy2DLayout(galaxy, options = {}) {
  const focused = buildFocusGalaxy(galaxy, {
    maxNodes: Number(options.maxNodes || 850),
    seedCount: Number(options.seedCount || 42),
    firstRingLimit: Number(options.firstRingLimit || 520),
    focusNodeId: options.focusNodeId,
  });
  const nodes = focused.nodes.map((node, index) => {
    const clusterKey = clusterKeyForType(node.type);
    const center = clusterCenters[clusterKey] || clusterCenters.external;
    const localRadius = (layerOrbit[node.layer] || layerOrbit.external) * 0.42;
    const angle = hashAngle(`${node.id}:cluster:${clusterKey}`);
    const jitter = ((hashNumber(`${node.id}:cluster-jitter`) % 100) / 100) * 38;
    const radius = localRadius + jitter + ((index % 7) * 4);
    const x = center.x + Math.cos(angle) * radius;
    const y = center.y + Math.sin(angle) * radius * 0.72;
    return {
      ...node,
      clusterKey,
      homeX: x,
      homeY: y,
      x,
      y,
      z: 0,
      renderRadius: Math.max(4, Math.sqrt(node.val) * 1.7),
      labelPriority: nodeScore(node),
    };
  });
  const pruned = pruneGalaxyLinks({ nodes, links: focused.links, metadata: focused.metadata }, {
    perNodeLimit: Number(options.perNodeLimit || 4),
  });
  return { nodes, links: pruned.links, metadata: focused.metadata };
}

export function buildGalacticOrbital2DLayout(galaxy, options = {}) {
  const focused = buildFocusGalaxy(galaxy, {
    maxNodes: Number(options.maxNodes || 850),
    seedCount: Number(options.seedCount || 48),
    firstRingLimit: Number(options.firstRingLimit || 540),
    focusNodeId: options.focusNodeId,
  });
  const starIds = starNodeIdsBySystem(focused.nodes);
  const nodes = focused.nodes.map((node, index) => {
    const memorySystem = memorySystemForNode(node);
    const systemCenter = galacticSystemCenters[memorySystem] || galacticSystemCenters.knowledge;
    const starId = starIds.get(memorySystem);
    const orbitalRole = memorySystem === "router"
      ? "galactic-core"
      : node.id === starId
        ? "star"
        : node.layer === "episode" || memorySystem === "source"
          ? "moon"
          : "planet";
    const angle = hashAngle(`${node.id}:orbital:${memorySystem}`);
    const ringBase = orbitalRole === "star"
      ? 0
      : orbitalRole === "moon"
        ? systemCenter.orbitRadius * 1.42
        : systemCenter.orbitRadius;
    const jitter = orbitalRole === "star" ? 0 : ((hashNumber(`${node.id}:orbital-jitter`) % 100) / 100) * 34;
    const radius = ringBase + jitter + ((index % 5) * 5);
    const flatten = memorySystem === "router" ? 1 : 0.64;
    const x = memorySystem === "router"
      ? Math.cos(angle) * Math.min(48, radius + 34)
      : systemCenter.x + Math.cos(angle) * radius;
    const y = memorySystem === "router"
      ? Math.sin(angle) * Math.min(38, radius + 26)
      : systemCenter.y + Math.sin(angle) * radius * flatten;
    return {
      ...node,
      clusterKey: memorySystem,
      memorySystem,
      orbitalRole,
      systemCenter,
      homeX: x,
      homeY: y,
      x,
      y,
      z: 0,
      renderRadius: priorityRadiusForNode(node),
      labelPriority: nodeScore(node) + (orbitalRole === "star" || orbitalRole === "galactic-core" ? 12 : 0),
    };
  });
  const pruned = pruneGalaxyLinks({ nodes, links: focused.links, metadata: focused.metadata }, {
    perNodeLimit: Number(options.perNodeLimit || 4),
  });
  return {
    nodes,
    links: pruned.links,
    metadata: focused.metadata,
    systems: Object.entries(galacticSystemCenters).map(([key, value]) => ({ key, ...value })),
  };
}

export function labelAnchorForNode(node) {
  const center = node.systemCenter || { x: 0, y: 0 };
  let dx = node.x - center.x;
  let dy = node.y - center.y;
  let distance = Math.hypot(dx, dy);
  if (distance < 1) {
    const angle = hashAngle(`${node.id}:label-anchor`);
    dx = Math.cos(angle);
    dy = Math.sin(angle);
    distance = 1;
  }
  const offset = Number(node.renderRadius || 8) + (node.orbitalRole === "star" || node.orbitalRole === "galactic-core" ? 20 : 14);
  const x = node.x + (dx / distance) * offset;
  const y = node.y + (dy / distance) * offset;
  return {
    x,
    y,
    align: x >= node.x ? "left" : "right",
  };
}

export function springBackTarget(node, options = {}) {
  const retainRatio = Number(options.retainRatio ?? 0.2);
  const homeX = Number(node.homeX ?? node.x ?? 0);
  const homeY = Number(node.homeY ?? node.y ?? 0);
  const x = Number(node.x ?? homeX);
  const y = Number(node.y ?? homeY);
  return {
    x: Math.round(homeX + (x - homeX) * retainRatio),
    y: Math.round(homeY + (y - homeY) * retainRatio),
  };
}

export function buildSphereGalaxyLayout(galaxy, options = {}) {
  const focused = buildFocusGalaxy(galaxy, {
    maxNodes: Number(options.maxNodes || 650),
    seedCount: Number(options.seedCount || 36),
    firstRingLimit: Number(options.firstRingLimit || 380),
    focusNodeId: options.focusNodeId,
  });
  const nodes = focused.nodes.map((node, index) => {
    const radius = sphereShell[node.layer] || sphereShell.external;
    const theta = hashAngle(`${node.id}:theta`);
    const phiSeed = ((hashNumber(`${node.id}:phi`) % 1000) / 1000);
    const phi = Math.acos(1 - 2 * phiSeed);
    const shellJitter = ((index % 7) - 3) * 5;
    const r = radius + shellJitter;
    return {
      ...node,
      theta,
      phi,
      x: r * Math.sin(phi) * Math.cos(theta),
      y: r * Math.cos(phi),
      z: r * Math.sin(phi) * Math.sin(theta),
      renderRadius: Math.max(3.5, Math.sqrt(node.val) * 1.45),
      labelPriority: nodeScore(node),
    };
  });
  return { nodes, links: focused.links, metadata: focused.metadata };
}

export function buildExpandedGalaxy(sourceGalaxy, baseGalaxy, expandedNodeIds, options = {}) {
  const neighborLimit = Number(options.neighborLimit || 120);
  const byId = new Map(sourceGalaxy.nodes.map(node => [node.id, node]));
  const baseIds = new Set(baseGalaxy.nodes.map(node => node.id));
  const keep = new Set(baseIds);
  const addedFrom = new Map();
  const adjacency = buildAdjacency(sourceGalaxy.links);

  for (const id of expandedNodeIds || []) {
    const nodeId = String(id);
    if (!byId.has(nodeId)) continue;
    keep.add(nodeId);
    const neighbors = (adjacency.get(nodeId) || [])
      .filter(edge => byId.has(edge.id))
      .sort((a, b) => (b.weight + nodeScore(byId.get(b.id))) - (a.weight + nodeScore(byId.get(a.id))))
      .slice(0, neighborLimit);
    for (const edge of neighbors) {
      keep.add(edge.id);
      if (!baseIds.has(edge.id) && !addedFrom.has(edge.id)) {
        addedFrom.set(edge.id, nodeId);
      }
    }
  }

  const baseById = new Map(baseGalaxy.nodes.map(node => [node.id, node]));
  const nodes = sourceGalaxy.nodes
    .filter(node => keep.has(node.id))
    .map(node => {
      const baseNode = baseById.get(node.id);
      if (baseNode) return baseNode;
      return positionExpandedNode(node, baseById.get(addedFrom.get(node.id)) || byId.get(addedFrom.get(node.id)));
    });
  const nodeIds = new Set(nodes.map(node => node.id));
  const links = sourceGalaxy.links.filter(link =>
    nodeIds.has(String(link.source.id || link.source)) &&
    nodeIds.has(String(link.target.id || link.target))
  ).map(link => {
    const source = String(link.source.id || link.source);
    const target = String(link.target.id || link.target);
    const expansionParentId = expandedNodeIds.has(source) && addedFrom.get(target) === source
      ? source
      : expandedNodeIds.has(target) && addedFrom.get(source) === target
        ? target
        : null;
    return expansionParentId ? { ...link, expansionParentId } : link;
  });

  return { nodes, links, metadata: sourceGalaxy.metadata };
}

export function buildEditIntent(action, payload) {
  return {
    action,
    payload,
    created_at: new Date().toISOString(),
    source: "memory-galaxy-viewer",
  };
}

export function memorySystemForNode(node) {
  const text = semanticText(node);
  if (/\b(router|routing|route|dispatch|orchestrat)/.test(text)) return "router";
  if (node.type === "rule" || /\b(rule|policy|must|never|required|guardrail)\b/.test(text)) return "rule";
  if (/\b(persona|personality|identity|tone|style|voice|character)\b/.test(text)) return "persona";
  if (/\b(skill|capability|trigger|workflow|procedure)\b/.test(text) || node.type === "capability") return "skill";
  if (/\b(harness|eval|evaluation|pytest|test runner|smoke test|verification|playwright|benchmark|browser automation|workflow runner)\b/.test(text)) return "harness";
  if (/\b(preference|prefers|user wants|style preference|interaction preference)\b/.test(text)) return "preference";
  if (node.type === "project") return "project";
  if (["event", "episode", "session", "observation"].includes(node.type) || node.layer === "episode") return "event";
  if (/\b(source|provenance|evidence|citation|origin)\b/.test(text) || node.layer === "external") return "source";
  return "knowledge";
}

export function priorityRadiusForNode(node) {
  const system = memorySystemForNode(node);
  const baseDiameter = memorySystemPriority[system] || memorySystemPriority.knowledge;
  const importance = Number(node.raw?.importance || 0);
  const activity = Number(node.raw?.activity || 0);
  const mentions = Math.log1p(Number(node.raw?.mention_count || 0));
  const diameter = baseDiameter + importance * 3 + activity * 4 + mentions * 1.4;
  return Math.max(6, Math.min(34, diameter / 2));
}

export function pruneGalaxyLinks(galaxy, options = {}) {
  const perNodeLimit = Number(options.perNodeLimit || 4);
  const kept = new Map();
  const counts = new Map();
  const sorted = [...galaxy.links].sort((a, b) => b.weight - a.weight);
  for (const link of sorted) {
    const source = String(link.source.id || link.source);
    const target = String(link.target.id || link.target);
    const sourceCount = counts.get(source) || 0;
    const targetCount = counts.get(target) || 0;
    if (sourceCount >= perNodeLimit || targetCount >= perNodeLimit) continue;
    kept.set(link.raw?.id || `${source}->${target}:${link.relation}`, link);
    counts.set(source, sourceCount + 1);
    counts.set(target, targetCount + 1);
  }
  return { nodes: galaxy.nodes, links: [...kept.values()], metadata: galaxy.metadata };
}

export function visibleLinksForSelection(links, options = {}) {
  const selectedNodeId = options.selectedNodeId ? String(options.selectedNodeId) : null;
  const hoveredNodeId = options.hoveredNodeId ? String(options.hoveredNodeId) : null;
  if (!selectedNodeId && !hoveredNodeId) {
    return pruneGalaxyLinks({ nodes: [], links, metadata: {} }, { perNodeLimit: Number(options.perNodeLimit || 4) }).links;
  }
  const focusIds = new Set([selectedNodeId, hoveredNodeId].filter(Boolean));
  const quiet = pruneGalaxyLinks({ nodes: [], links, metadata: {} }, { perNodeLimit: Number(options.perNodeLimit || 3) }).links;
  const focused = links.filter(link => {
    const source = String(link.source.id || link.source);
    const target = String(link.target.id || link.target);
    return focusIds.has(source) || focusIds.has(target);
  });
  const byKey = new Map();
  for (const link of [...quiet, ...focused]) {
    const source = String(link.source.id || link.source);
    const target = String(link.target.id || link.target);
    byKey.set(link.raw?.id || `${source}->${target}:${link.relation}`, link);
  }
  return [...byKey.values()];
}

export function selectVisibleLabels(nodes, options = {}) {
  const zoom = Number(options.zoom || 1);
  const selectedNodeId = options.selectedNodeId ? String(options.selectedNodeId) : null;
  const hoveredNodeId = options.hoveredNodeId ? String(options.hoveredNodeId) : null;
  const maxLabels = zoom < 0.8 ? 28 : zoom < 1.4 ? 72 : 160;
  return [...nodes]
    .filter(node =>
      node.id === selectedNodeId ||
      node.id === hoveredNodeId ||
      node.layer === "core" ||
      node.layer === "active" ||
      (zoom >= 1.55 && Number(node.raw.importance || 0) >= 0.7) ||
      (zoom >= 2.2 && Number(node.raw.mention_count || 0) >= 3)
    )
    .sort((a, b) => {
      const aPinned = a.id === selectedNodeId || a.id === hoveredNodeId ? 1000 : 0;
      const bPinned = b.id === selectedNodeId || b.id === hoveredNodeId ? 1000 : 0;
      return (bPinned + nodeScore(b)) - (aPinned + nodeScore(a));
    })
    .slice(0, maxLabels);
}

export function buildGalaxyCacheKey(graph, view) {
  const metadata = graph.metadata || {};
  const cache = metadata.cache || {};
  const identity = metadata.graph_identity || {};
  return [
    cache.layout_namespace || "memory-galaxy",
    view || "unknown",
    cache.default_root || "D:\\TotalAgentMemory\\memory-galaxy-cache",
    identity.node_ids_hash || "nodes",
    identity.edge_ids_hash || "edges",
  ].join(":");
}

export function groupNeighborRelations(galaxy, nodeId) {
  const targetId = String(nodeId);
  const byId = new Map(galaxy.nodes.map(node => [node.id, node]));
  const groups = {};
  for (const link of galaxy.links) {
    const source = String(link.source.id || link.source);
    const target = String(link.target.id || link.target);
    if (source !== targetId && target !== targetId) continue;
    const neighborId = source === targetId ? target : source;
    const neighbor = byId.get(neighborId);
    if (!neighbor) continue;
    const relation = link.relation || "related";
    if (!groups[relation]) groups[relation] = [];
    groups[relation].push({ neighbor, link });
  }
  for (const relation of Object.keys(groups)) {
    groups[relation].sort((a, b) => b.link.weight - a.link.weight);
  }
  return groups;
}

function semanticText(node) {
  return [
    node.id,
    node.label,
    node.raw?.label,
    node.raw?.name,
    node.type,
    node.layer,
    node.raw?.content,
    node.raw?.source,
    node.raw?.project,
    ...(node.raw?.knowledge || []).map(item => `${item.type || ""} ${item.project || ""} ${item.summary || ""}`),
  ].join(" ").toLowerCase();
}

function starNodeIdsBySystem(nodes) {
  const best = new Map();
  for (const node of nodes) {
    const system = memorySystemForNode(node);
    const current = best.get(system);
    if (!current || nodeScore(node) > nodeScore(current)) best.set(system, node);
  }
  return new Map([...best].map(([system, node]) => [system, node.id]));
}

function buildAdjacency(links) {
  const adjacency = new Map();
  for (const link of links) {
    const source = String(link.source.id || link.source);
    const target = String(link.target.id || link.target);
    if (!adjacency.has(source)) adjacency.set(source, []);
    if (!adjacency.has(target)) adjacency.set(target, []);
    adjacency.get(source).push({ id: target, weight: link.weight });
    adjacency.get(target).push({ id: source, weight: link.weight });
  }
  return adjacency;
}

function rankedNeighbors(nodes, adjacency, byId, keep) {
  const candidates = new Map();
  for (const node of nodes) {
    for (const edge of adjacency.get(node.id) || []) {
      if (keep.has(edge.id) || !byId.has(edge.id)) continue;
      const score = edge.weight * 4 + nodeScore(byId.get(edge.id));
      candidates.set(edge.id, Math.max(candidates.get(edge.id) || 0, score));
    }
  }
  return [...candidates]
    .sort((a, b) => b[1] - a[1])
    .map(([id]) => byId.get(id));
}

function withFocusRings(galaxy, rings) {
  return {
    nodes: galaxy.nodes.map(node => positionForFocusRing(node, rings.get(node.id) ?? 2)),
    links: galaxy.links,
    metadata: galaxy.metadata,
  };
}

function positionForFocusRing(node, ring) {
  const angle = hashAngle(node.id);
  const radius = [72, 190, 340][ring] || 430;
  const lift = ring === 0 ? 0 : ((hashNumber(node.id) % 9) - 4) * 12;
  return {
    ...node,
    focusRing: ring,
    val: ring === 0 ? node.val + 4 : node.val,
    x: Math.cos(angle) * radius,
    y: lift,
    z: Math.sin(angle) * radius,
  };
}

function nodeScore(node) {
  const importance = Number(node.raw.importance || 0);
  const activity = Number(node.raw.activity || 0);
  const freshness = Number(node.raw.freshness || 0);
  const mentions = Math.log1p(Number(node.raw.mention_count || 0));
  const layerBoost = { core: 10, active: 7, knowledge: 2, episode: 1, external: 0 }[node.layer] || 0;
  const typeBoost = { project: 4, rule: 3, decision: 3, concept: 1 }[node.type] || 0;
  return layerBoost + typeBoost + importance * 4 + activity * 8 + freshness * 3 + mentions;
}

function hashNumber(value) {
  let hash = 0;
  for (const char of String(value)) {
    hash = ((hash << 5) - hash + char.charCodeAt(0)) | 0;
  }
  return Math.abs(hash);
}

function hashAngle(value) {
  return (hashNumber(value) % 6283) / 1000;
}

function clusterKeyForType(type) {
  if (type === "project") return "project";
  if (type === "concept" || type === "domain") return "concept";
  if (type === "technology" || type === "company") return "technology";
  if (type === "pattern" || type === "rule" || type === "decision") return "pattern";
  if (type === "event" || type === "episode" || type === "session" || type === "observation") return "event";
  return "external";
}

function positionExpandedNode(node, parent) {
  const angle = hashAngle(node.id);
  const radius = 90 + (hashNumber(node.id) % 80);
  const parentX = parent?.x || 0;
  const parentY = parent?.y || 0;
  const parentZ = parent?.z || 0;
  return {
    ...node,
    focusRing: 3,
    x: parentX + Math.cos(angle) * radius,
    y: parentY + ((hashNumber(node.id) % 9) - 4) * 18,
    z: parentZ + Math.sin(angle) * radius,
  };
}

function inferLayer(data) {
  if (data.type === "rule" || data.type === "decision" || Number(data.importance || 0) >= 1.4) return "core";
  if (Number(data.mention_count || 0) >= 10 || Number(data.importance || 0) >= 0.9) return "active";
  if (["concept", "entity", "technology", "project"].includes(data.type)) return "knowledge";
  if (["episode", "session", "observation"].includes(data.type)) return "episode";
  return "external";
}



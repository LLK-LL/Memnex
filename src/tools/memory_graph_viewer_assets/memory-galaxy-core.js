const layerOrbit = {
  core: 70,
  active: 130,
  knowledge: 210,
  episode: 290,
  external: 370,
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
    return {
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

export function buildEditIntent(action, payload) {
  return {
    action,
    payload,
    created_at: new Date().toISOString(),
    source: "memory-galaxy-viewer",
  };
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

function inferLayer(data) {
  if (data.type === "rule" || data.type === "decision" || Number(data.importance || 0) >= 1.4) return "core";
  if (Number(data.mention_count || 0) >= 10 || Number(data.importance || 0) >= 0.9) return "active";
  if (["concept", "entity", "technology", "project"].includes(data.type)) return "knowledge";
  if (["episode", "session", "observation"].includes(data.type)) return "episode";
  return "external";
}

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

export function buildEditIntent(action, payload) {
  return {
    action,
    payload,
    created_at: new Date().toISOString(),
    source: "memory-galaxy-viewer",
  };
}

function inferLayer(data) {
  if (data.type === "rule" || data.type === "decision" || Number(data.importance || 0) >= 1.4) return "core";
  if (Number(data.mention_count || 0) >= 10 || Number(data.importance || 0) >= 0.9) return "active";
  if (["concept", "entity", "technology", "project"].includes(data.type)) return "knowledge";
  if (["episode", "session", "observation"].includes(data.type)) return "episode";
  return "external";
}

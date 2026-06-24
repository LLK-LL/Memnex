import {
  memorySystemForData,
  orbitRoleForData,
  priorityRadiusForData,
  systemColor,
  systemLayerForKey,
} from "./memory-galaxy-systems.js";

const systemLabels = {
  router: "Router",
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
};

const layerRadii = {
  control: 230,
  execution: 360,
  context: 500,
  evidence: 640,
  archive: 760,
};

const layerOrder = ["control", "execution", "context", "evidence", "archive"];
const systemOrder = ["router", "rule", "persona", "skill", "harness", "preference", "project", "knowledge", "event", "source", "archive"];

export function buildGalaxyOverviewLayout(galaxy, options = {}) {
  const nodeScale = Number(options.nodeScale || 0.48);
  const nodes = cloneGraphNodes(galaxy);
  const links = cloneLinks(galaxy.links || []);
  const grouped = groupBySystem(nodes);
  if (!grouped.has("router")) grouped.set("router", []);

  const systems = buildSystemDescriptors(grouped, nodeScale);
  const systemByKey = new Map(systems.map(system => [system.key, system]));
  const outputNodes = [];

  for (const system of systems) {
    if (system.key === "router") {
      const routerNode = grouped.get("router")?.[0] || syntheticNode("system:router", "Router", "router", nodeScale);
      outputNodes.push(placeNode(routerNode, system.x, system.y, {
        memorySystem: "router",
        orbitRole: "core",
        orbitalRole: "galactic-core",
        renderRadius: Math.max(18, priorityRadiusForData(routerNode.raw || routerNode, { scale: nodeScale })),
      }));
      continue;
    }

    const members = grouped.get(system.key) || [];
    const star = syntheticNode(`system:${system.key}`, systemLabels[system.key] || system.key, system.key, nodeScale);
    outputNodes.push(placeNode(star, system.x, system.y, {
      memorySystem: system.key,
      orbitRole: "star",
      orbitalRole: "star",
      renderRadius: Math.max(10, priorityRadiusForData(star.raw || star, { scale: nodeScale })),
    }));

    const bodies = overviewSummaryNodes(members).sort(compareNodePriority);
    const byRole = splitByRole(bodies);
    const roleSpecs = [
      ["planet", byRole.planet, 34],
      ["moon", byRole.moon, 58],
      ["evidence", byRole.evidence, 84],
    ];
    system.miniOrbits = [];
    for (const [role, roleNodes, baseRadius] of roleSpecs) {
      const tracks = splitTracks(roleNodes, baseRadius * Math.max(0.82, nodeScale / 0.48), 26, nodeScale);
      if (tracks.length === 0) system.miniOrbits.push({ kind: role, radius: baseRadius * Math.max(0.82, nodeScale / 0.48) });
      else system.miniOrbits.push(...tracks.map(track => ({ kind: role, radius: track.radius })));
      for (const track of tracks) {
        outputNodes.push(...placeOrbit(track.nodes, {
          centerX: system.x,
          centerY: system.y,
          radiusX: track.radius,
          radiusY: track.radius * 0.62,
          startAngle: roleStartAngle(role),
          memorySystem: system.key,
          orbitRole: role,
          orbitalRole: role,
          nodeScale,
        }));
      }
    }
  }

  return {
    view: "galaxy",
    nodes: resolveOverlaps(outputNodes),
    links,
    systems,
    orbits: buildGalacticOrbits(systems),
    bounds: boundsFor(outputNodes, systems),
  };
}

export function buildSolarSystemLayout(galaxy, systemKey, options = {}) {
  const nodeScale = Number(options.nodeScale || 0.48);
  const nodes = cloneGraphNodes(galaxy);
  const localIds = new Set(nodes.filter(node => node.memorySystem === systemKey).map(node => node.id));
  const neighborIds = oneHopNeighborIds(galaxy.links || [], localIds);
  const localNodes = nodes
    .filter(node => localIds.has(node.id) || neighborIds.has(node.id))
    .sort(compareNodePriority);
  const center = syntheticNode(`system:${systemKey}`, systemLabels[systemKey] || systemKey, systemKey, nodeScale);
  const outputNodes = [
    placeNode(center, 0, 0, {
      memorySystem: systemKey,
      orbitRole: "star",
      orbitalRole: "central-star",
      renderRadius: Math.max(22, priorityRadiusForData(center.raw || center, { scale: nodeScale })),
    }),
  ];

  const categoryNodes = buildCategoryNodes(systemKey, localNodes, nodeScale);
  const buckets = splitByRole(localNodes);
  const orbitGroups = [
    ["category", categoryNodes, 110],
    ["planet", buckets.planet, 210],
    ["moon", buckets.moon, 330],
    ["evidence", buckets.evidence, 470],
  ];
  const orbits = [];
  for (const [kind, groupNodes, radius] of orbitGroups) {
    const tracks = splitTracks(groupNodes, radius, 70, nodeScale);
    if (tracks.length === 0) orbits.push({ kind, radius });
    for (const track of tracks) {
      orbits.push({ kind, radius: track.radius });
      outputNodes.push(...placeOrbit(track.nodes, {
        centerX: 0,
        centerY: 0,
        radiusX: track.radius,
        radiusY: track.radius * 0.58,
        startAngle: roleStartAngle(kind),
        memorySystem: systemKey,
        orbitRole: kind === "category" ? "category" : kind,
        orbitalRole: kind,
        nodeScale,
      }));
    }
  }
  const satelliteSystems = buildSatelliteSystems(outputNodes, nodeScale);

  return {
    view: "solar",
    systemKey,
    nodes: resolveOverlaps([...outputNodes, ...satelliteSystems.flatMap(system => system.nodes)]),
    links: cloneLinks(galaxy.links || []),
    systems: [],
    orbits,
    satelliteSystems,
    bounds: boundsFor(outputNodes, [], orbits),
  };
}

export function buildPlanetSatelliteLayout(galaxy, systemKey, planetId, options = {}) {
  const nodeScale = Number(options.nodeScale || 0.5);
  const nodes = cloneGraphNodes(galaxy);
  const source = nodes.find(node => node.id === planetId) || nodes.find(node => node.memorySystem === systemKey) || syntheticNode(planetId || `planet:${systemKey}`, planetId || systemKey, systemKey, nodeScale);
  const directIds = oneHopNeighborIds(galaxy.links || [], new Set([source.id]));
  const derivedIds = oneHopNeighborIds(galaxy.links || [], directIds);
  derivedIds.delete(source.id);
  for (const id of directIds) derivedIds.delete(id);

  const direct = nodes.filter(node => directIds.has(node.id) && node.memorySystem === systemKey).sort(compareNodePriority);
  const derived = nodes.filter(node => derivedIds.has(node.id) && node.memorySystem === systemKey).sort(compareNodePriority);
  const evidence = nodes.filter(node => (directIds.has(node.id) || derivedIds.has(node.id)) && ["event", "source"].includes(node.memorySystem)).sort(compareNodePriority);
  const external = nodes.filter(node => (directIds.has(node.id) || derivedIds.has(node.id)) && node.memorySystem !== systemKey && !["event", "source"].includes(node.memorySystem)).sort(compareNodePriority);

  const outputNodes = [
    placeNode(source, 0, 0, {
      memorySystem: systemKey,
      orbitRole: "planet",
      orbitalRole: "central-planet",
      renderRadius: Math.max(18, priorityRadiusForData(source.raw || source, { scale: nodeScale })),
    }),
  ];
  const orbitGroups = [
    ["direct-moon", direct, 120],
    ["derived-moon", derived, 230],
    ["evidence", evidence, 340],
    ["external", external, 450],
  ];
  const orbits = [];
  for (const [kind, groupNodes, radius] of orbitGroups) {
    const fallbackNodes = kind === "direct-moon" && groupNodes.length === 0 ? nodes.filter(node => node.memorySystem === systemKey && node.id !== source.id).slice(0, 3) : groupNodes;
    const tracks = splitTracks(fallbackNodes, radius, 64, nodeScale);
    if (tracks.length === 0) orbits.push({ kind, radius });
    for (const track of tracks) {
      orbits.push({ kind, radius: track.radius });
      outputNodes.push(...placeOrbit(track.nodes, {
        centerX: 0,
        centerY: 0,
        radiusX: track.radius,
        radiusY: track.radius * 0.58,
        startAngle: roleStartAngle(kind),
        memorySystem: systemKey,
        orbitRole: kind,
        orbitalRole: kind,
        nodeScale,
      }));
    }
  }

  return {
    view: "planet",
    systemKey,
    planetId: source.id,
    nodes: resolveOverlaps(outputNodes),
    links: cloneLinks(galaxy.links || []),
    systems: [],
    orbits,
    bounds: boundsFor(outputNodes, [], orbits),
  };
}

export function buildCometOverlayLayout(galaxyLayout, comets = []) {
  const systems = new Map((galaxyLayout.systems || []).map(system => [system.key, system]));
  const activeComets = comets.slice(0, 3).map((comet, index) => {
    const influences = (comet.influenced_systems || [])
      .map(item => {
        const system = systems.get(item.system);
        if (!system) return null;
        return {
          system: item.system,
          weight: Number(item.weight || 0),
          x: system.x,
          y: system.y,
          radius: system.radius,
        };
      })
      .filter(Boolean);
    const headAnchor = influences[0] || { x: 120 + index * 40, y: -90 - index * 30, radius: 80 };
    const angle = -Math.PI / 3 + index * 0.82;
    const minDistance = Number(headAnchor.radius || 80) + 72 + index * 26;
    const head = {
      x: headAnchor.x + Math.cos(angle) * minDistance,
      y: headAnchor.y + Math.sin(angle) * minDistance,
    };
    const trajectory = (comet.trajectory || []).map((systemKey, step) => {
      const system = systems.get(systemKey);
      return system ? { system: systemKey, x: system.x, y: system.y, step } : null;
    }).filter(Boolean);
    const tail = trajectory.length
      ? trajectory.map((point, step) => ({
        x: head.x + (point.x - head.x) * (0.25 + step * 0.12),
        y: head.y + (point.y - head.y) * (0.25 + step * 0.12),
        alpha: Math.max(0.18, 0.78 - step * 0.14),
      }))
      : influences.map((item, step) => ({
        x: head.x + (item.x - head.x) * (0.2 + step * 0.16),
        y: head.y + (item.y - head.y) * (0.2 + step * 0.16),
        alpha: Math.max(0.18, 0.72 - step * 0.14),
      }));
    return {
      id: comet.id || `comet:${index}`,
      label: comet.label || "Active Context",
      cometType: comet.comet_type || "active_task",
      head,
      hitRadius: 24,
      tail,
      trajectory,
      influences,
    };
  });
  return { comets: activeComets };
}

function cloneGraphNodes(galaxy) {
  return (galaxy.nodes || []).map(node => {
    const raw = node.raw || node;
    const memorySystem = memorySystemForData(raw);
    return {
      ...node,
      raw,
      id: String(node.id || raw.id),
      label: String(node.label || raw.label || raw.name || raw.id || "Memory"),
      memorySystem,
      orbitRole: orbitRoleForData(raw),
      color: systemColor(memorySystem),
      renderRadius: priorityRadiusForData(raw, { scale: 0.48 }),
    };
  });
}

function cloneLinks(links) {
  return links.map(link => ({ ...link }));
}

function groupBySystem(nodes) {
  const grouped = new Map();
  for (const node of nodes) {
    if (!grouped.has(node.memorySystem)) grouped.set(node.memorySystem, []);
    grouped.get(node.memorySystem).push(node);
  }
  for (const bucket of grouped.values()) bucket.sort(compareNodePriority);
  return grouped;
}

function buildSystemDescriptors(grouped, nodeScale) {
  const byLayer = new Map(layerOrder.map(layer => [layer, []]));
  for (const key of systemOrder) {
    if (key === "router") continue;
    if (!grouped.has(key)) continue;
    const layer = systemLayerForKey(key);
    if (!byLayer.has(layer)) byLayer.set(layer, []);
    byLayer.get(layer).push(key);
  }
  const systems = [{
    key: "router",
    label: "Router",
    layer: "core",
    x: 0,
    y: 0,
    radius: 72,
    miniOrbits: [],
  }];
  layerOrder.forEach((layer, layerIndex) => {
    const keys = byLayer.get(layer) || [];
    const radius = layerRadii[layer] || 760;
    const angleOffset = Math.PI / (layerIndex + 4);
    keys.forEach((key, index) => {
      const angle = angleOffset + (index * Math.PI * 2) / Math.max(1, keys.length);
      const miniRadius = 98 * Math.max(0.82, nodeScale / 0.48);
      systems.push({
        key,
        label: systemLabels[key] || key,
        layer,
        color: systemColor(key),
        x: Math.cos(angle) * radius,
        y: Math.sin(angle) * radius * 0.58,
        radius: miniRadius,
        miniOrbits: [],
      });
    });
  });
  return systems;
}

function splitByRole(nodes) {
  return nodes.reduce((acc, node) => {
    const role = node.orbitRole || orbitRoleForData(node.raw || node);
    if (role === "planet") acc.planet.push(node);
    else if (role === "evidence") acc.evidence.push(node);
    else acc.moon.push(node);
    return acc;
  }, { planet: [], moon: [], evidence: [] });
}

function overviewSummaryNodes(nodes) {
  const byRole = splitByRole(nodes);
  const selected = [
    ...byRole.planet.slice(0, 4),
    ...byRole.moon.slice(0, 3),
    ...byRole.evidence.slice(0, 2),
  ];
  const seen = new Set();
  return selected.filter(node => {
    if (seen.has(node.id)) return false;
    seen.add(node.id);
    return true;
  });
}

function splitTracks(nodes, baseRadius, step, nodeScale) {
  if (!nodes.length) return [];
  const maxRadius = Math.max(...nodes.map(node => priorityRadiusForData(node.raw || node, { scale: nodeScale })));
  const capacity = Math.max(1, Math.floor((Math.PI * 2 * Math.max(24, baseRadius)) / Math.max(14, maxRadius * 2 + 8)));
  const tracks = [];
  for (let start = 0; start < nodes.length; start += capacity) {
    tracks.push({
      radius: baseRadius + tracks.length * step,
      nodes: nodes.slice(start, start + capacity),
    });
  }
  return tracks;
}

function placeOrbit(nodes, options) {
  const count = Math.max(1, nodes.length);
  return nodes.map((node, index) => {
    const angle = options.startAngle + (index * Math.PI * 2) / count;
    const x = options.centerX + Math.cos(angle) * options.radiusX;
    const y = options.centerY + Math.sin(angle) * options.radiusY;
    return placeNode(node, x, y, {
      memorySystem: options.memorySystem,
      orbitRole: options.orbitRole,
      orbitalRole: options.orbitalRole,
      renderRadius: priorityRadiusForData(node.raw || node, { scale: options.nodeScale }),
      labelAnchor: labelAnchor(x, y, angle),
      orbitCenterX: options.centerX,
      orbitCenterY: options.centerY,
    });
  });
}

function placeNode(node, x, y, overrides = {}) {
  const raw = node.raw || node;
  const memorySystem = overrides.memorySystem || node.memorySystem || memorySystemForData(raw);
  const renderRadius = overrides.renderRadius || priorityRadiusForData(raw, { scale: 0.48 });
  return {
    ...node,
    id: String(node.id || raw.id),
    label: String(node.label || raw.label || raw.name || raw.id || "Memory"),
    raw,
    memorySystem,
    orbitRole: overrides.orbitRole || node.orbitRole || orbitRoleForData(raw),
    orbitalRole: overrides.orbitalRole || node.orbitalRole || orbitRoleForData(raw),
    renderRadius,
    color: node.color || systemColor(memorySystem),
    x,
    y,
    homeX: x,
    homeY: y,
    labelAnchor: overrides.labelAnchor || labelAnchor(x, y, Math.atan2(y, x)),
    animation: {
      orbitCenterX: overrides.orbitCenterX ?? 0,
      orbitCenterY: overrides.orbitCenterY ?? 0,
      orbitRadiusX: Math.abs(x - (overrides.orbitCenterX ?? 0)),
      orbitRadiusY: Math.abs(y - (overrides.orbitCenterY ?? 0)),
      orbitAngle: Math.atan2(y - (overrides.orbitCenterY ?? 0), x - (overrides.orbitCenterX ?? 0)),
      orbitSpeed: overrides.orbitSpeed ?? animationSpeedFor(overrides.orbitalRole || node.orbitalRole),
      spinSpeed: overrides.spinSpeed ?? 0.018,
    },
  };
}

function syntheticNode(id, label, system, nodeScale) {
  const raw = {
    id,
    label,
    type: system === "router" ? "pattern" : "concept",
    content: `${system} synthetic system center`,
    importance: 1.5,
    mention_count: 12,
  };
  return {
    id,
    label,
    raw,
    memorySystem: system,
    orbitRole: "star",
    color: systemColor(system),
    renderRadius: priorityRadiusForData(raw, { scale: nodeScale }),
  };
}

function buildCategoryNodes(systemKey, localNodes, nodeScale) {
  const categories = Array.from(new Set(localNodes
    .map(node => String(node.raw?.type || node.type || "memory"))
    .slice(0, 6)));
  if (categories.length === 0) categories.push(systemKey);
  return categories.map(category => syntheticNode(`category:${systemKey}:${category}`, category, systemKey, nodeScale));
}

function buildSatelliteSystems(outputNodes, nodeScale) {
  const parents = outputNodes
    .filter(node => node.orbitalRole === "planet")
    .slice(0, 4);
  return parents.map((parent, parentIndex) => {
    const radius = 34 + parentIndex * 3;
    const satelliteNodes = Array.from({ length: 3 }, (_, index) => {
      const angle = -Math.PI / 2 + index * Math.PI * 2 / 3 + parentIndex * 0.24;
      const raw = {
        id: `satellite:${parent.id}:${index}`,
        label: index === 0 ? "usage moon" : index === 1 ? "context moon" : "evidence moon",
        type: index === 2 ? "event" : "concept",
        content: `satellite context for ${parent.label}`,
        importance: 0.35,
        mention_count: 2,
      };
      return placeNode({
        id: raw.id,
        label: raw.label,
        raw,
        memorySystem: parent.memorySystem,
        orbitRole: "satellite",
        color: index === 2 ? systemColor("source") : systemColor(parent.memorySystem),
        renderRadius: Math.max(3, priorityRadiusForData(raw, { scale: nodeScale }) * 0.72),
      }, parent.x + Math.cos(angle) * radius, parent.y + Math.sin(angle) * radius * 0.62, {
        memorySystem: parent.memorySystem,
        orbitRole: "satellite",
        orbitalRole: "satellite",
        renderRadius: Math.max(3, priorityRadiusForData(raw, { scale: nodeScale }) * 0.72),
        orbitCenterX: parent.x,
        orbitCenterY: parent.y,
        orbitSpeed: 0.012 + index * 0.002,
        spinSpeed: 0.025,
      });
    });
    return {
      parentId: parent.id,
      x: parent.x,
      y: parent.y,
      radius,
      orbits: [{ kind: "satellite", radius }],
      nodes: satelliteNodes,
    };
  });
}

function oneHopNeighborIds(links, ids) {
  const result = new Set();
  for (const link of links) {
    const source = String(link.source?.id || link.source);
    const target = String(link.target?.id || link.target);
    if (ids.has(source)) result.add(target);
    if (ids.has(target)) result.add(source);
  }
  return result;
}

function buildGalacticOrbits(systems) {
  const seen = new Set();
  const orbits = [];
  for (const system of systems) {
    if (system.layer === "core" || seen.has(system.layer)) continue;
    seen.add(system.layer);
    orbits.push({
      kind: system.layer,
      radius: layerRadii[system.layer] || Math.hypot(system.x, system.y),
    });
  }
  return orbits;
}

function boundsFor(nodes, systems = [], orbits = []) {
  let minX = Infinity;
  let maxX = -Infinity;
  let minY = Infinity;
  let maxY = -Infinity;
  for (const node of nodes) {
    const pad = (node.renderRadius || 4) + 80;
    minX = Math.min(minX, node.x - pad);
    maxX = Math.max(maxX, node.x + pad);
    minY = Math.min(minY, node.y - pad);
    maxY = Math.max(maxY, node.y + pad);
  }
  for (const system of systems) {
    const pad = (system.radius || 0) + 80;
    minX = Math.min(minX, system.x - pad);
    maxX = Math.max(maxX, system.x + pad);
    minY = Math.min(minY, system.y - pad);
    maxY = Math.max(maxY, system.y + pad);
  }
  for (const orbit of orbits) {
    const pad = (orbit.radius || 0) + 80;
    minX = Math.min(minX, -pad);
    maxX = Math.max(maxX, pad);
    minY = Math.min(minY, -pad * 0.62);
    maxY = Math.max(maxY, pad * 0.62);
  }
  if (!Number.isFinite(minX)) return { minX: -100, minY: -100, maxX: 100, maxY: 100, width: 200, height: 200 };
  return {
    minX,
    minY,
    maxX,
    maxY,
    width: maxX - minX,
    height: maxY - minY,
  };
}

function compareNodePriority(a, b) {
  const ar = a.raw || a;
  const br = b.raw || b;
  return scoreNode(br) - scoreNode(ar);
}

function scoreNode(node) {
  return Number(node.importance || 0) * 10
    + Number(node.activity || 0) * 5
    + Math.log1p(Number(node.mention_count || 0)) * 3;
}

function roleStartAngle(role) {
  return {
    category: -Math.PI / 2,
    planet: -Math.PI / 3,
    moon: -Math.PI / 5,
    evidence: Math.PI / 8,
    "direct-moon": -Math.PI / 2,
    "derived-moon": -Math.PI / 4,
    external: Math.PI / 5,
  }[role] || -Math.PI / 2;
}

function animationSpeedFor(role) {
  return {
    "galactic-core": 0,
    "central-star": 0,
    "central-planet": 0,
    star: 0.002,
    category: 0.004,
    planet: 0.006,
    moon: 0.009,
    evidence: 0.007,
    satellite: 0.014,
  }[role] ?? 0.004;
}

function labelAnchor(x, y, angle) {
  const align = Math.cos(angle) < 0 ? "right" : "left";
  return {
    x: x + Math.cos(angle) * 24,
    y: y + Math.sin(angle) * 18,
    align,
  };
}

function resolveOverlaps(nodes) {
  const placed = [];
  for (const node of nodes) {
    let output = { ...node };
    for (let attempt = 0; attempt < 12; attempt += 1) {
      const hit = placed.find(other => Math.hypot(output.x - other.x, output.y - other.y) < Math.min(14, output.renderRadius + other.renderRadius + 2));
      if (!hit) break;
      const angle = Math.atan2(output.y || 1, output.x || 1) + attempt * 0.55;
      output.x += Math.cos(angle) * (6 + attempt);
      output.y += Math.sin(angle) * (6 + attempt);
      output.homeX = output.x;
      output.homeY = output.y;
    }
    placed.push(output);
  }
  return placed;
}

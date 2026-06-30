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
const layoutSystemOrder = ["router", "rule", "persona", "skill", "harness", "preference", "project", "knowledge", "event", "source", "archive"];
export function buildGalaxyOverviewLayout(galaxy, options = {}) {
  const nodeScale = Number(options.nodeScale || 0.48);
  const nodes = cloneGraphNodes(galaxy);
  const links = cloneLinks(galaxy.links || []);
  const agentFrames = placeAgentGalaxies(groupByAgentNamespace(nodes, galaxy.agentGalaxies));
  const outputNodes = [];
  const systems = [];

  for (const frame of agentFrames) {
    const grouped = groupBySystem(frame.nodes);
    if (!grouped.has("router")) grouped.set("router", []);
    const localSystems = buildSystemDescriptors(grouped, nodeScale, frame);
    systems.push(...localSystems);

    const agentCore = syntheticNode(`agent:${frame.namespace}`, frame.label, "router", nodeScale);
    agentCore.raw.memberCount = frame.nodes.length;
    outputNodes.push(placeNode(agentCore, frame.centerX, frame.centerY, {
        memorySystem: "router",
        orbitRole: "core",
        orbitalRole: "agent-core",
        renderRadius: Math.max(54, priorityRadiusForData(agentCore.raw || agentCore, { scale: nodeScale }) * 2.4),
        labelPriority: 1000,
        labelAnchor: { x: frame.centerX, y: frame.centerY - 92, align: "center" },
        agentNamespace: frame.namespace,
        agentLabel: frame.label,
      }));

    for (const system of localSystems) {
      if ((system.baseKey || system.key) === "router") continue;

      const members = grouped.get(system.baseKey || system.key) || [];
      const star = syntheticNode(`system:${frame.namespace}:${system.baseKey || system.key}`, systemLabels[system.baseKey || system.key] || system.key, system.baseKey || system.key, nodeScale);
      star.raw.memberCount = members.length;
      outputNodes.push(placeNode(star, system.x, system.y, {
        memorySystem: system.baseKey || system.key,
        orbitRole: "star",
        orbitalRole: "star",
        renderRadius: Math.max(10, priorityRadiusForData(star.raw || star, { scale: nodeScale })),
        isSystemNode: true,
        systemKey: system.key,
        agentNamespace: frame.namespace,
        agentLabel: frame.label,
      }));

      const bodies = overviewSummaryNodes(members).sort(compareNodePriority);
      const byRole = splitByRole(bodies);
      const roleSpecs = [
        ["planet", byRole.planet, 34],
        ["moon", byRole.moon, 58],
        ["evidence", byRole.evidence, 84],
      ];
      system.miniOrbits = [];
      const miniOrbitAspect = Number(system.orbitAspect || 1);
      for (const [role, roleNodes, baseRadius] of roleSpecs) {
        const tracks = splitTracks(roleNodes, baseRadius * Math.max(0.82, nodeScale / 0.48), 26, nodeScale);
        if (tracks.length === 0) system.miniOrbits.push({ kind: role, radius: baseRadius * Math.max(0.82, nodeScale / 0.48), aspect: miniOrbitAspect });
        else system.miniOrbits.push(...tracks.map(track => ({ kind: role, radius: track.radius, aspect: miniOrbitAspect })));
        for (const track of tracks) {
          outputNodes.push(...placeOrbit(track.nodes, {
            centerX: system.x,
            centerY: system.y,
            radiusX: track.radius,
            radiusY: track.radius * miniOrbitAspect,
            startAngle: roleStartAngle(role),
            memorySystem: system.baseKey || system.key,
            orbitRole: role,
            orbitalRole: role,
            nodeScale,
            orbitSpeed: overviewOrbitSpeedFor(role),
            parentSystemKey: system.key,
          }));
        }
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
  const baseKey = baseSystemKey(systemKey);
  const agentNamespace = agentNamespaceForSystemKey(systemKey, options.agentNamespace);
  const scaleRatio = Math.max(0.58, Math.min(2.15, nodeScale / 0.48));
  const solarElementScale = 2;
  const solarPlanetOrbitScale = 1.5;
  const solarSatelliteOrbitScale = 2;
  const orbitAspect = 0.58;
  const nodes = cloneGraphNodes(galaxy);
  const { nodes: localNodes, links: localLinks } = buildSolarSubgraph(nodes, galaxy.links || [], baseKey, agentNamespace);
  const center = syntheticNode(`system:${systemKey}`, systemLabels[baseKey] || baseKey, baseKey, nodeScale);
  const centralRenderRadius = Math.max(44, priorityRadiusForData(center.raw || center, { scale: nodeScale }) * 1.42) * 3;
  const outputNodes = [
    placeNode(center, 0, 0, {
      memorySystem: baseKey,
      orbitRole: "star",
      orbitalRole: "central-star",
      renderRadius: centralRenderRadius,
      isSolarCenterStar: true,
    }),
  ];
  const planetSystems = buildSolarPlanetSystems(localNodes, localLinks, baseKey);
  const planetNodes = [];
  const satelliteSystems = [];
  const orbits = [];
  const planetTracks = buildSolarPlanetTracks(planetSystems, nodeScale, scaleRatio, centralRenderRadius, solarElementScale, solarPlanetOrbitScale, solarSatelliteOrbitScale);
  for (const [trackIndex, track] of planetTracks.entries()) {
    const trackSystems = track.systems;
    orbits.push({ kind: "planet", radius: track.radius, aspect: orbitAspect });
    const placed = placeOrbit(trackSystems.map(system => ({
      ...system.anchor,
      childCount: system.children.length,
      visibleChildCount: visibleSolarSatelliteCount(system),
      isPlanetSystemNode: system.children.length > 0,
      visualOrbitAspect: orbitAspect,
      plannedFootprintRadius: track.footprints.get(system.anchor.id),
      planetSystemId: system.anchor.id,
      parentPlanetId: system.anchor.id,
      renderRadius: solarPlanetSystemRadius(system, nodeScale, centralRenderRadius, solarElementScale),
    })), {
      centerX: 0,
      centerY: 0,
      radiusX: track.radius,
      radiusY: track.radius * orbitAspect,
      startAngle: roleStartAngle("planet") + trackIndex * 0.41,
      memorySystem: baseKey,
      orbitRole: "planet",
      orbitalRole: "planet",
      nodeScale,
      orbitSpeed: 0.028,
      spinSpeed: 0,
      angleStep: track.angleStep,
    });
    planetNodes.push(...placed);
  }
  outputNodes.push(...planetNodes);

  const placedPlanetById = new Map(planetNodes.map(node => [node.id, node]));
  for (const [systemIndex, system] of planetSystems.entries()) {
    const parent = placedPlanetById.get(system.anchor.id);
    if (!parent || system.children.length === 0) continue;
    const visibleChildren = system.children.slice(0, visibleSolarSatelliteCount(system));
    const satelliteProfile = solarSatelliteProfileFor(system, systemIndex, scaleRatio, solarSatelliteOrbitScale);
    const childTracks = splitTracks(visibleChildren, satelliteProfile.radius, satelliteProfile.step, nodeScale, 4);
    const childOrbits = [];
    const childNodes = [];
    for (const [trackIndex, track] of childTracks.entries()) {
      childOrbits.push({ kind: "satellite", radius: track.radius, aspect: satelliteProfile.aspect });
      childNodes.push(...placeOrbit(track.nodes.map(node => ({
        ...node,
        parentPlanetId: parent.id,
        renderRadius: Math.max(5, priorityRadiusForData(node.raw || node, { scale: nodeScale }) * 0.72 * solarElementScale),
      })), {
        centerX: parent.x,
        centerY: parent.y,
        radiusX: track.radius,
        radiusY: track.radius * satelliteProfile.aspect,
        startAngle: roleStartAngle("satellite") + satelliteProfile.phase + trackIndex * 0.73,
        memorySystem: baseKey,
        orbitRole: "satellite",
        orbitalRole: "satellite",
        nodeScale,
        orbitSpeed: satelliteProfile.orbitSpeed * (1 + trackIndex * 0.16),
        spinSpeed: satelliteProfile.spinSpeed,
        parentNodeId: parent.id,
        parentPlanetId: parent.id,
      }));
    }
    satelliteSystems.push({
      parentId: parent.id,
      x: parent.x,
      y: parent.y,
      radius: childOrbits.at(-1)?.radius || 34,
      aspect: satelliteProfile.aspect,
      color: parent.color || systemColor(baseKey),
      scaleFactor: solarElementScale,
      footprintRadius: parent.plannedFootprintRadius || ((childOrbits.at(-1)?.radius || 34) + Math.max(34, (parent.renderRadius || 12) * 2)),
      orbits: childOrbits,
      nodes: childNodes,
    });
  }
  const visibleNodes = [...outputNodes, ...satelliteSystems.flatMap(system => system.nodes)];
  const visibleIds = new Set(visibleNodes.map(node => String(node.id)));
  const bounds = boundsForSolarSystem(visibleNodes, orbits, satelliteSystems);
  bounds.fitPadding = 420;
  return {
    view: "solar",
    systemKey,
    nodes: visibleNodes,
    links: localLinks.filter(link => {
      const source = String(link.source?.id || link.source);
      const target = String(link.target?.id || link.target);
      return visibleIds.has(source) && visibleIds.has(target);
    }),
    systems: [],
    orbits,
    satelliteSystems,
    bounds,
  };
}

export function buildPlanetSatelliteLayout(galaxy, systemKey, planetId, options = {}) {
  const nodeScale = Number(options.nodeScale || 0.5);
  const baseKey = baseSystemKey(systemKey);
  const agentNamespace = agentNamespaceForSystemKey(systemKey, options.agentNamespace);
  const scaleRatio = Math.max(0.58, Math.min(2.15, nodeScale / 0.48));
  const orbitAspect = 0.58;
  const nodes = cloneGraphNodes(galaxy);
  const source = nodes.find(node => node.id === planetId) || nodes.find(node => node.memorySystem === baseKey && node.agentNamespace === agentNamespace) || syntheticNode(planetId || `planet:${systemKey}`, planetId || systemKey, baseKey, nodeScale);
  const directIds = oneHopNeighborIds(galaxy.links || [], new Set([source.id]));
  const derivedIds = oneHopNeighborIds(galaxy.links || [], directIds);
  derivedIds.delete(source.id);
  for (const id of directIds) derivedIds.delete(id);

  const direct = nodes.filter(node => node.agentNamespace === agentNamespace && directIds.has(node.id) && node.memorySystem === baseKey).sort(compareNodePriority);
  const derived = nodes.filter(node => node.agentNamespace === agentNamespace && derivedIds.has(node.id) && node.memorySystem === baseKey).sort(compareNodePriority);
  const evidence = nodes.filter(node => node.agentNamespace === agentNamespace && (directIds.has(node.id) || derivedIds.has(node.id)) && ["event", "source"].includes(node.memorySystem)).sort(compareNodePriority);
  const external = nodes.filter(node => node.agentNamespace === agentNamespace && (directIds.has(node.id) || derivedIds.has(node.id)) && node.memorySystem !== baseKey && !["event", "source"].includes(node.memorySystem)).sort(compareNodePriority);

  const outputNodes = [
    placeNode(source, 0, 0, {
      memorySystem: baseKey,
      orbitRole: "planet",
      orbitalRole: "central-planet",
      renderRadius: Math.max(24, priorityRadiusForData(source.raw || source, { scale: nodeScale }) * 1.35),
    }),
  ];
  const orbitGroups = [
    ["direct-moon", direct, 120 * scaleRatio],
    ["derived-moon", derived, 230 * scaleRatio],
    ["evidence", evidence, 340 * scaleRatio],
    ["external", external, 450 * scaleRatio],
  ];
  const orbits = [];
  for (const [kind, groupNodes, radius] of orbitGroups) {
    const fallbackNodes = kind === "direct-moon" && groupNodes.length === 0 ? nodes.filter(node => node.agentNamespace === agentNamespace && node.memorySystem === baseKey && node.id !== source.id).slice(0, 3) : groupNodes;
    const tracks = splitTracks(fallbackNodes, radius, 54, nodeScale, 5);
    if (tracks.length === 0) orbits.push({ kind, radius, aspect: orbitAspect });
    for (const [trackIndex, track] of tracks.entries()) {
      orbits.push({ kind, radius: track.radius, aspect: orbitAspect });
      outputNodes.push(...placeOrbit(track.nodes, {
        centerX: 0,
        centerY: 0,
        radiusX: track.radius,
        radiusY: track.radius * orbitAspect,
        startAngle: roleStartAngle(kind) + trackIndex * 0.73,
        memorySystem: baseKey,
        orbitRole: kind,
        orbitalRole: kind,
        nodeScale,
        orbitSpeed: orbitSpeedForPlanetRing(kind),
      }));
    }
  }

  const planetBounds = boundsFor(outputNodes, [], orbits.map(orbit => ({ ...orbit, aspect: orbitAspect })));
  planetBounds.fitPadding = 280;

  return {
    view: "planet",
    systemKey,
    planetId: source.id,
    nodes: outputNodes,
    links: cloneLinks(galaxy.links || []).filter(link => {
      const visibleIds = new Set(outputNodes.map(node => String(node.id)));
      const sourceId = String(link.source?.id || link.source);
      const targetId = String(link.target?.id || link.target);
      return visibleIds.has(sourceId) && visibleIds.has(targetId);
    }),
    systems: [],
    orbits: orbits.map(orbit => ({ ...orbit, aspect: orbitAspect })),
    bounds: planetBounds,
  };
}

export function buildCometOverlayLayout(galaxyLayout, comets = []) {
  const systems = new Map((galaxyLayout.systems || []).map(system => [system.key, system]));
  for (const system of galaxyLayout.systems || []) {
    if (system.baseKey && !systems.has(system.baseKey)) systems.set(system.baseKey, system);
  }
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
          color: system.color || systemColor(item.system),
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
      hitRadius: 34,
      tail,
      path: buildCometPath(head, trajectory, influences, index),
      trailHistory: tail.map(point => ({ x: point.x, y: point.y, alpha: point.alpha })),
      trajectory,
      influences,
      animation: {
        pathProgress: 0,
        pathSpeed: 1.4 + index * 0.15,
      },
    };
  });
  return { comets: activeComets };
}

function buildCometPath(head, trajectory, influences, index) {
  const anchors = [head, ...(trajectory.length ? trajectory : influences)].map(point => ({ x: point.x, y: point.y }));
  if (anchors.length <= 1) return anchors;
  const path = [anchors[0]];
  for (let i = 0; i < anchors.length - 1; i += 1) {
    const start = anchors[i];
    const end = anchors[i + 1];
    const dx = end.x - start.x;
    const dy = end.y - start.y;
    const distance = Math.hypot(dx, dy) || 1;
    const midpoint = { x: (start.x + end.x) / 2, y: (start.y + end.y) / 2 };
    const bend = Math.min(120, Math.max(32, distance * 0.22));
    const direction = ((i + index) % 2 === 0 ? 1 : -1);
    const control = {
      x: midpoint.x + (-dy / distance) * bend * direction,
      y: midpoint.y + (dx / distance) * bend * direction,
    };
    const steps = Math.max(6, Math.round(distance / 90));
    for (let step = 1; step <= steps; step += 1) {
      const t = step / steps;
      path.push(quadraticBezier(start, control, end, t));
    }
  }
  return path;
}

function quadraticBezier(start, control, end, t) {
  const inv = 1 - t;
  return {
    x: inv * inv * start.x + 2 * inv * t * control.x + t * t * end.x,
    y: inv * inv * start.y + 2 * inv * t * control.y + t * t * end.y,
  };
}

function cloneGraphNodes(galaxy) {
  return (galaxy.nodes || []).map(node => {
    const raw = node.raw || node;
    const memorySystem = node.memorySystem || memorySystemForData(raw);
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

function groupByAgentNamespace(nodes, agentGalaxies = new Map()) {
  const groups = new Map();
  for (const [namespace, meta] of agentGalaxies || []) {
    groups.set(namespace, {
      namespace,
      label: meta.label || labelForAgentNamespace(namespace),
      nodes: [],
    });
  }
  for (const node of nodes) {
    const namespace = node.agentNamespace || "codex";
    if (!groups.has(namespace)) {
      groups.set(namespace, {
        namespace,
        label: node.agentLabel || labelForAgentNamespace(namespace),
        nodes: [],
      });
    }
    groups.get(namespace).nodes.push(node);
  }
  return [...groups.values()].filter(group => group.nodes.length > 0);
}

function placeAgentGalaxies(groups) {
  const count = Math.max(1, groups.length);
  const radius = count === 1 ? 0 : Math.min(920, Math.max(520, 300 + count * 120));
  return groups.map((group, index) => {
    const angle = count === 1 ? 0 : (-Math.PI / 2) + (Math.PI * 2 * index) / count;
    return {
      ...group,
      centerX: Math.cos(angle) * radius,
      centerY: Math.sin(angle) * radius * 0.68,
      galaxyRadius: Math.max(280, Math.min(520, 160 + Math.sqrt(group.nodes.length) * 42)),
    };
  });
}

function labelForAgentNamespace(namespace) {
  return String(namespace || "codex")
    .split(/[-_:]+/)
    .filter(Boolean)
    .map(part => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ") || "Codex";
}

function baseSystemKey(systemKey) {
  const key = String(systemKey || "knowledge");
  const parts = key.split(":");
  return parts.length > 1 ? parts.at(-1) : key;
}

function agentNamespaceForSystemKey(systemKey, fallback = "codex") {
  const key = String(systemKey || "");
  const parts = key.split(":");
  return parts.length > 1 ? parts[0] : (fallback || "codex");
}

function buildSystemDescriptors(grouped, nodeScale, frame = null) {
  const offsetX = Number(frame?.centerX || 0);
  const offsetY = Number(frame?.centerY || 0);
  const namespace = frame?.namespace || "codex";
  const byLayer = new Map(layerOrder.map(layer => [layer, []]));
  for (const key of layoutSystemOrder) {
    if (key === "router") continue;
    if (!grouped.has(key)) continue;
    const layer = systemLayerForKey(key);
    if (!byLayer.has(layer)) byLayer.set(layer, []);
    byLayer.get(layer).push(key);
  }
  const systems = [{
    key: `${namespace}:router`,
    baseKey: "router",
    agentNamespace: namespace,
    label: frame?.label || "Codex",
    layer: "core",
    x: offsetX,
    y: offsetY,
    radius: 72,
    miniOrbits: [],
    orbitAspect: 1,
    animation: {
      orbitCenterX: 0,
      orbitCenterY: 0,
      orbitRadiusX: 0,
      orbitRadiusY: 0,
      orbitAngle: 0,
      orbitSpeed: 0,
    },
  }];
  layerOrder.forEach((layer, layerIndex) => {
    const keys = byLayer.get(layer) || [];
    const radius = layerRadii[layer] || 760;
    const angleOffset = Math.PI / (layerIndex + 4);
    keys.forEach((key, index) => {
      const angle = angleOffset + (index * Math.PI * 2) / Math.max(1, keys.length);
      const miniRadius = 98 * Math.max(0.82, nodeScale / 0.48);
        systems.push({
          key: `${namespace}:${key}`,
          baseKey: key,
          agentNamespace: namespace,
          label: systemLabels[key] || key,
          layer,
          color: systemColor(key),
          x: offsetX + Math.cos(angle) * radius,
          y: offsetY + Math.sin(angle) * radius * 0.58,
          radius: miniRadius,
          miniOrbits: [],
          orbitAspect: 0.58,
          animation: {
            orbitCenterX: offsetX,
            orbitCenterY: offsetY,
            orbitRadiusX: radius,
            orbitRadiusY: radius * 0.58,
            orbitAngle: angle,
            orbitSpeed: 0.06 + layerIndex * 0.012,
          },
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

function splitTracks(nodes, baseRadius, step, nodeScale, maxPerTrack = Infinity) {
  if (!nodes.length) return [];
  const maxRadius = Math.max(...nodes.map(node => priorityRadiusForData(node.raw || node, { scale: nodeScale })));
  const autoCapacity = Math.max(1, Math.floor((Math.PI * 2 * Math.max(24, baseRadius)) / Math.max(14, maxRadius * 2 + 8)));
  const capacity = Math.max(1, Math.min(autoCapacity, Number.isFinite(maxPerTrack) ? maxPerTrack : autoCapacity));
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
    const angle = options.startAngle + index * (options.angleStep || Math.PI * 2 / count);
    const x = options.centerX + Math.cos(angle) * options.radiusX;
    const y = options.centerY + Math.sin(angle) * options.radiusY;
    return placeNode(node, x, y, {
      memorySystem: options.memorySystem,
      orbitRole: options.orbitRole,
      orbitalRole: options.orbitalRole,
      renderRadius: node.renderRadius || priorityRadiusForData(node.raw || node, { scale: options.nodeScale }),
      labelAnchor: labelAnchor(x, y, angle),
      orbitCenterX: options.centerX,
      orbitCenterY: options.centerY,
      orbitRadiusX: options.radiusX,
      orbitRadiusY: options.radiusY,
      orbitSpeed: options.orbitSpeed,
      spinSpeed: options.spinSpeed,
      parentSystemKey: options.parentSystemKey,
      parentNodeId: options.parentNodeId,
      parentPlanetId: options.parentPlanetId || node.parentPlanetId,
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
    parentPlanetId: overrides.parentPlanetId || node.parentPlanetId || null,
    childCount: overrides.childCount ?? node.childCount ?? 0,
    isSystemNode: overrides.isSystemNode ?? node.isSystemNode ?? false,
    isSolarCenterStar: overrides.isSolarCenterStar ?? node.isSolarCenterStar ?? false,
    systemKey: overrides.systemKey ?? node.systemKey ?? null,
    agentNamespace: overrides.agentNamespace ?? node.agentNamespace ?? raw.agent_namespace ?? "codex",
    agentLabel: overrides.agentLabel ?? node.agentLabel ?? raw.agent_label ?? labelForAgentNamespace(raw.agent_namespace || "codex"),
    labelPriority: overrides.labelPriority ?? node.labelPriority,
    animation: {
      orbitCenterX: overrides.orbitCenterX ?? 0,
      orbitCenterY: overrides.orbitCenterY ?? 0,
      orbitRadiusX: overrides.orbitRadiusX ?? Math.abs(x - (overrides.orbitCenterX ?? 0)),
      orbitRadiusY: overrides.orbitRadiusY ?? Math.abs(y - (overrides.orbitCenterY ?? 0)),
      orbitAngle: Math.atan2(y - (overrides.orbitCenterY ?? 0), x - (overrides.orbitCenterX ?? 0)),
      orbitSpeed: overrides.orbitSpeed ?? animationSpeedFor(overrides.orbitalRole || node.orbitalRole),
      spinSpeed: overrides.spinSpeed ?? spinSpeedFor(overrides.orbitalRole || node.orbitalRole),
      parentSystemKey: overrides.parentSystemKey,
      parentNodeId: overrides.parentNodeId,
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

function solarSatelliteProfileFor(system, index, scaleRatio, solarElementScale = 1) {
  const childCount = Math.max(1, system.children.length);
  const weight = Math.min(1, scoreNode(system.anchor.raw || system.anchor) / 42);
  const aspect = Math.max(0.42, Math.min(0.78, 0.5 + (index % 4) * 0.07 + childCount * 0.015 - weight * 0.04));
  return {
    aspect,
    radius: (28 + (index % 3) * 7 + childCount * 7 + weight * 7) * scaleRatio * solarElementScale,
    step: (18 + (index % 2) * 8 + childCount * 3) * scaleRatio * solarElementScale,
    phase: index * 0.43 + childCount * 0.19,
    orbitSpeed: 0.04 + (index % 4) * 0.012 + childCount * 0.004,
    spinSpeed: 0.02 + (index % 3) * 0.006,
  };
}

function buildSolarPlanetTracks(planetSystems, nodeScale, scaleRatio, centralRenderRadius, solarElementScale = 1, solarPlanetOrbitScale = 1, solarSatelliteOrbitScale = 1) {
  const orbitScale = Math.max(0.1, Number(solarPlanetOrbitScale || 1));
  const planned = planetSystems.map((system, index) => {
    const profile = solarSatelliteProfileFor(system, index, scaleRatio, solarSatelliteOrbitScale);
    const parentRadius = solarPlanetSystemRadius(system, nodeScale, centralRenderRadius, solarElementScale);
    const visibleChildren = system.children.slice(0, visibleSolarSatelliteCount(system));
    const plannedChildTracks = splitTracks(visibleChildren, profile.radius, profile.step, nodeScale, 4);
    const satelliteRadius = plannedChildTracks.length > 0
      ? plannedChildTracks.at(-1).radius
      : 0;
    const footprint = satelliteRadius + Math.max(30, parentRadius + 16 * solarElementScale);
    return { system, footprint };
  });
  const tracks = [];
  let cursor = 0;
  let radius = 220 * scaleRatio * orbitScale;
  let previousMaxFootprint = 0;
  const trackGap = 92 * scaleRatio * orbitScale;
  while (cursor < planned.length) {
    let systemsForTrack = [];
    let footprintsForTrack = new Map();
    let maxFootprint = 0;
    for (let capacity = Math.min(5, planned.length - cursor); capacity >= 1; capacity -= 1) {
      const slice = planned.slice(cursor, cursor + capacity);
      maxFootprint = Math.max(...slice.map(item => item.footprint));
      const candidateRadius = minimumSolarTrackRadius(slice, Math.max(radius, centralRenderRadius + maxFootprint + 48 * scaleRatio * orbitScale), 0.58, orbitScale);
      const angleStep = Math.PI * 2 / capacity;
      if (Number.isFinite(candidateRadius)) {
        radius = candidateRadius;
        systemsForTrack = slice.map(item => item.system);
        footprintsForTrack = new Map(slice.map(item => [item.system.anchor.id, item.footprint]));
        break;
      }
    }
    if (systemsForTrack.length === 0) {
      const item = planned[cursor];
      systemsForTrack = [item.system];
      footprintsForTrack = new Map([[item.system.anchor.id, item.footprint]]);
      maxFootprint = item.footprint;
      radius = Math.max(radius, centralRenderRadius + maxFootprint + 48 * scaleRatio * orbitScale);
    }
    tracks.push({
      radius,
      systems: systemsForTrack,
      footprints: footprintsForTrack,
      angleStep: Math.PI * 2 / Math.max(1, systemsForTrack.length),
    });
    cursor += systemsForTrack.length;
    const nextTrackGap = previousMaxFootprint > 0
      ? (previousMaxFootprint + maxFootprint) * 0.92 + trackGap * 0.56
      : maxFootprint * 2 + trackGap * 0.56 + 48;
    radius += Math.max(170 * scaleRatio * orbitScale, nextTrackGap);
    previousMaxFootprint = maxFootprint;
  }
  return tracks;
}

function minimumSolarTrackRadius(items, startRadius, aspect, orbitScale = 1) {
  const minRadius = 260 * Math.max(0.1, Number(orbitScale || 1));
  const limit = Math.max(startRadius, minRadius) + 420 * Math.max(0.1, Number(orbitScale || 1));
  const angleStep = Math.PI * 2 / Math.max(1, items.length);
  for (let radius = startRadius; radius <= limit; radius += 8) {
    if (solarTrackFits(items, radius, angleStep, aspect)) return radius;
  }
  return null;
}

function solarTrackFits(items, radius, angleStep, aspect) {
  if (items.length <= 1) return true;
  const points = items.map((item, index) => {
    const angle = roleStartAngle("planet") + index * angleStep;
    return {
      x: Math.cos(angle) * radius,
      y: Math.sin(angle) * radius * aspect,
      footprint: item.footprint,
    };
  });
  for (let index = 0; index < points.length; index += 1) {
    const current = points[index];
    const next = points[(index + 1) % points.length];
    const distance = Math.hypot(current.x - next.x, current.y - next.y);
    if (distance < current.footprint + next.footprint + 18) return false;
  }
  return true;
}

function solarPlanetSystemRadius(system, nodeScale, centralRenderRadius, solarElementScale = 1) {
  if (system.children.length === 0) {
    const radius = priorityRadiusForData(system.anchor.raw || system.anchor, { scale: nodeScale }) * 1.05 * solarElementScale;
    return Math.min(centralRenderRadius * 0.62, Math.max(8, radius));
  }
  const influence = Math.min(1, scoreNode(system.anchor.raw || system.anchor) / 42);
  const capacityBoost = Math.min(4, system.children.length) * 0.7;
  const radius = 10 + influence * 8 + capacityBoost;
  return Math.min(centralRenderRadius * 0.68, Math.max(16, radius * solarElementScale));
}

function visibleSolarSatelliteCount(system) {
  if (system.children.length <= 0) return 0;
  return Math.min(6, Math.max(2, system.children.length));
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
        parentNodeId: parent.id,
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

function buildSolarPlanetSystems(localNodes, localLinks, systemKey) {
  if (localNodes.length === 0) return [];
  const adjacency = buildAdjacencyMap(localLinks);
  const maxChildrenPerSystem = 6;
  const systemNodes = localNodes
    .filter(node => node.memorySystem === systemKey)
    .sort(compareNodePriority);
  const ranked = [...localNodes].sort((a, b) => {
    const degreeDelta = (adjacency.get(String(b.id))?.size || 0) - (adjacency.get(String(a.id))?.size || 0);
    return degreeDelta || compareNodePriority(a, b);
  });
  const maxSeeds = Math.min(10, Math.max(3, Math.ceil(localNodes.length / 4)));
  const seeds = [];
  const seedIds = new Set();

  for (const node of [...systemNodes, ...ranked]) {
    if (seedIds.has(node.id)) continue;
    seeds.push(node);
    seedIds.add(node.id);
    if (seeds.length >= maxSeeds) break;
  }

  let systems = seeds.map(anchor => ({ anchor, children: [] }));

  for (const node of localNodes) {
    if (seedIds.has(node.id)) continue;
    const neighbors = adjacency.get(String(node.id)) || new Set();
    const directMatches = systems
      .filter(system => neighbors.has(String(system.anchor.id)))
      .sort((a, b) => a.children.length - b.children.length || scoreNode(b.anchor.raw || b.anchor) - scoreNode(a.anchor.raw || a.anchor));
    const preferredSystem = node.memorySystem === systemKey
      ? systems.find(system => system.anchor.memorySystem === systemKey && system.anchor.id !== node.id)
      : null;
    const fallbackMatches = systems
      .filter(system => system.anchor.id !== node.id)
      .sort((a, b) => a.children.length - b.children.length || scoreNode(b.anchor.raw || b.anchor) - scoreNode(a.anchor.raw || a.anchor));
    const target = directMatches[0] || preferredSystem || fallbackMatches[0];
    if (target && target.children.length < maxChildrenPerSystem) {
      target.children.push(node);
      continue;
    }
    if (systems.length < maxSeeds) {
      systems.push({ anchor: node, children: [] });
      seedIds.add(node.id);
      continue;
    }
    if (target) target.children.push(node);
  }

  if (!systems.some(system => system.children.length > 0)) {
    const fallbackChild = localNodes.find(node => !seedIds.has(node.id));
    if (fallbackChild && systems[0]) systems[0].children.push(fallbackChild);
  }

  while (systems.length < maxSeeds) {
    const donor = systems
      .filter(system => system.children.length > maxChildrenPerSystem)
      .sort((a, b) => b.children.length - a.children.length)[0];
    if (!donor) break;
    const peeledIndex = donor.children.findIndex(node => node.memorySystem === systemKey);
    const peeled = donor.children.splice(peeledIndex >= 0 ? peeledIndex : donor.children.length - 1, 1)[0];
    if (!peeled) break;
    seedIds.add(peeled.id);
    systems.push({ anchor: peeled, children: [] });
  }

  systems = systems.map(system => ({ anchor: system.anchor, children: [] }));
  for (const node of localNodes) {
    if (seedIds.has(node.id)) continue;
    const neighbors = adjacency.get(String(node.id)) || new Set();
    const directMatches = systems
      .filter(system => neighbors.has(String(system.anchor.id)))
      .sort((a, b) => a.children.length - b.children.length || scoreNode(b.anchor.raw || b.anchor) - scoreNode(a.anchor.raw || a.anchor));
    const preferredSystem = node.memorySystem === systemKey
      ? systems.find(system => system.anchor.memorySystem === systemKey && system.anchor.id !== node.id && system.children.length < maxChildrenPerSystem)
      : null;
    const fallbackMatches = systems
      .filter(system => system.anchor.id !== node.id)
      .sort((a, b) => a.children.length - b.children.length || scoreNode(b.anchor.raw || b.anchor) - scoreNode(a.anchor.raw || a.anchor));
    const target = directMatches.find(system => system.children.length < maxChildrenPerSystem)
      || preferredSystem
      || fallbackMatches.find(system => system.children.length < maxChildrenPerSystem)
      || directMatches[0]
      || fallbackMatches[0];
    if (target) target.children.push(node);
  }

  for (const system of systems) {
    const seen = new Set();
    system.children = system.children.filter(node => {
      if (node.id === system.anchor.id || seen.has(node.id)) return false;
      seen.add(node.id);
      return true;
    }).sort(compareNodePriority);
  }

  return systems
    .filter(system => system.anchor)
    .sort((a, b) => {
      const childDelta = Number(b.children.length > 0) - Number(a.children.length > 0);
      return childDelta || scoreNode(b.anchor.raw || b.anchor) - scoreNode(a.anchor.raw || a.anchor);
    });
}

function buildSolarSubgraph(nodes, links, systemKey, agentNamespace = "codex") {
  const clonedLinks = cloneLinks(links);
  const adjacency = buildAdjacencyMap(clonedLinks);
  const systemNodes = nodes
    .filter(node => node.memorySystem === systemKey && node.agentNamespace === agentNamespace)
    .sort(compareNodePriority);
  const systemIds = new Set(systemNodes.map(node => String(node.id)));
  const directIds = new Set();
  for (const id of systemIds) {
    for (const neighbor of adjacency.get(id) || []) {
      if (!systemIds.has(neighbor)) directIds.add(neighbor);
    }
  }
  const directNodes = nodes
    .filter(node => node.agentNamespace === agentNamespace && directIds.has(String(node.id)))
    .sort(compareNodePriority)
    .slice(0, 18);
  const directNodeIds = new Set(directNodes.map(node => String(node.id)));
  const secondIds = new Set();
  for (const id of directNodeIds) {
    for (const neighbor of adjacency.get(id) || []) {
      if (systemIds.has(neighbor) || directNodeIds.has(neighbor)) continue;
      secondIds.add(neighbor);
    }
  }
  const secondNodes = nodes
    .filter(node => node.agentNamespace === agentNamespace && secondIds.has(String(node.id)))
    .sort(compareNodePriority)
    .slice(0, 30);
  const selectedNodes = dedupeNodes([
    ...systemNodes,
    ...directNodes,
    ...secondNodes,
  ]);
  const selectedIds = new Set(selectedNodes.map(node => String(node.id)));
  return {
    nodes: selectedNodes,
    links: clonedLinks.filter(link => {
      const source = String(link.source?.id || link.source);
      const target = String(link.target?.id || link.target);
      return selectedIds.has(source) && selectedIds.has(target);
    }),
  };
}

function buildAdjacencyMap(links) {
  const adjacency = new Map();
  for (const link of links) {
    const source = String(link.source?.id || link.source);
    const target = String(link.target?.id || link.target);
    if (!adjacency.has(source)) adjacency.set(source, new Set());
    if (!adjacency.has(target)) adjacency.set(target, new Set());
    adjacency.get(source).add(target);
    adjacency.get(target).add(source);
  }
  return adjacency;
}

function dedupeNodes(nodes) {
  const seen = new Set();
  return nodes.filter(node => {
    const id = String(node.id);
    if (seen.has(id)) return false;
    seen.add(id);
    return true;
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
    if (system.layer === "core") continue;
    const key = `${system.agentNamespace || "codex"}:${system.layer}`;
    if (seen.has(key)) continue;
    seen.add(key);
    orbits.push({
      kind: system.layer,
      agentNamespace: system.agentNamespace || "codex",
      centerX: Number(system.animation?.orbitCenterX ?? 0),
      centerY: Number(system.animation?.orbitCenterY ?? 0),
      radius: layerRadii[system.layer] || Math.hypot(system.x, system.y),
      aspect: 0.58,
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
    const centerX = Number(orbit.centerX || 0);
    const centerY = Number(orbit.centerY || 0);
    const aspect = Number(orbit.aspect || 0.62);
    minX = Math.min(minX, centerX - pad);
    maxX = Math.max(maxX, centerX + pad);
    minY = Math.min(minY, centerY - pad * aspect);
    maxY = Math.max(maxY, centerY + pad * aspect);
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

function boundsForSolarSystem(nodes, orbits = [], satelliteSystems = []) {
  const centerNodes = nodes.filter(node => !node.animation?.parentNodeId);
  const bounds = boundsFor(centerNodes, [], []);
  for (const system of satelliteSystems) {
    const pad = Number(system.footprintRadius || system.radius || 0) + 34;
    bounds.minX = Math.min(bounds.minX, system.x - pad);
    bounds.maxX = Math.max(bounds.maxX, system.x + pad);
    bounds.minY = Math.min(bounds.minY, system.y - pad * Number(system.aspect || 0.62));
    bounds.maxY = Math.max(bounds.maxY, system.y + pad * Number(system.aspect || 0.62));
  }
  bounds.width = bounds.maxX - bounds.minX;
  bounds.height = bounds.maxY - bounds.minY;
  return bounds;
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
    satellite: -Math.PI / 2,
    "direct-moon": -Math.PI / 2,
    "derived-moon": -Math.PI / 4,
    external: Math.PI / 5,
  }[role] || -Math.PI / 2;
}

function animationSpeedFor(role) {
  return {
    "agent-core": 0,
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

function overviewOrbitSpeedFor(role) {
  return {
    planet: 0.16,
    moon: 0.208,
    evidence: 0.184,
  }[role] || 0.16;
}

function spinSpeedFor(role) {
  return {
    "agent-core": 0,
    "galactic-core": 0,
    "central-star": 0,
    "central-planet": 0,
    star: 0,
  }[role] ?? 0.018;
}

function orbitSpeedForPlanetRing(kind) {
  return {
    "direct-moon": 0.032,
    "derived-moon": 0.024,
    evidence: 0.018,
    external: 0.014,
  }[kind] || 0.02;
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

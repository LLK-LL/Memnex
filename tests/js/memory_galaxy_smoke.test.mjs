import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import vm from "node:vm";

const helperPath = resolve("src/tools/memory_graph_viewer_assets/memory-galaxy-core.js");
const helperSource = readFileSync(helperPath, "utf8").replaceAll("export function ", "function ");
const context = { exports: {} };
vm.runInNewContext(
  `${helperSource}
exports.convertGraphToGalaxy = convertGraphToGalaxy;
exports.filterGalaxy = filterGalaxy;
exports.buildFocusGalaxy = buildFocusGalaxy;
exports.buildExpandedGalaxy = buildExpandedGalaxy;
exports.buildEditIntent = buildEditIntent;
exports.buildGalaxy2DLayout = buildGalaxy2DLayout;
exports.buildSphereGalaxyLayout = buildSphereGalaxyLayout;
exports.selectVisibleLabels = selectVisibleLabels;
exports.buildGalaxyCacheKey = buildGalaxyCacheKey;
exports.groupNeighborRelations = groupNeighborRelations;
exports.buildClusterGalaxy2DLayout = buildClusterGalaxy2DLayout;
exports.pruneGalaxyLinks = pruneGalaxyLinks;
exports.visibleLinksForSelection = visibleLinksForSelection;
exports.springBackTarget = springBackTarget;
exports.memorySystemForNode = memorySystemForNode;
exports.priorityRadiusForNode = priorityRadiusForNode;
exports.buildGalacticOrbital2DLayout = buildGalacticOrbital2DLayout;
exports.labelAnchorForNode = labelAnchorForNode;`,
  context,
  { filename: helperPath },
);

const {
  convertGraphToGalaxy,
  filterGalaxy,
  buildFocusGalaxy,
  buildExpandedGalaxy,
  buildEditIntent,
  buildGalaxy2DLayout,
  buildSphereGalaxyLayout,
  selectVisibleLabels,
  buildGalaxyCacheKey,
  groupNeighborRelations,
  buildClusterGalaxy2DLayout,
  pruneGalaxyLinks,
  visibleLinksForSelection,
  springBackTarget,
  memorySystemForNode,
  priorityRadiusForNode,
  buildGalacticOrbital2DLayout,
  labelAnchorForNode,
} = context.exports;

const eventHelperPath = resolve("src/tools/memory_graph_viewer_assets/memory-galaxy-events.js");
const eventHelperSource = readFileSync(eventHelperPath, "utf8").replaceAll("export function ", "function ");
const eventContext = { exports: {} };
vm.runInNewContext(
  `${eventHelperSource}
exports.createMemoryGalaxyEvent = createMemoryGalaxyEvent;
exports.createInteractionLog = createInteractionLog;
exports.suggestAgentPrompt = suggestAgentPrompt;`,
  eventContext,
  { filename: eventHelperPath },
);
const { createMemoryGalaxyEvent, createInteractionLog, suggestAgentPrompt } = eventContext.exports;

const sharedHelperPath = resolve("src/tools/memory_graph_viewer_assets/viewer-shared.js");
const sharedHelperSource = readFileSync(sharedHelperPath, "utf8").replaceAll("export function ", "function ");
const sharedContext = { exports: {} };
vm.runInNewContext(
  `${sharedHelperSource}
exports.escapeHtml = escapeHtml;
exports.formatNodeDetails = formatNodeDetails;
exports.timelineCutoffFromPercent = timelineCutoffFromPercent;
exports.renderPromptText = renderPromptText;`,
  sharedContext,
  { filename: sharedHelperPath },
);
const { formatNodeDetails, timelineCutoffFromPercent, renderPromptText } = sharedContext.exports;

const systemsHelperPath = resolve("src/tools/memory_graph_viewer_assets/memory-galaxy-systems.js");
const systemsHelperSource = readFileSync(systemsHelperPath, "utf8")
  .replaceAll("export const ", "const ")
  .replaceAll("export function ", "function ");
const systemsContext = { exports: {} };
vm.runInNewContext(
  `${systemsHelperSource}
exports.memorySystemForData = memorySystemForData;
exports.orbitRoleForData = orbitRoleForData;
exports.priorityRadiusForData = priorityRadiusForData;
exports.systemColor = systemColor;
exports.systemLayerForKey = systemLayerForKey;`,
  systemsContext,
  { filename: systemsHelperPath },
);
const {
  memorySystemForData,
  orbitRoleForData,
  priorityRadiusForData,
  systemColor,
  systemLayerForKey,
} = systemsContext.exports;

const layoutsHelperPath = resolve("src/tools/memory_graph_viewer_assets/memory-galaxy-layouts.js");
const layoutsHelperSource = readFileSync(layoutsHelperPath, "utf8")
  .replace(/import[\s\S]*?from ".\/memory-galaxy-systems\.js";\n/, "")
  .replaceAll("export function ", "function ");
const layoutsContext = {
  exports: {},
  memorySystemForData,
  orbitRoleForData,
  priorityRadiusForData,
  systemColor,
  systemLayerForKey,
};
vm.runInNewContext(
  `${layoutsHelperSource}
exports.buildGalaxyOverviewLayout = buildGalaxyOverviewLayout;
exports.buildSolarSystemLayout = buildSolarSystemLayout;
exports.buildPlanetSatelliteLayout = buildPlanetSatelliteLayout;
exports.buildCometOverlayLayout = buildCometOverlayLayout;`,
  layoutsContext,
  { filename: layoutsHelperPath },
);
const {
  buildGalaxyOverviewLayout,
  buildSolarSystemLayout,
  buildPlanetSatelliteLayout,
  buildCometOverlayLayout,
} = layoutsContext.exports;

const fixture = {
  metadata: {
    type_counts: { project: 1, concept: 1, rule: 1 },
    timeline: { start: "2026-01-01T00:00:00+00:00", end: "2026-06-01T00:00:00+00:00" },
  },
  elements: {
    nodes: [
      { data: { id: "p1", label: "Jarvis", type: "project", content: "Project", mention_count: 10, importance: 1, galaxy_layer: "active", freshness: 1, activity: 1, last_seen_at: "2026-06-01T00:00:00+00:00", knowledge: [] } },
      { data: { id: "c1", label: "Memory", type: "concept", content: "Memory concept", mention_count: 3, importance: 0.5, galaxy_layer: "knowledge", freshness: 0.5, activity: 0.3, last_seen_at: "2026-03-01T00:00:00+00:00", knowledge: [] } },
      { data: { id: "r1", label: "Rule", type: "rule", content: "Rule content", mention_count: 1, importance: 2, galaxy_layer: "core", freshness: 0.2, activity: 0.1, last_seen_at: "2026-02-01T00:00:00+00:00", knowledge: [] } },
    ],
    edges: [
      { data: { id: "e1", source: "p1", target: "c1", relation: "related", weight: 2 } },
      { data: { id: "e2", source: "c1", target: "r1", relation: "context", weight: 5 } },
    ],
  },
};

const galaxy = convertGraphToGalaxy(fixture);
assert.equal(galaxy.nodes.length, 3);
assert.equal(galaxy.links.length, 2);
assert.equal(galaxy.nodes.find(node => node.id === "r1").layer, "core");

const filtered = filterGalaxy(galaxy, {
  query: "memory",
  activeTypes: new Set(["project", "concept", "rule"]),
  activeLayers: new Set(["core", "active", "knowledge"]),
  minWeight: 0,
  timelineCutoff: "2026-04-01T00:00:00+00:00",
});
assert.deepEqual(filtered.nodes.map(node => node.id), ["c1"]);
assert.equal(filtered.links.length, 0);

const focusFixture = {
  metadata: { type_counts: {}, timeline: {} },
  elements: {
    nodes: [
      { data: { id: "core", label: "Core", type: "rule", mention_count: 30, importance: 2, galaxy_layer: "core", freshness: 1, activity: 1, knowledge: [] } },
      ...Array.from({ length: 20 }, (_, index) => ({
        data: { id: `n${index}`, label: `Node ${index}`, type: "concept", mention_count: index, importance: 0.1, galaxy_layer: "knowledge", freshness: 0.2, activity: 0.2, knowledge: [] },
      })),
    ],
    edges: Array.from({ length: 20 }, (_, index) => ({
      data: { id: `e${index}`, source: "core", target: `n${index}`, relation: "related", weight: index + 1 },
    })),
  },
};
const focusGalaxy = buildFocusGalaxy(convertGraphToGalaxy(focusFixture), {
  maxNodes: 8,
  seedCount: 1,
  firstRingLimit: 4,
});
assert.equal(focusGalaxy.nodes.length, 8);
assert.ok(focusGalaxy.nodes.some(node => node.id === "core" && node.focusRing === 0));
assert.ok(focusGalaxy.links.length <= 7);

const expandedGalaxy = buildExpandedGalaxy(
  convertGraphToGalaxy(focusFixture),
  { nodes: focusGalaxy.nodes.slice(0, 3), links: [], metadata: focusGalaxy.metadata },
  new Set(["core"]),
  { neighborLimit: 5 },
);
assert.ok(expandedGalaxy.nodes.length > 3);
assert.ok(expandedGalaxy.nodes.some(node => node.id === "core"));
assert.ok(expandedGalaxy.nodes.length <= 8);
const expandedCore = expandedGalaxy.nodes.find(node => node.id === "core");
const expandedChild = expandedGalaxy.nodes.find(node => node.id !== "core" && !focusGalaxy.nodes.slice(0, 3).some(baseNode => baseNode.id === node.id));
assert.ok(Math.hypot(expandedChild.x - expandedCore.x, expandedChild.z - expandedCore.z) < 180);
assert.ok(expandedGalaxy.links.some(link => link.expansionParentId === "core"));

const intent = buildEditIntent("add_relation", { source: "p1", target: "c1", relation: "related" });
assert.equal(intent.action, "add_relation");
assert.equal(intent.payload.source, "p1");
assert.ok(intent.created_at);

const layout2dA = buildGalaxy2DLayout(galaxy, { maxNodes: 3 });
const layout2dB = buildGalaxy2DLayout(galaxy, { maxNodes: 3 });
assert.deepEqual(
  layout2dA.nodes.map(node => [node.id, Math.round(node.x), Math.round(node.y)]),
  layout2dB.nodes.map(node => [node.id, Math.round(node.x), Math.round(node.y)]),
);
assert.ok(layout2dA.nodes.every(node => Number.isFinite(node.x) && Number.isFinite(node.y)));
assert.ok(layout2dA.nodes.every(node => node.renderRadius >= 4));

const sphere = buildSphereGalaxyLayout(galaxy, { maxNodes: 3 });
assert.equal(sphere.nodes.length, 3);
for (const node of sphere.nodes) {
  const distance = Math.hypot(node.x, node.y, node.z);
  assert.ok(distance >= 70 && distance <= 430);
  assert.ok(Number.isFinite(node.theta));
  assert.ok(Number.isFinite(node.phi));
}

const labelsFar = selectVisibleLabels(layout2dA.nodes, {
  zoom: 0.45,
  selectedNodeId: "p1",
  hoveredNodeId: null,
});
assert.ok(labelsFar.some(node => node.id === "p1"));
assert.ok(labelsFar.every(node => node.layer === "core" || node.layer === "active" || node.id === "p1"));

const labelsNear = selectVisibleLabels(layout2dA.nodes, {
  zoom: 1.8,
  selectedNodeId: null,
  hoveredNodeId: "c1",
});
assert.ok(labelsNear.some(node => node.id === "c1"));
assert.ok(labelsNear.length >= labelsFar.length);

const cacheKey = buildGalaxyCacheKey({
  metadata: {
    cache: { layout_namespace: "memory-galaxy", default_root: "D:\\TotalAgentMemory\\memory-galaxy-cache" },
    graph_identity: { node_ids_hash: "nodes", edge_ids_hash: "edges" },
  },
}, "2d");
assert.equal(cacheKey, "memory-galaxy:2d:D:\\TotalAgentMemory\\memory-galaxy-cache:nodes:edges");

const grouped = groupNeighborRelations(galaxy, "c1");
assert.deepEqual(Object.keys(grouped).sort(), ["context", "related"]);
assert.equal(grouped.related[0].neighbor.id, "p1");
assert.equal(grouped.context[0].neighbor.id, "r1");

const denseFixture = {
  metadata: { type_counts: {}, timeline: {} },
  elements: {
    nodes: [
      { data: { id: "project", label: "Project", type: "project", mention_count: 20, importance: 1.4, galaxy_layer: "core", freshness: 1, activity: 1, knowledge: [] } },
      { data: { id: "concept", label: "Concept", type: "concept", mention_count: 15, importance: 1.0, galaxy_layer: "active", freshness: 0.8, activity: 0.8, knowledge: [] } },
      { data: { id: "tech", label: "Tech", type: "technology", mention_count: 10, importance: 0.8, galaxy_layer: "knowledge", freshness: 0.7, activity: 0.6, knowledge: [] } },
      { data: { id: "pattern", label: "Pattern", type: "pattern", mention_count: 8, importance: 0.7, galaxy_layer: "knowledge", freshness: 0.6, activity: 0.5, knowledge: [] } },
      { data: { id: "event", label: "Event", type: "event", mention_count: 5, importance: 0.5, galaxy_layer: "episode", freshness: 0.5, activity: 0.3, knowledge: [] } },
      { data: { id: "domain", label: "Domain", type: "domain", mention_count: 4, importance: 0.4, galaxy_layer: "external", freshness: 0.3, activity: 0.2, knowledge: [] } },
    ],
    edges: [
      { data: { id: "e1", source: "project", target: "concept", relation: "related", weight: 10 } },
      { data: { id: "e2", source: "project", target: "tech", relation: "related", weight: 8 } },
      { data: { id: "e3", source: "project", target: "pattern", relation: "related", weight: 6 } },
      { data: { id: "e4", source: "project", target: "event", relation: "related", weight: 4 } },
      { data: { id: "e5", source: "project", target: "domain", relation: "related", weight: 2 } },
      { data: { id: "e6", source: "concept", target: "tech", relation: "context", weight: 7 } },
      { data: { id: "e7", source: "concept", target: "pattern", relation: "context", weight: 5 } },
      { data: { id: "e8", source: "concept", target: "event", relation: "context", weight: 3 } },
    ],
  },
};
const denseGalaxy = convertGraphToGalaxy(denseFixture);

const pruned = pruneGalaxyLinks(denseGalaxy, { perNodeLimit: 3 });
assert.ok(pruned.links.length < denseGalaxy.links.length);
assert.ok(pruned.links.some(link => link.raw.id === "e1"));
assert.ok(pruned.links.some(link => link.raw.id === "e2"));
assert.ok(pruned.links.some(link => link.raw.id === "e6"));

const projectVisible = visibleLinksForSelection(denseGalaxy.links, {
  selectedNodeId: "project",
  hoveredNodeId: null,
  perNodeLimit: 3,
});
assert.ok(projectVisible.some(link => link.raw.id === "e5"));
assert.ok(projectVisible.filter(link => String(link.source.id || link.source) === "project" || String(link.target.id || link.target) === "project").length >= 5);

const clustered = buildClusterGalaxy2DLayout(denseGalaxy, { maxNodes: 6 });
const byIdClustered = new Map(clustered.nodes.map(node => [node.id, node]));
assert.ok(Math.hypot(byIdClustered.get("project").x - byIdClustered.get("event").x, byIdClustered.get("project").y - byIdClustered.get("event").y) > 220);
assert.ok(Math.hypot(byIdClustered.get("concept").x - byIdClustered.get("tech").x, byIdClustered.get("concept").y - byIdClustered.get("tech").y) > 120);
assert.ok(clustered.nodes.every(node => node.clusterKey));
assert.ok(clustered.nodes.every(node => Number.isFinite(node.homeX) && Number.isFinite(node.homeY)));

const springTarget = springBackTarget(
  { homeX: 100, homeY: 50, x: 300, y: 150 },
  { retainRatio: 0.2 },
);
assert.equal(springTarget.x, 140);
assert.equal(springTarget.y, 70);

const orbitalFixture = {
  metadata: { type_counts: {}, timeline: {} },
  elements: {
    nodes: [
      { data: { id: "router", label: "Router Core", type: "pattern", content: "routing orchestration and request dispatch", mention_count: 50, importance: 2.0, galaxy_layer: "core", freshness: 1, activity: 1, knowledge: [] } },
      { data: { id: "rule", label: "No Lumi edits", type: "rule", content: "rule: use the real memory viewer only", mention_count: 25, importance: 1.8, galaxy_layer: "core", freshness: 1, activity: 0.9, knowledge: [] } },
      { data: { id: "persona", label: "Persona Tone", type: "concept", content: "persona identity tone response style", mention_count: 18, importance: 1.3, galaxy_layer: "active", freshness: 0.9, activity: 0.8, knowledge: [] } },
      { data: { id: "skill", label: "Debugging Skill", type: "capability", content: "skill trigger systematic debugging workflow", mention_count: 15, importance: 1.2, galaxy_layer: "active", freshness: 0.9, activity: 0.7, knowledge: [] } },
      { data: { id: "harness", label: "Eval Harness", type: "technology", content: "harness test eval verification runner", mention_count: 12, importance: 1.1, galaxy_layer: "active", freshness: 0.8, activity: 0.7, knowledge: [] } },
      { data: { id: "pref", label: "User Preference", type: "concept", content: "preference deep-space playful visualization", mention_count: 10, importance: 0.9, galaxy_layer: "knowledge", freshness: 0.7, activity: 0.6, knowledge: [] } },
      { data: { id: "memory", label: "Viewer Memory", type: "concept", content: "memory graph visualization context", mention_count: 8, importance: 0.7, galaxy_layer: "knowledge", freshness: 0.7, activity: 0.5, knowledge: [] } },
      { data: { id: "source", label: "Source Episode", type: "event", content: "source episode observation", mention_count: 4, importance: 0.3, galaxy_layer: "episode", freshness: 0.5, activity: 0.3, knowledge: [] } },
    ],
    edges: [
      { data: { id: "or1", source: "router", target: "rule", relation: "routes", weight: 10 } },
      { data: { id: "or2", source: "router", target: "persona", relation: "routes", weight: 9 } },
      { data: { id: "or3", source: "router", target: "skill", relation: "routes", weight: 9 } },
      { data: { id: "or4", source: "skill", target: "harness", relation: "executes", weight: 8 } },
      { data: { id: "or5", source: "persona", target: "pref", relation: "shapes", weight: 7 } },
      { data: { id: "or6", source: "rule", target: "memory", relation: "guards", weight: 6 } },
      { data: { id: "or7", source: "memory", target: "source", relation: "evidence", weight: 3 } },
    ],
  },
};
const orbitalGalaxy = convertGraphToGalaxy(orbitalFixture);
const orbitalById = new Map(orbitalGalaxy.nodes.map(node => [node.id, node]));
assert.equal(memorySystemForData({ id: "router", type: "pattern", content: "routing orchestration dispatch" }), "router");
assert.equal(memorySystemForData({ id: "rule", type: "rule", content: "must verify source" }), "rule");
assert.equal(memorySystemForData({ id: "persona", type: "concept", content: "persona identity tone style" }), "persona");
assert.equal(memorySystemForData({ id: "skill", type: "capability", content: "skill workflow trigger" }), "skill");
assert.equal(memorySystemForData({ id: "harness", type: "technology", content: "eval harness pytest verification" }), "harness");
assert.equal(memorySystemForData({ id: "pref", type: "concept", content: "preference user wants deep-space view" }), "preference");
assert.equal(memorySystemForData({ id: "event", type: "event", galaxy_layer: "episode" }), "event");
assert.equal(memorySystemForData({ id: "source", type: "source", content: "provenance citation origin" }), "source");
assert.equal(systemLayerForKey("rule"), "control");
assert.equal(systemLayerForKey("skill"), "execution");
assert.equal(systemLayerForKey("knowledge"), "context");
assert.equal(systemLayerForKey("source"), "evidence");
assert.equal(orbitRoleForData({ type: "event", galaxy_layer: "episode" }), "evidence");
assert.equal(orbitRoleForData({ type: "concept", importance: 1.1, mention_count: 20 }), "planet");
assert.equal(orbitRoleForData({ type: "concept", importance: 0.2, mention_count: 2 }), "moon");
assert.ok(priorityRadiusForData({ type: "capability", content: "skill", importance: 2, activity: 1, mention_count: 30 }, { scale: 0.48 }) < 18);
assert.ok(priorityRadiusForData({ type: "capability", content: "skill", importance: 2, activity: 1, mention_count: 30 }, { scale: 0.7 }) > priorityRadiusForData({ type: "capability", content: "skill", importance: 2, activity: 1, mention_count: 30 }, { scale: 0.48 }));
assert.equal(systemColor("skill"), "#22d3ee");
assert.equal(memorySystemForNode(orbitalById.get("router")), "router");
assert.equal(memorySystemForNode(orbitalById.get("rule")), "rule");
assert.equal(memorySystemForNode(orbitalById.get("persona")), "persona");
assert.equal(memorySystemForNode(orbitalById.get("skill")), "skill");
assert.equal(memorySystemForNode(orbitalById.get("harness")), "harness");
assert.equal(memorySystemForNode(orbitalById.get("pref")), "preference");
assert.equal(memorySystemForNode(orbitalById.get("source")), "event");

assert.ok(priorityRadiusForNode(orbitalById.get("router")) > priorityRadiusForNode(orbitalById.get("rule")));
assert.ok(priorityRadiusForNode(orbitalById.get("persona")) > priorityRadiusForNode(orbitalById.get("pref")));
assert.ok(priorityRadiusForNode(orbitalById.get("skill")) > priorityRadiusForNode(orbitalById.get("memory")));
assert.ok(priorityRadiusForNode(orbitalById.get("harness")) > priorityRadiusForNode(orbitalById.get("source")));

const orbitalLayout = buildGalacticOrbital2DLayout(orbitalGalaxy, { maxNodes: 8, perNodeLimit: 5 });
const orbitalLayoutById = new Map(orbitalLayout.nodes.map(node => [node.id, node]));
const routerNode = orbitalLayoutById.get("router");
const ruleNode = orbitalLayoutById.get("rule");
const skillNode = orbitalLayoutById.get("skill");
const harnessNode = orbitalLayoutById.get("harness");
assert.ok(Math.hypot(routerNode.x, routerNode.y) < 80);
assert.ok(Math.hypot(ruleNode.systemCenter.x, ruleNode.systemCenter.y) > 220);
assert.equal(ruleNode.orbitalRole, "star");
assert.equal(skillNode.orbitalRole, "star");
assert.equal(harnessNode.memorySystem, "harness");
assert.ok(harnessNode.renderRadius >= 16);
assert.ok(orbitalLayout.systems.some(system => system.key === "persona"));
assert.ok(orbitalLayout.systems.some(system => system.key === "skill"));
assert.ok(orbitalLayout.systems.some(system => system.key === "harness"));

const finalOverview = buildGalaxyOverviewLayout(orbitalGalaxy, { nodeScale: 0.48, width: 1600, height: 1000 });
assert.equal(finalOverview.view, "galaxy");
assert.ok(finalOverview.systems.some(system => system.key === "router"));
assert.ok(finalOverview.systems.some(system => system.key === "skill"));
assert.ok(finalOverview.systems.every(system => system.key === "router" || system.miniOrbits.length >= 2));
assert.ok(finalOverview.nodes.every(node => Number.isFinite(node.x) && Number.isFinite(node.y)));
assert.ok(finalOverview.nodes.every(node => node.renderRadius <= 28));
assert.ok(finalOverview.bounds.width > 0);
for (let i = 0; i < finalOverview.nodes.length; i += 1) {
  for (let j = i + 1; j < finalOverview.nodes.length; j += 1) {
    const a = finalOverview.nodes[i];
    const b = finalOverview.nodes[j];
    const distance = Math.hypot(a.x - b.x, a.y - b.y);
    assert.ok(distance >= Math.min(14, a.renderRadius + b.renderRadius + 2));
  }
}

const skillSolar = buildSolarSystemLayout(orbitalGalaxy, "skill", { nodeScale: 0.48, width: 1400, height: 900 });
assert.equal(skillSolar.view, "solar");
assert.equal(skillSolar.systemKey, "skill");
assert.ok(skillSolar.orbits.some(orbit => orbit.kind === "category"));
assert.ok(skillSolar.orbits.some(orbit => orbit.kind === "planet"));
assert.ok(skillSolar.orbits.some(orbit => orbit.kind === "moon"));
assert.ok(skillSolar.orbits.some(orbit => orbit.kind === "evidence"));
assert.ok(skillSolar.nodes.some(node => node.orbitalRole === "central-star"));

const skillPlanet = buildPlanetSatelliteLayout(orbitalGalaxy, "skill", "skill", { nodeScale: 0.5, width: 1200, height: 800 });
assert.equal(skillPlanet.view, "planet");
assert.equal(skillPlanet.systemKey, "skill");
assert.equal(skillPlanet.planetId, "skill");
assert.ok(skillPlanet.orbits.some(orbit => orbit.kind === "direct-moon"));
assert.ok(skillPlanet.orbits.some(orbit => orbit.kind === "evidence"));
assert.ok(skillPlanet.nodes.some(node => node.orbitalRole === "central-planet"));

const cometOverlay = buildCometOverlayLayout(finalOverview, [{
  id: "comet:test",
  label: "Memory Galaxy Redesign",
  comet_type: "active_task",
  trajectory: ["preference", "skill", "harness", "rule"],
  influenced_systems: [{ system: "skill", weight: 0.92 }, { system: "harness", weight: 0.84 }],
}]);
assert.equal(cometOverlay.comets.length, 1);
assert.ok(cometOverlay.comets[0].influences.some(item => item.system === "skill" && item.weight > 0.9));
assert.ok(cometOverlay.comets[0].tail.length >= 2);

const denseOverviewFixture = {
  metadata: { type_counts: {}, timeline: {} },
  elements: {
    nodes: [
      { data: { id: "router-dense", label: "Router Dense", type: "pattern", content: "routing dispatch", mention_count: 100, importance: 2, galaxy_layer: "core", knowledge: [] } },
      ...Array.from({ length: 80 }, (_, index) => ({
        data: {
          id: `skill-dense-${index}`,
          label: `dense skill node ${index}`,
          type: "capability",
          content: "skill workflow trigger",
          mention_count: 80 - index,
          importance: index < 12 ? 1.2 : 0.2,
          galaxy_layer: index < 12 ? "active" : "knowledge",
          knowledge: [],
        },
      })),
    ],
    edges: Array.from({ length: 80 }, (_, index) => ({
      data: { id: `dense-edge-${index}`, source: "router-dense", target: `skill-dense-${index}`, relation: "routes", weight: 10 - index * 0.05 },
    })),
  },
};
const denseOverview = buildGalaxyOverviewLayout(convertGraphToGalaxy(denseOverviewFixture), { nodeScale: 0.48 });
const denseSkillNodes = denseOverview.nodes.filter(node => node.memorySystem === "skill");
assert.ok(denseSkillNodes.length <= 10);
assert.ok(denseSkillNodes.some(node => node.id === "system:skill" && node.label === "Skill System"));
assert.ok(!denseSkillNodes.some(node => node.label === "dense skill node 0" && node.orbitalRole === "star"));

const prefNode = orbitalLayoutById.get("pref");
const prefAnchor = labelAnchorForNode(prefNode);
assert.ok(Number.isFinite(prefAnchor.x));
assert.ok(Number.isFinite(prefAnchor.y));
assert.ok(Math.hypot(prefAnchor.x - prefNode.x, prefAnchor.y - prefNode.y) >= prefNode.renderRadius + 12);
assert.ok(["left", "right"].includes(prefAnchor.align));

const event = createMemoryGalaxyEvent("node:drag-ended", {
  node_id: "p1",
  gesture: "drag",
  view: "2d-galaxy",
  context: { layer: "active", visible_neighbors: 4 },
  timestamp: "2026-06-24T00:00:00.000Z",
});
assert.equal(event.type, "node:drag-ended");
assert.equal(event.node_id, "p1");
assert.equal(event.view, "2d-galaxy");
assert.equal(event.context.visible_neighbors, 4);

const log = createInteractionLog(2);
log.push(createMemoryGalaxyEvent("node:selected", { node_id: "a", timestamp: "2026-06-24T00:00:00.000Z" }));
log.push(createMemoryGalaxyEvent("node:hovered", { node_id: "b", timestamp: "2026-06-24T00:00:01.000Z" }));
log.push(createMemoryGalaxyEvent("node:drag-ended", { node_id: "c", timestamp: "2026-06-24T00:00:02.000Z" }));
assert.equal(JSON.stringify(log.all().map(item => item.node_id)), JSON.stringify(["b", "c"]));

const sourcePrompt = suggestAgentPrompt(event, {
  label: "RAG",
  provenance: { source: "explicit" },
  relation_counts: { total: 5 },
});
assert.equal(sourcePrompt.kind, "source-provenance");
assert.ok(sourcePrompt.message.includes("RAG"));

const detailHtml = formatNodeDetails({
  label: "RAG <Memory>",
  type: "concept",
  galaxy_layer: "active",
  mention_count: 4,
  importance: 0.8,
  source: "test",
  last_seen_at: "2026-01-02",
  content: "retrieval <augmented>",
  relation_counts: { total: 2, related: 1, context: 1 },
  provenance: { source: "test", first_seen_at: "2026-01-01", last_seen_at: "2026-01-02" },
  knowledge: [{ id: 1, type: "solution", project: "global", role: "tagged", strength: 0.9, summary: "Use <RAG>" }],
});
assert.ok(detailHtml.includes("RAG &lt;Memory&gt;"));
assert.ok(detailHtml.includes("Content Source"));
assert.ok(!detailHtml.includes("Use <RAG>"));

assert.equal(
  timelineCutoffFromPercent(
    { start: "2026-01-01T00:00:00+00:00", end: "2026-01-11T00:00:00+00:00" },
    50,
  ),
  "2026-01-06T00:00:00.000Z",
);
assert.equal(timelineCutoffFromPercent({}, 50), null);
assert.equal(renderPromptText({ message: "要不要查看来源？" }), "要不要查看来源？");
assert.equal(renderPromptText(null), "");

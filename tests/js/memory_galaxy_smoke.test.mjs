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
  .replace(/^import[\s\S]*?from\s+"\.\/memory-galaxy-systems\.js";\r?\n/, "")
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

const viewStateHelperPath = resolve("src/tools/memory_graph_viewer_assets/memory-galaxy-view-state.js");
const viewStateHelperSource = readFileSync(viewStateHelperPath, "utf8").replaceAll("export function ", "function ");
const viewStateContext = { exports: {} };
vm.runInNewContext(
  `${viewStateHelperSource}
exports.createGalaxyViewState = createGalaxyViewState;
exports.selectGalaxySystem = selectGalaxySystem;
exports.selectSolarPlanet = selectSolarPlanet;
exports.pauseGalaxyMotionForSelection = pauseGalaxyMotionForSelection;
exports.resumeGalaxyMotionFromBlank = resumeGalaxyMotionFromBlank;`,
  viewStateContext,
  { filename: viewStateHelperPath },
);
const { createGalaxyViewState, selectGalaxySystem, selectSolarPlanet, pauseGalaxyMotionForSelection, resumeGalaxyMotionFromBlank } = viewStateContext.exports;

const viewerSource = readFileSync(resolve("src/tools/memory_graph_viewer_assets/viewer.js"), "utf8");
assert.match(viewerSource, /enteredSolar/);
assert.match(viewerSource, /enteredPlanet/);
assert.doesNotMatch(viewerSource, /result\.entered(?!Solar|Planet)/);
assert.match(viewerSource, /influence-stack/);
assert.match(viewerSource, /influence-bar-fill/);
assert.match(viewerSource, /Trajectory/);

const rendererHelperPath = resolve("src/tools/memory_graph_viewer_assets/memory-galaxy-renderer.js");
const rendererHelperSource = readFileSync(rendererHelperPath, "utf8").replaceAll("export function ", "function ");
const rendererContext = { exports: {} };
vm.runInNewContext(
  `${rendererHelperSource}
exports.createMemoryGalaxyRenderer = createMemoryGalaxyRenderer;
exports.advanceGalaxyAnimationNodes = advanceGalaxyAnimationNodes;
exports.dynamicLabelAnchor = dynamicLabelAnchor;
exports.buildDeterministicStarfield = buildDeterministicStarfield;
exports.systemLabelLines = systemLabelLines;`,
  rendererContext,
  { filename: rendererHelperPath },
);
const {
  createMemoryGalaxyRenderer,
  advanceGalaxyAnimationNodes,
  dynamicLabelAnchor,
  buildDeterministicStarfield,
  systemLabelLines,
} = rendererContext.exports;

const starsA = buildDeterministicStarfield("fixture", 4, { minX: 0, maxX: 10, minY: 0, maxY: 10 });
const starsB = buildDeterministicStarfield("fixture", 4, { minX: 0, maxX: 10, minY: 0, maxY: 10 });
assert.deepEqual(starsA, starsB);
assert.equal(starsA.length, 4);
assert.ok(starsA.every(star => star.x >= 0 && star.x <= 10 && star.y >= 0 && star.y <= 10));
assert.deepEqual(
  Array.from(systemLabelLines({ label: "Router Core", memorySystem: "router", raw: { memberCount: 12847 } })),
  ["ROUTER CORE", "Route System", "12,847 memories"],
);

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
assert.ok(finalOverview.systems.filter(system => system.key !== "router").every(system => system.animation && Number(system.animation.orbitRadiusX) > 0));
assert.ok(finalOverview.nodes.some(node => node.id === "system:skill" && node.isSystemNode === true && node.systemKey === "skill"));
assert.ok(finalOverview.systems.filter(system => system.key !== "router").every(system => Number(system.orbitAspect || 1) < 1));
assert.ok(finalOverview.systems.filter(system => system.key !== "router").every(system => {
  const aspect = Number(system.orbitAspect || 1);
  return system.miniOrbits.every(orbit => Math.abs(Number(orbit.aspect || 1) - aspect) < 0.0001);
}));
assert.ok(finalOverview.nodes.filter(node => node.animation?.parentSystemKey).every(node => {
  const system = finalOverview.systems.find(item => item.key === node.animation.parentSystemKey);
  const aspect = Number(system?.orbitAspect || 1);
  return Math.abs(Number(node.animation.orbitRadiusY || 0) - Number(node.animation.orbitRadiusX || 0) * aspect) < 0.0001;
}));
assert.ok(finalOverview.nodes.filter(node => node.animation?.parentSystemKey).every(node => Math.abs(Number(node.animation.orbitSpeed || 0)) >= 0.16));
assert.ok(finalOverview.nodes.filter(node => ["galactic-core", "star", "central-star"].includes(node.orbitalRole)).every(node => Number(node.animation?.spinSpeed || 0) === 0));
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
assert.ok(skillSolar.bounds.fitPadding >= 260);
assert.ok(skillSolar.orbits.some(orbit => orbit.kind === "planet"));
assert.ok(skillSolar.nodes.some(node => node.orbitalRole === "central-star"));
assert.ok(skillSolar.satelliteSystems.length >= 1);
assert.ok(skillSolar.satelliteSystems.every(system => system.parentId && system.orbits.some(orbit => orbit.kind === "satellite")));
assert.ok(skillSolar.nodes.some(node => node.orbitalRole === "satellite"));
assert.ok(skillSolar.nodes.every(node => node.animation && Number.isFinite(node.animation.orbitSpeed) && Number.isFinite(node.animation.spinSpeed)));
assert.ok(skillSolar.nodes.some(node => node.orbitalRole === "satellite" && node.animation.parentNodeId));
assert.ok(skillSolar.orbits.every(orbit => Number(orbit.aspect || 1) > 0 && Number(orbit.aspect || 1) <= 1));
assert.ok(skillSolar.satelliteSystems.every(system => Number(system.aspect || 1) > 0 && Number(system.aspect || 1) <= 1));
assert.ok(skillSolar.satelliteSystems.every(system => system.orbits.every(orbit => Number(orbit.aspect || 1) > 0 && Number(orbit.aspect || 1) <= 1)));
assert.ok(skillSolar.nodes.filter(node => node.orbitalRole === "planet").every(node => Math.abs(node.animation.orbitRadiusX - Math.hypot(node.animation.orbitRadiusX, 0)) < 0.0001));
assert.ok(skillSolar.nodes.filter(node => node.orbitalRole === "planet").every(node => node.animation.orbitRadiusX >= 300 && node.animation.orbitRadiusY < node.animation.orbitRadiusX));
assert.ok(skillSolar.nodes.some(node => node.orbitalRole === "planet" && node.childCount > 0));
assert.ok(skillSolar.nodes.filter(node => node.orbitalRole === "planet").length >= 2);
assert.ok(skillSolar.nodes.find(node => node.orbitalRole === "central-star")?.renderRadius >= 84);
assert.equal(skillSolar.nodes.find(node => node.orbitalRole === "central-star")?.isSolarCenterStar, true);
assert.ok(skillSolar.nodes.filter(node => node.orbitalRole === "planet" && Number(node.childCount || 0) > 0).every(node => node.isPlanetSystemNode === true));
assert.ok(skillSolar.nodes.filter(node => node.isPlanetSystemNode).every(node => systemLabelLines(node)[1] === "Planet System"));
assert.ok(skillSolar.nodes.filter(node => node.isPlanetSystemNode).every(node => Number(node.animation?.spinSpeed || 0) === 0));
assert.ok(skillSolar.nodes.filter(node => node.isPlanetSystemNode).every(node => {
  const orbitAspectForNode = Number(node.animation.orbitRadiusY || 0) / Number(node.animation.orbitRadiusX || 1);
  return Math.abs(Number(node.visualOrbitAspect || 0) - orbitAspectForNode) < 0.0001;
}));
assert.ok(skillSolar.nodes.filter(node => node.isPlanetSystemNode).every(node => {
  return skillSolar.orbits.some(orbit => {
    const rx = Number(orbit.radius || 0);
    const ry = rx * Number(orbit.aspect || 1);
    const normalized = (node.x * node.x) / (rx * rx) + (node.y * node.y) / (ry * ry);
    return Math.abs(normalized - 1) < 0.0001;
  });
}));
{
  const visibleIds = new Set(skillSolar.nodes.map(node => String(node.id)));
  assert.ok(skillSolar.links.length < orbitalGalaxy.links.length);
  assert.ok(skillSolar.links.every(link => visibleIds.has(String(link.source?.id || link.source)) && visibleIds.has(String(link.target?.id || link.target))));
}

const skillPlanet = buildPlanetSatelliteLayout(orbitalGalaxy, "skill", "skill", { nodeScale: 0.5, width: 1200, height: 800 });
assert.equal(skillPlanet.view, "planet");
assert.equal(skillPlanet.systemKey, "skill");
assert.ok(skillPlanet.bounds.fitPadding >= 260);
assert.equal(skillPlanet.planetId, "skill");
assert.ok(skillPlanet.orbits.some(orbit => orbit.kind === "direct-moon"));
assert.ok(skillPlanet.orbits.some(orbit => orbit.kind === "evidence"));
assert.ok(skillPlanet.nodes.some(node => node.orbitalRole === "central-planet"));
assert.ok(skillPlanet.orbits.every(orbit => Number(orbit.aspect || 1) > 0 && Number(orbit.aspect || 1) < 1));
assert.ok(skillPlanet.nodes.filter(node => node.orbitalRole !== "central-planet").every(node => node.animation.orbitRadiusY < node.animation.orbitRadiusX));
assert.ok(skillPlanet.nodes.filter(node => node.orbitalRole !== "central-planet").some(node => Number(node.animation.orbitSpeed || 0) !== 0 && Number(node.animation.spinSpeed || 0) !== 0));
{
  const orbiting = skillPlanet.nodes.filter(node => node.orbitalRole !== "central-planet");
  const angles = orbiting.map(node => Math.round(Math.atan2(node.y, node.x) * 100) / 100);
  assert.ok(new Set(angles).size > 2);
}

const crowdedSolarFixture = {
  metadata: { type_counts: {}, timeline: {} },
  elements: {
    nodes: [
      { data: { id: "router-crowded", label: "Router Crowded", type: "pattern", content: "routing dispatch", mention_count: 50, importance: 2, galaxy_layer: "core", knowledge: [] } },
      { data: { id: "skill-hub", label: "Skill Hub", type: "capability", content: "skill workflow trigger", mention_count: 20, importance: 1.3, galaxy_layer: "active", knowledge: [] } },
      ...Array.from({ length: 8 }, (_, index) => ({
        data: {
          id: `skill-child-${index}`,
          label: `skill child ${index}`,
          type: "concept",
          content: "skill child concept",
          mention_count: 6 - Math.min(index, 5),
          importance: 0.6,
          galaxy_layer: "knowledge",
          knowledge: [],
        },
      })),
    ],
    edges: [
      { data: { id: "crowded-route", source: "router-crowded", target: "skill-hub", relation: "routes", weight: 10 } },
      ...Array.from({ length: 8 }, (_, index) => ({
        data: { id: `crowded-edge-${index}`, source: "skill-hub", target: `skill-child-${index}`, relation: "related", weight: 8 - index * 0.2 },
      })),
    ],
  },
};
const crowdedSolar = buildSolarSystemLayout(convertGraphToGalaxy(crowdedSolarFixture), "skill", { nodeScale: 0.48, width: 1200, height: 800 });
assert.ok(crowdedSolar.satelliteSystems.every(system => system.nodes.length <= 6));
assert.ok(crowdedSolar.satelliteSystems.some(system => system.nodes.length > 3));
assert.ok(crowdedSolar.nodes.filter(node => node.orbitalRole === "planet").length >= 3);
assert.ok(crowdedSolar.nodes.filter(node => node.orbitalRole === "planet").every(node => Number(node.childCount || 0) <= 6));
assert.ok(crowdedSolar.orbits.length >= Math.ceil(crowdedSolar.nodes.filter(node => node.orbitalRole === "planet").length / 4));
assert.ok(crowdedSolar.nodes.filter(node => node.isPlanetSystemNode).every(node => {
  return crowdedSolar.orbits.some(orbit => {
    const rx = Number(orbit.radius || 0);
    const ry = rx * Number(orbit.aspect || 1);
    const normalized = (node.x * node.x) / (rx * rx) + (node.y * node.y) / (ry * ry);
    return Math.abs(normalized - 1) < 0.0001;
  });
}));
assert.ok(crowdedSolar.satelliteSystems.every(system => Number(system.footprintRadius || 0) >= Number(system.radius || 0) + 34));
for (let i = 0; i < crowdedSolar.satelliteSystems.length; i += 1) {
  for (let j = i + 1; j < crowdedSolar.satelliteSystems.length; j += 1) {
    const a = crowdedSolar.satelliteSystems[i];
    const b = crowdedSolar.satelliteSystems[j];
    const distance = Math.hypot(a.x - b.x, a.y - b.y);
    assert.ok(distance >= Number(a.footprintRadius || 0) + Number(b.footprintRadius || 0));
  }
}
{
  const minX = Math.min(...crowdedSolar.satelliteSystems.map(system => system.x - Number(system.footprintRadius || 0)));
  const maxX = Math.max(...crowdedSolar.satelliteSystems.map(system => system.x + Number(system.footprintRadius || 0)));
  const minY = Math.min(...crowdedSolar.satelliteSystems.map(system => system.y - Number(system.footprintRadius || 0) * Number(system.aspect || 1)));
  const maxY = Math.max(...crowdedSolar.satelliteSystems.map(system => system.y + Number(system.footprintRadius || 0) * Number(system.aspect || 1)));
  assert.ok(crowdedSolar.bounds.height <= (maxY - minY) * 1.75);
}
assert.ok(new Set(crowdedSolar.satelliteSystems.map(system => Math.round(Number(system.aspect || 0) * 1000))).size > 1);
assert.ok(new Set(crowdedSolar.satelliteSystems.map(system => Math.round(Number(system.radius || 0) * 1000))).size > 1);
assert.ok(new Set(crowdedSolar.satelliteSystems.flatMap(system => system.nodes.map(node => Math.round(Math.abs(Number(node.animation.orbitSpeed || 0)) * 1000)))).size > 1);
assert.ok(crowdedSolar.satelliteSystems.every(system => system.orbits.every(orbit => Math.abs(Number(orbit.aspect || 0) - Number(system.aspect || 0)) < 0.0001)));
assert.ok(crowdedSolar.satelliteSystems.every(system => system.nodes.every(node => Math.abs(Number(node.animation.orbitRadiusY || 0) - Number(node.animation.orbitRadiusX || 0) * Number(system.aspect || 0)) < 0.0001)));
assert.ok(crowdedSolar.satelliteSystems.every(system => /^#[0-9a-f]{6}$/i.test(String(system.color || ""))));
assert.ok(crowdedSolar.satelliteSystems.every(system => system.nodes.every(node => {
  const distance = Math.hypot(node.x - system.x, node.y - system.y);
  return distance > 0;
})));
assert.ok(crowdedSolar.nodes.find(node => node.orbitalRole === "central-star")?.renderRadius >= 84);

const denseSolarOrbitFixture = {
  metadata: { type_counts: {}, timeline: {} },
  elements: {
    nodes: [
      { data: { id: "router-dense-solar", label: "Router Dense Solar", type: "pattern", content: "routing dispatch", mention_count: 80, importance: 2, galaxy_layer: "core", knowledge: [] } },
      ...Array.from({ length: 10 }, (_, index) => ({
        data: {
          id: `dense-planet-${index}`,
          label: `dense planet ${index}`,
          type: index % 3 === 0 ? "capability" : "concept",
          content: "skill dense planet workflow",
          mention_count: 30 - index,
          importance: 1.1 - index * 0.04,
          galaxy_layer: "active",
          knowledge: [],
        },
      })),
      ...Array.from({ length: 42 }, (_, index) => ({
        data: {
          id: `dense-moon-${index}`,
          label: `dense moon ${index}`,
          type: index % 4 === 0 ? "event" : "concept",
          content: "skill dense satellite context",
          mention_count: 10 - (index % 5),
          importance: 0.45,
          galaxy_layer: "knowledge",
          knowledge: [],
        },
      })),
    ],
    edges: [
      ...Array.from({ length: 10 }, (_, index) => ({
        data: { id: `dense-route-${index}`, source: "router-dense-solar", target: `dense-planet-${index}`, relation: "routes", weight: 10 - index * 0.2 },
      })),
      ...Array.from({ length: 42 }, (_, index) => ({
        data: { id: `dense-moon-edge-${index}`, source: `dense-planet-${index % 10}`, target: `dense-moon-${index}`, relation: "related", weight: 8 - (index % 6) * 0.3 },
      })),
    ],
  },
};
const denseSolar = buildSolarSystemLayout(convertGraphToGalaxy(denseSolarOrbitFixture), "skill", { nodeScale: 0.48, width: 1400, height: 900 });
assert.ok(denseSolar.satelliteSystems.length >= 8);
assert.ok(denseSolar.satelliteSystems.every(system => system.orbits.length <= 4));
assert.ok(denseSolar.satelliteSystems.every(system => Number(system.scaleFactor || 1) === 2));
assert.ok(denseSolar.nodes.filter(node => node.isPlanetSystemNode).every(node => Number(node.renderRadius || 0) >= 22));
{
  const centralStar = denseSolar.nodes.find(node => node.orbitalRole === "central-star");
  const planetSystems = denseSolar.nodes.filter(node => node.isPlanetSystemNode);
  assert.ok(centralStar);
  assert.ok(planetSystems.length > 0);
  assert.ok(Number(centralStar.renderRadius || 0) >= Math.max(...planetSystems.map(node => Number(node.renderRadius || 0))) * 1.42);
  assert.ok(Math.max(...denseSolar.orbits.map(orbit => Number(orbit.radius || 0))) <= 1500);
  assert.ok(denseSolar.satelliteSystems.every(system => Number(system.radius || 0) >= 116 && Number(system.radius || 0) <= 232));
}
for (let i = 0; i < denseSolar.satelliteSystems.length; i += 1) {
  for (let j = i + 1; j < denseSolar.satelliteSystems.length; j += 1) {
    const a = denseSolar.satelliteSystems[i];
    const b = denseSolar.satelliteSystems[j];
    const distance = Math.hypot(a.x - b.x, a.y - b.y);
    assert.ok(distance >= Number(a.footprintRadius || 0) + Number(b.footprintRadius || 0) + 16);
  }
}

const influenceSolarFixture = {
  metadata: { type_counts: {}, timeline: {} },
  elements: {
    nodes: [
      { data: { id: "router-inf", label: "Router Influence", type: "pattern", content: "routing dispatch", mention_count: 90, importance: 2, galaxy_layer: "core", knowledge: [] } },
      { data: { id: "skill-high", label: "High impact skill", type: "capability", content: "skill workflow trigger", mention_count: 40, importance: 1.4, galaxy_layer: "active", knowledge: [] } },
      { data: { id: "skill-mid", label: "Mid impact skill", type: "concept", content: "skill context", mention_count: 12, importance: 0.9, galaxy_layer: "knowledge", knowledge: [] } },
      { data: { id: "skill-low", label: "Low impact skill", type: "concept", content: "skill context", mention_count: 2, importance: 0.2, galaxy_layer: "knowledge", knowledge: [] } },
      { data: { id: "skill-low-2", label: "Low impact skill 2", type: "concept", content: "skill context", mention_count: 1, importance: 0.1, galaxy_layer: "knowledge", knowledge: [] } },
    ],
    edges: [
      { data: { id: "inf-route", source: "router-inf", target: "skill-high", relation: "routes", weight: 10 } },
      { data: { id: "inf-mid", source: "skill-high", target: "skill-mid", relation: "related", weight: 7 } },
      { data: { id: "inf-low", source: "skill-high", target: "skill-low", relation: "related", weight: 4 } },
      { data: { id: "inf-low-2", source: "skill-mid", target: "skill-low-2", relation: "related", weight: 3 } },
    ],
  },
};
const influenceSolar = buildSolarSystemLayout(convertGraphToGalaxy(influenceSolarFixture), "skill", { nodeScale: 0.48, width: 1200, height: 800 });
const influencePlanets = influenceSolar.nodes.filter(node => node.orbitalRole === "planet");
const highPlanet = influencePlanets.find(node => node.id === "skill-high");
const lowPlanet = influenceSolar.nodes.find(node => node.id === "skill-low" || node.id === "skill-low-2");
assert.ok(highPlanet);
assert.ok(lowPlanet);
assert.ok(highPlanet.renderRadius > lowPlanet.renderRadius);
{
  const byParent = new Map(influenceSolar.satelliteSystems.map(system => [system.parentId, system]));
  const highSystem = byParent.get("skill-high");
  const lowSystem = byParent.get(lowPlanet.id);
  if (highSystem && lowSystem) {
    assert.ok(Number(highSystem.radius || 0) >= Number(lowSystem.radius || 0));
    assert.ok(highSystem.nodes.length >= lowSystem.nodes.length);
  }
}

const cometOverlay = buildCometOverlayLayout(finalOverview, [{
  id: "comet:test",
  label: "Memory Galaxy Redesign",
  comet_type: "active_task",
  trajectory: ["preference", "skill", "harness", "rule"],
  influenced_systems: [{ system: "skill", weight: 0.92 }, { system: "harness", weight: 0.84 }],
}, {
  id: "comet:second",
  label: "Verification Trail",
  comet_type: "verification",
  trajectory: ["harness", "source"],
  influenced_systems: [{ system: "harness", weight: 0.82 }, { system: "source", weight: 0.62 }],
}]);
assert.equal(cometOverlay.comets.length, 2);
assert.ok(cometOverlay.comets[0].influences.some(item => item.system === "skill" && item.weight > 0.9));
assert.ok(cometOverlay.comets[0].tail.length >= 2);
assert.ok(Array.isArray(cometOverlay.comets[0].trailHistory));
assert.equal(cometOverlay.comets[0].influences.find(item => item.system === "skill")?.color, systemColor("skill"));
for (const comet of cometOverlay.comets) {
  assert.ok(Number.isFinite(comet.head.x));
  assert.ok(Number.isFinite(comet.head.y));
  assert.ok(comet.hitRadius >= 32);
  for (const influence of comet.influences) {
    assert.ok(Math.hypot(comet.head.x - influence.x, comet.head.y - influence.y) > influence.radius + comet.hitRadius);
  }
}

{
  const tickerCallbacks = [];
  class FakeContainer {
    constructor() {
      this.children = [];
      this.scale = { set: value => { this.scaleValue = value; } };
      this.position = { set: (x, y) => { this.positionValue = { x, y }; } };
    }
    addChild(...children) { this.children.push(...children); return children.at(-1); }
    removeChildren() { const children = this.children; this.children = []; return children; }
    on() {}
  }
  class FakeGraphics extends FakeContainer {
    constructor() { super(); this.commands = []; }
    clear() { this.commands = []; return this; }
    circle(...args) { this.commands.push({ name: "circle", args }); return this; }
    ellipse(...args) { this.commands.push({ name: "ellipse", args }); return this; }
    fill(...args) { this.commands.push({ name: "fill", args }); return this; }
    stroke(...args) { this.commands.push({ name: "stroke", args }); return this; }
    moveTo(...args) { this.commands.push({ name: "moveTo", args }); return this; }
    lineTo(...args) { this.commands.push({ name: "lineTo", args }); return this; }
    quadraticCurveTo(...args) { this.commands.push({ name: "quadraticCurveTo", args }); return this; }
    destroy() {}
  }
  class FakeText extends FakeContainer { destroy() {} }
  const stage = new FakeContainer();
  const renderer = createMemoryGalaxyRenderer({
    PIXI: { Container: FakeContainer, Graphics: FakeGraphics, Text: FakeText },
    app: { screen: { width: 1200, height: 800 }, ticker: { add: callback => tickerCallbacks.push(callback) } },
    stage,
  });
  renderer.draw(cometOverlay, { showComets: true, animationSpeed: 1 }, {});
  const root = stage.children[0];
  const cometLayer = root.children[2];
  const cometGraphics = cometLayer.children.filter(child => child.commands?.length);
  const visibleComet = cometGraphics.find(child => child.commands.some(command => command.name === "stroke"));
  assert.ok(visibleComet);
  const circles = visibleComet.commands.filter(command => command.name === "circle");
  assert.ok(circles.length >= 3);
  assert.ok(visibleComet.commands.some(command => command.name === "quadraticCurveTo"));
  const strokeColors = visibleComet.commands
    .filter(command => command.name === "stroke")
    .map(command => command.args[0]?.color)
    .filter(color => Number.isFinite(color));
  assert.ok(strokeColors.includes(0x22d3ee));
  assert.ok(strokeColors.includes(0x34d399));
  const hitCircle = cometGraphics.find(child => child.commands.some(command => command.name === "fill" && command.args[0]?.alpha === 0.001))
    ?.commands.find(command => command.name === "circle");
  assert.ok(hitCircle);
  assert.ok(hitCircle.args[2] >= 32);
  const initialCore = circles.find(command => command.args[2] === 34);
  assert.ok(initialCore);
  tickerCallbacks.forEach(callback => callback({ deltaMS: 240 }));
  const updatedVisibleComet = cometLayer.children
    .filter(child => child.commands?.length)
    .find(child => child.commands.some(command => command.name === "stroke"));
  const updatedCore = updatedVisibleComet?.commands
    .filter(command => command.name === "circle")
    .find(command => command.args[2] === 34);
  assert.ok(updatedCore);
  assert.notEqual(Math.round(updatedCore.args[0] * 1000), Math.round(initialCore.args[0] * 1000));
}

const galaxyClickState = createGalaxyViewState();
let systemTap = { key: null, time: 0 };
const firstTap = selectGalaxySystem(galaxyClickState, "skill", {
  now: 1000,
  lastSystemTap: systemTap,
  doubleTapMs: 420,
});
systemTap = firstTap.lastSystemTap;
assert.equal(firstTap.enteredSolar, false);
assert.equal(galaxyClickState.view, "galaxy");
const secondTap = selectGalaxySystem(galaxyClickState, "skill", {
  now: 2000,
  lastSystemTap: systemTap,
  doubleTapMs: 420,
});
assert.equal(secondTap.enteredSolar, true);
assert.equal(galaxyClickState.view, "solar");

const forcedTapState = createGalaxyViewState();
const forcedTap = selectGalaxySystem(forcedTapState, "skill", {
  now: 1000,
  lastSystemTap: { key: null, time: 0 },
  forceEnter: true,
});
assert.equal(forcedTap.enteredSolar, true);
assert.equal(forcedTapState.view, "solar");

const pauseState = createGalaxyViewState();
pauseState.animationSpeed = 1.35;
pauseState.motionEnabled = true;
pauseState.selectedNodeId = "old-node";
pauseState.selectedSystem = "skill";
pauseGalaxyMotionForSelection(pauseState, "node-1");
assert.equal(pauseState.animationSpeed, 0);
assert.equal(pauseState.motionEnabled, false);
assert.equal(pauseState.motionResumeSpeed, 1.35);
assert.equal(pauseState.selectedNodeId, "node-1");
assert.equal(pauseState.selectedSystem, "skill");

resumeGalaxyMotionFromBlank(pauseState);
assert.equal(pauseState.animationSpeed, 1.35);
assert.equal(pauseState.motionEnabled, true);
assert.equal(pauseState.selectedNodeId, null);
assert.equal(pauseState.selectedSystem, null);
assert.equal(pauseState.hoveredNodeId, null);

const defaultResumeState = createGalaxyViewState();
defaultResumeState.animationSpeed = 0;
resumeGalaxyMotionFromBlank(defaultResumeState);
assert.equal(defaultResumeState.animationSpeed, 1);
assert.equal(defaultResumeState.motionEnabled, true);

const solarResumeState = createGalaxyViewState();
solarResumeState.view = "solar";
solarResumeState.selectedSystem = "skill";
solarResumeState.selectedNodeId = "planet-1";
solarResumeState.selectedPlanet = "planet-1";
solarResumeState.animationSpeed = 0;
solarResumeState.motionResumeSpeed = 1.25;
resumeGalaxyMotionFromBlank(solarResumeState);
assert.equal(solarResumeState.view, "solar");
assert.equal(solarResumeState.selectedSystem, "skill");
assert.equal(solarResumeState.selectedPlanet, null);
assert.equal(solarResumeState.selectedNodeId, null);
assert.equal(solarResumeState.animationSpeed, 1.25);
assert.equal(solarResumeState.motionEnabled, true);

const solarClickState = createGalaxyViewState();
solarClickState.view = "solar";
solarClickState.selectedSystem = "skill";
let planetTap = { id: null, time: 0 };
const firstPlanetTap = selectSolarPlanet(solarClickState, "planet-1", {
  now: 2000,
  lastPlanetTap: planetTap,
  doubleTapMs: 420,
});
planetTap = firstPlanetTap.lastPlanetTap;
assert.equal(firstPlanetTap.enteredPlanet, false);
assert.equal(solarClickState.view, "solar");
const secondPlanetTap = selectSolarPlanet(solarClickState, "planet-1", {
  now: 3000,
  lastPlanetTap: planetTap,
  doubleTapMs: 420,
});
assert.equal(secondPlanetTap.enteredPlanet, true);
assert.equal(solarClickState.view, "planet");

const animatedLayout = {
  systems: [{
    key: "skill",
    x: 10,
    y: 0,
    animation: {
      orbitCenterX: 0,
      orbitCenterY: 0,
      orbitRadiusX: 10,
      orbitRadiusY: 10,
      orbitAngle: 0,
      orbitSpeed: Math.PI / 2,
    },
  }],
  nodes: [{
    id: "system:skill",
    isSystemNode: true,
    systemKey: "skill",
    x: 10,
    y: 0,
    animation: {
      orbitCenterX: 10,
      orbitCenterY: 0,
      orbitRadiusX: 0,
      orbitRadiusY: 0,
      orbitAngle: 0,
      orbitSpeed: 0,
      spinSpeed: 0,
    },
  }, {
    id: "planet:skill",
    x: 8,
    y: 0,
    animation: {
      orbitCenterX: 0,
      orbitCenterY: 0,
      orbitRadiusX: 8,
      orbitRadiusY: 8,
      orbitAngle: 0,
      orbitSpeed: Math.PI / 2,
      spinSpeed: 0,
    },
  }, {
    id: "satellite:skill:0",
    x: 10,
    y: 0,
    animation: {
      orbitCenterX: 8,
      orbitCenterY: 0,
      orbitRadiusX: 2,
      orbitRadiusY: 2,
      orbitAngle: 0,
      orbitSpeed: Math.PI / 2,
      spinSpeed: 0,
      parentNodeId: "planet:skill",
    },
  }],
  satelliteSystems: [{
    parentId: "planet:skill",
    x: 8,
    y: 0,
    radius: 2,
    orbits: [{ kind: "satellite", radius: 2 }],
  }],
  comets: [{
    head: { x: 100, y: 0 },
    tail: [],
    trailHistory: [{ x: 90, y: 0, alpha: 0.72 }],
    path: [{ x: 100, y: 0 }, { x: 0, y: 100 }],
    animation: { pathProgress: 0, pathSpeed: 1 },
  }],
};
assert.equal(advanceGalaxyAnimationNodes(animatedLayout, 1, new Map(), 1), true);
assert.ok(Math.abs(animatedLayout.systems[0].x) < 0.0001);
assert.ok(Math.abs(animatedLayout.systems[0].y - 10) < 0.0001);
assert.ok(Math.abs(animatedLayout.nodes[0].x - animatedLayout.systems[0].x) < 0.0001);
assert.ok(Math.abs(animatedLayout.nodes[1].x) < 0.0001);
assert.ok(Math.abs(animatedLayout.nodes[1].y - 8) < 0.0001);
assert.ok(Math.abs(animatedLayout.nodes[2].x - animatedLayout.nodes[1].x) < 2.0001);
assert.ok(Math.abs(animatedLayout.nodes[2].y - (animatedLayout.nodes[1].y + 2)) < 0.0001);
assert.ok(Math.abs(animatedLayout.satelliteSystems[0].x - animatedLayout.nodes[1].x) < 0.0001);
assert.ok(Math.abs(animatedLayout.satelliteSystems[0].y - animatedLayout.nodes[1].y) < 0.0001);
assert.ok(animatedLayout.comets[0].trailHistory[0].alpha < 0.72);
const stationaryLayout = JSON.parse(JSON.stringify(animatedLayout));
advanceGalaxyAnimationNodes(stationaryLayout, 1, new Map(), 0);
assert.equal(stationaryLayout.systems[0].x, animatedLayout.systems[0].x);
assert.equal(stationaryLayout.systems[0].y, animatedLayout.systems[0].y);
assert.equal(stationaryLayout.nodes[1].x, animatedLayout.nodes[1].x);
assert.equal(stationaryLayout.nodes[1].y, animatedLayout.nodes[1].y);

{
  const overviewMotion = buildGalaxyOverviewLayout(orbitalGalaxy, { nodeScale: 0.48 });
  const planet = overviewMotion.nodes.find(node => ["planet", "moon", "evidence"].includes(node.orbitalRole) && node.animation?.parentSystemKey);
  assert.ok(planet);
  const parentBefore = overviewMotion.systems.find(system => system.key === planet.animation.parentSystemKey);
  assert.ok(parentBefore);
  const parentBeforePosition = { x: parentBefore.x, y: parentBefore.y };
  const beforeOffset = { x: planet.x - parentBefore.x, y: planet.y - parentBefore.y };
  advanceGalaxyAnimationNodes(overviewMotion, 1, new Map(), 1);
  const parentAfter = overviewMotion.systems.find(system => system.key === planet.animation.parentSystemKey);
  const planetAfter = overviewMotion.nodes.find(node => node.id === planet.id);
  assert.ok(parentAfter);
  assert.ok(planetAfter);
  assert.notEqual(Math.round(parentAfter.x * 1000) / 1000, Math.round(parentBeforePosition.x * 1000) / 1000);
  assert.notEqual(Math.round((planetAfter.x - parentAfter.x) * 1000) / 1000, Math.round(beforeOffset.x * 1000) / 1000);
}
const animatedSystemNode = {
  ...animatedLayout.nodes[0],
  labelAnchor: { x: 40, y: 0, align: "left" },
};
assert.ok(animatedSystemNode.x !== animatedSystemNode.labelAnchor.x);

{
  const tickerCallbacks = [];
  let removeChildrenCalls = 0;
  let destroyedChildren = 0;
  let animationFrameCallbacks = 0;
  class FakeContainer {
    constructor() {
      this.children = [];
      this.scale = { set: value => { this.scaleValue = value; } };
      this.position = { set: (x, y) => { this.positionValue = { x, y }; } };
    }
    addChild(...children) {
      this.children.push(...children);
      return children.at(-1);
    }
    removeChildren() {
      removeChildrenCalls += 1;
      const children = this.children;
      this.children = [];
      return children;
    }
    on() {}
  }
  class FakeGraphics extends FakeContainer {
    constructor() {
      super();
      this.commands = [];
    }
    clear() { this.commands = []; return this; }
    circle(...args) { this.commands.push({ name: "circle", args }); return this; }
    ellipse(...args) { this.commands.push({ name: "ellipse", args }); return this; }
    fill() { return this; }
    stroke() { return this; }
    moveTo(...args) { this.commands.push({ name: "moveTo", args }); return this; }
    lineTo(...args) { this.commands.push({ name: "lineTo", args }); return this; }
    quadraticCurveTo(...args) { this.commands.push({ name: "quadraticCurveTo", args }); return this; }
    destroy() { destroyedChildren += 1; }
  }
  class FakeText extends FakeContainer {
    constructor({ text, style }) {
      super();
      this.text = text;
      this.style = style || {};
      this.width = String(text).length * 8;
      this.height = 16;
      this.anchor = { set: () => {} };
    }
    destroy() { destroyedChildren += 1; }
  }
  const stage = new FakeContainer();
  const fakeApp = {
    screen: { width: 800, height: 600 },
    ticker: { add: callback => tickerCallbacks.push(callback) },
  };
  const fakeRenderer = createMemoryGalaxyRenderer({
    PIXI: { Container: FakeContainer, Graphics: FakeGraphics, Text: FakeText },
    app: fakeApp,
    stage,
    onAnimationFrame: () => { animationFrameCallbacks += 1; },
  });
  const perfLayout = JSON.parse(JSON.stringify(animatedLayout));
  perfLayout.view = "galaxy";
  perfLayout.nodes[1].label = "Animated planet";
  perfLayout.nodes[1].renderRadius = 8;
  fakeRenderer.draw(perfLayout, { selectedNodeId: perfLayout.nodes[1].id, hoveredNodeId: null, labelMode: "medium", animationSpeed: 1 }, {});
  const afterInitialDrawRemoveCalls = removeChildrenCalls;
  const afterInitialDestroyedChildren = destroyedChildren;
  const root = stage.children[0];
  const orbitLayer = root.children.find(layer => layer.children.some(child => child.commands?.some(command => {
    return command.name === "ellipse"
      && Math.abs(command.args[0] - perfLayout.systems[0].x) < 0.0001
      && Math.abs(command.args[1] - perfLayout.systems[0].y) < 0.0001;
  })));
  const labelLayer = root.children.find(layer => layer.children.some(child => child.text === "Animated planet"));
  const animatedLabel = labelLayer.children.find(child => child.text === "Animated planet");
  const animatedSystemGuide = orbitLayer.children.find(child => child.commands?.some(command => {
    return command.name === "ellipse"
      && Math.abs(command.args[0] - perfLayout.systems[0].x) < 0.0001
      && Math.abs(command.args[1] - perfLayout.systems[0].y) < 0.0001;
  }));
  assert.ok(animatedLabel);
  assert.ok(animatedSystemGuide);
  for (let frame = 0; frame < 12; frame += 1) {
    tickerCallbacks.forEach(callback => callback({ deltaMS: 16.67 }));
  }
  assert.ok(animationFrameCallbacks > 0);
  assert.equal(removeChildrenCalls, afterInitialDrawRemoveCalls);
  assert.equal(destroyedChildren, afterInitialDestroyedChildren);
  assert.ok(Math.abs(animatedLabel.x - dynamicLabelAnchor(perfLayout.nodes[1]).x) < 0.0001);
  assert.ok(Math.abs(animatedLabel.y - dynamicLabelAnchor(perfLayout.nodes[1]).y) < 0.0001);
  const guideEllipse = animatedSystemGuide.commands.find(command => command.name === "ellipse");
  assert.ok(Math.abs(guideEllipse.args[0] - perfLayout.systems[0].x) < 0.0001);
  assert.ok(Math.abs(guideEllipse.args[1] - perfLayout.systems[0].y) < 0.0001);
  const removeChildrenAfterShortRun = removeChildrenCalls;
  const destroyedAfterShortRun = destroyedChildren;
  for (let frame = 0; frame < 600; frame += 1) {
    tickerCallbacks.forEach(callback => callback({ deltaMS: 16.67 }));
  }
  assert.equal(removeChildrenCalls, removeChildrenAfterShortRun);
  assert.equal(destroyedChildren, destroyedAfterShortRun);
}

{
  const tickerCallbacks = [];
  class FakeContainer {
    constructor() {
      this.children = [];
      this.scale = { set: value => { this.scaleValue = value; } };
      this.position = { set: (x, y) => { this.positionValue = { x, y }; } };
    }
    addChild(...children) { this.children.push(...children); return children.at(-1); }
    removeChildren() { const children = this.children; this.children = []; return children; }
    on() {}
  }
  class FakeGraphics extends FakeContainer {
    constructor() { super(); this.commands = []; }
    clear() { this.commands = []; return this; }
    circle(...args) { this.commands.push({ name: "circle", args }); return this; }
    ellipse(...args) { this.commands.push({ name: "ellipse", args }); return this; }
    fill() { return this; }
    stroke(...args) { this.commands.push({ name: "stroke", args }); return this; }
    moveTo(...args) { this.commands.push({ name: "moveTo", args }); return this; }
    lineTo(...args) { this.commands.push({ name: "lineTo", args }); return this; }
    quadraticCurveTo(...args) { this.commands.push({ name: "quadraticCurveTo", args }); return this; }
    destroy() {}
  }
  class FakeText extends FakeContainer {
    constructor({ text, style }) {
      super();
      this.text = text;
      this.style = style || {};
      this.width = String(text).length * 8;
      this.height = 16;
      this.anchor = { set: () => {} };
    }
    destroy() {}
  }
  const stage = new FakeContainer();
  const renderer = createMemoryGalaxyRenderer({
    PIXI: { Container: FakeContainer, Graphics: FakeGraphics, Text: FakeText },
    app: { screen: { width: 1200, height: 800 }, ticker: { add: callback => tickerCallbacks.push(callback) } },
    stage,
  });
  const solarLabelLayout = JSON.parse(JSON.stringify(denseSolar));
  renderer.draw(solarLabelLayout, { selectedNodeId: null, hoveredNodeId: null, labelMode: "medium", animationSpeed: 1 }, {});
  const root = stage.children[0];
  const labelLayer = root.children.find(layer => layer.children.some(child => child.text === "DENSE PLANET 0"));
  assert.ok(labelLayer);
  const planetLabel = labelLayer.children.find(child => child.text === "DENSE PLANET 0");
  assert.ok(planetLabel);
  assert.ok(Number(planetLabel.style.fontSize || 0) >= 15 && Number(planetLabel.style.fontSize || 0) <= 18);
  const centerLabel = labelLayer.children.find(child => child.text === "SKILL SYSTEM");
  assert.ok(centerLabel);
  assert.equal(centerLabel.style.fontSize, planetLabel.style.fontSize);
  const planetSubtitle = labelLayer.children.find(child => child.text === "Planet System");
  assert.ok(planetSubtitle);
  assert.ok(Number(planetSubtitle.style.fontSize || 0) >= 10 && Number(planetSubtitle.style.fontSize || 0) <= 12);
  const leaderLayer = root.children.find(layer => layer.children.some(child => child.commands?.some(command => command.name === "moveTo")));
  const leader = leaderLayer.children.find(child => child.commands?.some(command => command.name === "moveTo") && child.commands?.filter(command => command.name === "lineTo").length >= 2);
  assert.ok(leader);
  const move = leader.commands.find(command => command.name === "moveTo");
  const lines = leader.commands.filter(command => command.name === "lineTo");
  const firstLength = Math.hypot(lines[0].args[0] - move.args[0], lines[0].args[1] - move.args[1]);
  const secondLength = Math.hypot(lines[1].args[0] - lines[0].args[0], lines[1].args[1] - lines[0].args[1]);
  assert.ok(firstLength >= 32 && firstLength <= 140);
  assert.ok(secondLength >= 58 && secondLength <= 104);
  const labeledPlanet = solarLabelLayout.nodes.find(node => node.label === "dense planet 0");
  assert.ok(labeledPlanet);
  assert.ok(Math.hypot(move.args[0] - labeledPlanet.x, move.args[1] - labeledPlanet.y) >= Number(labeledPlanet.renderRadius || 0));
  const nodeLayer = root.children[4];
  const planetHit = nodeLayer.children.find(child => {
    const circle = child.commands?.find(command => command.name === "circle");
    return circle
      && Math.abs(circle.args[0] - labeledPlanet.x) < 0.0001
      && Math.abs(circle.args[1] - labeledPlanet.y) < 0.0001
      && circle.args[2] > Number(labeledPlanet.renderRadius || 0);
  });
  assert.ok(planetHit);
  const hitCircle = planetHit.commands.find(command => command.name === "circle");
  assert.ok(hitCircle.args[2] <= Number(labeledPlanet.renderRadius || 0) + 18);
}

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

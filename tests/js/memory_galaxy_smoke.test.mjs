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
exports.groupNeighborRelations = groupNeighborRelations;`,
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
} = context.exports;

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

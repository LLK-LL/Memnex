import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import vm from "node:vm";

const helperPath = resolve("src/tools/memory_graph_viewer_assets/memory-galaxy-core.js");
const helperSource = readFileSync(helperPath, "utf8").replaceAll("export function ", "function ");
const context = { exports: {} };
vm.runInNewContext(
  `${helperSource}\nexports.convertGraphToGalaxy = convertGraphToGalaxy;\nexports.filterGalaxy = filterGalaxy;\nexports.buildFocusGalaxy = buildFocusGalaxy;\nexports.buildExpandedGalaxy = buildExpandedGalaxy;\nexports.buildEditIntent = buildEditIntent;`,
  context,
  { filename: helperPath },
);

const { convertGraphToGalaxy, filterGalaxy, buildFocusGalaxy, buildExpandedGalaxy, buildEditIntent } = context.exports;

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

const intent = buildEditIntent("add_relation", { source: "p1", target: "c1", relation: "related" });
assert.equal(intent.action, "add_relation");
assert.equal(intent.payload.source, "p1");
assert.ok(intent.created_at);

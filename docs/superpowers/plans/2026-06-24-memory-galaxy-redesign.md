# Memory Galaxy Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the existing memory graph viewer with a performant, draggable 2D galaxy map and a spherical 3D memory galaxy, while adding a renderer-independent event bridge for future agent and voice interactions.

**Architecture:** Keep the static export model: Python exports `graph.json` plus browser assets, and the viewer runs locally with no backend. Move layout, filtering, cache metadata, and interaction-event logic into testable JavaScript helper modules. Directly overwrite the old 2D Cytoscape view with the new 2D galaxy; keep 3D as the spherical galaxy view; store viewer layout/cache artifacts under `D:\TotalAgentMemory\memory-galaxy-cache` by default.

**Tech Stack:** Python 3, pytest, static HTML/CSS/JavaScript ES modules, PixiJS for 2D galaxy rendering, Three.js for 3D spherical rendering, Node.js smoke tests.

---

## Confirmed Decisions

- **Old 2D viewer behavior:** Directly overwrite it. `index.html` and `viewer.js` become the 2D galaxy experience. Do not keep the old Cytoscape graph as a runtime mode.
- **Cache location:** Use `D:\TotalAgentMemory\memory-galaxy-cache` as the default external cache root. The viewer export should include cache metadata, and browser-side layout caches should key localStorage entries with this root and graph identity.
- **Lumi boundary:** Do not modify `F:\Users\Administrator\Desktop\Jarvis\tmp_lumi_os_research`.
- **Existing dirty work:** Preserve and account for the current uncommitted `src/tools/memory_graph_viewer_assets/viewer-3d.js` focused expansion changes unless the user explicitly asks to discard them.

## File Structure

- Modify: `src/tools/memory_graph_viewer_export.py`
  - Add cache-root metadata, graph identity, stable layout seed, relation counts, and source/provenance fields.
  - Copy new viewer assets.
- Modify: `tests/test_memory_graph_viewer_export.py`
  - Assert cache metadata, graph identity, stable layout seed, and copied assets.
- Modify: `src/tools/memory_graph_viewer_assets/memory-galaxy-core.js`
  - Add deterministic 2D galaxy positions, 3D sphere positions, visible subgraph budgets, label gating, neighbor grouping, and cache key helpers.
- Create: `src/tools/memory_graph_viewer_assets/memory-galaxy-events.js`
  - Normalize interaction events and provide local event log / prompt suggestion helpers.
- Create: `src/tools/memory_graph_viewer_assets/viewer-shared.js`
  - Shared DOM, filtering, stats, details, prompt, and timeline helpers for 2D/3D viewers.
- Replace: `src/tools/memory_graph_viewer_assets/index.html`
  - Remove Cytoscape script; load PixiJS and `viewer.js` as an ES module.
- Replace: `src/tools/memory_graph_viewer_assets/viewer.js`
  - Implement the draggable 2D galaxy renderer.
- Modify: `src/tools/memory_graph_viewer_assets/viewer-3d.html`
  - Load Three.js and updated spherical 3D renderer.
- Replace: `src/tools/memory_graph_viewer_assets/viewer-3d.js`
  - Implement the spherical 3D galaxy renderer while preserving focused expansion semantics.
- Modify: `src/tools/memory_graph_viewer_assets/styles.css`
  - Add dark galaxy layout, stable canvas dimensions, compact controls, right-side detail panel, prompt area, and responsive behavior.
- Modify: `tests/js/memory_galaxy_smoke.test.mjs`
  - Extend pure tests for layout, cache keys, label gating, focus budgets, and event normalization.
- Modify: `docs/v12.5.0-memory-graph-viewer.md`
  - Document the new 2D galaxy, 3D spherical galaxy, cache path, and static privacy boundary.

## Task 1: Protect Current State and Baseline Tests

**Files:**
- Inspect: `src/tools/memory_graph_viewer_assets/viewer-3d.js`
- Test: `tests/test_memory_graph_viewer_export.py`
- Test: `tests/js/memory_galaxy_smoke.test.mjs`

- [ ] **Step 1: Confirm current git status**

Run:

```powershell
git status --short
```

Expected: output includes the known dirty files:

```text
 M src/tools/memory_graph_viewer_assets/viewer-3d.js
?? evals/results/
```

If additional unexpected files appear, inspect them before editing and do not revert user changes.

- [ ] **Step 2: Inspect the existing 3D dirty diff**

Run:

```powershell
git diff -- src/tools/memory_graph_viewer_assets/viewer-3d.js
```

Expected: diff contains `expansionViewNodeId`, `exitExpansionView`, and focused expansion behavior. Keep these semantics in later 3D work.

- [ ] **Step 3: Run Python exporter tests**

Run:

```powershell
python -m pytest tests/test_memory_graph_viewer_export.py -v
```

Expected: PASS before edits.

- [ ] **Step 4: Run JavaScript galaxy smoke tests**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: no output and exit code 0.

- [ ] **Step 5: Commit only if baseline fixes were required**

If baseline tests fail because of unrelated environment or test drift, fix the baseline first and commit:

```powershell
git add tests/test_memory_graph_viewer_export.py tests/js/memory_galaxy_smoke.test.mjs src/tools/memory_graph_viewer_assets/memory-galaxy-core.js
git commit -m "test: stabilize memory galaxy baseline"
```

Expected: skip this commit if baseline tests already pass.

## Task 2: Export Cache Metadata and Stable Layout Identity

**Files:**
- Modify: `tests/test_memory_graph_viewer_export.py`
- Modify: `src/tools/memory_graph_viewer_export.py`

- [ ] **Step 1: Add failing assertions for cache and layout metadata**

In `tests/test_memory_graph_viewer_export.py`, inside `test_load_graph_filters_orphan_edges_and_links_knowledge`, after the existing timeline assertions, add:

```python
    assert graph["metadata"]["cache"] == {
        "default_root": "D:\\TotalAgentMemory\\memory-galaxy-cache",
        "layout_namespace": "memory-galaxy",
    }
    assert graph["metadata"]["graph_identity"]["node_ids_hash"]
    assert graph["metadata"]["graph_identity"]["edge_ids_hash"]
    assert graph["metadata"]["layout_seed"] == graph["metadata"]["graph_identity"]["node_ids_hash"][:16]
```

In the same test, after the existing `activity` assertion for `rag`, add:

```python
    assert rag["data"]["layout_seed"]
    assert "relation_counts" in rag["data"]
    assert rag["data"]["relation_counts"]["total"] == 1
    assert rag["data"]["provenance"]["source"] == "test"
    assert rag["data"]["provenance"]["first_seen_at"] == "2026-01-01"
    assert rag["data"]["provenance"]["last_seen_at"] == "2026-01-02"
```

- [ ] **Step 2: Add failing copied-asset assertions**

In `test_write_graph_json_and_copy_assets`, add:

```python
    assert (output / "memory-galaxy-events.js").exists()
    assert (output / "viewer-shared.js").exists()
```

- [ ] **Step 3: Run exporter tests and verify failure**

Run:

```powershell
python -m pytest tests/test_memory_graph_viewer_export.py -v
```

Expected: FAIL because metadata fields and new copied assets are not implemented yet.

- [ ] **Step 4: Add hash helper and cache constants**

In `src/tools/memory_graph_viewer_export.py`, add `hashlib` to imports:

```python
import hashlib
```

Add constants after `ASSET_DIR`:

```python
DEFAULT_GALAXY_CACHE_ROOT = Path("D:/TotalAgentMemory/memory-galaxy-cache")
GALAXY_LAYOUT_NAMESPACE = "memory-galaxy"
```

Add this helper near `_truncate`:

```python
def _stable_hash(values: list[str]) -> str:
    digest = hashlib.sha256()
    for value in sorted(str(item) for item in values):
        digest.update(value.encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()
```

- [ ] **Step 5: Compute relation counts and graph identity**

In `load_graph`, after `edges` are built and before `knowledge_by_node = ...`, insert:

```python
    relation_counts_by_node: dict[str, dict[str, int]] = {
        str(node_id): {"total": 0} for node_id in node_ids
    }
    for edge in edges:
        data = edge["data"]
        relation = str(data["relation"] or "related")
        for endpoint in (str(data["source"]), str(data["target"])):
            counts = relation_counts_by_node.setdefault(endpoint, {"total": 0})
            counts["total"] = counts.get("total", 0) + 1
            counts[relation] = counts.get(relation, 0) + 1

    node_ids_hash = _stable_hash([str(row["id"]) for row in node_rows])
    edge_ids_hash = _stable_hash([str(edge["data"]["id"]) for edge in edges])
```

- [ ] **Step 6: Add per-node layout and provenance fields**

In the node `data` dictionary inside `nodes = [...]`, after `"activity": ...`, add:

```python
                "layout_seed": _stable_hash([str(row["id"]), str(row["type"]), str(row["name"])]),
                "relation_counts": relation_counts_by_node.get(str(row["id"]), {"total": 0}),
                "provenance": {
                    "source": row["source"] or "",
                    "first_seen_at": row["first_seen_at"],
                    "last_seen_at": row["last_seen_at"],
                },
```

- [ ] **Step 7: Add metadata cache and identity fields**

Inside the returned `metadata` dictionary, after `timeline`, add:

```python
            "cache": {
                "default_root": str(DEFAULT_GALAXY_CACHE_ROOT),
                "layout_namespace": GALAXY_LAYOUT_NAMESPACE,
            },
            "graph_identity": {
                "node_ids_hash": node_ids_hash,
                "edge_ids_hash": edge_ids_hash,
            },
            "layout_seed": node_ids_hash[:16],
```

- [ ] **Step 8: Copy new assets**

In `copy_assets`, add the new files to the asset tuple:

```python
        "memory-galaxy-events.js",
        "viewer-shared.js",
```

- [ ] **Step 9: Create minimal asset modules so copy tests can pass**

Create `src/tools/memory_graph_viewer_assets/memory-galaxy-events.js`:

```javascript
export function createMemoryGalaxyEvent(type, payload = {}) {
  return {
    type,
    node_id: payload.node_id || null,
    gesture: payload.gesture || null,
    view: payload.view || "unknown",
    timestamp: payload.timestamp || new Date().toISOString(),
    context: payload.context || {},
  };
}
```

Create `src/tools/memory_graph_viewer_assets/viewer-shared.js`:

```javascript
export function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}
```

- [ ] **Step 10: Run exporter tests**

Run:

```powershell
python -m pytest tests/test_memory_graph_viewer_export.py -v
```

Expected: PASS.

- [ ] **Step 11: Commit**

Run:

```powershell
git add tests/test_memory_graph_viewer_export.py src/tools/memory_graph_viewer_export.py src/tools/memory_graph_viewer_assets/memory-galaxy-events.js src/tools/memory_graph_viewer_assets/viewer-shared.js
git commit -m "feat: export memory galaxy cache metadata"
```

## Task 3: Add Testable Galaxy Layout and Label Logic

**Files:**
- Modify: `tests/js/memory_galaxy_smoke.test.mjs`
- Modify: `src/tools/memory_graph_viewer_assets/memory-galaxy-core.js`

- [ ] **Step 1: Extend imports in JavaScript smoke test**

In `tests/js/memory_galaxy_smoke.test.mjs`, update the `vm.runInNewContext` export trailer to include:

```javascript
exports.buildGalaxy2DLayout = buildGalaxy2DLayout;
exports.buildSphereGalaxyLayout = buildSphereGalaxyLayout;
exports.selectVisibleLabels = selectVisibleLabels;
exports.buildGalaxyCacheKey = buildGalaxyCacheKey;
exports.groupNeighborRelations = groupNeighborRelations;
```

Update the destructuring line to:

```javascript
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
```

- [ ] **Step 2: Add failing tests for 2D, 3D, labels, cache, and neighbor grouping**

Append this code to `tests/js/memory_galaxy_smoke.test.mjs`:

```javascript
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
```

- [ ] **Step 3: Run JS smoke test and verify failure**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: FAIL because the new functions are not defined.

- [ ] **Step 4: Add layer radius constants**

In `src/tools/memory_graph_viewer_assets/memory-galaxy-core.js`, after `layerOrbit`, add:

```javascript
const sphereShell = {
  core: 85,
  active: 155,
  knowledge: 245,
  episode: 330,
  external: 410,
};
```

- [ ] **Step 5: Add 2D layout function**

After `buildFocusGalaxy`, add:

```javascript
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
```

- [ ] **Step 6: Add 3D sphere layout function**

After `buildGalaxy2DLayout`, add:

```javascript
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
```

- [ ] **Step 7: Add label gating, cache key, and neighbor grouping functions**

After `buildEditIntent`, add:

```javascript
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
      Number(node.raw.importance || 0) >= 1.2
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
```

- [ ] **Step 8: Run JS smoke test**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: PASS.

- [ ] **Step 9: Commit**

Run:

```powershell
git add tests/js/memory_galaxy_smoke.test.mjs src/tools/memory_graph_viewer_assets/memory-galaxy-core.js
git commit -m "feat: add deterministic memory galaxy layouts"
```

## Task 4: Build the Renderer-Independent Interaction Bridge

**Files:**
- Modify: `tests/js/memory_galaxy_smoke.test.mjs`
- Modify: `src/tools/memory_graph_viewer_assets/memory-galaxy-events.js`

- [ ] **Step 1: Extend the JS test loader for event helpers**

In `tests/js/memory_galaxy_smoke.test.mjs`, read and evaluate the event helper after the core helper block:

```javascript
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
```

- [ ] **Step 2: Add failing event bridge tests**

Append this code:

```javascript
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
assert.deepEqual(log.all().map(item => item.node_id), ["b", "c"]);

const sourcePrompt = suggestAgentPrompt(event, {
  label: "RAG",
  provenance: { source: "explicit" },
  relation_counts: { total: 5 },
});
assert.equal(sourcePrompt.kind, "source-provenance");
assert.ok(sourcePrompt.message.includes("RAG"));
```

- [ ] **Step 3: Run JS smoke test and verify failure**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: FAIL because `createInteractionLog` and `suggestAgentPrompt` are not implemented.

- [ ] **Step 4: Replace event helper implementation**

Replace `src/tools/memory_graph_viewer_assets/memory-galaxy-events.js` with:

```javascript
const allowedEventTypes = new Set([
  "node:selected",
  "node:hovered",
  "node:drag-started",
  "node:dragged",
  "node:drag-ended",
  "node:expanded",
  "view:filtered",
  "view:focus-cleared",
  "agent:suggestion-staged",
]);

export function createMemoryGalaxyEvent(type, payload = {}) {
  if (!allowedEventTypes.has(type)) {
    throw new Error(`Unsupported memory galaxy event: ${type}`);
  }
  return {
    type,
    node_id: payload.node_id ? String(payload.node_id) : null,
    gesture: payload.gesture || null,
    view: payload.view || "unknown",
    timestamp: payload.timestamp || new Date().toISOString(),
    context: payload.context || {},
  };
}

export function createInteractionLog(limit = 80) {
  const events = [];
  return {
    push(event) {
      events.push(event);
      while (events.length > limit) events.shift();
      return event;
    },
    all() {
      return [...events];
    },
    clear() {
      events.length = 0;
    },
  };
}

export function suggestAgentPrompt(event, nodeData = {}) {
  if (!event || !event.node_id || !event.type.startsWith("node:")) return null;
  const label = nodeData.label || nodeData.name || event.node_id;
  if (event.type === "node:selected" || event.type === "node:drag-ended") {
    return {
      kind: "source-provenance",
      message: `要不要查看「${label}」这个记忆节点的内容来源？`,
      action: "inspect_source",
      node_id: event.node_id,
    };
  }
  if (event.type === "node:expanded") {
    return {
      kind: "relationship-summary",
      message: `我可以帮你总结「${label}」周围的强关系。`,
      action: "summarize_neighbors",
      node_id: event.node_id,
    };
  }
  return null;
}
```

- [ ] **Step 5: Run JS smoke test**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```powershell
git add tests/js/memory_galaxy_smoke.test.mjs src/tools/memory_graph_viewer_assets/memory-galaxy-events.js
git commit -m "feat: add memory galaxy interaction events"
```

## Task 5: Extract Shared Viewer UI Helpers

**Files:**
- Modify: `tests/js/memory_galaxy_smoke.test.mjs`
- Modify: `src/tools/memory_graph_viewer_assets/viewer-shared.js`

- [ ] **Step 1: Extend JS test loader for shared helpers**

In `tests/js/memory_galaxy_smoke.test.mjs`, after the event helper block, add:

```javascript
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
```

- [ ] **Step 2: Add failing shared helper tests**

Append:

```javascript
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
```

- [ ] **Step 3: Run JS smoke test and verify failure**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: FAIL because shared helpers are not implemented.

- [ ] **Step 4: Replace shared helper implementation**

Replace `src/tools/memory_graph_viewer_assets/viewer-shared.js` with:

```javascript
export function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

export function timelineCutoffFromPercent(timeline, percent) {
  const value = Number(percent);
  if (value >= 100 || !timeline?.start || !timeline?.end) return null;
  const start = Date.parse(timeline.start);
  const end = Date.parse(timeline.end);
  if (!Number.isFinite(start) || !Number.isFinite(end) || end <= start) return null;
  return new Date(start + ((end - start) * value / 100)).toISOString();
}

export function renderPromptText(prompt) {
  return prompt?.message || "";
}

export function formatNodeDetails(data) {
  const relationCounts = data.relation_counts || {};
  const relations = Object.entries(relationCounts)
    .filter(([key]) => key !== "total")
    .sort((a, b) => b[1] - a[1])
    .map(([key, count]) => `<span class="pill">${escapeHtml(key)} ${escapeHtml(count)}</span>`)
    .join("");
  const memories = (data.knowledge || []).map(item => `
    <div class="memory">
      <strong>#${escapeHtml(item.id)} ${escapeHtml(item.type)} | ${escapeHtml(item.project)}</strong>
      <div class="meta">${escapeHtml(item.role)} | strength ${escapeHtml(item.strength)}</div>
      <div>${escapeHtml(item.summary)}</div>
    </div>
  `).join("");
  const provenance = data.provenance || {};
  return `
    <div class="node-title">${escapeHtml(data.label)}</div>
    <div class="meta">
      ${escapeHtml(data.type)} | ${escapeHtml(data.galaxy_layer || "external")}
      | mentions ${escapeHtml(data.mention_count)}
      | importance ${escapeHtml(data.importance)}
    </div>
    <div>${escapeHtml(data.content || "No node content.")}</div>
    <h2>Relations</h2>
    <div>${relations || '<span class="meta">No relation counts.</span>'}</div>
    <h2>Content Source</h2>
    <div class="meta">
      source ${escapeHtml(provenance.source || data.source || "unknown")}
      | first seen ${escapeHtml(provenance.first_seen_at || "unknown")}
      | last seen ${escapeHtml(provenance.last_seen_at || data.last_seen_at || "unknown")}
    </div>
    <h2>Linked Memories</h2>
    ${memories || "<p>No linked memories in exported sample.</p>"}
  `;
}
```

- [ ] **Step 5: Run JS smoke test**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```powershell
git add tests/js/memory_galaxy_smoke.test.mjs src/tools/memory_graph_viewer_assets/viewer-shared.js
git commit -m "feat: share memory galaxy viewer helpers"
```

## Task 6: Replace 2D Cytoscape View With PixiJS Galaxy

**Files:**
- Replace: `src/tools/memory_graph_viewer_assets/index.html`
- Replace: `src/tools/memory_graph_viewer_assets/viewer.js`
- Modify: `src/tools/memory_graph_viewer_assets/styles.css`

- [ ] **Step 1: Replace `index.html` with the 2D galaxy shell**

Replace `src/tools/memory_graph_viewer_assets/index.html` with:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Total Agent Memory Galaxy</title>
  <link rel="stylesheet" href="styles.css">
  <script src="https://unpkg.com/pixi.js@8.2.6/dist/pixi.min.js"></script>
</head>
<body>
  <main class="app galaxy-app">
    <aside class="sidebar">
      <header>
        <h1>Memory Galaxy</h1>
        <p id="stats">Loading galaxy...</p>
        <nav class="mode-links">
          <a class="active" href="index.html">2D Galaxy</a>
          <a href="viewer-3d.html">3D Sphere</a>
        </nav>
      </header>

      <label class="field">
        Search
        <input id="search" type="search" placeholder="node, project, concept">
      </label>

      <section>
        <h2>Node Types</h2>
        <div id="typeFilters" class="filters"></div>
      </section>

      <section>
        <h2>Galaxy Layers</h2>
        <div id="layerFilters" class="filters compact"></div>
      </section>

      <label class="field">
        Minimum edge weight
        <input id="weightFilter" type="range" min="0" max="10" step="0.1" value="0">
        <span id="weightValue">0</span>
      </label>

      <label class="field">
        Timeline
        <input id="timelineFilter" type="range" min="0" max="100" step="1" value="100">
        <span id="timelineValue">All time</span>
      </label>

      <section>
        <h2>View</h2>
        <div class="buttons">
          <button id="fit" type="button">Fit</button>
          <button id="clearFocus" type="button">Clear</button>
          <button id="focusNeighborhood" type="button">Neighborhood</button>
          <button id="focusView" type="button">Focus View</button>
        </div>
      </section>
    </aside>

    <section id="galaxy2d" class="galaxy-canvas" aria-label="2D memory galaxy"></section>

    <aside class="details">
      <h2>Agent Prompt</h2>
      <div id="agentPrompt" class="agent-prompt">Select or drag a node to stage an agent prompt.</div>
      <h2>Selection</h2>
      <div id="details">Select a node to inspect linked memories.</div>
    </aside>
  </main>
  <script type="module" src="viewer.js"></script>
</body>
</html>
```

- [ ] **Step 2: Replace `viewer.js` with PixiJS 2D galaxy renderer**

Replace `src/tools/memory_graph_viewer_assets/viewer.js` with:

```javascript
import {
  buildGalaxy2DLayout,
  buildGalaxyCacheKey,
  buildFocusGalaxy,
  convertGraphToGalaxy,
  filterGalaxy,
  selectVisibleLabels,
} from "./memory-galaxy-core.js";
import {
  createInteractionLog,
  createMemoryGalaxyEvent,
  suggestAgentPrompt,
} from "./memory-galaxy-events.js";
import {
  escapeHtml,
  formatNodeDetails,
  renderPromptText,
  timelineCutoffFromPercent,
} from "./viewer-shared.js";

const viewName = "2d-galaxy";
const focusLimit = 850;
const interactionLog = createInteractionLog();

let app;
let stageRoot;
let linkLayer;
let nodeLayer;
let labelLayer;
let originalGraph = { nodes: [], links: [], metadata: {} };
let visibleGraph = { nodes: [], links: [], metadata: {} };
let activeTypes = new Set();
let activeLayers = new Set(["core", "active", "knowledge", "episode", "external"]);
let selectedNodeId = null;
let hoveredNodeId = null;
let selectedNode = null;
let renderTimer = null;
let scale = 1;
let pan = { x: 0, y: 0 };
let dragState = null;

async function init() {
  if (!window.PIXI) throw new Error("PixiJS failed to load from CDN.");
  const response = await fetch("graph.json");
  const graph = await response.json();
  originalGraph = convertGraphToGalaxy(graph);
  activeTypes = new Set(Object.keys(graph.metadata.type_counts));
  renderTypeFilters(graph.metadata.type_counts);
  renderLayerFilters();
  renderStats(graph.metadata);
  await createPixi();
  bindControls();
  applyFilters();
}

async function createPixi() {
  const container = document.getElementById("galaxy2d");
  app = new PIXI.Application();
  await app.init({
    resizeTo: container,
    antialias: true,
    backgroundAlpha: 0,
    autoDensity: true,
    resolution: Math.min(window.devicePixelRatio || 1, 2),
  });
  container.appendChild(app.canvas);
  stageRoot = new PIXI.Container();
  linkLayer = new PIXI.Container();
  nodeLayer = new PIXI.Container();
  labelLayer = new PIXI.Container();
  stageRoot.addChild(linkLayer, nodeLayer, labelLayer);
  app.stage.addChild(stageRoot);
  stageRoot.eventMode = "static";
  app.stage.eventMode = "static";
  app.stage.hitArea = app.screen;
  app.stage.on("wheel", onWheel);
  app.stage.on("pointerdown", onStagePointerDown);
  app.stage.on("pointermove", onStagePointerMove);
  app.stage.on("pointerup", onStagePointerUp);
  app.stage.on("pointerupoutside", onStagePointerUp);
  window.addEventListener("resize", () => requestAnimationFrame(fitView));
}

function renderTypeFilters(typeCounts) {
  const root = document.getElementById("typeFilters");
  root.innerHTML = "";
  Object.entries(typeCounts).sort((a, b) => b[1] - a[1]).forEach(([type, count]) => {
    const label = document.createElement("label");
    label.innerHTML = `<input type="checkbox" data-type="${escapeHtml(type)}" checked><span><span class="pill">${escapeHtml(type)}</span>${count}</span>`;
    root.appendChild(label);
  });
}

function renderLayerFilters() {
  const root = document.getElementById("layerFilters");
  root.innerHTML = "";
  for (const [layer, labelText] of [["core", "Core"], ["active", "Active"], ["knowledge", "Knowledge"], ["episode", "Episodes"], ["external", "External"]]) {
    const label = document.createElement("label");
    label.innerHTML = `<input type="checkbox" data-layer="${escapeHtml(layer)}" checked><span><span class="pill">${escapeHtml(labelText)}</span></span>`;
    root.appendChild(label);
  }
}

function bindControls() {
  document.getElementById("search").addEventListener("input", scheduleApplyFilters);
  document.getElementById("weightFilter").addEventListener("input", event => {
    document.getElementById("weightValue").textContent = event.target.value;
    scheduleApplyFilters();
  });
  document.getElementById("timelineFilter").addEventListener("input", scheduleApplyFilters);
  document.getElementById("typeFilters").addEventListener("change", event => {
    if (!event.target.matches("input[type='checkbox']")) return;
    if (event.target.checked) activeTypes.add(event.target.dataset.type);
    else activeTypes.delete(event.target.dataset.type);
    scheduleApplyFilters();
  });
  document.getElementById("layerFilters").addEventListener("change", event => {
    if (!event.target.matches("input[type='checkbox']")) return;
    if (event.target.checked) activeLayers.add(event.target.dataset.layer);
    else activeLayers.delete(event.target.dataset.layer);
    scheduleApplyFilters();
  });
  document.getElementById("fit").addEventListener("click", fitView);
  document.getElementById("clearFocus").addEventListener("click", clearFocus);
  document.getElementById("focusNeighborhood").addEventListener("click", focusNeighborhood);
  document.getElementById("focusView").addEventListener("click", applyFilters);
}

function scheduleApplyFilters() {
  clearTimeout(renderTimer);
  renderTimer = setTimeout(applyFilters, 120);
}

function applyFilters() {
  const timelineCutoff = currentTimelineCutoff();
  const filtered = filterGalaxy(originalGraph, {
    query: document.getElementById("search").value,
    activeTypes,
    activeLayers,
    minWeight: Number(document.getElementById("weightFilter").value),
    timelineCutoff,
  });
  visibleGraph = buildGalaxy2DLayout(filtered, { maxNodes: focusLimit });
  selectedNodeId = null;
  selectedNode = null;
  drawGalaxy();
  renderStats({ node_count: `${visibleGraph.nodes.length}/${originalGraph.nodes.length}`, edge_count: `${visibleGraph.links.length}/${originalGraph.links.length}` });
  emitEvent("view:filtered", null, { visible_nodes: visibleGraph.nodes.length });
}

function focusNeighborhood() {
  if (!selectedNode) return;
  visibleGraph = buildGalaxy2DLayout(buildFocusGalaxy(originalGraph, {
    focusNodeId: selectedNode.id,
    maxNodes: 260,
    seedCount: 1,
    firstRingLimit: 160,
  }), { maxNodes: 260, focusNodeId: selectedNode.id });
  drawGalaxy();
  fitView();
  emitEvent("node:expanded", selectedNode, { visible_neighbors: visibleGraph.nodes.length - 1 });
}

function clearFocus() {
  selectedNodeId = null;
  selectedNode = null;
  document.getElementById("details").textContent = "Select a node to inspect linked memories.";
  document.getElementById("agentPrompt").textContent = "Select or drag a node to stage an agent prompt.";
  applyFilters();
  emitEvent("view:focus-cleared", null, {});
}

function drawGalaxy() {
  linkLayer.removeChildren();
  nodeLayer.removeChildren();
  labelLayer.removeChildren();
  const nodeById = new Map(visibleGraph.nodes.map(node => [node.id, node]));
  for (const link of visibleGraph.links) {
    const source = nodeById.get(String(link.source.id || link.source));
    const target = nodeById.get(String(link.target.id || link.target));
    if (!source || !target) continue;
    const line = new PIXI.Graphics();
    const selected = selectedNodeId && (source.id === selectedNodeId || target.id === selectedNodeId);
    line.moveTo(source.x, source.y).lineTo(target.x, target.y);
    line.stroke({ width: selected ? 2.2 : Math.max(0.4, Math.min(1.6, link.weight * 0.45)), color: selected ? 0xfacc15 : 0x5b6f91, alpha: selected ? 0.78 : 0.26 });
    linkLayer.addChild(line);
  }
  for (const node of visibleGraph.nodes) {
    const star = new PIXI.Graphics();
    star.eventMode = "static";
    star.cursor = "grab";
    star.memoryNode = node;
    drawStar(star, node);
    star.on("pointerdown", event => onNodePointerDown(event, node, star));
    star.on("pointerover", () => {
      hoveredNodeId = node.id;
      drawGalaxy();
      emitEvent("node:hovered", node, { layer: node.layer });
    });
    star.on("pointerout", () => {
      hoveredNodeId = null;
      drawGalaxy();
    });
    nodeLayer.addChild(star);
  }
  for (const node of selectVisibleLabels(visibleGraph.nodes, { zoom: scale, selectedNodeId, hoveredNodeId })) {
    const label = new PIXI.Text({ text: node.label, style: { fill: 0xe5f0ff, fontFamily: "Segoe UI, Microsoft YaHei, sans-serif", fontSize: 12, fontWeight: "600" } });
    label.x = node.x + node.renderRadius + 7;
    label.y = node.y - 8;
    label.alpha = node.id === selectedNodeId || node.id === hoveredNodeId ? 1 : 0.72;
    labelLayer.addChild(label);
  }
  updateTransform();
}

function drawStar(graphics, node) {
  const selected = node.id === selectedNodeId;
  const hovered = node.id === hoveredNodeId;
  graphics.clear();
  graphics.position.set(node.x, node.y);
  if (selected || hovered) {
    graphics.circle(0, 0, node.renderRadius + (selected ? 10 : 6));
    graphics.stroke({ width: selected ? 2.4 : 1.6, color: selected ? 0xfacc15 : 0x7dd3fc, alpha: 0.9 });
  }
  graphics.circle(0, 0, node.renderRadius);
  graphics.fill(parseColor(node.color));
}

function onNodePointerDown(event, node, star) {
  event.stopPropagation();
  selectedNodeId = node.id;
  selectedNode = node;
  showDetails(node);
  dragState = { node, star, start: event.global.clone(), origin: { x: node.x, y: node.y }, mode: "node" };
  star.cursor = "grabbing";
  emitEvent("node:selected", node, { layer: node.layer, visible_neighbors: countVisibleNeighbors(node.id) });
  emitEvent("node:drag-started", node, { layer: node.layer });
  drawGalaxy();
}

function onStagePointerDown(event) {
  dragState = { mode: "pan", start: event.global.clone(), origin: { ...pan } };
}

function onStagePointerMove(event) {
  if (!dragState) return;
  if (dragState.mode === "pan") {
    pan.x = dragState.origin.x + event.global.x - dragState.start.x;
    pan.y = dragState.origin.y + event.global.y - dragState.start.y;
    updateTransform();
    return;
  }
  const dx = (event.global.x - dragState.start.x) / scale;
  const dy = (event.global.y - dragState.start.y) / scale;
  dragState.node.x = dragState.origin.x + dx;
  dragState.node.y = dragState.origin.y + dy;
  emitEvent("node:dragged", dragState.node, { layer: dragState.node.layer });
  drawGalaxy();
}

function onStagePointerUp() {
  if (dragState?.mode === "node") {
    emitEvent("node:drag-ended", dragState.node, { layer: dragState.node.layer, visible_neighbors: countVisibleNeighbors(dragState.node.id) });
  }
  dragState = null;
}

function onWheel(event) {
  event.preventDefault();
  const factor = event.deltaY > 0 ? 0.9 : 1.1;
  scale = Math.max(0.25, Math.min(3.5, scale * factor));
  updateTransform();
  drawGalaxy();
}

function fitView() {
  if (!visibleGraph.nodes.length || !app) return;
  const bounds = visibleGraph.nodes.reduce((acc, node) => ({
    minX: Math.min(acc.minX, node.x),
    maxX: Math.max(acc.maxX, node.x),
    minY: Math.min(acc.minY, node.y),
    maxY: Math.max(acc.maxY, node.y),
  }), { minX: Infinity, maxX: -Infinity, minY: Infinity, maxY: -Infinity });
  const width = Math.max(1, bounds.maxX - bounds.minX);
  const height = Math.max(1, bounds.maxY - bounds.minY);
  scale = Math.min(app.screen.width / (width + 160), app.screen.height / (height + 160), 1.8);
  pan = {
    x: app.screen.width / 2 - ((bounds.minX + bounds.maxX) / 2) * scale,
    y: app.screen.height / 2 - ((bounds.minY + bounds.maxY) / 2) * scale,
  };
  updateTransform();
}

function updateTransform() {
  if (!stageRoot) return;
  stageRoot.scale.set(scale);
  stageRoot.position.set(pan.x, pan.y);
}

function showDetails(node) {
  document.getElementById("details").innerHTML = formatNodeDetails(node.raw);
}

function emitEvent(type, node, context) {
  const event = createMemoryGalaxyEvent(type, {
    node_id: node?.id,
    gesture: type.includes("drag") ? "drag" : type.includes("hover") ? "hover" : "click",
    view: viewName,
    context,
  });
  interactionLog.push(event);
  const prompt = suggestAgentPrompt(event, node?.raw || {});
  if (prompt) document.getElementById("agentPrompt").textContent = renderPromptText(prompt);
}

function currentTimelineCutoff() {
  const slider = document.getElementById("timelineFilter");
  const cutoff = timelineCutoffFromPercent(originalGraph.metadata.timeline || {}, Number(slider.value));
  document.getElementById("timelineValue").textContent = cutoff ? cutoff.slice(0, 10) : "All time";
  return cutoff;
}

function countVisibleNeighbors(nodeId) {
  return visibleGraph.links.filter(link => String(link.source.id || link.source) === nodeId || String(link.target.id || link.target) === nodeId).length;
}

function renderStats(metadata) {
  document.getElementById("stats").textContent = `${metadata.node_count} nodes, ${metadata.edge_count} edges`;
}

function parseColor(value) {
  return Number.parseInt(String(value || "#94a3b8").replace("#", ""), 16);
}

init().catch(error => {
  document.getElementById("stats").textContent = "Failed to load galaxy.";
  document.getElementById("details").textContent = String(error);
});
```

- [ ] **Step 3: Add CSS for galaxy canvas and prompt panel**

In `src/tools/memory_graph_viewer_assets/styles.css`, replace the duplicate `.graph-3d` background blocks and add:

```css
.galaxy-app {
  background: #050913;
}

.galaxy-canvas,
.graph-3d {
  min-width: 0;
  min-height: 0;
  position: relative;
  overflow: hidden;
  background:
    radial-gradient(circle at 50% 45%, rgba(56, 189, 248, 0.12), transparent 28%),
    radial-gradient(circle at 70% 30%, rgba(167, 139, 250, 0.10), transparent 22%),
    #050913;
}

.galaxy-canvas canvas,
.graph-3d canvas {
  display: block;
  width: 100%;
  height: 100%;
}

.agent-prompt {
  margin-bottom: 1rem;
  padding: 0.75rem;
  border: 1px solid rgba(96, 165, 250, 0.35);
  border-radius: 8px;
  background: rgba(37, 99, 235, 0.10);
  color: #1e3a8a;
}
```

Keep panel border radius at `8px` or less.

- [ ] **Step 4: Run syntax checks**

Run:

```powershell
node --check src/tools/memory_graph_viewer_assets/viewer.js
node --check src/tools/memory_graph_viewer_assets/viewer-shared.js
node --check src/tools/memory_graph_viewer_assets/memory-galaxy-events.js
```

Expected: PASS.

- [ ] **Step 5: Run test suites**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
python -m pytest tests/test_memory_graph_viewer_export.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```powershell
git add src/tools/memory_graph_viewer_assets/index.html src/tools/memory_graph_viewer_assets/viewer.js src/tools/memory_graph_viewer_assets/styles.css
git commit -m "feat: replace 2d graph with memory galaxy"
```

## Task 7: Replace 3D Nebula With Three.js Spherical Galaxy

**Files:**
- Modify: `src/tools/memory_graph_viewer_assets/viewer-3d.html`
- Replace: `src/tools/memory_graph_viewer_assets/viewer-3d.js`
- Modify: `src/tools/memory_graph_viewer_assets/styles.css`

- [ ] **Step 1: Replace `viewer-3d.html` CDN and labels**

Replace `src/tools/memory_graph_viewer_assets/viewer-3d.html` with:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Total Agent Memory Sphere</title>
  <link rel="stylesheet" href="styles.css">
  <script src="https://unpkg.com/three@0.165.0/build/three.min.js"></script>
</head>
<body>
  <main class="app galaxy-app">
    <aside class="sidebar">
      <header>
        <h1>Memory Sphere</h1>
        <p id="stats">Loading sphere...</p>
        <nav class="mode-links">
          <a href="index.html">2D Galaxy</a>
          <a class="active" href="viewer-3d.html">3D Sphere</a>
        </nav>
      </header>

      <label class="field">
        Search
        <input id="search" type="search" placeholder="node, project, concept">
      </label>

      <section>
        <h2>Node Types</h2>
        <div id="typeFilters" class="filters"></div>
      </section>

      <section>
        <h2>Galaxy Layers</h2>
        <div id="layerFilters" class="filters compact"></div>
      </section>

      <label class="field">
        Minimum edge weight
        <input id="weightFilter" type="range" min="0" max="10" step="0.1" value="0">
        <span id="weightValue">0</span>
      </label>

      <label class="field">
        Timeline
        <input id="timelineFilter" type="range" min="0" max="100" step="1" value="100">
        <span id="timelineValue">All time</span>
      </label>

      <section>
        <h2>View</h2>
        <div class="buttons">
          <button id="fit" type="button">Fit</button>
          <button id="clearFocus" type="button">Clear</button>
          <button id="focusNeighborhood" type="button">Neighborhood</button>
          <button id="focusView" type="button">Focus View</button>
        </div>
      </section>
    </aside>

    <section id="graph3d" class="graph-3d graph-sphere" aria-label="3D memory sphere"></section>

    <aside class="details">
      <h2>Agent Prompt</h2>
      <div id="agentPrompt" class="agent-prompt">Select a star to stage an agent prompt.</div>
      <h2>Selection</h2>
      <div id="details">Select a node to inspect linked memories.</div>
    </aside>
  </main>
  <script type="module" src="viewer-3d.js"></script>
</body>
</html>
```

- [ ] **Step 2: Replace `viewer-3d.js` with spherical Three.js renderer**

Replace `src/tools/memory_graph_viewer_assets/viewer-3d.js` with:

```javascript
import {
  buildFocusGalaxy,
  buildSphereGalaxyLayout,
  convertGraphToGalaxy,
  filterGalaxy,
} from "./memory-galaxy-core.js";
import {
  createInteractionLog,
  createMemoryGalaxyEvent,
  suggestAgentPrompt,
} from "./memory-galaxy-events.js";
import {
  escapeHtml,
  formatNodeDetails,
  renderPromptText,
  timelineCutoffFromPercent,
} from "./viewer-shared.js";

const viewName = "3d-sphere";
const focusLimit = 650;
const interactionLog = createInteractionLog();
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();

let scene;
let camera;
let renderer;
let root;
let container;
let originalGraph = { nodes: [], links: [], metadata: {} };
let visibleGraph = { nodes: [], links: [], metadata: {} };
let activeTypes = new Set();
let activeLayers = new Set(["core", "active", "knowledge", "episode", "external"]);
let selectedNodeId = null;
let selectedNode = null;
let renderTimer = null;
let expansionViewNodeId = null;
let isDraggingView = false;
let lastPointer = { x: 0, y: 0 };
let rotation = { x: -0.28, y: 0.42 };

async function init() {
  if (!window.THREE) throw new Error("Three.js failed to load from CDN.");
  const response = await fetch("graph.json");
  const graph = await response.json();
  originalGraph = convertGraphToGalaxy(graph);
  activeTypes = new Set(Object.keys(graph.metadata.type_counts));
  renderTypeFilters(graph.metadata.type_counts);
  renderLayerFilters();
  renderStats(graph.metadata);
  createScene();
  bindControls();
  applyFilters();
  animate();
}

function createScene() {
  container = document.getElementById("graph3d");
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(52, container.clientWidth / container.clientHeight, 1, 2500);
  camera.position.set(0, 0, 760);
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setSize(container.clientWidth, container.clientHeight);
  container.appendChild(renderer.domElement);
  root = new THREE.Group();
  scene.add(root);
  scene.add(new THREE.AmbientLight(0xffffff, 1.8));
  const light = new THREE.PointLight(0x93c5fd, 2.2, 1600);
  light.position.set(260, 180, 420);
  scene.add(light);
  renderer.domElement.addEventListener("pointerdown", onPointerDown);
  renderer.domElement.addEventListener("pointermove", onPointerMove);
  renderer.domElement.addEventListener("pointerup", onPointerUp);
  renderer.domElement.addEventListener("wheel", onWheel, { passive: false });
  window.addEventListener("resize", resize);
}

function renderTypeFilters(typeCounts) {
  const rootEl = document.getElementById("typeFilters");
  rootEl.innerHTML = "";
  Object.entries(typeCounts).sort((a, b) => b[1] - a[1]).forEach(([type, count]) => {
    const label = document.createElement("label");
    label.innerHTML = `<input type="checkbox" data-type="${escapeHtml(type)}" checked><span><span class="pill">${escapeHtml(type)}</span>${count}</span>`;
    rootEl.appendChild(label);
  });
}

function renderLayerFilters() {
  const rootEl = document.getElementById("layerFilters");
  rootEl.innerHTML = "";
  for (const [layer, labelText] of [["core", "Core"], ["active", "Active"], ["knowledge", "Knowledge"], ["episode", "Episodes"], ["external", "External"]]) {
    const label = document.createElement("label");
    label.innerHTML = `<input type="checkbox" data-layer="${escapeHtml(layer)}" checked><span><span class="pill">${escapeHtml(labelText)}</span></span>`;
    rootEl.appendChild(label);
  }
}

function bindControls() {
  document.getElementById("search").addEventListener("input", scheduleApplyFilters);
  document.getElementById("weightFilter").addEventListener("input", event => {
    document.getElementById("weightValue").textContent = event.target.value;
    scheduleApplyFilters();
  });
  document.getElementById("timelineFilter").addEventListener("input", scheduleApplyFilters);
  document.getElementById("typeFilters").addEventListener("change", event => {
    if (!event.target.matches("input[type='checkbox']")) return;
    if (event.target.checked) activeTypes.add(event.target.dataset.type);
    else activeTypes.delete(event.target.dataset.type);
    scheduleApplyFilters();
  });
  document.getElementById("layerFilters").addEventListener("change", event => {
    if (!event.target.matches("input[type='checkbox']")) return;
    if (event.target.checked) activeLayers.add(event.target.dataset.layer);
    else activeLayers.delete(event.target.dataset.layer);
    scheduleApplyFilters();
  });
  document.getElementById("fit").addEventListener("click", fitView);
  document.getElementById("clearFocus").addEventListener("click", clearFocus);
  document.getElementById("focusNeighborhood").addEventListener("click", focusNeighborhood);
  document.getElementById("focusView").addEventListener("click", applyFilters);
}

function scheduleApplyFilters() {
  clearTimeout(renderTimer);
  renderTimer = setTimeout(applyFilters, 120);
}

function applyFilters() {
  expansionViewNodeId = null;
  selectedNodeId = null;
  selectedNode = null;
  const filtered = currentFilteredGalaxy();
  visibleGraph = buildSphereGalaxyLayout(filtered, { maxNodes: focusLimit });
  drawSphere();
  renderStats({ node_count: `${visibleGraph.nodes.length}/${originalGraph.nodes.length}`, edge_count: `${visibleGraph.links.length}/${originalGraph.links.length}` });
  emitEvent("view:filtered", null, { visible_nodes: visibleGraph.nodes.length });
}

function currentFilteredGalaxy() {
  return filterGalaxy(originalGraph, {
    query: document.getElementById("search").value,
    activeTypes,
    activeLayers,
    minWeight: Number(document.getElementById("weightFilter").value),
    timelineCutoff: currentTimelineCutoff(),
  });
}

function focusNeighborhood() {
  if (!selectedNode) return;
  expansionViewNodeId = selectedNode.id;
  visibleGraph = buildSphereGalaxyLayout(buildFocusGalaxy(currentFilteredGalaxy(), {
    focusNodeId: selectedNode.id,
    maxNodes: 360,
    seedCount: 1,
    firstRingLimit: 180,
  }), { maxNodes: 360, focusNodeId: selectedNode.id });
  drawSphere();
  emitEvent("node:expanded", selectedNode, { visible_neighbors: visibleGraph.nodes.length - 1 });
}

function clearFocus() {
  expansionViewNodeId = null;
  selectedNodeId = null;
  selectedNode = null;
  document.getElementById("details").textContent = "Select a node to inspect linked memories.";
  document.getElementById("agentPrompt").textContent = "Select a star to stage an agent prompt.";
  applyFilters();
  emitEvent("view:focus-cleared", null, {});
}

function drawSphere() {
  root.clear();
  root.rotation.set(rotation.x, rotation.y, 0);
  drawShells();
  const nodeById = new Map(visibleGraph.nodes.map(node => [node.id, node]));
  for (const link of visibleGraph.links) {
    const source = nodeById.get(String(link.source.id || link.source));
    const target = nodeById.get(String(link.target.id || link.target));
    if (!source || !target) continue;
    const selected = selectedNodeId && (source.id === selectedNodeId || target.id === selectedNodeId);
    const curve = new THREE.CatmullRomCurve3([
      new THREE.Vector3(source.x, source.y, source.z),
      new THREE.Vector3((source.x + target.x) / 2 * 1.12, (source.y + target.y) / 2 * 1.12, (source.z + target.z) / 2 * 1.12),
      new THREE.Vector3(target.x, target.y, target.z),
    ]);
    const geometry = new THREE.BufferGeometry().setFromPoints(curve.getPoints(18));
    const material = new THREE.LineBasicMaterial({ color: selected ? 0xfacc15 : 0x49617f, transparent: true, opacity: selected ? 0.72 : 0.18 });
    root.add(new THREE.Line(geometry, material));
  }
  for (const node of visibleGraph.nodes) {
    const material = new THREE.MeshBasicMaterial({ color: parseColor(node.color), transparent: true, opacity: node.id === selectedNodeId ? 1 : 0.84 });
    const geometry = new THREE.SphereGeometry(node.renderRadius, 16, 12);
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.set(node.x, node.y, node.z);
    mesh.userData.memoryNode = node;
    root.add(mesh);
    if (node.id === selectedNodeId) {
      const halo = new THREE.Mesh(new THREE.SphereGeometry(node.renderRadius + 8, 24, 16), new THREE.MeshBasicMaterial({ color: 0xfacc15, wireframe: true, transparent: true, opacity: 0.65 }));
      halo.position.copy(mesh.position);
      root.add(halo);
    }
  }
}

function drawShells() {
  for (const radius of [85, 155, 245, 330, 410]) {
    const shell = new THREE.Mesh(
      new THREE.SphereGeometry(radius, 48, 24),
      new THREE.MeshBasicMaterial({ color: 0x60a5fa, wireframe: true, transparent: true, opacity: radius === 155 ? 0.08 : 0.045 }),
    );
    root.add(shell);
  }
}

function onPointerDown(event) {
  isDraggingView = true;
  lastPointer = { x: event.clientX, y: event.clientY };
}

function onPointerMove(event) {
  if (!isDraggingView) return;
  const dx = event.clientX - lastPointer.x;
  const dy = event.clientY - lastPointer.y;
  lastPointer = { x: event.clientX, y: event.clientY };
  rotation.y += dx * 0.006;
  rotation.x += dy * 0.006;
  root.rotation.set(rotation.x, rotation.y, 0);
}

function onPointerUp(event) {
  if (Math.abs(event.clientX - lastPointer.x) < 4 && Math.abs(event.clientY - lastPointer.y) < 4) {
    selectNodeAt(event);
  }
  isDraggingView = false;
}

function selectNodeAt(event) {
  const rect = renderer.domElement.getBoundingClientRect();
  pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  pointer.y = -(((event.clientY - rect.top) / rect.height) * 2 - 1);
  raycaster.setFromCamera(pointer, camera);
  const hit = raycaster.intersectObjects(root.children, false).find(item => item.object.userData.memoryNode);
  if (!hit) return;
  selectedNode = hit.object.userData.memoryNode;
  selectedNodeId = selectedNode.id;
  document.getElementById("details").innerHTML = formatNodeDetails(selectedNode.raw);
  emitEvent("node:selected", selectedNode, { layer: selectedNode.layer });
  drawSphere();
}

function onWheel(event) {
  event.preventDefault();
  camera.position.z = Math.max(360, Math.min(1200, camera.position.z + event.deltaY * 0.8));
}

function fitView() {
  camera.position.set(0, 0, expansionViewNodeId ? 560 : 760);
}

function resize() {
  camera.aspect = container.clientWidth / container.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(container.clientWidth, container.clientHeight);
}

function animate() {
  requestAnimationFrame(animate);
  if (!isDraggingView) {
    rotation.y += 0.0007;
    root.rotation.set(rotation.x, rotation.y, 0);
  }
  renderer.render(scene, camera);
}

function emitEvent(type, node, context) {
  const event = createMemoryGalaxyEvent(type, {
    node_id: node?.id,
    gesture: type.includes("drag") ? "drag" : "click",
    view: viewName,
    context,
  });
  interactionLog.push(event);
  const prompt = suggestAgentPrompt(event, node?.raw || {});
  if (prompt) document.getElementById("agentPrompt").textContent = renderPromptText(prompt);
}

function currentTimelineCutoff() {
  const slider = document.getElementById("timelineFilter");
  const cutoff = timelineCutoffFromPercent(originalGraph.metadata.timeline || {}, Number(slider.value));
  document.getElementById("timelineValue").textContent = cutoff ? cutoff.slice(0, 10) : "All time";
  return cutoff;
}

function renderStats(metadata) {
  document.getElementById("stats").textContent = `${metadata.node_count} nodes, ${metadata.edge_count} edges`;
}

function parseColor(value) {
  return Number.parseInt(String(value || "#94a3b8").replace("#", ""), 16);
}

init().catch(error => {
  document.getElementById("stats").textContent = "Failed to load sphere.";
  document.getElementById("details").textContent = String(error);
});
```

- [ ] **Step 3: Run syntax checks**

Run:

```powershell
node --check src/tools/memory_graph_viewer_assets/viewer-3d.js
node --check src/tools/memory_graph_viewer_assets/viewer-shared.js
node --check src/tools/memory_graph_viewer_assets/memory-galaxy-events.js
```

Expected: PASS.

- [ ] **Step 4: Run test suites**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
python -m pytest tests/test_memory_graph_viewer_export.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```powershell
git add src/tools/memory_graph_viewer_assets/viewer-3d.html src/tools/memory_graph_viewer_assets/viewer-3d.js src/tools/memory_graph_viewer_assets/styles.css
git commit -m "feat: render memory galaxy as 3d sphere"
```

## Task 8: Export, Serve, and Browser-Verify the New Viewer

**Files:**
- Runtime output: `C:\Users\Administrator\Documents\Codex\2026-06-16\new-chat-3\outputs\memory-graph-viewer`
- Verify: generated `graph.json`, `index.html`, `viewer-3d.html`

- [ ] **Step 1: Export the full viewer**

Run:

```powershell
Set-Location "C:\Users\Administrator\total-agent-memory"
python src/tools/memory_graph_viewer_export.py --output "C:\Users\Administrator\Documents\Codex\2026-06-16\new-chat-3\outputs\memory-graph-viewer"
```

Expected: command prints JSON metadata including node and edge counts. `graph.json` exists in the output directory.

- [ ] **Step 2: Confirm copied assets exist**

Run:

```powershell
Get-ChildItem "C:\Users\Administrator\Documents\Codex\2026-06-16\new-chat-3\outputs\memory-graph-viewer" | Select-Object Name,Length
```

Expected: includes `index.html`, `viewer.js`, `viewer-3d.html`, `viewer-3d.js`, `memory-galaxy-core.js`, `memory-galaxy-events.js`, `viewer-shared.js`, `styles.css`, and `graph.json`.

- [ ] **Step 3: Start or reuse static server**

If port 8765 is free, run:

```powershell
Set-Location "C:\Users\Administrator\Documents\Codex\2026-06-16\new-chat-3\outputs\memory-graph-viewer"
Start-Process -WindowStyle Hidden python -ArgumentList "-m", "http.server", "8765", "--bind", "127.0.0.1"
```

If port 8765 is occupied by an unrelated process, use 8766 and report the actual URL.

Expected URL:

```text
http://127.0.0.1:8765/
```

- [ ] **Step 4: HTTP smoke check**

Run:

```powershell
Invoke-WebRequest "http://127.0.0.1:8765/" -UseBasicParsing | Select-Object -ExpandProperty StatusCode
Invoke-WebRequest "http://127.0.0.1:8765/viewer-3d.html" -UseBasicParsing | Select-Object -ExpandProperty StatusCode
Invoke-WebRequest "http://127.0.0.1:8765/graph.json" -UseBasicParsing | Select-Object -ExpandProperty StatusCode
```

Expected: all return `200`.

- [ ] **Step 5: Browser verification**

Use Playwright or the available browser automation tool to open:

```text
http://127.0.0.1:8765/
http://127.0.0.1:8765/viewer-3d.html
```

Expected:

- 2D galaxy canvas is nonblank.
- 3D sphere canvas is nonblank.
- No console errors.
- Clicking a 2D node updates details.
- Dragging a 2D node changes its position and triggers an agent prompt.
- 3D sphere rotates and selecting a star updates details.
- The visible node counts respect default budgets.

- [ ] **Step 6: Commit verification docs if docs changed**

If verification uncovered doc updates, commit them:

```powershell
git add docs/v12.5.0-memory-graph-viewer.md
git commit -m "docs: update memory galaxy viewer usage"
```

Expected: skip if no docs changed.

## Task 9: Update Documentation and Final Checks

**Files:**
- Modify: `docs/v12.5.0-memory-graph-viewer.md`

- [ ] **Step 1: Update viewer documentation**

Replace the "Memory Galaxy Mode" section in `docs/v12.5.0-memory-graph-viewer.md` with:

```markdown
## Memory Galaxy Views

Open `index.html` for the 2D Memory Galaxy view. This is the default exploration surface: a draggable local star map with search, type filters, galaxy-layer filters, timeline filtering, selected-node details, provenance/source display, and local agent prompt stubs.

Open `viewer-3d.html` for the 3D Memory Sphere view. It renders a curated spherical galaxy of memory nodes across semantic shells so core, active, knowledge, episode, and external nodes can be explored spatially without loading the whole graph at once.

Both views use a default visible-node budget to stay responsive. Full graph exploration should be treated as an advanced mode for powerful browsers, not the default.

The viewer exports cache metadata with the default cache root:

```text
D:\TotalAgentMemory\memory-galaxy-cache
```

The browser viewer remains static and local. Interaction events such as node selection, dragging, expansion, and filtering are normalized in the browser so future voice or agent adapters can react to them, but this release does not call external APIs or write to the memory database.
```

- [ ] **Step 2: Run all relevant tests**

Run:

```powershell
python -m pytest tests/test_memory_graph_viewer_export.py -v
node tests/js/memory_galaxy_smoke.test.mjs
node --check src/tools/memory_graph_viewer_assets/viewer.js
node --check src/tools/memory_graph_viewer_assets/viewer-3d.js
```

Expected: PASS.

- [ ] **Step 3: Check final git diff**

Run:

```powershell
git status --short
git diff --stat
```

Expected: only intended viewer, tests, exporter, and docs files are changed. `evals/results/` remains untracked unless the user explicitly asks to include it.

- [ ] **Step 4: Commit docs**

Run:

```powershell
git add docs/v12.5.0-memory-graph-viewer.md
git commit -m "docs: document memory galaxy redesign"
```

Expected: commit succeeds if docs changed.

- [ ] **Step 5: Save implementation memory**

After all tasks are implemented and verified, save a memory record:

```text
Implemented the Total Agent Memory galaxy redesign: 2D PixiJS galaxy replaced old Cytoscape 2D viewer, 3D Three.js spherical galaxy replaced nebula view, cache metadata defaults to D:\TotalAgentMemory\memory-galaxy-cache, and renderer-independent interaction events prepare future voice/agent prompts.
```

Use tags:

```text
memory-galaxy, visualization, pixijs, threejs, interaction-events, total-agent-memory
```

Expected: memory save succeeds.

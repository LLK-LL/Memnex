# Memory Galaxy 2D Playability Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the 2D Memory Galaxy readable and playful by reducing edge/label clutter, splitting the layout into multiple star clusters, adding spring-back dragging, and replacing the flat background with a deeper space scene.

**Architecture:** Keep the current static PixiJS viewer. Add graph-level pure helpers in `memory-galaxy-core.js` for edge pruning, multi-cluster positioning, and label visibility, then update `viewer.js` to render only quiet default edges and animate dragged nodes back with a spring. Update `styles.css` to use layered deep-space gradients and star-field texture effects without adding image assets.

**Tech Stack:** Static JavaScript ES modules, PixiJS 8, CSS gradients, Node.js smoke tests, pytest exporter tests.

---

## Scope

This is a focused 2D upgrade. Do not rewrite the 3D sphere view in this plan.

The upgrade implements:

- Default edge denoising: each node keeps only its strongest `3-5` visible links unless selected.
- Quiet default edges: non-selected edges are faint enough to be background texture.
- Focus edge reveal: selected or hovered nodes reveal stronger one-hop links.
- Multi-cluster galaxy layout: nodes are divided into visual islands by type family.
- Ring layout inside each cluster: core, active, knowledge, episode, and external nodes occupy different local radii.
- Label gating: default labels only for core, active, selected, and hovered nodes; other labels appear at high zoom or hover.
- Spring-back dragging: drag offset is animated back toward the original orbit, retaining `15-25%` of the user displacement.
- Deep-space background: no flat color; use layered dark radial gradients, star speckles, and subtle nebula light.

## File Structure

- Modify: `src/tools/memory_graph_viewer_assets/memory-galaxy-core.js`
  - Add `buildClusterGalaxy2DLayout`, `pruneGalaxyLinks`, `visibleLinksForSelection`, and refined `selectVisibleLabels`.
- Modify: `tests/js/memory_galaxy_smoke.test.mjs`
  - Add pure tests for cluster separation, edge pruning, focus edge reveal, label gating, and spring target math.
- Modify: `src/tools/memory_graph_viewer_assets/viewer.js`
  - Use clustered layout and pruned links.
  - Add `dragOffsetByNodeId`, `springAnimations`, and animation ticker.
  - Draw selected and focus links above faint background links.
- Modify: `src/tools/memory_graph_viewer_assets/styles.css`
  - Add deep-space background layers to `.galaxy-canvas` and `.graph-3d`.
  - Add canvas overlay pseudo-elements for star field texture.

## Task 1: Add Pure Tests for Denoising and Cluster Layout

**Files:**
- Modify: `tests/js/memory_galaxy_smoke.test.mjs`
- Modify: `src/tools/memory_graph_viewer_assets/memory-galaxy-core.js`

- [ ] **Step 1: Export the new helper names in the JS smoke loader**

In `tests/js/memory_galaxy_smoke.test.mjs`, extend the core helper VM export block with:

```javascript
exports.buildClusterGalaxy2DLayout = buildClusterGalaxy2DLayout;
exports.pruneGalaxyLinks = pruneGalaxyLinks;
exports.visibleLinksForSelection = visibleLinksForSelection;
exports.springBackTarget = springBackTarget;
```

Extend the destructuring block with:

```javascript
  buildClusterGalaxy2DLayout,
  pruneGalaxyLinks,
  visibleLinksForSelection,
  springBackTarget,
```

- [ ] **Step 2: Add a dense-link fixture**

Append this fixture near the bottom of `tests/js/memory_galaxy_smoke.test.mjs`:

```javascript
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
```

- [ ] **Step 3: Add failing tests for edge pruning**

Append:

```javascript
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
```

- [ ] **Step 4: Add failing tests for cluster layout separation**

Append:

```javascript
const clustered = buildClusterGalaxy2DLayout(denseGalaxy, { maxNodes: 6 });
const byIdClustered = new Map(clustered.nodes.map(node => [node.id, node]));
assert.ok(Math.hypot(byIdClustered.get("project").x - byIdClustered.get("event").x, byIdClustered.get("project").y - byIdClustered.get("event").y) > 220);
assert.ok(Math.hypot(byIdClustered.get("concept").x - byIdClustered.get("tech").x, byIdClustered.get("concept").y - byIdClustered.get("tech").y) > 120);
assert.ok(clustered.nodes.every(node => node.clusterKey));
assert.ok(clustered.nodes.every(node => Number.isFinite(node.homeX) && Number.isFinite(node.homeY)));
```

- [ ] **Step 5: Add failing tests for spring-back target**

Append:

```javascript
const springTarget = springBackTarget(
  { homeX: 100, homeY: 50, x: 300, y: 150 },
  { retainRatio: 0.2 },
);
assert.deepEqual(springTarget, { x: 140, y: 70 });
```

- [ ] **Step 6: Run JS smoke test and verify failure**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: FAIL because the new helper functions do not exist.

- [ ] **Step 7: Add cluster constants and type-family helper**

In `src/tools/memory_graph_viewer_assets/memory-galaxy-core.js`, after `sphereShell`, add:

```javascript
const clusterCenters = {
  project: { x: -360, y: -150 },
  concept: { x: 0, y: -190 },
  technology: { x: 360, y: -120 },
  pattern: { x: -260, y: 190 },
  event: { x: 190, y: 210 },
  external: { x: 470, y: 150 },
};

function clusterKeyForType(type) {
  if (type === "project") return "project";
  if (type === "concept" || type === "domain") return "concept";
  if (type === "technology" || type === "company") return "technology";
  if (type === "pattern" || type === "rule" || type === "decision") return "pattern";
  if (type === "event" || type === "episode" || type === "session" || type === "observation") return "event";
  return "external";
}
```

- [ ] **Step 8: Add `pruneGalaxyLinks` and `visibleLinksForSelection`**

Before `buildEditIntent`, add:

```javascript
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
    if (sourceCount >= perNodeLimit && targetCount >= perNodeLimit) continue;
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
```

- [ ] **Step 9: Add `buildClusterGalaxy2DLayout` and `springBackTarget`**

After `buildGalaxy2DLayout`, add:

```javascript
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
```

- [ ] **Step 10: Refine label gating**

In `selectVisibleLabels`, replace the filter condition with:

```javascript
      node.id === selectedNodeId ||
      node.id === hoveredNodeId ||
      node.layer === "core" ||
      node.layer === "active" ||
      (zoom >= 1.55 && Number(node.raw.importance || 0) >= 0.7) ||
      (zoom >= 2.2 && Number(node.raw.mention_count || 0) >= 3)
```

- [ ] **Step 11: Run tests**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
python -m pytest tests/test_memory_graph_viewer_export.py -v
```

Expected: PASS.

- [ ] **Step 12: Commit**

Run:

```powershell
git add tests/js/memory_galaxy_smoke.test.mjs src/tools/memory_graph_viewer_assets/memory-galaxy-core.js
git commit -m "feat: denoise and cluster 2d memory galaxy"
```

## Task 2: Render Quiet Links and Focus Links in 2D Viewer

**Files:**
- Modify: `src/tools/memory_graph_viewer_assets/viewer.js`

- [ ] **Step 1: Update imports**

In `viewer.js`, replace the current import from `memory-galaxy-core.js` with:

```javascript
import {
  buildClusterGalaxy2DLayout,
  buildFocusGalaxy,
  convertGraphToGalaxy,
  filterGalaxy,
  selectVisibleLabels,
  visibleLinksForSelection,
  springBackTarget,
} from "./memory-galaxy-core.js";
```

- [ ] **Step 2: Use clustered layout in `applyFilters`**

Replace:

```javascript
  visibleGraph = buildGalaxy2DLayout(filtered, { maxNodes: focusLimit });
```

with:

```javascript
  visibleGraph = buildClusterGalaxy2DLayout(filtered, { maxNodes: focusLimit, perNodeLimit: 4 });
```

- [ ] **Step 3: Use clustered layout in `focusNeighborhood`**

Replace:

```javascript
  visibleGraph = buildGalaxy2DLayout(buildFocusGalaxy(originalGraph, {
```

with:

```javascript
  visibleGraph = buildClusterGalaxy2DLayout(buildFocusGalaxy(originalGraph, {
```

Keep the existing options object and trailing `), { maxNodes: 260, focusNodeId: selectedNode.id });`.

- [ ] **Step 4: Split default and focus link drawing**

In `drawGalaxy`, replace:

```javascript
  for (const link of visibleGraph.links) {
```

with:

```javascript
  const linksToDraw = visibleLinksForSelection(visibleGraph.links, {
    selectedNodeId,
    hoveredNodeId,
    perNodeLimit: 4,
  });
  for (const link of linksToDraw) {
```

- [ ] **Step 5: Reduce default edge opacity**

In the `line.stroke` call in `drawGalaxy`, replace:

```javascript
alpha: selected ? 0.78 : 0.26
```

with:

```javascript
alpha: selected ? 0.82 : 0.075
```

Replace:

```javascript
color: selected ? 0xfacc15 : 0x5b6f91
```

with:

```javascript
color: selected ? 0xfacc15 : 0x31445f
```

- [ ] **Step 6: Make selected focus links brighter**

Replace the width expression:

```javascript
width: selected ? 2.2 : Math.max(0.4, Math.min(1.6, link.weight * 0.45))
```

with:

```javascript
width: selected ? Math.max(2.2, Math.min(4.2, link.weight * 0.55)) : Math.max(0.25, Math.min(1.1, link.weight * 0.28))
```

- [ ] **Step 7: Run syntax and tests**

Run:

```powershell
node --check src/tools/memory_graph_viewer_assets/viewer.js
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: PASS.

- [ ] **Step 8: Commit**

Run:

```powershell
git add src/tools/memory_graph_viewer_assets/viewer.js
git commit -m "feat: render quiet and focused galaxy links"
```

## Task 3: Add Spring-Back Dragging and Neighbor Gravity

**Files:**
- Modify: `src/tools/memory_graph_viewer_assets/viewer.js`

- [ ] **Step 1: Add drag state maps**

After:

```javascript
let dragState = null;
```

add:

```javascript
const springAnimations = new Map();
const dragOffsetByNodeId = new Map();
```

- [ ] **Step 2: Start Pixi ticker**

At the end of `createPixi`, after the resize listener, add:

```javascript
  app.ticker.add(tickSpringAnimations);
```

- [ ] **Step 3: Preserve drag offsets after new layout**

In `applyFilters`, after `visibleGraph = ...`, add:

```javascript
  for (const node of visibleGraph.nodes) {
    const offset = dragOffsetByNodeId.get(node.id);
    if (!offset) continue;
    node.x += offset.x;
    node.y += offset.y;
  }
```

- [ ] **Step 4: Capture dragged node home position**

In `onNodePointerDown`, replace the `dragState = ...` assignment with:

```javascript
  springAnimations.delete(node.id);
  dragState = {
    node,
    star,
    start: event.global.clone(),
    origin: { x: node.x, y: node.y },
    home: { x: node.homeX ?? node.x, y: node.homeY ?? node.y },
    mode: "node",
  };
```

- [ ] **Step 5: Add neighbor gravity while dragging**

In `onStagePointerMove`, after:

```javascript
  dragState.node.x = dragState.origin.x + dx;
  dragState.node.y = dragState.origin.y + dy;
```

add:

```javascript
  applyNeighborGravity(dragState.node, dx, dy);
```

- [ ] **Step 6: Start spring animation on release**

In `onStagePointerUp`, inside `if (dragState?.mode === "node") { ... }`, before `emitEvent("node:drag-ended"...`, add:

```javascript
    const target = springBackTarget(dragState.node, { retainRatio: 0.2 });
    springAnimations.set(dragState.node.id, {
      node: dragState.node,
      target,
      velocity: { x: 0, y: 0 },
    });
    dragOffsetByNodeId.set(dragState.node.id, {
      x: target.x - (dragState.node.homeX ?? target.x),
      y: target.y - (dragState.node.homeY ?? target.y),
    });
```

- [ ] **Step 7: Add spring ticker functions**

Before `onWheel`, add:

```javascript
function tickSpringAnimations() {
  if (springAnimations.size === 0) return;
  let changed = false;
  for (const [nodeId, animation] of springAnimations) {
    const node = animation.node;
    const dx = animation.target.x - node.x;
    const dy = animation.target.y - node.y;
    animation.velocity.x = (animation.velocity.x + dx * 0.08) * 0.72;
    animation.velocity.y = (animation.velocity.y + dy * 0.08) * 0.72;
    node.x += animation.velocity.x;
    node.y += animation.velocity.y;
    if (Math.abs(dx) < 0.6 && Math.abs(dy) < 0.6 && Math.hypot(animation.velocity.x, animation.velocity.y) < 0.25) {
      node.x = animation.target.x;
      node.y = animation.target.y;
      springAnimations.delete(nodeId);
    }
    changed = true;
  }
  if (changed) drawGalaxy();
}

function applyNeighborGravity(node, dx, dy) {
  const neighborIds = new Set();
  for (const link of visibleGraph.links) {
    const source = String(link.source.id || link.source);
    const target = String(link.target.id || link.target);
    if (source === node.id) neighborIds.add(target);
    if (target === node.id) neighborIds.add(source);
  }
  for (const neighbor of visibleGraph.nodes) {
    if (!neighborIds.has(neighbor.id)) continue;
    neighbor.x += dx * 0.035;
    neighbor.y += dy * 0.035;
  }
}
```

- [ ] **Step 8: Run syntax check**

Run:

```powershell
node --check src/tools/memory_graph_viewer_assets/viewer.js
```

Expected: PASS.

- [ ] **Step 9: Export and manually verify drag feel**

Run:

```powershell
python src/tools/memory_graph_viewer_export.py --output "C:\Users\Administrator\Documents\Codex\2026-06-16\new-chat-3\outputs\memory-graph-viewer"
```

Open:

```text
http://127.0.0.1:8765/
```

Expected:

- Dragging a node moves it smoothly.
- Neighbor nodes drift slightly with it.
- Releasing the node creates a visible spring-back motion.
- The node retains a small offset instead of snapping fully home.

- [ ] **Step 10: Commit**

Run:

```powershell
git add src/tools/memory_graph_viewer_assets/viewer.js
git commit -m "feat: add spring drag to memory galaxy"
```

## Task 4: Add Deep-Space Background

**Files:**
- Modify: `src/tools/memory_graph_viewer_assets/styles.css`

- [ ] **Step 1: Replace the current galaxy background**

In `styles.css`, replace the `.galaxy-canvas, .graph-3d` `background` block with:

```css
  background:
    radial-gradient(circle at 50% 48%, rgba(125, 211, 252, 0.16), transparent 18%),
    radial-gradient(circle at 18% 20%, rgba(168, 85, 247, 0.16), transparent 24%),
    radial-gradient(circle at 82% 28%, rgba(45, 212, 191, 0.12), transparent 22%),
    radial-gradient(circle at 62% 82%, rgba(37, 99, 235, 0.16), transparent 28%),
    linear-gradient(145deg, #02040b 0%, #06111f 42%, #020617 100%);
```

- [ ] **Step 2: Add a star-field overlay**

After `.galaxy-canvas, .graph-3d`, add:

```css
.galaxy-canvas::before,
.graph-3d::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background-image:
    radial-gradient(circle, rgba(255,255,255,0.85) 0 1px, transparent 1.4px),
    radial-gradient(circle, rgba(147,197,253,0.75) 0 1px, transparent 1.6px),
    radial-gradient(circle, rgba(255,255,255,0.45) 0 0.8px, transparent 1.2px);
  background-size: 160px 160px, 230px 230px, 310px 310px;
  background-position: 12px 18px, 80px 42px, 140px 120px;
  opacity: 0.38;
}

.galaxy-canvas::after,
.graph-3d::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(ellipse at center, transparent 0%, transparent 52%, rgba(0,0,0,0.42) 100%);
}
```

- [ ] **Step 3: Ensure canvas remains above overlays**

Add:

```css
.galaxy-canvas canvas,
.graph-3d canvas {
  position: relative;
  z-index: 1;
}
```

If this selector already exists, merge the new `position` and `z-index` into it.

- [ ] **Step 4: Run static checks**

Run:

```powershell
node --check src/tools/memory_graph_viewer_assets/viewer.js
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: PASS.

- [ ] **Step 5: Export and inspect**

Run:

```powershell
python src/tools/memory_graph_viewer_export.py --output "C:\Users\Administrator\Documents\Codex\2026-06-16\new-chat-3\outputs\memory-graph-viewer"
```

Open:

```text
http://127.0.0.1:8765/
```

Expected:

- Background reads as deep space, not flat navy.
- Star speckles are visible but do not compete with memory nodes.
- Edge clutter is reduced enough that the background remains visible.

- [ ] **Step 6: Commit**

Run:

```powershell
git add src/tools/memory_graph_viewer_assets/styles.css
git commit -m "style: add deep space galaxy backdrop"
```

## Task 5: Final Verification

**Files:**
- Verify: `src/tools/memory_graph_viewer_assets/memory-galaxy-core.js`
- Verify: `src/tools/memory_graph_viewer_assets/viewer.js`
- Verify: `src/tools/memory_graph_viewer_assets/styles.css`

- [ ] **Step 1: Run all focused tests**

Run:

```powershell
python -m pytest tests/test_memory_graph_viewer_export.py -v
node tests/js/memory_galaxy_smoke.test.mjs
node --check src/tools/memory_graph_viewer_assets/viewer.js
node --check src/tools/memory_graph_viewer_assets/viewer-3d.js
```

Expected: PASS.

- [ ] **Step 2: Re-export viewer**

Run:

```powershell
python src/tools/memory_graph_viewer_export.py --output "C:\Users\Administrator\Documents\Codex\2026-06-16\new-chat-3\outputs\memory-graph-viewer"
```

Expected: export metadata prints node and edge counts; output assets are refreshed.

- [ ] **Step 3: HTTP smoke check**

Run:

```powershell
Invoke-WebRequest "http://127.0.0.1:8765/" -UseBasicParsing | Select-Object -ExpandProperty StatusCode
Invoke-WebRequest "http://127.0.0.1:8765/viewer.js" -UseBasicParsing | Select-Object -ExpandProperty StatusCode
Invoke-WebRequest "http://127.0.0.1:8765/styles.css" -UseBasicParsing | Select-Object -ExpandProperty StatusCode
```

Expected: all return `200`.

- [ ] **Step 4: Manual visual checklist**

Open:

```text
http://127.0.0.1:8765/
```

Expected:

- The first view shows several star islands, not one dense oval.
- Labels are not stacked in the center.
- Most edges are faint until a node is selected or hovered.
- Dragging a node has a playful spring-back feel.
- The background feels like deep space and remains behind the graph.

- [ ] **Step 5: Save implementation memory**

After implementation, save:

```text
Improved 2D Memory Galaxy readability and playability by pruning default links, splitting nodes into type-family star clusters, gating labels by layer/zoom/selection, adding spring-back dragging with slight neighbor gravity, and replacing the flat canvas background with layered deep-space CSS.
```

Use tags:

```text
memory-galaxy, 2d-viewer, playability, graph-denoising, spring-drag, deep-space-background
```

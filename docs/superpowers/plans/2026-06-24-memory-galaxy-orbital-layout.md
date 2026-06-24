# Memory Galaxy Orbital Layout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current type-clustered 2D star map with a galactic-orbital memory layout where Router is the galactic core, Rule/Persona/Skill/Harness and other domains are star systems, related memories orbit their strongest semantic center, and node size reflects memory-layer priority.

**Architecture:** Keep the static PixiJS viewer and existing export format. Add pure layout helpers in `memory-galaxy-core.js` that infer a node's memory system, priority, orbital parent, radius, and label anchor. Then update `viewer.js` to render orbit guides, larger priority-based stars, sharper labels, and clearer intra-system versus cross-system links.

**Tech Stack:** Static JavaScript ES modules, PixiJS 8, Node.js smoke tests, pytest exporter tests, existing local static viewer export.

---

## Design Decisions

- **Galactic Core:** Router/Routing nodes sit near the center. They represent top-level orchestration, not the biggest pile of content.
- **Star Systems:** Rule, Persona, Skill, Harness, Project, Preference, Knowledge, Event, and Source are orbital systems around the core. Each has one visual center and multiple rings.
- **Persona Layout:** Persona nodes represent identity, tone, long-term style, and user interaction preferences. They orbit a Persona star system near Rule and Preference.
- **Skill Layout:** Skill nodes represent callable procedures and triggerable capabilities. They orbit a Skill star system with category arcs such as coding, memory, research, visual, browser, planning, and debugging when those terms are detectable.
- **Harness Layout:** Harness nodes represent evaluation, tests, browser automation, workflow runners, verification, and execution infrastructure. They orbit a Harness star system placed near Skill because skills often execute through harnesses.
- **Node Diameter Priority:** Base visual diameter is driven by semantic priority first, then importance/activity/mention count. Priority order starts with Router, then Persona, Skill, Harness, Rule, Preference, Project, Knowledge, Event, Source.
- **Relationship Readability:** Spatial orbit is the first relationship cue. Lines become secondary: intra-system links are visible but calm, cross-system links are rare and curved, selected/hovered links become bright.
- **Text Clarity:** Labels are not drawn directly on tiny stars. Hub labels and selected/hovered labels use a high-contrast backing plate. Other labels appear by zoom/density mode and are offset outward from their orbit.

## File Structure

- Modify: `tests/js/memory_galaxy_smoke.test.mjs`
  - Add tests for memory-system inference, priority diameter mapping, orbital parent selection, orbital layout hierarchy, and label anchor offsets.
- Modify: `src/tools/memory_graph_viewer_assets/memory-galaxy-core.js`
  - Add `memorySystemForNode`, `priorityRadiusForNode`, `buildGalacticOrbital2DLayout`, `labelAnchorForNode`, and link classification helpers.
- Modify: `src/tools/memory_graph_viewer_assets/viewer.js`
  - Switch from `buildClusterGalaxy2DLayout` to `buildGalacticOrbital2DLayout`.
  - Draw orbital guides and system hub labels.
  - Render priority-sized stars and sharper label plates.
  - Draw intra-system and cross-system links with different visual weights.
- Modify: `src/tools/memory_graph_viewer_assets/styles.css`
  - Add no new app structure; only adjust canvas/label-support classes if DOM label overlays are introduced. Prefer Pixi labels first.
- Verify: `src/tools/memory_graph_viewer_export.py`
  - No schema change required. Existing `type`, `label`, `content`, `galaxy_layer`, `importance`, `activity`, `mention_count`, and relation weights are enough.

## Task 1: Add Pure Tests for Galactic-Orbital Semantics

**Files:**
- Modify: `tests/js/memory_galaxy_smoke.test.mjs`
- Modify: `src/tools/memory_graph_viewer_assets/memory-galaxy-core.js`

- [ ] **Step 1: Export the new helper names in the JS smoke loader**

In `tests/js/memory_galaxy_smoke.test.mjs`, extend the VM export block after:

```javascript
exports.springBackTarget = springBackTarget;`;
```

Replace that final line with:

```javascript
exports.springBackTarget = springBackTarget;
exports.memorySystemForNode = memorySystemForNode;
exports.priorityRadiusForNode = priorityRadiusForNode;
exports.buildGalacticOrbital2DLayout = buildGalacticOrbital2DLayout;
exports.labelAnchorForNode = labelAnchorForNode;`,
```

Extend the destructuring block after `springBackTarget,` with:

```javascript
  memorySystemForNode,
  priorityRadiusForNode,
  buildGalacticOrbital2DLayout,
  labelAnchorForNode,
```

- [ ] **Step 2: Add a semantic-system fixture**

Append this fixture near the existing `denseFixture` block:

```javascript
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
```

- [ ] **Step 3: Add failing tests for memory-system inference**

Append:

```javascript
const orbitalById = new Map(orbitalGalaxy.nodes.map(node => [node.id, node]));
assert.equal(memorySystemForNode(orbitalById.get("router")), "router");
assert.equal(memorySystemForNode(orbitalById.get("rule")), "rule");
assert.equal(memorySystemForNode(orbitalById.get("persona")), "persona");
assert.equal(memorySystemForNode(orbitalById.get("skill")), "skill");
assert.equal(memorySystemForNode(orbitalById.get("harness")), "harness");
assert.equal(memorySystemForNode(orbitalById.get("pref")), "preference");
assert.equal(memorySystemForNode(orbitalById.get("source")), "event");
```

- [ ] **Step 4: Add failing tests for priority diameter mapping**

Append:

```javascript
assert.ok(priorityRadiusForNode(orbitalById.get("router")) > priorityRadiusForNode(orbitalById.get("rule")));
assert.ok(priorityRadiusForNode(orbitalById.get("persona")) > priorityRadiusForNode(orbitalById.get("pref")));
assert.ok(priorityRadiusForNode(orbitalById.get("skill")) > priorityRadiusForNode(orbitalById.get("memory")));
assert.ok(priorityRadiusForNode(orbitalById.get("harness")) > priorityRadiusForNode(orbitalById.get("source")));
```

- [ ] **Step 5: Add failing tests for orbital layout hierarchy**

Append:

```javascript
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
```

- [ ] **Step 6: Add failing tests for label anchors**

Append:

```javascript
const prefNode = orbitalLayoutById.get("pref");
const prefAnchor = labelAnchorForNode(prefNode);
assert.ok(Number.isFinite(prefAnchor.x));
assert.ok(Number.isFinite(prefAnchor.y));
assert.ok(Math.hypot(prefAnchor.x - prefNode.x, prefAnchor.y - prefNode.y) >= prefNode.renderRadius + 12);
assert.ok(["left", "right"].includes(prefAnchor.align));
```

- [ ] **Step 7: Run JS smoke test and verify failure**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: FAIL with `memorySystemForNode is not defined`.

## Task 2: Implement Pure Galactic-Orbital Layout Helpers

**Files:**
- Modify: `src/tools/memory_graph_viewer_assets/memory-galaxy-core.js`
- Test: `tests/js/memory_galaxy_smoke.test.mjs`

- [ ] **Step 1: Add system constants after `clusterCenters`**

In `src/tools/memory_graph_viewer_assets/memory-galaxy-core.js`, after `clusterCenters`, add:

```javascript
const galacticSystemCenters = {
  router: { x: 0, y: 0, orbitRadius: 0, label: "Router Core" },
  rule: { x: -330, y: -150, orbitRadius: 128, label: "Rules" },
  persona: { x: 0, y: -250, orbitRadius: 126, label: "Persona" },
  skill: { x: 345, y: -120, orbitRadius: 142, label: "Skills" },
  harness: { x: 365, y: 185, orbitRadius: 122, label: "Harness" },
  preference: { x: -335, y: 185, orbitRadius: 112, label: "Preferences" },
  project: { x: 0, y: 265, orbitRadius: 126, label: "Projects" },
  knowledge: { x: -610, y: 35, orbitRadius: 118, label: "Knowledge" },
  event: { x: 610, y: 45, orbitRadius: 112, label: "Events" },
  source: { x: 0, y: 470, orbitRadius: 96, label: "Sources" },
};

const memorySystemPriority = {
  router: 56,
  persona: 48,
  skill: 44,
  harness: 40,
  rule: 38,
  preference: 30,
  project: 28,
  knowledge: 20,
  event: 14,
  source: 10,
};
```

- [ ] **Step 2: Add semantic text helper before `buildAdjacency`**

Add:

```javascript
function semanticText(node) {
  return [
    node.id,
    node.label,
    node.type,
    node.layer,
    node.raw?.content,
    node.raw?.source,
    node.raw?.project,
    ...(node.raw?.knowledge || []).map(item => `${item.type || ""} ${item.project || ""} ${item.summary || ""}`),
  ].join(" ").toLowerCase();
}
```

- [ ] **Step 3: Add `memorySystemForNode` before `buildEditIntent`**

Add:

```javascript
export function memorySystemForNode(node) {
  const text = semanticText(node);
  if (/\b(router|routing|route|dispatch|orchestrat)/.test(text)) return "router";
  if (/\b(persona|personality|identity|tone|style|voice|character)\b/.test(text)) return "persona";
  if (/\b(skill|capability|trigger|workflow|procedure)\b/.test(text) || node.type === "capability") return "skill";
  if (/\b(harness|eval|evaluation|pytest|test runner|smoke test|verification|browser automation|playwright|workflow runner)\b/.test(text)) return "harness";
  if (node.type === "rule" || /\b(rule|policy|must|never|required)\b/.test(text)) return "rule";
  if (/\b(preference|prefers|user wants|style preference|interaction preference)\b/.test(text)) return "preference";
  if (node.type === "project") return "project";
  if (["event", "episode", "session", "observation"].includes(node.type) || node.layer === "episode") return "event";
  if (/\b(source|provenance|evidence|citation|origin)\b/.test(text) || node.layer === "external") return "source";
  return "knowledge";
}
```

- [ ] **Step 4: Add `priorityRadiusForNode` after `memorySystemForNode`**

Add:

```javascript
export function priorityRadiusForNode(node) {
  const system = memorySystemForNode(node);
  const baseDiameter = memorySystemPriority[system] || memorySystemPriority.knowledge;
  const importance = Number(node.raw?.importance || 0);
  const activity = Number(node.raw?.activity || 0);
  const mentions = Math.log1p(Number(node.raw?.mention_count || 0));
  const diameter = baseDiameter + importance * 3 + activity * 4 + mentions * 1.4;
  return Math.max(6, Math.min(34, diameter / 2));
}
```

- [ ] **Step 5: Add system star selection helper after `priorityRadiusForNode`**

Add:

```javascript
function starNodeIdsBySystem(nodes) {
  const best = new Map();
  for (const node of nodes) {
    const system = memorySystemForNode(node);
    const current = best.get(system);
    if (!current || nodeScore(node) > nodeScore(current)) best.set(system, node);
  }
  return new Map([...best].map(([system, node]) => [system, node.id]));
}
```

- [ ] **Step 6: Add `buildGalacticOrbital2DLayout` after `buildClusterGalaxy2DLayout`**

Add:

```javascript
export function buildGalacticOrbital2DLayout(galaxy, options = {}) {
  const focused = buildFocusGalaxy(galaxy, {
    maxNodes: Number(options.maxNodes || 850),
    seedCount: Number(options.seedCount || 48),
    firstRingLimit: Number(options.firstRingLimit || 540),
    focusNodeId: options.focusNodeId,
  });
  const starIds = starNodeIdsBySystem(focused.nodes);
  const nodes = focused.nodes.map((node, index) => {
    const memorySystem = memorySystemForNode(node);
    const systemCenter = galacticSystemCenters[memorySystem] || galacticSystemCenters.knowledge;
    const starId = starIds.get(memorySystem);
    const orbitalRole = memorySystem === "router"
      ? "galactic-core"
      : node.id === starId
        ? "star"
        : node.layer === "episode" || memorySystem === "source"
          ? "moon"
          : "planet";
    const angle = hashAngle(`${node.id}:orbital:${memorySystem}`);
    const ringBase = orbitalRole === "star"
      ? 0
      : orbitalRole === "moon"
        ? systemCenter.orbitRadius * 1.42
        : systemCenter.orbitRadius;
    const jitter = orbitalRole === "star" ? 0 : ((hashNumber(`${node.id}:orbital-jitter`) % 100) / 100) * 34;
    const radius = ringBase + jitter + ((index % 5) * 5);
    const flatten = memorySystem === "router" ? 1 : 0.64;
    const x = memorySystem === "router"
      ? Math.cos(angle) * Math.min(48, radius + 34)
      : systemCenter.x + Math.cos(angle) * radius;
    const y = memorySystem === "router"
      ? Math.sin(angle) * Math.min(38, radius + 26)
      : systemCenter.y + Math.sin(angle) * radius * flatten;
    return {
      ...node,
      clusterKey: memorySystem,
      memorySystem,
      orbitalRole,
      systemCenter,
      homeX: x,
      homeY: y,
      x,
      y,
      z: 0,
      renderRadius: priorityRadiusForNode(node),
      labelPriority: nodeScore(node) + (orbitalRole === "star" || orbitalRole === "galactic-core" ? 12 : 0),
    };
  });
  const pruned = pruneGalaxyLinks({ nodes, links: focused.links, metadata: focused.metadata }, {
    perNodeLimit: Number(options.perNodeLimit || 4),
  });
  return {
    nodes,
    links: pruned.links,
    metadata: focused.metadata,
    systems: Object.entries(galacticSystemCenters).map(([key, value]) => ({ key, ...value })),
  };
}
```

- [ ] **Step 7: Add `labelAnchorForNode` after `buildGalacticOrbital2DLayout`**

Add:

```javascript
export function labelAnchorForNode(node) {
  const center = node.systemCenter || { x: 0, y: 0 };
  const dx = node.x - center.x;
  const dy = node.y - center.y;
  const distance = Math.max(1, Math.hypot(dx, dy));
  const offset = Number(node.renderRadius || 8) + (node.orbitalRole === "star" || node.orbitalRole === "galactic-core" ? 20 : 14);
  const x = node.x + (dx / distance) * offset;
  const y = node.y + (dy / distance) * offset;
  return {
    x,
    y,
    align: x >= node.x ? "left" : "right",
  };
}
```

- [ ] **Step 8: Run JS smoke test**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: PASS.

- [ ] **Step 9: Commit pure layout helpers**

Run:

```powershell
git add tests/js/memory_galaxy_smoke.test.mjs src/tools/memory_graph_viewer_assets/memory-galaxy-core.js
git commit -m "feat: add galactic orbital memory layout"
```

Expected: commit succeeds.

## Task 3: Switch 2D Viewer to Orbital Layout and Draw System Guides

**Files:**
- Modify: `src/tools/memory_graph_viewer_assets/viewer.js`
- Test: `src/tools/memory_graph_viewer_assets/viewer.js`

- [ ] **Step 1: Update imports**

In `viewer.js`, replace:

```javascript
  buildClusterGalaxy2DLayout,
```

with:

```javascript
  buildGalacticOrbital2DLayout,
  labelAnchorForNode,
```

- [ ] **Step 2: Add system guide layer state**

After:

```javascript
let linkLayer;
```

add:

```javascript
let orbitLayer;
```

- [ ] **Step 3: Create orbit layer before link layer**

In `createPixi`, replace:

```javascript
  linkLayer = new PIXI.Container();
  nodeLayer = new PIXI.Container();
  labelLayer = new PIXI.Container();
  stageRoot.addChild(linkLayer, nodeLayer, labelLayer);
```

with:

```javascript
  orbitLayer = new PIXI.Container();
  linkLayer = new PIXI.Container();
  nodeLayer = new PIXI.Container();
  labelLayer = new PIXI.Container();
  stageRoot.addChild(orbitLayer, linkLayer, nodeLayer, labelLayer);
```

- [ ] **Step 4: Use orbital layout in `applyFilters`**

Replace:

```javascript
  visibleGraph = buildClusterGalaxy2DLayout(filtered, { maxNodes: focusLimit, perNodeLimit: edgeDensity });
```

with:

```javascript
  visibleGraph = buildGalacticOrbital2DLayout(filtered, { maxNodes: focusLimit, perNodeLimit: edgeDensity });
```

- [ ] **Step 5: Use orbital layout in `focusNeighborhood`**

Replace:

```javascript
  visibleGraph = buildClusterGalaxy2DLayout(buildFocusGalaxy(originalGraph, {
```

with:

```javascript
  visibleGraph = buildGalacticOrbital2DLayout(buildFocusGalaxy(originalGraph, {
```

Keep the existing closing options object:

```javascript
  }), { maxNodes: 260, focusNodeId: selectedNode.id });
```

- [ ] **Step 6: Clear orbit layer in `drawGalaxy`**

At the top of `drawGalaxy`, before:

```javascript
  linkLayer.removeChildren();
```

add:

```javascript
  orbitLayer.removeChildren();
```

- [ ] **Step 7: Draw system guides before links**

After the `nodeById` line in `drawGalaxy`, add:

```javascript
  drawSystemGuides();
```

Before `drawStar`, add:

```javascript
function drawSystemGuides() {
  if (!visibleGraph.systems) return;
  for (const system of visibleGraph.systems) {
    if (system.key === "router") continue;
    const guide = new PIXI.Graphics();
    guide.ellipse(system.x, system.y, system.orbitRadius, system.orbitRadius * 0.64);
    guide.stroke({ width: 1.2, color: 0x5b6f91, alpha: 0.16 });
    guide.ellipse(system.x, system.y, system.orbitRadius * 1.42, system.orbitRadius * 0.91);
    guide.stroke({ width: 0.8, color: 0x5b6f91, alpha: 0.08 });
    orbitLayer.addChild(guide);
  }
}
```

- [ ] **Step 8: Classify link visuals by memory system**

In the link drawing loop, before `line.moveTo(...)`, add:

```javascript
    const sameSystem = source.memorySystem && source.memorySystem === target.memorySystem;
```

Replace the `line.stroke(...)` call with:

```javascript
    line.stroke({
      width: selected
        ? Math.max(2.4, Math.min(4.6, link.weight * 0.58))
        : sameSystem
          ? Math.max(0.35, Math.min(1.15, link.weight * 0.28))
          : Math.max(0.3, Math.min(0.9, link.weight * 0.18)),
      color: selected ? 0xfacc15 : sameSystem ? 0x3f6d8f : 0x6d5f9d,
      alpha: selected ? 0.84 : sameSystem ? 0.12 : 0.055,
    });
```

- [ ] **Step 9: Run syntax check**

Run:

```powershell
node --check src/tools/memory_graph_viewer_assets/viewer.js
```

Expected: PASS.

- [ ] **Step 10: Commit viewer layout switch**

Run:

```powershell
git add src/tools/memory_graph_viewer_assets/viewer.js
git commit -m "feat: use orbital layout in 2d memory galaxy"
```

Expected: commit succeeds.

## Task 4: Improve Label Sharpness and Avoid Label Overlap

**Files:**
- Modify: `src/tools/memory_graph_viewer_assets/viewer.js`
- Test: `src/tools/memory_graph_viewer_assets/viewer.js`

- [ ] **Step 1: Replace label drawing with anchored label plates**

In `drawGalaxy`, replace:

```javascript
  for (const node of selectVisibleLabels(visibleGraph.nodes, { zoom: scale * currentLabelZoomBoost(), selectedNodeId, hoveredNodeId })) {
    const label = new PIXI.Text({ text: node.label, style: { fill: 0xe5f0ff, fontFamily: "Segoe UI, Microsoft YaHei, sans-serif", fontSize: 12, fontWeight: "600" } });
    label.x = node.x + node.renderRadius + 7;
    label.y = node.y - 8;
    label.alpha = node.id === selectedNodeId || node.id === hoveredNodeId ? 1 : 0.72;
    labelLayer.addChild(label);
  }
```

with:

```javascript
  const placedLabelBounds = [];
  for (const node of selectVisibleLabels(visibleGraph.nodes, { zoom: scale * currentLabelZoomBoost(), selectedNodeId, hoveredNodeId })) {
    drawNodeLabel(node, placedLabelBounds);
  }
```

- [ ] **Step 2: Add `drawNodeLabel` before `drawSystemGuides`**

Add:

```javascript
function drawNodeLabel(node, placedLabelBounds) {
  const anchor = labelAnchorForNode(node);
  const isPinned = node.id === selectedNodeId || node.id === hoveredNodeId || node.orbitalRole === "star" || node.orbitalRole === "galactic-core";
  const fontSize = isPinned ? 13 : 11;
  const text = new PIXI.Text({
    text: node.label,
    resolution: 2,
    style: {
      fill: 0xf8fbff,
      fontFamily: "Segoe UI, Microsoft YaHei, sans-serif",
      fontSize,
      fontWeight: isPinned ? "700" : "600",
      lineJoin: "round",
      stroke: { color: 0x020617, width: 3, alpha: 0.75 },
    },
  });
  text.anchor.set(anchor.align === "left" ? 0 : 1, 0.5);
  text.x = anchor.x;
  text.y = anchor.y;
  const bounds = {
    x1: anchor.align === "left" ? text.x : text.x - text.width,
    y1: text.y - text.height / 2,
    x2: anchor.align === "left" ? text.x + text.width : text.x,
    y2: text.y + text.height / 2,
  };
  if (!isPinned && placedLabelBounds.some(item => boundsOverlap(bounds, item))) return;
  placedLabelBounds.push(bounds);
  const plate = new PIXI.Graphics();
  const padX = 7;
  const padY = 4;
  plate.roundRect(bounds.x1 - padX, bounds.y1 - padY, text.width + padX * 2, text.height + padY * 2, 7);
  plate.fill({ color: 0x020817, alpha: isPinned ? 0.74 : 0.46 });
  plate.stroke({ width: 1, color: isPinned ? 0x7dd3fc : 0x334155, alpha: isPinned ? 0.42 : 0.22 });
  labelLayer.addChild(plate);
  labelLayer.addChild(text);
}

function boundsOverlap(a, b) {
  return a.x1 < b.x2 && a.x2 > b.x1 && a.y1 < b.y2 && a.y2 > b.y1;
}
```

- [ ] **Step 3: Run syntax check**

Run:

```powershell
node --check src/tools/memory_graph_viewer_assets/viewer.js
```

Expected: PASS.

- [ ] **Step 4: Commit label improvements**

Run:

```powershell
git add src/tools/memory_graph_viewer_assets/viewer.js
git commit -m "fix: sharpen orbital galaxy labels"
```

Expected: commit succeeds.

## Task 5: Add System Hub Labels and Priority Legend

**Files:**
- Modify: `src/tools/memory_graph_viewer_assets/viewer.js`
- Modify: `src/tools/memory_graph_viewer_assets/index.html`
- Modify: `src/tools/memory_graph_viewer_assets/styles.css`

- [ ] **Step 1: Add a compact legend block to `index.html`**

After the `Galaxy Feel` section and before the `View` section, add:

```html
      <section>
        <h2>Priority Scale</h2>
        <div class="legend-list">
          <span><i class="legend-dot router"></i>Router</span>
          <span><i class="legend-dot persona"></i>Persona</span>
          <span><i class="legend-dot skill"></i>Skill</span>
          <span><i class="legend-dot harness"></i>Harness</span>
          <span><i class="legend-dot rule"></i>Rule</span>
          <span><i class="legend-dot preference"></i>Preference</span>
        </div>
      </section>
```

- [ ] **Step 2: Add legend styles to `styles.css`**

After `.compact-field span`, add:

```css
.legend-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  color: var(--muted);
  font-size: 12px;
}

.legend-list span {
  display: flex;
  align-items: center;
  gap: 7px;
  min-width: 0;
}

.legend-dot {
  width: 10px;
  height: 10px;
  flex: 0 0 10px;
  border-radius: 999px;
  box-shadow: 0 0 12px currentColor;
}

.legend-dot.router { color: #60a5fa; background: #60a5fa; }
.legend-dot.persona { color: #a78bfa; background: #a78bfa; }
.legend-dot.skill { color: #22d3ee; background: #22d3ee; }
.legend-dot.harness { color: #34d399; background: #34d399; }
.legend-dot.rule { color: #facc15; background: #facc15; }
.legend-dot.preference { color: #f472b6; background: #f472b6; }
```

- [ ] **Step 3: Draw system hub labels in `drawSystemGuides`**

Inside the `for (const system of visibleGraph.systems)` loop in `drawSystemGuides`, after the guide strokes, add:

```javascript
    const label = new PIXI.Text({
      text: system.label,
      resolution: 2,
      style: {
        fill: 0xbfd7ff,
        fontFamily: "Segoe UI, Microsoft YaHei, sans-serif",
        fontSize: 12,
        fontWeight: "700",
        stroke: { color: 0x020617, width: 3, alpha: 0.65 },
      },
    });
    label.anchor.set(0.5, 0.5);
    label.x = system.x;
    label.y = system.y - system.orbitRadius * 0.78;
    label.alpha = 0.68;
    orbitLayer.addChild(label);
```

- [ ] **Step 4: Run syntax check**

Run:

```powershell
node --check src/tools/memory_graph_viewer_assets/viewer.js
```

Expected: PASS.

- [ ] **Step 5: Commit legend and hub labels**

Run:

```powershell
git add src/tools/memory_graph_viewer_assets/viewer.js src/tools/memory_graph_viewer_assets/index.html src/tools/memory_graph_viewer_assets/styles.css
git commit -m "feat: add memory galaxy priority legend"
```

Expected: commit succeeds.

## Task 6: Export and Verify Viewer

**Files:**
- Verify: `src/tools/memory_graph_viewer_assets/memory-galaxy-core.js`
- Verify: `src/tools/memory_graph_viewer_assets/viewer.js`
- Runtime output: `C:\Users\Administrator\Documents\Codex\2026-06-16\new-chat-3\outputs\memory-graph-viewer`

- [ ] **Step 1: Run focused verification**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
node --check src/tools/memory_graph_viewer_assets/viewer.js
node --check src/tools/memory_graph_viewer_assets/viewer-3d.js
python -m pytest tests/test_memory_graph_viewer_export.py -v
```

Expected: all commands PASS.

- [ ] **Step 2: Re-export viewer**

Run:

```powershell
python src/tools/memory_graph_viewer_export.py --output "C:\Users\Administrator\Documents\Codex\2026-06-16\new-chat-3\outputs\memory-graph-viewer"
```

Expected: JSON metadata prints `node_count`, `edge_count`, `cache.default_root`, and `layout_seed`.

- [ ] **Step 3: HTTP smoke check**

Run:

```powershell
Invoke-WebRequest "http://127.0.0.1:8765/" -UseBasicParsing | Select-Object -ExpandProperty StatusCode
Invoke-WebRequest "http://127.0.0.1:8765/viewer.js" -UseBasicParsing | Select-Object -ExpandProperty StatusCode
Invoke-WebRequest "http://127.0.0.1:8765/styles.css" -UseBasicParsing | Select-Object -ExpandProperty StatusCode
```

Expected: each command prints `200`.

- [ ] **Step 4: Manual visual checklist**

Open:

```text
http://127.0.0.1:8765/
```

Expected:

- Router nodes appear near the galactic center.
- Rule, Persona, Skill, Harness, Preference, Project, Knowledge, Event, and Source appear as separate orbital systems.
- Persona, Skill, and Harness are visually identifiable as their own star systems.
- Priority is visible through diameter: Router stars are larger than Rule/Preference, and Skill/Harness stars are larger than ordinary memory nodes.
- Labels are crisp and do not stack over dense node groups.
- Intra-system relations are easy to follow; cross-system lines are visible only as quiet context until a node is selected or hovered.

- [ ] **Step 5: Save implementation memory**

After implementation and verification, save:

```text
Implemented Galactic-Orbital Memory Layout for Total Agent Memory: Router is the galactic core, Rule/Persona/Skill/Harness and other semantic systems are orbital star systems, node diameter reflects semantic priority, orbit guides clarify relationship structure, and label plates reduce text blur/overlap.
```

Use tags:

```text
memory-galaxy, galactic-orbital-layout, persona, skill, harness, graph-layout, label-clarity
```

## Self-Review

- Spec coverage: The plan covers the requested galaxy metaphor, central galactic core, Rule/Persona/Skill/Harness star systems, priority-based node diameter, clearer relationships, and label blur/overlap fixes.
- Placeholder scan: No placeholder tokens or unspecified implementation steps remain. Each code-changing step includes concrete code.
- Type consistency: The plan consistently uses `memorySystem`, `orbitalRole`, `systemCenter`, `buildGalacticOrbital2DLayout`, `priorityRadiusForNode`, and `labelAnchorForNode`.
- Scope check: This plan changes only the 2D galaxy layout and visual readability. It does not alter the exporter schema, 3D sphere, memory database, or Lumi.

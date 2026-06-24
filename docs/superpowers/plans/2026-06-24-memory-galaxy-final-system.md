# Memory Galaxy Final System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the current rough 2D memory graph into the confirmed multi-level memory galaxy: galaxy overview, solar-system focus, planet-satellite focus, and comet influence overlay.

**Architecture:** Keep the existing Python static exporter, `graph.json` format, shared detail panel helpers, interaction event helper, and 3D sphere page. Treat the current 2D `viewer.js` as replaceable: implement the final 2D experience through pure system/layout modules, a small view-state module, a PixiJS renderer, and a thin controller.

**Tech Stack:** Python exporter, static ES modules, PixiJS 8, Node.js smoke tests, pytest exporter tests.

---

## Source Of Truth

Confirmed design specs:

- `docs/superpowers/specs/2026-06-24-memory-galaxy-final-visual-summary.md`
- `docs/superpowers/specs/2026-06-24-memory-galaxy-galactic-layout.md`
- `docs/superpowers/specs/2026-06-24-memory-galaxy-solar-system-layout.md`
- `docs/superpowers/specs/2026-06-24-memory-galaxy-planet-satellite-layout.md`
- `docs/superpowers/specs/2026-06-24-memory-galaxy-comet-overlay-layout.md`

Confirmed preview assets:

- `C:\Users\Administrator\Documents\Codex\2026-06-16\new-chat-3\outputs\memory-galaxy-galactic-responsive-preview.png`
- `C:\Users\Administrator\Documents\Codex\2026-06-16\new-chat-3\outputs\memory-galaxy-solar-nested-preview.png`
- `C:\Users\Administrator\Documents\Codex\2026-06-16\new-chat-3\outputs\memory-galaxy-planet-satellite-preview.png`
- `C:\Users\Administrator\Documents\Codex\2026-06-16\new-chat-3\outputs\memory-galaxy-comet-overlay-preview.png`

## Non-Negotiable Product Requirements

- The default 2D view is a galaxy overview, not a force-directed graph.
- `Router` is the galactic core.
- `Rule`, `Persona`, `Skill`, `Harness`, `Preference`, `Project`, `Knowledge`, `Event`, and `Source` are separate star systems.
- Star systems sit on multiple Router-centered layers, not one orbit.
- Every visible star system in overview is a mini solar system, not a single dot.
- Clicking a star system enters a solar-system focus view.
- Clicking an important planet enters a planet-satellite focus view.
- Comets appear only in galaxy overview and show active cross-system influence.
- Nodes use small default diameters and expose a `Node diameter` control.
- Layout must allocate extra tracks when an orbit is crowded; no intentional node overlap.
- Relationship reading uses spatial orbit first, focused lines second, right panel third.
- The interaction layer remains extensible for later voice/API agent reactions.

## File Structure

- Create: `src/tools/memory_graph_viewer_assets/memory-galaxy-systems.js`
  - Classifies nodes into memory systems, hierarchy roles, priority radii, and colors.
- Create: `src/tools/memory_graph_viewer_assets/memory-galaxy-layouts.js`
  - Builds collision-aware pure layouts for galaxy, solar, planet-satellite, and comet overlay views.
- Create: `src/tools/memory_graph_viewer_assets/memory-galaxy-view-state.js`
  - Owns selected view, selected system, selected planet, selected node, relationship mode, node scale, and path endpoints.
- Create: `src/tools/memory_graph_viewer_assets/memory-galaxy-renderer.js`
  - Draws deep-space PixiJS layers: orbit guides, relations, 2.5D nodes, labels, comet trails, and influence halos.
- Replace: `src/tools/memory_graph_viewer_assets/viewer.js`
  - Thin 2D controller that wires data, filters, layout, renderer, controls, and interactions.
- Modify: `src/tools/memory_graph_viewer_assets/index.html`
  - Add final controls for relationship mode, node diameter, and back navigation.
- Modify: `src/tools/memory_graph_viewer_assets/styles.css`
  - Add compact dark-space control styling and view badges.
- Modify: `src/tools/memory_graph_viewer_export.py`
  - Copy new ES modules during static export.
- Modify: `tests/js/memory_galaxy_smoke.test.mjs`
  - Add pure module smoke tests.
- Modify: `tests/test_memory_graph_viewer_export.py`
  - Assert new assets are exported.

## Implementation Policy

- Runtime code changes must stay inside `C:\Users\Administrator\total-agent-memory`.
- Do not touch `F:\Users\Administrator\Desktop\Jarvis\tmp_lumi_os_research`.
- Do not change the memory database schema or data.
- Do not change `viewer-3d.html` or `viewer-3d.js` in this plan.
- Do not try to salvage the old 2D controller if replacement is cleaner.
- Preserve existing `viewer-shared.js` detail rendering and `memory-galaxy-events.js` interaction events.
- Keep every layout function pure: no DOM, no PixiJS, no mutation of input graph nodes.
- Each implementation task ends with a focused test and a commit.

## Task 1: Freeze Specs And Reset Wrong Runtime Direction

**Files:**
- Add: all spec files listed in "Source Of Truth"
- Modify: `docs/superpowers/plans/2026-06-24-memory-galaxy-final-system.md`

- [ ] **Step 1: Verify that only docs/specs are pending**

Run:

```powershell
git status --short
```

Expected:

```text
?? docs/superpowers/plans/2026-06-24-memory-galaxy-final-system.md
?? docs/superpowers/specs/2026-06-24-memory-galaxy-comet-overlay-layout.md
?? docs/superpowers/specs/2026-06-24-memory-galaxy-final-visual-summary.md
?? docs/superpowers/specs/2026-06-24-memory-galaxy-galactic-layout.md
?? docs/superpowers/specs/2026-06-24-memory-galaxy-planet-satellite-layout.md
?? docs/superpowers/specs/2026-06-24-memory-galaxy-solar-system-layout.md
```

`evals/results/` may also appear and must remain untracked.

- [ ] **Step 2: Remove obsolete narrow plan if present**

Run:

```powershell
if (Test-Path docs\superpowers\plans\2026-06-24-memory-galaxy-2d-final-visual.md) {
  Remove-Item docs\superpowers\plans\2026-06-24-memory-galaxy-2d-final-visual.md
}
```

Expected: `git status --short` does not show `2026-06-24-memory-galaxy-2d-final-visual.md`.

- [ ] **Step 3: Commit final specs and plan**

Run:

```powershell
git add docs/superpowers/specs/2026-06-24-memory-galaxy-final-visual-summary.md `
  docs/superpowers/specs/2026-06-24-memory-galaxy-galactic-layout.md `
  docs/superpowers/specs/2026-06-24-memory-galaxy-solar-system-layout.md `
  docs/superpowers/specs/2026-06-24-memory-galaxy-planet-satellite-layout.md `
  docs/superpowers/specs/2026-06-24-memory-galaxy-comet-overlay-layout.md `
  docs/superpowers/plans/2026-06-24-memory-galaxy-final-system.md
git commit -m "docs: specify final memory galaxy system"
```

Expected: commit succeeds. `evals/results/` remains untracked.

## Task 2: Add Memory System Classifier

**Files:**
- Create: `src/tools/memory_graph_viewer_assets/memory-galaxy-systems.js`
- Modify: `tests/js/memory_galaxy_smoke.test.mjs`

- [ ] **Step 1: Add failing tests for the classifier**

In `tests/js/memory_galaxy_smoke.test.mjs`, add this loader after the existing helper loaders:

```javascript
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
```

Append these assertions near the existing orbital fixture tests:

```javascript
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
```

- [ ] **Step 2: Run the smoke test and confirm failure**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: failure because `memory-galaxy-systems.js` does not exist.

- [ ] **Step 3: Create `memory-galaxy-systems.js`**

Create the file with these exported APIs and exact behavior:

```javascript
export const systemOrder = [
  "router",
  "rule",
  "persona",
  "skill",
  "harness",
  "preference",
  "project",
  "knowledge",
  "event",
  "source",
  "archive",
];

export const systemColors = {
  router: "#60a5fa",
  rule: "#facc15",
  persona: "#a78bfa",
  skill: "#22d3ee",
  harness: "#34d399",
  preference: "#f472b6",
  project: "#2dd4bf",
  knowledge: "#7dd3fc",
  event: "#38bdf8",
  source: "#94a3b8",
  archive: "#64748b",
};

export function systemColor(system) {
  return systemColors[system] || systemColors.knowledge;
}

export function systemLayerForKey(system) {
  if (["rule", "persona"].includes(system)) return "control";
  if (["skill", "harness", "preference"].includes(system)) return "execution";
  if (["project", "knowledge"].includes(system)) return "context";
  if (["event", "source"].includes(system)) return "evidence";
  if (system === "router") return "core";
  return "archive";
}

export function memorySystemForData(data = {}) {
  const text = [
    data.id,
    data.label,
    data.name,
    data.type,
    data.content,
    data.source,
    data.project,
    ...(Array.isArray(data.knowledge) ? data.knowledge : []).map(item => `${item.type || ""} ${item.project || ""} ${item.summary || ""}`),
  ].join(" ").toLowerCase();

  if (/\b(router|routing|route|dispatch|orchestrat)/.test(text)) return "router";
  if (data.type === "rule" || /\b(rule|policy|must|never|required|guardrail)\b/.test(text)) return "rule";
  if (/\b(persona|personality|identity|tone|style|voice|character)\b/.test(text)) return "persona";
  if (data.type === "capability" || /\b(skill|capability|trigger|workflow|procedure)\b/.test(text)) return "skill";
  if (/\b(harness|eval|evaluation|pytest|test runner|smoke test|verification|playwright|benchmark)\b/.test(text)) return "harness";
  if (/\b(preference|prefers|user wants|style preference|interaction preference)\b/.test(text)) return "preference";
  if (data.type === "project") return "project";
  if (["event", "episode", "session", "observation"].includes(data.type) || data.galaxy_layer === "episode") return "event";
  if (["source", "citation", "provenance"].includes(data.type) || /\b(source|provenance|evidence|citation|origin)\b/.test(text) || data.galaxy_layer === "external") return "source";
  return "knowledge";
}

export function orbitRoleForData(data = {}) {
  if (data.type === "event" || data.galaxy_layer === "episode" || data.galaxy_layer === "external") return "evidence";
  if (Number(data.importance || 0) >= 0.9 || Number(data.mention_count || 0) >= 10) return "planet";
  return "moon";
}

export function priorityRadiusForData(data = {}, options = {}) {
  const system = memorySystemForData(data);
  const baseDiameter = {
    router: 54,
    persona: 42,
    skill: 40,
    harness: 36,
    rule: 34,
    preference: 28,
    project: 26,
    knowledge: 20,
    event: 14,
    source: 10,
    archive: 8,
  }[system] || 20;
  const diameter = baseDiameter
    + Number(data.importance || 0) * 2.5
    + Number(data.activity || 0) * 3
    + Math.log1p(Number(data.mention_count || 0)) * 1.2;
  const scale = Math.max(0.42, Math.min(0.7, Number(options.scale || 0.48)));
  return Math.max(3, Math.min(28, (diameter / 2) * scale));
}
```

- [ ] **Step 4: Run smoke test**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: pass.

- [ ] **Step 5: Commit classifier**

Run:

```powershell
git add src/tools/memory_graph_viewer_assets/memory-galaxy-systems.js tests/js/memory_galaxy_smoke.test.mjs
git commit -m "feat: classify memory galaxy systems"
```

Expected: commit succeeds.

## Task 3: Add Collision-Aware Pure Layout Builders

**Files:**
- Create: `src/tools/memory_graph_viewer_assets/memory-galaxy-layouts.js`
- Modify: `tests/js/memory_galaxy_smoke.test.mjs`

- [ ] **Step 1: Add failing layout tests**

Add a VM loader for `memory-galaxy-layouts.js`. Because the module imports `memory-galaxy-systems.js`, strip the import and inject classifier functions in the VM context:

```javascript
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
```

Append assertions:

```javascript
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
```

- [ ] **Step 2: Run smoke test and confirm failure**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: failure because `memory-galaxy-layouts.js` does not exist.

- [ ] **Step 3: Create `memory-galaxy-layouts.js`**

Create a pure module with these functions:

```javascript
import {
  memorySystemForData,
  orbitRoleForData,
  priorityRadiusForData,
  systemColor,
  systemLayerForKey,
} from "./memory-galaxy-systems.js";

export function buildGalaxyOverviewLayout(galaxy, options = {}) {}
export function buildSolarSystemLayout(galaxy, systemKey, options = {}) {}
export function buildPlanetSatelliteLayout(galaxy, systemKey, planetId, options = {}) {}
export function buildCometOverlayLayout(galaxyLayout, comets = []) {}
```

Fill those functions with this deterministic layout contract:

- Clone every returned node; never mutate `galaxy.nodes`.
- `buildGalaxyOverviewLayout` groups nodes by `memorySystemForData(node.raw || node)`.
- It creates a synthetic router core if no router node exists. Synthetic id: `system:router`.
- It creates system descriptors with `{ key, label, layer, x, y, radius, miniOrbits }`.
- Galactic layer radii:
  - `control`: `230`
  - `execution`: `360`
  - `context`: `500`
  - `evidence`: `640`
  - `archive`: `760`
- Systems in the same layer use evenly spaced angular slots. Offset each layer by `Math.PI / (layerIndex + 4)` so layers do not align into a single spoke.
- Each non-router system gets mini orbit radii `[34, 58, 84]` multiplied by `Math.max(0.82, nodeScale / 0.48)`.
- In overview, each system star sits at its system center. Its strongest local planet/moon/evidence nodes are placed on those mini orbits.
- When a mini orbit has more bodies than can fit with `minSpacing = maxNodeDiameter + 8`, split the bodies into a second or third same-type track by adding `26` to the local orbit radius per track.
- `buildSolarSystemLayout` filters to nodes whose inferred system matches `systemKey`, plus direct one-hop neighbors of those nodes. It returns a central synthetic star id `system:${systemKey}` and orbit descriptors for `category`, `planet`, `moon`, and `evidence`.
- Solar orbit base radii are `110`, `210`, `330`, and `470`. Dense roles split into additional tracks by adding `70`.
- `buildPlanetSatelliteLayout` centers the selected planet, finds one-hop and two-hop local neighbors, and assigns them to `direct-moon`, `derived-moon`, `evidence`, and `external` orbits.
- Planet orbit base radii are `120`, `230`, `340`, and `450`. Dense roles split into additional tracks by adding `64`.
- Every layout returns `{ view, nodes, links, systems, orbits, bounds }` where missing collections are empty arrays.
- Bounds include node radius and orbit radius with at least `80` units of padding.
- Each returned node includes `id`, `label`, `raw`, `memorySystem`, `orbitRole`, `orbitalRole`, `renderRadius`, `color`, `x`, `y`, `homeX`, `homeY`, and `labelAnchor`.
- `buildCometOverlayLayout` accepts the galaxy overview layout and 1-3 comet payloads. It maps each influenced system to the matching system descriptor and returns `{ comets }`, where each comet has `id`, `label`, `head`, `tail`, `trajectory`, and `influences`.

- [ ] **Step 4: Run smoke test**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: pass.

- [ ] **Step 5: Commit layout builders**

Run:

```powershell
git add src/tools/memory_graph_viewer_assets/memory-galaxy-layouts.js tests/js/memory_galaxy_smoke.test.mjs
git commit -m "feat: build final memory galaxy layouts"
```

Expected: commit succeeds.

## Task 4: Add View State And Renderer

**Files:**
- Create: `src/tools/memory_graph_viewer_assets/memory-galaxy-view-state.js`
- Create: `src/tools/memory_graph_viewer_assets/memory-galaxy-renderer.js`

- [ ] **Step 1: Create `memory-galaxy-view-state.js`**

Create:

```javascript
export function createGalaxyViewState() {
  return {
    view: "galaxy",
    selectedSystem: null,
    selectedPlanet: null,
    selectedNodeId: null,
    hoveredNodeId: null,
    relationshipMode: "structure",
    nodeScale: 0.48,
    pathStartId: null,
    pathEndId: null,
    viewStack: [],
  };
}

export function enterGalaxyView(state) {
  state.view = "galaxy";
  state.selectedSystem = null;
  state.selectedPlanet = null;
  state.viewStack = [];
  return state;
}

export function enterSolarView(state, systemKey) {
  if (state.view !== "solar" || state.selectedSystem !== systemKey) {
    state.viewStack.push({ view: state.view, selectedSystem: state.selectedSystem, selectedPlanet: state.selectedPlanet });
  }
  state.view = "solar";
  state.selectedSystem = systemKey;
  state.selectedPlanet = null;
  return state;
}

export function enterPlanetView(state, planetId) {
  state.viewStack.push({ view: state.view, selectedSystem: state.selectedSystem, selectedPlanet: state.selectedPlanet });
  state.view = "planet";
  state.selectedPlanet = planetId;
  return state;
}

export function goBackView(state) {
  const previous = state.viewStack.pop();
  if (!previous) return enterGalaxyView(state);
  state.view = previous.view;
  state.selectedSystem = previous.selectedSystem;
  state.selectedPlanet = previous.selectedPlanet;
  return state;
}
```

- [ ] **Step 2: Create `memory-galaxy-renderer.js`**

Create a renderer module exporting `createMemoryGalaxyRenderer`. The module must:

- Accept `{ PIXI, app, stage }`.
- Create containers in this order: `backgroundLayer`, `orbitLayer`, `cometLayer`, `linkLayer`, `nodeLayer`, `labelLayer`.
- Expose `draw(layout, state, handlers)`.
- Expose `fitToBounds(bounds)`.
- Draw orbit guides as ellipses with low-alpha blue strokes.
- Draw relation lines using the active relationship mode:
  - `structure`: system/parent links only, low alpha.
  - `focus`: selected or hovered one-hop links bright; all others faint.
  - `path`: links with `isPath === true` bright; all others quiet.
- Draw nodes as 2.5D bodies: outer glow, filled body, small white highlight, optional selection ring.
- Draw labels with high-contrast plates and collision rejection.
- Draw comet heads, tails, influence lines, and influence halos when `layout.comets` exists.
- Attach pointer handlers through `handlers.onNodePointerDown`, `handlers.onNodePointerOver`, `handlers.onNodePointerOut`, and `handlers.onSystemClick`.

The node drawing helper inside the module must use this body style:

```javascript
function drawNodeBody(graphics, node, state) {
  const selected = node.id === state.selectedNodeId;
  const hovered = node.id === state.hoveredNodeId;
  const color = parseColor(node.color || "#94a3b8");
  const radius = Number(node.renderRadius || 4);
  graphics.circle(0, 0, radius + 10);
  graphics.fill({ color, alpha: selected || hovered ? 0.22 : 0.12 });
  graphics.circle(0, 0, radius);
  graphics.fill({ color, alpha: 0.92 });
  graphics.circle(-radius * 0.28, -radius * 0.34, Math.max(1.2, radius * 0.22));
  graphics.fill({ color: 0xffffff, alpha: 0.36 });
  if (selected || hovered) {
    graphics.circle(0, 0, radius + 6);
    graphics.stroke({ width: selected ? 2.2 : 1.4, color: selected ? 0xfacc15 : 0x7dd3fc, alpha: 0.9 });
  }
}
```

- [ ] **Step 3: Syntax-check new modules**

Run:

```powershell
node --check src/tools/memory_graph_viewer_assets/memory-galaxy-view-state.js
node --check src/tools/memory_graph_viewer_assets/memory-galaxy-renderer.js
```

Expected: both pass.

- [ ] **Step 4: Commit view state and renderer**

Run:

```powershell
git add src/tools/memory_graph_viewer_assets/memory-galaxy-view-state.js `
  src/tools/memory_graph_viewer_assets/memory-galaxy-renderer.js
git commit -m "feat: add memory galaxy renderer"
```

Expected: commit succeeds.

## Task 5: Replace 2D Viewer Controller

**Files:**
- Replace: `src/tools/memory_graph_viewer_assets/viewer.js`

- [ ] **Step 1: Replace imports**

The new `viewer.js` must import exactly these project modules:

```javascript
import { convertGraphToGalaxy, filterGalaxy } from "./memory-galaxy-core.js";
import { createInteractionLog, createMemoryGalaxyEvent, suggestAgentPrompt } from "./memory-galaxy-events.js";
import { buildCometOverlayLayout, buildGalaxyOverviewLayout, buildPlanetSatelliteLayout, buildSolarSystemLayout } from "./memory-galaxy-layouts.js";
import { createMemoryGalaxyRenderer } from "./memory-galaxy-renderer.js";
import { createGalaxyViewState, enterGalaxyView, enterPlanetView, enterSolarView, goBackView } from "./memory-galaxy-view-state.js";
import { escapeHtml, formatNodeDetails, renderPromptText, timelineCutoffFromPercent } from "./viewer-shared.js";
```

- [ ] **Step 2: Implement controller state**

Controller state must include:

```javascript
const viewName = "2d-memory-galaxy";
const focusLimit = 900;
const interactionLog = createInteractionLog();
const state = createGalaxyViewState();

let app;
let renderer;
let originalGraph = { nodes: [], links: [], metadata: {} };
let filteredGraph = { nodes: [], links: [], metadata: {} };
let activeTypes = new Set();
let activeLayers = new Set(["core", "active", "knowledge", "episode", "external"]);
let renderTimer = null;
```

- [ ] **Step 3: Implement data flow**

The controller must:

- Fetch `graph.json`.
- Convert it with `convertGraphToGalaxy`.
- Build type/layer filter controls.
- Create PixiJS app in `#galaxy2d`.
- Create `renderer = createMemoryGalaxyRenderer({ PIXI: window.PIXI, app, stage: app.stage })`.
- Recompute `filteredGraph` through `filterGalaxy`.
- Build the active layout with:
  - `buildGalaxyOverviewLayout(filteredGraph, { nodeScale: state.nodeScale, width: app.screen.width, height: app.screen.height })`
  - `buildSolarSystemLayout(filteredGraph, state.selectedSystem, { nodeScale: state.nodeScale, width: app.screen.width, height: app.screen.height })`
  - `buildPlanetSatelliteLayout(filteredGraph, state.selectedSystem, state.selectedPlanet, { nodeScale: state.nodeScale, width: app.screen.width, height: app.screen.height })`
- Add comet overlay only when `state.view === "galaxy"`.
- Call `renderer.draw(layout, state, handlers)` and `renderer.fitToBounds(layout.bounds)`.

- [ ] **Step 4: Implement interactions**

The controller must wire:

- System click in galaxy view: `enterSolarView(state, system.key)`.
- Planet click in solar view: `enterPlanetView(state, node.id)` only when `node.orbitRole === "planet"` or `node.orbitalRole` contains `planet`.
- Back button: `goBackView(state)`.
- Fit button: `renderer.fitToBounds(currentLayout.bounds)`.
- Node diameter input: update `state.nodeScale`, update visible label, redraw.
- Relationship mode select: update `state.relationshipMode`, redraw.
- Hover: update `state.hoveredNodeId`, redraw with focused relation lines.
- Node click: update details panel using `formatNodeDetails(node.raw)`, emit `node:selected`.
- Node drag events may stay renderer-local in this task; they must still emit `node:drag-started` and `node:drag-ended` when implemented by the renderer.

- [ ] **Step 5: Preserve filters and details**

The controller must keep existing behavior for:

- Search input.
- Type filters.
- Layer filters.
- Minimum edge weight.
- Timeline slider.
- Stats text.
- Agent prompt text through `suggestAgentPrompt` and `renderPromptText`.

- [ ] **Step 6: Syntax-check viewer**

Run:

```powershell
node --check src/tools/memory_graph_viewer_assets/viewer.js
```

Expected: pass.

- [ ] **Step 7: Commit controller replacement**

Run:

```powershell
git add src/tools/memory_graph_viewer_assets/viewer.js
git commit -m "feat: replace 2d memory galaxy controller"
```

Expected: commit succeeds.

## Task 6: Add Final Controls And Export Wiring

**Files:**
- Modify: `src/tools/memory_graph_viewer_assets/index.html`
- Modify: `src/tools/memory_graph_viewer_assets/styles.css`
- Modify: `src/tools/memory_graph_viewer_export.py`
- Modify: `tests/test_memory_graph_viewer_export.py`

- [ ] **Step 1: Update `index.html` controls**

Inside the `Galaxy Feel` section, replace the old spring/neighborhood controls with:

```html
<label class="field compact-field">
  Node diameter
  <input id="nodeScale" type="range" min="0.42" max="0.70" step="0.01" value="0.48">
  <span id="nodeScaleValue">0.48</span>
</label>
<label class="field compact-field">
  Relation mode
  <select id="relationshipMode">
    <option value="structure" selected>Structure</option>
    <option value="focus">Focus</option>
    <option value="path">Path</option>
  </select>
</label>
<label class="field compact-field">
  Labels
  <select id="labelMode">
    <option value="minimal">Minimal</option>
    <option value="normal" selected>Normal</option>
    <option value="dense">Dense</option>
  </select>
</label>
```

Inside the `View` section, use:

```html
<div class="buttons">
  <button id="backView" type="button">Back</button>
  <button id="fit" type="button">Fit</button>
  <button id="clearFocus" type="button">Galaxy</button>
  <button id="focusView" type="button">Refresh</button>
</div>
```

- [ ] **Step 2: Update `styles.css`**

Add styling for:

```css
.view-badge {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  margin-top: 10px;
  padding: 3px 8px;
  border: 1px solid rgba(125, 211, 252, 0.35);
  border-radius: 6px;
  background: rgba(14, 165, 233, 0.10);
  color: #075985;
  font-size: 12px;
  font-weight: 700;
}
```

Keep the deep-space canvas background already present.

- [ ] **Step 3: Copy new assets in exporter**

In `copy_assets`, add:

```python
"memory-galaxy-systems.js",
"memory-galaxy-layouts.js",
"memory-galaxy-renderer.js",
"memory-galaxy-view-state.js",
```

- [ ] **Step 4: Assert exported assets**

In `tests/test_memory_graph_viewer_export.py`, add assertions that the output directory contains:

```python
"memory-galaxy-systems.js",
"memory-galaxy-layouts.js",
"memory-galaxy-renderer.js",
"memory-galaxy-view-state.js",
```

- [ ] **Step 5: Run tests**

Run:

```powershell
python -m pytest tests/test_memory_graph_viewer_export.py -v
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: both pass.

- [ ] **Step 6: Commit controls and export wiring**

Run:

```powershell
git add src/tools/memory_graph_viewer_assets/index.html `
  src/tools/memory_graph_viewer_assets/styles.css `
  src/tools/memory_graph_viewer_export.py `
  tests/test_memory_graph_viewer_export.py
git commit -m "feat: wire final memory galaxy viewer assets"
```

Expected: commit succeeds.

## Task 7: Export And Verify The Viewer

**Files:**
- Runtime output: `C:\Users\Administrator\Documents\Codex\2026-06-16\new-chat-3\outputs\memory-graph-viewer`

- [ ] **Step 1: Run focused checks**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
node --check src/tools/memory_graph_viewer_assets/viewer.js
node --check src/tools/memory_graph_viewer_assets/viewer-3d.js
python -m pytest tests/test_memory_graph_viewer_export.py -v
```

Expected: all pass.

- [ ] **Step 2: Export viewer**

Run:

```powershell
python src/tools/memory_graph_viewer_export.py --output "C:\Users\Administrator\Documents\Codex\2026-06-16\new-chat-3\outputs\memory-graph-viewer"
```

Expected: export prints metadata JSON and writes `graph.json` plus all viewer assets.

- [ ] **Step 3: Start or verify local server**

If no server is running on port `8765`, run from the output directory:

```powershell
python -m http.server 8765
```

If a server is already running, keep it and continue.

- [ ] **Step 4: HTTP smoke check**

Run:

```powershell
Invoke-WebRequest "http://127.0.0.1:8765/" -UseBasicParsing | Select-Object -ExpandProperty StatusCode
Invoke-WebRequest "http://127.0.0.1:8765/viewer.js" -UseBasicParsing | Select-Object -ExpandProperty StatusCode
Invoke-WebRequest "http://127.0.0.1:8765/memory-galaxy-layouts.js" -UseBasicParsing | Select-Object -ExpandProperty StatusCode
```

Expected: each command returns `200`.

- [ ] **Step 5: Manual visual checklist**

Open:

```text
http://127.0.0.1:8765/
```

Expected:

- Default view is the whole galaxy.
- Star systems are on multiple galactic layers.
- Star systems do not all sit on one ring.
- Each visible star system looks like a mini solar system.
- Node diameters are small by default and adjustable.
- Orbit guides are visible.
- Clicking a star system centers/focuses that solar system.
- Clicking a planet opens the planet-satellite view.
- Back returns one level at a time.
- Structure mode keeps edges quiet.
- Focus mode highlights selected or hovered relations.
- Comet overlay appears only in galaxy overview.
- Labels are readable and do not cover dense node clusters.

- [ ] **Step 6: Commit final verification note if docs changed**

If manual verification reveals a necessary spec clarification, update the relevant spec and commit:

```powershell
git add docs/superpowers/specs
git commit -m "docs: clarify memory galaxy verification"
```

Expected: no code commit is created for manual verification unless a file actually changed.

## Self-Review

- Spec coverage: The plan covers galaxy overview, solar-system focus, planet-satellite focus, comet overlay, small adjustable node diameter, multi-orbit non-overlap, relationship modes, screen fitting, and future interaction extensibility.
- Deferred-work scan: The plan avoids deferred-work markers and unnamed future work. Algorithms and file responsibilities are concrete.
- Type consistency: The plan consistently uses `memorySystemForData`, `orbitRoleForData`, `priorityRadiusForData`, `systemColor`, `systemLayerForKey`, `buildGalaxyOverviewLayout`, `buildSolarSystemLayout`, `buildPlanetSatelliteLayout`, `buildCometOverlayLayout`, `createGalaxyViewState`, and `createMemoryGalaxyRenderer`.
- Scope: The plan explicitly allows replacing the current 2D viewer, preserves exporter/3D/shared detail behavior, and avoids Lumi.

# Galaxy Canvas Visual Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade only the center Memory Galaxy canvas so it reads closer to the preview image with richer starfield texture, luminous spiral systems, glow arcs, and more legible system labels.

**Architecture:** Keep PixiJS 8 and the existing graph data, layout, pointer, drag, zoom, minimap, and selection behavior. Add renderer-local drawing helpers for background stars, nebula wisps, system spiral disks, system-level arcs, and multi-line pinned labels; touch the stage CSS only for middle-canvas texture and leave left/right sidebars unchanged.

**Tech Stack:** Static CSS, ES modules, PixiJS 8 Graphics/Text, existing Node smoke tests, existing Playwright regression test.

---

## Design Direction

Use the Retro-Futuristic anchor because the product is a navigable memory galaxy: pitch-black surface, cyan/blue/violet glow, and explicit texture are allowed and visible. The differentiator is a layered "deep-space cartography" canvas: CSS provides far nebula and distant stars; PixiJS adds near star dust, spiral system disks, and luminous routed arcs that move with the graph.

## File Structure

- Modify: `src/tools/memory_graph_viewer_assets/styles.css`
  - Only update `.galaxy-canvas` / `.graph-3d` background and pseudo-element texture.
  - Do not change `.sidebar`, `.details`, `.inspector`, `.panel-section`, or any left/right panel rules.
- Modify: `src/tools/memory_graph_viewer_assets/memory-galaxy-renderer.js`
  - Add a background Pixi layer inside the canvas root.
  - Add deterministic starfield and nebula helpers.
  - Replace simple system bodies with denser spiral disk rendering.
  - Add overview-level system connection arcs independent of selected node links.
  - Upgrade pinned system labels to title/type/count blocks with leader lines.
- Modify: `tests/js/memory_galaxy_smoke.test.mjs`
  - Export and assert pure renderer helpers for deterministic starfield and label line formatting.
- Run: `node --check src/tools/memory_graph_viewer_assets/memory-galaxy-renderer.js`
- Run: `node tests/js/memory_galaxy_smoke.test.mjs`
- Run if local server is available: `node tests/js/memory_galaxy_browser_regression.test.mjs`

## Non-Goals

- Do not alter left sidebar DOM or CSS.
- Do not alter right inspector DOM or CSS.
- Do not fabricate preview names or fake counts.
- Do not change graph export format, system classification, layout math, selection, minimap, or event behavior.

## Task 1: Add Renderer Visual Contracts

**Files:**
- Modify: `src/tools/memory_graph_viewer_assets/memory-galaxy-renderer.js`
- Modify: `tests/js/memory_galaxy_smoke.test.mjs`

- [ ] **Step 1: Add pure helper exports**

Add these helpers near the bottom of `memory-galaxy-renderer.js`:

```javascript
export function buildDeterministicStarfield(seed = "memory-galaxy", count = 180, bounds = { minX: -900, maxX: 900, minY: -560, maxY: 560 }) {
  const points = [];
  let state = seededNumber(seed);
  for (let index = 0; index < count; index += 1) {
    state = lcg(state);
    const x = bounds.minX + (state / 0xffffffff) * (bounds.maxX - bounds.minX);
    state = lcg(state);
    const y = bounds.minY + (state / 0xffffffff) * (bounds.maxY - bounds.minY);
    state = lcg(state);
    const radius = 0.7 + (state / 0xffffffff) * 2.4;
    state = lcg(state);
    const alpha = 0.18 + (state / 0xffffffff) * 0.72;
    points.push({ x, y, radius, alpha, warm: index % 17 === 0, blue: index % 5 === 0 });
  }
  return points;
}

export function systemLabelLines(node) {
  const name = String(node.label || "Memory System").toUpperCase();
  const type = systemTypeLabel(node.memorySystem || node.systemKey || "memory");
  const count = Number(node.raw?.memberCount ?? node.memberCount ?? 0);
  return [name, type, count > 0 ? `${count.toLocaleString()} memories` : ""].filter(Boolean);
}
```

- [ ] **Step 2: Add smoke assertions**

Extend the renderer helper export block in `tests/js/memory_galaxy_smoke.test.mjs`:

```javascript
exports.buildDeterministicStarfield = buildDeterministicStarfield;
exports.systemLabelLines = systemLabelLines;
```

Add assertions:

```javascript
const starsA = buildDeterministicStarfield("fixture", 4, { minX: 0, maxX: 10, minY: 0, maxY: 10 });
const starsB = buildDeterministicStarfield("fixture", 4, { minX: 0, maxX: 10, minY: 0, maxY: 10 });
assert.deepEqual(starsA, starsB);
assert.equal(starsA.length, 4);
assert.ok(starsA.every(star => star.x >= 0 && star.x <= 10 && star.y >= 0 && star.y <= 10));
assert.deepEqual(systemLabelLines({ label: "Router Core", memorySystem: "router", raw: { memberCount: 12847 } }), ["ROUTER CORE", "Route System", "12,847 memories"]);
```

- [ ] **Step 3: Verify failing or passing contract**

Run: `node tests/js/memory_galaxy_smoke.test.mjs`

Expected before implementation: failure if helpers are not exported. Expected after implementation: pass.

## Task 2: Add Layered Canvas Background

**Files:**
- Modify: `src/tools/memory_graph_viewer_assets/styles.css`
- Modify: `src/tools/memory_graph_viewer_assets/memory-galaxy-renderer.js`

- [ ] **Step 1: Update only center canvas CSS**

Replace the `.galaxy-canvas, .graph-3d` background and pseudo-element texture with deeper nebula/star layers. Do not modify sidebar or inspector selectors.

- [ ] **Step 2: Add Pixi background layer**

Create `backgroundLayer` before `orbitLayer`, add it to `root`, and clear it in `draw()`. Draw deterministic stars and faint nebula strokes before orbits.

- [ ] **Step 3: Verify syntax and smoke tests**

Run:

```bash
node --check src/tools/memory_graph_viewer_assets/memory-galaxy-renderer.js
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: both pass.

## Task 3: Upgrade System Disks, Arcs, And Labels

**Files:**
- Modify: `src/tools/memory_graph_viewer_assets/memory-galaxy-renderer.js`

- [ ] **Step 1: Add overview system arcs**

When `layout.view === "galaxy"`, draw curved arcs from the router system to visible systems before selected links. Use real `layout.systems` positions and colors.

- [ ] **Step 2: Replace system body with spiral disk**

Enhance `drawSystemBody()` with layered glows, spiral particle arms, dense star dust, and multiple orbit strokes. Keep all hit targets and pointer handling unchanged.

- [ ] **Step 3: Upgrade pinned labels**

For system-like nodes, render a multi-line label block using `systemLabelLines(node)`, with uppercase title, colored type line, optional count line, and a leader line. Non-system labels keep the existing compact text behavior.

- [ ] **Step 4: Verify**

Run:

```bash
node --check src/tools/memory_graph_viewer_assets/memory-galaxy-renderer.js
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: both pass.

## Task 4: Browser Regression And Visual Safety Check

**Files:**
- No code changes unless verification reveals a regression.

- [ ] **Step 1: Run browser regression against the existing local viewer URL**

Run:

```bash
node tests/js/memory_galaxy_browser_regression.test.mjs
```

Expected: pass if the local static server is running at `http://127.0.0.1:8765/`.

- [ ] **Step 2: If no server is running, start one without changing app files**

Run from `src/tools/memory_graph_viewer_assets`:

```bash
python -m http.server 8765
```

Then rerun the browser regression.

- [ ] **Step 3: Confirm scope**

Run:

```bash
git diff -- src/tools/memory_graph_viewer_assets/styles.css src/tools/memory_graph_viewer_assets/memory-galaxy-renderer.js tests/js/memory_galaxy_smoke.test.mjs
```

Expected: no sidebar/inspector structure changes and no changes outside the planned files except this plan document.


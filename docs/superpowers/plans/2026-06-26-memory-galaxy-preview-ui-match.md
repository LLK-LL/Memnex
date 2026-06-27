# Memory Galaxy Preview UI Match Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restyle the existing Memory Galaxy viewer so its layout, visual hierarchy, and HUD presentation match the supplied preview image while preserving current filtering, selection, navigation, prompt, relation, and graph-rendering logic.

**Architecture:** Keep PixiJS 8 as the GPU-accelerated renderer already used by the current viewer. Treat this as a presentation-layer redesign: update `index.html`, `styles.css`, and Pixi drawing helpers in `memory-galaxy-renderer.js`, with only thin DOM rendering changes in `viewer.js` where the preview requires new panel structure. Do not change graph schema, system classification, layout math, event names, or existing selection/filter data flow unless a visual target cannot be reached without a compatible additive wrapper.

**Tech Stack:** Static HTML/CSS, ES modules, PixiJS 8, existing Node.js smoke tests, existing Playwright browser regression tests.

---

## Preview Image Breakdown

### 1. Overall Composition

- The page is a full-viewport dark space cockpit with three fixed columns.
- Left sidebar width is approximately `292px`; right inspector width is approximately `320px`; center canvas consumes the remaining width.
- Left and right panels are translucent black-blue HUD surfaces with 1px cool borders.
- Center stage is edge-to-edge starfield, not a boxed card.
- There are no floating section cards around the main canvas except HUD overlays and the bottom toolbar/minimap.
- Typography is compact, uppercase for section labels, mixed case for control labels and data values.
- Dominant palette is near-black `#020712`, panel black `rgba(5, 12, 22, 0.88)`, blue border `rgba(93, 130, 180, 0.24)`, text white `#f4f7fb`, muted slate `#7f8da7`, accent blue `#4ea1ff`, green `#55d6a0`, gold `#f7c65a`, purple `#b36cff`, cyan `#55dce0`.

### 2. Left Sidebar

- Header contains a compass-like circular brand icon, title `MEMORY GALAXY`, green `GPU` badge, and subtitle `Real-time Memory Graph Visualization`.
- Divider below header is subtle and full width.
- `VIEW CONTROLS` section includes:
  - `Camera Mode` select set to `Orbit`.
  - `Speed` row showing numeric value such as `1.25x` and a blue range slider.
  - Two compact icon-plus-label toggles: `Auto Rotate`, `Motion Trails`.
- `FILTERS` section includes:
  - Search input with placeholder `Search nodes...` and search icon.
  - `Node Types` select set to `All`.
  - Checkbox list with right-aligned counts.
  - `Edge Types` select set to `All`.
  - Checkbox list for relations.
  - `Metrics` select set to `All`.
  - `Relevance` and `Strength` range rows with `0.00` to `1.00` labels.
  - `Recency` row with `Any Time`.
- `GPU PERFORMANCE` section includes metrics rows and a compact sparkline.
- The sidebar must keep the existing IDs used by `viewer.js`: `search`, `typeFilters`, `layerFilters`, `weightFilter`, `timelineFilter`, `motionToggle`, `animationSpeed`, `cometsToggle`, `orbitGuidesToggle`, `nodeScale`, `relationshipMode` or hidden compatibility controls.

### 3. Top Center Toolbar

- Toolbar floats over the canvas at the top, aligned left-to-right.
- Left group:
  - Back button with left arrow icon.
  - View dropdown/pill reading `Galactic View`.
  - Search input reading `Search memory galaxy...`.
- Right group:
  - Icon buttons for visual settings, help, fullscreen.
- Toolbar controls are translucent rounded rectangles with 1px blue-gray borders and subtle hover glow.
- Existing functions must map to these visuals:
  - Back button triggers `backView`.
  - View pill mirrors `viewBadge`.
  - Search input remains `search`.
  - Fit/fullscreen button can call existing `fitTop` or a new non-breaking wrapper.

### 4. Center Galaxy Stage

- Background is a rich starfield with faint blue nebula bands and sparse warm stars.
- Main layout is a galaxy map with:
  - Bright central `ROUTER CORE`.
  - Multiple named systems around it.
  - Each system rendered as a glowing spiral disk with concentric orbit trails.
  - Curved luminous connection arcs between systems.
  - Dense points/stars around systems, not plain flat dots.
  - Labels with leader lines, uppercase system name, type line, and node count line.
- System colors in preview:
  - Router: electric blue.
  - Aegis/right: gold.
  - Pegasus/Phoenix: magenta-purple.
  - Andromeda/Orion: blue.
  - Cygnus: cyan.
  - Lyra: violet.
- Existing systems should keep real memory-system labels; if preview labels are not real data, do not fabricate them. Match the format, not the fake content.
- Existing click, double-click, drag, hover, zoom, pan, labels, relation modes, and animation behavior must remain intact.

### 5. Floating Stats HUD

- Near upper-left of the canvas is a small glass panel with:
  - `Live` green pill.
  - `Streaming Updates`.
  - Rows for systems, nodes, connections, inferred links.
- This should be populated from existing metadata and filtered graph counts.
- It should not replace the left sidebar stats text unless needed for compatibility; it can mirror `renderStats`.

### 6. Bottom Toolbar

- Center-bottom toolbar floats over the stage.
- Contains icon-only controls: target/orbit, hand/pan, focus, rotate, zoom out, zoom in, and `3D` pill.
- Visual requirement is more important than adding new behavior.
- Map existing actions:
  - target/orbit: `fit`.
  - hand/pan: visual hint for Ctrl-drag/pan.
  - focus: selected focus or fit current bounds.
  - rotate: `motionToggle`.
  - zoom controls can call renderer zoom methods only if added safely; otherwise leave disabled-looking but non-breaking.
  - `3D` links to `viewer-3d.html`.

### 7. Minimap

- Bottom-right canvas overlay is a small minimap with translucent panel border.
- Contains tiny colored dots and a rectangular viewport indicator.
- Initial implementation can be DOM/CSS plus layout-derived dot positions if renderer transform is readable.
- It must not intercept canvas pointer events except where a later task explicitly supports minimap navigation.

### 8. Right Inspector

- Top header displays selected system/node:
  - star/icon marker.
  - uppercase title.
  - `Focus` button.
  - type line, system ID line, active status.
- Tab bar contains `OVERVIEW`, `NODES (...)`, `CONNECTIONS`.
- Overview section includes:
  - circular integrity/progress gauge.
  - right-aligned metric rows: total nodes, connections, average connections, density, last updated.
- `NODE TYPE BREAKDOWN` section:
  - `View All` link.
  - colored dot, label, progress bar, count, percent.
- `TOP CONNECTIONS` section:
  - same progress-list structure.
- `RECENT ACTIVITY` section:
  - vertical timeline dots, activity label, timestamp.
  - bottom link `View All Activity`.
- This panel must still show existing selection content, relation information, agent prompt, and system summary. The implementation should reformat those sections into preview-like blocks rather than deleting them.

## File Structure

- Modify: `src/tools/memory_graph_viewer_assets/index.html`
  - Reorder DOM into preview-matching left sidebar, top toolbar, floating stats HUD, center stage overlays, bottom toolbar, minimap, and right inspector.
- Modify: `src/tools/memory_graph_viewer_assets/styles.css`
  - Replace current panel-card styling with the preview's dark HUD system, exact column sizing, typography, controls, sliders, checkboxes, tabs, gauges, progress rows, minimap, and starfield.
- Modify: `src/tools/memory_graph_viewer_assets/viewer.js`
  - Keep existing data flow and event handlers. Add or adapt render helpers for live stats HUD, right-panel preview sections, tabs, gauge/progress lists, minimap data, and toolbar state.
- Modify: `src/tools/memory_graph_viewer_assets/memory-galaxy-renderer.js`
  - Upgrade Pixi drawing to preview-like luminous spiral systems, orbit trails, label leader lines, curved arcs, star glows, selected focus rings, and nebula/star density without changing pointer handlers.
- Modify: `tests/js/memory_galaxy_smoke.test.mjs`
  - Add pure checks for renderer helper exports only if new pure helpers are exported.
- Modify: `tests/js/memory_galaxy_browser_regression.test.mjs`
  - Add DOM and interaction assertions for preview UI shell while preserving existing galaxy, solar, planet, and motion assertions.
- Optional Modify: `src/tools/memory_graph_viewer_assets/viewer-shared.js`
  - Only if shared formatting helpers are needed for counts, percentages, or safe progress rows.

## Non-Breaking Rules

- Do not rename existing DOM IDs without updating `viewer.js` in the same task.
- Do not remove current filters: type, layer, search, minimum edge weight, timeline.
- Do not remove selection, relations, agent prompt, or system summary content.
- Do not change graph export format.
- Do not change `memory-galaxy-layouts.js` positions solely for cosmetics unless renderer styling cannot match the preview with the existing layout.
- Do not replace PixiJS with a new renderer. PixiJS already provides GPU-accelerated rendering for this use case.
- Do not add fabricated preview data. Use real metadata and current graph-derived counts.
- Keep `viewer-3d.html` and `viewer-3d.js` behavior intact.

## Task 1: Add Browser Test For Preview Shell

**Files:**
- Modify: `tests/js/memory_galaxy_browser_regression.test.mjs`

- [ ] **Step 1: Add DOM shell assertions after initial page load**

Add this block after `await page.waitForFunction(...)`:

```javascript
const shell = await page.evaluate(() => ({
  app: document.querySelector(".galaxy-app") ? true : false,
  left: document.querySelector(".sidebar-left") ? true : false,
  stage: document.querySelector(".galaxy-stage") ? true : false,
  right: document.querySelector(".inspector") ? true : false,
  topToolbar: document.querySelector(".stage-toolbar") ? true : false,
  liveHud: document.querySelector(".live-hud") ? true : false,
  bottomToolbar: document.querySelector(".stage-bottom-toolbar") ? true : false,
  minimap: document.querySelector(".galaxy-minimap") ? true : false,
  inspectorTabs: [...document.querySelectorAll(".inspector-tabs button")].map(button => button.textContent.trim()),
}));
assert.equal(shell.app, true);
assert.equal(shell.left, true);
assert.equal(shell.stage, true);
assert.equal(shell.right, true);
assert.equal(shell.topToolbar, true);
assert.equal(shell.liveHud, true);
assert.equal(shell.bottomToolbar, true);
assert.equal(shell.minimap, true);
assert.deepEqual(shell.inspectorTabs, ["OVERVIEW", "NODES", "CONNECTIONS"]);
```

- [ ] **Step 2: Add layout measurements**

Add:

```javascript
const shellMetrics = await page.evaluate(() => {
  const left = document.querySelector(".sidebar-left").getBoundingClientRect();
  const right = document.querySelector(".inspector").getBoundingClientRect();
  const stage = document.querySelector(".galaxy-stage").getBoundingClientRect();
  return {
    leftWidth: Math.round(left.width),
    rightWidth: Math.round(right.width),
    stageWidth: Math.round(stage.width),
  };
});
assert.ok(shellMetrics.leftWidth >= 270 && shellMetrics.leftWidth <= 310);
assert.ok(shellMetrics.rightWidth >= 300 && shellMetrics.rightWidth <= 340);
assert.ok(shellMetrics.stageWidth > 700);
```

- [ ] **Step 3: Run and confirm failure before implementation**

Run:

```powershell
node tests/js/memory_galaxy_browser_regression.test.mjs
```

Expected: failure because `.live-hud`, `.stage-bottom-toolbar`, `.galaxy-minimap`, and `.inspector-tabs` do not exist yet.

## Task 2: Rebuild HTML Shell To Match Preview

**Files:**
- Modify: `src/tools/memory_graph_viewer_assets/index.html`

- [ ] **Step 1: Replace left header markup**

Change the header inside `.sidebar-left` to:

```html
<header class="app-header">
  <div class="brand-row">
    <div class="brand-mark" aria-hidden="true"></div>
    <div class="brand-copy">
      <div class="brand-title-row">
        <h1>MEMORY GALAXY</h1>
        <span class="gpu-badge">GPU</span>
      </div>
      <p id="stats">Loading galaxy...</p>
    </div>
  </div>
</header>
```

- [ ] **Step 2: Convert left sections to preview labels**

Keep existing input IDs, but arrange them under:

```html
<section class="panel-section view-controls">
  <h2>VIEW CONTROLS</h2>
  ...
</section>
<section class="panel-section filters-panel">
  <h2>FILTERS</h2>
  ...
</section>
<section class="panel-section gpu-panel">
  <h2>GPU PERFORMANCE</h2>
  ...
</section>
```

The controls must include these existing IDs at least once: `search`, `typeFilters`, `layerFilters`, `weightFilter`, `timelineFilter`, `animationSpeed`, `motionToggle`, `cometsToggle`, `orbitGuidesToggle`, `nodeScale`.

- [ ] **Step 3: Add top toolbar, live HUD, bottom toolbar, minimap**

Inside `.galaxy-stage`, use this structure:

```html
<header class="stage-toolbar">
  <button id="backView" type="button" class="icon-button" aria-label="Back">‹</button>
  <button id="viewBadge" type="button" class="toolbar-pill">Galactic View</button>
  <label class="stage-search">
    <span aria-hidden="true">⌕</span>
    <input id="stageSearchMirror" type="search" placeholder="Search memory galaxy...">
  </label>
  <div class="stage-toolbar-spacer"></div>
  <button type="button" class="icon-button" aria-label="Display settings">☼</button>
  <button type="button" class="icon-button" aria-label="Help">?</button>
  <button id="fitTop" type="button" class="icon-button" aria-label="Fit view">⛶</button>
</header>
<section id="galaxy2d" class="galaxy-canvas" aria-label="2D memory galaxy">
  <aside class="live-hud" aria-label="Live graph statistics">
    <div class="live-title"><span class="live-dot"></span><span>Live</span><strong>Streaming Updates</strong></div>
    <div id="liveHudRows" class="live-hud-rows"></div>
  </aside>
  <nav class="stage-bottom-toolbar" aria-label="Canvas tools">
    <button id="fit" type="button" aria-label="Fit">◎</button>
    <button type="button" aria-label="Pan mode"> hand </button>
    <button id="clearFocus" type="button" aria-label="Galaxy">⌖</button>
    <button id="motionButton" type="button" aria-label="Motion">◌</button>
    <button id="zoomOut" type="button" aria-label="Zoom out">−</button>
    <button id="zoomIn" type="button" aria-label="Zoom in">+</button>
    <a class="toolbar-3d" href="viewer-3d.html">3D</a>
  </nav>
  <aside class="galaxy-minimap" aria-label="Galaxy minimap">
    <div id="minimapDots" class="minimap-dots"></div>
    <div class="minimap-window"></div>
  </aside>
</section>
```

Use real icon components later if available; the first implementation keeps text/icon characters minimal and accessible.

- [ ] **Step 4: Replace right inspector shell**

Keep these IDs in the right panel: `selectionCard`, `relationsPanel`, `agentPrompt`, `systemSummary`. Wrap them in preview sections:

```html
<aside class="details inspector">
  <section id="selectionCard" class="selection-card inspector-hero">Select a system or node to inspect it.</section>
  <nav class="inspector-tabs" aria-label="Inspector sections">
    <button type="button" class="is-active" data-tab="overview">OVERVIEW</button>
    <button type="button" data-tab="nodes">NODES</button>
    <button type="button" data-tab="connections">CONNECTIONS</button>
  </nav>
  <section id="systemSummary" class="system-summary inspector-block">System counts and top members appear here.</section>
  <section id="relationsPanel" class="relations-panel inspector-block">Relations appear here when a node is selected.</section>
  <section id="agentPrompt" class="agent-prompt inspector-block">Select or drag a node to stage an agent prompt.</section>
</aside>
```

- [ ] **Step 5: Run HTML-dependent browser test**

Run:

```powershell
node tests/js/memory_galaxy_browser_regression.test.mjs
```

Expected: shell assertions pass or fail only on styling/behavior not yet implemented.

## Task 3: Implement Preview HUD CSS

**Files:**
- Modify: `src/tools/memory_graph_viewer_assets/styles.css`

- [ ] **Step 1: Replace global tokens**

Use:

```css
:root {
  color-scheme: dark;
  --bg-app: #020712;
  --bg-panel: rgba(5, 12, 22, 0.92);
  --bg-panel-strong: rgba(7, 15, 28, 0.96);
  --bg-control: rgba(9, 18, 34, 0.82);
  --line-soft: rgba(111, 139, 180, 0.22);
  --line-strong: rgba(125, 163, 220, 0.36);
  --text-1: #f4f7fb;
  --text-2: #b6c2d7;
  --text-3: #77859c;
  --accent-blue: #4ea1ff;
  --accent-cyan: #55dce0;
  --accent-green: #55d6a0;
  --accent-gold: #f7c65a;
  --accent-purple: #b36cff;
  --radius-panel: 8px;
  --radius-control: 6px;
}
```

- [ ] **Step 2: Set exact preview grid**

Use:

```css
.app {
  display: grid;
  grid-template-columns: 292px minmax(720px, 1fr) 320px;
  height: 100vh;
  overflow: hidden;
  background: #020712;
}
```

- [ ] **Step 3: Style sidebars as HUD planes**

Implement:

```css
.sidebar,
.details {
  min-height: 0;
  overflow-y: auto;
  background: linear-gradient(180deg, rgba(6, 13, 24, 0.96), rgba(4, 10, 19, 0.92));
  border-color: var(--line-soft);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(12px);
}
```

- [ ] **Step 4: Style center overlays**

Add CSS for `.stage-toolbar`, `.live-hud`, `.stage-bottom-toolbar`, `.galaxy-minimap`, `.minimap-window`, `.toolbar-3d`, and `.stage-search` so they float over `.galaxy-canvas` with absolute positioning.

- [ ] **Step 5: Style inspector blocks**

Add CSS for `.inspector-hero`, `.inspector-tabs`, `.integrity-gauge`, `.breakdown-row`, `.progress-track`, `.activity-list`, and `.activity-item` matching the preview's compact right rail.

- [ ] **Step 6: Verify shell measurements**

Run:

```powershell
node tests/js/memory_galaxy_browser_regression.test.mjs
```

Expected: DOM shell and width assertions pass.

## Task 4: Adapt Viewer DOM Rendering Without Changing Logic

**Files:**
- Modify: `src/tools/memory_graph_viewer_assets/viewer.js`

- [ ] **Step 1: Mirror stage search to existing search**

Add a small binding after existing search listener:

```javascript
const search = document.getElementById("search");
const stageSearch = document.getElementById("stageSearchMirror");
stageSearch?.addEventListener("input", event => {
  if (search) search.value = event.target.value;
  scheduleApplyFilters();
});
search?.addEventListener("input", event => {
  if (stageSearch && stageSearch.value !== event.target.value) stageSearch.value = event.target.value;
});
```

- [ ] **Step 2: Render live HUD rows from existing stats data**

Update `renderStats(metadata)` to also fill `#liveHudRows`:

```javascript
const liveRows = document.getElementById("liveHudRows");
if (liveRows) {
  liveRows.innerHTML = [
    ["Systems", countVisibleSystems()],
    ["Nodes", visibleNodes],
    ["Connections", visibleEdges],
    ["Inferred Links", filteredEdges],
  ].map(([label, value]) => `
    <div class="hud-row"><span>${escapeHtml(label)}</span><strong>${escapeHtml(formatCompactNumber(value))}</strong></div>
  `).join("");
}
```

Add local helpers:

```javascript
function formatCompactNumber(value) {
  const number = Number(value || 0);
  if (number >= 1000000) return `${(number / 1000000).toFixed(1)}M`;
  if (number >= 1000) return `${(number / 1000).toFixed(number >= 10000 ? 0 : 1)}K`;
  return String(number);
}

function countVisibleSystems() {
  return new Set(filteredGraph.nodes.map(node => visibleNodeSystem(node))).size;
}
```

- [ ] **Step 3: Reformat system selection card**

Change `showSystemSelection(systemKey)` so `selectionCard` renders:

```html
<div class="inspector-title-row">
  <div class="inspector-title-main">
    <span class="selection-glow" style="color:..."></span>
    <div>
      <div class="selection-name">...</div>
      <div class="meta-inline">...</div>
      <div class="meta-inline">System ID: ...</div>
    </div>
  </div>
  <button type="button" class="focus-button">Focus</button>
</div>
<div class="active-row"><span class="live-dot"></span><span>Active</span></div>
```

- [ ] **Step 4: Reformat `renderSystemSummary(systemKey)`**

Make the summary include:

```html
<div class="overview-metrics">
  <div class="integrity-gauge" style="--value: 0.987"><strong>98.7%</strong><span>Excellent</span></div>
  <div class="metric-stack">...</div>
</div>
<div class="breakdown-section">...</div>
<div class="activity-list">...</div>
```

Use real values from `members`, `filteredGraph.links`, and available timestamps. If no timestamp exists, show `unknown`, not fabricated seconds.

- [ ] **Step 5: Keep relation panel content but preview-style rows**

Update `renderRelationsForNode` and `renderRelationsForSystem` rows to include colored dots and bars. The relation counts and weights must remain graph-derived.

- [ ] **Step 6: Syntax-check**

Run:

```powershell
node --check src/tools/memory_graph_viewer_assets/viewer.js
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: both pass.

## Task 5: Upgrade Pixi Rendering To Preview Galaxy Style

**Files:**
- Modify: `src/tools/memory_graph_viewer_assets/memory-galaxy-renderer.js`

- [ ] **Step 1: Add curved relation arcs**

Change `drawLinks` from straight `moveTo().lineTo()` to quadratic curves:

```javascript
const midX = (source.x + target.x) / 2;
const midY = (source.y + target.y) / 2;
const dx = target.x - source.x;
const dy = target.y - source.y;
const distance = Math.hypot(dx, dy) || 1;
const bend = Math.min(120, Math.max(26, distance * 0.16));
const controlX = midX + (-dy / distance) * bend;
const controlY = midY + (dx / distance) * bend;
line.moveTo(source.x, source.y).quadraticCurveTo(controlX, controlY, target.x, target.y);
```

- [ ] **Step 2: Draw spiral systems for system nodes**

In `drawNodeBody`, detect:

```javascript
const systemLike = node.isSystemNode || ["galactic-core", "central-star", "star"].includes(node.orbitalRole);
```

For `systemLike`, draw:

- 4-6 low-alpha concentric ellipses.
- 16-36 tiny particles placed around the ellipse.
- A bright core glow.
- A horizontal/diagonal lens flare for selected or high-priority systems.

- [ ] **Step 3: Draw smaller star nodes for normal nodes**

For non-system nodes:

- Keep outer glow and filled body.
- Add one small highlight dot.
- Keep selected/hover ring.
- Do not increase hit target behavior.

- [ ] **Step 4: Add label leader lines**

In `drawLabels`, before adding text for pinned/system labels, draw a subtle line from node edge to label anchor:

```javascript
const leader = new PIXI.Graphics();
leader.moveTo(node.x, node.y).lineTo(anchor.x, anchor.y);
leader.stroke({ width: 0.8, color: 0xc8d8ff, alpha: 0.34 });
labelLayer.addChild(leader);
```

- [ ] **Step 5: Keep pointer handlers intact**

Do not alter `graphics.on("pointerdown")`, `pointerover`, `pointerout`, system hit zones, drag handling, wheel zoom, Ctrl-pan, or ticker animation.

- [ ] **Step 6: Syntax-check and run interaction regression**

Run:

```powershell
node --check src/tools/memory_graph_viewer_assets/memory-galaxy-renderer.js
node tests/js/memory_galaxy_browser_regression.test.mjs
```

Expected: existing interaction assertions still pass.

## Task 6: Add Minimap Rendering

**Files:**
- Modify: `src/tools/memory_graph_viewer_assets/viewer.js`
- Modify: `src/tools/memory_graph_viewer_assets/styles.css`

- [ ] **Step 1: Render minimap dots after layout draw**

At the end of `drawCurrentLayout`, call:

```javascript
renderMinimap(currentLayout);
```

Add:

```javascript
function renderMinimap(layout) {
  const root = document.getElementById("minimapDots");
  if (!root || !layout?.bounds) return;
  const bounds = layout.bounds;
  const width = Math.max(1, bounds.width);
  const height = Math.max(1, bounds.height);
  root.innerHTML = (layout.systems || []).filter(system => system.key !== "router").map(system => {
    const x = ((system.x - bounds.minX) / width) * 100;
    const y = ((system.y - bounds.minY) / height) * 100;
    return `<span class="minimap-dot" style="left:${x.toFixed(2)}%;top:${y.toFixed(2)}%;background:${escapeHtml(system.color || systemColor(system.key))}"></span>`;
  }).join("");
}
```

If `systemColor` is not imported, use existing `systemColor(systemKey)` helper already defined in `viewer.js`.

- [ ] **Step 2: Style minimap dots**

Add:

```css
.minimap-dot {
  position: absolute;
  width: 5px;
  height: 5px;
  border-radius: 999px;
  transform: translate(-50%, -50%);
  box-shadow: 0 0 10px currentColor;
}
```

- [ ] **Step 3: Test minimap exists and has dots**

Add to browser test after layout is available:

```javascript
const minimapCount = await page.locator(".minimap-dot").count();
assert.ok(minimapCount >= 1);
```

- [ ] **Step 4: Run regression**

Run:

```powershell
node tests/js/memory_galaxy_browser_regression.test.mjs
```

Expected: pass.

## Task 7: Visual Verification Against Preview

**Files:**
- No code changes unless a mismatch is found.

- [ ] **Step 1: Run focused checks**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
node --check src/tools/memory_graph_viewer_assets/viewer.js
node --check src/tools/memory_graph_viewer_assets/memory-galaxy-renderer.js
node tests/js/memory_galaxy_browser_regression.test.mjs
```

Expected: all pass.

- [ ] **Step 2: Start local viewer**

Run the existing dashboard/export command used by this repo, or serve the asset directory if `graph.json` is already present:

```powershell
python -m http.server 8766
```

Expected: viewer is reachable at `http://127.0.0.1:8766/`.

- [ ] **Step 3: Capture screenshots**

Use Playwright or the browser regression harness to capture:

- Desktop `1728x960`.
- Desktop `1440x960`.
- Narrow `980x900`.

Expected desktop:

- Left rail visually matches preview density.
- Center is full starfield with floating top toolbar, live HUD, bottom toolbar, and minimap.
- Right rail has preview-like selected hero, tabs, gauge, progress lists, and activity rows.
- Graph interactions still work: click system, double-click system, click planet, double-click planet, hover, drag, wheel zoom, Ctrl-pan.

Expected narrow:

- No text overlaps.
- Side panels collapse according to existing responsive rules or remain scrollable.
- Canvas remains usable.

- [ ] **Step 4: Pixel sanity checks**

Use screenshot inspection to verify:

- Canvas is not blank.
- Left and right panels are darker than the center starfield.
- At least five distinct system glow colors are visible.
- The minimap is visible in the lower-right of the canvas.
- No large marketing-style card appears over the primary galaxy.

## Self-Review

- Spec coverage: This plan covers every visible area in the preview: left controls, top toolbar, live HUD, center galaxy styling, bottom toolbar, minimap, and right inspector.
- Preservation coverage: The plan keeps current IDs, graph data flow, filters, selection, relations, agent prompt, Pixi pointer handlers, and 3D page behavior.
- Dependency decision: No GitHub dependency search is required before implementation because the current code already uses PixiJS 8 for GPU-accelerated rendering; adding another renderer would increase risk without being necessary for the requested UI match.
- Placeholder scan: No task depends on unknown files or unspecified future work.
- Type consistency: The plan consistently uses the current files and functions: `drawCurrentLayout`, `renderStats`, `showSystemSelection`, `renderSystemSummary`, `renderRelationsForNode`, `renderRelationsForSystem`, and `createMemoryGalaxyRenderer`.

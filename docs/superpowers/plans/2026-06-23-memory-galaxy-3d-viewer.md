# Memory Galaxy 3D Viewer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the existing Total Agent Memory 3D graph viewer into a galaxy-style focus exploration view with lightweight organization actions.

**Architecture:** Keep the current static export model: Python writes `graph.json` plus static assets, and the browser renders the graph locally. Extend the exported metadata enough for a 3D "memory galaxy" layout, then enhance `viewer-3d.js` with focus-centered orbit layout, layer filters, timeline filtering, and a right-side inspector with safe copy/export/edit-intent actions.

**Tech Stack:** Python 3 standard library, pytest, static HTML/CSS/JavaScript, `3d-force-graph`, Three.js via CDN, existing Total Agent Memory SQLite graph tables.

---

## Scope

This plan enhances the existing local viewer in `C:\Users\Administrator\total-agent-memory`. It does not replace the memory backend, add a live write API, or require a web framework. Editing actions in this version are intentionally lightweight and local-first: copy commands, export selected node details, and stage relation/edit intent JSON that a later backend or MCP action can consume.

## File Structure

- Modify: `src/tools/memory_graph_viewer_export.py`
  - Add derived fields used by the galaxy UI: layer, freshness, activity, relation class counts, timeline bounds.
- Modify: `tests/test_memory_graph_viewer_export.py`
  - Assert the new metadata and node fields are exported.
- Modify: `src/tools/memory_graph_viewer_assets/viewer-3d.html`
  - Rename the page experience to "Memory Galaxy", add controls for focus mode, layer filters, timeline slider, and inspector action buttons.
- Modify: `src/tools/memory_graph_viewer_assets/viewer-3d.js`
  - Add galaxy layout, focus orbit behavior, semantic layers, timeline filtering, neighborhood expansion, and inspector actions.
- Modify: `src/tools/memory_graph_viewer_assets/styles.css`
  - Add galaxy-specific layout, compact filter chips, inspector action styles, and timeline controls.
- Create: `tests/js/memory_galaxy_smoke.test.mjs`
  - Node-based pure-function smoke tests for graph conversion, filtering, and action payload creation.
- Create: `src/tools/memory_graph_viewer_assets/memory-galaxy-core.js`
  - Extract pure conversion/filter/action helpers from `viewer-3d.js` so they can be tested without a browser.

## Task 1: Export Galaxy Metadata

**Files:**
- Modify: `tests/test_memory_graph_viewer_export.py`
- Modify: `src/tools/memory_graph_viewer_export.py`

- [ ] **Step 1: Inspect the existing export test**

Run:

```powershell
python -m pytest tests/test_memory_graph_viewer_export.py -v
```

Expected: PASS before edits. If it fails, stop and fix the existing test fixture before changing the exporter.

- [ ] **Step 2: Add failing assertions for node galaxy fields**

In `tests/test_memory_graph_viewer_export.py`, update the test that inspects exported nodes. Add assertions equivalent to:

```python
node = graph["elements"]["nodes"][0]["data"]
assert "galaxy_layer" in node
assert node["galaxy_layer"] in {"core", "active", "knowledge", "episode", "external"}
assert "freshness" in node
assert 0.0 <= node["freshness"] <= 1.0
assert "activity" in node
assert 0.0 <= node["activity"] <= 1.0
```

- [ ] **Step 3: Add failing assertions for graph-level timeline metadata**

In the same test file, add:

```python
metadata = graph["metadata"]
assert "timeline" in metadata
assert set(metadata["timeline"]) == {"start", "end"}
assert metadata["timeline"]["start"] <= metadata["timeline"]["end"]
```

- [ ] **Step 4: Run test to verify it fails**

Run:

```powershell
python -m pytest tests/test_memory_graph_viewer_export.py -v
```

Expected: FAIL because `galaxy_layer`, `freshness`, `activity`, and `metadata.timeline` are not exported yet.

- [ ] **Step 5: Add helper functions to the exporter**

In `src/tools/memory_graph_viewer_export.py`, add these helpers near `_truncate`:

```python
from datetime import datetime, timezone


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        text = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(text)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def _freshness(last_seen_at: str | None, newest: datetime | None, oldest: datetime | None) -> float:
    seen = _parse_iso(last_seen_at)
    if not seen or not newest or not oldest or newest <= oldest:
        return 0.5
    span = (newest - oldest).total_seconds()
    pos = (seen - oldest).total_seconds()
    return round(max(0.0, min(1.0, pos / span)), 3)


def _activity(mention_count: int, max_mentions: int) -> float:
    if max_mentions <= 0:
        return 0.0
    return round(max(0.0, min(1.0, mention_count / max_mentions)), 3)


def _galaxy_layer(node_type: str, importance: float, mention_count: int) -> str:
    if node_type in {"rule", "decision"} or importance >= 1.4:
        return "core"
    if mention_count >= 10 or importance >= 0.9:
        return "active"
    if node_type in {"concept", "entity", "technology", "project"}:
        return "knowledge"
    if node_type in {"episode", "session", "observation"}:
        return "episode"
    return "external"
```

- [ ] **Step 6: Compute timeline and activity bounds in `load_graph`**

After `node_rows` is loaded, add:

```python
seen_dates = [_parse_iso(row["last_seen_at"]) for row in node_rows]
seen_dates = [date for date in seen_dates if date is not None]
oldest_seen = min(seen_dates) if seen_dates else None
newest_seen = max(seen_dates) if seen_dates else None
max_mentions = max((int(row["mention_count"] or 0) for row in node_rows), default=0)
```

- [ ] **Step 7: Add fields to each exported node**

In the `nodes = [...]` comprehension, add these fields inside `data`:

```python
"galaxy_layer": _galaxy_layer(
    str(row["type"]),
    float(row["importance"] or 0.0),
    int(row["mention_count"] or 0),
),
"freshness": _freshness(row["last_seen_at"], newest_seen, oldest_seen),
"activity": _activity(int(row["mention_count"] or 0), max_mentions),
```

- [ ] **Step 8: Add timeline metadata**

Inside the returned `metadata` dict, add:

```python
"timeline": {
    "start": oldest_seen.isoformat() if oldest_seen else "",
    "end": newest_seen.isoformat() if newest_seen else "",
},
```

- [ ] **Step 9: Run tests**

Run:

```powershell
python -m pytest tests/test_memory_graph_viewer_export.py -v
```

Expected: PASS.

- [ ] **Step 10: Commit**

```powershell
git add tests/test_memory_graph_viewer_export.py src/tools/memory_graph_viewer_export.py
git commit -m "feat: export memory galaxy metadata"
```

## Task 2: Extract Testable Galaxy Core Helpers

**Files:**
- Create: `src/tools/memory_graph_viewer_assets/memory-galaxy-core.js`
- Create: `tests/js/memory_galaxy_smoke.test.mjs`
- Modify: `src/tools/memory_graph_viewer_assets/viewer-3d.html`
- Modify: `src/tools/memory_graph_viewer_export.py`
- Modify: `tests/test_memory_graph_viewer_export.py`

- [ ] **Step 1: Write the JavaScript smoke test**

Create `tests/js/memory_galaxy_smoke.test.mjs`:

```javascript
import assert from "node:assert/strict";
import {
  convertGraphToGalaxy,
  filterGalaxy,
  buildEditIntent,
} from "../../src/tools/memory_graph_viewer_assets/memory-galaxy-core.js";

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

const intent = buildEditIntent("add_relation", { source: "p1", target: "c1", relation: "related" });
assert.equal(intent.action, "add_relation");
assert.equal(intent.payload.source, "p1");
assert.ok(intent.created_at);
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: FAIL because `memory-galaxy-core.js` does not exist.

- [ ] **Step 3: Create the core helper module**

Create `src/tools/memory_graph_viewer_assets/memory-galaxy-core.js`:

```javascript
const layerOrbit = {
  core: 70,
  active: 130,
  knowledge: 210,
  episode: 290,
  external: 370,
};

const typeColors = {
  project: "#60a5fa",
  concept: "#34d399",
  entity: "#fbbf24",
  memory: "#a78bfa",
  rule: "#f87171",
  decision: "#fb7185",
  solution: "#22c55e",
  lesson: "#f97316",
  convention: "#38bdf8",
  technology: "#38bdf8",
  pattern: "#fb7185",
  domain: "#c084fc",
  person: "#facc15",
  company: "#22c55e",
  default: "#94a3b8",
};

export function nodeColor(type) {
  return typeColors[type] || typeColors.default;
}

export function convertGraphToGalaxy(graph) {
  const nodes = graph.elements.nodes.map((node, index) => {
    const data = node.data;
    const layer = data.galaxy_layer || inferLayer(data);
    const orbit = layerOrbit[layer] || layerOrbit.external;
    const angle = index * 2.399963229728653;
    const lift = ((index % 9) - 4) * 14;
    return {
      id: String(data.id),
      label: data.label || data.name || String(data.id),
      type: data.type || "default",
      layer,
      orbit,
      val: Math.max(3, Math.min(28, 4 + Number(data.activity || 0) * 20 + Number(data.importance || 0) * 3)),
      color: nodeColor(data.type),
      x: Math.cos(angle) * orbit,
      y: lift,
      z: Math.sin(angle) * orbit,
      raw: data,
    };
  });

  const links = graph.elements.edges.map(edge => ({
    source: String(edge.data.source),
    target: String(edge.data.target),
    relation: edge.data.relation || "related",
    weight: Number(edge.data.weight || 0),
    raw: edge.data,
  }));

  return {
    nodes,
    links,
    metadata: graph.metadata || {},
  };
}

export function filterGalaxy(galaxy, options) {
  const query = (options.query || "").trim().toLowerCase();
  const activeTypes = options.activeTypes || new Set();
  const activeLayers = options.activeLayers || new Set();
  const minWeight = Number(options.minWeight || 0);
  const cutoff = options.timelineCutoff ? Date.parse(options.timelineCutoff) : null;

  const nodes = galaxy.nodes.filter(node => {
    if (activeTypes.size > 0 && !activeTypes.has(node.type)) return false;
    if (activeLayers.size > 0 && !activeLayers.has(node.layer)) return false;
    if (cutoff && node.raw.last_seen_at && Date.parse(node.raw.last_seen_at) > cutoff) return false;
    if (!query) return true;
    return `${node.label} ${node.type} ${node.layer} ${node.raw.content || ""}`.toLowerCase().includes(query);
  });

  const nodeIds = new Set(nodes.map(node => node.id));
  const links = galaxy.links.filter(link =>
    link.weight >= minWeight &&
    nodeIds.has(String(link.source.id || link.source)) &&
    nodeIds.has(String(link.target.id || link.target))
  );

  return { nodes, links, metadata: galaxy.metadata };
}

export function buildEditIntent(action, payload) {
  return {
    action,
    payload,
    created_at: new Date().toISOString(),
    source: "memory-galaxy-viewer",
  };
}

function inferLayer(data) {
  if (data.type === "rule" || data.type === "decision" || Number(data.importance || 0) >= 1.4) return "core";
  if (Number(data.mention_count || 0) >= 10 || Number(data.importance || 0) >= 0.9) return "active";
  if (["concept", "entity", "technology", "project"].includes(data.type)) return "knowledge";
  if (["episode", "session", "observation"].includes(data.type)) return "episode";
  return "external";
}
```

- [ ] **Step 4: Update 3D HTML to load the module**

In `src/tools/memory_graph_viewer_assets/viewer-3d.html`, replace:

```html
<script src="viewer-3d.js"></script>
```

with:

```html
<script type="module" src="viewer-3d.js"></script>
```

- [ ] **Step 5: Export the new asset**

In `src/tools/memory_graph_viewer_export.py`, update `copy_assets`:

```python
for asset in (
    "index.html",
    "styles.css",
    "viewer.js",
    "viewer-3d.html",
    "viewer-3d.js",
    "memory-galaxy-core.js",
):
    shutil.copy2(asset_dir / asset, output_dir / asset)
```

- [ ] **Step 6: Update the asset-copy test**

In `tests/test_memory_graph_viewer_export.py`, add:

```python
assert (output / "memory-galaxy-core.js").exists()
```

- [ ] **Step 7: Run tests**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
python -m pytest tests/test_memory_graph_viewer_export.py -v
```

Expected: both PASS.

- [ ] **Step 8: Commit**

```powershell
git add src/tools/memory_graph_viewer_assets/memory-galaxy-core.js src/tools/memory_graph_viewer_assets/viewer-3d.html src/tools/memory_graph_viewer_export.py tests/test_memory_graph_viewer_export.py tests/js/memory_galaxy_smoke.test.mjs
git commit -m "feat: add testable memory galaxy helpers"
```

## Task 3: Build the 3D Galaxy Experience

**Files:**
- Modify: `src/tools/memory_graph_viewer_assets/viewer-3d.html`
- Modify: `src/tools/memory_graph_viewer_assets/viewer-3d.js`
- Modify: `src/tools/memory_graph_viewer_assets/styles.css`

- [ ] **Step 1: Rename the 3D page shell**

In `viewer-3d.html`, change the title and header:

```html
<title>Total Agent Memory Galaxy</title>
...
<h1>Memory Galaxy</h1>
<p id="stats">Loading galaxy...</p>
```

- [ ] **Step 2: Add layer filters and timeline controls to the sidebar**

After the Node Types section in `viewer-3d.html`, add:

```html
<section>
  <h2>Galaxy Layers</h2>
  <div id="layerFilters" class="filters compact"></div>
</section>

<label class="field">
  Timeline
  <input id="timelineFilter" type="range" min="0" max="100" step="1" value="100">
  <span id="timelineValue">All time</span>
</label>
```

- [ ] **Step 3: Add focus controls**

Inside the View button group, keep existing buttons and add:

```html
<button id="focusNeighborhood" type="button">Neighborhood</button>
<button id="copySelection" type="button">Copy</button>
<button id="stageIntent" type="button">Stage Intent</button>
```

- [ ] **Step 4: Replace `viewer-3d.js` imports and globals**

At the top of `viewer-3d.js`, replace the current color helpers with:

```javascript
import {
  buildEditIntent,
  convertGraphToGalaxy,
  filterGalaxy,
  nodeColor,
} from "./memory-galaxy-core.js";

let Graph3D;
let originalGraph = { nodes: [], links: [], metadata: {} };
let visibleGraph = { nodes: [], links: [], metadata: {} };
let activeTypes = new Set();
let activeLayers = new Set(["core", "active", "knowledge", "episode", "external"]);
let selectedNodeId = null;
let selectedNode = null;
let stagedIntents = [];
```

- [ ] **Step 5: Use galaxy conversion in `init`**

Replace the conversion call in `init`:

```javascript
originalGraph = convertGraphToGalaxy(graph);
activeTypes = new Set(Object.keys(graph.metadata.type_counts));
renderTypeFilters(graph.metadata.type_counts);
renderLayerFilters();
renderStats(graph.metadata);
createGraph();
bindControls();
applyFilters();
```

- [ ] **Step 6: Add layer filter rendering**

Add:

```javascript
function renderLayerFilters() {
  const root = document.getElementById("layerFilters");
  const layers = [
    ["core", "Core"],
    ["active", "Active"],
    ["knowledge", "Knowledge"],
    ["episode", "Episodes"],
    ["external", "External"],
  ];
  root.innerHTML = "";
  for (const [layer, labelText] of layers) {
    const label = document.createElement("label");
    label.innerHTML = `
      <input type="checkbox" data-layer="${escapeHtml(layer)}" checked>
      <span><span class="pill">${escapeHtml(labelText)}</span></span>
    `;
    root.appendChild(label);
  }
}
```

- [ ] **Step 7: Update graph visual style**

In `createGraph`, use:

```javascript
Graph3D = ForceGraph3D()(container)
  .backgroundColor("#050913")
  .nodeLabel(node => `${node.label} | ${node.type} | ${node.layer}`)
  .nodeColor(node => node.id === selectedNodeId ? "#ffffff" : node.color)
  .nodeVal(node => node.val)
  .nodeOpacity(0.94)
  .linkColor(link => relationColor(link.relation))
  .linkWidth(link => Math.max(0.35, Math.min(4, link.weight)))
  .linkOpacity(0.34)
  .linkDirectionalParticles(link => link.weight >= 4 ? 2 : 0)
  .linkDirectionalParticleWidth(1.1)
  .cooldownTicks(120)
  .onNodeClick(node => {
    selectedNodeId = node.id;
    selectedNode = node;
    showDetails(node.raw);
    focusNode(node);
    Graph3D.nodeColor(n => n.id === selectedNodeId ? "#ffffff" : n.color);
  });
```

Add:

```javascript
function relationColor(relation) {
  if (relation === "contradicts") return "rgba(248, 113, 113, 0.75)";
  if (relation === "solution") return "rgba(34, 197, 94, 0.65)";
  if (relation === "causal") return "rgba(251, 191, 36, 0.65)";
  if (relation === "context") return "rgba(96, 165, 250, 0.55)";
  return "rgba(148, 163, 184, 0.42)";
}
```

- [ ] **Step 8: Wire layer and timeline controls**

In `bindControls`, add:

```javascript
document.getElementById("layerFilters").addEventListener("change", event => {
  if (!event.target.matches("input[type='checkbox']")) return;
  const layer = event.target.dataset.layer;
  if (event.target.checked) activeLayers.add(layer);
  else activeLayers.delete(layer);
  applyFilters();
});

document.getElementById("timelineFilter").addEventListener("input", applyFilters);
document.getElementById("focusNeighborhood").addEventListener("click", showNeighborhoodOnly);
document.getElementById("copySelection").addEventListener("click", copySelection);
document.getElementById("stageIntent").addEventListener("click", stageSelectedIntent);
```

- [ ] **Step 9: Replace `applyFilters`**

Use:

```javascript
function applyFilters() {
  const timelineCutoff = timelineCutoffFromSlider();
  visibleGraph = filterGalaxy(originalGraph, {
    query: document.getElementById("search").value,
    activeTypes,
    activeLayers,
    minWeight: Number(document.getElementById("weightFilter").value),
    timelineCutoff,
  });
  Graph3D.graphData(visibleGraph);
  selectedNodeId = null;
  selectedNode = null;
}
```

- [ ] **Step 10: Add timeline helper**

Add:

```javascript
function timelineCutoffFromSlider() {
  const slider = document.getElementById("timelineFilter");
  const value = Number(slider.value);
  const timeline = originalGraph.metadata.timeline || {};
  if (value >= 100 || !timeline.start || !timeline.end) {
    document.getElementById("timelineValue").textContent = "All time";
    return null;
  }
  const start = Date.parse(timeline.start);
  const end = Date.parse(timeline.end);
  if (!Number.isFinite(start) || !Number.isFinite(end) || end <= start) return null;
  const cutoff = new Date(start + ((end - start) * value / 100));
  document.getElementById("timelineValue").textContent = cutoff.toISOString().slice(0, 10);
  return cutoff.toISOString();
}
```

- [ ] **Step 11: Add neighborhood focus**

Add:

```javascript
function showNeighborhoodOnly() {
  if (!selectedNode) return;
  const keep = new Set([selectedNode.id]);
  for (const link of originalGraph.links) {
    const source = String(link.source.id || link.source);
    const target = String(link.target.id || link.target);
    if (source === selectedNode.id) keep.add(target);
    if (target === selectedNode.id) keep.add(source);
  }
  const nodes = originalGraph.nodes.filter(node => keep.has(node.id));
  const links = originalGraph.links.filter(link =>
    keep.has(String(link.source.id || link.source)) &&
    keep.has(String(link.target.id || link.target))
  );
  visibleGraph = { nodes, links, metadata: originalGraph.metadata };
  Graph3D.graphData(visibleGraph);
}
```

- [ ] **Step 12: Add copy and intent staging actions**

Add:

```javascript
async function copySelection() {
  if (!selectedNode) return;
  const text = `${selectedNode.label}\nType: ${selectedNode.type}\nLayer: ${selectedNode.layer}\n\n${selectedNode.raw.content || ""}`;
  await navigator.clipboard.writeText(text);
  flashDetails("Copied selection to clipboard.");
}

function stageSelectedIntent() {
  if (!selectedNode) return;
  const intent = buildEditIntent("inspect_or_edit_node", {
    node_id: selectedNode.id,
    label: selectedNode.label,
    type: selectedNode.type,
    layer: selectedNode.layer,
  });
  stagedIntents.push(intent);
  localStorage.setItem("memoryGalaxyIntents", JSON.stringify(stagedIntents, null, 2));
  flashDetails(`Staged intent ${stagedIntents.length}. Stored in localStorage.memoryGalaxyIntents.`);
}

function flashDetails(message) {
  const root = document.getElementById("details");
  const notice = document.createElement("div");
  notice.className = "notice";
  notice.textContent = message;
  root.prepend(notice);
  setTimeout(() => notice.remove(), 2600);
}
```

- [ ] **Step 13: Improve selected-node details**

Update `showDetails` so the first block includes layer, freshness, activity, source, and timestamps:

```javascript
document.getElementById("details").innerHTML = `
  <div class="node-title">${escapeHtml(data.label)}</div>
  <div class="meta">
    ${escapeHtml(data.type)} | ${escapeHtml(data.galaxy_layer || "external")}
    | mentions ${escapeHtml(data.mention_count)}
    | importance ${escapeHtml(data.importance)}
  </div>
  <div class="meta">
    last seen ${escapeHtml(data.last_seen_at || "unknown")}
    | source ${escapeHtml(data.source || "unknown")}
  </div>
  <div>${escapeHtml(data.content || "No node content.")}</div>
  <h2>Linked Memories</h2>
  ${memories || "<p>No linked memories in exported sample.</p>"}
`;
```

- [ ] **Step 14: Add galaxy styles**

In `styles.css`, add:

```css
.filters.compact label {
  padding: 0.35rem 0.4rem;
}

.notice {
  margin: 0 0 0.75rem;
  padding: 0.55rem 0.65rem;
  border: 1px solid rgba(52, 211, 153, 0.4);
  border-radius: 6px;
  background: rgba(16, 185, 129, 0.12);
  color: #bbf7d0;
  font-size: 0.85rem;
}

.graph-3d {
  background:
    radial-gradient(circle at 50% 45%, rgba(56, 189, 248, 0.12), transparent 28%),
    radial-gradient(circle at 70% 30%, rgba(167, 139, 250, 0.10), transparent 22%),
    #050913;
}
```

- [ ] **Step 15: Run smoke tests**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
python -m pytest tests/test_memory_graph_viewer_export.py -v
```

Expected: PASS.

- [ ] **Step 16: Commit**

```powershell
git add src/tools/memory_graph_viewer_assets/viewer-3d.html src/tools/memory_graph_viewer_assets/viewer-3d.js src/tools/memory_graph_viewer_assets/styles.css
git commit -m "feat: turn 3d viewer into memory galaxy"
```

## Task 4: Add Safe Export And Verification Flow

**Files:**
- Modify: `docs/v12.5.0-memory-graph-viewer.md`
- Modify: `tests/test_memory_graph_viewer_export.py`

- [ ] **Step 1: Update documentation**

In `docs/v12.5.0-memory-graph-viewer.md`, add a section:

```markdown
## Memory Galaxy Mode

Open `viewer-3d.html` after exporting the viewer. The galaxy mode uses the same `graph.json` as the 2D Cytoscape viewer and adds:

- Focus-centered 3D navigation.
- Layer filters: core, active, knowledge, episode, external.
- Timeline cutoff filtering from the exported graph metadata.
- A right-side inspector for selected node metadata and linked memories.
- Local-only action staging through `localStorage.memoryGalaxyIntents`.

The galaxy mode does not write to the memory database. Use staged intents as reviewable suggestions for later MCP or CLI operations.
```

- [ ] **Step 2: Add doc asset assertions if the test checks docs**

If `tests/test_memory_graph_viewer_export.py` includes documentation checks, assert that the docs mention:

```python
assert "Memory Galaxy Mode" in docs_text
assert "localStorage.memoryGalaxyIntents" in docs_text
```

If the test file has no docs test, do not add one just for this plan.

- [ ] **Step 3: Run documentation-adjacent tests**

Run:

```powershell
python -m pytest tests/test_memory_graph_viewer_export.py -v
```

Expected: PASS.

- [ ] **Step 4: Commit**

```powershell
git add docs/v12.5.0-memory-graph-viewer.md tests/test_memory_graph_viewer_export.py
git commit -m "docs: describe memory galaxy mode"
```

## Task 5: End-To-End Browser Verification

**Files:**
- Output: `C:\Users\Administrator\Documents\Codex\2026-06-16\new-chat-3\outputs\memory-graph-viewer`

- [ ] **Step 1: Export the full viewer**

Run:

```powershell
python src/tools/memory_graph_viewer_export.py --output "C:\Users\Administrator\Documents\Codex\2026-06-16\new-chat-3\outputs\memory-graph-viewer"
```

Expected: JSON metadata prints with nonzero `node_count`, nonzero `edge_count`, and a `timeline` object.

- [ ] **Step 2: Verify exported files**

Run:

```powershell
Get-ChildItem "C:\Users\Administrator\Documents\Codex\2026-06-16\new-chat-3\outputs\memory-graph-viewer" | Select-Object Name,Length
```

Expected files include:

```text
graph.json
index.html
viewer.js
viewer-3d.html
viewer-3d.js
memory-galaxy-core.js
styles.css
```

- [ ] **Step 3: Start or reuse static server**

Run:

```powershell
Set-Location "C:\Users\Administrator\Documents\Codex\2026-06-16\new-chat-3\outputs\memory-graph-viewer"
python -m http.server 8765 --bind 127.0.0.1
```

Expected: server listens at `http://127.0.0.1:8765/`. If 8765 is occupied, use 8766 and report the actual URL.

- [ ] **Step 4: Manually verify the galaxy UI**

Open:

```text
http://127.0.0.1:8765/viewer-3d.html
```

Expected:

- The page title reads `Memory Galaxy`.
- The 3D canvas is nonblank and looks like a star field or galaxy.
- Type filters hide/show node classes.
- Layer filters hide/show `core`, `active`, `knowledge`, `episode`, and `external`.
- Timeline slider changes the visible graph and displayed date.
- Clicking a node focuses the camera and fills the inspector.
- `Neighborhood` reduces the scene to the selected node plus linked nodes.
- `Copy` writes readable node details to the clipboard.
- `Stage Intent` writes JSON to `localStorage.memoryGalaxyIntents`.

- [ ] **Step 5: Verify 2D mode still works**

Open:

```text
http://127.0.0.1:8765/index.html
```

Expected: existing 2D Cytoscape viewer still loads and reads the same `graph.json`.

- [ ] **Step 6: Commit verification note if docs changed during verification**

If verification revealed a documentation correction, commit it:

```powershell
git add docs/v12.5.0-memory-graph-viewer.md
git commit -m "docs: clarify memory galaxy verification"
```

If no docs changed, do not create an empty commit.

## Self-Review

- Spec coverage: The plan implements the requested 3D galaxy-style B view as the main experience, keeps A-style layers through layer filters, and supports C-style lightweight organization actions through copy/staged intents.
- Placeholder scan: The plan avoids open placeholders and gives exact files, code blocks, commands, and expected outcomes.
- Type consistency: The plan consistently uses `galaxy_layer`, `freshness`, `activity`, `timeline`, `convertGraphToGalaxy`, `filterGalaxy`, and `buildEditIntent` across Python export, JavaScript rendering, and tests.

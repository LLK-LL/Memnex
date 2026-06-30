# MAGMA Memory Galaxy Visualization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a dedicated MAGMA View to Memory Galaxy that visualizes semantic, temporal, causal, entity, and procedural graph families while preserving the current multi-agent Galaxy View.

**Architecture:** Extend the existing graph export with derived MAGMA family fields, preserve those fields through frontend conversion, then add a separate MAGMA layout mode with family shells, filters, and lightweight explanation in the existing inspector. `agent_namespace` remains the top-level visual and data isolation boundary.

**Tech Stack:** Python, SQLite, pytest, vanilla JavaScript modules, PixiJS renderer, Node smoke tests, Playwright browser regression.

---

## File Structure

- Modify: `src/tools/memory_graph_viewer_export.py`
  - Derive `edge_family`, node family weights, primary family, relation counts, and `metadata.magma_families`.
- Modify: `tests/test_memory_graph_viewer_export.py`
  - Add export tests for MAGMA family metadata and backward-compatible defaults.
- Modify: `src/tools/memory_graph_viewer_assets/memory-galaxy-core.js`
  - Preserve MAGMA fields on nodes and links; support family-aware filtering without deleting nodes.
- Modify: `src/tools/memory_graph_viewer_assets/memory-galaxy-layouts.js`
  - Add `buildMagmaGalaxyLayout(galaxy, options)` as a separate layout helper.
- Modify: `src/tools/memory_graph_viewer_assets/memory-galaxy-renderer.js`
  - Draw MAGMA family shells and style MAGMA edges.
- Modify: `src/tools/memory_graph_viewer_assets/memory-galaxy-view-state.js`
  - Add `view: "magma"` transitions and family filter state helpers.
- Modify: `src/tools/memory_graph_viewer_assets/viewer.js`
  - Add Galaxy/MAGMA mode switch, family filter controls, MAGMA draw path, and inspector explanation section.
- Modify: `src/tools/memory_graph_viewer_assets/index.html`
  - Add mode switch and family filter control containers.
- Modify: `src/tools/memory_graph_viewer_assets/styles.css`
  - Style mode switch, family filters, shell labels, and explanation section.
- Modify: `tests/js/memory_galaxy_smoke.test.mjs`
  - Add unit-style tests for conversion, filtering, layout, state, and inspector source checks.
- Modify or create: `tests/js/memory_galaxy_browser_regression.test.mjs`
  - Add browser regression for nonblank MAGMA View, five visible shells, multi-agent spacing, and overlay usability.

## Data Model

Use these constants in both Python and JavaScript:

```text
semantic
entity
temporal
causal
procedural
```

Suggested family colors:

```javascript
{
  semantic: "#7dd3fc",
  entity: "#a78bfa",
  temporal: "#34d399",
  causal: "#f87171",
  procedural: "#facc15",
}
```

The frontend must tolerate missing MAGMA fields by deriving or defaulting:

- missing `edge_family` -> `"semantic"`;
- missing `magma_primary_family` -> `"semantic"`;
- missing `magma_family_weights` -> `{ semantic: 0 }`;
- missing `magma_relation_counts` -> `{}`.

---

### Task 1: Export MAGMA Family Fields

**Files:**
- Modify: `tests/test_memory_graph_viewer_export.py`
- Modify: `src/tools/memory_graph_viewer_export.py`

- [ ] **Step 1: Write the failing export test**

Add this test to `tests/test_memory_graph_viewer_export.py`:

```python
def test_load_graph_exports_magma_family_fields(tmp_path):
    db = tmp_path / "memory.db"
    _make_db(db)
    with sqlite3.connect(db) as conn:
        conn.execute(
            "INSERT INTO graph_edges VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("e3", "n2", "n1", "caused_by", 3.0, "failure caused retrieval fix", "2026-01-01", "2026-01-02", 1),
        )
        conn.commit()

    with connect_readonly(db) as conn:
        graph = load_graph(conn)

    families = {item["family"]: item for item in graph["metadata"]["magma_families"]}
    assert set(families) == {"semantic", "entity", "temporal", "causal", "procedural"}
    assert families["semantic"]["edge_count"] == 1
    assert families["causal"]["edge_count"] == 1

    edges = {edge["data"]["id"]: edge["data"] for edge in graph["elements"]["edges"]}
    assert edges["e1"]["edge_family"] == "semantic"
    assert edges["e3"]["edge_family"] == "causal"

    rag = next(node for node in graph["elements"]["nodes"] if node["data"]["source_id"] == "n1")
    hermes = next(node for node in graph["elements"]["nodes"] if node["data"]["source_id"] == "n2")
    assert rag["data"]["magma_relation_counts"]["semantic"] == 1
    assert rag["data"]["magma_relation_counts"]["causal"] == 1
    assert rag["data"]["magma_family_weights"]["causal"] == 3.0
    assert rag["data"]["magma_primary_family"] == "causal"
    assert hermes["data"]["magma_primary_family"] == "causal"
```

- [ ] **Step 2: Run the export test and verify RED**

Run:

```powershell
python -m pytest tests/test_memory_graph_viewer_export.py::test_load_graph_exports_magma_family_fields -q
```

Expected: FAIL with missing `magma_families`, missing `edge_family`, or missing node MAGMA fields.

- [ ] **Step 3: Implement export constants and relation mapping**

In `src/tools/memory_graph_viewer_export.py`, add imports and constants near the existing helpers:

```python
try:
    from graph.edge_taxonomy import EDGE_FAMILIES, edge_family_for_relation
except Exception:
    EDGE_FAMILIES = ("semantic", "temporal", "causal", "entity", "procedural")

    def edge_family_for_relation(relation_type: str | None) -> str:
        return "semantic"


MAGMA_FAMILY_LABELS = {
    "semantic": "Semantic",
    "entity": "Entity",
    "temporal": "Temporal",
    "causal": "Causal",
    "procedural": "Procedural",
}

MAGMA_FAMILY_COLORS = {
    "semantic": "#7dd3fc",
    "entity": "#a78bfa",
    "temporal": "#34d399",
    "causal": "#f87171",
    "procedural": "#facc15",
}
```

- [ ] **Step 4: Add `edge_family` to exported edges**

Inside the `for row in edge_rows:` loop in `load_graph`, before `edges.append(...)`, add:

```python
        edge_family = edge_family_for_relation(row["relation_type"])
```

Then add this field to `edge["data"]`:

```python
                    "edge_family": edge_family,
```

- [ ] **Step 5: Compute node family weights and counts**

After `relation_counts_by_node` is created, add:

```python
    magma_weights_by_node: dict[str, dict[str, float]] = {
        str(node_id): {family: 0.0 for family in EDGE_FAMILIES} for node_id in node_ids
    }
    magma_counts_by_node: dict[str, dict[str, int]] = {
        str(node_id): {family: 0 for family in EDGE_FAMILIES} for node_id in node_ids
    }
```

Inside the existing `for edge in edges:` loop, after `relation = ...`, add:

```python
        family = str(data.get("edge_family") or "semantic")
        weight = float(data.get("weight") or 0.0)
```

Inside the endpoint loop, add:

```python
            if family not in magma_weights_by_node.setdefault(endpoint, {f: 0.0 for f in EDGE_FAMILIES}):
                family = "semantic"
            magma_weights_by_node[endpoint][family] += weight
            magma_counts_by_node.setdefault(endpoint, {f: 0 for f in EDGE_FAMILIES})[family] += 1
```

Add this helper near `_galaxy_layer`:

```python
def _primary_magma_family(weights: dict[str, float]) -> str:
    if not weights:
        return "semantic"
    family, score = max(weights.items(), key=lambda item: (item[1], item[0] == "semantic"))
    return family if score > 0 else "semantic"
```

Add these fields to each node `data`:

```python
                "magma_family_weights": magma_weights_by_node.get(str(row["id"]), {family: 0.0 for family in EDGE_FAMILIES}),
                "magma_primary_family": _primary_magma_family(magma_weights_by_node.get(str(row["id"]), {})),
                "magma_relation_counts": magma_counts_by_node.get(str(row["id"]), {family: 0 for family in EDGE_FAMILIES}),
```

- [ ] **Step 6: Add MAGMA metadata**

Before the `return` in `load_graph`, after `agent_galaxies`, add:

```python
    magma_families = []
    for family in EDGE_FAMILIES:
        node_count = sum(
            1 for node in nodes
            if node["data"].get("magma_primary_family") == family
        )
        edge_count = sum(
            1 for edge in edges
            if edge["data"].get("edge_family") == family
        )
        magma_families.append({
            "family": family,
            "label": MAGMA_FAMILY_LABELS.get(family, family.title()),
            "color": MAGMA_FAMILY_COLORS.get(family, "#7dd3fc"),
            "node_count": node_count,
            "edge_count": edge_count,
        })
```

Add this to metadata:

```python
            "magma_families": magma_families,
```

- [ ] **Step 7: Run export tests and verify GREEN**

Run:

```powershell
python -m pytest tests/test_memory_graph_viewer_export.py -q
```

Expected: PASS.

- [ ] **Step 8: Commit Task 1**

```powershell
git add src/tools/memory_graph_viewer_export.py tests/test_memory_graph_viewer_export.py
git commit -m "feat: export magma family metadata"
```

---

### Task 2: Preserve MAGMA Fields And Add Family Filtering

**Files:**
- Modify: `tests/js/memory_galaxy_smoke.test.mjs`
- Modify: `src/tools/memory_graph_viewer_assets/memory-galaxy-core.js`

- [ ] **Step 1: Write failing conversion and filtering tests**

In `tests/js/memory_galaxy_smoke.test.mjs`, extend the VM export block for `memory-galaxy-core.js` with:

```javascript
exports.magmaFamilyForLink = magmaFamilyForLink;
```

Add this test after the existing `convertGraphToGalaxy` tests:

```javascript
{
  const magmaGraph = {
    metadata: {
      magma_families: [
        { family: "semantic", label: "Semantic", color: "#7dd3fc", node_count: 1, edge_count: 1 },
        { family: "causal", label: "Causal", color: "#f87171", node_count: 1, edge_count: 1 },
      ],
    },
    elements: {
      nodes: [
        {
          data: {
            id: "codex:seed",
            label: "Seed",
            type: "concept",
            agent_namespace: "codex",
            magma_primary_family: "causal",
            magma_family_weights: { causal: 3, semantic: 1 },
            magma_relation_counts: { causal: 1, semantic: 1 },
            knowledge: [],
          },
        },
        {
          data: {
            id: "codex:neighbor",
            label: "Neighbor",
            type: "concept",
            agent_namespace: "codex",
            knowledge: [],
          },
        },
      ],
      edges: [
        { data: { id: "e1", source: "codex:seed", target: "codex:neighbor", relation: "caused_by", edge_family: "causal", weight: 3 } },
        { data: { id: "e2", source: "codex:seed", target: "codex:neighbor", relation: "related_to", weight: 1 } },
      ],
    },
  };
  const converted = convertGraphToGalaxy(magmaGraph);
  const seed = converted.nodes.find(node => node.id === "codex:seed");
  assert.equal(seed.magmaPrimaryFamily, "causal");
  assert.deepEqual(seed.magmaFamilyWeights, { causal: 3, semantic: 1 });
  assert.deepEqual(seed.magmaRelationCounts, { causal: 1, semantic: 1 });
  assert.equal(converted.links.find(link => link.id === "e1").edgeFamily, "causal");
  assert.equal(converted.links.find(link => link.id === "e2").edgeFamily, "semantic");

  const filtered = filterGalaxy(converted, { edgeFamilies: new Set(["causal"]) });
  assert.equal(filtered.nodes.length, 2);
  assert.equal(filtered.links.length, 1);
  assert.equal(filtered.links[0].id, "e1");
}
```

- [ ] **Step 2: Run JS smoke test and verify RED**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: FAIL because MAGMA fields and `edgeFamilies` filtering are not implemented.

- [ ] **Step 3: Add MAGMA field preservation**

In `src/tools/memory_graph_viewer_assets/memory-galaxy-core.js`, inside node conversion, add:

```javascript
      magmaPrimaryFamily: data.magma_primary_family || "semantic",
      magmaFamilyWeights: data.magma_family_weights || { semantic: 0 },
      magmaRelationCounts: data.magma_relation_counts || {},
```

Inside link conversion, add:

```javascript
    edgeFamily: magmaFamilyForLink(edge.data),
```

Add this exported helper near `filterGalaxy`:

```javascript
export function magmaFamilyForLink(data = {}) {
  const explicit = String(data.edge_family || "").trim().toLowerCase();
  if (["semantic", "entity", "temporal", "causal", "procedural"].includes(explicit)) return explicit;
  const relation = String(data.relation || data.relation_type || "").trim().toLowerCase().replaceAll("-", "_").replaceAll(" ", "_");
  if (["precedes", "succeeds", "before", "after", "during", "concurrent", "same_session"].includes(relation)) return "temporal";
  if (["causes", "caused_by", "leads_to", "because_of", "enables", "prevents", "blocks", "blocked_by", "breaks", "broke"].includes(relation)) return "causal";
  if (["mentions", "mentioned_in", "refers_to", "owns", "owned_by", "created_by", "maintained_by", "works_on", "works_with"].includes(relation)) return "entity";
  if (["fixed_by", "resolved_by", "step_after", "step_before", "workflow_depends_on", "requires_step", "implemented_by", "tested_by"].includes(relation)) return "procedural";
  return "semantic";
}
```

- [ ] **Step 4: Add family-aware link filtering**

In `filterGalaxy(galaxy, options)`, define:

```javascript
  const activeEdgeFamilies = options?.edgeFamilies instanceof Set ? options.edgeFamilies : null;
```

Update the link filter to include:

```javascript
    && (!activeEdgeFamilies || activeEdgeFamilies.has(link.edgeFamily || magmaFamilyForLink(link.raw || link)))
```

Keep node filtering unchanged so family filtering does not delete nodes.

- [ ] **Step 5: Run JS smoke test and verify GREEN**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: PASS.

- [ ] **Step 6: Commit Task 2**

```powershell
git add src/tools/memory_graph_viewer_assets/memory-galaxy-core.js tests/js/memory_galaxy_smoke.test.mjs
git commit -m "feat: preserve magma fields in galaxy data"
```

---

### Task 3: Add MAGMA Layout Helper

**Files:**
- Modify: `tests/js/memory_galaxy_smoke.test.mjs`
- Modify: `src/tools/memory_graph_viewer_assets/memory-galaxy-layouts.js`

- [ ] **Step 1: Write failing MAGMA layout tests**

In `tests/js/memory_galaxy_smoke.test.mjs`, extend the layout VM export block with:

```javascript
exports.buildMagmaGalaxyLayout = buildMagmaGalaxyLayout;
```

Add `buildMagmaGalaxyLayout` to the destructuring from `layoutsContext.exports`.

Add this test after the multi-agent overview layout tests:

```javascript
{
  const graph = {
    metadata: {
      agent_galaxies: [
        { namespace: "codex", label: "Codex", node_count: 2, edge_count: 1 },
        { namespace: "reasonix", label: "Reasonix", node_count: 2, edge_count: 1 },
      ],
      magma_families: [
        { family: "semantic", label: "Semantic", color: "#7dd3fc", node_count: 1, edge_count: 1 },
        { family: "entity", label: "Entity", color: "#a78bfa", node_count: 1, edge_count: 0 },
        { family: "temporal", label: "Temporal", color: "#34d399", node_count: 0, edge_count: 0 },
        { family: "causal", label: "Causal", color: "#f87171", node_count: 1, edge_count: 1 },
        { family: "procedural", label: "Procedural", color: "#facc15", node_count: 1, edge_count: 0 },
      ],
    },
    elements: {
      nodes: [
        { data: { id: "codex:a", label: "A", type: "concept", agent_namespace: "codex", agent_label: "Codex", magma_primary_family: "causal", knowledge: [] } },
        { data: { id: "codex:b", label: "B", type: "concept", agent_namespace: "codex", agent_label: "Codex", magma_primary_family: "semantic", knowledge: [] } },
        { data: { id: "reasonix:a", label: "A", type: "concept", agent_namespace: "reasonix", agent_label: "Reasonix", magma_primary_family: "procedural", knowledge: [] } },
        { data: { id: "reasonix:b", label: "B", type: "concept", agent_namespace: "reasonix", agent_label: "Reasonix", magma_primary_family: "entity", knowledge: [] } },
      ],
      edges: [
        { data: { id: "ce", source: "codex:a", target: "codex:b", edge_family: "causal", relation: "caused_by", weight: 2 } },
        { data: { id: "re", source: "reasonix:a", target: "reasonix:b", edge_family: "procedural", relation: "fixed_by", weight: 1 } },
      ],
    },
  };
  const layout = buildMagmaGalaxyLayout(convertGraphToGalaxy(graph), { maxNodes: 20 });
  assert.equal(layout.view, "magma");
  assert.equal(layout.nodes.filter(node => node.orbitalRole === "agent-core").length, 2);
  assert.equal(layout.familyShells.length, 10);
  assert.equal(new Set(layout.familyShells.map(shell => shell.family)).size, 5);
  assert.equal(new Set(layout.nodes.filter(node => !node.id.startsWith("agent:")).map(node => node.id)).size, 4);
  const codexCausalShell = layout.familyShells.find(shell => shell.agentNamespace === "codex" && shell.family === "causal");
  const codexCausalNode = layout.nodes.find(node => node.id === "codex:a");
  assert.ok(Math.abs(Math.hypot(codexCausalNode.x - codexCausalShell.centerX, codexCausalNode.y - codexCausalShell.centerY) - codexCausalShell.radius) < 90);
}
```

- [ ] **Step 2: Run JS smoke test and verify RED**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: FAIL because `buildMagmaGalaxyLayout` is missing.

- [ ] **Step 3: Add MAGMA family constants to layout file**

In `src/tools/memory_graph_viewer_assets/memory-galaxy-layouts.js`, add near existing constants:

```javascript
const magmaFamilies = ["semantic", "entity", "temporal", "causal", "procedural"];
const magmaFamilyLabels = {
  semantic: "Semantic",
  entity: "Entity",
  temporal: "Temporal",
  causal: "Causal",
  procedural: "Procedural",
};
const magmaFamilyColors = {
  semantic: "#7dd3fc",
  entity: "#a78bfa",
  temporal: "#34d399",
  causal: "#f87171",
  procedural: "#facc15",
};
const magmaFamilyRadii = {
  semantic: 170,
  entity: 285,
  temporal: 400,
  causal: 520,
  procedural: 640,
};
```

- [ ] **Step 4: Implement `buildMagmaGalaxyLayout`**

Add this exported function after `buildGalaxyOverviewLayout`:

```javascript
export function buildMagmaGalaxyLayout(galaxy, options = {}) {
  const nodeScale = Number(options.nodeScale || 0.48);
  const nodes = cloneGraphNodes(galaxy);
  const links = cloneLinks(galaxy.links || []);
  const agentFrames = placeAgentGalaxies(groupByAgentNamespace(nodes, galaxy.agentGalaxies));
  const outputNodes = [];
  const familyShells = [];

  for (const frame of agentFrames) {
    const agentCore = syntheticNode(`agent:${frame.namespace}`, frame.label, "router", nodeScale);
    outputNodes.push(placeNode(agentCore, frame.centerX, frame.centerY, {
      memorySystem: "router",
      orbitRole: "core",
      orbitalRole: "agent-core",
      renderRadius: Math.max(54, priorityRadiusForData(agentCore.raw || agentCore, { scale: nodeScale }) * 2.4),
      labelPriority: 1000,
      labelAnchor: { x: frame.centerX, y: frame.centerY - 92, align: "center" },
      agentNamespace: frame.namespace,
      agentLabel: frame.label,
    }));

    const grouped = groupByMagmaFamily(frame.nodes);
    for (const family of magmaFamilies) {
      const radius = magmaFamilyRadii[family] * Math.max(0.9, Math.min(1.35, Math.sqrt(Math.max(1, frame.nodes.length)) / 4));
      familyShells.push({
        family,
        label: magmaFamilyLabels[family],
        color: magmaFamilyColors[family],
        agentNamespace: frame.namespace,
        agentLabel: frame.label,
        centerX: frame.centerX,
        centerY: frame.centerY,
        radius,
        aspect: 0.62,
      });

      const familyNodes = (grouped.get(family) || []).sort(compareNodePriority);
      const tracks = splitTracks(familyNodes, radius, 48, nodeScale, 24);
      for (const [trackIndex, track] of tracks.entries()) {
        outputNodes.push(...placeOrbit(track.nodes, {
          centerX: frame.centerX,
          centerY: frame.centerY,
          radiusX: track.radius,
          radiusY: track.radius * 0.62,
          startAngle: magmaFamilyStartAngle(family) + trackIndex * 0.21,
          memorySystem: family,
          orbitRole: "magma-node",
          orbitalRole: `magma-${family}`,
          nodeScale,
          orbitSpeed: 0.012 + trackIndex * 0.002,
        }).map(node => ({
          ...node,
          magmaFamily: family,
          color: magmaFamilyColors[family],
        })));
      }
    }
  }

  const visibleIds = new Set(outputNodes.map(node => String(node.id)));
  const visibleLinks = links.filter(link => {
    const source = String(link.source?.id || link.source);
    const target = String(link.target?.id || link.target);
    return visibleIds.has(source) && visibleIds.has(target);
  });
  return {
    view: "magma",
    nodes: resolveOverlaps(outputNodes),
    links: visibleLinks,
    systems: [],
    familyShells,
    orbits: familyShells.map(shell => ({
      kind: "magma-family",
      family: shell.family,
      agentNamespace: shell.agentNamespace,
      centerX: shell.centerX,
      centerY: shell.centerY,
      radius: shell.radius,
      aspect: shell.aspect,
      color: shell.color,
    })),
    bounds: boundsFor(outputNodes, [], familyShells),
  };
}
```

- [ ] **Step 5: Add MAGMA grouping helpers**

Add these helpers near `groupBySystem`:

```javascript
function groupByMagmaFamily(nodes) {
  const grouped = new Map(magmaFamilies.map(family => [family, []]));
  for (const node of nodes) {
    const family = magmaFamilies.includes(node.magmaPrimaryFamily) ? node.magmaPrimaryFamily : "semantic";
    grouped.get(family).push(node);
  }
  return grouped;
}

function magmaFamilyStartAngle(family) {
  return {
    semantic: -Math.PI / 2,
    entity: -Math.PI / 5,
    temporal: Math.PI / 10,
    causal: Math.PI / 3,
    procedural: Math.PI / 1.4,
  }[family] || -Math.PI / 2;
}
```

- [ ] **Step 6: Run JS smoke test and verify GREEN**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: PASS.

- [ ] **Step 7: Commit Task 3**

```powershell
git add src/tools/memory_graph_viewer_assets/memory-galaxy-layouts.js tests/js/memory_galaxy_smoke.test.mjs
git commit -m "feat: add magma galaxy layout"
```

---

### Task 4: Draw MAGMA Shells And Family Edge Styles

**Files:**
- Modify: `tests/js/memory_galaxy_smoke.test.mjs`
- Modify: `src/tools/memory_graph_viewer_assets/memory-galaxy-renderer.js`

- [ ] **Step 1: Write failing renderer source and fake renderer tests**

In `tests/js/memory_galaxy_smoke.test.mjs`, add source assertions near existing renderer assertions:

```javascript
assert.match(rendererHelperSource, /function drawMagmaFamilyShells/);
assert.match(rendererHelperSource, /function edgeStyleForFamily/);
assert.match(rendererHelperSource, /layout\.familyShells/);
```

Add this fake renderer test near other fake renderer tests:

```javascript
{
  const stage = new (class {
    constructor() { this.children = []; this.scale = { set() {} }; this.position = { set() {} }; }
    addChild(...children) { this.children.push(...children); return children.at(-1); }
    removeChildren() { const out = this.children; this.children = []; return out; }
    on() {}
  })();
  class FakeContainer {
    constructor() { this.children = []; this.scale = { set() {} }; this.position = { set() {} }; }
    addChild(...children) { this.children.push(...children); return children.at(-1); }
    removeChildren() { const out = this.children; this.children = []; return out; }
    on() {}
  }
  class FakeGraphics extends FakeContainer {
    constructor() { super(); this.commands = []; }
    clear() { this.commands = []; return this; }
    circle(...args) { this.commands.push({ name: "circle", args }); return this; }
    ellipse(...args) { this.commands.push({ name: "ellipse", args }); return this; }
    stroke(...args) { this.commands.push({ name: "stroke", args }); return this; }
    fill(...args) { this.commands.push({ name: "fill", args }); return this; }
    moveTo(...args) { this.commands.push({ name: "moveTo", args }); return this; }
    lineTo(...args) { this.commands.push({ name: "lineTo", args }); return this; }
    quadraticCurveTo(...args) { this.commands.push({ name: "quadraticCurveTo", args }); return this; }
    destroy() {}
  }
  class FakeText extends FakeContainer {
    constructor({ text, style }) { super(); this.text = text; this.style = style || {}; this.anchor = { set() {} }; this.width = String(text).length * 8; this.height = 16; }
    destroy() {}
  }
  const renderer = createMemoryGalaxyRenderer({
    PIXI: { Container: FakeContainer, Graphics: FakeGraphics, Text: FakeText },
    app: { screen: { width: 1000, height: 700 }, ticker: { add() {} } },
    stage,
  });
  const magmaLayout = {
    view: "magma",
    nodes: [],
    links: [],
    systems: [],
    familyShells: [
      { family: "causal", label: "Causal", color: "#f87171", centerX: 0, centerY: 0, radius: 220, aspect: 0.62 },
      { family: "semantic", label: "Semantic", color: "#7dd3fc", centerX: 0, centerY: 0, radius: 120, aspect: 0.62 },
    ],
    bounds: { minX: -300, maxX: 300, minY: -220, maxY: 220, width: 600, height: 440 },
  };
  renderer.draw(magmaLayout, { selectedNodeId: null, hoveredNodeId: null, labelMode: "medium", animationSpeed: 0 }, {});
  const commands = stage.children.flatMap(layer => layer.children || []).flatMap(layer => layer.children || []).flatMap(child => child.commands || []);
  assert.ok(commands.some(command => command.name === "ellipse" && command.args[2] === 220));
  assert.ok(commands.some(command => command.name === "ellipse" && command.args[2] === 120));
}
```

- [ ] **Step 2: Run JS smoke test and verify RED**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: FAIL because MAGMA shell drawing functions are missing.

- [ ] **Step 3: Add family style helpers**

In `src/tools/memory_graph_viewer_assets/memory-galaxy-renderer.js`, add near style helpers:

```javascript
function edgeStyleForFamily(family) {
  return {
    semantic: { color: 0x7dd3fc, alpha: 0.26, width: 1.1 },
    entity: { color: 0xa78bfa, alpha: 0.3, width: 1.2 },
    temporal: { color: 0x34d399, alpha: 0.32, width: 1.2 },
    causal: { color: 0xf87171, alpha: 0.42, width: 1.6 },
    procedural: { color: 0xfacc15, alpha: 0.38, width: 1.5 },
  }[family] || { color: 0x7dd3fc, alpha: 0.24, width: 1.0 };
}
```

- [ ] **Step 4: Draw MAGMA family shells**

Add:

```javascript
function drawMagmaFamilyShells(layer, layout, PIXI) {
  if (!Array.isArray(layout?.familyShells)) return;
  for (const shell of layout.familyShells) {
    const color = Number.parseInt(String(shell.color || "#7dd3fc").replace("#", ""), 16);
    const guide = new PIXI.Graphics();
    guide.ellipse(
      Number(shell.centerX || 0),
      Number(shell.centerY || 0),
      Number(shell.radius || 0),
      Number(shell.radius || 0) * Number(shell.aspect || 0.62),
    );
    guide.stroke({ color, alpha: 0.22, width: 1.4 });
    layer.addChild(guide);
  }
}
```

Call it in the renderer draw path after normal orbit guides are drawn:

```javascript
drawMagmaFamilyShells(orbitLayer, layout, PIXI);
```

- [ ] **Step 5: Use family styles for MAGMA edges**

In edge drawing code, derive:

```javascript
const familyStyle = layout?.view === "magma" ? edgeStyleForFamily(link.edgeFamily || link.raw?.edge_family || "semantic") : null;
```

When stroking a MAGMA edge, use:

```javascript
const strokeColor = familyStyle?.color ?? existingColor;
const strokeAlpha = familyStyle?.alpha ?? existingAlpha;
const strokeWidth = familyStyle?.width ?? existingWidth;
```

Use the local names in the existing `stroke` call.

- [ ] **Step 6: Run JS smoke test and verify GREEN**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: PASS.

- [ ] **Step 7: Commit Task 4**

```powershell
git add src/tools/memory_graph_viewer_assets/memory-galaxy-renderer.js tests/js/memory_galaxy_smoke.test.mjs
git commit -m "feat: render magma family shells"
```

---

### Task 5: Add MAGMA View State And Controls

**Files:**
- Modify: `tests/js/memory_galaxy_smoke.test.mjs`
- Modify: `src/tools/memory_graph_viewer_assets/memory-galaxy-view-state.js`
- Modify: `src/tools/memory_graph_viewer_assets/index.html`
- Modify: `src/tools/memory_graph_viewer_assets/viewer.js`
- Modify: `src/tools/memory_graph_viewer_assets/styles.css`

- [ ] **Step 1: Write failing state tests**

In `tests/js/memory_galaxy_smoke.test.mjs`, extend the view-state VM export block with:

```javascript
exports.enterMagmaView = enterMagmaView;
exports.toggleMagmaFamily = toggleMagmaFamily;
exports.enterGalaxyView = enterGalaxyView;
```

Add these functions to the destructuring from `viewStateContext.exports`.

Add this test near other view state tests:

```javascript
{
  const magmaState = createGalaxyViewState();
  enterMagmaView(magmaState);
  assert.equal(magmaState.view, "magma");
  assert.ok(magmaState.activeMagmaFamilies.has("causal"));
  assert.ok(magmaState.activeMagmaFamilies.has("semantic"));
  toggleMagmaFamily(magmaState, "causal");
  assert.equal(magmaState.activeMagmaFamilies.has("causal"), false);
  toggleMagmaFamily(magmaState, "causal");
  assert.equal(magmaState.activeMagmaFamilies.has("causal"), true);
  enterGalaxyView(magmaState);
  assert.equal(magmaState.view, "galaxy");
}
```

- [ ] **Step 2: Write failing viewer source assertions**

Add source assertions near existing `viewerSource` assertions:

```javascript
assert.match(viewerSource, /buildMagmaGalaxyLayout/);
assert.match(viewerSource, /magmaViewToggle/);
assert.match(viewerSource, /magmaFamilyFilters/);
assert.match(viewerSource, /activeMagmaFamilies/);
```

- [ ] **Step 3: Run JS smoke test and verify RED**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: FAIL because MAGMA state helpers and viewer controls are missing.

- [ ] **Step 4: Add state helpers**

In `src/tools/memory_graph_viewer_assets/memory-galaxy-view-state.js`, ensure `createGalaxyViewState()` returns:

```javascript
    activeMagmaFamilies: new Set(["semantic", "entity", "temporal", "causal", "procedural"]),
```

Add:

```javascript
export function enterMagmaView(state) {
  state.view = "magma";
  state.selectedSystem = null;
  state.selectedPlanet = null;
  state.selectedNodeId = null;
  if (!(state.activeMagmaFamilies instanceof Set)) {
    state.activeMagmaFamilies = new Set(["semantic", "entity", "temporal", "causal", "procedural"]);
  }
  return state;
}

export function toggleMagmaFamily(state, family) {
  if (!(state.activeMagmaFamilies instanceof Set)) {
    state.activeMagmaFamilies = new Set(["semantic", "entity", "temporal", "causal", "procedural"]);
  }
  if (state.activeMagmaFamilies.has(family)) {
    state.activeMagmaFamilies.delete(family);
  } else {
    state.activeMagmaFamilies.add(family);
  }
  return state;
}
```

- [ ] **Step 5: Add HTML controls**

In `src/tools/memory_graph_viewer_assets/index.html`, add controls near existing view controls:

```html
<div class="view-toggle" aria-label="Memory view mode">
  <button id="galaxyViewToggle" class="chip chip-active" type="button">Galaxy</button>
  <button id="magmaViewToggle" class="chip" type="button">MAGMA</button>
</div>
<div id="magmaFamilyFilters" class="magma-family-filters" aria-label="MAGMA family filters">
  <button class="magma-family-chip" data-family="semantic" type="button">Semantic</button>
  <button class="magma-family-chip" data-family="entity" type="button">Entity</button>
  <button class="magma-family-chip" data-family="temporal" type="button">Temporal</button>
  <button class="magma-family-chip" data-family="causal" type="button">Causal</button>
  <button class="magma-family-chip" data-family="procedural" type="button">Procedural</button>
</div>
```

- [ ] **Step 6: Wire viewer imports and layout selection**

In `viewer.js`, import `buildMagmaGalaxyLayout` from `memory-galaxy-layouts.js`.

Import `enterMagmaView` and `toggleMagmaFamily` from `memory-galaxy-view-state.js`.

In the layout selection logic, add:

```javascript
  if (state.view === "magma") {
    return buildMagmaGalaxyLayout(filteredGraph, {
      maxNodes: currentMaxNodes(),
      nodeScale: currentNodeScale(),
    });
  }
```

When calling `filterGalaxy`, include:

```javascript
    edgeFamilies: state.view === "magma" ? state.activeMagmaFamilies : null,
```

- [ ] **Step 7: Wire mode buttons and family filter buttons**

In the viewer initialization code, add:

```javascript
document.getElementById("galaxyViewToggle")?.addEventListener("click", () => {
  enterGalaxyView(state);
  redrawCurrentLayoutState();
});

document.getElementById("magmaViewToggle")?.addEventListener("click", () => {
  enterMagmaView(state);
  redrawCurrentLayoutState();
});

document.querySelectorAll("[data-family]").forEach(button => {
  button.addEventListener("click", () => {
    toggleMagmaFamily(state, button.dataset.family);
    renderMagmaFamilyFilters();
    redrawCurrentLayoutState();
  });
});
```

Add:

```javascript
function renderMagmaFamilyFilters() {
  document.querySelectorAll("[data-family]").forEach(button => {
    const family = button.dataset.family;
    button.classList.toggle("chip-active", state.activeMagmaFamilies?.has(family));
  });
  document.getElementById("galaxyViewToggle")?.classList.toggle("chip-active", state.view !== "magma");
  document.getElementById("magmaViewToggle")?.classList.toggle("chip-active", state.view === "magma");
}
```

Call `renderMagmaFamilyFilters()` whenever the layout redraws.

- [ ] **Step 8: Add minimal styles**

In `styles.css`, add:

```css
.view-toggle,
.magma-family-filters {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.magma-family-chip {
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: rgba(15, 23, 42, 0.62);
  color: #dbeafe;
  border-radius: 999px;
  padding: 5px 9px;
  font: inherit;
  cursor: pointer;
}

.magma-family-chip.chip-active {
  border-color: rgba(125, 211, 252, 0.8);
  background: rgba(14, 116, 144, 0.34);
}
```

- [ ] **Step 9: Run JS smoke test and verify GREEN**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: PASS.

- [ ] **Step 10: Commit Task 5**

```powershell
git add src/tools/memory_graph_viewer_assets/index.html src/tools/memory_graph_viewer_assets/styles.css src/tools/memory_graph_viewer_assets/viewer.js src/tools/memory_graph_viewer_assets/memory-galaxy-view-state.js tests/js/memory_galaxy_smoke.test.mjs
git commit -m "feat: add magma view controls"
```

---

### Task 6: Add Lightweight MAGMA Explanation In Inspector

**Files:**
- Modify: `tests/js/memory_galaxy_smoke.test.mjs`
- Modify: `src/tools/memory_graph_viewer_assets/viewer-shared.js`
- Modify: `src/tools/memory_graph_viewer_assets/viewer.js`
- Modify: `src/tools/memory_graph_viewer_assets/styles.css`

- [ ] **Step 1: Write failing details rendering test**

In `tests/js/memory_galaxy_smoke.test.mjs`, add this test near existing `formatNodeDetails` tests:

```javascript
const magmaDetailHtml = formatNodeDetails({
  label: "Failure Fix",
  type: "solution",
  magma_primary_family: "causal",
  magma_family_weights: { causal: 3, procedural: 2, semantic: 1 },
  magma_relation_counts: { causal: 2, procedural: 1 },
  knowledge: [{ id: 493, type: "solution", project: "total-agent-memory", role: "structural_source", strength: 0.9, summary: "Fixed MAGMA namespace isolation" }],
});
assert.ok(magmaDetailHtml.includes("MAGMA"));
assert.ok(magmaDetailHtml.includes("causal"));
assert.ok(magmaDetailHtml.includes("493"));
```

- [ ] **Step 2: Write failing viewer source assertions**

Add:

```javascript
assert.match(viewerSource, /renderMagmaExplanation/);
assert.match(viewerSource, /edge_family/);
assert.match(viewerSource, /magma_primary_family/);
```

- [ ] **Step 3: Run JS smoke test and verify RED**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: FAIL because MAGMA explanation rendering is missing.

- [ ] **Step 4: Add node MAGMA details to shared formatter**

In `viewer-shared.js`, inside `formatNodeDetails(data)`, append this section before returning:

```javascript
  const magmaFamily = data.magma_primary_family || data.magmaPrimaryFamily;
  const magmaWeights = data.magma_family_weights || data.magmaFamilyWeights || {};
  const magmaCounts = data.magma_relation_counts || data.magmaRelationCounts || {};
  if (magmaFamily || Object.keys(magmaWeights).length || Object.keys(magmaCounts).length) {
    const weights = Object.entries(magmaWeights)
      .filter(([, value]) => Number(value || 0) > 0)
      .sort((a, b) => Number(b[1] || 0) - Number(a[1] || 0))
      .slice(0, 5)
      .map(([family, value]) => `${escapeHtml(family)} ${Number(value || 0).toFixed(1)}`)
      .join(" · ");
    sections.push(`
      <section class="detail-section magma-explanation">
        <h3>MAGMA</h3>
        <p>Primary: ${escapeHtml(magmaFamily || "semantic")}</p>
        ${weights ? `<p>${weights}</p>` : ""}
        ${Object.keys(magmaCounts).length ? `<p>Relations: ${escapeHtml(Object.entries(magmaCounts).map(([family, count]) => `${family}:${count}`).join(" · "))}</p>` : ""}
      </section>
    `);
  }
```

Use the local array or string assembly pattern already present in `formatNodeDetails`; do not introduce a second return path.

- [ ] **Step 5: Add selected edge explanation helper**

In `viewer.js`, add:

```javascript
function renderMagmaExplanation(item) {
  if (!item) return "";
  const data = item.raw || item;
  const family = data.edge_family || item.edgeFamily || data.magma_primary_family || item.magmaPrimaryFamily || "semantic";
  const relation = data.relation || data.relation_type || "related";
  const weight = Number(data.weight || item.weight || 0);
  const context = data.context || "";
  return `
    <section class="detail-section magma-explanation">
      <h3>MAGMA</h3>
      <p>Family: ${escapeHtml(family)}</p>
      <p>Relation: ${escapeHtml(relation)}</p>
      ${weight ? `<p>Weight: ${weight.toFixed(2)}</p>` : ""}
      ${context ? `<p>${escapeHtml(context)}</p>` : ""}
    </section>
  `;
}
```

Call this helper in the inspector path for selected node or selected edge. For nodes, pass the selected node; for edges, pass the selected link.

- [ ] **Step 6: Add styles**

In `styles.css`, add:

```css
.magma-explanation {
  border-left: 2px solid rgba(248, 113, 113, 0.72);
  padding-left: 10px;
}
```

- [ ] **Step 7: Run JS smoke test and verify GREEN**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: PASS.

- [ ] **Step 8: Commit Task 6**

```powershell
git add src/tools/memory_graph_viewer_assets/viewer-shared.js src/tools/memory_graph_viewer_assets/viewer.js src/tools/memory_graph_viewer_assets/styles.css tests/js/memory_galaxy_smoke.test.mjs
git commit -m "feat: explain magma relations in inspector"
```

---

### Task 7: Browser Regression For MAGMA View

**Files:**
- Modify or create: `tests/js/memory_galaxy_browser_regression.test.mjs`

- [ ] **Step 1: Inspect current browser regression entry point**

Run:

```powershell
if (Test-Path tests/js/memory_galaxy_browser_regression.test.mjs) { Get-Content -Raw tests/js/memory_galaxy_browser_regression.test.mjs } else { Write-Output "missing" }
```

Expected: existing browser regression content or `missing`.

- [ ] **Step 2: Add MAGMA browser assertions**

If the file exists, add a MAGMA test case using its existing server/page helper pattern. If it is missing, create `tests/js/memory_galaxy_browser_regression.test.mjs` with the same dependency style used by other JS browser tests in this repository.

The test must perform these actions:

```javascript
await page.goto(viewerUrl);
await page.waitForSelector("#galaxy2d canvas");
await page.click("#magmaViewToggle");
await page.waitForFunction(() => {
  const canvas = document.querySelector("#galaxy2d canvas");
  return canvas && canvas.width > 0 && canvas.height > 0;
});
const pixelStats = await page.evaluate(() => {
  const canvas = document.querySelector("#galaxy2d canvas");
  const ctx = canvas.getContext("2d");
  const image = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
  let nonBlank = 0;
  for (let i = 0; i < image.length; i += 4) {
    if (image[i] || image[i + 1] || image[i + 2]) nonBlank += 1;
  }
  return { nonBlank, width: canvas.width, height: canvas.height };
});
assert.ok(pixelStats.nonBlank > 500);
const filterCount = await page.locator("[data-family]").count();
assert.equal(filterCount, 5);
await page.click('[data-family="causal"]');
await page.click('[data-family="causal"]');
```

- [ ] **Step 3: Run browser regression and verify RED or GREEN**

Run:

```powershell
node tests/js/memory_galaxy_browser_regression.test.mjs
```

Expected before Task 5 implementation: FAIL because `#magmaViewToggle` does not exist. Expected after Task 5 and Task 6: PASS.

- [ ] **Step 4: Fix only browser-test integration issues**

If the test fails because the browser test fixture cannot locate the exported viewer path, adapt the test to the repository's existing export helper pattern. Do not change production code in this task unless a real MAGMA rendering bug is exposed.

- [ ] **Step 5: Commit Task 7**

```powershell
git add tests/js/memory_galaxy_browser_regression.test.mjs
git commit -m "test: cover magma view browser rendering"
```

---

### Task 8: Full Verification

**Files:**
- No planned source edits.

- [ ] **Step 1: Run focused Python tests**

Run:

```powershell
python -m pytest tests/test_memory_graph_viewer_export.py tests/test_agent_namespace_recall.py tests/test_query_router.py tests/test_graph_expander_family.py -q
```

Expected: PASS. Warnings about FastEmbed model pooling are acceptable if no tests fail.

- [ ] **Step 2: Run JS smoke test**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: PASS.

- [ ] **Step 3: Run browser regression**

Run:

```powershell
node tests/js/memory_galaxy_browser_regression.test.mjs
```

Expected: PASS with nonblank MAGMA canvas and five family filter controls.

- [ ] **Step 4: Run export manually on the live DB**

Run:

```powershell
python -m src.tools.memory_graph_viewer_export --db C:\Users\Administrator\.tam\memory.db --output tmp\magma-viewer-check --max-nodes 120 --max-edges 300
```

Expected: JSON metadata includes `magma_families`, `agent_galaxies`, and nonzero `node_count`.

- [ ] **Step 5: Inspect generated graph JSON**

Run:

```powershell
@'
import json
from pathlib import Path
graph=json.loads(Path("tmp/magma-viewer-check/graph.json").read_text(encoding="utf-8"))
print(graph["metadata"].get("magma_families"))
node=next(iter(graph["elements"]["nodes"]), None)
edge=next(iter(graph["elements"]["edges"]), None)
print(node["data"].get("magma_primary_family") if node else None)
print(edge["data"].get("edge_family") if edge else None)
'@ | python -
```

Expected: first print is a list of five family metadata records; second print is a family name; third print is a family name when edges exist.

- [ ] **Step 6: Run CodeGraph affected check**

Run:

```powershell
& 'C:\Users\Administrator\AppData\Local\codegraph\current\bin\codegraph.cmd' affected --path C:\Users\Administrator\total-agent-memory src\tools\memory_graph_viewer_export.py src\tools\memory_graph_viewer_assets\memory-galaxy-core.js src\tools\memory_graph_viewer_assets\memory-galaxy-layouts.js src\tools\memory_graph_viewer_assets\memory-galaxy-renderer.js src\tools\memory_graph_viewer_assets\viewer.js
```

Expected: command completes and reports affected files/tests. Run any additional tests it reports.

- [ ] **Step 7: Record verification result**

If all verification passes, save a memory record:

```text
type=solution
project=total-agent-memory
tags=magma,visualization,memory-galaxy,verification
content=Implemented MAGMA View as a second Memory Galaxy projection with export fields, family shells, filters, and lightweight explanations.
context=Include test commands and any browser regression notes.
```

## Self-Review

- Spec coverage: Tasks cover export fields, frontend conversion, MAGMA layout, family filtering, renderer shells, view state, controls, inspector explanation, browser regression, and full verification.
- Placeholder scan: no placeholder markers or unspecified implementation steps remain.
- Type consistency: the plan consistently uses `edge_family`, `magma_family_weights`, `magma_primary_family`, `magma_relation_counts`, `metadata.magma_families`, `edgeFamilies`, `buildMagmaGalaxyLayout`, and `view: "magma"`.
- Scope check: full router debug diagnostics are excluded, matching the approved lightweight overlay design.

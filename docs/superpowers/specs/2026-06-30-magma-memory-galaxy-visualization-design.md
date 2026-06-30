# MAGMA Memory Galaxy Visualization Design

## Goal

Add a dedicated MAGMA View to the existing Memory Galaxy viewer so the upgraded MAGMA-style memory graph can be understood visually without replacing the current multi-agent galaxy model.

The default Galaxy View remains the main long-term memory browsing surface. MAGMA View is a second structural projection over the same graph data, showing how each agent's memory is organized across semantic, temporal, causal, entity, and procedural relationship families.

## Current Context

Total Agent Memory now has two related graph concepts:

- Agent namespace isolation: each durable memory belongs to an `agent_namespace`, such as `codex` or `reasonix`.
- MAGMA-style graph families: `graph_edges.relation_type` is mapped into `semantic`, `temporal`, `causal`, `entity`, or `procedural` via `graph.edge_taxonomy`.

The current viewer already exports namespace-qualified nodes and renders multiple agent galaxies in the same canvas. The MAGMA visualization should build on that export instead of introducing a separate graph source.

## Design Choice

Use a dual-mode viewer:

- `Galaxy View`: current memory-system galaxy using router, rule, skill, project, knowledge, event, source, and related systems.
- `MAGMA View`: a dedicated mode that rearranges the same nodes into five MAGMA family orbit shells inside each agent galaxy.

This keeps the existing visual model stable while giving MAGMA enough structural space to be recognizable.

## Data Mapping

The export format remains compatible with the current `elements.nodes` and `elements.edges` shape. MAGMA data is added as derived fields.

For each edge:

- `edge_family`: derived from `relation_type` with `edge_family_for_relation`.
- `relation_type`: the original relation label.
- `weight`: the graph edge weight.
- `context`: existing edge context.
- `source_id` and `target_id`: raw graph node IDs for traceability.

For each node:

- `magma_family_weights`: weighted relation totals by family.
- `magma_primary_family`: the strongest family for placement.
- `magma_relation_counts`: relation counts by family.

For metadata:

- `metadata.magma_families`: labels, colors, node counts, and edge counts for all five families.

Nodes with no relation evidence default to `magma_primary_family = "semantic"` so they remain visible.

`agent_namespace` stays the top-level isolation boundary. MAGMA fields do not override namespace filtering or grouping.

## MAGMA View Layout

Each agent galaxy keeps one central agent core, labeled for the namespace, such as `Codex` or `Reasonix`.

Around that center, MAGMA View draws five relationship shells:

- `semantic`
- `entity`
- `temporal`
- `causal`
- `procedural`

Nodes are unique. A memory node appears once, positioned in the shell for its `magma_primary_family`. Secondary family participation is shown through subtle markers and edge highlighting rather than duplicated node projections.

Placement uses three inputs:

- `magma_primary_family` chooses the shell.
- `memorySystem` helps cluster angle within the shell.
- `importance`, `activity`, and `mention_count` influence radius and size.

Multiple agents render as separate MAGMA shell systems in the same canvas, preserving the spatial separation already used by multi-agent galaxy layout.

## Interaction Model

The viewer adds a `Galaxy / MAGMA` mode switch.

MAGMA View includes family filters:

- semantic
- temporal
- causal
- entity
- procedural

All families are visible by default. Disabling a family hides or fades that family's edges and lowers the emphasis of nodes that depend only on that family. Nodes are not removed by ordinary family filtering, which keeps navigation stable.

Clicking a family shell focuses that family by emphasizing its edges and related nodes.

Existing pan, zoom, minimap, selection, and inspector behavior remain available.

## Lightweight Explanation Overlay

MAGMA View uses a lightweight explanation section in the existing inspector rather than a separate debug panel.

When a node is selected, show:

- primary MAGMA family;
- family weight summary;
- strongest MAGMA relations touching the node;
- linked memory IDs where available.

When an edge is selected, show:

- relation type;
- edge family;
- weight;
- context;
- source and target labels;
- source and target raw IDs.

When entered from a recall or search result, the explanation shows the path that made the result relevant:

```text
seed memory -> graph edge -> candidate memory
```

The path explanation includes family, relation type, weight, context, and memory IDs.

The first version intentionally excludes full router diagnostics, tier scores, dropped candidates, and query classification internals. Those belong in a future debug mode if needed.

## Component Boundaries

Python export layer:

- Derive `edge_family` from `relation_type`.
- Compute node family weights and primary family.
- Emit `metadata.magma_families`.
- Preserve namespace-qualified node IDs and raw source IDs.

Frontend data conversion:

- Preserve MAGMA fields in `convertGraphToGalaxy`.
- Keep existing Galaxy View behavior unchanged.

Frontend layout:

- Add `buildMagmaGalaxyLayout(galaxy, options)`.
- Keep it separate from the current overview galaxy layout.
- Add family shell descriptors to the returned layout.

Filtering:

- Extend filtering to support `edgeFamilies`.
- Family filtering affects edge visibility and node emphasis, not node existence.

Renderer:

- Draw MAGMA family shells.
- Style edges by family.
- Keep labels collision-aware.

Viewer state:

- Add `view: "magma"` alongside existing galaxy, solar, and planet states.
- Preserve back navigation between MAGMA selection and default galaxy views.

## Error Handling And Fallbacks

If `edge_family` is missing, the frontend derives or defaults it to `semantic`.

If `magma_family_weights` is missing, the frontend treats the node as semantic-only.

If a database lacks namespace fields, export treats records as `codex`, matching the current backward-compatible namespace behavior.

If all MAGMA edges are filtered out, the MAGMA View still shows the nodes and family shells with an empty-edge state rather than a blank canvas.

## Testing

Python tests:

- export maps known `relation_type` values to `edge_family`;
- export emits `magma_family_weights`, `magma_primary_family`, and `metadata.magma_families`;
- namespace-qualified IDs remain stable;
- old databases without namespace or MAGMA fields still export usable MAGMA defaults.

JavaScript tests:

- MAGMA layout creates five family shells;
- nodes remain unique across family filters;
- family filtering hides or fades edges without deleting nodes;
- multi-agent MAGMA layouts keep agent galaxies separated;
- inspector can render node and edge MAGMA explanation fields.

Browser regression:

- MAGMA View renders a nonblank canvas;
- five shells are visible;
- multiple agent galaxies do not overlap;
- explanation overlay does not obscure the selected node or primary canvas controls.

Recall/path integration tests:

- path explanation uses namespace-safe graph expansion;
- path explanation includes family, relation type, weight, context, and memory IDs.

## Rollout

1. Extend graph export with MAGMA family fields.
2. Preserve MAGMA fields through frontend conversion.
3. Add MAGMA layout helper and tests.
4. Add view switch and family filters.
5. Add lightweight explanation section to the inspector.
6. Add browser regression for MAGMA View.

## Self-Review

- Placeholder scan: no placeholder markers remain.
- Internal consistency: MAGMA View is consistently defined as a second projection over the same namespace-aware graph export.
- Scope check: this is one focused visualization feature; debug-mode internals are explicitly deferred.
- Ambiguity check: nodes are unique, family filters affect edges/emphasis rather than deleting nodes, and namespace remains the top-level boundary.

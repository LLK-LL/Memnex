# Agent Namespaced Memory Galaxies Design

## Goal

Add first-class agent namespaces to Total Agent Memory so Codex, Reasonix, and future agents save, retrieve, graph, and visualize their memories in isolated frameworks by default, while still allowing explicit cross-agent access when requested.

## Current Context

CodeGraph reports the repository index is healthy and current: 384 files, 10,193 nodes, and 25,447 edges. The relevant implementation surface is:

- `src/server.py`: `Store.save_knowledge` and `Store._save_knowledge_impl` are the central save path.
- `migrations/028_agent_lineage.sql`: existing `agent_id` and `parent_agent_id` lineage support.
- `src/tools/memory_graph_viewer_export.py`: graph export for the Memory Galaxy viewer.
- `src/tools/memory_graph_viewer_server.py`: HTTP serving and graph API.
- `src/tools/memory_graph_viewer_assets/*`: current 2D/3D Memory Galaxy UI.
- `tests/test_memory_graph_viewer_export.py`, `tests/test_memory_graph_viewer_server.py`, and `tests/js/memory_galaxy_smoke.test.mjs`: current regression coverage.

Memory recall found these related records:

- `428`, `429`, `437`, `438`, `441`, `444`: Memory Galaxy implementation and redesign history.
- `467`: Reasonix integration with Total Agent Memory MCP, tagged `reasonix`, `mcp`, `testing`, `integration`, `configuration`.

## Terminology

- `agent_namespace`: the owning agent memory framework. Examples: `codex`, `reasonix`, `claude`, `cursor`, `jarvis`, `custom:<name>`.
- `agent_id`: a specific subagent or runtime ID, already used for lineage.
- `parent_agent_id`: the parent dispatcher for lineage.
- `agent galaxy`: the visual galaxy containing one agent namespace's memory graph.

`agent_namespace` is not a replacement for `agent_id`. Namespace controls storage and retrieval isolation. `agent_id` and `parent_agent_id` continue to describe subagent lineage inside a namespace.

## Recommended Architecture

Use one physical SQLite database and one shared memory system, but add namespace ownership to every durable and derived memory layer. This preserves existing storage, migration, evaluation, and visualization infrastructure while making agent isolation explicit.

The default namespace is `codex` for existing Codex-originated writes. Reasonix-originated writes must use `reasonix`. Future agents receive their own namespace instead of sharing Codex records.

Default recall and graph tools only search the caller's namespace. Cross-agent search is allowed only when the user explicitly asks for it, through parameters such as `agent_namespace`, `agent_namespaces`, or `scope="all_agents"`.

## Storage Design

Add a migration such as `029_agent_namespace.sql`.

The `knowledge` table should gain:

```sql
agent_namespace TEXT NOT NULL DEFAULT 'codex'
```

Indexes should support the hot paths:

```sql
CREATE INDEX IF NOT EXISTS idx_knowledge_agent_namespace
ON knowledge(agent_namespace);

CREATE INDEX IF NOT EXISTS idx_knowledge_project_agent_namespace
ON knowledge(project, agent_namespace);

CREATE INDEX IF NOT EXISTS idx_knowledge_type_agent_namespace
ON knowledge(type, agent_namespace);
```

Derived tables that can cheaply store ownership should also carry `agent_namespace`. Where duplication would be risky, they may derive namespace by joining back to `knowledge`. The implementation plan should inspect each table before deciding:

- FTS index rows
- vector / embedding rows
- knowledge representations
- concept and graph node tables
- triple extraction rows
- episode links
- enrichment queues
- summary or recall caches

The rule is simple: no derived layer may return cross-agent data unless the original query explicitly requested cross-agent scope.

## Save Path

`memory_save`, `memory_save_fast`, `memory_episode_save`, structured decision save, observation save, and session extraction writes should accept an optional `agent_namespace`.

Resolution order:

1. Explicit tool parameter `agent_namespace`.
2. Trusted client/session metadata, if available.
3. Environment variable such as `TAM_AGENT_NAMESPACE`.
4. Fallback `codex`.

Reasonix should be configured to pass `agent_namespace="reasonix"` on all writes. If its MCP client cannot pass the parameter directly, configure its launch environment with `TAM_AGENT_NAMESPACE=reasonix`. If neither is possible, add a small compatibility shim in the server that recognizes Reasonix client metadata.

All tags remain useful for filtering and discovery, but tags are not the isolation boundary.

## Existing Reasonix Migration

Existing mixed records should be backfilled to `agent_namespace='reasonix'` when either condition is true:

- `tags` contains `reasonix`.
- `content`, `context`, or structured metadata clearly indicates Reasonix origin, for example phrases such as `Reasonix`, `reasonix`, or a known Reasonix integration/session marker.

The migration should be previewable before applying:

```text
matched_by_tag
matched_by_content
matched_by_context
already_reasonix
will_update
ambiguous
```

Ambiguous records should remain `codex` unless the evidence is clear. The migration should write a small audit report with updated IDs and match reasons, and it should be idempotent.

## Recall Policy

Default behavior:

- Codex recalls only `agent_namespace='codex'`.
- Reasonix recalls only `agent_namespace='reasonix'`.
- Future agents recall only their own namespace.

Explicit cross-agent behavior:

- A user command such as "search Reasonix memories" may set `agent_namespaces=['reasonix']`.
- A user command such as "search across all agents" may set `scope='all_agents'`.
- Cross-agent results must include their namespace in metadata and display labels.

Default recall must not leak Reasonix results into Codex queries after the migration.

## Graph Policy

Each namespace owns its own graph. Concepts with the same label in different namespaces are distinct nodes unless explicitly bridged.

Graph node IDs in export should be namespace-stable, for example:

```text
codex:concept:memory_recall
reasonix:concept:memory_recall
```

Cross-agent bridge edges are allowed only as explicit derived relationships and should be hidden by default in the viewer. When shown, they should use a distinct visual style.

## Memory Galaxy Visualization

Do not add another top-level view layer.

The existing galaxy view should directly render multiple agent galaxies in the same canvas. Each agent namespace becomes one complete galaxy that uses the current Memory Galaxy architecture internally:

- core
- active
- knowledge
- episode
- external
- existing solar-system drill-down behavior

The central star label for each galaxy should be the agent name, such as `Codex` or `Reasonix`. It should no longer use the generic `Router` / `Router Core` naming for the visual center.

Layout requirements:

- Multiple agent galaxies should be spatially separated in the same scene.
- The center star label must be large and visually dominant enough to identify the owning agent at a glance.
- Labels must not overlap the center star, other labels, system nodes, or neighboring galaxies.
- The layout should avoid excessive empty space between galaxies.
- If labels would collide, the layout should use deterministic placement, label hiding, or scale adjustment rather than allowing overlap.
- Existing zoom, pan, minimap, hover, and solar drill-down behavior should remain intact.

The viewer should default to showing the current agent's galaxy clearly, while still making other available agent galaxies visible in the same galaxy scene when graph data includes them.

## Export Shape

Graph export should include namespace metadata:

```json
{
  "metadata": {
    "agent_galaxies": [
      {
        "namespace": "codex",
        "label": "Codex",
        "node_count": 1200,
        "edge_count": 2400
      },
      {
        "namespace": "reasonix",
        "label": "Reasonix",
        "node_count": 80,
        "edge_count": 160
      }
    ],
    "default_agent_namespace": "codex"
  },
  "nodes": [
    {
      "data": {
        "id": "codex:project:total-agent-memory",
        "agent_namespace": "codex",
        "agent_label": "Codex",
        "galaxy_layer": "core"
      }
    }
  ]
}
```

The frontend should treat `agent_namespace` as the top-level galaxy grouping key.

## Tests

Python tests should cover:

- saving without namespace defaults to `codex`;
- saving with `agent_namespace='reasonix'` persists the namespace;
- default recall from Codex excludes Reasonix records;
- explicit Reasonix recall returns Reasonix records;
- explicit all-agent recall returns both and labels namespaces;
- graph export groups nodes by namespace;
- Reasonix backfill detects tag and content matches and leaves ambiguous records unchanged.

JavaScript tests should cover:

- converting graph data into multiple agent galaxies;
- center labels use agent names;
- center label sizing and collision guards;
- no extra top-level view mode is required;
- existing solar drill-down still works inside each agent galaxy.

Browser regression should verify at least two agent galaxies render in one scene, labels are readable, and there is no obvious overlap on desktop and mobile viewports.

## Rollout

1. Add schema migration and tests.
2. Add namespace resolution to save tools.
3. Add namespace filters to recall/search tools.
4. Add Reasonix backfill preview and apply commands.
5. Add graph namespace propagation.
6. Update galaxy export and frontend layout.
7. Run Python, JS, and browser regression tests.
8. Configure Reasonix to pass `agent_namespace='reasonix'` or `TAM_AGENT_NAMESPACE=reasonix`.

## Open Operational Point

Reasonix may need one configuration change so every future write carries `agent_namespace='reasonix'`. If the Reasonix MCP client can pass the new field directly, use that. If it cannot, set `TAM_AGENT_NAMESPACE=reasonix` in Reasonix's MCP server environment. If neither route is available, implement a server-side client detection fallback and document it as a compatibility path.

## Self-Review

- Placeholder scan: no placeholders remain.
- Internal consistency: namespace isolation is used consistently for save, recall, graph, and visualization.
- Scope check: this is one coherent feature because schema, recall, graph, and viewer all depend on the same namespace contract.
- Ambiguity check: Reasonix migration is intentionally conservative; ambiguous records stay in `codex` until explicitly identified.

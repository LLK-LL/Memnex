# Graph Expand Routing Design

## Goal

Change graph expansion from a global recall-wide behavior into a routed behavior:
ordinary semantic recall should not automatically pull graph neighbors, while
relational, causal, temporal, and entity-oriented queries can still use the
Family graph automatically.

## Context

`MEMORY_GRAPH_EXPAND=1` currently acts as a broad server-side gate in
`src/server.py`. When enabled, every `memory_recall` path with at least one
ranked result can append one-hop graph neighbors. This makes graph expansion
available, but it also lets unrelated graph neighbors compete with ordinary RAG
hits for semantic queries.

The current query router already classifies queries and infers graph families in
`src/query_router.py`:

- `kind == "relational"` for relationship-style queries.
- `graph_families` can include `temporal`, `causal`, `procedural`, `entity`, or
  `semantic`.
- The graph expander already accepts `edge_families`, so the Family graph can be
  used as a real filter rather than only metadata.

The desired behavior is not keyword-triggered by the word "graph". It is
intent-triggered by query type, with an explicit API override for callers that
already know they want graph context.

## Approved Product Semantics

`expand_context=true` is a manual override. If a caller explicitly passes it,
graph expansion must run even for a normal semantic query.

When `expand_context` is absent or false, automatic graph expansion is allowed
only if both conditions are true:

1. `MEMORY_GRAPH_EXPAND` is enabled.
2. The query classification indicates relationship-style reasoning:
   - `router_classification.kind == "relational"`, or
   - `router_classification.graph_families` contains `entity`, or
   - `router_classification.graph_families` contains `causal`, or
   - `router_classification.graph_families` contains `temporal`.

Pure semantic queries should not auto-expand. Pure procedural queries should not
auto-expand unless they also carry a causal, temporal, entity, or relational
signal. For example, "how do I install X" should stay ordinary recall, while
"why did install fail and what fixed it" can auto-expand because it is causal.

## Architecture

Add a small server-side decision helper near the recall pipeline in
`src/server.py`, for example `_should_apply_graph_expand(...)`. The helper owns
the interaction between:

- server capability: `HAS_GRAPH_EXPAND`;
- explicit caller intent: `expand_context=true`;
- environment gate: `MEMORY_GRAPH_EXPAND=1`;
- query-router classification: `kind`, `signals`, and `graph_families`;
- available ranked seed results.

This keeps `query_router.py` responsible for query classification only. It does
not make the router depend on MCP argument semantics or environment variables.

## Data Flow

1. The recall pipeline builds the normal ranked candidate list.
2. The smart query router classifies the query and may inject relational-router
   hits for explicitly relational queries.
3. The graph-expansion decision helper evaluates:
   - no ranked seeds: skip;
   - explicit `expand_context=true`: apply graph expansion;
   - otherwise, if `MEMORY_GRAPH_EXPAND` is disabled: skip;
   - otherwise, apply only for relational, entity, causal, or temporal query
     families.
4. If graph expansion runs, pass the selected families into `_graph_expand` via
   `edge_families=...`.
5. Fetch graph neighbor records, score them against existing primary results,
   sort, and truncate as today.
6. Add metadata to the response explaining whether and why graph expansion ran.

## Family Filtering

Automatic graph expansion should use query families as filters. The expected
family behavior is:

- Relational/entity query: include `entity`.
- Causal query: include `causal`.
- Temporal query: include `temporal`.
- Causal procedural query: include both `causal` and `procedural` if the router
  inferred both.
- Pure semantic query: skip automatic expansion.

For explicit `expand_context=true`, preserve the broad current behavior unless
the caller also provides a future explicit family filter. This keeps manual
debugging and existing integration tests compatible.

## Observability

Return graph-expansion metadata alongside existing routing metadata:

```json
{
  "graph_expand_applied": true,
  "graph_expand_reason": "explicit_expand_context",
  "graph_expand_families": ["causal", "procedural"]
}
```

Recommended reason values:

- `explicit_expand_context`
- `auto_relational`
- `auto_entity`
- `auto_causal`
- `auto_temporal`
- `skipped_no_seed_results`
- `skipped_disabled`
- `skipped_semantic`
- `skipped_procedural_only`

These fields make monitoring and audit scripts able to distinguish "graph
expansion is available" from "graph expansion actually influenced this recall".

## Error Handling

Graph expansion remains best-effort. If classification or graph expansion throws
an exception, the recall pipeline should keep the original ranked results and log
the failure, matching the current behavior.

The decision helper should treat a missing router classification as semantic
unless `expand_context=true` is present. This avoids broad expansion when the
router is unavailable, while preserving explicit caller control.

## Tests

Update tests around recall graph expansion:

- Semantic query with `MEMORY_GRAPH_EXPAND=1` and no explicit
  `expand_context` should not call `_graph_expand`.
- Temporal query with `MEMORY_GRAPH_EXPAND=1` should call `_graph_expand` with a
  temporal family filter.
- Causal query with `MEMORY_GRAPH_EXPAND=1` should call `_graph_expand` with a
  causal family filter.
- Semantic query with `expand_context=true` should call `_graph_expand` even
  though automatic expansion would skip it.
- Existing ranking/budget tests that assume global expansion should either use a
  relational/causal/temporal query or pass `expand_context=true`.

## Non-Goals

- Do not change the storage schema.
- Do not replace the existing smart query router.
- Do not make the literal word "graph" the trigger for automatic graph
  expansion.
- Do not enable graph expansion for every procedural query by default.
- Do not implement a new LLM-based router.

## Success Criteria

- `MEMORY_GRAPH_EXPAND=1` no longer makes every recall query graph-expanded.
- Natural relationship, cause, and timeline questions still receive graph
  expansion automatically.
- Explicit `expand_context=true` remains a reliable manual override.
- Returned metadata explains the graph expansion decision.
- Tests cover semantic skip, causal auto-expand, temporal auto-expand, and
  explicit override.

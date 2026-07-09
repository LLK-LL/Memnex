# Graph Expand Routing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make graph expansion automatic only for relational/entity, causal, or temporal recall queries while preserving `expand_context=true` as a manual override.

**Architecture:** Keep query classification in `src/query_router.py` and put the graph-expansion execution decision in `src/server.py`, close to the recall pipeline. Add a pure decision helper for testability, pass `edge_families` into `_graph_expand` for automatic routes, and expose response metadata that explains the decision.

**Tech Stack:** Python, SQLite-backed Total Agent Memory store, existing `query_router.py`, existing `graph_expander.py`, pytest.

---

## File Structure

- Modify `src/server.py`
  - Add pure graph-expansion decision helpers near the optional graph-expander import section or before `class Recall`.
  - Add `expand_context` and `expand_budget` parameters to `Recall.search(...)` and `Recall._search_impl(...)`.
  - Replace the current broad Stage 6.5 `MEMORY_GRAPH_EXPAND=1` gate with the routed decision helper.
  - Pass `edge_families` to `_graph_expand(...)` for automatic expansion.
  - Add `graph_expand_applied`, `graph_expand_reason`, and `graph_expand_families` to recall results.
  - Pass MCP `expand_context` and `expand_budget` into `recall.search(...)`.
  - Remove the old MCP-level `ContextExpander` post-processing block so explicit expansion has one canonical path.
  - Include graph expansion inputs in both cache layers so routed and non-routed recall results do not share stale cache entries.
- Modify `tests/test_recall_modes.py`
  - Add unit coverage for the decision helper.
  - Add recall-pipeline coverage for semantic skip, temporal auto-expand, causal auto-expand, and explicit override.
  - Update the existing graph budget/ranking test to use explicit `expand_context=True`.
- Keep `tests/test_query_router.py` unchanged unless the existing classifier behavior fails; it already covers temporal and causal family inference.
- Keep `tests/test_integration_expand_context.py` schema coverage, but update only if the removed old post-processing path creates a stale assertion.

---

### Task 1: Add a Pure Graph Expansion Decision Helper

**Files:**
- Modify: `src/server.py`
- Test: `tests/test_recall_modes.py`

- [ ] **Step 1: Write failing helper tests**

Append these tests near the existing graph expansion test in `tests/test_recall_modes.py`:

```python
from types import SimpleNamespace


def test_graph_expand_decision_skips_semantic_auto(monkeypatch):
    import server

    monkeypatch.setattr(server, "HAS_GRAPH_EXPAND", True)
    monkeypatch.setenv("MEMORY_GRAPH_EXPAND", "1")

    decision = server._graph_expand_decision(
        has_graph_expand=server.HAS_GRAPH_EXPAND,
        ranked_count=1,
        explicit_expand_context=False,
        router_classification=SimpleNamespace(
            kind="semantic",
            graph_families=["semantic"],
        ),
    )

    assert decision.apply is False
    assert decision.reason == "skipped_semantic"
    assert decision.edge_families == []
    assert decision.graph_families == ["semantic"]


def test_graph_expand_decision_explicit_override_ignores_env(monkeypatch):
    import server

    monkeypatch.setattr(server, "HAS_GRAPH_EXPAND", True)
    monkeypatch.setenv("MEMORY_GRAPH_EXPAND", "0")

    decision = server._graph_expand_decision(
        has_graph_expand=server.HAS_GRAPH_EXPAND,
        ranked_count=1,
        explicit_expand_context=True,
        router_classification=SimpleNamespace(
            kind="semantic",
            graph_families=["semantic"],
        ),
    )

    assert decision.apply is True
    assert decision.reason == "explicit_expand_context"
    assert decision.edge_families is None
    assert decision.graph_families == ["semantic"]


def test_graph_expand_decision_allows_temporal_auto(monkeypatch):
    import server

    monkeypatch.setattr(server, "HAS_GRAPH_EXPAND", True)
    monkeypatch.setenv("MEMORY_GRAPH_EXPAND", "1")

    decision = server._graph_expand_decision(
        has_graph_expand=server.HAS_GRAPH_EXPAND,
        ranked_count=1,
        explicit_expand_context=False,
        router_classification=SimpleNamespace(
            kind="semantic",
            graph_families=["temporal"],
        ),
    )

    assert decision.apply is True
    assert decision.reason == "auto_temporal"
    assert decision.edge_families == ["temporal"]


def test_graph_expand_decision_skips_procedural_only(monkeypatch):
    import server

    monkeypatch.setattr(server, "HAS_GRAPH_EXPAND", True)
    monkeypatch.setenv("MEMORY_GRAPH_EXPAND", "1")

    decision = server._graph_expand_decision(
        has_graph_expand=server.HAS_GRAPH_EXPAND,
        ranked_count=1,
        explicit_expand_context=False,
        router_classification=SimpleNamespace(
            kind="semantic",
            graph_families=["procedural"],
        ),
    )

    assert decision.apply is False
    assert decision.reason == "skipped_procedural_only"
    assert decision.edge_families == []
```

- [ ] **Step 2: Run helper tests and verify they fail**

Run:

```powershell
python -m pytest tests/test_recall_modes.py::test_graph_expand_decision_skips_semantic_auto tests/test_recall_modes.py::test_graph_expand_decision_explicit_override_ignores_env tests/test_recall_modes.py::test_graph_expand_decision_allows_temporal_auto tests/test_recall_modes.py::test_graph_expand_decision_skips_procedural_only -q
```

Expected: all four tests fail with `AttributeError: module 'server' has no attribute '_graph_expand_decision'`.

- [ ] **Step 3: Implement the decision helper**

In `src/server.py`, add this near the optional `_graph_expand` import block, before `class Recall`:

```python
from dataclasses import dataclass


_AUTO_GRAPH_EXPAND_FAMILIES = ("entity", "causal", "temporal")


@dataclass(frozen=True)
class _GraphExpandDecision:
    apply: bool
    reason: str
    graph_families: list[str]
    edge_families: list[str] | None


def _env_truthy(name: str, default: str = "0") -> bool:
    return os.environ.get(name, default).strip().lower() in (
        "1", "true", "yes", "on",
    )


def _classification_graph_families(router_classification) -> list[str]:
    if router_classification is None:
        return []
    families = getattr(router_classification, "graph_families", None) or []
    out: list[str] = []
    for family in families:
        value = str(family).strip().lower()
        if value and value not in out:
            out.append(value)
    return out


def _auto_graph_edge_families(families: list[str]) -> list[str]:
    return [family for family in families if family != "semantic"]


def _graph_expand_decision(
    *,
    has_graph_expand: bool,
    ranked_count: int,
    explicit_expand_context: bool,
    router_classification,
) -> _GraphExpandDecision:
    families = _classification_graph_families(router_classification)

    if not has_graph_expand:
        return _GraphExpandDecision(False, "skipped_disabled", families, [])
    if ranked_count <= 0:
        return _GraphExpandDecision(False, "skipped_no_seed_results", families, [])
    if explicit_expand_context:
        return _GraphExpandDecision(True, "explicit_expand_context", families, None)
    if not _env_truthy("MEMORY_GRAPH_EXPAND", "0"):
        return _GraphExpandDecision(False, "skipped_disabled", families, [])
    if router_classification is None:
        return _GraphExpandDecision(False, "skipped_semantic", families, [])

    kind = str(getattr(router_classification, "kind", "") or "").lower()
    edge_families = _auto_graph_edge_families(families)

    if kind == "relational":
        return _GraphExpandDecision(True, "auto_relational", families, edge_families)
    for family in _AUTO_GRAPH_EXPAND_FAMILIES:
        if family in families:
            return _GraphExpandDecision(True, f"auto_{family}", families, edge_families)
    if families == ["procedural"]:
        return _GraphExpandDecision(False, "skipped_procedural_only", families, [])
    return _GraphExpandDecision(False, "skipped_semantic", families, [])
```

- [ ] **Step 4: Run helper tests and verify they pass**

Run:

```powershell
python -m pytest tests/test_recall_modes.py::test_graph_expand_decision_skips_semantic_auto tests/test_recall_modes.py::test_graph_expand_decision_explicit_override_ignores_env tests/test_recall_modes.py::test_graph_expand_decision_allows_temporal_auto tests/test_recall_modes.py::test_graph_expand_decision_skips_procedural_only -q
```

Expected: `4 passed`.

- [ ] **Step 5: Commit Task 1**

Run:

```powershell
git add src/server.py tests/test_recall_modes.py
git commit -m "test: cover graph expand routing decision"
```

Expected: commit succeeds with only `src/server.py` and `tests/test_recall_modes.py` staged.

---

### Task 2: Route Stage 6.5 Through the Decision Helper

**Files:**
- Modify: `src/server.py:3354-3367`
- Modify: `src/server.py:4089-4310`
- Test: `tests/test_recall_modes.py`

- [ ] **Step 1: Write failing recall-pipeline tests**

Append these helper and tests near the existing graph expansion test in `tests/test_recall_modes.py`:

```python
def _new_recall_with_knowledge(monkeypatch, tmp_path, content: str):
    import server

    monkeypatch.setattr(server, "MEMORY_DIR", tmp_path)
    monkeypatch.setattr(server, "HAS_GRAPH_EXPAND", True)
    (tmp_path / "blobs").mkdir(exist_ok=True)
    (tmp_path / "chroma").mkdir(exist_ok=True)

    store = server.Store()
    recall = server.Recall(store)
    sid = "sess-graph-routing"
    store.db.execute(
        "INSERT INTO sessions (id, started_at, project, status) VALUES (?, ?, ?, ?)",
        (sid, "2026-04-14T00:00:00Z", "demo", "open"),
    )
    store.db.commit()
    kid, *_ = store.save_knowledge(
        sid=sid,
        content=content,
        ktype="fact",
        project="demo",
        skip_dedup=True,
    )
    return store, recall, kid


def test_graph_expand_auto_skips_semantic_query(monkeypatch, tmp_path):
    store, recall, _kid = _new_recall_with_knowledge(
        monkeypatch,
        tmp_path,
        "database setting for ordinary semantic recall",
    )
    monkeypatch.setenv("MEMORY_GRAPH_EXPAND", "1")

    def fail_expand(*_args, **_kwargs):
        raise AssertionError("_graph_expand should not run for semantic auto recall")

    import server
    monkeypatch.setattr(server, "_graph_expand", fail_expand)

    out = recall.search(
        "what database are we using",
        project="demo",
        limit=1,
        detail="summary",
    )

    assert out["graph_expand_applied"] is False
    assert out["graph_expand_reason"] == "skipped_semantic"
    assert out["graph_expand_families"] == ["semantic"]

    store.db.close()


def test_graph_expand_auto_temporal_query_passes_family(monkeypatch, tmp_path):
    store, recall, _kid = _new_recall_with_knowledge(
        monkeypatch,
        tmp_path,
        "migration was last touched during the April maintenance window",
    )
    monkeypatch.setenv("MEMORY_GRAPH_EXPAND", "1")
    calls = []

    def fake_expand(_db, seed_ids, **kwargs):
        calls.append((list(seed_ids), kwargs))
        return []

    import server
    monkeypatch.setattr(server, "_graph_expand", fake_expand)

    out = recall.search(
        "when did we last touch the migration?",
        project="demo",
        limit=1,
        detail="summary",
    )

    assert calls
    assert calls[0][1]["edge_families"] == ["temporal"]
    assert out["graph_expand_applied"] is True
    assert out["graph_expand_reason"] == "auto_temporal"
    assert out["graph_expand_families"] == ["temporal"]

    store.db.close()


def test_graph_expand_auto_causal_query_passes_family(monkeypatch, tmp_path):
    store, recall, _kid = _new_recall_with_knowledge(
        monkeypatch,
        tmp_path,
        "install failed because the provider URL was wrong and was fixed later",
    )
    monkeypatch.setenv("MEMORY_GRAPH_EXPAND", "1")
    calls = []

    def fake_expand(_db, seed_ids, **kwargs):
        calls.append((list(seed_ids), kwargs))
        return []

    import server
    monkeypatch.setattr(server, "_graph_expand", fake_expand)

    out = recall.search(
        "why did install fail and what fixed it?",
        project="demo",
        limit=1,
        detail="summary",
    )

    assert calls
    assert calls[0][1]["edge_families"] == ["causal", "procedural"]
    assert out["graph_expand_applied"] is True
    assert out["graph_expand_reason"] == "auto_causal"
    assert out["graph_expand_families"] == ["causal", "procedural"]

    store.db.close()
```

- [ ] **Step 2: Run recall-pipeline tests and verify they fail**

Run:

```powershell
python -m pytest tests/test_recall_modes.py::test_graph_expand_auto_skips_semantic_query tests/test_recall_modes.py::test_graph_expand_auto_temporal_query_passes_family tests/test_recall_modes.py::test_graph_expand_auto_causal_query_passes_family -q
```

Expected before implementation: at least one failure because Stage 6.5 still expands every query when `MEMORY_GRAPH_EXPAND=1`, does not pass `edge_families`, and does not return graph decision metadata.

- [ ] **Step 3: Add search parameters for explicit graph expansion**

In `src/server.py`, change `Recall.search(...)` and `Recall._search_impl(...)` signatures and forwarding:

```python
    def search(self, query, project=None, ktype="all", limit=10, detail="full", branch=None, fusion="rrf",
               rerank=False, diverse=False, embedding_space=None, agent_namespace=None,
               agent_namespaces=None, scope=None, expand_context=False, expand_budget=None,
               _explain=False):
```

Forward the new parameters into `_search_impl(...)`:

```python
                embedding_space=embedding_space, agent_namespace=agent_namespace,
                agent_namespaces=agent_namespaces, scope=scope,
                expand_context=expand_context, expand_budget=expand_budget,
                _explain=_explain,
```

Change `_search_impl(...)` to accept the same parameters:

```python
    def _search_impl(self, query, project=None, ktype="all", limit=10, detail="full",
                     branch=None, fusion="rrf", rerank=False, diverse=False,
                     embedding_space=None, agent_namespace=None, agent_namespaces=None,
                     scope=None, expand_context=False, expand_budget=None,
                     _explain=False):
```

- [ ] **Step 4: Replace Stage 6.5 broad gate**

In `src/server.py`, replace the current Stage 6.5 `if (HAS_GRAPH_EXPAND ... MEMORY_GRAPH_EXPAND ...)` block with this routed version:

```python
        graph_decision = _graph_expand_decision(
            has_graph_expand=HAS_GRAPH_EXPAND,
            ranked_count=len(ranked),
            explicit_expand_context=bool(expand_context),
            router_classification=router_classification,
        )
        graph_expand_applied = False

        if graph_decision.apply:
            try:
                seed_ids = [item["r"]["id"] for item in ranked[:limit]]
                existing_ids = {item["r"]["id"] for item in ranked}
                budget = (
                    int(expand_budget)
                    if expand_budget is not None
                    else max(1, limit)
                )
                neighbours = _graph_expand(
                    self.s.db,
                    seed_ids,
                    budget=max(1, budget),
                    edge_families=graph_decision.edge_families,
                    agent_namespace=agent_namespace,
                    agent_namespaces=agent_namespaces,
                    scope=scope,
                )
                graph_expand_applied = True
                new_kids = [kid for kid, _ in neighbours if kid not in existing_ids]
                if new_kids:
                    new_id_set = set(new_kids)
                    rows = _graph_fetch(self.s.db, new_kids)
                    if rows and ranked:
                        max_primary = max(
                            it.get("rrf_score", it.get("score", 0.0))
                            for it in ranked
                        )
                        graph_scores = {
                            kid: float(score)
                            for kid, score in neighbours
                            if kid in new_id_set
                        }
                        max_graph = max(graph_scores.values(), default=1.0) or 1.0
                        boost = float(os.environ.get("MEMORY_GRAPH_EXPAND_BOOST", "1.1"))
                        for row in rows:
                            graph_score = graph_scores.get(row.get("id"), 0.0)
                            fused_score = max_primary * (graph_score / max_graph) * boost
                            ranked.append({
                                "r": row,
                                "score": fused_score,
                                "via": ["graph_expand"],
                                "rrf_score": fused_score,
                                "graph_score": graph_score,
                            })
                        ranked.sort(
                            key=lambda x: x.get("rrf_score", x.get("score", 0.0)),
                            reverse=True,
                        )
                        ranked = ranked[:limit]
            except Exception as e:
                graph_expand_applied = False
                LOG(f"graph_expand failed, keeping original ranked: {e}")
```

- [ ] **Step 5: Add metadata to the recall result**

In `src/server.py`, where `result = {...}` is built after grouping results, add:

```python
        result["graph_expand_applied"] = graph_expand_applied
        result["graph_expand_reason"] = graph_decision.reason
        result["graph_expand_families"] = graph_decision.graph_families
```

In the existing router metadata block, add graph family visibility:

```python
            result["routed_graph_families"] = router_classification.graph_families
```

- [ ] **Step 6: Update cache key to avoid stale graph-routing results**

In the `_v9_filters = {...}` dictionary near the start of `_search_impl(...)`, add:

```python
            "expand_context": str(bool(expand_context)),
            "expand_budget": str(expand_budget or ""),
            "graph_expand": os.environ.get("MEMORY_GRAPH_EXPAND", "0"),
```

In the `cache_key = self.s.cache.make_key(...)` call in `src/server.py`, add these keyword arguments:

```python
                                               expand_context=str(bool(expand_context)),
                                               expand_budget=str(expand_budget or ""),
                                               graph_expand=os.environ.get("MEMORY_GRAPH_EXPAND", "0"),
                                               graph_expand_reason=graph_decision.reason,
```

Expected behavior: semantic results cached while graph expansion is disabled are not reused for graph-expanded relationship queries or explicit override calls in either the v9 L1 cache or the standard query cache.

- [ ] **Step 7: Run recall-pipeline tests and verify they pass**

Run:

```powershell
python -m pytest tests/test_recall_modes.py::test_graph_expand_auto_skips_semantic_query tests/test_recall_modes.py::test_graph_expand_auto_temporal_query_passes_family tests/test_recall_modes.py::test_graph_expand_auto_causal_query_passes_family -q
```

Expected: `3 passed`.

- [ ] **Step 8: Commit Task 2**

Run:

```powershell
git add src/server.py tests/test_recall_modes.py
git commit -m "feat: route automatic graph expansion by query type"
```

Expected: commit succeeds with only `src/server.py` and `tests/test_recall_modes.py` staged.

---

### Task 3: Wire MCP `expand_context` Into the Canonical Recall Path

**Files:**
- Modify: `src/server.py:6338-6347`
- Modify: `src/server.py:6417-6459`
- Test: `tests/test_recall_modes.py`
- Test: `tests/test_integration_expand_context.py`

- [ ] **Step 1: Write failing explicit override pipeline test**

Append this test near the graph routing tests in `tests/test_recall_modes.py`:

```python
def test_graph_expand_explicit_override_runs_for_semantic_query(monkeypatch, tmp_path):
    store, recall, graph_id = _new_recall_with_knowledge(
        monkeypatch,
        tmp_path,
        "alpha seed one for explicit semantic graph expansion",
    )
    monkeypatch.setenv("MEMORY_GRAPH_EXPAND", "0")
    calls = []

    def fake_expand(_db, seed_ids, **kwargs):
        calls.append((list(seed_ids), kwargs))
        return [(graph_id + 1000, 10.0)]

    def fake_fetch(_db, ids):
        return [{
            "id": ids[0],
            "type": "fact",
            "content": "explicit override graph neighbour",
            "context": "",
            "project": "demo",
            "tags": [],
            "status": "active",
            "confidence": 1.0,
            "source": "",
            "created_at": "2026-04-14T00:00:00Z",
            "last_confirmed": "2026-04-14T00:00:00Z",
            "recall_count": 0,
            "session_id": "sess-graph-routing",
        }]

    import server
    monkeypatch.setattr(server, "_graph_expand", fake_expand)
    monkeypatch.setattr(server, "_graph_fetch", fake_fetch)

    out = recall.search(
        "alpha",
        project="demo",
        limit=2,
        detail="summary",
        expand_context=True,
        expand_budget=2,
    )

    ids = [item["id"] for group in out["results"].values() for item in group]
    assert calls
    assert calls[0][1]["budget"] == 2
    assert calls[0][1]["edge_families"] is None
    assert out["graph_expand_applied"] is True
    assert out["graph_expand_reason"] == "explicit_expand_context"
    assert graph_id + 1000 in ids

    store.db.close()
```

- [ ] **Step 2: Run explicit override test and verify it fails**

Run:

```powershell
python -m pytest tests/test_recall_modes.py::test_graph_expand_explicit_override_runs_for_semantic_query -q
```

Expected before full wiring: failure if `Recall.search(...)` does not accept `expand_context`, does not honor `expand_budget`, or does not call `_graph_expand` when `MEMORY_GRAPH_EXPAND=0`.

- [ ] **Step 3: Pass MCP parameters into `Recall.search(...)`**

In `_do("memory_recall", a)`, change the `recall.search(...)` call to include:

```python
                               agent_namespace=a.get("agent_namespace"),
                               agent_namespaces=a.get("agent_namespaces"),
                               scope=a.get("scope"),
                               expand_context=a.get("expand_context", False),
                               expand_budget=a.get("expand_budget"))
```

- [ ] **Step 4: Remove the old MCP-level `ContextExpander` block**

Delete the block starting with:

```python
        # Optional graph-based context expansion (1-hop neighbors).
        # Also skipped for index/timeline modes (callers opt-in to lightweight output).
        if mode_param == "search" and a.get("expand_context"):
```

and ending after:

```python
            except Exception as e:
                LOG(f"Context expansion error: {e}")
```

Expected behavior after deletion: graph expansion is returned through normal ranked recall results and metadata, not through a separate `result["expansion"]` side channel.

- [ ] **Step 5: Update the existing budget/ranking test**

In `tests/test_recall_modes.py::test_graph_expand_scores_compete_with_seed_budget`, change:

```python
    out = recall.search("alpha", project="demo", limit=2, detail="summary")
```

to:

```python
    out = recall.search(
        "alpha",
        project="demo",
        limit=2,
        detail="summary",
        expand_context=True,
        expand_budget=2,
    )
```

Keep the existing `assert kwargs["budget"] == 2` in `fake_expand`.

- [ ] **Step 6: Run explicit override and schema tests**

Run:

```powershell
python -m pytest tests/test_recall_modes.py::test_graph_expand_explicit_override_runs_for_semantic_query tests/test_recall_modes.py::test_graph_expand_scores_compete_with_seed_budget tests/test_integration_expand_context.py -q
```

Expected: all selected tests pass. `tests/test_integration_expand_context.py::test_memory_recall_schema_includes_expand_context` should still pass because the MCP schema still advertises `expand_context` and `expand_budget`.

- [ ] **Step 7: Commit Task 3**

Run:

```powershell
git add src/server.py tests/test_recall_modes.py tests/test_integration_expand_context.py
git commit -m "feat: honor explicit graph expansion override"
```

Expected: commit succeeds. If `tests/test_integration_expand_context.py` is unchanged, omit it from `git add`.

---

### Task 4: Verification, Regression Sweep, and Documentation Check

**Files:**
- Verify: `src/server.py`
- Verify: `tests/test_recall_modes.py`
- Verify: `tests/test_query_router.py`
- Verify: `tests/test_graph_expander_family.py`
- Verify: `tests/test_integration_expand_context.py`

- [ ] **Step 1: Run the focused graph and router test suite**

Run:

```powershell
python -m pytest tests/test_recall_modes.py tests/test_query_router.py tests/test_graph_expander_family.py tests/test_integration_expand_context.py -q
```

Expected: all selected tests pass.

- [ ] **Step 2: Inspect changed files**

Run:

```powershell
git diff -- src/server.py tests/test_recall_modes.py tests/test_integration_expand_context.py
```

Expected:

- `src/server.py` contains `_GraphExpandDecision`, `_graph_expand_decision(...)`, routed Stage 6.5 logic, `edge_families=...`, and graph expansion metadata.
- `Recall.search(...)` and `_search_impl(...)` accept `expand_context` and `expand_budget`.
- `_do("memory_recall", a)` passes MCP `expand_context` and `expand_budget` into `recall.search(...)`.
- The old MCP-level `ContextExpander` block is gone.
- `tests/test_recall_modes.py` covers semantic skip, temporal auto-expand, causal auto-expand, explicit override, and the updated budget/ranking path.

- [ ] **Step 3: Check for accidental broad graph expansion conditions**

Run:

```powershell
rg -n "MEMORY_GRAPH_EXPAND|ContextExpander|graph_expand_reason|edge_families" src/server.py tests/test_recall_modes.py tests/test_integration_expand_context.py
```

Expected:

- `MEMORY_GRAPH_EXPAND` appears in `_graph_expand_decision(...)`, cache-key construction, and tests.
- `ContextExpander` no longer appears in the `memory_recall` handler path.
- `_graph_expand(...)` is called with `edge_families=graph_decision.edge_families`.

- [ ] **Step 4: Commit verification fixes if any were needed**

If Step 1 or Step 2 required edits, run:

```powershell
git add src/server.py tests/test_recall_modes.py tests/test_integration_expand_context.py
git commit -m "test: verify routed graph expansion behavior"
```

Expected: commit succeeds only if verification required edits. If no edits were needed after Task 3, skip this commit.

- [ ] **Step 5: Save a project memory after implementation**

After implementation and tests pass, save a concise durable decision or solution memory:

```json
{
  "type": "solution",
  "project": "total-agent-memory",
  "content": "Graph expansion recall routing now treats expand_context=true as an explicit override and limits automatic MEMORY_GRAPH_EXPAND behavior to relational/entity, causal, and temporal query families.",
  "context": "Implemented from docs/superpowers/specs/2026-07-10-graph-expand-routing-design.md. This avoids noisy graph neighbors in ordinary semantic recall while preserving graph reasoning for relationship, cause, and timeline questions.",
  "tags": ["project:total-agent-memory", "graph-expand", "recall-routing"]
}
```

---

## Self-Review

Spec coverage:

- Explicit `expand_context=true` override is covered in Task 1 and Task 3.
- Automatic relational/entity, causal, and temporal routing is covered in Task 1 and Task 2.
- Pure semantic and procedural-only skip behavior is covered in Task 1 and Task 2.
- Family filtering through `edge_families` is covered in Task 2.
- Response metadata is covered in Task 2 and verified in Task 4.
- Removal of the duplicate MCP-level expansion path is covered in Task 3.

Vague-instruction scan:

- The plan contains concrete file paths, commands, code snippets, and expected results.
- The plan avoids underspecified implementation instructions.

Type consistency:

- The helper type is `_GraphExpandDecision`.
- The helper function is `_graph_expand_decision(...)`.
- Result metadata fields are `graph_expand_applied`, `graph_expand_reason`, and `graph_expand_families`.
- `Recall.search(...)` and `Recall._search_impl(...)` both use `expand_context` and `expand_budget`.

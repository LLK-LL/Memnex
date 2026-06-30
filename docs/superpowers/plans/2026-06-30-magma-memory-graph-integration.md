# MAGMA Memory Graph Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fold MAGMA-style multi-graph memory routing into total-agent-memory while preserving the existing local-first MCP architecture.

**Architecture:** Add a compatibility taxonomy layer that maps existing `graph_edges.relation_type` values into semantic, temporal, causal, entity, and procedural edge families without requiring a schema migration. Extend query routing and graph expansion to use these families, then add graph path explanations and a throttled structural consolidation stage that respects local 3B Ollama throughput.

**Tech Stack:** Python, SQLite, pytest, existing `src/graph/*`, `src/query_router.py`, `src/graph_expander.py`, `src/enrichment_worker.py`.

---

### Task 1: Edge Family Taxonomy

**Files:**
- Create: `src/graph/edge_taxonomy.py`
- Modify: `src/graph/__init__.py`
- Test: `tests/test_graph_edge_taxonomy.py`

- [ ] **Step 1: Write the failing tests**

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from graph.edge_taxonomy import (
    edge_family_for_relation,
    normalize_edge_families,
    relation_allowed_by_families,
)


def test_maps_known_relations_to_magma_families():
    assert edge_family_for_relation("similar_to") == "semantic"
    assert edge_family_for_relation("precedes") == "temporal"
    assert edge_family_for_relation("caused_by") == "causal"
    assert edge_family_for_relation("mentions") == "entity"
    assert edge_family_for_relation("fixed_by") == "procedural"


def test_unknown_relations_default_to_semantic():
    assert edge_family_for_relation("custom_project_link") == "semantic"


def test_normalize_edge_families_dedupes_and_drops_unknowns():
    assert normalize_edge_families(["causal", "semantic", "causal", "bogus"]) == [
        "causal",
        "semantic",
    ]


def test_relation_allowed_by_families_accepts_empty_filter():
    assert relation_allowed_by_families("uses", None)
    assert relation_allowed_by_families("uses", [])


def test_relation_allowed_by_families_filters_by_family():
    assert relation_allowed_by_families("caused_by", ["causal"])
    assert not relation_allowed_by_families("caused_by", ["semantic"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_graph_edge_taxonomy.py -q`

Expected: FAIL with `ModuleNotFoundError: No module named 'graph.edge_taxonomy'`.

- [ ] **Step 3: Implement the minimal taxonomy module**

Create constants for valid families, relation synonym sets, and three pure functions.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_graph_edge_taxonomy.py -q`

Expected: PASS.

### Task 2: Family-Aware Graph Traversal

**Files:**
- Modify: `src/graph/store.py`
- Modify: `src/graph/query.py`
- Test: `tests/test_graph.py`

- [ ] **Step 1: Write failing tests**

Add tests that `GraphStore.get_edges(..., edge_families=["causal"])` returns only causal-family relations and that `GraphQuery.neighborhood(..., edge_families=["causal"])` walks only causal edges.

- [ ] **Step 2: Run targeted tests to verify failure**

Run: `pytest tests/test_graph.py::TestGraphStoreEdges tests/test_graph.py::TestGraphQueryTraversal -q`

Expected: FAIL because `edge_families` is not an accepted argument.

- [ ] **Step 3: Add optional `edge_families` parameters**

Keep old callers untouched. Filter in Python using `relation_allowed_by_families` after SQL fetch so old schemas remain valid.

- [ ] **Step 4: Run targeted tests**

Run: `pytest tests/test_graph.py::TestGraphStoreEdges tests/test_graph.py::TestGraphQueryTraversal -q`

Expected: PASS.

### Task 3: Query Router Graph Families

**Files:**
- Modify: `src/query_router.py`
- Test: `tests/test_query_router.py`

- [ ] **Step 1: Write failing tests**

Add tests that temporal questions route to `["temporal"]`, why/failure questions route to `["causal", "procedural"]`, entity/co-mention questions include `["entity"]`, and default semantic questions use `["semantic"]`.

- [ ] **Step 2: Run tests to verify failure**

Run: `pytest tests/test_query_router.py -q`

Expected: FAIL because `QueryClassification` has no `graph_families`.

- [ ] **Step 3: Add `graph_families` to `QueryClassification`**

Use heuristic patterns only. No LLM calls. Keep existing `kind`, `confidence`, `entities`, and `signals` behavior backward compatible.

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_query_router.py -q`

Expected: PASS.

### Task 4: Family-Aware Graph Expansion and Path Explanation

**Files:**
- Modify: `src/graph_expander.py`
- Test: `tests/test_graph_expander.py` or create `tests/test_graph_expander_family.py`

- [ ] **Step 1: Write failing tests**

Seed graph edges with causal and semantic relations. Assert `expand_top_k(..., edge_families=["causal"])` returns only candidates reached through causal edges and includes path metadata through a new explanation helper.

- [ ] **Step 2: Run tests to verify failure**

Run targeted graph expander tests.

- [ ] **Step 3: Add optional `edge_families` and `explain_paths` support**

Preserve existing `expand()` return shape by default. Add a separate helper for explanation instead of breaking current callers.

- [ ] **Step 4: Run tests**

Expected: PASS.

### Task 5: 3B Ollama-Safe Structural Consolidation

**Files:**
- Modify: `src/enrichment_worker.py`
- Create or modify tests: `tests/test_enrichment_worker.py`

- [ ] **Step 1: Write failing throttle tests**

Add tests for a new structural stage config:
`MEMORY_STRUCTURAL_CONSOLIDATION`, `MEMORY_STRUCTURAL_MAX_PER_TICK`, `MEMORY_STRUCTURAL_MIN_INTERVAL_SEC`, and `MEMORY_STRUCTURAL_MODEL_SIZE`.

- [ ] **Step 2: Run tests to verify failure**

Run: `pytest tests/test_enrichment_worker.py -q`

Expected: FAIL because config/stage is missing.

- [ ] **Step 3: Implement a conservative no-op-by-default structural stage**

Default off. For `MEMORY_STRUCTURAL_MODEL_SIZE=3b`, cap to one task per tick and require a minimum interval unless overridden. The first implementation should only schedule/skip safely; deeper LLM edge inference can be a later slice.

- [ ] **Step 4: Run tests**

Expected: PASS.

### Task 6: Integration Verification

**Files:**
- No new files unless tests expose gaps.

- [ ] **Step 1: Run targeted suites**

Run:

```powershell
pytest tests/test_graph_edge_taxonomy.py tests/test_graph.py tests/test_query_router.py tests/test_enrichment_worker.py -q
```

- [ ] **Step 2: Run CodeGraph affected**

Run:

```powershell
& 'C:\Users\Administrator\AppData\Local\codegraph\current\bin\codegraph.cmd' affected --path C:\Users\Administrator\total-agent-memory src\query_router.py src\graph_expander.py src\graph\store.py src\graph\query.py src\enrichment_worker.py
```

- [ ] **Step 3: Commit only task-related code files**

Stage only files touched by this task, excluding existing unrelated user changes.

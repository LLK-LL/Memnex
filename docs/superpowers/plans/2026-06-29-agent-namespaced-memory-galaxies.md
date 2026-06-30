# Agent Namespaced Memory Galaxies Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add first-class agent namespaces so Codex, Reasonix, and future agents store, retrieve, graph, and visualize isolated memory frameworks by default.

**Architecture:** Use a single SQLite database with explicit `agent_namespace` ownership on durable records and namespace-aware filters in save, recall, graph, and viewer export paths. The existing Memory Galaxy view renders multiple agent galaxies directly in one scene; each galaxy keeps the current internal layer and solar drill-down model, with the center label set to the agent name.

**Tech Stack:** Python, SQLite migrations, MCP tool schemas in `src/server.py`, graph export in `src/tools/memory_graph_viewer_export.py`, PixiJS/vanilla JS viewer assets, pytest, Node test runner, Playwright browser regression.

---

## File Structure

- Create: `migrations/029_agent_namespace.sql`
  - Numbered migration for namespace columns and hot-path indexes.
- Create: `scripts/backfill_agent_namespace.py`
  - Preview/apply migration of existing Reasonix records using tag/content/context evidence.
- Modify: `src/server.py`
  - Bootstrap migration, namespace resolver, save tool schemas, dispatchers, recall/search filters, cache keys, and response metadata.
- Modify: `src/tools/memory_graph_viewer_export.py`
  - Export namespace metadata, namespace-qualified node IDs, and `agent_galaxies` metadata.
- Modify: `src/tools/memory_graph_viewer_assets/memory-galaxy-core.js`
  - Preserve namespace fields in graph conversion and cache key generation.
- Modify: `src/tools/memory_graph_viewer_assets/memory-galaxy-layouts.js`
  - Group same-scene overview into multiple agent galaxies and rename center stars to agent labels.
- Modify: `src/tools/memory_graph_viewer_assets/memory-galaxy-renderer.js`
  - Make center labels prominent and collision-aware.
- Modify: `src/tools/memory_graph_viewer_assets/viewer.js`
  - Surface namespace labels in inspector/stats and keep existing view mode.
- Modify: `tests/test_integration_memory_save.py`
  - Save-path namespace tests.
- Create: `tests/test_agent_namespace_recall.py`
  - Recall/search isolation tests.
- Modify: `tests/test_memory_graph_viewer_export.py`
  - Export grouping and namespace-qualified IDs.
- Modify: `tests/js/memory_galaxy_smoke.test.mjs`
  - Multi-agent galaxy layout and center label tests.
- Modify or create: `tests/js/memory_galaxy_browser_regression.test.mjs`
  - Browser regression for two galaxies in one scene, readable center labels, and no visible overlap.

## Task 1: Schema And Bootstrap Migration

**Files:**
- Create: `migrations/029_agent_namespace.sql`
- Modify: `src/server.py`
- Test: `tests/test_integration_memory_save.py`

- [ ] **Step 1: Add failing schema test**

Add this test to `tests/test_integration_memory_save.py`:

```python
def test_memory_save_defaults_agent_namespace_to_codex(store):
    rid, deduped, *_ = store.save_knowledge(
        "session-namespace-default",
        "Namespace default probe for Codex storage",
        "fact",
        project="namespace-test",
        tags=["namespace-test"],
        skip_quality=True,
    )

    assert rid
    assert deduped is False
    row = store.q1("SELECT agent_namespace FROM knowledge WHERE id=?", (rid,))
    assert row["agent_namespace"] == "codex"
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m pytest tests/test_integration_memory_save.py::test_memory_save_defaults_agent_namespace_to_codex -q
```

Expected: FAIL because `knowledge.agent_namespace` does not exist.

- [ ] **Step 3: Add numbered migration**

Create `migrations/029_agent_namespace.sql`:

```sql
-- 029_agent_namespace.sql
-- Adds first-class agent namespace ownership for multi-agent memory isolation.

ALTER TABLE knowledge ADD COLUMN agent_namespace TEXT NOT NULL DEFAULT 'codex';

CREATE INDEX IF NOT EXISTS idx_k_agent_namespace
    ON knowledge(agent_namespace);

CREATE INDEX IF NOT EXISTS idx_k_project_agent_namespace
    ON knowledge(project, agent_namespace);

CREATE INDEX IF NOT EXISTS idx_k_type_agent_namespace
    ON knowledge(type, agent_namespace);
```

- [ ] **Step 4: Add bootstrap migration in `src/server.py`**

In `Store._migrate`, after the existing branch migration and before `agent_id`, add:

```python
        # v12.6: agent namespace isolation (Codex, Reasonix, future agents).
        if "agent_namespace" not in cols:
            self.db.execute("ALTER TABLE knowledge ADD COLUMN agent_namespace TEXT NOT NULL DEFAULT 'codex'")
            self.db.execute("CREATE INDEX IF NOT EXISTS idx_k_agent_namespace ON knowledge(agent_namespace)")
            self.db.execute(
                "CREATE INDEX IF NOT EXISTS idx_k_project_agent_namespace "
                "ON knowledge(project, agent_namespace)"
            )
            self.db.execute(
                "CREATE INDEX IF NOT EXISTS idx_k_type_agent_namespace "
                "ON knowledge(type, agent_namespace)"
            )
            LOG("Migration: added agent_namespace to knowledge table")
        else:
            self.db.execute("CREATE INDEX IF NOT EXISTS idx_k_agent_namespace ON knowledge(agent_namespace)")
            self.db.execute(
                "CREATE INDEX IF NOT EXISTS idx_k_project_agent_namespace "
                "ON knowledge(project, agent_namespace)"
            )
            self.db.execute(
                "CREATE INDEX IF NOT EXISTS idx_k_type_agent_namespace "
                "ON knowledge(type, agent_namespace)"
            )
```

- [ ] **Step 5: Run schema test**

Run:

```powershell
python -m pytest tests/test_integration_memory_save.py::test_memory_save_defaults_agent_namespace_to_codex -q
```

Expected: PASS.

## Task 2: Namespace Resolution And Save Path

**Files:**
- Modify: `src/server.py`
- Test: `tests/test_integration_memory_save.py`

- [ ] **Step 1: Add failing explicit namespace save test**

Add:

```python
def test_memory_save_persists_explicit_agent_namespace(store):
    rid, deduped, *_ = store.save_knowledge(
        "session-namespace-reasonix",
        "Reasonix namespace probe should stay separate from Codex",
        "fact",
        project="namespace-test",
        tags=["reasonix", "namespace-test"],
        skip_quality=True,
        agent_namespace="reasonix",
    )

    assert rid
    assert deduped is False
    row = store.q1("SELECT agent_namespace FROM knowledge WHERE id=?", (rid,))
    assert row["agent_namespace"] == "reasonix"
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m pytest tests/test_integration_memory_save.py::test_memory_save_persists_explicit_agent_namespace -q
```

Expected: FAIL because `save_knowledge` does not accept `agent_namespace`.

- [ ] **Step 3: Add namespace helpers**

Near other small helper functions in `src/server.py`, add:

```python
def _normalise_agent_namespace(value: str | None) -> str:
    raw = (value or "").strip().lower()
    if not raw:
        return "codex"
    raw = re.sub(r"[^a-z0-9_.:-]+", "-", raw)
    raw = raw.strip("-._:")
    return raw or "codex"


def resolve_agent_namespace(value: str | None = None) -> str:
    return _normalise_agent_namespace(
        value
        or os.environ.get("TAM_AGENT_NAMESPACE")
        or os.environ.get("MEMORY_AGENT_NAMESPACE")
        or "codex"
    )
```

- [ ] **Step 4: Thread namespace through `save_knowledge`**

Update both signatures:

```python
    def save_knowledge(self, sid, content, ktype, project="general", tags=None,
                        context="", branch="", skip_dedup=False, filter_name=None,
                        importance="medium", skip_quality=False, coref=None,
                        agent_id=None, parent_agent_id=None, agent_namespace=None,
                        _from_outbox=False):
```

```python
    def _save_knowledge_impl(self, sid, content, ktype, project="general", tags=None,
                              context="", branch="", skip_dedup=False, filter_name=None,
                              importance="medium", skip_quality=False, coref=None,
                              agent_id=None, parent_agent_id=None, agent_namespace=None,
                              _from_outbox=False):
```

In `save_knowledge`, pass:

```python
                agent_id=agent_id, parent_agent_id=parent_agent_id,
                agent_namespace=agent_namespace,
                _from_outbox=_from_outbox,
```

At the start of `_save_knowledge_impl`, after `now = ...`, add:

```python
        agent_namespace = resolve_agent_namespace(agent_namespace)
```

Add `agent_namespace` to the outbox payload:

```python
                        "agent_id": agent_id, "parent_agent_id": parent_agent_id,
                        "agent_namespace": agent_namespace,
```

Update the insert:

```python
        cur = self.db.execute("""
            INSERT INTO knowledge (session_id,type,content,context,project,tags,source,confidence,
                                   created_at,last_confirmed,recall_count,branch,importance,
                                   agent_id,parent_agent_id,agent_namespace)
            VALUES (?,?,?,?,?,?,'explicit',1.0,?,?,0,?,?,?,?,?)
        """, (sid, ktype, content, context, project, json.dumps(tags or []), now, now,
              branch or "", importance_value, agent_id, parent_agent_id, agent_namespace))
```

- [ ] **Step 5: Run save tests**

Run:

```powershell
python -m pytest tests/test_integration_memory_save.py::test_memory_save_defaults_agent_namespace_to_codex tests/test_integration_memory_save.py::test_memory_save_persists_explicit_agent_namespace -q
```

Expected: PASS.

## Task 3: MCP Tool Schemas And Dispatchers

**Files:**
- Modify: `src/server.py`
- Test: existing MCP schema tests or `tests/test_v11_new_tools.py`

- [ ] **Step 1: Add schema assertions**

Add to an existing schema test file that already inspects `list_tools`, or create a focused test in `tests/test_agent_namespace_recall.py`:

```python
def test_memory_save_tools_expose_agent_namespace(wired_server):
    tools = {tool.name: tool for tool in wired_server.list_tools()}

    assert "agent_namespace" in tools["memory_save"].inputSchema["properties"]
    assert "agent_namespace" in tools["memory_save_fast"].inputSchema["properties"]
```

- [ ] **Step 2: Run schema test to verify it fails**

Run:

```powershell
python -m pytest tests/test_agent_namespace_recall.py::test_memory_save_tools_expose_agent_namespace -q
```

Expected: FAIL until schemas expose the field.

- [ ] **Step 3: Update tool schema fields**

In the `memory_save` input schema properties, add:

```python
                    "agent_namespace": {
                        "type": "string",
                        "description": "Owning agent memory namespace. Defaults to TAM_AGENT_NAMESPACE or codex. Use reasonix for Reasonix-originated writes.",
                    },
```

In `memory_save_fast`, add the same `agent_namespace` property.

- [ ] **Step 4: Update dispatchers**

In the `memory_save` dispatcher, pass:

```python
            agent_id=a.get("agent_id"),
            parent_agent_id=a.get("parent_agent_id"),
            agent_namespace=a.get("agent_namespace"))
```

In the `memory_save_fast` dispatcher, pass:

```python
            agent_id=a.get("agent_id"),
            parent_agent_id=a.get("parent_agent_id"),
            agent_namespace=a.get("agent_namespace"),
```

Add namespace to successful return payloads:

```python
        result = {
            "saved": True,
            "id": rid,
            "deduplicated": was_dedup,
            "agent_namespace": resolve_agent_namespace(a.get("agent_namespace")),
        }
```

```python
        out = {
            "saved": True,
            "id": rid,
            "deduplicated": was_dedup,
            "mode": "fast",
            "agent_namespace": resolve_agent_namespace(a.get("agent_namespace")),
        }
```

- [ ] **Step 5: Run schema and fast save tests**

Run:

```powershell
python -m pytest tests/test_agent_namespace_recall.py::test_memory_save_tools_expose_agent_namespace tests/test_v11_new_tools.py::test_memory_save_fast_skips_quality_gate -q
```

Expected: PASS.

## Task 4: Recall/Search Isolation

**Files:**
- Modify: `src/server.py`
- Create: `tests/test_agent_namespace_recall.py`

- [ ] **Step 1: Add failing recall isolation tests**

Create `tests/test_agent_namespace_recall.py` with:

```python
import pytest


def test_search_defaults_to_codex_namespace(store):
    codex_id, *_ = store.save_knowledge(
        "ns-search-codex",
        "Codex-only namespace recall probe alpha",
        "fact",
        project="namespace-recall",
        tags=["namespace-recall"],
        skip_quality=True,
        agent_namespace="codex",
    )
    reasonix_id, *_ = store.save_knowledge(
        "ns-search-reasonix",
        "Reasonix-only namespace recall probe alpha",
        "fact",
        project="namespace-recall",
        tags=["reasonix", "namespace-recall"],
        skip_quality=True,
        agent_namespace="reasonix",
    )

    result = store.recall.search(
        "namespace recall probe alpha",
        project="namespace-recall",
        limit=10,
        detail="full",
    )
    ids = {item["id"] for group in result.get("results", {}).values() for item in group}

    assert codex_id in ids
    assert reasonix_id not in ids


def test_search_can_explicitly_query_reasonix_namespace(store):
    reasonix_id, *_ = store.save_knowledge(
        "ns-search-reasonix-explicit",
        "Reasonix explicit namespace recall probe beta",
        "fact",
        project="namespace-recall",
        tags=["reasonix", "namespace-recall"],
        skip_quality=True,
        agent_namespace="reasonix",
    )

    result = store.recall.search(
        "explicit namespace recall probe beta",
        project="namespace-recall",
        limit=10,
        detail="full",
        agent_namespace="reasonix",
    )
    ids = {item["id"] for group in result.get("results", {}).values() for item in group}

    assert reasonix_id in ids
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```powershell
python -m pytest tests/test_agent_namespace_recall.py -q
```

Expected: FAIL because `Recall.search` does not accept or filter `agent_namespace`.

- [ ] **Step 3: Extend search signatures and cache keys**

Update `Recall.search` and `_search_impl` signatures:

```python
    def search(self, query, project=None, ktype="all", limit=10, detail="full", branch=None, fusion="rrf",
               rerank=False, diverse=False, embedding_space=None, agent_namespace=None,
               agent_namespaces=None, scope=None, _explain=False):
```

```python
    def _search_impl(self, query, project=None, ktype="all", limit=10, detail="full",
                     branch=None, fusion="rrf", rerank=False, diverse=False,
                     embedding_space=None, agent_namespace=None, agent_namespaces=None,
                     scope=None, _explain=False):
```

Pass the new args from `search` to `_search_impl`.

At the start of `_search_impl`, add:

```python
        namespace_filter = resolve_agent_namespaces(
            agent_namespace=agent_namespace,
            agent_namespaces=agent_namespaces,
            scope=scope,
        )
```

Add helper near `resolve_agent_namespace`:

```python
def resolve_agent_namespaces(agent_namespace=None, agent_namespaces=None, scope=None) -> list[str] | None:
    if str(scope or "").strip().lower() in {"all", "all_agents", "cross_agent"}:
        return None
    if agent_namespaces:
        if isinstance(agent_namespaces, str):
            values = [agent_namespaces]
        else:
            values = list(agent_namespaces)
        resolved = [_normalise_agent_namespace(v) for v in values if str(v).strip()]
        return sorted(set(resolved)) or [resolve_agent_namespace(agent_namespace)]
    return [resolve_agent_namespace(agent_namespace)]
```

Include namespace filters in `_v9_filters` and cache keys:

```python
            "agent_namespaces": ",".join(namespace_filter) if namespace_filter else "*",
```

- [ ] **Step 4: Apply SQL filters**

In the FTS tier, after branch filtering:

```python
            if namespace_filter:
                ph = ",".join("?" * len(namespace_filter))
                conds.append(f"k.agent_namespace IN ({ph})")
                params.extend(namespace_filter)
```

When fetching semantic candidate rows, replace:

```python
rec = self.s.q1("SELECT * FROM knowledge WHERE id=?", (kid,))
```

with:

```python
rec = self.s.q1("SELECT * FROM knowledge WHERE id=?", (kid,))
if rec and namespace_filter and rec.get("agent_namespace", "codex") not in namespace_filter:
    rec = None
```

Apply the same guard in every non-FTS tier that fetches `SELECT * FROM knowledge WHERE id=?`.

- [ ] **Step 5: Add tool schema and dispatcher parameters**

In `memory_recall` and `memory_search_fast` tool schemas, add:

```python
                    "agent_namespace": {"type": "string", "description": "Search one agent namespace. Defaults to current namespace."},
                    "agent_namespaces": {"type": "array", "items": {"type": "string"}, "description": "Explicit list of agent namespaces for cross-agent search."},
                    "scope": {"type": "string", "enum": ["default", "all_agents"], "description": "Use all_agents only when the user explicitly requests cross-agent search."},
```

Pass these fields into `recall.search(...)` in both dispatchers.

- [ ] **Step 6: Run recall isolation tests**

Run:

```powershell
python -m pytest tests/test_agent_namespace_recall.py -q
```

Expected: PASS.

## Task 5: Reasonix Backfill Script

**Files:**
- Create: `scripts/backfill_agent_namespace.py`
- Test: create `tests/test_agent_namespace_backfill.py`

- [ ] **Step 1: Add failing script tests**

Create `tests/test_agent_namespace_backfill.py`:

```python
import sqlite3
from pathlib import Path

from scripts.backfill_agent_namespace import find_reasonix_candidates, apply_reasonix_backfill


def _db(tmp_path: Path):
    path = tmp_path / "memory.db"
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            context TEXT,
            tags TEXT,
            agent_namespace TEXT NOT NULL DEFAULT 'codex'
        );
        """
    )
    return conn


def test_reasonix_backfill_matches_tags_and_content(tmp_path):
    conn = _db(tmp_path)
    conn.execute("INSERT INTO knowledge(content, context, tags) VALUES (?, ?, ?)", ("plain codex", "", "[]"))
    conn.execute("INSERT INTO knowledge(content, context, tags) VALUES (?, ?, ?)", ("plain", "", '["reasonix"]'))
    conn.execute("INSERT INTO knowledge(content, context, tags) VALUES (?, ?, ?)", ("Total Agent Memory integrated into Reasonix", "", "[]"))
    conn.commit()

    candidates = find_reasonix_candidates(conn)
    assert {item["id"] for item in candidates["will_update"]} == {2, 3}

    updated = apply_reasonix_backfill(conn)
    assert updated == 2
    rows = conn.execute("SELECT id, agent_namespace FROM knowledge ORDER BY id").fetchall()
    assert [row["agent_namespace"] for row in rows] == ["codex", "reasonix", "reasonix"]
```

- [ ] **Step 2: Run test to verify failure**

Run:

```powershell
python -m pytest tests/test_agent_namespace_backfill.py -q
```

Expected: FAIL because script does not exist.

- [ ] **Step 3: Implement script**

Create `scripts/backfill_agent_namespace.py`:

```python
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path


REASONIX_MARKERS = ("reasonix",)


def _loads_tags(value: str | None) -> list[str]:
    if not value:
        return []
    try:
        parsed = json.loads(value)
    except Exception:
        return []
    if not isinstance(parsed, list):
        return []
    return [str(item).strip().lower() for item in parsed]


def _has_reasonix_marker(*values: str | None) -> bool:
    text = "\n".join(v or "" for v in values).lower()
    return any(marker in text for marker in REASONIX_MARKERS)


def find_reasonix_candidates(conn: sqlite3.Connection) -> dict[str, list[dict]]:
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, content, context, tags, agent_namespace FROM knowledge ORDER BY id"
    ).fetchall()
    report = {
        "matched_by_tag": [],
        "matched_by_content": [],
        "matched_by_context": [],
        "already_reasonix": [],
        "will_update": [],
        "ambiguous": [],
    }
    seen_update: set[int] = set()
    for row in rows:
        item = {
            "id": int(row["id"]),
            "agent_namespace": row["agent_namespace"],
            "reason": "",
        }
        tags = _loads_tags(row["tags"])
        if row["agent_namespace"] == "reasonix":
            item["reason"] = "already_reasonix"
            report["already_reasonix"].append(item)
            continue
        matched = False
        if "reasonix" in tags:
            matched = True
            tagged = dict(item)
            tagged["reason"] = "tag:reasonix"
            report["matched_by_tag"].append(tagged)
        if _has_reasonix_marker(row["content"]):
            matched = True
            content = dict(item)
            content["reason"] = "content:reasonix"
            report["matched_by_content"].append(content)
        if _has_reasonix_marker(row["context"]):
            matched = True
            context = dict(item)
            context["reason"] = "context:reasonix"
            report["matched_by_context"].append(context)
        if matched and int(row["id"]) not in seen_update:
            seen_update.add(int(row["id"]))
            update_item = dict(item)
            update_item["reason"] = "reasonix evidence"
            report["will_update"].append(update_item)
    return report


def apply_reasonix_backfill(conn: sqlite3.Connection) -> int:
    report = find_reasonix_candidates(conn)
    ids = [item["id"] for item in report["will_update"]]
    if not ids:
        return 0
    conn.executemany(
        "UPDATE knowledge SET agent_namespace='reasonix' WHERE id=?",
        [(item_id,) for item_id in ids],
    )
    conn.commit()
    return len(ids)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    report = find_reasonix_candidates(conn)
    if args.apply:
        report["updated"] = apply_reasonix_backfill(conn)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run script tests**

Run:

```powershell
python -m pytest tests/test_agent_namespace_backfill.py -q
```

Expected: PASS.

- [ ] **Step 5: Preview live backfill only**

Run:

```powershell
python scripts/backfill_agent_namespace.py --db C:\Users\Administrator\.tam\memory.db
```

Expected: JSON report with `will_update`; no database writes.

Do not run `--apply` until the preview report is reviewed.

## Task 6: Graph Export Namespace Metadata

**Files:**
- Modify: `src/tools/memory_graph_viewer_export.py`
- Modify: `tests/test_memory_graph_viewer_export.py`

- [ ] **Step 1: Add failing export test**

Add to `tests/test_memory_graph_viewer_export.py`:

```python
def test_load_graph_groups_agent_galaxies(tmp_path):
    db = tmp_path / "memory.db"
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE graph_nodes (
            id TEXT PRIMARY KEY,
            type TEXT,
            name TEXT,
            importance REAL DEFAULT 0.5,
            mention_count INTEGER DEFAULT 1,
            status TEXT DEFAULT 'active',
            first_seen_at TEXT,
            last_seen_at TEXT
        );
        CREATE TABLE graph_edges (
            source_id TEXT,
            target_id TEXT,
            type TEXT,
            weight REAL DEFAULT 1.0
        );
        CREATE TABLE knowledge (
            id INTEGER PRIMARY KEY,
            type TEXT,
            project TEXT,
            content TEXT,
            tags TEXT,
            status TEXT DEFAULT 'active',
            created_at TEXT,
            last_confirmed TEXT,
            agent_namespace TEXT NOT NULL DEFAULT 'codex'
        );
        CREATE TABLE knowledge_nodes (
            knowledge_id INTEGER,
            node_id TEXT
        );
        """
    )
    conn.execute("INSERT INTO graph_nodes(id, type, name) VALUES ('n1', 'project', 'Codex Project')")
    conn.execute("INSERT INTO graph_nodes(id, type, name) VALUES ('n2', 'project', 'Reasonix Project')")
    conn.execute("INSERT INTO knowledge(id, type, project, content, tags, agent_namespace) VALUES (1, 'fact', 'p', 'codex', '[]', 'codex')")
    conn.execute("INSERT INTO knowledge(id, type, project, content, tags, agent_namespace) VALUES (2, 'fact', 'p', 'reasonix', '[\"reasonix\"]', 'reasonix')")
    conn.execute("INSERT INTO knowledge_nodes(knowledge_id, node_id) VALUES (1, 'n1')")
    conn.execute("INSERT INTO knowledge_nodes(knowledge_id, node_id) VALUES (2, 'n2')")
    conn.commit()

    graph = load_graph(conn, limit=20, content_limit=120)
    galaxies = {item["namespace"]: item for item in graph["metadata"]["agent_galaxies"]}

    assert set(galaxies) == {"codex", "reasonix"}
    assert all("agent_namespace" in node["data"] for node in graph["nodes"])
    assert any(node["data"]["id"].startswith("reasonix:") for node in graph["nodes"])
```

- [ ] **Step 2: Run test to verify failure**

Run:

```powershell
python -m pytest tests/test_memory_graph_viewer_export.py::test_load_graph_groups_agent_galaxies -q
```

Expected: FAIL because export does not include `agent_namespace`.

- [ ] **Step 3: Update `_load_knowledge_links`**

Select `k.agent_namespace`:

```sql
               k.id AS knowledge_id, k.type, k.project, k.content, k.tags,
               k.created_at, k.last_confirmed, k.agent_namespace
```

Include it in each knowledge item:

```python
                "agent_namespace": row["agent_namespace"] or "codex",
```

- [ ] **Step 4: Namespace graph nodes in `load_graph`**

When building nodes, derive namespace from linked knowledge:

```python
            linked_knowledge = knowledge_by_node.get(row["id"], [])
            namespace_counts: dict[str, int] = {}
            for item in linked_knowledge:
                ns = item.get("agent_namespace") or "codex"
                namespace_counts[ns] = namespace_counts.get(ns, 0) + 1
            agent_namespace = max(namespace_counts, key=namespace_counts.get) if namespace_counts else "codex"
            agent_label = agent_namespace.replace("-", " ").replace("_", " ").title()
            export_id = f"{agent_namespace}:{row['id']}"
```

Use `export_id` for node `data.id`, and add:

```python
                "source_id": row["id"],
                "agent_namespace": agent_namespace,
                "agent_label": agent_label,
```

For edges, emit only when both endpoint export IDs exist and use namespaced endpoint IDs.

- [ ] **Step 5: Add metadata**

Before returning graph:

```python
    agent_galaxies = []
    for namespace, counts in sorted(agent_counts.items()):
        agent_galaxies.append({
            "namespace": namespace,
            "label": namespace.replace("-", " ").replace("_", " ").title(),
            "node_count": counts["nodes"],
            "edge_count": counts["edges"],
        })
```

Add to metadata:

```python
            "agent_galaxies": agent_galaxies,
            "default_agent_namespace": os.environ.get("TAM_AGENT_NAMESPACE", "codex"),
```

- [ ] **Step 6: Run export tests**

Run:

```powershell
python -m pytest tests/test_memory_graph_viewer_export.py -q
```

Expected: PASS.

## Task 7: Multi-Agent Galaxy Data Conversion

**Files:**
- Modify: `src/tools/memory_graph_viewer_assets/memory-galaxy-core.js`
- Modify: `tests/js/memory_galaxy_smoke.test.mjs`

- [ ] **Step 1: Add failing JS conversion test**

Add to `tests/js/memory_galaxy_smoke.test.mjs`:

```javascript
{
  const multiAgentGraph = {
    metadata: {
      agent_galaxies: [
        { namespace: "codex", label: "Codex", node_count: 1, edge_count: 0 },
        { namespace: "reasonix", label: "Reasonix", node_count: 1, edge_count: 0 },
      ],
    },
    nodes: [
      { data: { id: "codex:n1", label: "Codex Memory", type: "project", agent_namespace: "codex", agent_label: "Codex", galaxy_layer: "core", knowledge: [] } },
      { data: { id: "reasonix:n2", label: "Reasonix Memory", type: "project", agent_namespace: "reasonix", agent_label: "Reasonix", galaxy_layer: "core", knowledge: [] } },
    ],
    edges: [],
  };
  const converted = convertGraphToGalaxy(multiAgentGraph);
  assert.deepEqual([...converted.agentGalaxies.keys()], ["codex", "reasonix"]);
  assert.equal(converted.nodes.find(node => node.id === "reasonix:n2").agentNamespace, "reasonix");
  assert.equal(converted.nodes.find(node => node.id === "codex:n1").agentLabel, "Codex");
}
```

- [ ] **Step 2: Run JS smoke test to verify failure**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: FAIL because `agentGalaxies` is not present.

- [ ] **Step 3: Update `convertGraphToGalaxy`**

In node conversion, add:

```javascript
      agentNamespace: data.agent_namespace || "codex",
      agentLabel: data.agent_label || labelForAgentNamespace(data.agent_namespace || "codex"),
```

Before returning, build `agentGalaxies`:

```javascript
  const agentGalaxies = new Map();
  for (const meta of graph.metadata?.agent_galaxies || []) {
    agentGalaxies.set(meta.namespace, {
      namespace: meta.namespace,
      label: meta.label || labelForAgentNamespace(meta.namespace),
      nodeCount: Number(meta.node_count || 0),
      edgeCount: Number(meta.edge_count || 0),
    });
  }
  for (const node of nodes) {
    if (!agentGalaxies.has(node.agentNamespace)) {
      agentGalaxies.set(node.agentNamespace, {
        namespace: node.agentNamespace,
        label: node.agentLabel || labelForAgentNamespace(node.agentNamespace),
        nodeCount: 0,
        edgeCount: 0,
      });
    }
    agentGalaxies.get(node.agentNamespace).nodeCount += 1;
  }
```

Return:

```javascript
  return { nodes, links, metadata: graph.metadata || {}, agentGalaxies };
```

Add helper:

```javascript
function labelForAgentNamespace(namespace) {
  return String(namespace || "codex")
    .split(/[-_:]+/)
    .filter(Boolean)
    .map(part => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ") || "Codex";
}
```

- [ ] **Step 4: Update cache key**

In `buildGalaxyCacheKey`, include agent galaxy namespaces:

```javascript
  const namespaces = galaxy?.agentGalaxies
    ? [...galaxy.agentGalaxies.keys()].join(",")
    : "codex";
```

Add `namespaces` to the key array.

- [ ] **Step 5: Run JS smoke test**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: PASS.

## Task 8: Same-Scene Multi-Galaxy Layout

**Files:**
- Modify: `src/tools/memory_graph_viewer_assets/memory-galaxy-layouts.js`
- Modify: `tests/js/memory_galaxy_smoke.test.mjs`

- [ ] **Step 1: Add failing layout test**

Add:

```javascript
{
  const graph = {
    metadata: {
      agent_galaxies: [
        { namespace: "codex", label: "Codex", node_count: 2, edge_count: 0 },
        { namespace: "reasonix", label: "Reasonix", node_count: 2, edge_count: 0 },
      ],
    },
    nodes: [
      { data: { id: "codex:a", label: "A", type: "project", agent_namespace: "codex", agent_label: "Codex", galaxy_layer: "core", knowledge: [] } },
      { data: { id: "codex:b", label: "B", type: "concept", agent_namespace: "codex", agent_label: "Codex", galaxy_layer: "active", knowledge: [] } },
      { data: { id: "reasonix:a", label: "A", type: "project", agent_namespace: "reasonix", agent_label: "Reasonix", galaxy_layer: "core", knowledge: [] } },
      { data: { id: "reasonix:b", label: "B", type: "concept", agent_namespace: "reasonix", agent_label: "Reasonix", galaxy_layer: "active", knowledge: [] } },
    ],
    edges: [],
  };
  const galaxy = convertGraphToGalaxy(graph);
  const layout = buildGalaxyOverviewLayout(galaxy, { maxNodes: 20 });
  const centers = layout.nodes.filter(node => node.orbitalRole === "agent-core");
  assert.equal(centers.length, 2);
  assert.deepEqual(centers.map(node => node.label).sort(), ["Codex", "Reasonix"]);
  const distance = Math.hypot(centers[0].x - centers[1].x, centers[0].y - centers[1].y);
  assert.ok(distance > 420);
  assert.ok(distance < 1400);
}
```

- [ ] **Step 2: Run JS test to verify failure**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: FAIL because overview layout has one `Router Core`.

- [ ] **Step 3: Replace single router center with agent centers**

In `buildGalaxyOverviewLayout`, group nodes:

```javascript
  const agentGroups = groupByAgentNamespace(nodes, galaxy.agentGalaxies);
  const agentFrames = placeAgentGalaxies(agentGroups);
```

Add helper:

```javascript
function groupByAgentNamespace(nodes, agentGalaxies = new Map()) {
  const groups = new Map();
  for (const [namespace, meta] of agentGalaxies || []) {
    groups.set(namespace, { namespace, label: meta.label, nodes: [] });
  }
  for (const node of nodes) {
    const namespace = node.agentNamespace || "codex";
    if (!groups.has(namespace)) {
      groups.set(namespace, { namespace, label: node.agentLabel || namespace, nodes: [] });
    }
    groups.get(namespace).nodes.push(node);
  }
  return [...groups.values()].filter(group => group.nodes.length > 0);
}

function placeAgentGalaxies(groups) {
  const count = Math.max(1, groups.length);
  const radius = count === 1 ? 0 : Math.min(920, Math.max(520, 300 + count * 120));
  return groups.map((group, index) => {
    const angle = count === 1 ? 0 : (-Math.PI / 2) + (Math.PI * 2 * index) / count;
    return {
      ...group,
      centerX: Math.cos(angle) * radius,
      centerY: Math.sin(angle) * radius * 0.68,
      galaxyRadius: Math.max(280, Math.min(520, 160 + Math.sqrt(group.nodes.length) * 42)),
    };
  });
}
```

For each frame, create:

```javascript
const agentCore = syntheticNode(`agent:${frame.namespace}`, frame.label, "router", nodeScale);
placed.push(placeNode(agentCore, frame.centerX, frame.centerY, {
  orbitalRole: "agent-core",
  renderRadius: Math.max(54, priorityRadiusForData(agentCore.raw || agentCore, { scale: nodeScale }) * 2.4),
  labelPriority: 1000,
  labelAnchor: { x: frame.centerX, y: frame.centerY - 92, align: "center" },
}));
```

Place each frame's existing systems around its own center, using the current internal system layout offsets.

- [ ] **Step 4: Keep same view mode**

Ensure the returned layout still uses:

```javascript
    view: "galaxy",
```

Do not introduce `view: "agent-galaxies"` or a new top-level mode.

- [ ] **Step 5: Run layout tests**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: PASS.

## Task 9: Prominent Center Labels And Collision Guards

**Files:**
- Modify: `src/tools/memory_graph_viewer_assets/memory-galaxy-renderer.js`
- Modify: `tests/js/memory_galaxy_smoke.test.mjs`

- [ ] **Step 1: Add failing label test**

Add:

```javascript
{
  const graph = {
    metadata: { agent_galaxies: [{ namespace: "reasonix", label: "Reasonix", node_count: 1, edge_count: 0 }] },
    nodes: [
      { data: { id: "reasonix:a", label: "A", type: "project", agent_namespace: "reasonix", agent_label: "Reasonix", galaxy_layer: "core", knowledge: [] } },
    ],
    edges: [],
  };
  const layout = buildGalaxyOverviewLayout(convertGraphToGalaxy(graph), { maxNodes: 20 });
  const center = layout.nodes.find(node => node.orbitalRole === "agent-core");
  assert.equal(center.label, "Reasonix");
  assert.ok(center.labelPriority >= 1000);
  assert.ok(center.renderRadius >= 54);
  assert.equal(center.labelAnchor.align, "center");
}
```

- [ ] **Step 2: Run test to verify failure**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: FAIL until layout center metadata is present.

- [ ] **Step 3: Make renderer center labels larger**

In `drawLabels`, before creating label text, detect:

```javascript
      const isAgentCore = node.orbitalRole === "agent-core";
```

When building label style, use:

```javascript
      const label = buildNodeLabel(node, {
        titleSize: isAgentCore ? 24 : undefined,
        subtitleSize: isAgentCore ? 11 : undefined,
        weight: isAgentCore ? "800" : undefined,
        maxWidth: isAgentCore ? 220 : undefined,
      });
```

If current renderer does not accept options in `buildNodeLabel`, extend it with defaults:

```javascript
function buildNodeLabel(node, options = {}) {
  const titleSize = options.titleSize || existingTitleSizeExpression;
  const subtitleSize = options.subtitleSize || existingSubtitleSizeExpression;
  const maxWidth = options.maxWidth || existingMaxWidthExpression;
}
```

- [ ] **Step 4: Add center label overlap guard**

After computing label bounds for an `agent-core`, reserve a larger exclusion box:

```javascript
      if (isAgentCore) {
        bounds.pad = Math.max(bounds.pad || 0, 18);
      }
```

If the existing label collision mechanism uses an array of bounds, push agent-core bounds first so other labels yield to it.

- [ ] **Step 5: Run JS and browser tests**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
node tests/js/memory_galaxy_browser_regression.test.mjs
```

Expected: PASS. Browser test should verify nonblank canvas and no obvious label overlap.

## Task 10: Viewer Inspector And Stats Namespace Labels

**Files:**
- Modify: `src/tools/memory_graph_viewer_assets/viewer.js`
- Modify: `tests/js/memory_galaxy_smoke.test.mjs`

- [ ] **Step 1: Add failing inspector metadata assertion**

Extend existing node-list rendering tests or add:

```javascript
{
  const graph = {
    metadata: { agent_galaxies: [{ namespace: "reasonix", label: "Reasonix", node_count: 1, edge_count: 0 }] },
    nodes: [
      { data: { id: "reasonix:node", label: "Reasonix Node", type: "project", agent_namespace: "reasonix", agent_label: "Reasonix", galaxy_layer: "core", knowledge: [] } },
    ],
    edges: [],
  };
  const galaxy = convertGraphToGalaxy(graph);
  const node = galaxy.nodes[0];
  assert.equal(node.agentLabel, "Reasonix");
}
```

- [ ] **Step 2: Update inspector metadata text**

In `renderNodeListItem`, change metadata composition from:

```javascript
${escapeHtml(raw.type || node.type || "memory")} · ${escapeHtml(systemLabel(system))} · ${escapeHtml(raw.galaxy_layer || node.layer || "unknown")}
```

to:

```javascript
${escapeHtml(node.agentLabel || raw.agent_label || "Codex")} · ${escapeHtml(raw.type || node.type || "memory")} · ${escapeHtml(systemLabel(system))} · ${escapeHtml(raw.galaxy_layer || node.layer || "unknown")}
```

- [ ] **Step 3: Update stats**

In `renderStats(metadata)`, include agent galaxy count:

```javascript
const agentCount = Array.isArray(metadata?.agent_galaxies) ? metadata.agent_galaxies.length : 1;
```

Add display row:

```javascript
["Agent galaxies", agentCount],
```

- [ ] **Step 4: Run JS tests**

Run:

```powershell
node tests/js/memory_galaxy_smoke.test.mjs
```

Expected: PASS.

## Task 11: Reasonix Future Write Configuration

**Files:**
- Modify: `install-codex.ps1`, `install.ps1`, `install.sh` only if they generate Reasonix MCP config.
- Otherwise document an external Reasonix setting in `docs/superpowers/specs/2026-06-29-agent-namespaced-memory-galaxies-design.md` or a new operations note.

- [ ] **Step 1: Inspect Reasonix config ownership**

Run:

```powershell
rg -n "Reasonix|reasonix|TAM_AGENT_NAMESPACE|mcp_servers.memory|total-agent-memory" . --glob "!node_modules/**" --glob "!.git/**"
```

Expected: identify whether this repo owns Reasonix MCP config.

- [ ] **Step 2: If repo owns Reasonix config, add env var**

Add:

```toml
TAM_AGENT_NAMESPACE = "reasonix"
```

to the Reasonix memory MCP server env block.

- [ ] **Step 3: If repo does not own Reasonix config, record manual instruction**

Add an operations note:

```markdown
Reasonix MCP must launch Total Agent Memory with `TAM_AGENT_NAMESPACE=reasonix`, or pass `agent_namespace="reasonix"` to all save tools. This guarantees future Reasonix writes stay in the Reasonix namespace even when tags are absent.
```

- [ ] **Step 4: Ask user for Reasonix assistance only if needed**

If no local Reasonix config can be found or edited, ask the user to use Reasonix to set the MCP environment variable:

```text
Please set `TAM_AGENT_NAMESPACE=reasonix` in Reasonix's Total Agent Memory MCP server environment, then restart Reasonix's MCP session.
```

## Task 12: Full Verification

**Files:**
- No code changes unless failures reveal gaps.

- [ ] **Step 1: Run focused Python tests**

Run:

```powershell
python -m pytest tests/test_integration_memory_save.py tests/test_agent_namespace_recall.py tests/test_agent_namespace_backfill.py tests/test_memory_graph_viewer_export.py tests/test_memory_graph_viewer_server.py -q
```

Expected: PASS.

- [ ] **Step 2: Run JS smoke tests**

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

Expected: PASS with nonblank canvas and readable multi-agent center labels.

- [ ] **Step 4: Run CodeGraph affected tests**

Run:

```powershell
& 'C:\Users\Administrator\AppData\Local\codegraph\current\bin\codegraph.cmd' affected --path C:\Users\Administrator\total-agent-memory src\server.py
& 'C:\Users\Administrator\AppData\Local\codegraph\current\bin\codegraph.cmd' affected --path C:\Users\Administrator\total-agent-memory src\tools\memory_graph_viewer_export.py
```

Run any additional tests CodeGraph reports.

- [ ] **Step 5: Preview Reasonix backfill**

Run:

```powershell
python scripts/backfill_agent_namespace.py --db C:\Users\Administrator\.tam\memory.db
```

Expected: preview report only. Review `will_update` before applying.

- [ ] **Step 6: Apply Reasonix backfill after preview approval**

Run only after the preview looks correct:

```powershell
python scripts/backfill_agent_namespace.py --db C:\Users\Administrator\.tam\memory.db --apply
```

Expected: JSON report with `updated` count. No ambiguous records changed.

- [ ] **Step 7: Re-run live recall probe**

Use MCP or direct tests to verify:

```text
Codex default recall excludes Reasonix-only probe.
Explicit Reasonix recall returns Reasonix-only probe.
All-agent recall returns both with namespace metadata.
```

## Self-Review

- Spec coverage: covers namespace storage, Reasonix migration, default isolated recall, explicit cross-agent recall, same-scene multi-galaxy visualization, center star naming, label sizing, overlap, and future Reasonix writes.
- Placeholder scan: no unresolved placeholder markers remain in the task steps.
- Type consistency: the plan consistently uses `agent_namespace`, `agent_namespaces`, and `scope="all_agents"`.
- Risk note: Task 4 must inspect all recall tiers after editing; any tier that fetches records by ID must apply the namespace guard before adding results.

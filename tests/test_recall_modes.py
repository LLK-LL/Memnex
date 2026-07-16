"""Tests for memory_recall mode='index' and mode='timeline'.

Covers the standalone transforms in ``recall_modes.py`` plus an
integration check that the dispatcher wires them in without breaking
backward compatibility (``mode`` default = ``search``).
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# ── unit: index_response ─────────────────────────────────────


def _make_item(i: int, content: str, score: float = 0.5, **extra):
    base = {
        "id": i,
        "content": content,
        "score": score,
        "type": extra.pop("type", "fact"),
        "project": extra.pop("project", "demo"),
        "created_at": extra.pop("created_at", f"2026-04-{i:02d}T00:00:00Z"),
        "session_id": extra.pop("session_id", "s1"),
        "context": extra.pop("context", "ctx"),
        "tags": extra.pop("tags", []),
    }
    base.update(extra)
    return base


def test_mode_index_returns_only_metadata():
    from recall_modes import index_response

    raw = {
        "query": "auth",
        "results": {
            "fact": [_make_item(1, "jwt refresh tokens ok", score=0.8, context="WHY")],
        },
    }
    out = index_response(raw)
    assert out["mode"] == "index"
    assert out["total"] == 1
    [entry] = out["results"]
    assert set(entry.keys()) == {"id", "title", "score", "type", "project", "created_at"}
    # Explicitly verify no content/context leakage.
    assert "content" not in entry and "context" not in entry
    assert "session_id" not in entry and "tags" not in entry


def test_mode_index_title_truncated_to_80():
    from recall_modes import index_response

    long_body = "x" * 200
    raw = {"results": {"fact": [_make_item(1, long_body)]}}
    [entry] = index_response(raw)["results"]
    # 80 chars + "..." suffix
    assert entry["title"].endswith("...")
    assert len(entry["title"]) == 83


def test_mode_index_title_uses_first_line():
    from recall_modes import index_response

    raw = {"results": {"fact": [_make_item(1, "first line\nsecond line\nthird")]}}
    [entry] = index_response(raw)["results"]
    assert entry["title"] == "first line"


def test_mode_index_respects_limit_via_caller():
    """``index_response`` does not re-truncate — it trusts the underlying
    ``Recall.search`` limit. We verify that 3 items in → 3 items out, sorted
    by score desc across type groups.
    """
    from recall_modes import index_response

    raw = {
        "results": {
            "fact": [_make_item(1, "a", score=0.9), _make_item(2, "b", score=0.3)],
            "solution": [_make_item(3, "c", score=0.6)],
        },
    }
    out = index_response(raw)
    assert out["total"] == 3
    scores = [e["score"] for e in out["results"]]
    assert scores == sorted(scores, reverse=True)


def test_mode_index_skips_cognitive_expansion(monkeypatch, tmp_path):
    """Dispatcher must not attach cognitive/expansion blocks for index mode."""
    # Use a real Store so recall.search works, but intercept cognitive.
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    (tmp_path / "blobs").mkdir(exist_ok=True)
    (tmp_path / "chroma").mkdir(exist_ok=True)

    import server
    monkeypatch.setattr(server, "MEMORY_DIR", tmp_path)

    s = server.Store()
    server.store = s
    server.recall = server.Recall(s)
    server.SID = "sess-index-1"
    server.BRANCH = ""

    s.db.execute(
        "INSERT INTO sessions (id, started_at, project, status) VALUES (?, ?, ?, ?)",
        (server.SID, "2026-04-14T00:00:00Z", "demo", "open"),
    )
    s.db.commit()

    s.save_knowledge(
        sid=server.SID,
        content="Use Argon2id for password hashing in auth layer.",
        ktype="solution",
        project="demo",
        tags=["auth", "security"],
    )

    # Spy on cognitive enrichment — must not be called for index mode.
    cognitive_called = {"yes": False}

    def fake_get_v5(name, db):
        if name == "cognitive":
            cognitive_called["yes"] = True
        raise RuntimeError("blocked for test")

    monkeypatch.setattr(server, "_get_v5", fake_get_v5)

    out_raw = asyncio.run(server._do("memory_recall", {
        "query": "password hashing", "project": "demo",
        "mode": "index", "limit": 5,
    }))
    out = json.loads(out_raw)
    assert out["mode"] == "index"
    # Cognitive should be absent (skipped) and must not have been called.
    assert "cognitive" not in out
    assert cognitive_called["yes"] is False
    # Each entry must be minimal.
    if out["results"]:
        entry = out["results"][0]
        assert "content" not in entry
        assert "context" not in entry

    try:
        s.db.close()
    except Exception:
        pass


def test_mode_rag_dedupes_uses_cached_summary_and_prioritizes_failures():
    from recall_modes import rag_response

    class _DB:
        def execute(self, _sql: str, _params: list[int]):
            return self

        def fetchall(self):
            return [
                {"knowledge_id": 1, "representation": "summary", "content": "Same cached fix summary."},
                {"knowledge_id": 2, "representation": "summary", "content": "Same cached fix summary."},
            ]

    class _Store:
        db = _DB()

    raw = {
        "query": "error while applying patch",
        "results": {
            "fact": [
                _make_item(3, "General note about patch usage.", score=0.9, type="fact"),
            ],
            "solution": [
                _make_item(1, "Long solution body one.", score=0.7, type="solution",
                           tags=["phase:build"]),
                _make_item(2, "Long solution body two.", score=0.6, type="solution",
                           tags=["phase:build"]),
            ],
        },
    }

    out = rag_response(raw, _Store(), query=raw["query"], phase="build", limit=10)
    assert out["mode"] == "rag"
    assert out["strategy"]["failure_priority"] is True
    assert out["candidate_total"] == 3
    assert out["total"] == 2

    first = out["results"][0]
    assert first["type"] == "solution"
    assert first["summary"] == "Same cached fix summary."
    assert first["summary_source"] == "summary"
    assert first["duplicate_count"] == 2
    assert first["related_ids"] == [1, 2]
    assert first["phase_match"] is True
    assert "content" not in first


def test_mode_rag_prioritizes_specific_preference_over_governance():
    from recall_modes import rag_response

    raw = {
        "query": "QR code output preference",
        "results": {
            "decision": [
                _make_item(
                    352,
                    "Completed layer cleanup: promoted actionable preference-layer items.",
                    score=0.09,
                    type="decision",
                    project="global",
                    tags=["memory-governance", "preference-layer", "layer-cleanup"],
                ),
            ],
            "convention": [
                _make_item(
                    346,
                    "Preference layer index: when the user asks for memory iteration, run the full workflow.",
                    score=0.08,
                    type="convention",
                    project="global",
                    tags=["layer:preference", "user-preference", "memory-iteration", "iteration"],
                ),
                _make_item(
                    342,
                    "Preference layer: when the user asks for a QR code, provide terminal instructions or a QR-code URL by default.",
                    score=0.07,
                    type="convention",
                    project="global",
                    tags=["layer:preference", "user-preference", "qr", "output-format"],
                ),
            ],
        },
    }

    out = rag_response(raw, store=None, query=raw["query"], limit=5)

    assert out["strategy"]["preference_priority"] is True
    assert out["results"][0]["id"] == 342
    assert out["results"][0]["preference_match"] is True


def test_mode_rag_dispatch_skips_cognitive_expansion(monkeypatch, tmp_path):
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    (tmp_path / "blobs").mkdir(exist_ok=True)
    (tmp_path / "chroma").mkdir(exist_ok=True)

    import server
    monkeypatch.setattr(server, "MEMORY_DIR", tmp_path)

    s = server.Store()
    server.store = s
    server.recall = server.Recall(s)
    server.SID = "sess-rag-1"
    server.BRANCH = ""

    s.db.execute(
        "INSERT INTO sessions (id, started_at, project, status) VALUES (?, ?, ?, ?)",
        (server.SID, "2026-04-14T00:00:00Z", "demo", "open"),
    )
    s.db.commit()

    s.save_knowledge(
        sid=server.SID,
        content="Patch failure: use smaller ASCII-only apply_patch context.",
        ktype="solution",
        project="demo",
        tags=["phase:build", "pitfalls"],
    )

    cognitive_called = {"yes": False}

    def fake_get_v5(name, db):
        if name == "cognitive":
            cognitive_called["yes"] = True
        raise RuntimeError("blocked for test")

    monkeypatch.setattr(server, "_get_v5", fake_get_v5)

    out_raw = asyncio.run(server._do("memory_recall", {
        "query": "patch failure",
        "project": "demo",
        "mode": "rag",
        "phase": "build",
        "limit": 5,
    }))
    out = json.loads(out_raw)
    assert out["mode"] == "rag"
    assert cognitive_called["yes"] is False
    assert "cognitive" not in out
    assert out["results"], "rag mode returned nothing"
    entry = out["results"][0]
    assert "summary" in entry
    assert "content" not in entry
    assert entry["phase_match"] is True

    try:
        s.db.close()
    except Exception:
        pass


# ── unit: timeline_response ──────────────────────────────────


class _FakeStore:
    """Minimal stand-in for Store with just a ``db`` exposing fetchall rows."""

    def __init__(self, rows: list[dict]):
        self._rows = rows

        class _DB:
            def __init__(self, parent):
                self._parent = parent

            def execute(self, sql: str, params: tuple):
                return _FakeCursor(self._parent, sql, params)

        self.db = _DB(self)


class _FakeRow(dict):
    """dict subclass that mimics sqlite3.Row's ``keys()`` + ``__getitem__``."""

    def keys(self):  # noqa: D401
        return super().keys()


class _FakeCursor:
    def __init__(self, store: _FakeStore, sql: str, params: tuple):
        self._store = store
        self._sql = sql
        self._params = params

    def fetchall(self):
        rows = [_FakeRow(r) for r in self._store._rows]
        sql = self._sql
        # Very light SQL interpretation — good enough for the neighbour logic.
        before = "created_at < ?" in sql
        after = "created_at > ?" in sql
        session_filtered = "session_id=?" in sql

        if session_filtered:
            sid = self._params[0]
            pivot_ca = self._params[1]
            limit = self._params[-1]
            filt = [r for r in rows if r.get("session_id") == sid and r.get("status") == "active"]
        else:
            pivot_ca = self._params[0]
            limit = self._params[-1]
            filt = [r for r in rows if r.get("status") == "active"]

        if before:
            filt = [r for r in filt if (r.get("created_at") or "") < pivot_ca]
            filt.sort(key=lambda r: r.get("created_at") or "", reverse=True)
        elif after:
            filt = [r for r in filt if (r.get("created_at") or "") > pivot_ca]
            filt.sort(key=lambda r: r.get("created_at") or "")

        return filt[:limit]


def test_mode_timeline_adds_neighbors():
    from recall_modes import timeline_response

    # Session s1 has 5 records by created_at. Anchor hit = id=3.
    all_rows = [
        {"id": 1, "session_id": "s1", "type": "fact", "content": "c1",
         "project": "demo", "created_at": "2026-04-10T10:00:00Z", "status": "active"},
        {"id": 2, "session_id": "s1", "type": "fact", "content": "c2",
         "project": "demo", "created_at": "2026-04-10T10:05:00Z", "status": "active"},
        {"id": 3, "session_id": "s1", "type": "solution", "content": "hit",
         "project": "demo", "created_at": "2026-04-10T10:10:00Z", "status": "active"},
        {"id": 4, "session_id": "s1", "type": "fact", "content": "c4",
         "project": "demo", "created_at": "2026-04-10T10:15:00Z", "status": "active"},
        {"id": 5, "session_id": "s1", "type": "fact", "content": "c5",
         "project": "demo", "created_at": "2026-04-10T10:20:00Z", "status": "active"},
    ]
    fake = _FakeStore(all_rows)

    raw = {
        "results": {
            "solution": [_make_item(3, "hit", score=0.9,
                                    session_id="s1",
                                    created_at="2026-04-10T10:10:00Z")],
        },
    }
    out = timeline_response(raw, fake, neighbors=2, limit=5)
    assert out["mode"] == "timeline"
    ids = [e["id"] for e in out["results"]]
    # Anchor plus 2 before + 2 after — ordered chronologically.
    assert ids == [1, 2, 3, 4, 5]
    roles = [e.get("role") for e in out["results"]]
    assert roles.count("hit") == 1
    assert roles.count("neighbor") == 4


def test_mode_timeline_no_duplicates():
    from recall_modes import timeline_response

    all_rows = [
        {"id": i, "session_id": "s1", "type": "fact", "content": f"c{i}",
         "project": "demo", "created_at": f"2026-04-10T10:{i:02d}:00Z",
         "status": "active"}
        for i in range(1, 6)
    ]
    fake = _FakeStore(all_rows)

    # Two hits — id=2 and id=4 — with overlapping neighbours.
    raw = {
        "results": {
            "fact": [
                _make_item(2, "c2", score=0.8, session_id="s1",
                           created_at="2026-04-10T10:02:00Z"),
                _make_item(4, "c4", score=0.7, session_id="s1",
                           created_at="2026-04-10T10:04:00Z"),
            ],
        },
    }
    out = timeline_response(raw, fake, neighbors=2, limit=5)
    ids = [e["id"] for e in out["results"]]
    # No duplicates despite overlapping windows.
    assert len(ids) == len(set(ids))
    # And both anchors must still be marked role=hit.
    hits = [e for e in out["results"] if e.get("role") == "hit"]
    assert {h["id"] for h in hits} == {2, 4}


def test_mode_timeline_falls_back_when_no_session_neighbors():
    """When ``session_id`` is empty, neighbour lookup falls back to global
    chronology so the hit still gets context."""
    from recall_modes import timeline_response

    all_rows = [
        {"id": 10, "session_id": "other", "type": "fact", "content": "earlier",
         "project": "demo", "created_at": "2026-04-10T09:00:00Z", "status": "active"},
        {"id": 20, "session_id": "other", "type": "fact", "content": "later",
         "project": "demo", "created_at": "2026-04-10T11:00:00Z", "status": "active"},
    ]
    fake = _FakeStore(all_rows)

    raw = {
        "results": {
            "fact": [_make_item(99, "anchor", score=0.9,
                                session_id="",  # no session info
                                created_at="2026-04-10T10:00:00Z")],
        },
    }
    out = timeline_response(raw, fake, neighbors=1, limit=5)
    ids = [e["id"] for e in out["results"]]
    # Fallback must fetch one before and one after the anchor.
    assert 10 in ids
    assert 20 in ids
    assert 99 in ids


# ── integration: backward compat ─────────────────────────────


def test_memory_recall_defaults_to_rag_and_explicit_search_keeps_legacy_shape(monkeypatch, tmp_path):
    """Default call (no ``mode=``) must return the legacy ``results`` dict
    shape grouped by type — existing callers break otherwise.
    """
    (tmp_path / "blobs").mkdir(exist_ok=True)
    (tmp_path / "chroma").mkdir(exist_ok=True)

    import server
    monkeypatch.setattr(server, "MEMORY_DIR", tmp_path)
    s = server.Store()
    server.store = s
    server.recall = server.Recall(s)
    server.SID = "sess-compat-1"
    server.BRANCH = ""
    s.db.execute(
        "INSERT INTO sessions (id, started_at, project, status) VALUES (?, ?, ?, ?)",
        (server.SID, "2026-04-14T00:00:00Z", "demo", "open"),
    )
    s.db.commit()
    s.save_knowledge(
        sid=server.SID,
        content="Use Postgres row-level security for multi-tenant SaaS.",
        ktype="solution", project="demo", tags=["db"],
    )

    # Avoid cognitive engine side effects.
    monkeypatch.setattr(server, "_get_v5", lambda *a, **kw: (_ for _ in ()).throw(RuntimeError()))

    raw = asyncio.run(server._do("memory_recall", {
        "query": "row-level security", "project": "demo",
    }))
    out = json.loads(raw)
    assert out["mode"] == "rag"
    assert isinstance(out["results"], list)
    if out["results"]:
        assert "summary" in out["results"][0]
        assert "content" not in out["results"][0]

    raw_search = asyncio.run(server._do("memory_recall", {
        "query": "row-level security", "project": "demo", "mode": "search",
    }))
    out_search = json.loads(raw_search)
    assert "results" in out_search
    assert isinstance(out_search["results"], dict)
    assert out_search.get("mode") != "rag"

    try:
        s.db.close()
    except Exception:
        pass


def test_memory_recall_rag_overfetches_before_compact_rerank(monkeypatch):
    import server

    calls = {}

    class _Recall:
        def search(self, *args, **_kwargs):
            calls["limit"] = args[3]
            return {
                "query": args[0],
                "results": {
                    "fact": [
                        _make_item(
                            663,
                            "academic-search paper-search ccswitch exact config",
                            score=0.1,
                            type="fact",
                            project="global",
                        ),
                    ],
                },
            }

    class _DB:
        def execute(self, *_args, **_kwargs):
            raise RuntimeError("no representation cache in this fixture")

    class _Store:
        db = _DB()

    monkeypatch.setattr(server, "recall", _Recall())
    monkeypatch.setattr(server, "store", _Store())
    monkeypatch.setattr(server, "_monitor_recall_event", lambda *_args, **_kwargs: None)

    raw = asyncio.run(server._do("memory_recall", {
        "query": "academic-search paper-search ccswitch",
        "mode": "rag",
        "limit": 5,
    }))
    out = json.loads(raw)

    assert calls["limit"] == 20
    assert out["mode"] == "rag"
    assert out["total"] == 1


def test_memory_recall_include_cognitive_false_skips_cognitive(monkeypatch, tmp_path):
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    (tmp_path / "blobs").mkdir(exist_ok=True)
    (tmp_path / "chroma").mkdir(exist_ok=True)

    import server
    monkeypatch.setattr(server, "MEMORY_DIR", tmp_path)

    s = server.Store()
    server.store = s
    server.recall = server.Recall(s)
    server.SID = "sess-no-cognitive-1"
    server.BRANCH = ""
    s.db.execute(
        "INSERT INTO sessions (id, started_at, project, status) VALUES (?, ?, ?, ?)",
        (server.SID, "2026-04-14T00:00:00Z", "demo", "open"),
    )
    s.db.commit()
    s.save_knowledge(
        sid=server.SID,
        content="Use compact rule context before recall.",
        ktype="convention", project="demo", tags=["memory"],
    )

    cognitive_called = {"yes": False}

    def fake_get_v5(name, db):
        if name == "cognitive":
            cognitive_called["yes"] = True
        raise RuntimeError("blocked for test")

    monkeypatch.setattr(server, "_get_v5", fake_get_v5)

    raw = asyncio.run(server._do("memory_recall", {
        "query": "compact rule context",
        "project": "demo",
        "include_cognitive": False,
        "detail": "compact",
    }))
    out = json.loads(raw)
    assert "results" in out
    assert "cognitive" not in out
    assert cognitive_called["yes"] is False

    try:
        s.db.close()
    except Exception:
        pass


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


def test_graph_expand_decision_skips_entity_only_auto(monkeypatch):
    import server

    monkeypatch.setattr(server, "HAS_GRAPH_EXPAND", True)
    monkeypatch.setenv("MEMORY_GRAPH_EXPAND", "1")

    decision = server._graph_expand_decision(
        has_graph_expand=server.HAS_GRAPH_EXPAND,
        ranked_count=1,
        explicit_expand_context=False,
        router_classification=SimpleNamespace(
            kind="hybrid",
            graph_families=["entity"],
        ),
    )

    assert decision.apply is False
    assert decision.reason == "skipped_entity_only"
    assert decision.edge_families == []


def test_graph_expand_decision_allows_relational_auto(monkeypatch):
    import server

    monkeypatch.setattr(server, "HAS_GRAPH_EXPAND", True)
    monkeypatch.setenv("MEMORY_GRAPH_EXPAND", "1")

    decision = server._graph_expand_decision(
        has_graph_expand=server.HAS_GRAPH_EXPAND,
        ranked_count=1,
        explicit_expand_context=False,
        router_classification=SimpleNamespace(
            kind="relational",
            graph_families=["entity"],
        ),
    )

    assert decision.apply is True
    assert decision.reason == "auto_relational"
    assert decision.edge_families == ["entity"]


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
    assert calls[0][1]["project"] == ["demo"]
    assert out["graph_expand_applied"] is True
    assert out["graph_expand_reason"] == "auto_temporal"
    assert out["graph_expand_families"] == ["temporal"]

    store.db.close()


def test_project_path_aliases_recall_slash_variants_without_basename_merging(
    monkeypatch, tmp_path,
):
    import server

    monkeypatch.setattr(server, "MEMORY_DIR", tmp_path)
    monkeypatch.setenv("MEMORY_GRAPH_EXPAND", "0")
    (tmp_path / "blobs").mkdir(exist_ok=True)
    (tmp_path / "chroma").mkdir(exist_ok=True)

    store = server.Store()
    recall = server.Recall(store)
    sid = "sess-project-aliases"
    store.session_start(sid, project=r"D:\MemoryGalaxy3DResearch")

    canonical_id, *_ = store.save_knowledge(
        sid=sid,
        content="legacy alias marker canonical project record",
        ktype="fact",
        project="D:/MemoryGalaxy3DResearch",
        skip_dedup=True,
    )
    backslash_id, *_ = store.save_knowledge(
        sid=sid,
        content="legacy alias marker backslash project record",
        ktype="fact",
        project="D:/MemoryGalaxy3DResearch",
        skip_dedup=True,
    )
    slash_id, *_ = store.save_knowledge(
        sid=sid,
        content="legacy alias marker slash project record",
        ktype="fact",
        project="D:/MemoryGalaxy3DResearch",
        skip_dedup=True,
    )
    store.db.execute(
        "UPDATE knowledge SET project=? WHERE id=?",
        (r"D:\MemoryGalaxy3DResearch", backslash_id),
    )
    store.db.execute(
        "UPDATE knowledge SET project=? WHERE id=?",
        ("D:/MemoryGalaxy3DResearch", slash_id),
    )
    store.db.commit()

    normalized_id, *_ = store.save_knowledge(
        sid=sid,
        content="new project path is normalized on write",
        ktype="fact",
        project="D:/MemoryGalaxy3DResearch",
        skip_dedup=True,
    )
    normalized_row = store.db.execute(
        "SELECT project FROM knowledge WHERE id=?", (normalized_id,),
    ).fetchone()

    out = recall.search(
        "legacy alias marker",
        project="D:/MemoryGalaxy3DResearch",
        limit=5,
        detail="summary",
    )
    ids = {item["id"] for group in out["results"].values() for item in group}

    assert normalized_row["project"] == "D:/MemoryGalaxy3DResearch"
    assert {canonical_id, backslash_id, slash_id}.issubset(ids)
    assert out["project_canonical"] == "D:/MemoryGalaxy3DResearch"
    assert set(out["project_aliases"]) == {
        r"D:\MemoryGalaxy3DResearch",
        "D:/MemoryGalaxy3DResearch",
    }

    store.db.close()


def _seed_explicit_project_alias_recall(
    monkeypatch, tmp_path, *, alias, canonical, records,
):
    import server

    monkeypatch.setattr(server, "MEMORY_DIR", tmp_path)
    monkeypatch.setenv("MEMORY_GRAPH_EXPAND", "0")
    (tmp_path / "blobs").mkdir(exist_ok=True)
    (tmp_path / "chroma").mkdir(exist_ok=True)

    store = server.Store()
    recall = server.Recall(store)
    sid = "sess-explicit-project-alias"
    store.session_start(sid, project=canonical)
    ids = {}
    for label, project in records.items():
        kid, *_ = store.save_knowledge(
            sid=sid,
            content=f"explicit alias equivalence marker {label}",
            ktype="fact",
            project=project,
            skip_dedup=True,
        )
        ids[label] = kid
    store.db.execute(
        "INSERT INTO project_aliases(alias, canonical) VALUES (?, ?)",
        (alias, canonical),
    )
    store.db.commit()
    return store, recall, ids


def test_explicit_project_alias_recall_preserves_name_and_path_identity(
    monkeypatch, tmp_path,
):
    store, recall, ids = _seed_explicit_project_alias_recall(
        monkeypatch,
        tmp_path,
        alias="D:/MemoryGalaxy3DResearch",
        canonical="MemoryGalaxy3DResearch",
        records={
            "name": "MemoryGalaxy3DResearch",
            "path": "D:/MemoryGalaxy3DResearch",
            "unrelated": "D:/OtherProject",
        },
    )

    try:
        for project in ("MemoryGalaxy3DResearch", "D:/MemoryGalaxy3DResearch"):
            out = recall.search(
                "explicit alias equivalence marker",
                project=project,
                limit=5,
                detail="summary",
            )
            result_ids = {
                item["id"] for group in out["results"].values() for item in group
            }
            assert {ids["name"], ids["path"]}.issubset(result_ids)
            assert ids["unrelated"] not in result_ids
    finally:
        store.db.close()


def test_explicit_project_alias_recall_maps_ti_al_english_and_chinese(
    monkeypatch, tmp_path,
):
    english = "Ti-Al explosive welding SPH-FEM analysis"
    chinese = (
        "\u949b\u94dd\u7206\u70b8\u710a\u63a5\u754c\u9762\u6ce2"
        "\u70ed\u5851\u6027\u8026\u5408SPH-FEM\u5206\u6790"
    )
    store, recall, ids = _seed_explicit_project_alias_recall(
        monkeypatch,
        tmp_path,
        alias=english,
        canonical=chinese,
        records={"mapped": chinese},
    )

    try:
        for project in (english, chinese):
            out = recall.search(
                "explicit alias equivalence marker",
                project=project,
                limit=5,
                detail="summary",
            )
            result_ids = {
                item["id"] for group in out["results"].values() for item in group
            }
            assert ids["mapped"] in result_ids
    finally:
        store.db.close()


def test_relevance_gate_drops_zero_overlap_before_graph_expansion(
    monkeypatch, tmp_path,
):
    store, recall, _kid = _new_recall_with_knowledge(
        monkeypatch,
        tmp_path,
        "南京理工项目 报告",
    )
    store.db.execute(
        "UPDATE knowledge SET project=? WHERE content=?",
        ("南京理工项目", "南京理工项目 报告"),
    )
    store.db.commit()
    monkeypatch.setenv("MEMORY_GRAPH_EXPAND", "1")
    monkeypatch.delenv("MEMORY_RECALL_MIN_COVERAGE", raising=False)

    def fail_expand(*_args, **_kwargs):
        raise AssertionError("graph expansion must not run without a relevant seed")

    import server
    monkeypatch.setattr(server, "_graph_expand", fail_expand)

    out = recall.search(
        "南京理工项目 吸收能量曲线 报告 SPH ALE",
        project="南京理工项目",
        limit=5,
        detail="summary",
    )

    assert out["total"] == 0
    assert out["results"] == {}
    assert out["relevance_gate_applied"] is True
    assert out["relevance_gate_reason"] == "below_minimum"
    assert out["relevance_gate_best_coverage"] == 0.0
    assert out["relevance_gate_filtered_count"] >= 1
    assert out["graph_expand_reason"] == "skipped_no_seed_results"

    store.db.close()


def test_relevance_gate_keeps_raw_content_overlap_and_reports_terms(
    monkeypatch, tmp_path,
):
    store, recall, kid = _new_recall_with_knowledge(
        monkeypatch,
        tmp_path,
        "energy curve processing for projectile trajectory analysis",
    )
    monkeypatch.setenv("MEMORY_GRAPH_EXPAND", "0")
    monkeypatch.setenv("MEMORY_RECALL_MIN_COVERAGE", "0.1")

    out = recall.search(
        "energy curve projectile trajectory",
        project="demo",
        limit=5,
        detail="summary",
    )
    items = [item for group in out["results"].values() for item in group]

    assert out["relevance_gate_applied"] is True
    assert out["relevance_gate_reason"] == "passed"
    assert out["relevance_gate_best_coverage"] == 1.0
    assert items[0]["id"] == kid
    assert items[0]["query_coverage"] == 1.0
    assert set(items[0]["matched_query_terms"]) == {
        "energy", "curve", "projectile", "trajectory",
    }

    store.db.close()


def test_relevance_gate_default_requires_quarter_query_coverage(
    monkeypatch, tmp_path,
):
    store, recall, weak_id = _new_recall_with_knowledge(
        monkeypatch,
        tmp_path,
        "alpha beta unrelated record",
    )
    strong_id, *_ = store.save_knowledge(
        sid="sess-graph-routing",
        content="alpha beta gamma delta relevant record",
        ktype="fact",
        project="demo",
        skip_dedup=True,
    )
    monkeypatch.setenv("MEMORY_GRAPH_EXPAND", "0")
    monkeypatch.delenv("MEMORY_RECALL_MIN_COVERAGE", raising=False)

    out = recall.search(
        "alpha beta gamma delta epsilon zeta theta lambda omega",
        project="demo",
        limit=5,
        detail="summary",
    )
    ids = [item["id"] for group in out["results"].values() for item in group]

    assert out["relevance_gate_threshold"] == 0.25
    assert strong_id in ids
    assert weak_id not in ids
    assert out["relevance_gate_filtered_count"] >= 1

    store.db.close()


def test_query_coverage_ignores_project_name_and_generic_report_terms():
    from recall_modes import _query_coverage_terms

    terms = _query_coverage_terms("南京理工项目 吸收能量曲线 报告 SPH ALE")

    assert "南京理工项目" not in terms
    assert "报告" not in terms
    assert "吸收能量曲线" in terms
    assert "SPH" in terms
    assert "ALE" in terms


def test_query_coverage_requires_boundaries_for_latin_technical_tokens():
    from recall_modes import _query_coverage, _query_coverage_terms

    terms = _query_coverage_terms("南京理工项目 吸收能量曲线 报告 SPH ALE")
    coverage, matched = _query_coverage(
        {"context": "", "tags": []},
        content="LZMA codec is unsupported for this project report.",
        summary="",
        query_terms=terms,
    )

    assert "ALE" not in matched
    assert "SPH" not in matched
    assert coverage == 0.0


def test_relevance_gate_filters_project_report_only_overlap(
    monkeypatch, tmp_path,
):
    store, recall, _kid = _new_recall_with_knowledge(
        monkeypatch,
        tmp_path,
        "南京理工项目 报告",
    )
    store.db.execute(
        "UPDATE knowledge SET project=? WHERE content=?",
        ("南京理工项目", "南京理工项目 报告"),
    )
    store.db.commit()
    monkeypatch.setenv("MEMORY_GRAPH_EXPAND", "0")
    monkeypatch.delenv("MEMORY_RECALL_MIN_COVERAGE", raising=False)

    out = recall.search(
        "南京理工项目 吸收能量曲线 报告 SPH ALE",
        project="南京理工项目",
        limit=5,
        detail="summary",
    )

    assert out["relevance_gate_applied"] is True
    assert out["relevance_gate_reason"] == "below_minimum"
    assert out["relevance_gate_best_coverage"] < out["relevance_gate_threshold"]
    assert out["total"] == 0
    assert out["results"] == {}

    store.db.close()


def test_recall_search_threads_phase_to_rag_phase_match(monkeypatch, tmp_path):
    from recall_modes import rag_response

    store, recall, kid = _new_recall_with_knowledge(
        monkeypatch,
        tmp_path,
        "build phase deployment checklist for phase matching",
    )
    store.db.execute(
        "UPDATE knowledge SET tags=? WHERE id=?",
        ('["phase:build"]', kid),
    )
    store.db.commit()
    monkeypatch.setenv("MEMORY_GRAPH_EXPAND", "0")

    build_raw = recall.search(
        "build phase deployment checklist",
        project="demo",
        limit=5,
        detail="full",
        phase="build",
    )
    plan_raw = recall.search(
        "build phase deployment checklist",
        project="demo",
        limit=5,
        detail="full",
        phase="plan",
    )

    build_out = rag_response(
        build_raw, store, query=build_raw["query"], phase=build_raw.get("phase")
    )
    plan_out = rag_response(
        plan_raw, store, query=plan_raw["query"], phase=plan_raw.get("phase")
    )

    assert build_raw["phase"] == "build"
    assert plan_raw["phase"] == "plan"
    assert build_out["results"][0]["id"] == kid
    assert build_out["results"][0]["phase_match"] is True
    assert plan_out["results"][0]["id"] == kid
    assert plan_out["results"][0]["phase_match"] is False

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


def test_graph_expand_explicit_override_runs_for_semantic_query(monkeypatch, tmp_path):
    store, recall, graph_id = _new_recall_with_knowledge(
        monkeypatch,
        tmp_path,
        "alpha seed one for explicit semantic graph expansion",
    )
    monkeypatch.setenv("MEMORY_GRAPH_EXPAND", "0")
    monkeypatch.setenv("MEMORY_GRAPH_EXPAND_BOOST", "100")
    monkeypatch.setenv("MEMORY_GRAPH_EXPAND_MAX_RATIO", "0.5")
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

    items = [item for group in out["results"].values() for item in group]
    ids = [item["id"] for item in items]
    primary = next(item for item in items if item["id"] == graph_id)
    neighbour = next(item for item in items if item["id"] == graph_id + 1000)
    assert calls
    assert calls[0][1]["budget"] == 2
    assert calls[0][1]["edge_families"] is None
    assert out["graph_expand_applied"] is True
    assert out["graph_expand_reason"] == "explicit_expand_context"
    assert graph_id + 1000 in ids
    assert neighbour["score"] <= primary["score"] * 0.5
    assert neighbour["rrf_score"] <= primary["rrf_score"]

    store.db.close()


def test_graph_expand_scores_compete_with_seed_budget(monkeypatch, tmp_path):
    (tmp_path / "blobs").mkdir(exist_ok=True)
    (tmp_path / "chroma").mkdir(exist_ok=True)

    import server
    monkeypatch.setattr(server, "MEMORY_DIR", tmp_path)
    monkeypatch.setattr(server, "HAS_GRAPH_EXPAND", True)
    monkeypatch.setenv("MEMORY_GRAPH_EXPAND", "1")

    s = server.Store()
    recall = server.Recall(s)
    sid = "sess-graph-budget-1"
    s.db.execute(
        "INSERT INTO sessions (id, started_at, project, status) VALUES (?, ?, ?, ?)",
        (sid, "2026-04-14T00:00:00Z", "demo", "open"),
    )
    s.db.commit()

    seed_a, *_ = s.save_knowledge(
        sid=sid, content="alpha seed one for hybrid recall", ktype="fact",
        project="demo", skip_dedup=True,
    )
    seed_b, *_ = s.save_knowledge(
        sid=sid, content="alpha seed two for hybrid recall", ktype="fact",
        project="demo", skip_dedup=True,
    )
    graph_id, *_ = s.save_knowledge(
        sid=sid, content="structural neighbour chosen by magma graph", ktype="fact",
        project="demo", skip_dedup=True,
    )

    seen_seed_ids = []

    def fake_expand(_db, seed_ids, **kwargs):
        seen_seed_ids.extend(seed_ids)
        assert kwargs["budget"] == 2
        return [(graph_id, 10.0)]

    def fake_fetch(_db, ids):
        assert ids == [graph_id]
        return [{
            "id": graph_id,
            "type": "fact",
            "content": "structural neighbour chosen by magma graph",
            "context": "",
            "project": "demo",
            "tags": [],
            "status": "active",
            "confidence": 1.0,
            "source": "",
            "created_at": "2026-04-14T00:00:00Z",
            "last_confirmed": "2026-04-14T00:00:00Z",
            "recall_count": 0,
            "session_id": sid,
        }]

    monkeypatch.setattr(server, "_graph_expand", fake_expand)
    monkeypatch.setattr(server, "_graph_fetch", fake_fetch)

    out = recall.search(
        "alpha",
        project="demo",
        limit=3,
        detail="summary",
        expand_context=True,
        expand_budget=2,
    )
    ids = [item["id"] for group in out["results"].values() for item in group]

    assert seen_seed_ids == [seed_a, seed_b]
    assert len(ids) == 3
    assert ids[:2] == [seed_a, seed_b]
    assert graph_id in ids

    try:
        s.db.close()
    except Exception:
        pass


def test_literal_identifier_match_survives_rrf_importance_boosts(monkeypatch, tmp_path):
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    (tmp_path / "blobs").mkdir(exist_ok=True)
    (tmp_path / "chroma").mkdir(exist_ok=True)

    import server
    monkeypatch.setattr(server, "MEMORY_DIR", tmp_path)

    s = server.Store()
    server.store = s
    server.recall = server.Recall(s)
    server.SID = "sess-literal-1"
    server.BRANCH = ""
    s.db.execute(
        "INSERT INTO sessions (id, started_at, project, status) VALUES (?, ?, ?, ?)",
        (server.SID, "2026-04-14T00:00:00Z", "demo", "open"),
    )
    s.db.commit()

    marker = "UNIQUE_LITERAL_PROBE_20260613"
    literal_id, *_ = s.save_knowledge(
        sid=server.SID,
        content=f"Low importance diagnostic record with marker {marker}.",
        ktype="fact",
        project="demo",
        tags=["diagnostic"],
        importance="low",
    )
    for i in range(12):
        s.save_knowledge(
            sid=server.SID,
            content=f"Critical memory governance and routing layer record {i}.",
            ktype="decision",
            project="demo",
            tags=["memory-governance", "routing-layer"],
            importance="critical",
        )

    monkeypatch.setattr(server, "_get_v5", lambda *a, **kw: (_ for _ in ()).throw(RuntimeError()))
    out = server.Recall(s).search(
        marker,
        project="demo",
        ktype="all",
        limit=5,
        detail="full",
        fusion="rrf",
    )

    found = [
        item["id"]
        for group in out["results"].values()
        for item in group
    ]
    assert literal_id in found

    try:
        s.db.close()
    except Exception:
        pass


def test_exact_entity_coverage_outranks_popular_generic_mcp_record():
    from recall_modes import rag_response

    query = "配置 academic-search MCP paper-search Codex++ ccswitch 模板 MCP 配置"
    raw = {
        "query": query,
        "results": {
            "fact": [
                _make_item(
                    451,
                    "Playwright MCP was installed and registered in Codex as a global MCP server.",
                    score=0.09,
                    rrf_score=0.08,
                    type="fact",
                    project="global",
                    tags=["mcp", "codex", "playwright-mcp", "ui-testing"],
                    importance="high",
                ),
                _make_item(
                    663,
                    (
                        "Configured academic literature MCPs for Codex: academic-search is "
                        "registered in config.toml; paper-search is registered using uvx "
                        "paper-search-mcp; ccswitch templates preserve both MCP blocks."
                    ),
                    score=0.08,
                    rrf_score=0.075,
                    type="fact",
                    project="global",
                    tags=["mcp", "codex", "academic-search", "paper-search", "ccswitch"],
                    importance="high",
                ),
            ],
        },
    }

    out = rag_response(raw, store=None, query=query, limit=2)

    assert out["results"][0]["id"] == 663
    assert out["results"][0]["query_coverage"] > out["results"][1]["query_coverage"]


def test_rag_query_coverage_ignores_generated_summary_and_project_name():
    from recall_modes import rag_response

    raw = {
        "query": "energy curve projectile trajectory",
        "graph_expand_applied": False,
        "graph_expand_reason": "skipped_semantic",
        "relevance_gate_applied": True,
        "relevance_gate_reason": "passed",
        "results": {
            "fact": [{
                **_make_item(
                    901,
                    "7-Zip executable path and archive extraction notes",
                    score=0.2,
                    type="fact",
                    project="energy curve projectile trajectory",
                ),
                "context": "unrelated Windows tooling",
                "via": ["semantic"],
            }],
        },
    }

    class _DB:
        def execute(self, *_args, **_kwargs):
            return [{
                "knowledge_id": 901,
                "representation": "summary",
                "content": "energy curve projectile trajectory",
            }]

    out = rag_response(
        raw,
        store=SimpleNamespace(db=_DB()),
        query=raw["query"],
        limit=1,
    )

    assert out["results"][0]["query_coverage"] == 0.0
    assert out["results"][0]["matched_query_terms"] == []
    assert out["results"][0]["via"] == ["semantic"]
    assert out["graph_expand_reason"] == "skipped_semantic"
    assert out["relevance_gate_reason"] == "passed"


def test_recall_count_is_telemetry_not_relevance_boost():
    import inspect
    import server

    source = inspect.getsource(server.Recall._search_impl)

    assert "recall_boost" not in source
    assert 'item["decay_factor"] = decay' in source
    assert "return Store._decay_factor(lc, hl)" in source


def test_memory_recall_rag_error_logs_and_falls_back(monkeypatch, tmp_path):
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    (tmp_path / "blobs").mkdir(exist_ok=True)
    (tmp_path / "chroma").mkdir(exist_ok=True)

    import server
    import recall_modes
    monkeypatch.setattr(server, "MEMORY_DIR", tmp_path)

    s = server.Store()
    server.store = s
    server.recall = server.Recall(s)
    server.SID = "sess-rag-error-1"
    server.BRANCH = ""
    s.db.execute(
        "INSERT INTO sessions (id, started_at, project, status) VALUES (?, ?, ?, ?)",
        (server.SID, "2026-04-14T00:00:00Z", "demo", "open"),
    )
    s.db.commit()
    s.save_knowledge(
        sid=server.SID,
        content="RAG error fallback should preserve an index result.",
        ktype="solution", project="demo", tags=["memory"],
    )

    def broken_rag(*_args, **_kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(recall_modes, "rag_response", broken_rag)

    raw = asyncio.run(server._do("memory_recall", {
        "query": "rag error fallback", "project": "demo", "mode": "rag",
    }))
    out = json.loads(raw)
    assert out["mode"] == "rag_fallback_index"
    assert out["rag_error"] == "boom"
    assert isinstance(out["results"], list)

    row = s.db.execute(
        "SELECT description, fix, tags FROM errors WHERE project='demo' ORDER BY id DESC LIMIT 1"
    ).fetchone()
    assert row is not None
    assert "RAG workflow failed" in row["description"]
    assert "downgraded this call to index_response" in row["fix"]
    assert "memory_recall" in row["tags"]

    try:
        s.db.close()
    except Exception:
        pass

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

    out = recall.search("alpha", project="demo", limit=2, detail="summary")
    ids = [item["id"] for group in out["results"].values() for item in group]

    assert seen_seed_ids == [seed_a, seed_b]
    assert len(ids) == 2
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

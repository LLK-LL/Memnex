"""Tests for v10.1 async enrichment worker.

Covers:
  - enqueue puts a row with status='pending'
  - run_pending claims rows atomically and runs all stages
  - per-stage failures are isolated and logged in last_error
  - stages are idempotent (replaying a row twice does not duplicate audit rows)
  - retry up to MEMORY_ENRICH_MAX_ATTEMPTS, then status flips to 'failed'
  - quality_gate 'drop' verdict marks knowledge.status='quality_dropped'
    rather than physically removing the record
  - daemon thread starts only when MEMORY_ASYNC_ENRICHMENT=true
"""

from __future__ import annotations

import json
import sqlite3
import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import enrichment_worker as ew


# ──────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────


@pytest.fixture
def db():
    """Minimal SQLite with the columns each stage reads/writes."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT, type TEXT, content TEXT,
            project TEXT DEFAULT 'general',
            status TEXT DEFAULT 'active',
            importance TEXT DEFAULT 'medium',
            tags TEXT DEFAULT '[]', created_at TEXT
        );

        -- enrichment_queue (the unit under test)
        CREATE TABLE enrichment_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            knowledge_id INTEGER NOT NULL,
            session_id TEXT,
            project TEXT NOT NULL DEFAULT 'general',
            ktype TEXT NOT NULL,
            content_snapshot TEXT NOT NULL,
            tags_snapshot TEXT NOT NULL DEFAULT '[]',
            importance TEXT NOT NULL DEFAULT 'medium',
            skip_quality INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending','processing','done','failed')),
            attempts INTEGER NOT NULL DEFAULT 0,
            last_error TEXT,
            enqueued_at TEXT NOT NULL,
            started_at TEXT, finished_at TEXT
        );

        -- audit log targets the stages write into
        CREATE TABLE quality_gate_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            knowledge_id INTEGER, project TEXT, ktype TEXT,
            decision TEXT, total REAL, specificity REAL, actionability REAL,
            verifiability REAL, reason TEXT, threshold REAL,
            provider TEXT, model TEXT, latency_ms INTEGER,
            content TEXT, created_at TEXT NOT NULL
        );
        """
    )
    yield conn
    conn.close()


@pytest.fixture
def seed_record(db):
    """Insert a knowledge row and return its id."""
    cur = db.execute(
        "INSERT INTO knowledge (session_id, type, content, project, created_at) "
        "VALUES ('s1', 'fact', 'Postgres 18 настроен в claude-memory-server', 'p', '2026-04-27T10:00:00Z')"
    )
    db.commit()
    return cur.lastrowid


# ──────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────


def test_enabled_default_off(monkeypatch):
    monkeypatch.delenv("MEMORY_ASYNC_ENRICHMENT", raising=False)
    assert ew._enabled() is False


def test_enabled_when_true(monkeypatch):
    monkeypatch.setenv("MEMORY_ASYNC_ENRICHMENT", "true")
    assert ew._enabled() is True


def test_structural_consolidation_default_off(monkeypatch):
    monkeypatch.delenv("MEMORY_STRUCTURAL_CONSOLIDATION", raising=False)
    assert ew._structural_enabled() is False


def test_structural_3b_profile_caps_to_one_task(monkeypatch):
    monkeypatch.setenv("MEMORY_STRUCTURAL_CONSOLIDATION", "true")
    monkeypatch.setenv("MEMORY_STRUCTURAL_MODEL_SIZE", "3b")
    monkeypatch.setenv("MEMORY_STRUCTURAL_MAX_PER_TICK", "9")
    assert ew._structural_max_per_tick() == 1


def test_structural_throttle_skips_until_interval_elapsed(monkeypatch):
    monkeypatch.setenv("MEMORY_STRUCTURAL_CONSOLIDATION", "true")
    monkeypatch.setenv("MEMORY_STRUCTURAL_MIN_INTERVAL_SEC", "60")
    ew._STRUCTURAL_LAST_RUN = 100.0
    try:
        assert ew._structural_should_run(now=120.0) is False
        assert ew._structural_should_run(now=161.0) is True
    finally:
        ew._STRUCTURAL_LAST_RUN = 0.0


def test_parse_structural_edges_from_ollama_json():
    raw = """
    {"edges": [
      {"source": "install failure", "target": "missing package", "relation_type": "caused_by", "confidence": 0.82, "context": "Package was absent"},
      {"source": "missing package", "target": "pip install", "relation_type": "fixed_by", "confidence": 0.76, "context": "Install resolved it"},
      {"source": "", "target": "ignored", "relation_type": "caused_by"}
    ]}
    """

    edges = ew._parse_structural_edges(raw)

    assert edges == [
        {
            "source": "install failure",
            "target": "missing package",
            "relation_type": "caused_by",
            "confidence": 0.82,
            "context": "Package was absent",
        },
        {
            "source": "missing package",
            "target": "pip install",
            "relation_type": "fixed_by",
            "confidence": 0.76,
            "context": "Install resolved it",
        },
    ]


def test_structural_consolidation_writes_ollama_edges(db, seed_record, monkeypatch):
    db.executescript(
        """
        CREATE TABLE graph_nodes (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            name TEXT NOT NULL,
            content TEXT,
            properties TEXT,
            source TEXT,
            importance REAL DEFAULT 0.5,
            first_seen_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL,
            mention_count INTEGER DEFAULT 1,
            status TEXT DEFAULT 'active'
        );
        CREATE TABLE graph_edges (
            id TEXT PRIMARY KEY,
            source_id TEXT NOT NULL,
            target_id TEXT NOT NULL,
            relation_type TEXT NOT NULL,
            weight REAL DEFAULT 1.0,
            context TEXT,
            created_at TEXT NOT NULL,
            last_reinforced_at TEXT,
            reinforcement_count INTEGER DEFAULT 0,
            UNIQUE(source_id, target_id, relation_type)
        );
        CREATE TABLE knowledge_nodes (
            knowledge_id INTEGER,
            node_id TEXT,
            role TEXT DEFAULT 'related',
            strength REAL DEFAULT 1.0,
            PRIMARY KEY (knowledge_id, node_id)
        );
        """
    )
    monkeypatch.setenv("MEMORY_STRUCTURAL_CONSOLIDATION", "true")
    monkeypatch.setenv("MEMORY_STRUCTURAL_MIN_INTERVAL_SEC", "0")
    ew._STRUCTURAL_LAST_RUN = 0.0
    monkeypatch.setattr(
        ew,
        "_ollama_structural_call",
        lambda task: '{"edges":[{"source":"install failure","target":"missing package","relation_type":"caused_by","confidence":0.8,"context":"missing dependency"}]}',
    )
    task = ew.EnrichmentTask(
        id=1,
        knowledge_id=seed_record,
        session_id="s1",
        project="p",
        ktype="solution",
        content_snapshot="Install failed because a package was missing.",
        tags_snapshot=[],
        importance="medium",
        skip_quality=False,
        attempts=1,
    )

    try:
        ew._run_structural_consolidation(db, task)
    finally:
        ew._STRUCTURAL_LAST_RUN = 0.0

    edge = db.execute("SELECT relation_type, weight, context FROM graph_edges").fetchone()
    assert edge["relation_type"] == "caused_by"
    assert edge["weight"] == 0.8
    assert "missing dependency" in edge["context"]
    assert db.execute("SELECT COUNT(*) FROM knowledge_nodes").fetchone()[0] == 2


# ──────────────────────────────────────────────
# Enqueue
# ──────────────────────────────────────────────


def test_enqueue_creates_pending_row(db, seed_record):
    qid = ew.enqueue(
        db,
        knowledge_id=seed_record,
        session_id="s1",
        project="p",
        ktype="fact",
        content_snapshot="payload",
        tags_snapshot=["postgres", "infra"],
    )
    row = db.execute("SELECT * FROM enrichment_queue WHERE id=?", (qid,)).fetchone()
    assert row["status"] == "pending"
    assert row["attempts"] == 0
    assert row["knowledge_id"] == seed_record
    assert json.loads(row["tags_snapshot"]) == ["postgres", "infra"]


# ──────────────────────────────────────────────
# Claim
# ──────────────────────────────────────────────


def test_claim_pending_moves_rows_to_processing(db, seed_record):
    for i in range(3):
        ew.enqueue(db, knowledge_id=seed_record, session_id="s1",
                   project="p", ktype="fact",
                   content_snapshot=f"row {i}", tags_snapshot=[])
    tasks = ew._claim_pending(db, limit=2)
    assert len(tasks) == 2
    statuses = [r[0] for r in db.execute(
        "SELECT status FROM enrichment_queue ORDER BY id"
    ).fetchall()]
    assert statuses[:2] == ["processing", "processing"]
    assert statuses[2] == "pending"
    # attempts bumped
    assert all(t.attempts == 1 for t in tasks)


def test_claim_returns_empty_when_no_pending(db):
    assert ew._claim_pending(db, limit=5) == []


# ──────────────────────────────────────────────
# run_pending end-to-end with all stages stubbed out
# ──────────────────────────────────────────────


def _all_stages_succeed_no_op(*args, **kwargs):
    """Stub stage runner that does nothing — tests the queue mechanics."""
    return None


def test_run_pending_marks_done_when_stages_succeed(db, seed_record, monkeypatch):
    ew.enqueue(db, knowledge_id=seed_record, session_id="s1",
               project="p", ktype="fact",
               content_snapshot="payload", tags_snapshot=["postgres"])
    monkeypatch.setattr(ew, "_STAGES", [
        ("fake1", _all_stages_succeed_no_op),
        ("fake2", _all_stages_succeed_no_op),
    ])
    counts = ew.run_pending(db, max_rows=10)
    assert counts["done"] == 1
    assert counts["claimed"] == 1
    row = db.execute("SELECT status, last_error, finished_at FROM enrichment_queue").fetchone()
    assert row["status"] == "done"
    assert row["last_error"] is None
    assert row["finished_at"] is not None


def test_run_pending_isolates_one_failing_stage(db, seed_record, monkeypatch):
    ew.enqueue(db, knowledge_id=seed_record, session_id="s1",
               project="p", ktype="fact",
               content_snapshot="payload", tags_snapshot=[])
    calls = []

    def good(db, task, store=None):
        calls.append("good")

    def bad(db, task, store=None):
        calls.append("bad")
        raise RuntimeError("LLM provider down")

    monkeypatch.setattr(ew, "_STAGES", [
        ("good_first", good),
        ("bad_second", bad),
        ("good_third", good),
    ])
    counts = ew.run_pending(db, max_rows=10)
    # All three stages were attempted (fail isolation)
    assert calls == ["good", "bad", "good"]
    # Row marked retry-pending after first failure
    row = db.execute("SELECT status, last_error, attempts FROM enrichment_queue").fetchone()
    assert row["status"] == "pending"
    assert "bad_second" in row["last_error"]
    assert "LLM provider down" in row["last_error"]
    assert row["attempts"] == 1


def test_run_pending_marks_failed_after_max_attempts(db, seed_record, monkeypatch):
    monkeypatch.setenv("MEMORY_ENRICH_MAX_ATTEMPTS", "2")
    ew.enqueue(db, knowledge_id=seed_record, session_id="s1",
               project="p", ktype="fact",
               content_snapshot="payload", tags_snapshot=[])

    def always_fails(db, task, store=None):
        raise RuntimeError("permanent error")

    monkeypatch.setattr(ew, "_STAGES", [("only", always_fails)])
    # First attempt → retry
    ew.run_pending(db, max_rows=10)
    # Second attempt → should flip to failed
    ew.run_pending(db, max_rows=10)
    row = db.execute("SELECT status, attempts FROM enrichment_queue").fetchone()
    assert row["status"] == "failed"
    assert row["attempts"] == 2


# ──────────────────────────────────────────────
# Quality gate stage (real wiring — the "soft drop" semantic)
# ──────────────────────────────────────────────


def test_quality_gate_stage_marks_dropped_record(db, seed_record):
    """Async drop must NOT delete the row — it just flips status."""
    ew.enqueue(db, knowledge_id=seed_record, session_id="s1",
               project="p", ktype="fact",
               content_snapshot="garbage", tags_snapshot=[])

    # Fake quality_gate module returning a 'drop' verdict.
    fake_score = type("S", (), {
        "decision": "drop", "total": 0.2, "specificity": 0.2,
        "actionability": 0.2, "verifiability": 0.2,
        "reason": "noise", "threshold": 0.5,
        "provider": "fake", "model": "fake-1", "latency_ms": 10,
    })()
    log_calls = []
    fake_qg = type("M", (), {
        "score_quality": lambda content, ktype, project: fake_score,
        "log_decision": lambda *a, **k: log_calls.append(k),
    })

    with patch.dict(sys.modules, {"quality_gate": fake_qg}):
        # Drive only the quality_gate stage so the test is hermetic.
        task = ew._claim_pending(db, limit=1)[0]
        ew._run_quality_gate(db, task)

    knowledge_row = db.execute(
        "SELECT status FROM knowledge WHERE id=?", (seed_record,)
    ).fetchone()
    assert knowledge_row["status"] == "quality_dropped"
    # Audit row was journalled with the knowledge id
    assert log_calls and log_calls[0]["knowledge_id"] == seed_record


def test_quality_gate_stage_skipped_when_skip_quality_flag(db, seed_record):
    ew.enqueue(db, knowledge_id=seed_record, session_id="s1",
               project="p", ktype="fact",
               content_snapshot="payload", tags_snapshot=[],
               skip_quality=True)
    called = {"n": 0}
    fake_qg = type("M", (), {
        "score_quality": lambda *a, **k: called.update(n=called["n"] + 1),
        "log_decision": lambda *a, **k: None,
    })
    with patch.dict(sys.modules, {"quality_gate": fake_qg}):
        task = ew._claim_pending(db, limit=1)[0]
        ew._run_quality_gate(db, task)
    assert called["n"] == 0  # gate was skipped


# ──────────────────────────────────────────────
# Daemon thread
# ──────────────────────────────────────────────


# ──────────────────────────────────────────────
# Stale-processing recovery
# ──────────────────────────────────────────────


def test_reclaim_stale_flips_old_processing_back_to_pending(db, seed_record, monkeypatch):
    """Row stuck in 'processing' for > stale_after_sec → reclaimed."""
    monkeypatch.setenv("MEMORY_ENRICH_STALE_AFTER_SEC", "5")
    qid = ew.enqueue(db, knowledge_id=seed_record, session_id="s1",
                     project="p", ktype="fact",
                     content_snapshot="payload", tags_snapshot=[])
    # Force the row into a stale processing state.
    db.execute(
        "UPDATE enrichment_queue SET status='processing', "
        "started_at='2020-01-01T00:00:00Z' WHERE id=?",
        (qid,),
    )
    db.commit()

    n = ew.reclaim_stale(db)
    assert n == 1
    row = db.execute(
        "SELECT status, last_error FROM enrichment_queue WHERE id=?", (qid,)
    ).fetchone()
    assert row["status"] == "pending"
    assert "reclaimed" in (row["last_error"] or "").lower()


def test_reclaim_stale_leaves_fresh_processing_alone(db, seed_record, monkeypatch):
    """A row that *just* started processing must NOT be reclaimed."""
    monkeypatch.setenv("MEMORY_ENRICH_STALE_AFTER_SEC", "60")
    qid = ew.enqueue(db, knowledge_id=seed_record, session_id="s1",
                     project="p", ktype="fact",
                     content_snapshot="payload", tags_snapshot=[])
    # Started just now (well within the stale window).
    fresh = ew._now()
    db.execute(
        "UPDATE enrichment_queue SET status='processing', started_at=? WHERE id=?",
        (fresh, qid),
    )
    db.commit()
    n = ew.reclaim_stale(db)
    assert n == 0
    status = db.execute(
        "SELECT status FROM enrichment_queue WHERE id=?", (qid,)
    ).fetchone()["status"]
    assert status == "processing"


def test_run_pending_reports_reclaimed_count(db, seed_record, monkeypatch):
    """run_pending() returns reclaimed count alongside claimed/done."""
    monkeypatch.setenv("MEMORY_ENRICH_STALE_AFTER_SEC", "5")
    qid = ew.enqueue(db, knowledge_id=seed_record, session_id="s1",
                     project="p", ktype="fact",
                     content_snapshot="payload", tags_snapshot=[])
    db.execute(
        "UPDATE enrichment_queue SET status='processing', "
        "started_at='2020-01-01T00:00:00Z' WHERE id=?",
        (qid,),
    )
    db.commit()
    monkeypatch.setattr(ew, "_STAGES", [("noop", lambda *a, **k: None)])
    counts = ew.run_pending(db, max_rows=10)
    assert counts["reclaimed"] == 1
    # The reclaimed row should also be picked up in the same tick.
    assert counts["claimed"] == 1
    assert counts["done"] == 1


# ──────────────────────────────────────────────
# Daemon thread
# ──────────────────────────────────────────────


def test_start_worker_returns_none_when_disabled(monkeypatch):
    monkeypatch.delenv("MEMORY_ASYNC_ENRICHMENT", raising=False)
    fake_store = type("S", (), {"db": None})()
    assert ew.start_worker(fake_store) is None


def test_start_worker_launches_thread_when_enabled(monkeypatch, db, seed_record):
    monkeypatch.setenv("MEMORY_ASYNC_ENRICHMENT", "true")
    monkeypatch.setenv("MEMORY_ENRICH_TICK_SEC", "0.02")

    drained = []

    def fake_run(db_, store=None, **kw):
        drained.append(time.monotonic())
        return {"claimed": 0, "done": 0, "retried": 0, "failed": 0}

    monkeypatch.setattr(ew, "run_pending", fake_run)
    fake_store = type("S", (), {"db": db})()
    t = ew.start_worker(fake_store)
    assert t is not None
    try:
        # Give the thread a couple of ticks
        time.sleep(0.1)
        assert len(drained) >= 2
    finally:
        t.stop()
        t.join(timeout=1)
        assert not t.is_alive()

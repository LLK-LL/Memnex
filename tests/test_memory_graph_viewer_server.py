from __future__ import annotations

import json
import sqlite3
import urllib.request
from unittest.mock import patch

from src.tools.memory_graph_viewer_server import (
    MemoryGraphViewerHandler,
    ThreadedMemoryGraphViewerServer,
    collect_system_performance,
    get_cached_system_performance,
)


def _make_db(path):
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE graph_nodes (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            name TEXT NOT NULL,
            content TEXT,
            properties JSON,
            source TEXT,
            importance REAL DEFAULT 0.5,
            first_seen_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL,
            mention_count INTEGER DEFAULT 1,
            status TEXT DEFAULT 'active',
            name_norm TEXT
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
            reinforcement_count INTEGER DEFAULT 0
        );
        CREATE TABLE knowledge (
            id INTEGER PRIMARY KEY,
            session_id TEXT NOT NULL,
            type TEXT NOT NULL,
            content TEXT NOT NULL,
            context TEXT DEFAULT '',
            project TEXT DEFAULT 'general',
            tags TEXT DEFAULT '[]',
            status TEXT DEFAULT 'active',
            superseded_by INTEGER,
            confidence REAL DEFAULT 1.0,
            source TEXT DEFAULT 'explicit',
            created_at TEXT NOT NULL,
            last_confirmed TEXT,
            recall_count INTEGER DEFAULT 0,
            last_recalled TEXT,
            branch TEXT DEFAULT '',
            agent_id TEXT DEFAULT NULL,
            parent_agent_id TEXT DEFAULT NULL,
            importance TEXT NOT NULL DEFAULT 'medium'
        );
        CREATE TABLE knowledge_nodes (
            knowledge_id INTEGER,
            node_id TEXT,
            role TEXT DEFAULT 'related',
            strength REAL DEFAULT 1.0,
            PRIMARY KEY (knowledge_id, node_id)
        );
        INSERT INTO graph_nodes VALUES
          ('n1', 'concept', 'RAG', 'retrieval augmented memory', '{}', 'test', 0.8, '2026-01-01', '2026-01-02', 4, 'active', 'rag'),
          ('n2', 'project', 'Hermes', NULL, '{}', 'test', 0.6, '2026-01-01', '2026-01-02', 2, 'active', 'hermes');
        INSERT INTO graph_edges VALUES ('e1', 'n1', 'n2', 'fixed_by', 2.5, 'ctx', '2026-01-01', '2026-01-02', 3);
        """
    )
    conn.commit()
    conn.close()


def _get_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=5) as response:
        assert response.status == 200
        return json.loads(response.read().decode("utf-8"))


def test_viewer_backend_serves_live_graph_and_system_performance(tmp_path):
    db_path = tmp_path / "memory.db"
    asset_dir = tmp_path / "assets"
    asset_dir.mkdir()
    (asset_dir / "index.html").write_text("<!doctype html><title>viewer</title>", encoding="utf-8")
    _make_db(db_path)

    server = ThreadedMemoryGraphViewerServer(
        ("127.0.0.1", 0),
        MemoryGraphViewerHandler,
        db_path=db_path,
        asset_dir=asset_dir,
    )
    try:
        server.start_in_thread()
        base_url = f"http://127.0.0.1:{server.server_port}"

        with urllib.request.urlopen(base_url, timeout=5) as response:
            assert response.status == 200
            assert response.headers["Cache-Control"] == "no-store, max-age=0"

        graph = _get_json(f"{base_url}/api/graph")
        assert graph["metadata"]["node_count"] == 2
        assert graph["metadata"]["edge_count"] == 1
        assert graph["elements"]["edges"][0]["data"]["edge_family"] == "procedural"

        perf = _get_json(f"{base_url}/api/system/performance")
        assert perf["source"] == "backend"
        assert "timestamp" in perf
        assert "cpu_percent" in perf
        assert "memory" in perf
        assert "gpu" in perf
    finally:
        server.shutdown()
        server.server_close()


def test_collect_system_performance_has_bounded_shape():
    perf = collect_system_performance()
    assert perf["source"] == "backend"
    assert isinstance(perf["timestamp"], float)
    assert set(perf["memory"]) >= {"used_mb", "total_mb", "percent"}
    assert "gpu" in perf


def test_system_performance_cache_reuses_recent_snapshot():
    calls = []

    def fake_collect():
        calls.append(len(calls))
        return {
            "source": "backend",
            "timestamp": 1000.0 + len(calls),
            "cpu_percent": 7.0,
            "memory": {"used_mb": 1, "total_mb": 2, "percent": 50},
            "gpu": None,
        }

    cache = {}
    with patch("src.tools.memory_graph_viewer_server.collect_system_performance", fake_collect):
        first = get_cached_system_performance(cache, now=1.0)
        second = get_cached_system_performance(cache, now=2.5)
        third = get_cached_system_performance(cache, now=4.2)

    assert first is second
    assert third is not first
    assert len(calls) == 2

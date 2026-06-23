from __future__ import annotations

import json
import sqlite3

from src.tools.memory_graph_viewer_export import (
    connect_readonly,
    copy_assets,
    load_graph,
    write_graph_json,
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
        """
    )
    conn.executemany(
        "INSERT INTO graph_nodes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            ("n1", "concept", "RAG", "retrieval augmented memory", "{}", "test", 0.8, "2026-01-01", "2026-01-02", 4, "active", "rag"),
            ("n2", "project", "Hermes", None, "{}", "test", 0.6, "2026-01-01", "2026-01-02", 2, "active", "hermes"),
            ("n3", "concept", "Inactive", None, "{}", "test", 0.1, "2026-01-01", "2026-01-02", 9, "archived", "inactive"),
        ],
    )
    conn.executemany(
        "INSERT INTO graph_edges VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            ("e1", "n1", "n2", "related_to", 2.5, "ctx", "2026-01-01", "2026-01-02", 3),
            ("e2", "n1", "missing", "orphan", 9.0, "", "2026-01-01", "2026-01-02", 1),
        ],
    )
    conn.execute(
        "INSERT INTO knowledge (id, session_id, type, content, project, tags, created_at) VALUES (1, 's', 'solution', 'Use RAG first', 'global', '[\"rag\"]', '2026-01-01')"
    )
    conn.execute(
        "INSERT INTO knowledge_nodes VALUES (1, 'n1', 'tagged', 0.9)"
    )
    conn.commit()
    conn.close()


def test_load_graph_filters_orphan_edges_and_links_knowledge(tmp_path):
    db = tmp_path / "memory.db"
    _make_db(db)
    with connect_readonly(db) as conn:
        graph = load_graph(conn)

    assert graph["metadata"]["node_count"] == 2
    assert graph["metadata"]["edge_count"] == 1
    assert graph["metadata"]["max_nodes"] is None
    assert graph["metadata"]["max_edges"] is None
    assert "timeline" in graph["metadata"]
    assert set(graph["metadata"]["timeline"]) == {"start", "end"}
    assert graph["metadata"]["timeline"]["start"] <= graph["metadata"]["timeline"]["end"]
    assert graph["elements"]["edges"][0]["data"]["id"] == "e1"
    rag = next(node for node in graph["elements"]["nodes"] if node["data"]["id"] == "n1")
    assert rag["data"]["knowledge"][0]["summary"] == "Use RAG first"
    assert "galaxy_layer" in rag["data"]
    assert rag["data"]["galaxy_layer"] in {"core", "active", "knowledge", "episode", "external"}
    assert "freshness" in rag["data"]
    assert 0.0 <= rag["data"]["freshness"] <= 1.0
    assert "activity" in rag["data"]
    assert 0.0 <= rag["data"]["activity"] <= 1.0


def test_load_graph_honors_explicit_limits(tmp_path):
    db = tmp_path / "memory.db"
    _make_db(db)
    with connect_readonly(db) as conn:
        graph = load_graph(conn, max_nodes=1, max_edges=1)

    assert graph["metadata"]["node_count"] == 1
    assert graph["metadata"]["edge_count"] == 0
    assert graph["metadata"]["max_nodes"] == 1
    assert graph["metadata"]["max_edges"] == 1


def test_write_graph_json_and_copy_assets(tmp_path):
    graph = {"metadata": {"node_count": 0}, "elements": {"nodes": [], "edges": []}}
    output = tmp_path / "viewer"
    graph_path = write_graph_json(graph, output)
    copy_assets(output)

    assert json.loads(graph_path.read_text(encoding="utf-8")) == graph
    assert (output / "index.html").exists()
    assert (output / "styles.css").exists()
    assert (output / "viewer.js").exists()
    assert (output / "viewer-3d.html").exists()
    assert (output / "viewer-3d.js").exists()

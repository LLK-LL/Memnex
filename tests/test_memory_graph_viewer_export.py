from __future__ import annotations

import json
import sqlite3

from src.tools.memory_graph_viewer_export import (
    connect_readonly,
    copy_assets,
    inline_viewer_modules,
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
            ("e3", "n2", "n1", "fixed_by", 1.5, "fix ctx", "2026-01-01", "2026-01-02", 1),
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
    assert graph["metadata"]["edge_count"] == 2
    assert graph["metadata"]["max_nodes"] is None
    assert graph["metadata"]["max_edges"] is None
    assert "timeline" in graph["metadata"]
    assert set(graph["metadata"]["timeline"]) == {"start", "end"}
    assert graph["metadata"]["timeline"]["start"] <= graph["metadata"]["timeline"]["end"]
    assert graph["metadata"]["cache"] == {
        "default_root": "D:\\TotalAgentMemory\\memory-galaxy-cache",
        "layout_namespace": "memory-galaxy",
    }
    assert graph["metadata"]["graph_identity"]["node_ids_hash"]
    assert graph["metadata"]["graph_identity"]["edge_ids_hash"]
    assert graph["metadata"]["layout_seed"] == graph["metadata"]["graph_identity"]["node_ids_hash"][:16]
    edges = {edge["data"]["id"]: edge["data"] for edge in graph["elements"]["edges"]}
    assert edges["e1"]["edge_family"] == "semantic"
    assert edges["e3"]["edge_family"] == "procedural"
    rag = next(node for node in graph["elements"]["nodes"] if node["data"]["id"] == "codex:n1")
    assert rag["data"]["source_id"] == "n1"
    assert rag["data"]["agent_namespace"] == "codex"
    assert rag["data"]["knowledge"][0]["summary"] == "Use RAG first"
    assert "galaxy_layer" in rag["data"]
    assert rag["data"]["galaxy_layer"] in {"core", "active", "knowledge", "episode", "external"}
    assert "freshness" in rag["data"]
    assert 0.0 <= rag["data"]["freshness"] <= 1.0
    assert "activity" in rag["data"]
    assert 0.0 <= rag["data"]["activity"] <= 1.0
    assert rag["data"]["layout_seed"]
    assert "relation_counts" in rag["data"]
    assert rag["data"]["relation_counts"]["total"] == 2
    assert rag["data"]["provenance"]["source"] == "test"
    assert rag["data"]["provenance"]["first_seen_at"] == "2026-01-01"
    assert rag["data"]["provenance"]["last_seen_at"] == "2026-01-02"


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
    from src.tools.memory_graph_viewer_export import embed_graph_data
    embed_graph_data(graph, output)
    inline_viewer_modules(output)

    assert json.loads(graph_path.read_text(encoding="utf-8")) == graph
    assert (output / "index.html").exists()
    assert (output / "styles.css").exists()
    assert (output / "pixi.min.js").exists()
    assert (output / "viewer.js").exists()
    assert (output / "viewer-3d.html").exists()
    assert (output / "viewer-3d.js").exists()
    assert (output / "memory-galaxy-core.js").exists()
    assert (output / "memory-galaxy-events.js").exists()
    assert (output / "memory-galaxy-systems.js").exists()
    assert (output / "memory-galaxy-layouts.js").exists()
    assert (output / "memory-galaxy-renderer.js").exists()
    assert (output / "memory-galaxy-view-state.js").exists()
    assert (output / "viewer-shared.js").exists()
    index_html = (output / "index.html").read_text(encoding="utf-8")
    viewer_3d_html = (output / "viewer-3d.html").read_text(encoding="utf-8")
    assert 'id="graph-data"' in index_html
    assert 'src="pixi.min.js' in index_html
    assert 'id="graph-data"' in viewer_3d_html
    assert 'src="viewer.js"' not in index_html
    assert 'src="viewer-3d.js"' not in viewer_3d_html
    assert "type=\"module\">" in index_html
    assert "type=\"module\">" in viewer_3d_html
    assert index_html.count("function systemColor(") == 1

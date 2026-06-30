import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import graph_expander


def _db():
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.executescript(
        """
        CREATE TABLE knowledge (
            id INTEGER PRIMARY KEY,
            type TEXT,
            content TEXT,
            project TEXT,
            tags TEXT,
            status TEXT DEFAULT 'active',
            confidence REAL,
            source TEXT,
            created_at TEXT,
            last_confirmed TEXT,
            recall_count INTEGER DEFAULT 0,
            session_id TEXT
        );
        CREATE TABLE knowledge_nodes (
            knowledge_id INTEGER NOT NULL,
            node_id TEXT NOT NULL,
            role TEXT DEFAULT 'related',
            strength REAL DEFAULT 1.0
        );
        CREATE TABLE graph_edges (
            id TEXT PRIMARY KEY,
            source_id TEXT NOT NULL,
            target_id TEXT NOT NULL,
            relation_type TEXT NOT NULL,
            weight REAL DEFAULT 1.0,
            context TEXT
        );
        """
    )
    return db


def _seed(db):
    db.executemany(
        "INSERT INTO knowledge (id, type, content, project, created_at) VALUES (?, 'fact', ?, 'demo', '2026-06-30')",
        [
            (1, "seed"),
            (2, "causal neighbor"),
            (3, "semantic neighbor"),
        ],
    )
    db.executemany(
        "INSERT INTO knowledge_nodes (knowledge_id, node_id, strength) VALUES (?, ?, 1.0)",
        [
            (1, "seed-node"),
            (2, "causal-node"),
            (3, "semantic-node"),
        ],
    )
    db.executemany(
        "INSERT INTO graph_edges (id, source_id, target_id, relation_type, weight, context) VALUES (?, ?, ?, ?, 1.0, ?)",
        [
            ("e1", "seed-node", "causal-node", "caused_by", "cause path"),
            ("e2", "seed-node", "semantic-node", "similar_to", "semantic path"),
        ],
    )
    db.commit()


def test_expand_top_k_filters_by_edge_family():
    db = _db()
    _seed(db)

    result = graph_expander.expand_top_k(db, [1], budget=10, edge_families=["causal"])

    assert result == [(2, 1.0)]


def test_explain_expansion_paths_reports_relation_family_and_context():
    db = _db()
    _seed(db)

    result = graph_expander.explain_expansion_paths(
        db, [1], candidate_ids=[2], edge_families=["causal"],
    )

    assert result[2]["via_seed_id"] == 1
    assert result[2]["relation_type"] == "caused_by"
    assert result[2]["edge_family"] == "causal"
    assert result[2]["context"] == "cause path"

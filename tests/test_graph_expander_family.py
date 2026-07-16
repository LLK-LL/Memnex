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
            agent_namespace TEXT NOT NULL DEFAULT 'codex',
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
        "INSERT INTO knowledge (id, type, content, project, agent_namespace, created_at) VALUES (?, 'fact', ?, 'demo', ?, '2026-06-30')",
        [
            (1, "seed", "codex"),
            (2, "causal neighbor", "codex"),
            (3, "semantic neighbor", "codex"),
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


def test_expand_top_k_defaults_to_seed_namespace():
    db = _db()
    _seed(db)
    db.execute(
        "INSERT INTO knowledge (id, type, content, project, agent_namespace, created_at) VALUES (4, 'fact', 'reasonix neighbor', 'demo', 'reasonix', '2026-06-30')"
    )
    db.execute(
        "INSERT INTO knowledge_nodes (knowledge_id, node_id, strength) VALUES (4, 'reasonix-node', 1.0)"
    )
    db.execute(
        "INSERT INTO graph_edges (id, source_id, target_id, relation_type, weight, context) VALUES ('e3', 'seed-node', 'reasonix-node', 'caused_by', 1.0, 'cross namespace path')"
    )
    db.commit()

    result = graph_expander.expand_top_k(db, [1], budget=10, edge_families=["causal"])

    assert result == [(2, 1.0)]


def test_expand_top_k_all_agents_scope_keeps_cross_namespace_candidates():
    db = _db()
    _seed(db)
    db.execute(
        "INSERT INTO knowledge (id, type, content, project, agent_namespace, created_at) VALUES (4, 'fact', 'reasonix neighbor', 'demo', 'reasonix', '2026-06-30')"
    )
    db.execute(
        "INSERT INTO knowledge_nodes (knowledge_id, node_id, strength) VALUES (4, 'reasonix-node', 1.0)"
    )
    db.execute(
        "INSERT INTO graph_edges (id, source_id, target_id, relation_type, weight, context) VALUES ('e3', 'seed-node', 'reasonix-node', 'caused_by', 1.0, 'cross namespace path')"
    )
    db.commit()

    result = graph_expander.expand_top_k(
        db, [1], budget=10, edge_families=["causal"], scope="all_agents",
    )

    assert set(result) == {(2, 1.0), (4, 1.0)}


def test_expand_hard_filters_graph_and_association_candidates_by_project():
    db = _db()
    _seed(db)
    db.executescript(
        """
        CREATE TABLE relations (
            from_id INTEGER NOT NULL,
            to_id INTEGER NOT NULL,
            type TEXT
        );
        INSERT INTO knowledge
            (id, type, content, project, agent_namespace, created_at)
        VALUES
            (4, 'fact', 'cross-project graph neighbor', 'other', 'codex', '2026-06-30'),
            (5, 'fact', 'same-project association neighbor', 'demo', 'codex', '2026-06-30'),
            (6, 'fact', 'cross-project association neighbor', 'other', 'codex', '2026-06-30');
        INSERT INTO knowledge_nodes (knowledge_id, node_id, strength)
        VALUES (4, 'cross-project-node', 1.0);
        INSERT INTO graph_edges
            (id, source_id, target_id, relation_type, weight, context)
        VALUES
            ('e3', 'seed-node', 'cross-project-node', 'caused_by', 1.0, 'cross-project path');
        INSERT INTO relations (from_id, to_id, type)
        VALUES
            (1, 5, 'related'),
            (1, 6, 'related');
        """
    )
    db.commit()

    result = graph_expander.expand(
        db,
        [1],
        budget=10,
        edge_families=["causal"],
        project="demo",
    )

    assert set(result) == {(2, 1.0), (5, 0.5)}


def test_explain_expansion_paths_defaults_to_seed_namespace():
    db = _db()
    _seed(db)
    db.execute(
        "INSERT INTO knowledge (id, type, content, project, agent_namespace, created_at) VALUES (4, 'fact', 'reasonix neighbor', 'demo', 'reasonix', '2026-06-30')"
    )
    db.execute(
        "INSERT INTO knowledge_nodes (knowledge_id, node_id, strength) VALUES (4, 'reasonix-node', 1.0)"
    )
    db.execute(
        "INSERT INTO graph_edges (id, source_id, target_id, relation_type, weight, context) VALUES ('e3', 'seed-node', 'reasonix-node', 'caused_by', 1.0, 'cross namespace path')"
    )
    db.commit()

    result = graph_expander.explain_expansion_paths(
        db, [1], candidate_ids=[2, 4], edge_families=["causal"],
    )

    assert set(result) == {2}

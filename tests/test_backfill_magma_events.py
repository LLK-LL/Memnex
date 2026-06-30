import argparse
import sqlite3
from pathlib import Path


def _schema(db: sqlite3.Connection) -> None:
    db.executescript(
        """
        CREATE TABLE knowledge (
            id INTEGER PRIMARY KEY,
            session_id TEXT NOT NULL DEFAULT 's1',
            type TEXT NOT NULL,
            content TEXT NOT NULL,
            context TEXT DEFAULT '',
            project TEXT DEFAULT 'general',
            tags TEXT DEFAULT '[]',
            status TEXT DEFAULT 'active',
            importance TEXT DEFAULT 'medium',
            agent_namespace TEXT DEFAULT 'codex',
            created_at TEXT DEFAULT '2026-06-30T00:00:00Z'
        );
        CREATE TABLE knowledge_enrichment (
            knowledge_id INTEGER PRIMARY KEY,
            entities TEXT NOT NULL DEFAULT '[]',
            intent TEXT NOT NULL DEFAULT 'unknown',
            topics TEXT NOT NULL DEFAULT '[]',
            updated_at TEXT NOT NULL
        );
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


def test_parse_response_keeps_event_role_and_allowed_edges():
    from tools.backfill_magma_events import parse_response

    out = parse_response(
        """
        {"event_role":"fix","event_summary":"Fixed install",
         "edges":[
           {"source":"failure","target":"missing package","relation_type":"caused_by","confidence":0.8},
           {"source":"bad","target":"edge","relation_type":"random"}
         ]}
        """
    )

    assert out["event_role"] == "fix"
    assert out["edges"] == [
        {
            "source": "failure",
            "target": "missing package",
            "relation_type": "caused_by",
            "confidence": 0.8,
            "context": "",
        }
    ]


def test_backfill_writes_only_active_rows(tmp_path: Path, monkeypatch):
    from tools import backfill_magma_events as bm

    db_path = tmp_path / "memory.db"
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    _schema(db)
    db.execute(
        "INSERT INTO knowledge (id,type,content,status) VALUES (1,'solution','Fixed because dependency missing','active')"
    )
    db.execute(
        "INSERT INTO knowledge (id,type,content,status) VALUES (2,'solution','Deleted memory','deleted')"
    )
    db.commit()
    db.close()

    monkeypatch.setattr(
        bm,
        "ollama_infer",
        lambda row, model, url, timeout: {
            "event_role": "fix",
            "event_summary": "Fixed dependency",
            "edges": [
                {
                    "source": "install failure",
                    "target": "missing dependency",
                    "relation_type": "caused_by",
                    "confidence": 0.8,
                    "context": "because dependency was absent",
                }
            ],
        },
    )
    args = argparse.Namespace(
        db=str(db_path),
        dry_run=False,
        no_backup=True,
        limit=10,
        project=None,
        model="fake",
        ollama_url="http://127.0.0.1:11434",
        timeout=1.0,
        sleep=0.0,
        max_edges=1,
        keep_going=True,
    )

    report = bm.run(args)

    assert report["processed"] == 1
    assert report["edges_written"] == 1
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    assert db.execute("SELECT event_role FROM knowledge_enrichment WHERE knowledge_id=1").fetchone()[0] == "fix"
    assert db.execute("SELECT COUNT(*) FROM knowledge_enrichment WHERE knowledge_id=2").fetchone()[0] == 0
    assert db.execute("SELECT COUNT(*) FROM graph_edges WHERE relation_type='caused_by'").fetchone()[0] == 1
    assert db.execute("SELECT COUNT(*) FROM knowledge_nodes WHERE knowledge_id=1 AND role='event_role'").fetchone()[0] == 1
    assert db.execute("SELECT COUNT(*) FROM knowledge_nodes WHERE knowledge_id=1 AND role='structural_source'").fetchone()[0] == 1
    db.close()


def test_dry_run_does_not_write(tmp_path: Path, monkeypatch):
    from tools import backfill_magma_events as bm

    db_path = tmp_path / "memory.db"
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    _schema(db)
    db.execute(
        "INSERT INTO knowledge (id,type,content,status) VALUES (1,'solution','Fixed issue','active')"
    )
    db.commit()
    db.close()

    monkeypatch.setattr(
        bm,
        "ollama_infer",
        lambda row, model, url, timeout: {"event_role": "fix", "event_summary": "", "edges": []},
    )
    args = argparse.Namespace(
        db=str(db_path),
        dry_run=True,
        no_backup=True,
        limit=10,
        project=None,
        model="fake",
        ollama_url="http://127.0.0.1:11434",
        timeout=1.0,
        sleep=0.0,
        max_edges=1,
        keep_going=True,
    )

    report = bm.run(args)

    assert report["processed"] == 1
    db = sqlite3.connect(db_path)
    assert "event_role" in [r[1] for r in db.execute("PRAGMA table_info(knowledge_enrichment)")]
    assert db.execute("SELECT COUNT(*) FROM knowledge_enrichment").fetchone()[0] == 0
    assert db.execute("SELECT COUNT(*) FROM graph_edges").fetchone()[0] == 0
    db.close()

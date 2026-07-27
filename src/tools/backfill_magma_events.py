#!/usr/bin/env python3
"""Backfill MAGMA-style event roles and structural edges for active memories."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sqlite3
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from graph.store import GraphStore  # noqa: E402
from paths import memory_dir  # noqa: E402

RELATIONS = {
    "caused_by",
    "causes",
    "leads_to",
    "because_of",
    "blocks",
    "blocked_by",
    "fixed_by",
    "resolved_by",
    "step_after",
    "step_before",
    "workflow_depends_on",
    "validated_by",
    "tested_by",
}

EVENT_ROLES = {
    "incident",
    "diagnosis",
    "fix",
    "verification",
    "decision",
    "procedure",
    "fact",
    "preference",
    "other",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_schema(conn: sqlite3.Connection) -> None:
    cols = {r["name"] for r in conn.execute("PRAGMA table_info(knowledge_enrichment)")}
    if "event_role" not in cols:
        conn.execute("ALTER TABLE knowledge_enrichment ADD COLUMN event_role TEXT DEFAULT NULL")
    if "event_payload" not in cols:
        conn.execute("ALTER TABLE knowledge_enrichment ADD COLUMN event_payload TEXT DEFAULT NULL")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_kenr_event_role ON knowledge_enrichment(event_role)")
    conn.commit()


def online_backup(db_path: Path) -> Path:
    backup_dir = db_path.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup = backup_dir / f"memory-before-magma-backfill-{time.strftime('%Y%m%d-%H%M%S')}.db"
    src = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    dst = sqlite3.connect(backup)
    src.backup(dst)
    dst.close()
    src.close()
    return backup


def _extract_json(raw: str) -> dict[str, Any]:
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start < 0 or end <= start:
            return {}
        try:
            data = json.loads(raw[start:end + 1])
            return data if isinstance(data, dict) else {}
        except json.JSONDecodeError:
            return {}


def parse_response(raw: str) -> dict[str, Any]:
    data = _extract_json(raw)
    role = str(data.get("event_role") or "other").strip().lower().replace("-", "_")
    if role not in EVENT_ROLES:
        role = "other"
    out: dict[str, Any] = {
        "event_role": role,
        "event_summary": str(data.get("event_summary") or "").strip()[:300],
        "edges": [],
    }
    edges = data.get("edges") or []
    if isinstance(edges, list):
        for item in edges[:5]:
            if not isinstance(item, dict):
                continue
            source = str(item.get("source") or "").strip()
            target = str(item.get("target") or "").strip()
            relation_type = str(item.get("relation_type") or "").strip().lower()
            relation_type = relation_type.replace("-", "_").replace(" ", "_")
            if not source or not target or relation_type not in RELATIONS:
                continue
            try:
                confidence = float(item.get("confidence", 0.5))
            except (TypeError, ValueError):
                confidence = 0.5
            out["edges"].append({
                "source": source[:160],
                "target": target[:160],
                "relation_type": relation_type,
                "confidence": max(0.1, min(1.0, confidence)),
                "context": str(item.get("context") or "").strip()[:500],
            })
    return out


def build_prompt(row: sqlite3.Row) -> str:
    text = f"{row['content']}\n\nContext:\n{row['context'] or ''}"[:3000]
    return (
        "Classify this coding-agent memory into one MAGMA event role and extract at most "
        "3 causal/procedural/verification edges.\n"
        "Return JSON only with schema:\n"
        "{\"event_role\":\"incident|diagnosis|fix|verification|decision|procedure|fact|preference|other\","
        "\"event_summary\":\"short summary\","
        "\"edges\":[{\"source\":\"short noun phrase\",\"target\":\"short noun phrase\","
        "\"relation_type\":\"caused_by|causes|leads_to|because_of|blocks|blocked_by|fixed_by|resolved_by|step_after|step_before|workflow_depends_on|validated_by|tested_by\","
        "\"confidence\":0.0,\"context\":\"brief evidence\"}]}\n"
        "Use fix for resolved solutions, incident for failures, procedure for reusable steps, "
        "decision for design choices, verification for validation checks.\n\n"
        f"Memory id: {row['id']}\nType: {row['type']}\nProject: {row['project']}\nContent:\n{text}"
    )


def ollama_infer(row: sqlite3.Row, model: str, url: str, timeout: float) -> dict[str, Any]:
    payload = {
        "model": model,
        "prompt": build_prompt(row),
        "stream": False,
        "format": "json",
        "options": {"temperature": 0, "num_predict": 512},
    }
    req = urllib.request.Request(
        f"{url.rstrip('/')}/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8", errors="replace"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Ollama inference failed for knowledge {row['id']}: {exc}") from exc
    return parse_response(str(body.get("response") or ""))


def select_candidates(conn: sqlite3.Connection, limit: int, project: str | None = None) -> list[sqlite3.Row]:
    params: list[Any] = []
    where = [
        "k.status='active'",
        "k.type IN ('solution','lesson','decision','fact','convention')",
        "NOT EXISTS (SELECT 1 FROM knowledge_nodes kn WHERE kn.knowledge_id=k.id AND kn.role IN ('structural_source','structural_target','event_role'))",
    ]
    if project:
        where.append("k.project=?")
        params.append(project)
    params.append(limit)
    return conn.execute(
        f"""
        SELECT k.id, k.type, k.content, COALESCE(k.context,'') AS context,
               k.project, k.tags, k.importance, k.agent_namespace, e.intent
        FROM knowledge k
        LEFT JOIN knowledge_enrichment e ON e.knowledge_id=k.id
        WHERE {' AND '.join(where)}
        ORDER BY CASE k.type
                   WHEN 'solution' THEN 0
                   WHEN 'lesson' THEN 1
                   WHEN 'decision' THEN 2
                   WHEN 'fact' THEN 3
                   ELSE 4
                 END,
                 k.id DESC
        LIMIT ?
        """,
        params,
    ).fetchall()


def upsert_event_role(conn: sqlite3.Connection, row: sqlite3.Row, result: dict[str, Any]) -> None:
    existing = conn.execute(
        "SELECT entities, intent, topics FROM knowledge_enrichment WHERE knowledge_id=?",
        (row["id"],),
    ).fetchone()
    entities = existing["entities"] if existing else "[]"
    intent = existing["intent"] if existing else (row["type"] or "unknown")
    topics = existing["topics"] if existing else "[]"
    conn.execute(
        """
        INSERT INTO knowledge_enrichment
          (knowledge_id, entities, intent, topics, updated_at, event_role, event_payload)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(knowledge_id) DO UPDATE SET
          event_role=excluded.event_role,
          event_payload=excluded.event_payload,
          updated_at=excluded.updated_at
        """,
        (
            row["id"],
            entities,
            intent,
            topics,
            _now(),
            result["event_role"],
            json.dumps(result, ensure_ascii=False),
        ),
    )
    store = GraphStore(conn)
    role_node = store.add_node(
        "event_role",
        result["event_role"],
        content=f"MAGMA event role: {result['event_role']}",
        source="magma_backfill",
    )
    store.link_knowledge(row["id"], role_node, role="event_role", strength=1.0)


def write_edges(conn: sqlite3.Connection, row: sqlite3.Row, result: dict[str, Any], max_edges: int) -> int:
    store = GraphStore(conn)
    written = 0
    for edge in result.get("edges", [])[:max_edges]:
        created = store.link_pair(
            edge["source"],
            "event",
            edge["target"],
            "event",
            edge["relation_type"],
            weight=edge["confidence"],
            context=edge.get("context") or f"magma backfill for knowledge {row['id']}",
        )
        if created is None:
            continue
        source_id, target_id, _ = created
        store.link_knowledge(row["id"], source_id, role="structural_source", strength=edge["confidence"])
        store.link_knowledge(row["id"], target_id, role="structural_target", strength=edge["confidence"])
        written += 1
    return written


def run(args: argparse.Namespace) -> dict[str, Any]:
    db_path = Path(args.db) if args.db else memory_dir() / "memory.db"
    conn = connect(db_path)
    ensure_schema(conn)
    backup = None if args.dry_run or args.no_backup else online_backup(db_path)
    rows = select_candidates(conn, args.limit, args.project)
    report: dict[str, Any] = {
        "db": str(db_path),
        "backup": str(backup) if backup else None,
        "dry_run": args.dry_run,
        "selected": len(rows),
        "processed": 0,
        "edges_written": 0,
        "failed": [],
        "items": [],
    }
    for row in rows:
        try:
            result = ollama_infer(row, args.model, args.ollama_url, args.timeout)
            edge_count = min(len(result.get("edges", [])), args.max_edges)
            if not args.dry_run:
                upsert_event_role(conn, row, result)
                edge_count = write_edges(conn, row, result, args.max_edges)
                conn.commit()
            report["processed"] += 1
            report["edges_written"] += edge_count
            report["items"].append({
                "id": row["id"],
                "event_role": result["event_role"],
                "edges": edge_count,
                "summary": result.get("event_summary", ""),
            })
            if args.sleep > 0:
                time.sleep(args.sleep)
        except Exception as exc:  # noqa: BLE001
            report["failed"].append({"id": row["id"], "error": str(exc)})
            if not args.keep_going:
                break
    conn.close()
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", help="SQLite memory DB path; defaults to TAM memory.db")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--project")
    parser.add_argument("--model", default=os.environ.get("MEMORY_STRUCTURAL_OLLAMA_MODEL", "qwen2.5:3b"))
    parser.add_argument("--ollama-url", default=os.environ.get("MEMORY_OLLAMA_URL", "http://127.0.0.1:11434"))
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--sleep", type=float, default=2.0)
    parser.add_argument("--max-edges", type=int, default=1)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-backup", action="store_true")
    parser.add_argument("--keep-going", action="store_true")
    args = parser.parse_args(argv)
    args.limit = max(1, min(100, args.limit))
    args.max_edges = max(0, min(3, args.max_edges))
    report = run(args)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not report["failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

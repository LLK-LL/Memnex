"""Export the Total Agent Memory graph to a local Cytoscape.js viewer."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_DB = Path.home() / ".tam" / "memory.db"
ASSET_DIR = Path(__file__).with_name("memory_graph_viewer_assets")
DEFAULT_GALAXY_CACHE_ROOT = Path("D:/TotalAgentMemory/memory-galaxy-cache")
GALAXY_LAYOUT_NAMESPACE = "memory-galaxy"


def connect_readonly(db_path: Path) -> sqlite3.Connection:
    uri = f"file:{db_path.as_posix()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _json_loads(value: str | None) -> Any:
    if not value:
        return {}
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return {"raw": value}


def _truncate(value: str | None, limit: int) -> str:
    if not value:
        return ""
    text = " ".join(value.split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def _stable_hash(values: list[str]) -> str:
    digest = hashlib.sha256()
    for value in sorted(str(item) for item in values):
        digest.update(value.encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        text = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(text)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def _freshness(last_seen_at: str | None, newest: datetime | None, oldest: datetime | None) -> float:
    seen = _parse_iso(last_seen_at)
    if not seen or not newest or not oldest or newest <= oldest:
        return 0.5
    span = (newest - oldest).total_seconds()
    pos = (seen - oldest).total_seconds()
    return round(max(0.0, min(1.0, pos / span)), 3)


def _activity(mention_count: int, max_mentions: int) -> float:
    if max_mentions <= 0:
        return 0.0
    return round(max(0.0, min(1.0, mention_count / max_mentions)), 3)


def _galaxy_layer(node_type: str, importance: float, mention_count: int) -> str:
    if node_type in {"rule", "decision"} or importance >= 1.4:
        return "core"
    if mention_count >= 10 or importance >= 0.9:
        return "active"
    if node_type in {"concept", "entity", "technology", "project"}:
        return "knowledge"
    if node_type in {"episode", "session", "observation"}:
        return "episode"
    return "external"


def load_graph(
    conn: sqlite3.Connection,
    *,
    max_nodes: int | None = None,
    max_edges: int | None = None,
    min_edge_weight: float = 0.0,
    content_limit: int = 500,
) -> dict[str, Any]:
    node_sql = """
        SELECT id, type, name, content, properties, source, importance,
               first_seen_at, last_seen_at, mention_count, status
        FROM graph_nodes
        WHERE COALESCE(status, 'active') = 'active'
        ORDER BY mention_count DESC, importance DESC, last_seen_at DESC
        """
    node_params: tuple[Any, ...] = ()
    if max_nodes is not None:
        node_sql += " LIMIT ?"
        node_params = (max_nodes,)
    node_rows = conn.execute(node_sql, node_params).fetchall()
    node_ids = {row["id"] for row in node_rows}
    seen_dates = [_parse_iso(row["last_seen_at"]) for row in node_rows]
    seen_dates = [date for date in seen_dates if date is not None]
    oldest_seen = min(seen_dates) if seen_dates else None
    newest_seen = max(seen_dates) if seen_dates else None
    max_mentions = max((int(row["mention_count"] or 0) for row in node_rows), default=0)

    edge_sql = """
        SELECT id, source_id, target_id, relation_type, weight, context,
               created_at, last_reinforced_at, reinforcement_count
        FROM graph_edges
        WHERE weight >= ?
        ORDER BY weight DESC, reinforcement_count DESC, last_reinforced_at DESC
        """
    edge_params: tuple[Any, ...] = (min_edge_weight,)
    if max_edges is not None:
        edge_sql += " LIMIT ?"
        edge_params = (min_edge_weight, max_edges * 3)
    edge_rows = conn.execute(edge_sql, edge_params).fetchall()

    edges: list[dict[str, Any]] = []
    for row in edge_rows:
        if row["source_id"] not in node_ids or row["target_id"] not in node_ids:
            continue
        edges.append(
            {
                "data": {
                    "id": row["id"],
                    "source": row["source_id"],
                    "target": row["target_id"],
                    "relation": row["relation_type"],
                    "weight": float(row["weight"] or 0.0),
                    "context": row["context"] or "",
                    "created_at": row["created_at"],
                    "last_reinforced_at": row["last_reinforced_at"],
                    "reinforcement_count": int(row["reinforcement_count"] or 0),
                }
            }
        )
        if max_edges is not None and len(edges) >= max_edges:
            break

    relation_counts_by_node: dict[str, dict[str, int]] = {
        str(node_id): {"total": 0} for node_id in node_ids
    }
    for edge in edges:
        data = edge["data"]
        relation = str(data["relation"] or "related")
        for endpoint in (str(data["source"]), str(data["target"])):
            counts = relation_counts_by_node.setdefault(endpoint, {"total": 0})
            counts["total"] = counts.get("total", 0) + 1
            counts[relation] = counts.get(relation, 0) + 1

    node_ids_hash = _stable_hash([str(row["id"]) for row in node_rows])
    edge_ids_hash = _stable_hash([str(edge["data"]["id"]) for edge in edges])
    knowledge_by_node = _load_knowledge_links(conn, node_ids, content_limit)
    nodes = [
        {
            "data": {
                "id": row["id"],
                "label": row["name"],
                "type": row["type"],
                "content": _truncate(row["content"], content_limit),
                "properties": _json_loads(row["properties"]),
                "source": row["source"] or "",
                "importance": float(row["importance"] or 0.0),
                "mention_count": int(row["mention_count"] or 0),
                "first_seen_at": row["first_seen_at"],
                "last_seen_at": row["last_seen_at"],
                "galaxy_layer": _galaxy_layer(
                    str(row["type"]),
                    float(row["importance"] or 0.0),
                    int(row["mention_count"] or 0),
                ),
                "freshness": _freshness(row["last_seen_at"], newest_seen, oldest_seen),
                "activity": _activity(int(row["mention_count"] or 0), max_mentions),
                "layout_seed": _stable_hash([str(row["id"]), str(row["type"]), str(row["name"])]),
                "relation_counts": relation_counts_by_node.get(str(row["id"]), {"total": 0}),
                "provenance": {
                    "source": row["source"] or "",
                    "first_seen_at": row["first_seen_at"],
                    "last_seen_at": row["last_seen_at"],
                },
                "knowledge": knowledge_by_node.get(row["id"], []),
            }
        }
        for row in node_rows
    ]

    type_counts: dict[str, int] = {}
    for node in nodes:
        node_type = str(node["data"]["type"])
        type_counts[node_type] = type_counts.get(node_type, 0) + 1

    return {
        "metadata": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "max_nodes": max_nodes,
            "max_edges": max_edges,
            "min_edge_weight": min_edge_weight,
            "type_counts": type_counts,
            "timeline": {
                "start": oldest_seen.isoformat() if oldest_seen else "",
                "end": newest_seen.isoformat() if newest_seen else "",
            },
            "cache": {
                "default_root": str(DEFAULT_GALAXY_CACHE_ROOT),
                "layout_namespace": GALAXY_LAYOUT_NAMESPACE,
            },
            "graph_identity": {
                "node_ids_hash": node_ids_hash,
                "edge_ids_hash": edge_ids_hash,
            },
            "layout_seed": node_ids_hash[:16],
        },
        "elements": {
            "nodes": nodes,
            "edges": edges,
        },
    }


def _load_knowledge_links(
    conn: sqlite3.Connection, node_ids: set[str], content_limit: int
) -> dict[str, list[dict[str, Any]]]:
    if not node_ids:
        return {}
    placeholders = ",".join("?" for _ in node_ids)
    rows = conn.execute(
        f"""
        SELECT kn.node_id, kn.role, kn.strength,
               k.id AS knowledge_id, k.type, k.project, k.content, k.tags,
               k.importance, k.created_at
        FROM knowledge_nodes kn
        JOIN knowledge k ON k.id = kn.knowledge_id
        WHERE kn.node_id IN ({placeholders})
          AND COALESCE(k.status, 'active') = 'active'
        ORDER BY kn.strength DESC, k.created_at DESC
        """,
        tuple(node_ids),
    ).fetchall()
    links: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        bucket = links.setdefault(row["node_id"], [])
        if len(bucket) >= 8:
            continue
        bucket.append(
            {
                "id": row["knowledge_id"],
                "role": row["role"],
                "strength": float(row["strength"] or 0.0),
                "type": row["type"],
                "project": row["project"],
                "summary": _truncate(row["content"], content_limit),
                "tags": _json_loads(row["tags"]) if row["tags"] else [],
                "importance": row["importance"],
                "created_at": row["created_at"],
            }
        )
    return links


def write_graph_json(graph: dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "graph.json"
    path.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def copy_assets(output_dir: Path, asset_dir: Path = ASSET_DIR) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for asset in (
        "index.html",
        "styles.css",
        "viewer.js",
        "viewer-3d.html",
        "viewer-3d.js",
        "memory-galaxy-core.js",
        "memory-galaxy-events.js",
        "viewer-shared.js",
    ):
        shutil.copy2(asset_dir / asset, output_dir / asset)


def export_viewer(
    *,
    db_path: Path,
    output_dir: Path,
    max_nodes: int | None,
    max_edges: int | None,
    min_edge_weight: float,
) -> dict[str, Any]:
    with connect_readonly(db_path) as conn:
        graph = load_graph(
            conn,
            max_nodes=max_nodes,
            max_edges=max_edges,
            min_edge_weight=min_edge_weight,
        )
    copy_assets(output_dir)
    write_graph_json(graph, output_dir)
    return graph["metadata"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-nodes", type=int, default=None, help="Limit exported nodes; omit for full export.")
    parser.add_argument("--max-edges", type=int, default=None, help="Limit exported edges; omit for full export.")
    parser.add_argument("--min-edge-weight", type=float, default=0.0)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    metadata = export_viewer(
        db_path=args.db,
        output_dir=args.output,
        max_nodes=args.max_nodes,
        max_edges=args.max_edges,
        min_edge_weight=args.min_edge_weight,
    )
    print(json.dumps(metadata, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

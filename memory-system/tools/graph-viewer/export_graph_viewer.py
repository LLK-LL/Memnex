"""Export a local memory graph to the Memnex Memory Galaxy viewer."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_DB = Path.home() / ".tam" / "memory.db"
ASSET_DIR = Path(__file__).with_name("assets")
DEFAULT_GALAXY_CACHE_ROOT = Path("D:/TotalAgentMemory/memory-galaxy-cache")
GALAXY_LAYOUT_NAMESPACE = "memory-galaxy"
VIEWER_BUNDLES = {
    "index.html": [
        "memory-galaxy-systems.js",
        "memory-galaxy-core.js",
        "memory-galaxy-events.js",
        "memory-galaxy-layouts.js",
        "memory-galaxy-renderer.js",
        "memory-galaxy-view-state.js",
        "viewer-shared.js",
        "viewer.js",
    ],
    "viewer-3d.html": [
        "memory-galaxy-systems.js",
        "memory-galaxy-core.js",
        "memory-galaxy-events.js",
        "viewer-shared.js",
        "viewer-3d.js",
    ],
}


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


def embed_graph_data(graph: dict[str, Any], output_dir: Path) -> None:
    payload = json.dumps(graph, ensure_ascii=False).replace("<", "\\u003c")
    snippet = f'<script id="graph-data" type="application/json">{payload}</script>'
    for asset in ("index.html", "viewer-3d.html"):
        path = output_dir / asset
        text = path.read_text(encoding="utf-8")
        if 'id="graph-data"' in text:
            continue
        text, count = re.subn(
            r"(\s*<script type=\"module\" src=\"viewer(?:-3d)?\.js[^\"]*\"></script>)",
            lambda match: f"\n  {snippet}{match.group(1)}",
            text,
            count=1,
        )
        if count != 1:
            raise ValueError(f"Unable to embed graph data into {path}")
        path.write_text(text, encoding="utf-8")


def _version_local_asset_refs(text: str, version: str) -> str:
    def _append_version(url: str) -> str:
        if "?v=" in url or "://" in url or url.startswith("data:"):
            return url
        joiner = "&" if "?" in url else "?"
        return f"{url}{joiner}v={version}"

    text = re.sub(
        r'((?:src|href)=["\'])([^"\']+\.(?:js|css|html))(["\'])',
        lambda match: f"{match.group(1)}{_append_version(match.group(2))}{match.group(3)}",
        text,
    )
    text = re.sub(
        r'((?:from|import)\s*["\'])(\./[^"\']+\.js)(["\'])',
        lambda match: f"{match.group(1)}{_append_version(match.group(2))}{match.group(3)}",
        text,
    )
    text = re.sub(
        r'fetch\((["\'])graph\.json\1\)',
        lambda match: f'fetch({match.group(1)}graph.json?v={version}{match.group(1)})',
        text,
    )
    return text


def _strip_local_imports(text: str) -> str:
    output: list[str] = []
    block: list[str] = []
    in_import = False
    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        if not in_import and stripped.startswith("import "):
            in_import = True
            block = [line]
            if ";" in line:
                joined = "".join(block)
                if 'from "./' not in joined and "from './" not in joined:
                    output.append(joined)
                in_import = False
                block = []
            continue
        if in_import:
            block.append(line)
            if ";" in line:
                joined = "".join(block)
                if 'from "./' not in joined and "from './" not in joined:
                    output.append(joined)
                in_import = False
                block = []
            continue
        output.append(line)
    if in_import and block:
        output.extend(block)
    return "".join(output)


def _strip_exports(text: str) -> str:
    return re.sub(r"(?m)^export\s+", "", text)


def _build_inline_module(asset_names: list[str], asset_dir: Path) -> str:
    chunks: list[str] = []
    for asset_name in asset_names:
        text = (asset_dir / asset_name).read_text(encoding="utf-8")
        text = _strip_local_imports(text)
        text = _strip_exports(text)
        chunks.append("// " + asset_name + "\n" + text.strip() + "\n")
    return "\n".join(chunks)


def inline_viewer_modules(output_dir: Path, asset_dir: Path = ASSET_DIR) -> None:
    for html_name, assets in VIEWER_BUNDLES.items():
        path = output_dir / html_name
        text = path.read_text(encoding="utf-8")
        entry_asset = assets[-1]
        module_code = _build_inline_module(assets, asset_dir)
        inline_tag = f"<script type=\"module\">\n{module_code}</script>"
        text, count = re.subn(
            rf"\s*<script type=\"module\" src=\"{re.escape(entry_asset)}[^\"]*\"></script>",
            lambda _match, tag=inline_tag: "\n  " + tag,
            text,
            count=1,
        )
        if count != 1:
            raise ValueError(f"Unable to inline module script into {path}")
        path.write_text(text, encoding="utf-8")


def copy_assets(output_dir: Path, asset_dir: Path = ASSET_DIR, *, version: str | None = None) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for asset in (
        "index.html",
        "styles.css",
        "viewer.js",
        "viewer-3d.html",
        "viewer-3d.js",
        "memory-galaxy-core.js",
        "memory-galaxy-events.js",
        "memory-galaxy-systems.js",
        "memory-galaxy-layouts.js",
        "memory-galaxy-renderer.js",
        "memory-galaxy-view-state.js",
        "viewer-shared.js",
    ):
        shutil.copy2(asset_dir / asset, output_dir / asset)
    if not version:
        return
    for asset in ("index.html", "viewer.js", "viewer-3d.html", "viewer-3d.js"):
        path = output_dir / asset
        path.write_text(_version_local_asset_refs(path.read_text(encoding="utf-8"), version), encoding="utf-8")


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
    version = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    copy_assets(output_dir, version=version)
    write_graph_json(graph, output_dir)
    embed_graph_data(graph, output_dir)
    inline_viewer_modules(output_dir)
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

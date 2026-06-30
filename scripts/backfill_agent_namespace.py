from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path


REASONIX_MARKERS = ("reasonix",)


def _column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(row["name"] == column for row in rows)


def _loads_tags(value: str | None) -> list[str]:
    if not value:
        return []
    try:
        parsed = json.loads(value)
    except Exception:
        return []
    if not isinstance(parsed, list):
        return []
    return [str(item).strip().lower() for item in parsed]


def _has_reasonix_marker(*values: str | None) -> bool:
    text = "\n".join(v or "" for v in values).lower()
    return any(marker in text for marker in REASONIX_MARKERS)


def find_reasonix_candidates(conn: sqlite3.Connection) -> dict[str, list[dict]]:
    conn.row_factory = sqlite3.Row
    if not _column_exists(conn, "knowledge", "agent_namespace"):
        raise RuntimeError(
            "knowledge.agent_namespace is missing. Start the Total Agent Memory server "
            "with this build once to run the bootstrap migration, then rerun this preview."
        )
    rows = conn.execute(
        "SELECT id, content, context, tags, agent_namespace FROM knowledge ORDER BY id"
    ).fetchall()
    report: dict[str, list[dict]] = {
        "matched_by_tag": [],
        "matched_by_content": [],
        "matched_by_context": [],
        "already_reasonix": [],
        "will_update": [],
        "ambiguous": [],
    }
    seen_update: set[int] = set()
    for row in rows:
        item = {
            "id": int(row["id"]),
            "agent_namespace": row["agent_namespace"],
            "reason": "",
        }
        tags = _loads_tags(row["tags"])
        if row["agent_namespace"] == "reasonix":
            item["reason"] = "already_reasonix"
            report["already_reasonix"].append(item)
            continue

        matched = False
        if "reasonix" in tags:
            matched = True
            tagged = dict(item)
            tagged["reason"] = "tag:reasonix"
            report["matched_by_tag"].append(tagged)
        if _has_reasonix_marker(row["content"]):
            matched = True
            content = dict(item)
            content["reason"] = "content:reasonix"
            report["matched_by_content"].append(content)
        if _has_reasonix_marker(row["context"]):
            matched = True
            context = dict(item)
            context["reason"] = "context:reasonix"
            report["matched_by_context"].append(context)

        row_id = int(row["id"])
        if matched and row_id not in seen_update:
            seen_update.add(row_id)
            update_item = dict(item)
            update_item["reason"] = "reasonix evidence"
            report["will_update"].append(update_item)
    return report


def apply_reasonix_backfill(conn: sqlite3.Connection) -> int:
    report = find_reasonix_candidates(conn)
    ids = [item["id"] for item in report["will_update"]]
    if not ids:
        return 0
    conn.executemany(
        "UPDATE knowledge SET agent_namespace='reasonix' WHERE id=?",
        [(item_id,) for item_id in ids],
    )
    conn.commit()
    return len(ids)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    try:
        try:
            report = find_reasonix_candidates(conn)
            if args.apply:
                report["updated"] = apply_reasonix_backfill(conn)  # type: ignore[index]
            print(json.dumps(report, ensure_ascii=False, indent=2))
        except RuntimeError as exc:
            print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2))
            return 2
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

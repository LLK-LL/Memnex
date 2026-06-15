"""Backfill governance tags for active memory records.

This script is intentionally small and idempotent: it only appends missing tags
to active knowledge rows and leaves content, context, status, and existing tags
unchanged.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path


DEFAULT_DB = Path.home() / ".tam" / "memory.db"


def load_tags(raw: str | None) -> list[str]:
    try:
        tags = json.loads(raw or "[]")
    except json.JSONDecodeError:
        return []
    if not isinstance(tags, list):
        return []
    return [str(tag) for tag in tags]


def backfill(db_path: Path, dry_run: bool = False) -> tuple[int, int]:
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            "select id, type, tags from knowledge where status='active'"
        ).fetchall()
        updated = 0
        for knowledge_id, knowledge_type, raw_tags in rows:
            tags = load_tags(raw_tags)
            seen = set(tags)
            required = ["layer:rag-memory"]
            if knowledge_type:
                required.append(f"memory:{knowledge_type}")

            changed = False
            for tag in required:
                if tag not in seen:
                    tags.append(tag)
                    seen.add(tag)
                    changed = True

            if changed:
                updated += 1
                if not dry_run:
                    conn.execute(
                        "update knowledge set tags=? where id=?",
                        (json.dumps(tags, ensure_ascii=False), knowledge_id),
                    )

        if not dry_run:
            conn.commit()
        return len(rows), updated
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default=str(DEFAULT_DB))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    total, updated = backfill(Path(args.db), args.dry_run)
    mode = "dry_run" if args.dry_run else "updated"
    print(f"active={total} {mode}={updated}")


if __name__ == "__main__":
    main()

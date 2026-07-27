# -*- coding: utf-8 -*-
"""v12.7 embedding-model migration: MiniLM-L12 (384d) -> jina-v2-base-zh (768d).

Re-encodes, in place and idempotently:
  1. `embeddings`                — from knowledge.content + context
  2. `knowledge_representations` — from the stored representation `content`
     (NO LLM involved: the representation texts already exist, so this does
     not enqueue anything into the background enrichment/repr queues)
  3. ensures the CJK trigram FTS shadow table exists and is backfilled

Safe against a live server: WAL + busy_timeout; rows are updated in batches
with commits. Re-run any time — only rows whose embed_model differs from the
target (or whose dim mismatches) are re-encoded, so a second pass after the
server restart picks up rows written in between by the old process.

Usage:
    python scripts/migrate_embeddings_v127.py [--model <fastembed-model>] [--dry-run]
"""
from __future__ import annotations

import argparse
import os
import sqlite3
import struct
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

DEFAULT_MODEL = os.environ.get("FASTEMBED_MODEL", "jinaai/jina-embeddings-v2-base-zh")
BATCH = 64


def _quantize_binary(vec) -> bytes:
    import numpy as np
    arr = np.asarray(vec, dtype=np.float32)
    return np.packbits(np.where(arr > 0, 1, 0).astype(np.uint8)).tobytes()


def _f32_blob(vec) -> bytes:
    return struct.pack(f"{len(vec)}f", *vec)


def _db_path() -> Path:
    from paths import memory_db
    return memory_db()


def migrate(model_name: str, dry_run: bool = False) -> None:
    from fastembed import TextEmbedding

    db_path = _db_path()
    print(f"DB: {db_path}")
    print(f"target model: {model_name}")

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=15000")

    print("loading model...", flush=True)
    t0 = time.perf_counter()
    _cache_dir = os.environ.get("FASTEMBED_CACHE_DIR")
    _kwargs = {"cache_dir": _cache_dir} if _cache_dir else {}
    model = TextEmbedding(model_name, **_kwargs)
    probe = list(model.embed(["dim probe"]))[0]
    dim = len(probe)
    print(f"model loaded in {time.perf_counter() - t0:.1f}s, dim={dim}", flush=True)

    # ── 1. embeddings table (source text = knowledge content + context) ──
    rows = conn.execute(
        """SELECT k.id, k.content, COALESCE(k.context,'') AS context
             FROM knowledge k
            WHERE k.status='active'
              AND (NOT EXISTS (SELECT 1 FROM embeddings e WHERE e.knowledge_id=k.id)
                   OR EXISTS (SELECT 1 FROM embeddings e WHERE e.knowledge_id=k.id
                              AND (e.embed_model IS NOT ? OR e.embed_dim IS NOT ?)))
        """,
        (model_name, dim),
    ).fetchall()
    print(f"embeddings: {len(rows)} rows to (re-)encode")
    done = 0
    t0 = time.perf_counter()
    for i in range(0, len(rows), BATCH):
        chunk = rows[i:i + BATCH]
        texts = [f"{r['content']} {r['context']}".strip() for r in chunk]
        vecs = list(model.embed(texts))
        if dry_run:
            done += len(chunk)
            continue
        for r, v in zip(chunk, vecs):
            v = v.tolist() if hasattr(v, "tolist") else list(v)
            conn.execute(
                """INSERT INTO embeddings
                       (knowledge_id, binary_vector, float32_vector, embed_model,
                        embed_dim, created_at, embedding_provider, embedding_space,
                        content_type, language)
                   VALUES (?,?,?,?,?,datetime('now'),'fastembed',
                           COALESCE((SELECT embedding_space FROM embeddings
                                      WHERE knowledge_id=?), 'text'),
                           COALESCE((SELECT content_type FROM embeddings
                                      WHERE knowledge_id=?), 'text'),
                           (SELECT language FROM embeddings WHERE knowledge_id=?))
                   ON CONFLICT(knowledge_id) DO UPDATE SET
                       binary_vector=excluded.binary_vector,
                       float32_vector=excluded.float32_vector,
                       embed_model=excluded.embed_model,
                       embed_dim=excluded.embed_dim,
                       created_at=excluded.created_at,
                       embedding_provider=excluded.embedding_provider""",
                (r["id"], _quantize_binary(v), _f32_blob(v), model_name, dim,
                 r["id"], r["id"], r["id"]),
            )
        conn.commit()
        done += len(chunk)
        if done % 256 == 0 or done == len(rows):
            rate = done / max(time.perf_counter() - t0, 1e-6)
            print(f"  embeddings {done}/{len(rows)} ({rate:.0f}/s)", flush=True)

    # ── 2. knowledge_representations (source text = stored content) ──
    rrows = conn.execute(
        """SELECT id, knowledge_id, representation, content
             FROM knowledge_representations
            WHERE (embed_model IS NOT ? OR embed_dim IS NOT ?)""",
        (model_name, dim),
    ).fetchall()
    encodable = [r for r in rrows if (r["content"] or "").strip()]
    skipped_empty = len(rrows) - len(encodable)
    print(f"knowledge_representations: {len(encodable)} rows to re-encode "
          f"({skipped_empty} skipped: empty content)")
    done = 0
    t0 = time.perf_counter()
    for i in range(0, len(encodable), BATCH):
        chunk = encodable[i:i + BATCH]
        texts = [r["content"] for r in chunk]
        vecs = list(model.embed(texts))
        if dry_run:
            done += len(chunk)
            continue
        for r, v in zip(chunk, vecs):
            v = v.tolist() if hasattr(v, "tolist") else list(v)
            conn.execute(
                """UPDATE knowledge_representations
                      SET float32_vector=?, binary_vector=?, embed_model=?, embed_dim=?
                    WHERE id=?""",
                (_f32_blob(v), _quantize_binary(v), model_name, dim, r["id"]),
            )
        conn.commit()
        done += len(chunk)
        if done % 256 == 0 or done == len(encodable):
            rate = done / max(time.perf_counter() - t0, 1e-6)
            print(f"  representations {done}/{len(encodable)} ({rate:.0f}/s)", flush=True)

    # ── 3. CJK trigram FTS shadow table (same DDL as Store._ensure_cjk_fts) ──
    if not dry_run:
        try:
            existed = conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='knowledge_fts_cjk'"
            ).fetchone() is not None
            conn.executescript("""
                CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts_cjk USING fts5(
                    content, context, tags, content='knowledge', content_rowid='id',
                    tokenize='trigram'
                );
                CREATE TRIGGER IF NOT EXISTS k_ftsc_i AFTER INSERT ON knowledge BEGIN
                    INSERT INTO knowledge_fts_cjk(rowid,content,context,tags)
                    VALUES (new.id,new.content,new.context,new.tags);
                END;
                CREATE TRIGGER IF NOT EXISTS k_ftsc_u AFTER UPDATE ON knowledge BEGIN
                    INSERT INTO knowledge_fts_cjk(knowledge_fts_cjk,rowid,content,context,tags)
                    VALUES ('delete',old.id,old.content,old.context,old.tags);
                    INSERT INTO knowledge_fts_cjk(rowid,content,context,tags)
                    VALUES (new.id,new.content,new.context,new.tags);
                END;
            """)
            if not existed:
                conn.execute(
                    "INSERT INTO knowledge_fts_cjk(knowledge_fts_cjk) VALUES('rebuild')"
                )
                print("CJK trigram FTS: created + backfilled")
            else:
                print("CJK trigram FTS: already present")
            conn.commit()
        except Exception as e:
            print(f"CJK trigram FTS skipped: {e}")

    # ── summary ──
    for label, sql in [
        ("embeddings by (model, dim)",
         "SELECT embed_model, embed_dim, COUNT(*) c FROM embeddings GROUP BY 1,2"),
        ("representations by (model, dim)",
         "SELECT embed_model, embed_dim, COUNT(*) c FROM knowledge_representations GROUP BY 1,2"),
    ]:
        print(label + ":")
        for row in conn.execute(sql):
            print("   ", dict(row))
    conn.close()
    print("DONE")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()
    migrate(a.model, a.dry_run)

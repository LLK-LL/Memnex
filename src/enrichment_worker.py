"""v10.1 — Async enrichment worker (inbox/outbox style).

Sync hot-path of `save_knowledge` is fast: privacy → canonical_tags →
INSERT → embed → graph link → enqueue → return.

This worker picks rows out of `enrichment_queue` and runs the heavy
LLM-bound stages: quality gate, entity-dedup audit, contradiction
detector, episodic event linking, wiki auto-refresh.

The worker is **opt-in** by default; the sync path runs the legacy
inline pipeline unless `MEMORY_ASYNC_ENRICHMENT=true`. A daemon
thread is started by `Store.__init__` when the flag is on; tests can
also drive it deterministically through `run_pending(db, max_rows=N)`.

Idempotency
-----------
Each stage is idempotent and writes its own audit row. A row may be
processed more than once if the worker is killed mid-stage; downstream
log tables tolerate duplicate inserts (UNIQUE on knowledge_id+stage
where applicable, or a "skip if already present" guard).

Failure isolation
-----------------
A single failing stage does NOT block subsequent rows: each is wrapped
in try/except and logged to `last_error`. Rows that fail >3 times are
marked `failed` and stay out of the active queue until manually retried.
"""
from __future__ import annotations

import json
import os
import sys
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

from paths import memory_dir

LOG = lambda msg: sys.stderr.write(f"[enrich-worker] {msg}\n")


# ──────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────


def _enabled() -> bool:
    return os.environ.get("MEMORY_ASYNC_ENRICHMENT", "false").strip().lower() in (
        "1", "true", "yes", "on",
    )


def _tick_interval() -> float:
    raw = os.environ.get("MEMORY_ENRICH_TICK_SEC")
    if not raw:
        return 0.1
    try:
        v = float(raw)
        return max(0.01, min(5.0, v))
    except ValueError:
        return 0.1


def _batch_size() -> int:
    raw = os.environ.get("MEMORY_ENRICH_BATCH")
    if not raw:
        return 5
    try:
        return max(1, min(50, int(raw)))
    except ValueError:
        return 5


def _max_attempts() -> int:
    raw = os.environ.get("MEMORY_ENRICH_MAX_ATTEMPTS")
    if not raw:
        return 3
    try:
        return max(1, int(raw))
    except ValueError:
        return 3


def _stale_after_sec() -> int:
    """How long a row may sit in 'processing' before we assume the
    worker that claimed it died. Default 60s — well above any healthy
    stage latency, well below any retention concern.
    """
    raw = os.environ.get("MEMORY_ENRICH_STALE_AFTER_SEC")
    if not raw:
        return 60
    try:
        return max(5, int(raw))
    except ValueError:
        return 60


_STRUCTURAL_LAST_RUN = 0.0


def _structural_enabled() -> bool:
    return os.environ.get("MEMORY_STRUCTURAL_CONSOLIDATION", "false").strip().lower() in (
        "1", "true", "yes", "on",
    )


def _structural_model_size() -> str:
    return os.environ.get("MEMORY_STRUCTURAL_MODEL_SIZE", "3b").strip().lower()


def _structural_max_per_tick() -> int:
    raw = os.environ.get("MEMORY_STRUCTURAL_MAX_PER_TICK")
    try:
        requested = int(raw) if raw else 1
    except ValueError:
        requested = 1
    requested = max(1, min(20, requested))
    if _structural_model_size() == "3b":
        return 1
    return requested


def _structural_min_interval_sec() -> float:
    raw = os.environ.get("MEMORY_STRUCTURAL_MIN_INTERVAL_SEC")
    if not raw:
        return 5.0 if _structural_model_size() == "3b" else 1.0
    try:
        return max(0.0, float(raw))
    except ValueError:
        return 5.0 if _structural_model_size() == "3b" else 1.0


def _structural_should_run(now: float | None = None) -> bool:
    if not _structural_enabled():
        return False
    current = time.monotonic() if now is None else now
    return current - _STRUCTURAL_LAST_RUN >= _structural_min_interval_sec()


def _structural_model() -> str:
    return os.environ.get("MEMORY_STRUCTURAL_OLLAMA_MODEL", "qwen2.5:3b").strip()


def _ollama_url() -> str:
    return os.environ.get("MEMORY_OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")


def _structural_timeout_sec() -> float:
    raw = os.environ.get("MEMORY_STRUCTURAL_TIMEOUT_SEC")
    if not raw:
        return 45.0
    try:
        return max(5.0, min(180.0, float(raw)))
    except ValueError:
        return 45.0


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


# ──────────────────────────────────────────────
# Enqueue
# ──────────────────────────────────────────────


@dataclass
class EnrichmentTask:
    id: int
    knowledge_id: int
    session_id: str | None
    project: str
    ktype: str
    content_snapshot: str
    tags_snapshot: list[str]
    importance: str
    skip_quality: bool
    attempts: int


def enqueue(
    db,
    *,
    knowledge_id: int,
    session_id: str | None,
    project: str,
    ktype: str,
    content_snapshot: str,
    tags_snapshot: list[str] | None,
    importance: str = "medium",
    skip_quality: bool = False,
) -> int:
    """Insert a pending row into the enrichment queue. Returns row id."""
    cur = db.execute(
        """INSERT INTO enrichment_queue
             (knowledge_id, session_id, project, ktype,
              content_snapshot, tags_snapshot, importance, skip_quality,
              status, enqueued_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)""",
        (
            knowledge_id, session_id, project, ktype,
            content_snapshot, json.dumps(list(tags_snapshot or [])),
            importance, 1 if skip_quality else 0,
            _now(),
        ),
    )
    db.commit()
    return cur.lastrowid


# ──────────────────────────────────────────────
# Claim & finalise
# ──────────────────────────────────────────────


def reclaim_stale(db) -> int:
    """Flip 'processing' rows older than MEMORY_ENRICH_STALE_AFTER_SEC
    back to 'pending' so a healthy worker picks them up. Returns the
    number of rows reclaimed.

    Called once at worker start and on every tick — cheap (single
    UPDATE with index on `status`).
    """
    cutoff_sec = _stale_after_sec()
    cutoff_ts = (
        datetime.now(timezone.utc).timestamp() - cutoff_sec
    )
    cutoff_iso = (
        datetime.fromtimestamp(cutoff_ts, tz=timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )
    cur = db.execute(
        """UPDATE enrichment_queue
              SET status='pending',
                  last_error='reclaimed: previous worker did not finish in time'
            WHERE status='processing'
              AND started_at IS NOT NULL
              AND started_at < ?""",
        (cutoff_iso,),
    )
    db.commit()
    return cur.rowcount or 0


def _claim_pending(db, limit: int) -> list[EnrichmentTask]:
    """Atomically move up to `limit` pending rows to 'processing'.

    Uses one UPDATE statement to avoid two workers grabbing the same row
    when running multi-threaded (defensive — by default there is only
    one daemon thread per Store).
    """
    now = _now()
    cur = db.execute(
        """UPDATE enrichment_queue
              SET status='processing',
                  started_at=?,
                  attempts = attempts + 1
            WHERE id IN (
                SELECT id FROM enrichment_queue
                 WHERE status='pending'
              ORDER BY enqueued_at ASC
                 LIMIT ?
            )
        RETURNING id, knowledge_id, session_id, project, ktype,
                  content_snapshot, tags_snapshot, importance, skip_quality,
                  attempts""",
        (now, limit),
    )
    rows = cur.fetchall()
    db.commit()
    out: list[EnrichmentTask] = []
    for row in rows:
        try:
            tags = json.loads(row[6]) if row[6] else []
        except Exception:
            tags = []
        out.append(EnrichmentTask(
            id=row[0],
            knowledge_id=row[1],
            session_id=row[2],
            project=row[3] or "general",
            ktype=row[4] or "fact",
            content_snapshot=row[5] or "",
            tags_snapshot=tags,
            importance=row[7] or "medium",
            skip_quality=bool(row[8]),
            attempts=row[9] or 0,
        ))
    return out


def _mark_done(db, task_id: int) -> None:
    db.execute(
        "UPDATE enrichment_queue SET status='done', finished_at=?, last_error=NULL WHERE id=?",
        (_now(), task_id),
    )
    db.commit()


def _mark_failed_or_retry(db, task_id: int, attempts: int, error: str) -> None:
    next_status = "failed" if attempts >= _max_attempts() else "pending"
    db.execute(
        "UPDATE enrichment_queue SET status=?, last_error=?, finished_at=? WHERE id=?",
        (next_status, error[:500], _now() if next_status == "failed" else None, task_id),
    )
    db.commit()


# ──────────────────────────────────────────────
# Stage runners (each idempotent, each fail-isolated)
# ──────────────────────────────────────────────


def _run_quality_gate(db, task: EnrichmentTask, store=None) -> None:
    """Score the record async. On 'drop' verdict, mark the knowledge row
    as `quality_dropped` rather than physically removing it (we already
    committed an INSERT in the sync path).
    """
    if task.skip_quality:
        return
    try:
        from quality_gate import score_quality, log_decision
    except Exception as e:
        LOG(f"quality_gate import failed: {e}")
        return
    score = score_quality(task.content_snapshot, ktype=task.ktype, project=task.project)
    log_decision(
        db, score, project=task.project, ktype=task.ktype,
        content=task.content_snapshot, knowledge_id=task.knowledge_id,
    )
    if score.decision == "drop":
        db.execute(
            "UPDATE knowledge SET status='quality_dropped' WHERE id=? AND status='active'",
            (task.knowledge_id,),
        )
        db.commit()
        LOG(
            f"async quality-gate dropped id={task.knowledge_id} "
            f"(score={score.total:.2f}<{score.threshold}, reason={score.reason!r})"
        )


def _run_entity_dedup_audit(db, task: EnrichmentTask, store=None) -> None:
    """Walk the canonicalised tags and persist audit-log rows.

    The actual canonicalisation already happened in the sync path
    (`canonical_tags` is cheap). What's deferred here is the embed-based
    second-pass dedup — comparing leftover free-form tags against
    `graph_nodes` via cosine similarity, which is the FastEmbed-heavy
    part. We re-run the cheap path here too so audit log rows reflect
    the ground truth at processing time.
    """
    try:
        import entity_dedup as _ed
    except Exception as e:
        LOG(f"entity_dedup import failed: {e}")
        return
    if not _ed._enabled() or not task.tags_snapshot:
        return
    cand_pool = _ed.production_candidates_query(db, project=task.project)
    if not cand_pool:
        return
    if store is not None:
        embed_fn = lambda texts: store.embed(texts) or None
    else:
        return  # cannot embed without store — skip
    _, decisions = _ed.canonicalize_entity_tags(
        task.tags_snapshot, candidates=cand_pool, embed_fn=embed_fn,
    )
    if decisions:
        _ed.log_decisions(
            db, decisions,
            knowledge_id=task.knowledge_id, project=task.project,
        )


def _run_contradiction_detector(db, task: EnrichmentTask, store=None) -> None:
    """Re-run the contradiction sweep against existing same-type records."""
    try:
        from contradiction_detector import (
            should_run as _cd_should_run,
            detect_contradictions as _cd_detect,
            production_candidates_query as _cd_fetch,
            production_llm_call as _cd_llm,
            apply_and_log as _cd_apply,
        )
    except Exception as e:
        LOG(f"contradiction_detector import failed: {e}")
        return
    ok, reason = _cd_should_run(task.ktype)
    if not ok or store is None:
        return
    embs = store.embed([task.content_snapshot])
    if not embs:
        return
    cand_pool = store._binary_search(
        embs[0], n_candidates=50, project=task.project, n_results=10
    )
    cand_pool = [(cid, cos) for cid, cos in cand_pool if cid != task.knowledge_id]
    if not cand_pool:
        return
    verdicts = _cd_detect(
        task.content_snapshot,
        ktype=task.ktype, project=task.project,
        candidate_pool=cand_pool,
        fetch_candidates=lambda ids: _cd_fetch(
            db, project=task.project, ktype=task.ktype, candidate_ids=ids
        ),
        llm_fn=_cd_llm,
    )
    if verdicts:
        counts = _cd_apply(db, verdicts, new_id=task.knowledge_id)
        if counts.get("superseded"):
            LOG(
                f"async contradiction superseded {counts['superseded']} "
                f"record(s) on save id={task.knowledge_id}"
            )


def _run_episodic_event(db, task: EnrichmentTask, store=None) -> None:
    """Spawn an Event node + MENTIONED_IN edges to entity nodes."""
    try:
        import episodic as _ep
    except Exception as e:
        LOG(f"episodic import failed: {e}")
        return
    _ep.record_save_event(
        db, knowledge_id=task.knowledge_id,
        project=task.project, session_id=task.session_id or "",
    )


def _run_wiki_refresh(db, task: EnrichmentTask, store=None) -> None:
    """Maybe regenerate <MEMORY_DIR>/wikis/<project>.md.

    Off by default (`MEMORY_WIKI_AUTO_REFRESH_EVERY_N=0`), so this is
    typically a cheap no-op. When enabled, runs only every N saves.
    """
    try:
        import project_wiki as _pw
    except Exception as e:
        LOG(f"project_wiki import failed: {e}")
        return
    output_dir = str(memory_dir())
    _pw.maybe_auto_refresh(
        db, project=task.project, save_count=task.knowledge_id,
        output_dir=os.path.join(output_dir, "wikis"),
    )


_STRUCTURAL_RELATIONS = {
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
}


def _extract_json_object(text: str) -> dict[str, Any]:
    if not text:
        return {}
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end <= start:
            return {}
        try:
            data = json.loads(text[start:end + 1])
            return data if isinstance(data, dict) else {}
        except json.JSONDecodeError:
            return {}


def _parse_structural_edges(raw: str) -> list[dict[str, Any]]:
    """Parse conservative causal/procedural edges from an Ollama response."""
    data = _extract_json_object(raw)
    edges = data.get("edges", [])
    if not isinstance(edges, list):
        return []
    out: list[dict[str, Any]] = []
    for item in edges[:5]:
        if not isinstance(item, dict):
            continue
        source = str(item.get("source") or "").strip()
        target = str(item.get("target") or "").strip()
        relation_type = str(item.get("relation_type") or "").strip().lower()
        relation_type = relation_type.replace("-", "_").replace(" ", "_")
        if not source or not target or relation_type not in _STRUCTURAL_RELATIONS:
            continue
        try:
            confidence = float(item.get("confidence", 0.5))
        except (TypeError, ValueError):
            confidence = 0.5
        confidence = max(0.1, min(1.0, confidence))
        context = str(item.get("context") or "").strip()
        out.append({
            "source": source[:160],
            "target": target[:160],
            "relation_type": relation_type,
            "confidence": confidence,
            "context": context[:500],
        })
    return out


def _structural_prompt(task: EnrichmentTask) -> str:
    content = task.content_snapshot[:2500]
    return (
        "Extract at most 3 causal or procedural memory graph edges from this coding-agent memory.\n"
        "Return only compact JSON with this schema:\n"
        "{\"edges\":[{\"source\":\"short noun phrase\",\"target\":\"short noun phrase\","
        "\"relation_type\":\"caused_by|causes|leads_to|because_of|blocks|blocked_by|fixed_by|resolved_by|step_after|step_before|workflow_depends_on\","
        "\"confidence\":0.0,\"context\":\"brief evidence\"}]}\n"
        "Use caused_by/fixed_by for failures and fixes. Use step_after/step_before for workflows.\n\n"
        f"Memory type: {task.ktype}\nProject: {task.project}\nContent:\n{content}"
    )


def _ollama_structural_call(task: EnrichmentTask) -> str:
    payload = {
        "model": _structural_model(),
        "prompt": _structural_prompt(task),
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0,
            "num_predict": 384,
        },
    }
    request = urllib.request.Request(
        f"{_ollama_url()}/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=_structural_timeout_sec()) as response:
            body = response.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"ollama structural call failed: {exc}") from exc
    data = json.loads(body)
    return str(data.get("response") or "")


def _write_structural_edges(db, task: EnrichmentTask, edges: list[dict[str, Any]]) -> int:
    if not edges:
        return 0
    try:
        from graph.store import GraphStore
    except Exception as exc:
        LOG(f"structural graph import failed: {exc}")
        return 0
    store = GraphStore(db)
    written = 0
    for edge in edges[:_structural_max_per_tick()]:
        result = store.link_pair(
            edge["source"],
            "concept",
            edge["target"],
            "concept",
            edge["relation_type"],
            weight=edge["confidence"],
            context=edge.get("context") or f"structural inference for knowledge {task.knowledge_id}",
        )
        if result is None:
            continue
        source_id, target_id, _edge_id = result
        store.link_knowledge(task.knowledge_id, source_id, role="structural_source", strength=edge["confidence"])
        store.link_knowledge(task.knowledge_id, target_id, role="structural_target", strength=edge["confidence"])
        written += 1
    return written


def _run_structural_consolidation(db, task: EnrichmentTask, store=None) -> None:
    """Run throttled MAGMA-style slow structural consolidation via Ollama.

    The stage is opt-in and intentionally conservative for local 3B Ollama:
    at most one task per tick and a minimum interval between runs.
    """
    global _STRUCTURAL_LAST_RUN
    if not _structural_should_run():
        return
    _STRUCTURAL_LAST_RUN = time.monotonic()
    raw = _ollama_structural_call(task)
    edges = _parse_structural_edges(raw)
    written = _write_structural_edges(db, task, edges)
    LOG(f"structural consolidation wrote {written} edge(s) for kid={task.knowledge_id}")


# Stages run in deterministic order. quality_gate first so a 'drop' is
# visible to a follow-up read before contradiction_detector spends LLM
# budget on a record we are about to soft-drop anyway.
_STAGES: list[tuple[str, Callable[..., None]]] = [
    ("quality_gate", _run_quality_gate),
    ("entity_dedup", _run_entity_dedup_audit),
    ("contradiction", _run_contradiction_detector),
    ("episodic", _run_episodic_event),
    ("wiki", _run_wiki_refresh),
    ("structural", _run_structural_consolidation),
]


def process_task(db, task: EnrichmentTask, *, store=None) -> tuple[bool, str | None]:
    """Run all stages for one task. Returns (ok, error_or_None).

    Per-stage errors are collected and reported as a single string so the
    queue row can be retried; one bad stage does not nuke the others.
    """
    errors: list[str] = []
    for label, runner in _STAGES:
        try:
            runner(db, task, store=store)
        except Exception as e:
            LOG(f"stage {label!r} failed for kid={task.knowledge_id}: {e}")
            errors.append(f"{label}: {e}")
    if errors:
        return False, "; ".join(errors)
    return True, None


def run_pending(db, *, max_rows: int | None = None, store=None) -> dict[str, int]:
    """Drain the queue once. Returns counts {claimed,done,retried,failed,reclaimed}.

    Tests call this directly to bypass the daemon thread.
    """
    # Reclaim rows whose previous worker died mid-stage. Cheap: indexed
    # UPDATE that touches only stale 'processing' rows.
    reclaimed = reclaim_stale(db)
    limit = max_rows if max_rows is not None else _batch_size()
    tasks = _claim_pending(db, limit)
    counts = {
        "claimed": len(tasks), "done": 0, "retried": 0,
        "failed": 0, "reclaimed": reclaimed,
    }
    for task in tasks:
        ok, err = process_task(db, task, store=store)
        if ok:
            _mark_done(db, task.id)
            counts["done"] += 1
        else:
            _mark_failed_or_retry(db, task.id, task.attempts, err or "unknown")
            if task.attempts >= _max_attempts():
                counts["failed"] += 1
            else:
                counts["retried"] += 1
    return counts


# ──────────────────────────────────────────────
# Daemon thread
# ──────────────────────────────────────────────


class _WorkerThread(threading.Thread):
    def __init__(self, store):
        super().__init__(daemon=True, name="enrich-worker")
        self._store = store
        self._stop_event = threading.Event()

    def stop(self) -> None:
        self._stop_event.set()

    def run(self) -> None:
        tick = _tick_interval()
        LOG(f"started (tick={tick}s, batch={_batch_size()})")
        while not self._stop_event.is_set():
            try:
                run_pending(self._store.db, store=self._store)
            except Exception as e:
                LOG(f"tick error: {e}")
            self._stop_event.wait(tick)


def start_worker(store) -> _WorkerThread | None:
    """Launch the daemon thread if async enrichment is enabled."""
    if not _enabled():
        return None
    t = _WorkerThread(store)
    t.start()
    return t

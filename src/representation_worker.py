"""Background worker for memory representation generation.

The save path enqueues representation work and returns. This worker drains
that durable SQLite queue out of band so LLM-backed views cannot block
`memory_save`.
"""

from __future__ import annotations

import os
import sqlite3
import sys
import threading
import time
from datetime import datetime, timezone
from typing import Any

from representations import generate_representations
from representations_queue import RepresentationsQueue


LOG = lambda msg: sys.stderr.write(f"[repr-worker] {msg}\n")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _age_seconds(value: str | None, *, now: datetime | None = None) -> int | None:
    ts = _parse_ts(value)
    if ts is None:
        return None
    now = now or datetime.now(timezone.utc)
    return max(0, int((now - ts).total_seconds()))


def _col(row: Any, key: str, index: int) -> Any:
    if row is None:
        return None
    if isinstance(row, sqlite3.Row):
        return row[key]
    return row[index]


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, str(default)))
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, str(default)))
    except ValueError:
        return default


def immediate_representations_enabled() -> bool:
    """Explicit compatibility switch for synchronous post-save processing."""
    return _env_bool("MEMORY_IMMEDIATE_REPRESENTATIONS", False)


def representation_worker_enabled() -> bool:
    return _env_bool("MEMORY_REPRESENTATION_WORKER_ENABLED", True)


def representation_queue_snapshot(
    db: sqlite3.Connection,
    worker: "RepresentationWorker | None" = None,
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "pending": 0,
        "processing": 0,
        "done": 0,
        "failed": 0,
        "oldest_pending_age_sec": None,
        "oldest_processing_age_sec": None,
        "last_processed_at": None,
        "worker": worker.status() if worker is not None else {"status": "not_started"},
    }
    try:
        rows = db.execute(
            "SELECT status, COUNT(*) AS c FROM representations_queue GROUP BY status"
        ).fetchall()
        for row in rows:
            out[str(_col(row, "status", 0))] = int(_col(row, "c", 1))

        pending = db.execute(
            "SELECT created_at FROM representations_queue "
            "WHERE status='pending' ORDER BY created_at ASC LIMIT 1"
        ).fetchone()
        processing = db.execute(
            "SELECT claimed_at FROM representations_queue "
            "WHERE status='processing' ORDER BY claimed_at ASC LIMIT 1"
        ).fetchone()
        last_done = db.execute(
            "SELECT processed_at FROM representations_queue "
            "WHERE status='done' AND processed_at IS NOT NULL "
            "ORDER BY processed_at DESC LIMIT 1"
        ).fetchone()

        out["oldest_pending_age_sec"] = _age_seconds(_col(pending, "created_at", 0))
        out["oldest_processing_age_sec"] = _age_seconds(_col(processing, "claimed_at", 0))
        out["last_processed_at"] = (
            _col(last_done, "processed_at", 0) if last_done is not None else None
        )
    except Exception as exc:  # noqa: BLE001
        out["error"] = str(exc)
        out["worker"] = worker.status() if worker is not None else {"status": "error"}
    return out


def representation_queue_health(snapshot: dict[str, Any]) -> str:
    if snapshot.get("error"):
        return "degraded"
    if int(snapshot.get("failed") or 0) > 0:
        return "degraded"
    pending_age = snapshot.get("oldest_pending_age_sec")
    processing_age = snapshot.get("oldest_processing_age_sec")
    pending_limit = _env_int("MEMORY_REPR_PENDING_DEGRADED_AFTER_SEC", 300)
    stale_limit = _env_int("MEMORY_REPR_STALE_AFTER_SEC", 1800)
    if pending_age is not None and pending_age > pending_limit:
        return "degraded"
    if processing_age is not None and processing_age > stale_limit:
        return "degraded"
    worker = snapshot.get("worker") or {}
    if worker.get("status") not in ("running", "idle"):
        return "degraded"
    return "ok"


class RepresentationWorker:
    def __init__(self, store, *, interval_sec: float | None = None, limit: int | None = None) -> None:
        self.store = store
        self.interval_sec = interval_sec if interval_sec is not None else _env_float(
            "MEMORY_REPR_WORKER_INTERVAL_SEC", 2.0
        )
        self.limit = limit if limit is not None else _env_int("MEMORY_REPR_DRAIN_LIMIT", 5)
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self._status: dict[str, Any] = {
            "status": "stopped",
            "last_heartbeat": None,
            "last_processed_at": None,
            "last_error": None,
        }

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._run,
            name="tam-representation-worker",
            daemon=True,
        )
        self._thread.start()
        LOG("started")

    def stop(self, timeout: float = 5.0) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=timeout)

    def status(self) -> dict[str, Any]:
        with self._lock:
            return dict(self._status)

    def drain_once(self) -> dict[str, int]:
        self._heartbeat("running")
        stats = RepresentationsQueue(self.store.db).process_pending(
            generator=generate_representations,
            embedder=self._embed_one,
            model_name=self.store._embed_mode or "auto",
            limit=self.limit,
        )
        if stats.get("processed"):
            self._heartbeat("running", last_processed_at=_now(), last_error=None)
        return stats

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                stats = self.drain_once()
                if not stats.get("processed") and not stats.get("failed"):
                    self._heartbeat("idle", last_error=None)
            except Exception as exc:  # noqa: BLE001
                LOG(f"error: {exc}")
                self._heartbeat("error", last_error=str(exc))
            self._stop.wait(self.interval_sec)
        self._heartbeat("stopped")

    def _embed_one(self, text: str) -> list[float]:
        embs = self.store.embed([text])
        return embs[0] if embs else []

    def _heartbeat(
        self,
        status: str,
        *,
        last_processed_at: str | None = None,
        last_error: str | None = None,
    ) -> None:
        with self._lock:
            self._status["status"] = status
            self._status["last_heartbeat"] = _now()
            if last_processed_at is not None:
                self._status["last_processed_at"] = last_processed_at
            if last_error is not None:
                self._status["last_error"] = last_error

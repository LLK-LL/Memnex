"""
Task phases state machine — v8.0.

Tracks explicit lifecycle phases per task: van → plan → creative → build →
reflect → archive. Enforces per-level phase whitelists from the classifier
so that, say, an L1 "typo fix" cannot jump straight into `creative`.

Integrates with procedural.ProceduralMemory: when a task reaches `archive`,
an outcome is recorded via workflow_track-style API so the predictor
learns from real executions.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Any

from task_classifier import LEVEL_PHASES, PHASES_ORDER, classify_task

VALID_PHASES = set(PHASES_ORDER)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class TaskPhaseError(ValueError):
    """Raised for invalid phase transitions."""


class TaskPhases:
    """SQLite-backed state machine for task phases."""

    def __init__(self, db: sqlite3.Connection) -> None:
        self.db = db
        # Per-task cached level (set via create_task). If unset, derived on read.
        self._level_cache: dict[str, int] = {}

    # ──────────────────────────────────────────────
    # Creation
    # ──────────────────────────────────────────────

    def create_task(
        self,
        task_id: str,
        description: str,
        level: int | None = None,
    ) -> dict[str, Any]:
        """Start a task — inserts an open `van` phase row.

        If `level` is not provided, it is derived via classify_task().
        """
        if not task_id:
            raise ValueError("task_id is required")
        if not description:
            raise ValueError("description is required")

        existing = self.db.execute(
            "SELECT 1 FROM task_phases WHERE task_id = ? LIMIT 1",
            (task_id,),
        ).fetchone()
        if existing:
            raise TaskPhaseError(f"task {task_id} already exists")

        if level is None:
            level = classify_task(description)["level"]
        if level not in LEVEL_PHASES:
            raise ValueError(f"invalid level {level}")
        self._level_cache[task_id] = level

        artifacts = json.dumps({"description": description, "level": level})
        now = _now()
        self.db.execute(
            """INSERT INTO task_phases
               (task_id, phase, entered_at, exited_at, artifacts_json, notes)
               VALUES (?, 'van', ?, NULL, ?, ?)""",
            (task_id, now, artifacts, f"level={level}"),
        )
        self.db.commit()
        return {
            "task_id": task_id,
            "phase": "van",
            "entered_at": now,
            "level": level,
            "allowed_phases": LEVEL_PHASES[level],
        }

    # ──────────────────────────────────────────────
    # Transitions
    # ──────────────────────────────────────────────

    def _get_level(self, task_id: str) -> int:
        if task_id in self._level_cache:
            return self._level_cache[task_id]
        row = self.db.execute(
            """SELECT artifacts_json FROM task_phases
               WHERE task_id = ? AND phase = 'van'
               ORDER BY entered_at ASC LIMIT 1""",
            (task_id,),
        ).fetchone()
        if not row or not row[0]:
            raise TaskPhaseError(f"task {task_id} has no van phase")
        try:
            meta = json.loads(row[0])
            lvl = int(meta.get("level", 3))
        except (json.JSONDecodeError, TypeError, ValueError):
            lvl = 3
        self._level_cache[task_id] = lvl
        return lvl

    def phase_transition(
        self,
        task_id: str,
        new_phase: str,
        artifacts: dict[str, Any] | None = None,
        notes: str | None = None,
    ) -> dict[str, Any]:
        """Close the current phase and open `new_phase`.

        Validates that `new_phase` is allowed for the task's level and that
        the transition does not skip required phases in canonical order.
        """
        if new_phase not in VALID_PHASES:
            raise TaskPhaseError(f"unknown phase '{new_phase}'")

        level = self._get_level(task_id)
        allowed = LEVEL_PHASES[level]
        if new_phase not in allowed:
            raise TaskPhaseError(
                f"phase '{new_phase}' not allowed for L{level} "
                f"(allowed: {allowed})"
            )

        cur = self.current_phase(task_id)
        if cur is None:
            raise TaskPhaseError(f"task {task_id} not found")

        # Enforce monotone ordering within the allowed subset.
        try:
            cur_idx = allowed.index(cur)
        except ValueError:
            # Current phase no longer in allowed set — should not happen, but
            # fall back to canonical order.
            cur_idx = PHASES_ORDER.index(cur)
        try:
            new_idx = allowed.index(new_phase)
        except ValueError:
            new_idx = PHASES_ORDER.index(new_phase)
        if new_idx <= cur_idx:
            raise TaskPhaseError(
                f"cannot go from '{cur}' back to '{new_phase}' "
                f"(phases are forward-only)"
            )
        # Disallow skipping required intermediate phases. The allowed list
        # for a level is already a whitelist, so any skipped phase inside
        # `allowed[cur_idx+1:new_idx]` is a violation.
        skipped = allowed[cur_idx + 1:new_idx]
        if skipped:
            raise TaskPhaseError(
                f"cannot skip phases {skipped} — must go "
                f"{cur} → {allowed[cur_idx + 1]} first"
            )

        now = _now()
        try:
            # Close previous phase
            self.db.execute(
                """UPDATE task_phases
                   SET exited_at = ?
                   WHERE task_id = ? AND phase = ? AND exited_at IS NULL""",
                (now, task_id, cur),
            )
            # Open new one
            self.db.execute(
                """INSERT INTO task_phases
                   (task_id, phase, entered_at, exited_at, artifacts_json, notes)
                   VALUES (?, ?, ?, NULL, ?, ?)""",
                (
                    task_id, new_phase, now,
                    json.dumps(artifacts) if artifacts is not None else None,
                    notes,
                ),
            )
            self.db.commit()
        except sqlite3.Error:
            self.db.rollback()
            raise

        return {
            "task_id": task_id,
            "from_phase": cur,
            "to_phase": new_phase,
            "entered_at": now,
            "rules_preview": (
                f"Rules for phase '{new_phase}': call "
                f"self_rules_context(project=..., phase='{new_phase}', "
                f"query='<current task>', top_k=5, include_always_on=True) to load."
            ),
        }

    # ──────────────────────────────────────────────
    # Queries
    # ──────────────────────────────────────────────

    def current_phase(self, task_id: str) -> str | None:
        """Return currently open phase, or the most recent one if all are closed."""
        row = self.db.execute(
            """SELECT phase FROM task_phases
               WHERE task_id = ? AND exited_at IS NULL
               ORDER BY entered_at DESC LIMIT 1""",
            (task_id,),
        ).fetchone()
        if row:
            return row[0]
        # All phases closed — return the latest.
        row = self.db.execute(
            """SELECT phase FROM task_phases
               WHERE task_id = ?
               ORDER BY entered_at DESC LIMIT 1""",
            (task_id,),
        ).fetchone()
        return row[0] if row else None

    def list_phases(self, task_id: str) -> list[dict[str, Any]]:
        """Return all phases in chronological order."""
        cur = self.db.cursor()
        cur.row_factory = sqlite3.Row
        rows = cur.execute(
            """SELECT task_id, phase, entered_at, exited_at, artifacts_json, notes
               FROM task_phases WHERE task_id = ?
               ORDER BY entered_at ASC""",
            (task_id,),
        ).fetchall()
        result: list[dict[str, Any]] = []
        for r in rows:
            d = dict(r)
            if d.get("artifacts_json"):
                try:
                    d["artifacts"] = json.loads(d["artifacts_json"])
                except (json.JSONDecodeError, TypeError):
                    d["artifacts"] = None
            else:
                d["artifacts"] = None
            d.pop("artifacts_json", None)
            result.append(d)
        return result

    # ──────────────────────────────────────────────
    # Completion
    # ──────────────────────────────────────────────

    def complete_task(
        self,
        task_id: str,
        final_notes: str | None = None,
        outcome: str = "success",
    ) -> dict[str, Any]:
        """Close the open `archive` phase and push outcome to procedural memory.

        Must be invoked while the current phase is `archive`. Calling on any
        other phase raises TaskPhaseError — the caller should transition to
        archive first (honoring the level's allowed skip-set).
        """
        cur = self.current_phase(task_id)
        if cur != "archive":
            raise TaskPhaseError(
                f"complete_task requires current phase = 'archive', got '{cur}'"
            )

        now = _now()
        self.db.execute(
            """UPDATE task_phases
               SET exited_at = ?, notes = COALESCE(?, notes)
               WHERE task_id = ? AND phase = 'archive' AND exited_at IS NULL""",
            (now, final_notes, task_id),
        )
        self.db.commit()

        # Hook into procedural memory: best-effort, never fail the
        # transition if the workflow row is missing.
        tracked: dict[str, Any] | None = None
        try:
            from procedural import ProceduralMemory
            pm = ProceduralMemory(self.db)
            # If a workflow with this task_id exists, track outcome.
            wf = pm.get_workflow(task_id)
            if wf:
                run_id = pm.track_outcome(task_id, outcome)
                tracked = {"workflow_id": task_id, "run_id": run_id}
        except Exception:
            tracked = None

        return {
            "task_id": task_id,
            "completed_at": now,
            "outcome": outcome,
            "tracked": tracked,
        }

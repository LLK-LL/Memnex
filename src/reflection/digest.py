"""
Reflection Digest Phase -- cleanup, deduplication, decay, contradiction resolution.

Phase 1 of the reflection pipeline. Cleans up stale knowledge,
merges duplicates, resolves contradictions, and prunes orphan graph nodes.
Runs synchronously since individual operations are fast.
"""

from __future__ import annotations

import json
import math
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

LOG = lambda msg: sys.stderr.write(f"[memory-reflection] {msg}\n")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_dt(raw: str) -> datetime:
    """Parse a datetime string from DB, always returning UTC-aware datetime."""
    dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _new_id() -> str:
    return uuid.uuid4().hex


def _parse_json(val: str | None, default: list | dict | None = None) -> list | dict:
    """Safely parse a JSON string, returning default on failure."""
    if val is None:
        return default if default is not None else []
    try:
        return json.loads(val)
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else []


class DigestPhase:
    """Phase 1: Clean up, deduplicate, decay, resolve contradictions."""

    DECAY_HALF_LIFE = 90  # days

    # Knowledge types that should NEVER decay
    IMMORTAL_TYPES = frozenset({"rule", "prohibition", "convention"})

    # Episode outcomes that resist decay when impact is high
    HIGH_IMPACT_THRESHOLD = 0.7

    def __init__(self, db: sqlite3.Connection) -> None:
        self.db = db

    def run(self) -> dict:
        """Run full digest. Returns stats dict."""
        stats: dict = {
            "duplicates_merged": 0,
            "decay": {"checked": 0, "archived": 0, "kept": 0},
            "contradictions_found": 0,
            "contradictions_resolved": 0,
            "orphan_nodes_removed": 0,
            "weak_edges_removed": 0,
        }

        try:
            stats["duplicates_merged"] = self.merge_duplicates()
        except Exception as e:
            LOG(f"merge_duplicates error: {e}")

        try:
            stats["decay"] = self.apply_intelligent_decay()
        except Exception as e:
            LOG(f"apply_intelligent_decay error: {e}")

        try:
            contradictions = self.find_contradictions()
            stats["contradictions_found"] = len(contradictions)
            for c in contradictions:
                try:
                    self.resolve_contradiction(c["old_id"], c["new_id"])
                    stats["contradictions_resolved"] += 1
                except Exception as e:
                    LOG(f"resolve_contradiction error for {c}: {e}")
        except Exception as e:
            LOG(f"find_contradictions error: {e}")

        try:
            stats["orphan_nodes_removed"] = self.cleanup_orphan_nodes()
        except Exception as e:
            LOG(f"cleanup_orphan_nodes error: {e}")

        try:
            stats["weak_edges_removed"] = self.cleanup_weak_edges()
        except Exception as e:
            LOG(f"cleanup_weak_edges error: {e}")

        LOG(f"Digest complete: {stats}")
        return stats

    def merge_duplicates(self, threshold: float = 0.85) -> int:
        """
        Find and merge semantic duplicates in knowledge table.
        Uses content similarity (SequenceMatcher).
        Returns number of merged records.
        """
        knowledge_cols = {
            row["name"]
            for row in self.db.execute("PRAGMA table_info(knowledge)").fetchall()
        }
        namespace_select = (
            "agent_namespace"
            if "agent_namespace" in knowledge_cols
            else "'codex' AS agent_namespace"
        )
        rows = self.db.execute(
            f"""SELECT id, type, content, project, tags, confidence,
                      recall_count, created_at, {namespace_select}
               FROM knowledge
               WHERE status = 'active'
               ORDER BY project, type, agent_namespace, created_at DESC"""
        ).fetchall()

        if len(rows) < 2:
            return 0

        merged = 0
        merged_ids: set[int] = set()

        # Group by namespace too; agent memories are isolated even when content matches.
        groups: dict[tuple[str, str, str], list[dict]] = {}
        for row in rows:
            key = (
                row["project"] or "general",
                row["type"],
                row["agent_namespace"] or "codex",
            )
            entry = dict(row)
            groups.setdefault(key, []).append(entry)

        for group_key, group_rows in groups.items():
            for i in range(len(group_rows)):
                if group_rows[i]["id"] in merged_ids:
                    continue

                for j in range(i + 1, len(group_rows)):
                    if group_rows[j]["id"] in merged_ids:
                        continue

                    content_a = group_rows[i]["content"]
                    content_b = group_rows[j]["content"]

                    # Quick length check to skip obviously different records
                    len_a, len_b = len(content_a), len(content_b)
                    if len_a == 0 or len_b == 0:
                        continue
                    ratio = min(len_a, len_b) / max(len_a, len_b)
                    if ratio < 0.5:
                        continue

                    similarity = SequenceMatcher(
                        None, content_a, content_b
                    ).ratio()

                    if similarity >= threshold:
                        # Keep the record with higher recall_count,
                        # or the newer one if equal
                        keep = group_rows[i]
                        remove = group_rows[j]
                        if (remove["recall_count"] or 0) > (keep["recall_count"] or 0):
                            keep, remove = remove, keep

                        # Merge: supersede the duplicate
                        self.db.execute(
                            """UPDATE knowledge
                               SET status = 'superseded',
                                   superseded_by = ?
                               WHERE id = ?""",
                            (keep["id"], remove["id"]),
                        )

                        # Transfer recall count
                        total_recalls = (keep["recall_count"] or 0) + (remove["recall_count"] or 0)
                        self.db.execute(
                            "UPDATE knowledge SET recall_count = ? WHERE id = ?",
                            (total_recalls, keep["id"]),
                        )

                        # Transfer knowledge_nodes links
                        self.db.execute(
                            """INSERT OR IGNORE INTO knowledge_nodes (knowledge_id, node_id, role, strength)
                               SELECT ?, node_id, role, strength
                               FROM knowledge_nodes WHERE knowledge_id = ?""",
                            (keep["id"], remove["id"]),
                        )

                        merged_ids.add(remove["id"])
                        merged += 1

        if merged > 0:
            self.db.commit()
            LOG(f"Merged {merged} duplicate knowledge records")

        return merged

    def apply_intelligent_decay(self) -> dict:
        """
        Apply decay based on node type and usage patterns:
        - Rules/prohibitions: NEVER decay
        - High-impact episodes (impact > 0.7): NEVER decay
        - Skills: decay by usage (not used in 30+ days)
        - Episodes: impact-based (high impact = slower decay)
        - Facts/solutions: time-based with recall reinforcement

        Returns: {checked, archived, kept}
        """
        result = {"checked": 0, "archived": 0, "kept": 0}
        now = datetime.now(timezone.utc)

        # Process knowledge records
        rows = self.db.execute(
            """SELECT id, type, content, confidence, source, created_at,
                      last_confirmed, recall_count, last_recalled, tags
               FROM knowledge
               WHERE status = 'active'"""
        ).fetchall()

        for row in rows:
            result["checked"] += 1
            kid = row["id"]
            ktype = row["type"]
            confidence = row["confidence"] or 1.0

            # NEVER decay rules and prohibitions
            if ktype in self.IMMORTAL_TYPES:
                result["kept"] += 1
                continue

            # Check for high-impact tag
            tags = _parse_json(row["tags"])
            if "critical" in tags or "never-decay" in tags:
                result["kept"] += 1
                continue

            # Calculate age in days
            try:
                created = _parse_dt(row["created_at"])
                age_days = (now - created).days
            except (ValueError, AttributeError):
                result["kept"] += 1
                continue

            # Calculate effective age considering recalls
            recall_count = row["recall_count"] or 0
            last_recalled = row["last_recalled"]

            # Each recall effectively reduces perceived age
            effective_age = age_days
            if recall_count > 0 and last_recalled:
                try:
                    last_recall_dt = _parse_dt(last_recalled)
                    days_since_recall = (now - last_recall_dt).days
                    # Recalls reset the decay clock partially
                    effective_age = min(age_days, days_since_recall + (age_days // (recall_count + 1)))
                except (ValueError, AttributeError):
                    pass

            # Exponential decay: score = 2^(-t/half_life)
            decay_score = math.pow(2, -effective_age / self.DECAY_HALF_LIFE)

            # Apply confidence modifier (high confidence decays slower)
            adjusted_score = decay_score * (0.5 + 0.5 * confidence)

            # Source modifier: auto-saved content decays faster
            if row["source"] == "auto":
                adjusted_score *= 0.8

            # Archive threshold
            archive_threshold = 0.15
            if ktype in ("episode", "observation"):
                archive_threshold = 0.10  # episodes can live longer

            if adjusted_score < archive_threshold:
                self.db.execute(
                    "UPDATE knowledge SET status = 'archived' WHERE id = ?",
                    (kid,),
                )
                result["archived"] += 1
            else:
                result["kept"] += 1

        # Process episodes separately
        episode_rows = self.db.execute(
            """SELECT id, impact_score, outcome, timestamp
               FROM episodes"""
        ).fetchall()

        for row in episode_rows:
            result["checked"] += 1

            # High-impact and failure episodes never decay
            if (row["impact_score"] or 0) >= self.HIGH_IMPACT_THRESHOLD:
                result["kept"] += 1
                continue
            if row["outcome"] == "failure":
                result["kept"] += 1
                continue

            try:
                ts = _parse_dt(row["timestamp"])
                age_days = (now - ts).days
            except (ValueError, AttributeError):
                result["kept"] += 1
                continue

            # Routine episodes decay after 180 days
            if row["outcome"] == "routine" and age_days > 180:
                # Don't delete episodes, just mark them
                # (episodes don't have status field, so we skip actual archival)
                result["archived"] += 1
            else:
                result["kept"] += 1

        if result["archived"] > 0:
            self.db.commit()
            LOG(f"Decay: archived {result['archived']} of {result['checked']} records")

        return result

    def find_contradictions(self) -> list[dict]:
        """
        Find pairs of knowledge records that may contradict each other.
        Strategy: same project + same type + overlapping concepts + different content.
        Returns list of {old_id, new_id, reason}.
        """
        contradictions: list[dict] = []

        # Get active knowledge with their linked graph nodes
        rows = self.db.execute(
            """SELECT k.id, k.type, k.content, k.project, k.created_at,
                      k.confidence, k.recall_count,
                      GROUP_CONCAT(gn.name, '|') as concepts
               FROM knowledge k
               LEFT JOIN knowledge_nodes kn ON kn.knowledge_id = k.id
               LEFT JOIN graph_nodes gn ON kn.node_id = gn.id
               WHERE k.status = 'active'
               GROUP BY k.id
               ORDER BY k.project, k.type, k.created_at"""
        ).fetchall()

        if len(rows) < 2:
            return contradictions

        # Group by (project, type) for comparison
        groups: dict[tuple[str, str], list[dict]] = {}
        for row in rows:
            key = (row["project"] or "general", row["type"])
            entry = dict(row)
            entry["concept_set"] = set(
                (entry.get("concepts") or "").split("|")
            ) - {"", None}
            groups.setdefault(key, []).append(entry)

        for group_key, group_rows in groups.items():
            for i in range(len(group_rows)):
                for j in range(i + 1, len(group_rows)):
                    a = group_rows[i]
                    b = group_rows[j]

                    # Need overlapping concepts
                    if not a["concept_set"] or not b["concept_set"]:
                        continue
                    overlap = a["concept_set"] & b["concept_set"]
                    if not overlap:
                        continue

                    # Need at least 50% concept overlap
                    union = a["concept_set"] | b["concept_set"]
                    if len(overlap) / len(union) < 0.5:
                        continue

                    # Check content dissimilarity
                    sim = SequenceMatcher(
                        None, a["content"], b["content"]
                    ).ratio()

                    # Similar concepts but different content = potential contradiction
                    if 0.2 < sim < 0.6:
                        # Older record is the one to supersede
                        old, new = (a, b) if a["created_at"] < b["created_at"] else (b, a)
                        contradictions.append({
                            "old_id": old["id"],
                            "new_id": new["id"],
                            "reason": f"Same concepts ({', '.join(list(overlap)[:3])}) "
                                      f"but divergent content (sim={sim:.2f})",
                            "shared_concepts": list(overlap),
                        })

        LOG(f"Found {len(contradictions)} potential contradictions")
        return contradictions

    def resolve_contradiction(self, old_id: int, new_id: int) -> None:
        """Supersede old record with new one. Keep link for history."""
        # Check both exist and are active
        old = self.db.execute(
            "SELECT id, status FROM knowledge WHERE id = ?", (old_id,)
        ).fetchone()
        new = self.db.execute(
            "SELECT id, status FROM knowledge WHERE id = ?", (new_id,)
        ).fetchone()

        if not old or not new:
            LOG(f"resolve_contradiction: record not found (old={old_id}, new={new_id})")
            return
        if old["status"] != "active":
            return

        self.db.execute(
            """UPDATE knowledge
               SET status = 'superseded', superseded_by = ?
               WHERE id = ?""",
            (new_id, old_id),
        )

        # Create a 'supersedes' edge if both have graph nodes
        old_nodes = self.db.execute(
            "SELECT node_id FROM knowledge_nodes WHERE knowledge_id = ?",
            (old_id,),
        ).fetchall()
        new_nodes = self.db.execute(
            "SELECT node_id FROM knowledge_nodes WHERE knowledge_id = ?",
            (new_id,),
        ).fetchall()

        if old_nodes and new_nodes:
            # Create edge from new concept to old concept
            for on in old_nodes:
                for nn in new_nodes:
                    if on["node_id"] != nn["node_id"]:
                        try:
                            self.db.execute(
                                """INSERT OR IGNORE INTO graph_edges
                                   (id, source_id, target_id, relation_type, weight, context, created_at)
                                   VALUES (?, ?, ?, 'supersedes', 1.0, ?, ?)""",
                                (
                                    _new_id(),
                                    nn["node_id"],
                                    on["node_id"],
                                    f"Knowledge {new_id} supersedes {old_id}",
                                    _now(),
                                ),
                            )
                        except sqlite3.IntegrityError:
                            pass  # edge already exists

        self.db.commit()
        LOG(f"Resolved contradiction: {old_id} superseded by {new_id}")

    def cleanup_orphan_nodes(self) -> int:
        """Remove graph nodes with no edges and no knowledge links."""
        cursor = self.db.execute(
            """DELETE FROM graph_nodes
               WHERE id NOT IN (
                   SELECT DISTINCT source_id FROM graph_edges
                   UNION
                   SELECT DISTINCT target_id FROM graph_edges
               )
               AND id NOT IN (
                   SELECT DISTINCT node_id FROM knowledge_nodes
               )
               AND status = 'active'
               AND mention_count <= 1"""
        )
        self.db.commit()
        count = cursor.rowcount
        if count > 0:
            LOG(f"Removed {count} orphan graph nodes")
        return count

    def cleanup_weak_edges(self, min_weight: float = 0.1) -> int:
        """Remove edges below the minimum weight threshold."""
        cursor = self.db.execute(
            "DELETE FROM graph_edges WHERE weight < ?", (min_weight,)
        )
        self.db.commit()
        count = cursor.rowcount
        if count > 0:
            LOG(f"Removed {count} weak edges (weight < {min_weight})")
        return count

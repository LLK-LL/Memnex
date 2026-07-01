"""Tests for Reflection — digest, synthesis, and agent."""

import asyncio
import pytest
from datetime import datetime, timezone, timedelta


class TestDigestPhase:
    def test_merge_duplicates(self, db):
        from reflection.digest import DigestPhase
        digest = DigestPhase(db)

        # Insert duplicate knowledge records
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        db.execute(
            "INSERT INTO knowledge (type, content, project, status, confidence, recall_count, created_at, updated_at) "
            "VALUES ('solution', 'Deploy Docker container to production', 'proj1', 'active', 1.0, 0, ?, ?)",
            (now, now),
        )
        db.execute(
            "INSERT INTO knowledge (type, content, project, status, confidence, recall_count, created_at, updated_at) "
            "VALUES ('solution', 'Deploy Docker container to production server', 'proj1', 'active', 1.0, 0, ?, ?)",
            (now, now),
        )
        db.commit()

        merged = digest.merge_duplicates()
        assert merged >= 1

        # One should be superseded
        rows = db.execute(
            "SELECT status FROM knowledge WHERE type = 'solution'"
        ).fetchall()
        statuses = [r[0] for r in rows]
        assert "superseded" in statuses

    def test_merge_duplicates_keeps_agent_namespaces_isolated(self, db):
        from reflection.digest import DigestPhase
        digest = DigestPhase(db)

        db.execute("ALTER TABLE knowledge ADD COLUMN agent_namespace TEXT DEFAULT 'codex'")

        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        content = "MAGMA-style event graph backfill completed for Total Agent Memory"
        for namespace in ("codex", "doubao"):
            db.execute(
                "INSERT INTO knowledge "
                "(type, content, project, status, confidence, recall_count, created_at, updated_at, agent_namespace) "
                "VALUES ('fact', ?, 'total-agent-memory', 'active', 1.0, 0, ?, ?, ?)",
                (content, now, now, namespace),
            )
        db.commit()

        merged = digest.merge_duplicates()
        assert merged == 0

        rows = db.execute(
            "SELECT agent_namespace, status, superseded_by FROM knowledge ORDER BY agent_namespace"
        ).fetchall()
        assert [(r[0], r[1], r[2]) for r in rows] == [
            ("codex", "active", None),
            ("doubao", "active", None),
        ]

    def test_intelligent_decay_preserves_failures(self, db):
        from reflection.digest import DigestPhase
        digest = DigestPhase(db)

        # Insert a high-impact failure episode
        from memory_systems.episode_store import EpisodeStore
        store = EpisodeStore(db)
        store.save(
            session_id="s1",
            narrative="Critical failure",
            outcome="failure",
            impact_score=0.9,
        )

        result = digest.apply_intelligent_decay()
        assert result["checked"] > 0
        # Failures should be kept
        assert result["kept"] >= 1

    def test_intelligent_decay_preserves_rules(self, db):
        from reflection.digest import DigestPhase
        digest = DigestPhase(db)

        # Insert a rule-type knowledge (immortal)
        old_date = (datetime.now(timezone.utc) - timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")
        db.execute(
            "INSERT INTO knowledge (type, content, status, confidence, recall_count, created_at, updated_at) "
            "VALUES ('rule', 'Always use strict mode', 'active', 1.0, 0, ?, ?)",
            (old_date, old_date),
        )
        db.commit()

        result = digest.apply_intelligent_decay()
        # Rules should never decay
        rule = db.execute(
            "SELECT status FROM knowledge WHERE type = 'rule'"
        ).fetchone()
        assert rule[0] == "active"

    def test_intelligent_decay_archives_old(self, db):
        from reflection.digest import DigestPhase
        digest = DigestPhase(db)

        # Insert very old low-confidence auto-saved knowledge
        very_old = (datetime.now(timezone.utc) - timedelta(days=400)).strftime("%Y-%m-%dT%H:%M:%SZ")
        db.execute(
            "INSERT INTO knowledge (type, content, status, confidence, recall_count, source, created_at, updated_at) "
            "VALUES ('fact', 'Very old fact nobody recalls', 'active', 0.3, 0, 'auto', ?, ?)",
            (very_old, very_old),
        )
        db.commit()

        result = digest.apply_intelligent_decay()
        assert result["checked"] > 0
        # Very old, low-confidence, auto-saved should be archived
        assert result["archived"] >= 1


class TestSynthesizePhase:
    def test_cluster_episodes(self, db):
        from reflection.synthesize import SynthesizePhase
        from memory_systems.episode_store import EpisodeStore
        synth = SynthesizePhase(db)
        store = EpisodeStore(db)

        # Create 3+ episodes with overlapping concepts
        for i in range(4):
            store.save(
                session_id=f"s{i}",
                narrative=f"Auth work {i}",
                outcome="routine",
                concepts=["auth", "jwt", "go"],
            )

        clusters = synth.cluster_recent_episodes(days=1, min_cluster_size=3)
        assert len(clusters) >= 1
        assert len(clusters[0]) >= 3

    def test_find_cross_project_patterns(self, db):
        from reflection.synthesize import SynthesizePhase
        synth = SynthesizePhase(db)

        # This requires knowledge linked to graph nodes across projects
        # Just verify it runs without error on empty data
        patterns = synth.find_cross_project_patterns()
        assert isinstance(patterns, list)

    def test_weekly_digest(self, db):
        from reflection.synthesize import SynthesizePhase
        synth = SynthesizePhase(db)

        # Insert a session and knowledge for the digest
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        db.execute(
            "INSERT INTO sessions (id, started_at, project) VALUES ('s1', ?, 'test')",
            (now,),
        )
        db.execute(
            "INSERT INTO knowledge (type, content, project, status, created_at, updated_at) "
            "VALUES ('solution', 'Test solution', 'test', 'active', ?, ?)",
            (now, now),
        )
        db.commit()

        digest = synth.generate_weekly_digest()
        assert "sessions_count" in digest
        assert "memories_created" in digest
        assert "focus_areas" in digest
        assert digest["sessions_count"] >= 1


class TestReflectionAgent:
    def test_reflection_agent_quick(self, db):
        from reflection.agent import ReflectionAgent
        agent = ReflectionAgent(db)
        report = asyncio.run(agent.run("quick"))
        assert report["scope"] == "quick"
        assert "digest" in report
        assert report["synthesis"] is None

    def test_reflection_agent_full(self, db):
        from reflection.agent import ReflectionAgent
        agent = ReflectionAgent(db)
        report = asyncio.run(agent.run("full"))
        assert report["scope"] == "full"
        assert "digest" in report
        assert "synthesis" in report
        assert report["synthesis"] is not None

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def store(monkeypatch, tmp_path):
    (tmp_path / "blobs").mkdir(exist_ok=True)
    (tmp_path / "chroma").mkdir(exist_ok=True)

    import server
    monkeypatch.setattr(server, "MEMORY_DIR", tmp_path)

    s = server.Store()
    s.db.execute(
        "INSERT INTO sessions (id, started_at, project, status) "
        "VALUES ('sess-rule-domain-test', '2026-07-07T00:00:00Z', 'myproj', 'open')"
    )
    s.db.commit()
    yield s
    try:
        s.db.close()
    except Exception:
        pass


def _add_rule(store, content, priority=5, tags=None, category="manual"):
    now = "2026-07-07T00:00:00Z"
    cur = store.db.execute(
        """INSERT INTO rules (session_id, content, context, category, scope,
                              priority, project, tags, status, created_at, updated_at)
           VALUES ('sess-rule-domain-test', ?, '', ?, 'project:myproj', ?, 'myproj',
                   ?, 'active', ?, ?)""",
        (content, category, priority, json.dumps(tags or []), now, now),
    )
    store.db.commit()
    return cur.lastrowid


def test_query_domain_filter_excludes_mismatched_contextual_rules(monkeypatch, store):
    monkeypatch.setattr(store, "embed", lambda texts: None)
    code_id = _add_rule(
        store,
        "Run pytest before changing repository implementation.",
        priority=5,
        tags=["domain:code", "primary_domain:code"],
        category="implementation",
    )
    writing_id = _add_rule(
        store,
        "For manuscript rewriting, return revised prose directly.",
        priority=10,
        tags=["domain:writing", "primary_domain:writing"],
        category="output_format",
    )

    result = store.get_rules_for_context(
        project="myproj",
        query="fix pytest bug in repository implementation",
        top_k=5,
    )

    ids = {rule["id"] for rule in result["rules"]}
    assert code_id in ids
    assert writing_id not in ids
    assert result["query_filter"]["query_domain"]["primary"] == "code"
    assert result["query_filter"]["domain_filter"]["active"] is True
    assert result["query_filter"]["domain_filter"]["excluded_count"] == 1


def test_query_domain_filter_keeps_global_domain_contextual_rules(monkeypatch, store):
    monkeypatch.setattr(store, "embed", lambda texts: None)
    global_id = _add_rule(
        store,
        "Use checklist handling for multi requirement requests.",
        priority=1,
        tags=["domain:global", "primary_domain:global"],
        category="task_execution",
    )
    writing_id = _add_rule(
        store,
        "For manuscript rewriting, return revised prose directly.",
        priority=10,
        tags=["domain:writing", "primary_domain:writing"],
        category="output_format",
    )

    result = store.get_rules_for_context(
        project="myproj",
        query="fix pytest bug in repository implementation",
        top_k=5,
    )

    ids = {rule["id"] for rule in result["rules"]}
    assert global_id in ids
    assert writing_id not in ids


def test_query_domain_filter_keeps_triggered_rule_from_other_domain(monkeypatch, store):
    monkeypatch.setattr(store, "embed", lambda texts: None)
    banana_id = _add_rule(
        store,
        "When the user says banana for slides, route to the presentation workflow.",
        priority=1,
        tags=["banana", "domain:design", "primary_domain:design"],
        category="skill_routing",
    )
    _add_rule(
        store,
        "Run pytest before changing repository implementation.",
        priority=10,
        tags=["domain:code", "primary_domain:code"],
        category="implementation",
    )

    result = store.get_rules_for_context(
        project="myproj",
        query="banana fix pytest bug in repository implementation",
        top_k=1,
    )

    assert result["rules"][0]["id"] == banana_id
    assert result["query_filter"]["trigger_matches"][0]["matched"] == ["banana"]
    assert result["query_filter"]["domain_filter"]["active"] is True


def test_query_domain_filter_inactive_when_query_confidence_is_low(monkeypatch, store):
    monkeypatch.setattr(store, "embed", lambda texts: None)
    writing_id = _add_rule(
        store,
        "For manuscript rewriting, return revised prose directly.",
        priority=10,
        tags=["domain:writing", "primary_domain:writing"],
        category="output_format",
    )
    _add_rule(
        store,
        "Run pytest before changing repository implementation.",
        priority=1,
        tags=["domain:code", "primary_domain:code"],
        category="implementation",
    )

    result = store.get_rules_for_context(
        project="myproj",
        query="continue this",
        top_k=1,
    )

    assert result["rules"][0]["id"] == writing_id
    assert result["query_filter"]["query_domain"]["primary"] is None
    assert result["query_filter"]["domain_filter"]["active"] is False

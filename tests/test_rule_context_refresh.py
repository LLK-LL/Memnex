from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def srv(monkeypatch, tmp_path):
    (tmp_path / "blobs").mkdir(exist_ok=True)
    (tmp_path / "chroma").mkdir(exist_ok=True)

    import server

    monkeypatch.setattr(server, "MEMORY_DIR", tmp_path)
    server.RULE_CONTEXT_REFRESH_STATE["cooldowns"].clear()
    server.RULE_CONTEXT_REFRESH_STATE["code_errors"].clear()

    store = server.Store()
    store.embed = lambda texts: None
    store.db.execute(
        "INSERT INTO sessions (id, started_at, project, status) "
        "VALUES ('sess-rule-refresh', '2026-07-04T00:00:00Z', 'myproj', 'open')"
    )
    store.db.commit()
    server.store = store
    server.SID = "sess-rule-refresh"
    yield server
    try:
        store.db.close()
    except Exception:
        pass


def _add_rule(store, content, project="myproj", scope=None,
              priority=5, tags=None, category="manual", context=""):
    if scope is None:
        scope = f"project:{project}" if project != "general" else "global"
    now = "2026-07-04T00:00:00Z"
    cur = store.db.execute(
        """INSERT INTO rules (session_id, content, context, category, scope,
                              priority, project, tags, status, created_at, updated_at)
           VALUES ('sess-rule-refresh', ?, ?, ?, ?, ?, ?, ?, 'active', ?, ?)""",
        (content, context, category, scope, priority, project, json.dumps(tags or []), now, now),
    )
    store.db.commit()
    return cur.lastrowid


def _seed_rules(store):
    _add_rule(store, "Always redact secrets before public sync.", tags=["always_on"], priority=10)
    for idx in range(1, 8):
        _add_rule(
            store,
            f"Rule context refresh memory governance relevant rule {idx}.",
            category="memory_governance",
            priority=10 - idx,
        )


def _call(server_mod, name, args):
    return json.loads(asyncio.run(server_mod._do(name, args)))


def test_rule_context_refresh_tool_registered(srv):
    tools = asyncio.run(srv.list_tools())
    assert "rule_context_refresh" in {tool.name for tool in tools}


def test_task_start_refreshes_with_diagnostics_shape(srv):
    _seed_rules(srv.store)

    result = srv.rule_context_refresh(
        srv.store,
        project="myproj",
        phase="build",
        event="task_start",
        latest_user_instruction="implement rule context refresh",
        now=100.0,
    )

    assert result["refreshed"] is True
    assert result["skip_reason"] is None
    assert result["event"] == "task_start"
    assert result["phase"] == "build"
    assert "implement rule context refresh" in result["query"]
    assert result["cooldown_hit"] is False
    assert result["counts"] == {"always_on": 1, "contextual": 3, "total": 4}
    assert result["refresh_reason"] == "task_start"
    assert result["conflict_hints"] == []
    assert len(result["rules"]) == 4


@pytest.mark.parametrize("phase", ["plan", "build", "reflect"])
def test_refreshes_on_plan_build_reflect_phase_entry(srv, phase):
    _seed_rules(srv.store)

    result = srv.rule_context_refresh(
        srv.store,
        project="myproj",
        phase=phase,
        event="phase_change",
        latest_user_instruction="continue implementation",
        now=100.0,
    )

    assert result["refreshed"] is True
    assert result["refresh_reason"] == f"phase_change:{phase}"


@pytest.mark.parametrize("phase", ["van", "creative", "archive"])
def test_van_creative_archive_phase_entry_skips_by_default(srv, phase):
    _seed_rules(srv.store)

    result = srv.rule_context_refresh(
        srv.store,
        project="myproj",
        phase=phase,
        event="phase_change",
        latest_user_instruction="continue implementation",
        now=100.0,
    )

    assert result["refreshed"] is False
    assert result["skip_reason"] == "phase_not_refreshing"
    assert result["counts"] == {"always_on": 0, "contextual": 0, "total": 0}
    assert result["rules"] == []


def test_cooldown_hit_for_same_phase_query_and_error_category(srv):
    _seed_rules(srv.store)
    args = dict(
        project="myproj",
        phase="build",
        event="error",
        latest_user_instruction="fix timeout",
        error_category="timeout",
    )

    first = srv.rule_context_refresh(srv.store, now=100.0, **args)
    second = srv.rule_context_refresh(srv.store, now=120.0, **args)

    assert first["refreshed"] is True
    assert second["refreshed"] is False
    assert second["skip_reason"] == "cooldown_hit"
    assert second["cooldown_hit"] is True


def test_different_error_category_is_not_blocked_by_cooldown(srv):
    _seed_rules(srv.store)

    timeout_result = srv.rule_context_refresh(
        srv.store,
        project="myproj",
        phase="build",
        event="error",
        latest_user_instruction="fix tool failure",
        error_category="timeout",
        now=100.0,
    )
    api_result = srv.rule_context_refresh(
        srv.store,
        project="myproj",
        phase="build",
        event="error",
        latest_user_instruction="fix tool failure",
        error_category="api_error",
        now=120.0,
    )

    assert timeout_result["refreshed"] is True
    assert api_result["refreshed"] is True
    assert timeout_result["cooldown_key"] != api_result["cooldown_key"]


@pytest.mark.parametrize(
    "category",
    ["timeout", "config_error", "api_error", "missing_context", "wrong_assumption"],
)
def test_immediate_error_categories_refresh(srv, category):
    _seed_rules(srv.store)

    result = srv.rule_context_refresh(
        srv.store,
        project="myproj",
        phase="build",
        event="error",
        latest_user_instruction=f"handle {category}",
        error_category=category,
        now=100.0,
    )

    assert result["refreshed"] is True
    assert result["counts"]["contextual"] == 5


def test_code_error_refreshes_on_second_consecutive_occurrence(srv):
    _seed_rules(srv.store)
    args = dict(
        project="myproj",
        phase="build",
        event="error",
        latest_user_instruction="fix assertion failure",
        error_category="code_error",
    )

    first = srv.rule_context_refresh(srv.store, now=100.0, **args)
    second = srv.rule_context_refresh(srv.store, now=110.0, **args)

    assert first["refreshed"] is False
    assert first["skip_reason"] == "code_error_threshold"
    assert second["refreshed"] is True
    assert second["refresh_reason"] == "error:code_error:threshold"


def test_query_aware_rules_context_returns_all_always_on_without_count_limit(srv):
    for idx in range(5):
        _add_rule(srv.store, f"Always-on baseline rule {idx}.", tags=["always_on"], priority=10)
    for idx in range(3):
        _add_rule(srv.store, f"Rule context refresh relevant rule {idx}.", priority=8)

    result = srv.store.get_rules_for_context(
        project="myproj",
        phase="build",
        detail="compact",
        query="rule context refresh",
        top_k=1,
        include_always_on=True,
    )

    assert result["query_filter"]["always_on_count"] == 5
    assert result["query_filter"]["contextual_count"] == 1
    assert result["rules_count"] == 6


def test_contextual_rules_replace_between_refreshes_instead_of_accumulating(srv):
    _seed_rules(srv.store)

    first = srv.rule_context_refresh(
        srv.store,
        project="myproj",
        phase="build",
        event="task_start",
        latest_user_instruction="rule context refresh",
        now=100.0,
    )
    second = srv.rule_context_refresh(
        srv.store,
        project="myproj",
        phase="build",
        event="target_change",
        latest_user_instruction="different memory governance target",
        now=500.0,
    )

    assert first["counts"]["total"] == 4
    assert second["counts"]["total"] == 6
    assert len(second["rules"]) == 6


def test_mcp_dispatcher_calls_rule_context_refresh(srv):
    _seed_rules(srv.store)

    result = _call(srv, "rule_context_refresh", {
        "project": "myproj",
        "phase": "build",
        "event": "task_start",
        "latest_user_instruction": "implement rule context refresh",
    })

    assert result["refreshed"] is True
    assert result["counts"]["total"] == 4

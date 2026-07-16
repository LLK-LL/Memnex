"""Tests for v8.0 phase-scoped rule loading (self_rules_context + rule_set_phase).

Uses tag-based routing: a rule is phase-specific iff its tags JSON contains
"phase:<X>". Rules without any "phase:*" tag are core — applied to every phase.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pytest

# Ensure src/ is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def store(monkeypatch, tmp_path):
    """Fresh Store on an isolated MEMORY_DIR (no prod data)."""
    (tmp_path / "blobs").mkdir(exist_ok=True)
    (tmp_path / "chroma").mkdir(exist_ok=True)

    import server  # lazy import so MEMORY_DIR override sticks
    monkeypatch.setattr(server, "MEMORY_DIR", tmp_path)

    s = server.Store()
    # Need an active session for rules (rules.session_id NOT NULL).
    s.db.execute(
        "INSERT INTO sessions (id, started_at, project, status) "
        "VALUES ('sess-phase-test', '2026-04-19T00:00:00Z', 'myproj', 'open')"
    )
    s.db.commit()
    yield s
    try:
        s.db.close()
    except Exception:
        pass


def _add_rule(store, content, project="myproj", scope=None,
              priority=5, tags=None, category="manual", context=""):
    """Helper: insert a rule, return rule_id."""
    if scope is None:
        scope = f"project:{project}" if project != "general" else "global"
    now = "2026-04-19T00:00:00Z"
    cur = store.db.execute(
        """INSERT INTO rules (session_id, content, context, category, scope,
                              priority, project, tags, status, created_at, updated_at)
           VALUES ('sess-phase-test', ?, ?, ?, ?, ?, ?, ?, 'active', ?, ?)""",
        (content, context, category, scope, priority, project, json.dumps(tags or []), now, now),
    )
    store.db.commit()
    return cur.lastrowid


# ──────────────────────────────────────────────
# self_rules_context: backward compat + phase filter
# ──────────────────────────────────────────────

def test_self_rules_context_no_phase_returns_all(store):
    """Backward compat: phase=None returns every active rule (core + phased)."""
    _add_rule(store, "core rule A")
    _add_rule(store, "build-only rule", tags=["phase:build"])
    _add_rule(store, "plan-only rule", tags=["phase:plan"])

    r = store.get_rules_for_context(project="myproj")
    contents = [x["content"] for x in r["rules"]]
    assert r["rules_count"] == 3
    assert "core rule A" in contents
    assert "build-only rule" in contents
    assert "plan-only rule" in contents
    # No phase_filter key when phase not requested
    assert "phase_filter" not in r


def test_self_rules_context_build_returns_core_plus_build(store):
    """phase='build' → core rules (no phase tag) + rules tagged phase:build."""
    _add_rule(store, "core 1")
    _add_rule(store, "core 2", tags=["go", "misc"])  # no phase:* tags
    _add_rule(store, "build rule", tags=["phase:build"])
    _add_rule(store, "plan rule", tags=["phase:plan"])

    r = store.get_rules_for_context(project="myproj", phase="build")
    contents = {x["content"] for x in r["rules"]}
    assert r["phase_filter"] == "build"
    assert r["rules_count"] == 3
    assert contents == {"core 1", "core 2", "build rule"}


def test_self_rules_context_plan_excludes_build_rules(store):
    """phase='plan' must not leak build-only rules."""
    _add_rule(store, "core")
    _add_rule(store, "build only", tags=["phase:build"])
    _add_rule(store, "plan only", tags=["phase:plan"])

    r = store.get_rules_for_context(project="myproj", phase="plan")
    contents = {x["content"] for x in r["rules"]}
    assert contents == {"core", "plan only"}
    assert "build only" not in contents


def test_self_rules_context_compact_omits_metadata(store):
    _add_rule(store, "compact core", tags=["phase:build"])

    r = store.get_rules_for_context(project="myproj", phase="build", detail="compact")

    assert r["detail"] == "compact"
    assert r["rules_count"] == 1
    [rule] = r["rules"]
    assert set(rule) == {"id", "content", "category", "priority", "detail_available"}
    assert rule["content"] == "compact core"
    assert rule["detail_available"] is False
    assert "fire_count" not in rule
    assert "created_at" not in rule


def test_self_rules_context_compact_truncates_long_rules(store):
    long_rule = "x" * 220
    _add_rule(store, long_rule, tags=["phase:build"])

    r = store.get_rules_for_context(project="myproj", phase="build", detail="compact")

    [rule] = r["rules"]
    assert len(rule["content"]) < len(long_rule)
    assert rule["content"].endswith("...")
    assert rule["detail_available"] is True


def test_self_rules_context_unknown_phase_raises(store):
    """Unknown phase returns an error payload with hint."""
    _add_rule(store, "core")
    r = store.get_rules_for_context(project="myproj", phase="deploy")
    assert "error" in r
    assert "deploy" in r["error"]
    # Hint lists valid phases
    for valid in ("van", "plan", "creative", "build", "reflect", "archive"):
        assert valid in r["error"]


def test_phase_filter_returns_expected_count(store):
    """Seed: 3 core + 2 build + 1 plan. Request phase='build' → 5 rules."""
    _add_rule(store, "core 1")
    _add_rule(store, "core 2")
    _add_rule(store, "core 3", tags=["lang:go"])  # no phase:* tag
    _add_rule(store, "build 1", tags=["phase:build"])
    _add_rule(store, "build 2", tags=["phase:build", "lang:sql"])
    _add_rule(store, "plan 1", tags=["phase:plan"])

    r = store.get_rules_for_context(project="myproj", phase="build")
    assert r["rules_count"] == 5
    contents = {x["content"] for x in r["rules"]}
    assert contents == {"core 1", "core 2", "core 3", "build 1", "build 2"}


# ──────────────────────────────────────────────
# rule_set_phase
# ──────────────────────────────────────────────

def test_query_aware_rules_context_returns_always_on_plus_relevant_top_k(monkeypatch, store):
    monkeypatch.setattr(store, "embed", lambda texts: None)
    _add_rule(
        store,
        "Before public publishing or pushing, remove secrets and tokens.",
        priority=10,
        tags=["always_on", "security-critical"],
        category="security",
    )
    _add_rule(
        store,
        "Memory iteration must use the layered chain RAG memory preference layer rule layer routing layer.",
        priority=10,
        category="iteration",
    )
    _add_rule(
        store,
        "Rule layer recall should rank rules by current query and reduce unrelated core rules.",
        priority=9,
        category="memory_governance",
    )
    _add_rule(
        store,
        "When the user asks for a QR code, provide command-line output by default.",
        priority=9,
        category="output_format",
    )
    _add_rule(
        store,
        "When the user says banana for slides, route to banana-ppt-workflow.",
        priority=9,
        category="skill_routing",
    )
    _add_rule(
        store,
        "When the user mentions Igor, use the igor-remote-codex skill.",
        priority=9,
        category="skill_routing",
    )

    r = store.get_rules_for_context(
        project="myproj",
        phase="plan",
        detail="compact",
        query="规则层召回为什么包含很多用不上的内容 rule layer memory routing",
        top_k=2,
    )

    contents = [x["content"] for x in r["rules"]]
    joined = "\n".join(contents)
    assert r["rules_count"] == 3
    assert r["query_filter"]["strategy"] == "always_on_plus_trigger_semantic_top_k"
    assert "remove secrets and tokens" in joined
    assert "Rule layer recall" in joined
    assert "Memory iteration" in joined
    assert "QR code" not in joined
    assert "banana" not in joined
    assert "Igor" not in joined


def test_query_aware_rules_context_can_skip_always_on(monkeypatch, store):
    monkeypatch.setattr(store, "embed", lambda texts: None)
    _add_rule(store, "Always remove secrets before publishing.", tags=["always_on"], priority=10)
    _add_rule(store, "Rule layer recall ranks memory governance rules by query.", priority=9)

    r = store.get_rules_for_context(
        project="myproj",
        query="memory governance rule layer recall",
        top_k=1,
        include_always_on=False,
    )

    contents = [x["content"] for x in r["rules"]]
    assert contents == ["Rule layer recall ranks memory governance rules by query."]
    assert r["query_filter"]["always_on_count"] == 0


def test_query_aware_rules_context_exact_tag_match_outranks_generic_rules(monkeypatch, store):
    monkeypatch.setattr(store, "embed", lambda texts: None)
    for idx in range(25):
        _add_rule(
            store,
            f"Memory governance generic routing rule {idx}.",
            priority=10,
            category="memory_governance",
        )
    qr_id = _add_rule(
        store,
        "When the user asks for code output format, provide terminal-safe output.",
        priority=1,
        tags=["qr", "\u4e8c\u7ef4\u7801", "output-format"],
        category="output_format",
    )

    r = store.get_rules_for_context(
        project="myproj",
        query="QR memory governance routing",
        top_k=1,
    )

    assert r["rules_count"] == 1
    assert r["rules"][0]["id"] == qr_id
    assert r["query_filter"]["candidate_count"] == 26
    assert r["query_filter"]["contextual_count"] == 1
    assert r["query_filter"]["trigger_matches"] == [
        {"rule_id": qr_id, "matched": ["qr"], "source": "tags"}
    ]


def test_query_aware_rules_context_trigger_matches_count_toward_limit(monkeypatch, store):
    monkeypatch.setattr(store, "embed", lambda texts: None)
    banana_id = _add_rule(
        store,
        "When the user says banana for slides, route to the presentation workflow.",
        priority=2,
        tags=["banana", "ppt", "presentation"],
        category="skill_routing",
    )
    _add_rule(
        store,
        "Memory governance generic routing rule.",
        priority=10,
        category="memory_governance",
    )

    r = store.get_rules_for_context(
        project="myproj",
        query="banana memory governance",
        top_k=1,
    )

    assert r["rules_count"] == 1
    assert r["rules"][0]["id"] == banana_id
    assert r["query_filter"]["contextual_count"] == 1
    assert r["query_filter"]["contextual_limit"] == 1


@pytest.mark.parametrize(
    ("query", "expected_tag"),
    [
        ("Igor remote work", "igor"),
        ("banana slides", "banana"),
        ("\u4e8c\u7ef4\u7801 output", "\u4e8c\u7ef4\u7801"),
    ],
)
def test_query_aware_rules_context_returns_explicit_trigger_rules(
    monkeypatch,
    store,
    query,
    expected_tag,
):
    monkeypatch.setattr(store, "embed", lambda texts: None)
    rule_ids = {
        "igor": _add_rule(
            store,
            "When the user mentions Igor, use the remote Codex workflow.",
            priority=2,
            tags=["igor", "remote-codex-cli", "skill-routing"],
        ),
        "banana": _add_rule(
            store,
            "When the user says banana, route slide work to banana-ppt-workflow.",
            priority=2,
            tags=["banana", "ppt", "presentation"],
        ),
        "\u4e8c\u7ef4\u7801": _add_rule(
            store,
            "When the user asks for a QR code, provide command-line output.",
            priority=2,
            tags=["qr", "\u4e8c\u7ef4\u7801", "output-format"],
        ),
    }
    _add_rule(
        store,
        "Memory governance generic routing rule.",
        priority=10,
        category="memory_governance",
    )

    r = store.get_rules_for_context(project="myproj", query=query, top_k=1)

    assert r["rules_count"] == 1
    assert r["rules"][0]["id"] == rule_ids[expected_tag]
    assert r["query_filter"]["trigger_matches"][0]["matched"] == [expected_tag]


def test_rule_set_phase_adds_tag_or_column(store):
    """set_rule_phase('build') attaches 'phase:build' tag."""
    rid = _add_rule(store, "mutable rule", tags=["go"])
    result = store.set_rule_phase(rid, "build")
    assert result == {"rule_id": rid, "phase": "build", "updated": True}

    row = store.db.execute("SELECT tags FROM rules WHERE id=?", (rid,)).fetchone()
    tags = json.loads(row[0])
    assert "phase:build" in tags
    assert "go" in tags  # existing tags preserved


def test_rule_set_phase_replaces_existing_phase(store):
    """Setting phase twice replaces previous phase tag."""
    rid = _add_rule(store, "mutable", tags=["phase:plan", "keep"])
    store.set_rule_phase(rid, "build")

    row = store.db.execute("SELECT tags FROM rules WHERE id=?", (rid,)).fetchone()
    tags = json.loads(row[0])
    assert "phase:build" in tags
    assert "phase:plan" not in tags
    assert "keep" in tags


def test_rule_set_phase_none_removes_phase(store):
    """phase=None clears phase:* tag → rule becomes core."""
    rid = _add_rule(store, "phased", tags=["phase:build", "misc"])
    result = store.set_rule_phase(rid, None)
    assert result["phase"] is None
    assert result["updated"] is True

    row = store.db.execute("SELECT tags FROM rules WHERE id=?", (rid,)).fetchone()
    tags = json.loads(row[0])
    assert not any(t.startswith("phase:") for t in tags)
    assert "misc" in tags  # other tags preserved

    # And now it behaves as a core rule for any phase.
    r = store.get_rules_for_context(project="myproj", phase="plan")
    assert any(x["id"] == rid for x in r["rules"])


def test_rule_set_phase_unknown_phase_errors(store):
    rid = _add_rule(store, "victim")
    result = store.set_rule_phase(rid, "deploy")
    assert "error" in result
    assert "deploy" in result["error"]


def test_rule_set_phase_missing_rule(store):
    result = store.set_rule_phase(999_999, "build")
    assert "error" in result
    assert result["rule_id"] == 999_999


# ──────────────────────────────────────────────
# Integration: phase_transition exposes rules_preview
# ──────────────────────────────────────────────

def test_phase_transition_adds_rules_preview_in_response():
    """phase_transition() returns rules_preview pointing at rule_context_refresh."""
    from task_phases import TaskPhases

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    mig = Path(__file__).parent.parent / "migrations" / "012_task_phases.sql"
    conn.executescript(mig.read_text(encoding="utf-8"))
    proc = Path(__file__).parent.parent / "migrations" / "009_procedural.sql"
    conn.executescript(proc.read_text(encoding="utf-8"))

    tp = TaskPhases(conn)
    tp.create_task("t-preview", "add /users endpoint", level=2)
    r = tp.phase_transition("t-preview", "plan")
    assert "rules_preview" in r
    assert "plan" in r["rules_preview"]
    assert "rule_context_refresh" in r["rules_preview"]

    # And on build, preview should mention build.
    r2 = tp.phase_transition("t-preview", "build")
    assert "build" in r2["rules_preview"]

    conn.close()

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def store(monkeypatch, tmp_path):
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

    (tmp_path / "blobs").mkdir(exist_ok=True)
    (tmp_path / "chroma").mkdir(exist_ok=True)

    import server

    monkeypatch.setattr(server, "MEMORY_DIR", tmp_path)
    s = server.Store()
    yield s
    try:
        s.db.close()
    except Exception:
        pass


def _save(store, sid, content, namespace):
    return store.save_knowledge(
        sid,
        content,
        "fact",
        project="namespace-recall",
        tags=["namespace-recall", namespace],
        skip_quality=True,
        agent_namespace=namespace,
    )[0]


def _recall(store):
    import server

    return server.Recall(store)


def test_search_defaults_to_codex_namespace(store):
    codex_id = _save(store, "ns-recall-codex", "Codex-only namespace recall probe alpha", "codex")
    reasonix_id = _save(store, "ns-recall-reasonix", "Reasonix-only namespace recall probe alpha", "reasonix")

    result = _recall(store).search(
        "namespace recall probe alpha",
        project="namespace-recall",
        limit=10,
        detail="full",
    )
    ids = {item["id"] for group in result.get("results", {}).values() for item in group}

    assert codex_id in ids
    assert reasonix_id not in ids
    assert result["agent_namespaces"] == ["codex"]


def test_search_can_explicitly_query_reasonix_namespace(store):
    codex_id = _save(store, "ns-recall-codex-explicit", "Explicit namespace recall probe beta", "codex")
    reasonix_id = _save(store, "ns-recall-reasonix-explicit", "Explicit namespace recall probe beta", "reasonix")

    result = _recall(store).search(
        "explicit namespace recall probe beta",
        project="namespace-recall",
        limit=10,
        detail="full",
        agent_namespace="reasonix",
    )
    ids = {item["id"] for group in result.get("results", {}).values() for item in group}

    assert reasonix_id in ids
    assert codex_id not in ids
    assert result["agent_namespaces"] == ["reasonix"]


def test_search_all_agents_scope_returns_both_namespaces(store):
    codex_id = _save(store, "ns-recall-codex-all", "All agents namespace recall probe gamma", "codex")
    reasonix_id = _save(store, "ns-recall-reasonix-all", "All agents namespace recall probe gamma", "reasonix")

    result = _recall(store).search(
        "all agents namespace recall probe gamma",
        project="namespace-recall",
        limit=10,
        detail="full",
        scope="all_agents",
    )
    ids = {item["id"] for group in result.get("results", {}).values() for item in group}

    assert {codex_id, reasonix_id}.issubset(ids)
    assert result["agent_scope"] == "all_agents"

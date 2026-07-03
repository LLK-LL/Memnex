"""Integration: memory_save → representations_queue; reflection generates views."""

from __future__ import annotations

import asyncio
import hashlib
import json
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


def _fake_embedder(text: str) -> list[float]:
    h = hashlib.md5(text.encode()).digest()
    return [b / 255.0 for b in h[:8]]


def test_ollama_representation_completion_uses_resolved_model(monkeypatch):
    import representations

    captured = {}

    class _Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def read(self):
            return b'{"response":"ok"}'

    def fake_urlopen(req, timeout):
        captured["body"] = json.loads(req.data.decode("utf-8"))
        return _Response()

    monkeypatch.setattr(representations.config, "get_phase_provider", lambda phase: "ollama")
    monkeypatch.setattr(representations.config, "get_phase_model", lambda phase: "qwen2.5-coder:7b")
    monkeypatch.setattr(representations.config, "resolve_ollama_model", lambda name=None: "qwen2.5:3b")
    monkeypatch.setattr(representations.urllib.request, "urlopen", fake_urlopen)

    assert representations._llm_complete("prompt") == "ok"
    assert captured["body"]["model"] == "qwen2.5:3b"


def test_save_enqueues_representations_by_default(store, monkeypatch):
    monkeypatch.setattr(store, "embed", lambda texts: [_fake_embedder(t) for t in texts])
    store.db.execute(
        "INSERT INTO sessions (id, started_at, project, status) VALUES ('s1', '2026-04-14T00:00:00Z', 'demo', 'open')"
    )
    store.db.commit()
    rid, *_save = store.save_knowledge(
        sid="s1", content="content", ktype="fact", project="demo"
    )

    row = store.db.execute(
        "SELECT status FROM representations_queue WHERE knowledge_id=?", (rid,)
    ).fetchone()
    assert row is not None
    assert row["status"] == "pending"
    count = store.db.execute(
        "SELECT COUNT(*) FROM knowledge_representations WHERE knowledge_id=?",
        (rid,),
    ).fetchone()[0]
    assert count == 0


def test_save_generates_representations_when_immediate_enabled(store, monkeypatch):
    monkeypatch.setenv("MEMORY_IMMEDIATE_REPRESENTATIONS", "true")
    monkeypatch.setattr("config.has_llm", lambda phase=None: False)
    monkeypatch.setattr(store, "embed", lambda texts: [_fake_embedder(t) for t in texts])
    store.db.execute(
        "INSERT INTO sessions (id, started_at, project, status) VALUES ('s1', '2026-04-14T00:00:00Z', 'demo', 'open')"
    )
    store.db.commit()
    rid, *_save = store.save_knowledge(
        sid="s1", content="content", ktype="fact", project="demo"
    )

    row = store.db.execute(
        "SELECT status FROM representations_queue WHERE knowledge_id=?", (rid,)
    ).fetchone()
    assert row is not None
    assert row["status"] == "done"
    kinds = {
        r["representation"]
        for r in store.db.execute(
            "SELECT representation FROM knowledge_representations WHERE knowledge_id=?",
            (rid,),
        ).fetchall()
    }
    assert {"raw", "summary", "keywords", "compressed"}.issubset(kinds)


def test_background_worker_processes_pending_representations(store, monkeypatch):
    import representations
    from representation_worker import RepresentationWorker

    monkeypatch.setattr(store, "embed", lambda texts: [_fake_embedder(t) for t in texts])
    monkeypatch.setattr("config.has_llm", lambda phase=None: True)
    monkeypatch.setattr(
        representations,
        "_llm_complete",
        lambda prompt, **_: "generated representation",
    )
    store.db.execute(
        "INSERT INTO sessions (id, started_at, project, status) VALUES ('s1', '2026-04-14T00:00:00Z', 'demo', 'open')"
    )
    store.db.commit()
    rid, *_save = store.save_knowledge(
        sid="s1",
        content="background representation worker content " * 40,
        ktype="fact",
        project="demo",
    )

    stats = RepresentationWorker(store, limit=1).drain_once()

    assert stats["processed"] == 1
    row = store.db.execute(
        "SELECT status FROM representations_queue WHERE knowledge_id=?", (rid,)
    ).fetchone()
    assert row["status"] == "done"
    kinds = {
        r["representation"]
        for r in store.db.execute(
            "SELECT representation FROM knowledge_representations WHERE knowledge_id=?",
            (rid,),
        ).fetchall()
    }
    assert {"raw", "summary", "keywords", "questions", "compressed"}.issubset(kinds)


def test_reflection_generates_representations(store, monkeypatch):
    from reflection.agent import ReflectionAgent
    import representations
    monkeypatch.setattr(store, "embed", lambda texts: [_fake_embedder(t) for t in texts])

    store.db.execute(
        "INSERT INTO sessions (id, started_at, project, status) VALUES ('s1', '2026-04-14T00:00:00Z', 'demo', 'open')"
    )
    store.db.commit()

    long_content = (
        "A comprehensive production guide about Go microservices built with "
        "gRPC transport and PostgreSQL 18 as backing store. It covers health "
        "checks, Prometheus metrics, structured slog logging, OpenTelemetry "
        "tracing, Docker Compose v2 orchestration, GitHub Actions pipelines, "
        "and safe database migrations with concurrent index creation. "
        "Additional sections discuss auth via JWT, rate limiting, and caching."
    ) * 5
    rid, *_save = store.save_knowledge(
        sid="s1", content=long_content, ktype="fact", project="demo"
    )

    # Stub the LLM in representations module
    def fake_llm(prompt, **_):
        p = prompt.lower()
        if "summary" in p or "summarize" in p:
            return "Short summary of Go microservices guide."
        if "keyword" in p:
            return "go, grpc, postgres, microservices"
        if "question" in p:
            return "What services does this cover?\nHow does auth work?"
        return "Compressed Go microservices guide with observability and migrations."

    monkeypatch.setattr(representations, "_llm_complete", fake_llm)
    monkeypatch.setattr("config.has_llm", lambda phase=None: True)

    # Also stub triple extractor + deep_enricher to keep run_full fast and offline
    import ingestion.extractor as extractor_mod
    monkeypatch.setattr(
        extractor_mod.ConceptExtractor, "extract_and_link",
        lambda self, text, knowledge_id=None, deep=False: {"relations": [], "entities": []},
    )
    import deep_enricher
    monkeypatch.setattr(deep_enricher, "_llm_complete", lambda *a, **kw: "")

    agent = ReflectionAgent(store.db, embedder=_fake_embedder)
    report = asyncio.run(agent.run_full())

    assert report["representations"]["processed"] >= 1

    # The background reflection drain generates RAG-ready views after save.
    kinds = {
        r["representation"]
        for r in store.db.execute(
            "SELECT representation FROM knowledge_representations WHERE knowledge_id=?",
            (rid,),
        ).fetchall()
    }
    assert "raw" in kinds
    assert "summary" in kinds
    assert "keywords" in kinds
    assert "compressed" in kinds

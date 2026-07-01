"""Tests for src/embed_provider.py — cloud + local embedding provider abstraction."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────


class _FakeResp:
    def __init__(self, payload: dict) -> None:
        self._payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self):
        return self._payload


def _capture_urlopen(payload: dict, sink: dict):
    # Accept and discard `context=` (production callers may pass an
    # SSL context kwarg for certifi-based fixes); accept any other
    # forward-compatible kwargs so tests don't break when callers
    # adopt new urllib options.
    def fake(req, timeout=None, *, context=None, **_kw):
        sink["url"] = req.full_url
        sink["headers"] = dict(req.headers)
        sink["body"] = json.loads(req.data.decode("utf-8")) if req.data else None
        sink["timeout"] = timeout
        sink["context"] = context
        return _FakeResp(payload)
    return fake


# ──────────────────────────────────────────────
# FastEmbedProvider — wraps existing fastembed flow
# ──────────────────────────────────────────────


def test_fastembed_provider_extracts_existing_logic(monkeypatch):
    """Confirms the provider drives a TextEmbedding-like object the same way
    the current server.py does: list(model.embed(texts)) → tolist()."""
    import embed_provider

    class _FakeVec:
        def __init__(self, vals: list[float]) -> None:
            self._vals = vals

        def tolist(self) -> list[float]:
            return list(self._vals)

    class _FakeModel:
        def __init__(self, model_name: str) -> None:
            self.model_name = model_name

        def embed(self, texts):
            # Emulate generator of numpy-like arrays
            for i, t in enumerate(texts):
                yield _FakeVec([float(i), float(len(t)), 0.5])

    fake_module = type(sys)("fastembed")
    fake_module.TextEmbedding = _FakeModel  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "fastembed", fake_module)

    # Use a model not in the known-dim table so dim() is populated from
    # the first embed() call rather than the lookup.
    p = embed_provider.FastEmbedProvider(model="unknown/custom-model-xyz")
    assert p.available() is True
    assert p.dim() == 0  # unknown until first call
    out = p.embed(["ab", "abcd"])
    assert out == [[0.0, 2.0, 0.5], [1.0, 4.0, 0.5]]
    assert p.dim() == 3  # cached after first call

    # Known-dim model reports expected dim up front (table lookup)
    p_known = embed_provider.FastEmbedProvider(model="BAAI/bge-small-en-v1.5")
    assert p_known.dim() == 384


def test_fastembed_provider_uses_configured_cache_dir(monkeypatch):
    import embed_provider

    captured = {}

    class _FakeModel:
        def __init__(self, model_name: str, **kwargs) -> None:
            captured["model_name"] = model_name
            captured["kwargs"] = kwargs

        def embed(self, texts):
            for _ in texts:
                yield [0.1, 0.2, 0.3]

    fake_module = type(sys)("fastembed")
    fake_module.TextEmbedding = _FakeModel  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "fastembed", fake_module)
    monkeypatch.setenv("FASTEMBED_CACHE_DIR", r"D:\CodexCache\fastembed")

    p = embed_provider.FastEmbedProvider(model="BAAI/bge-small-en-v1.5")
    assert p.available() is True
    assert captured["kwargs"]["cache_dir"] == r"D:\CodexCache\fastembed"


def test_fastembed_provider_returns_unavailable_when_missing(monkeypatch):
    import embed_provider

    # Force ImportError by removing fastembed from sys.modules and shadowing
    monkeypatch.setitem(sys.modules, "fastembed", None)

    p = embed_provider.FastEmbedProvider(model="x")
    assert p.available() is False
    with pytest.raises(RuntimeError, match="unavailable"):
        p.embed(["hi"])


# ──────────────────────────────────────────────
# OpenAIEmbedProvider
# ──────────────────────────────────────────────


def test_openai_embed_provider_batch(monkeypatch):
    import embed_provider

    sink: dict = {}
    payload = {
        "data": [
            {"index": 0, "embedding": [0.1, 0.2, 0.3]},
            {"index": 1, "embedding": [0.4, 0.5, 0.6]},
        ]
    }
    monkeypatch.setattr(
        embed_provider.urllib.request, "urlopen", _capture_urlopen(payload, sink)
    )

    p = embed_provider.OpenAIEmbedProvider(
        api_key="sk-x",
        api_base="https://api.openai.com/v1",
        model="text-embedding-3-small",
    )
    assert p.available() is True
    out = p.embed(["hello", "world"], timeout=11.0)

    assert out == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    assert sink["url"] == "https://api.openai.com/v1/embeddings"
    h = {k.lower(): v for k, v in sink["headers"].items()}
    assert h["authorization"] == "Bearer sk-x"
    assert sink["body"] == {
        "input": ["hello", "world"],
        "model": "text-embedding-3-small",
    }
    assert sink["timeout"] == 11.0


def test_openai_embed_provider_reorders_by_index(monkeypatch):
    """Out-of-order responses should be restored to input order."""
    import embed_provider

    sink: dict = {}
    payload = {
        "data": [
            {"index": 1, "embedding": [9.0]},
            {"index": 0, "embedding": [1.0]},
        ]
    }
    monkeypatch.setattr(
        embed_provider.urllib.request, "urlopen", _capture_urlopen(payload, sink)
    )

    p = embed_provider.OpenAIEmbedProvider(
        api_key="sk", api_base="https://x/v1", model="text-embedding-3-small"
    )
    out = p.embed(["a", "b"])
    assert out == [[1.0], [9.0]]


def test_openai_embed_provider_empty_texts_skips_http(monkeypatch):
    import embed_provider

    def should_not_be_called(req, timeout=None):
        raise AssertionError("HTTP call on empty input")

    monkeypatch.setattr(embed_provider.urllib.request, "urlopen", should_not_be_called)
    p = embed_provider.OpenAIEmbedProvider(
        api_key="sk", api_base="https://x/v1", model="m"
    )
    assert p.embed([]) == []


def test_openai_embed_provider_unavailable_without_key():
    import embed_provider

    p = embed_provider.OpenAIEmbedProvider(
        api_key=None, api_base="https://api.openai.com/v1"
    )
    assert p.available() is False
    with pytest.raises(RuntimeError, match="missing api_key"):
        p.embed(["x"])


# ──────────────────────────────────────────────
# CohereEmbedProvider
# ──────────────────────────────────────────────


def test_cohere_embed_provider_batch_v2(monkeypatch):
    import embed_provider

    sink: dict = {}
    payload = {"embeddings": {"float": [[0.1, 0.2], [0.3, 0.4]]}}
    monkeypatch.setattr(
        embed_provider.urllib.request, "urlopen", _capture_urlopen(payload, sink)
    )

    p = embed_provider.CohereEmbedProvider(
        api_key="co-test",
        api_base="https://api.cohere.com/v2",
        model="embed-multilingual-v3.0",
    )
    out = p.embed(["hi", "bye"])

    assert out == [[0.1, 0.2], [0.3, 0.4]]
    assert sink["url"] == "https://api.cohere.com/v2/embed"
    h = {k.lower(): v for k, v in sink["headers"].items()}
    assert h["authorization"] == "Bearer co-test"
    assert sink["body"]["texts"] == ["hi", "bye"]
    assert sink["body"]["model"] == "embed-multilingual-v3.0"
    assert sink["body"]["input_type"] == "search_document"


def test_cohere_embed_provider_legacy_shape(monkeypatch):
    import embed_provider

    sink: dict = {}
    payload = {"embeddings": [[1.0, 2.0]]}
    monkeypatch.setattr(
        embed_provider.urllib.request, "urlopen", _capture_urlopen(payload, sink)
    )

    p = embed_provider.CohereEmbedProvider(
        api_key="k", api_base="https://api.cohere.com/v2", model="embed-english-v3.0"
    )
    assert p.embed(["x"]) == [[1.0, 2.0]]


# ──────────────────────────────────────────────
# Dim reporting
# ──────────────────────────────────────────────


def test_embed_provider_dim_matches_model():
    import embed_provider

    small = embed_provider.OpenAIEmbedProvider(
        api_key="k", api_base="https://x/v1", model="text-embedding-3-small"
    )
    large = embed_provider.OpenAIEmbedProvider(
        api_key="k", api_base="https://x/v1", model="text-embedding-3-large"
    )
    coh = embed_provider.CohereEmbedProvider(
        api_key="k", api_base="https://x/v2", model="embed-multilingual-v3.0"
    )

    assert small.dim() == 1536
    assert large.dim() == 3072
    assert coh.dim() == 1024


def test_make_embed_provider_factory(monkeypatch):
    import embed_provider

    monkeypatch.setenv("OPENAI_API_KEY", "sk-env")
    p = embed_provider.make_embed_provider("openai")
    assert isinstance(p, embed_provider.OpenAIEmbedProvider)
    assert p.api_key == "sk-env"

    monkeypatch.setenv("COHERE_API_KEY", "co-env")
    monkeypatch.delenv("MEMORY_EMBED_API_KEY", raising=False)
    q = embed_provider.make_embed_provider("cohere")
    assert isinstance(q, embed_provider.CohereEmbedProvider)
    assert q.api_key == "co-env"

    with pytest.raises(ValueError, match="unknown embedding provider"):
        embed_provider.make_embed_provider("bogus")

def test_sentence_transformers_fallback_is_local_only(monkeypatch, tmp_path):
    monkeypatch.setenv("TAM_MEMORY_DIR", str(tmp_path))
    monkeypatch.setenv("MEMORY_MODE", "fast")
    monkeypatch.delenv("MEMORY_ALLOW_HF_DOWNLOAD_IN_HOT_PATH", raising=False)

    import server

    calls = []

    class FakeSentenceTransformer:
        def __init__(self, model_name, **kwargs):
            calls.append((model_name, kwargs))
            raise OSError("model not cached")

    store = object.__new__(server.Store)
    store._embedder = None

    monkeypatch.setattr(server, "HAS_ST", True)
    monkeypatch.setattr(server, "SentenceTransformer", FakeSentenceTransformer, raising=False)

    assert server.Store.embedder.fget(store) is None
    assert calls == [(server.EMBEDDING_MODEL, {"local_files_only": True})]
    assert server.Store.embedder.fget(store) is None
    assert len(calls) == 1

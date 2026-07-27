"""v11.0 Memory Core — deterministic, LLM-free hot path.

This package is THE rule the rest of the codebase must obey:

    Nothing in `memory_core` is allowed to import `llm_provider` or talk
    to Ollama / Anthropic / OpenAI synchronously. Anything that needs an
    LLM lives in `src/ai_layer/` and is invoked through the async
    enrichment worker.

Phase 3 lands the full set of facade modules (storage, embeddings,
vector_store, classifier, chunker, dedup, cache, graph_links, telemetry,
health) on top of the existing `embedding_spaces` resolver. Submodules
are imported on demand — the package itself is import-cheap.

Keep the no-LLM-in-hot-path rule visible in reviews: this package must
remain import-cheap and network-free.
"""

from . import embedding_spaces  # noqa: F401  (re-export entry point)

__all__ = [
    "embedding_spaces",
    "storage",
    "embeddings",
    "vector_store",
    "classifier",
    "chunker",
    "dedup",
    "cache",
    "graph_links",
    "telemetry",
    "health",
]

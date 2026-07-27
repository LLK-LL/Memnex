"""
Advanced RAG: HyDE + Pluggable Reranker + MMR Diversity.

- HyDE: generates hypothetical answer, embeds it for semantic search.
- Reranker (v9 D4): pluggable backend selected via V9_RERANKER_BACKEND.
    * ce-marco   (default, legacy) cross-encoder/ms-marco-MiniLM-L-6-v2 via
                 sentence-transformers.CrossEncoder. Web-search trained —
                 known to regress on LoCoMo conversational data (-1.2pp).
    * bge-v2-m3  BAAI/bge-reranker-v2-m3 via FlagEmbedding.FlagReranker.
                 Multilingual, conversation-friendly. Recommended for v9.
    * bge-large  BAAI/bge-reranker-large via FlagReranker. English-only,
                 higher accuracy on long context, slower.
    * off        skip reranking entirely.
  All backends return scores normalized to [0,1] via sigmoid; downstream
  blending logic is identical (CE-boost-only: never demote originals).
  Falls back to Ollama LLM reranker if the configured backend fails to load.
- MMR: Maximal Marginal Relevance for result diversity (λ=0.7).
"""

import json
import os
import sys
import urllib.request
from typing import Optional

import numpy as np

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
# Use smaller model for speed — 7b is ~3x faster than 32b for reranking
RERANKER_MODEL = os.environ.get("RERANKER_MODEL", "qwen2.5-coder:7b")
HYDE_MODEL = os.environ.get("HYDE_MODEL", "qwen2.5-coder:7b")
OLLAMA_EMBED_MODEL = os.environ.get("OLLAMA_EMBED_MODEL", "nomic-embed-text")

LOG = lambda msg: sys.stderr.write(f"[reranker] {msg}\n")


def _ollama_generate(prompt: str, model: str, max_tokens: int = 200, temperature: float = 0.3) -> Optional[str]:
    """Call Ollama generate API."""
    try:
        payload = json.dumps({
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
            }
        }).encode()
        req = urllib.request.Request(
            f"{OLLAMA_URL}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            return data.get("response", "").strip()
    except Exception as e:
        LOG(f"generate error ({model}): {e}")
        return None


def _ollama_embed(text: str, model: str = None) -> Optional[list]:
    """Get embedding via Ollama. Retained for backward compat; new code
    should use _provider_embed() which dispatches to the configured
    EmbeddingProvider (fastembed|openai|cohere)."""
    model = model or OLLAMA_EMBED_MODEL
    try:
        payload = json.dumps({"model": model, "prompt": text}).encode()
        req = urllib.request.Request(
            f"{OLLAMA_URL}/api/embeddings",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return data.get("embedding")
    except Exception as e:
        LOG(f"embed error: {e}")
        return None


# Module-level cache for the configured provider. Rebuilt on first call;
# tests that mutate MEMORY_EMBED_PROVIDER between invocations should call
# _reset_embed_provider() (e.g. via monkeypatch with raising=False).
_embed_provider_cache = None


def _reset_embed_provider() -> None:
    """Clear the cached embed provider — used by tests after env changes."""
    global _embed_provider_cache
    _embed_provider_cache = None


def _provider_embed(text: str) -> Optional[list]:
    """Embed a single text via the configured EmbeddingProvider.

    Falls back to the legacy Ollama path only if the provider init or
    call fails — this way the default MEMORY_EMBED_PROVIDER=fastembed
    keeps working locally while OpenAI/Cohere routes go through HTTP.
    """
    global _embed_provider_cache
    try:
        if _embed_provider_cache is None:
            import config as _cfg
            from embed_provider import make_embed_provider
            _embed_provider_cache = make_embed_provider(_cfg.get_embed_provider())
        vecs = _embed_provider_cache.embed([text])
        if vecs:
            return list(vecs[0])
    except Exception as e:  # noqa: BLE001
        LOG(f"provider embed error: {e}")
    # Last-ditch fallback — keeps HyDE working when no provider reachable.
    return _ollama_embed(text)


# =============================================================================
# HyDE — Hypothetical Document Embeddings
# =============================================================================

def hyde_expand(query: str, project: str = None) -> Optional[list]:
    """
    Generate a hypothetical answer to the query, then embed it.
    Returns the embedding of the hypothetical answer (not the answer itself).

    Why: "auth JWT" as query might not match "Используем Bearer токен с RS256 подписью".
         But a hypothetical answer about auth WILL be semantically close to that record.

    Returns None if no LLM is configured — caller falls back to plain semantic search.
    """
    try:
        from config import has_llm
        if not has_llm():
            return None
    except Exception:
        pass

    context = f" in project {project}" if project else ""
    prompt = f"""You are a developer knowledge base. Write a short factual answer (2-3 sentences) to this query{context}.
If you don't know, write a plausible answer based on common patterns.

Query: {query}

Answer:"""

    hypothetical = _ollama_generate(prompt, HYDE_MODEL, max_tokens=150, temperature=0.5)
    if not hypothetical:
        return None

    # Embed the hypothetical answer (not the original query)
    embedding = _provider_embed(hypothetical)
    return embedding


# =============================================================================
# Reranker — pluggable backend (CE / BGE-v2-m3 / BGE-large) with LLM fallback
# =============================================================================

# Default kept on the legacy ce-marco for backward compatibility with v8 callers
# that import this constant directly. Active backend is resolved per-call from
# config.get_v9_reranker_backend() so tests can flip env vars.
CROSS_ENCODER_MODEL = os.environ.get("CROSS_ENCODER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")

_BACKEND_TO_MODEL = {
    "ce-marco": "cross-encoder/ms-marco-MiniLM-L-6-v2",
    "bge-v2-m3": "BAAI/bge-reranker-v2-m3",
    "bge-large": "BAAI/bge-reranker-large",
    # v12.7 — ONNX cross-encoder via fastembed (no torch / sentence-transformers
    # import). bge-reranker-base is zh+en; ~250ms per 20 pairs on CPU.
    "fastembed-ce": "BAAI/bge-reranker-base",
}

# {backend_key: (model_obj_or_False, kind)}; kind ∈ {"ce", "flag"}
_reranker_cache: dict = {}


def _resolve_reranker_backend() -> str:
    """Read V9_RERANKER_BACKEND each call so tests can monkeypatch env."""
    try:
        import config as _cfg  # local import: avoids hard dep at module load
        return _cfg.get_v9_reranker_backend()
    except Exception:
        return "ce-marco"


def _resolve_reranker_model(backend: str) -> str:
    """Honor V9_RERANKER_MODEL override; else fall back to backend table."""
    try:
        import config as _cfg
        override = _cfg.get_v9_reranker_model_override()
        if override:
            return override
    except Exception:
        pass
    return _BACKEND_TO_MODEL.get(backend, CROSS_ENCODER_MODEL)


def _reset_reranker_cache() -> None:
    """Clear loaded reranker models — used by tests after env changes."""
    global _reranker_cache
    _reranker_cache = {}


def _load_ce_reranker(model_name: str):
    """sentence-transformers CrossEncoder — works for ms-marco-* family."""
    try:
        from sentence_transformers import CrossEncoder
        ce = CrossEncoder(model_name)
        LOG(f"CrossEncoder loaded: {model_name}")
        return ce
    except Exception as e:  # noqa: BLE001
        LOG(f"CrossEncoder load failed ({model_name}): {e}")
        return None


def _load_flag_reranker(model_name: str):
    """Load a BAAI/bge-reranker-* model.

    Strategy: prefer sentence-transformers CrossEncoder first — it works
    with bge-reranker-v2-m3 and bge-reranker-large under any modern
    transformers version. FlagEmbedding's custom tokenizer wrapper is
    fragile across transformers releases (e.g. transformers>=4.40 removes
    XLMRobertaTokenizer.prepare_for_model that FlagEmbedding 1.2.x relies on).

    Fall back to FlagReranker only if CrossEncoder cannot load the model
    (rare — usually means HF download failed).
    """
    ce = _load_ce_reranker(model_name)
    if ce is not None:
        LOG(f"Reranker loaded via CrossEncoder API: {model_name}")
        return ce

    use_fp16 = True
    try:
        import config as _cfg
        use_fp16 = _cfg.get_v9_reranker_use_fp16()
    except Exception:
        pass

    try:
        from FlagEmbedding import FlagReranker  # type: ignore[import-not-found]
        rr = FlagReranker(model_name, use_fp16=use_fp16)
        LOG(f"FlagReranker loaded: {model_name} (fp16={use_fp16})")
        return rr
    except Exception as e:  # noqa: BLE001
        LOG(f"FlagReranker load failed ({model_name}): {e}")
        return None


# =============================================================================
# v11 D4 — BGE-v2-m3 named-function entrypoints
# =============================================================================
# These named helpers are part of the public API contract for v11 LoCoMo D4.
# The dispatch layer (`rerank_results` → `_get_reranker`) already routes via
# `V9_RERANKER_BACKEND`; the helpers below give explicit, test-friendly
# handles for the multilingual BGE-v2-m3 path so callers (notebooks, ad-hoc
# scripts, benchmark code) can pin to it without touching env vars.

_bge_v2_m3_singleton = None


def _get_bge_v2_m3():
    """Lazy singleton for BAAI/bge-reranker-v2-m3.

    Tries sentence-transformers CrossEncoder first (works with any modern
    transformers release), then FlagEmbedding.FlagReranker. fp16 honored
    via V9_RERANKER_FP16 (default on — ~2x speed on Apple Silicon/CUDA).

    Returns the loaded model object, or None if neither backend is
    importable. Cached for the process lifetime.
    """
    global _bge_v2_m3_singleton
    if _bge_v2_m3_singleton is not None:
        # `False` sentinel marks a previous failed load — don't retry.
        return _bge_v2_m3_singleton if _bge_v2_m3_singleton is not False else None
    obj = _load_flag_reranker("BAAI/bge-reranker-v2-m3")
    _bge_v2_m3_singleton = obj if obj is not None else False
    return obj


def _reset_bge_v2_m3_singleton() -> None:
    """Test helper — drop cached singleton so monkeypatched loaders re-run."""
    global _bge_v2_m3_singleton
    _bge_v2_m3_singleton = None


def _bge_rerank_scores(query: str, passages: list[str]) -> list[float]:
    """Score (query, passage) pairs with BGE-v2-m3, normalised to [0,1].

    Used by tests and external callers that want raw scores without going
    through the full `rerank_results` dispatch / boost-blend pipeline.

    Returns a list of floats with len == len(passages). If the model fails
    to load, returns an all-zeros list of the right length so callers can
    treat the reranker as a no-op without branching on None.
    """
    if not passages:
        return []
    model = _get_bge_v2_m3()
    if model is None:
        return [0.0] * len(passages)

    pairs = [[query, p] for p in passages]
    try:
        if hasattr(model, "compute_score"):
            # FlagReranker path — `normalize=True` applies sigmoid → [0,1].
            scores = model.compute_score(pairs, normalize=True)
        else:
            # CrossEncoder path — predict returns logits, sigmoid manually.
            raw = model.predict(pairs)
            scores = (1.0 / (1.0 + np.exp(-np.array(raw, dtype=np.float32)))).tolist()
    except Exception as e:  # noqa: BLE001
        LOG(f"BGE-v2-m3 scoring failed: {e}")
        return [0.0] * len(passages)

    if isinstance(scores, (int, float)):
        scores = [float(scores)]
    return [float(s) for s in scores]


def _load_fastembed_reranker(model_name: str):
    """ONNX cross-encoder via fastembed — importable even where torch is broken."""
    try:
        from fastembed.rerank.cross_encoder import TextCrossEncoder
        # Honour the same cache-dir override Store.fastembed uses so the
        # server finds models wherever its embedding models already live.
        cache_dir = os.environ.get("FASTEMBED_CACHE_DIR")
        kwargs = {"cache_dir": cache_dir} if cache_dir else {}
        ce = TextCrossEncoder(model_name, **kwargs)
        LOG(f"fastembed TextCrossEncoder loaded: {model_name}")
        return ce
    except Exception as e:  # noqa: BLE001
        LOG(f"fastembed TextCrossEncoder load failed ({model_name}): {e}")
        return None


def _get_reranker(backend: str | None = None):
    """Lazy-load the configured reranker. Returns (model, kind) or (None, None)."""
    backend = backend or _resolve_reranker_backend()
    if backend == "off":
        return None, None
    cached = _reranker_cache.get(backend)
    if cached is not None:
        return cached if cached[0] is not False else (None, None)

    model_name = _resolve_reranker_model(backend)
    if backend == "fastembed-ce":
        obj = _load_fastembed_reranker(model_name)
        kind = "fastembed"
    elif backend == "ce-marco":
        obj = _load_ce_reranker(model_name)
        kind = "ce"
    else:  # bge-v2-m3, bge-large
        obj = _load_flag_reranker(model_name)
        # FlagReranker exposes .compute_score; CrossEncoder exposes .predict —
        # we sniff at score-time, so kind tracks the *requested* backend for
        # logging only.
        kind = "flag" if obj is not None and hasattr(obj, "compute_score") else "ce"

    _reranker_cache[backend] = (obj if obj is not None else False, kind)
    return (obj, kind) if obj is not None else (None, None)


def _get_cross_encoder():
    """Backward-compat shim — returns the legacy ce-marco CrossEncoder."""
    obj, _ = _get_reranker("ce-marco")
    return obj


def rerank_results(query: str, results: list, top_k: int = 10) -> list:
    """
    Rerank search results using the configured backend (V9_RERANKER_BACKEND).

    Backends:
      ce-marco   ms-marco-MiniLM-L-6-v2  ~5ms /20 pairs, MS-MARCO web search.
      bge-v2-m3  BAAI/bge-reranker-v2-m3 multilingual, conversation-friendly.
      bge-large  BAAI/bge-reranker-large higher acc, English-only, slower.
      off        no-op, returns top_k as-is.
    LLM fallback (Ollama) used only if the configured backend fails to load.
    """
    if not results:
        return results

    backend = _resolve_reranker_backend()
    if backend == "off":
        return results[:top_k]

    model, kind = _get_reranker(backend)
    if model is not None:
        # v12.7 — CE latency on CPU scales linearly with pair count (~50-110ms
        # per pair for real-length records), and rag-mode over-fetch can push
        # top_k*2 to 40+. Cap scored pairs; the unscored tail keeps its
        # original (already gate-filtered) order below the scored head.
        try:
            max_pairs = int(os.environ.get("MEMORY_CE_MAX_PAIRS", "8"))
        except (TypeError, ValueError):
            max_pairs = 8
        max_pairs = max(2, max_pairs)
        head = results[:min(len(results), min(top_k * 2, max_pairs))]
        tail = [item for item in results if id(item) not in {id(h) for h in head}]
        # The model path may legitimately return FEWER than len(head) items
        # (CE cutoff). Do NOT backfill the removed ones from the unscored
        # tail-of-head: that would resurrect exactly the noise the cutoff
        # removed. The never-scored tail is appended after the scored head.
        ranked_head = _rerank_with_model(model, kind, query, head, top_k)
        return (ranked_head + tail)[:top_k]

    candidates = results[:min(len(results), top_k * 2)]

    ranked = _rerank_llm(query, candidates, top_k)  # noqa: F841 — legacy path
    # Combine reranked + remaining (legacy LLM-fallback behaviour).
    reranked_ids = {id(item) for item in ranked}
    remaining = [item for item in results if id(item) not in reranked_ids]
    return ranked[:top_k] + remaining[:max(0, top_k - len(ranked))]


def _rerank_with_model(model, kind: str, query: str, candidates: list, top_k: int) -> list:
    """Score candidates with the loaded model; true demote-capable blend.

    v12.7 — the old behaviour was boost-only (`max(orig, blend)`): the
    reranker could promote results but never demote them, so it was unable
    to push noise below relevant hits. Now the blended score replaces the
    original outright (weight via MEMORY_CE_BLEND_WEIGHT, default 0.5).

    Optional hard cutoff: candidates with sigmoid(CE) < MEMORY_CE_CUTOFF are
    dropped entirely. Default 0.0 (off) — measured on this stack,
    bge-reranker-base reliably scores irrelevant pairs ~0.0 but can also
    score RELEVANT cross-lingual pairs (zh query → en doc) near 0.0, so a
    global cutoff is only safe on monolingual corpora. Opt in deliberately.
    """
    pairs = []
    for item in candidates:
        content = item["r"].get("content", "")[:200]
        project = item["r"].get("project", "")
        tags = item["r"].get("tags", "")
        doc = f"[{project}] {content}"
        if tags:
            doc += f" tags:{tags}"
        pairs.append([query, doc])

    raw_scores = _score_pairs(model, kind, pairs)
    if raw_scores is None:
        return candidates[:top_k]

    # All paths return logits/raw; sigmoid → [0,1] for stable blending.
    scores_norm = 1.0 / (1.0 + np.exp(-np.array(raw_scores, dtype=np.float32)))

    try:
        ce_weight = float(os.environ.get("MEMORY_CE_BLEND_WEIGHT", "0.5"))
    except (TypeError, ValueError):
        ce_weight = 0.5
    ce_weight = min(1.0, max(0.0, ce_weight))
    try:
        ce_cutoff = float(os.environ.get("MEMORY_CE_CUTOFF", "0.0"))
    except (TypeError, ValueError):
        ce_cutoff = 0.0

    # Blend in normalized space, then write the blended ordering back to
    # BOTH score fields at their own scales. Downstream consumers differ:
    # detail-formatting sorts by the additive "score", while rag_response
    # (the default memory_recall mode) re-sorts by "rrf_score" — updating
    # only "score" would silently discard the CE ordering there.
    max_orig = max(item["score"] for item in candidates) or 1.0
    rrf_values = [item.get("rrf_score", 0.0) for item in candidates]
    max_rrf = max(rrf_values) or 1.0
    kept = []
    for i, item in enumerate(candidates):
        if i < len(scores_norm):
            ce_score = float(scores_norm[i])
            if "rrf_score" in item:
                orig_norm = item["rrf_score"] / max_rrf
            else:
                orig_norm = item["score"] / max_orig
            blended = ce_score * ce_weight + orig_norm * (1.0 - ce_weight)
            item["score"] = blended * max_orig  # restore additive scale
            if "rrf_score" in item:
                item["rrf_score"] = blended * max_rrf  # restore RRF scale
            item["reranked"] = True
            item["ce_score"] = round(ce_score, 4)
            if ce_cutoff > 0.0 and ce_score < ce_cutoff:
                continue
        kept.append(item)

    kept.sort(key=lambda x: x.get("rrf_score", x["score"]), reverse=True)
    return kept


def _score_pairs(model, kind: str, pairs: list[list[str]]):
    """Backend-specific scoring. Returns list[float] of raw scores or None."""
    try:
        if kind == "fastembed":
            # fastembed TextCrossEncoder scores one query against N docs.
            # All pairs share the same query in our pipeline.
            if not pairs:
                return []
            q = pairs[0][0]
            docs = [p[1] for p in pairs]
            return [float(s) for s in model.rerank(q, docs)]
        if kind == "flag" and hasattr(model, "compute_score"):
            # FlagReranker accepts list[[q,p]]; returns list[float] of logits.
            scores = model.compute_score(pairs)
            if isinstance(scores, (int, float)):
                return [float(scores)]
            return [float(s) for s in scores]
        # sentence-transformers CrossEncoder.predict
        return model.predict(pairs)
    except Exception as e:  # noqa: BLE001
        LOG(f"reranker scoring failed ({kind}): {e}")
        return None


def _rerank_cross_encoder(ce, query: str, candidates: list, top_k: int) -> list:
    """Legacy entrypoint kept for tests that imported it by name."""
    return _rerank_with_model(ce, "ce", query, candidates, top_k)


def _rerank_llm(query: str, candidates: list, top_k: int) -> list:
    """Fallback: rerank using Ollama LLM as cross-encoder."""
    entries = []
    for i, item in enumerate(candidates):
        content = item["r"].get("content", "")[:200]
        project = item["r"].get("project", "")
        rtype = item["r"].get("type", "")
        entries.append(f"{i}. [{rtype}|{project}] {content}")

    prompt = (
        "Rate how relevant each knowledge entry is to the query. Score 0-10.\n"
        "0 = completely irrelevant, 10 = perfect match.\n"
        "Return ONLY a JSON array of scores, e.g. [8, 3, 7, 1, 9]\n\n"
        f"Query: {query}\n\n"
        f"Entries:\n{chr(10).join(entries)}\n\n"
        "Scores (JSON array):"
    )

    response = _ollama_generate(prompt, RERANKER_MODEL, max_tokens=100, temperature=0.1)
    if not response:
        return candidates[:top_k]

    scores = _parse_scores(response, len(candidates))
    if not scores:
        return candidates[:top_k]

    max_orig = max(item["score"] for item in candidates) or 1.0
    for i, item in enumerate(candidates):
        if i < len(scores):
            rerank_score = scores[i] / 10.0
            orig_norm = item["score"] / max_orig
            item["score"] = rerank_score * 0.6 + orig_norm * 0.4
            item["reranked"] = True

    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates


def _parse_scores(response: str, expected_count: int) -> Optional[list]:
    """Parse JSON array of scores from LLM response."""
    response = response.strip()

    for attempt in [response, f"[{response}]"]:
        try:
            scores = json.loads(attempt)
            if isinstance(scores, list):
                result = []
                for s in scores[:expected_count]:
                    try:
                        val = float(s)
                        result.append(max(0, min(10, val)))
                    except (TypeError, ValueError):
                        result.append(5.0)
                return result
        except json.JSONDecodeError:
            continue

    import re
    numbers = re.findall(r'\b(\d+(?:\.\d+)?)\b', response)
    if numbers:
        return [max(0, min(10, float(n))) for n in numbers[:expected_count]]

    LOG(f"Failed to parse reranker scores: {response[:100]}")
    return None


# =============================================================================
# MMR — Maximal Marginal Relevance (diversity in search results)
# =============================================================================

def mmr_diversify(results: list, embeddings: list, lambda_param: float = 0.7,
                  top_k: int = 10, redundancy_threshold: float = 0.85) -> list:
    """
    Adaptive MMR: only activates when top results are truly redundant.

    Checks avg pairwise similarity of top-k results first.
    If below threshold — returns as-is (no diversity penalty).
    If above — applies MMR with high λ (0.9) to gently remove near-duplicates.

    Args:
        results: list of dicts with "r" (record) and "score" (relevance score)
        embeddings: list of numpy arrays, same length as results
        lambda_param: base λ (overridden to 0.9 when redundancy detected)
        top_k: number of results to return
        redundancy_threshold: avg pairwise sim above which MMR activates

    Returns:
        reordered list (only reordered if redundancy detected)
    """
    if len(results) <= 2 or not embeddings:
        return results[:top_k]

    n = len(results)
    if len(embeddings) != n:
        LOG(f"MMR: embeddings count ({len(embeddings)}) != results count ({n}), skipping")
        return results[:top_k]

    # Normalize embeddings
    emb_matrix = np.array(embeddings, dtype=np.float32)
    norms = np.linalg.norm(emb_matrix, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1, norms)
    emb_matrix = emb_matrix / norms

    # Pairwise similarity
    sim_matrix = emb_matrix @ emb_matrix.T

    # Check if top results are actually redundant
    check_n = min(top_k, n)
    if check_n > 1:
        top_sims = []
        for i in range(check_n):
            for j in range(i + 1, check_n):
                top_sims.append(float(sim_matrix[i][j]))
        avg_sim = sum(top_sims) / len(top_sims) if top_sims else 0

        if avg_sim < redundancy_threshold:
            # Results are diverse enough — don't apply MMR
            return results[:top_k]

        LOG(f"MMR activated: avg_sim={avg_sim:.3f} > {redundancy_threshold} (top-{check_n} redundant)")

    # Apply MMR with high λ (gentle: mostly relevance, slight diversity push)
    effective_lambda = 0.9

    scores = np.array([item["score"] for item in results], dtype=np.float32)
    max_score = scores.max()
    if max_score > 0:
        scores = scores / max_score

    selected = []
    remaining = list(range(n))

    for _ in range(min(top_k, n)):
        if not remaining:
            break

        if not selected:
            best_idx = remaining[int(np.argmax(scores[remaining]))]
        else:
            best_score = -float("inf")
            best_idx = remaining[0]
            for idx in remaining:
                relevance = scores[idx]
                max_sim = max(sim_matrix[idx][s] for s in selected)
                mmr_score = effective_lambda * relevance - (1 - effective_lambda) * max_sim
                if mmr_score > best_score:
                    best_score = mmr_score
                    best_idx = idx

        selected.append(best_idx)
        remaining.remove(best_idx)

    return [results[i] for i in selected]


# =============================================================================
# Query Analyzer — classify query to choose strategy
# =============================================================================

def analyze_query(query: str) -> dict:
    """
    Classify query type to optimize search strategy.
    Fast heuristic-based (no LLM call).

    Returns:
        {
            "type": "factual"|"solution"|"debug"|"architecture"|"search",
            "expand": True/False (should use HyDE),
            "deep_graph": True/False (should do multi-hop)
        }
    """
    ql = query.lower()

    # Debug/error patterns
    if any(w in ql for w in ["error", "ошибка", "bug", "fix", "broken", "fail", "не работает", "crash"]):
        return {"type": "debug", "expand": True, "deep_graph": False}

    # Factual lookup (check BEFORE solution — "какой стек" is factual, not "как")
    if any(w in ql for w in ["что", "what", "where", "где", "какой", "какая", "какое", "стек",
                              "порт", "url", "пароль", "домен", "версия", "кто", "сколько"]):
        return {"type": "factual", "expand": False, "deep_graph": False}

    # Architecture patterns
    if any(w in ql for w in ["architect", "архитектур", "структур", "pattern", "design", "подход", "выбор", "сравн"]):
        return {"type": "architecture", "expand": True, "deep_graph": True}

    # Solution/how-to patterns
    if any(w in ql for w in ["как", "how", "implement", "реализ", "сделать", "настро", "создать"]):
        return {"type": "solution", "expand": True, "deep_graph": False}

    # Default: try HyDE for better recall
    return {"type": "search", "expand": len(query.split()) >= 3, "deep_graph": False}


# =============================================================================
# Multi-hop graph traversal
# =============================================================================

def multi_hop_expand(store, seed_ids: list, results: dict, depth: int = 2) -> dict:
    """
    Expand graph relations to depth N (default 2 hops).
    Current system does 1 hop — this does 2+ for architecture queries.

    A → B → C: if A is relevant, B is likely relevant, C might be.
    Score decays: hop1 = parent * 0.4, hop2 = parent * 0.2
    """
    visited = set(results.keys())
    current_layer = seed_ids

    for hop in range(depth):
        next_layer = []
        decay = 0.4 / (hop + 1)  # 0.4, 0.2, 0.13...

        for kid in current_layer:
            if kid not in results:
                continue
            parent_score = results[kid]["score"]

            for r in store.q("""
                SELECT k.* FROM relations rel
                JOIN knowledge k ON k.id = CASE WHEN rel.from_id=? THEN rel.to_id ELSE rel.from_id END
                WHERE (rel.from_id=? OR rel.to_id=?) AND k.status='active'
            """, (kid, kid, kid)):
                rid = r["id"]
                if rid not in visited:
                    visited.add(rid)
                    results[rid] = {"r": r, "score": parent_score * decay, "via": ["graph"]}
                    next_layer.append(rid)

        current_layer = next_layer
        if not current_layer:
            break

    return results

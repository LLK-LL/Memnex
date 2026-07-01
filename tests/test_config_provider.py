"""Tests for new provider-config helpers in src/config.py."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# ──────────────────────────────────────────────
# get_llm_provider
# ──────────────────────────────────────────────


def test_get_llm_provider_default_ollama(monkeypatch):
    import config

    for var in ("MEMORY_LLM_PROVIDER", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    assert config.get_llm_provider() == "ollama"


def test_get_llm_provider_env_override(monkeypatch):
    import config

    monkeypatch.setenv("MEMORY_LLM_PROVIDER", "OpenAI")
    assert config.get_llm_provider() == "openai"

    monkeypatch.setenv("MEMORY_LLM_PROVIDER", "anthropic")
    assert config.get_llm_provider() == "anthropic"


def test_get_llm_provider_invalid_falls_back(monkeypatch):
    import config

    monkeypatch.setenv("MEMORY_LLM_PROVIDER", "some-garbage")
    assert config.get_llm_provider() == "ollama"


# ──────────────────────────────────────────────
# API key resolution
# ──────────────────────────────────────────────


def test_get_llm_api_key_falls_back_to_provider_specific(monkeypatch):
    import config

    monkeypatch.setenv("MEMORY_LLM_PROVIDER", "openai")
    monkeypatch.delenv("MEMORY_LLM_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai-1")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    assert config.get_llm_api_key() == "sk-openai-1"

    # Anthropic branch
    monkeypatch.setenv("MEMORY_LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-1")
    assert config.get_llm_api_key() == "sk-ant-1"


def test_get_llm_api_key_universal_override_wins(monkeypatch):
    import config

    monkeypatch.setenv("MEMORY_LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-normal")
    monkeypatch.setenv("MEMORY_LLM_API_KEY", "sk-override")

    assert config.get_llm_api_key() == "sk-override"


def test_get_llm_api_key_none_for_ollama(monkeypatch):
    import config

    monkeypatch.setenv("MEMORY_LLM_PROVIDER", "ollama")
    monkeypatch.delenv("MEMORY_LLM_API_KEY", raising=False)
    assert config.get_llm_api_key() is None


# ──────────────────────────────────────────────
# API base
# ──────────────────────────────────────────────


def test_get_llm_api_base_defaults_per_provider(monkeypatch):
    import config

    monkeypatch.delenv("MEMORY_LLM_API_BASE", raising=False)
    assert config.get_llm_api_base("openai") == "https://api.openai.com/v1"
    assert config.get_llm_api_base("anthropic") == "https://api.anthropic.com/v1"


def test_get_llm_api_base_honours_openrouter_override(monkeypatch):
    import config

    monkeypatch.setenv("MEMORY_LLM_API_BASE", "https://openrouter.ai/api/v1")
    assert config.get_llm_api_base("openai") == "https://openrouter.ai/api/v1"


def test_get_llm_api_base_strips_trailing_slash(monkeypatch):
    import config

    monkeypatch.setenv("MEMORY_LLM_API_BASE", "https://example.com/v1/")
    assert config.get_llm_api_base() == "https://example.com/v1"


# ──────────────────────────────────────────────
# Model resolution per provider
# ──────────────────────────────────────────────


def test_get_llm_model_for_provider_defaults(monkeypatch):
    import config

    monkeypatch.delenv("MEMORY_LLM_MODEL", raising=False)
    assert config.get_llm_model_for_provider("openai") == "gpt-4o-mini"
    assert config.get_llm_model_for_provider("anthropic") == "claude-haiku-4-5"
    assert config.get_llm_model_for_provider("ollama") == "qwen2.5-coder:7b"


def test_get_llm_model_for_provider_env_override(monkeypatch):
    import config

    monkeypatch.setenv("MEMORY_LLM_MODEL", "custom-model")
    assert config.get_llm_model_for_provider("openai") == "custom-model"
    assert config.get_llm_model_for_provider("anthropic") == "custom-model"


# ──────────────────────────────────────────────
# Per-phase overrides
# ──────────────────────────────────────────────


def test_phase_provider_override(monkeypatch):
    """MEMORY_TRIPLE_PROVIDER=openai → triple uses openai, others stay default."""
    import config

    for var in (
        "MEMORY_LLM_PROVIDER",
        "MEMORY_TRIPLE_PROVIDER",
        "MEMORY_ENRICH_PROVIDER",
        "MEMORY_REPR_PROVIDER",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
    ):
        monkeypatch.delenv(var, raising=False)

    monkeypatch.setenv("MEMORY_TRIPLE_PROVIDER", "openai")

    assert config.get_phase_provider("triple") == "openai"
    assert config.get_phase_provider("enrich") == "ollama"
    assert config.get_phase_provider("repr") == "ollama"


def test_phase_provider_falls_back_to_global(monkeypatch):
    import config

    monkeypatch.setenv("MEMORY_LLM_PROVIDER", "anthropic")
    for var in (
        "MEMORY_TRIPLE_PROVIDER",
        "MEMORY_ENRICH_PROVIDER",
        "MEMORY_REPR_PROVIDER",
    ):
        monkeypatch.delenv(var, raising=False)

    assert config.get_phase_provider("triple") == "anthropic"
    assert config.get_phase_provider("enrich") == "anthropic"


def test_phase_provider_invalid_phase():
    import config

    with pytest.raises(ValueError):
        config.get_phase_provider("unknown_phase")


def test_phase_model_override(monkeypatch):
    import config

    monkeypatch.setenv("MEMORY_TRIPLE_PROVIDER", "openai")
    monkeypatch.setenv("MEMORY_TRIPLE_MODEL", "gpt-4o")
    monkeypatch.delenv("MEMORY_LLM_MODEL", raising=False)
    monkeypatch.delenv("MEMORY_ENRICH_MODEL", raising=False)
    monkeypatch.delenv("MEMORY_ENRICH_PROVIDER", raising=False)
    monkeypatch.delenv("MEMORY_LLM_PROVIDER", raising=False)

    assert config.get_phase_model("triple") == "gpt-4o"
    # Enrich still takes default model for the default (ollama) provider
    assert config.get_phase_model("enrich") == "qwen2.5-coder:7b"


# ──────────────────────────────────────────────
# Auto-resolve
# ──────────────────────────────────────────────


def test_auto_resolves_by_available_keys_openai(monkeypatch):
    import config

    monkeypatch.setenv("MEMORY_LLM_PROVIDER", "auto")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-1")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    assert config.get_llm_provider() == "openai"


def test_auto_resolves_by_available_keys_anthropic(monkeypatch):
    import config

    monkeypatch.setenv("MEMORY_LLM_PROVIDER", "auto")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant")

    assert config.get_llm_provider() == "anthropic"


def test_auto_falls_back_to_ollama_when_no_keys(monkeypatch):
    import config

    monkeypatch.setenv("MEMORY_LLM_PROVIDER", "auto")
    for var in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "COHERE_API_KEY"):
        monkeypatch.delenv(var, raising=False)

    assert config.get_llm_provider() == "ollama"


# ──────────────────────────────────────────────
# Embedding config
# ──────────────────────────────────────────────


def test_get_embed_provider_default_fastembed(monkeypatch):
    import config

    monkeypatch.delenv("MEMORY_EMBED_PROVIDER", raising=False)
    assert config.get_embed_provider() == "fastembed"


def test_get_embed_provider_env_override(monkeypatch):
    import config

    monkeypatch.setenv("MEMORY_EMBED_PROVIDER", "OpenAI")
    assert config.get_embed_provider() == "openai"

    monkeypatch.setenv("MEMORY_EMBED_PROVIDER", "cohere")
    assert config.get_embed_provider() == "cohere"


def test_get_embed_model_defaults(monkeypatch):
    import config

    monkeypatch.delenv("MEMORY_EMBED_MODEL", raising=False)
    assert config.get_embed_model("openai") == "text-embedding-3-small"
    assert config.get_embed_model("cohere") == "embed-multilingual-v3.0"


def test_get_fastembed_cache_dir(monkeypatch):
    import config

    monkeypatch.delenv("FASTEMBED_CACHE_DIR", raising=False)
    assert config.get_fastembed_cache_dir() is None

    monkeypatch.setenv("FASTEMBED_CACHE_DIR", r"D:\CodexCache\fastembed")
    assert config.get_fastembed_cache_dir() == r"D:\CodexCache\fastembed"


def test_get_embed_api_key_provider_specific(monkeypatch):
    import config

    monkeypatch.delenv("MEMORY_EMBED_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-oa")
    monkeypatch.setenv("COHERE_API_KEY", "co-k")

    assert config.get_embed_api_key("openai") == "sk-oa"
    assert config.get_embed_api_key("cohere") == "co-k"
    assert config.get_embed_api_key("fastembed") is None


def test_get_embed_api_base_default(monkeypatch):
    import config

    monkeypatch.delenv("MEMORY_EMBED_API_BASE", raising=False)
    assert config.get_embed_api_base("openai") == "https://api.openai.com/v1"
    assert config.get_embed_api_base("cohere") == "https://api.cohere.com/v2"

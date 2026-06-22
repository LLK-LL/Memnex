# Banana Slides Setup

Full documentation: https://docs.bananaslides.online/

## Install and Start Backend

```bash
git clone https://github.com/Anionex/banana-slides
cd banana-slides
cp .env.example .env
# Edit .env 鈥?at minimum set an AI provider key (see below)
cd backend
uv sync
uv run alembic upgrade head
uv run python app.py
```

Backend starts on http://localhost:5000.

## Required Configuration

Edit `.env` with at least one AI provider:

```env
# Google Gemini (default)
AI_PROVIDER_FORMAT=gemini
# REDACTED: sensitive-looking memory line

# OR OpenAI-compatible
AI_PROVIDER_FORMAT=openai
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
```

Supported providers: `gemini`, `openai`, `vertex`, `lazyllm`, `anthropic`.

## Verify

```bash
curl -sf http://localhost:5000/health
```

## Install banana-cli

```bash
# Option A: use directly from project root (no install needed)
uv run banana-cli --help

# Option B: install globally (then use banana-cli directly)
uv tool install .
banana-cli --help
```

If the backend runs on a non-default port, pass `--base-url` or set `BANANA_CLI_BASE_URL`.

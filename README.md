# Memnex

> Local-first memory for AI coding agents.
> Memnex gives Codex, Claude Code, Cursor, and any MCP client a durable memory
> layer that can recall decisions, fixes, rules, workflows, entities, and graph
> context without sending your private history to a hosted memory service.

[![Repository](https://img.shields.io/badge/repository-LLK--LL%2FMemnex-181717?logo=github)](https://github.com/LLK-LL/Memnex)
[![Version](https://img.shields.io/badge/version-12.7.1-8ad.svg)](https://pypi.org/project/total-agent-memory/)
[![License](https://img.shields.io/badge/license-MIT-fa4.svg)](LICENSE)
[![Local First](https://img.shields.io/badge/local--first-yes-4a9.svg)]()
[![MCP](https://img.shields.io/badge/protocol-MCP-blue.svg)](https://modelcontextprotocol.io)
[![PyPI](https://img.shields.io/badge/PyPI-total--agent--memory-3776AB.svg)](https://pypi.org/project/total-agent-memory/)
[![Docker GHCR](https://img.shields.io/badge/docker-ghcr.io-2496ED.svg)](https://github.com/LLK-LL/Memnex/pkgs/container/total-agent-memory)

Memnex was previously published under the package name `total-agent-memory`.
The package, CLI names, and legacy `claude_total_memory` compatibility shim are
kept so existing installs continue to work.

![Memnex Knowledge Galaxy workspace](docs/assets/memnex-v12.7-galaxy-workspace.png)

![Memnex Knowledge Galaxy observatory](docs/assets/memnex-v12.7-galaxy-observatory.png)

![Memnex Knowledge Galaxy flight view](docs/assets/memnex-v12.7-galaxy-flight.png)

## Why Memnex

AI coding agents are excellent inside one task and forgetful across many. They
lose the decisions you made, the bugs you fixed, the project-specific rules you
care about, and the workflows that were already proven once.

Memnex turns that scattered working history into a local memory engine:

- **Recall that respects project boundaries:** search, RAG, timeline, and graph
  modes can stay scoped to the current project or agent namespace.
- **Multi-representation retrieval:** raw text, summaries, keywords, questions,
  compressed forms, FTS, vectors, graph expansion, and reranking cooperate in
  one recall chain.
- **Temporal and procedural memory:** remember what changed, when it changed,
  what worked before, and which workflows usually solve similar tasks.
- **Local-first privacy:** SQLite, local vector storage, local logs, generated
  graph exports, and real memory databases stay on your machine.
- **3D Knowledge Galaxy:** inspect memory as a live 2D/3D graph workspace with
  galaxy, solar-system, planet, and satellite views.

## Install

Clone the repository and install the runtime dependencies:

```bash
git clone https://github.com/LLK-LL/Memnex.git
cd Memnex
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

Windows PowerShell:

```powershell
git clone https://github.com/LLK-LL/Memnex.git
cd Memnex
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
```

Register Memnex with an agent:

```bash
bash install.sh --ide codex
bash install.sh --ide claude-code
```

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Ide codex
```

Supported IDE and agent targets include Codex, Claude Code, Cursor, Cline,
Continue, Aider, Windsurf, Gemini CLI, and OpenCode.

## Quick Start

Start the MCP server:

```bash
tam
```

Look up memory from a terminal:

```bash
tam-lookup "why did we choose the current vector backend?"
lookup-memory "recent recall-chain fixes"
```

Export the Memory Galaxy viewer:

```bash
python src/tools/memory_graph_viewer_export.py --output ./graph-viewer-output
```

Open `graph-viewer-output/index.html` in a browser. The export reads the memory
database in read-only mode and writes a static local workspace.

## Core Tools

Memnex exposes MCP tools for the operations an agent needs during real work:

- `memory_save`, `memory_save_fast` - persist facts, decisions, lessons,
  solutions, and conventions.
- `memory_recall`, `memory_search_fast`, `memory_get` - retrieve concise or
  full memory context.
- `memory_explain_search`, `memory_perf_report` - inspect retrieval tiers,
  reranking, caches, and recent recall effectiveness.
- `rule_context_refresh`, `save_rule`, `list_rules` - keep durable behavior
  rules active without overloading every prompt.
- `session_init`, `session_end` - preserve continuity between coding sessions.
- `ingest_codebase`, `file_context`, `learn_error` - connect code, files, and
  recurring fixes to the memory graph.

## Architecture

```text
total_agent_memory/        package entrypoints
claude_total_memory/       legacy compatibility shim
src/                       memory engine, MCP server, recall, graph, AI layer
src/memory_core/           deterministic storage, embeddings, retrieval helpers
src/ai_layer/              optional LLM-bound enrichment and reasoning helpers
src/tools/                 maintenance tools and Memory Galaxy exporter
migrations/                SQLite schema migrations
skills/memory-protocol/    reusable agent memory protocol
hooks/                     optional capture and workflow hooks
memory-system/             local vault sync scripts and governance notes
docs/                      current user docs and release guides
```

The public repository is intentionally runtime-focused. Generated logs, private
memory data, graph exports, local work directories, and QA artifacts are ignored.

## Configuration

Common environment variables:

```bash
TAM_MEMORY_DIR=~/.tam
TAM_AGENT_NAMESPACE=codex
MEMORY_MODE=fast
MEMORY_TEXT_EMBED_MODEL=jinaai/jina-embeddings-v2-base-zh
MEMORY_RERANK_ENABLED=true
```

See [.env.example](.env.example), [docs/installation.md](docs/installation.md),
and [docs/security-and-redaction.md](docs/security-and-redaction.md) for setup
and privacy notes.

## Knowledge Galaxy

The v12.7 viewer ships with package data, so installed wheels can serve the same
visual workspace as a source checkout. The current route renders graph-derived
galaxies, systems, planets, satellites, relationship lines, inspection panels,
and a flight mode for navigating large memory spaces.

More detail:

- [v12.7.0 release guide](docs/v12.7.0-recall-galaxy-release.md)

## Privacy

Memnex is designed for local agent memory. Do not publish real `memory.db`,
Chroma stores, raw transcripts, generated `graph-viewer-output/`, logs, or
private memory snapshots. The repository `.gitignore` excludes those paths by
default, but first-time public releases should still be reviewed manually.

## Contributing

Open an issue before large changes, keep runtime behavior narrowly scoped, and
update the relevant docs when user-facing tools change. See
[CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT - see [LICENSE](LICENSE).

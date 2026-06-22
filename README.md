# Memnex

**Language:** English | [简体中文](README.zh-CN.md)

**Repository:** [LLK-LL/Memnex](https://github.com/LLK-LL/Memnex)

Memnex is a local-first memory vault for personal AI agents. It helps Codex, Claude, Cursor, MCP tools, and local agents preserve the useful parts of your work across sessions: memories, rules, skills, preferences, workflows, exports, and snapshots.

> Your AI agent learns during a task, then forgets the useful parts when the next session starts.

Memnex turns that fragile local state into a reviewable, recoverable, portable, and self-iterating memory system.

![Memnex memory network overview](assets/memory-network-overview.png)

## What It Saves

Memnex is not another chat-history dump. It preserves the operational layer around your AI work:

| Asset | What it captures | Why it matters |
| --- | --- | --- |
| `memories/` | Facts, lessons, decisions, fixes, and reflections | The durable experience your agent should remember |
| `rules/` | Behavior rules and working constraints | How the agent should act next time |
| `skills/` | Reusable Codex skills and workflows | Repeatable task procedures |
| `agent-skills/` | Cross-agent skill layers and routers | Shared workflows across agent ecosystems |
| `preferences/` | Redacted preference and configuration snapshots | Stable working preferences without obvious secrets |
| `templates/` | Governance templates for memory, rule, and skill iteration | A repeatable way to improve the memory system |
| `manifest.json` | Sync provenance and safety metadata | What was collected, when, and how |

## Before and After

| Without Memnex | With Memnex |
| --- | --- |
| Each AI session starts from a blank working memory. | The next session can reuse relevant memories, rules, and skills. |
| Useful debugging lessons disappear into old chats. | Fixes and lessons become file-backed memory assets. |
| Prompt rules are scattered across clients and projects. | Rules are versioned, inspectable, and portable. |
| Local memory databases become opaque over time. | Memory state can be reviewed, diffed, rolled back, and migrated. |
| Personal workflows are retrained repeatedly by hand. | Successful workflows can become reusable skills. |

## Why Memnex?

Most AI memory tools focus on one of several directions:

| Category | Examples | Best for | Typical gap for personal users |
| --- | --- | --- | --- |
| General memory APIs | Mem0 | Developers building AI apps | Powerful, but still product/API oriented |
| Stateful agent frameworks | Letta / MemGPT | Long-running custom agents | More like an agent framework than a personal memory vault |
| Enterprise memory graphs | Zep | Business agents and production context | Optimized for scale, compliance, and teams |
| Local MCP memory layers | OpenMemory and similar tools | Sharing memory across AI clients | Often focused on storing and retrieving memories only |
| Personal knowledge RAG | Obsidian AI, Khoj, local document assistants | Asking questions over notes and documents | Great for document search, less focused on agent behavior, rules, and skills |

Memnex takes a smaller and more personal route. It does not try to become another large AI platform. Instead, it preserves the training assets that already live on your machine so your assistant can become more aligned over time without a complex backend.

## How It Works

Memnex follows a simple loop:

```text
Collect -> Retrieve -> Self-iterate
```

### 1. Collect

During real work, AI produces reusable knowledge:

- preferred writing and coding style;
- project-specific conventions;
- debugging lessons;
- research workflows;
- reliable tool commands;
- mistakes that should not be repeated;
- skills that should trigger in specific situations.

Memnex collects these assets from local memory exports, file-backed memories, rules, skills, preferences, and templates into a consistent `memory-data/` structure.

### 2. Retrieve

Memnex is not meant to dump all history into every prompt. That wastes context and adds noise.

Instead, the agent should retrieve the relevant memory, rule, skill, or preference for the current task:

- research tasks can retrieve research workflows and citation habits;
- coding tasks can retrieve project conventions and past fixes;
- writing tasks can retrieve tone, structure, and style preferences;
- automation tasks can retrieve tested commands and recovery paths.

### 3. Self-iterate

After each task, new experience can be folded back into the system:

- What worked?
- What failed?
- Which rule should be updated?
- Which workflow can become a reusable skill?
- Which memory is outdated?
- Which preference should be preserved?
- Which content should be redacted or removed?

Over time, this creates a personal operating layer for AI:

```text
task experience
  -> durable memory
  -> reusable rule
  -> triggerable skill
  -> better next task
  -> new experience
```

Memnex does not retrain the base model. It trains the local memory, rules, and skills around the model.

## v0.2.0 - Memory graph visualization

Memnex now includes a local graph viewer exporter for memory systems that expose
SQLite graph tables. It exports a read-only snapshot into a static browser
workspace with 2D and 3D views, type filters, weighted edges, search, and linked
memory summaries.

```powershell
python .\memory-system\tools\graph-viewer\export_graph_viewer.py `
  --db "$env:USERPROFILE\.tam\memory.db" `
  --output .\graph-viewer-output
```

Open `graph-viewer-output\index.html` for the 2D view or
`graph-viewer-output\viewer-3d.html` for the 3D view.

The exporter reads the source database in SQLite read-only mode. Generated
viewer output can contain private memory summaries, so it is ignored by Git and
should be reviewed before sharing.

## Quick Start

Memnex currently ships with a PowerShell sync workflow for Windows.

Run a manual sync from the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\memory-system\scripts\sync-memory-library.ps1
```

Install the weekly local Windows task:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\memory-system\scripts\install-weekly-task.ps1
```

The sync script rebuilds `memory-data/current/`, copies approved memory-related sources, applies conservative redaction, writes `memory-data/manifest.json`, and commits/pushes changes when there is a diff.

## Example Workflow

```text
1. Finish a real AI-assisted task.
2. Keep the useful lesson, rule, command, or workflow in your local memory layer.
3. Run the Memnex sync script.
4. Review the generated memory-data/ snapshot.
5. Let future agents retrieve the relevant memory instead of relearning it.
```

See the examples:

- [Codex memory sync](examples/codex-memory-sync.md)
- [Claude adapter](examples/claude-adapter.md)
- [Cursor rules adapter](examples/cursor-rules.md)
- [MCP memory export](examples/mcp-memory-export.md)

## Supported Agent Platforms

Memnex is strongest today in the Codex + local MCP memory ecosystem, but its storage model is platform-neutral. Any agent that can read Markdown, rules, JSON exports, local files, or MCP tools can use Memnex as a personal memory source.

| Platform | Current support level | What Memnex provides |
| --- | --- | --- |
| Codex CLI / Codex Desktop / Codex App | Native | `AGENTS.md`, `.codex/memories`, `.codex/rules`, `.codex/skills`, `.codex/templates`, redacted `.codex/config.toml` snapshots |
| Codex in VS Code / Cursor / Windsurf | Native through Codex extension behavior | Same Codex memory, rules, and skills layer |
| `.agents` skill ecosystem | Native | `agent-skills/` layer for cross-agent skills and platform routers |
| MCP memory tools / Total Agent Memory style exports | Native export/archive support | Structured memory exports under `memory-data/.../exports` |
| Claude Code / Claude Desktop | Easy adapter | Long-term memories, rules, skills, and workflow notes translated into Claude instructions or MCP-backed memory |
| Cursor | Easy adapter | Project conventions, workflow rules, and reusable task guidance converted into Cursor Rules |
| Continue | Easy adapter | Rules, prompts, tools, and MCP-readable memory exports |
| Windsurf / Cascade | Easy adapter | Memories, rules, and optional MCP-backed retrieval |
| Cline / Roo-style coding agents | Easy adapter | Memory-bank style Markdown context, project decisions, active context, and rules |
| OpenAI Agents SDK | Developer integration | External memory source, retrieval tool, policy/rule source, skill registry |
| LangChain / LangGraph / LlamaIndex / AutoGen / CrewAI | Developer integration | File-backed long-term memory and workflow knowledge |
| Obsidian / Khoj / local knowledge-base tools | Knowledge-base integration | Human-readable long-term notes, templates, and workflow records |

## Repository Layout

```text
memory-system/
  README.md
  scripts/
    sync-memory-library.ps1        # collect, sanitize, commit, and push the latest state
    install-weekly-task.ps1        # install a local Windows weekly scheduled task
  tools/
    graph-viewer/                  # local 2D/3D memory graph viewer exporter

memory-data/
  current/
    exports/                       # structured memory exports and database snapshots
    memories/                      # file-backed long-term memories
    rules/                         # local behavior rules
    skills/                        # Codex skills
    agent-skills/                  # agent-level skills
    preferences/                   # redacted preference/config snapshots
    templates/                     # memory/rule/skill governance templates
  snapshots/                       # historical sync snapshots
  manifest.json                    # sync metadata and safety records
```

## Privacy and Safety

Memnex is intentionally conservative. Current public releases exclude
`memory-data/` from Git so system files can be published without bundling live
memory content. Sync outputs, graph viewer exports, obvious caches, logs,
temporary files, and transient database files are ignored. Preference and
configuration snapshots are redacted for sensitive-looking keywords such as:

- `token`
- `password`
- `secret`
- `api_key`
- `credential`
- `cookie`
- `session`

You should still review the first sync before making a repository public. For details, see [Security and redaction](docs/security-and-redaction.md).

## Roadmap

- Add macOS/Linux sync scripts.
- Add a demo GIF for the end-to-end memory sync loop.
- Add a lightweight retrieval helper for selected memories/rules/skills.
- Add tests for the graph viewer exporter and redaction workflow.
- Add more adapter examples for Claude, Cursor, Continue, Windsurf, Cline, and MCP servers.
- Add cross-platform redaction and sync path checks.

## Contributing

Memnex is early and deliberately small. Good contributions are adapter examples, redaction improvements, cross-platform sync support, and clear documentation for real agent workflows.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the current contribution guide.

## One-Sentence Summary

**Memnex is a lightweight local memory vault for personal AI users: it turns your experience, preferences, rules, and skills into a reviewable, portable, self-iterating AI memory system.**

# Memnex

**Language:** English | [简体中文](README.zh-CN.md)

**Repository:** [LLK-LL/AI-brain](https://github.com/LLK-LL/AI-brain)

**Memnex** is a lightweight local memory system for personal AI agents. The name comes from **Memory + Nexus**: memory means durable experience, preferences, rules, and skills; nexus means the connecting hub that links those fragments into a usable personal AI memory network.

It is not a heavy enterprise agent platform, and it is not just a folder of chat summaries. Memnex is closer to a personal "brain drive" for AI: it continuously organizes your experience, preferences, rules, skills, workflows, and hard-won lessons so that your AI assistant can remember how you work and reuse what you have already trained it to do.

If you use Codex-style agents, Claude, ChatGPT, local agents, or MCP memory tools every day, Memnex helps solve a familiar problem:

> Your AI gets smarter during a task, then forgets the useful parts when the next session starts.

Memnex turns that fragile local state into a reviewable, recoverable, and portable personal memory vault.

## Why Memnex?

Most AI memory tools focus on one of several directions:

| Category | Examples | Best for | Typical gap for personal users |
| --- | --- | --- | --- |
| General memory APIs | Mem0 | Developers building AI apps | Powerful, but still product/API oriented |
| Stateful agent frameworks | Letta / MemGPT | Long-running custom agents | More like an agent framework than a personal memory vault |
| Enterprise memory graphs | Zep | Business agents and production context | Optimized for scale, compliance, and teams |
| Local MCP memory layers | OpenMemory and similar tools | Sharing memory across AI clients | Often focused on storing and retrieving memories only |
| Personal knowledge RAG | Obsidian AI, Khoj, local document assistants | Asking questions over notes and documents | Great for document search, less focused on agent behavior, rules, and skills |

Memnex takes a smaller and more personal route.

It does not try to become another large AI platform. Instead, it preserves the training assets that already live on your machine: memories, rules, skills, preferences, templates, exports, and snapshots. That makes it especially useful for individuals who want a personal AI assistant that becomes more aligned over time without requiring a complex backend.

## Key Advantages

### Lightweight enough for personal use

Memnex is built around local files, structured exports, Git versioning, and scheduled sync.

- Local-first and user-controlled.
- Easy to inspect with normal file tools.
- Can be backed up to GitHub.
- Does not require an enterprise memory stack.
- Works well as a long-term personal training loop.

This makes it practical for everyday users: researchers, developers, writers, builders, and anyone who repeatedly trains AI through real work.

### It remembers how you work, not just what you said

Many memory systems store facts, summaries, or conversation snippets. Memnex stores the operational layer around your AI usage:

- `memories/`: facts, lessons, decisions, fixes, and reflections.
- `rules/`: behavior rules the agent should follow.
- `skills/`: reusable task workflows and Codex skills.
- `agent-skills/`: agent-level skill layers.
- `preferences/`: redacted preference and configuration snapshots.
- `templates/`: governance templates for memory, rule, skill, and workflow iteration.
- `manifest.json`: machine-readable sync provenance.

In other words, Memnex does not only preserve what the AI learned. It preserves the way you trained the AI to work.

### Reviewable, recoverable, and portable

Hidden memory databases are convenient, but they can become opaque over time. Memnex keeps the system layer and data layer separate:

```text
memory-system/      # sync scripts, scheduling, architecture, governance notes
memory-data/        # memories, rules, skills, preferences, templates, snapshots
```

Because the memory state is versioned, you can:

- inspect what the AI remembers;
- compare memory changes across time;
- roll back to an earlier snapshot;
- migrate your memory system to another machine;
- share or archive your personal AI training assets.

### Privacy-aware by default

The sync workflow is intentionally conservative. It excludes obvious caches, logs, temporary files, and transient database files. Preference and configuration snapshots are redacted for sensitive-looking keywords such as:

- `token`
- `password`
- `secret`
- `api_key`
- `credential`
- `cookie`
- `session`

You should still review the first sync before making a repository public, but Memnex is designed with personal safety in mind from the start.

## Supported Agent Platforms

Memnex is strongest today in the Codex + local MCP memory ecosystem, but its storage model is platform-neutral. Any agent that can read Markdown, rules, JSON exports, local files, or MCP tools can use Memnex as a personal memory source.

| Platform | Current support level | What Memnex provides | Configuration method |
| --- | --- | --- | --- |
| Codex CLI / Codex Desktop / Codex App | Native | `AGENTS.md`, `.codex/memories`, `.codex/rules`, `.codex/skills`, `.codex/templates`, redacted `.codex/config.toml` snapshots | Keep global guidance in `~/.codex/AGENTS.md`, project guidance in repository `AGENTS.md`, store reusable workflows as Codex skills, then run `memory-system/scripts/sync-memory-library.ps1` to snapshot the local Codex state. |
| Codex in VS Code / Cursor / Windsurf | Native through Codex extension behavior | Same Codex memory, rules, and skills layer | Install/use Codex in the editor, keep the same `AGENTS.md` and `.codex/skills` structure, and sync Memnex from the shared local Codex home. |
| `.agents` skill ecosystem | Native | `agent-skills/` layer for cross-agent skills and platform routers | Put shared skills under `~/.agents/skills`, then run the Memnex sync script so they are copied into `memory-data/.../agent-skills`. |
| MCP memory tools / Total Agent Memory style exports | Native export/archive support | Structured memory exports under `memory-data/.../exports` | Export or back up MCP memory into the configured local backup directory, then let Memnex collect the latest export and record provenance in `manifest.json`. |
| Claude Code / Claude Desktop | Easy adapter | Long-term memories, rules, skills, and workflow notes can be translated into Claude instructions and MCP-backed memory | Convert high-level Memnex rules into `CLAUDE.md`, project-scoped rules into `.claude/rules/`, and expose memory exports through an MCP server or manually referenced Markdown files. |
| Cursor | Easy adapter | Project conventions, workflow rules, and reusable task guidance | Convert Memnex rules or selected memories into Cursor Rules, such as project rules under `.cursor/rules/`, user rules in Cursor settings, or `AGENTS.md` where supported. |
| Continue | Easy adapter | Rules, prompts, tools, and MCP-readable memory exports | Add Memnex-derived rules to Continue local/global config, and connect memory search through an MCP server listed in Continue's tools/MCP configuration. |
| Windsurf / Cascade | Easy adapter | Memories, rules, and optional MCP-backed retrieval | Convert selected Memnex rules into Windsurf/Cascade Rules, add stable facts to Memories, and connect a memory MCP server through Cascade MCP settings when retrieval is needed. |
| Cline / Roo-style coding agents | Easy adapter | Memory-bank style Markdown context, project decisions, active context, and rules | Convert Memnex memories into Memory Bank files, add the operating instructions to `.clinerules/`, and optionally expose structured exports through MCP. |
| OpenAI Agents SDK | Developer integration | External memory source, retrieval tool, policy/rule source, skill registry | Load `memory-data/` from application code, index selected memories for retrieval, or wrap Memnex search as an MCP/tool call used by the agent. |
| LangChain / LangGraph / LlamaIndex / AutoGen / CrewAI | Developer integration | File-backed long-term memory and workflow knowledge | Parse `memory-data/exports`, `memories`, `rules`, and `skills` into your framework's memory/retriever/tool layer; MCP adapters can be used where the framework supports MCP. |
| Obsidian / Khoj / local knowledge-base tools | Knowledge-base integration | Human-readable long-term notes, templates, and workflow records | Import or link `memory-data/.../memories` and selected templates into the knowledge base, then use the tool's normal search/RAG layer over those files. |

## Current Memory Network

The images below visualize the current Memnex memory network. They show how many small pieces of experience, rules, skills, and workflow knowledge form a connected personal memory layer.

![Memnex memory network overview](assets/memory-network-overview.png)

![Memnex memory network map](assets/memory-network-map.png)

## How It Works

Memnex follows a simple loop:

```text
Collect -> Retrieve -> Self-iterate
```

### 1. Collect

During real work, AI produces valuable reusable knowledge:

- your preferred writing and coding style;
- project-specific conventions;
- debugging lessons;
- research workflows;
- reliable tool commands;
- mistakes that should not be repeated;
- skills that should be triggered in specific situations.

Memnex collects these assets from local memory exports, file-backed memories, rules, skills, preferences, and templates into a consistent `memory-data/` structure.

The point is simple: useful experience should not disappear when a chat ends.

### 2. Retrieve

Memnex is not meant to dump all history into every prompt. That would waste context and add noise.

Instead, the agent should retrieve the relevant memory, rule, skill, or preference for the current task:

- research tasks can retrieve research workflows and citation habits;
- coding tasks can retrieve project conventions and past fixes;
- writing tasks can retrieve tone, structure, and style preferences;
- automation tasks can retrieve tested commands and recovery paths.

The AI does not need to memorize the whole diary. It needs to open the right notes at the right time.

### 3. Self-iterate

The most important part of Memnex is not a single memory write. It is the long-term iteration loop.

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

Memnex does not retrain the base model. It trains the local memory, rules, and skills around the model so your assistant becomes increasingly aligned with your way of working.

## How Memnex Differs from Traditional RAG

Traditional RAG is usually:

```text
question -> retrieve document chunks -> answer
```

Memnex is closer to:

```text
task -> retrieve memories/rules/skills/preferences -> work in your style -> capture new experience -> improve the memory system
```

Traditional RAG helps an AI answer from documents. Memnex helps an AI become a better personal working partner.

## Who Is It For?

Memnex is useful for:

- people who use AI agents frequently;
- developers who want AI to remember project conventions;
- researchers who repeat literature, writing, and review workflows;
- builders who want to preserve automation and debugging lessons;
- personal users who do not want to run a heavy memory platform;
- anyone who wants their AI assistant to improve through repeated use.

## Repository Layout

```text
memory-system/
  README.md
  scripts/
    sync-memory-library.ps1        # collect, sanitize, commit, and push the latest state
    install-weekly-task.ps1        # install a local Windows weekly scheduled task

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

## Quick Start

Run a manual sync from the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\memory-system\scripts\sync-memory-library.ps1
```

Install the weekly local Windows task:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\memory-system\scripts\install-weekly-task.ps1
```

The sync script rebuilds `memory-data/current/`, copies approved memory-related sources, applies conservative redaction, writes `memory-data/manifest.json`, and commits/pushes changes when there is a diff.

## One-Sentence Summary

**Memnex is a lightweight local memory vault for personal AI users: it turns your experience, preferences, rules, and skills into a reviewable, portable, self-iterating AI memory system.**

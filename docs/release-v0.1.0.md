# v0.1.0 - Local-first memory vault for personal AI agents

Memnex v0.1.0 introduces the first public shape of a local-first memory vault for personal AI users.

## What is included

- A versioned `memory-data/` structure for memories, rules, skills, agent skills, preferences, templates, exports, and snapshots.
- A `memory-system/` layer with sync and scheduling scripts.
- PowerShell-based manual sync for Windows.
- Weekly Windows scheduled task installer.
- Conservative redaction for sensitive-looking preference and configuration values.
- Manifest metadata for sync provenance.
- English and Simplified Chinese README files.
- Adapter examples for Codex, Claude, Cursor, and MCP memory exports.
- Security and redaction guidance for public/private vault use.

## Who should try it

Memnex is useful if you:

- use AI agents frequently;
- want Codex, Claude, Cursor, or MCP-backed tools to remember how you work;
- prefer local files over opaque memory databases;
- want to version and review your AI working memory;
- want a small personal system instead of a heavy agent platform.

## Current limitations

- The sync workflow is currently Windows/PowerShell-first.
- macOS and Linux sync scripts are not included yet.
- Retrieval is intentionally left to the agent/client layer for now.
- Public sharing still requires manual review of memory data.

## Suggested repository description

```text
Lightweight local memory vault for personal AI agents. Preserve memories, rules, skills, preferences, and workflows across Codex, Claude, Cursor, MCP, and local agents.
```

## Suggested topics

```text
ai-agent, ai-memory, memory, mcp, codex, claude, cursor, personal-ai, local-first, agent-tools, rag, knowledge-base, automation, powershell
```

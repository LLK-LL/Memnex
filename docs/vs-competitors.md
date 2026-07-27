# Memnex Compared With Other Memory Systems

Memnex is not trying to replace every memory product. It is focused on one
specific niche: local, MCP-native memory for coding agents.

## Positioning

| Project | Best fit | Local-first | MCP-native | Coding-agent workflow memory |
| --- | --- | :-: | :-: | :-: |
| mem0 | Hosted or embedded memory SDKs | Partial | SDK-driven | Partial |
| Letta | Stateful agent runtime | Yes | No | Partial |
| Zep / Graphiti | Enterprise temporal knowledge graph | Partial | Partial | Partial |
| Supermemory | Personal second brain and SaaS memory API | No | Partial | No |
| Cognee | GraphRAG knowledge pipelines | Partial | No | Partial |
| LangMem | LangGraph long-term memory primitives | Partial | No | Partial |
| Memnex | Local coding-agent memory through MCP | Yes | Yes | Yes |

## Where Memnex Is Different

- **MCP is the primary interface.** The tool surface is built for Codex, Claude
  Code, Cursor, and similar agents that work through local tools.
- **The data lives on disk.** SQLite, local vector stores, graph exports, logs,
  and private memory stay outside the public repository and outside hosted
  memory APIs.
- **It tracks work, not only chat.** Decisions, fixes, file risks, sessions,
  command failures, project rules, workflow predictions, and cross-project
  analogies are first-class memory objects.
- **It includes a visual graph workspace.** Memory Galaxy exposes the same
  local graph through 2D and 3D inspection surfaces.

## When To Pick Memnex

Pick Memnex when you want a private memory layer that follows your coding agent
from task to task and project to project.

Pick a hosted service when you need managed infrastructure, team dashboards,
SaaS API quotas, or product memory for end users rather than a developer's local
agent environment.

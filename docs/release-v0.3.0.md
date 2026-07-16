# v0.3.0 - Memory Galaxy visualization workspace

Memnex v0.3.0 upgrades the graph viewer from a plain node-link export into a
local Memory Galaxy workspace: a cinematic but practical interface for reading
personal AI memory systems.

## Visual tour

### Galaxy overview

![Memory Galaxy overview](https://raw.githubusercontent.com/LLK-LL/Memnex/main/assets/memory-galaxy-overview.png)

The overview turns the whole memory graph into an orbiting map of memory
systems. Use it to scan system density, search nodes, filter types/layers, and
watch the live performance HUD while navigating large graphs.

### System solar-system view

![Memory Galaxy solar system view](https://raw.githubusercontent.com/LLK-LL/Memnex/main/assets/memory-galaxy-solar-system.png)

Double-click a system to enter its local solar system. The system center becomes
the star; important memories become planets; the inspector shows counts,
density, recent activity, and high-weight connections.

### Planet-satellite context

![Memory Galaxy planet satellite view](https://raw.githubusercontent.com/LLK-LL/Memnex/main/assets/memory-galaxy-planet-satellite.png)

Double-click a planet to inspect direct neighbors, derived context, evidence,
and external relations as readable orbital rings.


## What is included

- PixiJS-powered Memory Galaxy UI.
- Galaxy overview, system drill-down, and planet-satellite navigation.
- Full graph export by default. Node/edge limits are used only when explicitly
  requested with `--max-nodes` or `--max-edges`.
- Search, node type filters, layer/edge filters, breadcrumbs, minimap, and
  inspector tabs.
- Performance HUD for FPS, frame time, memory estimate, GPU renderer, and
  visible graph size.
- Exporter support for embedded graph data and inlined viewer modules, making
  exported folders easy to open locally.
- Animation rendering tuned to update existing scene objects instead of
  rebuilding the scene on every animation tick.

## Who should try it

- Codex, Claude, Cursor, and MCP users with local memory graphs.
- People who want to audit what their AI assistant has learned without reading
  raw SQLite rows.
- Developers building local-first agent memory workflows.
- Researchers comparing rule, preference, skill, and evidence structures inside
  a personal memory system.

## Privacy boundary

This release includes viewer source code and sanitized demo screenshots only. It
does not include live memory databases, raw memories, private graph exports,
logs, transcripts, backups, WAL/SHM files, tokens, cookies, or user data.

Generated viewer folders may contain private memory summaries from the selected
database. Keep generated `graph.json` files private unless you have reviewed and
sanitized them.

## How to use

```powershell
python .\memory-system\tools\graph-viewer\export_graph_viewer.py `
  --db "$env:USERPROFILE\.tam\memory.db" `
  --output .\graph-viewer-output
```

Open `graph-viewer-output\index.html` for the full 2D Memory Galaxy workspace.
Do not pass `--max-nodes` or `--max-edges` when you want the full graph.

## Current limitations

- The viewer is a local static export, not a hosted service.
- Very large graphs may need export limits or local filtering.
- The exporter expects Total Agent Memory-style graph tables.
- Demo screenshots use synthetic/sanitized graph data, not a public dump of a
  private memory database.

## Suggested repository description

Local-first memory vault for personal AI agents, now with a Memory Galaxy viewer
for exploring rules, skills, preferences, evidence, and graph context.

## Suggested topics

`ai-memory`, `ai-agent`, `local-first`, `mcp`, `codex`, `claude`, `cursor`,
`knowledge-graph`, `memory-graph`, `graph-visualization`, `personal-ai`,
`agent-tools`

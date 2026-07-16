# Memory System

This directory contains the durable system layer for the Memnex memory vault.

## Layering

Memnex stores system logic and live knowledge separately:

| Layer | Path | Purpose |
| --- | --- | --- |
| System | `memory-system/` | Architecture, sync scripts, scheduling, governance notes |
| Data | `memory-data/current/` | Latest memory exports, rules, skills, preferences, templates |
| Metadata | `memory-data/manifest.json` | Machine-readable sync provenance |

## Memory Galaxy Viewer

Memnex includes a local static Memory Galaxy exporter. It reads a Total Agent
Memory-style SQLite graph in read-only mode and writes a portable browser
workspace with:

- 2D Memory Galaxy overview;
- system-level solar-system drill-down;
- planet-satellite local context view;
- search, filters, minimap, inspector tabs, and performance HUD.

By default, the exporter writes the full graph. Use `--max-nodes` or
`--max-edges` only when you intentionally want a reduced rendering workload.

```powershell
python .\memory-system\tools\graph-viewer\export_graph_viewer.py `
  --db "$env:USERPROFILE\.tam\memory.db" `
  --output .\graph-viewer-output
```

Open `graph-viewer-output\index.html` for the full 2D Memory Galaxy workspace. Generated viewer output is ignored by Git because it can contain private memory summaries from the selected database.

## Data Layers

- `exports/`: MCP memory exports and SQLite snapshots from the local memory engine.
- `memories/`: file-backed memory notes from `.codex/memories`.
- `rules/`: behavioral rules from `.codex/rules`.
- `skills/`: local Codex skills from `.codex/skills`.
- `agent-skills/`: agent-level skills from `.agents/skills`.
- `preferences/`: redacted configuration and agent instruction snapshots.
- `templates/`: governance templates for memory, rules, preferences, and workflow iteration.

## Sync Contract

`sync-memory-library.ps1` performs a repeatable sync:

1. Rebuild `memory-data/current/`.
2. Copy only approved memory-related sources.
3. Exclude obvious secrets, caches, logs, and transient state.
4. Redact sensitive-looking preference/config lines.
5. Write `memory-data/manifest.json`.
6. Commit and push changes when a diff exists.

The script is safe to run manually or from a scheduler.

## Scheduling

Two scheduling paths are supported:

- Codex automation: preferred when MCP memory export should be refreshed by an agent before committing.
- Windows Scheduled Task: useful for local unattended file-level sync.

Use `install-weekly-task.ps1` to install a local Windows task that runs every Monday at 09:00.

# Memory System

This directory contains the durable system layer for the Memnex memory vault.

## Layering

Memnex stores system logic and live knowledge separately:

| Layer | Path | Purpose |
| --- | --- | --- |
| System | `memory-system/` | Architecture, sync scripts, scheduling, governance notes |
| Data | `memory-data/current/` | Latest memory exports, rules, skills, preferences, templates |
| Metadata | `memory-data/manifest.json` | Machine-readable sync provenance |

## Graph Viewer

Memnex includes a local static graph viewer exporter:

```powershell
python .\memory-system\tools\graph-viewer\export_graph_viewer.py `
  --db "$env:USERPROFILE\.tam\memory.db" `
  --output .\graph-viewer-output
```

The exporter opens the SQLite memory database in read-only mode, writes
`graph.json`, and copies static 2D/3D viewer assets to the output directory.
Generated viewer output is ignored by Git because it can contain private memory
summaries from the selected database.

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

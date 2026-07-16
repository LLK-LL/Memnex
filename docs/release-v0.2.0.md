# v0.2.0 - Memory graph visualization

Memnex v0.2.0 publishes only the memory system layer and adds a local graph
viewer for inspecting memory graph structure without committing private memory
data.

## What is included

- A local 2D/3D memory graph viewer exporter under
  `memory-system/tools/graph-viewer/`.
- Static browser assets for Cytoscape.js 2D graph exploration and
  `3d-force-graph` 3D exploration.
- Read-only SQLite export from graph tables into `graph.json`.
- README and memory-system documentation for the visualization workflow.
- Git ignore rules that exclude live memory data, generated graph viewer output,
  SQLite databases, WAL/SHM files, logs, and temporary files.

## Privacy boundary

This release intentionally excludes `memory-data/` from Git. It contains system
files only: documentation, scripts, viewer source, and static assets. It does
not include live memory exports, raw memories, database snapshots, logs,
transcripts, backups, or generated graph exports.

## How to use

```powershell
python .\memory-system\tools\graph-viewer\export_graph_viewer.py `
  --db "$env:USERPROFILE\.tam\memory.db" `
  --output .\graph-viewer-output
```

Open `graph-viewer-output\index.html` for 2D mode or
`graph-viewer-output\viewer-3d.html` for 3D mode.

## Current limitations

- The graph viewer is a local static export, not a hosted service.
- Generated `graph.json` can contain private memory summaries; keep exported
  viewer directories private unless reviewed.
- The exporter expects Total Agent Memory-style graph tables.

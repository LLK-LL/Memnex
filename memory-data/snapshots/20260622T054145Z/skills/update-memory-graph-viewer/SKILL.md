---
name: update-memory-graph-viewer
description: Refresh the local Total Agent Memory Cytoscape graph visualization. Use when the user says "鏇存柊璁板繂搴撶殑鍙鍖栧唴瀹?, asks to update, refresh, or re-export the memory graph viewer, or wants the current memory network visualization regenerated from memory.db.
---

# Update Memory Graph Viewer

## Purpose

Regenerate the local Cytoscape.js memory graph viewer from the live Total Agent Memory SQLite database and make the refreshed `graph.json` available to the existing static viewer.

## Default Workflow

Run the export from the Total Agent Memory repository. Do not pass `--max-nodes` or `--max-edges` by default; the expected behavior is a full graph export.

```powershell
Set-Location "C:\Users\Administrator\total-agent-memory"
python src/tools/memory_graph_viewer_export.py --output "C:\Users\Administrator\Documents\Codex\2026-06-16\new-chat-3\outputs\memory-graph-viewer"
```

After export, read the printed JSON metadata and report at least `node_count`, `edge_count`, and the viewer URL.

## Viewer Server

If a server is already serving the output directory, reuse it. Otherwise start a local static server from the output directory:

```powershell
Set-Location "C:\Users\Administrator\Documents\Codex\2026-06-16\new-chat-3\outputs\memory-graph-viewer"
python -m http.server 8765 --bind 127.0.0.1
```

Use `http://127.0.0.1:8765/` as the default URL. If port `8765` is occupied by an unrelated process, use the next free local port and report the actual URL.

## Degraded Mode

Only reduce graph size after the user reports that the page freezes, becomes unusably slow, or the browser cannot render the full graph. In that case, re-export with explicit limits:

```powershell
Set-Location "C:\Users\Administrator\total-agent-memory"
python src/tools/memory_graph_viewer_export.py --output "C:\Users\Administrator\Documents\Codex\2026-06-16\new-chat-3\outputs\memory-graph-viewer" --max-nodes 1500 --max-edges 4000
```

Treat these limits as a temporary rendering workaround, not the default.

## Validation

Confirm `graph.json` exists in the output directory after export. If the user asks for verification, request `http://127.0.0.1:8765/graph.json` or open the viewer in the browser and confirm the metadata shown in the page matches the export metadata.

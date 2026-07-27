# Changelog

## 12.7.1 - 2026-07-27

- Removed internal tests, smoke workflows, benchmark harnesses, evaluation
  datasets, generated temporary files, and stale design-planning artifacts from
  the public repository.
- Moved the shared LLM provider adapter into `src/ai_layer/llm_adapter.py` so
  runtime answerability and iterative recall no longer depend on benchmark-only
  modules.
- Trimmed release documentation to the current v12.7 Knowledge Galaxy guide and
  kept only the latest real 3D UI screenshots under `docs/assets/`.
- Simplified installers and update scripts to install runtime dependencies only.
- Updated package metadata and cleanup boundaries for a runtime-focused source
  tree.

## 12.7.0 - 2026-07-27

- Changed the default FastEmbed text model to
  `jinaai/jina-embeddings-v2-base-zh` with a 768-dimensional vector space.
- Added `scripts/migrate_embeddings_v127.py` for in-place re-encoding of
  active knowledge embeddings and existing representation rows.
- Repaired stale and inconsistent representation queue handling before drain.
- Tightened `memory_recall` diagnostics across FTS, CJK FTS, semantic vectors,
  multi-representation candidates, graph expansion, and local reranking.
- Added the Knowledge Galaxy 3D route and bundled its static assets with the
  package data.
- Cleaned the public repository to focus on runtime source, installers,
  documentation, migrations, skills, hooks, and visual assets.

## 12.6.0 - 2026-07-16

- Added the 2D/3D Memory Galaxy workspace.
- Hardened save, recall, graph expansion, multi-representation search, and
  rule-layer recall boundaries.
- Added visual release documentation and screenshots under `docs/assets/`.

## 12.5.0 - 2026-06-22

- Added the static memory graph viewer exporter at
  `src/tools/memory_graph_viewer_export.py`.
- Kept exports local and out of Git by default because graph data can contain
  private memory summaries.

## Earlier History

Older internal release notes and generated evaluation artifacts were removed
from the public source tree during the v12.7 repository cleanup. The current
source keeps the compatibility shims, migrations, and runtime behavior needed by
existing installs.

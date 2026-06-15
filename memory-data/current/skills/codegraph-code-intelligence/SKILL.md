---
name: codegraph-code-intelligence
description: Use local CodeGraph for repository code intelligence. Trigger when the user mentions codegraph, CodeGraph, code graph, symbol graph, call graph, callers/callees, impact analysis, affected tests, MCP code intelligence, or asks Codex to inspect a codebase structurally before broad grep/read exploration.
---

# CodeGraph Code Intelligence

Use the local CodeGraph executable directly:

`C:\Users\Administrator\AppData\Local\codegraph\current\bin\codegraph.cmd`

Do not rediscover the executable path when the user mentions CodeGraph unless this path fails.

## Default Workflow

1. Resolve the target repository path from the user request or current working directory.
2. Run `status` first to see whether `.codegraph/` exists and whether the index is usable.
3. If uninitialized, run `init <repo-path>`. Indexing runs by default in current CodeGraph versions.
4. If initialized but stale, run `sync <repo-path>` before answering structural questions.
5. Prefer CodeGraph queries before broad manual `rg`/file reads:
   - `query` for symbols.
   - `files` for indexed structure.
   - `callers` and `callees` for call relationships.
   - `impact` for change radius.
   - `affected` for likely tests after source changes.
6. Use normal file reads after CodeGraph identifies the relevant files/symbols.
7. For MCP integration, use `serve --mcp --path <repo-path>` or `install` only when the user asks to configure an agent.

## Reference

Read `references/cli.md` when you need exact command syntax, JSON output, failure handling, MCP setup, or the theory model behind CodeGraph.

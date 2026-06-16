# CodeGraph CLI Reference

## Local Installation

Primary executable:

```powershell
& 'C:\Users\Administrator\AppData\Local\codegraph\current\bin\codegraph.cmd'
```

Observed local version:

```powershell
& 'C:\Users\Administrator\AppData\Local\codegraph\current\bin\codegraph.cmd' --version
```

Expected at creation time: `0.9.9`.

## Mental Model

CodeGraph is a local-first code intelligence system. It parses supported code with tree-sitter, writes symbols, files, and relationship edges into a per-project `.codegraph/` SQLite/FTS5 database, then exposes query and graph traversal operations through a CLI and MCP server.

The practical theory is:

```text
files
  -> AST extraction with tree-sitter
  -> local graph database: files, symbols, edges
  -> reference resolution: imports, names, framework patterns
  -> graph traversal: callers, callees, impact, affected tests
  -> compact context for AI agents
```

This means CodeGraph should guide where Codex reads next; it does not replace source-file verification.

## Command Patterns

Set a reusable variable in PowerShell:

```powershell
$cg = 'C:\Users\Administrator\AppData\Local\codegraph\current\bin\codegraph.cmd'
$repo = 'C:\path\to\repo'
```

Check state:

```powershell
& $cg status $repo
```

Initialize and build the first index:

```powershell
& $cg init $repo
```

Refresh after file changes:

```powershell
& $cg sync $repo
```

Search symbols:

```powershell
& $cg query 'SymbolName' --path $repo --limit 20
& $cg query 'SymbolName' --path $repo --limit 20 --json
& $cg query 'SymbolName' --path $repo --kind function --json
```

Inspect indexed files:

```powershell
& $cg files --path $repo
```

Find graph relationships:

```powershell
& $cg callers 'functionName' --path $repo
& $cg callees 'functionName' --path $repo
& $cg impact 'functionName' --path $repo
```

Find likely tests affected by source files:

```powershell
& $cg affected --path $repo 'src\path\changed-file.ts'
```

Start as MCP server:

```powershell
& $cg serve --mcp --path $repo
```

Install into supported agents only when requested:

```powershell
& $cg install --target auto --location global --yes
```

Print config without writing files:

```powershell
& $cg install --print-config codex
```

Remove stale lock:

```powershell
& $cg unlock $repo
```

## Failure Handling

- If `status` reports no project index, run `init`.
- If results look stale after edits, run `sync`.
- If indexing is blocked by a lock and no CodeGraph process is active, run `unlock`.
- If a query returns too many matches, rerun with `--kind` and smaller `--limit`.
- If CodeGraph finds candidate symbols, still read the actual files before editing.
- If the fixed executable path fails, run `Get-Command codegraph` and `where.exe codegraph`, then report the changed path to the user before continuing.

## Source Notes

- GitHub repository: https://github.com/colbymchenry/codegraph
- Project notes: https://github.com/colbymchenry/codegraph/blob/main/CLAUDE.md
- Package metadata: https://github.com/colbymchenry/codegraph/blob/main/package.json

# Memory Protocol

Append the block below into your `~/.codex/AGENTS.md` or project
`AGENTS.md`. The installer should keep this block in sync for Codex.

---

## Memory Protocol (total-agent-memory v10.5)

A persistent cross-session memory is wired in via the `memory` MCP server.
The same protocol applies as in Claude Code / Cursor / Cline:

1. **Session start:** call `self_rules_context(project=..., detail="compact")`,
   then `memory_recall(query, project)` for the current task.
2. **Before any non-trivial task:** call `memory_recall` to find the recipe.
   Do not reinvent conventions you can recall.
3. **After every significant action:** call `memory_save` immediately with a
   concise reusable record. Use tags such as `reusable`, the technology, and
   the project area when applicable.
4. **On reproducible non-zero shell/tool/API/config errors:** call
   `self_error_log(description, category, severity, fix, project)`. After 3
   similar patterns, extract an insight with `self_insight(action="add", ...)`.
5. **End of significant work:** save a short summary, next steps, or reflection
   when new reusable knowledge was created.

Cross-project lookup: `analogize(text, exclude_project=<current>)`.
Time-travel: `kg_at(timestamp)`. Stuck after 3 failures: stop, save a
`type="lesson"` record, and ask the user for direction.

Full reference: `skills/memory-protocol/`.

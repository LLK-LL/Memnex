# Memory Protocol

Append the block below into your `~/.codex/AGENTS.md` or project
`AGENTS.md`. The installer should keep this block in sync for Codex.

---

## Memory Protocol

Use memory only when the task depends on durable local state: prior preferences, rules, decisions, conventions, known bugs, repo history, or user wording like "之前/上次/继续/按我的习惯/记得/沿用".

Load for local repo/code work, memory/rule/skill/agent workflow changes, or history-dependent tasks:

1. `self_rules_context(project="<project>", detail="compact", phase="<phase>")`
2. `memory_recall(query="<specific current task>", project="<project>", mode="rag", limit=5, include_cognitive=false)`

Skip memory for self-contained external tasks: GitHub/web/paper/doc/package/news search, public project lookup, general Q&A, prompt-provided rewrite/translation/summary, casual chat, or trivial deterministic commands.

For external search, use search/research skills directly. If durable user preferences may matter, call only:
`self_rules_context(project="global", detail="compact", phase="<phase>")`
Run `memory_recall` only if rules or user wording point to project-specific history.

Save durable knowledge only:
- decision: architectural decision
- solution: non-trivial bug fix
- lesson: gotcha/pitfall
- fact: infrastructure/config fact
- convention: project convention

Use `memory_save(type="<kind>", ...)`. Do not save transient search results, obvious code facts, casual comments, or one-off recommendations.

On reproducible command/tool/API/config errors, log them:

`self_error_log(description="...", category="code_error|config_error|api_error|timeout|wrong_assumption|missing_context", severity="low|medium|high|critical", fix="...", project="<project>")`

At the end of significant work, save a brief memory or reflection if new reusable knowledge was created.

Full reference: `skills/memory-protocol/`.

# Claude Adapter

Memnex can be used with Claude Code or Claude Desktop by translating selected memories, rules, and workflows into Claude-readable instructions.

## What to Export

Start small. Do not move the whole vault into Claude.

Good candidates:

- stable project rules;
- writing or coding style preferences;
- tool usage rules;
- repeated debugging lessons;
- reusable workflows;
- a short index of important memory files.

Avoid:

- raw private exports;
- noisy old snapshots;
- secrets or credentials;
- long unfiltered chat history.

## Suggested Claude Code Shape

```text
project/
  CLAUDE.md
  .claude/
    rules/
      project-memory.md
      coding-style.md
      workflow-rules.md
```

`CLAUDE.md` can point Claude to the relevant Memnex files:

```md
# Project Memory

Use the Memnex-derived rules in `.claude/rules/` before changing code.

When a task repeats a past workflow, check the relevant memory note first instead of rediscovering the process.
```

## Suggested Manual Conversion

1. Pick 3-5 stable rules from `memory-data/current/rules/`.
2. Convert them into short Claude instructions.
3. Pick 1-3 high-value workflows from `memory-data/current/skills/`.
4. Summarize each workflow as a task checklist.
5. Keep a link or local path back to the original Memnex source.

## Future MCP Path

If Claude is connected to an MCP server that can search local files, expose selected Memnex directories as a retrieval source:

```text
memory-data/current/memories/
memory-data/current/rules/
memory-data/current/skills/
```

Keep retrieval selective. Claude should fetch the memory needed for the task, not load the entire vault.

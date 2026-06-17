# Codex Memory Sync

This example shows the native Memnex path: preserve Codex memories, rules, skills, preferences, and templates as a versioned local memory vault.

## Use Case

You use Codex regularly and keep teaching it:

- project conventions;
- preferred coding style;
- recurring debugging fixes;
- reusable workflows;
- task-specific rules;
- skills that should trigger in specific situations.

Without a memory vault, those assets can remain scattered across chats, local configuration, and skill folders. Memnex snapshots them into a reviewable structure.

## Suggested Local Layout

```text
~/.codex/
  AGENTS.md
  memories/
  rules/
  skills/
  templates/
  config.toml

Memnex/
  memory-system/
  memory-data/
```

## Run a Manual Sync

From the Memnex repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\memory-system\scripts\sync-memory-library.ps1
```

The script rebuilds `memory-data/current/`, applies conservative redaction, writes `memory-data/manifest.json`, and commits/pushes if there is a diff.

## Review the Result

Check:

- `memory-data/current/memories/`
- `memory-data/current/rules/`
- `memory-data/current/skills/`
- `memory-data/current/preferences/`
- `memory-data/manifest.json`

Before publishing anything, follow the [security and redaction checklist](../docs/security-and-redaction.md).

## How a Future Agent Uses It

A future Codex task can retrieve the relevant file-backed memory, rule, skill, or preference from `memory-data/` instead of asking you to restate the same context.

The goal is not to paste the whole vault into every prompt. The goal is to open the right memory at the right time.

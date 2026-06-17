# MCP Memory Export

Memnex can archive structured exports from MCP memory tools or Total Agent Memory style systems.

## Goal

Keep memory exports reviewable and portable:

```text
MCP memory tool
  -> export JSON / SQLite snapshot / Markdown notes
  -> Memnex memory-data/current/exports/
  -> manifest provenance
  -> versioned backup
```

## Suggested Export Shape

```text
memory-data/
  current/
    exports/
      memory-export-latest.json
      latest-backup.json
    memories/
    rules/
    skills/
  manifest.json
```

## What to Record in the Manifest

The manifest should make it clear:

- when the export was collected;
- which source path or tool produced it;
- which files were copied;
- which files were excluded;
- whether redaction was applied;
- whether any safety warnings were raised.

## Retrieval Pattern

Avoid loading an entire export into a prompt. Instead:

1. Search the export or derived Markdown notes.
2. Select the relevant memory.
3. Add only that memory to the current agent context.
4. Capture any new lesson back into Memnex after the task.

## Public Sharing Warning

MCP exports often contain raw user memory. Treat them as private unless you have reviewed and sanitized them. See [Security and redaction](../docs/security-and-redaction.md).

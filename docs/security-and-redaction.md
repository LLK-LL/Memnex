# Security and Redaction

Memnex is designed for personal memory vaults, so the default sync workflow is intentionally conservative. It tries to preserve useful AI working memory while avoiding obvious secrets, caches, logs, and transient files.

## What the Sync Should Avoid

The sync workflow should not collect:

- runtime logs;
- temporary files;
- cache directories;
- database write-ahead files such as `*.sqlite-wal` and `*.sqlite-shm`;
- raw credential stores;
- browser cookies;
- unreviewed private exports;
- any file that is not needed for long-term AI memory.

## Redaction Keywords

Preference and configuration snapshots are redacted for sensitive-looking keywords such as:

- `token`
- `password`
- `secret`
- `api_key`
- `credential`
- `cookie`
- `session`

This is a safety layer, not a guarantee. Redaction rules can miss unusual secret names, encoded secrets, private project names, personal notes, or sensitive business context.

## Public Repository Checklist

Before making a Memnex repository public, review:

- `memory-data/current/preferences/`
- `memory-data/current/exports/`
- `memory-data/current/memories/`
- `memory-data/current/rules/`
- `memory-data/current/skills/`
- `memory-data/snapshots/`
- `memory-data/manifest.json`

Search for obvious sensitive strings:

```powershell
Select-String -Path .\memory-data\**\* -Pattern "token","password","secret","api_key","credential","cookie","session" -CaseSensitive:$false
```

Also search for personal identifiers, private project names, customer names, internal hosts, and private repository URLs.

## Recommended Publishing Pattern

For public examples, prefer one of these approaches:

1. Publish a sanitized demo vault with representative fake memories.
2. Publish the `memory-system/` layer and example `memory-data/` structure, while keeping private snapshots in a separate private repository.
3. Publish real snapshots only after a manual review.

Memnex can support public sharing, but the safest default is to treat your first sync as private until you have inspected it carefully.

## Reporting Security Issues

If you find a redaction issue or unsafe sync behavior, please open a private report if GitHub Security Advisories are enabled for the repository. Otherwise, open a minimal issue that describes the class of problem without pasting secrets.

# AI-brain

AI-brain is a portable memory vault for Codex-style agents: not just a backup of notes, but a living operating layer that keeps experience, rules, skills, and preferences versioned together.

This repository separates the memory system from the current memory contents:

- `memory-system/` contains the architecture, operating guide, and sync scripts.
- `memory-data/current/` contains the latest synced memory, rules, skills, preferences, and exports.
- `memory-data/manifest.json` records what was captured, when it was captured, and where each layer came from.

## Why It Matters

Most agent setups forget everything important at the worst possible moment. AI-brain turns that fragile local state into a reviewable, recoverable, and shareable knowledge base:

- decisions and lessons are preserved across sessions;
- behavioral rules stay separate from ordinary memories;
- reusable SKILL instructions are stored as first-class assets;
- user preferences are versioned without mixing them into implementation code;
- weekly sync keeps the repository fresh without manual babysitting.

## Repository Layout

```text
memory-system/
  README.md                       # architecture and operating model
  scripts/
    sync-memory-library.ps1        # collect, sanitize, commit, and push the latest state
    install-weekly-task.ps1        # install a local Windows weekly scheduled task

memory-data/
  current/
    exports/                       # structured memory exports and database snapshots
    memories/                      # file-backed memory notes
    rules/                         # local behavioral rules
    skills/                        # local Codex skills
    agent-skills/                  # .agents skill layer
    preferences/                   # redacted preference/config snapshots
    templates/                     # memory/rule/skill governance templates
  manifest.json                    # sync metadata
```

## Quick Start

Run a manual sync from the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\memory-system\scripts\sync-memory-library.ps1
```

Install the weekly local Windows task:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\memory-system\scripts\install-weekly-task.ps1
```

The sync script rebuilds `memory-data/current/`, stages changes, commits when there is a diff, and pushes to the configured GitHub remote.

## Privacy Model

The sync tooling is intentionally conservative. It excludes known secret stores and redacts lines containing sensitive keywords such as token, password, secret, and API key from preference/config snapshots. Review the first sync before treating the repository as public.

## Current Status

Initial sync target: `LLK-LL/AI-brain`.

The repository is designed to be updated every week so it reflects the newest memory records, rules, SKILL files, and preferences.

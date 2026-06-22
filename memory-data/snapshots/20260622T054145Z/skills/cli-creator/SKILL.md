---
name: cli-creator
# REDACTED: sensitive-looking memory line
---

# CLI Creator

Create a real CLI that future Codex threads can run by command name from any working directory.

This skill is for durable tools, not one-off scripts. If a short script in the current repo solves the task, write the script there instead.

## Start

Name the target tool, its source, and the first real jobs it should do:

- Source: API docs, OpenAPI JSON, SDK docs, curl examples, browser app, existing internal script, article, or working shell history.
- Jobs: literal reads/writes such as `list drafts`, `download failed job logs`, `search messages`, `upload media`, `read queue schedule`.
- Install name: a short binary name such as `ci-logs`, `slack-cli`, `sentry-cli`, or `buildkite-logs`.

Prefer a new folder under `~/code/clis/<tool-name>` when the user wants a personal tool and has not named a repo.

Before scaffolding, check whether the proposed command already exists:

```bash
command -v <tool-name> || true
```

If it exists, choose a clearer install name or ask the user.

## Choose the Runtime

Before choosing, inspect the user's machine and source material:

```bash
command -v cargo rustc node pnpm npm python3 uv || true
```

Then choose the least surprising toolchain:

- Default to **Rust** for a durable CLI Codex should run from any repo: one fast binary, strong argument parsing, good JSON handling, easy copy/install into `~/.local/bin`.
# REDACTED: sensitive-looking memory line
- Use **Python** when the source is data science, local file transforms, notebooks, SQLite/CSV/JSON analysis, or Python-heavy admin tooling that can still be installed as a durable command.

Do not pick a language that adds setup friction unless it materially improves the CLI. If the best language is not installed, either install the missing toolchain with the user's approval or choose the next-best installed option.

State the choice in one sentence before scaffolding, including the reason and the installed toolchain you found.

## Command Contract

# REDACTED: sensitive-looking memory line

When designing the command surface, read [references/agent-cli-patterns.md](references/agent-cli-patterns.md) for the expected composable CLI shape.

Build toward this surface:

- `tool-name --help` shows every major capability.
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
- Discovery commands find accounts, projects, workspaces, teams, queues, channels, repos, dashboards, or other top-level containers.
- Resolve commands turn names, URLs, slugs, permalinks, customer input, or build links into stable IDs so future commands do not repeat broad searches.
- Read commands fetch exact objects and list/search collections. Paginated lists support a bounded `--limit`, cursor, offset, or clearly documented default.
- Write commands do one named action each: create, update, delete, upload, schedule, retry, comment, draft. They accept the narrowest stable resource ID, support `--dry-run`, `draft`, or `preview` first when the service allows it, and do not hide writes inside broad commands such as `fix`, `debug`, or `auto`.
- `--json` returns stable machine-readable output.
- A raw escape hatch exists: `request`, `tool-call`, `api`, or the nearest honest name.

Do not expose only a generic `request` command. Give Codex high-level verbs for the repeated jobs.

# REDACTED: sensitive-looking memory line

# REDACTED: sensitive-looking memory line

Support the boring paths first, in this precedence order:

# REDACTED: sensitive-looking memory line
2. User config under `~/.<tool-name>/config.toml` or another simple documented path.
# REDACTED: sensitive-looking memory line

# REDACTED: sensitive-looking memory line

# REDACTED: sensitive-looking memory line

# REDACTED: sensitive-looking memory line

Use screenshots to infer workflow, UI vocabulary, fields, and confirmation points. Do not treat screenshots as API evidence unless they are paired with a network request, export, docs page, or fixture.

## Build Workflow

# REDACTED: sensitive-looking memory line
2. Sketch the command list in chat. Keep names short and shell-friendly.
3. Scaffold the CLI with a README or equivalent repo-facing instructions.
4. Implement `doctor`, discovery, resolve, read commands, one narrow draft or dry-run write path if requested, and the raw escape hatch.
5. Install the CLI on PATH so `tool-name ...` works outside the source folder.
6. Smoke test from another repo or `/tmp`, not only with `cargo run` or package-manager wrappers. Run `command -v <tool-name>`, `<tool-name> --help`, and `<tool-name> --json doctor`.
# REDACTED: sensitive-looking memory line

If a live write is needed for confidence, ask first and make it reversible or draft-only.

When the source is an existing script or shell history, split the working invocation into real phases: setup, discovery, download/export, transform/index, draft, upload, poll, live write. Preserve the flags, paths, and environment variables the user already relies on, then wrap the repeatable phases with stable IDs, bounded JSON, and file outputs.

For raw escape hatches, support read-only calls first. Do not run raw non-GET/HEAD requests against a live service unless the user asked for that specific write.

For media, artifact, or presigned upload flows, test each phase separately: create upload, transfer bytes, poll/read processing status, then attach or reference the resulting ID.

For fixture-backed prototypes, keep fixtures in a predictable project path and make the CLI locate them after installation. Smoke-test from `/tmp` to catch binaries that only work inside the source folder.

For log-oriented CLIs, keep deterministic snippet extraction separate from model interpretation. Prefer a command that emits filenames, line numbers or byte ranges, matched rules, and short excerpts.

## Rust Defaults

When building in Rust, use established crates instead of custom parsers:

- `clap` for commands and help
- `reqwest` for HTTP
- `serde` / `serde_json` for payloads
- `toml` for small config files
- `anyhow` for CLI-shaped error context

Add a `Makefile` target such as `make install-local` that builds release and installs the binary into `~/.local/bin`.

## TypeScript/Node Defaults

When building in TypeScript/Node, keep the CLI installable as a normal command:

- `commander` or `cac` for commands and help
- native `fetch`, the official SDK, or the user's existing HTTP helper for API calls
- `zod` only where external payload validation prevents real breakage
- `package.json` `bin` entry for the installed command
- `tsup`, `tsx`, or `tsc` using the repo's existing convention

Add an install path such as `pnpm install`, `pnpm build`, and `pnpm link --global`, or a `Makefile` target that installs a small wrapper into `~/.local/bin`.

## Python Defaults

When building in Python, prefer boring standard-library pieces unless the workflow needs more:

- `argparse` for commands and help, or `typer` when subcommands would otherwise get messy
- `urllib.request` / `urllib.parse`, `requests`, or `httpx` for HTTP, matching what is already installed or already used nearby
- `json`, `csv`, `sqlite3`, `pathlib`, and `subprocess` for local files, exports, databases, and existing scripts
- `pyproject.toml` console script or a small executable wrapper for the installed command
- `uv` or a virtualenv only when dependencies are actually needed

Add a `Makefile` target such as `make install-local` that installs the command on PATH and document whether it depends on `uv`, a virtualenv, or only system Python.

## Companion Skill

After the CLI works, create or update a small skill for it. Use `$skill-creator` when it is available. Use `$CODEX_HOME/skills/<tool-name>/SKILL.md` for a personal companion skill unless the user names a repo-local `.codex/skills/...` path or another skill repo.

Write the companion skill in the order a future Codex thread should use the CLI, not as a tour of every feature. Explain:

- How to verify the installed command exists.
- Which command to run first.
# REDACTED: sensitive-looking memory line
- Which discovery command finds the common ID.
- The safe read path.
- The intended draft/write path.
- The raw escape hatch.
- What not to do without explicit user approval.
- Three copy-pasteable command examples.

Keep API reference details in the CLI docs or a skill reference file. Keep the skill focused on ordering, safety, and examples future Codex threads should actually run.

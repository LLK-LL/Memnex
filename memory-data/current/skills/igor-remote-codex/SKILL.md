---
name: igor-remote-codex
description: Use whenever the user mentions `伊戈尔`, Igor, the remote server Codex CLI, SSH alias `igor`/`codex-server`, host `desktop-hhrefkb`, or asks to check, configure, update, operate, troubleshoot, or recall information about that remote Codex CLI. This skill disambiguates Igor from Hermes profiles, OpenClaw profiles, and the local Codex agent.
---

# Igor Remote Codex

## Identity

- Treat `伊戈尔` and Igor as the remote server Codex CLI agent.
- Do not interpret `伊戈尔` as a Hermes profile, OpenClaw profile, local Codex instance, or generic AI model unless the user explicitly says so.
- Default target:
  - SSH aliases: `igor` and `codex-server`
  - Host: `desktop-hhrefkb`
  - Tailscale IP: `100.125.252.98`
  - Remote user: `codex`
  - Default project path: `C:\codex-work\codex-CLI`
  - Remote config path: `C:\Users\codex.DESKTOP-HHREFKB\.codex\config.toml`
  - Remote instruction file: `C:\codex-work\codex-CLI\AGENTS.md`

## Current Known Configuration

- Current model: `gpt-5.5`
- Current review model: `gpt-5.5`
- Model provider: `custom`
- Reasoning effort: `medium`
- Provider base URL: `https://api.0029.org`
- Wire API: `responses`
- OpenAI auth requirement: `requires_openai_auth = true`
- Remote `AGENTS.md` was reduced to: `Your name is 伊戈尔.`

Historical note: an older configuration used `gpt-5.4` with `https://api.zygtoken.com/v1`. Treat that as superseded unless live remote config proves otherwise.

## Workflow

1. First recall Igor-specific memory before searching unrelated records:
   `伊戈尔 remote server Codex CLI SSH alias default model config`
2. If the user asks a factual question and memory is enough, answer from this skill plus memory.
3. If the user asks to inspect or change Igor, connect through `ssh igor` or `ssh codex-server`.
4. Before changing configuration, read the current remote files and create a timestamped backup.
5. Never print, store, or repeat API keys, auth tokens, or copied experimental secrets.
6. After any configuration change, run a lightweight verification such as `codex doctor --summary` on the remote server.
7. Summarize only the target, changed files, backup paths, verification result, and remaining risks.

## Useful Remote Commands

Use PowerShell-friendly quoting from the local Windows host.

```powershell
ssh igor "hostname"
ssh igor "cd C:\codex-work\codex-CLI; codex --version"
ssh igor "codex doctor --summary"
ssh igor "powershell -NoProfile -Command Get-Content -LiteralPath 'C:\Users\codex.DESKTOP-HHREFKB\.codex\config.toml'"
ssh igor "powershell -NoProfile -Command Get-Content -LiteralPath 'C:\codex-work\codex-CLI\AGENTS.md'"
```

## Guardrails

- Prefer `ssh igor` first; use `ssh codex-server` only if the first alias fails.
- Treat destructive actions, credential rotation, config replacement, service restarts, and file deletion as requiring explicit user intent.
- When command output is long or noisy, summarize it. Preserve exact stack traces or diagnostics when debugging.
- If live remote config conflicts with this skill, trust the live config for the immediate task and save an updated memory record after resolving the discrepancy.

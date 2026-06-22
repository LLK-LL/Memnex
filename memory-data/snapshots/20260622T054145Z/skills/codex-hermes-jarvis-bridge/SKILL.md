---
name: codex-hermes-jarvis-bridge
description: Configure, repair, verify, or use the Codex-to-Hermes Jarvis bridge, including visible bidirectional Codex/Jarvis duplex discussions. Use when the user asks Codex and Jarvis to talk, discuss, coordinate, collaborate, or make their exchange visible in Hermes WebUI.
---

# Codex Hermes Jarvis Bridge

Use this workflow to connect Codex directly to the Hermes `jarvis` profile while keeping the conversation visible in Hermes WebUI.

## Target State

- Codex MCP server: `codex_jarvis`
- MCP tools exposed to Codex: `ask_jarvis`, `discuss_with_jarvis`, `list_jarvis_discussions`, `read_jarvis_discussion`, `sync_jarvis_discussion`
- Bridge files:
  - `D:\Hermes\codex-bridge\jarvis_mcp.py`
  - `D:\Hermes\codex-bridge\run_jarvis_job.ps1`
  - `D:\Hermes\codex-bridge\codex_inbox.py`
  - `D:\Hermes\codex-bridge\codex_inbox_mcp.py`
  - `D:\Hermes\codex-bridge\codex_duplex.py`
  - `D:\Hermes\codex-bridge\codex_duplex_mcp.py`
- Codex config: `C:\Users\Administrator\.codex\config.toml`
- Hermes profile: `jarvis`
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
- Reverse inbox store:
  - `D:\Hermes\codex-bridge\inbox\pending.jsonl`
  - `D:\Hermes\codex-bridge\inbox\claims.jsonl`
  - `D:\Hermes\codex-bridge\inbox\results.jsonl`
- Duplex discussion store:
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line

## Correct Architecture

Do not rely on `hermes mcp serve` alone if the requirement is WebUI sidebar visibility.

Forward flow:

```text
Codex MCP tool ask_jarvis
  -> D:\Hermes\codex-bridge\jarvis_mcp.py
  -> background PowerShell runner
  -> hermes -p jarvis chat
# REDACTED: sensitive-looking memory line
  -> sync WebUI sidecar JSON and _index.json
```

Rules for the forward flow:

# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line

Reverse flow:

```text
Hermes WebUI Jarvis
  -> MCP tool send_to_codex
  -> D:\Hermes\codex-bridge\inbox\pending.jsonl
  -> Codex MCP tool check_codex_inbox
  -> Codex MCP tool write_codex_result
  -> D:\Hermes\codex-bridge\inbox\results.jsonl
  -> Jarvis MCP tool read_codex_results
```

Rules for the reverse flow:

- Use the JSONL inbox for Jarvis-to-Codex messages; do not try to push directly into the Codex UI.
- Jarvis sends only a concise task, priority, and optional evidence file paths.
- Codex reads with `check_codex_inbox`, claims the task, acts, then writes a concise result with `write_codex_result`.
- Jarvis reads Codex replies with `read_codex_results`.
- Long evidence, logs, transcripts, or patches must be written to files and passed as paths.

Duplex discussion flow:

```text
Codex tool discuss_with_jarvis
  or Jarvis tool start_codex_duplex
  -> D:\Hermes\codex-bridge\codex_duplex.py coordinator
# REDACTED: sensitive-looking memory line
  -> bounded running summary plus transcript files
  -> compact result returned to the initiating side
```

Rules for the duplex flow:

- Use duplex for actual back-and-forth discussion, deliberation, brainstorming, or joint decisions.
- Do not use inbox polling for real-time discussion; inbox is only for one-way task delivery.
- Default to `rounds=2` and keep `max_turn_chars` around 900.
- Each turn receives only `topic`, `constraints`, `running_summary`, and the last peer message.
- Full details must go in files and be referenced by path; do not paste large evidence into the turn prompt.
- The coordinator may be started from Codex via `discuss_with_jarvis(...)` or from Jarvis via `start_codex_duplex(...)`.
# REDACTED: sensitive-looking memory line
- Codex Desktop list visibility requires an explicit Codex record thread; do not create extra Codex threads silently.

# REDACTED: sensitive-looking memory line

- `ask_jarvis` defaults to `return_mode="brief"`.
- Brief mode returns only the final concise result to Codex and caps Codex-visible text.
- Use `return_mode="detailed"` only for key evidence, file paths, or patch summaries.
- Use `return_mode="full"` only when the user explicitly asks for raw/full Jarvis output.
- Preserve the user's message exactly when sending it to Jarvis; do not prepend bridge policy text such as `Codex bridge:` or `User message:`. Enforce concise Codex-visible output through `return_mode`, output compaction, tool metadata, or profile-level instructions instead.
- Default `toolsets` is `hermes-cli`; pass `toolsets=""` for pure chat/reasoning when Hermes tools are not needed.
- Reverse inbox messages and Codex result summaries should stay under about 1200 characters.
- Duplex discussion turns should stay under about 900 characters by default; use 1-3 rounds unless the user explicitly asks for deeper debate.

## Codex Config

Ensure this block exists in `C:\Users\Administrator\.codex\config.toml`:

```toml
[mcp_servers.codex_jarvis]
enabled = true
command = 'D:\Hermes\hermes-agent\venv\Scripts\python.exe'
args = ['D:\Hermes\codex-bridge\jarvis_mcp.py']
startup_timeout_sec = 120
tool_timeout_sec = 900

[mcp_servers.codex_jarvis.env]
HERMES_HOME = 'D:\Hermes'
PYTHONIOENCODING = "utf-8"
PYTHONUTF8 = "1"
```

## Bridge Requirements

`jarvis_mcp.py` must:

- Expose a FastMCP tool named `ask_jarvis(message: str, toolsets: Optional[str] = None, return_mode: Optional[str] = None)`.
- Also expose `check_codex_inbox(limit: int = 3, claim: bool = True)` and `write_codex_result(id: str, summary: str, paths: Optional[list[str]] = None, status: str = "done")`.
# REDACTED: sensitive-looking memory line
- Use `HERMES_HOME=D:\Hermes`.
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
- Launch Hermes through `run_jarvis_job.ps1` as a background job.
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
- Default `return_mode` to `brief`, returning only Jarvis's concise final result to Codex.
# REDACTED: sensitive-looking memory line
- Use `return_mode="detailed"` only when Codex needs key evidence or a short patch summary.
- Use `return_mode="full"` only when the user explicitly needs raw/full Jarvis output.
- Default `toolsets` to `hermes-cli`; pass `toolsets=""` for pure chat/reasoning when Hermes tools are not needed.
- Never return Jarvis's full reasoning, long logs, or full tool output to Codex by default.
# REDACTED: sensitive-looking memory line

`codex_inbox.py` must:

- Store reverse messages as append-only JSONL under `D:\Hermes\codex-bridge\inbox`.
- Cap queued messages and Codex result summaries at about 1200 characters.
- Store long evidence as file paths, not inline logs.
- Use `pending.jsonl`, `claims.jsonl`, and `results.jsonl` so interrupted runs do not corrupt a shared state file.

`codex_inbox_mcp.py` must:

# REDACTED: sensitive-looking memory line
- Return only queued id, concise message, evidence paths, or concise results.
- Be configured in `D:\Hermes\profiles\jarvis\config.yaml` under `mcp_servers.codex-inbox`.

`codex_duplex.py` must:

- Coordinate synchronous turn-based discussion between Codex CLI and Jarvis CLI.
- Run Codex with `codex exec` in ephemeral, read-only, no-approval mode.
- Run Jarvis with `hermes -p jarvis chat -q <prompt> --quiet --max-turns 1`.
- Pass only compact discussion state per turn.
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line

`codex_duplex_mcp.py` must:

# REDACTED: sensitive-looking memory line
- Be configured in `D:\Hermes\profiles\jarvis\config.yaml` under `mcp_servers.codex-duplex`.

Jarvis profile must include a concise `codex-inbox` skill:

- Trigger when the user asks Jarvis to send, forward, hand off, or ask Codex.
- Convert the request into a concise task for Codex.
- Do not send reasoning, long logs, or full tool output.
- Use `send_to_codex`; use `read_codex_results` only when the user asks for Codex's reply.

Jarvis profile must include a concise `codex-duplex` skill:

- Trigger when the user asks Jarvis to discuss, deliberate, brainstorm, coordinate, or decide with Codex.
- Prefer `start_codex_duplex(topic, rounds=2, starter="jarvis", constraints="...")`.
- Report the compact summary and transcript path to the user.
- Use `codex-inbox` instead when the user only wants to send a one-way task.

Jarvis profile config must include:

```yaml
mcp_servers:
  codex-inbox:
    command: D:\Hermes\hermes-agent\venv\Scripts\python.exe
    args:
      - D:\Hermes\codex-bridge\codex_inbox_mcp.py
    env:
      HERMES_HOME: D:\Hermes
      PYTHONIOENCODING: utf-8
      PYTHONUTF8: '1'
    enabled: true
  codex-duplex:
    command: D:\Hermes\hermes-agent\venv\Scripts\python.exe
    args:
      - D:\Hermes\codex-bridge\codex_duplex_mcp.py
    env:
      HERMES_HOME: D:\Hermes
      PYTHONIOENCODING: utf-8
      PYTHONUTF8: '1'
    enabled: true
```

`run_jarvis_job.ps1` must:

- Set `$env:HERMES_HOME = "D:\Hermes"`.
- Read UTF-8 prompt text from the job directory.
- Run:

```powershell
& "D:\Hermes\hermes-agent\venv\Scripts\hermes.EXE" -p jarvis chat -q <prompt> --toolsets <toolsets> --quiet --max-turns 1
```

# REDACTED: sensitive-looking memory line
- Omit `--toolsets` when the Python wrapper passes an empty `Toolsets` value.
- Write `stdout.txt`, `stderr.txt`, and `status.json` into the job directory.

## Verification

Run a forward MCP-level smoke test:

```powershell
@'
import asyncio
# REDACTED: sensitive-looking memory line
from mcp.client.stdio import stdio_client

async def main():
    params = StdioServerParameters(
        command=r"D:\Hermes\hermes-agent\venv\Scripts\python.exe",
        args=[r"D:\Hermes\codex-bridge\jarvis_mcp.py"],
        env={"HERMES_HOME": r"D:\Hermes", "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"},
    )
    async with stdio_client(params) as (read, write):
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
            print([tool.name for tool in tools.tools])
# REDACTED: sensitive-looking memory line
                "message": "Reply BRIDGE_OK only.",
                "return_mode": "brief",
                "toolsets": ""
            })
            for item in result.content:
                print(getattr(item, "text", item))

asyncio.run(main())
'@ | & 'D:\Hermes\hermes-agent\venv\Scripts\python.exe' -
```

Pass criteria:

- Tool list contains `ask_jarvis`, `check_codex_inbox`, and `write_codex_result`.
- Tool response includes the requested reply.
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
  - `profile`: `jarvis`
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line

Run reverse checks:

```powershell
& 'D:\Hermes\hermes-agent\venv\Scripts\hermes.EXE' -p jarvis mcp test codex-inbox
```

Pass criteria:

- `codex-inbox` connects.
- Tools discovered include `send_to_codex` and `read_codex_results`.
- A Jarvis call with `--toolsets codex-inbox` can queue a short task.
- `check_codex_inbox(limit=3, claim=True)` returns that queued task to Codex.
- `write_codex_result(...)` writes a concise result to `D:\Hermes\codex-bridge\inbox\results.jsonl`.
- `read_codex_results()` returns the Codex result to Jarvis.

## Operational Notes

# REDACTED: sensitive-looking memory line
- Avoid PowerShell heredoc literals for Chinese smoke tests; use WebUI/MCP JSON or UTF-8 files to avoid code-page replacement with `?`.
- Keep this skill concise; do not add trial-and-error history.

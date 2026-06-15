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
- WebUI-visible session title prefix: `codex-jarvis-<codex-session>`
- WebUI session store:
  - `D:\Hermes\webui\sessions\_index.json`
  - `D:\Hermes\webui\sessions\<session_id>.json`
- Reverse inbox store:
  - `D:\Hermes\codex-bridge\inbox\pending.jsonl`
  - `D:\Hermes\codex-bridge\inbox\claims.jsonl`
  - `D:\Hermes\codex-bridge\inbox\results.jsonl`
- Duplex discussion store:
  - `D:\Hermes\codex-bridge\duplex\<session_id>\session.json`
  - `D:\Hermes\codex-bridge\duplex\<session_id>\transcript.md`
  - `D:\Hermes\codex-bridge\duplex\<session_id>\events.jsonl`

## Correct Architecture

Do not rely on `hermes mcp serve` alone if the requirement is WebUI sidebar visibility.

Forward flow:

```text
Codex MCP tool ask_jarvis
  -> D:\Hermes\codex-bridge\jarvis_mcp.py
  -> background PowerShell runner
  -> hermes -p jarvis chat
  -> Jarvis state.db session title codex-jarvis-<codex-session>
  -> sync WebUI sidecar JSON and _index.json
```

Rules for the forward flow:

- Each new Codex conversation must map to a separate Hermes/Jarvis session.
- The Hermes session title must start with `codex-jarvis-`.
- The bridge should use `CODEX_SESSION_ID`, `CODEX_THREAD_ID`, or `CODEX_CONVERSATION_ID` when present.
- If no Codex session env var exists, use bridge process start time plus PID.
- Do not put every Codex/Jarvis exchange into one fixed `codex-jarvis` session.
- Keep the actual Jarvis conversation on Hermes's native `chat` path so Hermes memory, session storage, curator, and skill-promotion rules still apply.

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
  -> alternating low-token Codex CLI and Jarvis CLI turns
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
- Every completed duplex session must sync a read-only Hermes WebUI session titled `codex-duplex-<session>` so the user can inspect the actual Codex and Jarvis turns in the Jarvis conversation list.
- Codex Desktop list visibility requires an explicit Codex record thread; do not create extra Codex threads silently.

## Token Policy

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
- Also expose duplex tools: `discuss_with_jarvis(...)`, `list_jarvis_discussions(limit=5)`, and `read_jarvis_discussion(session_id="")`.
- Use `HERMES_HOME=D:\Hermes`.
- Create one Hermes session title per Codex conversation, using prefix `codex-jarvis-`.
- Prefer `CODEX_SESSION_ID`, `CODEX_THREAD_ID`, or `CODEX_CONVERSATION_ID` when present; otherwise use bridge process start time plus PID.
- Continue that per-Codex Hermes session title when it exists.
- Create and rename the first Jarvis session for that Codex conversation when it does not exist.
- Launch Hermes through `run_jarvis_job.ps1` as a background job.
- Read the latest matching per-Codex Jarvis session from `D:\Hermes\profiles\jarvis\state.db`.
- Write/update WebUI sidecar and index files under `D:\Hermes\webui\sessions`.
- Keep calls on Hermes's normal `chat` path so Jarvis profile memory/session-end hooks, memory storage, curator, and skill-promotion rules can run normally.
- Default `return_mode` to `brief`, returning only Jarvis's concise final result to Codex.
- Keep full session content available in Hermes WebUI sidecar/index sync.
- Use `return_mode="detailed"` only when Codex needs key evidence or a short patch summary.
- Use `return_mode="full"` only when the user explicitly needs raw/full Jarvis output.
- Default `toolsets` to `hermes-cli`; pass `toolsets=""` for pure chat/reasoning when Hermes tools are not needed.
- Never return Jarvis's full reasoning, long logs, or full tool output to Codex by default.
- Directly update the new Hermes session title in `state.db` after the first native `hermes chat` call creates the session; avoid shelling out to `hermes sessions rename` because that path can hang in this bridge.

`codex_inbox.py` must:

- Store reverse messages as append-only JSONL under `D:\Hermes\codex-bridge\inbox`.
- Cap queued messages and Codex result summaries at about 1200 characters.
- Store long evidence as file paths, not inline logs.
- Use `pending.jsonl`, `claims.jsonl`, and `results.jsonl` so interrupted runs do not corrupt a shared state file.

`codex_inbox_mcp.py` must:

- Expose Jarvis-side MCP tools `send_to_codex(message: str, priority: str = "normal", evidence_paths: Optional[list[str]] = None, hermes_session: str = "")` and `read_codex_results(limit: int = 10)`.
- Return only queued id, concise message, evidence paths, or concise results.
- Be configured in `D:\Hermes\profiles\jarvis\config.yaml` under `mcp_servers.codex-inbox`.

`codex_duplex.py` must:

- Coordinate synchronous turn-based discussion between Codex CLI and Jarvis CLI.
- Run Codex with `codex exec` in ephemeral, read-only, no-approval mode.
- Run Jarvis with `hermes -p jarvis chat -q <prompt> --quiet --max-turns 1`.
- Pass only compact discussion state per turn.
- Store `session.json`, `transcript.md`, and `events.jsonl` under `D:\Hermes\codex-bridge\duplex`.
- Sync completed sessions into `D:\Hermes\webui\sessions\_index.json` and a sidecar JSON titled `codex-duplex-<session>` for Jarvis WebUI visibility.
- Return a compact result containing session id, status, summary, and file paths.

`codex_duplex_mcp.py` must:

- Expose Jarvis-side MCP tools `start_codex_duplex(...)`, `list_codex_duplex(limit=5)`, `read_codex_duplex(session_id="")`, and `sync_codex_duplex(session_id="")`.
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

- Add `--continue <SessionName>` when the Python wrapper passes `ContinueSession=1`.
- Omit `--toolsets` when the Python wrapper passes an empty `Toolsets` value.
- Write `stdout.txt`, `stderr.txt`, and `status.json` into the job directory.

## Verification

Run a forward MCP-level smoke test:

```powershell
@'
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    params = StdioServerParameters(
        command=r"D:\Hermes\hermes-agent\venv\Scripts\python.exe",
        args=[r"D:\Hermes\codex-bridge\jarvis_mcp.py"],
        env={"HERMES_HOME": r"D:\Hermes", "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"},
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print([tool.name for tool in tools.tools])
            result = await session.call_tool("ask_jarvis", {
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
- `hermes -p jarvis sessions list` shows a session whose title starts with `codex-jarvis-`.
- `D:\Hermes\webui\sessions\_index.json` contains an entry with:
  - `title`: `codex-jarvis-<codex-session>`
  - `profile`: `jarvis`
- `D:\Hermes\webui\sessions\<session_id>.json` exists for the same session.
- After refreshing Hermes WebUI, the sidebar shows the matching `codex-jarvis-<codex-session>` session.

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

- Existing Hermes WebUI sessions may need refresh or `/reload-mcp` after adding `codex-inbox`.
- Avoid PowerShell heredoc literals for Chinese smoke tests; use WebUI/MCP JSON or UTF-8 files to avoid code-page replacement with `?`.
- Keep this skill concise; do not add trial-and-error history.

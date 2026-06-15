---
name: hermes-provider-config
description: Configure Hermes agent/profile provider URL and API key safely. Use when the user asks Codex to change Hermes, Hermes agents, 大牛马, 中牛马, or other Hermes profiles to a provided URL/API/API key, copy the working Codex API credential into Hermes, diagnose why Hermes cannot wake an agent while Codex works, or verify Hermes profile wake-up after provider changes.
---

# Hermes Provider Config

Use this short path for Hermes profile URL/API changes. Keep model names unchanged unless the user explicitly asks to change them.

## Low-Token Mode

If the user says lowest token, no tests, or follow the already-successful flow, do only the essential steps:

1. Read current Codex `config.toml` and `auth.json`.
2. Update the target Hermes profile top `model:` block.
3. Print one redacted consistency table.
4. Do not run Hermes smoke tests unless the user asks for verification or the config check shows a problem.

## Correct Flow

1. Identify target profile files under `D:\Hermes\profiles\<profile>\config.yaml`.
   - 大牛马: `da-niuma`
   - 中牛马: `zhong-niuma`

2. Read each target `config.yaml` and inspect only the top `model:` block first.
   - Preserve `model.default`.
   - Set `model.provider: custom` for OpenAI-compatible custom endpoints.
   - Set `model.base_url` exactly to the user-provided URL.
   - If matching Codex behavior, set `model.api_mode: codex_responses`.

3. Choose the API key source.
   - If the user provides a key or screenshot-derived key and it fails with 401, do not keep retrying variants.
   - If the user says Codex works but Hermes does not, compare against Codex local config:
     - `C:\Users\Administrator\.codex\config.toml`
     - `C:\Users\Administrator\.codex\auth.json`
   - Copy `OPENAI_API_KEY` from Codex auth into `model.api_key` only when this is the intended working credential.
   - Never print the key in chat, logs, diffs, or command output.

4. Edit only the intended profile files.
   - Use a scoped edit of the top `model:` block.
   - Do not accidentally edit later `auxiliary.*`, `delegation.*`, or unrelated `api_mode` fields.
   - For full profile configs, restore `delegation.api_mode` to `''` unless the user requested delegation changes.

5. Verify with a secret-safe config summary.
   - Print profile, model, base URL, api mode, and whether the key matches the intended source.
   - Redact any `api_key` value as `<redacted>`.

6. Run one smoke test per changed profile unless the user requested low-token/no-test mode:

```powershell
& D:\Hermes\hermes-agent\venv\Scripts\hermes.EXE --profile <profile> -z "只回复 OK" --toolsets hermes-cli
```

Success means the command returns `OK`.

## Fast Diagnostics

- `Unknown provider 'custom:...'`: use `provider: custom`.
- HTTP 401 / Unauthorized: wrong API key for that endpoint; use the working credential source rather than changing model names.
- Codex works but Hermes fails: Codex may be using `wire_api = "responses"` plus a different `OPENAI_API_KEY`; mirror that with `model.api_mode: codex_responses` and the same working key.
- HTTP 500/502 upstream errors: provider-side or upstream route instability; retry once after config is correct, then report it as provider-side if it persists.

## Logging Check

Check only relevant current logs:

```powershell
Select-String -Path D:\Hermes\profiles\<profile>\logs\agent.log,D:\Hermes\profiles\<profile>\logs\errors.log -Pattern '401|Unauthorized|500|502|Unknown provider|no final response|api.zygtoken|api.fjzyg' -CaseSensitive:$false
```

Avoid broad recursive searches from `D:\Hermes`; backup and cache directories are large and slow.

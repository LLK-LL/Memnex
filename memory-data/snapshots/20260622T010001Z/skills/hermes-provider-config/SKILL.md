---
name: hermes-provider-config
# REDACTED: sensitive-looking memory line
---

# Hermes Provider Config

Use this short path for Hermes profile URL/API changes. Keep model names unchanged unless the user explicitly asks to change them.

# REDACTED: sensitive-looking memory line

# REDACTED: sensitive-looking memory line

# REDACTED: sensitive-looking memory line
2. Update the target Hermes profile top `model:` block.
3. Print one redacted consistency table.
4. Do not run Hermes smoke tests unless the user asks for verification or the config check shows a problem.

## Correct Flow

1. Identify target profile files under `D:\Hermes\profiles\<profile>\config.yaml`.
   - 澶х墰椹? `da-niuma`
   - 涓墰椹? `zhong-niuma`

2. Read each target `config.yaml` and inspect only the top `model:` block first.
   - Preserve `model.default`.
   - Set `model.provider: custom` for OpenAI-compatible custom endpoints.
   - Set `model.base_url` exactly to the user-provided URL.
   - If matching Codex behavior, set `model.api_mode: codex_responses`.

3. Choose the API key source.
   - If the user provides a key or screenshot-derived key and it fails with 401, do not keep retrying variants.
   - If the user says Codex works but Hermes does not, compare against Codex local config:
     - `C:\Users\Administrator\.codex\config.toml`
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
   - Never print the key in chat, logs, diffs, or command output.

4. Edit only the intended profile files.
   - Use a scoped edit of the top `model:` block.
   - Do not accidentally edit later `auxiliary.*`, `delegation.*`, or unrelated `api_mode` fields.
   - For full profile configs, restore `delegation.api_mode` to `''` unless the user requested delegation changes.

# REDACTED: sensitive-looking memory line
   - Print profile, model, base URL, api mode, and whether the key matches the intended source.
# REDACTED: sensitive-looking memory line

# REDACTED: sensitive-looking memory line

```powershell
& D:\Hermes\hermes-agent\venv\Scripts\hermes.EXE --profile <profile> -z "鍙洖澶?OK" --toolsets hermes-cli
```

Success means the command returns `OK`.

## Fast Diagnostics

- `Unknown provider 'custom:...'`: use `provider: custom`.
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
- HTTP 500/502 upstream errors: provider-side or upstream route instability; retry once after config is correct, then report it as provider-side if it persists.

## Logging Check

Check only relevant current logs:

```powershell
# REDACTED: sensitive-looking memory line
```

Avoid broad recursive searches from `D:\Hermes`; backup and cache directories are large and slow.

# Banana Shared Workflow Reference

## Purpose

Use this shared reference before any Banana-native image or PPT deliverable. It covers local invocation, backend health, model settings, common failure recovery, and evidence that must be preserved for final reporting.

This file intentionally does not define the image or PPT generation steps. After preflight, continue with `image-workflow.md`, `ppt-workflow.md`, or both.

## Local Invocation

On this machine, prefer running Banana CLI from the local Banana Slides repository:

```powershell
Set-Location "C:/Users/Administrator/Documents/Codex/2026-06-09/github/work/banana-slides"
$env:PYTHONIOENCODING = "utf-8"
uv run banana-cli <command>
```

Use plain `banana-cli` only after confirming it is available on PATH.

## Backend Preflight

Run these checks before formal generation:

```powershell
Set-Location "C:/Users/Administrator/Documents/Codex/2026-06-09/github/work/banana-slides"
$env:PYTHONIOENCODING = "utf-8"
curl.exe -sf http://localhost:5000/health
uv run banana-cli settings get
uv run banana-cli settings test --name image-model
uv run banana-cli settings test-status --task-id <task_id>
```

Treat image generation as available only when the image-model test reaches `status: COMPLETED` and reports an `image_size`.

Settings tests and generation tasks use different status paths:

- Settings image-model test: `uv run banana-cli settings test-status --task-id <settings_task_id>`
- Image/PPT generation task: `uv run banana-cli tasks wait --project-id <project_id> --task-id <generation_task_id>`
- Generation task inspection: `uv run banana-cli tasks status --project-id <project_id> --task-id <generation_task_id>`

## Verified Image API Configuration

For the local OpenAI-compatible Banana setup, do not assume the text model is also the image model. Use this split unless the user explicitly provides a different working image configuration:

```text
text_model = gpt-5.5
image_caption_model = gpt-5.5
image_model = gpt-image-2
image_model_source = openai
image_api_base_url = same base URL as the user's configured custom provider
# REDACTED: sensitive-looking memory line
openai_image_api_protocol = images
image_resolution = 1K
image_aspect_ratio = 16:9
max_image_workers = 1
```

Why: Banana's OpenAI image provider routes `gpt-image-*` models through the native `images.generate` / `images.edit` path when `openai_image_api_protocol` is `images`, or when protocol is `auto` and the image model name is `gpt-image-2`. Using `gpt-5.5` with `responses` can test the wrong path and may fail even when the native image API works.

## API And Settings Locations

For Banana API/base/provider changes, check and update these locations first:

1. Repo env file:

   ```text
   C:/Users/Administrator/Documents/Codex/2026-06-09/github/work/banana-slides/.env
   ```

2. Persistent runtime settings:

   ```text
   uv run banana-cli settings get
   uv run banana-cli settings update
   ```

3. Backend defaults and load chain:

   ```text
   backend/config.py
   backend/app.py
   backend/controllers/settings_controller.py
   backend/models/settings.py
   ```

4. Frontend settings form:

   ```text
   frontend/src/pages/Settings.tsx
   ```

Always update both `.env` and persistent Settings when changing API/base/provider values because database settings can override env at runtime.

Do not expose API keys in replies.

## Common Failure Recovery

- **CLI not found:** run `uv run banana-cli` from `C:/Users/Administrator/Documents/Codex/2026-06-09/github/work/banana-slides`.
- **Backend unreachable:** start the local Banana backend, then rerun `curl.exe -sf http://localhost:5000/health`.
- **Windows Chinese encoding:** set `$env:PYTHONIOENCODING = "utf-8"` before CLI commands that handle Chinese text.
- **Image settings mismatch:** update both `.env` and persistent settings. Database settings can override environment values at runtime.
- **Wrong image protocol:** use `gpt-image-2` with `openai_image_api_protocol = images` unless a settings test proves another image configuration works.
- **Missing template/style:** set `template_style` or upload/select a template before generating images if Banana image generation fails due to absent visual style.
- **Failed Banana task:** inspect the task status, project state, page descriptions, image model settings, and generated page status before retrying.
# REDACTED: sensitive-looking memory line
- **Unrelated skill drift:** do not read or invoke non-Banana generation skills for a formal Banana deliverable.
- **Command probing drift:** check the documented shortest path first; inspect extra CLI groups only when that path fails for a concrete reason.
- **Encoding retry loop:** for long Chinese descriptions, use a UTF-8 file plus the local API helper instead of repeated PowerShell argument escaping.

## Evidence To Preserve

For image deliverables, record:

- settings image-model test status and image size,
- project ID,
- generated image task ID,
- requested page IDs,
- `projects get` evidence showing `generated_image_url` and `status = COMPLETED`,
- exported image path,
- exported image count.

For PPT deliverables, record:

- settings image-model test status and image size,
- project ID,
- expected page count,
- `GENERATE_IMAGES` task status,
- completed and failed counts,
- exported PPTX path,
- exported slide count.

Use PowerShell to verify output files:

```powershell
Test-Path "<absolute-output-path>.pptx"
Test-Path "<absolute-output-path>.zip"
```

For PPTX slide count, use a local inspection utility when available. If no utility is available, open the PPTX as a zip and count `ppt/slides/slide*.xml`.

On 2026-06-12, a compliant 8-slide Banana deck succeeded with:

```text
text_model = gpt-5.5
image_model = gpt-image-2
image_caption_model = gpt-5.5
image_api_protocol = images
image_resolution = 1K
image_aspect_ratio = 16:9
max_image_workers = 1
```

Validation evidence:

```text
settings image-model test: COMPLETED, image_size = 1280x720
GENERATE_IMAGES task: COMPLETED, completed = 8, failed = 0, total = 8
exported PPTX: 8 slides, 8 media files
```

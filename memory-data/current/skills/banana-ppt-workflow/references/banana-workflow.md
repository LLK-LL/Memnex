# Banana Workflow Reference

## Current Hard Rule

When the user explicitly asks to use `banana` for PPT or single-page generation, only use a verified Banana-native workflow for the formal deliverable.

Do not use:

- local fallback image generation,
- manual page reconstruction,
- non-Banana drawing or layout,
- alternative model pipelines,
- generic PPT generation as the formal deliverable.

If image generation or export fails, continue debugging Banana's model, settings, template, description, task status, API, or export chain until Banana can export the PPT/images, or report the exact blocker.

## Verified Workflows

### Full Deck

Use the verified full-deck flow:

```text
outline project
-> workflows outline refine
-> template-style
-> template image
-> workflows full --skip-outline
-> export pptx
```

Avoid unverified variants when this verified path fits the task.

### Single Page

Use the verified single-page flow:

```text
descriptions project
-> template image
-> manual pages create(description-json)
-> pages gen-image
-> export pptx/images
```

Use this when the user asks for one page, one visual page, or a page-level PPT/image deliverable.

## Strict Page-Count Workflow

For strict page-count or structure-sensitive decks:

1. Verify backend health and CLI settings first.
2. On Windows Chinese runs, set:

   ```powershell
   $env:PYTHONIOENCODING = "utf-8"
   ```

3. Prefer idea-based project creation with a concise idea prompt plus extra requirements. Do not dump a long outline into the initial create step.
4. Use a content-first staged flow:
   - generate outline,
   - refine outline until page count and structure are acceptable,
   - generate/refine descriptions,
   - verify structure,
   - generate images only after content lock.
5. If using `workflows full` for convenience during validation, use `--skip-images`.
6. Treat `--pages` as a hint, not a hard guarantee.
7. If page count overshoots:
   - refine the outline with a strict compression instruction,
   - rerun content generation with `--skip-outline --skip-images`,
   - generate images only after the final content structure is locked.
8. Export only after the final project matches the target page count.

## Verified Image API Configuration

For the local OpenAI-compatible Banana setup, do not assume the text model is also the image model.

Use this split unless the user explicitly provides a different working image configuration:

```text
text_model = gpt-5.5
image_caption_model = gpt-5.5
image_model = gpt-image-2
image_model_source = openai
image_api_base_url = same base URL as the user's configured custom provider
image_api_key = same bearer token/key as the user's configured custom provider
openai_image_api_protocol = images
image_resolution = 1K for initial validation
```

Why: Banana's OpenAI image provider routes `gpt-image-*` models through the native `images.generate` / `images.edit` path when `openai_image_api_protocol` is `images`, or when protocol is `auto` and the image model name is `gpt-image-2`. Using `gpt-5.5` with `responses` can test the wrong path and may fail even when the native image API works.

Before generating a formal deck, run:

```powershell
$env:PYTHONIOENCODING = "utf-8"
banana-cli settings test --name image-model
banana-cli settings test-status --task-id <task_id>
```

Treat image generation as available only when the settings test returns `status: COMPLETED` and an `image_size`, for example `1280x720` for 16:9 1K.

## Formal Banana PPT Acceptance Standard

A PPT requested with `banana` is compliant only if all of the following are true:

- The deck uses a fresh Banana project or a project whose pages were not populated with local fallback images.
- Page count is verified before image generation.
- Banana's formal image task succeeds:

  ```text
  task_type = GENERATE_IMAGES
  status = COMPLETED
  progress.completed = expected_page_count
  progress.failed = 0
  ```

- Every exported page has `generated_image_url` and page `status = COMPLETED` in `banana-cli projects get`.
- The PPTX is exported with `banana-cli exports pptx`.
- The exported PPTX contains the expected slide count and matching media count.

Do not treat these as compliant:

- local SVG/rendered images registered into Banana pages,
- manually reconstructed PPTX files,
- Banana exports from projects whose image task ended with failed pages,
- generic PPTX generation outside Banana,
- image placeholders or pages without `generated_image_url`.

## Configuration And API Locations

For Banana API/base/provider changes, check and update these locations first:

1. Repo env file:

   ```text
   C:/Users/Administrator/Documents/Codex/2026-06-09/github/work/banana-slides/.env
   ```

2. Persistent runtime settings:

   ```text
   banana-cli settings get
   banana-cli settings update
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

## Supplementary Experience

### Outline Projects Need Refinement

When using Banana CLI with `creation_type=outline`, the backend may still require running:

```text
workflows outline --refine ...
```

before descriptions can be generated.

### Template Style Or Template Image May Be Required

Image generation can fail unless `template_style` or a template image is set.

Reliable outline-based flow:

```text
create outline project
-> workflows outline with a style-preserving refine prompt
-> update project with --template-style
-> optionally templates upload using a prior slide preview
-> workflows full --skip-outline --skip-descriptions
-> export PPTX
```

### Local Banana Slides Adaptation

The local Banana Slides setup was adapted for a yue-yun Responses API that can return SVG text instead of `image_generation_call` results.

Relevant implementation facts:

- `backend/services/ai_providers/image/openai_provider.py` contains a Responses protocol branch.
- `settings_controller.py` allows `openai_image_api_protocol='responses'`.
- `scripts/render-svg.mjs` uses frontend Playwright Chromium to render returned SVG into PNG/PIL.
- A fallback SVG generator exists when the model returns textual design instructions.
- `scripts/start-codex-local.ps1` syncs Codex text config and supports `BANANA_IMAGE_API_BASE` / `BANANA_IMAGE_API_KEY` overrides for the image provider.

Keep API keys local and do not expose them in replies.

### Current Verified Successful Run

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

This is the minimum evidence to preserve in the final answer or working notes for future Banana PPT deliveries.

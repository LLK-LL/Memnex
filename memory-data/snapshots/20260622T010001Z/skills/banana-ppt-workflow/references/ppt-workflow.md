# Banana PPT Workflow

## Use Cases

Use PPT mode for:

- PPTX deliverables,
- slide decks,
- presentations,
- strict page-count decks,
- PDF exports derived from a deck,
- requests that need both deck structure and generated slide images.

## Standard Deck Flow

```powershell
Set-Location "C:/Users/Administrator/Documents/Codex/2026-06-09/github/work/banana-slides"
$env:PYTHONIOENCODING = "utf-8"

uv run banana-cli --json projects create `
  --creation-type idea `
  --idea-prompt "<deck topic>" `
  --extra-requirements "<audience, style, structure, language>" `
  --image-aspect-ratio "16:9"

uv run banana-cli projects use <project_id>
uv run banana-cli workflows outline --pages <target_page_count> --language zh
uv run banana-cli workflows outline --refine "<compression or structure instruction>" --pages <target_page_count> --language zh
uv run banana-cli workflows descriptions --language zh --max-workers 1
uv run banana-cli workflows images --language zh --max-workers 1 --use-template
uv run banana-cli exports pptx --output "<absolute-output-path>.pptx"
```

## Strict Page-Count Flow

Use `--pages` as a hint, not a guarantee. For strict page-count decks, lock outline structure before generating images.

```powershell
Set-Location "C:/Users/Administrator/Documents/Codex/2026-06-09/github/work/banana-slides"
$env:PYTHONIOENCODING = "utf-8"

uv run banana-cli workflows full --pages <target_page_count> --language zh --skip-images
uv run banana-cli projects get <project_id>
uv run banana-cli workflows outline --refine "Compress or expand to exactly <target_page_count> pages while preserving the requested structure." --pages <target_page_count> --language zh
uv run banana-cli workflows descriptions --language zh --max-workers 1
uv run banana-cli workflows images --language zh --max-workers 1 --use-template
uv run banana-cli exports pptx --output "<absolute-output-path>.pptx"
```

## PPT Acceptance Standard

A PPT deliverable is compliant only when:

- page count is verified before image generation when the user requested a strict count,
- the formal image generation task reports `task_type = GENERATE_IMAGES`,
- the formal image generation task reports `status = COMPLETED`,
- the formal image generation task reports `progress.completed = expected_page_count`,
- the formal image generation task reports `progress.failed = 0`,
- every exported page has `generated_image_url`,
- every exported page has `status = COMPLETED`,
- the PPTX is exported with `uv run banana-cli exports pptx`,
- the exported PPTX exists locally and contains the expected slide count.

## Non-Compliant Outputs

Do not present these as Banana PPT deliverables:

- manually reconstructed PPTX files,
- local fallback images inserted into a deck,
- Banana projects with failed image pages,
- placeholder-only PPTX exports,
- generic PowerPoint generation outside Banana.

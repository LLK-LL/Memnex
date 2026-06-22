# Banana Image Workflow

## Use Cases

Use image mode for:

- one Banana-generated image,
- multiple generated images,
- a single visual page exported as image,
- page images requested without a PPTX,
- image-first drafts where the formal deliverable is PNG/JPG/ZIP.

## Single Image Shortest Path

Use this path for one Banana image. Do not read `imagegen`, do not try local fallback rendering, do not probe unrelated command groups, and do not pass long Chinese JSON through PowerShell CLI arguments.

1. Read only `banana-workflow.md` and this file.
2. Run backend and image-model preflight.
3. Create a Banana project with `creation-type idea`; do not rely on `creation-type descriptions` to auto-create a page.
4. Upload the reference image only if the user provided one.
5. Create exactly one blank Banana page with minimal JSON.
6. Write the full UTF-8 page description through `references/scripts/write-page-description.py`.
7. Verify `projects get` shows the page description is not mojibake and any material URL is present.
8. Run `pages gen-image`.
9. Wait for the returned image task using `tasks wait --project-id <project_id> --task-id <task_id>`.
10. Verify page status and export images.

```powershell
Set-Location "C:/Users/Administrator/Documents/Codex/2026-06-09/github/work/banana-slides"
$env:PYTHONIOENCODING = "utf-8"

curl.exe -sf http://localhost:5000/health
$test = uv run banana-cli --json settings test --name image-model
uv run banana-cli settings test-status --task-id <settings_task_id>

$project = uv run banana-cli --json projects create `
  --creation-type idea `
  --idea-prompt "<short image topic>" `
  --template-style "<visual style>" `
  --image-aspect-ratio "<ratio>"

uv run banana-cli projects use <project_id>

# Optional, only when the user supplied a reference file.
uv run banana-cli materials upload --project-id <project_id> --file "<absolute-reference-image-path>"
uv run banana-cli projects get <project_id>

$page = uv run banana-cli --json pages create `
  --project-id <project_id> `
  --order-index 0 `
  --description-json '{"title":"Single Banana Image","text":"Description will be replaced through UTF-8 API.","extra_fields":{}}'

python "C:/Users/Administrator/.codex/skills/banana-ppt-workflow/references/scripts/write-page-description.py" `
  --project-id <project_id> `
  --page-id <page_id> `
  --description-file "<absolute-utf8-description-json-path>"

uv run banana-cli projects get <project_id>

$imageTask = uv run banana-cli --json pages gen-image `
  --project-id <project_id> `
  --page-id <page_id> `
  --language zh `
  --use-template `
  --force-regenerate

uv run banana-cli tasks wait --project-id <project_id> --task-id <image_task_id>
uv run banana-cli tasks status --project-id <project_id> --task-id <image_task_id>
uv run banana-cli projects get <project_id>
uv run banana-cli exports images --project-id <project_id> --page-ids <page_id> --output "<absolute-output-path>.zip"
Test-Path "<absolute-output-path>.zip"
```

## Multi-Image Flow

Use this flow when the user wants multiple Banana-generated images and does not require per-page reference-image control.

```powershell
Set-Location "C:/Users/Administrator/Documents/Codex/2026-06-09/github/work/banana-slides"
$env:PYTHONIOENCODING = "utf-8"

uv run banana-cli --json projects create `
  --creation-type idea `
  --idea-prompt "<image batch topic>" `
  --extra-requirements "<number of images, visual style, aspect ratio, language>" `
  --image-aspect-ratio "16:9"

uv run banana-cli projects use <project_id>
uv run banana-cli workflows outline --pages <image_count> --language zh
uv run banana-cli workflows descriptions --language zh --max-workers 1
uv run banana-cli workflows images --language zh --max-workers 1 --use-template
uv run banana-cli tasks status --project-id <project_id> --task-id <image_task_id>
uv run banana-cli projects get <project_id>
uv run banana-cli exports images --output "<absolute-output-path>.zip"
```

## Avoid These Detours

- Do not read or invoke `imagegen` for Banana image tasks.
- Do not inspect `refs` unless the selected shortest path fails specifically because reference files are required.
- Do not inspect backend source code unless documented CLI/API commands fail.
- Do not retry PowerShell quoting for long Chinese JSON after the first encoding or parsing failure; switch to the UTF-8 helper script.
- Do not keep a page if its description was created with mojibake. Delete it or overwrite it through the UTF-8 helper and verify `projects get`.
- Do not stop after `pages gen-image` starts. The task must be waited, verified, exported, and checked locally.

## Image Acceptance Standard

An image deliverable is compliant only when all checks pass:

- `settings test-status` reports `status = COMPLETED` and an `image_size`.
- The Banana project exists and contains the requested page IDs.
- If a reference image was provided, `projects get` shows the uploaded material or an accessible material URL used in the page description.
- `projects get` shows the page description is UTF-8-correct, not `??` mojibake.
- The image generation task reports `status = COMPLETED`.
- The image generation task reports `failed = 0` when progress fields are available.
- Every requested page has `generated_image_url`.
- Every requested page has `status = COMPLETED`.
- `uv run banana-cli exports images` produced the final file.
- `Test-Path "<absolute-output-path>.zip"` returns `True`.
- The exported ZIP contains the expected number of image files.

Use this PowerShell check to count exported image files:

```powershell
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead("<absolute-output-path>.zip")
($zip.Entries | Where-Object { $_.FullName -match '\.(png|jpg|jpeg|webp)$' }).Count
$zip.Dispose()
```

## Non-Compliant Outputs

Do not present these as Banana image deliverables:

- local SVG or PNG files created outside Banana,
- manually rendered slide images,
- image placeholders,
- pages without `generated_image_url`,
- image ZIPs exported from projects with failed requested pages.

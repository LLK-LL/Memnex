---
name: banana-ppt-workflow
description: Use when the user says "banana" in the context of image generation, single-page visual generation, slides, PPT, deck, presentation, page generation, or explicitly asks to use Banana/Banana Slides. Routes to Banana-native image or PPT workflows, enforces no-fallback delivery, performs API/config preflight, and validates exported artifacts.
---

# Banana Deliverable Workflow

## Mode Selection

When the user says `banana`, first classify the requested deliverable:

- **Image mode:** single image, visual page, poster-like page, page image, PNG/JPG, image batch, or "generate pictures/images".
- **PPT mode:** PPTX, slide deck, presentation, multiple slides, strict page-count deck, PDF from deck.
- **Both:** user asks for PPT and exported images, or asks for a deck plus page images.

If unclear, infer from the requested file type. If still unclear, ask one short question: "Do you want Banana to output images, a PPT, or both?"

## Required References

- Always read `references/banana-workflow.md` for shared preflight and failure recovery.
- For image mode, read `references/image-workflow.md`.
- For PPT mode, read `references/ppt-workflow.md`.
- For both, run PPT mode first when slide structure matters, then export images from the validated project.

## Hard Rule

Formal deliverables must be produced through Banana-native generation and Banana-native export. Do not substitute local fallback drawing, manual page reconstruction, non-Banana layout/image generation, or an alternative model pipeline as the formal deliverable.

If Banana generation fails, continue diagnosing model, settings, template, description, task status, API, and export issues until Banana succeeds or a concrete blocker is identified.

## CLI Invocation

On this machine, prefer:

```powershell
Set-Location "C:/Users/Administrator/Documents/Codex/2026-06-09/github/work/banana-slides"
$env:PYTHONIOENCODING = "utf-8"
uv run banana-cli <command>
```

Use plain `banana-cli` only after confirming it is on PATH.

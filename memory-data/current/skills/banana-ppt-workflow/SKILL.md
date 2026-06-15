---
name: banana-ppt-workflow
description: Use when the user says "banana" in the context of slides, PPT, deck, presentation, page generation, or explicitly asks to use Banana/Banana Slides for PPT or single-page generation. Routes to powerpoint-builder plus the verified local Banana Slides workflow, enforces the no-fallback Banana-native hard rule, strict page-count workflow, API/config checks, and export validation.
---

# Banana PPT Workflow

## Core Routing

When the user says `banana` in a slides/PPT/deck/presentation/page-generation context, use this skill together with `powerpoint-builder` and the verified local Banana Slides workflow. Do not use a generic PPT generation path.

Read [references/banana-workflow.md](references/banana-workflow.md) before executing a Banana task that involves generation, export, page-count control, API/config changes, or failure recovery.

## Hard Rule

When the user explicitly asks to use Banana for PPT or single-page generation, the formal deliverable must be produced through the verified Banana-native workflow. Do not substitute local fallback drawing, manual page reconstruction, non-Banana layout/image generation, or an alternative model pipeline as the formal deliverable.

If Banana generation fails, continue diagnosing Banana model, settings, template, description, task status, API, and export issues until the Banana-native chain succeeds or a real blocker is identified and reported.

## Execution Outline

1. Confirm the requested output: full deck, strict page-count deck, or single page.
2. Verify Banana backend health, CLI settings, and relevant API/config state before generation.
3. Select the verified workflow from the reference:
   - full deck,
   - single page,
   - strict page-count/content-first deck,
   - API/config repair.
4. For Chinese content on Windows, set `PYTHONIOENCODING=utf-8`.
5. Keep content and structure stable before generating images when page count or structure matters.
6. Export only after the project meets the requested structure and page-count requirements.
7. Validate the final PPTX/images were exported from Banana and match the requested deliverable.

## Validation

- The final deliverable comes from Banana-native export, not fallback reconstruction.
- Full decks use the verified outline/refine/template/export flow.
- Single pages use the verified descriptions/manual-page/image/export flow.
- Strict page-count decks verify actual page count; `--pages` is treated only as a hint.
- Images are generated after content lock when structure or cost matters.
- Formal PPT delivery is valid only when Banana's `GENERATE_IMAGES` task reports `COMPLETED` with `completed = expected_page_count` and `failed = 0`.
- For the local OpenAI-compatible setup, use `gpt-image-2` with `openai_image_api_protocol = images` for Banana image generation unless a settings test proves another image configuration works.
- API keys are never exposed in replies.

## Failure Modes

- **Fallback temptation:** stay inside Banana unless the user explicitly authorizes a non-Banana deliverable.
- **Page-count drift:** refine outline and regenerate content before image generation.
- **Wasted images:** avoid early `workflows full` image generation; use `--skip-images` during validation.
- **Windows Chinese encoding:** set `PYTHONIOENCODING=utf-8`.
- **API/settings mismatch:** update both `.env` and persistent Banana settings because database settings can override env at runtime.

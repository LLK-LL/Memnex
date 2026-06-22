---
name: pptx-automizer
description: Use when the user asks to create, edit, generate, or batch-produce PowerPoint presentations from an existing PPTX template, especially when they mention using a template, replacing template text/images/charts/tables, preserving a designed slide layout, or using the open-source pptx-automizer project.
---

# PPTX Automizer

## Purpose

Use `pptx-automizer` when the task is template-first PowerPoint generation: start from an existing `.pptx` design, reuse selected slides, replace placeholders or named shapes, and export a new `.pptx`.

Prefer this skill over from-scratch slide generation when the user provides or references a PowerPoint template.

## Workflow

1. Inspect the user's template and requirements.
   - Identify input `.pptx` files, output filename, slide order, data source, and assets.
   - If the user has not provided the template file yet, ask for it before implementing.
   - Use the `powerpoint-builder` skill for template inspection, thumbnails, text extraction, and visual QA whenever actual `.pptx` files are touched.

2. Prepare a Node.js workspace.
   - Install dependencies locally unless the project already has them:

```bash
npm install pptx-automizer
```

   - Add `pptxgenjs` only when new shapes/slides must be drawn instead of only modifying existing template content.

3. Use a template directory and an output directory.

```js
const { Automizer } = require('pptx-automizer');

const automizer = new Automizer({
  templateDir: 'templates',
  outputDir: 'outputs',
  removeExistingSlides: true,
});
```

4. Build from reusable template slides.
   - Load slides from the template deck.
   - Modify named shapes, text boxes, images, tables, or charts according to the user's data.
   - Preserve the template layout unless the user asks for redesign.

5. Validate the generated file.
   - Extract text and check for missing or leftover placeholders.
   - Render slides to images and inspect for overflow, misalignment, unreadable text, or broken images.
   - Fix and re-render affected slides before reporting completion.

## Implementation Guidance

- Treat PowerPoint as OpenXML; avoid brittle ad hoc zip/XML edits unless `pptx-automizer` cannot express the required change.
- Prefer stable element identifiers: named shapes, slide names, or creation IDs.
- Keep template files separate from generated outputs.
- For repeated reports, put user data in JSON, CSV, Excel, or a small config file and keep generation code deterministic.
- When library behavior or APIs are uncertain, check the current official GitHub README or docs before coding.

## Best Fit

Use this for:

- Company or school PPT templates with fixed visual identity.
- Batch reports with the same slide layout and changing text, images, tables, or charts.
- Combining slides from multiple existing `.pptx` decks.
- Automating PPT output while preserving designer-made layouts.

Do not use this as the only tool when:

- There is no template and the user wants a fully designed deck from scratch. Use `powerpoint-builder` or `pptxgenjs` patterns instead.
- The user asks for an AI presentation generator product or hosted app. Consider project-level tools such as Presenton instead.

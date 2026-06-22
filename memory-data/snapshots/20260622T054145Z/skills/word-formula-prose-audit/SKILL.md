---
name: word-formula-prose-audit
description: >
  Use when checking or repairing Word DOCX manuscript prose around formulas,
  especially real subscript/superscript runs, italic/upright symbol typography,
  raw underscore notation, Greek placeholder names, formatting-rationale text
  accidentally written into the manuscript body, or post-BuildUp formula prose
  regressions.
---

# Word Formula Prose Audit

## Goal

Ensure formula-neighbouring manuscript prose uses real Word symbol formatting
and contains only article content, not audit or formatting rationale.

## Use When

- A Word manuscript contains formula explanations, inline symbols, or prose
  symbols with subscripts or superscripts.
- The user reports raw forms such as `W_IJ`, `rho_J`, `epsilon_dot`, `N_s`, or
  English placeholders for Greek symbols.
- A DOCX was generated or modified after Word `OMath.BuildUp()`.
- The task needs run-level checks for italic variables and upright numbers,
  operators, constants, abbreviations, or label-like indices.

## Do Not Use When

- The document has no DOCX structure or formula-related prose.
- The task is only formula-object repair; use `docx-omml-repair` first.
- The user only asks for conceptual writing advice without Word output.

## Inputs

- Source DOCX path.
- Target section or formula range, if known.
- Expected symbol conventions from local paper memory.

## Workflow

1. Use project RAG for local formula typography rules and known regressions.
2. Inspect the DOCX at run/XML level, not only flattened paragraph text.
3. Check visible prose for raw notation: underscores, caret braces, placeholder
   Greek names, formula fragments, and operator-like text where real symbols are
   required.
4. Check run formatting for true Word subscript/superscript and italic/upright
   classification.
5. Check manuscript-body purity: remove or flag wording such as "subscript is
   numeric", "should remain upright", "audit", "checked", or similar process
   rationale.
6. If edits are needed, rebuild the affected runs with real Word formatting and
   preserve only symbol meanings in the manuscript body.
7. Save a new DOCX unless overwrite is explicitly allowed.
8. Re-run the visible prose and run-level checks before final reporting.

## Validation

- No raw underscore or caret notation remains in the target prose.
- Greek/math symbols are real characters or Word math/prose runs, not English
  placeholders.
- Numeric and label-like indices are upright; variable bodies remain italic.
- The manuscript body contains no formatting rationale, audit language, or
  self-check wording.
- The output DOCX opens and target paragraph counts/locations did not drift.

## Failure Modes

- Plain text looks acceptable but runs are wrong: inspect `word/document.xml`
  and run properties directly.
- Word BuildUp changes structure after a precheck: audit after BuildUp, not
  before.
- PowerShell corrupts symbols: use saved scripts with Unicode escapes or code
  points.
- Adjacent formula tables merge after BuildUp: separate and audit table counts,
  equation-number continuity, and number-cell purity.

## RAG Handoff

Search local memory for `formula typography`, `prose symbol`, `upright`,
`italic`, `subscript`, `BuildUp`, `OMML`, `placeholder`, `formatting rationale`,
and the target section name before editing.

---
name: docx-omml-repair
description: >
  Use when editing, generating, repairing, or validating Word DOCX files that
  contain OMML equations, manuscript formulas, python-docx edits, lxml XML
  construction, Unicode math symbols, damaged placeholders, or formula layout
  issues on Windows.
---

# DOCX OMML Repair

## Goal

Repair DOCX formula and Word-processing issues without corrupting equations,
formatting, Unicode symbols, or document package validity.

## Use When

- A DOCX contains OMML equations, formula numbering, placeholders, damaged math
  glyphs, or missing formula symbols.
- You are generating OMML with `lxml` or editing Word content with
  `python-docx`.
- The task involves Windows PowerShell, Unicode math symbols, Greek letters, or
  manuscript formula formatting.

## Do Not Use When

- The file is plain text, Markdown, LaTeX, or PDF-only.
- The task is only prose polishing with no DOCX structure or formula handling.

## Inputs

- Source `.docx` path.
- Target edits or repair symptoms.
- Whether overwrite is allowed. Default to saving a new output file.

## Workflow

1. Recall project memory for local DOCX conventions and prior failures.
2. Inspect the package with structured DOCX tools before editing raw XML.
3. Prefer `python-docx` for paragraph, table, header, footer, and run edits.
4. For OMML repairs, rebuild damaged equations as clean OMML rather than
   patching corrupted fragments in place.
5. When constructing OMML with `lxml`, create a fresh XML element for every
   repeated occurrence. Reusing the same element moves it from the old parent.
6. Flatten nested formula-fragment lists before appending to XML elements.
7. Avoid piping Python source with literal Greek, accented, or math symbols
   through PowerShell. Prefer a saved script plus Unicode escapes or explicit
   code-point construction.
8. Remove stale inline math objects from prose paragraphs when they are remnants
   of damaged formulas.
9. Save to a new `.docx` unless overwrite was explicitly requested.
10. Reopen the output and run validation checks.

## Validation

- Confirm the DOCX package can be opened and parsed.
- Check paragraph counts and target term counts did not regress.
- Inspect equations for placeholder boxes, missing symbols, flattened
  subscripts or superscripts, and stray inline OMML.
- Verify equation numbering and expected formula locations.
- On Windows, use the `py` launcher if `python` is unavailable and configure
  UTF-8 output before printing non-ASCII characters.

## Failure Modes

- Missing repeated symbols: reused one `lxml` element object. Rebuild with
  factory functions that return fresh elements.
- `TypeError` while appending formula fragments: nested lists were not
  flattened before XML append.
- Question marks replace math symbols: PowerShell or console encoding damaged
  source text. Use saved scripts and Unicode escapes.
- Fix appears visual only: stale inline OMML may remain in prose paragraphs.

## RAG Handoff

Search memory for `docx`, `omml`, `python-docx`, `lxml`, `formula`, and
`windows-encoding` before editing project documents.

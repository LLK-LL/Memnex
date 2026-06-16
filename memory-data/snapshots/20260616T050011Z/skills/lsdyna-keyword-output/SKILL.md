---
name: lsdyna-keyword-output
description: >
  Use when generating, repairing, or testing LS-DYNA `.k` keyword files,
  especially material or EOS cards whose numeric fields serialize, shift,
  overflow fixed columns, or fail import due to formatting.
---

# LS-DYNA Keyword Output

## Goal

Write generated LS-DYNA keyword cards in a robust format that import tools parse
without shifted or serialized numeric fields.

## Use When

- Generated `.k` cards show shifted, merged, serialized, or corrupted fields.
- Writing `*MAT_HIGH_EXPLOSIVE_BURN`, `*EOS_JWL`, or similar numeric cards.
- Tests need to verify generated keyword data rows.

## Do Not Use When

- The task is solver physics calibration rather than keyword formatting.
- A fixed-column format is explicitly required by the receiving tool and has
  already been verified.

## Inputs

- Target keyword cards.
- Expected field names and row counts.
- Existing writer or export code.

## Workflow

1. Recall project memory for card-specific conventions.
2. Inspect failing rows and identify whether scientific notation overflows
   nominal fixed-width columns.
3. Prefer comma-separated free format for generated numeric rows when supported.
4. Keep each card row at the expected field count.
5. Use one shared float formatter such as `format(value, ".8E")`.
6. Avoid mixing fixed widths in the same generated material card.
7. Add tests that ignore keyword and comment lines, then assert data row count
   and comma-split field counts.

## Validation

- Import the `.k` file in the target LS-DYNA-compatible tool when available.
- For `MAT_HIGH_EXPLOSIVE_BURN` and `EOS_JWL`, assert two data rows and exactly
  eight comma-separated fields per row.
- Confirm large exponent values remain separate fields.

## Failure Modes

- Adjacent values merge: fixed-width columns overflowed under scientific
  notation. Use free-format comma-separated rows.
- Tests pass visually but import fails: assert parsed field counts, not only
  string containment.
- Card-specific comments confuse checks: ignore keyword and comment lines.

## RAG Handoff

Search memory for `ls-dyna`, `k-file`, `keyword-output`, `free-format`, and the
specific card names before editing a writer.

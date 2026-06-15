---
name: openradioss-kfile-compatibility
description: >
  Use when preparing, scanning, repairing, or validating LS-DYNA `.k` files for
  OpenRadioss Starter compatibility, including unsupported keyword variants,
  contact card conversion, deterministic auto-repairs, and manual-review
  boundaries.
---

# OpenRadioss K-File Compatibility

## Goal

Make conservative, deterministic LS-DYNA `.k` compatibility repairs before
OpenRadioss Starter while stopping for modeling judgment when needed.

## Use When

- OpenRadioss Starter rejects or warns on LS-DYNA keyword variants.
- A launcher or preprocessor scans `.k` files before Starter.
- Contact keyword variants or set metadata tails need compatibility cleanup.

## Do Not Use When

- The requested change alters physical modeling assumptions without user review.
- The issue is unrelated to OpenRadioss or LS-DYNA keyword compatibility.

## Inputs

- `.k` file path.
- Starter error or compatibility scan output.
- Supported keyword documentation or local compatibility rules.

## Workflow

1. Recall prior OpenRadioss `.k` compatibility memory.
2. Compare the failing keyword against official or project-accepted supported
   keyword behavior.
3. Auto-repair only deterministic layout or keyword-variant changes.
4. Convert unsupported contact `_ID` variants such as
   `*CONTACT_SURFACE_TO_SURFACE_ID` or
   `*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE_ID` to
   `*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE` when that conversion is known valid.
5. Remove the following CID/title card when converting those `_ID` variants.
6. Trim LS-DYNA-only set metadata tails only when they are confirmed to produce
   compatibility warnings.
7. Stop for manual review on unsupported keywords that require modeling
   judgment.
8. Run the scan or Starter again and record remaining findings.

## Validation

- Compatibility scan returns zero findings or only documented manual-review
  items.
- OpenRadioss Starter reaches zero errors for the repaired case.
- Large files are scanned in acceptable time and without rewriting unrelated
  content.

## Failure Modes

- Starter stops before reading model data: check unsupported keyword variants
  near the reported line.
- Conversion leaves extra fields: remove the CID/title comment and data card
  associated with `_ID` contact variants.
- Auto-fix scope grows into modeling choices: stop and ask for review.

## RAG Handoff

Search memory for `openradioss`, `ls-dyna`, `k-file`, `keyword-conversion`,
`contact`, and local project paths before repair.

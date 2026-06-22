# Workflow and output format

## Accepted inputs

# REDACTED: sensitive-looking memory line

If reviewer boundaries or comment segmentation are ambiguous, flag the ambiguity instead of inventing reviewer structure.

## Workflow

1. Identify task mode and input readiness: `draft`, `audit`, `revise`, `triage-only`, or `appeal-like`.
2. Identify decision type: minor revision, major revision, revise-and-resubmit, transfer after review, or unclear.
3. Extract editor instructions first and assign IDs such as `E.1`, then split reviewer comments with IDs such as `R1.1`, `R1.2`, and `R2.1`.
4. Classify each item by category, severity, action label, missing input, readiness state, and risk.
5. Create a response strategy summary before drafting prose.
6. Draft responses using preserved reviewer comments unless the mode is `triage-only` or `appeal-like`.
7. Map each claimed change to manuscript location, figure, table, supplement, citation, or explicit placeholder.
# REDACTED: sensitive-looking memory line
9. Run QA for completeness, traceability, factuality, tone, and unresolved risk.
# REDACTED: sensitive-looking memory line

## Output format

Unless the user asks for another format, return:

```text
Response strategy summary
- Decision type:
- Overall posture:
- Major risks:
- Suggested ordering:

Comment-response tracker
# REDACTED: sensitive-looking memory line
|---|---|---|---|---|---|

Draft point-by-point response letter
[editor-readable English response]

Manuscript change checklist
- [specific manuscript changes or placeholders]

Missing information / risk flags
- [specific unresolved items or "None"]

涓枃鏍稿
- [when the user writes in Chinese; otherwise omit unless useful]
```

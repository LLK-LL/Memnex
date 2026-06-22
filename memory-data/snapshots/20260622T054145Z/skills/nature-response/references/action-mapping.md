# Action mapping

Use this file to map every reviewer concern to a concrete response action.

## Action labels

| Action label | Meaning | Use when |
|---|---|---|
# REDACTED: sensitive-looking memory line
| `ACCEPT_ANALYSIS` | Added or revised analysis | The response depends on real analysis output |
# REDACTED: sensitive-looking memory line
| `ACCEPT_FIGURE` | Added or modified figure, table, panel, legend, or supplement | A visual or tabular item addresses the concern |
| `CLARIFY_EXISTING` | Existing data already address the concern, but manuscript presentation needed clarification | The evidence exists and location can be cited |
| `ADD_CITATION` | Added verified citation | The citation is genuinely relevant and metadata is supplied or flagged |
| `SOFTEN_CLAIM` | Reduced claim strength or added boundary | The original claim was too broad, causal, novel, clinical, or mechanistic |
| `PARTIAL` | Partly addressed with explicit remaining limitation | A valid concern cannot be fully resolved in the revision |
| `DISAGREE` | Respectfully disagree with evidence or scope-based reasoning | The reviewer interpretation is not supported by the manuscript facts |
| `OUT_OF_SCOPE` | Valid suggestion but outside current manuscript scope | The request requires a new cohort, system, longitudinal design, or different study |
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line

## Internal tracker fields

Use this shape internally when organizing a response:

```yaml
comment_id: R1.3
reviewer: Reviewer 1
severity: major
category: methodological
action: ACCEPT_ANALYSIS
# REDACTED: sensitive-looking memory line
readiness: draft_with_placeholders
risk_level: high
manuscript_location: Methods; Results; Supplementary Fig. S2
```

## Readiness state

| State | Meaning |
|---|---|
| `ready_to_submit` | Enough facts are supplied to draft final text with traceable manuscript location |
| `draft_with_placeholders` | Draft can proceed, but placeholders must remain visible |
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line

## Risk level

| Risk | Use when |
|---|---|
| `low` | Wording, format, or straightforward clarification |
| `medium` | Citation, figure, method detail, or presentation issue requiring verification |
| `high` | Evidence, statistics, validation, claim strength, or out-of-scope request |
| `blocking` | Ethics, compliance, data integrity, missing central evidence, or unsupported response |

## Mapping rules

# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
- If a reviewer asks for impossible or out-of-scope work, use `PARTIAL` or `OUT_OF_SCOPE` plus claim softening or limitation.
- If a reviewer is factually wrong, usually combine `CLARIFY_EXISTING` with a small text clarification.
- If a central claim remains unsupported, use `SOFTEN_CLAIM` or `BLOCKING`, not confident compliance language.

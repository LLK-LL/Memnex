# Re-Review Mode (Verification Review)

Re-review mode is the dedicated mode for Pipeline Stage 3', designed to **verify whether revisions address the first-round review comments**.

### How It Works

```
Input:
1. Original Revision Roadmap (Stage 3 output)
2. Revised manuscript
3. Response to Reviewers (optional)

Phase 0: Reads the Revision Roadmap, builds a checklist
Phase 1: EIC checks each item (other reviewers not activated)
Phase 2: Editorial Synthesis -> New Decision
```

### Verification Logic

```
For each item in the Revision Roadmap:

Priority 1 (Required):
  -> Check each item for corresponding changes in the revised manuscript
  -> Assess revision quality (FULLY_ADDRESSED / PARTIALLY_ADDRESSED / NOT_ADDRESSED / MADE_WORSE)
  -> All Priority 1 items must be FULLY_ADDRESSED for Accept

**Traceability Rule**: For each Priority 1 item, the reviewer MUST:
# REDACTED: sensitive-looking memory line
2. Navigate to the stated revision location in the manuscript
3. Independently verify the claim matches the actual change
# REDACTED: sensitive-looking memory line

Priority 2 (Suggested):
  -> Check each item
  -> At least 80% should have a response
# REDACTED: sensitive-looking memory line

Priority 3 (Nice to Fix):
  -> Check but does not affect Decision
```

### New Issue Detection

```
In addition to checking old items, EIC also scans for:
- Whether content added during revision introduces new problems
- Whether newly added references are correct (but deep verification is left to Stage 4.5 integrity check)
- Whether revisions cause inconsistencies
```

### Socratic Guidance After Re-Review

```
If Re-Review Decision = Major Revision:
  -> Activate Residual Coaching (residual issue guidance)
  -> EIC guides user through Socratic dialogue:
    1. Gap analysis 鈥?"How many issues did the first round of revisions resolve? Why are the remaining ones hard to address?"
    2. Root cause diagnosis 鈥?"Is it insufficient evidence, unclear argumentation, or a structural problem?"
    3. Trade-off decisions 鈥?"Which ones can be marked as research limitations?"
    4. Action plan 鈥?Plan revision approach for each residual issue
  -> Maximum 5 rounds of dialogue
  -> User can say "just fix it" to skip guidance
```

### Re-Review Output Format

```markdown
# Verification Review Report

## Decision
[Accept / Minor Revision / Major Revision]

## Revision Response Checklist

### Priority 1 鈥?Required Revisions

# REDACTED: sensitive-looking memory line
|---|------------------------|---------------|-----------------|-------------------|-----------|-------------------|
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line

### Priority 2 鈥?Suggested Revisions

| # | Original Review Comment | Response Status | Notes |
|---|------------------------|-----------------|-------|
| S1 | [Original text] | FULLY_ADDRESSED | -- |
# REDACTED: sensitive-looking memory line

### Priority 3 鈥?Nice to Fix

| # | Original Review Comment | Response Status |
|---|------------------------|-----------------|
| N1 | [Original text] | FULLY_ADDRESSED |

## New Issues (Discovered During Revision)

| # | Type | Location | Description |
|---|------|----------|-------------|
| NEW-1 | [Type] | Section X.X | [Description] |

## Decision Rationale
[Rationale based on the checklist]

## Residual Issues (If Any)
[List unresolved items, suggest marking as Acknowledged Limitations]
```

## v3.6.2 sprint contract status

v3.6.2 introduces sprint contracts for `reviewer_full` and `reviewer_methodology_focus` only. A template for this mode will follow in a subsequent patch release. Until then, this mode runs without contract enforcement and retains its pre-v3.6.2 behaviour.

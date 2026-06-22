# `nature-reviewer` skill

# REDACTED: sensitive-looking memory line

This skill was created specifically from the reviewer-related content in `Nature`'s official `Editorial criteria and processes` page:
# REDACTED: sensitive-looking memory line

The motivation is narrow and explicit:

- extract the reviewer-relevant rules from that official `Nature` source
- ensure the simulated reviewer behaviour stays consistent with those rules
- avoid drifting into generic peer-review habits or invented reviewer personas
- produce a reusable `nature-reviewer` skill that reflects the official source basis as closely as possible within the repository's skill format

Accordingly, this skill is intentionally conservative. It is grounded in the local copy of that source under `references/editorial criteria and processes.md`, then converted into a conservative output contract: `3 reviewer reports + 1 cross-review synthesis`. The three reports differ only by `emphasis`, because the source supports reviewer function and report content, but does not define fictional reviewer identities or specialty personas.

## What it does

# REDACTED: sensitive-looking memory line
- evaluates the work against source-grounded `Nature`-style axes: `originality`, `scientific importance`, `interdisciplinary readership`, `technical soundness`, and `readability for nonspecialists`
- generates `3` reviewer reports that differ only in `emphasis`, not in invented identity or specialty
- states who would be interested in the results and why
# REDACTED: sensitive-looking memory line
- synthesizes consensus and emphasis differences across the three reports
- flags unsupported claims and material that cannot be assessed from the supplied evidence

## When to use

- simulating a `Nature` reviewer report before submission
- stress-testing whether a manuscript makes a credible broad-interest case
- asking for a reviewer-style assessment of novelty, significance, or technical soundness
- generating a pre-submission critique from the referee perspective
- evaluating whether a manuscript is readable to non-specialists
# REDACTED: sensitive-looking memory line

# REDACTED: sensitive-looking memory line

## What it returns

Unless the user asks for another format, the skill returns:

1. `Review setup`
2. `Reviewer 1`
3. `Reviewer 2`
4. `Reviewer 3`
5. `Cross-review synthesis`
6. `Risk / unsupported claims`

## Core rules

- Ground the assessment in the local reviewer source and the user-supplied manuscript facts only.
- Keep the three reviewers aligned on the same facts; vary only the weighting of those facts.
- Do not invent reviewer identities, narrow specialty roles, institutions, or hidden knowledge.
- Explicitly address `who will be interested in the new results and why`.
# REDACTED: sensitive-looking memory line
- Distinguish technical validity from broad-interest fit; the source treats these as related but not identical.
# REDACTED: sensitive-looking memory line

## Source hierarchy

# REDACTED: sensitive-looking memory line
- user-supplied manuscript facts and evidence
- conservative local implementation rules summarized in `references/source-basis.md`

This skill must not silently expand beyond that source basis into generic reviewer-role invention or journal-policy speculation.

## File structure

```text
nature-reviewer/
鈹溾攢鈹€ README.md
鈹溾攢鈹€ SKILL.md
鈹斺攢鈹€ references/
    鈹溾攢鈹€ editorial criteria and processes.md
    鈹溾攢鈹€ source-basis.md
    鈹溾攢鈹€ reviewer-workflow.md
    鈹溾攢鈹€ review-axes.md
    鈹溾攢鈹€ report-structure.md
    鈹溾攢鈹€ role-boundaries.md
    鈹斺攢鈹€ qa-checklist.md
```

## Status

Draft. The first version is source-defined and structured for grounded reviewer simulation, but it has not yet been validated against a library of real anonymized manuscript-review examples.

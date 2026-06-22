# `nature-response` skill

A reviewer-response skill for drafting, auditing, and revising point-by-point response
letters for Nature-family and high-impact journal manuscript revisions.

This skill is bilingual-aware. It accepts Chinese or English reviewer comments, editor
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line

## What it does

- splits reviewer comments into stable IDs such as `R1.1`, `R1.2`, and `R2.1`
- classifies each concern by type, severity, action, evidence need, and risk
- creates a response strategy summary before drafting prose
- routes requests into drafting, auditing, revising, triage-only, or appeal-like handling
- assigns editor instruction IDs such as `E.1` before reviewer IDs when the decision letter includes editor instructions
- drafts an editor-readable point-by-point response letter
- maps each response to a manuscript action, location, or missing-information flag
# REDACTED: sensitive-looking memory line
- handles difficult cases such as out-of-scope experiments, factual reviewer errors, conflicting reviewers, statistical critiques, and compliance concerns
- flags missing experiments, analyses, line numbers, citations, figure panels, and manuscript changes instead of inventing them

## When to use

- preparing a Nature, Nature Portfolio, Springer Nature, or similar high-impact journal revision
- responding to major or minor revision comments
- turning reviewer comments into a manuscript change checklist
- auditing a draft rebuttal for missing responses, tone problems, or unsupported claims
# REDACTED: sensitive-looking memory line
- deciding how to respectfully disagree with a reviewer or explain a scope boundary

## What it returns

Unless the user asks for another format, the skill returns:

1. response strategy summary
2. comment-response tracker
3. draft point-by-point response letter
4. manuscript change checklist
5. missing information / risk flags
6. Chinese confirmation notes when the user writes in Chinese

## Core rules

- Preserve reviewer comments faithfully before responding.
- Answer every concern, cross-reference it, or mark it unresolved.
# REDACTED: sensitive-looking memory line
- Do not invent experiments, analyses, citations, line numbers, figure panels, supplementary items, reviewer identities, editor instructions, or manuscript changes.
- Use cooperative, evidence-forward, non-defensive language.
- Treat the response letter as an editor-facing verification document, not a politeness exercise.

## Source hierarchy

- Target journal instructions and decision-letter requirements.
- Nature / Nature Portfolio / Springer Nature revision and peer-review process guidance.
- Springer Nature editorial advice on rebuttal letters.
# REDACTED: sensitive-looking memory line

The source basis is summarized in `references/source-basis.md` with URLs, rule summaries, and source-type labels.

## File structure

The skill uses a router/static-dynamic split (like the other nature-* skills): a short `SKILL.md` router plus a `manifest.yaml`. nature-response is a linear workflow with no content axis, so the split is core (always loaded) plus on-demand references.

```text
nature-response/
鈹溾攢鈹€ README.md
鈹溾攢鈹€ SKILL.md                     # short router
鈹溾攢鈹€ manifest.yaml                # always_load core + on-demand references (no axis)
鈹溾攢鈹€ static/
鈹?  鈹斺攢鈹€ core/                    # always loaded
鈹?      鈹溾攢鈹€ stance.md            # purpose, default stance, red lines, source hierarchy
鈹?      鈹斺攢鈹€ workflow.md          # accepted inputs, 10-step workflow, output format
鈹溾攢鈹€ references/
鈹?  鈹溾攢鈹€ source-basis.md
鈹?  鈹溾攢鈹€ response-structure.md
鈹?  鈹溾攢鈹€ comment-taxonomy.md
鈹?  鈹溾攢鈹€ action-mapping.md
鈹?  鈹溾攢鈹€ tone-and-stance.md
# REDACTED: sensitive-looking memory line
鈹?  鈹溾攢鈹€ difficult-cases.md
鈹?  鈹溾攢鈹€ intake-and-routing.md
鈹?  鈹斺攢鈹€ qa-checklist.md
鈹溾攢鈹€ tests/
    鈹溾攢鈹€ conflicting-reviewers.md
    鈹溾攢鈹€ defensive-draft-audit.md
    鈹溾攢鈹€ evaluation-summary.md
    鈹溾攢鈹€ minor-revision.md
    鈹溾攢鈹€ major-revision-missing-evidence.md
    鈹溾攢鈹€ impossible-experiment.md
    鈹斺攢鈹€ rubric.md
鈹斺攢鈹€ examples/
    鈹溾攢鈹€ conflicting-reviewers.md
    鈹溾攢鈹€ major-revision-with-missing-evidence.md
    鈹斺攢鈹€ minor-revision.md
```

## Status

Beta. The behavior is defined by synthetic Markdown fixtures and examples. The skill should remain
# REDACTED: sensitive-looking memory line

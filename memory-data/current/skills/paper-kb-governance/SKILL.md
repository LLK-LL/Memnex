---
name: paper-kb-governance
description: >
  Use when maintaining an Obsidian/local RAG paper-writing knowledge base,
  deciding whether repeated paper-workflow memories should become skills,
  separating manuscript-writing rules from workflow governance, running
  paper-rule iteration, auditing evidence boundaries, or updating paper
  knowledge-base promotion registries.
---

# Paper KB Governance

## Goal

Keep paper-writing knowledge usable, evidence-grounded, and separated from
reusable workflow skills.

## Use When

- The user asks to update, clean, audit, iterate, or reorganize a paper-writing
  knowledge base.
- Repeated paper-workflow lessons may need promotion into a Codex skill.
- Workflow-governance notes risk being mistaken for manuscript-writing rules.
- A local paper harness, Obsidian vault, RAG retrieval, rule layer, conflict
  layer, or promotion registry is involved.

## Do Not Use When

- The user only asks for ordinary manuscript prose revision.
- The task is a one-off project fact, source note, or mentor comment with no
  reusable workflow.
- A narrower skill already covers the operation, such as DOCX OMML repair.

## Inputs

- Project root or knowledge-base path.
- User request and target layer, if specified.
- Existing local workflow file or AGENTS instructions, if present.

## Workflow

1. Load the project-local workflow instructions first.
2. Use low-token local RAG to retrieve workflow-governance notes before scanning
   the whole vault.
3. Classify each item as `paper_writing`, `process_governance`, `concrete_case`,
   or `skill_candidate`.
4. Keep manuscript claims, mentor feedback, evidence, and writing rules in the
   paper knowledge base.
5. Promote only stable, repeatable procedures with triggers, ordered steps,
   validation, and failure handling into skills.
6. Preserve original evidence notes as provenance after promotion.
7. Update the local promotion registry with the stage: P0 memory, P1
   promotable, P2 draft skill, P3 active skill, or P4 revise/retire.
8. Run the local harness or no-regression check required by the project before
   reporting completion.

## Validation

- Workflow-governance notes are not inserted into manuscript-writing rule
  layers unless explicitly intended.
- Skill candidates cite source notes and have clear triggers and validation.
- Existing paper RAG still retrieves writing rules without loading workflow
  governance for ordinary writing tasks.
- The project harness entrypoint succeeds when the local workflow requires it.

## Failure Modes

- Writing rules become skills too early: keep them in the RAG layers until they
  become cross-project executable workflows.
- Governance text contaminates manuscript prose: move it to workflow governance
  and rerun the no-regression guard.
- A skill trigger is too broad: split or narrow the skill before marking it P3.
- RAG summaries are treated as final evidence: open the source notes before
  final generalization or promotion.

## RAG Handoff

Search local paper memory for `workflow-governance`, `kb-rag`, `promotion`,
`conflict`, `mentor`, `supervision`, and `no-regression`. Use total memory only
for cross-project decisions or skill-promotion precedent.

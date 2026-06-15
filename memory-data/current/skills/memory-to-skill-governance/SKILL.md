---
name: memory-to-skill-governance
description: >
  Use when deciding whether remembered project work, bug fixes, lessons,
  workflows, or repeated solutions should stay in RAG memory or be promoted
  into a reusable Codex skill. Also use when designing, reviewing, creating,
  splitting, retiring, or updating skills from accumulated memory records.
---

# Memory To Skill Governance

## Goal

Keep factual project context in memory while promoting stable, repeatable
methods into skills that can be triggered directly in future tasks.

## Use When

- A solution, lesson, debugging process, setup flow, migration flow, or review
  checklist appears reusable across tasks or projects.
- The user asks to improve memory, RAG, skill selection, workflow reuse, or
  automatic learning from past work.
- Several memory records describe similar fixes or approaches and need to be
  consolidated into an executable procedure.
- An existing skill has become too broad, stale, noisy, or ambiguous and needs
  governance.

## Do Not Use When

- The content is only a project fact, one-off decision, or temporary workaround.
- The method has succeeded only once and is not yet stable.
- The record mainly answers what happened, not what to do next.
- The solution depends on private, repository-specific state that cannot be
  generalized.

## Classification

Store these in memory:

- `fact`: project facts, configuration, environment, current state.
- `decision`: architectural or product choices and why they were made.
- `solution`: one concrete problem, root cause, and fix.
- `lesson`: pitfall, failed assumption, or prevention note.
- `convention`: project-local rule or coding pattern.

Promote these to skills:

- Repeatable workflows with stable trigger conditions.
- Cross-project debugging, setup, migration, review, or automation procedures.
- Processes with clear inputs, ordered steps, validation, and failure handling.
- Methods that reduce repeated reasoning, repeated failures, or repeated code.

## Promotion Threshold

Treat a memory record or cluster as a skill candidate when it satisfies all of:

1. The approach is reusable outside a single project incident.
2. The steps are stable enough to describe without excessive exceptions.
3. The process can be expressed as trigger -> inputs -> workflow -> validation.
4. Success can be verified with concrete checks.

Prioritize promotion when either is also true:

- Similar records appeared at least two times.
- The workflow is high-value because it prevents expensive mistakes or saves
  significant repeated effort.

## Lifecycle

Use this promotion lifecycle:

1. `P0 memory`: save the specific case normally.
2. `P1 promotable`: tag likely reusable records with `promotable` and a domain
   tag such as `debug`, `setup`, `migration`, `review`, or `automation`.
3. `P2 draft skill`: after two or more similar records, extract the common
   workflow and create a concise skill draft.
4. `P3 active skill`: validate the draft against a real task and install it as
   a discoverable skill.
5. `P4 revise or retire`: split, update, or retire skills whose triggers are
   too broad, steps are stale, or behavior is no longer useful.

## Workflow

1. Load current rules and use low-token RAG to search related memory first.
2. Decide whether the content is context, a concrete case, a reusable method,
   or a behavior rule.
3. Keep context and concrete cases in memory with accurate types and tags.
   Every saved memory should include `layer:rag-memory` plus a type tag such as
   `memory:fact`, `memory:decision`, `memory:solution`, `memory:lesson`, or
   `memory:convention`.
4. For skill candidates, extract only the stable procedure and discard
   project-specific noise.
5. Write or update `SKILL.md` with a clear frontmatter description, trigger
   conditions, non-use conditions, inputs, workflow, validation, failure modes,
   and RAG handoff guidance.
6. Keep the skill body concise. Move long details to `references/` or
   deterministic repeatable operations to `scripts/`.
7. Validate that the skill can guide a future task without requiring the
   original memory records.
8. Save a memory entry describing the promotion decision and why it matters.

## Maintenance

Run `scripts/backfill_memory_tags.py` after bulk imports, migrations, or
validation runs to ensure every active memory record has `layer:rag-memory` and
its `memory:<type>` tag. The script is idempotent and only appends missing tags.

## RAG Handoff

Even when a skill triggers, use memory/RAG to supplement:

- Project-specific conventions.
- Prior failures in the same repository.
- Architectural decisions that affect the current task.
- Recent user preferences or workflow constraints.

The skill should decide the method. Memory should provide local context.

## Skill Template

Use this compact template for promoted skills:

```md
---
name: skill-name
description: >
  Use when [trigger conditions, task types, input signals, and intended result].
---

# Skill Title

## Goal

One sentence describing the outcome this skill produces.

## Use When

- Trigger condition.
- User wording or task shape.
- When this should run before a generic workflow.

## Do Not Use When

- Non-applicable case.
- Case that should stay in memory or use another skill.

## Inputs

- Required input.
- Optional input and default assumption.

## Workflow

1. Confirm prerequisites.
2. Gather the smallest useful context.
3. Execute the main procedure.
4. Validate the result.
5. Handle failure branches.
6. Save durable learnings to memory.

## Validation

- Concrete success check.
- Command, file, output, or behavioral signal to inspect.

## Failure Modes

- Symptom: likely cause -> response.

## RAG Handoff

- When to search memory for local context.
- Which memory types or tags to prefer.
```

## Quality Bar

- One skill should solve one coherent class of problems.
- Skill names should be short, lowercase, hyphenated, and action-oriented.
- Frontmatter descriptions must be precise because they control triggering.
- Avoid storing bulky project history in a skill.
- Retain original memory records as examples and provenance.

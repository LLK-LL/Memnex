---
name: iteration-harness
description: >
  Use when the user asks to run an iteration, a memory iteration, a persona
  iteration, a workflow-iteration assessment, or a skill-promotion assessment,
  or asks which memories should enter persona, which workflows need revision,
  or which memories should be promoted into a reusable skill.
---

# Iteration Harness

## Goal

Execute memory, persona, workflow, and skill iteration requests in a stable,
evidence-based order and return a consistent decision-oriented result.

## Use When

- The user explicitly asks to run an iteration.
- The user asks for memory cleaning, persona evaluation, workflow revision
  assessment, or skill promotion assessment.
- The user asks which memories should affect persona behavior.
- The user asks which workflows should be revised or promoted into skills.

## Do Not Use When

- The task is casual chat about memory with no request to assess or revise it.
- The task is only to retrieve one known memory record.
- The user only wants code or document changes unrelated to memory/persona/workflow evolution.

## Inputs

- The user's iteration request.
- Relevant memory records, rules, and existing skills.
- Any active persona or workflow publication surface such as `AGENTS.md`.

## Workflow

1. Load compact rules and use low-token memory recall for the current iteration request.
2. Decide which stage the user requested:
   - full iteration,
   - memory cleaning only,
   - preference condensation only,
   - rule promotion only,
   - routing promotion only,
   - persona evaluation only,
   - skill promotion evaluation only.
3. If the request is ambiguous but clearly iteration-related, interpret it as a combined iteration request by default.
4. If the user asks for memory iteration or equivalent wording, complete the requested iteration flow end to end and return the final result in one response by default.
5. Do not stop mid-iteration for candidate review or intermediate confirmation unless:
   - the user explicitly asks to review candidates first,
   - or the user explicitly says that plan changes or fallback paths require prior approval.
6. For the default memory iteration flow, use this layered chain:
   - RAG memory layer: collect raw experiences, project records, fixes, user expressions, and context.
   - Preference layer: extract only stable cross-task user preferences or behavioral tendencies.
   - Rule layer: promote preferences that are explicit, executable, and success/failure-testable.
   - Routing layer: promote only rules that are trigger-and-surface routing logic, such as which skill or harness to use.
7. Keep skill promotion as a separate bypass from RAG memory, not as the default path through preference/rule/routing. A RAG memory may become a skill only when it is a stable, reusable, executable workflow, engineering method, verification process, or failure-recovery procedure.
8. Persona iteration is separate from memory iteration. Evaluate persona candidates separately, and before applying a new persona or major persona revision, ask the user whether to apply it.
9. Before proposing any workflow or skill change, explicitly decide whether the work is:
   - updating an existing workflow or skill,
   - or creating a genuinely new workflow or skill.
10. Prefer updating an existing workflow, harness, or skill when the new content substantially overlaps existing behavior.
11. Treat fallback, workaround, degraded mode, or substitute execution paths as confirmation-required only when the user has explicitly required approval before plan changes.
12. If active instruction/config/template files contain obvious recoverable mojibake or encoding corruption, repair them as part of the current task and verify the fix.
13. When iteration results are durable, save the resulting decision, lesson, convention, or rule-layer change to memory.
14. Treat routing-layer publication as stricter than ordinary rule promotion. A rule qualifies for routing only when it is stable cross-task trigger logic, has a narrow and defensible surface, and is not better stored as a rule, preference, memory, harness, or skill.
15. Do not propose routing-layer candidates for project-local knowledge, one-off debugging paths, tool-version-specific quirks, or habits that require many exceptions.

## Validation

- The response clearly states which iteration stage(s) were run.
- Memory iteration follows the layered chain: RAG memory -> preference -> rule -> routing.
- Skill candidates are handled as a separate RAG-memory bypass and must be executable workflows or methods.
- Persona iteration is reported separately from memory iteration.
- Any new persona or major persona revision is not applied until the user confirms it.
- Recommendations distinguish memory-only, preference-layer, rule-layer, routing-layer, persona, and skill outcomes.
- Any proposed routing target is a real supported surface such as a rule, skill, harness, `AGENTS.md`, `AGENTS.override.md`, or a configured fallback filename.
- Any proposed skill action explicitly says whether it updates an existing skill or creates a new one.

## Failure Modes

- Ambiguous scope: if the request is clearly iteration-related but does not narrow the stage, default to the combined workflow and state that interpretation.
- Mid-iteration review pressure: unless the user explicitly asks to inspect candidates first, finish the requested iteration flow and then report the result with the required template.
- Weak evidence: keep the result in memory instead of promoting it to persona or skill.
- Preference overreach: keep raw evidence in RAG memory when it does not show a stable cross-task user preference.
- Rule overreach: keep a candidate in the preference layer when it is not executable or success/failure-testable.
- Routing overreach: keep a candidate in the rule layer when it does not define stable trigger-and-surface logic.
- Wrong publication target: do not treat files under `outputs/` as active persona sources unless they are explicitly promoted into a supported instruction surface.
- Overlapping skill candidate: update the existing skill instead of creating a duplicate.
- Persona auto-apply: never apply a new persona or major persona revision without asking the user first.

## Output Template

For any iteration request, use the standardized iteration result template defined in:

- `C:\Users\Administrator\.codex\templates\memory-iteration-layered-output-template.md`

This output format is mandatory. After this harness is installed, iteration responses must follow that external template instead of a shorter ad hoc summary.

## RAG Handoff

Before finalizing the result, search memory for:

- existing iteration or harness rules,
- prior persona publication lessons,
- prior workflow repairs,
- prior skill-promotion decisions,
- stable user preferences that affect routing or authority boundaries.

## Publication Boundary

Treat `AGENTS.md` publication as a stricter candidate layer than ordinary persona evaluation.

- Only propose `AGENTS.md` candidates when the content reflects stable day-to-day operating habits with narrow, defensible scope and clear cross-task reuse.
- Do not publish such candidates automatically.
- Candidate identification may be automatic, but writing them into `AGENTS.md` still requires explicit user confirmation.

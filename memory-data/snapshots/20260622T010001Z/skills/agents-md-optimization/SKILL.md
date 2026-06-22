---
name: agents-md-optimization
description: >
  Use when the user asks to reorganize, compress, rewrite, clean up, or
  normalize a Codex AGENTS.md file according to the established routing-first
  structure, including requests phrased as following the agreed harness for
  AGENTS.md cleanup.
---

# AGENTS.md Optimization

## Goal

Restructure `AGENTS.md` into a concise, routing-oriented system file without
changing intended behavior.

## Use When

- The user asks to reorganize or compress `AGENTS.md`.
- The user asks to rewrite `AGENTS.md` according to the established harness.
- The user asks to move long templates or detailed workflow logic out of `AGENTS.md`.
- The user asks to simplify routing, remove duplication, or normalize the file structure of `AGENTS.md`.
- The task is to optimize a Codex system-level `AGENTS.md` while preserving current behavior.

## Do Not Use When

- The task is only to read or explain `AGENTS.md` without changing it.
- The task concerns project-local instructions rather than the Codex system-level `AGENTS.md`.
- The file should intentionally remain long because it is the final artifact rather than a routing surface.
- The user asks to change persona or policy content itself rather than optimize the structure and placement of that content.

## Inputs

- The current `AGENTS.md`.
- Any referenced skills, templates, or external instruction files.
- Relevant memory about prior AGENTS cleanup decisions.
- The user's specific constraints about language, routing, or publication boundaries.

## Workflow

# REDACTED: sensitive-looking memory line
2. Inspect the current `AGENTS.md` and identify:
   - routing rules,
   - stable global constraints,
   - duplicated guidance,
   - long templates,
   - detailed execution logic that belongs in a skill or external file.
3. Keep `AGENTS.md` concise and routing-oriented. Retain only:
   - stable routing rules,
   - durable global constraints,
   - short section-level indexes to related skills or external files.
4. Write system-level rule prose in English by default.
5. Preserve Chinese only when the original wording is meaning-critical, such as:
   - user trigger wording,
   - command wording,
   - fixed output labels,
   - direct quotes,
   - terms that would lose meaning if translated.
6. Move long templates, detailed workflow logic, or publication governance into:
   - the relevant `SKILL.md`,
   - a dedicated template file,
   - or another external system-level reference file.
7. Separate orthogonal concerns into short sections instead of mixing them into one large block.
8. Remove duplication across `AGENTS.md`, skills, and external templates.
9. Prefer semantic trigger definitions over hard-coded Chinese trigger strings when intent routing is sufficient.
10. If a referenced skill does not yet exist and the method is stable, create or update that skill instead of expanding `AGENTS.md`.
11. After edits, verify that `AGENTS.md` still expresses the same effective behavior with a smaller and clearer surface.

## Validation

- `AGENTS.md` is shorter, clearer, and still routing-oriented.
- Long templates or detailed procedures are externalized instead of embedded.
- English is the default system-level prose language.
- Chinese remains only in meaning-critical fragments.
- Trigger rules still match the intended user requests.
- Validation covers realistic request scenarios, not only file presence or syntax.

## Failure Modes

- Over-compression: if a removed section carried active routing behavior, restore the minimum required rule.
- Hidden duplication: if the same policy remains in both `AGENTS.md` and a skill, keep the route in `AGENTS.md` and the procedure in the skill.
- Wrong externalization: if content is actually a stable global rule, keep a short version in `AGENTS.md` instead of moving everything out.
- Over-translation: if the Chinese wording itself is the trigger or required user-facing label, preserve it.
- Weak validation: do not call the refactor complete based only on file existence or successful write operations.

## RAG Handoff

# REDACTED: sensitive-looking memory line

- prior AGENTS cleanup conventions,
- language policy decisions,
- skill-routing preferences,
- publication boundary lessons,
- and prior cases where templates were split out successfully.

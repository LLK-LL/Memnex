# Cursor Rules Adapter

Memnex can feed Cursor by turning selected memories, rules, and workflows into Cursor Rules.

## Best Fit

Cursor works well with Memnex content that is:

- project-specific;
- short enough to remain actionable;
- stable across many tasks;
- written as rules, conventions, or checklists.

Good examples:

- project architecture conventions;
- testing expectations;
- coding style rules;
- common commands;
- mistakes to avoid;
- release or review workflow checklists.

## Suggested Project Layout

```text
project/
  .cursor/
    rules/
      project-conventions.mdc
      testing-workflow.mdc
      memory-notes.mdc
```

## Example Rule

```md
---
description: Project conventions derived from Memnex
globs:
  - "**/*"
alwaysApply: true
---

# Project Conventions

- Prefer existing project patterns before adding new abstractions.
- Run the documented test command before claiming a fix is complete.
- Check Memnex-derived memory notes when a task matches a known workflow.
```

## Conversion Workflow

1. Review `memory-data/current/rules/`.
2. Copy only stable, reusable rules into `.cursor/rules/`.
3. Review `memory-data/current/skills/`.
4. Convert high-value workflows into short task checklists.
5. Keep noisy or personal notes out of project-shared rules.

## Safety Note

Cursor rules can be committed to a project repository. Before committing Memnex-derived rules, remove private names, tokens, machine paths, customer details, and personal-only preferences.

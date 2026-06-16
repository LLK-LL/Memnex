---
name: sci-memory
description: Use when the user wants Codex to apply, update, or iterate an Obsidian/local-memory based SCI paper-writing knowledge base. Trigger for requests to use paper-writing memory, reuse conclusions from Obsidian, apply previous writing rules to a manuscript, save reusable writing lessons into the paper vault, analyze conflicts in writing memory, or directly iterate the writing-rule layers with Codex.
---

# SCI-memory

Use this skill to turn accumulated paper-writing memory into active writing constraints. In this project, `PROJECT_HARNESS_WORKFLOW.md` is the primary workflow; this skill is a fallback or reusable external workflow.

## Collection Rule

Invoking `SCI-memory` automatically enables the collection stage.

That means when this skill is explicitly used for paper-related work, Codex should by default perform collection unless the user explicitly says not to record.

When this skill is explicitly used for paper-related writing, revision, mentor-feedback analysis, manuscript polishing, or writing-rule discussion, Codex must complete the collection-stage promotion chain in one pass unless the user explicitly says not to record.

Collection-stage routing:

1. Concrete modification process goes into `paper_writing_obsidian_vault/10_Project_Change_Log`.
2. Suggestions, preferences, reusable lessons, and mentor feedback go into `paper_writing_obsidian_vault/20_Paper_Memories`.
3. If the user explicitly says the conclusion is already a rule, or if the evidence is already stable enough for the intermediate layer, Codex writes it into `paper_writing_obsidian_vault/30_Writing_Rules`.

In short:

- `修改过程 -> 10`
- `建议 -> 20`
- `明确说是规则 -> 30`

So the collection stage itself completes `10 -> 20 -> 30`.

## Collection Constraints

- Do not write `40_Final_Generalized_Rules` during ordinary collection.
- Do not force `50_Conflicts` or `60_Limited_Rules` during ordinary collection unless the user is explicitly iterating.
- No outside knowledge.
- No local memory database import.

## Locate The Knowledge Base

Prefer these paths:

- `paper_writing_obsidian_vault/00_Index.md`
- `paper_writing_obsidian_vault/10_Project_Change_Log`
- `paper_writing_obsidian_vault/20_Paper_Memories`
- `paper_writing_obsidian_vault/30_Writing_Rules`
- `paper_writing_obsidian_vault/40_Final_Generalized_Rules`
- `paper_writing_obsidian_vault/50_Conflicts`
- `paper_writing_obsidian_vault/60_Limited_Rules`
- `paper_writing_obsidian_vault/70_Iterative_Thinking`

## Automation Rule

When the user starts the automation or explicitly asks to iterate the rule layers, Codex must treat `30_Writing_Rules` as the automation input layer.

Automation-stage order:

1. Read `00_Index.md`.
2. Read current `30_Writing_Rules`.
3. Re-check supporting `20_Paper_Memories` when a rule needs evidence review.
4. For each intermediate rule, decide whether it is final, conflicted, or still limited.
5. Write unresolved contradictions into `50_Conflicts`.
6. Write still-limited rules into `60_Limited_Rules`.
7. Write stable rules into `40_Final_Generalized_Rules`.
8. Write `70_Iterative_Thinking` only when a trace, audit, or report is needed.

So the automation stage completes:

`30 -> 50 / 60 / 40`

## Conflict Handling

Conflict handling follows this rule:

1. If mentor-priority evidence clearly resolves a contradiction, Codex may resolve it automatically.
2. If mentor-priority evidence is not decisive enough, Codex must write the issue into `50_Conflicts` and wait for the user to judge it.

That means conflicts are either:

- auto-resolved by decisive mentor-priority evidence, or
- explicitly surfaced for user judgment

## Writing Application Order

Before revising manuscript text:

1. Load `40_Final_Generalized_Rules` if relevant notes exist.
2. Check `50_Conflicts` if the topic is disputed.
3. Check `60_Limited_Rules` if the task touches a still-local rule.
4. Fall back to `30_Writing_Rules` when the final layer is empty or the user explicitly asks for intermediate reasoning.
5. Build a no-regression checklist from prior final rules, conflicts, limited rules, and known old-error types.
6. Apply the checklist to the text.
7. After generating the new text, run a regression pass to check whether old errors have reappeared.
8. If an old error reappears, correct it before closing the round whenever feasible.

## Non-Negotiable Constraints

- No outside knowledge unless the user explicitly asks for it.
- Do not import local memory database records into `20_Paper_Memories`.
# REDACTED: sensitive-looking memory line
- Higher priority changes weighing, not factual invention.
- If the evidence is insufficient, keep the rule in `50_Conflicts` or `60_Limited_Rules` instead of forcing final generalization.

## Response Pattern

For collection tasks:

1. State what was written into `10_Project_Change_Log`.
2. State what was written into `20_Paper_Memories`.
3. State what was written into `30_Writing_Rules`.
4. State whether any previous error reappeared and how it was corrected.

For automation tasks:

1. State what was written into `40_Final_Generalized_Rules`.
2. State what was written into `50_Conflicts`.
3. State what was written into `60_Limited_Rules`.
4. State which conflicts were auto-resolved by mentor priority and which still need user judgment.
5. State whether any previous error reappeared and how it was corrected.
6. State what must remain fixed in the next round so later revisions do not drift.

<!-- AUTO-GENERATED FINAL RULES START -->
## Current Final Writing Rules Snapshot

This section is auto-generated from `paper_writing_obsidian_vault/40_Final_Generalized_Rules`.
Use these rules directly when the `SCI-memory` skill is invoked for drafting, revision, or analysis.

### Abstract opening should state object-variable-effect

Across domains, an abstract should start from the study object, the key variable or mechanism, and the affected outcome. A broad background opening is weaker when the central scientific relation can be stated directly.

### Method description should serve the research purpose

Method descriptions in abstracts and introductions should be scoped to the research purpose. Implementation details should move to the methods section unless they are part of the core contribution.

### Literature review should progress through capability and limitation

A literature review should not be a mechanical category list. It should move from what prior work can do, to what remains missing, to why the next method is needed, and finally to the remaining gap addressed by the paper.

### Experiment-simulation gaps should be expressed with variables

For papers combining experiments and simulations, the gap should be stated as a missing bridge between observable experimental variables and simulated variables.

### Reference upgrades must preserve sentence-level support

Newer or higher-ranked references are only better when they directly support the sentence-level claim. Argument-source fit comes before recency and journal rank.

### SCI paper sections should form a complete problem-method-evidence chain

An SCI manuscript should connect abstract, introduction, theoretical model, numerical simulation, discussion, and conclusion into one coherent chain: topic and unresolved problem, method and theory, simulation or experimental evidence, mechanism-level analysis, engineering implication, limitations, and future extension.

### SCI abstract should cover topic purpose method result conclusion

An SCI abstract should cover five elements: topic, purpose, method, result, and conclusion, and each element should directly serve the central research problem.

### SCI introduction should use recent literature to expose gaps and route the study

An SCI introduction should use recent literature to move from research background and importance, to current methods and limitations, to this paper's objective, research content, technical route, and main conclusions.

### Theoretical model section should explain equations assumptions and derivations

A theoretical model section should explain the theory, algorithm, governing equations, formulas, assumptions, derivation logic, and variable definitions used to solve the research problem.

### Numerical simulation section should connect model parameters to research claims

A numerical simulation section should build a computational model from the theory or algorithm and extract parameters that are sufficient to explain or prove the paper's research topic.

### Discussion section should analyze mechanism comparison application and limitations

A discussion section should analyze key parameters, mechanisms, comparisons, engineering implementation, advantages, limitations, and feasible solutions to unresolved problems.

### Conclusion section should summarize work innovation limitations and future extension

An SCI conclusion should begin with an overall summary and then use itemized conclusions to summarize the main work, innovations, advantages, limitations, applicability, and future extensions.

### Numeric and abbreviation subscripts must be upright in formulas and prose

In manuscript formulas and ordinary prose, variable bodies should be italic, but numeric subscripts and subscripts that represent English abbreviations, names, or labels must be upright. This applies to displayed formulas, inline formulas, and textual symbol explanations; DOCX checks should inspect run-level formatting rather than relying on flattened plain text.

### Abstract opening should connect application context to core relation

The abstract opening may begin from the application context, but it must immediately connect that context to the paper's core research relation. It should bind the study object, key variable or mechanism, and performance or bonding outcome instead of remaining a broad background sentence.

### Paper framing should keep interface wave and intermetallic compound as dual mainlines

The paper should use a coordinated dual-mainline framing: interface wave formation process prediction plus intermetallic compound scale prediction. Interface wave should not be demoted to a validation-only result when describing the paper's central framing.
<!-- AUTO-GENERATED FINAL RULES END -->

---
name: vibe-paper-writing
description: Guide for integrating user-provided materials (chat logs, documents, citations) into academic papers with proper scholarly style. Use when the user wants to incorporate chat/email threads, personal documents, or references into a LaTeX paper, or asks for academic writing assistance that requires careful source attribution and style preservation.
---

# Vibe Paper Writing

## Overview

This skill guides you in merging user-supplied materials into a professional academic paper. The core challenge is not mechanical insertion but *intelligent integration*: understanding what the user endorses, what belongs where, and how new content echoes existing arguments—all while preserving rigorous scholarly prose.

---

## Task Types

When the user provides materials to incorporate, identify the task type and load the corresponding file for detailed guidance.

| Task | When to use | Detail file |
|---|---|---|
| Chat logs / email threads | User pastes a conversation or email thread | `tasks/chat-and-email.md` |
| User-authored documents | User provides their own draft, notes, or memo | `tasks/user-documents.md` |
| Citations and references | User wants to add a paper, passage, or finding | `tasks/citations.md` |
| Mathematical notation | Writing or checking math expressions and symbols | `tasks/math-notation.md` |
| Paper review | Checking for contradictions, consistency, references, and privacy | `tasks/paper-review.md` |
| Writing improvement | Linearizing logic, enforcing abbreviation policy, moving content to appendix | `tasks/writing-improvement.md` |
| Upgrade | Update the skill to the latest version from GitHub | `tasks/upgrade.md` |

---

## Universal Rules

These apply to every task type. Deviations require explicit user instruction.

**Academic style:**
- Professional English academic prose. No colloquialisms, no blog-post energy.
- Do not use bullet points unless the user explicitly requests them. Prose paragraphs are the default.
- Use subheadings sparingly. Prefer flowing paragraphs within a section.
- Bold and italic are for technical terms and conventional academic emphasis only—not decoration.
- Follow the paper's established voice ("we", impersonal, etc.) and do not switch without reason.
- Match the epistemic hedging already present in the paper ("suggests," "indicates," "may").
- Every inserted paragraph must connect to the one before and after via explicit transition sentences.

**LaTeX compilation:**
After every substantive edit, compile and fix all errors before reporting completion. See `tasks/latex-compilation.md` for the full workflow.

---

## Output Expectations

For every completed task, produce:

1. The updated `.tex` section(s) with changes clearly scoped.
2. A brief explanation of what was integrated, why, and where.
3. Confirmation that LaTeX compilation succeeded (or the specific unresolved error).
4. If endorsement was ambiguous in a chat log, explicitly flag omitted portions so the user can override.

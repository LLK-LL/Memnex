---
name: memory-writing-style
description: >
  Use when saving, rewriting, normalizing, or reviewing content that will be
  written into Codex system-level files or the memory system. Enforces the
  default writing style: write system-level content in English unless the
  original Chinese wording must be preserved for user triggers, commands,
  fixed output labels, quoted text, or other meaning-critical content.
---

# Memory Writing Style

## Goal

Normalize system-bound content into a consistent English-first style while preserving Chinese only where the original wording is meaning-critical.

## Use When

- Saving or revising `AGENTS.md`, skill files, templates, or other Codex system-level files.
- Saving new memory records.
- Rewriting or updating existing memory records.
- Converting free-form notes into memory-ready content.
- Reviewing whether system-bound or memory-bound text follows the preferred style.

## Do Not Use When

- The content is not being written into a Codex system-level file or the memory system.
- Chinese wording must be preserved in full because the text itself is the target artifact.
- The user explicitly requires the entire memory record to remain in Chinese.

## Default Style

- Write system-level content, memory content, context, summaries, and durable rules in English by default.
- Keep Chinese only when the original wording is meaning-critical.

## Preserve Chinese Only For

- User trigger phrases.
- User command wording.
- Fixed output labels that must match user expectations.
- Direct quotes from the user.
- Terms that lose meaning if translated.

## Workflow

1. Identify whether the content will be written into memory.
2. Convert the explanatory body, summary, and durable rule or lesson into concise English.
3. Preserve Chinese only for meaning-critical fragments.
4. If mixed-language content is unavoidable, keep the structure English-first and isolate the Chinese fragments minimally.
5. Before saving, check that the system-level file content or memory record is readable, compact, and consistent with the English-first style.

## Validation

- The system-level file content or memory record is primarily written in English.
- Chinese appears only where preserving the original wording is necessary.
- The result remains faithful to the user's meaning and future retrieval needs.

## Failure Modes

- Over-translation: if a Chinese phrase is itself the trigger or command, preserve it.
- Under-normalization: if large explanatory sections remain in Chinese without necessity, rewrite them into English.
- Mixed-language clutter: reduce bilingual duplication unless both forms are needed.

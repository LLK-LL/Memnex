---
name: memory-rag-optimization
description: >
  Use when optimizing, debugging, or reviewing an agent memory system for
  low-token RAG retrieval, compact rule loading, representation caches,
  no-LLM fallbacks, recall mode defaults, or memory-to-skill promotion flow.
---

# Memory RAG Optimization

## Goal

Reduce memory-system token cost while preserving useful recall, provenance,
and failure-prevention behavior.

## Use When

- Memory recall returns too much full content, duplicate context, or noisy rule
  payloads.
- A memory system needs explicit RAG/index/summary recall modes.
- Saved records should generate summary, keywords, or compressed
  representations for later retrieval.
- The environment may not have an LLM available for representation generation.
- A user asks to iterate the memory library, improve memory retrieval, or make
  memory records promotable into skills.

## Do Not Use When

- The task is only to answer from one known memory record.
- The issue is project-specific content quality, not memory retrieval mechanics.
- A memory candidate is a one-off fact, decision, or incident with no reusable
  workflow.

## Workflow

1. Start with low-token retrieval: use index, compact, summary, or RAG mode
   before reading full records.
2. Narrow candidates by project, type, tags, phase, and limit. Fetch full
   records only for the few candidates needed for a decision or edit.
3. Prefer cached `summary` or `compressed` representations for RAG responses.
   Fall back to short deterministic truncation when caches are missing.
4. Avoid duplicate cognitive context. If rules were already loaded, call memory
   recall with cognitive enrichment disabled where supported.
5. Use compact rule loading for routine work. Load full rules only when a
   compact record advertises that more detail is available and the task needs
   it.
6. When records are saved, ensure representation work is queued or processed so
   future recall can use summaries instead of full text.
7. In no-LLM environments, generate deterministic `summary`, `keywords`, and
   `compressed` fields; leave generated questions empty rather than blocking
   the queue.
8. For memory-to-skill iteration, keep facts, decisions, incidents, and local
   conventions in memory. Promote only stable workflows with triggers, inputs,
   steps, validation, and failure handling.

## Validation

- Recall response contains deduplicated summaries or index entries, not
  repeated full records.
- Failure or debugging queries prioritize `solution` and `lesson` records.
- Phase-scoped queries boost records tagged for the requested phase.
- Representation queues drain after saves, migrations, or backfills.
- No-LLM representation generation still produces deterministic summaries.
- Existing callers remain compatible when defaults change.

## Failure Modes

- Recall still returns large payloads: check default recall mode, cognitive
  enrichment, and whether compact/detail flags are honored.
- RAG mode fails: log the error and return a lightweight index fallback rather
  than failing the tool call.
- New records lack summaries: inspect save hooks, representation queue state,
  and drain/backfill scripts.
- Skill promotion becomes noisy: require at least two similar records or a
  high-value workflow before creating or updating a skill.

## RAG Handoff

Before changing code or creating a skill, search memory for:

- `memory-rag`, `token_efficiency`, `representations`, and `summary-cache`
  records.
- Prior decisions about default recall modes and compatibility.
- Repeated records tagged `promotable`, `skill-ready`, or `promotion:P3`.

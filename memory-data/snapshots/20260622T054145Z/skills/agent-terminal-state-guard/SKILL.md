---
name: agent-terminal-state-guard
description: >
  Use when an agent UI, streaming bridge, backend loop, or automation marks a
  turn as done even though the assistant only produced a planning or
  acknowledgement sentence and no tool-backed work occurred.
---

# Agent Terminal State Guard

## Goal

Prevent agent systems from treating planning-only replies as successful terminal
answers.

## Use When

- A frontend shows Done after text such as "I will inspect the config" or "I
  will load the skill" without tool activity.
- A streaming bridge emits a success event for an incomplete agent turn.
- Backend prompt guidance fails to prevent premature completion.
- Provider or transport behavior changes role handling or terminal state.

## Do Not Use When

- The assistant actually completed the requested work.
- The issue is only frontend display text while backend state is correct.

## Inputs

- Streaming logs or event sequence.
- Agent loop state machine code.
- Frontend/backend terminal event definitions.
- Regression test harness if available.

## Workflow

1. Reproduce or inspect the event sequence and separate frontend display from
   backend terminal state.
2. Identify whether the backend accepts any non-empty assistant text as final.
3. Add a state-machine guard for planning-only or acknowledgement-only text when
   no live tool calls or completed work exist.
4. Detect common English and Chinese next-step patterns without blocking valid
   final answers after real work.
5. Emit an explicit incomplete-turn error event instead of a success `done`
   event.
6. Add regression tests for direct detector cases and streaming integration.
7. Include provider-specific role handling tests if transport roles contributed
   to the failure.

## Validation

- Planning-only replies produce an incomplete-turn error, not Done.
- Tool-backed turns can still finish successfully.
- Tests cover English and Chinese planning phrases.
- Frontend receives zero success terminal events for incomplete turns.

## Failure Modes

- Prompt-only fix fails: terminal behavior belongs in backend state handling.
- Frontend appears wrong but backend sent Done: fix backend terminal semantics.
- Detector blocks valid answers: require absence of tool activity or completed
  work before classifying as incomplete.
- OpenAI-compatible providers reject role `developer`: make role conversion
  provider-aware and keep `system` for providers that do not support developer.

## RAG Handoff

Search memory for `agent-loop`, `streaming`, `done-event`, `intermediate-ack`,
`provider`, and the product name before changing terminal behavior.

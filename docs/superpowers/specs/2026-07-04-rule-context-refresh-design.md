# Rule Context Refresh Design

## Purpose

The rules layer should not be recalled only once at task start, and it should not be refreshed before every tool call. The selected design is event-triggered refresh: refresh rules when task context changes enough that the active rule set may be stale.

This design keeps `self_rules_context` as the low-level rule retrieval tool and adds a new MCP tool, `rule_context_refresh`, to coordinate event handling, cooldown, query construction, and diagnostic output.

## Goals

- Refresh rules during execution only when useful.
- Avoid returning full or steadily growing rule context.
- Keep user-selected `always_on` rules active.
- Replace contextual rules on each refresh instead of accumulating them.
- Expose enough diagnostics to debug low hit rate and noisy recalls.
- Preserve existing `self_rules_context` compatibility.

## Non-Goals

- Do not recall rules before every tool call.
- Do not replace `self_rules_context`.
- Do not build a complex rule family router in this iteration.
- Do not infer high-risk plan changes silently.

## Trigger Policy

`rule_context_refresh` should be called at these events:

- Task start.
- Entering `plan`, `build`, or `reflect`.
- User target changes.
- Error occurs and passes the error refresh policy.

Phase entries `van`, `creative`, and `archive` do not trigger refresh by default.

User target change means:

- The user explicitly switches tasks.
- The user adds a clearly different subtask.

These do not count as target changes:

- The user adds details to the same task.
- The user answers a clarifying question.
- The user asks for status or asks to continue.

## Query Construction

The refresh query should be built from:

```text
latest user instruction + current phase + recent error/tool context summary
```

The query should be short and task-specific. It should not include the full conversation transcript.

## Rule Selection

Rules are split into two layers:

- `always_on`: all user-selected rules tagged `always_on`. No count limit.
- `contextual`: rules selected by query-aware retrieval.

Refresh behavior:

- Keep all `always_on` rules.
- Replace contextual rules on each refresh.
- Do not merge contextual rules indefinitely.

Contextual rule count:

- Default event: top 3.
- Error event: top 5.
- Target-change event: top 5.

## Error Refresh Policy

Refresh immediately for:

- `timeout`
- `config_error`
- `api_error`
- `missing_context`
- `wrong_assumption`

For ordinary `code_error`, refresh only after two consecutive occurrences in the same task context.

## Cooldown

Avoid duplicate refreshes for the same context.

Cooldown key:

```text
phase + query + error_category
```

If the same cooldown key appears again within 5 minutes, skip refresh and return a diagnostic skip result. A different `error_category` must not be blocked by a previous cooldown key.

## Conflict Handling

If refreshed rules conflict with the current execution plan:

- Low-risk conflict: adjust automatically.
- High-risk conflict: pause and ask the user to confirm.

High-risk areas include:

- Delete, overwrite, rollback, or destructive filesystem operations.
- Upload, publish, push, or sync to public networks.
- Remote operations.
- Memory write boundaries.
- Credential, privacy, or redaction-sensitive behavior.

## New MCP Tool

Add:

```text
rule_context_refresh(
  project,
  phase,
  event,
  latest_user_instruction,
  tool_context?,
  error_category?,
  previous_query?,
  detail="compact"
)
```

Accepted events:

- `task_start`
- `phase_change`
- `target_change`
- `error`

The tool should:

1. Decide whether the event requires a refresh.
2. Construct the refresh query.
3. Apply cooldown.
4. Determine contextual `top_k`.
5. Call the existing query-aware `self_rules_context`.
6. Return rules plus diagnostics.

## Return Shape

When refreshed:

```json
{
  "refreshed": true,
  "skip_reason": null,
  "event": "error",
  "phase": "build",
  "query": "...",
  "cooldown_key": "...",
  "cooldown_hit": false,
  "rules": [],
  "counts": {
    "always_on": 3,
    "contextual": 5,
    "total": 8
  },
  "refresh_reason": "...",
  "conflict_hints": []
}
```

When skipped:

```json
{
  "refreshed": false,
  "skip_reason": "cooldown_hit",
  "event": "error",
  "phase": "build",
  "query": "...",
  "cooldown_key": "...",
  "cooldown_hit": true,
  "rules": [],
  "counts": {
    "always_on": 0,
    "contextual": 0,
    "total": 0
  },
  "refresh_reason": null,
  "conflict_hints": []
}
```

Diagnostics are part of the public return shape because rule hit quality is still being tuned.

## Protocol Updates

Update the active protocols to call `rule_context_refresh` at event boundaries:

- `~/.codex/AGENTS.md`
- `~/.agents/skills/memory/SKILL.md`
- Repository `AGENTS.md.template`
- `codex-skill/SKILL.md`
- `skills/memory-protocol`
- SessionStart hook hints
- Phase transition preview text

`self_rules_context` remains available for manual debugging and direct low-level recall.

## Data and State

The tool needs lightweight refresh state:

- Last refresh timestamp per cooldown key.
- Consecutive ordinary `code_error` count per task context.

The first implementation can store this state in memory inside the MCP process. Persistent storage is not required unless restart behavior becomes important.

## Tests

Required coverage:

- Task start refreshes.
- Entering `plan`, `build`, and `reflect` refreshes.
- Entering `van`, `creative`, and `archive` does not refresh by default.
- Same `phase + query + error_category` within 5 minutes returns `cooldown_hit`.
- Different `error_category` is not blocked by cooldown.
- `timeout`, `config_error`, `api_error`, `missing_context`, and `wrong_assumption` refresh immediately.
- First ordinary `code_error` does not refresh.
- Second consecutive ordinary `code_error` refreshes.
- All `always_on` rules are returned without count limit.
- Contextual rules are replaced on refresh and do not accumulate.
- Return shape includes diagnostics fields.
- Existing `self_rules_context` behavior remains compatible.

## Open Decisions

None for this design. The next step is an implementation plan.

# Rule Retrieval Ranking Design

## Purpose

The rule layer currently uses a priority-limited SQL candidate set and then reranks candidates when a query is provided. This improves over bulk loading, but it can still miss relevant rules because `priority DESC LIMIT 20` runs before semantic and trigger-term scoring.

This design improves rule retrieval hit rate without building a full rule RAG system yet.

## Current Method

Current `self_rules_context` behavior:

1. Query active rules by scope.
2. Sort by `priority DESC, success_rate DESC`.
3. Limit candidates to 20.
4. Apply phase filtering.
5. If `query` is provided, split `always_on` and contextual rules.
6. Score contextual rules by semantic similarity, phase match, category hint, and priority.
7. Return `always_on + top_k(contextual)`.

This is not full RAG. It is SQL preselection plus query-aware reranking.

## Problems

- Relevant lower-priority rules can be excluded before scoring.
- `always_on` rules are selected only from the priority-limited candidate pool.
- Trigger-word rules such as `Igor`, `banana`, `QR`, `GitHub`, and `PowerShell` need stronger exact-match behavior than semantic similarity provides.
- Rule count is still small enough that full rule RAG would add more complexity than value.

## Confirmed Retrieval Strategy

Use a layered retrieval strategy:

```text
always_on: fetch all active rules tagged always_on
contextual: fetch all active rules that pass scope + phase eligibility
ranking: exact trigger boost + semantic score + phase/category match + priority
output: always_on + strongest contextual rules
```

This optimizes for:

- User-selected `always_on` coverage.
- High precision for normal contextual recalls.
- Higher recall during error and target-change events.

## Retrieval Objectives

The selected objective is layered balance:

- `always_on`: always included, because the user selected them manually.
- Normal contextual recall: precision first.
- Error or target-change recall: recall can be wider.

## Candidate Selection

Candidate selection should no longer use `priority DESC LIMIT 20` before scoring.

Instead:

1. Fetch all active `always_on` rules by tag.
2. Fetch all active rules matching the requested scope:
   - `scope='global'`
   - `scope='project:<project>'`
   - optionally `scope='category:<category>'`
3. Apply phase eligibility:
   - rules without `phase:*` tags are phase-neutral
   - rules with `phase:<current>` are eligible
   - rules with another phase are excluded
4. Remove `always_on` rules from the contextual candidate set to avoid duplication.

This is acceptable while active rule count is small. If active rules grow beyond roughly 100, revisit a dedicated rule index.

## Ranking Signals

Contextual rules should be ranked with these signals:

- Semantic similarity between query and rule text.
- Exact trigger match against tags, category, and important phrases.
- Phase match.
- Category match.
- Priority.

Do not use `success_rate` or `fire_count` in ranking yet. Existing data is noisy and many rules have zero values.

## Trigger Terms

Do not add a new `trigger_terms` column in this iteration.

Use existing `tags`, but normalize tag practice:

- Include lowercase English aliases for explicit triggers.
- Include Chinese trigger words where relevant.
- Include tool or skill names exactly when they are user-facing.
- Keep tags short and stable.

Examples:

- Igor rule: `igor`, `伊戈尔`, `remote-codex-cli`, `skill-routing`
- Banana rule: `banana`, `ppt`, `presentation`, `powerpoint-builder`
- QR rule: `qr`, `二维码`, `output-format`
- PowerShell rule: `powershell`, `windows`, `quoting`, `encoding`

## Exact Trigger Boost

Exact tag, category, or trigger phrase matches should be a strong boost.

This is stronger than a small ranking nudge but not a hard filter. The reason is that rule content is short, and many rule activations are explicit trigger-word matches rather than broad semantic matches.

Recommended behavior:

- If query exactly matches a rule tag or category, strongly boost that rule.
- If query contains a trigger phrase found in rule content, strongly boost that rule.
- If multiple trigger-word rules match, keep all strongest matches subject to the contextual total limit.

## Guaranteed Trigger Matches

When the query contains an explicit trigger word and one or more rules strongly match it:

- Guarantee those matched rules are included ahead of weaker contextual rules.
- They still count toward the contextual rule limit.
- They do not bypass the total output limit.

This prevents rules like `Igor`, `banana`, or `QR` from being pushed out by generic high-priority rules.

## Full RAG Decision

Do not implement full rule RAG yet.

Full RAG would mean a dedicated rule index with FTS/BM25, embeddings, representation refresh, and reranking. That is unnecessary while the active rule set is small.

Revisit full rule RAG when:

- Active rules exceed roughly 100.
- Full candidate scoring becomes slow.
- Rule tags become too hard to maintain.
- Recall evaluation shows semantic-only misses that tags cannot fix.

## Proposed Scoring Shape

The exact weights can be tuned during implementation, but the ranking should follow this shape:

```text
final_score =
  trigger_match_score
  + semantic_score
  + phase_match_score
  + category_match_score
  + priority_score
```

Recommended starting weights:

```text
trigger_match_score: 0.45
semantic_score:      0.30
phase_match_score:   0.10
category_match_score:0.10
priority_score:      0.05
```

Trigger score should distinguish:

- exact tag/category match
- query contains tag
- content phrase match

## Output Shape

Rule retrieval diagnostics should include:

```json
{
  "strategy": "always_on_plus_trigger_semantic_top_k",
  "candidate_count": 31,
  "always_on_count": 3,
  "contextual_count": 5,
  "trigger_matches": [
    {
      "rule_id": 19,
      "matched": ["igor", "伊戈尔"],
      "source": "tags"
    }
  ],
  "ranking_weights": {
    "trigger": 0.45,
    "semantic": 0.30,
    "phase": 0.10,
    "category": 0.10,
    "priority": 0.05
  }
}
```

Diagnostics are important because rule hit rate is still being tuned.

## Interaction With Rule Context Refresh

`rule_context_refresh` should call the improved retrieval path through `self_rules_context` or a shared internal helper.

Event policy remains defined in `2026-07-04-rule-context-refresh-design.md`.

Retrieval policy is defined here:

- no priority-limited preselection
- all user-selected `always_on` included
- all phase-eligible contextual rules scored
- trigger matches strongly boosted and guaranteed within contextual limits

## Tests

Required coverage:

- `always_on` rules are fetched outside the priority-limited path and all are returned.
- A low-priority but exact tag match can outrank high-priority generic rules.
- A query containing `Igor` returns the Igor rule.
- A query containing `banana` returns the banana/PPT rule.
- A query containing `QR` or `二维码` returns the QR rule.
- Phase-ineligible rules are excluded from contextual candidates.
- Phase-neutral rules remain eligible.
- Trigger matches count toward contextual limits.
- No `priority DESC LIMIT 20` candidate truncation is used for query-aware retrieval.
- Legacy no-query behavior remains compatible unless explicitly changed.

## Open Decisions

None. The next step is to update the implementation plan together with the rule context refresh design.

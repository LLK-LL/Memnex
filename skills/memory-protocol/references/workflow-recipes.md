# Workflow recipes

Ready-made flows for the most common situations. Copy the recipe,
substitute the concrete arguments. Each recipe shows:

- **Trigger** — when this fires
- **Steps** — the concrete sequence of MCP calls
- **Why this shape** — the reasoning behind the order
- **Anti-recipe** — what people do wrong

---

## R1. Session start — universal

**Trigger:** new chat / new terminal session / `claude` / `codex` /
Cursor reopen / etc.

```
1. session_init(project="<current>")
   → returns previous summary + next_steps + pitfalls (consumed)

2. rule_context_refresh(project="<current>", phase="<phase>", event="task_start", latest_user_instruction="<current task>")
   → load always-on rules plus query-ranked behavioural rules for this project

3. (if user references prior work) memory_recall(query=<from prompt>, project=...)
```

**Why this shape:** `session_init` must come *first* because it marks
its summary consumed; calling `memory_recall` first risks recalling
stale next-steps from the previous session as if they were facts.

**Anti-recipe:** "let me jump straight in" without `session_init` —
you will repeat work the previous session already finished.

---

## R2. Before any non-trivial task

**Trigger:** user says "implement X" / "fix Y" / "refactor Z" / "what's
the convention for ...".

```
1. memory_recall(query="<task description, specific>", project="<current>", limit=5)
2. If no hit → analogize(text="<task description>", exclude_project="<current>")
3. If still no hit → context7 (for libraries) → WebSearch → first principles
```

**Why this shape:** memory first (current project's recipe), then
sibling projects (cross-project analogy), then external docs. Skip
this and you reinvent a convention that's already in the corpus.

**Anti-recipe:** generic queries. `memory_recall(query="auth")` returns
noise. Be specific: `memory_recall(query="JWT refresh rotation in
symfony auth middleware")`.

---

## R3. Before edit / write to a file

**Trigger:** about to call `Edit`, `Write`, or any file-modifying tool.

```
1. file_context(path="/abs/path/to/file")
   → returns risk_score, warnings, hot_spots
2. If risk_score > 0.5: read warnings; consider whether the change is
   really safe given past errors on this path
```

**Why:** warnings include past `learn_error` records on the same path —
"three times someone broke this regex", "this function has a hidden
race with X". Free regression intelligence.

**Anti-recipe:** edit-and-pray. The hook (`pre-edit.sh`) automates this
when installed.

---

## R4. After a fix / bug solved

**Trigger:** any meaningful fix lands.

```
1. memory_save(
       type='solution',
       content='ЧТО: ...\nПРОЕКТ: ...\nФАЙЛЫ: ...:LINE\nСТЕК: ...\nПОДХОД: ...\nНЮАНСЫ: ...',
       project='<current>',
       tags=['reusable', '<tech>', '<bug-area>'],
       importance='high' if breaking else 'medium',
   )
```

If the bug is reproducible (you can see it again):
```
2. learn_error(
       file='<abs path>',
       error='<exact error message>',
       root_cause='<one sentence>',
       fix='<one sentence>',
       pattern='<short slug for grouping, e.g. argpartition-kth-bound>',
   )
```

**Why two calls:** `memory_save` is the recipe (how to fix it next time).
`learn_error` is the rule trigger — after 3 identical patterns it
auto-consolidates into a `self_rule` so future agents avoid the
mistake without recall.

**Anti-recipe:** "I'll save it later." You won't. Save now.

---

## R5. Architectural decision

**Trigger:** picking between options (DB engine, queue backend, lib).

```
1. memory_recall(query='<decision area>', project, decisions_only=true)
2. analogize(text='<decision area>', exclude_project='<current>')
3. (after decision is made):
   save_decision(
       title='Queue backend for X',
       options=[
           {"name": "PG LISTEN/NOTIFY", "pros": [...], "cons": [...]},
           {"name": "Redis Streams", "pros": [...], "cons": [...]},
       ],
       criteria_matrix={
           "infra cost": {"PG LISTEN/NOTIFY": 5, "Redis Streams": 3},
           "throughput": {"PG LISTEN/NOTIFY": 3, "Redis Streams": 5},
           ...
       },
       selected='PG LISTEN/NOTIFY',
       rationale='<one paragraph why>',
       project='<current>',
   )
```

**Why:** structured decisions with the criteria matrix are gold for
onboarding ("why did we pick X?") and surface as
`memory_recall(decisions_only=true)` filter.

**Anti-recipe:** unstructured `memory_save(type='decision', content='we chose X')`
without criteria. Six months later you can't reconstruct the trade-off.

---

## R6. Tech-stack / dependency / config change

**Trigger:** Postgres version bump, new framework, new env var, etc.

```
1. kg_add_fact(
       subject='<project or component>',
       predicate='uses' | 'depends_on' | 'configured_with',
       object='<Tool Version>',
       project='<current>',
   )
```

**Why:** old facts about the same `(subject, predicate)` auto-invalidate
via `valid_to`. Time-travel queries (`kg_at(timestamp)`) work
afterwards.

```
2. memory_save(type='fact', content='ЧТО: bumped X 17 → 18, миграция Y\n...')
```

If the bump triggered a migration / refactor:
```
3. save_decision(...) on the upgrade path itself.
```

**Anti-recipe:** only saving the human-readable note (`memory_save`).
The KG triple is what makes "what was the stack on 2026-04-15" answerable.

---

## R7. Stuck / 3 identical errors / contradicting sources

**Trigger:** three identical errors, three failed hypotheses, or
contradicting recall results.

```
1. STOP. Don't guess.
2. memory_save(
       type='lesson',
       content='STUCK: <symptom>\nTRIED: ...\nWHAT WORKED LAST TIME: ...',
       tags=['stuck', '<tech>'],
   )
3. AskUserQuestion (Claude Code) or plain question:
   "Three approaches failed. Which direction:
    (A) ... (B) ... (C) ..."
4. Optional: /ask-codex for a second opinion (Claude Code only).
```

**Why:** the save is a future signal — if the same situation comes back,
recall surfaces "you got stuck here last time, the answer was X".

**Anti-recipe:** keep guessing. After three failed attempts, additional
guesses get worse, not better.

---

## R8. End of session — "сохранись" / "save" / context approaching limit

**Trigger:** user says "сохранись" / "save" / "закругляемся"; context
auto-save hook fires; session is wrapping up.

```
1. memory_save (any pending records that weren't saved during work)
2. session_end(
       session_id='<current>',
       summary='2-4 sentences',
       next_steps=['concrete', 'actionable'],
       pitfalls=['watch out for X', 'don\'t Y'],
       open_questions=[...],
   )
3. Dual-write to Obsidian: append to
   ~/Documents/project/Projects/<project>/sessions/YYYY-MM-DD.md
   with [HH:MM] markers and [[wiki-links]]
   (skip if Obsidian vault not present)
```

**Why:** `session_end` is what the *next* session's `session_init` reads.
Skip it and the next session has no recovery context.

**Anti-recipe:** assuming "the recall will find it". Recall searches
content; `session_init` reads the structured handoff. Different paths.

---

## R9. Resuming a project — "продолжаем" / "resume"

**Trigger:** user says "продолжаем" / "resume" / "where did we leave off".

```
1. session_init(project='<current>')
   → returns prior summary + next_steps + pitfalls
2. memory_recall(query='<recent work>', project, limit=3, mode='index')
   → quick scan, not deep dig
3. (do NOT read Obsidian sessions/ — that's human-facing log, not the
    canonical state)
```

**Why:** Save = both systems (MCP + Obsidian).
Resume = MCP only. Obsidian is human-facing journal — reading it during
restore double-loads context.

**Anti-recipe:** `cat sessions/2026-04-27.md` to "remember what we did".
Reads twice, doesn't update memory.

---

## R10. Cross-project investigation — "we did this somewhere else"

**Trigger:** user references work on a sibling project, or you suspect
this problem was solved elsewhere.

```
1. memory_recall(query='...', project='<current>')   # local first
2. analogize(text='...', exclude_project='<current>') # then siblings
3. If a hit: read the recipe + verify the file/function still exists
   in the source project (memory is a claim, source is truth).
```

**Why:** `analogize` uses Jaccard similarity + Dempster-Shafer fusion
across all projects. It's the right tool for "have we seen this
before, anywhere".

**Anti-recipe:** searching with `memory_recall` without `project=` —
returns a mash of all projects, hard to read.

---

## R11. Indexing a new codebase

**Trigger:** opening a project for the first time, or a major refactor.

```
1. ingest_codebase(
       path='/abs/path/to/project',
       languages=['python', 'go', 'typescript'],
       project='<project name>',
   )
   → AST tree-sitter, builds graph_nodes + graph_edges
```

**Why:** cheaper than reading files line-by-line. Yields structured
nodes for `memory_graph(node='<name>')` queries afterwards.

**Anti-recipe:** building the graph by hand with `kg_add_fact` calls.
Use the indexer for bulk; `kg_add_fact` is for facts the indexer
can't see (decisions, deadlines, who-owns-what).

---

## R12. Performance regression — "saves got slow"

**Trigger:** `memory_save` taking longer than usual; user reports
30-second saves on WSL2.

```
1. memory_stats()                    # baseline
2. benchmark(scenarios=['recall', 'save'])  # baseline numbers

If save > 1s on macOS or > 5s on WSL2:
3. Set MEMORY_ASYNC_ENRICHMENT=true (see Performance tuning in README)
4. Restart MCP server
5. benchmark again
```

**Anti-recipe:** raising timeouts to mask slow LLM. Lower
`MEMORY_TRIPLE_MAX_PREDICT`, then async-enable, *then* bump
timeouts if still needed.

---

## R13. Sub-agent delegation

**Trigger:** spawning a sub-agent (`Agent(subagent_type='php-pro')`).

```
1. memory_recall(query='<task>', project='<current>')
2. Pass recalled recipes into sub-agent's prompt: "Context from prior
   sessions: <ids and one-line gist of each hit>".
3. (sub-agent runs.)
4. After sub-agent returns: memory_save(type='solution',
       tags=['reusable', '<tech>'])
   if the sub-agent produced a reusable result.
```

**Why:** sub-agents have memory access too, but the cheap way is to
hand them recalled context in the prompt rather than have them
re-search.

For the full sub-agent prompt header, see `subagent-protocol.md`.

**Anti-recipe:** spawning sub-agent without recalled context. It
re-discovers the same recipe at sub-agent cost.

---

## R14. Periodic reflection (weekly retro)

**Trigger:** end of week, end of sprint, after a release.

```
1. memory_timeline(limit=50)        # what happened
2. self_patterns(view='full_report', days=7)  # error patterns
3. memory_self_assess()             # corpus health + blind spots
4. self_reflect(
       reflection='<2-3 paragraphs of takeaways>',
       task_summary='week of <date>',
       outcome='success' | 'partial' | 'mixed',
   )
5. memory_consolidate()             # dedupe + decay
6. memory_wiki_generate(project='<current>')   # refresh digest
```

**Why:** the system gets smarter only if reflection happens
deliberately. The async worker handles per-save consolidation; the
weekly retro handles cross-save patterns.

**Anti-recipe:** never reflecting. The corpus accumulates noise; recall
quality degrades.

---

## R15. Privacy — secrets in content

**Trigger:** about to save content that contains a token, password,
PII, or anything you wouldn't paste in a public Slack.

```
1. Wrap secrets in <private>...</private> tags BEFORE save:

   memory_save(content='''
   ЧТО: configured Stripe webhook
   КЛЮЧ: <private>sk_test_4eC39...</private>
   ENDPOINT: https://api.example.com/webhook
   ''', ...)

2. memory_save's privacy_filter redacts the wrapped block before INSERT.
   Counter increments in privacy_counters table.
```

**Why:** the redactor is best-effort, not absolute. `<private>` is the
explicit guarantee. The endpoint URL above is fine to keep
unredacted (it's public surface).

**Anti-recipe:** trusting auto-detection. Don't paste the token raw.
Wrap it.

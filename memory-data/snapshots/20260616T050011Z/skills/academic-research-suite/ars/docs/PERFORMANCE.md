# ARS Performance Notes

> **Recommended model: Claude Opus 4.7** with **Max plan** (or equivalent configuration). Opus 4.7 uses adaptive thinking; you no longer set a fixed thinking budget.
>
# REDACTED: sensitive-looking memory line
>
> Individual skills (e.g., `deep-research` alone, or `academic-paper-reviewer` alone) consume significantly less.

# REDACTED: sensitive-looking memory line

# REDACTED: sensitive-looking memory line
|---|---|---|---|
| `deep-research` socratic | ~30K | ~15K | ~$0.60 |
| `deep-research` full | ~60K | ~30K | ~$1.20 |
| `deep-research` systematic-review | ~100K | ~50K | ~$2.00 |
| `academic-paper` plan | ~40K | ~20K | ~$0.80 |
| `academic-paper` full | ~80K | ~50K | ~$1.80 |
| `academic-paper-reviewer` full | ~50K | ~30K | ~$1.10 |
| `academic-paper-reviewer` quick | ~15K | ~8K | ~$0.30 |
| **Full pipeline (10 stages)** | **~200K+** | **~100K+** | **~$4-6** |
| + Cross-model verification | +~10K (external) | +~5K (external) | +~$0.60-1.10 |

*Estimates based on a ~15,000-word paper with ~60 references. Actual usage varies with paper length, revision rounds, and dialogue depth. Costs at Anthropic API pricing as of April 2026.*

## Recommended Claude Code settings

| Setting | What it does | How to enable | Docs |
|---|---|---|---|
# REDACTED: sensitive-looking memory line
| **Skip Permissions** | Bypasses per-tool confirmation prompts, enabling uninterrupted autonomous execution across all pipeline stages | Launch with `claude --dangerously-skip-permissions` | [Permissions](https://docs.anthropic.com/en/docs/claude-code/cli-reference) 路 [Advanced Usage](https://docs.anthropic.com/en/docs/claude-code/advanced) |

> **鈿狅笍 Skip Permissions**: This flag disables all tool-use confirmation dialogs. Use at your own discretion 鈥?it is convenient for trusted, long-running pipelines but removes the safety net of manual approval. Only enable this in environments where you are comfortable with Claude executing file reads, writes, and shell commands without asking first.

### v3.7.0 Plugin agents and model routing

# REDACTED: sensitive-looking memory line

# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line

# REDACTED: sensitive-looking memory line

# REDACTED: sensitive-looking memory line

# REDACTED: sensitive-looking memory line

The full academic pipeline is designed for human-in-the-loop execution, with mandatory user confirmation at every stage. In practice, a full run often spans hours to days 鈥?longer than Anthropic's prompt cache TTL (5 minutes). Two consequences:

1. **Cache misses between checkpoints are normal.** When a stage checkpoint pauses longer than 5 minutes, the next stage reads its context uncached. This is an unavoidable cost of human-paced pipelines.
# REDACTED: sensitive-looking memory line

### v3.6.2 Sprint Contract reviewer cost (always-on for `full` / `methodology-focus`)

The Schema 13 sprint contract gate splits each reviewer agent's run into Phase 1 (paper-content-blind, commits scoring plan) + Phase 2 (paper-visible review). For modes that ship templates (`full` panel 5 + `methodology-focus` panel 2), each reviewer therefore costs roughly two LLM turns instead of one. Reserved modes (`re-review` / `calibration` / `guided` / `quick`) keep pre-v3.6.2 behaviour.

# REDACTED: sensitive-looking memory line
|---|---|---|
| `academic-paper-reviewer full` | ~+30-40% input + small output bump per reviewer 脳 5 reviewers | Each reviewer reads the contract template + paper metadata in Phase 1, then full paper in Phase 2 |
| `academic-paper-reviewer methodology-focus` | Same shape, panel 2 | Two reviewers (EIC + methodology) each run two phases |
| Synthesizer (always one) | +~2-3K input | Reads contract + reviewer outputs to run three-step mechanical protocol |

Empirical measurement pending real review runs at scale. The two-phase shape is non-optional for the gated modes; treat as fixed overhead, not a tunable.

### v3.4.0 compliance agent cost

# REDACTED: sensitive-looking memory line

# REDACTED: sensitive-looking memory line
|---|---|---|---|
| `deep-research systematic-review` (2.5 only) | +~5鈥?K | +~3鈥?K | +~$0.15 |
| Full pipeline SR (2.5 + 4.5) | +~10鈥?5K | +~5鈥?K | +~$0.30 |
| `academic-paper full` (pre-finalize) | +~3鈥?K | +~2鈥?K | +~$0.08 |

These are on top of the existing per-skill costs in the table above (same 15,000-word / 60-reference basis; see footnote on line 23). Cross-model verification costs (if enabled) are unchanged.

### v3.6.3 Passport reset boundary (opt-in)

When `ARS_PASSPORT_RESET=1` is set, every FULL checkpoint becomes a context-reset boundary. The intended workflow is:

# REDACTED: sensitive-looking memory line
2. Copy the `[PASSPORT-RESET: hash=<hash>, stage=<completed>, next=<next>]` tag from the checkpoint notification.
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line

**When reset beats continuation:**

# REDACTED: sensitive-looking memory line
- `systematic-review` mode runs where stage independence is cleanly defined by the Material Passport.
- Any case where you hit the 5-minute prompt-cache TTL mid-pipeline; a reset lets the next stage start fresh instead of paying a cache miss on a bloated context.

**When continuation still wins:**

# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
- When the flag is OFF, continuation is the unchanged pre-v3.6.3 default.

**Passport file location convention:**

By default, the orchestrator looks for the passport file in `./passports/<slug>/` or matching `./material_passport*.yaml` relative to the current working directory. Resolving the hash to a passport file on disk is the integrator's responsibility; the orchestrator loads whichever passport the enclosing tool provides. See 搂"Passport file location convention" above for the `./passports/<slug>/` default.

The resume command only defines the hash and optional stage/mode overrides:

```
resume_from_passport=<hash> [stage=<n>] [mode=<m>]
```

There is no path syntax on the resume command itself. Custom passport locations are configured in the project's `CLAUDE.md` or handled by the integrator's tooling before the orchestrator is invoked.

# REDACTED: sensitive-looking memory line

## Literature corpus ingestion (v3.6.4+)

The Material Passport `literature_corpus[]` field is populated by user-written adapters, not ARS itself. Three reference adapters ship with v3.6.4: `scripts/adapters/folder_scan.py`, `scripts/adapters/zotero.py`, `scripts/adapters/obsidian.py`. See [`scripts/adapters/README.md`](../scripts/adapters/README.md) for how to run them and how to write your own.

### Performance posture

# REDACTED: sensitive-looking memory line
- Adapters must be deterministic: re-running on identical input produces byte-identical output modulo timestamps.
- `literature_corpus[]` entries are sorted by `citation_key`; rejections are sorted by `source`.
- Adapter output size grows linearly with corpus size. A 500-entry Zotero library typically produces a passport of ~300 KB YAML. ARS consumers should lazy-load when the corpus is large.

### Ingestion-layer boundaries

- Does not ingest PDFs, extract text, or run OCR.
- Does not call the Zotero Web API, Notion API, or any live service.
# REDACTED: sensitive-looking memory line

These boundaries are deliberate and reflect the ARS data-layer decision: ARS is a writing/review-layer framework; corpus integration stays in user-owned code. Users who want API-based live-sync adapters are expected to write them themselves, using the three reference adapters as starting points.

### Consumer-side integration

As of v3.6.5, two Phase 1 literature agents read `literature_corpus[]` via the **corpus-first, search-fills-gap** flow: `deep-research/agents/bibliography_agent.md` and `academic-paper/agents/literature_strategist_agent.md`. Both consumers follow the same five-step shared flow and four Iron Rules (Same criteria / No silent skip / No corpus mutation / Graceful fallback on parse failure). Search Strategy reports gain a PRE-SCREENED reproducibility block that enumerates included / excluded / skipped corpus entries with F3 zero-hit and F4 provenance reporting. Consumer integration is presence-based 鈥?auto-engages when the passport carries a non-empty `literature_corpus[]` and parses cleanly; parse failures fall back to external-DB-only flow with a `[CORPUS PARSE FAILURE]` surface.

See [`academic-pipeline/references/literature_corpus_consumers.md`](../academic-pipeline/references/literature_corpus_consumers.md) for the full consumer protocol. `citation_compliance_agent` corpus integration is deferred (target version TBD post-v3.8).

### v3.6.5 corpus consumer cost (presence-gated)

When the Material Passport carries a non-empty `literature_corpus[]`, Phase 1 reads scale with corpus size. The PRE-SCREENED block emit itself is prompt-layer (effectively free); the LLM cost is Step 1 pre-screening 鈥?applying the current Inclusion / Exclusion criteria to each corpus entry's `title` (always present) and any populated optional fields (`abstract` / `tags`).

| Corpus size | Step 1 pre-screening (per consumer) | Notes |
|---|---|---|
| Empty / absent | 0 | External-DB-only flow runs unchanged |
| ~50 entries (typical Zotero subset) | +~3-5K input + ~1-2K output | Title + abstract scan |
| ~200 entries | +~10-15K input + ~3-5K output | Title-only scan dominates; abstract scan only when populated |
| ~500 entries (large library) | +~25-40K input + ~8-12K output | Consider trimming the corpus before passport emit |

Step 2 search-fills-gap reduces external-DB cost when `uncovered_topics` is small (case A), which can offset Step 1 cost. Empirical net delta pending real systematic-review run instrumentation; until then, no aggregate numeric claim is made. Parse failures cost roughly one short turn (parse + emit `[CORPUS PARSE FAILURE]` + fall back).

## v3.6.7 Step 6 cross-model audit wrapper (onboarding)

v3.6.7 Step 6 ships `scripts/run_codex_audit.sh` and `scripts/parse_audit_verdict.py`, which dispatch a separate codex CLI process to audit `synthesis_agent`, `research_architect_agent` (survey-designer mode), and `report_compiler_agent` (abstract-only mode) deliverables before stage transitions. The wrapper is the boundary object between deployment-side audit execution and ARS-side artifact verification 鈥?see [spec 搂4](design/2026-04-30-ars-v3.6.7-step-6-orchestrator-hooks-spec.md) for the full contract.

# REDACTED: sensitive-looking memory line

The wrapper invokes `codex exec --json -m gpt-5.5 -c 'model_reasoning_effort="xhigh"'`. Required setup before first audit run:

| Step | macOS | Linux / WSL |
|---|---|---|
| Install codex CLI | `brew install codex` (or vendor installer) | vendor installer |
| Verify install | `codex --version` should print a `codex-cli X.Y.Z` line; the wrapper requires bare-semver match `^[0-9]+\.[0-9]+\.[0-9]+$` | same |
# REDACTED: sensitive-looking memory line
| Bash 3.2+ | stock macOS `/bin/bash` is supported by the Codex adapter | distro default usually 5.x |
| `jq` | `brew install jq` | distro package |
| `sha256sum` (optional 鈥?wrapper falls back to `shasum -a 256`) | `brew install coreutils` | preinstalled |

The wrapper preflights every dependency at startup (搂4.1 dependency table) and exits 64 (`EX_USAGE`) with `missing dependency: <name>` before touching any artifact file. No partial state is written when a dependency is missing.

### Required environment

| Variable | Required? | Purpose |
|---|---|---|
# REDACTED: sensitive-looking memory line
| Standard PATH containing `codex`, `git`, `jq`, `python3` | yes | wrapper preflight checks each |
| Working directory inside the ARS repo | yes | `git rev-parse --short HEAD` for `runner.git_sha`, repo-relative paths in sidecar |

The wrapper does NOT read any ARS-specific environment variables (no `ARS_*` flags affect Step 6). Audit dispatch is purely flag-driven.

### Threat-model boundary

Per [spec 搂1.2](design/2026-04-30-ars-v3.6.7-step-6-orchestrator-hooks-spec.md), Step 6 defends against Pattern C3 (sub-agent fabricated audit metadata, where a downstream agent claims to have run audit and surfaces simulated findings). The artifact-as-contract design closes the inadvertent-overclaim attack surface: the wrapper produces four cryptographically-pinned files (jsonl + sidecar + verdict + proposal entry), and the orchestrator runs eleven layered verification checks before merging any audit outcome into the Material Passport.

Step 6 is **known-insufficient against motivated forgery** (a determined attacker with shell access could invoke codex with a different model and the JSONL stream alone would not betray them 鈥?see 搂9.1 R2). Two structural mitigations apply:

# REDACTED: sensitive-looking memory line
- **Lifecycle ownership (搂3.7 family E).** The wrapper writes only to `--output-dir`, never to the passport file. The orchestrator is the sole writer of `audit_artifact[]` entries. A wrapper-emitted proposal carrying `verdict.verified_at` or `verdict.verified_by` is rejected as malformed at lifecycle step 4 (Pattern C3 attack surface).

Deployment-side discipline is the load-bearing defense for the residual motivated-forgery surface; ARS spec-level enforcement is the partial inversion of the three downstream agent prompts (搂6) so the agent has no awareness that a downstream audit exists, removing the trigger for fabricated tool-call hallucination.

### Wrapper exit-code contract

The wrapper's process exit code always agrees with the verdict it just wrote (搂4.6):

| Exit code | Meaning | Verdict status | Orchestrator response |
|---|---|---|---|
| `0` | Audit completed cleanly | `PASS` / `MINOR` / `MATERIAL` | Read verdict, run 搂5.2 eleven gating checks, ship or block per 搂5.3 |
| `64` (`EX_USAGE`) | Input validation failed | none (no files written) | Block, surface `<missing flag>` error to user |
| `70` (`EX_SOFTWARE`) | codex itself exited 70 OR `parse_audit_verdict.py --probe` rejected JSONL OR bundle TOCTOU mutation detected | `AUDIT_FAILED` (with `failure_reason`) | 搂5.6 Path B5 short-circuits to BLOCK without gating |
| `73` (`EX_CANTCREAT`) | Tee write failed (disk full / EIO) | none / partial (cleaned up) | Block, surface filesystem error |
| `75` (`EX_TEMPFAIL`) | codex rate-limited OR SIGTERM/SIGINT received | `AUDIT_FAILED` | Same as 70: BLOCK without gating; deployment may apply backoff before retry |
| Other non-zero (1, 2, 137, 鈥? | codex exited with a code not enumerated above; wrapper preserves the code rather than normalizing | `AUDIT_FAILED` | Same as 70: BLOCK without gating |

Even on AUDIT_FAILED, the wrapper writes all four contract files (jsonl placeholder + sidecar with `process.exit_code` carrying codex's actual exit + verdict.yaml carrying `status: AUDIT_FAILED` + proposal entry) so orchestrator can distinguish "audit ran but failed" (proposal exists with `AUDIT_FAILED`) from "audit never ran" (no proposal at all). Both states block transition; only `PASS / MINOR / MATERIAL` proposals reach the eleven gating checks.

### Cost posture

A typical Phase 2 chapter audit (synthesis + verification + bibliography bundle) runs codex `gpt-5.5` at `xhigh` reasoning effort for 30-90 seconds wall-clock per round. ARS-side cost is constant: the wrapper adds ~1-2 KB of metadata (sidecar + proposal entry) per audit run regardless of bundle size; the orchestrator's eleven-gate verification is sub-second per audit. The dominant cost is codex API usage on the deployment side, governed by audit template Section 1's three-round convergence target (搂10 ship-quality target update).

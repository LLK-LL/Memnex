# Passport as Reset Boundary (v3.6.3)

## Purpose

# REDACTED: sensitive-looking memory line

## When this protocol applies

| Flag state | Mode | Behavior at FULL checkpoint |
|------------|------|-----------------------------|
| `ARS_PASSPORT_RESET` unset / `=0` | any | Continuation (pre-v3.6.3 default). No reset tag emitted. |
| `ARS_PASSPORT_RESET=1` | `systematic-review` | **Mandatory reset** at every FULL checkpoint. |
| `ARS_PASSPORT_RESET=1` | any other mode | **Strong-default reset** at every FULL checkpoint. User `continue` response overrides back to continuation for the next stage only. |

MANDATORY checkpoints (integrity Stage 2.5 / 4.5, review decisions, Stage 5 finalization) are orthogonal: reset can co-occur with MANDATORY. SLIM checkpoints never trigger reset.

## The reset boundary protocol

When the orchestrator reaches a FULL checkpoint with the flag ON:

1. **Freeze state.** `state_tracker` stages the current stage's deliverables and prepares a new `kind: boundary` ledger entry 鈥?but does NOT yet write `hash` (append happens in Step 2 after hash is known).
2. **Compute hash.** Canonical byte serialization is normative; two implementations must produce the same bytes from the same ledger:
   - Each entry is serialized as **JSON Canonical Form (RFC 8785 / JCS)**: UTF-8, no insignificant whitespace, keys sorted ASCII-ascending at every object level, numbers in JCS canonical form.
   - Entries are separated by a single `\x0a` (LF) byte. The first entry has no leading separator; the last entry has a trailing LF.
   - The new entry is serialized with `hash` set to the canonical placeholder `"000000000000"` and all other fields populated; concatenated AFTER every prior entry (each already carrying its own finalized `hash`).
   - SHA-256 the byte stream. Take the lowercase hex digest. Take the first 12 characters. That IS the new entry's `hash`. Overwrite the placeholder before appending to the ledger.
   - **Iron rule (see 搂Iron rules 2 + 7):** never hash an entry that already contains a non-placeholder `hash` for itself; never reorder prior entries; never include `kind: resume` entries in a boundary hash computation.
3. **Emit reset tag.** In the checkpoint notification block, append a machine-stable line:
   ```
   [PASSPORT-RESET: hash=<hash>, stage=<completed>, next=<next>]
   ```
4. **Emit human instruction.** In the same checkpoint notification, include a `### Resume Instruction` subsection with:
   - Passport file path (absolute or repo-relative)
# REDACTED: sensitive-looking memory line
     ```
     resume_from_passport=<hash>
     ```
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
8. **Pending MANDATORY decision.** If the reset co-occurs with a MANDATORY checkpoint that requires a user decision with multiple valid branches (e.g., Stage 3 review outcome: `revise` / `restructure` / `abort`; Stage 5 finalization format choice), the orchestrator sets `pending_decision` on the ledger entry. Each option is an object with required fields `value` (branch identifier) and `next_stage` (stage to route to, or `null` to terminate), plus optional `next_mode` for downstream mode override. On resume, the orchestrator looks up the user's chosen `value` in `options[]` and uses that entry's `next_stage`/`next_mode` to determine actual routing. The boundary entry's `next` field is populated as a best-guess default only; it is advisory and is superseded by the matched option's `next_stage` at resume time. `next` must NOT be used to auto-advance when `pending_decision` is present. `next` MAY be `null` when all branches of `pending_decision` terminate or when no sensible default exists.

## `resume_from_passport` mode contract

# REDACTED: sensitive-looking memory line

```
resume_from_passport=<hash> [stage=<stage_number_or_name>] [mode=<downstream_mode>]
```

Required:
# REDACTED: sensitive-looking memory line

Optional:
- `stage=<stage_number_or_name>` 鈥?override the `next=` recorded in the reset tag. Useful when the user wants to re-run a stage rather than proceed. If omitted, the orchestrator uses `next=` from the reset tag.
- `mode=<downstream_mode>` 鈥?override the mode of the next stage (e.g., swap `full` for `quick`). Orchestrator validates the override against Mode Advisor rules.

Orchestrator obligations on resume:
- Locate the target `kind: boundary` entry by matching `hash`. Hard error if no match, or if a later `kind: resume` entry already carries `consumes_hash == <hash>` (double-resume is forbidden).
# REDACTED: sensitive-looking memory line
- Honor the `verification_status` field. If `STALE` or `UNVERIFIED`, display a warning and prompt the user to re-verify before continuing. If `VERIFIED`, proceed without prompting.
- If `pending_decision` is set on the ledger entry, re-prompt the user for that decision BEFORE invoking any downstream stage. Display `pending_decision.question` and each option's `value`. After the user picks, look up the matching entry in `options[]` by `value`, then use that entry's `next_stage` and `next_mode` to determine actual routing. Record the chosen `value` as `chosen_branch` on the new `resume` entry. `next` on the boundary entry is advisory and is superseded by the matched option's `next_stage`. A user-supplied `stage=<n>` override on the resume command does NOT satisfy `pending_decision` 鈥?the decision prompt always fires when `pending_decision` is present. CLI `stage=`/`mode=` overrides still win over option routing if the user supplies them after the decision prompt.
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line

## Append-only ledger semantics

Material Passport ledger (`compliance_history[]` + new `reset_boundary` entries) is append-only:
- Every checkpoint with the flag ON appends one `reset_boundary` entry of kind `boundary` under Schema 9's `reset_boundary` field.
- Re-running a stage (e.g., after a review rejection) appends a new entry with `version_label` bumped (`v1.0 鈫?v1.1-revised`).
- `resume_from_passport` consumption appends one entry of kind `resume` to the same ledger, carrying the `consumes_hash` pointer to the `boundary` entry it resolves. This is how resume leaves a trace 鈥?no mutation of prior entries.
- Prior entries are never deleted, reordered, or mutated.
- Stage-re-run cases produce adjacent entries for the same `stage`; both are preserved.

### Computing `awaiting_resume` from the ledger

A `boundary` entry with hash `H` is considered **awaiting resume** iff no `resume` entry exists later in the ledger with `consumes_hash == H`. Downstream readers (state machine, observers, external audit tools) compute this by a single pass over `reset_boundary[]` 鈥?no out-of-band state required.

## Concurrency model

Resume consumption is a three-step read-modify-write on the passport ledger:

1. Read the ledger and locate the target `boundary` entry by `hash`.
2. Verify no `resume` entry later in the ledger carries `consumes_hash` equal to that hash.
3. Append a new `resume` entry.

Without coordination, two processes can complete step 2 in parallel before either reaches step 3, both observe "no prior resume", and both append. The append-only-ledger invariant survives, but the "one boundary, one resume" invariant breaks. To prevent this, every compliant orchestrator implementation MUST hold an exclusive advisory lock on the passport file for the entire read-check-append sequence.

**POSIX requirement.** On POSIX systems the lock is an `fcntl` exclusive advisory lock (`fcntl.flock(fd, fcntl.LOCK_EX)` in Python, `flock(fd, LOCK_EX)` in C). Acquire before step 1, release after step 3. Do not release between steps under any circumstance. Releasing between steps 2 and 3 reopens the exact race this rule prevents.

# REDACTED: sensitive-looking memory line

**Non-POSIX (Windows).** `fcntl` is unavailable. Compliant implementations use `msvcrt.locking` with `LK_NBLCK`/`LK_LOCK`, or a cross-platform library like `portalocker`. Implementations that cannot provide OS-level exclusion MUST fail loudly on resume with a "concurrency protection unavailable on this platform" error and refuse to consume the boundary. Silent best-effort is forbidden.

**Observability.** The lock is advisory: external readers that don't honor the protocol can still read the passport. Only cooperating writers get safety. This is acceptable because the passport is intended to be consumed by one tool family (ARS-compatible orchestrators).

## Iron rules

1. Flag OFF is pre-v3.6.3 behavior, bit-for-bit.
2. Ledger is append-only. No exception, no "clean up" operation.
3. Reset tag is the sole machine-stable handoff. Human-readable `### Resume Instruction` is for user ergonomics; consumers parse the tag.
# REDACTED: sensitive-looking memory line
5. Hash mismatch on resume is a hard error; orchestrator never proceeds on a guessed or coerced hash.
6. MANDATORY checkpoints are not downgraded by reset; they co-occur.
7. Hash is computed over the entry with the canonical placeholder `"000000000000"` in the `hash` field, serialized per the byte rules in 搂"The reset boundary protocol" step 2. `kind: resume` entries are never included in a `boundary` hash computation 鈥?the hash covers only prior `boundary` entries plus the new boundary entry itself. Any other convention (exclude-field, variable-length placeholder, post-hoc mutation, including resume entries) breaks cross-implementation interoperability and is forbidden.
8. A `boundary` entry is "consumed" only by appending a `resume` entry with matching `consumes_hash`. If a `boundary` entry has `pending_decision` set, the orchestrator MUST re-prompt the user on resume and MUST NOT auto-advance using `next`. Each option in `pending_decision.options[]` carries its own routing (`next_stage`/`next_mode`); the boundary entry's `next` field is advisory only and MAY be `null` when all branches terminate or no sensible default exists. Actual routing on resume comes from the matched option's `next_stage`/`next_mode`, not from the boundary `next` field.
9. Resume consumption MUST hold an exclusive advisory lock on the passport file for the entire read-check-append sequence. Releasing the lock between the no-prior-resume check and the resume-entry append reopens the double-resume race the rule exists to prevent. Non-POSIX implementations that cannot provide OS-level exclusion MUST refuse to resume rather than degrade silently.

## Interaction with existing features

# REDACTED: sensitive-looking memory line
- **Compliance agent (v3.4.0):** `compliance_history[]` remains append-only and is consumed from the passport on resume. No change to Schema 12.
- **Sprint contract (v3.6.2):** reviewer sprint contracts load from the passport on resume (Phase 1 paper-content-blind stage remains valid across the reset boundary because the contract + paper metadata are carried in the passport).
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line

## What this protocol does NOT do

- Does not define Zotero / Obsidian / folder-scan adapter shapes (defined in [`academic-pipeline/references/adapters/overview.md`](adapters/overview.md) from v3.6.4+).
- Does not define `literature_corpus` entry shape (defined in [`shared/contracts/passport/literature_corpus_entry.schema.json`](../../shared/contracts/passport/literature_corpus_entry.schema.json) from v3.6.4+).
- Does not add runtime CLI tooling. Passport resolution is the user's responsibility 鈥?the orchestrator loads from the path the user provides.
# REDACTED: sensitive-looking memory line

## Related references

- [`shared/handoff_schemas.md`](../../shared/handoff_schemas.md) 鈥?Schema 9 definition
- [`academic-pipeline/agents/pipeline_orchestrator_agent.md`](../agents/pipeline_orchestrator_agent.md) 鈥?orchestrator integration
- [`academic-pipeline/references/pipeline_state_machine.md`](pipeline_state_machine.md) 鈥?state transitions
# REDACTED: sensitive-looking memory line

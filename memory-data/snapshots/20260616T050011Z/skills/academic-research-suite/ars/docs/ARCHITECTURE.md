# ARS Codex Pipeline Architecture (tracks ARS v3.9.4.2)

Full pipeline view across stages 脳 workflows 脳 artifacts 脳 gates for the
Codex package. The research logic is inherited from upstream ARS, but runtime
packaging is different: Codex installs one router skill at
`skills/academic-research-suite/SKILL.md`, then reads the vendored workflow
files under `ars/`.

Every completed stage requires a user-confirmation checkpoint (per
`academic-pipeline/WORKFLOW.md` and `pipeline_state_machine.md`); the diagrams
below surface the **decision-heavy** checkpoints visually so they are easy to
locate. The post-stage confirmation checkpoints at 2.5 and 4.5 are
machine-verified first, then confirmed by the user 鈥?they are not skipped.

## Codex Runtime Overlay

This file describes the logical ARS architecture, not Claude Code plugin
mechanics. Apply these Codex mappings when reading the diagrams and matrices:

| Upstream / diagram term | Codex package behavior |
|---|---|
| `deep-research`, `academic-paper`, `academic-paper-reviewer`, `academic-pipeline` as separate skills | Vendored workflows selected by the single `$academic-research-suite` router |
| `/ars-*` slash commands | Emulated by `ars-*` aliases handled in the router; not native Codex slash commands |
| Vague paper topic without a clear RQ | Router starts with `deep-research` `socratic` mode before outline, drafting, or full pipeline execution |
| Agent Team / agent dispatch | Agent markdown files are role prompts run inline unless the user explicitly asks for delegated or parallel agents |
| Plugin agents and `model: inherit` | Preserved as upstream metadata; Codex uses the active model |
# REDACTED: sensitive-looking memory line
| Cross-model GPT/Gemini dispatch | Disabled in this package; optional external review uses Anthropic Claude Opus 4.7 only when explicitly configured |
| Git-history-derived v3.6.7 block baseline | Uses upstream Git history when available; falls back to `scripts/codex_v3_6_7_block_baseline.json` during first-time Codex vendoring so protected-block mutation tests remain active before the initial vendor commit |

## How to read

- **Flow diagram** (搂2): macro view 鈥?which stage follows which, where loops exist, where gates block. Every rectangle ends in a post-stage user confirmation (elided for readability); decision markers call out the moments where the user chooses a branch.
- **Matrix** (搂3): the only place where (stage 脳 workflow 脳 mode 脳 data_level 脳 artifacts 脳 agent prompts 脳 gate) all co-exist. Use this when asking "what happens at Stage X?" The Gate column lists both machine checks and the user-confirmation checkpoint that closes the stage.
- **Data access flow** (搂4) and **skill graph** (搂6): orthogonal views answering "who sees what" and "who depends on what" respectively.
- **Literature corpus flow** (搂5): producer/consumer view of the optional Material Passport `literature_corpus[]` input port (v3.6.4) and Phase 1 consumer integration (v3.6.5).
- **Quality gates** (搂7): zoom on the blocking checks 鈥?both machine-enforced and human-enforced.
- **Timeline** (搂8): why the architecture looks the way it does 鈥?each release added one honesty primitive or a new contract.
- **Modes** (搂9): reference when composing a pipeline invocation or a Codex
  `ars-*` alias request.

The matrix alone is insufficient: it hides data-access hierarchy and skill dependency. The diagrams alone are insufficient: they hide artifact flow and per-stage agent detail. Together they are the full architecture.

## 1. Checkpoints (at-a-glance)

The pipeline has **two classes of user checkpoint**. Both require the user to confirm before the pipeline advances; they differ in what the user is actually deciding.

**Decision-heavy checkpoints** 鈥?the user chooses a branch or accepts a material decision:

| # | Stage | What the user decides |
|---|---|---|
| 馃 1 | 1. RESEARCH | RQ Brief + Methodology Blueprint |
| 馃 2 | 2. WRITE | Outline approval before drafting |
| 馃 3 | 3. REVIEW | Editorial decision (Accept / Minor / Major / Reject) |
| 馃 4 | 3 鈫?4 Revision Coaching | Revision strategy (up to 8 Socratic rounds; user can skip) |
| 馃 5 | 4. REVISE | Revision changes confirmed |
| 馃 6 | 3'. RE-REVIEW | Verification-review decision |
| 馃 7 | 3' 鈫?4' Residual Coaching | Residual-issue trade-offs (up to 5 Socratic rounds; user can skip) |
| 馃 8 | 4'. RE-REVISE | Content frozen 鈥?no further review loop |
| 馃 9 | 5. FINALIZE | Output format selection (MD / DOCX / LaTeX / PDF) |
| 馃 10 | 6. PROCESS SUMMARY | Language confirmation + collaboration quality review |

**Post-stage confirmation checkpoints** 鈥?machine verification runs first; the user then acknowledges the integrity report before proceeding. These are also user-gated (per `pipeline_state_machine.md` 鈥?every stage ends in `[checkpoint]`), but the decision is "acknowledge the automated report" rather than "choose a branch":

| # | Stage | What runs | What the user acknowledges |
|---|---|---|---|
| 鉁?1 | 2.5 INTEGRITY | 7-mode failure checklist (see 搂3 for exact taxonomy) | Integrity Report PASS/FAIL + any SUSPECTED flags |
| 鉁?2 | 4.5 FINAL INTEGRITY | Deep Mode 2 check, zero-tolerance | Final Integrity Report PASS + populated Material Passport |

## 2. Pipeline Flow

```mermaid
flowchart TD
    Start([User input])
    S1[1. RESEARCH<br/>馃 deep-research<br/>馃憗 observer]
    S2[2. WRITE<br/>馃 academic-paper<br/>馃憗 observer]
    G25{{2.5 INTEGRITY<br/>鉁?7-mode checklist<br/>then user ack<br/>鈥?observer SKIPPED}}
    S3[3. REVIEW<br/>馃 academic-paper-reviewer<br/>馃憗 observer]
    D3{Decision}
    RC[馃 3鈫? Revision<br/>Coaching<br/>max 8 rounds]
    S4[4. REVISE<br/>馃 academic-paper<br/>馃憗 observer]
    S3p[3'. RE-REVIEW<br/>馃<br/>馃憗 observer]
    D3p{Decision}
    RS[馃 3'鈫?' Residual<br/>Coaching<br/>max 5 rounds]
    S4p[4'. RE-REVISE<br/>馃 content frozen<br/>馃憗 observer]
    G45{{4.5 FINAL INTEGRITY<br/>鉁?Mode 2 deep check<br/>then user ack<br/>鈥?observer SKIPPED}}
    S5[5. FINALIZE<br/>馃 format selection]
    S6[6. PROCESS SUMMARY<br/>馃<br/>馃憗 observer<br/>pipeline-completion dispatch]
    End([Done])

    Start --> S1 --> S2 --> G25
    G25 -- PASS --> S3
    G25 -- FAIL, max 3 retries --> S2
    S3 --> D3
    D3 -- Accept --> G45
    D3 -- Minor / Major --> RC --> S4
    D3 -- Reject --> End
    S4 --> S3p --> D3p
    D3p -- Accept / Minor --> G45
    D3p -- Major --> RS --> S4p
    S4p --> G45
    G45 -- PASS --> S5
    G45 -- FAIL --> S4p
    S5 --> S6 --> End

    classDef humanGate fill:#fff1f0,stroke:#cf1322,stroke-width:3px
    classDef integrityGate fill:#fff4e6,stroke:#d48806,stroke-width:2px
    classDef coaching fill:#fcffe6,stroke:#7cb305,stroke-width:2px
    classDef decision fill:#f9f0ff,stroke:#9254de
    class S1,S2,S3,S4,S3p,S4p,S5,S6 humanGate
    class G25,G45 integrityGate
    class RC,RS coaching
    class D3,D3p decision
```

**Legend:**
- **Solid red (馃)** = decision-heavy human gate 鈥?the user chooses a branch or approves a material decision.
- **Solid orange (鉁?** = integrity gate 鈥?machine verification runs first, user then acknowledges the report. Not skipped.
- **Green** = Socratic coaching sub-stage. User may engage or say "just fix it" to skip the dialogue.
- **馃憗 observer** (v3.5.0) = `collaboration_depth_agent` dispatches at every FULL/SLIM checkpoint + pipeline completion. **Never blocks.** Advisory only. MANDATORY integrity gates (2.5 / 4.5) explicitly skip the observer so compliance checks are not diluted.

## 3. Stage 脳 Dimension Matrix

| Stage | Workflow / Mode | Data level | Artifact produced | Core agent prompts | Gate / Checkpoint |
|---|---|---|---|---|---|
| **1. RESEARCH** | `deep-research` v2.9.2 (full / socratic / lit-review / systematic-review / fact-check / review / quick) | RAW | RQ Brief; Methodology Blueprint; Annotated Bibliography (S2-verified); Synthesis Report; INSIGHT Collection. **Search Strategy report includes PRE-SCREENED block (v3.6.5)** when Material Passport carries `literature_corpus[]` | research_question_agent; research_architect_agent; **馃摎 bibliography_agent (v3.6.5+ corpus reader 鈥?corpus-first / search-fills-gap flow)**; source_verification_agent; synthesis_agent; meta_analysis_agent; editor_in_chief_agent; devils_advocate_agent; risk_of_bias_agent; ethics_review_agent; **馃煢 socratic_mentor_agent (v3.5.1 reading-check probe layer, opt-in)**; report_compiler_agent; monitoring_agent (13 agents); **馃憗 collaboration_depth_agent (v3.5.0, advisory)** | 馃 **Decision-heavy checkpoint:** user confirms RQ brief + methodology. Machine checks: S2 API Tier-0 verification (Levenshtein 鈮?0.70); evidence hierarchy graded; anti-sycophancy on DA (score 1-5, concede only 鈮?4); **corpus-first flow with 4 Iron Rules + F3/F4 provenance reporting (v3.6.5)** when corpus present. 馃憗 Observer runs post-checkpoint; never blocks |
| **2. WRITE** | `academic-paper` v3.1.1 (full / plan / outline-only / lit-review / revision-coach / abstract-only / citation-check / disclosure / format-convert / revision) | REDACTED | Paper Configuration Record; Outline; Argument Map; Draft Text; Bilingual Abstract; Figures + Captions; Citation List. **Literature Search Report includes PRE-SCREENED block (v3.6.5)** when Material Passport carries `literature_corpus[]`; merged `final_included` set feeds the Literature Matrix and Research Gap Identification | 12-agent pipeline: intake_agent; **馃摎 literature_strategist_agent (v3.6.5+ corpus reader 鈥?corpus-first / search-fills-gap flow)**; structure_architect_agent; argument_builder_agent; draft_writer_agent; citation_compliance_agent; abstract_bilingual_agent; peer_reviewer_agent; formatter_agent; socratic_mentor_agent; visualization_agent; revision_coach_agent; **馃憗 collaboration_depth_agent (v3.5.0, advisory)** | 馃 **Decision-heavy checkpoint:** outline approved before drafting. Machine checks: anti-leakage protocol (unsupported fill 鈫?`[MATERIAL GAP]`); VLM figure verification (10-pt APA checklist, max 2 refinements); style calibration vs user voice; Stage 2 parallelization (Phase 1 + visualization after outline); **corpus-first flow with 4 Iron Rules + F3/F4 provenance reporting (v3.6.5)** when corpus present. 馃憗 Observer runs post-checkpoint; never blocks |
| **2.5 INTEGRITY** | `academic-pipeline` v3.8.0 (gate) | VERIFIED_ONLY | Material Passport (Schema 9, required) + `repro_lock` (v3.3.5, declared 鈥?populated or `null`); Claim Verification Report (pre-review sampling: 30% of claims, min 10 鈥?per `claim_verification_protocol.md`); Data Provenance Audit | integrity_verification_agent; state_tracker_agent; pipeline_orchestrator_agent. **馃憗 collaboration_depth_agent: SKIPPED (MANDATORY gate 鈥?observer dilution explicitly prevented)** | 鉁?**Integrity gate** + user ack. 7-mode AI failure checklist (Lu 2026, canonical order per `ai_research_failure_modes.md`): **M1** implementation bug passing AI self-review; **M2** hallucinated citation; **M3** hallucinated experimental result; **M4** shortcut reliance; **M5** implementation bug reframed as novel insight; **M6** methodology fabrication; **M7** frame-lock at early pipeline stage. Pre-review claim sampling mode. FAIL 鈫?fix + re-verify (max 3 rounds) |
| **3. REVIEW** | `academic-paper-reviewer` v1.9.0 (full / guided / quick / methodology-focus / calibration) | VERIFIED_ONLY | **First-round review package** (per `academic-paper-reviewer/WORKFLOW.md`): 5 review reports (EIC + R1 methodology + R2 domain + R3 interdisciplinary + Devil's Advocate) + Editorial Decision (Accept / Minor / Major / Reject) + Revision Roadmap. **v3.6.2 Schema 13 Sprint Contract (`shared/sprint_contract.schema.json`) is required** for `full` and `methodology-focus` modes (other modes reserved with pre-v3.6.2 behaviour). | field_analyst_agent (auto-detects domain, configures 3 field-adaptive reviewers); eic_agent; methodology_reviewer_agent; domain_reviewer_agent; perspective_reviewer_agent; devils_advocate_reviewer_agent; **馃敀 editorial_synthesizer_agent (v3.6.2 three-step mechanical protocol + forbidden-ops list)** (7 agents); **馃憗 collaboration_depth_agent (v3.5.0, advisory)** | 馃 **Decision-heavy checkpoint:** user reviews editorial decision. Machine checks: concession threshold protocol (DA rebuttal scored 1-5, no concede below 4); attack intensity preserved through revisions; cross-model DA critique (optional, `ARS_CROSS_MODEL` env); read-only constraint (no new claims). **v3.6.2 Sprint Contract two-phase protocol**: each reviewer runs paper-content-blind Phase 1 (commits scoring plan) then paper-visible Phase 2 via `<phase1_output>` data delimiter; synthesizer runs three-step mechanical protocol (build matrix 鈫?evaluate with panel-relative quantifier 鈫?resolve precedence by severity). Validated by `scripts/check_sprint_contract.py`. 馃憗 Observer runs post-checkpoint; never blocks |
| **3 鈫?4 Revision Coaching** | `academic-paper-reviewer` (EIC Socratic sub-stage) | VERIFIED_ONLY | Revision strategy dialogue (not an artifact handed forward; feeds Stage 4 revision plan) | eic_agent | 馃 **Decision-heavy checkpoint:** Socratic dialogue with EIC (max 8 rounds). User may say "just fix it for me" to skip. Source: `two_stage_review_protocol.md` |
| **4. REVISE** | `academic-paper` v3.1.1 (revision / revision-coach) | REDACTED | Point-by-Point Response; Revised Draft; Delta Report (what changed + why) | revision_coach_agent (v3.3 Socratic mode); draft_writer_agent (re-entry); argument_builder_agent (if structural); **馃憗 collaboration_depth_agent (v3.5.0, advisory)** | 馃 **Decision-heavy checkpoint:** user confirms changes. Machine checks: score trajectory tracked per rubric dimension (v3.3) 鈥?revisions that regress a dimension are flagged. 馃憗 Observer runs post-checkpoint; never blocks |
# REDACTED: sensitive-looking memory line
| **3' 鈫?4' Residual Coaching** | `academic-paper-reviewer` (EIC Socratic sub-stage) | VERIFIED_ONLY | Residual-issue dialogue | eic_agent | 馃 **Decision-heavy checkpoint:** Socratic dialogue on trade-offs for residual issues (max 5 rounds). User may skip. Source: `two_stage_review_protocol.md` |
| **4'. RE-REVISE** | `academic-paper` v3.1.1 (revision) | REDACTED | Final Revised Draft (terminal; advances to 4.5) | draft_writer_agent; revision_coach_agent; **馃憗 collaboration_depth_agent (v3.5.0, advisory)** | 馃 **Decision-heavy checkpoint:** user confirms content frozen. No further review loop permitted. 馃憗 Observer runs post-checkpoint; never blocks |
| **4.5 FINAL INTEGRITY** | `academic-pipeline` v3.8.0 (gate) | VERIFIED_ONLY | Updated Material Passport (`verification_status: VERIFIED`) + `repro_lock` declared 鈥?populated or explicit `null` (honest opt-out); Claim Verification Report (**final-check mode: 100% of claims** per `claim_verification_protocol.md`) | integrity_verification_agent (deeper re-run of 7 modes); state_tracker_agent. **馃憗 collaboration_depth_agent: SKIPPED (MANDATORY gate 鈥?observer dilution explicitly prevented)** | 鉁?**Integrity gate** + user ack. **Zero-tolerance on the 7-mode re-run; no skip permitted.** Any mode SUSPECTED at 2.5 must be CLEAR or user-Overridden by 4.5. `repro_lock` is **not** read by the integrity gate at runtime (per `artifact_reproducibility_pattern.md`); if populated, `stochasticity_declaration` must be verbatim and is validated by the standalone `check_repro_lock.py` 鈥?this is post-hoc documentation, not a runtime block |
| **4鈫? CLAIM-AUDIT** (v3.8, opt-in via `ARS_CLAIM_AUDIT=1`) | `academic-pipeline` v3.8.0 (gate) | VERIFIED_ONLY | `claim_audit_results[]` + `claim_drifts[]` + `uncited_assertions[]` + `constraint_violations[]` + `audit_sampling_summaries[]` aggregates; reads `claim_intent_manifests[]` (writer-side pre-commitment baseline). Emits 5 HIGH-WARN annotation classes consumed by Stage 5 formatter REFUSE rules 6-10 | claim_ref_alignment_audit_agent (Stage 4鈫? dispatch slot, after v3.7.1 cite finalizer, before formatter hard gate) | 鉁?**Audit gate** (default OFF for v3.8.0). Per-citation LLM-as-judge against retrieved excerpt; 8-row finalizer matrix discriminates paywall (LOW-WARN) / fabricated (HIGH-WARN) / anchorless (HIGH-WARN) / audit_tool_failure (MED-WARN) via `ref_retrieval_method`. Calibration runner (`scripts/test_claim_audit_calibration.py`) gates with FNR<0.15 + FPR<0.10 on the shipped 20-tuple gold set. Spec: `docs/design/2026-05-15-issue-103-claim-alignment-audit-spec.md` |
| **5. FINALIZE** | `academic-paper` v3.1.1 (format-convert / disclosure) | VERIFIED_ONLY | Publication-ready MD; DOCX (Pandoc, if available); LaTeX (user confirms); PDF (tectonic); AI Disclosure Statement (venue-specific) | formatter_agent | 馃 **Decision-heavy checkpoint:** user selects format before render. Disclosure statement must match venue (ICLR / NeurIPS / Nature / Science / ACL / EMNLP). **v3.8 terminal hard gate (formatter_agent REFUSE rules 6-10)** refuses output on any unresolved `[HIGH-WARN-CLAIM-NOT-SUPPORTED]` / `[HIGH-WARN-NEGATIVE-CONSTRAINT-VIOLATION]` / `[HIGH-WARN-FABRICATED-REFERENCE]` / `[HIGH-WARN-CLAIM-AUDIT-ANCHORLESS]` / `[HIGH-WARN-CONSTRAINT-VIOLATION-UNCITED]` annotation when `ARS_CLAIM_AUDIT=1` was set upstream |
| **6. PROCESS SUMMARY** | `academic-pipeline` v3.8.0 | VERIFIED_ONLY | Paper Creation Process Record (MD + PDF); AI Self-Reflection Report (concession rate, sycophancy risk, health alerts, Failure Mode Audit Log); Score trajectory visualization; **Collaboration Depth Chapter (v3.5.0)** summarising the per-checkpoint observer reports from `collaboration_depth_history[]` | state_tracker_agent; pipeline_orchestrator_agent; **馃憗 collaboration_depth_agent (v3.5.0, pipeline-completion dispatch 鈥?final advisory report)** | 馃 **Decision-heavy checkpoint:** language confirmed with user. Collaboration quality evaluated. Post-publication audit report (if peer-review published). 馃憗 Observer runs final pipeline-completion dispatch; never blocks |

## 4. Data Access Level Flow (v3.3.2+)

```mermaid
flowchart LR
    User[User input<br/>web / PDFs / queries]
    Raw[deep-research<br/>data_access_level: raw]
    Red[academic-paper<br/>data_access_level: redacted]
    Ver1[academic-paper-reviewer<br/>data_access_level: verified_only]
    Ver2[academic-pipeline<br/>data_access_level: verified_only]

    User --> Raw
    Raw -- source_verification elevates --> Red
    Red -- Gate 2.5: 7-mode integrity --> Ver1
    Red -- Gate 2.5 --> Ver2
    Ver2 -. orchestrates .-> Raw
    Ver2 -. orchestrates .-> Red
    Ver2 -. orchestrates .-> Ver1

    classDef raw fill:#fff1f0,stroke:#cf1322
    classDef red fill:#fffbe6,stroke:#d48806
    classDef ver fill:#f6ffed,stroke:#389e0d
    class Raw raw
    class Red red
    class Ver1,Ver2 ver
```

Rules (per `shared/ground_truth_isolation_pattern.md`):

- `data_access_level` is a **declarative** annotation, not a runtime-enforced permission system. The Codex package lint `scripts/check_data_access_level.py` confirms every `WORKFLOW.md` / `SKILL.md` carries a valid value; it does not inspect context windows at runtime.
- `raw` skills consume layer-1 data (arbitrary, possibly adversarial).
- `redacted` skills operate on sanitized material, no new raw ingestion.
- `verified_only` skills run only after upstream integrity gates.
- The reviewer side **may hold a rubric privately** 鈥?the key guarantee is that rubric / gold-label content must not be present in the candidate-generating agent's context. Calibration gold sets are runtime-supplied by the human researcher, not bundled into the repository.
- Stage 2.5 and Stage 4.5 (plus the user's review at each gate) are the actual enforcement points. This pattern document explains the data-flow structure that makes those gates meaningful; it is not itself a runtime lock.

## 5. Material Passport `literature_corpus[]` Flow (v3.6.4 input port + v3.6.5 consumers)

# REDACTED: sensitive-looking memory line

```mermaid
flowchart LR
    subgraph Producer["Out-of-band (user-owned)"]
        Source[User corpus<br/>Zotero / Obsidian /<br/>folder of PDFs / etc.]
        Adapter["Adapter<br/>(reference: scripts/adapters/<br/>folder_scan.py / zotero.py /<br/>obsidian.py 鈥?v3.6.4+)"]
        Source --> Adapter
    end
    Passport["Material Passport<br/>passport.yaml<br/>+ rejection_log.yaml<br/>(literature_corpus[]<br/>optional Schema 9 field)"]
    Adapter --> Passport
    subgraph Consumer["Phase 1 ARS runtime (v3.6.5)"]
        BA["馃摎 deep-research<br/>bibliography_agent<br/>(Phase 1)"]
        LS["馃摎 academic-paper<br/>literature_strategist_agent<br/>(Phase 1)"]
    end
    Passport -- presence-based<br/>auto-engage --> BA
    Passport -- presence-based<br/>auto-engage --> LS
    BA --> SR1[Search Strategy report<br/>+ PRE-SCREENED block<br/>final_included = pre_screened 鈭?external]
    LS --> SR2[Literature Search Report<br/>+ PRE-SCREENED block<br/>+ corpus-aware Matrix / Gap]

    classDef producer fill:#fffbe6,stroke:#d48806
    classDef passport fill:#f0f5ff,stroke:#2f54eb,stroke-width:2px
    classDef consumer fill:#f6ffed,stroke:#52c41a
    classDef report fill:#f9f0ff,stroke:#9254de
    class Source,Adapter producer
    class Passport passport
    class BA,LS consumer
    class SR1,SR2 report
```

# REDACTED: sensitive-looking memory line

**Consumer side (v3.6.5).** Two Phase 1 literature agents read `literature_corpus[]` via the **corpus-first, search-fills-gap** flow 鈥?`deep-research/agents/bibliography_agent.md` and `academic-paper/agents/literature_strategist_agent.md`. The flow is presence-based: it auto-engages when the passport carries a non-empty `literature_corpus[]` and parses cleanly. When the corpus is absent, empty, or fails the minimal shape check, each consumer runs its existing external-DB-only flow unchanged (Iron Rule 4 graceful fallback for the failure cases).

**Five-step shared flow.** Step 0 minimal shape check 鈫?Step 1 pre-screen corpus against current RQ 鈫?Step 2 search-fills-gap (4-case dispatch on `uncovered_topics` 脳 `user_corpus_only`) 鈫?Step 3 merge into `final_included` 鈫?Step 4 emit Search Strategy report with PRE-SCREENED block. `final_included` stays neutral 鈥?no provenance tags on bibliography entries, no provenance column in the Literature Matrix.

**Four Iron Rules** govern every consumer:

1. **Same criteria.** Apply the same Inclusion / Exclusion criteria to corpus entries and external database results. No exceptions.
2. **No silent skip.** Any skipped corpus entry is recorded in the PRE-SCREENED block's skipped sub-section with a reason. Silently dropping an entry is a prompt-layer violation.
3. **No corpus mutation.** Consumer agents never modify, backfill, or derive new content into `literature_corpus[]`. Read only.
4. **Graceful fallback on parse failure.** Consumer agents do NOT re-validate schema, do NOT parse JSON Schema at runtime, and do NOT dereference `source_pointer` URIs. When the corpus cannot be parsed, emit `[CORPUS PARSE FAILURE: <cause>]` and fall back to external-DB-only flow.

**PRE-SCREENED reproducibility block.** Lives inside the Search Strategy section of each consumer's report, immediately before the existing `Databases` line. Enumerates included / excluded / skipped citation_keys with reasons; carries F3 zero-hit note when corpus is non-empty but 0 entries survived screening; carries F4a鈥揊4f provenance reporting for `obtained_via` (adapter origin) and `obtained_at` (snapshot date) covering full / partial / undeclared / wide-spread sub-cases. CI lint `scripts/check_corpus_consumer_protocol.py` enforces nine invariants L1-L9 with manifest-driven consumer list (`scripts/corpus_consumer_manifest.json`) and tuple-matched closed-set state machine.

**Out of v3.6.5 scope.** `citation_compliance_agent` corpus reading is deferred (target version TBD post-v3.8). `source_pointer` URI dereferencing and source verification remain a future `source_verification_agent` concern. Schema is unchanged from v3.6.4 鈥?existing user adapters work without modification.

# REDACTED: sensitive-looking memory line

## 6. Skill Dependency Graph

```mermaid
graph TD
    Pipeline[academic-pipeline<br/>orchestrator<br/>v3.8.0<br/>5 agent prompts]
    Observer[collaboration_depth_agent<br/>observer 路 advisory only<br/>blocking: false]
    DR[deep-research<br/>13 agents<br/>v2.9.2<br/>+ corpus reader]
    AP[academic-paper<br/>12 agents<br/>v3.1.1<br/>+ corpus reader]
    APR[academic-paper-reviewer<br/>7 agents<br/>v1.9.0]
    Shared[shared/<br/>handoff_schemas.md<br/>ground_truth_isolation<br/>benchmark_report<br/>artifact_reproducibility<br/>cross_model_verification<br/>mode_spectrum<br/>style_calibration<br/>collaboration_depth_rubric<br/>sprint_contract.schema<br/>contracts/passport/reset_ledger_entry<br/>contracts/passport/literature_corpus_entry<br/>contracts/passport/rejection_log<br/>contracts/reviewer/full + methodology_focus]

    Pipeline --> DR
    Pipeline --> AP
    Pipeline --> APR
    Pipeline -. "FULL/SLIM ckpt + pipeline completion<br/>MANDATORY gates skip" .-> Observer
    DR -. "RQ Brief + Bibliography + Synthesis" .-> AP
    AP -. "Complete manuscript" .-> APR
    APR -. "Revision Roadmap" .-> AP
    DR --- Shared
    AP --- Shared
    APR --- Shared
    Pipeline --- Shared
    Observer --- Shared

    classDef orch fill:#f0f5ff,stroke:#2f54eb,stroke-width:2px
    classDef skill fill:#e6f4ff,stroke:#1677ff
    classDef shared fill:#f5f5f5,stroke:#595959,stroke-dasharray:5 5
    classDef observer fill:#f6ffed,stroke:#52c41a,stroke-dasharray:3 3
    class Pipeline orch
    class DR,AP,APR skill
    class Shared shared
    class Observer observer
```

## 7. Quality Gates

Two classes of gate: **馃 decision-heavy** (user chooses a branch or approves material) and **鉁?integrity** (machine verification + user ack). Pure machine-enforced 馃 lint checks run in CI.

| Gate | Class | Stage | What blocks advancement | Failure handling |
|---|---|---|---|---|
| RQ + methodology confirmation | 馃 | 1 | User hasn't approved RQ Brief and Methodology Blueprint | Revise and re-present |
| S2 API verification | 馃 | 1 | Citation not in Semantic Scholar; title Levenshtein < 0.70 | Flag; user decides to drop or re-cite |
| Outline approval | 馃 | 2 | User hasn't approved outline | Revise and re-present |
# REDACTED: sensitive-looking memory line
| VLM figure verify (v3.3) | 馃 | 2 | Rendered figure fails 10-pt APA 7.0 checklist | Max 2 refinement iterations |
| Stage 2.5 integrity + ack | 鉁?| 2.5 | Any mode SUSPECTED on 7-mode checklist, or Modes 1/3/5/6 INSUFFICIENT EVIDENCE, or user hasn't acknowledged report | Fix + re-verify (max 3 rounds); or user override with reasoning (logged) |
| Editor-in-Chief decision review | 馃 | 3 | User hasn't reviewed decision letter | Present decision; await user |
| Concession threshold | 馃 | 3 | DA rebuttal scored < 4/5 by responder | No concession; frame-lock detector runs |
| Revision Coaching | 馃 | 3鈫? | User hasn't engaged or explicitly skipped (max 8 rounds) | User may say "just fix it" to skip |
| Revision confirmation | 馃 | 4 | User hasn't confirmed changes | Revise; re-present |
| Revision loop cap | 馃 | 4 / 3' / 4' | 2 revision loops already consumed | Forced advance to Stage 4.5 |
| Residual Coaching | 馃 | 3'鈫?' | User hasn't engaged or explicitly skipped (max 5 rounds) | User may say "just fix it" to skip |
| Content-frozen confirmation | 馃 | 4' | User hasn't confirmed freeze | Await user; no further review loop permitted |
| Stage 4.5 final integrity + ack | 鉁?| 4.5 | ANY issue on deeper 7-mode re-run; mode still SUSPECTED since 2.5 and unresolved | ZERO-tolerance; no skip; fix + re-verify |
| Format selection | 馃 | 5 | User hasn't chosen output format | Await user format choice |
| Disclosure check | 馃 | 5 | Venue-specific AI disclosure absent or wrong form | Block render until fixed |
| `repro_lock` (v3.3.5) | 馃 (standalone) | 鈥?| `repro_lock` key required in Material Passport v3.3.5+; value must be either a populated block or explicit `null` (honest opt-out). Populated blocks validated by `check_repro_lock.py`. Per `artifact_reproducibility_pattern.md`: **not** wired into the CI lint suite by default and **not** read by the Stage 2.5 / 4.5 integrity gate at runtime 鈥?this is post-hoc documentation, not a pipeline block | Run `check_repro_lock.py <passport>` on demand |
| Language + collaboration review | 馃 | 6 | User hasn't confirmed output language / reviewed self-reflection | Await user |
| `benchmark_report` (v3.3.5, external) | 馃 | 鈥?| Publishing a benchmark without honest disclosure | Users run `check_benchmark_report.py` before publishing |
| Collaboration Depth Observer (v3.5.0) | 馃 observer | Every FULL/SLIM checkpoint + pipeline completion | **Never blocks.** Advisory only. Scores user-AI collaboration pattern on 4 dimensions (Delegation Intensity / Cognitive Vigilance / Cognitive Reallocation / Zone Classification) per `shared/collaboration_depth_rubric.md`. Injects a named section into checkpoint presentation and a chapter in the Process Record. MANDATORY integrity gates (2.5 / 4.5) do NOT invoke the observer. | n/a 鈥?output is advisory; user `Ready to proceed?` prompt unchanged |
# REDACTED: sensitive-looking memory line
| Sprint Contract hard gate (v3.6.2) | 馃 + 馃 | 3 (REVIEW) | Each reviewer must produce a Schema 13 sprint contract (`shared/sprint_contract.schema.json`) BEFORE seeing the paper (Phase 1 metadata-only). Phase 2 paper-visible review consumes the committed contract via `<phase1_output>` data delimiter. `editorial_synthesizer_agent` runs three-step mechanical protocol with forbidden-ops list. Validated by `scripts/check_sprint_contract.py` (structural invariants + 9 soft warnings). Templates: `shared/contracts/reviewer/full.json` (panel 5) + `methodology_focus.json` (panel 2); reserved modes (`re-review` / `calibration` / `guided` / `quick`) keep pre-v3.6.2 behaviour. | Synthesizer rejects post-hoc rubric edits; user sees contract pre-commitment in review log |
# REDACTED: sensitive-looking memory line
| Corpus consumer protocol (v3.6.5) | 馃 + Phase 1 agents | 1 / 2 (when `literature_corpus[]` present) | Presence-based auto-engage when Material Passport carries non-empty `literature_corpus[]` and parses cleanly. Four Iron Rules (Same criteria / No silent skip / No corpus mutation / Graceful fallback on parse failure). PRE-SCREENED reproducibility block in Search Strategy report (F3 zero-hit + F4a鈥揊4f provenance). Validated by `scripts/check_corpus_consumer_protocol.py` (9 invariants L1-L9 with manifest-driven consumer list). | Parse failure 鈫?emit `[CORPUS PARSE FAILURE: <cause>]` and fall back to external-DB-only flow (Iron Rule 4) |

## 8. ARS Evolution Timeline

```mermaid
timeline
    title ARS evolution timeline
    v3.3 : Semantic Scholar API verification
         : Anti-leakage protocol
         : VLM figure verification
         : Score trajectory tracking
         : Stage 2 parallelization
    v3.3.1-v3.3.6 : Public contract drift fixes + check_spec_consistency.py
                  : data_access_level + task_type frontmatter
                  : Lint hardening + ground_truth_isolation_pattern
                  : benchmark_report.schema.json + repro_lock on Material Passport
                  : README changelog summaries sync + CI validation
    v3.4.0 : compliance_agent (PRISMA-trAIce + RAISE)
           : Schema 12 compliance_report + compliance_history[]
           : 3-round override ladder + disclosure_addendum
           : freshness check (180-day threshold)
    v3.5.0 : collaboration_depth_agent (advisory observer)
           : shared/collaboration_depth_rubric.md (Wang & Zhang 2026)
           : dialogue_log_ref + collaboration_depth_history[]
           : short-stage guard + ARS_CROSS_MODEL_SAMPLE_INTERVAL
    v3.5.1 : Socratic reading-check probe (opt-in via ARS_SOCRATIC_READING_PROBE)
# REDACTED: sensitive-looking memory line
           : decline logged without penalty
    v3.6.2 : Schema 13 Sprint Contract hard gate for reviewers
           : two-phase protocol (paper-blind Phase 1 + paper-visible Phase 2)
           : editorial_synthesizer three-step mechanical protocol + forbidden-ops list
           : full.json (panel 5) + methodology_focus.json (panel 2) templates
    v3.6.3 : Opt-in passport reset boundary (ARS_PASSPORT_RESET=1)
           : resume_from_passport mode + Schema 9 reset_boundary[] ledger
           : JSON Canonical Form + SHA-256 hash with canonical placeholder
           : POSIX fcntl.flock LOCK_EX concurrency contract
    v3.6.4 : Material Passport literature_corpus[] input port (Schema 9 optional)
           : language-neutral adapter contract + 3 reference Python adapters
           : rejection_log.yaml contract (closed enum, always emitted)
           : check_literature_corpus_schema.py + sync_adapter_docs.py CI lints
    v3.6.5 : literature_corpus[] consumer integration in Phase 1
           : bibliography_agent + literature_strategist_agent corpus-first flow
           : 4 Iron Rules + PRE-SCREENED block + F3 zero-hit + F4 provenance
           : check_corpus_consumer_protocol.py (9 invariants, manifest-driven)
    v3.6.7 : Downstream-agent PATTERN PROTECTION (Step 1+2)
           : synthesis_agent A1-A5 + research_architect_agent B1-B5 + report_compiler_agent C1-C3
           : 4 reference glossaries (IRB / psychometric / hedging / word-count)
           : check_v3_6_7_pattern_protection.py (29-test mutation suite)
    v3.6.8 : Generator-Evaluator Contract Gate (v3.6.6 spec ship, naming offset)
           : Schema 13.1 + writer_full / evaluator_full templates
           : two-phase orchestration in academic-paper full mode (Phase 4a/4b + 6a/6b)
           : SC-* mode-gating in check_sprint_contract.py
    v3.7.0 : Claude Code plugin packaging
           : .claude-plugin/{plugin,marketplace}.json + skills/ symlinks
           : 10 slash commands (commands/ars-*.md, model pinned opus/sonnet, no haiku)
           : 3 plugin agents (agents/, symlink to v3.6.7-hardened source, model: inherit)
# REDACTED: sensitive-looking memory line
    v3.7.3 : L3 locator infrastructure (claim faithfulness 鈥?first half)
           : Three-Layer Citation Emission (synthesis / draft_writer / report_compiler)
           : <!--anchor:kind:value--> on every <!--ref:slug--> (quote / page / section / paragraph / none)
           : contamination_signals advisory (preprint_post_llm_inflection + semantic_scholar_unmatched)
           : check_v3_7_3_three_layer_citation.py + finalizer 5-cell with precedence-zero NO-LOCATOR
    v3.8.0 : L3 claim-faithfulness audit (second half 鈥?paired with v3.7.3)
           : claim_ref_alignment_audit_agent (opt-in via ARS_CLAIM_AUDIT=1, default OFF)
           : 5 new passport schemas (claim_audit_result / claim_intent_manifest / claim_drift / uncited_assertion / constraint_violation)
           : 8-row finalizer matrix + 5 new HIGH-WARN classes (formatter REFUSE rules 6-10)
           : Calibration runner (20-tuple gold set, FNR<0.15 + FPR<0.10 acceptance gate)
           : check_claim_audit_consistency.py (38 invariants) + check_v3_8_annotation_literal_sync.py
    v3.9.0 : Cross-index triangulation measurement layer
           : contamination_signals extends S2 to S2 + OpenAlex + Crossref
           : openalex_unmatched + crossref_unmatched optional booleans
           : 4-tier advisory matrix; refusal list unchanged
           : migrate_literature_corpus_to_v3_9_0.py + check_v3_9_0_triangulation.py
    v3.9.1 : Client hardening (#129 + #130)
           : OpenAlex/Crossref response-read failures degrade as *Unavailable
           : claim-audit lint guards malformed non-string manifest_id
    v3.9.2 : Phase scope inflation hot-fix (#133)
           : phase-boundary blocks across single-phase agents
           : intent clarification for ambiguous cross-phase materials
    v3.9.3 : Shared client utilities + migration YAML helper extraction
           : _text_similarity.py + _passport_yaml.py
           : time.monotonic throttle standardization
    v3.9.4 : Temporal verification advisory layer (#135)
           : timeline_extraction_agent + 5-pass verifier at Phase 4鈫?
           : Temporal Integrity Iron Rule in writer/compiler prompts
           : first-party Crossref/pdftotext verification sidecars
    v3.9.4.1 : Temporal verification post-ship hotfix
             : citation_provenance wiring, date parser coverage, direct-date P4 binding
             : citation_provenance confidence:high required-field schema fix
    v3.9.4.2 : CI/release-gate-only upstream tag
             : .github changes intentionally excluded from the Codex package
```

## 9. Skill Modes

| Skill | Modes |
|---|---|
| `deep-research` v2.9.4 | full, quick, socratic, review, lit-review, fact-check, systematic-review (7) |
| `academic-paper` v3.1.2 | full, plan, outline-only, revision, revision-coach, abstract-only, lit-review, format-convert, citation-check, disclosure (10) |
| `academic-paper-reviewer` v1.9.1 | full, re-review, quick, methodology-focus, guided, calibration (6) |
# REDACTED: sensitive-looking memory line

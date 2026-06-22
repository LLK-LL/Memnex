# Policy-Anchor Disclosure Protocol

**Status**: #108 implementation (parented to Decision Doc 20ed72d)
**Parent skill**: `academic-paper`
**Mode name**: `disclosure` with `--policy-anchor=<a>` selector (parallel track to `--venue=<v>` v3.2 path; see `disclosure_mode_protocol.md` for the dispatch).
**Anchor inventory**: `prisma-trAIce, icmje, nature, ieee` (closed enum; expansion via 搂4.7 deferred per Decision Doc 搂4.2).
**Data source**: `policy_anchor_table.md` (read at runtime; LLM looks up the row for `--policy-anchor=<a>` 脳 field-N).

This protocol document is the runtime instruction set the LLM follows when the user invokes `disclosure` mode with a policy-anchor selector. It encodes the 8 Decision Doc 搂4.3 frozen invariants, the 搂3 G10 7-row precedence table for whole-disclosure output decision, the 11 搂4.4 open-concern resolutions (per implementation spec 搂3), the auto-promotion forbiddance, and the per-anchor render flows (PRISMA-trAIce / ICMJE / Nature / IEEE).

---

## 0. Why this protocol exists

# REDACTED: sensitive-looking memory line

---

## 1. Inputs

1. **Paper draft** (same as v3.2): manuscript text plus pipeline log if available.
2. **Selector**: `--policy-anchor=<a>` where `a 鈭?{prisma-trAIce, icmje, nature, ieee}`. **Selector-mutually-exclusive by default** 鈥?supplying both `--policy-anchor` and `--venue` triggers the 搂5 conflict-resolution flow, which permits exactly one consistent pair (any Nature Portfolio venue + `--policy-anchor=nature`, sharing the canonical `shared/policy_data/nature_policy.md` source) and rejects every other combination with explicit error. See 搂5 for the full enumeration.
3. **Pipeline signal**: `slr_lineage=true|false` set by the upstream pipeline orchestrator when an SLR-mode stage appears in the run history. Drives the 搂4.3 G2 invariant track gate (concern #1 resolution: explicit `slr_lineage` input).
# REDACTED: sensitive-looking memory line
5. **v3.2 Phase 2 AI usage categorization**: the same input shape v3.2 uses. Each AI usage category carries state 鈭?`{USED, NOT USED, UNCERTAIN}`.
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line

---

## 2. Whole-disclosure decision 鈥?搂3 G10 7-row precedence table

Rows are evaluated in priority order from top to bottom; the renderer emits the output of the **first** row whose precondition matches. Subsequent rows do not fire. This table is the 搂4.3 **G3 / G10 invariant** in load-bearing form.

| # | Precondition (first match wins) | Whole-disclosure output |
|---|---|---|
| 1 | `ai_used: false` supplied AND 鈮? v3.2 category is USED (contradiction) | Honest "AI-disclosure conflict 鈥?explicit no-AI input contradicts USED category" annotation; renderer prompts the user to reconcile before any anchor render emits. |
| 2 | `ai_used: false` supplied AND no v3.2 category is USED AND no v3.2 category is UNCERTAIN | "No AI was used in preparing this paper" statement (G10 opt-in path). |
| 3 | `ai_used: false` supplied AND 鈮? v3.2 category is UNCERTAIN AND no v3.2 category is USED | Honest "AI-disclosure tension 鈥?explicit no-AI input but categories still UNCERTAIN" annotation; renderer prompts the user to resolve UNCERTAIN before emitting the no-AI statement. |
| 4 | `ai_used: true` supplied OR 鈮? v3.2 category is USED, AND row 1 did not match | Full anchor-specific disclosure render per 搂3 below, applying the **concern #6 resolution** (USED facets at full strength; per-facet "AI disclosure pending 鈥?category {X} not confirmed; resolve via v3.2 Phase 2" annotation immediately after each still-UNCERTAIN facet's render slot). |
| 5 | 鈮? v3.2 category is UNCERTAIN AND no v3.2 category is USED AND no `ai_used` input | Honest "AI-disclosure status not supplied 鈥?categories pending confirmation" annotation; renderer prompts the user to run the v3.2 UNCERTAIN-confirmation flow before re-invoking. |
| 6 | 鈮? v3.2 category supplied AND every supplied category is NOT USED AND no UNCERTAIN AND no `ai_used` input | Silence 鈥?emit no AI-disclosure statement at all (G10 "silence is default-OK"). |
| 7 | None of rows 1鈥? match (empty input across every dimension) | Honest "AI-disclosure status not supplied for this run" annotation (G3 D3 pure cold-start). |

**Concern #10 resolution (`ai_used: true` substantive-content gate):** when `ai_used: true` is supplied **and no v3.2 category is marked USED** (regardless of whether Phase 2 has been performed 鈥?i.e., this gate fires for both "bare-flag input only, no categorization" **and** "Phase 2 done but every category came back NOT USED while `ai_used:true` is still set"), row 4 does not emit a complete render. Instead, the input is treated as a **prompt-trigger** that halts the current run and asks the user to reconcile: either supply a USED category, change `ai_used` to false, or run / re-run v3.2 Phase 2 categorization. Once a USED category is supplied (or `ai_used` flipped), re-evaluate against the 搂2 table from the top. This implements the concern #10 resolved path: "force v3.2 categorization flow", consistent with concern #6's honest-signal-preservation discipline. The forbiddance: emitting a full anchor disclosure with `ai_used:true` and zero USED facets.

---

## 3. Per-anchor render flows

For each anchor, the renderer reads `policy_anchor_table.md` rows 1..16 and applies the field-level rules below. The 4 anchors share the row-4 dispatcher above; the per-anchor sections only describe **what to emit** after row 4 fires.

### 3.1 `--policy-anchor=prisma-trAIce`

**Track gate (G2 invariant):** this anchor is only valid when `slr_lineage=true` (pipeline signal) or `mode=systematic-review` (cold-start input). Selecting `--policy-anchor=prisma-trAIce` with `slr_lineage=false` is non-conformant 鈥?the renderer refuses with an explicit error citing the G2 invariant.

**G5 invariant 鈥?three gates for M6 prompt disclosure:** PRISMA-trAIce M6 prompt disclosure fires only when **all three** hold:
1. PRISMA-trAIce track selected (the gate above).
2. `tool_type 鈭?{LLM, GenAI}` (per PRISMA M6 "if any" predicate).
3. AI use is methodological-in-SLR (search / screening / data extraction / Risk of Bias / synthesis / drafting per PRISMA M3.a), **not pure copyediting**.

When gate 3 fails (SLR manuscript whose only LLM use is editorial), the renderer routes to the 搂3.5 copyediting-carve-out path instead. PRISMA-trAIce track does not own the copyediting case.

**Render fields:**
# REDACTED: sensitive-looking memory line
- Row 4鈥?: emit one **(tool 脳 task) record** per (tool, task) tuple across the M3.a 6-stage enum (concern #3 resolution). Missing tuples produce "not supplied" annotation per tuple. Per-task prompt disclosure follows M6.a granularity.
- Row 8: emit prompt records per (tool 脳 task) tuple per gate G5.
- Row 9: emit human oversight description per M8 sub-items.
- Rows 11鈥?2: emit performance evaluation method + results per M9 + R2 when applicable.
- Row 13: emit limitations narrative per D1.
- Row 14: distribute disclosure fragments per Table 1 row groupings (Title / Abstract / Introduction / Methods / Results / Discussion). The renderer emits per-section fragments, not a single paragraph.

### 3.2 `--policy-anchor=icmje`

**Track gate:** no SLR lineage requirement. Available regardless of `slr_lineage` value.

**Render fields:**
- Row 10 (explicit-mandate): emit ICMJE human-responsibility statement using the verbatim "humans are responsible for any submitted material that included the use of AI-assisted technologies" language. This sentence appears in **every** ICMJE render where row 4 fires.
- Row 14 (explicit-recommend): emit two channels 鈥?cover letter (verbatim ICMJE language) + manuscript "appropriate section" (per the venue's submission policy). The two channels carry different paragraphs, not a single duplicated paragraph.
- Row 16 (explicit-mandate): emit the text-attribution clause: appropriate attribution and full citations for AI-quoted material + the prohibition against citing AI-generated material as primary source. Surface this paragraph even when no images are involved (rule covers text-attribution).
- Rows with `not-addressed` strength (9/16 cells): the renderer skips these by default; if v3.2 Phase 2 provides a category USED that would be served by such a field, surface a "ICMJE delegates this detail to journal-level policy; consider the v3.2 venue track for journal-specific phrasing" annotation.

### 3.3 `--policy-anchor=nature`

**Track gate:** no SLR lineage requirement.

**Dedup with v3.2 Nature venue path:** the Nature substantive policy text is co-cited from `shared/policy_data/nature_policy.md` (canonical source pointer). Both consumers 鈥?the v3.2 Nature venue renderer in `venue_disclosure_policies.md` and this Nature anchor renderer 鈥?derive their substantive content from that shared source. **G4 invariant**: edits to Nature-specific policy quotes must go through the shared source first, never directly into either consumer.

**Render fields:**
# REDACTED: sensitive-looking memory line
- Row 14 (explicit-recommend): emit Methods-section placement instruction citing the verbatim "Methods section (and if a Methods section is not available, in a suitable alternative part)" language.
- Row 15 (explicit-recommend) carve-out semantics: **eliminate** strength. Copyediting-only use produces **no disclosure paragraph**, only an internal renderer log entry. The 搂4.3 G7 invariant forbids collapsing this into a boolean shared with IEEE's downgrade semantics.
- Row 16 (explicit-mandate) image-rights handling: concern #5 resolution = **hybrid (annotation block + suggested inline patches)**. The renderer emits two outputs:
  1. A standalone `image_disclosure_instructions.md` block describing, per image, which Nature carve-out applies (or default-deny) and what Nature label text appears in the image field.
# REDACTED: sensitive-looking memory line

### 3.4 `--policy-anchor=ieee`

**Track gate:** no SLR lineage requirement.

**G8 invariant 鈥?paired mandate:** IEEE row 5 (`Specific task within stage`, explicit-mandate) and row 6 (`Affected manuscript sections / content locator`, explicit-mandate) are a paired mandate. The renderer emits **both** inputs together. Emitting `level_of_involvement` (row 5 narrative annotation) without an `affected_sections` locator (row 6) 鈥?or vice versa 鈥?is **non-conformant**.

**Concern #4 resolution (IEEE section locator shape):** free-form list with recommended IMRaD exemplars. Accepted values: `"Introduction" | "Methods" | "Results" | "Discussion" | "Abstract" | "Title" | free-form-other`. Closed-enum would over-constrain IEEE's "brief explanation" language; free-form preserves the policy's narrative invitation. Test fixture covers both exemplar-match and free-form-other inputs.

**Render fields:**
- Row 1 (explicit-mandate): emit "The AI system used shall be identified" formulation 鈥?name + identifier per AI tool.
- Rows 5鈥? (paired explicit-mandate per G8): emit `affected_sections` list + `level_of_involvement` narrative annotation **together**.
- Row 14 (explicit-mandate): emit placement instruction citing "acknowledgments section of any article submitted to an IEEE publication" verbatim. **No Methods placement, no cover-letter channel** 鈥?the tightest closed enum across all four anchors.
- Row 15 (explicit-recommend) carve-out semantics: **downgrade-not-eliminate** strength. Copyediting-only use still produces a disclosure paragraph at the same acknowledgments location, but with recommend-strength rather than mandate language. The 搂4.3 G7 invariant forbids collapsing this into a boolean shared with Nature's eliminate semantics.
- Row 16 (implicit): images/figures/code fold into the same acknowledgments-disclosure mandate as text. **No separate image-rights regime, no default-prohibition** (contrasts with Nature). The renderer emits a single acknowledgments paragraph covering all content types per IEEE policy. The 搂4.3 G9 invariant: each anchor's image-rights regime stays distinct; IEEE's fold-into-acknowledgments path does not merge with Nature's default-deny regime.

### 3.5 Copyediting carve-out cross-anchor handling

Per 搂4.3 G7 invariant + 搂4.5 / 搂4.6 cell #15, the copyediting carve-out semantics are anchor-specific:

- **Nature anchor**: eliminate strength 鈥?no disclosure paragraph for copyediting-only use.
- **IEEE anchor**: downgrade-not-eliminate 鈥?disclosure still emitted at acknowledgments, with recommend-strength language ("is recommended" rather than "shall be disclosed").
- **PRISMA-trAIce anchor**: not in scope (M6 G5 gate 3 routes copyediting cases away from PRISMA-trAIce track entirely; see 搂3.1).
- **ICMJE anchor**: not-addressed in the policy text; the renderer treats copyediting cases per the same path as substantive AI use (no carve-out, full ICMJE render).

The renderer MUST NOT collapse these four behaviors into a single boolean `exempted_uses: [copyediting]` field 鈥?doing so would silently lose the eliminate-vs-downgrade-vs-not-in-scope distinctions.

---

## 4. Auto-promotion forbiddance (搂4.3 G3 / G10 invariant)

A still-UNCERTAIN category MUST NOT be rendered as though USED in any of the four anchor outputs. This is the load-bearing constraint behind concern #6's resolution: USED facets render at full strength; UNCERTAIN facets surface the per-facet annotation, never the full-strength render. The renderer MUST surface UNCERTAIN as UNCERTAIN throughout the disclosure text; silent promotion of any UNCERTAIN category to USED is **forbidden**.

The test suite covers this forbiddance with negative fixtures asserting that an input with `ai_used:true` + 1 UNCERTAIN category + 0 USED categories does NOT emit a full-strength render of the UNCERTAIN category.

---

## 5. Venue + anchor conflict resolution (concern #7)

When the user passes both `--venue=<v>` and `--policy-anchor=<a>`, the renderer evaluates whether the two map to compatible policies. The consistent-pair recognition for the Nature track covers the full Nature Portfolio venue family:

- **Consistent 鈥?Nature Portfolio venue + `--policy-anchor=nature`**: includes canonical labels `{"Nature", "Nature Portfolio", "Nature (Nature Publishing Group)", "Nature Publishing Group"}` **and** any venue whose name starts with the prefix `"Nature "` (e.g., `Nature Medicine`, `Nature Communications`, `Nature Climate Change`, `Nature Energy`, `Nature Methods`, ...). All Nature Portfolio journals inherit the same parent AI policy, so each of these venue strings + `--policy-anchor=nature` proceeds via the shared source pointer.
- **Conflicting 鈥?any other (venue, anchor) pair**: e.g., `--venue=Nature` + `--policy-anchor=IEEE`, `--venue=ICLR` + `--policy-anchor=icmje`, or a Nature Portfolio venue with a non-nature anchor 鈫?**reject with explicit error** listing the policy conflict and the canonical Nature consistent-pair definition above.

Silent precedence is **forbidden** (Decision Doc 搂4.4 #7 + concern #7 resolution). The renderer must surface the conflict to the user and require an explicit selector choice. The recognition logic above is mirrored by the conformance referee's `is_nature_portfolio_venue()` helper in `scripts/policy_anchor_disclosure_referee.py` 鈥?when this protocol text drifts from that helper, the alignment is a non-conformance.

---

## 6. Three-state input completeness flag (concern #8)

The 搂2 G10 7-row table evaluates first-match across (`ai_used` 脳 per-category-state). Field-level computation:

- `ai_used` 鈭?`{true, false, unset}`.
- Each v3.2 category 鈭?`{USED, NOT USED, UNCERTAIN, not-supplied}`.
- First-match-wins evaluation across 搂2's 7 rows.
- Row-4 partial-state composition per concern #6 resolution: USED at full strength; per-facet annotation for each still-UNCERTAIN; auto-promotion forbidden.

The 搂4.3 invariants constrain the evaluation:
- **G1 invariant** 鈥?no `ai_disclosure` field is read from / written to the corpus entry schema; all input flows through the renderer's runtime input contract.
- **G2 invariant** 鈥?track selection reads `slr_lineage` first, never derives SLR-status from `origin_mode` alone.
- **G3 / G10 invariant** 鈥?the 7-row table holds; auto-promotion forbidden.
- **G4 invariant** 鈥?4 anchors, Nature dedup via shared source.
- **G5 invariant** 鈥?three gates for M6 prompts.
- **G7 invariant** 鈥?anchor-specific carve-out semantics.
- **G8 invariant** 鈥?IEEE paired-mandate (row 5 + row 6).
- **G9 invariant** 鈥?anchor-specific image-rights regimes.

---

## 7. 搂4.4 concern resolutions reference

For audit traceability, this protocol implements each Decision Doc 搂4.4 open concern as follows. See implementation spec 搂3 for full rationale.

- **concern #1** 鈥?Track-selection lookup mechanism resolved as: explicit `slr_lineage` input from pipeline orchestrator; cold-start `mode=` parameter.
# REDACTED: sensitive-looking memory line
- **concern #3** 鈥?Prompt scope: per-(tool 脳 task) tuple across M3.a 6-stage enum; missing tuples emit "not supplied" annotation per tuple.
- **concern #4** 鈥?IEEE section locator: free-form list with recommended IMRaD exemplars; parallel to G8 `level_of_involvement` design.
- **concern #5** 鈥?Nature image metadata + labelling: hybrid output channel 鈥?standalone annotation block + suggested inline manuscript patches; ARS does not modify manuscript source autonomously.
- **concern #6** 鈥?UNCERTAIN per-facet finalization: USED facets render at full strength; UNCERTAIN facets surface per-facet annotation immediately after each render slot.
- **concern #7** 鈥?Venue + anchor conflict: reject with explicit error citing the policy conflict; silent precedence forbidden.
- **concern #8** 鈥?Three-state completeness flag: full spec encoded in 搂6 above.
- **concern #9** 鈥?Test set scope: covers 搂4.3 8 invariants + 搂4.4 #1鈥?8 + #10 + #11; positive + negative fixture per resolved path / forbidden path.
- **concern #10** 鈥?`ai_used: true` substantive-content gate: bare-flag input treated as prompt-trigger forcing v3.2 categorization flow before any anchor render.
# REDACTED: sensitive-looking memory line

---

## 8. Related

- Decision Doc: `../docs/design/2026-05-14-ai-disclosure-schema-decision.md`
- Implementation spec: `../docs/design/2026-05-14-ai-disclosure-impl-spec.md`
- Anchor data table (consumer of this protocol): `policy_anchor_table.md`
- v3.2 disclosure mode protocol (parallel track): `disclosure_mode_protocol.md`
- v3.2 venue disclosure policies (Nature dedup peer): `venue_disclosure_policies.md`
- Shared Nature policy source (canonical pointer, forthcoming): `shared/policy_data/nature_policy.md`
- Lint contract: `../../scripts/check_policy_anchor_protocol.py`
- Conformance test suite: `../../scripts/test_policy_anchor_disclosure.py` (Task #7)

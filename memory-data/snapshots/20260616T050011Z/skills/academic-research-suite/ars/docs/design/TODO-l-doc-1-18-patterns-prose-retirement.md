# L-doc-1 follow-up 鈥?"18 patterns" prose retirement (docs-only)

**Status:** open. Logged when v3.6.7 Step 6 + Step 8 (Phase 6.8) shipped. Mechanical docs-only edit; not a spec amendment.

**Why:** the v3.6.7 inventory enumerates 17 numbered pattern IDs (A1-A5, B1-B5, C1-C3, D1-D4). Earlier prose drafted before the 搂7.1 inventory walk used "18 patterns" as a summary count. The fixture set (17 micro + 1 integration) already tracks the 17-ID inventory; only the summary prose needs retirement. See `docs/design/2026-04-30-ars-v3.6.7-step-6-orchestrator-hooks-spec.md` 搂7.1 + 搂9.2 L-doc-1 for the off-by-one analysis.

## Eight retirement locations

### Upstream main spec 鈥?`docs/design/2026-04-29-ars-v3.6.7-downstream-agent-pattern-protection-spec.md`

1. 搂1 鈥?"18 distinct patterns" 鈫?"17 distinct patterns"
2. 搂2.1 鈥?"18 distinct patterns" 鈫?"17 distinct patterns"
3. 搂9 Step 8 鈥?"demonstrating all 18 patterns triggered + protected" 鈫?"demonstrating all 17 patterns triggered + protected"
4. 搂10 鈥?any "18 patterns" reference 鈫?"17 patterns"

### This spec 鈥?`docs/design/2026-04-30-ars-v3.6.7-step-6-orchestrator-hooks-spec.md`

5. line 6 (Scope) 鈥?"all 18 patterns trigger and protect" 鈫?"all 17 patterns trigger and protect"
6. line 17 (Step 8 bullet) 鈥?"synthetic evaluation case demonstrating all 18 patterns triggered and protected" 鈫?"...all 17 patterns triggered and protected"
7. line 29 (搂1.2) 鈥?"two-tier (18 micro + 1 integration)" 鈫?"two-tier (17 micro + 1 integration)"
8. line 64 (搂2.1 Q4 row) 鈥?"18 per-pattern micro-fixtures + 1 chapter-level integration fixture" 鈫?"17 per-pattern micro-fixtures + 1 chapter-level integration fixture"

## Out of scope for this retirement

- The 17 numbered pattern IDs themselves 鈥?they are correct.
- The fixture count "18" in 搂7.1 / 搂7.6 鈥?that is "17 micro + 1 integration = 18 fixture artifacts", a coincident match, NOT a claim about 18 patterns.
- Memory files referencing "18 patterns" 鈥?those are local snapshots; do not retroactively edit shipped memory entries.

## Procedure

1. New branch `docs/retire-18-patterns-prose`.
2. Edit the eight locations above with `sed -i '' 's/18 distinct patterns/17 distinct patterns/g' ...` etc., or hand-edit per location's exact wording.
3. Verify no remaining `"18 patterns"` / `"18 distinct patterns"` / `"18 micro"` / `"18 per-pattern"` matches via `grep -rn '18 [a-z]\+ patterns\|18 distinct patterns\|18 micro\|18 per-pattern' docs/design/`.
4. PR with title `docs(v3.6.7): retire "18 patterns" prose; inventory enumerates 17 numbered IDs`.
5. After merge, delete this TODO file.

## Why a separate PR

- v3.6.7 Step 6 + Step 8 ship is large; bundling docs-prose changes with implementation increases review surface without adding test coverage.
- The retirement is decoupled by design 鈥?fixture set and lint already track the 17-ID inventory. Prose drift was identified during 搂7.1 review and noted for follow-up.
- A future reviewer who sees "18 patterns" in upstream prose during v3.6.7 review can match it against this TODO file and confirm the discrepancy is logged, not unobserved.

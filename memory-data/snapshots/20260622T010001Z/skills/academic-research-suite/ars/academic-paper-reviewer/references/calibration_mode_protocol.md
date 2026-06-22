# Calibration Mode Protocol

**Status**: v3.2
**Parent skill**: `academic-paper-reviewer`
**Mode name**: `calibration`
# REDACTED: sensitive-looking memory line

---

## Why this mode exists

A single LLM reviewer produces an absolute 0-100 rubric score, but that score is weakly interpretable without knowing the reviewer's error profile. Two reviewers could give the same paper a 65, yet one might systematically over-score weak methodology papers and the other might systematically under-score cross-disciplinary work. Absolute scores don't reveal this.

Lu et al. (2026, Nature 651:914-919) demonstrated in Table 1 that an LLM-based Automated Reviewer can approach human balanced accuracy (0.65 vs human 0.67-0.73 on 500 ICLR 2022 papers) while having a dramatically different error profile: FNR 0.17 vs human 0.52, at the cost of FPR 0.50 vs human 0.17-0.34. Human reviewers miss half of the papers that should be rejected; the Automated Reviewer misses very few but over-rejects more.

Translation for ARS: **our reviewer has an error profile too, and we do not currently measure it.** Calibration mode closes that gap. It does not try to make the reviewer perfect; it makes the reviewer's imperfections legible.

---

## Inputs

1. **Gold-standard set**: 5-20 papers the user has labelled with known outcomes. Minimum 5; recommended 10-15. Each entry:
   - Paper file path or text
   - Ground-truth label: `accept`, `reject`, or `borderline`
   - Venue context (journal/conference, tier)
   - Optional: human reviewer scores for comparison

2. **Domain specification**: the user's target field, used to seed `field_analyst_agent`. Calibration for "machine learning venues" is not valid for "qualitative education research" 鈥?error profiles are domain-specific.

# REDACTED: sensitive-looking memory line

---

## Process

### Phase 0: Intake

- Verify the set has at least one `accept` and one `reject` (otherwise FNR or FPR is undefined).
- If all labels are on one side, refuse to proceed and ask the user for at least one counter-example.
- Warn if n < 10: "Calibration with fewer than 10 papers produces wide confidence intervals. Results should be treated as directional, not conclusive."

### Phase 1: Run `full` mode on each gold paper, with ensembling

# REDACTED: sensitive-looking memory line
- Median rubric score per dimension
- Variance across the 5 runs (reported as a stability indicator)
- Editorial decision (majority vote across 5)

**Cross-model verification**: In calibration mode, `ARS_CROSS_MODEL` is **default-on** rather than opt-in. At least one of the 5 runs should use a different model family if available, to avoid single-model blind spots. If no cross-model is configured, emit a warning and run all 5 on the primary model.

### Phase 2: Build the confusion matrix

Compare reviewer's majority-vote decision against the user's ground-truth label.

- `borderline` ground truth papers are excluded from the binary confusion matrix but reported separately (see Phase 3).
- Map `Accept` and `Minor Revision` reviewer decisions 鈫?positive. Map `Major Revision` and `Reject` 鈫?negative. This follows Lu 2026 Table 1's binarization.

Compute:

| Metric | Formula | Report with |
|---|---|---|
| Balanced accuracy | (TPR + TNR) / 2 | 95% CI via bootstrap (1000 resamples) |
| FNR (miss rate) | FN / (FN + TP) | Same |
| FPR (false alarm) | FP / (FP + TN) | Same |
| AUC | ROC over rubric-score threshold | Same |
| Calibration error | Mean &#124;rubric_score - ground_truth_severity&#124; | Per-dimension |

### Phase 3: Borderline handling

Borderline papers don't enter the binary matrix but are useful for rubric-score calibration. For each borderline paper, report:
- The reviewer's rubric score
- The reviewer's decision
- Whether the reviewer's decision respects the user's "this is borderline" signal (i.e., did it correctly land in Major Revision rather than confidently Accept or Reject?)

A reviewer that confidently Accepts or Rejects borderline papers has a "confidence miscalibration" problem even if its binary accuracy looks fine.

### Phase 4: Produce the Calibration Report

Output document structured as:

```
# Calibration Report for <Reviewer Instance>
Domain: <domain>
Gold set: n=<N> (accept=<a>, reject=<r>, borderline=<b>)
Runs per paper: 5 (ensembled)
Cross-model: <yes/no, model families used>

## Summary metrics
- Balanced accuracy: 0.XX [95% CI: 0.XX - 0.XX]
- FNR: 0.XX [95% CI ...]
- FPR: 0.XX [95% CI ...]
- AUC: 0.XX
- Ensemble stability: <mean std of rubric scores across runs>

## Comparison to Lu 2026 Table 1 baselines
| Metric | This reviewer | Lu 2026 Automated Reviewer | Lu 2026 Human |
|---|---|---|---|
| Balanced accuracy | X | 0.65 | 0.67-0.73 |
| FNR | X | 0.17 | 0.52 |
| FPR | X | 0.50 | 0.17-0.34 |

(Note: Lu 2026 numbers are for ML venues specifically. Compare with caution outside ML.)

## Per-dimension calibration error
<table of 7 review dimensions with mean absolute calibration error>

## Systematic biases detected
<natural-language narrative identifying patterns, e.g.
 "Reviewer tends to over-score originality on cross-disciplinary papers"
 "Reviewer under-scores qualitative methodology by ~8 points vs ground truth"
>

# REDACTED: sensitive-looking memory line
- Treat this reviewer's rubric scores as having calibration error 卤X points
- For accept/reject decisions, the reviewer misses X% of reject cases (FNR)
- For decisions near the accept/reject boundary, escalate to human judgement
```

# REDACTED: sensitive-looking memory line

# REDACTED: sensitive-looking memory line

```
# REDACTED: sensitive-looking memory line
> This reviewer has measured balanced accuracy 0.XX, FNR 0.XX, FPR 0.XX on a
> gold set of <N> papers in <domain>. Rubric scores below have calibration
> error 卤X points. Treat borderline decisions with human judgement.
```

# REDACTED: sensitive-looking memory line

---

## Ensembling methodology notes

Lu 2026 Methods A.1.1 describes reviewer ensembling across 5 independent runs with majority voting. This mode follows that spec with two changes:

1. **Median instead of mean for rubric scores**: mean is vulnerable to single-run outliers (e.g., a run that hallucinates a methodological flaw); median is robust.
# REDACTED: sensitive-looking memory line

# REDACTED: sensitive-looking memory line

---

## Failure cases this mode does NOT fix

Calibration reports this reviewer's error profile on a **specific** gold set in a **specific** domain. It does not:

- Predict performance on papers outside that domain
- Detect frame-lock within a single paper review (that's `devils_advocate_reviewer` territory)
- Catch implementation-bug-as-finding cases (that's the AI Research Failure Mode Checklist, ROADMAP_v3.2.md item 2)
- Replace the `re-review` mode for revision verification

If the user's gold set is itself biased (e.g., all papers from one lab, all from one year), calibration reports a biased profile. Emit a warning during intake if papers share obvious metadata clusters.

---

## Integration with existing modes

| Existing mode | Interaction with calibration |
|---|---|
| `full` | Calibration runs `full` 5x per gold paper. No change to `full` itself. |
| `re-review` | Calibration profile attaches to re-review decisions. |
| `quick` | Calibration profile attaches. Confidence disclosure notes that `quick` has additional uncalibrated error on top of the measured profile. |
| `methodology-focus` | Calibration should ideally be run with methodology-heavy gold papers if this mode is the user's target. |
| `guided` | Not applicable 鈥?guided mode is Socratic dialogue, rubric scores are not the primary output. |

---

## Resolved design decisions (2026-04-09)

- **Activation**: opt-in only. User invokes `calibration` mode explicitly. ARS does not auto-calibrate on first use in a new domain.
# REDACTED: sensitive-looking memory line
- **Shipped gold sets**: not planned for v3.2. Users bring their own gold set. Shipping a built-in ML gold set was considered and rejected to avoid domain-coverage bias and staleness.
- **Continuous/self-calibration**: rejected. Using the reviewer's own historical decisions as pseudo-ground-truth is circular and would make the error profile look better over time without actually improving accuracy.

---

## References

- Lu, C. et al. (2026). Towards end-to-end automation of AI research. *Nature* 651, 914-919. doi:10.1038/s41586-026-10265-5 鈥?Table 1 (reviewer validation), Methods A.1.1 (ensembling).
- Efron, B. & Tibshirani, R. J. (1993). *An Introduction to the Bootstrap*. Chapman & Hall/CRC 鈥?bootstrap CI methodology.
- ARS `shared/cross_model_verification.md` 鈥?cross-model reviewer integration.
- ARS `academic-paper-reviewer/references/quality_rubrics.md` 鈥?scoring rubric definitions.

## v3.6.2 sprint contract status

v3.6.2 introduces sprint contracts for `reviewer_full` and `reviewer_methodology_focus` only. A template for this mode will follow in a subsequent patch release. Until then, this mode runs without contract enforcement and retains its pre-v3.6.2 behaviour.

# Argumentation & Reasoning Framework

A cognitive framework for evaluating the strength and validity of research arguments. Use this to **think about** argument quality, not just check boxes.

## Toulmin Model of Argumentation

Every research argument has 6 components. When evaluating, identify each:

| Component | Question | Red Flag if Missing |
|-----------|----------|-------------------|
| **Claim** | What is being asserted? | Vague or shifting thesis |
| **Data/Evidence** | What evidence supports it? | Claims without empirical backing |
| **Warrant** | Why does the evidence support the claim? | Logical gap between data and conclusion |
| **Backing** | What supports the warrant itself? | Assumed methodology validity |
| **Qualifier** | How certain is the claim? | Absolute language ("proves", "always") |
| **Rebuttal** | What would undermine the claim? | No acknowledged limitations |

**Judgment heuristic**: If you can't identify the Warrant, the argument is likely weak regardless of how much Data is presented. Data without Warrant is just information.

## Causal Reasoning (Bradford Hill Criteria, adapted)

When a paper claims X causes Y, evaluate against these 9 criteria:

1. **Strength of association** 鈥?How large is the effect?
2. **Consistency** 鈥?Replicated across studies/contexts?
3. **Specificity** 鈥?Does X specifically lead to Y (not everything)?
4. **Temporality** 鈥?Does X precede Y? (Only mandatory criterion)
5. **Biological/theoretical gradient** 鈥?More X 鈫?more Y?
6. **Plausibility** 鈥?Is there a reasonable mechanism?
7. **Coherence** 鈥?Consistent with existing knowledge?
8. **Experiment** 鈥?Is there experimental evidence?
9. **Analogy** 鈥?Do similar causes produce similar effects?

**Judgment heuristic**: Most social science papers satisfy 3-5 criteria. Fewer than 3 = causal claim is unsupported. Only #4 (temporality) is strictly required; the rest are cumulative evidence.

## Inference to Best Explanation (IBE)

When multiple explanations exist for the same finding:

# REDACTED: sensitive-looking memory line
2. Evaluate each on: **explanatory scope** (how much it explains), **simplicity** (fewer ad-hoc assumptions), **fit** (consistency with known facts), **predictive power** (does it predict new observations?)
# REDACTED: sensitive-looking memory line

**Judgment heuristic**: If the paper only considers one explanation, that's confirmation bias regardless of how well-argued it is. At minimum, the Discussion section should address the two strongest alternative explanations.

## Epistemic Status of Claims

Not all claims carry equal weight. Classify each major claim:

| Status | Meaning | Appropriate Language |
|--------|---------|---------------------|
| **Established** | Replicated, peer-reviewed, high consensus | "X is..." |
| **Supported** | Evidence exists but not yet replicated | "Evidence suggests X..." |
| **Preliminary** | Single study or small sample | "Preliminary findings indicate..." |
| **Speculative** | Based on reasoning, not direct evidence | "We hypothesize that..." |
| **Contested** | Conflicting evidence exists | "While some studies find X, others..." |

**Judgment heuristic**: If a paper uses "Established" language for "Preliminary" findings, that's overclaiming 鈥?one of the most common quality issues in academic writing.

## Application by Agent

| Agent | Primary Use |
|-------|------------|
| `synthesis_agent` | Toulmin analysis of synthesized arguments; IBE for competing explanations |
| `devils_advocate_agent` | Causal reasoning audit; identify missing Rebuttals and Qualifiers |
| `source_verification_agent` | Epistemic status classification of source claims |
| `socratic_mentor_agent` | Guide users through Toulmin decomposition of their own arguments |
| `research_architect_agent` | Ensure methodology design supports causal claims at appropriate level |

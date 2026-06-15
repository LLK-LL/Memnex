# Scientific Paper Architecture

## Purpose

Use this reference when the user wants the report to read like a rigorous scientific paper rather than a progress log.

## Claim-First Planning

Before drafting, create a short claim map:

| Element | Question |
|---|---|
| Problem | What exact technical problem is studied? |
| Importance | Why does the problem matter in this field? |
| Gap | What do existing methods fail to solve? |
| Method | What is the proposed route or core design? |
| Evidence | What experiments, analyses, or results support it? |
| Contribution | What changes because of this work? |

Do not draft prose until the claim map is coherent.

## Section Logic

### Introduction / Background

Use a five-part movement:

1. Problem context
2. Importance
3. Difficulty
4. Existing gap
5. Proposed approach and current progress

For midterm reports, mention "本文/本课题拟..." for planned work and "目前已..." for completed work.

### Related Work

Group papers by method family, task setting, or limitation:

- rule-based or traditional methods
- machine learning methods
- deep learning or foundation-model methods
- task-specific or domain-specific methods
- evaluation datasets and benchmarks

End each group by explaining what remains unresolved.

### Method / Technical Route

Use problem-design-advantage structure:

1. Problem: what limitation or subproblem is addressed
2. Design: what module, algorithm, model, or pipeline is used
3. Advantage: why this design helps, tied to mechanism or evaluation

Keep symbols, variable definitions, and module names stable.

### Experiments / Evaluation

For each experiment, state:

- purpose
- dataset or scenario
- baseline or comparison
- metric
- result or expected result
- interpretation

If results are not ready, describe the evaluation protocol and clearly mark planned experiments.

### Contribution

Write contributions as specific research outputs, not inflated novelty claims:

- "构建了..."
- "设计了..."
- "提出了..."
- "实现了..."
- "在...数据集/场景下进行了验证"

Avoid "首次", "突破性", "显著提升" unless supported by evidence and comparison.

## Cohort-Informed Writing

When the target field or school has strong conventions, inspect 3 to 5 representative papers, theses, or prior midterm reports. Record:

- section order
- paragraph pattern
- terminology
- figure/table style
- how contributions are stated
- how limitations are handled

Let the local cohort override generic advice.

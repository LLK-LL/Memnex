# Task: Mathematical Notation

When writing or checking mathematical expressions, follow the ICLR/deep-learning-book notation standard defined in `resources/math_commands.tex`. Do not invent your own formatting.

## Core Principle

Every category of mathematical object has a dedicated command. Never write raw `\mathbf`, `\mathcal`, `\mathbb`, or `\bm` directly in the body text—use the predefined macros instead. This keeps notation consistent and makes future refactoring easy.

## Convention Table

| Object type | Command pattern | LaTeX rendering | Example |
|---|---|---|---|
| Vector | `\va` … `\vz`, `\vmu`, `\vtheta`, `\veps`, `\vzero`, `\vone` | `\bm{x}` (bold italic) | `\vx` for vector **x** |
| Matrix | `\mA` … `\mZ`, `\mBeta`, `\mPhi`, `\mLambda`, `\mSigma` | `\bm{X}` (bold italic) | `\mW` for matrix **W** |
| Tensor | `\tA` … `\tZ` | `\bm{\mathsfit{X}}` (bold sans-serif italic) | `\tX` for tensor X |
| Random variable (scalar) | `\ra` … `\rz`, `\reta` | `\textnormal{x}` (upright) | `\rx` for random var x |
| Random vector | `\rva` … `\rvz`, `\rvtheta`, `\rvepsilon` | `\mathbf{x}` (bold upright) | `\rvx` for random vector x |
| Random matrix | `\rmA` … `\rmZ` | `\mathbf{X}` (bold upright) | `\rmX` for random matrix X |
| Element of a vector | `\eva` … `\evz`, `\evalpha` … | plain italic | `\evx` for scalar element x |
| Element of a matrix | `\emA` … `\emZ`, `\emSigma` | plain upright | `\emX` for scalar element X |
| Element of a tensor | `\etA` … `\etZ`, `\etLambda` | `\mathsfit{X}` (sans-serif) | `\etX` |
| Graph / function space | `\gA` … `\gZ` | `\mathcal{X}` | `\gL` for loss function ℒ |
| Set / number system | `\sR`, `\sN`, `\sZ`, etc. | `\mathbb{R}` | `\sR` for ℝ |

## Vectors — the Most Common Case

Vectors are the most frequently misused object. The rule is simple:

- **Correct:** `\vx`, `\vy`, `\vw`, `\vtheta` (uses `\bm{}`, bold italic)
- **Wrong:** `\mathbf{x}` (that is for *random* vectors), `\vec{x}` (arrow notation, not used in this style), plain `x` (indistinguishable from a scalar)

Greek letter vectors have their own named commands: `\vmu`, `\vtheta`, `\veps`.

## Project Setup — First-Time Use

Before writing or checking any math in a new project, ensure `math_commands.tex` is present and wired in.

**Step 1 — Copy the file into the user's project:**

The canonical file lives at `resources/math_commands.tex` inside this skill. Copy it to the root of the user's LaTeX project (next to the main `.tex` file):

```bash
cp <skill-root>/resources/math_commands.tex <project-root>/math_commands.tex
```

**Step 2 — Add the `\input` line to the preamble:**

In the main `.tex` file, add the following line in the preamble (after `\documentclass` and package declarations, before `\begin{document}`):

```latex
\input{math_commands}
```

**Step 3 — Compile to confirm:**

Run the standard compilation workflow (see `tasks/latex-compilation.md`) to verify no errors are introduced by the new file.

Only do this once per project. If `math_commands.tex` is already present in the project folder, skip to writing or checking math directly.

## When Writing New Math

1. Check the convention table above before choosing notation.
2. Use the predefined macro. If a needed symbol is not covered (e.g., a new Greek vector), define a new command following the same pattern (`\def\vphi{{\bm{\phi}}}`) rather than writing `\bm{\phi}` inline. Add the definition to `math_commands.tex` in the project, not inline in the body.
3. Recompile after any addition to `math_commands.tex`.

## When Checking Existing Math

Look for these common violations and correct them:

- Bare `\mathbf{x}` used for a deterministic vector → replace with `\vx`
- `\vec{x}` arrow notation → replace with `\vx`
- Inconsistent casing (vector written as uppercase, matrix as lowercase)
- Greek letters written without a vector macro (e.g., `\theta` where `\vtheta` is intended)
- Missing `\bm{}` package or `math_commands.tex` input in the preamble

## Other Useful Macros in `math_commands.tex`

| Command | Meaning |
|---|---|
| `\E` | Expectation `𝔼` |
| `\R` | Real numbers `ℝ` |
| `\KL` | KL divergence `D_KL` |
| `\Var`, `\Cov` | Variance, covariance |
| `\argmax`, `\argmin` | Properly typeset arg max/min |
| `\Tr` | Trace operator |
| `\dd` | Differential `d` (upright) |
| `\normlzero` … `\normmax` | L0 … L∞ norms |
| `\softmax`, `\sigmoid` | Named activation functions |
| `\figref`, `\secref`, `\eqref` | Cross-references (lower-case) |
| `\Figref`, `\Secref`, `\Eqref` | Cross-references (sentence-initial) |

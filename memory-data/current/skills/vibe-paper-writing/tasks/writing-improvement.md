# Task: Writing Improvement

This task covers logical restructuring and prose refinement. The governing constraint throughout is: **do not alter the paper's intended claims or meaning**. Every change must preserve what the authors want to say; only the order and expression may be improved.

---

## 1. Linearizing the Logical Flow

Academic papers sometimes develop in a non-linear way during drafting, leaving forward dependencies: the reader encounters a concept, term, or result in section N that only becomes fully meaningful after reading section M > N. This is the primary target of logical improvement.

**The goal:** every sentence and paragraph should depend only on what has already been established, not on what comes later.

### How to identify non-linear dependencies

- A term is used before it is defined.
- A claim is made that implicitly assumes a result or method introduced later.
- A paragraph refers to a distinction or contrast that the reader has not yet been given the tools to appreciate.
- A motivation section mentions a problem that is only fully described in the methods section.

### How to fix them

Prefer reordering over rewriting. The cleanest fix is usually to move the dependent content so it appears after the content it depends on. Large-scale reorderings—moving entire paragraphs or subsections—are acceptable and often necessary.

When reordering alone is insufficient (e.g., the non-linearity spans sections that cannot be easily rearranged), add a brief bridging sentence that summarizes the dependency in plain terms, so the reader can proceed without having to hold an unresolved reference in mind.

After any reordering, verify that:
- All cross-references (`\secref`, `\figref`, etc.) still point to the correct locations.
- Transition sentences at the boundaries of moved blocks are updated to reflect the new context.

---

## 2. Abbreviation Policy

Abbreviations reduce verbosity but impose a cognitive cost on the reader, who must map the abbreviation back to its meaning throughout. Apply the following rules strictly.

**Use an abbreviation when:**
- The term consists of three or more words (e.g., *Large Language Model* → LLM, *Variational Autoencoder* → VAE).
- The abbreviation is already widely recognized in the field and appears frequently in the paper.

**Do not use an abbreviation when:**
- The term consists of two words only (e.g., *Diffusion Model*, *Reward Model*, *Attention Mechanism*). Write it out in full every time. The two-word form is short enough that an abbreviation saves little space while adding lookup cost.
- The abbreviated form would be used fewer than approximately five times in the paper. In that case, define the term once and use the full form thereafter.

When reviewing existing text, replace disallowed abbreviations with their full forms throughout the document. If an abbreviation was defined in the text (e.g., "Diffusion Model (DM)"), remove the parenthetical definition and replace all subsequent uses of the abbreviation with the full term.

---

## 3. Moving Content to the Appendix

Mathematical derivations, proof details, hyperparameter tables, and other material that is correct but not essential to following the main argument are candidates for the appendix.

Move content to the appendix when:
- The main narrative flows more cleanly without it.
- The content is referenced by the main text but not required to understand the core claims.
- The section is already logically self-contained and can be detached without creating a gap.

Do not move content to the appendix when:
- It contains the primary contribution (a key theorem, the main algorithm, the central experimental result).
- Its absence would leave a logical gap that the reader cannot bridge from the surrounding text.

When moving a block to the appendix:
1. Create or extend the appendix section in the `.tex` file.
2. Replace the moved block in the main text with a concise forward reference (e.g., "We provide the full derivation in Appendix~\ref{app:derivation}.").
3. Ensure the appendix section has a clear heading and is self-contained.
4. Compile to confirm all references resolve correctly.

---

## Governing Constraint

All changes under this task—reordering, abbreviation replacement, appendix migration—must preserve the paper's intended meaning exactly. If a restructuring would require changing what a claim says (not just where or how it appears), stop and flag it for the user rather than proceeding unilaterally.

# Task: Paper Review

When asked to review or proofread a paper, work through the following checks in order. Each category has its own rules about what you may fix automatically versus what must be flagged for the user.

---

## 1. Internal Contradictions

Read for claims that contradict each other鈥攁cross sections, between a claim and its supporting evidence, or between the abstract/introduction and the body.

- You may fix contradictions directly when the correct resolution is unambiguous from context (e.g., one statement is clearly a stale remnant of an earlier draft).
# REDACTED: sensitive-looking memory line
- After completing all fixes, report every contradiction found and resolved, specifying the location (section, paragraph) and what was changed.

---

## 2. Consistency

### 2a. Terminological Consistency

Key terms must be introduced once and used uniformly throughout. Common violations:

- The same concept referred to by multiple names across sections (e.g., "latent variable," "hidden variable," and "latent code" used interchangeably without definition).
- Abbreviations introduced inconsistently (e.g., defined in one section, re-introduced in another, or used before definition).
- Capitalization of technical terms changing between sections.

Fix terminological inconsistencies directly. In your report, list each term that was consolidated and the canonical form chosen.

### 2b. Mathematical Symbol Consistency

Every symbol must refer to exactly one quantity throughout the paper.

- Scan for the same letter or symbol used to denote different quantities in different sections (e.g., `k` used as a kernel function in one equation and as a count in another).
- Scan for the same quantity denoted by different symbols in different sections.
- Check that all symbols are defined before first use and that definitions are not silently overridden.
- Cross-reference with `math_commands.tex` conventions if the project uses them (see `tasks/math-notation.md`).

Fix symbol inconsistencies directly. Report every change made, including the old symbol, the new symbol, and all locations updated.

---

## 3. Figure and Table References

Check that every `\figref`, `\ref`, or equivalent cross-reference to a figure or table is accurate given the surrounding context.

- Confirm that the referenced figure/table actually contains what the surrounding text claims it shows.
- Confirm that the figure number has not drifted due to reordering (a common issue in evolving drafts).
- Check that every figure and table in the document is referenced at least once in the text.
- Check that every figure reference in the text points to a figure that exists.

Do not modify figure content. If a reference appears wrong, fix the reference label or surrounding description, and flag any cases where the figure itself may need updating.

---

## 4. Privacy and Anonymization

# REDACTED: sensitive-looking memory line

**Do not modify any of this content yourself.** Instead, compile a list and present it to the user at the end of your review.

Common privacy risks to flag:

# REDACTED: sensitive-looking memory line
- Institution names, department names, or lab names in the body text, footnotes, or figure captions.
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
- Funding acknowledgments naming specific grants or agencies that could identify the team.

Present these findings as a dedicated section in your report, clearly labeled **Anonymization Warnings**, so the user can review and decide what to redact before submission.

---

## Report Format

After completing all four checks, provide a structured report in this order:

1. **Contradictions fixed** 鈥?location, original claim, revised claim.
2. **Consistency fixes** 鈥?terminology changes and symbol changes, each with locations.
3. **Figure/table reference issues** 鈥?any mismatch or orphaned references found and how they were resolved.
4. **Anonymization Warnings** 鈥?list of locations with potentially identifying content. No edits made; user must decide.

If a category is clean, state that explicitly rather than omitting it.

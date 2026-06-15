# Task: Citations and References

Users may point to a paper, a passage, or a finding and ask you to add it as a citation.

## Step 1 — Identify Intent

Before deciding where to place the citation, determine *why* the user wants to cite it. The same paper can serve very different rhetorical roles:

- Supporting an existing claim in the paper
- Providing background or historical context
- Offering a contrasting or competing view
- Establishing a gap that the paper fills
- Crediting prior methodology the paper builds on

If the user's instruction does not make the intent clear, ask before proceeding.

## Step 2 — Map to the Paper Structure

Locate the most natural home for this citation. Think beyond the obvious insertion point: a single new citation often has ripple effects. If the cited work is relevant to claims A, C, and D already in the paper—not just B where the user asked you to add it—acknowledge it at each relevant site, not only at the point of first insertion. A brief cross-reference or additional sentence at A, C, D may be warranted.

## Step 3 — Integrate Gracefully

Avoid orphaned citations that appear without surrounding explanation. The sentence(s) surrounding the citation should make clear what it is doing rhetorically—supporting, contrasting, extending, or contextualizing. A bare `\cite{foo}` appended to an existing sentence is rarely sufficient.

## Step 4 — BibTeX Hygiene

- Add the entry to the `.bib` file using a consistent key convention (e.g., `AuthorYear` or `AuthorYearKeyword`).
- Include all required fields for the entry type (author, title, journal/booktitle, year, volume, pages, doi as appropriate).
- After adding the entry, compile to confirm the key resolves without warnings.

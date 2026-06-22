# Citation Parser

Strategy reference for extracting citations from documents. Used by Workflow 2 (Citation Verification).

## Extraction by Source Format

### .docx

**Method:** Use python-docx to iterate paragraphs. For each paragraph, apply regex patterns below in order.

**Preprocessing:**
- Skip paragraphs inside EndNote field codes: if paragraph text matches `ADDIN EN\.\w+`, skip entire paragraph.
- Skip Zotero field codes: if paragraph text matches `\{[|]?\|[^}]+\}`, skip.
- Strip inline Zotero markers: remove `\{citation:\d+\}` spans from text.

**Regex patterns** (apply to cleaned text):

| Pattern | Target | Example |
|---------|--------|---------|
| `10\.\d{4,}/[^\s]+` | DOI | `10.1038/nature14539` |
| `PMID:?\s*\d{7,8}` | PMID | `PMID: 28344011` |
| `PMCID:?\s*PMC\d+` | PMCID | `PMCID: PMC5390525` |
| `arXiv:\s*\d{4}\.\d{4,}(v\d+)?` | arXiv ID | `arXiv: 1706.03762v7` |

### .tex / .bib

**Method:** Read file as text. Apply patterns:

| Pattern | Target |
|---------|--------|
| `\\cite\{([^}]+)\}` | Citation keys (comma-separated) |
| `\\bibitem\{([^}]+)\}` | Bibitem keys |
| `@article\{([^,]+),` | BibTeX entry keys |
| `doi\s*=\s*\{([^}]+)\}` | DOI in BibTeX |
| `pmid\s*=\s*\{([^}]+)\}` | PMID in BibTeX |

**Resolution:** Citation keys 鈫?resolve via .bib file `@article` entries. If standalone .tex without .bib, flag as `manual_needed`.

**natbib/biblatex:** `\\citep`, `\\citet`, `\\textcite` all reduce to `\\cite` semantics for key extraction.

### .txt

**Method:** Line-by-line scan. Apply the same DOI/PMID/arXiv regex patterns as .docx.

**Edge cases:**
- Paste-imported references may have line-wrapping that splits DOIs. Before scanning, join lines where the previous line ends mid-DOI pattern (no terminal punctuation, next line starts with alphanumeric).
# REDACTED: sensitive-looking memory line

## Resolution Priority

For each extracted reference:
1. DOI 鈫?`get_paper_by_doi` or `search_crossref`
2. PMID 鈫?`pubmed_fetch_articles`
3. arXiv ID 鈫?`search_arxiv`
# REDACTED: sensitive-looking memory line
5. Citation key only (unresolvable from .bib) 鈫?`manual_needed`

## Classification Labels

| Label | Condition |
|-------|-----------|
| `verified` | Retrieved metadata matches document metadata (title + journal + year all match) |
| `mismatch` | Retrieved metadata exists but conflicts with document |
| `not_found` | No match found in any database |
| `suspicious` | Match found but metadata incomplete (e.g., missing DOI, only partial title match) |
| `manual_needed` | Cannot resolve to a database query (no DOI/PMID, title too generic) |

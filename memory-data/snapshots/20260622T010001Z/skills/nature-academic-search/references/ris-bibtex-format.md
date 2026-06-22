# RIS and BibTeX Format Specifications

## RIS Format

RIS is the standard import format for EndNote, Zotero, and most reference managers.

### Journal article template
```
TY  - JOUR
AU  - Last, First
AU  - Last2, First2
TI  - Article Title
JO  - Journal Name (full)
JA  - Journal Abbreviation
PY  - 2024
VL  - 10
IS  - 3
SP  - 123
EP  - 145
DO  - 10.1234/example
UR  - https://doi.org/10.1234/example
AB  - Abstract text
KW  - keyword1
KW  - keyword2
AN  - PMID:12345678
DB  - PubMed
ER  -
```

### MEDLINE-to-RIS field mapping

| MEDLINE tag | RIS tag | Notes |
|---|---|---|
| `PMID-` | `AN  - PMID:` | Accession number |
| `TI  -` | `TI  -` | Title |
| `AU  -` | `AU  -` | Last, First format |
| `JT  -` | `JO  -` | Full journal title |
| `TA  -` | `JA  -` | Journal abbreviation |
| `DP  -` | `PY  -` | Extract year only |
| `VI  -` | `VL  -` | Volume |
| `IP  -` | `IS  -` | Issue |
| `PG  -` | `SP  -` / `EP  -` | Split on `-` |
| `AB  -` | `AB  -` | Abstract |
| `MH  -` | `KW  -` | MeSH as keywords |
| `LID -` | `DO  -` | DOI (strip `[doi]` suffix) |
| `AID -` | `DO  -` | Alternative DOI field |
| `SO  -` | `JO  -` | Source (journal + date + vol + pages) |

### RIS record separator
Each record must end with `ER  -` followed by a blank line.

## BibTeX Format

### Journal article template
```bibtex
@article{pmid12345678,
# REDACTED: sensitive-looking memory line
  title   = {Article Title},
  journal = {Journal Name},
  year    = {2024},
  volume  = {10},
  number  = {3},
  pages   = {123--145},
  doi     = {10.1234/example},
  url     = {https://doi.org/10.1234/example},
  abstract = {Abstract text},
  pmid    = {12345678}
}
```

### Citation key convention
- Use `pmid` prefix + PMID: `pmid12345678`
# REDACTED: sensitive-looking memory line
- If duplicate keys: append `a`, `b`: `smith2024a`

### MEDLINE-to-BibTeX field mapping

| MEDLINE tag | BibTeX field | Notes |
|---|---|---|
| `PMID-` | `pmid` | Custom field |
| `TI  -` | `title` | Wrap in `{...}` to preserve case |
# REDACTED: sensitive-looking memory line
| `JT  -` | `journal` | Full journal title |
| `DP  -` | `year` | Extract 4-digit year |
| `VI  -` | `volume` | |
| `IP  -` | `number` | |
| `PG  -` | `pages` | Replace `-` with `--` |
| `AB  -` | `abstract` | |
| `LID -` / `AID -` | `doi` | Strip `[doi]` suffix |

### Required fields by entry type

# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line

### BibTeX cleaning rules
# REDACTED: sensitive-looking memory line
- Wrap titles with special characters in `{...}`
- Strip HTML tags from abstract
# REDACTED: sensitive-looking memory line
- Sort entries alphabetically by citation key

## ENW (EndNote Tagged) Format

ENW uses percent-tagged fields for EndNote import. Supported by EndNote desktop and EndNote Web.

### Journal article template
```
%0 Journal Article
%T Article Title
%A Last, First
%A Last2, First2
%J Journal Name
%V 10
%N 3
%P 123-145
%D 2024
%R 10.1234/example
%U https://doi.org/10.1234/example
%X Abstract text
```

### MEDLINE-to-ENW field mapping

| MEDLINE tag | ENW tag | Notes |
|---|---|---|
| `TI  -` | `%T` | Title |
# REDACTED: sensitive-looking memory line
| `JT  -` | `%J` | Full journal title |
| `VI  -` | `%V` | Volume |
| `IP  -` | `%N` | Issue |
| `PG  -` | `%P` | Pages |
| `DP  -` | `%D` | Year only |
| `LID -` / `AID -` | `%R` | DOI |
| 鈥?| `%U` | URL (derived from DOI) |
| `AB  -` | `%X` | Abstract |

### EndNote import instruction

In EndNote: File > Import > File, choose the `.enw` file, set Import Option to EndNote generated XML or Tagged format, then import.

## Text Escaping (ris_escape)

Applied to all free-text fields (TI, AU, JO, N2/AB, KW) in RIS and ENW output:

- HTML tags stripped: `<sup>1</sup>` 鈫?`1`
- Whitespace normalized: multiple spaces/newlines 鈫?single space
- Leading/trailing whitespace trimmed
- Abstract truncated to 500 chars in RIS/ENW to keep records compact

## Format Selection Guide

| User says | Use format |
|---|---|
| "EndNote", ".enw" | ENW (EndNote tagged) or RIS |
| "Zotero" | RIS (Zotero imports RIS natively) |
| "LaTeX", "BibTeX", "Bib" | BibTeX (.bib) |
| "PubMed format", "MEDLINE", ".nbib" | .nbib (default) |

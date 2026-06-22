# Search Strategy Guide

## Query Construction

### From topic to query
1. Extract core concepts from the research question
2. Identify synonyms and alternate spellings for each concept
3. For biomedical topics: map concepts to MeSH terms via `pubmed_lookup_mesh`
4. Assemble Boolean query: `(concept1 OR synonym1) AND (concept2 OR synonym2)`
5. Add field qualifiers for precision: `[Title/Abstract]`, `[MeSH Terms]`, `[Journal]`
6. Test and refine 鈥?if >500 results, add filters; if <10, broaden terms

### Query templates by domain

| Domain | Template |
|--------|----------|
| Medical | `("disease"[MeSH] OR "disease"[tiab]) AND ("treatment"[MeSH] OR "treatment"[tiab])` |
| Molecular | `("gene"[tiab] OR "protein"[tiab]) AND ("pathway"[tiab] OR "mechanism"[tiab])` |
| Epidemiology | `("condition"[MeSH]) AND (incidence OR prevalence OR "risk factor")` |
| Methods | `("method"[tiab]) AND ("application"[tiab]) AND (validation OR comparison)` |

## Source Selection

### Decision tree
```
Topic is medical/clinical?
鈹溾攢 Yes 鈫?PubMed primary, Google Scholar secondary
鈹斺攢 No 鈫?Topic is CS/physics/math?
    鈹溾攢 Yes 鈫?arXiv primary, Semantic Scholar secondary
    鈹斺攢 No 鈫?CrossRef primary, Semantic Scholar secondary
```

### Journal scope awareness
- Nature Portfolio journals: use `nature.com` domain filter
- Chinese journals: CNKI/涓囨柟 not indexed in PubMed/CrossRef 鈥?flag for manual check
- Preprints only: arXiv, bioRxiv, medRxiv 鈥?no peer review status available

## Deduplication Logic

See [Dedup Engine](dedup-engine.md) for the unified deduplication strategy shared by Workflows 1, 2, and 5a.

## Result Ranking

### Default: relevance
Use the search engine's default relevance ranking.

### Date-weighted
When user requests "recent" or "latest": sort by publication date descending.

### Citation-weighted
When user cares about impact: sort by citation count descending (available via CrossRef or Semantic Scholar).

### Combined scoring
For systematic reviews: `score = relevance * 0.5 + recency * 0.3 + citations * 0.2`

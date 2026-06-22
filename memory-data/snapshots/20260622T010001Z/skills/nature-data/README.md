# `nature-data` skill

A data-availability skill for preparing manuscript data statements, repository plans, dataset
citations, and FAIR metadata checks in a Nature / Springer Nature publication style.

# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line

## What it does

- drafts ready-to-paste Data Availability statements
- audits weak or incomplete data statements before submission
- maps each supporting dataset to a repository, accession, DOI, or access route
- distinguishes public, controlled-access, third-party, supplementary, and not-applicable cases
- prepares FAIR metadata and DataCite-style dataset citation checks
- flags missing repository records, licences, provenance, embargo details, and access conditions
# REDACTED: sensitive-looking memory line

## Source hierarchy

- Nature Portfolio and Springer Nature research data policies
- Nature Portfolio reporting standards for availability of data, code, materials, and protocols
- Scientific Data data policies for repository, rawness, preservation, and data citation practice
- FAIR Guiding Principles and DataCite metadata schema

## File structure

The skill uses a router/static-dynamic split (like the other nature-* skills): a short `SKILL.md` router plus a `manifest.yaml`. nature-data is a linear workflow with no content axis, so the split is core (always loaded) plus on-demand references.

```text
nature-data/
鈹溾攢鈹€ SKILL.md                     # short router
鈹溾攢鈹€ manifest.yaml                # always_load core + on-demand references (no axis)
鈹溾攢鈹€ README.md
鈹溾攢鈹€ agents/
鈹?  鈹斺攢鈹€ openai.yaml
鈹溾攢鈹€ static/
鈹?  鈹斺攢鈹€ core/                    # always loaded
鈹?      鈹溾攢鈹€ stance.md            # default stance + source hierarchy
鈹?      鈹溾攢鈹€ chinese-mode.md      # Chinese-user operating mode
鈹?      鈹斺攢鈹€ workflow.md          # the 8-step workflow + output format
鈹斺攢鈹€ references/
    鈹溾攢鈹€ fair-metadata-checklist.md
# REDACTED: sensitive-looking memory line
    鈹溾攢鈹€ policy-principles.md
    鈹溾攢鈹€ repository-and-identifiers.md
    鈹溾攢鈹€ source-basis.md
    鈹斺攢鈹€ statement-patterns.md
```

## When to use

- preparing a Data Availability statement for a Nature-family or Springer Nature journal
- deciding where to deposit data before submission
- revising "available on request" language
- handling controlled-access, human-participant, proprietary, or third-party data
- citing datasets with DOI, accession number, Handle, ARK, or repository record
- checking whether a dataset deposit is FAIR enough for publication
- converting Chinese data-availability notes into precise English submission language

## Design intent

The skill should make the availability route explicit for every dataset that supports the paper's
claims. It should not fabricate accessions, licences, restrictions, or repository metadata. When
# REDACTED: sensitive-looking memory line
confirm, preferably with Chinese notes when the user is working from a Chinese draft.

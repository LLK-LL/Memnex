# `nature-paper2ppt` skill

A journal-club and lab-meeting skill for turning scientific papers into concise Chinese
PowerPoint decks with a Nature-style evidence narrative.

The skill accepts a paper PDF, preprint, article text, abstract plus figure legends, or
structured reading notes. It identifies the paper type, extracts the scientific argument,
selects only the figures that support that argument, writes Chinese slide content and
speaker notes, builds a real `.pptx`, and performs lightweight package QA.

## What it does

- converts a scientific paper into a 10-16 slide Chinese presentation
- keeps the paper's argument as the slide spine instead of copying section order
- classifies the paper type before choosing the narrative logic
- selects key figures, tables, or panels as evidence rather than decoration
- crops dense figure panels when full figures would be unreadable
- writes Chinese titles, concise bullets, captions, takeaways, and speaker notes
- creates an actual editable `.pptx` deck as the primary deliverable
- records used figure assets in an asset manifest when figures are extracted
- runs lightweight QA on slide count, embedded media, speaker notes, and PPTX package structure

## Source and design hierarchy

- Nature-style scientific reporting logic: problem, gap, claim, evidence, validation,
  reuse value, limitations, and discussion
- Academic journal-club practice: short live-presentation slides rather than dense
  reading notes
- Evidence-first slide design: one dominant figure or table per result slide when possible
- Low-overhead production: avoid exhaustive OCR, figure extraction, and rendering unless
  they materially improve the deck

## File structure

The skill uses a router/static-dynamic split (like `nature-writing`, `nature-polishing`, and `nature-reader`): a short `SKILL.md` router plus a `manifest.yaml` that loads only the fragments a given job needs.

```text
nature-paper2ppt/
鈹溾攢鈹€ SKILL.md                     # short router: detect paper_type, load fragments
鈹溾攢鈹€ manifest.yaml                # always_load core + paper_type axis + on-demand references
鈹溾攢鈹€ README.md
鈹溾攢鈹€ static/
鈹?  鈹溾攢鈹€ core/                    # always loaded
鈹?  鈹?  鈹溾攢鈹€ principles.md        # purpose, core principle, lean mode, inputs, language
鈹?  鈹?  鈹溾攢鈹€ toolchain.md         # cross-platform Python stack + default fast path
鈹?  鈹?  鈹溾攢鈹€ workflow.md          # the 9-step spine
鈹?  鈹?  鈹斺攢鈹€ output-and-quality.md# output package, citation, quality, fallback rules
鈹?  鈹斺攢鈹€ fragments/
鈹?      鈹斺攢鈹€ paper_type/          # one presentation arc per type (loaded on match)
鈹?          鈹溾攢鈹€ discovery.md     # question-to-evidence
鈹?          鈹溾攢鈹€ methods.md       # problem-to-solution
鈹?          鈹溾攢鈹€ resource.md      # workflow-to-validation
鈹?          鈹溾攢鈹€ clinical.md      # design-to-inference
鈹?          鈹溾攢鈹€ materials.md     # property-to-mechanism / design-to-performance
鈹?          鈹斺攢鈹€ review.md        # evidence-map
鈹斺攢鈹€ references/                  # opened on demand
    鈹溾攢鈹€ design-and-layout.md     # composition, layout, typography, anti-template, archetypes
    鈹溾攢鈹€ figure-assets.md         # figure selection, extraction, crop self-check
    鈹斺攢鈹€ self-review.md           # self-review loop, severity, programmatic checks, verification
```

The shared Terminology Ledger (`../_shared/core/terminology-ledger.md`) is loaded on every job so technical terms stay consistent across slides.

## When to use

- making a PPT or PPTX from a research paper PDF
- preparing a journal club, group meeting, lab meeting, paper sharing, or thesis seminar
- summarising a Nature-family paper into Chinese slides
- turning article text, figure legends, or reading notes into a presentation
- creating a figure-integrated deck rather than only an outline or summary
- needing speaker notes, source labels, and a QA report for the deck

## Default output package

The expected default output is a small working folder containing:

```text
output/
鈹溾攢鈹€ final_presentation_cn.pptx
鈹溾攢鈹€ qa_report.md
鈹溾攢鈹€ asset_manifest.md          # when source figures/tables are extracted
鈹斺攢鈹€ assets/
    鈹斺攢鈹€ figures/
```

Optional outline or script files may be created when they help review or debugging, but
the `.pptx` remains the main deliverable.

## Presentation logic

The default arc helps the audience answer:

1. Why does this problem matter?
2. What gap or bottleneck does the paper address?
# REDACTED: sensitive-looking memory line
4. What is the key evidence?
5. Why should we trust the result?
6. What is new, reusable, or broadly meaningful?
7. Where are the boundaries and open questions?

The skill adapts this arc by paper type. Discovery papers use a question-to-evidence
logic; methods, AI, and tool papers use problem-to-solution; resources and atlases use
workflow-to-validation; reviews use an evidence-map structure.

## Design intent

The skill should create a deck that can be used directly in an academic oral report. It
should be concise, figure-led, and evidence-aware. It should not fabricate values,
methods, mechanisms, datasets, or figure interpretations that are not supported by the
source paper.

Dense result visuals should be cropped, split, or given their own slide instead of being
shrunk into a symmetrical two-column layout. Explanatory text should stay short on slides,
with deeper interpretation moved into speaker notes.

## Notes

- Default language is Simplified Chinese while preserving important technical terms,
  abbreviations, gene names, model names, equations, and statistical terms in English.
- The skill is designed for research papers across domains, not only biomedical papers.
- When no reliable headless renderer is available, the skill performs structural QA and
  records that rendered preview QA was skipped.

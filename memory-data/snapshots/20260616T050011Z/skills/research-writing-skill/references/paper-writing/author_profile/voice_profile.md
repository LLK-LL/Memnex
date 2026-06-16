# Voice Profile

## Source
Derived from sentence-level analysis of multiple published papers across systems and ML venues.

---

## Sentence-Level Style

### Length
- Mean words/sentence in final versions: ~21
- Student drafts average ~24 words/sentence 鈥?the advisor compresses by ~12%
- Maximum sentence length in final versions: ~40 words (for contribution-list items)
- Shortest functional unit: single-clause Takeaway sentences

### Structure
- **Claim-first**: Topic sentences lead with the assertion, followed by evidence. State the claim before citing the table or figure.
- **Parallel construction in contribution lists**: "(1) Learning problem. We formulate... (2) Design. We implement... (3) Evaluation. We demonstrate..."
- **Rhetorical questions** (sparingly, in introductions only): "Do speed tests need to transmit their full data volume to produce accurate results?"
- **Colon elaboration**: "Three fundamental limitations: (i) non-stationarity... (ii) no tuning knob... (iii) inability to incorporate..."

### Voice markers
- Avoids first-person hedging: rarely "We believe" or "We think" 鈥?prefers "We show" or "This confirms"
- Zero exclamation marks in final versions
- Minimal use of "However" as a paragraph opener (used for gap transitions, never as filler)
- Active voice everywhere 鈥?no exceptions. "System X achieves" not "accuracy was achieved by System X." "We evaluate on dataset X" not "Experiments were conducted on dataset X." "We collected data from campus gateway" not "Data was collected from campus gateway." Passive voice is never the right choice 鈥?it obscures agency and weakens prose.

---

## Paragraph Density

### Sentences per paragraph
- Introduction labeled blocks: 3鈥? sentences (tight, focused)
- Design sections: 4鈥? sentences (mechanism explanations need space)
- Evaluation result paragraphs: 3鈥? sentences before a Takeaway
- Takeaway paragraphs: 1鈥? sentences (maximally compressed)

### Information density
- No empty "connector" paragraphs 鈥?every paragraph either (a) makes a claim, (b) presents evidence, or (c) synthesizes a takeaway
- **Signposting through claims, not placeholders.** Sections may open with a preamble that states the section's conclusion or purpose 鈥?"This section shows that event-centric decomposition reduces error 13脳 by analyzing three failure modes." What is banned is *content-free* preambles 鈥?"In this section, we describe our evaluation setup" 鈥?which delay the claim without guiding the reader. The test: does the opening sentence tell a skim-reader what the section *concludes*, or only what it *contains*?
- Quantitative data density in evaluation: one number per clause, pattern per paragraph, takeaway per experiment cluster

---

## Tone

### Assertive vs. hedged
- **Final versions are strongly assertive**: "System X achieves 2鈥?脳 higher savings" not "System X appears to offer improved savings"
- **Hedging reserved for scope limitations**: "Our evaluation focuses on dataset Y" (scoping, not undermining)
- **Calibrated confidence**: Claims match evidence scope. No "we solve the problem of" 鈥?instead "we address [specific aspect] of [bounded problem]"
- Measured academic register in ML venues: slightly less assertive than systems venues

### Tonal evolution from student draft to final
| Dimension | Student draft | Final version |
|-----------|-------------|---------------|
| Enthusiasm | "shown immense promise" | "is transforming" |
| Hedging | "can potentially offer" | "achieves" |
| Scope | "universal solution" | "methodology-agnostic layer" |
| Agency | "we propose" | "this paper does not focus on X; instead it addresses Y" |

---

## Vocabulary Patterns

### Preferred terms
- Infrastructure language: "layer", "substrate", "abstraction"
- Analysis-of-structure language: "disaggregation", "decomposition"
- Prioritization language: "first-order requirement"
- Design-parameter language: "configurable trade-off"
- Formal precision: "intrinsic evaluation"

### Avoided terms (consistently removed in editing)
- "novel" 鈥?never in final versions
- "significant" / "substantial" / "impressive" / "promising" 鈥?replaced with numbers
- "state-of-the-art" 鈥?used only when naming a specific prior system
- "paradigm" / "leverage" / "utilize" 鈥?academic filler
- "In this paper, we..." 鈥?always removed

### Named abstraction coining pattern
- The advisor typically coins 1鈥? named abstractions per paper
- Naming convention: compound noun phrase with architectural metaphor (e.g., "external termination layer," "progressive disaggregation," "intrinsic evaluation framework")
- Named abstractions appear ONLY in final versions 鈥?they are discovered through writing, not pre-planned

---

## Structural Preferences

### Labeled paragraphs (systems venues)
- Labels are short imperative phrases: "The opportunity.", "Key contributions.", "Limitations of existing approaches."
- Each label is a narrative contract 鈥?what follows must deliver on the label
- Removed for ML venues 鈥?replaced with colon-style subtitles

### Heading style
- **Systems venues**: Problem-driven. "Why do linear approaches fail?" / "Taming the tails"
- **ML venues**: Method-driven. "Embedding Analysis: quantifying representation space utilization"
- **Universal**: Claim-first in final versions. Never "Section 4" or "Evaluation Results" 鈥?always a claim or question

### Contribution framing
- Numbered, labeled list: "(1) Learning problem. (2) Design. (3) Evaluation."
- Each item starts with a bold domain label, followed by a claim (not a process description)
- "We show" preferred over "We propose" 鈥?positions the paper as delivering evidence, not promises

---

## Engineering Specificity

- Named protocols and tools, not generic references (not "network metrics" but "RTT, retransmissions, congestion window")
- Named data sources, not generic references (not "speed tests" but the specific benchmark names)
- Named scales: "2鈥?脳", "65% compression" (not "significantly reduced")
- Architecture as metaphor: "layer" = pluggable component; "substrate" = foundational platform; "framework" = evaluation methodology

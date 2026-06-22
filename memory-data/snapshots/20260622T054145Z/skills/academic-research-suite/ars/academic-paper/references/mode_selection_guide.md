# Mode Selection Guide

This guide helps users and the `intake_agent` select the most appropriate operational mode.

---

## Mode Selection Flowchart

```
User Input 鈫?
鈹?
鈹溾攢鈹€ Already have complete research?
鈹?  鈹溾攢鈹€ Yes 鈫?Want a full paper?
鈹?  鈹?  鈹溾攢鈹€ Yes 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈫?full mode
鈹?  鈹?  鈹斺攢鈹€ No 鈫?Just need an outline?
鈹?  鈹?      鈹溾攢鈹€ Yes 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈫?outline-only mode
鈹?  鈹?      鈹斺攢鈹€ No 鈫?Just need an abstract?
鈹?  鈹?          鈹溾攢鈹€ Yes 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈫?abstract-only mode
鈹?  鈹?          鈹斺攢鈹€ No 鈫?Just need a literature review?
鈹?  鈹?              鈹溾攢鈹€ Yes 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈫?lit-review mode
鈹?  鈹?              鈹斺攢鈹€ No 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈫?full mode
鈹?  鈹?
鈹?  鈹斺攢鈹€ No 鈫?Want guided thinking?
鈹?      鈹溾攢鈹€ Yes 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈫?plan mode 鈽?NEW
鈹?      鈹斺攢鈹€ No 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈫?full mode (Phase 0 will conduct an interview)
鈹?
鈹溾攢鈹€ Have an existing paper to revise? 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈫?revision mode
鈹溾攢鈹€ Just need format conversion? 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈫?format-convert mode
鈹斺攢鈹€ Just need a citation check? 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈫?citation-check mode
```

---

## Detailed Description of Each Mode

### full mode 鈥?Complete Paper Writing

**Applicable Scenarios**:
- User has a clear research question and (partial) materials
- Needs to produce a complete paper from start to finish
- Includes all phases: Interview 鈫?Literature 鈫?Structure 鈫?Argumentation 鈫?Writing 鈫?Citation 鈫?Review 鈫?Formatting

**Not Applicable When**:
- User has no idea about research direction (鈫?use `deep-research` first)
- Only need a specific section (鈫?use another specialized mode)

**Expected Output**: Complete paper draft + references + bilingual abstract + review report
**Expected Duration**: Long (all 8 Phases fully executed)
**Agents Used**: All 9 + socratic_mentor (if needed)

---

### outline-only mode 鈥?Outline Generation

**Applicable Scenarios**:
- Only need the paper structure and outline
- A proposal to submit to an advisor for review
- Need to quickly plan the paper structure

**Not Applicable When**:
- Need complete paper content (鈫?full mode)
- Need guided thinking (鈫?plan mode)

**Expected Output**: Detailed outline + evidence allocation + word count distribution
**Expected Duration**: Short (Phase 0-2)
**Agents Used**: intake 鈫?literature_strategist 鈫?structure_architect

---

### plan mode 鈥?Chapter-by-Chapter Guided Planning 鈽?NEW

**Applicable Scenarios**:
- User has ideas but they are not yet clear enough
- Wants guided thinking for each chapter's content
- First-time academic paper writer
- Wants to think through every section before writing
- Just received materials from deep-research and needs to transform them into a paper plan

**Not Applicable When**:
- Already knows exactly what to write (鈫?full mode is faster)
- Only needs an outline without deep thinking (鈫?outline-only mode)
- Time-pressured and needs rapid output (鈫?full mode)

**Expected Output**: Chapter Plan + INSIGHT Collection
**Expected Duration**: Medium (Step 0-3, approximately 20-30 rounds of conversation)
**Agents Used**: intake 鈫?socratic_mentor 鈫?structure_architect 鈫?argument_builder

**Subsequent Connections**:
- Chapter Plan 鈫?full mode (produce complete paper)
- Chapter Plan 鈫?academic-paper-reviewer (review the plan)

---

### revision mode 鈥?Paper Revision

**Applicable Scenarios**:
- Already have a completed paper draft
- Received reviewer comments requiring revision
- Feel certain sections need improvement

**Not Applicable When**:
- No existing paper draft (鈫?full mode)
- Only need to check citation format (鈫?citation-check mode)

**Expected Output**: Revised paper + revision notes (tracked changes)
**Expected Duration**: Medium
**Agents Used**: peer_reviewer 鈫?draft_writer 鈫?citation_compliance

**Prerequisite**: User must provide existing paper content

---

### abstract-only mode 鈥?Abstract Writing

**Applicable Scenarios**:
- Paper is already complete, only need an abstract
- Need to submit a conference abstract
- Need a bilingual abstract

**Not Applicable When**:
- No paper content to summarize (鈫?full mode or plan mode)

**Expected Output**: Bilingual abstract (zh-TW + EN) + keywords
**Expected Duration**: Short
**Agents Used**: intake 鈫?abstract_bilingual

---

### lit-review mode 鈥?Literature Review

**Applicable Scenarios**:
- Need a literature review on a specific topic
- Preparing the Literature Review chapter of a paper
- Need a systematic search strategy and literature matrix

**Not Applicable When**:
- Need a complete paper (鈫?full mode)
- Need an in-depth research investigation (鈫?deep-research)

**Expected Output**: Annotated bibliography + literature matrix + synthesis analysis
**Expected Duration**: Medium
**Agents Used**: intake 鈫?literature_strategist

---

### format-convert mode 鈥?Format Conversion

**Applicable Scenarios**:
- Already have paper content, need format conversion
- Markdown 鈫?LaTeX / DOCX / PDF
- Need to comply with a specific journal's formatting requirements

**Not Applicable When**:
- No existing content (鈫?full mode)
- Need content modifications (鈫?revision mode)

**Expected Output**: Document in target format
**Expected Duration**: Short
**Agents Used**: formatter used standalone

---

### citation-check mode 鈥?Citation Check

**Applicable Scenarios**:
- Already have a paper, only need to check citation format
- Final check before submission
- Switching citation format (e.g., APA 鈫?IEEE)

**Not Applicable When**:
- No existing citation list (鈫?full mode)
- Need to modify paper content (鈫?revision mode)

**Expected Output**: Citation error report + automatic correction suggestions
**Expected Duration**: Short
**Agents Used**: citation_compliance used standalone

---

## Paths from deep-research

```
deep-research completed
  鈹?
  鈹溾攢鈹€ deep-research (full mode) outputs:
  鈹?  RQ Brief + Methodology Blueprint + Annotated Bibliography + Synthesis Report
  鈹?  鈹?
  鈹?  鈹溾攢鈹€ Want to write the paper directly 鈹€鈹€鈫?academic-paper (full mode)
  鈹?  鈹?  intake_agent auto-detects materials, skips redundant questions
  鈹?  鈹?
  鈹?  鈹斺攢鈹€ Want to plan before writing 鈹€鈹€鈫?academic-paper (plan mode)
  鈹?      socratic_mentor leverages existing materials to accelerate guidance
  鈹?
  鈹斺攢鈹€ deep-research (socratic mode) outputs:
      INSIGHT Collection + Synthesis Report
      鈹?
      鈹溾攢鈹€ INSIGHTs are sufficiently clear 鈹€鈹€鈫?academic-paper (full mode)
      鈹?
      鈹斺攢鈹€ Need more guidance 鈹€鈹€鈫?academic-paper (plan mode)
          socratic_mentor continues deepening from INSIGHTs
```

## Connecting to academic-paper-reviewer

```
academic-paper completed
  鈹?
  鈹溾攢鈹€ full mode produces complete paper 鈹€鈹€鈫?academic-paper-reviewer (full / guided)
  鈹?  Complete peer review + revision suggestions
  鈹?
  鈹溾攢鈹€ plan mode produces Chapter Plan 鈹€鈹€鈫?academic-paper-reviewer (guided)
  鈹?  Review the plan's feasibility and completeness
  鈹?
  鈹斺攢鈹€ reviewer feedback 鈹€鈹€鈫?academic-paper (revision mode)
      Revise paper based on review comments
```

---

## Common Misselection Scenarios

| User Says | Easily Misselected | Correct Choice | Reason |
|---------|---------|---------|------|
| "Help me write an outline" / 銆屽公鎴戝澶х侗銆?| outline-only | First confirm: Do they want a simple outline or deep planning? | May need plan mode |
| "I want to write a paper but don't know how to start" / 銆屾兂瀵珫鏂囦絾涓嶇煡閬撴€庨杭闁嬪銆?| full | plan mode | Needs guided thinking |
| "Help me revise my paper" / 銆屽公鎴戜慨鏀硅珫鏂囥€?| revision | First confirm: Are there reviewer comments? | May need full mode rewrite |
| "Help me search for literature" / 銆屽公鎴戞壘鏂囩嵒銆?| lit-review | First confirm: Is it a literature review for a paper or a research investigation? | May need deep-research |
| "I have deep-research results, help me write a paper" / 銆屾垜鏈夌爺绌剁祼鏋滐紝骞垜瀵垚璜栨枃銆?| full (skip Phase 0 directly) | full (but intake needs to detect handoff) | Materials need to be properly imported |
| "I want to plan my paper step by step" / 銆屾垜鎯抽€愭瑕忓妰璜栨枃銆?| outline-only | plan mode | Needs interactive guidance |
| "The paper format is wrong" / 銆岃珫鏂囨牸寮忎笉灏嶃€?| revision | citation-check or format-convert | May only need format correction |
| 銆屽付鎴戝璜栨枃銆?銆屽紩灏庢垜瀵珫鏂囥€?| full | plan mode | 浣跨敤鑰呴渶瑕佷簰鍕曞紡寮曞皫锛屼笉鏄洿鎺ョ敘鍑?|
| 銆岀涓€娆″璜栨枃銆?銆岃珫鏂囨柊鎵嬨€?| full | plan mode | 鏂版墜闇€瑕佽槆鏍兼媺搴曞紡閫愮珷寮曞皫 |

---

## Quick Decision Table

| What Do You Have? | What Do You Want? | Choose This Mode |
|-----------|-----------|------------|
| Nothing | Complete paper | plan mode 鈫?full mode |
| Research question + literature | Complete paper | full mode |
| Research question + literature | Outline | outline-only mode |
| Vague idea | Paper plan | plan mode |
| deep-research results | Complete paper | full mode (auto-handoff) |
| deep-research results | Guided planning | plan mode |
| Completed paper | Revision | revision mode |
| Completed paper | Abstract | abstract-only mode |
| Completed paper | Format conversion | format-convert mode |
| Completed paper | Citation check | citation-check mode |

---

### Plan to Full Mode Conversion Protocol

When a user completes `plan` mode and wants to proceed to `full` mode for actual paper writing:

#### Conversion Checklist

| Plan Mode Output | Full Mode Input | Conversion Action |
|-----------------|-----------------|-------------------|
| Chapter Plan (structure outline) | `structure_architect` agent | Map chapters 鈫?formal sections with heading levels; validate against `paper_structure_patterns.md` |
| Socratic Responses (Q&A transcripts) | `argument_builder` agent | Extract claims + evidence + warrants from dialogue; discard conversational scaffolding |
| Literature Notes (if any) | `literature_strategist` agent | Independent execution 鈥?plan mode notes serve as seed keywords only; full systematic search required |
| Argument Sketches | `argument_builder` agent | Evaluate each sketch against 4-level scoring; only `adequate` or above proceed |

#### Quality Gate

Before conversion, ALL of the following must be true:
- [ ] Every chapter in the Chapter Plan has at least 1 argument sketch rated `adequate` or above
- [ ] The overall paper structure maps to a recognized pattern in `paper_structure_patterns.md`
- [ ] At least 5 potential references have been identified (seeds for `literature_strategist`)
- [ ] The research question is finalized (not still evolving from Socratic dialogue)

#### What Gets Discarded
- Conversational filler from Socratic dialogue (greetings, confirmations, repetitions)
- Tentative ideas explicitly marked as "maybe" or "not sure" by the user
- Plan mode's iterative drafts (only the final version of each chapter plan carries over)

---

## Trigger-to-Mode Mapping Examples

```
"Write a paper on SDGs in HEI"           -> full
"Give me a paper outline for..."         -> outline-only
"Revise this paper based on feedback"    -> revision
"Write an abstract for this paper"       -> abstract-only
"Do a literature review on..."           -> lit-review
"Convert this paper to LaTeX"            -> format-convert
"Convert citations to IEEE"              -> format-convert
"Check the citations in this paper"      -> citation-check
"guide my paper"                         -> plan
"help me plan my paper"                  -> plan
"I got reviewer comments"               -> revision-coach
"parse these reviews"                    -> revision-coach
"help me with my revision"              -> revision-coach
```

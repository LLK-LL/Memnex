---
name: nature-citation
description: >-
  Add strict Nature/CNS citations to manuscript text by splitting long passages into citable
  segments, searching only accepted flagship and subjournal titles from Nature Portfolio, the
  AAAS Science family, and Cell Press, filtering by publication time range, and exporting one
  reference-manager-ready output by default. Use this skill whenever the user asks to input text and
  automatically get references, add citations to a paragraph/manuscript, find Nature-series or CNS
  support for statements, create text-to-reference correspondence, "鍒嗘寮曠敤", "鑷姩缁欏嚭寮曠敤",
  "Nature绯诲垪寮曠敤", "CNS鍙婂瓙鍒?, "鏀拺鏂囩尞", "琛ュ紩鐢?, "鎵惧紩鐢?, or export EndNote/RIS/ENW/Zotero RDF.
  Also trigger on general academic-writing citation needs even without the word "Nature", such as
  adding references while writing a paper, finding sources/literature for a claim, building a
  reference list, citation/referencing for academic writing, and Chinese phrasings like
  瀛︽湳鍐欎綔寮曠敤銆佸啓璁烘枃鍔犲紩鐢ㄣ€佸啓paper鎵炬枃鐚€佸姞鍙傝€冩枃鐚€侀厤鏂囩尞銆佸紩鐢ㄦ枃鐚€佹枃鐚敮鎾?
version: 2.0.0
# REDACTED: sensitive-looking memory line
---

# Nature Citation 鈥?Router

This skill is split into two layers:

- A **static layer** under `static/` that holds versioned, reusable content fragments (core principles and scope, the Chinese-user operating mode, and the citation workflow).
- A **dynamic layer** (this file plus `manifest.yaml`) that loads the core every time and reaches for heavier material only when a step needs it.

Do not try to apply the citation logic from memory or from this router. Always load fragments from disk as described below.

## Routing protocol

Follow these four steps every time the skill is invoked.

### 1. Load the manifest and the core layer

Read [manifest.yaml](manifest.yaml). Then read every file listed under `always_load`:

- `static/core/principles.md` 鈥?what the skill produces, the strict journal scope, the source hierarchy, and the search-quality rules.
- `static/core/chinese-mode.md` 鈥?how to operate when the user writes in Chinese or asks for `Nature绯诲垪`/`CNS鍙婂瓙鍒奰 style support.
- `static/core/workflow.md` 鈥?the seven-step workflow and the final report format.

### 2. No content axis 鈥?confirm scope and language inline

Unlike the other nature-* skills, nature-citation has no fragment axis. Its variation is runtime parameters, not different content bodies:

- **journal scope** 鈥?`Nature绯诲垪` / `CNS` / `CNS鍙婂瓙鍒奰 / flagship-only. Read it from the user's wording (see `core/principles.md`) and pass it to the script as `--scope`.
- **user language** 鈥?if the user writes Chinese, follow `core/chinese-mode.md` (Chinese notes, English search queries).
- **input length** 鈥?if there are more than ~10 segments, switch to the batched long-article strategy in `references/script-usage.md`.

State the detected scope and date limits in one short line before searching.

### 3. Run the workflow

Follow the seven steps in `core/workflow.md`: segment, parse, search, evaluate support conservatively, export one reference-manager file, generate review artifacts when useful, and report with the HTML browser path first. Prefer `scripts/nature_citation.py` for the search/export when internet access is available; open `references/script-usage.md` for its full flag list and the long-article batch strategy.

Never present a paper as support merely because its title is related, and never cite a metadata-only candidate without checking the abstract or publisher page. Do not invent missing bibliographic fields.

### 4. Reach for references only when needed

The files under `references/` are deep references, not defaults. Open them on demand per the `references.on_demand` table in the manifest:

- running the script, full flags, long-article batching 鈫?`references/script-usage.md`.
- turning a claim into search queries and support grades 鈫?`references/search-strategy.md`.
- the exact Nature/CNS journal-family boundary 鈫?`references/journal-scope.md`.
- RIS / EndNote / Zotero RDF export details 鈫?`references/ris-endnote.md`.

## Why this split

- The static layer is versioned and reviewable; the core stays small for a normal short run.
- The dynamic layer keeps each invocation cheap: the script flag dump and long-article strategy load only when actually running a search.
- The router itself is short on purpose. Update fragments and references, not this file, when adding scope.
- This structure mirrors `nature-writing`, `nature-polishing`, `nature-reader`, `nature-paper2ppt`, and `nature-figure`.

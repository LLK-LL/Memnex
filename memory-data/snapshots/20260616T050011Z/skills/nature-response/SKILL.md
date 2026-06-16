---
name: nature-response
description: >-
  Draft, audit, or revise point-by-point reviewer response letters for Nature-family
  manuscript revisions. Use when the user provides reviewer comments, editor decision
  letters, revision notes, response drafts, or asks how to respond to major/minor
  revision requests, rebuttal letters, response to reviewers, peer-review reports,
  瀹＄鎰忚鍥炲, 閫愮偣鍥炲, 淇洖淇? 澶т慨鍥炲, 灏忎慨鍥炲, or 濡備綍鍥炲 reviewer.
  Also trigger on general peer-review response needs during academic writing/revision even without
  the word "Nature", such as replying to reviewers for any journal, writing a rebuttal/response
  letter, handling revision comments, and Chinese phrasings like 鍥炲瀹＄浜恒€佸绋垮洖澶嶃€佽繑淇€?
  淇敼绋垮洖澶嶃€佸啓rebuttal銆佸洖搴斿绋挎剰瑙併€佸簲瀵瑰绋?
version: 1.0.0
status: Beta
# REDACTED: sensitive-looking memory line
---

# Nature Reviewer Response 鈥?Router

This skill is split into two layers:

- A **static layer** under `static/` that holds versioned, reusable content fragments (the default stance and red lines, and the response workflow with output format).
- A **dynamic layer** (this file plus `manifest.yaml`) that loads the core every time and reaches for the deeper response references only when a step needs them.

Do not try to apply the response logic from memory or from this router. Always load fragments from disk as described below.

## Routing protocol

Follow these four steps every time the skill is invoked.

### 1. Load the manifest and the core layer

Read [manifest.yaml](manifest.yaml). Then read every file listed under `always_load`:

- `static/core/stance.md` 鈥?the editor-facing purpose, the default stance, the red lines, and the source hierarchy that apply to every response job.
- `static/core/workflow.md` 鈥?accepted inputs, the ten-step workflow, and the output package format.

### 2. No content axis 鈥?identify mode and language inline

Unlike nature-writing or nature-figure, nature-response has no fragment axis. Its variation is identified at runtime, not by loading different content bodies:

- **task mode** 鈥?`draft` / `audit` / `revise` / `triage-only` / `appeal-like`.
- **decision type** 鈥?minor revision, major revision, revise-and-resubmit, transfer after review, or unclear.
- **user language** 鈥?if the user writes Chinese, also produce the 涓枃鏍稿 block.

Use `references/intake-and-routing.md` to fix the task mode, minimum inputs, and readiness state before drafting. Route appeal-like cases separately; do not draft an appeal as the default path.

### 3. Run the workflow

# REDACTED: sensitive-looking memory line

# REDACTED: sensitive-looking memory line

### 4. Reach for references only when needed

# REDACTED: sensitive-looking memory line

## Why this split

- The static layer is versioned and reviewable; the core stays small for a normal response.
- The dynamic layer keeps each invocation cheap: the difficult-case, taxonomy, and QA depth load only when a step needs them.
- The router itself is short on purpose. Update fragments and references, not this file, when adding scope.
- This structure mirrors `nature-writing`, `nature-polishing`, `nature-reader`, `nature-paper2ppt`, `nature-figure`, and `nature-citation`.

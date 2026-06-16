# Strict Review

Use this file when the user wants a reviewer-style diagnosis, a pre-submission paper check, or a thesis submission recommendation.

This reference should preserve the intent of the original prompts while using Codex-native skill structure instead of XML-like prompt tags.

<a id="reviewer-review"></a>
## 1. Reviewer 椋庢牸瀹℃煡

Use when the user wants a paper, section, experiment package, or uploaded PDF reviewed from a strict reviewer perspective for a target venue.

### Core role

Act like a demanding but fair senior reviewer for top CS conferences.

### Core task

Read the paper closely and write a strict yet constructive review that distinguishes real strengths from fatal weaknesses and reflects the actual submission quality.

### Constraints

1. Review tone
   - Be objective, direct, and evidence-based.
   - Distinguish structural flaws from issues that can be fixed in revision.
   - Do not inflate harshness as a style choice if the paper is actually strong.
2. Review dimensions
   - community contribution
   - rigor and fairness of experiments
   - consistency between claimed contributions and demonstrated evidence
3. Writing rules
   - Use Chinese.
   - Prefer connected paragraphs over over-fragmented bulleting when explaining complex logic.
   - Do not add extra conversational filler.

### Required output

1. `Part 1 [The Review Report]`
   - `Summary`
   - `Strengths`
   - `Weaknesses (Critical)`
   - `Rating`
2. `Part 2 [Strategic Advice]`
   - `闂鏍规簮`
   - `鍙晳鎬у垽鏂璥
   - `琛屽姩鎸囧崡`

### Self-review checklist

1. Make each weakness concrete and operational rather than vague.
2. Do not confuse writing problems with method flaws.
3. Make sure the rating matches the paper's real contribution level instead of a fixed harsh prior.

<a id="strict-thesis-review"></a>
## 2. 涓ユ牸閫佸璇勮

Use when the user wants a thesis-style gatekeeping review rather than a casual reviewer note.

### Core role

Act like an anonymous internal thesis reviewer whose job is both to help revision and to guard the minimum quality bar for submission.

### Must-cover dimensions

1. 鏍煎紡瑙勮寖
2. 鍐欎綔閫昏緫
3. 宸ヤ綔閲?4. 鍒涙柊鐐规垨璐＄尞

### Required output structure

1. `涓€銆佹€讳綋璇勪环`
2. `浜屻€佸垎椤硅瘎璁剰瑙乣
3. `涓夈€佷富瑕侀棶棰樹笌淇敼寤鸿`
4. `鍥涖€佺患鍚堢粨璁篳

### Verdict

Choose exactly one:

- `鍚屾剰閫佸`
- `涓嶅悓鎰忛€佸`

### Constraints

1. Every judgment must have a concrete basis.
2. Suggestions must be actionable.
3. If the verdict is `涓嶅悓鎰忛€佸`, explain the blocking problems clearly and in enough detail to support the decision.

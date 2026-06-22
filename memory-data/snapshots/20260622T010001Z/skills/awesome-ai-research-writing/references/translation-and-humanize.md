# Translation And Humanize

Use this file when the user wants detailed sentence translation or specific de-AI rewriting behavior.

This reference should preserve the intent of the original prompts while using Codex-native skill structure instead of XML-like prompt tags.

<a id="long-sentence-translation"></a>
## 1. 鑻辫闀块毦鍙ョ炕璇?
Use when the user gives one sentence or one dense paragraph and wants grammar-aware translation rather than a quick paraphrase.

### Core role

Act like a bilingual translator who explains grammar, clause structure, collocations, and the final meaning in readable Chinese.

### Internal checklist

1. What type of text this is.
2. What the main clause is.
3. Which subordinate clauses and modifiers matter most.
4. Which keywords need context-sensitive explanation.

### Required output

1. `鍙ュ瓙鎷嗗垎`
   - 涓诲彞
   - 浠庡彞鎴栦慨楗版垚鍒?2. `鍏抽敭璇嶆眹涓庢惌閰峘
3. `璇硶瑕佺偣`
4. `鏁村彞缈昏瘧`

### Constraints

1. Keep the translation faithful to the original meaning.
2. Explain idioms or fixed collocations when needed.
3. Avoid translationese in the final Chinese sentence.

<a id="de-ai-latex-en"></a>
## 2. 鍘?AI 鍛筹紙LaTeX 鑻辨枃锛?
Use when English LaTeX paper text sounds generic or over-produced.

### Core role

Act like a senior CS academic editor who rewrites machine-like English into natural paper prose suitable for ACL-, NeurIPS-, or top-conference-level writing.

### Core task

Rewrite English LaTeX text so that it sounds like it was written by a careful human researcher rather than a generic text generator.

### Constraints

1. Lexical normalization
   - Prefer plain, precise academic words.
   - Avoid overused flashy words such as `leverage`, `delve into`, or other inflated vocabulary unless the technical context truly needs them.
   - Do not stack ornate wording just to sound advanced.
2. Structural naturalization
   - Convert list-like item content into connected prose.
   - Remove mechanical transitions such as `First and foremost` or `It is worth noting that` when they do not carry meaning.
   - Reduce em dashes and use cleaner clause structure instead.
3. Formatting rules
   - Do not add bold or italics.
   - Keep the LaTeX source clean and preserve commands, citations, labels, and formulas.
4. Modification threshold
   - If the text is already natural and publication-ready, keep it unchanged.
   - Do not rewrite merely to create visible edits.
5. Technical preservation
   - Escape newly added `%`, `_`, and `&`.
   - Keep formulas unchanged.

### Required output

1. `Part 1 [LaTeX]`
   - output the revised English LaTeX text
   - if the source is already strong, output it unchanged
2. `Part 2 [Translation]`
3. `Part 3 [Modification Log]`
   - if revised, explain which mechanical or inflated expressions were removed
   - if unchanged, output `[妫€娴嬮€氳繃] 鍘熸枃琛ㄨ揪鍦伴亾鑷劧锛屾棤鏄庢樉 AI 鍛筹紝寤鸿淇濈暀銆俙

### Self-review checklist

1. Check whether the revised text sounds natural rather than templated.
2. Revert any change made only for word substitution without readability gain.

<a id="de-ai-word-zh"></a>
## 3. 鍘?AI 鍛筹紙Word 涓枃锛?
Use when Chinese technical or academic prose sounds too templated and the user wants a more natural but still professional version.

### Core role

Act like a senior Chinese academic editor who can remove machine flavor and translationese while preserving the discipline-specific meaning.

### Core task

Rewrite Chinese text into natural, rigorous, Word-friendly academic prose that reads like it was written by a careful native-speaking researcher.

### Constraints

1. Vocabulary normalization
   - Replace empty rhetorical or emotionally inflated wording with concrete academic description.
   - Keep core technical terms accurate and unchanged when they are standard in the field.
2. Sentence and structure naturalization
   - Break long nested attributive chains into more natural Chinese structure.
   - Prefer active or impersonal Chinese constructions over heavy `琚玚-style phrasing when possible.
   - Avoid rigid `棣栧厛 / 鍏舵 / 鏈€鍚巂 or numbered list sequencing unless the logic truly depends on it.
3. Word-friendly output
   - Do not use Markdown symbols such as `**`, `*`, or headings.
   - Keep formulas or variable names only when they are necessary to preserve meaning.
4. Modification threshold
   - If the text is already natural, rigorous, and free of obvious AI flavor, keep it unchanged.
   - Do not rewrite just to look busy.

### Required output

1. `Part 1 [姝ｆ枃]`
   - output the revised plain text
   - if the source is already strong, output it unchanged
2. `Part 2 [淇敼鏃ュ織 / Modification Log]`
   - if revised, summarize the removed translationese or empty rhetorical phrasing
   - if unchanged, output `[妫€娴嬮€氳繃] 鍘熸枃琛ㄨ揪涓ヨ皑鑷劧锛屾棤鏄庢樉 AI 鐥曡抗锛屽缓璁繚鐣欍€俙

### Self-review checklist

1. Check whether the text reads like a rigorous domestic academic paper rather than translated machine prose.
2. Remove all Markdown symbols before finalizing.
3. Revert any change that only swaps words without improving clarity or naturalness.

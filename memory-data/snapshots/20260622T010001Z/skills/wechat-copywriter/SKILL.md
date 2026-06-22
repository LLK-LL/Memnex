---
name: wechat-copywriter
description: Write, rewrite, polish, structure, title, and package Chinese WeChat public account articles. Use when Codex is asked to create 寰俊鍏紬鍙锋枃绔?鍏紬鍙锋枃妗?鍏紬鍙锋帹鏂? generate article titles, design openings and endings, polish a draft for WeChat reading habits, plan article structure, produce layout suggestions, or adapt notes/audio/transcripts into publishable public-account copy.
---

# WeChat Copywriter

Use this skill to turn a topic, rough notes, draft, outline, or spoken idea into a WeChat public account article that is readable, sincere, and structurally clear.

## Intake

Before writing, identify or infer:

- Topic: what the article is about.
- Reader: who should care.
- Core viewpoint: the article's main claim or emotional center.
- Article type: viewpoint, practical guide, story, analysis, product/brand article, or event/news commentary.
- Target length: default to 1500-2500 Chinese characters unless the user specifies otherwise.
- Constraints: tone, brand voice, prohibited claims, required facts, CTA, links, or source material.

If key information is missing and the user expects a full article, ask at most 2 concise questions. If the request is clear enough, make reasonable assumptions and continue.

## Workflow

1. Understand the goal.
   - Clarify reader benefit: information, comfort, persuasion, action, or brand trust.
   - Distill one sentence as the article's core viewpoint.

2. Plan the structure.
   - Choose one structure:
     - 鎬诲垎鎬? best for clear viewpoints.
     - 闂-鍒嗘瀽-瑙ｅ喅: best for practical or business topics.
     - 鏁呬簨绾? best for emotional resonance and personal narrative.
     - 閫掕繘寮? best for deep analysis.
   - Plan 3-5 sections, each with one clear job.

3. Create title options.
   - Provide 3-6 titles unless the user asks for one.
   - Prefer honest curiosity, concrete value, contrast, or reader identity.
   - Avoid clickbait, fabricated urgency, exaggerated results, and anxiety selling.

4. Write or rewrite the article.
   - Open with a scene, question, story, counterintuitive point, or crisp sentence.
   - Keep paragraphs short; most paragraphs should be 1-4 lines.
   - Use specific examples and concrete details instead of abstract slogans.
   - Let emotion support the argument, not replace it.
   - End with a useful summary, memorable line, or natural CTA.

5. Optimize for WeChat reading.
   - Add section headings when they improve scanning.
   - Suggest where to bold key sentences.
   - Suggest image positions or visual moments when relevant.
   - Keep language natural and oral enough for mobile reading.

## Quality Rules

- Value first: every article should offer a real insight, useful method, or emotional recognition.
- Truthful title: titles must match the body.
- Clear logic: each section should advance the central argument.
- Measured emotion: no moral coercion, panic marketing, or fake certainty.
- Practical claims: do not invent data, quotes, cases, institutions, or outcomes.
- Platform fit: use short paragraphs, readable rhythm, and direct transitions.

## Output Modes

Match the user's request:

- Full article: output title options, recommended title, body, and layout suggestions.
- Outline only: output title options, central viewpoint, section plan, and opening/ending direction.
- Polish draft: preserve the user's meaning, improve rhythm and structure, then list major edits.
- Title only: output title options grouped by angle, with a short reason for each.
- Publish package: include title,鎽樿/瀵艰,姝ｆ枃,灏忔爣棰?缁撳熬CTA,鎺掔増寤鸿,閰嶅浘寤鸿.

## Default Full Article Format

When the user asks for a complete article, use this shape:

```markdown
## 鏍囬鏂规

涓绘帹鏍囬锛?澶囬€夋爣棰?1锛?澶囬€夋爣棰?2锛?
鏍囬寤鸿锛?
## 姝ｆ枃

[鏂囩珷姝ｆ枃]

## 鎺掔増寤鸿

- 閲嶇偣鍔犵矖锛?- 閰嶅浘寤鸿锛?- 缁撳熬寮曞锛?```

## Source Inspiration

This local skill was adapted from the public prompt "鍏紬鍙峰啓浣滀笓瀹? in `yaojingang/yao-open-prompts`, with unstable claims softened into practical writing guidance.

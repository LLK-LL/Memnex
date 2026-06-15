---
name: voice-command-cleaner
description: Clean dictated or speech-to-text Codex commands by removing filler words, verbal hesitations, redundant conjunctions, and off-topic fragments, then extract the user's main intent and execute the clarified instruction. Use when the user provides voice input, mentions dictation/语音输入/语音转文字/口述指令, asks to clean spoken text, or sends a command that looks like raw speech with fillers, repetitions, self-corrections, or loose oral phrasing.
---

# Voice Command Cleaner

## Purpose

Turn noisy voice-transcribed text into a clear Codex instruction. Preserve the user's actual intent, constraints, file paths, names, code terms, and requested output while removing words that only came from speaking style.

## Default Workflow

1. Identify the likely command hidden in the dictated text.
2. Remove filler words, verbal pauses, repeated starts, redundant connectives, and abandoned fragments.
3. Extract the main intent, target object, constraints, and requested action.
4. If the cleaned command is clear and safe, execute it directly.
5. If a missing detail blocks execution or could change the result materially, ask one focused clarification question.

Do not make the user manually rewrite a voice command. Interpret it for them, then act.

## Cleaning Rules

Remove content-free speech artifacts such as:

- Chinese fillers: 嗯, 呃, 啊, 额, 那个, 这个, 就是, 然后呢, 怎么说呢, 你知道吧, 对吧, 反正, 大概就是
- English fillers: um, uh, er, like, you know, I mean, basically, actually, sort of, kind of, so yeah
- Repeated starts: "帮我帮我...", "我想我想...", "please please..."
- Self-corrections: keep the final corrected meaning, remove the abandoned phrase
- Redundant connectors when they do not express order or causality

Preserve words that may be meaningful:

- File paths, commands, code identifiers, branch names, issue numbers, URLs, quoted text, and exact strings
- Required ordering words such as "first", "then", "after", "before", "先", "再", "然后" when they define a real sequence
- Tone or style requirements, such as "正式一点", "简洁", "不要改代码", "只解释"
- Safety or scope constraints, such as "不要提交", "只看一下", "不要联网", "仅修改这个文件"

When uncertain whether a phrase is filler or requirement, keep it.

## Intent Extraction

Internally rewrite the voice input into this brief before acting:

- Main intent: what the user wants Codex to accomplish
- Target: file, repo, tool, skill, issue, text, or artifact involved
- Constraints: scope limits, style, exclusions, deadlines, or verification requirements
- Action: explain, edit, create, search, run, test, summarize, commit, or ask a question

Use this brief to guide execution. Do not expose it unless it helps the user understand an ambiguous interpretation.

## Response Behavior

For normal Codex commands, respond as if the user had typed the cleaned command directly. A brief interpretation line is useful when the raw input was messy or when you are about to modify files.

When the user asks only to clean or summarize spoken text, return:

```text
清理后的指令：
[clean command]

主旨：
[one-sentence intent]

可执行动作：
[short action]
```

Keep the response compact. This skill exists to reduce friction from voice input, not to add another review layer.

## Examples

Raw voice input:

```text
嗯帮我就是看一下这个项目里面啊那个登录的地方为什么报错然后呢不要改太多
```

Cleaned command:

```text
检查这个项目的登录报错原因，尽量少改代码。
```

Raw voice input:

```text
so uh can you like add a test for the parser and actually don't touch the API just the parser test
```

Cleaned command:

```text
Add a parser test without changing the API.
```

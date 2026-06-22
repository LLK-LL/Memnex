---
name: voice-command-cleaner
description: Clean dictated or speech-to-text Codex commands by removing filler words, verbal hesitations, redundant conjunctions, and off-topic fragments, then extract the user's main intent and execute the clarified instruction. Use when the user provides voice input, mentions dictation/璇煶杈撳叆/璇煶杞枃瀛?鍙ｈ堪鎸囦护, asks to clean spoken text, or sends a command that looks like raw speech with fillers, repetitions, self-corrections, or loose oral phrasing.
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

- Chinese fillers: 鍡? 鍛? 鍟? 棰? 閭ｄ釜, 杩欎釜, 灏辨槸, 鐒跺悗鍛? 鎬庝箞璇村憿, 浣犵煡閬撳惂, 瀵瑰惂, 鍙嶆, 澶ф灏辨槸
- English fillers: um, uh, er, like, you know, I mean, basically, actually, sort of, kind of, so yeah
- Repeated starts: "甯垜甯垜...", "鎴戞兂鎴戞兂...", "please please..."
- Self-corrections: keep the final corrected meaning, remove the abandoned phrase
- Redundant connectors when they do not express order or causality

Preserve words that may be meaningful:

- File paths, commands, code identifiers, branch names, issue numbers, URLs, quoted text, and exact strings
- Required ordering words such as "first", "then", "after", "before", "鍏?, "鍐?, "鐒跺悗" when they define a real sequence
- Tone or style requirements, such as "姝ｅ紡涓€鐐?, "绠€娲?, "涓嶈鏀逛唬鐮?, "鍙В閲?
- Safety or scope constraints, such as "涓嶈鎻愪氦", "鍙湅涓€涓?, "涓嶈鑱旂綉", "浠呬慨鏀硅繖涓枃浠?

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
娓呯悊鍚庣殑鎸囦护锛?[clean command]

涓绘棬锛?[one-sentence intent]

鍙墽琛屽姩浣滐細
[short action]
```

Keep the response compact. This skill exists to reduce friction from voice input, not to add another review layer.

## Examples

Raw voice input:

```text
鍡府鎴戝氨鏄湅涓€涓嬭繖涓」鐩噷闈㈠晩閭ｄ釜鐧诲綍鐨勫湴鏂逛负浠€涔堟姤閿欑劧鍚庡憿涓嶈鏀瑰お澶?```

Cleaned command:

```text
妫€鏌ヨ繖涓」鐩殑鐧诲綍鎶ラ敊鍘熷洜锛屽敖閲忓皯鏀逛唬鐮併€?```

Raw voice input:

```text
so uh can you like add a test for the parser and actually don't touch the API just the parser test
```

Cleaned command:

```text
Add a parser test without changing the API.
```

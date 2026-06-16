---
description: Scan text for AI patterns without modifying
argument-hint: [text to analyze]
---

# Check AI Patterns

You are executing the `/check-ai-patterns` command.

@../SKILL.md

Analyze the provided text for AI-generated patterns WITHOUT making changes.

## Input

If `$ARGUMENTS` is provided, analyze that text.
Otherwise, ask the user to provide the text to scan.

## Process

Scan the text for all patterns listed in the skill and report findings:

1. **Punctuation Tells** 鈥?em dashes, excessive colons, semicolons in casual writing
2. **Filler Phrases** 鈥?"It's worth noting", "Let's dive in", etc.
3. **Buzzwords** 鈥?delve, leverage, robust, seamless, etc.
4. **Overwrought Metaphors** 鈥?tapestry, symphony, beacon, etc.
5. **Weak Intensifiers** 鈥?very, really, crucial, paramount, etc.
6. **Hedging/Padding** 鈥?"One could argue", "It could be said", etc.
7. **Mechanical Transitions** 鈥?Furthermore, Moreover, In conclusion, etc.
8. **Structural Tells** 鈥?repetitive patterns, mirrored phrasing, etc.
9. **Opening Line Cliches** 鈥?"In the world of", "When it comes to", etc.

## Output Format

```
AI Pattern Analysis
-------------------
Patterns Found: [count]

Category Breakdown:
- Punctuation: [count] instances
- Filler phrases: [count] instances
- Buzzwords: [list found]
- ...

Specific Instances:
1. "[exact phrase]" 鈥?[category] 鈥?Suggestion: [replacement]
2. ...

Overall Assessment: [Low/Medium/High] AI detectability
```

---
description: Transform AI-sounding text into natural human prose (US spelling)
argument-hint: [text or leave empty for clipboard/selection]
---

# Humanize Text

You are executing the `/humanize-text` command (US spelling variant).

@../SKILL.md

This is an alias for `/humanise-text`. Apply the humanisation rules above to transform the provided text.

## Input

If `$ARGUMENTS` is provided, humanize that text.
Otherwise, ask the user to provide the text they want humanized.

## Process

1. Identify all AI-sounding patterns in the text
2. Apply replacements from the pattern tables
3. Remove filler phrases entirely
4. Restructure any mechanical sentence patterns
5. Read the result aloud mentally; revise if it sounds robotic
6. Present the humanized version

## Output Format

Provide the humanized text, then briefly list the changes made.

---
description: Transform AI-sounding text into natural human prose
argument-hint: [text or leave empty for clipboard/selection]
---

# Humanise Text

You are executing the `/humanise-text` command.

@../SKILL.md

Apply the humanisation rules above to transform the provided text.

## Input

If `$ARGUMENTS` is provided, humanise that text.
Otherwise, ask the user to provide the text they want humanised.

## Process

1. Identify all AI-sounding patterns in the text
2. Apply replacements from the pattern tables
3. Remove filler phrases entirely
4. Restructure any mechanical sentence patterns
5. Read the result aloud mentally; revise if it sounds robotic
6. Present the humanised version

## Output Format

Provide the humanised text, then briefly list the changes made (e.g., "Removed 3 filler phrases, replaced 'leverage' with 'use', varied sentence structure").

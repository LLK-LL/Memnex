# Task: Upgrade the Skill

When the user asks to upgrade this skill, fetch the latest version from GitHub.

## Step 1 — Locate the skill directory

The skill is a git repository. Try the standard installation paths in this order:

| Platform | Global path | Project-level path |
|---|---|---|
| Claude Code | `~/.claude/skills/vibe-paper-writing` | `.claude/skills/vibe-paper-writing` |
| Cursor | `~/.cursor/skills/vibe-paper-writing` | `.cursor/skills/vibe-paper-writing` |
| Codex | `~/.agents/skills/vibe-paper-writing` | `.agents/skills/vibe-paper-writing` |
| GitHub Copilot | `~/.copilot/skills/vibe-paper-writing` | `.github/skills/vibe-paper-writing` |

Check which path exists:

```bash
ls ~/.claude/skills/vibe-paper-writing 2>/dev/null \
  || ls ~/.cursor/skills/vibe-paper-writing 2>/dev/null \
  || ls ~/.agents/skills/vibe-paper-writing 2>/dev/null \
  || echo "not found"
```

If none of the standard paths exist, ask the user where the skill is installed before proceeding.

## Step 2 — Pull the latest version

```bash
git -C <skill-directory> pull
```

For example, for Claude Code:

```bash
git -C ~/.claude/skills/vibe-paper-writing pull
```

## Step 3 — Report the result

After the pull completes, report:

- Whether any files were updated (show the git output).
- The current HEAD commit hash and date, so the user knows which version is now active:

```bash
git -C <skill-directory> log -1 --format="%H %ci %s"
```

If the pull fails (e.g., network error, local modifications), show the error and suggest the user run the command manually.

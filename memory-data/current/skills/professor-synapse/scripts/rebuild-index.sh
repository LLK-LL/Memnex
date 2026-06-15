#!/bin/bash
# Rebuild INDEX.md from agent frontmatter

show_help() {
    cat << 'EOF'
USAGE
  bash scripts/rebuild-index.sh [options]

DESCRIPTION
  Regenerates agents/INDEX.md from YAML frontmatter in each agent file.
  Also ensures every agent file has a Learned Patterns section and reminder.

OPTIONS
  -h, --help       Show this help message

EXAMPLES
  bash scripts/rebuild-index.sh
  bash scripts/rebuild-index.sh --help

NOTES
  Run from the skill root directory (professor-synapse/).
  After running, complete the packaging workflow to persist changes.
EOF
}

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_help
    exit 0
fi

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
AGENTS_DIR="$PROJECT_ROOT/agents"
INDEX_FILE="$AGENTS_DIR/INDEX.md"

# Define the learned patterns section template
LEARNED_PATTERNS_SECTION="## Learned Patterns

### Effective Patterns
<!-- Domain-specific patterns that work well for this agent. Add entries as you learn. -->

### Anti-Patterns
<!-- Domain-specific mistakes to avoid for this agent. Add entries as you learn. -->"

# Define the reminder text to append to each agent
REMINDER_TEXT="---

**REMEMBER**: You learn over time! Update SKILL.md's **Global Learned Patterns** for cross-cutting insights and this agent's **Learned Patterns** section above for domain-specific insights. Always complete the packaging workflow afterward."

# Start the index file
cat > "$INDEX_FILE" << 'HEADER'
# Agent Index

Auto-generated from agent frontmatter. Run `bash scripts/rebuild-index.sh` to refresh.

## Available Agents

| Agent | Emoji | Description | Triggers |
|-------|-------|-------------|----------|
HEADER

# Process each agent file (except INDEX.md)
for file in "$AGENTS_DIR"/*.md; do
    filename=$(basename "$file")

    # Skip INDEX.md itself
    if [ "$filename" = "INDEX.md" ]; then
        continue
    fi

    # Extract frontmatter fields using grep/sed
    name=$(sed -n '/^---$/,/^---$/p' "$file" | grep "^name:" | sed 's/name: *//')
    emoji=$(sed -n '/^---$/,/^---$/p' "$file" | grep "^emoji:" | sed 's/emoji: *//')
    description=$(sed -n '/^---$/,/^---$/p' "$file" | grep "^description:" | sed 's/description: *//')
    triggers=$(sed -n '/^---$/,/^---$/p' "$file" | grep "^triggers:" | sed 's/triggers: *//')

    # Add row to table
    if [ -n "$name" ]; then
        echo "| [$name]($filename) | $emoji | $description | $triggers |" >> "$INDEX_FILE"
    fi

    # Append Learned Patterns section if not already present
    if ! grep -q "^## Learned Patterns" "$file"; then
        # Remove old-style reminder if present (we'll re-add the updated one below)
        if grep -q "One of your superpowers is that you learn over time" "$file"; then
            # Remove the old reminder block (--- + blank line + REMEMBER line)
            sed -i '' '/^---$/,/One of your superpowers is that you learn over time/{
                /One of your superpowers is that you learn over time/d
            }' "$file"
            # Clean up the leftover --- and blank lines at the end
            sed -i '' -e :a -e '/^\n*$/{$d;N;ba' -e '}' "$file"
        fi
        echo "" >> "$file"
        echo "$LEARNED_PATTERNS_SECTION" >> "$file"
        echo "" >> "$file"
        echo "$REMINDER_TEXT" >> "$file"
        echo "  Added Learned Patterns section to $filename"
    fi

    # Ensure reminder is present (updated version)
    if ! grep -q "Always complete the packaging workflow afterward" "$file"; then
        # Remove old-style reminder if present
        if grep -q "One of your superpowers is that you learn over time" "$file"; then
            sed -i '' '/One of your superpowers is that you learn over time/d' "$file"
            # Clean up trailing blank lines
            sed -i '' -e :a -e '/^\n*$/{$d;N;ba' -e '}' "$file"
        fi
        echo "" >> "$file"
        echo "$REMINDER_TEXT" >> "$file"
    fi
done

echo "" >> "$INDEX_FILE"
echo "_Last updated: $(date '+%Y-%m-%d %H:%M')_" >> "$INDEX_FILE"

# Count entries (subtract header row)
ENTRY_COUNT=$(($(grep -c '^|' "$INDEX_FILE") - 1))

echo "✅ INDEX.md rebuilt with $ENTRY_COUNT agent(s)"
echo "✅ Learned Patterns section ensured on all agents"

echo ""
echo "📋 NEXT STEPS to complete skill update:"
echo "  1. Package skill:  python3 /mnt/skills/examples/skill-creator/scripts/package_skill.py /mnt/skills/user/professor-synapse /home/claude/"
echo "  2. Copy to outputs: cp /home/claude/professor-synapse.skill /mnt/user-data/outputs/"
echo "  3. Present file:    present_files → professor-synapse.skill"
echo ""
echo "⚠️  The user must click 'Copy to your skills' to complete the update!"

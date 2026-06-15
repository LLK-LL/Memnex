# Agent Creation Template

Use this template when NO existing agent in `agents/` matches the user's need.

## Required Frontmatter

Every agent file MUST start with YAML frontmatter for auto-indexing:

```yaml
---
name: [agent-name]
emoji: [emoji]
description: [One-line description of what this agent does]
triggers: [comma-separated keywords that should summon this agent]
---
```

**Naming rules:** `name` must use only lowercase letters, numbers, and hyphens (e.g., `python-async-expert`).

**Example:**
```yaml
---
name: python-async-expert
emoji: 🐍
description: Expert in Python async/await patterns, concurrency, and asyncio
triggers: python, async, await, asyncio, concurrency, coroutines
---
```

## Template Structure

All agents follow CONTEXT/MISSION/INSTRUCTIONS/GUIDELINES + optional FORMAT:

```markdown
# [emoji]: [Title] Expert

## CONTEXT
[User's situation, background, constraints - gathered from your questions]

## MISSION
[Specific goal + completion criteria]

## INSTRUCTIONS
1. [Reasoned step 1]
2. [Reasoned step 2]
3. [Reasoned step 3]

## GUIDELINES
- [Domain-specific best practice]
- [Communication style]
- [Quality standard]
- Express uncertainty when present - "I'm not certain about X"
- Ask clarifying questions rather than assume

## FORMAT (optional)
Include ONLY if agent produces specific deliverables with required structure.
Examples:
- Report with specific headings
- Analysis with required tables
- Code with specific file structure
- Document following a template

If no specific output format needed, omit this section.

## Learned Patterns

### Effective Patterns
<!-- Domain-specific patterns that work well for this agent. Add entries as you learn. -->

### Anti-Patterns
<!-- Domain-specific mistakes to avoid for this agent. Add entries as you learn. -->
```

## Using Research Output

When creating a new agent, first summon 🔎 Domain Researcher. Use their structured output to fill in:
- **CONTEXT**: Informed by "Common User Needs" research
- **INSTRUCTIONS**: Based on "Key Frameworks/Methodologies"
- **GUIDELINES**: Incorporate "Anti-Patterns to Avoid" and domain vocabulary
- **Emoji/Title**: Use "Recommended Agent Configuration" suggestions

## Scripts (Optional)

If this agent needs to run the same operation repeatedly (rebuild a cache, fetch external data, transform files), create a script for it rather than embedding the steps in the agent's instructions.

**When a script would benefit this agent, follow `references/scripts-protocol.md`.**

After creating the script, add a **Scripts** section to the agent file:

```markdown
## Scripts

| Script | Purpose | Invoke |
|--------|---------|--------|
| `scripts/[name].sh` | What it does | `bash scripts/[name].sh --help` |
```

The agent can then invoke `bash scripts/[name].sh --help` at runtime to get usage instructions without needing to read the source.

## After Creation - MANDATORY

> **⚠️ DO NOT SKIP ANY STEP BELOW. If you do, the agent will NOT be available to the user. Changes are LOST without the full packaging workflow.**

**Claude Desktop cannot edit skills in place.** After creating or editing ANY agent, you MUST complete ALL of these steps:

### Step 1: Save the Agent
```
create_file → /mnt/skills/user/professor-synapse/agents/[domain]-[specialty].md
```

Example: An ML expert for business users -> `agents/ml-business-translator.md`

### Step 2: Rebuild the Index
```bash
cd /mnt/skills/user/professor-synapse && bash scripts/rebuild-index.sh
```

### Step 3: Package the Skill
```bash
python3 /mnt/skills/examples/skill-creator/scripts/package_skill.py /mnt/skills/user/professor-synapse /home/claude/
```

### Step 4: Copy to Outputs
```bash
cp /home/claude/professor-synapse.skill /mnt/user-data/outputs/
```

### Step 5: Present to User
```
present_files → professor-synapse.skill
```

The user will then see "Copy to your skills" button to install the updated skill.

**⚠️ If you skip any step, the agent will NOT be available when the user invokes Professor Synapse. The changes are LOST.**

## Synapse_CoR Declaration

When summoning (new or existing), announce with:

```
"[emoji]: I am an expert in **[role]** specializing in **[domain]**.

I understand you need to **[context]** and want to achieve **[goal]**.

I will use **[techniques]** and **[frameworks]** to help.

Let's progress:
1. [Step 1]
2. [Step 2]
3. [Step 3]

Ready to begin?"
```

## How to Fill In Learned Patterns

When adding entries to an agent's Learned Patterns section (or to SKILL.md's Global Learned Patterns), use these formats:

### Adding a Pattern (what worked)

```
#### [Pattern Name]
**Triggers**: [keywords, user level, task type]
**Effective Config**:
- Emoji: [emoji]
- Title: [title]
- Techniques: [what worked]
- Style: [communication approach]

**What Worked**:
- [Specific effective approach]
- [Question that clarified well]
```

### Adding an Anti-Pattern (what to avoid)

```
#### [Anti-Pattern Name]
**Triggers**: [when this mistake tends to happen]
**The Mistake**: [what went wrong]
**Why It Failed**: [root cause]
**Instead Do**: [correct approach]
```

**Where does this pattern belong?**
- **SKILL.md (Global Learned Patterns)**: Applies across multiple agents or to Professor Synapse's general behavior
- **Agent file (Learned Patterns section)**: Applies only to one agent's domain

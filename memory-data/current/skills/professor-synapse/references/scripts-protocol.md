# Scripts Protocol

Scripts are standalone, self-documenting CLI tools. Agents don't need to read source code — they run `script --help` to learn usage, then invoke as needed.

## Philosophy

- **Code lives in `scripts/`** — separate from documentation
- **CLI-first design** — every script explains itself via `--help`
- **Agents reference, not embed** — agent files point to scripts; they don't duplicate logic

## When to Create a Script

Create a script when an agent needs to perform the same operation repeatedly:
- Rebuilding indexes or caches
- Fetching or syncing external data
- Packaging or transforming files
- Any multi-step operation worth automating

## Required Interface

Every script MUST support a `--help` / `-h` flag that prints:

1. **What it does** — one-line description
2. **Usage** — syntax with argument placeholders
3. **Arguments** — each argument described
4. **Examples** — at least two concrete examples
5. **Dependencies** — any required tools

### Shell Script Template

```bash
#!/bin/bash
# [one-line description]

show_help() {
    cat << 'EOF'
USAGE
  script-name.sh [options] <required-arg> [optional-arg]

DESCRIPTION
  What the script does in 1-2 sentences.

ARGUMENTS
  <required-arg>   Description of required argument
  [optional-arg]   Description of optional argument (default: value)

OPTIONS
  -h, --help       Show this help message

EXAMPLES
  script-name.sh foo
  script-name.sh foo bar

DEPENDENCIES
  tool1, tool2
EOF
}

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_help
    exit 0
fi
```

### Python Script Template

```python
#!/usr/bin/env python3
"""one-line description"""

import argparse

def main():
    parser = argparse.ArgumentParser(description="What the script does.")
    parser.add_argument("required_arg", help="Description")
    parser.add_argument("optional_arg", nargs="?", default="value", help="Description")
    args = parser.parse_args()
    # ...

if __name__ == "__main__":
    main()
```

Python's `argparse` generates `--help` automatically — no extra work needed.

## How Agents Reference Scripts

In an agent's definition, add a **Scripts** section listing scripts the agent may need:

```markdown
## Scripts

| Script | Purpose | Invoke |
|--------|---------|--------|
| `scripts/rebuild-index.sh` | Regenerate agent index | `bash scripts/rebuild-index.sh --help` |
```

Agents should run `--help` first if uncertain about arguments or options.

## Existing Scripts

| Script | Purpose | Help |
|--------|---------|------|
| `scripts/rebuild-index.sh` | Rebuild `agents/INDEX.md` from agent frontmatter | `bash scripts/rebuild-index.sh --help` |
| `scripts/fetch-github-file.sh` | Fetch files from GitHub (works around blocked raw/API domains) | `bash scripts/fetch-github-file.sh --help` |
| `scripts/github_blob_parser.py` | Parse GitHub HTML blobs to Markdown | Internal helper — called by `fetch-github-file.sh` |

## Adding a New Script

1. Create `scripts/[name].sh` (or `.py`)
2. Implement `--help` following the template above
3. Add a row to the **Existing Scripts** table in this file
4. In any agent that uses the script, add a **Scripts** section pointing to it

No need to update SKILL.md — this protocol is the catalog.

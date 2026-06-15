#!/bin/bash
# Fetches raw file content from GitHub by parsing the blob page HTML

show_help() {
    cat << 'EOF'
USAGE
  fetch-github-file.sh <github-blob-url> [output-file]
  fetch-github-file.sh <owner/repo> <branch> <path/to/file> [output-file]

DESCRIPTION
  Fetches raw file content from GitHub by parsing the blob page HTML.
  Works around blocked raw.githubusercontent.com and api.github.com domains.

ARGUMENTS
  <github-blob-url>          Full GitHub blob URL
  <owner/repo>               Repository in owner/repo format
  <branch>                   Branch name (e.g. main)
  <path/to/file>             File path within the repository
  [output-file]              Optional: save output to this file (default: stdout)

OPTIONS
  -h, --help                 Show this help message

EXAMPLES
  fetch-github-file.sh "https://github.com/ProfSynapse/Professor-Synapse/blob/main/professor-synapse/SKILL.md"
  fetch-github-file.sh ProfSynapse/Professor-Synapse main professor-synapse/SKILL.md
  fetch-github-file.sh ProfSynapse/Professor-Synapse main professor-synapse/SKILL.md /tmp/output.md

DEPENDENCIES
  python3, html2text (auto-installed if missing)
  github_blob_parser.py (must be in the same directory as this script)
EOF
}

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_help
    exit 0
fi

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARSER_SCRIPT="$SCRIPT_DIR/github_blob_parser.py"

# Check for parser script
if [[ ! -f "$PARSER_SCRIPT" ]]; then
    echo "Error: github_blob_parser.py not found in $SCRIPT_DIR" >&2
    exit 1
fi

# Check for html2text
if ! python3 -c "import html2text" 2>/dev/null; then
    echo "Installing html2text..." >&2
    pip install html2text --break-system-packages -q
fi

# Parse arguments
if [[ "$1" == https://github.com/* ]]; then
    URL="$1"
    OUTPUT="$2"
else
    REPO="$1"
    BRANCH="$2"
    FILEPATH="$3"
    OUTPUT="$4"
    
    if [[ -z "$REPO" || -z "$BRANCH" || -z "$FILEPATH" ]]; then
        echo "Usage: $0 <github-blob-url> [output-file]" >&2
        echo "   or: $0 owner/repo branch path/to/file [output-file]" >&2
        exit 1
    fi
    
    URL="https://github.com/${REPO}/blob/${BRANCH}/${FILEPATH}"
fi

# Fetch and parse
CONTENT=$(curl -sL "$URL" | python3 "$PARSER_SCRIPT")

# Output
if [[ -n "$OUTPUT" ]]; then
    echo "$CONTENT" > "$OUTPUT"
    echo "Saved to $OUTPUT" >&2
else
    echo "$CONTENT"
fi
#!/usr/bin/env bash
# version: 1.0.0
#
# REDACTED: sensitive-looking memory line
#
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# The plugin loader injects that context into the LLM's first turn so the
# REDACTED: sensitive-looking memory line
# slash commands and plugin agents are available.
#
# REDACTED: sensitive-looking memory line
# This script is safe to run from any context; it does not invoke codex,
# does not write outside its own stdout, and produces no side effects on
# the working tree.
#
# Exit codes:
#   0    Always 鈥?even on parse failure, fall back to the long-form announce.
# REDACTED: sensitive-looking memory line

set -euo pipefail

# ---------------------------------------------------------------------------
# This script intentionally avoids Bash 4+ features (no associative arrays,
# no indirect expansion via `${!var}`, no `<<<` here-strings on the hot
# path). It runs cleanly on macOS stock /bin/bash 3.2 so plugin users
# REDACTED: sensitive-looking memory line
# `run_codex_audit.sh` does need Bash 4+ 鈥?that wrapper guards itself.
# ---------------------------------------------------------------------------
# REDACTED: sensitive-looking memory line
# startup / resume / clear / compact) without taking a hard dependency on
# jq 鈥?many ARS users won't have it installed and we want this hook to
# work out of the box.
# ---------------------------------------------------------------------------
INPUT=""
if [[ ! -t 0 ]]; then
  INPUT=$(cat)
fi

SOURCE="startup"
if [[ -n "${INPUT}" ]]; then
  # Match `"source": "<value>"` with optional whitespace; tolerate single-line
  # or multi-line JSON. Falls through to default `startup` on any parse miss.
  if [[ "${INPUT}" =~ \"source\"[[:space:]]*:[[:space:]]*\"([a-z]+)\" ]]; then
    SOURCE="${BASH_REMATCH[1]}"
  fi
fi

# ---------------------------------------------------------------------------
# For `compact` and `resume` we keep the announce minimal: the LLM already
# has prior ARS context from the resumed transcript or carried-over summary,
# and re-injecting the full slash-command list every resume burns context.
# `startup` and `clear` get the full version.
# ---------------------------------------------------------------------------
case "${SOURCE}" in
  compact|resume)
    ANNOUNCE="ARS v3.7.0 plugin still loaded after ${SOURCE}. Slash commands: /ars-full /ars-plan /ars-outline /ars-revision /ars-revision-coach /ars-abstract /ars-lit-review /ars-format-convert /ars-citation-check /ars-disclosure. Plugin agents: synthesis_agent, research_architect_agent, report_compiler_agent."
    ;;
  startup|clear|*)
    ANNOUNCE="ARS v3.7.0 (academic-research-skills) plugin loaded.

Slash commands (10) 鈥?model routing pinned in frontmatter:
  /ars-full              opus    Full pipeline (research 鈫?write 鈫?review 鈫?revise 鈫?finalize)
  /ars-revision-coach    opus    Parse reviewer comments 鈫?Revision Roadmap + Response Letter skeleton
  /ars-plan              sonnet  Socratic chapter-by-chapter planning
  /ars-outline           sonnet  Detailed outline + evidence map (no full draft)
  /ars-revision          sonnet  Revised draft + R&R responses
  /ars-abstract          sonnet  Bilingual abstract + keywords
  /ars-lit-review        sonnet  Annotated bibliography in paper format
  /ars-format-convert    sonnet  Convert paper between LaTeX / DOCX / PDF / Markdown
  /ars-citation-check    sonnet  Citation error report
  /ars-disclosure        sonnet  Venue-specific AI-usage disclosure statement

Plugin agents (3, v3.6.7-hardened, model: inherit) 鈥?dispatched by ARS pipeline:
  synthesis_agent             Cross-source integration, contradiction resolution, gap analysis
  research_architect_agent    Methodology blueprint (paradigm, method, data strategy)
  report_compiler_agent       APA 7.0 report drafting (Phase 4 + Phase 6)

Other ARS agents (bibliography_agent, literature_strategist_agent, field_analyst_agent, etc.) remain in-skill prompt templates loaded via SKILL.md, not plugin agents.

# REDACTED: sensitive-looking memory line
    ;;
esac

# ---------------------------------------------------------------------------
# Emit the JSON. We assemble it with a here-doc and a sentinel substitution
# rather than printf/jq to keep the output stable across Bash patch versions.
# additionalContext must be a JSON string 鈥?escape backslashes, double quotes,
# newlines.
# ---------------------------------------------------------------------------
escape_json() {
  local raw="$1"
  raw="${raw//\\/\\\\}"
  raw="${raw//\"/\\\"}"
  raw="${raw//$'\n'/\\n}"
  printf '%s' "${raw}"
}

ESCAPED=$(escape_json "${ANNOUNCE}")

cat <<JSON
# REDACTED: sensitive-looking memory line
JSON

exit 0

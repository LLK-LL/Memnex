# ===========================================
# PostToolUse Hook (PowerShell) — v7.0 learn_error trigger for Bash
#
# Port of ~/.claude/hooks/on-bash-error.sh for Windows.
# Fires on non-zero bash exit with a distinguishable root cause.
# Emits a reminder to call learn_error(...). N>=3 similar patterns
# auto-consolidate into a rule on the MCP side.
#
# Hook: PostToolUse (matcher: "Bash")
# ===========================================

$ErrorActionPreference = "SilentlyContinue"

# Parse stdin JSON (Claude Code hook payload).
$stdinRaw = [Console]::In.ReadToEnd()
if (-not $stdinRaw) { exit 0 }

try {
    $data = $stdinRaw | ConvertFrom-Json
} catch {
    exit 0
}

if ($data.tool_name -ne "Bash") { exit 0 }

$exitCode = $null
$stderr = $null
$commandStr = $null

if ($data.tool_response) {
    $exitCode = $data.tool_response.exit_code
    $stderr = $data.tool_response.stderr
}
if ($data.tool_input) {
    $commandStr = $data.tool_input.command
}

# Empty or zero -> no error, skip
if ($null -eq $exitCode -or $exitCode -eq 0) { exit 0 }
if (-not $stderr) { exit 0 }

# Truncate for display
if ($commandStr -and $commandStr.Length -gt 200) {
    $commandStr = $commandStr.Substring(0, 200)
}
if ($stderr.Length -gt 500) {
    $stderr = $stderr.Substring(0, 500)
}

# Skip noise: user aborts, interactive prompts, benign warnings
$noisePatterns = @(
    "permission denied by user",
    "User denied",
    "SIGINT"
)
foreach ($pat in $noisePatterns) {
    if ($stderr -like "*$pat*") { exit 0 }
}

$reminder = @"
<system-reminder>
Memory self_error_log trigger: bash exited $exitCode. If the root cause is
reproducible and fixable, call:
  self_error_log(
      description="Bash failed: <short stderr>; command: $commandStr",
      category="code_error|config_error|api_error|timeout|wrong_assumption|missing_context",
      severity="medium",
      fix="<what resolves it, or empty if unresolved>",
      project="<project>"
  )
Skip if this is user-aborted, interactive, or benign. Do not re-log if you
just fixed it and the root cause is identical to an earlier call this turn.
</system-reminder>
"@

# TODO: when a PowerShell-native learn_error CLI client is available, wire
# the actual call here in addition to the reminder (mirror the eventual
# bash equivalent). For now the reminder is sufficient - agent picks it up.

Write-Output $reminder
exit 0

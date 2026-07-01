# ===========================================
# PostToolUse Hook (PowerShell) - self_error_log trigger for Bash
#
# Fires on non-zero bash exit with a distinguishable root cause.
# Logs a lightweight error row directly to the local memory DB, then emits a
# reminder to call self_error_log(...) when the agent can add a better fix.
#
# Hook: PostToolUse (matcher: "Bash")
# ===========================================

$ErrorActionPreference = "SilentlyContinue"

$InstallDir = if ($env:CLAUDE_MEMORY_INSTALL_DIR) {
    $env:CLAUDE_MEMORY_INSTALL_DIR
} else {
    Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
}
$MemoryDir = if ($env:TAM_MEMORY_DIR) {
    $env:TAM_MEMORY_DIR
} elseif ($env:CLAUDE_MEMORY_DIR) {
    $env:CLAUDE_MEMORY_DIR
} else {
    Join-Path $env:USERPROFILE ".tam"
}
$HookPython = if ($env:HOOK_PYTHON) {
    $env:HOOK_PYTHON
} else {
    [System.IO.Path]::Combine($InstallDir, ".venv", "Scripts", "python.exe")
}
if (-not (Test-Path $HookPython)) {
    $HookPython = (Get-Command python -ErrorAction SilentlyContinue).Source
    if (-not $HookPython) {
        $HookPython = (Get-Command python3 -ErrorAction SilentlyContinue).Source
    }
}

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

# Empty or zero -> no error, skip.
if ($null -eq $exitCode -or $exitCode -eq 0) { exit 0 }
if (-not $stderr) { exit 0 }

# Truncate for display and DB storage.
if ($commandStr -and $commandStr.Length -gt 200) {
    $commandStr = $commandStr.Substring(0, 200)
}
if ($stderr.Length -gt 500) {
    $stderr = $stderr.Substring(0, 500)
}

# Skip noise: user aborts, interactive prompts, benign warnings.
$noisePatterns = @(
    "permission denied by user",
    "User denied",
    "SIGINT"
)
foreach ($pat in $noisePatterns) {
    if ($stderr -like "*$pat*") { exit 0 }
}

$Project = if ($data.cwd) { Split-Path -Leaf $data.cwd } else { Split-Path -Leaf (Get-Location) }
if (-not $Project) { $Project = "general" }
$Description = "Bash failed ($exitCode): $stderr"
$Context = "command: $commandStr"

if ($HookPython) {
    try {
        $AutoImprove = [System.IO.Path]::Combine($InstallDir, "src", "auto_self_improve.py")
        if (Test-Path -LiteralPath $AutoImprove) {
            $env:TAM_MEMORY_DIR = $MemoryDir
            $env:CLAUDE_MEMORY_DIR = $MemoryDir
            $logArgs = @(
                $AutoImprove, "error",
                "--description", $Description,
                "--category", "code_error",
                "--severity", "medium",
                "--context", $Context,
                "--project", $Project
            )
            & $HookPython @logArgs 2>$null | Out-Null
        }
    } catch {
        # Never fail the user session.
    }
}

$reminder = @"
<system-reminder>
Memory self_error_log trigger: bash exited $exitCode. A lightweight error row
was auto-logged to the local memory DB. If the root cause is reproducible and
fixable, also call:
  self_error_log(
      description="Bash failed: <short stderr>; command: $commandStr",
      category="code_error|config_error|api_error|timeout|wrong_assumption|missing_context",
      severity="medium",
      fix="<what resolves it, or empty if unresolved>",
      project="$Project"
  )
Skip the extra call if this is user-aborted, interactive, benign, or already
captured with the same root cause this turn.
</system-reminder>
"@

Write-Output $reminder
exit 0

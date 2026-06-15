param(
    [string]$TaskName = "AI-brain weekly memory sync",
    [string]$RepositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [string]$At = "09:00"
)

$ErrorActionPreference = "Stop"

$syncScript = Join-Path $RepositoryRoot "memory-system\scripts\sync-memory-library.ps1"
if (-not (Test-Path -LiteralPath $syncScript)) {
    throw "Sync script not found: $syncScript"
}

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$syncScript`" -RepositoryRoot `"$RepositoryRoot`""

$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At $At
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel LeastPrivilege
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Principal $principal `
    -Settings $settings `
    -Description "Weekly sync of AI-brain memory, rules, skills, and preferences to GitHub." `
    -Force | Out-Null

Write-Host "Installed scheduled task '$TaskName' for every Monday at $At."

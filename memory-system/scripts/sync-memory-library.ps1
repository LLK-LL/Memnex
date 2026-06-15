param(
    [string]$RepositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [string]$CodexHome = "$env:USERPROFILE\.codex",
    [string]$AgentsHome = "$env:USERPROFILE\.agents",
    [string]$TamHome = "$env:USERPROFILE\.tam",
    [switch]$NoPush
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[AI-brain] $Message"
}

function New-CleanDirectory {
    param([string]$Path)
    if (Test-Path -LiteralPath $Path) {
        Remove-Item -LiteralPath $Path -Recurse -Force
    }
    New-Item -ItemType Directory -Path $Path -Force | Out-Null
}

function Copy-TreeFiltered {
    param(
        [string]$Source,
        [string]$Destination,
        [string[]]$ExcludeDirectoryNames = @(".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "node_modules"),
        [string[]]$ExcludeFilePatterns = @("*.log", "*.tmp", "*.bak", "*.sqlite-shm", "*.sqlite-wal")
    )

    if (-not (Test-Path -LiteralPath $Source)) {
        return
    }

    New-Item -ItemType Directory -Path $Destination -Force | Out-Null
    $sourceRoot = (Resolve-Path -LiteralPath $Source).Path

    Get-ChildItem -LiteralPath $sourceRoot -Recurse -Force | ForEach-Object {
        $item = $_
        $relative = $item.FullName.Substring($sourceRoot.Length).TrimStart("\", "/")
        if ([string]::IsNullOrWhiteSpace($relative)) {
            return
        }

        $parts = $relative -split "[\\/]"
        foreach ($excluded in $ExcludeDirectoryNames) {
            if ($parts -contains $excluded) {
                return
            }
        }

        if (-not $item.PSIsContainer) {
            foreach ($pattern in $ExcludeFilePatterns) {
                if ($item.Name -like $pattern) {
                    return
                }
            }
        }

        $target = Join-Path $Destination $relative
        if ($item.PSIsContainer) {
            New-Item -ItemType Directory -Path $target -Force | Out-Null
        } else {
            New-Item -ItemType Directory -Path (Split-Path -Parent $target) -Force | Out-Null
            Copy-Item -LiteralPath $item.FullName -Destination $target -Force
        }
    }
}

function Copy-RedactedTextFile {
    param(
        [string]$Source,
        [string]$Destination
    )

    if (-not (Test-Path -LiteralPath $Source)) {
        return
    }

    New-Item -ItemType Directory -Path (Split-Path -Parent $Destination) -Force | Out-Null
    $sensitivePattern = "(?i)(api[_-]?key|token|secret|password|passwd|credential|auth|bearer|cookie|session)"
    Get-Content -LiteralPath $Source -Raw -ErrorAction Stop |
        ForEach-Object { $_ -split "`r?`n" } |
        ForEach-Object {
            if ($_ -match $sensitivePattern) {
                "# REDACTED: sensitive-looking configuration line"
            } else {
                $_
            }
        } |
        Set-Content -LiteralPath $Destination -Encoding UTF8
}

function Copy-LatestFile {
    param(
        [string]$Directory,
        [string]$Pattern,
        [string]$Destination
    )

    if (-not (Test-Path -LiteralPath $Directory)) {
        return $null
    }

    $file = Get-ChildItem -LiteralPath $Directory -Filter $Pattern -File |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1

    if ($null -eq $file) {
        return $null
    }

    New-Item -ItemType Directory -Path (Split-Path -Parent $Destination) -Force | Out-Null
    Copy-Item -LiteralPath $file.FullName -Destination $Destination -Force
    return $file.FullName
}

Set-Location -LiteralPath $RepositoryRoot

$dataRoot = Join-Path $RepositoryRoot "memory-data"
$currentRoot = Join-Path $dataRoot "current"
New-Item -ItemType Directory -Path $dataRoot -Force | Out-Null
New-CleanDirectory -Path $currentRoot

Write-Step "Copying exported memory data"
$exportsRoot = Join-Path $currentRoot "exports"
New-Item -ItemType Directory -Path $exportsRoot -Force | Out-Null
$latestExport = Copy-LatestFile -Directory (Join-Path $TamHome "backups") -Pattern "export_all_*.json" -Destination (Join-Path $exportsRoot "memory-export-latest.json")
Copy-LatestFile -Directory (Join-Path $TamHome "backups") -Pattern "*.json" -Destination (Join-Path $exportsRoot "latest-backup.json") | Out-Null
if (Test-Path -LiteralPath (Join-Path $TamHome "memory.db")) {
    Copy-Item -LiteralPath (Join-Path $TamHome "memory.db") -Destination (Join-Path $exportsRoot "memory.db.snapshot") -Force
}

Write-Step "Copying file-backed memories, rules, skills, templates, and preferences"
Copy-TreeFiltered -Source (Join-Path $CodexHome "memories") -Destination (Join-Path $currentRoot "memories")
Copy-TreeFiltered -Source (Join-Path $CodexHome "rules") -Destination (Join-Path $currentRoot "rules")
Copy-TreeFiltered -Source (Join-Path $CodexHome "skills") -Destination (Join-Path $currentRoot "skills")
Copy-TreeFiltered -Source (Join-Path $AgentsHome "skills") -Destination (Join-Path $currentRoot "agent-skills")
Copy-TreeFiltered -Source (Join-Path $CodexHome "templates") -Destination (Join-Path $currentRoot "templates")

$preferencesRoot = Join-Path $currentRoot "preferences"
New-Item -ItemType Directory -Path $preferencesRoot -Force | Out-Null
Copy-RedactedTextFile -Source (Join-Path $CodexHome "AGENTS.md") -Destination (Join-Path $preferencesRoot "AGENTS.md")
Copy-RedactedTextFile -Source (Join-Path $CodexHome "config.toml") -Destination (Join-Path $preferencesRoot "config.redacted.toml")
Copy-RedactedTextFile -Source (Join-Path $CodexHome ".codex-global-state.json") -Destination (Join-Path $preferencesRoot "codex-global-state.redacted.json")

$manifest = [ordered]@{
    synced_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    repository = "LLK-LL/AI-brain"
    system_layer = "memory-system"
    data_layer = "memory-data/current"
    latest_memory_export_source = $latestExport
    sources = [ordered]@{
        tam_backups = (Join-Path $TamHome "backups")
        tam_database = (Join-Path $TamHome "memory.db")
        codex_memories = (Join-Path $CodexHome "memories")
        codex_rules = (Join-Path $CodexHome "rules")
        codex_skills = (Join-Path $CodexHome "skills")
        agents_skills = (Join-Path $AgentsHome "skills")
        codex_templates = (Join-Path $CodexHome "templates")
        codex_preferences = @(
            (Join-Path $CodexHome "AGENTS.md"),
            (Join-Path $CodexHome "config.toml"),
            (Join-Path $CodexHome ".codex-global-state.json")
        )
    }
    safety = [ordered]@{
        excluded_directories = @(".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "node_modules")
        excluded_file_patterns = @("*.log", "*.tmp", "*.bak", "*.sqlite-shm", "*.sqlite-wal")
        redacted_preference_keywords = @("api_key", "token", "secret", "password", "credential", "auth", "bearer", "cookie", "session")
    }
}

$manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $dataRoot "manifest.json") -Encoding UTF8

Write-Step "Preparing git commit"
git add README.md .gitignore .gitattributes memory-system memory-data
$status = git status --porcelain
if ([string]::IsNullOrWhiteSpace($status)) {
    Write-Step "No changes to commit"
    exit 0
}

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss K"
git commit -m "Sync memory library snapshot ($timestamp)"

if (-not $NoPush) {
    Write-Step "Pushing to origin"
    git push origin HEAD
}

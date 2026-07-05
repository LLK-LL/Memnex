$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$HostName = "127.0.0.1"
$Port = 8765
$BaseUrl = "http://${HostName}:${Port}"
$GraphUrl = "${BaseUrl}/api/graph"
$IndexUrl = "${BaseUrl}/"
$PixiUrl = "${BaseUrl}/pixi.min.js"
$MemoryUniverse3dScriptUrl = "${BaseUrl}/memory-universe-3d/memory-universe-viewer.js"
$MemoryUniverse3dStyleUrl = "${BaseUrl}/memory-universe-3d/memory-universe-viewer.css"
$MemoryUniverse3dManifestUrl = "${BaseUrl}/memory-universe-3d/manifest.json"

function Test-ViewerHealthy {
    try {
        $index = Invoke-WebRequest -Uri $IndexUrl -UseBasicParsing -TimeoutSec 4
        if (
            $index.StatusCode -ne 200 -or
            $index.Content -notmatch "pixi\.min\.js" -or
            $index.Content -notmatch "memory-universe-3d"
        ) { return $false }
        $pixi = Invoke-WebRequest -Uri $PixiUrl -UseBasicParsing -TimeoutSec 4 -Method Head
        if ($pixi.StatusCode -ne 200) { return $false }
        $universeScript = Invoke-WebRequest -Uri $MemoryUniverse3dScriptUrl -UseBasicParsing -TimeoutSec 4 -Method Head
        if ($universeScript.StatusCode -ne 200) { return $false }
        $universeStyle = Invoke-WebRequest -Uri $MemoryUniverse3dStyleUrl -UseBasicParsing -TimeoutSec 4 -Method Head
        if ($universeStyle.StatusCode -ne 200) { return $false }
        $universeManifest = Invoke-WebRequest -Uri $MemoryUniverse3dManifestUrl -UseBasicParsing -TimeoutSec 4
        if (
            $universeManifest.StatusCode -ne 200 -or
            $universeManifest.Content -notmatch '"publicApiVersion"\s*:\s*"memory-universe-viewer/v1"'
        ) { return $false }
        $response = Invoke-WebRequest -Uri $GraphUrl -UseBasicParsing -TimeoutSec 8
        if ($response.StatusCode -ne 200) { return $false }
        return (
            $response.Content -match '"elements"\s*:' -and
            $response.Content -match '"nodes"\s*:' -and
            $response.Content -match '"metadata"\s*:' -and
            $response.Content -match '"agent_galaxies"\s*:'
        )
    } catch {
        return $false
    }
}

function Stop-ViewerServers {
    $servers = Get-CimInstance Win32_Process | Where-Object {
        $_.CommandLine -match "memory_graph_viewer_server" -and $_.CommandLine -match "--port\s+$Port"
    }
    foreach ($server in $servers) {
        Stop-Process -Id $server.ProcessId -Force -ErrorAction SilentlyContinue
    }
}

function Wait-ViewerHealthy {
    $deadline = (Get-Date).AddSeconds(25)
    do {
        if (Test-ViewerHealthy) { return $true }
        Start-Sleep -Milliseconds 500
    } while ((Get-Date) -lt $deadline)
    return $false
}

function Resolve-ChromePath {
    $chrome = Get-Command chrome -ErrorAction SilentlyContinue
    if ($chrome) { return $chrome.Source }

    $candidates = @(
        "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
        "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
        "$env:LocalAppData\Google\Chrome\Application\chrome.exe"
    )
    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path -LiteralPath $candidate)) { return $candidate }
    }
    throw "Google Chrome was not found. Install Chrome or add chrome.exe to PATH."
}

Stop-ViewerServers
Start-Sleep -Milliseconds 400

if (-not (Test-ViewerHealthy)) {
    $python = Get-Command py -ErrorAction SilentlyContinue
    if ($python) {
        Start-Process -FilePath $python.Source -ArgumentList @("-3", "-m", "src.tools.memory_graph_viewer_server", "--host", $HostName, "--port", [string]$Port) -WorkingDirectory $Root -WindowStyle Hidden
    } else {
        $python = Get-Command python -ErrorAction SilentlyContinue
        if (-not $python) { throw "Python was not found. Install Python or add it to PATH." }
        Start-Process -FilePath $python.Source -ArgumentList @("-m", "src.tools.memory_graph_viewer_server", "--host", $HostName, "--port", [string]$Port) -WorkingDirectory $Root -WindowStyle Hidden
    }
}

if (-not (Wait-ViewerHealthy)) {
    throw "Memory Galaxy Viewer did not become healthy at $GraphUrl"
}

$fresh = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()
$launchUrl = "${BaseUrl}/?fresh=${fresh}"
$chromePath = Resolve-ChromePath
Start-Process -FilePath $chromePath -ArgumentList @($launchUrl)

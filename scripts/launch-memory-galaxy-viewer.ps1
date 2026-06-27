$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$HostName = "127.0.0.1"
$Port = 8765
$BaseUrl = "http://${HostName}:${Port}"
$GraphUrl = "${BaseUrl}/api/graph"
$IndexUrl = "${BaseUrl}/"
$PixiUrl = "${BaseUrl}/pixi.min.js"

function Test-ViewerHealthy {
    try {
        $index = Invoke-WebRequest -Uri $IndexUrl -UseBasicParsing -TimeoutSec 4
        if ($index.StatusCode -ne 200 -or $index.Content -notmatch "pixi\.min\.js") { return $false }
        $pixi = Invoke-WebRequest -Uri $PixiUrl -UseBasicParsing -TimeoutSec 4 -Method Head
        if ($pixi.StatusCode -ne 200) { return $false }
        $response = Invoke-WebRequest -Uri $GraphUrl -UseBasicParsing -TimeoutSec 8
        if ($response.StatusCode -ne 200) { return $false }
        $payload = $response.Content | ConvertFrom-Json
        return $null -ne $payload.elements -and $null -ne $payload.elements.nodes
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

if (-not (Test-ViewerHealthy)) {
    Stop-ViewerServers
    Start-Sleep -Milliseconds 400

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
Start-Process "${BaseUrl}/?fresh=${fresh}"

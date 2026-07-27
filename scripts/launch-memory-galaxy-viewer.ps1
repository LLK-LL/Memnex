$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$HostName = "127.0.0.1"
$Port = 8765
$BaseUrl = "http://${HostName}:${Port}"
$VenvPython = Join-Path $Root ".venv\Scripts\python.exe"
$ServerScript = Join-Path $Root "src\tools\memory_graph_viewer_server.py"
$GraphUrl = "${BaseUrl}/api/graph"
$IndexUrl = "${BaseUrl}/"
$PixiUrl = "${BaseUrl}/pixi.min.js"
$MemoryUniverse3dScriptUrl = "${BaseUrl}/memory-universe-3d/memory-universe-viewer.js"
$MemoryUniverse3dStyleUrl = "${BaseUrl}/memory-universe-3d/memory-universe-viewer.css"
$MemoryUniverse3dManifestUrl = "${BaseUrl}/memory-universe-3d/manifest.json"
$SolarIndexUrl = "${BaseUrl}/knowledge-solar-system/index.html?viewerBase=%2F"
$GalaxyIndexUrl = "${BaseUrl}/knowledge-galaxy-system/index.html?viewerBase=%2F"
$SolarBridgeUrl = "${BaseUrl}/memory-universe-bridge.js"
$GestureWorkerMarker = "gesture.worker"

function Test-ViewerHealthy {
    try {
        $index = Invoke-WebRequest -Uri $IndexUrl -UseBasicParsing -TimeoutSec 4
        if (
            $index.StatusCode -ne 200 -or
            $index.Content -notmatch "pixi\.min\.js" -or
            $index.Content -notmatch "memory-universe-3d" -or
            $index.Content -notmatch "universe3dGalaxy"
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
        $solarBridge = Invoke-WebRequest -Uri $SolarBridgeUrl -UseBasicParsing -TimeoutSec 4
        if (
            $solarBridge.StatusCode -ne 200 -or
            $solarBridge.Content -notmatch 'camera; fullscreen'
        ) { return $false }
        $solarIndex = Invoke-WebRequest -Uri $SolarIndexUrl -UseBasicParsing -TimeoutSec 4
        if (
            $solarIndex.StatusCode -ne 200 -or
            $solarIndex.Content -notmatch 'data-knowledge-solar-gesture-control-start="true"' -or
            $solarIndex.Content -notmatch 'src="\./(assets/index-[^"]+\.js)"'
        ) { return $false }
        $solarMainUrl = "${BaseUrl}/knowledge-solar-system/$($Matches[1])"
        $solarMain = Invoke-WebRequest -Uri $solarMainUrl -UseBasicParsing -TimeoutSec 8
        if (
            $solarMain.StatusCode -ne 200 -or
            $solarMain.Content -notmatch $GestureWorkerMarker
        ) { return $false }
        $galaxyIndex = Invoke-WebRequest -Uri $GalaxyIndexUrl -UseBasicParsing -TimeoutSec 4
        if (
            $galaxyIndex.StatusCode -ne 200 -or
            $galaxyIndex.Content -notmatch 'data-knowledge-galaxy-shell="true"' -or
            $galaxyIndex.Content -notmatch '__knowledgeSolarViewerBasePath' -or
            $galaxyIndex.Content -notmatch 'src="/knowledge-galaxy-system/(assets/[^"]+\.js)"'
        ) { return $false }
        $galaxyMainUrl = "${BaseUrl}/knowledge-galaxy-system/$($Matches[1])"
        $galaxyMain = Invoke-WebRequest -Uri $galaxyMainUrl -UseBasicParsing -TimeoutSec 8 -Method Head
        if ($galaxyMain.StatusCode -ne 200) { return $false }
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
    # 8765 是本地查看器专用端口；按实际监听者回收可避免复用其他工作树的旧服务。
    $processIds = @()
    $servers = Get-CimInstance Win32_Process | Where-Object {
        $_.CommandLine -match "memory_graph_viewer_server" -and $_.CommandLine -match "--port\s+$Port"
    }
    foreach ($server in $servers) {
        $processIds += [int]$server.ProcessId
    }
    $listeners = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    foreach ($listener in $listeners) {
        if ($listener.OwningProcess -gt 0) {
            $processIds += [int]$listener.OwningProcess
        }
    }
    foreach ($processId in ($processIds | Select-Object -Unique)) {
        Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
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
    # 中文注释：固定使用项目虚拟环境，避免 py.exe 选到缺依赖的系统 Python。
    if (-not (Test-Path -LiteralPath $VenvPython)) { throw "Memory Galaxy Viewer Python was not found: $VenvPython" }
    if (-not (Test-Path -LiteralPath $ServerScript)) { throw "Memory Galaxy Viewer server was not found: $ServerScript" }
    Start-Process -FilePath $VenvPython -ArgumentList @($ServerScript, "--host", $HostName, "--port", [string]$Port) -WorkingDirectory $Root -WindowStyle Hidden
}

if (-not (Wait-ViewerHealthy)) {
    throw "Memory Galaxy Viewer did not become healthy at $GraphUrl"
}

$fresh = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()
$launchUrl = "${BaseUrl}/?fresh=${fresh}"
$chromePath = Resolve-ChromePath
Start-Process -FilePath $chromePath -ArgumentList @($launchUrl)

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_memory_galaxy_launcher_uses_health_checked_powershell_script():
    launcher = (ROOT / "launch-memory-galaxy-viewer.cmd").read_text(encoding="utf-8")

    assert "magma-memory-galaxy-visualization" in launcher
    assert "MAGMA_VIEWER_ROOT" in launcher
    assert "if not exist" in launcher
    assert "exit /b 1" in launcher
    assert 'set "VIEWER_ROOT=' not in launcher
    assert "scripts\\launch-memory-galaxy-viewer.ps1" in launcher
    assert "ExecutionPolicy Bypass" in launcher


def test_memory_galaxy_launcher_waits_for_magma_graph_api_before_opening_browser():
    script = (ROOT / "scripts" / "launch-memory-galaxy-viewer.ps1").read_text(encoding="utf-8")

    assert "/api/graph" in script
    assert "magma_families" in script
    assert "agent_galaxies" in script
    assert "ConvertFrom-Json" not in script
    assert "memory_graph_viewer_server" in script
    assert "Stop-Process" in script


def test_memory_galaxy_launcher_opens_google_chrome_directly():
    script = (ROOT / "scripts" / "launch-memory-galaxy-viewer.ps1").read_text(encoding="utf-8")

    assert "function Resolve-ChromePath" in script
    assert "Google\\Chrome\\Application\\chrome.exe" in script
    assert "Start-Process -FilePath $chromePath" in script

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_memory_galaxy_launcher_uses_health_checked_powershell_script():
    launcher = (ROOT / "launch-memory-galaxy-viewer.cmd").read_text(encoding="utf-8")

    assert "scripts\\launch-memory-galaxy-viewer.ps1" in launcher
    assert "ExecutionPolicy Bypass" in launcher


def test_memory_galaxy_launcher_waits_for_graph_api_before_opening_browser():
    script = (ROOT / "scripts" / "launch-memory-galaxy-viewer.ps1").read_text(encoding="utf-8")

    assert "/api/graph" in script
    assert "memory_graph_viewer_server" in script
    assert "Stop-Process" in script

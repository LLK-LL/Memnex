from pathlib import Path


def test_knowledge_solar_iframe_allows_camera_access() -> None:
    bridge = Path("src/tools/memory_graph_viewer_assets/memory-universe-bridge.js").read_text(encoding="utf-8")

    assert 'solarFrame.setAttribute("allow", "camera; fullscreen")' in bridge

"""Serve the memory graph viewer with lightweight local backend APIs."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
from socketserver import ThreadingMixIn
from typing import Any
from urllib.parse import urlparse
from http.server import HTTPServer

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.tools.memory_graph_viewer_export import ASSET_DIR, DEFAULT_DB, connect_readonly, load_graph

PERFORMANCE_CACHE_TTL_SECONDS = 3.0


def collect_system_performance() -> dict[str, Any]:
    """Collect a small, bounded snapshot of host performance."""
    cpu_percent: float | None = None
    memory = {"used_mb": None, "total_mb": None, "percent": None}
    try:
        import psutil  # type: ignore

        cpu_percent = float(psutil.cpu_percent(interval=None))
        vm = psutil.virtual_memory()
        memory = {
            "used_mb": round(float(vm.used) / 1048576, 1),
            "total_mb": round(float(vm.total) / 1048576, 1),
            "percent": round(float(vm.percent), 1),
        }
    except Exception:
        pass

    return {
        "source": "backend",
        "timestamp": time.time(),
        "cpu_percent": cpu_percent,
        "memory": memory,
        "gpu": _collect_nvidia_gpu(),
    }


def get_cached_system_performance(
    cache: dict[str, Any],
    *,
    now: float | None = None,
    ttl_seconds: float = PERFORMANCE_CACHE_TTL_SECONDS,
) -> dict[str, Any]:
    """Return a bounded performance snapshot without repeatedly spawning probes."""
    timestamp = time.time() if now is None else now
    cached_at = float(cache.get("timestamp", 0) or 0)
    payload = cache.get("payload")
    if payload is not None and timestamp - cached_at < ttl_seconds:
        return payload
    payload = collect_system_performance()
    cache["timestamp"] = timestamp
    cache["payload"] = payload
    return payload


def _collect_nvidia_gpu() -> dict[str, Any] | None:
    command = [
        "nvidia-smi",
        "--query-gpu=utilization.gpu,memory.used,memory.total,name",
        "--format=csv,noheader,nounits",
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=0.7, check=False)
    except Exception:
        return None
    if result.returncode != 0:
        return None
    line = result.stdout.splitlines()[0].strip() if result.stdout.splitlines() else ""
    parts = [part.strip() for part in line.split(",", 3)]
    if len(parts) < 4:
        return None
    try:
        return {
            "utilization_percent": float(parts[0]),
            "memory_used_mb": float(parts[1]),
            "memory_total_mb": float(parts[2]),
            "name": parts[3],
        }
    except ValueError:
        return None


class ThreadedMemoryGraphViewerServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

    def __init__(self, server_address, request_handler_class, *, db_path: Path, asset_dir: Path):
        super().__init__(server_address, request_handler_class)
        self.db_path = Path(db_path)
        self.asset_dir = Path(asset_dir)
        self._perf_cache: dict[str, Any] = {}
        self._thread: threading.Thread | None = None

    def start_in_thread(self) -> threading.Thread:
        self._thread = threading.Thread(target=self.serve_forever, daemon=True)
        self._thread.start()
        return self._thread


class MemoryGraphViewerHandler(SimpleHTTPRequestHandler):
    server: ThreadedMemoryGraphViewerServer

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/graph":
            self._send_graph()
            return
        if parsed.path == "/api/system/performance":
            self._send_performance()
            return
        super().do_GET()

    def translate_path(self, path: str) -> str:
        parsed = urlparse(path)
        relative = parsed.path.lstrip("/") or "index.html"
        relative_path = Path(relative)
        if relative_path.is_absolute() or ".." in relative_path.parts:
            return str(self.server.asset_dir / "index.html")
        return str(self.server.asset_dir / relative_path)

    def _send_graph(self) -> None:
        try:
            with connect_readonly(self.server.db_path) as conn:
                graph = load_graph(conn)
            self._send_json(graph)
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=500)

    def _send_performance(self) -> None:
        payload = get_cached_system_performance(self.server._perf_cache)
        self._send_json(payload)

    def _send_json(self, payload: dict[str, Any], *, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--assets", type=Path, default=ASSET_DIR)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    server = ThreadedMemoryGraphViewerServer(
        (args.host, args.port),
        MemoryGraphViewerHandler,
        db_path=args.db,
        asset_dir=args.assets,
    )
    print(f"Serving memory graph viewer at http://{args.host}:{server.server_port}/", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

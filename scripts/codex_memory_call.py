#!/usr/bin/env python3
"""Small Codex fallback client for the local total-agent-memory MCP server.

This uses line-delimited JSON-RPC because this installation's MCP Python
stdio server reads one JSON message per line. Use it when a Codex session has
not exposed deferred MCP tools yet.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "src" / "server.py"
PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
MEMORY_DIR = Path(os.environ.get("TAM_MEMORY_DIR") or os.environ.get("CLAUDE_MEMORY_DIR") or (Path.home() / ".tam"))


def _start() -> subprocess.Popen[str]:
    env = os.environ.copy()
    env.setdefault("TAM_MEMORY_DIR", str(MEMORY_DIR))
    env.setdefault("CLAUDE_MEMORY_DIR", str(MEMORY_DIR))
    env.setdefault("MEMORY_MODE", "fast")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    return subprocess.Popen(
        [str(PYTHON), str(SERVER)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        env=env,
    )


def _send(proc: subprocess.Popen[str], obj: dict) -> None:
    assert proc.stdin is not None
    proc.stdin.write(json.dumps(obj, ensure_ascii=True) + "\n")
    proc.stdin.flush()


def _recv(proc: subprocess.Popen[str], request_id: int, timeout: float = 90.0) -> dict:
    assert proc.stdout is not None
    deadline = time.time() + timeout
    while time.time() < deadline:
        line = proc.stdout.readline()
        if not line:
            raise RuntimeError("MCP server stdout closed")
        msg = json.loads(line)
        if msg.get("id") == request_id:
            return msg
    raise TimeoutError(f"Timed out waiting for request id {request_id}")


def call_tool(name: str, arguments: dict) -> dict:
    proc = _start()
    try:
        _send(proc, {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"codex-memory-fallback","version":"1"}}})
        _recv(proc, 1)
        _send(proc, {"jsonrpc":"2.0","method":"notifications/initialized","params":{}})
        _send(proc, {"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":name,"arguments":arguments}})
        return _recv(proc, 2)
    finally:
        proc.kill()


def main() -> int:
    parser = argparse.ArgumentParser(description="Call local total-agent-memory MCP tools from Codex.")
    parser.add_argument("tool", help="MCP tool name, e.g. memory_save or memory_recall")
    parser.add_argument("arguments_json", help="JSON object containing tool arguments")
    args = parser.parse_args()
    if args.arguments_json.startswith("@"):
        payload = Path(args.arguments_json[1:]).read_text(encoding="utf-8-sig")
    else:
        payload = args.arguments_json
    result = call_tool(args.tool, json.loads(payload))
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0 if "error" not in result else 1


if __name__ == "__main__":
    raise SystemExit(main())



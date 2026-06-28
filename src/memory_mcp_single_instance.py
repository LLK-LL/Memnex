from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def default_lock_path(memory_dir: Path) -> Path:
    return Path(memory_dir) / "memory-mcp.lock"


def should_claim_single_instance_lock(value: str | None) -> bool:
    """Return whether destructive stdio single-instance cleanup is enabled.

    Stdio MCP clients own the server process they spawn. Killing older
    ``server.py`` processes by default can close another active client's pipe
    during initialize, so this legacy cleanup must be explicit opt-in.
    """
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "kill-old", "force"}


def claim_single_instance_lock(
    lock_path: Path,
    *,
    current_pid: int | None = None,
    script_path: Path | None = None,
) -> None:
    current_pid = int(current_pid or os.getpid())
    owner_pid = _parent_pid(current_pid) or current_pid
    script_path = Path(script_path or sys.argv[0]).resolve()
    lock_path = Path(lock_path)
    lock_path.parent.mkdir(parents=True, exist_ok=True)

    for old_pid in _older_matching_instance_owner_pids(script_path, owner_pid):
        if old_pid not in {current_pid, owner_pid}:
            _terminate_process_tree(old_pid)

    previous = _read_lock(lock_path)
    previous_pid = _coerce_pid(previous.get("pid")) if previous else None
    if previous_pid and previous_pid not in {current_pid, owner_pid} and _pid_is_running(previous_pid):
        _terminate_process_tree(previous_pid)

    payload = {
        "pid": owner_pid,
        "worker_pid": current_pid,
        "script": str(script_path),
        "updated_at": time.time(),
    }
    lock_path.write_text(json.dumps(payload, ensure_ascii=True), encoding="utf-8")


def _read_lock(lock_path: Path) -> dict[str, Any]:
    try:
        return json.loads(Path(lock_path).read_text(encoding="utf-8"))
    except Exception:
        return {}


def _coerce_pid(value: Any) -> int | None:
    try:
        pid = int(value)
    except (TypeError, ValueError):
        return None
    return pid if pid > 0 else None


def _pid_is_running(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _parent_pid(pid: int) -> int | None:
    if os.name != "nt":
        return None
    try:
        output = subprocess.check_output(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                f"(Get-CimInstance Win32_Process -Filter \"ProcessId={int(pid)}\").ParentProcessId",
            ],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=2,
        ).strip()
        parent = int(output) if output else 0
    except Exception:
        return None
    return parent if parent > 0 else None


def _older_matching_instance_owner_pids(script_path: Path, owner_pid: int) -> list[int]:
    if os.name != "nt":
        return []
    script_text = str(Path(script_path).resolve()).replace("\\", "/").lower()
    try:
        output = subprocess.check_output(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-CimInstance Win32_Process | "
                "Where-Object { $_.Name -in @('python.exe','py.exe') } | "
                "Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress",
            ],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=4,
        ).strip()
    except Exception:
        return []
    if not output:
        return []
    try:
        records = json.loads(output)
    except json.JSONDecodeError:
        return []
    if isinstance(records, dict):
        records = [records]

    by_pid = {}
    for record in records:
        pid = _coerce_pid(record.get("ProcessId"))
        if pid:
            by_pid[pid] = record

    owner_record = by_pid.get(owner_pid)
    owner_created = str(owner_record.get("CreationDate", "")) if owner_record else ""
    owners: set[int] = set()
    for record in records:
        command = str(record.get("CommandLine") or "").replace("\\", "/").lower()
        if script_text not in command:
            continue
        pid = _coerce_pid(record.get("ProcessId"))
        if not pid or pid == os.getpid():
            continue
        parent = _coerce_pid(record.get("ParentProcessId"))
        candidate_owner = parent if parent and parent in by_pid else pid
        if candidate_owner == owner_pid:
            continue
        created = str(record.get("CreationDate", ""))
        if owner_created and created and created > owner_created:
            continue
        owners.add(candidate_owner)
    return sorted(owners)


def _terminate_process_tree(pid: int) -> None:
    if pid <= 0 or pid == os.getpid():
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError:
        pass

from pathlib import Path

from src import memory_mcp_single_instance as single_instance


def test_single_instance_lock_is_opt_in_for_stdio_mcp():
    assert single_instance.should_claim_single_instance_lock(None) is False
    assert single_instance.should_claim_single_instance_lock("") is False
    assert single_instance.should_claim_single_instance_lock("0") is False
    assert single_instance.should_claim_single_instance_lock("false") is False
    assert single_instance.should_claim_single_instance_lock("1") is True
    assert single_instance.should_claim_single_instance_lock("kill-old") is True


def test_single_instance_lock_terminates_previous_live_owner(tmp_path, monkeypatch):
    lock_path = tmp_path / "memory-mcp.lock"
    lock_path.write_text('{"pid": 111, "script": "old"}', encoding="utf-8")
    terminated = []

    monkeypatch.setattr(single_instance, "_pid_is_running", lambda pid: pid == 111)
    monkeypatch.setattr(single_instance, "_terminate_process_tree", lambda pid: terminated.append(pid))

    single_instance.claim_single_instance_lock(lock_path, current_pid=222, script_path=Path("server.py"))

    assert terminated == [111]
    assert '"pid": 222' in lock_path.read_text(encoding="utf-8")


def test_single_instance_lock_records_parent_pid_for_child_process(tmp_path, monkeypatch):
    lock_path = tmp_path / "memory-mcp.lock"
    terminated = []

    monkeypatch.setattr(single_instance, "_parent_pid", lambda pid: 111 if pid == 222 else None)
    monkeypatch.setattr(single_instance, "_pid_is_running", lambda pid: False)
    monkeypatch.setattr(single_instance, "_terminate_process_tree", lambda pid: terminated.append(pid))

    single_instance.claim_single_instance_lock(lock_path, current_pid=222, script_path=Path("server.py"))

    assert terminated == []
    assert '"pid": 111' in lock_path.read_text(encoding="utf-8")


def test_single_instance_lock_ignores_current_owner(tmp_path, monkeypatch):
    lock_path = tmp_path / "memory-mcp.lock"
    lock_path.write_text('{"pid": 222, "script": "same"}', encoding="utf-8")
    terminated = []

    monkeypatch.setattr(single_instance, "_pid_is_running", lambda pid: True)
    monkeypatch.setattr(single_instance, "_terminate_process_tree", lambda pid: terminated.append(pid))

    single_instance.claim_single_instance_lock(lock_path, current_pid=222, script_path=Path("server.py"))

    assert terminated == []
    assert '"pid": 222' in lock_path.read_text(encoding="utf-8")


def test_single_instance_lock_replaces_stale_owner_without_terminating(tmp_path, monkeypatch):
    lock_path = tmp_path / "memory-mcp.lock"
    lock_path.write_text('{"pid": 111, "script": "old"}', encoding="utf-8")
    terminated = []

    monkeypatch.setattr(single_instance, "_pid_is_running", lambda pid: False)
    monkeypatch.setattr(single_instance, "_terminate_process_tree", lambda pid: terminated.append(pid))

    single_instance.claim_single_instance_lock(lock_path, current_pid=222, script_path=Path("server.py"))

    assert terminated == []
    assert '"pid": 222' in lock_path.read_text(encoding="utf-8")


def test_single_instance_lock_reaps_older_matching_instances(tmp_path, monkeypatch):
    lock_path = tmp_path / "memory-mcp.lock"
    terminated = []

    monkeypatch.setattr(single_instance, "_parent_pid", lambda pid: None)
    monkeypatch.setattr(single_instance, "_pid_is_running", lambda pid: False)
    monkeypatch.setattr(single_instance, "_terminate_process_tree", lambda pid: terminated.append(pid))
    monkeypatch.setattr(single_instance, "_older_matching_instance_owner_pids", lambda script, pid: [111, 333])

    single_instance.claim_single_instance_lock(lock_path, current_pid=222, script_path=Path("server.py"))

    assert terminated == [111, 333]

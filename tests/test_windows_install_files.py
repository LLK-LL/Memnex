"""Cross-platform file audits for the Windows installer (install.ps1).

These tests run on macOS/Linux CI where `pwsh` is typically absent, so they
rely on regex auditing + filesystem structure checks rather than invoking
PowerShell. They verify shape, not runtime behaviour - Test-Install.ps1
covers runtime smoke on Windows.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest


ROOT = Path(__file__).parent.parent
INSTALL_PS1 = ROOT / "install.ps1"
HOOKS_DIR = ROOT / "hooks"
RUN_REFLECTION_TASK_PS1 = ROOT / "scripts" / "run_reflection_task.ps1"


@pytest.fixture(scope="module")
def install_text() -> str:
    assert INSTALL_PS1.exists(), "install.ps1 must exist at repo root"
    return INSTALL_PS1.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def run_reflection_task_text() -> str:
    assert RUN_REFLECTION_TASK_PS1.exists(), "run_reflection_task.ps1 must exist"
    return RUN_REFLECTION_TASK_PS1.read_text(encoding="utf-8")


# ------------------------------------------------------------------
# Version / banner
# ------------------------------------------------------------------

def test_install_ps1_version_bumped(install_text: str):
    """Banner must advertise v8.0, not the old v6.0."""
    assert "v8.0" in install_text, "install.ps1 banner must reference v8.0"
    assert "v6.0" not in install_text, (
        "stale 'v6.0' found in install.ps1 - bump the banner"
    )


def test_install_ps1_mentions_total_agent_memory(install_text: str):
    """Project rebranded from 'Claude Total Memory' to 'total-agent-memory'."""
    # Banner line should use the new slug
    assert re.search(r"total-agent-memory\s+v8\.0", install_text)


# ------------------------------------------------------------------
# Parameters
# ------------------------------------------------------------------

def test_install_ps1_has_ide_parameter(install_text: str):
    """-Ide <name> parameter with full ValidateSet must be declared."""
    assert re.search(r"\[string\]\s*\$Ide", install_text), (
        "missing [string]$Ide parameter declaration"
    )
    # ValidateSet must include all 5 supported IDEs
    for ide in ("claude-code", "cursor", "gemini-cli", "opencode", "codex"):
        assert ide in install_text, f"ValidateSet must include '{ide}'"
    assert "ValidateSet" in install_text


def test_install_ps1_has_uninstall_switch(install_text: str):
    assert re.search(r"\[switch\]\s*\$Uninstall", install_text), (
        "missing [switch]$Uninstall parameter"
    )
    # And the branch must actually fire when -Uninstall is passed
    assert "if ($Uninstall)" in install_text


def test_install_ps1_has_testmode_switch(install_text: str):
    assert re.search(r"\[switch\]\s*\$TestMode", install_text)


def test_install_ps1_honors_install_test_mode_env(install_text: str):
    """INSTALL_TEST_MODE=1 env should still force -TestMode (bash parity)."""
    assert "INSTALL_TEST_MODE" in install_text


# ------------------------------------------------------------------
# Register-Mcp-* functions (one per IDE)
# ------------------------------------------------------------------

REGISTER_FUNCS = (
    "Register-Mcp-ClaudeCode",
    "Register-Mcp-Cursor",
    "Register-Mcp-GeminiCli",
    "Register-Mcp-OpenCode",
    "Register-Mcp-Codex",
)


@pytest.mark.parametrize("func_name", REGISTER_FUNCS)
def test_register_mcp_function_defined(install_text: str, func_name: str):
    pattern = rf"function\s+{re.escape(func_name)}\b"
    assert re.search(pattern, install_text), f"missing function {func_name}"


def test_register_mcp_dispatch_switch(install_text: str):
    """All 5 IDEs must be dispatched from the switch."""
    # Match the dispatch switch block
    assert 'switch ($Ide)' in install_text
    assert "Register-Mcp-ClaudeCode" in install_text
    assert "Register-Mcp-Cursor" in install_text
    assert "Register-Mcp-GeminiCli" in install_text
    assert "Register-Mcp-OpenCode" in install_text
    assert "Register-Mcp-Codex" in install_text


def test_codex_register_uses_toml_fence(install_text: str):
    """Codex branch must use the same fence markers as install.sh."""
    assert "# --- Claude Total Memory MCP Server ---" in install_text
    assert "# --- End Claude Total Memory ---" in install_text
    assert 'type = "stdio"' in install_text
    assert 'TAM_MEMORY_DIR = "$memEsc"' in install_text
    # v7.1 env overrides
    assert 'MEMORY_TRIPLE_TIMEOUT_SEC' in install_text
    assert 'MEMORY_ENRICH_TIMEOUT_SEC' in install_text
    assert 'MEMORY_REPR_TIMEOUT_SEC' in install_text
    assert 'MEMORY_TRIPLE_MAX_PREDICT' in install_text


# ------------------------------------------------------------------
# v8.0 hooks - .ps1 counterparts must exist
# ------------------------------------------------------------------

V8_HOOK_PAIRS = [
    # (bash_name, ps1_name) - .sh in repo must have a .ps1 sibling
    ("auto-capture.sh",       "auto-capture.ps1"),
    ("memory-trigger.sh",     "memory-trigger.ps1"),
    ("session-start.sh",      "session-start.ps1"),
    ("session-end.sh",        "session-end.ps1"),
    ("on-stop.sh",            "on-stop.ps1"),
    ("codex-notify.sh",       "codex-notify.ps1"),
    # v8.0 additions
    ("user-prompt-submit.sh", "user-prompt-submit.ps1"),
    ("post-tool-use.sh",      "post-tool-use.ps1"),
]


@pytest.mark.parametrize("bash_name,ps1_name", V8_HOOK_PAIRS)
def test_all_v8_hooks_have_ps1_version(bash_name: str, ps1_name: str):
    bash_path = HOOKS_DIR / bash_name
    ps1_path = HOOKS_DIR / ps1_name
    if not bash_path.exists():
        pytest.skip(f"{bash_name} not in repo - nothing to port")
    assert ps1_path.exists(), (
        f"hook {bash_name} has no PowerShell port at {ps1_name}"
    )


def test_pre_edit_ps1_exists_even_without_bash():
    """pre-edit / on-bash-error live in ~/.claude/hooks/ globally, but the
    Windows installer copies them from repo - they must be in-repo too."""
    assert (HOOKS_DIR / "pre-edit.ps1").exists()
    assert (HOOKS_DIR / "on-bash-error.ps1").exists()


@pytest.mark.parametrize("ps1_name", [p for _, p in V8_HOOK_PAIRS] + ["pre-edit.ps1", "on-bash-error.ps1"])
def test_ps1_hook_is_nonempty(ps1_name: str):
    p = HOOKS_DIR / ps1_name
    assert p.exists(), f"missing {ps1_name}"
    text = p.read_text(encoding="utf-8")
    assert len(text.strip()) > 0, f"{ps1_name} is empty"
    # Must not contain obvious bashism leftovers
    assert "#!/usr/bin/env bash" not in text, (
        f"{ps1_name} still has bash shebang - incomplete port"
    )


def test_windows_user_prompt_hook_defaults_to_tam_dir():
    text = (HOOKS_DIR / "user-prompt-submit.ps1").read_text(encoding="utf-8")
    assert "$env:TAM_MEMORY_DIR" in text
    assert 'Join-Path $env:USERPROFILE ".tam"' in text
    assert 'Join-Path $env:USERPROFILE ".claude-memory"' not in text


def test_windows_bash_error_hook_uses_self_error_log_and_auto_writer():
    text = (HOOKS_DIR / "on-bash-error.ps1").read_text(encoding="utf-8")
    assert "self_error_log" in text
    assert "auto_self_improve.py" in text
    assert '"error"' in text
    assert "learn_error" not in text


# ------------------------------------------------------------------
# Hook registration in settings.json
# ------------------------------------------------------------------

def test_register_claudecode_wires_all_v8_hooks(install_text: str):
    """SessionStart, SessionEnd, Stop, UserPromptSubmit, PreToolUse, PostToolUse all present."""
    # These must appear as keys in the hooks hashtable assignment
    required_events = (
        "SessionStart",
        "SessionEnd",
        "Stop",
        "UserPromptSubmit",
        "PreToolUse",
        "PostToolUse",
    )
    # narrow search to the ClaudeCode function body
    match = re.search(
        r"function\s+Register-Mcp-ClaudeCode.*?^\}",
        install_text,
        re.DOTALL | re.MULTILINE,
    )
    assert match, "Register-Mcp-ClaudeCode function body not found"
    body = match.group(0)
    for evt in required_events:
        assert f'"{evt}"' in body, f"hooks block must set {evt}"


# ------------------------------------------------------------------
# Task Scheduler
# ------------------------------------------------------------------

def test_register_background_task_helper_defined(install_text: str):
    assert "function Register-BackgroundTask" in install_text


def test_three_background_tasks_registered(install_text: str):
    """reflection, orphan-backfill, check-updates - mirrors launchagents/."""
    for task in (
        "total-agent-memory-reflection",
        "total-agent-memory-orphan-backfill",
        "total-agent-memory-check-updates",
    ):
        assert task in install_text, f"missing scheduled task '{task}'"


def test_reflection_task_uses_local_ollama_3b(run_reflection_task_text: str):
    """Scheduled reflection should not depend on Codex remote API credentials."""
    assert '$env:FASTEMBED_CACHE_DIR = "D:\\CodexCache\\fastembed"' in run_reflection_task_text
    assert '$env:MEMORY_LLM_PROVIDER = "ollama"' in run_reflection_task_text
    assert '$env:MEMORY_LLM_MODEL = "qwen2.5:3b"' in run_reflection_task_text
    assert '$env:MEMORY_TRIPLE_PROVIDER = "ollama"' in run_reflection_task_text
    assert '$env:MEMORY_ENRICH_PROVIDER = "ollama"' in run_reflection_task_text
    assert "auth.json" not in run_reflection_task_text
    assert "OPENAI_API_KEY" not in run_reflection_task_text
    assert "gpt-5.4-mini" not in run_reflection_task_text


def test_uninstall_removes_all_tasks(install_text: str):
    """Uninstall branch must Unregister-ScheduledTask for each task.

    The function body is allowed to reference tasks by variable (e.g.
    ``$TaskReflection``) as long as those variables are defined at script
    scope and point at the expected literal task names.
    """
    match = re.search(
        r"function\s+Invoke-Uninstall.*?^\}",
        install_text,
        re.DOTALL | re.MULTILINE,
    )
    assert match, "Invoke-Uninstall body not found"
    body = match.group(0)
    assert "Unregister-ScheduledTask" in body

    task_vars = ("$TaskReflection", "$TaskOrphanBackfill", "$TaskCheckUpdates")
    task_literals = (
        "total-agent-memory-reflection",
        "total-agent-memory-orphan-backfill",
        "total-agent-memory-check-updates",
    )

    # Each task must be referenced inside Invoke-Uninstall (as literal or var)
    for lit, var in zip(task_literals, task_vars):
        assert (lit in body) or (var in body), (
            f"uninstall must remove {lit} (literal or {var})"
        )

    # When variables are used, they must be defined at script scope to the
    # expected literal task names.
    for lit, var in zip(task_literals, task_vars):
        if var in body and lit not in body:
            # Find declaration like:  $TaskReflection = "total-agent-memory-reflection"
            pattern = rf'{re.escape(var)}\s*=\s*"{re.escape(lit)}"'
            assert re.search(pattern, install_text), (
                f"{var} must be declared as '{lit}' at script scope"
            )


# ------------------------------------------------------------------
# Cross-drive path safety
# ------------------------------------------------------------------

def test_install_uses_path_combine(install_text: str):
    """All cross-drive paths should use [System.IO.Path]::Combine for safety."""
    # We still permit Join-Path here and there, but Combine must be used for
    # the venv python resolution at least (where Scripts\python.exe goes).
    assert "[System.IO.Path]::Combine" in install_text
    # And the key variables should use it
    assert re.search(
        r"\$VenvPython\s*=\s*\[System\.IO\.Path\]::Combine",
        install_text,
    )


# ------------------------------------------------------------------
# Test-Install.ps1 companion smoke test file must exist
# ------------------------------------------------------------------

def test_pester_smoke_file_present():
    p = ROOT / "tests" / "Test-Install.ps1"
    assert p.exists(), "tests/Test-Install.ps1 must exist for Windows CI"
    # Minimal sanity
    body = p.read_text(encoding="utf-8")
    assert "TestMode" in body or "Test-Path" in body

---
name: windows-scheduled-task-hidden
description: >
  Use when Windows Scheduled Tasks, watchdogs, launchers, or background services
  flash visible PowerShell or console windows, need hidden startup wrappers, or
  fail because existing processes lock installer or virtualenv files.
---

# Windows Scheduled Task Hidden

## Goal

Run Windows scheduled background tasks without visible console popups while
preserving existing watchdog, logging, and startup behavior.

## Use When

- A scheduled task flashes a PowerShell or console window in an interactive
  desktop session.
- `-WindowStyle Hidden` is not enough.
- A watchdog or service launcher should start silently.
- Installers fail because existing app-owned processes lock venv or executable
  files.

## Do Not Use When

- The user explicitly wants a visible interactive window.
- The task is a foreground CLI the user must control.

## Inputs

- Scheduled task name.
- Existing PowerShell or batch launcher.
- Target port, health check, or log path if relevant.

## Workflow

1. Inspect the current scheduled task action and trigger.
2. Preserve the existing PowerShell logic when it already handles checks,
   logging, or startup correctly.
3. Add a minimal `.vbs` WScript wrapper that launches the existing script with
   window style `0` and non-blocking execution when appropriate.
4. Change the scheduled task action to run `wscript.exe` with the wrapper path.
5. For installer file-lock failures, stop only app-owned processes and
   temporarily disable app-owned scheduled tasks before reinstalling.
6. Restore or rerun task installation after the install completes.
7. Verify both direct task execution and the recurring trigger path.

## Validation

- `LastTaskResult` is `0` or the expected success code.
- Target process, port, or health endpoint is available.
- No visible PowerShell window appears during manual `Start-ScheduledTask`.
- Logs still update as before.

## Failure Modes

- Console still flashes: task still launches `powershell.exe` directly or an
  intermediate launcher opens a console.
- Installer cannot rebuild venv: app-owned Python processes still hold files.
- Shortcut or task points at stale launcher names: inspect actual generated
  paths before assuming entrypoint names.

## RAG Handoff

Search memory for `windows`, `scheduled-task`, `powershell-popup`, `wscript`,
`installer`, and the app name before editing tasks.

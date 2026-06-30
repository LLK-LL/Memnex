@echo off
setlocal

cd /d "%~dp0"

set "MAGMA_VIEWER_ROOT=%~dp0.worktrees\magma-memory-galaxy-visualization\"
if not exist "%MAGMA_VIEWER_ROOT%scripts\launch-memory-galaxy-viewer.ps1" (
    echo MAGMA Memory Galaxy viewer chain was not found:
    echo %MAGMA_VIEWER_ROOT%
    exit /b 1
)

cd /d "%MAGMA_VIEWER_ROOT%"
powershell -NoProfile -ExecutionPolicy Bypass -File "%MAGMA_VIEWER_ROOT%scripts\launch-memory-galaxy-viewer.ps1"

endlocal

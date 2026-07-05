@echo off
setlocal

cd /d "%~dp0"

set "VIEWER_ROOT=%~dp0"
if not exist "%VIEWER_ROOT%scripts\launch-memory-galaxy-viewer.ps1" (
    echo Memory Galaxy viewer launcher was not found:
    echo %VIEWER_ROOT%scripts\launch-memory-galaxy-viewer.ps1
    exit /b 1
)

cd /d "%VIEWER_ROOT%"
powershell -NoProfile -ExecutionPolicy Bypass -File "%VIEWER_ROOT%scripts\launch-memory-galaxy-viewer.ps1"

endlocal

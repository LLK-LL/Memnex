@echo off
setlocal

cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
  set "PYTHON_CMD=py -3"
) else (
  where python >nul 2>nul
  if %errorlevel%==0 (
    set "PYTHON_CMD=python"
  ) else (
    echo Python was not found. Install Python or add it to PATH.
    pause
    exit /b 1
  )
)

start "Memory Galaxy Viewer" /min %PYTHON_CMD% -m src.tools.memory_graph_viewer_server --host 127.0.0.1 --port 8765

timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:8765/"

endlocal

@echo off
REM Auto-start TAM Memory HTTP Server
set PORT=3747
set LOG=C:/Users/Administrator/total-agent-memory/tmp/http_server.log

REM Check if already listening
powershell -NoProfile -Command "if (Get-NetTCPConnection -LocalPort %PORT% -ErrorAction SilentlyContinue) { exit 1 } else { exit 0 }" >/dev/null 2>&1
if %ERRORLEVEL% EQU 1 exit /b 0

echo Starting TAM HTTP server... >> %LOG%
set MEMORY_MODE=fast
set MEMORY_EMBED_PROVIDER=fastembed
set MEMORY_MCP_SINGLE_INSTANCE=0
set TAM_MEMORY_DIR=C:/Users/Administrator/.tam
set TAM_AGENT_NAMESPACE=reasonix
set MCP_TRANSPORT=http
set MCP_HTTP_HOST=127.0.0.1
set MCP_HTTP_PORT=%PORT%
C:/Users/Administrator/total-agent-memory/.venv/Scripts/python.exe C:/Users/Administrator/total-agent-memory/src/server.py >> %LOG% 2>&1

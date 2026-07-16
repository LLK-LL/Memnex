@echo off
REM Auto-start TAM Memory HTTP Server
set PORT=3747
set LOG=C:/Users/Administrator/Memnex/tmp/http_server.log

REM Check if already listening
powershell -NoProfile -Command "if (Get-NetTCPConnection -LocalPort %PORT% -ErrorAction SilentlyContinue) { exit 1 } else { exit 0 }" >nul 2>&1
if %ERRORLEVEL% EQU 1 exit /b 0

echo Starting TAM HTTP server... >> %LOG%
set MEMORY_MODE=fast
set MEMORY_GRAPH_EXPAND=1
set MEMORY_GRAPH_EXPAND_MAX_RATIO=0.5
set MEMORY_RECALL_RELEVANCE_GATE=1
set MEMORY_RECALL_MIN_COVERAGE=0.25
set MEMORY_EMBED_PROVIDER=fastembed
set MEMORY_LLM_PROVIDER=ollama
set MEMORY_LLM_MODEL=qwen2.5:3b
set MEMORY_ASYNC_ENRICHMENT=false
set MEMORY_ENRICHMENT_ENABLED=false
set FASTEMBED_CACHE_DIR=D:/CodexCache/fastembed
set MEMORY_ALLOW_OLLAMA_IN_HOT_PATH=false
set MEMORY_MCP_SINGLE_INSTANCE=0
set MEMORY_ALLOW_HF_DOWNLOAD_IN_HOT_PATH=false
set HF_HUB_OFFLINE=1
set TRANSFORMERS_OFFLINE=1
set HF_HUB_ETAG_TIMEOUT=1
set TAM_MEMORY_DIR=C:/Users/Administrator/.tam
set TAM_AGENT_NAMESPACE=codex
set MCP_TRANSPORT=http
set MCP_HTTP_HOST=127.0.0.1
set MCP_HTTP_PORT=%PORT%
C:/Users/Administrator/Memnex/.venv/Scripts/python.exe C:/Users/Administrator/Memnex/src/server.py >> %LOG% 2>&1

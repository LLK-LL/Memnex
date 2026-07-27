# Installation

Memnex runs on Python 3.10+ and exposes a local MCP server for Codex, Claude
Code, Cursor, Cline, Continue, Aider, Windsurf, Gemini CLI, OpenCode, and other
MCP clients.

## Prerequisites

- Python 3.10 or newer
- Git
- 2 GB free disk space for the virtual environment, models, and local memory
- Optional: Ollama for deeper local enrichment

## Clone And Install

```bash
git clone https://github.com/LLK-LL/Memnex.git
cd Memnex
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

Windows PowerShell:

```powershell
git clone https://github.com/LLK-LL/Memnex.git
cd Memnex
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
```

## Register An Agent

macOS/Linux/WSL:

```bash
bash install.sh --ide codex
bash install.sh --ide claude-code
bash install.sh --ide cursor
```

Windows:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Ide codex
```

Use `--ide` / `-Ide` with one of:

```text
claude-code, codex, cursor, cline, continue, aider, windsurf, gemini-cli, opencode
```

## Start Manually

```bash
tam
```

or:

```bash
python src/server.py
```

## Verify

```bash
tam-lookup "recent memory setup decisions"
python src/tools/version_status.py
```

The local dashboard and Memory Galaxy launcher use localhost services only.

## Export Memory Galaxy

```bash
python src/tools/memory_graph_viewer_export.py --output ./graph-viewer-output
```

Open `graph-viewer-output/index.html`. Do not publish exports from a real
memory database unless you have reviewed and redacted them.

## Update

```bash
git pull
pip install -r requirements.txt
pip install -e .
python src/tools/version_status.py
```

or use:

```bash
bash update.sh
```

## Uninstall

macOS/Linux/WSL:

```bash
bash install.sh --uninstall
```

Windows:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Uninstall
```

The uninstall path removes registered services and MCP entries, but keeps your
local memory directory by default.

# Memnex

**语言：** 简体中文 | [English](README.md)

**仓库：** [LLK-LL/Memnex](https://github.com/LLK-LL/Memnex)

Memnex 是一个面向 AI 编程 agent 的本地优先记忆系统。它让 Codex、Claude
Code、Cursor 和任何 MCP 客户端都能长期保存并召回项目决策、修复经验、规则、
偏好、工作流、实体关系和图谱上下文，而不需要把私人历史交给云端记忆服务。

项目此前以 `total-agent-memory` 作为包名发布；包名、CLI 名称和旧
`claude_total_memory` 兼容层都会继续保留。

![Memnex Knowledge Galaxy 工作台](docs/assets/memnex-v12.7-galaxy-workspace.png)

![Memnex Knowledge Galaxy 观测视图](docs/assets/memnex-v12.7-galaxy-observatory.png)

![Memnex Knowledge Galaxy 飞行视图](docs/assets/memnex-v12.7-galaxy-flight.png)

## 为什么需要 Memnex

AI agent 在一次任务里会越来越懂你的项目，但下一次打开又容易从空白上下文
开始。它会忘记你已经做过的架构取舍、踩过的坑、稳定规则和高频工作流。

Memnex 把这些零散经验整理成本地记忆引擎：

- **项目边界清晰的召回：** search、RAG、timeline、graph 模式可以按项目或
  agent namespace 隔离。
- **多表示检索：** 原文、摘要、关键词、问题、压缩表示、FTS、向量、图扩展
  和 rerank 共同组成召回链路。
- **时间与流程记忆：** 记录什么发生过、何时变化、哪种修复有效、相似任务
  通常怎么做。
- **本地优先隐私：** SQLite 数据库、向量库、日志、真实图谱导出和私人记忆
  默认留在本机。
- **3D Knowledge Galaxy：** 用 2D/3D 工作台查看记忆图谱、星系、太阳系、
  行星、卫星和关系链路。

## 安装

```bash
git clone https://github.com/LLK-LL/Memnex.git
cd Memnex
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

Windows PowerShell：

```powershell
git clone https://github.com/LLK-LL/Memnex.git
cd Memnex
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
```

注册到 agent：

```bash
bash install.sh --ide codex
bash install.sh --ide claude-code
```

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Ide codex
```

支持 Codex、Claude Code、Cursor、Cline、Continue、Aider、Windsurf、
Gemini CLI 和 OpenCode。

## 快速使用

启动 MCP server：

```bash
tam
```

在终端检索记忆：

```bash
tam-lookup "为什么选择当前向量后端？"
lookup-memory "最近 recall 链路修复"
```

导出 Memory Galaxy：

```bash
python src/tools/memory_graph_viewer_export.py --output ./graph-viewer-output
```

打开 `graph-viewer-output/index.html` 查看本地静态可视化。导出器以只读方式
读取记忆数据库，生成的 viewer 目录默认不会进入 Git。

## 核心能力

- `memory_save` / `memory_save_fast`：保存事实、决策、教训、解决方案和约定。
- `memory_recall` / `memory_search_fast` / `memory_get`：召回紧凑或完整上下文。
- `memory_explain_search` / `memory_perf_report`：查看召回层、rerank、缓存和
  近期召回效果。
- `rule_context_refresh` / `save_rule` / `list_rules`：让长期行为规则按需进入上下文。
- `session_init` / `session_end`：让下一次任务能接上上一次的工作。
- `ingest_codebase` / `file_context` / `learn_error`：把代码、文件风险和反复出现的
  修复经验写入记忆图谱。

## 仓库结构

```text
total_agent_memory/        包入口
claude_total_memory/       旧名称兼容层
src/                       记忆引擎、MCP server、召回、图谱、AI 层
src/memory_core/           确定性存储、embedding、检索辅助
src/ai_layer/              可选 LLM 增强与推理辅助
src/tools/                 维护工具和 Memory Galaxy 导出器
migrations/                SQLite schema 迁移
skills/memory-protocol/    可复用 agent 记忆协议
hooks/                     可选捕获和工作流 hook
memory-system/             本地记忆库同步脚本和治理说明
docs/                      当前用户文档和发布说明
```

公开仓库只保留运行时代码、安装脚本、文档和可视化资源。生成日志、私人记忆数据、
本地工作目录、图谱导出和 QA 产物都不会进入仓库。

## 常用配置

```bash
TAM_MEMORY_DIR=~/.tam
TAM_AGENT_NAMESPACE=codex
MEMORY_MODE=fast
MEMORY_TEXT_EMBED_MODEL=jinaai/jina-embeddings-v2-base-zh
MEMORY_RERANK_ENABLED=true
```

更多设置见 [.env.example](.env.example)、[安装文档](docs/installation.md) 和
[安全与脱敏说明](docs/security-and-redaction.md)。

## Knowledge Galaxy

v12.7 的可视化资源已经随包发布，wheel 安装后也能提供和源码仓库一致的视觉工作台。
当前 3D 路由可以渲染由图谱派生的星系、系统、行星、卫星、关系线、inspection
面板和飞行模式。

更多说明：

- [v12.7.0 发布指南](docs/v12.7.0-recall-galaxy-release.md)

## 隐私边界

Memnex 面向本地 agent 记忆。不要公开真实的 `memory.db`、Chroma 存储、原始转录、
`graph-viewer-output/`、日志或私人记忆快照。仓库 `.gitignore` 已经默认排除这些路径，
但第一次公开发布前仍建议人工复查。

## 贡献

大改动前请先开 issue；用户可见工具变化需要同步文档。更多说明见
[CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

MIT，见 [LICENSE](LICENSE)。

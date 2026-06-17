# Memnex

**语言：** [English](README.md) | 简体中文

**仓库地址：** [LLK-LL/Memnex](https://github.com/LLK-LL/Memnex)

Memnex 是一个面向个人 AI agent 的本地优先记忆库。它帮助 Codex、Claude、Cursor、MCP 工具和本地 agent 把一次次工作中真正有价值的内容沉淀下来：记忆、规则、技能、偏好、工作流、导出和快照。

> AI 在一次任务里被你调教得越来越聪明，但下一次打开又像重新开始。

Memnex 会把这种脆弱的本地状态整理成可审查、可恢复、可迁移、可持续迭代的个人 AI 记忆系统。

![Memnex 记忆网络总览](assets/memory-network-overview.png)

## 它保存什么

Memnex 不是简单的聊天记录备份。它保存的是你使用 AI 时形成的“操作层资产”：

| 资产 | 保存内容 | 为什么重要 |
| --- | --- | --- |
| `memories/` | 事实、经验、决策、修复方法、反思记录 | 让 agent 长期记住真正有用的经验 |
| `rules/` | 行为规则和工作约束 | 告诉 agent 下次应该怎么做 |
| `skills/` | 可复用的 Codex skills 和任务流程 | 把成功流程变成可触发技能 |
| `agent-skills/` | 跨 agent 的技能层和路由器 | 在不同 agent 生态里复用工作流 |
| `preferences/` | 脱敏后的偏好和配置快照 | 保留稳定偏好，同时避开明显密钥 |
| `templates/` | 记忆、规则、技能迭代模板 | 让记忆系统可以被持续治理 |
| `manifest.json` | 同步来源和安全处理记录 | 知道每次收集了什么、何时收集、如何处理 |

## 使用前后对比

| 没有 Memnex | 使用 Memnex |
| --- | --- |
| 每次 AI 会话都从空白工作记忆开始。 | 下一次会话可以复用相关记忆、规则和技能。 |
| 调试经验散落在旧聊天里。 | 修复方法和教训变成文件化记忆资产。 |
| 提示词规则分散在多个客户端和项目中。 | 规则可版本化、可审查、可迁移。 |
| 本地记忆数据库时间久了变成黑箱。 | 记忆状态可以查看、对比、回滚和迁移。 |
| 个人工作流需要反复手动训练。 | 成功流程可以沉淀成可复用技能。 |

## 为什么需要 Memnex？

现在的 AI 记忆工具大致分成几类：

| 类型 | 代表项目 | 更适合谁 | 对个人用户的常见不足 |
| --- | --- | --- | --- |
| 通用记忆 API | Mem0 | 开发者、AI 应用、SaaS 产品 | 强大但偏产品/API 集成，对普通个人用户仍有门槛 |
| Stateful Agent 框架 | Letta / MemGPT | 构建长期运行 agent 的开发者 | 更像 agent 开发框架，不只是个人记忆库 |
| 企业级图谱记忆 | Zep | 企业 agent、客服、业务系统 | 强调规模、延迟、合规，个人使用偏重 |
| 本地 MCP 记忆层 | OpenMemory 等 | 多客户端共享记忆的用户 | 主要解决存取记忆，不一定管理技能、规则和工作流资产 |
| 个人知识库 RAG | Obsidian AI、Khoj 等 | 笔记问答、文档检索 | 更偏资料检索，不一定沉淀 AI 行为规则和可复用技能 |

Memnex 选择了一条更适合个人用户的路线。它不追求搭建一个巨大的 AI 平台，而是把你本地已经训练出来的 AI 经验变成可保存、可检索、可迁移、可迭代的个人资产。

## 它是怎么工作的？

Memnex 可以理解成一个三段式循环：

```text
收集 -> 检索 -> 自我迭代
```

### 1. 收集

AI 在真实任务中会产生很多可复用知识：

- 你的写作和代码风格；
- 某个项目的技术约定；
- 调试中的踩坑和修复方法；
- 科研、写作、调研流程；
- 验证过的工具命令；
- 不应该重复走的错误路径；
- 某个技能应该在什么场景触发。

Memnex 会把这些内容从本地记忆导出、文件化记忆、规则、技能、偏好和模板中收集起来，整理到统一的 `memory-data/` 结构中。

### 2. 检索

Memnex 不是为了把全部历史都塞进每一次提示词里。那样既浪费上下文，也会引入噪音。

更合理的方式是：根据当前任务，检索相关的记忆、规则、技能或偏好。

- 做研究任务时，检索研究流程和引用习惯；
- 做代码任务时，检索项目约定和过去修过的问题；
- 做写作任务时，检索语气、结构和风格偏好；
- 做自动化任务时，检索验证过的命令和恢复路径。

### 3. 自我迭代

每次任务结束后，都可以把新的经验沉淀回来：

- 这次哪个流程有效？
- 哪个方法失败了？
- 哪条规则需要更新？
- 哪个工作流可以变成可复用技能？
- 哪些旧记忆已经过时？
- 哪些偏好应该长期保留？
- 哪些内容应该脱敏或删除？

经过多轮使用后，Memnex 会形成一个个人化的 AI 工作系统：

```text
一次任务经验
  -> 长期记忆
  -> 可复用规则
  -> 可触发技能
  -> 下一次任务表现更好
  -> 再次沉淀
```

Memnex 并不是重新训练基础模型，而是在模型外层持续训练你的本地记忆、规则和技能，让 AI 越来越贴近你的工作方式。

## Quick Start

Memnex 当前提供 Windows PowerShell 同步流程。

手动同步：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\memory-system\scripts\sync-memory-library.ps1
```

安装每周自动同步任务：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\memory-system\scripts\install-weekly-task.ps1
```

同步脚本会重建 `memory-data/current/`，复制经过允许的记忆相关来源，进行保守脱敏，生成 `memory-data/manifest.json`，并在有变化时提交和推送。

## 示例流程

```text
1. 完成一次真实的 AI 辅助任务。
2. 把有价值的经验、规则、命令或工作流保存在本地记忆层。
3. 运行 Memnex 同步脚本。
4. 审查生成的 memory-data/ 快照。
5. 让未来的 agent 检索相关记忆，而不是重新学习。
```

查看示例：

- [Codex 记忆同步](examples/codex-memory-sync.md)
- [Claude 适配](examples/claude-adapter.md)
- [Cursor Rules 适配](examples/cursor-rules.md)
- [MCP 记忆导出](examples/mcp-memory-export.md)

## 支持的 Agent 平台

Memnex 当前最适合 Codex + 本地 MCP 记忆生态，但它的存储方式本身是平台无关的。只要某个 agent 能读取 Markdown、规则文件、JSON 导出、本地文件或 MCP 工具，就可以把 Memnex 当成个人记忆来源。

| 平台 | 当前支持程度 | Memnex 提供什么 |
| --- | --- | --- |
| Codex CLI / Codex Desktop / Codex App | 原生支持 | `AGENTS.md`、`.codex/memories`、`.codex/rules`、`.codex/skills`、`.codex/templates`、脱敏后的 `.codex/config.toml` 快照 |
| VS Code / Cursor / Windsurf 中的 Codex | 通过 Codex 扩展原生支持 | 同一套 Codex 记忆、规则和技能层 |
| `.agents` 技能生态 | 原生支持 | 用于跨 agent 复用的 `agent-skills/` 技能层和平台路由 |
| MCP 记忆工具 / Total Agent Memory 类导出 | 原生导出与归档支持 | `memory-data/.../exports` 下的结构化记忆导出 |
| Claude Code / Claude Desktop | 易适配 | 长期记忆、规则、技能和工作流笔记，可转换成 Claude 指令或 MCP 记忆 |
| Cursor | 易适配 | 项目约定、工作流规则、可复用任务指导，可转换成 Cursor Rules |
| Continue | 易适配 | Rules、prompts、tools 和 MCP 可读的记忆导出 |
| Windsurf / Cascade | 易适配 | Memories、Rules 和可选的 MCP 检索 |
| Cline / Roo 类编码 agent | 易适配 | Memory Bank 风格的 Markdown 上下文、项目决策、当前状态和规则 |
| OpenAI Agents SDK | 开发者集成 | 外部记忆源、检索工具、规则/策略来源、技能注册表 |
| LangChain / LangGraph / LlamaIndex / AutoGen / CrewAI | 开发者集成 | 文件化长期记忆和工作流知识 |
| Obsidian / Khoj / 本地知识库工具 | 知识库集成 | 人类可读的长期笔记、模板和工作流记录 |

## Repository Layout

```text
memory-system/
  README.md
  scripts/
    sync-memory-library.ps1        # 收集、脱敏、提交并推送最新状态
    install-weekly-task.ps1        # 安装本地 Windows 每周定时任务

memory-data/
  current/
    exports/                       # 结构化记忆导出和数据库快照
    memories/                      # 文件化长期记忆
    rules/                         # 本地行为规则
    skills/                        # Codex skills
    agent-skills/                  # Agent 层技能
    preferences/                   # 脱敏后的偏好和配置快照
    templates/                     # 记忆/规则/技能治理模板
  snapshots/                       # 历史同步快照
  manifest.json                    # 同步元数据和安全处理记录
```

## 隐私与安全

Memnex 的同步流程默认是保守的。它会排除明显的缓存、日志、临时文件、数据库中间写入文件等不适合上传的内容，也会对偏好和配置快照中的敏感关键词进行脱敏，例如：

- `token`
- `password`
- `secret`
- `api_key`
- `credential`
- `cookie`
- `session`

如果你要公开仓库，仍然建议先人工审查第一次同步结果。更多说明见 [安全与脱敏](docs/security-and-redaction.md)。

## Roadmap

- 增加 macOS/Linux 同步脚本。
- 增加端到端记忆同步流程 demo GIF。
- 增加轻量级记忆、规则、技能检索 helper。
- 增加 Claude、Cursor、Continue、Windsurf、Cline 和 MCP server 适配示例。
- 增加脱敏行为和同步路径处理测试。

## 贡献

Memnex 还处在早期，并且刻意保持小而清晰。最适合的贡献包括：适配示例、脱敏改进、跨平台同步支持，以及真实 agent 工作流文档。

查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解当前贡献方式。

## 一句话总结

**Memnex 是给个人 AI 用户准备的轻量级本地记忆库：它把你的经验、偏好、规则和技能沉淀成可审查、可迁移、可持续迭代的 AI 记忆系统。**

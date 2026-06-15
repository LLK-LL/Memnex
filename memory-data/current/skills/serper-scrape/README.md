# Serper Search & Scrape Skill

用于 [Claude Code](https://claude.ai/code) 的 Serper API 搜索和网页抓取 skill。

通过 Serper API 实现 Google 搜索和网页内容抓取，支持将处理后的内容保存到 Obsidian。

## 功能概览

- **搜索模式** - 根据关键词搜索网页，支持多语言、多国家和时间范围筛选
- **抓取模式** - 获取指定 URL 的完整页面内容（Markdown 格式）
- **组合工作流** - 先搜索获取链接，再抓取感兴趣的页面进行深度分析
- **内容处理** - 自动去除页面噪音，保留有价值信息
- **Obsidian 集成** - 将处理后的内容保存到指定 Obsidian 目录

## 前提条件

- [Claude Code](https://claude.ai/code) 已安装
- [Serper API](https://serper.dev) 账号和 API Key
- `curl` 命令可用（macOS/Linux 默认已安装）

## 安装

### 1. 安装 Skill

将本目录（或 `.skill` 文件）安装到 Claude Code 的 skills 目录中。

### 2. 设置环境变量

将你的 Serper API Key 设置为环境变量：

```bash
# 临时设置（当前终端会话）
export SERPER_API_KEY="your-serper-api-key"

# 永久设置（添加到 shell 配置文件）
echo 'export SERPER_API_KEY="your-serper-api-key"' >> ~/.zshrc
source ~/.zshrc
```

> 获取 API Key：在 [serper.dev](https://serper.dev) 注册账号后，从 Dashboard 复制。

### 3. 验证安装

```bash
# 检查环境变量是否设置
echo $SERPER_API_KEY

# 测试搜索（在 Claude Code 中触发 skill）
# 输入："搜索关于 AI 的最新新闻"
```

## 使用方法

### 搜索网页

在 Claude Code 中输入包含搜索意图的指令，例如：

- "搜索最近一周关于 Claude 4 的新闻"
- "查找 Python 异步编程教程"
- "搜索 2024 年 AI 发展趋势"
- "用中文搜索人工智能最新进展"

Claude 会根据你的指令自动选择搜索参数（关键词、语言、国家、时间范围等）。

### 抓取网页内容

- "获取 https://example.com 的内容"
- "抓取这个网页的正文：https://..."
- "帮我看看这篇文章讲了什么：https://..."

### 组合使用

- "搜索 Claude 相关的新闻，然后获取最相关的两篇文章的详细内容"

## 搜索参数

通过自然语言描述，Claude 会自动解析以下参数：

| 参数 | 说明 | 示例 |
|------|------|------|
| 关键词 | 搜索内容 | "Claude 4" |
| 国家 | 搜索结果地域 | 中文内容用 `cn`，美国用 `us` |
| 语言 | 返回结果语言 | 中文用 `zh-cn`，英文用 `en` |
| 时间范围 | 时效性筛选 | `最近1小时` / `最近24小时` / `最近1周` / `最近1个月` / `最近1年` |
| 数量 | 返回结果条数 | 默认 10 条，最多 100 条 |

## 内容保存

抓取的网页内容会自动处理后保存到 Obsidian。保存规则：

- **普通内容**（新闻、观点、案例等）→ `~/tars/Resources/Web-Search/`
- **技术/工具类**（官方文档、API、教程等）→ `~/tars/Knowledge/`

保存的文件包含：原始 URL、抓取日期、核心内容摘要、金句提取、引用链接等元数据。

## 限制说明

| 限制项 | 说明 |
|--------|------|
| 每次搜索最多抓取 | 5 个网页 |
| API 配额 | 取决于你的 Serper 套餐 |
| 反爬限制 | 部分网站可能无法正常抓取 |
| URL 格式 | 必须包含 `https://` 前缀 |

## 安全说明

- **API Key** 通过环境变量 `SERPER_API_KEY` 读取，切勿硬编码在代码或配置文件中
- 如 API Key 意外泄露，请立即在 [Serper Dashboard](https://serper.dev/dashboard) 重置
- 本 skill 的所有脚本均从环境变量读取密钥，不存储任何凭证

## 目录结构

```
serper-scrape/
├── SKILL.md              # Skill 指令（供 Claude 读取）
├── README.md             # 本文件，使用指南
└── scripts/
    ├── serper-search.sh  # 搜索辅助脚本
    └── serper-scrape.sh  # 抓取辅助脚本
```

## 常见问题

**Q: 搜索没有返回结果？**
A: 检查 SERPER_API_KEY 是否设置正确，以及搜索关键词是否合适。

**Q: 抓取某些网站失败？**
A: 部分网站有反爬机制，Serper 可能无法抓取其内容。可以尝试其他来源。

**Q: 如何调整搜索结果的条数？**
A: 在指令中说明需要的数量，如"搜索 20 条关于..."。

**Q: 能保存到其他目录吗？**
A: 可在指令中指定，如"把这个内容保存到我的 Downloads 文件夹"。

## 相关资源

- [Serper API 文档](https://serper.dev/docs)
- [Google Search Parameters](https://serper.dev/playground)
- [Claude Code Skills](https://claude.ai/code)

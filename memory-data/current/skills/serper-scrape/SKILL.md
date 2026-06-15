---
name: serper-scrape
description: Search the web with Serper and scrape result pages into Markdown. Use when the user asks to 搜索, 查找, 查资料, 找资料, 调研, search, look up, research, browse, scrape, 抓网页, 获取网页内容, 网页转 Markdown, URL 转 Markdown, 提取网页正文, or when researching GitHub repositories, README files, docs, API docs, project pages, release notes, blog posts, news, tutorials, or technical references from the web. Prefer this skill over generic web search when the user wants source material, page content, saved notes, or Markdown extraction.
---

# Serper Search & Scrape Skill

## Trigger Contract

Use this skill for:

- Web search where the user asks to collect, inspect, research, compare, summarize, or preserve source pages.
- GitHub/project research, including repository discovery, README extraction, release notes, issues, docs, API references, and tutorials.
- Any request that combines search/discovery with Markdown extraction or note saving.
- Any direct URL request where the expected output is page text, Markdown, cleaned article content, or an Obsidian-style note.

Do not use this skill for:

- Local files that are already downloaded; use `markitdown` when the task is file conversion.
- Browser UI testing, screenshots, clicking, login flows, or JavaScript-heavy interaction; use the Browser skill/tool.
- Pure factual questions where no source page needs to be preserved.

When uncertain between generic web search and this skill, choose this skill if the user says "查资料", "找资料", "调研", "GitHub", "文档", "资料整理", "抓取", "转 Markdown", or asks for source-backed notes.

通过 Serper API 进行网页搜索和内容抓取。使用前需设置 `SERPER_API_KEY` 环境变量。

> **安全警告**：永远不要在代码、配置或命令行参数中硬编码 API KEY。始终通过环境变量读取。

## 使用方式

优先使用 `scripts/` 目录下的辅助脚本进行 API 调用，而非直接写 curl 命令：

### 搜索
```bash
bash <skill_path>/scripts/serper-search.sh "<query>" [gl] [hl] [tbs] [num] [page]
```

### 抓取
```bash
bash <skill_path>/scripts/serper-scrape.sh "<url>" [includeMarkdown]
```

其中 `<skill_path>` 是此 skill 的安装目录。如不确定，可通过 `which serper-scrape` 或查询 Claude skills 目录定位。

---

## API 参考

### 搜索 (Search)

**Endpoint**: `https://google.serper.dev/search` (POST)

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `q` | string | 是 | 搜索关键词 |
| `gl` | string | 否 | 国家代码，默认 `us` |
| `hl` | string | 否 | 语言代码，默认 `en` |
| `tbs` | string | 否 | 时间范围筛选 |
| `num` | number | 否 | 返回结果数，默认 10，最大 100 |
| `page` | number | 否 | 页码，默认 1 |

**时间范围 (tbs)**: `qdr:h`(1小时) / `qdr:d`(24小时) / `qdr:w`(1周) / `qdr:m`(1个月) / `qdr:y`(1年)

**响应关键字段**:
- `searchParameters` - 请求参数回显
- `knowledgeGraph` - 知识图谱（如存在）
- `organic[]` - 自然搜索结果列表（title, link, snippet, position）
- `peopleAlsoAsk[]` - 相关问答
- `relatedSearches[]` - 相关搜索

### 抓取 (Scrape)

**Endpoint**: `https://scrape.serper.dev` (POST)

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `url` | string | 是 | 目标网页完整 URL（需含 `https://`） |
| `includeMarkdown` | boolean | 否 | 返回 markdown 格式，默认 `true` |

**响应关键字段**: `markdown`(页面 markdown 内容) / `text`(纯文本) / `metadata`(元数据)

---

## 组合工作流

**推荐流程**：先搜索获取链接 → 筛选最相关的 → 抓取详情页内容。

```bash
# 步骤 1: 搜索
bash scripts/serper-search.sh "Claude 4 Anthropic" "us" "en" "qdr:w" 5

# 步骤 2: 从 organic[].link 提取感兴趣的 URL

# 步骤 3: 抓取每个链接
bash scripts/serper-scrape.sh "https://example-article.com"
```

---

## 限制规则（必须遵守）

### 1. 抓取数量限制

**每次搜索最多抓取 5 个网页**。如搜索结果超过 5 条，只选择最相关的前 5 个。若用户明确要求更多，需告知限制并确认。

### 2. 内容保存规则

所有抓取的网页内容必须处理后保存到 Obsidian：

| 内容类型 | 保存目录 |
|---------|---------|
| 普通内容（新闻、观点、案例等） | `~/tars/Resources/Web-Search/` |
| 技术/工具类（官方文档、API、GitHub README、教程等） | `~/tars/Knowledge/` |

### 3. 内容处理规则

**必须保留**：案例和示例、核心观点、事实和数据、金句精华、引用链接、原文链接

**必须去除**：导航菜单/页脚、广告、图片链接（关键图表除外）、视频嵌入、社交按钮、评论区（有价值评论除外）、相关推荐、Cookie 弹窗

### 4. 保存文件格式

```markdown
---
title: {{页面标题}}
source: {{原始URL}}
date_scraped: {{抓取日期 YYYY-MM-DD}}
tags: [web-search, {{主题标签}}]
---

# {{页面标题}}

> 来源：[{{网站名称}}]({{原始URL}})

## 一句话总结
{{核心要点概括}}

## 关键内容
{{处理后的正文内容}}

## 金句/要点
- {{提取的金句或关键观点}}

## 引用链接
- [{{链接标题}}]({{URL}})
```

---

## 注意事项

- 确保 `SERPER_API_KEY` 已设置，否则脚本会报错
- 搜索时合理使用 `tbs` 缩小时间范围，提高结果相关性
- 抓取 URL 必须是完整路径（含 `https://`）
- 某些网站有反爬措施，抓取失败时告知用户
- 组合搜索+抓取会消耗多次 API 调用，注意配额

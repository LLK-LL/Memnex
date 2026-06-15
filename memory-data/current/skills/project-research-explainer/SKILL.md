---
name: project-research-explainer
description: >
  Use when the user asks to find, search, look up, inspect, evaluate, or
  explain a software project, open-source repository, GitHub repo, framework,
  library, tool, SDK, model project, or developer product. Prioritize GitHub
  as the primary source, verify official docs when needed, and answer in the
  fixed Chinese structure: 项目描述, 项目原理, 如何部署, 对我有什么用, plus
  参考链接.
---

# Project Research Explainer

## Overview

This skill standardizes project lookup and explanation work for software repositories and developer tools.
It ensures the answer is source-grounded, deployment-aware, and consistently formatted for the user.

## Trigger Conditions

Use this skill when the user says or implies any of the following:

- "在 GitHub 上找一下某个项目"
- "搜一下这个开源项目"
- "看看这个 repo 是干什么的"
- "帮我讲解一下这个项目"
- "这个项目怎么部署"
- "这个项目对我有什么用"
- Requests to compare multiple candidate repositories before explaining one

Do not use this skill for:

- Pure conceptual questions with no project lookup intent
- Local code review of the current workspace
- Non-software products unless the same repository-style workflow still applies

## Source Priority

1. Search GitHub first and identify the most likely target repository.
2. Prefer the official repository README, releases, tags, docs site, and package metadata.
3. Use the official project website or documentation as the second primary source when needed.
4. Expand to other sources only if GitHub and official docs are insufficient.
5. If there are multiple same-name projects, state which one was chosen and why.

## Workflow

### 1. Identify the target project

- Search GitHub first.
- If there are multiple matches, choose the repository with the strongest evidence:
  highest relevance, official homepage, star/activity level, matching description, and current maintenance.
- Mention disambiguation briefly when needed.

### 2. Verify the current facts

- Verify unstable facts from live sources:
  stars, recent activity, latest release, license wording, deployment steps, installation commands, supported platforms.
- Use exact dates when mentioning "latest", "recent", "today", or similar relative time concepts.

### 3. Extract the minimum useful facts

Collect and compress:

- What the project is
- What problem it solves
- How it works at a high level
- What stack or architecture it uses
- How to deploy or install it in a realistic environment
- Who should use it and who should not
- Risks, limits, maintenance burden, and license caveats when relevant

### 4. Answer in the fixed user format

Always use this section order:

- `项目名称`
- `项目描述`
- `项目原理`
- `如何部署`
- `对我有什么用`
- `参考链接`

The first four content sections are mandatory even if some parts are short.

### 5. Adapt the deployment guidance to the user

- If the user environment is unknown, provide the shortest practical local deployment path first.
- If the project is not worth deploying for the user, say so clearly.
- When deployment is heavy or optional, explain whether trying the hosted demo/docs is enough.

## Output Requirements

- Write the final answer in Chinese.
- Keep the structure stable and easy to scan.
- Use links to official sources.
- Do not only summarize features. Explain mechanism, deployment reality, and user value.
- When a fact is inferred rather than directly stated by the sources, make that clear.
- If no trustworthy repository is found, say that explicitly instead of guessing.

## Template

Use the fixed template in [references/template.md](references/template.md).

## Validation Checklist

Before answering, confirm:

- The repository identity is correct.
- Unstable facts were checked live.
- The response includes all required sections.
- Deployment steps are practical, not generic filler.
- "对我有什么用" is personalized to the user's likely scenario, not a generic sales pitch.

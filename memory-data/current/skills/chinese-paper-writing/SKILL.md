---
name: chinese-paper-writing
description: Chinese scientific paper, graduate thesis, and master's midterm defense writing workflow. Use when Codex needs to plan, draft, restructure, polish, or quality-check Chinese academic writing, including master's thesis midterm reports, research background, literature review, technical route, methodology, experiments, phased progress, future work, abstracts, contribution statements, figure/table narration, LaTeX thesis sections, and defense-slide content.
---

# Chinese Paper Writing

## Overview

Use this skill to turn research materials into rigorous Chinese academic writing for thesis reports and defense documents. It combines three patterns:

- Thesis workflow: Chinese graduate thesis/report structure, staged drafting, terminology consistency, and defense material preparation.
- Paper architecture: problem-driven scientific writing with clear claims, method logic, experiments, related work, and contribution framing.
- High-end narrative polish: concise abstract, strong motivation, evidence-calibrated claims, and figure/table storytelling.

## Load The Right Reference

Read only the reference needed for the current task:

| Task | Read |
|---|---|
| Plan or draft a master's midterm report | `references/midterm-report-workflow.md` |
| Structure research background, method, experiments, or contributions | `references/scientific-paper-architecture.md` |
| Polish Chinese academic style or remove AI-like phrasing | `references/chinese-academic-style.md` |
| Write abstract, motivation, contribution, figure/table narration, or PPT story | `references/story-and-figures.md` |
| Final review before submission or defense | `references/quality-check.md` |

## Default Workflow

1. Identify the artifact: midterm report, thesis chapter, paper section, abstract, slide outline, or full defense package.
2. Build a claim map before drafting:
   - research problem
   - why it matters
   - unresolved gap
   - proposed method or route
   - evidence already obtained
   - remaining plan and risks
3. Choose the closest report/paper structure from the references.
4. Draft in Chinese with stable terminology and evidence-calibrated claims.
5. Polish for concision, logical transitions, and academic register.
6. Run the final quality checklist before handing back the result.

## Writing Rules

- Prefer precise Chinese academic prose over literal translation from English.
- State concrete research objects, methods, datasets, metrics, figures, tables, and findings whenever available.
- Keep claims proportional to evidence. Use "表明", "说明", "初步验证" for midterm-stage evidence; reserve "证明", "显著优于", "实现突破" for fully supported results.
- Keep terminology stable. Do not alternate among synonyms for the same technical concept.
- Avoid empty evaluative phrases such as "具有重要意义", "提供了新思路", "取得了良好效果" unless followed by concrete evidence.
- Do not invent references, experiments, metrics, institutions, dates, or results.
- When source material is incomplete, write with explicit placeholders rather than hallucinating details.

## Midterm Report Shape

For a master's midterm report, prefer this order unless the user's template says otherwise:

1. 课题背景与研究意义
2. 国内外研究现状
3. 研究目标与主要内容
4. 技术路线与研究方法
5. 已完成工作与阶段性成果
6. 存在问题与解决思路
7. 后续研究计划与进度安排
8. 参考文献

## Source Lineage

This skill is a local synthesis inspired by:

- `kisisjrlly/BUAA-Thesis-Paper-Writing-Skills`: Chinese graduate thesis workflow and defense-material orientation.
- `YurainSoon/paper-writing-skill`: cohort-first scientific paper architecture and section-level drafting order.
- `SyntaxSmith/nature-writing-skill`: Chinese AI/ML researcher-oriented abstract, motivation, result, and figure storytelling craft.

Use the synthesis here as the operating procedure. Consult the original GitHub repositories only when the user explicitly asks for upstream details or installation of the original skills.

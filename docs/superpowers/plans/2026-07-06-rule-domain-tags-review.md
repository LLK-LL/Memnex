# Rule Domain Tags Review

Status: applied to `C:\Users\Administrator\.tam\memory.db` on 2026-07-07 after user approval.

Backup created before applying:

```text
C:\Users\Administrator\.tam\backups\memory.db.rule-domain-tags-20260707-002553.bak
```

## Confirmed Design

- Domain enum: `global`, `code`, `writing`, `research`, `memory`, `ops`, `design`.
- Each active rule may have multiple `domain:*` tags.
- Each active rule must have exactly one `primary_domain:*` tag.
- Default behavior after implementation: directly exclude ordinary contextual rules that do not match the detected query domain.
- Exceptions that must not be excluded by domain mismatch:
  - rules tagged `always_on`, `hard`, or `security-critical`
  - rules tagged `domain:global`
  - rules with explicit trigger matches
- If query domain confidence is low or no primary query domain is detected, fall back to the current rule ranking behavior.

## Proposed Active Rule Mapping

| Rule ID | Category | Primary Domain | Domain Tags | Existing Intent |
|---:|---|---|---|---|
| 5 | `memory_boundary` | `primary_domain:writing` | `domain:writing`, `domain:memory`, `domain:code` | Keep paper-writing knowledge out of general memory, while allowing reusable engineering failures into general memory. |
| 8 | `network_safety` | `primary_domain:ops` | `domain:ops`, `domain:code` | Protect active VPN/proxy/network access during connectivity work. |
| 11 | `project_research` | `primary_domain:research` | `domain:research`, `domain:code`, `domain:ops` | Prefer GitHub-first project lookup and deployment-oriented project explanation. |
| 12 | `implementation_efficiency` | `primary_domain:code` | `domain:code` | Reuse existing scripts/tools before creating new batch implementations. |
| 13 | `workspace_hygiene` | `primary_domain:ops` | `domain:ops`, `domain:code`, `domain:design` | Clean temporary workspace/cache artifacts created by the current task. |
| 16 | `output_format` | `primary_domain:ops` | `domain:ops`, `domain:design` | Return QR-code requests as terminal/URL output unless image output is explicitly requested. |
| 17 | `task_execution` | `primary_domain:global` | `domain:global` | Use a checklist skill for multi-task or multi-requirement requests. |
| 19 | `skill_routing` | `primary_domain:ops` | `domain:ops`, `domain:code` | Route Igor requests to the remote Codex workflow. |
| 20 | `skill_routing` | `primary_domain:memory` | `domain:memory`, `domain:code` | Route AGENTS.md optimization/rewrite/compression tasks to the relevant skill. |
| 23 | `output_compression` | `primary_domain:global` | `domain:global`, `domain:code`, `domain:ops`, `domain:memory` | Use `rtk` selectively for long compressible output. |
| 25 | `memory-architecture` | `primary_domain:memory` | `domain:memory` | Treat harness as explicit-write-only memory layer. |
| 26 | `template_governance` | `primary_domain:memory` | `domain:memory`, `domain:code`, `domain:ops` | Store durable skill/rule/preference/memory governance templates under the global templates directory. |
| 27 | `memory-architecture` | `primary_domain:memory` | `domain:memory` | Require explicit `project:<project-name>` tags on harness-layer records. |
| 28 | `iteration` | `primary_domain:memory` | `domain:memory` | Keep memory iteration on the layered RAG/preference/rule/routing chain. |
| 29 | `persona_iteration` | `primary_domain:memory` | `domain:memory` | Keep persona iteration separate and require confirmation before applying persona changes. |
| 30 | `iteration_output` | `primary_domain:memory` | `domain:memory`, `domain:writing` | Use the memory-iteration layered output template. |
| 31 | `skill_routing` | `primary_domain:design` | `domain:design`, `domain:writing` | Route banana slide/deck/page generation to banana + PowerPoint skills. |
| 32 | `skill-governance` | `primary_domain:memory` | `domain:memory`, `domain:code` | Allow limited local skill self-optimization for directly evidenced errors. |
| 33 | `system_writing_style` | `primary_domain:memory` | `domain:memory`, `domain:writing`, `domain:code` | Use memory-writing style for system-level files and memory records. |
| 34 | `memory_governance` | `primary_domain:writing` | `domain:writing`, `domain:research`, `domain:memory` | Interpret project knowledge-base wording in the Ti-Al paper workspace. |
| 37 | `tool-paths` | `primary_domain:code` | `domain:code`, `domain:ops` | Prefer the known local CodeGraph executable path. |
| 39 | `file_reading` | `primary_domain:ops` | `domain:ops`, `domain:writing`, `domain:research`, `domain:code`, `domain:memory` | Route complex local file/document conversion to markitdown when useful. |
| 41 | `security` | `primary_domain:global` | `domain:global`, `domain:code`, `domain:writing`, `domain:research`, `domain:ops`, `domain:memory`, `domain:design` | Redaction check before public upload/publish/push/sync. |
| 43 | `github-publishing` | `primary_domain:code` | `domain:code`, `domain:research`, `domain:ops` | Use the standard GitHub repository launch workflow for public repo content. |
| 44 | `skill_routing` | `primary_domain:ops` | `domain:ops`, `domain:code`, `domain:memory` | Route Windows command safety, large workspace search, memory audit, and encoding issues to the right skill. |
| 45 | `workspace_hygiene` | `primary_domain:global` | `domain:global`, `domain:code`, `domain:ops`, `domain:writing`, `domain:research`, `domain:design` | Put task cache files under `D:\CodexCache` and remove current-task cache afterward. |
| 47 | `output_format` | `primary_domain:writing` | `domain:writing`, `domain:research` | Return rewritten/polished/translated prose directly unless a code block is requested. |

## Review Notes

- `domain:global` is intentionally limited to broadly applicable execution rules and always-on safety rules.
- Rule 8 is not marked `domain:global` because it should be kept by `ops`/`code` domain detection or by explicit network trigger matching, not by every task.
- Rule 13 is not marked `domain:global` because the always-on cache rule 45 already covers the broad cache baseline.
- Rule 16 is intentionally not `domain:global`; explicit `qr` trigger matching should preserve it across domains.
- Rule 39 is broad but remains `primary_domain:ops` because it is a tool-routing/file-processing rule, with secondary domains for writing, research, code, and memory tasks.

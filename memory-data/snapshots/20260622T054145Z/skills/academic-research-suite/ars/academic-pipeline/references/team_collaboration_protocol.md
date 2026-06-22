# Team Collaboration Protocol

## Purpose

# REDACTED: sensitive-looking memory line

---

## Role Definitions

| Role | Pipeline Stages | Responsibilities |
|------|----------------|-----------------|
| Research Lead | Stage 1 (RESEARCH) | Defines RQ, manages literature search, approves synthesis, sets theoretical framework |
# REDACTED: sensitive-looking memory line
| Methods Specialist | Stage 1 (methodology), Stage 2 (methods section) | Ensures methodological rigor, validates statistical analysis, reviews data integrity |
| Review Coordinator | Stage 3/3' (REVIEW) | Manages simulated review process, distributes feedback, facilitates revision coaching |
| Integration Lead | All stages | Ensures consistency across stages, manages handoffs, resolves cross-stage conflicts |

### Role Assignment Rules

- One person may hold multiple roles (common in small teams)
# REDACTED: sensitive-looking memory line
- Integration Lead is recommended for teams of 3+
- Methods Specialist is strongly recommended for empirical papers
- All role assignments should be documented at pipeline intake

---

## Handoff Protocol

For each stage transition, the following handoff procedure applies:

### Stage 1 -> Stage 2 (Research -> Write)

| Item | Detail |
|------|--------|
| **Who hands off** | Research Lead |
# REDACTED: sensitive-looking memory line
| **Materials** | RQ Brief, Bibliography, Synthesis Report (conforming to Schemas 1-3 in `shared/handoff_schemas.md`) |
| **Approval needed** | Research Lead confirms synthesis is complete and RQ is finalized |
| **Handoff checklist** | All Material Passports (Schema 9) attached; Bibliography minimum source count met; Synthesis has 3+ themes |

### Stage 2 -> Stage 2.5 (Write -> Integrity)

| Item | Detail |
|------|--------|
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
| **Materials** | Paper Draft (conforming to Schema 4) |
# REDACTED: sensitive-looking memory line
| **Handoff checklist** | All sections complete; reference list formatted; word count within target range |

### Stage 2.5 -> Stage 3 (Integrity -> Review)

| Item | Detail |
|------|--------|
| **Who hands off** | Integration Lead |
| **Who receives** | Review Coordinator |
| **Materials** | Verified Paper Draft + Integrity Report (Schema 5) |
| **Approval needed** | Integrity verdict is PASS; any PASS_WITH_CONDITIONS items acknowledged |
| **Handoff checklist** | Integrity Report attached; all SERIOUS/MEDIUM issues resolved |

### Stage 3 -> Stage 4 (Review -> Revise)

| Item | Detail |
|------|--------|
| **Who hands off** | Review Coordinator |
# REDACTED: sensitive-looking memory line
| **Materials** | Review Report (Schema 6) + Revision Roadmap (Schema 7) |
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line

### Stage 4 -> Stage 3' (Revise -> Re-Review)

| Item | Detail |
|------|--------|
# REDACTED: sensitive-looking memory line
| **Who receives** | Review Coordinator |
| **Materials** | Revised Draft + Response to Reviewers (Schema 8) |
# REDACTED: sensitive-looking memory line
| **Handoff checklist** | Response to Reviewers covers every roadmap item; new references verified |

### Stage 4.5 -> Stage 5 (Final Integrity -> Finalize)

| Item | Detail |
|------|--------|
| **Who hands off** | Integration Lead |
# REDACTED: sensitive-looking memory line
| **Materials** | Final Verified Draft + Final Integrity Report |
| **Approval needed** | Integrity verdict PASS with zero issues |
| **Handoff checklist** | All previous integrity issues confirmed resolved; Material Passport updated to VERIFIED |

---

## Version Control

### Git Branching Strategy

```
main
  |-- paper/draft-v1          (Stage 2 output)
  |-- paper/post-integrity-v1 (Stage 2.5 output)
  |-- paper/post-review-v1    (Stage 4 output)
  |-- paper/final-v1          (Stage 5 output)
```

### Tagging Convention

| Tag | When | Example |
|-----|------|---------|
| `v0.1-draft` | After Stage 2 completion | First complete draft |
| `v0.2-post-integrity` | After Stage 2.5 PASS | Draft verified for integrity |
| `v0.3-post-review` | After Stage 4 completion | First revision complete |
| `v0.4-post-rereview` | After Stage 4' completion (if applicable) | Second revision complete |
| `v1.0-final` | After Stage 5 completion | Final manuscript |

### Rules

- Never overwrite; always create a new version
- All versions are preserved for audit trail
- Version labels must match the Material Passport `version_label` field (Schema 9 in `shared/handoff_schemas.md`)
# REDACTED: sensitive-looking memory line

---

## Conflict Resolution

# REDACTED: sensitive-looking memory line
|--------------|---------------------|-----------------|
# REDACTED: sensitive-looking memory line
| Methodological disagreements | Methods Specialist has final say | If unresolved: cite literature precedent |
| Scope disagreements | Research Lead has final say | If unresolved: team vote |
# REDACTED: sensitive-looking memory line
| Integrity findings disagreements | Integration Lead has final say | Cannot override SERIOUS findings |

### Disagreement Documentation

All disagreements must be documented in the revision tracking:

```markdown
## Disagreement Record

**Date**: [date]
**Stage**: [stage]
**Parties**: [who disagreed]
**Issue**: [what the disagreement was about]
**Resolution**: [how it was resolved]
# REDACTED: sensitive-looking memory line
**Rationale**: [why this decision was made]
```

---

## Communication Templates

### 1. Handoff Notification

```markdown
## Handoff: Stage [X] -> Stage [Y]

**From**: [Role] ([Name])
**To**: [Role] ([Name])
**Date**: [date]

**Materials Delivered**:
- [Material 1] (version: [version_label])
- [Material 2] (version: [version_label])

**Status Summary**:
[1-2 sentence summary of what was accomplished and any open items]

**Action Required**:
[What the receiving person needs to do next]

**Deadline**: [if applicable]
```

### 2. Review Request

```markdown
## Review Request: [Paper Title]

**From**: [Review Coordinator]
**To**: [Team / External Reviewer]
**Date**: [date]

**Paper Version**: [version_label]
**Word Count**: [N]
**Review Type**: [Internal simulated / External journal / Team peer review]

**Focus Areas**:
1. [specific area to focus on]
2. [specific area to focus on]

**Deadline**: [date]
**Return Format**: [Use Schema 6 format from shared/handoff_schemas.md]
```

### 3. Revision Assignment

```markdown
## Revision Assignment: [Paper Title]

**From**: [Review Coordinator]
# REDACTED: sensitive-looking memory line
**Date**: [date]

**Revision Round**: [N]
**Total Items**: [N] (must_fix: [N], should_fix: [N], consider: [N])

**Your Assignments**:
- [REV-001]: [brief description] 鈥?assigned to [name]
- [REV-003]: [brief description] 鈥?assigned to [name]

**Deadline**: [date]
**Coordination Notes**: [any dependencies between revision items]
```

---

## Workflow for Teams

### Small Team (2-3 people)

```
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
  - Receives revision items, runs Stage 4/4'
  - Runs Stage 5 (FINALIZE)

Person B (Methods Specialist + Review Coordinator):
  - Reviews Stage 1 methodology output
  - Reviews Stage 2 methods section
  - Manages Stage 3/3' review process
  - Handles specific methodology revision items

Handoff: via shared folder or git repo
Materials: conform to schemas in shared/handoff_schemas.md
```

### Large Team (4+ people)

```
Add Integration Lead role:
  - Monitors all stage transitions
  - Validates handoff completeness
  - Resolves cross-stage inconsistencies
  - Maintains pipeline state document (shared with all team members)
```

---

## Limitations

# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
- Real-time co-editing is not supported; use git or shared documents for synchronization
# REDACTED: sensitive-looking memory line
- The pipeline does not enforce team role permissions; discipline is maintained by convention

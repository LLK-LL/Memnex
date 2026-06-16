---
name: multi-requirement-checklist
description: Handle user requests that contain multiple distinct requirements by first creating a temporary Markdown checklist with one item per requirement and an explicit verification standard per item, then executing and verifying each item one by one, and deleting the checklist only after the whole task is fully completed. Use when the user gives several requirements, acceptance criteria, or sub-tasks in one message.
---

# Multi Requirement Checklist

## Overview

Use this skill when a single user request contains multiple distinct requirements that must all be tracked, executed, and verified carefully.

The core rule is:

1. Write a temporary Markdown checklist first.
2. List each requirement separately.
3. Write a completion or verification standard for each requirement.
4. Execute and verify each item one by one.
5. Delete the temporary Markdown file only after every item is fully completed and verified.

## Workflow

### Step 1: Normalize the Request

Before doing implementation work, rewrite the user's multi-part request into a clean internal checklist.

For each item, capture:

- the requirement,
- the intended output or change,
- the verification standard,
- the final status.

If two user sentences describe one combined requirement, keep them together.
If one sentence contains multiple independent asks, split them into separate checklist items.

### Step 2: Create the Temporary Markdown File

Create a temporary Markdown file inside the current workspace `work/` directory unless the user already requested another location.

The file should exist only for task execution and verification tracking. It is not a deliverable unless the user explicitly asks to keep it.

Use a compact structure like this:

```md
# Task Checklist

## Item 1
- Requirement:
- Verification:
- Status: pending

## Item 2
- Requirement:
- Verification:
- Status: pending
```

### Step 3: Execute One Item at a Time

Work through the checklist sequentially unless safe parallelism is clearly beneficial.

For each item:

1. Implement the requirement.
2. Run the relevant verification.
3. Update the checklist status mentally or in-file as completed only after verification passes.

Do not mark an item complete merely because the code or file was edited.

### Step 4: Verify Explicitly

Every checklist item needs a concrete verification standard.

Examples:

- code change -> relevant tests pass
- document change -> required sections or formatting confirmed
- config change -> expected value exists in the target file
- bug fix -> repro no longer fails and regression check passes

If verification is blocked, say so clearly and leave the item incomplete.

## Completion Rule

Delete the temporary Markdown checklist only when all of the following are true:

- every listed requirement has been addressed,
- every item has been verified or explicitly reported as blocked,
- the final response can summarize the completed work without needing the checklist file anymore.

If the task is not fully complete, keep the checklist file in place.

## Output Behavior

When reporting back to the user:

- summarize the requirements you tracked,
- state which ones were completed,
- state how they were verified,
- mention any blocked or partial items,
- mention that the temporary checklist was deleted if and only if the whole task finished.

Do not keep stale checklist files after successful completion.

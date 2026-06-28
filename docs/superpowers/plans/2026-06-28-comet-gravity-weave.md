# Comet Gravity Weave Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace comet influence straight lines with gravity-weave curve trails, make comet selection highlight normal graph relation lines, and add weak glow feedback for influenced systems.

**Architecture:** Keep the existing comet overlay data model and renderer entry points, but change rendering from `head -> influence` straight segments to influence-aware curve generation layered on top of `trailHistory/path`. Use a dedicated `selectedCometId` state so comet selection can reuse graph relation highlighting without pretending a comet is a normal node.

**Tech Stack:** Vanilla JS, Pixi Graphics rendering, existing local test harness in `tests/js/memory_galaxy_smoke.test.mjs`, browser verification with Playwright.

---

### Task 1: Add failing tests for comet curve behavior and selection state

**Files:**
- Modify: `C:\Users\Administrator\total-agent-memory\tests\js\memory_galaxy_smoke.test.mjs`

- [ ] Add a failing renderer test that asserts comet visuals no longer emit `lineTo` commands for `influences`, but do emit multiple `quadraticCurveTo` segments for the gravity-weave path.
- [ ] Add a failing viewer-state test that asserts clicking a comet stores a `selectedCometId` and clears node selection.
- [ ] Run: `node --test tests\js\memory_galaxy_smoke.test.mjs`
- [ ] Confirm the new assertions fail before implementation.

### Task 2: Add comet selection state and viewer selection plumbing

**Files:**
- Modify: `C:\Users\Administrator\total-agent-memory\src\tools\memory_graph_viewer_assets\memory-galaxy-view-state.js`
- Modify: `C:\Users\Administrator\total-agent-memory\src\tools\memory_graph_viewer_assets\viewer.js`

- [ ] Add `selectedCometId` to the shared view state.
- [ ] Clear `selectedCometId` anywhere the current code clears node/system/planet selection on blank/reset/breadcrumb transitions.
- [ ] Update comet click handlers so single-click selects the comet, renders the comet selection card, and leaves graph/node selection empty.
- [ ] Update the relations panel text so selected comets now show highlighted related graph edges instead of the current “overlays summarize active context” placeholder.

### Task 3: Replace comet influence straight lines with gravity-weave curves

**Files:**
- Modify: `C:\Users\Administrator\total-agent-memory\src\tools\memory_graph_viewer_assets\memory-galaxy-renderer.js`

- [ ] Remove direct `moveTo(head).lineTo(influence)` rendering from comet visuals.
- [ ] Add a helper that builds curve control points from the comet head, nearby trail segments, and the nearest/next influenced systems.
- [ ] Render two trail layers:
  - soft wide glow curve for history
  - brighter narrow core curve for recent/current path
- [ ] Keep the comet hit target unchanged.

### Task 4: Hook comet selection into relation highlighting and glow feedback

**Files:**
- Modify: `C:\Users\Administrator\total-agent-memory\src\tools\memory_graph_viewer_assets\memory-galaxy-renderer.js`
- Modify: `C:\Users\Administrator\total-agent-memory\src\tools\memory_graph_viewer_assets\viewer.js`

- [ ] In link rendering, treat a selected comet as highlighting links touching the comet’s influenced systems.
- [ ] In comet rendering, when `selectedCometId` matches, boost trail alpha/width and add weak glow rings for influenced systems.
- [ ] Keep ordinary node selection logic unchanged.

### Task 5: Verify tests and browser behavior

**Files:**
- Modify if needed: `C:\Users\Administrator\total-agent-memory\tests\js\memory_galaxy_smoke.test.mjs`

- [ ] Run: `node --test tests\js\memory_galaxy_smoke.test.mjs`
- [ ] Run: `node --test tests\js\memory_galaxy_browser_regression.test.mjs`
- [ ] Verify in browser that:
  - comet influence straight lines are gone
  - comet path is curved across multiple systems
  - clicking the comet highlights graph relation lines and weakly glows influenced systems


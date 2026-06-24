# Memory Galaxy Solar System Layout

## Purpose

This document defines the confirmed focused star-system layout for the memory visualization. It describes the view shown after a user clicks one galaxy system in the whole-galaxy overview.

## Core Idea

A focused system should behave like a solar system:

- the selected memory system is the central star
- major subcategories orbit as category stars
- important related memories orbit as planets
- usage records, context records, and derived memories orbit as moons
- sources, episodes, provenance, and old observations orbit as evidence bodies

The focused system must not collapse into one crowded ring.

## Internal Orbit Types

Each focused system uses nested orbit classes:

1. **Central Star**
   - the selected system center, such as `Skill System`, `Persona Core`, or `Rule Core`
   - visually largest node in the focused view

2. **Category Star Orbit**
   - major subcategories
   - examples for `Skill`: `debug`, `memory`, `research`, `browser`, `visual`, `planning`, `agent`, `workflow`

3. **Primary Planet Orbit**
   - strongest directly related memories
   - important memories can own local satellite systems

4. **Secondary Planet Orbit**
   - ordinary related memories
   - no local satellites by default unless selected

5. **Local Moon Orbits**
   - usage records
   - context records
   - derived memories
   - if a planet has many moons, create `moon orbit A`, `moon orbit B`, and more as needed

6. **Evidence Orbits**
   - sources
   - episodes
   - old observations
   - provenance records
   - if evidence nodes are dense, create multiple evidence tracks

## Nested Satellite Systems

Important planet nodes can own local satellite systems.

Example:

```text
Skill System
  -> memory galaxy planet
      -> moon orbit A: related usage/context records
      -> moon orbit B: additional derived records
      -> evidence orbit: source episodes and provenance
```

This is required so satellite-like nodes do not pile onto the main system orbit.

## Non-Overlap Rules

The focused solar-system view must avoid node overlap.

Implementation requirements:

1. Use small default node scale.
2. Allocate nodes into angular slots.
3. Maintain minimum spacing based on maximum node diameter for that orbit.
4. Create extra same-type orbits when an orbit is crowded.
5. Keep labels outside local node clusters.

Suggested focused-view default:

```text
nodeScale = 0.48
```

Useful inspection range:

```text
0.42 - 0.70
```

## Screen Fitting

The focused system must adapt to the available screen size.

Implementation requirements:

1. Compute bounds for all nested local orbits.
2. Include labels and local satellite systems in the bounds.
3. Scale the camera so the full focused system fits inside the canvas.
4. Hide low-priority labels until hover or zoom.
5. Keep the selected central system visually centered.

## Relationship Display

Relationships in focused solar-system view are read through:

- orbit class
- local parent-child placement
- focused relationship lines
- right-side relation explanation panel

Default edge behavior:

- center-to-category and center-to-planet links are visible but calm
- planet-to-moon/evidence links show when the planet is selected or hovered
- cross-orbit edges stay quiet unless relevant to selection

## Interaction

The focused solar-system view supports:

- slow local orbit animation
- individual node self-rotation / light movement
- click a planet to expand its satellite system
- hover a node to highlight direct local relations
- back action to return to the whole-galaxy overview
- node diameter control

## Confirmed Preview

The confirmed solar-system layout preview is:

```text
C:\Users\Administrator\Documents\Codex\2026-06-16\new-chat-3\outputs\memory-galaxy-solar-nested-preview.png
```

# Memory Galaxy Planet-Satellite Layout

## Purpose

This document defines the confirmed third-level focused layout for the memory visualization. It describes the view shown after a user clicks an important planet node inside a focused solar-system view.

## Core Idea

A selected planet represents an important memory node. It can own a local satellite system:

- the selected planet is the center
- strongest direct records orbit as direct moons
- derived context records orbit as derived moons
- sources, episodes, tests, observations, and provenance orbit as evidence belts
- external cross-system references sit on the outermost orbit

The view should make a single memory node's local context readable without showing every edge in the whole graph.

## Orbit Types

1. **Central Planet**
   - selected important memory node
   - visually largest body in this local view

2. **Direct Moon Orbit**
   - strongest directly related records
   - examples: implementation changes, user feedback, layout tests, export runs

3. **Derived Moon Orbit**
   - derived context records
   - secondary implementation details
   - related local memories

4. **Evidence Belt A**
   - source records
   - episodes
   - validation runs
   - provenance entries

5. **Evidence Belt B**
   - older observations
   - historical records
   - lower-priority evidence

6. **External Links Orbit**
   - cross-system references
   - related rules
   - related skills
   - weak links to other solar systems

## Micro-Satellite Systems

Important moon nodes may own a very small local micro-orbit.

Example:

```text
memory galaxy planet
  -> viewer.js change moon
      -> micro evidence orbit: smoke test, export run, HTTP check
```

This prevents important moon nodes from becoming unexplained single dots.

## Non-Overlap Rules

The planet-satellite view must avoid visual collisions.

Implementation requirements:

1. Use small default node scale.
2. Allocate each orbit into angular slots.
3. Split dense moon/evidence groups into multiple belts.
4. Keep labels outside orbit clusters.
5. Show only focused labels by default.

Suggested default:

```text
nodeScale = 0.50
```

Useful range:

```text
0.42 - 0.70
```

## Relationship Display

The planet-satellite view should not show all edges by default.

Relationship reading order:

1. Orbit position shows relation type and strength.
2. Selected relation path highlights the relevant chain.
3. Right-side relation panel explains the selected node.

Default edge behavior:

- central planet to direct moon links are calm but visible
- selected path is bright
- evidence links appear when a moon is selected or hovered
- external links stay faint unless selected

## Interaction

The planet-satellite view supports:

- click moon to reveal micro-satellite evidence
- hover node to highlight local direct relations
- click evidence to inspect source/provenance
- back action to return to the solar-system view
- node diameter control
- selected path display

## Screen Fitting

The local subsystem must fit inside the focus viewport.

Implementation requirements:

1. Compute bounds for planet, moon orbits, evidence belts, external links, and labels.
2. Scale the local camera to fit all visible local content.
3. Keep the central planet visually centered.
4. Hide low-priority labels until hover or zoom.

## Confirmed Preview

The confirmed planet-satellite layout preview is:

```text
C:\Users\Administrator\Documents\Codex\2026-06-16\new-chat-3\outputs\memory-galaxy-planet-satellite-preview.png
```

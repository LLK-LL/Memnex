# Memory Galaxy Final Visual Summary

## Goal

Build the memory visualization as a real galaxy-like system, not a dense graph. The default view should show the whole memory universe clearly, with no node overlap, visible orbital structure, and meaningful relationships that can be explored by focus interactions.

## Core Metaphor

- `Router` is the galactic core.
- Major memory systems are star systems orbiting the core.
- Important nodes are planets or category stars.
- Usage records, evidence, sources, events, and old observations are moons or outer evidence bodies.
- Relationship strength determines orbital distance.

## Global Galaxy Layout

Star systems should not all sit on one orbit. They are assigned to multiple Router-centered galactic layers:

1. **Inner control layer:** `Rule`, `Persona`
2. **Execution / behavior layer:** `Skill`, `Harness`, `Preference`
3. **Context layer:** `Project`, `Knowledge`
4. **History / evidence layer:** `Event`, `Source`
5. **Archive / low-confidence layer:** old or weakly related observations

Closer to `Router` means stronger relationship, higher priority, or more direct influence on agent behavior.

## Solar-System Layout

Each star system also has multiple internal orbits:

1. **Star / category orbit:** system center and major subcategories
2. **Planet orbit:** important directly related memories
3. **Moon orbit:** usage records, context records, derived memories
4. **Evidence orbit:** sources, episodes, old observations, provenance

If one orbit becomes crowded, the layout should create another same-type orbit instead of packing nodes together.

## Node Size

The default node diameter should be much smaller than the current implementation. Add a global `Node diameter` control:

- Suggested default scale: `0.50`
- Useful range: about `0.45` to `0.75`
- Larger values are optional for inspection, not the default

Node size still reflects semantic priority, but the whole scale is reduced so nodes do not cover each other.

Suggested priority order:

```text
Router > Persona > Skill > Harness > Rule > Preference > Project > Knowledge > Event > Source
```

## Relationship Reading

Relationships are shown in three layers:

1. **Spatial relation:** what a node orbits and which orbit layer it sits on.
2. **Focused lines:** hover/click reveals one-hop or two-hop explicit edges.
3. **Relation panel:** selected node shows readable relation explanations.

Default mode should avoid showing every edge at once.

Recommended relationship modes:

- **Structure:** mostly orbit/position, quiet edges
- **Focus:** selected node reveals direct and nearby relationships
- **Path:** select two nodes and show the shortest path between them

## Interaction

- Default view shows the whole galaxy.
- Clicking a star system centers and zooms into that system.
- Focused system view shows all internal orbits for that system.
- Clicking a node highlights related nodes and updates the relation panel.
- Nodes and systems can animate:
  - star systems slowly revolve around `Router`
  - planets/moons rotate around their local system center
  - individual nodes have subtle self-rotation / light movement

## Visual Requirements

- No node overlap in the default view.
- Every major galactic layer and internal orbit should be visible.
- Nodes should have 2.5D depth: glow, highlight, shadow, not flat solid dots.
- Labels should not sit on top of tiny nodes.
- Labels should use hover/focus/zoom rules and high-contrast plates.
- Background should remain deep-space themed without competing with nodes.

## Preview Assets

Current final preview images are in:

```text
C:\Users\Administrator\Documents\Codex\2026-06-16\new-chat-3\outputs\memory-galaxy-final-previews
```

Key previews:

- `01-overall-multilayer-galaxy.png`
- `02-skill-system.png`
- `03-persona-system.png`
- `04-rule-system.png`
- `05-harness-system.png`
- `06-source-event-system.png`

## Implementation Direction

The current live viewer should be upgraded from fixed centers and crowded orbit rings to a collision-free orbital slot layout:

1. Compute relationship score from `Router` to each star system.
2. Assign systems to Router-centered galactic layers by score.
3. Assign each node to a local system and local orbit class.
4. Allocate angular slots with minimum spacing.
5. Add new orbits when a class has too many nodes.
6. Add diameter scale control.
7. Add focus transition for clicking a star system.

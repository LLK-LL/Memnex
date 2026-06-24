# Memory Galaxy Comet Overlay Layout

## Purpose

This document defines the confirmed comet overlay design for the memory visualization. Comets appear in the whole-galaxy view as dynamic, transient influence paths.

## Core Idea

A comet represents active or recent information that affects multiple memory systems but is not yet a stable long-term node.

Examples:

- current active task
- recent memory update
- user feedback that may become a preference
- incident / bugfix chain
- research trajectory
- review or verification pass

Comets are not fixed star systems. They are dynamic overlays on top of the galactic layer.

## Visual Components

1. **Comet Head**
   - the active dynamic context itself
   - bright, directional, clickable
   - example: `Memory Galaxy Redesign`

2. **Comet Tail**
   - recent systems or memories the comet has influenced
   - fades over time
   - tail particles become dimmer with age

3. **Forward Trajectory**
   - faint dots showing likely next affected systems
   - lower confidence than the tail

4. **Influence Pull Lines**
   - lines from the comet head to affected solar systems
   - brighter and thicker means stronger influence

5. **Influence Halo**
   - affected systems glow according to influence strength
   - stronger influence means larger/brighter halo

## Influence Strength

Influence should be readable from distance and styling.

Rules:

- closer to comet head means stronger influence
- brighter pull line means stronger carried context
- thicker pull line means stronger carried context
- stronger halo means stronger affected system
- low influence systems remain faint

Example:

```text
Strong impact:
Skill, Harness, Preference

Medium impact:
Rule, Persona

Weak impact:
Knowledge, Source
```

## Data Meaning

A comet carries dynamic information:

```text
Comet = transient influence + active context + recent trajectory
```

Suggested comet fields:

```json
{
  "id": "comet:memory-galaxy-redesign:2026-06-24",
  "type": "comet",
  "comet_type": "active_task",
  "label": "Memory Galaxy Redesign",
  "started_at": "2026-06-24T10:00:00Z",
  "last_active_at": "2026-06-24T12:00:00Z",
  "decay": 0.82,
  "trajectory": ["preference", "skill", "harness", "rule"],
  "influenced_systems": [
    { "system": "skill", "weight": 0.92 },
    { "system": "harness", "weight": 0.84 },
    { "system": "preference", "weight": 0.78 }
  ]
}
```

## Interaction

Clicking a comet opens a comet payload panel.

Panel should show:

- comet type
- carried information
- affected systems
- influence strength
- trajectory
- status

Actions:

- **Pin:** keep comet visible temporarily
- **Stabilize:** convert it into a long-term memory node or preference/project memory
- **Dismiss:** allow it to decay and hide

## Display Rules

The galaxy view should not show too many comets.

Recommended defaults:

- show only `1-3` active comets
- hide low-decay comets
- fade old comet tails
- avoid comet labels unless selected or hovered
- keep comet overlay above orbit guides but below selected node labels

## Relationship With Other Layouts

Comets exist only at the galaxy overview layer.

They can point into:

- whole solar systems
- selected system centers
- specific high-impact nodes when focused

They should not replace the stable hierarchy:

```text
Galaxy -> Solar System -> Planet/Satellite System
```

Instead, they show temporary cross-system influence on top of that hierarchy.

## Confirmed Preview

The confirmed comet overlay preview is:

```text
C:\Users\Administrator\Documents\Codex\2026-06-16\new-chat-3\outputs\memory-galaxy-comet-overlay-preview.png
```

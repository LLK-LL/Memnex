# Memory Galaxy Galactic Layout

## Purpose

This document defines the confirmed whole-galaxy layout for the memory visualization. It describes the default overview screen shown before a user clicks into a single star system.

## Core Idea

The whole memory library is shown as a galaxy:

- `Router` is the galactic core.
- Major memory systems orbit around `Router`.
- Systems are not placed on one shared orbit.
- Systems are assigned to multiple galactic layers according to relationship strength, priority, and behavioral influence.
- Every visible system is drawn as a miniature solar system, not a single dot.

## Galactic Layers

Relationship strength controls distance from `Router`.

1. **Layer 1: Control**
   - `Rule`
   - `Persona`
   - Closest to the core because these directly shape agent behavior.

2. **Layer 2: Execution / Behavior**
   - `Skill`
   - `Harness`
   - `Preference`
   - These determine how the agent acts, executes, tests, and follows user preferences.

3. **Layer 3: Context**
   - `Project`
   - `Knowledge`
   - These provide working context and domain memory.

4. **Layer 4: History / Evidence**
   - `Event`
   - `Source`
   - These are supporting history, provenance, and evidence.

5. **Layer 5: Archive / Low Confidence**
   - old observations
   - weakly related records
   - low-confidence or low-priority memories

## System Placement

Each star system has:

- a fixed galactic layer
- an angular slot on that layer
- a minimum safe distance from neighboring systems
- an external label placed outside its mini system

The layout must avoid system overlap. If a layer becomes crowded, the renderer should add another nearby layer band rather than compressing systems into each other.

## Mini Solar System Representation

In the whole-galaxy view, each major system should still look like a small solar system:

- center star
- tiny internal planet orbit
- tiny moon orbit
- tiny evidence/source orbit

This makes each system recognizable without requiring the user to zoom in.

## Screen Fitting

The whole galaxy must fit inside the available canvas.

Implementation requirements:

1. Compute bounds for all system orbits and labels.
2. Scale and pan the camera so the full galaxy fits inside the viewport.
3. Keep labels inside the safe screen area.
4. Use small default node scale in overview mode.

Suggested default:

```text
nodeScale = 0.48
```

## Relationship Display

Default whole-galaxy mode should emphasize structure over edge density.

- Spatial layer shows broad relationship strength.
- Quiet lines from `Router` to systems show global influence.
- Cross-system edges are hidden or very faint by default.
- Hovering a system highlights its direct global relationships.
- Clicking a system transitions into the solar-system focused view.

## Interaction

The whole-galaxy view supports:

- slow system revolution around `Router`
- hover highlight for a system
- click-to-focus transition
- global node diameter control
- structure / focus / path relationship modes

## Confirmed Preview

The confirmed galactic layout preview is:

```text
C:\Users\Administrator\Documents\Codex\2026-06-16\new-chat-3\outputs\memory-galaxy-galactic-responsive-preview.png
```

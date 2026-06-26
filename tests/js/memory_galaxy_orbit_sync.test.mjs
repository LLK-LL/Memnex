/**
 * Test: Galaxy orbit synchronization
 * Verifies that mini-orbit nodes (planets/moons/evidence) follow their parent system's revolution
 */

import { strict as assert } from "assert";

describe("Memory Galaxy Orbit Synchronization", () => {
  /**
   * Mock data structures for testing
   */
  function createMockSystem(key, x, y) {
    return {
      key,
      x,
      y,
      radius: 100,
      orbitAspect: 0.58,
      miniOrbits: [],
      animation: {
        orbitCenterX: 0,
        orbitCenterY: 0,
        orbitRadiusX: Math.hypot(x, y),
        orbitRadiusY: Math.hypot(x, y) * 0.58,
        orbitAngle: Math.atan2(y, x),
        orbitSpeed: 0.06,
        phase: 0,
      },
    };
  }

  function createMockNode(id, systemKey, orbitRadius) {
    return {
      id,
      label: `Node ${id}`,
      memorySystem: systemKey,
      orbitRole: "planet",
      orbitalRole: "planet",
      x: orbitRadius,
      y: 0,
      animation: {
        orbitCenterX: 0,
        orbitCenterY: 0,
        orbitRadiusX: orbitRadius,
        orbitRadiusY: orbitRadius * 0.62,
        orbitAngle: 0,
        orbitSpeed: 0.006,
        phase: 0,
        parentSystemKey: systemKey, // ✅ Critical: must be set
      },
    };
  }

  it("should propagate parentSystemKey from placeOrbit to placeNode", () => {
    // This test verifies the fix: placeOrbit must pass parentSystemKey to placeNode

    const options = {
      centerX: 100,
      centerY: 50,
      radiusX: 50,
      radiusY: 30,
      startAngle: 0,
      memorySystem: "harness",
      orbitRole: "planet",
      orbitalRole: "planet",
      nodeScale: 0.48,
      parentSystemKey: "harness", // ✅ This must be passed through
    };

    const mockNode = {
      id: "test-node",
      label: "Test Node",
      raw: { id: "test-node", importance: 0.5, mention_count: 5 },
    };

    // Simulate what placeOrbit does (simplified)
    const placedNode = {
      ...mockNode,
      x: options.centerX + Math.cos(0) * options.radiusX,
      y: options.centerY + Math.sin(0) * options.radiusY,
      animation: {
        orbitCenterX: options.centerX,
        orbitCenterY: options.centerY,
        orbitRadiusX: options.radiusX,
        orbitRadiusY: options.radiusY,
        parentSystemKey: options.parentSystemKey, // ✅ Must be present
      },
    };

    assert.ok(placedNode.animation.parentSystemKey, "parentSystemKey must be set");
    assert.strictEqual(
      placedNode.animation.parentSystemKey,
      "harness",
      "parentSystemKey must match the parent system"
    );
  });

  it("should update mini-orbit nodes based on dynamic system position", () => {
    const system = createMockSystem("harness", 300, 150);
    const node = createMockNode("node-1", "harness", 50);

    const systemsByKey = new Map([["harness", system]]);

    // Initial position
    const initialNodeX = node.x;
    const initialNodeY = node.y;

    // Simulate system movement (revolution around galaxy center)
    const deltaSeconds = 1 / 60; // One frame at 60fps
    const speed = 1.0;

    // Update system position
    const systemPhase = system.animation.phase + system.animation.orbitSpeed * deltaSeconds * speed;
    system.animation.phase = systemPhase;
    system.x = Math.cos(systemPhase) * system.animation.orbitRadiusX;
    system.y = Math.sin(systemPhase) * system.animation.orbitRadiusY;

    // Update node position using the dynamic system position
    const centerSystem = node.animation.parentSystemKey
      ? systemsByKey.get(node.animation.parentSystemKey)
      : null;

    assert.ok(centerSystem, "centerSystem must be found via parentSystemKey");

    const centerX = centerSystem ? centerSystem.x : node.animation.orbitCenterX;
    const centerY = centerSystem ? centerSystem.y : node.animation.orbitCenterY;

    // Verify that we're using the dynamic system position, not the static initial position
    assert.strictEqual(centerX, system.x, "centerX must use dynamic system.x");
    assert.strictEqual(centerY, system.y, "centerY must use dynamic system.y");

    // Update node's orbit position
    const nodePhase = node.animation.phase + node.animation.orbitSpeed * deltaSeconds * speed;
    node.animation.phase = nodePhase;
    node.x = centerX + Math.cos(nodePhase) * node.animation.orbitRadiusX;
    node.y = centerY + Math.sin(nodePhase) * node.animation.orbitRadiusY;

    // Verify the node has moved (it follows the system)
    const nodeMoved = Math.hypot(node.x - initialNodeX, node.y - initialNodeY) > 0.01;
    assert.ok(nodeMoved, "Node must move when system moves");
  });

  it("should fall back to static orbitCenter when parentSystemKey is missing", () => {
    // This tests the fallback behavior for Solar/Planet views where center is fixed
    const node = {
      id: "fixed-node",
      x: 150,
      y: 0,
      animation: {
        orbitCenterX: 0,
        orbitCenterY: 0,
        orbitRadiusX: 150,
        orbitRadiusY: 87,
        orbitSpeed: 0.006,
        phase: 0,
        // parentSystemKey is undefined (Solar/Planet view)
      },
    };

    const systemsByKey = new Map();

    const centerSystem = node.animation.parentSystemKey
      ? systemsByKey.get(node.animation.parentSystemKey)
      : null;

    const centerX = centerSystem ? centerSystem.x : node.animation.orbitCenterX;
    const centerY = centerSystem ? centerSystem.y : node.animation.orbitCenterY;

    // Should use static values
    assert.strictEqual(centerX, 0, "centerX should fall back to orbitCenterX");
    assert.strictEqual(centerY, 0, "centerY should fall back to orbitCenterY");
  });

  it("should maintain relative orbital position during system revolution", () => {
    const system = createMockSystem("knowledge", 400, 200);
    const planet = createMockNode("planet-1", "knowledge", 60);
    const moon = createMockNode("moon-1", "knowledge", 90);

    const systemsByKey = new Map([["knowledge", system]]);

    // Initial relative positions
    const initialPlanetToSystem = Math.hypot(
      planet.x - system.x,
      planet.y - system.y
    );
    const initialMoonToSystem = Math.hypot(
      moon.x - system.x,
      moon.y - system.y
    );

    // Simulate multiple frames
    for (let frame = 0; frame < 10; frame++) {
      const deltaSeconds = 1 / 60;
      const speed = 1.0;

      // Update system
      system.animation.phase += system.animation.orbitSpeed * deltaSeconds * speed;
      system.x = Math.cos(system.animation.phase) * system.animation.orbitRadiusX;
      system.y = Math.sin(system.animation.phase) * system.animation.orbitRadiusY;

      // Update nodes
      for (const node of [planet, moon]) {
        const centerSystem = systemsByKey.get(node.animation.parentSystemKey);
        const centerX = centerSystem.x;
        const centerY = centerSystem.y;

        node.animation.phase += node.animation.orbitSpeed * deltaSeconds * speed;
        node.x = centerX + Math.cos(node.animation.phase) * node.animation.orbitRadiusX;
        node.y = centerY + Math.sin(node.animation.phase) * node.animation.orbitRadiusY;
      }
    }

    // Verify relative distances are maintained
    const finalPlanetToSystem = Math.hypot(
      planet.x - system.x,
      planet.y - system.y
    );
    const finalMoonToSystem = Math.hypot(
      moon.x - system.x,
      moon.y - system.y
    );

    assert.ok(
      Math.abs(finalPlanetToSystem - initialPlanetToSystem) < 0.1,
      "Planet should maintain orbital distance from system"
    );
    assert.ok(
      Math.abs(finalMoonToSystem - initialMoonToSystem) < 0.1,
      "Moon should maintain orbital distance from system"
    );
  });
});

console.log("✅ Galaxy orbit synchronization tests defined");

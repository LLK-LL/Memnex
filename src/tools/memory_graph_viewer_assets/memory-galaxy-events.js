export function createMemoryGalaxyEvent(type, payload = {}) {
  return {
    type,
    node_id: payload.node_id || null,
    gesture: payload.gesture || null,
    view: payload.view || "unknown",
    timestamp: payload.timestamp || new Date().toISOString(),
    context: payload.context || {},
  };
}

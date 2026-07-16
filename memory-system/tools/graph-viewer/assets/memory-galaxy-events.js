const allowedEventTypes = new Set([
  "system:selected",
  "node:selected",
  "node:hovered",
  "node:drag-started",
  "node:dragged",
  "node:drag-ended",
  "node:expanded",
  "view:filtered",
  "view:focus-cleared",
  "agent:suggestion-staged",
]);

export function createMemoryGalaxyEvent(type, payload = {}) {
  if (!allowedEventTypes.has(type)) {
    throw new Error(`Unsupported memory galaxy event: ${type}`);
  }
  return {
    type,
    node_id: payload.node_id ? String(payload.node_id) : null,
    gesture: payload.gesture || null,
    view: payload.view || "unknown",
    timestamp: payload.timestamp || new Date().toISOString(),
    context: payload.context || {},
  };
}

export function createInteractionLog(limit = 80) {
  const events = [];
  return {
    push(event) {
      events.push(event);
      while (events.length > limit) events.shift();
      return event;
    },
    all() {
      return [...events];
    },
    clear() {
      events.length = 0;
    },
  };
}

export function suggestAgentPrompt(event, nodeData = {}) {
  if (!event || !event.node_id || !event.type.startsWith("node:")) return null;
  const label = nodeData.label || nodeData.name || event.node_id;
  if (event.type === "node:selected" || event.type === "node:drag-ended") {
    return {
      kind: "source-provenance",
      message: `要不要查看「${label}」这个记忆节点的内容来源？`,
      action: "inspect_source",
      node_id: event.node_id,
    };
  }
  if (event.type === "node:expanded") {
    return {
      kind: "relationship-summary",
      message: `我可以帮你总结「${label}」周围的强关系。`,
      action: "summarize_neighbors",
      node_id: event.node_id,
    };
  }
  return null;
}

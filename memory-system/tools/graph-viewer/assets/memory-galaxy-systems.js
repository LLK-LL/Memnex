export const systemOrder = [
  "router",
  "rule",
  "persona",
  "skill",
  "harness",
  "preference",
  "project",
  "knowledge",
  "event",
  "source",
  "archive",
];

export const systemColors = {
  router: "#60a5fa",
  rule: "#facc15",
  persona: "#a78bfa",
  skill: "#22d3ee",
  harness: "#34d399",
  preference: "#f472b6",
  project: "#2dd4bf",
  knowledge: "#7dd3fc",
  event: "#38bdf8",
  source: "#94a3b8",
  archive: "#64748b",
};

export function systemColor(system) {
  return systemColors[system] || systemColors.knowledge;
}

export function systemLayerForKey(system) {
  if (["rule", "persona"].includes(system)) return "control";
  if (["skill", "harness", "preference"].includes(system)) return "execution";
  if (["project", "knowledge"].includes(system)) return "context";
  if (["event", "source"].includes(system)) return "evidence";
  if (system === "router") return "core";
  return "archive";
}

export function memorySystemForData(data = {}) {
  const text = [
    data.id,
    data.label,
    data.name,
    data.type,
    data.content,
    data.source,
    data.project,
    ...(Array.isArray(data.knowledge)
      ? data.knowledge
      : []).map(item => `${item.type || ""} ${item.project || ""} ${item.summary || ""}`),
  ].join(" ").toLowerCase();

  if (/\b(router|routing|route|dispatch|orchestrat)/.test(text)) return "router";
  if (data.type === "rule" || /\b(rule|policy|must|never|required|guardrail)\b/.test(text)) return "rule";
  if (/\b(persona|personality|identity|tone|style|voice|character)\b/.test(text)) return "persona";
  if (data.type === "capability" || /\b(skill|capability|trigger|workflow|procedure)\b/.test(text)) return "skill";
  if (/\b(harness|eval|evaluation|pytest|test runner|smoke test|verification|playwright|benchmark)\b/.test(text)) return "harness";
  if (/\b(preference|prefers|user wants|style preference|interaction preference)\b/.test(text)) return "preference";
  if (data.type === "project") return "project";
  if (["event", "episode", "session", "observation"].includes(data.type) || data.galaxy_layer === "episode") return "event";
  if (["source", "citation", "provenance"].includes(data.type) || /\b(source|provenance|evidence|citation|origin)\b/.test(text) || data.galaxy_layer === "external") return "source";
  return "knowledge";
}

export function orbitRoleForData(data = {}) {
  if (data.type === "event" || data.galaxy_layer === "episode" || data.galaxy_layer === "external") return "evidence";
  if (Number(data.importance || 0) >= 0.9 || Number(data.mention_count || 0) >= 10) return "planet";
  return "moon";
}

export function priorityRadiusForData(data = {}, options = {}) {
  const system = memorySystemForData(data);
  const baseDiameter = {
    router: 54,
    persona: 42,
    skill: 40,
    harness: 36,
    rule: 34,
    preference: 28,
    project: 26,
    knowledge: 20,
    event: 14,
    source: 10,
    archive: 8,
  }[system] || 20;
  const diameter = baseDiameter
    + Number(data.importance || 0) * 2.5
    + Number(data.activity || 0) * 3
    + Math.log1p(Number(data.mention_count || 0)) * 1.2;
  const scale = Math.max(0.42, Math.min(0.7, Number(options.scale || 0.48)));
  return Math.max(3, Math.min(28, (diameter / 2) * scale));
}

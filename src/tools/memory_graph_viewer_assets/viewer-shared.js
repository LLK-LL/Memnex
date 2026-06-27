export function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

export function timelineCutoffFromPercent(timeline, percent) {
  const value = Number(percent);
  if (value >= 100 || !timeline?.start || !timeline?.end) return null;
  const start = Date.parse(timeline.start);
  const end = Date.parse(timeline.end);
  if (!Number.isFinite(start) || !Number.isFinite(end) || end <= start) return null;
  return new Date(start + ((end - start) * value / 100)).toISOString();
}

export function renderPromptText(prompt) {
  return prompt?.message || "";
}

export function copyableInline(label, value) {
  return `
    <div class="copyable-inline">
      <span>${escapeHtml(label)}</span>
      <code>${escapeHtml(value)}</code>
    </div>
  `;
}

export function renderMetricGrid(items) {
  return `
    <div class="metric-grid">
      ${items.map(item => `
        <div class="metric-cell">
          <span class="metric-label">${escapeHtml(item.label)}</span>
          <span class="metric-value">${escapeHtml(item.value)}</span>
        </div>
      `).join("")}
    </div>
  `;
}

export function renderInspectorList(items) {
  if (!items?.length) return '<div class="empty-state">No items in the current scope.</div>';
  return `
    <div class="summary-list">
      ${items.map((item, index) => `
        <div class="summary-row">
          <span>${escapeHtml(index + 1)}</span>
          <strong>${escapeHtml(item.label)}</strong>
          <span>${escapeHtml(item.value)}</span>
        </div>
      `).join("")}
    </div>
  `;
}

export function renderTag(label) {
  return `<span class="pill">${escapeHtml(label)}</span>`;
}

export function formatNodeDetails(data) {
  const relationCounts = data.relation_counts || {};
  const relations = Object.entries(relationCounts)
    .filter(([key]) => key !== "total")
    .sort((a, b) => b[1] - a[1])
    .map(([key, count]) => `<span class="pill">${escapeHtml(key)} ${escapeHtml(count)}</span>`)
    .join("");
  const memories = (data.knowledge || []).map(item => `
    <div class="memory">
      <strong>#${escapeHtml(item.id)} ${escapeHtml(item.type)} | ${escapeHtml(item.project)}</strong>
      <div class="meta">${escapeHtml(item.role)} | strength ${escapeHtml(item.strength)}</div>
      <div>${escapeHtml(item.summary)}</div>
    </div>
  `).join("");
  const provenance = data.provenance || {};
  return `
    <div class="node-title">${escapeHtml(data.label)}</div>
    <div class="meta">
      ${escapeHtml(data.type)} | ${escapeHtml(data.galaxy_layer || "external")}
      | mentions ${escapeHtml(data.mention_count)}
      | importance ${escapeHtml(data.importance)}
    </div>
    <div>${escapeHtml(data.content || "No node content.")}</div>
    <h2>Relations</h2>
    <div>${relations || '<span class="meta">No relation counts.</span>'}</div>
    <h2>Content Source</h2>
    <div class="meta">
      source ${escapeHtml(provenance.source || data.source || "unknown")}
      | first seen ${escapeHtml(provenance.first_seen_at || "unknown")}
      | last seen ${escapeHtml(provenance.last_seen_at || data.last_seen_at || "unknown")}
    </div>
    <h2>Linked Memories</h2>
    ${memories || "<p>No linked memories in exported sample.</p>"}
  `;
}

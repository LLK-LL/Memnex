let cy;
let originalElements = { nodes: [], edges: [] };
let activeTypes = new Set();

const colors = {
  project: "#2563eb",
  concept: "#059669",
  entity: "#d97706",
  memory: "#7c3aed",
  rule: "#dc2626",
  default: "#64748b",
};

function nodeColor(type) {
  return colors[type] || colors.default;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

async function init() {
  const response = await fetch("graph.json");
  const graph = await response.json();
  originalElements = graph.elements;
  activeTypes = new Set(Object.keys(graph.metadata.type_counts));
  renderTypeFilters(graph.metadata.type_counts);
  renderStats(graph.metadata);
  createGraph();
  bindControls();
  applyFilters();
}

function renderStats(metadata) {
  document.getElementById("stats").textContent =
    `${metadata.node_count} nodes, ${metadata.edge_count} edges`;
}

function renderTypeFilters(typeCounts) {
  const root = document.getElementById("typeFilters");
  root.innerHTML = "";
  Object.entries(typeCounts)
    .sort((a, b) => b[1] - a[1])
    .forEach(([type, count]) => {
      const label = document.createElement("label");
      label.innerHTML = `
        <input type="checkbox" data-type="${escapeHtml(type)}" checked>
        <span><span class="pill">${escapeHtml(type)}</span>${count}</span>
      `;
      root.appendChild(label);
    });
}

function createGraph() {
  cy = cytoscape({
    container: document.getElementById("cy"),
    elements: [],
    style: [
      {
        selector: "node",
        style: {
          "background-color": ele => nodeColor(ele.data("type")),
          label: "data(label)",
          "font-size": 10,
          color: "#16202a",
          "text-outline-width": 2,
          "text-outline-color": "#ffffff",
          width: ele => Math.min(48, 14 + ele.data("mention_count")),
          height: ele => Math.min(48, 14 + ele.data("mention_count")),
        },
      },
      {
        selector: "edge",
        style: {
          width: ele => Math.max(1, Math.min(8, ele.data("weight"))),
          "line-color": "#a8b3c1",
          "target-arrow-color": "#a8b3c1",
          "target-arrow-shape": "triangle",
          "curve-style": "bezier",
          opacity: 0.55,
        },
      },
      {
        selector: ".faded",
        style: { opacity: 0.08 },
      },
      {
        selector: ".focused",
        style: {
          "border-width": 3,
          "border-color": "#111827",
          opacity: 1,
        },
      },
    ],
  });

  cy.on("tap", "node", event => {
    const node = event.target;
    showDetails(node.data());
    focusNeighborhood(node);
  });
}

function bindControls() {
  document.getElementById("search").addEventListener("input", applyFilters);
  document.getElementById("weightFilter").addEventListener("input", event => {
    document.getElementById("weightValue").textContent = event.target.value;
    applyFilters();
  });
  document.getElementById("typeFilters").addEventListener("change", event => {
    if (!event.target.matches("input[type='checkbox']")) return;
    const type = event.target.dataset.type;
    if (event.target.checked) activeTypes.add(type);
    else activeTypes.delete(type);
    applyFilters();
  });
  document.getElementById("layoutCose").addEventListener("click", () => runLayout("cose"));
  document.getElementById("layoutCircle").addEventListener("click", () => runLayout("circle"));
  document.getElementById("fit").addEventListener("click", () => cy.fit(undefined, 40));
  document.getElementById("clearFocus").addEventListener("click", clearFocus);
}

function applyFilters() {
  const query = document.getElementById("search").value.trim().toLowerCase();
  const minWeight = Number(document.getElementById("weightFilter").value);
  const nodes = originalElements.nodes.filter(node => {
    const data = node.data;
    if (!activeTypes.has(data.type)) return false;
    if (!query) return true;
    return `${data.label} ${data.type} ${data.content}`.toLowerCase().includes(query);
  });
  const nodeIds = new Set(nodes.map(node => node.data.id));
  const edges = originalElements.edges.filter(edge =>
    edge.data.weight >= minWeight &&
    nodeIds.has(edge.data.source) &&
    nodeIds.has(edge.data.target)
  );
  cy.elements().remove();
  cy.add([...nodes, ...edges]);
  runLayout(cy.nodes().length > 250 ? "grid" : "cose");
}

function runLayout(name) {
  const options = name === "cose"
    ? { name, animate: false, fit: true, padding: 40, nodeRepulsion: 9000, idealEdgeLength: 90 }
    : { name, animate: false, fit: true, padding: 40 };
  cy.layout(options).run();
}

function focusNeighborhood(node) {
  cy.elements().addClass("faded");
  node.closedNeighborhood().removeClass("faded").addClass("focused");
}

function clearFocus() {
  cy.elements().removeClass("faded focused");
  document.getElementById("details").textContent = "Select a node to inspect linked memories.";
}

function showDetails(data) {
  const memories = (data.knowledge || []).map(item => `
    <div class="memory">
      <strong>#${escapeHtml(item.id)} ${escapeHtml(item.type)} · ${escapeHtml(item.project)}</strong>
      <div class="meta">${escapeHtml(item.role)} · strength ${escapeHtml(item.strength)}</div>
      <div>${escapeHtml(item.summary)}</div>
    </div>
  `).join("");
  document.getElementById("details").innerHTML = `
    <div class="node-title">${escapeHtml(data.label)}</div>
    <div class="meta">${escapeHtml(data.type)} · mentions ${escapeHtml(data.mention_count)} · importance ${escapeHtml(data.importance)}</div>
    <div>${escapeHtml(data.content || "No node content.")}</div>
    <h2>Linked Memories</h2>
    ${memories || "<p>No linked memories in exported sample.</p>"}
  `;
}

init().catch(error => {
  document.getElementById("stats").textContent = "Failed to load graph.json";
  document.getElementById("details").textContent = String(error);
});

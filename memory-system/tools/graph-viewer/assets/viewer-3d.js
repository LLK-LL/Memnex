import * as THREE from "https://unpkg.com/three@0.165.0/build/three.module.min.js";
import {
  buildFocusGalaxy,
  buildSphereGalaxyLayout,
  convertGraphToGalaxy,
  filterGalaxy,
} from "./memory-galaxy-core.js";
import {
  createInteractionLog,
  createMemoryGalaxyEvent,
  suggestAgentPrompt,
} from "./memory-galaxy-events.js";
import {
  escapeHtml,
  formatNodeDetails,
  renderPromptText,
  timelineCutoffFromPercent,
} from "./viewer-shared.js";

const viewName = "3d-sphere";
const focusLimit = 650;
const interactionLog = createInteractionLog();

let raycaster;
let pointer;
let scene;
let camera;
let renderer;
let root;
let container;
let originalGraph = { nodes: [], links: [], metadata: {} };
let visibleGraph = { nodes: [], links: [], metadata: {} };
let activeTypes = new Set();
let activeLayers = new Set(["core", "active", "knowledge", "episode", "external"]);
let selectedNodeId = null;
let selectedNode = null;
let renderTimer = null;
let expansionViewNodeId = null;
let isDraggingView = false;
let pointerMoved = false;
let lastPointer = { x: 0, y: 0 };
let rotation = { x: -0.28, y: 0.42 };

function loadEmbeddedGraph() {
  const el = document.getElementById("graph-data");
  if (!el?.textContent) return null;
  return JSON.parse(el.textContent);
}

async function loadGraph() {
  const backendGraph = await loadBackendGraph();
  if (backendGraph) return backendGraph;
  const embedded = loadEmbeddedGraph();
  if (embedded) return embedded;
  const response = await fetch("graph.json");
  if (!response.ok) throw new Error(`graph.json load failed: ${response.status}`);
  return response.json();
}

async function loadBackendGraph() {
  try {
    const response = await fetch("/api/graph", { cache: "no-store" });
    if (!response.ok || !response.headers.get("content-type")?.includes("application/json")) return null;
    const graph = await response.json();
    return graph?.elements?.nodes && graph?.elements?.edges ? graph : null;
  } catch {
    return null;
  }
}

async function init() {
  raycaster = new THREE.Raycaster();
  pointer = new THREE.Vector2();
  const graph = await loadGraph();
  originalGraph = convertGraphToGalaxy(graph);
  activeTypes = new Set(Object.keys(graph.metadata.type_counts));
  renderTypeFilters(graph.metadata.type_counts);
  renderLayerFilters();
  renderStats(graph.metadata);
  createScene();
  bindControls();
  applyFilters();
  animate();
}

function createScene() {
  container = document.getElementById("graph3d");
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(52, container.clientWidth / container.clientHeight, 1, 2500);
  camera.position.set(0, 0, 760);
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setSize(container.clientWidth, container.clientHeight);
  container.appendChild(renderer.domElement);
  root = new THREE.Group();
  scene.add(root);
  scene.add(new THREE.AmbientLight(0xffffff, 1.8));
  const light = new THREE.PointLight(0x93c5fd, 2.2, 1600);
  light.position.set(260, 180, 420);
  scene.add(light);
  renderer.domElement.addEventListener("pointerdown", onPointerDown);
  renderer.domElement.addEventListener("pointermove", onPointerMove);
  renderer.domElement.addEventListener("pointerup", onPointerUp);
  renderer.domElement.addEventListener("wheel", onWheel, { passive: false });
  window.addEventListener("resize", resize);
}

function renderTypeFilters(typeCounts) {
  const rootEl = document.getElementById("typeFilters");
  rootEl.innerHTML = "";
  Object.entries(typeCounts).sort((a, b) => b[1] - a[1]).forEach(([type, count]) => {
    const label = document.createElement("label");
    label.innerHTML = `<input type="checkbox" data-type="${escapeHtml(type)}" checked><span><span class="pill">${escapeHtml(type)}</span>${count}</span>`;
    rootEl.appendChild(label);
  });
}

function renderLayerFilters() {
  const rootEl = document.getElementById("layerFilters");
  rootEl.innerHTML = "";
  for (const [layer, labelText] of [["core", "Core"], ["active", "Active"], ["knowledge", "Knowledge"], ["episode", "Episodes"], ["external", "External"]]) {
    const label = document.createElement("label");
    label.innerHTML = `<input type="checkbox" data-layer="${escapeHtml(layer)}" checked><span><span class="pill">${escapeHtml(labelText)}</span></span>`;
    rootEl.appendChild(label);
  }
}

function bindControls() {
  document.getElementById("search").addEventListener("input", scheduleApplyFilters);
  document.getElementById("weightFilter").addEventListener("input", event => {
    document.getElementById("weightValue").textContent = event.target.value;
    scheduleApplyFilters();
  });
  document.getElementById("timelineFilter").addEventListener("input", scheduleApplyFilters);
  document.getElementById("typeFilters").addEventListener("change", event => {
    if (!event.target.matches("input[type='checkbox']")) return;
    if (event.target.checked) activeTypes.add(event.target.dataset.type);
    else activeTypes.delete(event.target.dataset.type);
    scheduleApplyFilters();
  });
  document.getElementById("layerFilters").addEventListener("change", event => {
    if (!event.target.matches("input[type='checkbox']")) return;
    if (event.target.checked) activeLayers.add(event.target.dataset.layer);
    else activeLayers.delete(event.target.dataset.layer);
    scheduleApplyFilters();
  });
  document.getElementById("fit").addEventListener("click", fitView);
  document.getElementById("clearFocus").addEventListener("click", clearFocus);
  document.getElementById("focusNeighborhood").addEventListener("click", focusNeighborhood);
  document.getElementById("focusView").addEventListener("click", applyFilters);
}

function scheduleApplyFilters() {
  clearTimeout(renderTimer);
  renderTimer = setTimeout(applyFilters, 120);
}

function applyFilters() {
  expansionViewNodeId = null;
  selectedNodeId = null;
  selectedNode = null;
  const filtered = currentFilteredGalaxy();
  visibleGraph = buildSphereGalaxyLayout(filtered, { maxNodes: focusLimit });
  drawSphere();
  renderStats({
    node_count: filtered.nodes.length,
    edge_count: filtered.links.length,
    total_node_count: originalGraph.nodes.length,
    total_edge_count: originalGraph.links.length,
    visible_node_count: visibleGraph.nodes.length,
    visible_edge_count: visibleGraph.links.length,
  });
  emitEvent("view:filtered", null, { visible_nodes: visibleGraph.nodes.length });
}

function currentFilteredGalaxy() {
  return filterGalaxy(originalGraph, {
    query: document.getElementById("search").value,
    activeTypes,
    activeLayers,
    minWeight: Number(document.getElementById("weightFilter").value),
    timelineCutoff: currentTimelineCutoff(),
  });
}

function focusNeighborhood() {
  if (!selectedNode) return;
  expansionViewNodeId = selectedNode.id;
  visibleGraph = buildSphereGalaxyLayout(buildFocusGalaxy(currentFilteredGalaxy(), {
    focusNodeId: selectedNode.id,
    maxNodes: 360,
    seedCount: 1,
    firstRingLimit: 180,
  }), { maxNodes: 360, focusNodeId: selectedNode.id });
  drawSphere();
  fitView();
  emitEvent("node:expanded", selectedNode, { visible_neighbors: visibleGraph.nodes.length - 1 });
}

function clearFocus() {
  expansionViewNodeId = null;
  selectedNodeId = null;
  selectedNode = null;
  document.getElementById("details").textContent = "Select a node to inspect linked memories.";
  document.getElementById("agentPrompt").textContent = "Select a star to stage an agent prompt.";
  applyFilters();
  emitEvent("view:focus-cleared", null, {});
}

function drawSphere() {
  root.clear();
  root.rotation.set(rotation.x, rotation.y, 0);
  drawShells();
  const nodeById = new Map(visibleGraph.nodes.map(node => [node.id, node]));
  for (const link of visibleGraph.links) {
    const source = nodeById.get(String(link.source.id || link.source));
    const target = nodeById.get(String(link.target.id || link.target));
    if (!source || !target) continue;
    const selected = selectedNodeId && (source.id === selectedNodeId || target.id === selectedNodeId);
    const curve = new THREE.CatmullRomCurve3([
      new THREE.Vector3(source.x, source.y, source.z),
      new THREE.Vector3((source.x + target.x) / 2 * 1.12, (source.y + target.y) / 2 * 1.12, (source.z + target.z) / 2 * 1.12),
      new THREE.Vector3(target.x, target.y, target.z),
    ]);
    const geometry = new THREE.BufferGeometry().setFromPoints(curve.getPoints(18));
    const material = new THREE.LineBasicMaterial({ color: selected ? 0xfacc15 : 0x49617f, transparent: true, opacity: selected ? 0.72 : 0.18 });
    root.add(new THREE.Line(geometry, material));
  }
  for (const node of visibleGraph.nodes) {
    const material = new THREE.MeshBasicMaterial({ color: parseColor(node.color), transparent: true, opacity: node.id === selectedNodeId ? 1 : 0.84 });
    const geometry = new THREE.SphereGeometry(node.renderRadius, 16, 12);
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.set(node.x, node.y, node.z);
    mesh.userData.memoryNode = node;
    root.add(mesh);
    if (node.id === selectedNodeId) {
      const halo = new THREE.Mesh(new THREE.SphereGeometry(node.renderRadius + 8, 24, 16), new THREE.MeshBasicMaterial({ color: 0xfacc15, wireframe: true, transparent: true, opacity: 0.65 }));
      halo.position.copy(mesh.position);
      root.add(halo);
    }
  }
}

function drawShells() {
  for (const radius of [85, 155, 245, 330, 410]) {
    const shell = new THREE.Mesh(
      new THREE.SphereGeometry(radius, 48, 24),
      new THREE.MeshBasicMaterial({ color: 0x60a5fa, wireframe: true, transparent: true, opacity: radius === 155 ? 0.08 : 0.045 }),
    );
    root.add(shell);
  }
}

function onPointerDown(event) {
  isDraggingView = true;
  pointerMoved = false;
  lastPointer = { x: event.clientX, y: event.clientY };
}

function onPointerMove(event) {
  if (!isDraggingView) return;
  const dx = event.clientX - lastPointer.x;
  const dy = event.clientY - lastPointer.y;
  if (Math.abs(dx) + Math.abs(dy) > 3) pointerMoved = true;
  lastPointer = { x: event.clientX, y: event.clientY };
  rotation.y += dx * 0.006;
  rotation.x += dy * 0.006;
  root.rotation.set(rotation.x, rotation.y, 0);
}

function onPointerUp(event) {
  if (!pointerMoved) selectNodeAt(event);
  isDraggingView = false;
}

function selectNodeAt(event) {
  const rect = renderer.domElement.getBoundingClientRect();
  pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  pointer.y = -(((event.clientY - rect.top) / rect.height) * 2 - 1);
  raycaster.setFromCamera(pointer, camera);
  const hit = raycaster.intersectObjects(root.children, false).find(item => item.object.userData.memoryNode);
  if (!hit) return;
  selectedNode = hit.object.userData.memoryNode;
  selectedNodeId = selectedNode.id;
  document.getElementById("details").innerHTML = formatNodeDetails(selectedNode.raw);
  emitEvent("node:selected", selectedNode, { layer: selectedNode.layer });
  drawSphere();
}

function onWheel(event) {
  event.preventDefault();
  camera.position.z = Math.max(360, Math.min(1200, camera.position.z + event.deltaY * 0.8));
}

function fitView() {
  camera.position.set(0, 0, expansionViewNodeId ? 560 : 760);
}

function resize() {
  camera.aspect = container.clientWidth / container.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(container.clientWidth, container.clientHeight);
}

function animate() {
  requestAnimationFrame(animate);
  if (!isDraggingView) {
    rotation.y += 0.0007;
    root.rotation.set(rotation.x, rotation.y, 0);
  }
  renderer.render(scene, camera);
}

function emitEvent(type, node, context) {
  const event = createMemoryGalaxyEvent(type, {
    node_id: node?.id,
    gesture: type.includes("drag") ? "drag" : "click",
    view: viewName,
    context,
  });
  interactionLog.push(event);
  const prompt = suggestAgentPrompt(event, node?.raw || {});
  if (prompt) document.getElementById("agentPrompt").textContent = renderPromptText(prompt);
}

function currentTimelineCutoff() {
  const slider = document.getElementById("timelineFilter");
  const cutoff = timelineCutoffFromPercent(originalGraph.metadata.timeline || {}, Number(slider.value));
  document.getElementById("timelineValue").textContent = cutoff ? cutoff.slice(0, 10) : "All time";
  return cutoff;
}

function renderStats(metadata) {
  const totalNodes = Number(metadata.total_node_count ?? metadata.node_count ?? 0);
  const totalEdges = Number(metadata.total_edge_count ?? metadata.edge_count ?? 0);
  const filteredNodes = Number(metadata.node_count ?? totalNodes);
  const filteredEdges = Number(metadata.edge_count ?? totalEdges);
  const visibleNodes = Number(metadata.visible_node_count ?? filteredNodes);
  const visibleEdges = Number(metadata.visible_edge_count ?? filteredEdges);
  const visibleSuffix = visibleNodes !== filteredNodes || visibleEdges !== filteredEdges
    ? ` (${visibleNodes}/${visibleEdges} shown)`
    : "";
  document.getElementById("stats").textContent = `${filteredNodes}/${totalNodes} nodes / ${filteredEdges}/${totalEdges} edges${visibleSuffix}`;
}

function parseColor(value) {
  return Number.parseInt(String(value || "#94a3b8").replace("#", ""), 16);
}

init().catch(error => {
  document.getElementById("stats").textContent = "Failed to load sphere.";
  document.getElementById("details").textContent = String(error);
});

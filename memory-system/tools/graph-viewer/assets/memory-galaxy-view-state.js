export function createGalaxyViewState() {
  return {
    view: "galaxy",
    selectedSystem: null,
    selectedPlanet: null,
    selectedNodeId: null,
    hoveredNodeId: null,
    relationshipMode: "structure",
    nodeScale: 0.48,
    animationSpeed: 1,
    pathStartId: null,
    pathEndId: null,
    viewStack: [],
  };
}

export function enterGalaxyView(state) {
  state.view = "galaxy";
  state.selectedSystem = null;
  state.selectedPlanet = null;
  state.viewStack = [];
  return state;
}

export function enterSolarView(state, systemKey) {
  if (state.view !== "solar" || state.selectedSystem !== systemKey) {
    state.viewStack.push({ view: state.view, selectedSystem: state.selectedSystem, selectedPlanet: state.selectedPlanet });
  }
  state.view = "solar";
  state.selectedSystem = systemKey;
  state.selectedPlanet = null;
  return state;
}

export function enterPlanetView(state, planetId) {
  state.viewStack.push({ view: state.view, selectedSystem: state.selectedSystem, selectedPlanet: state.selectedPlanet });
  state.view = "planet";
  state.selectedPlanet = planetId;
  return state;
}

export function goBackView(state) {
  const previous = state.viewStack.pop();
  if (!previous) return enterGalaxyView(state);
  state.view = previous.view;
  state.selectedSystem = previous.selectedSystem;
  state.selectedPlanet = previous.selectedPlanet;
  return state;
}

export function selectGalaxySystem(state, systemKey, options = {}) {
  if (state.view !== "galaxy" || !systemKey || systemKey === "router") {
    return {
      enteredSolar: false,
      lastSystemTap: options.lastSystemTap || { key: null, time: 0 },
    };
  }
  const now = Number(options.now ?? Date.now());
  const doubleTapMs = Number(options.doubleTapMs ?? 420);
  const lastSystemTap = options.lastSystemTap || { key: null, time: 0 };
  const doubleTap = Boolean(options.forceEnter) || (lastSystemTap.key === systemKey && now - lastSystemTap.time < doubleTapMs);
  state.selectedSystem = systemKey;
  state.selectedNodeId = null;
  const nextTap = { key: systemKey, time: now };
  if (doubleTap) enterSolarView(state, systemKey);
  return { enteredSolar: doubleTap, lastSystemTap: nextTap };
}

export function selectSolarPlanet(state, planetId, options = {}) {
  if (state.view !== "solar" || !planetId) {
    return {
      enteredPlanet: false,
      lastPlanetTap: options.lastPlanetTap || { id: null, time: 0 },
    };
  }
  const now = Number(options.now ?? Date.now());
  const doubleTapMs = Number(options.doubleTapMs ?? 420);
  const lastPlanetTap = options.lastPlanetTap || { id: null, time: 0 };
  const doubleTap = Boolean(options.forceEnter) || (lastPlanetTap.id === planetId && now - lastPlanetTap.time < doubleTapMs);
  state.selectedNodeId = planetId;
  const nextTap = { id: planetId, time: now };
  if (doubleTap) enterPlanetView(state, planetId);
  return { enteredPlanet: doubleTap, lastPlanetTap: nextTap };
}

export function createGalaxyViewState() {
  return {
    view: "galaxy",
    selectedSystem: null,
    selectedPlanet: null,
    selectedNodeId: null,
    hoveredNodeId: null,
    relationshipMode: "structure",
    nodeScale: 0.48,
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

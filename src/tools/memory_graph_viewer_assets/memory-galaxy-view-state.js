export function createGalaxyViewState() {
  return {
    view: "galaxy",
    selectedSystem: null,
    selectedPlanet: null,
    selectedNodeId: null,
    selectedCometId: null,
    hoveredNodeId: null,
    relationshipMode: "structure",
    nodeScale: 0.48,
    animationSpeed: 1,
    motionResumeSpeed: 1,
    pathStartId: null,
    pathEndId: null,
    viewStack: [],
  };
}

export function enterGalaxyView(state) {
  state.view = "galaxy";
  state.selectedSystem = null;
  state.selectedPlanet = null;
  state.selectedNodeId = null;
  state.selectedCometId = null;
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
  state.selectedCometId = null;
  return state;
}

export function enterPlanetView(state, planetId) {
  state.viewStack.push({ view: state.view, selectedSystem: state.selectedSystem, selectedPlanet: state.selectedPlanet });
  state.view = "planet";
  state.selectedPlanet = planetId;
  state.selectedCometId = null;
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
  const lockedSystemTap = state.selectedSystem === systemKey;
  const enterSolar = Boolean(options.forceEnter) || lockedSystemTap || (lastSystemTap.key === systemKey && now - lastSystemTap.time < doubleTapMs);
  state.selectedSystem = systemKey;
  state.selectedNodeId = null;
  state.selectedCometId = null;
  const nextTap = { key: systemKey, time: now };
  if (enterSolar) enterSolarView(state, systemKey);
  return { enteredSolar: enterSolar, lastSystemTap: nextTap };
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
  const lockedPlanetTap = state.selectedNodeId === planetId;
  const enterPlanet = Boolean(options.forceEnter) || lockedPlanetTap || (lastPlanetTap.id === planetId && now - lastPlanetTap.time < doubleTapMs);
  state.selectedNodeId = planetId;
  state.selectedCometId = null;
  const nextTap = { id: planetId, time: now };
  if (enterPlanet) enterPlanetView(state, planetId);
  return { enteredPlanet: enterPlanet, lastPlanetTap: nextTap };
}

export function pauseGalaxyMotionForSelection(state, selectedNodeId = null) {
  const speed = Number(state.animationSpeed || 0);
  if (speed > 0) state.motionResumeSpeed = speed;
  state.animationSpeed = 0;
  state.motionEnabled = false;
  if (selectedNodeId !== null) state.selectedNodeId = selectedNodeId;
  state.selectedCometId = null;
  return state;
}

export function selectCometOverlay(state, cometId) {
  state.selectedNodeId = null;
  state.selectedCometId = cometId;
  return state;
}

export function resumeGalaxyMotionFromBlank(state) {
  const resumeSpeed = Number(state.motionResumeSpeed || 0);
  state.animationSpeed = resumeSpeed > 0 ? resumeSpeed : 1;
  state.motionEnabled = true;
  state.selectedNodeId = null;
  state.selectedCometId = null;
  if (state.view === "galaxy") {
    state.selectedSystem = null;
    state.selectedPlanet = null;
  } else if (state.view === "solar") {
    state.selectedPlanet = null;
  }
  state.hoveredNodeId = null;
  return state;
}

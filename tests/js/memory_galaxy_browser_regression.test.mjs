import assert from "node:assert/strict";
import path from "node:path";
import { pathToFileURL } from "node:url";

const playwrightIndex = process.env.PLAYWRIGHT_INDEX
  || "C:/Users/Administrator/AppData/Local/OpenAI/Codex/runtimes/cua_node/1b23c930bdf84ed6/bin/node_modules/playwright/index.mjs";
const edgePath = process.env.EDGE_PATH
  || "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
const viewerUrl = process.env.MEMORY_GALAXY_URL || "http://127.0.0.1:8766/";

const { chromium } = await import(pathToFileURL(path.normalize(playwrightIndex)).href);

const browser = await chromium.launch({ headless: true, executablePath: path.normalize(edgePath) });
const page = await browser.newPage({ viewport: { width: 1440, height: 960 } });

try {
  await page.goto(viewerUrl, { waitUntil: "networkidle" });
  await page.waitForFunction(() => !!window.__memoryGalaxyDebug?.getLayout?.(), { timeout: 15000 });

  const galaxySnapshot = await page.evaluate(() => {
    const dbg = window.__memoryGalaxyDebug;
    const layout = dbg.getLayout();
    const transform = dbg.getTransform();
    const skillSystem = layout.systems.find(system => system.key === "skill") || layout.systems.find(system => system.key !== "router");
    const skillStar = layout.nodes.find(node => node.id === `system:${skillSystem.key}`);
    const canvas = document.querySelector("#galaxy2d canvas");
    const rect = canvas.getBoundingClientRect();
    return {
      state: dbg.getState(),
      transform,
      skillSystem: { x: skillSystem.x, y: skillSystem.y },
      skillStar: { x: skillStar.x, y: skillStar.y, label: skillStar.label },
      canvasRect: { left: rect.left, top: rect.top },
    };
  });

  const galaxyMotion = await page.evaluate(async () => {
    const dbg = window.__memoryGalaxyDebug;
    const snap = () => {
      const layout = dbg.getLayout();
      const system = layout.systems.find(item => item.key === "skill") || layout.systems.find(item => item.key !== "router");
      const star = layout.nodes.find(item => item.id === `system:${system.key}`);
      return {
        system: { x: system.x, y: system.y },
        star: { x: star.x, y: star.y },
      };
    };
    const first = snap();
    await new Promise(resolve => setTimeout(resolve, 600));
    const second = snap();
    return { first, second };
  });
  assert.equal(Math.round(galaxyMotion.first.system.x * 1000) / 1000, Math.round(galaxyMotion.first.star.x * 1000) / 1000);
  assert.equal(Math.round(galaxyMotion.second.system.y * 1000) / 1000, Math.round(galaxyMotion.second.star.y * 1000) / 1000);

  const clickX = galaxySnapshot.canvasRect.left
    + galaxySnapshot.skillSystem.x * galaxySnapshot.transform.scale
    + galaxySnapshot.transform.pan.x;
  const clickY = galaxySnapshot.canvasRect.top
    + galaxySnapshot.skillSystem.y * galaxySnapshot.transform.scale
    + galaxySnapshot.transform.pan.y;

  await page.mouse.click(clickX, clickY, { clickCount: 2, delay: 120 });
  await page.waitForTimeout(800);

  const solarSnapshot = await page.evaluate(async () => {
    const dbg = window.__memoryGalaxyDebug;
    const snap = () => {
      const layout = dbg.getLayout();
      const planet = layout.nodes.find(node => node.orbitalRole === "planet");
      const satellite = layout.nodes.find(node => node.orbitalRole === "satellite");
      const satelliteSystem = layout.satelliteSystems?.[0];
      return {
        state: dbg.getState(),
        layoutView: layout?.view,
        orbits: (layout?.orbits || []).map(orbit => ({ kind: orbit.kind, aspect: Number(orbit.aspect || 1) })),
        planet: planet ? { x: planet.x, y: planet.y, id: planet.id } : null,
        satellite: satellite ? { x: satellite.x, y: satellite.y, parentNodeId: satellite.animation?.parentNodeId } : null,
        satelliteSystem: satelliteSystem ? { x: satelliteSystem.x, y: satelliteSystem.y, parentId: satelliteSystem.parentId } : null,
      };
    };
    const first = snap();
    await new Promise(resolve => setTimeout(resolve, 1200));
    const second = snap();
    return { first, second };
  });

  assert.equal(solarSnapshot.first.state.view, "solar");
  assert.equal(solarSnapshot.first.layoutView, "solar");
  assert.ok(solarSnapshot.first.orbits.every(orbit => orbit.aspect > 0 && orbit.aspect < 1));
  assert.ok(solarSnapshot.first.planet);
  assert.ok(solarSnapshot.first.satellite);
  assert.ok(solarSnapshot.first.satelliteSystem);
  assert.ok((solarSnapshot.first.satelliteSystem?.parentId));
  assert.notEqual(solarSnapshot.first.planet.x, solarSnapshot.second.planet.x);
  assert.notEqual(solarSnapshot.first.satellite.x, solarSnapshot.second.satellite.x);
  assert.equal(
    Math.round(solarSnapshot.second.satelliteSystem.x * 1000) / 1000,
    Math.round(solarSnapshot.second.planet.x * 1000) / 1000,
  );
  assert.equal(
    Math.round(solarSnapshot.second.satelliteSystem.y * 1000) / 1000,
    Math.round(solarSnapshot.second.planet.y * 1000) / 1000,
  );
  assert.ok((solarSnapshot.first.orbits || []).every(orbit => orbit.aspect > 0 && orbit.aspect < 1));

  const solarTransform = await page.evaluate(() => {
    const dbg = window.__memoryGalaxyDebug;
    const layout = dbg.getLayout();
    const transform = dbg.getTransform();
    const canvas = document.querySelector("#galaxy2d canvas");
    const rect = canvas.getBoundingClientRect();
    const firstPlanet = layout.nodes.find(node => node.orbitalRole === "planet");
    return {
      planet: { id: firstPlanet.id, x: firstPlanet.x, y: firstPlanet.y },
      transform,
      canvasRect: { left: rect.left, top: rect.top, width: rect.width, height: rect.height },
    };
  });
  const planetX = solarTransform.canvasRect.left
    + solarTransform.planet.x * solarTransform.transform.scale
    + solarTransform.transform.pan.x;
  const planetY = solarTransform.canvasRect.top
    + solarTransform.planet.y * solarTransform.transform.scale
    + solarTransform.transform.pan.y;

  await page.mouse.click(planetX, planetY, { clickCount: 1 });
  await page.waitForTimeout(300);
  const afterSingleClick = await page.evaluate(() => {
    const dbg = window.__memoryGalaxyDebug;
    const layout = dbg.getLayout();
    const selectedPlanet = layout.nodes.find(node => node.id === dbg.getState().selectedNodeId);
    return {
      state: dbg.getState(),
      selectedPlanet: selectedPlanet ? { id: selectedPlanet.id, x: selectedPlanet.x, y: selectedPlanet.y } : null,
      transform: dbg.getTransform(),
    };
  });
  assert.equal(afterSingleClick.state.view, "solar");
  assert.equal(afterSingleClick.selectedPlanet.id, solarTransform.planet.id);

  await page.mouse.click(planetX, planetY, { clickCount: 2, delay: 120 });
  await page.waitForTimeout(500);
  const afterDoubleClick = await page.evaluate(() => {
    const dbg = window.__memoryGalaxyDebug;
    return {
      state: dbg.getState(),
      layoutView: dbg.getLayout()?.view,
    };
  });
  assert.equal(afterDoubleClick.state.view, "planet");
  assert.equal(afterDoubleClick.layoutView, "planet");

  const speedFreezeSnapshot = await page.evaluate(async () => {
    const dbg = window.__memoryGalaxyDebug;
    const speed = document.getElementById("animationSpeed");
    speed.value = "0";
    speed.dispatchEvent(new Event("input", { bubbles: true }));
    const snap = () => {
      const layout = dbg.getLayout();
      const planet = layout.nodes.find(node => node.orbitalRole === "central-planet");
      const directMoon = layout.nodes.find(node => node.orbitalRole === "direct-moon");
      return {
        state: dbg.getState(),
        layoutView: layout?.view,
        orbits: (layout?.orbits || []).map(orbit => ({ kind: orbit.kind, aspect: Number(orbit.aspect || 1) })),
        planet: planet ? { x: planet.x, y: planet.y } : null,
        directMoon: directMoon ? { x: directMoon.x, y: directMoon.y } : null,
      };
    };
    const first = snap();
    await new Promise(resolve => setTimeout(resolve, 1200));
    const second = snap();
    return { first, second };
  });
  assert.equal(speedFreezeSnapshot.first.state.animationSpeed, 0);
  assert.ok(speedFreezeSnapshot.first.orbits.every(orbit => orbit.aspect > 0 && orbit.aspect < 1));
  assert.equal(
    Math.round(speedFreezeSnapshot.first.planet.x * 1000) / 1000,
    Math.round(speedFreezeSnapshot.second.planet.x * 1000) / 1000,
  );
  assert.equal(
    Math.round(speedFreezeSnapshot.first.planet.y * 1000) / 1000,
    Math.round(speedFreezeSnapshot.second.planet.y * 1000) / 1000,
  );
  assert.equal(
    Math.round(speedFreezeSnapshot.first.directMoon.x * 1000) / 1000,
    Math.round(speedFreezeSnapshot.second.directMoon.x * 1000) / 1000,
  );
  assert.equal(
    Math.round(speedFreezeSnapshot.first.directMoon.y * 1000) / 1000,
    Math.round(speedFreezeSnapshot.second.directMoon.y * 1000) / 1000,
  );
} finally {
  await browser.close();
}

import assert from "node:assert/strict";
import path from "node:path";
import { pathToFileURL } from "node:url";

const playwrightIndex = process.env.PLAYWRIGHT_INDEX
  || "C:/Users/Administrator/AppData/Local/OpenAI/Codex/runtimes/cua_node/1b23c930bdf84ed6/bin/node_modules/playwright/index.mjs";
const edgePath = process.env.EDGE_PATH
  || "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
const viewerUrl = process.env.MEMORY_GALAXY_URL || "http://127.0.0.1:8765/";

const { chromium } = await import(pathToFileURL(path.normalize(playwrightIndex)).href);

const browser = await chromium.launch({ headless: true, executablePath: path.normalize(edgePath) });
const page = await browser.newPage({ viewport: { width: 1440, height: 960 } });

try {
  await page.goto(viewerUrl, { waitUntil: "networkidle" });
  await page.waitForFunction(() => !!window.__memoryGalaxyDebug?.getLayout?.(), { timeout: 15000 });

  const shell = await page.evaluate(() => ({
    app: document.querySelector(".galaxy-app") ? true : false,
    left: document.querySelector(".sidebar-left") ? true : false,
    stage: document.querySelector(".galaxy-stage") ? true : false,
    right: document.querySelector(".inspector") ? true : false,
    topToolbar: document.querySelector(".stage-toolbar") ? true : false,
    liveHud: document.querySelector(".live-hud") ? true : false,
    bottomToolbar: document.querySelector(".stage-bottom-toolbar") ? true : false,
    minimap: document.querySelector(".galaxy-minimap") ? true : false,
    inspectorTabs: [...document.querySelectorAll(".inspector-tabs button")].map(button => button.textContent.trim()),
  }));
  assert.equal(shell.app, true);
  assert.equal(shell.left, true);
  assert.equal(shell.stage, true);
  assert.equal(shell.right, true);
  assert.equal(shell.topToolbar, true);
  assert.equal(shell.liveHud, true);
  assert.equal(shell.bottomToolbar, true);
  assert.equal(shell.minimap, true);
  assert.deepEqual(shell.inspectorTabs, ["OVERVIEW", "NODES", "CONNECTIONS"]);
  assert.equal(await page.locator('button[aria-label="Display settings"]').count(), 0);
  assert.equal(await page.locator('button[aria-label="Help"]').count(), 0);
  assert.equal(await page.locator(".focus-button").count(), 0);
  assert.equal(await page.locator('.stage-bottom-toolbar .toolbar-mode', { hasText: "2D" }).count(), 1);
  assert.equal(await page.locator('.stage-bottom-toolbar a.toolbar-mode[href="viewer-3d.html"]', { hasText: "3D" }).count(), 1);
  assert.equal(await page.locator('.stage-bottom-toolbar button').count(), 0);

  const shellMetrics = await page.evaluate(() => {
    const left = document.querySelector(".sidebar-left").getBoundingClientRect();
    const right = document.querySelector(".inspector").getBoundingClientRect();
    const stage = document.querySelector(".galaxy-stage").getBoundingClientRect();
    return {
      leftWidth: Math.round(left.width),
      rightWidth: Math.round(right.width),
      stageWidth: Math.round(stage.width),
    };
  });
  assert.ok(shellMetrics.leftWidth >= 270 && shellMetrics.leftWidth <= 310);
  assert.ok(shellMetrics.rightWidth >= 300 && shellMetrics.rightWidth <= 340);
  assert.ok(shellMetrics.stageWidth > 700);

  const leftLayout = await page.evaluate(() => {
    const sidebar = document.querySelector(".sidebar-left");
    const header = document.querySelector(".app-header");
    const viewControls = document.querySelector(".view-controls");
    const filters = document.querySelector(".filters-panel");
    const perf = document.querySelector(".gpu-panel");
    const rect = element => {
      const box = element.getBoundingClientRect();
      return { top: Math.round(box.top), bottom: Math.round(box.bottom), height: Math.round(box.height) };
    };
    return {
      sidebar: rect(sidebar),
      header: rect(header),
      viewControls: rect(viewControls),
      filters: rect(filters),
      perf: rect(perf),
      sparklineRightGap: Math.round(sidebar.getBoundingClientRect().right - document.getElementById("perfSparkline").getBoundingClientRect().right),
      sidebarOverflowY: getComputedStyle(sidebar).overflowY,
      filtersOverflowY: getComputedStyle(filters).overflowY,
      filtersScrollable: filters.scrollHeight > filters.clientHeight,
      perfTitle: perf.querySelector("h2")?.textContent?.trim() || "",
    };
  });
  assert.equal(leftLayout.sidebarOverflowY, "hidden");
  assert.equal(leftLayout.filtersOverflowY, "auto");
  assert.equal(leftLayout.filtersScrollable, true);
  assert.equal(leftLayout.perfTitle, "");
  assert.ok(leftLayout.header.top >= leftLayout.sidebar.top);
  assert.ok(leftLayout.viewControls.top >= leftLayout.header.bottom);
  assert.ok(leftLayout.filters.top >= leftLayout.viewControls.bottom);
  assert.ok(leftLayout.perf.top >= leftLayout.filters.bottom);
  assert.ok(Math.abs(leftLayout.perf.bottom - leftLayout.sidebar.bottom) <= 18);
  assert.ok(leftLayout.sparklineRightGap <= 18);

  const rightLayout = await page.evaluate(() => {
    const inspector = document.querySelector(".inspector");
    const selection = document.getElementById("selectionCard");
    const scroll = document.querySelector(".inspector-scroll");
    const tabs = document.querySelector(".inspector-tabs");
    const summary = document.getElementById("systemSummary");
    const rect = element => {
      const box = element.getBoundingClientRect();
      return { top: Math.round(box.top), bottom: Math.round(box.bottom), height: Math.round(box.height) };
    };
    return {
      inspector: rect(inspector),
      selection: rect(selection),
      scroll: rect(scroll),
      tabs: rect(tabs),
      summary: rect(summary),
      inspectorOverflowY: getComputedStyle(inspector).overflowY,
      scrollOverflowY: getComputedStyle(scroll).overflowY,
      scrollCanContainOverflow: scroll.clientHeight > 0 && scroll.scrollHeight >= scroll.clientHeight,
      selectionTopGap: Math.round(selection.getBoundingClientRect().top - inspector.getBoundingClientRect().top),
    };
  });
  assert.equal(rightLayout.inspectorOverflowY, "hidden");
  assert.equal(rightLayout.scrollOverflowY, "auto");
  assert.equal(rightLayout.scrollCanContainOverflow, true);
  assert.ok(rightLayout.selectionTopGap <= 20);
  assert.ok(rightLayout.tabs.top >= rightLayout.selection.bottom);
  assert.ok(rightLayout.summary.top >= rightLayout.tabs.bottom);
  assert.ok(rightLayout.scroll.top >= rightLayout.summary.bottom);
  assert.ok(rightLayout.summary.height < rightLayout.inspector.height * 0.45);

  const minimapInitial = await page.evaluate(() => ({
    dots: document.querySelectorAll(".minimap-dot").length,
    window: {
      left: document.getElementById("minimapWindow")?.style.left || "",
      top: document.getElementById("minimapWindow")?.style.top || "",
      width: document.getElementById("minimapWindow")?.style.width || "",
      height: document.getElementById("minimapWindow")?.style.height || "",
    },
  }));
  assert.ok(minimapInitial.dots >= 1);
  assert.match(minimapInitial.window.left, /%$/);
  assert.match(minimapInitial.window.width, /%$/);

  const beforeMinimapPan = await page.evaluate(() => window.__memoryGalaxyDebug.getTransform().pan);
  const minimapBox = await page.locator(".galaxy-minimap").boundingBox();
  assert.ok(minimapBox);
  await page.mouse.click(minimapBox.x + minimapBox.width * 0.18, minimapBox.y + minimapBox.height * 0.78);
  await page.waitForTimeout(150);
  const afterMinimapPan = await page.evaluate(() => window.__memoryGalaxyDebug.getTransform().pan);
  assert.ok(Math.abs(afterMinimapPan.x - beforeMinimapPan.x) > 1 || Math.abs(afterMinimapPan.y - beforeMinimapPan.y) > 1);
  await page.locator("#fitTop").click();
  await page.waitForTimeout(250);

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

  await page.evaluate(() => {
    const dbg = window.__memoryGalaxyDebug;
    const layout = dbg.getLayout();
    const transform = dbg.getTransform();
    const system = layout.systems.find(item => item.key === "skill") || layout.systems.find(item => item.key !== "router");
    const canvas = document.querySelector("#galaxy2d canvas");
    const rect = canvas.getBoundingClientRect();
    const clickX = rect.left + system.x * transform.scale + transform.pan.x;
    const clickY = rect.top + system.y * transform.scale + transform.pan.y;
    canvas.dispatchEvent(new MouseEvent("dblclick", {
      bubbles: true,
      cancelable: true,
      clientX: clickX,
      clientY: clickY,
    }));
  });
  await page.waitForTimeout(800);

  const solarSnapshot = await page.evaluate(async () => {
    const dbg = window.__memoryGalaxyDebug;
    const snap = () => {
      const layout = dbg.getLayout();
      const transform = dbg.getTransform();
      const canvas = document.querySelector("#galaxy2d canvas");
      const canvasRect = canvas.getBoundingClientRect();
      const planet = layout.nodes.find(node => node.orbitalRole === "planet");
      const satellite = layout.nodes.find(node => node.orbitalRole === "satellite");
      const satelliteSystem = layout.satelliteSystems?.[0];
      const fitNodes = layout.nodes.filter(node => node.orbitalRole === "planet" || node.orbitalRole === "satellite" || node.isPlanetSystemNode);
      const outsideFitNodes = fitNodes.filter(node => {
        const radius = Number(node.renderRadius || 0) * transform.scale;
        const x = node.x * transform.scale + transform.pan.x;
        const y = node.y * transform.scale + transform.pan.y;
        return x - radius < 0 || y - radius < 0 || x + radius > canvasRect.width || y + radius > canvasRect.height;
      });
      return {
        state: dbg.getState(),
        layoutView: layout?.view,
        fitNodeCount: fitNodes.length,
        outsideFitNodeCount: outsideFitNodes.length,
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
  assert.equal(solarSnapshot.first.state.selectedNodeId, null);
  assert.equal(solarSnapshot.first.state.animationSpeed > 0, true);
  assert.equal(solarSnapshot.first.layoutView, "solar");
  assert.ok(solarSnapshot.first.fitNodeCount > 0);
  assert.equal(solarSnapshot.first.outsideFitNodeCount, 0);
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

  const systemInspectorLayout = await page.evaluate(() => {
    const inspector = document.querySelector(".inspector");
    const summary = document.getElementById("systemSummary");
    const details = document.getElementById("systemDetails");
    const scroll = document.querySelector(".inspector-scroll");
    const rect = element => {
      const box = element.getBoundingClientRect();
      return { top: Math.round(box.top), bottom: Math.round(box.bottom), height: Math.round(box.height) };
    };
    return {
      inspector: rect(inspector),
      summary: rect(summary),
      details: rect(details),
      scroll: rect(scroll),
      scrollScrollable: scroll.scrollHeight > scroll.clientHeight,
    };
  });
  assert.ok(systemInspectorLayout.summary.height < systemInspectorLayout.inspector.height * 0.45);
  assert.ok(systemInspectorLayout.details.top >= systemInspectorLayout.scroll.top);
  assert.ok(systemInspectorLayout.scrollScrollable);

  const solarMinimap = await page.evaluate(() => ({
    view: window.__memoryGalaxyDebug.getState().view,
    dots: document.querySelectorAll(".minimap-dot").length,
    windowWidth: document.getElementById("minimapWindow")?.style.width || "",
  }));
  assert.equal(solarMinimap.view, "solar");
  assert.ok(solarMinimap.dots >= 1);
  assert.match(solarMinimap.windowWidth, /%$/);

  const liveDataText = await page.evaluate(() => ({
    liveTitle: document.querySelector(".live-title")?.textContent || "",
    selection: document.getElementById("selectionCard")?.textContent || "",
    summary: document.getElementById("systemSummary")?.textContent || "",
    overview: document.getElementById("systemDetails")?.textContent || "",
  }));
  assert.match(liveDataText.liveTitle, /Graph Scope/);
  assert.doesNotMatch(liveDataText.liveTitle, /Streaming Updates/);
  assert.doesNotMatch(liveDataText.selection, /System ID: sys_|Execution Layer|Control Layer|Context Layer|Evidence Layer|Encapsulates executable capabilities/);
  assert.match(liveDataText.selection, /memories and .*visible links|Top memory:/);
  assert.doesNotMatch(liveDataText.summary, /Excellent/);
  assert.match(liveDataText.summary, /Dated/);
  assert.doesNotMatch(liveDataText.overview, /View All/);

  await page.locator('.inspector-tabs button[data-tab="nodes"]').click();
  const nodesPanel = await page.evaluate(() => ({
    visible: !document.getElementById("nodesPanel").hidden,
    overviewHidden: document.getElementById("systemDetails").hidden,
    connectionHidden: document.getElementById("relationsPanel").hidden,
    nodeCount: document.querySelectorAll("#nodesPanel .memory-node-item").length,
    hasPlaceholder: /appear here|Select a system/.test(document.getElementById("nodesPanel").textContent || ""),
    text: document.getElementById("nodesPanel").textContent || "",
  }));
  assert.equal(nodesPanel.visible, true);
  assert.equal(nodesPanel.overviewHidden, true);
  assert.equal(nodesPanel.connectionHidden, true);
  assert.ok(nodesPanel.nodeCount > 0);
  assert.equal(nodesPanel.hasPlaceholder, false);
  assert.match(nodesPanel.text, /Node ID/);

  await page.locator('.inspector-tabs button[data-tab="connections"]').click();
  const connectionsPanel = await page.evaluate(() => ({
    visible: !document.getElementById("relationsPanel").hidden,
    nodeHidden: document.getElementById("nodesPanel").hidden,
    connectionCount: document.querySelectorAll("#relationsPanel .connection-item").length,
    hasPlaceholder: /Relations appear here/.test(document.getElementById("relationsPanel").textContent || ""),
    text: document.getElementById("relationsPanel").textContent || "",
  }));
  assert.equal(connectionsPanel.visible, true);
  assert.equal(connectionsPanel.nodeHidden, true);
  assert.ok(connectionsPanel.connectionCount > 0);
  assert.equal(connectionsPanel.hasPlaceholder, false);
  assert.match(connectionsPanel.text, /links|→/);

  await page.locator('.inspector-tabs button[data-tab="overview"]').click();
  assert.equal(await page.locator("#systemDetails[hidden]").count(), 0);

  await page.evaluate(() => {
    const speed = document.getElementById("animationSpeed");
    speed.value = "0";
    speed.dispatchEvent(new Event("input", { bubbles: true }));
  });

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
      minimapDots: document.querySelectorAll(".minimap-dot").length,
      minimapWindowWidth: document.getElementById("minimapWindow")?.style.width || "",
    };
  });
  assert.equal(afterDoubleClick.state.view, "planet");
  assert.equal(afterDoubleClick.state.selectedNodeId, null);
  assert.equal(afterDoubleClick.layoutView, "planet");
  assert.ok(afterDoubleClick.minimapDots >= 1);
  assert.match(afterDoubleClick.minimapWindowWidth, /%$/);

  const beforePlanetMinimapPan = await page.evaluate(() => window.__memoryGalaxyDebug.getTransform().pan);
  await page.mouse.move(minimapBox.x + minimapBox.width * 0.25, minimapBox.y + minimapBox.height * 0.25);
  await page.mouse.down();
  await page.mouse.move(minimapBox.x + minimapBox.width * 0.75, minimapBox.y + minimapBox.height * 0.7);
  await page.mouse.up();
  await page.waitForTimeout(150);
  const afterPlanetMinimapPan = await page.evaluate(() => window.__memoryGalaxyDebug.getTransform().pan);
  assert.ok(Math.abs(afterPlanetMinimapPan.x - beforePlanetMinimapPan.x) > 1 || Math.abs(afterPlanetMinimapPan.y - beforePlanetMinimapPan.y) > 1);

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

  await page.waitForTimeout(1400);
  const perfPanel = await page.evaluate(() => {
    const text = id => document.getElementById(id)?.textContent?.trim() || "";
    return {
      fps: text("perfFps"),
      frameTime: text("perfFrameTime"),
      cpu: text("perfCpu"),
      memory: text("perfMemory"),
      gpu: text("perfGpu"),
      gpuRenderer: text("perfGpuRenderer"),
      sparklineBars: document.querySelectorAll("#perfSparkline span").length,
      sampleCount: window.__memoryGalaxyDebug?.getPerformanceStats?.()?.sampleCount ?? 0,
      sampleLimit: window.__memoryGalaxyDebug?.getPerformanceStats?.()?.sampleLimit ?? 0,
    };
  });
  assert.match(perfPanel.fps, /^\d+$/);
  assert.match(perfPanel.frameTime, /^\d+(\.\d)? ms$/);
  assert.match(perfPanel.cpu, /^\d+(\.\d)?%$/);
  assert.ok(perfPanel.memory === "N/A" || /^\d+(\.\d)? MB( \/ \d+(\.\d)? MB)?$/.test(perfPanel.memory));
  assert.match(perfPanel.gpu, /^(~\d+(\.\d)? MB|\d+ \/ \d+ MB)$/);
  assert.ok(perfPanel.gpuRenderer.length > 0);
  assert.equal(perfPanel.sparklineBars, 36);
  assert.ok(perfPanel.sampleCount > 0);
  assert.ok(perfPanel.sampleLimit === 36);
  assert.ok(perfPanel.sampleCount <= perfPanel.sampleLimit);
} finally {
  await browser.close();
}

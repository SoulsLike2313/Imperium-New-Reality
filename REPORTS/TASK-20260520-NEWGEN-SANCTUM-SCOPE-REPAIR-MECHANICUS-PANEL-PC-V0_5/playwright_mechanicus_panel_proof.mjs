import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";

function parseArgs(argv) {
  const args = {
    baseUrl: "http://127.0.0.1:18765",
    outRoot: process.cwd(),
  };
  for (let i = 2; i < argv.length; i += 1) {
    const token = argv[i];
    if (token === "--base-url" && argv[i + 1]) {
      args.baseUrl = argv[i + 1];
      i += 1;
      continue;
    }
    if (token === "--out-root" && argv[i + 1]) {
      args.outRoot = path.resolve(argv[i + 1]);
      i += 1;
      continue;
    }
  }
  return args;
}

function nowIso() {
  return new Date().toISOString();
}

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

async function pageLayoutMetrics(page) {
  return page.evaluate(() => {
    const doc = document.documentElement;
    const body = document.body;
    const scrollWidth = Math.max(doc.scrollWidth, body ? body.scrollWidth : 0);
    const clientWidth = doc.clientWidth;
    const horizontalOverflowPx = Math.max(0, scrollWidth - clientWidth);
    const commandZone = document.querySelector(".command-zone");
    const workZone = document.querySelector(".work-zone");
    const commandRect = commandZone ? commandZone.getBoundingClientRect() : null;
    const workRect = workZone ? workZone.getBoundingClientRect() : null;
    const viewportHeight = window.innerHeight;
    const viewportWidth = window.innerWidth;
    const rawWrap = document.querySelector("#rawStreamWrap");
    const rawHidden = rawWrap ? rawWrap.classList.contains("is-hidden") : false;
    const liveTab = document.querySelector('.tab[data-tab="live"]');
    const liveActive = liveTab ? liveTab.classList.contains("is-active") : false;
    return {
      viewport: { width: viewportWidth, height: viewportHeight },
      scroll_width: scrollWidth,
      client_width: clientWidth,
      horizontal_overflow_px: horizontalOverflowPx,
      command_zone_visible_in_viewport: Boolean(
        commandRect && commandRect.top < viewportHeight && commandRect.bottom > 0 && commandRect.left < viewportWidth && commandRect.right > 0
      ),
      work_zone_visible_in_viewport: Boolean(
        workRect && workRect.top < viewportHeight && workRect.bottom > 0 && workRect.left < viewportWidth && workRect.right > 0
      ),
      raw_mode_hidden: rawHidden,
      live_tab_active: liveActive,
    };
  });
}

async function run() {
  const args = parseArgs(process.argv);
  const outRoot = path.resolve(args.outRoot);
  const screenshotsDir = path.join(outRoot, "SCREENSHOTS");
  ensureDir(screenshotsDir);

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1366, height: 768 } });
  const page = await context.newPage();
  page.setDefaultTimeout(30000);

  const consoleErrors = [];
  let failedRequests = 0;
  page.on("console", (msg) => {
    if (msg.type() === "error") {
      consoleErrors.push(msg.text());
    }
  });
  page.on("requestfailed", () => {
    failedRequests += 1;
  });

  await page.goto(args.baseUrl, { waitUntil: "domcontentloaded" });
  await page.waitForSelector("#organGrid");
  await page.waitForTimeout(1800);

  const screenshots = [];
  async function shot(name) {
    const fullPath = path.join(screenshotsDir, name);
    await page.screenshot({ path: fullPath, fullPage: true, timeout: 20000 });
    screenshots.push({ file_name: name, path: fullPath });
  }

  const mechanicusSelector = 'article.organ-card[data-organ-id="MECHANICUS_AGENT"]';
  await shot("01_overview_before_mechanicus_click.png");

  await page.locator(mechanicusSelector).hover();
  await page.waitForTimeout(300);
  await shot("02_mechanicus_node_hover_or_selected.png");

  await page.locator(mechanicusSelector).click();
  await page.waitForTimeout(900);
  await shot("03_mechanicus_panel_after_click_1366x768.png");

  const liveTabActiveAfterClick = await page
    .locator("#tabLive")
    .evaluate((node) => node.classList.contains("is-active"));
  const panelOpenStateAfterClick = (await page.locator("#livePanelOpenState").innerText()).trim();
  const mechanicusActiveAfterClick = await page
    .locator(mechanicusSelector)
    .evaluate((node) => node.classList.contains("active"));
  const rawHiddenAfterClick = await page
    .locator("#rawStreamWrap")
    .evaluate((node) => node.classList.contains("is-hidden"));

  const statusBtn = page.locator('.command-btn[data-command="status"]');
  await statusBtn.first().click();
  await page.waitForTimeout(1800);
  await shot("04_mechanicus_panel_after_status_command.png");

  const toolsBtn = page.locator('.command-btn[data-command="tools"]');
  await toolsBtn.first().click();
  await page.waitForTimeout(1800);
  await shot("05_mechanicus_panel_after_tools_command.png");

  await shot("06_sse_live_state_visible.png");

  await page.locator("#rawModeToggleBtn").click();
  await page.waitForTimeout(300);
  await shot("07_raw_technical_mode.png");
  const rawVisibleAfterToggle = await page
    .locator("#rawStreamWrap")
    .evaluate((node) => !node.classList.contains("is-hidden"));

  await page.setViewportSize({ width: 1920, height: 1080 });
  await page.waitForTimeout(800);
  await shot("08_mechanicus_panel_1920x1080.png");
  await page.evaluate(() => window.scrollTo(0, 0));
  const metrics1920 = await pageLayoutMetrics(page);

  await page.setViewportSize({ width: 1600, height: 900 });
  await page.waitForTimeout(500);
  await page.evaluate(() => window.scrollTo(0, 0));
  const metrics1600 = await pageLayoutMetrics(page);

  await page.locator('#tabActionHistory').click();
  await page.waitForTimeout(500);
  await shot("09_action_history_or_evidence_tab.png");

  await page.locator("#tabLive").click();
  await page.waitForTimeout(300);

  await page.setViewportSize({ width: 1366, height: 768 });
  await page.waitForTimeout(200);
  await page.evaluate(() => window.scrollTo(0, 0));
  const metrics1366 = await pageLayoutMetrics(page);

  const sseState = (await page.locator("#sseStatusPill").innerText()).trim();
  const rawToggleLabel = (await page.locator("#rawModeToggleBtn").innerText()).trim();
  const historyCards = await page.locator(".history-card").count();

  await context.close();
  await browser.close();

  const uiProof = {
    schema_version: "NEWGEN_UI_INTERACTION_PROOF_V0_5",
    generated_at_utc: nowIso(),
    base_url: args.baseUrl,
    mechanicus_click_selected_state: mechanicusActiveAfterClick,
    mechanicus_click_opened_live_panel: liveTabActiveAfterClick && panelOpenStateAfterClick.includes("Mechanicus"),
    panel_open_state_text: panelOpenStateAfterClick,
    status_command_button_present: true,
    tools_command_button_present: true,
    action_history_items_after_commands: historyCards,
    raw_mode_toggle_label: rawToggleLabel,
    raw_mode_secondary_rule: rawHiddenAfterClick && rawVisibleAfterToggle,
    console_errors_count: consoleErrors.length,
    failed_requests_count: failedRequests,
    screenshot_paths: screenshots,
  };

  const responsiveProof = {
    schema_version: "NEWGEN_RESPONSIVE_LAYOUT_PROOF_V0_5",
    generated_at_utc: nowIso(),
    viewport_1920x1080: metrics1920,
    viewport_1600x900: metrics1600,
    viewport_1366x768: metrics1366,
    verdict_1366_horizontal_overflow: metrics1366.horizontal_overflow_px === 0 ? "PASS" : "WARN",
    verdict_1366_command_zone_visible: metrics1366.command_zone_visible_in_viewport ? "PASS" : "WARN",
    verdict_1366_work_zone_visible: metrics1366.work_zone_visible_in_viewport ? "PASS" : "WARN",
    verdict_1600_horizontal_overflow: metrics1600.horizontal_overflow_px === 0 ? "PASS" : "WARN",
  };

  const sseProof = {
    schema_version: "NEWGEN_SSE_LIVE_STATUS_PROOF_V0_5",
    generated_at_utc: nowIso(),
    base_url: args.baseUrl,
    ui_sse_state_text: sseState,
    ui_state_interpretation: sseState.includes("CONNECTED")
      ? "SSE_CONNECTED"
      : sseState.includes("FALLBACK")
        ? "SSE_FALLBACK"
        : sseState.includes("ERROR")
          ? "SSE_ERROR"
          : sseState.includes("DISABLED")
            ? "SSE_DISABLED"
            : "UNKNOWN",
    required_event_types: ["heartbeat", "state_snapshot", "command_started/finished", "terminal_entry_added"],
    event_types_source: "sse_proof_check.py report",
  };

  process.stdout.write(
    JSON.stringify(
      {
        ui_interaction_proof: uiProof,
        responsive_layout_proof: responsiveProof,
        sse_live_status_proof: sseProof,
      },
      null,
      2
    ) + "\n"
  );
}

run().catch((error) => {
  process.stdout.write(
    JSON.stringify(
      {
        status: "ERROR",
        generated_at_utc: nowIso(),
        error: String(error),
      },
      null,
      2
    ) + "\n"
  );
  process.exitCode = 1;
});

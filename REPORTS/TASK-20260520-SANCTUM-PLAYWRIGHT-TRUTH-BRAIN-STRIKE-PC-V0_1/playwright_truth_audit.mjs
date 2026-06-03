import { chromium } from "playwright";
import fs from "node:fs";
import path from "node:path";

function nowIso() {
  return new Date().toISOString();
}

function parseArgs(argv) {
  const args = {
    baseUrl: "http://127.0.0.1:8876",
    label: "baseline",
    outDir: path.resolve("playwright_audit"),
  };
  for (let i = 2; i < argv.length; i += 1) {
    const token = argv[i];
    if (token === "--base-url" && argv[i + 1]) {
      args.baseUrl = argv[i + 1];
      i += 1;
      continue;
    }
    if (token === "--label" && argv[i + 1]) {
      args.label = argv[i + 1];
      i += 1;
      continue;
    }
    if (token === "--out-dir" && argv[i + 1]) {
      args.outDir = path.resolve(argv[i + 1]);
      i += 1;
      continue;
    }
  }
  return args;
}

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

async function getJson(url) {
  const response = await fetch(url, { cache: "no-store" });
  const text = await response.text();
  let body;
  try {
    body = JSON.parse(text);
  } catch {
    body = null;
  }
  return {
    ok: response.ok,
    status: response.status,
    url,
    body,
    raw: text,
  };
}

function toBool(value) {
  return Boolean(value);
}

function safeText(value) {
  return value == null ? "" : String(value);
}

function fileExistsMaybe(p) {
  if (!p) {
    return false;
  }
  try {
    return fs.existsSync(p);
  } catch {
    return false;
  }
}

function verdictFromChecks(checks) {
  return checks.every((item) => item.pass) ? "PASS" : "FAIL";
}

async function run() {
  const args = parseArgs(process.argv);
  const outDir = path.resolve(args.outDir);
  const shotsDir = path.join(outDir, "screenshots");
  ensureDir(outDir);
  ensureDir(shotsDir);

  const audit = {
    schema_version: "SANCTUM_PLAYWRIGHT_TRUTH_AUDIT_V0_1",
    label: args.label,
    base_url: args.baseUrl,
    generated_at_utc: nowIso(),
    endpoint_checks: [],
    visible_claim_checks: [],
    action_checks: [],
    truth_checks: [],
    screenshots: [],
    gaps: [],
    notes: [],
  };

  const endpoints = ["/api/health", "/api/state", "/api/actions", "/api/actions/history", "/api/terminal/history"];
  const endpointPayloads = {};
  for (const endpoint of endpoints) {
    const result = await getJson(`${args.baseUrl}${endpoint}`);
    endpointPayloads[endpoint] = result;
    audit.endpoint_checks.push({
      endpoint,
      http_status: result.status,
      ok: result.ok,
      json: toBool(result.body),
      pass: result.ok && toBool(result.body),
    });
  }

  const stateBefore = endpointPayloads["/api/state"]?.body || {};
  const healthBefore = endpointPayloads["/api/health"]?.body || {};

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
  const page = await context.newPage();
  page.setDefaultTimeout(20000);

  await page.goto(args.baseUrl, { waitUntil: "domcontentloaded" });
  await page.waitForSelector("#organGrid", { timeout: 20000 });
  await page.waitForTimeout(1500);

  async function shot(name, locator = null, fullPage = false) {
    const fileName = `${String(audit.screenshots.length + 1).padStart(2, "0")}_${name}.png`;
    const filePath = path.join(shotsDir, fileName);
    try {
      if (locator) {
        await page.locator(locator).first().screenshot({ path: filePath, timeout: 10000 });
      } else {
        await page.screenshot({ path: filePath, fullPage, timeout: 10000 });
      }
    } catch (error) {
      const fallbackName = `${String(audit.screenshots.length + 1).padStart(2, "0")}_${name}_fallback_fullpage.png`;
      const fallbackPath = path.join(shotsDir, fallbackName);
      await page.screenshot({ path: fallbackPath, fullPage: true, timeout: 10000 });
      audit.screenshots.push({
        name: `${name}_fallback_fullpage`,
        file_name: fallbackName,
        path: fallbackPath,
        note: `locator_capture_failed:${String(error)}`,
      });
      return;
    }
    audit.screenshots.push({ name, file_name: fileName, path: filePath });
  }

  await shot("overview", null, true);
  const brainLocatorCount = await page.locator("#brainZoneMap").count();
  const brainLikeDetected = brainLocatorCount > 0;
  await shot("active_brain_or_organ_zone", brainLikeDetected ? "#brainZoneMap" : "#organGrid");

  const metricChips = await page.locator("#headerMetrics .metric-chip").allTextContents();
  const truthRows = await page.evaluate(() => {
    const rows = [];
    for (const node of document.querySelectorAll("#truthBlock .truth-item")) {
      const key = node.querySelector(".truth-key")?.textContent?.trim() || "";
      const value = node.querySelector(".truth-value")?.textContent?.trim() || "";
      rows.push({ key, value });
    }
    return rows;
  });

  const headShort = safeText(stateBefore?.repo?.head).slice(0, 12);
  const worktreeState = safeText(stateBefore?.repo?.worktree_state);
  const activeOrgan = safeText(stateBefore?.server?.active_organ);

  audit.visible_claim_checks.push({
    id: "header_head_visible",
    pass: metricChips.some((t) => t.includes(headShort)),
    expected: headShort,
    actual_chips: metricChips,
  });
  audit.visible_claim_checks.push({
    id: "header_worktree_visible",
    pass: metricChips.some((t) => t.includes(worktreeState)),
    expected: worktreeState,
    actual_chips: metricChips,
  });
  audit.visible_claim_checks.push({
    id: "header_active_organ_visible",
    pass: metricChips.some((t) => t.includes(activeOrgan)),
    expected: activeOrgan,
    actual_chips: metricChips,
  });

  function truthValueByKeyToken(tokens) {
    const tokenList = Array.isArray(tokens) ? tokens : [tokens];
    const row = truthRows.find((x) => {
      const key = x.key.toLowerCase();
      return tokenList.some((token) => key.includes(String(token).toLowerCase()));
    });
    return row ? row.value : "";
  }

  const connectedUi = Number.parseInt(truthValueByKeyToken(["connected", "подключ"]), 10);
  const placeholderUi = Number.parseInt(truthValueByKeyToken(["placeholder"]), 10);
  const lockedUi = Number.parseInt(truthValueByKeyToken(["locked"]), 10);

  audit.truth_checks.push({
    id: "counts_connected_match",
    pass: connectedUi === Number(stateBefore?.global_truth?.connected_organs_count),
    ui: connectedUi,
    api: stateBefore?.global_truth?.connected_organs_count,
  });
  audit.truth_checks.push({
    id: "counts_placeholder_match",
    pass: placeholderUi === Number(stateBefore?.global_truth?.placeholders_count),
    ui: placeholderUi,
    api: stateBefore?.global_truth?.placeholders_count,
  });
  audit.truth_checks.push({
    id: "counts_locked_match",
    pass: lockedUi === Number(stateBefore?.global_truth?.locked_count),
    ui: lockedUi,
    api: stateBefore?.global_truth?.locked_count,
  });

  const requiredActionIds = [
    "refresh_state",
    "mechanicus_visual_status",
    "mechanicus_visual_tools",
    "mechanicus_visual_check",
    "mechanicus_visual_identity",
    "open_or_show_latest_report",
    "open_or_show_screenshots_folder",
    "show_api_state_json",
  ];

  for (const actionId of requiredActionIds) {
    const selector = `button[data-action-id='${actionId}']`;
    const count = await page.locator(selector).count();
    if (!count) {
      audit.action_checks.push({ action_id: actionId, pass: false, reason: "button_missing" });
      continue;
    }

    const historyBeforeRes = await getJson(`${args.baseUrl}/api/actions/history`);
    const historyBeforeLen = Array.isArray(historyBeforeRes.body?.history) ? historyBeforeRes.body.history.length : 0;

    await page.locator(selector).first().click({ timeout: 10000 });
    await page.waitForTimeout(1200);

    let found = false;
    for (let tryIdx = 0; tryIdx < 25; tryIdx += 1) {
      const historyAfterRes = await getJson(`${args.baseUrl}/api/actions/history`);
      const history = Array.isArray(historyAfterRes.body?.history) ? historyAfterRes.body.history : [];
      found = history.some((row) => row.action_id === actionId);
      const expanded = history.length >= historyBeforeLen;
      if (found && expanded) {
        break;
      }
      await page.waitForTimeout(300);
    }

    audit.action_checks.push({
      action_id: actionId,
      pass: found,
      button_present: true,
      history_recorded: found,
    });
  }

  const tabActionHistorySelector = "button[data-center-tab='action-history']";
  if ((await page.locator(tabActionHistorySelector).count()) > 0) {
    await page.locator(tabActionHistorySelector).first().click({ timeout: 10000 });
    await page.waitForTimeout(450);
  }
  await shot("action_click_result_examples", "#actionHistoryPanel");

  const mechanicusSelector = "article.organ-card[data-organ-id='MECHANICUS_AGENT']";
  if ((await page.locator(mechanicusSelector).count()) > 0) {
    await page.locator(mechanicusSelector).first().click();
    await page.waitForTimeout(450);
  }

  const tabEvidenceSelector = "button[data-center-tab='evidence']";
  if ((await page.locator(tabEvidenceSelector).count()) > 0) {
    await page.locator(tabEvidenceSelector).first().click();
    await page.waitForTimeout(500);
  }
  await shot("mechanicus_expanded_view", "main.center-zone");

  const placeholderSelector = "article.organ-card[data-organ-id='ADMINISTRATUM_AGENT']";
  if ((await page.locator(placeholderSelector).count()) > 0) {
    await page.locator(placeholderSelector).first().click();
    await page.waitForTimeout(500);
    await shot("failure_gap_placeholder_mode", "main.center-zone");
  }

  await shot("right_truth_panel", "#truthBlock");

  const stateAfterRes = await getJson(`${args.baseUrl}/api/state`);
  const stateAfter = stateAfterRes.body || {};

  const latestReportPath = stateAfter?.global_truth?.latest_report_path || "";
  const latestScreenshotPath = stateAfter?.global_truth?.latest_screenshot_path || "";
  const latestEvidencePath = stateAfter?.global_truth?.latest_evidence_path || "";

  audit.truth_checks.push({
    id: "latest_report_path_exists",
    pass: latestReportPath ? fileExistsMaybe(latestReportPath) : false,
    path: latestReportPath || "MISSING",
  });
  audit.truth_checks.push({
    id: "latest_screenshot_path_exists",
    pass: latestScreenshotPath ? fileExistsMaybe(latestScreenshotPath) : false,
    path: latestScreenshotPath || "MISSING",
  });
  audit.truth_checks.push({
    id: "latest_evidence_path_exists",
    pass: latestEvidencePath ? fileExistsMaybe(latestEvidencePath) : false,
    path: latestEvidencePath || "MISSING",
  });

  audit.truth_checks.push({
    id: "brain_zone_layout_detected",
    pass: brainLikeDetected,
    detail: brainLikeDetected ? "#brainZoneMap found" : "#brainZoneMap missing",
  });

  audit.notes.push(`health_status=${safeText(healthBefore?.status)}`);
  audit.notes.push(`brain_like_detected=${brainLikeDetected}`);

  const allChecks = [
    ...audit.endpoint_checks,
    ...audit.visible_claim_checks,
    ...audit.action_checks,
    ...audit.truth_checks,
  ];

  audit.verdict = verdictFromChecks(allChecks);

  for (const row of allChecks) {
    if (!row.pass) {
      audit.gaps.push(row.id || row.action_id || "unknown_gap");
    }
  }

  const jsonPath = path.join(outDir, `PLAYWRIGHT_TRUTH_AUDIT_${args.label.toUpperCase()}.json`);
  fs.writeFileSync(jsonPath, JSON.stringify(audit, null, 2));

  const mdLines = [];
  mdLines.push(`# Playwright Truth Audit (${args.label})`);
  mdLines.push("");
  mdLines.push(`- generated_at_utc: ${audit.generated_at_utc}`);
  mdLines.push(`- base_url: ${audit.base_url}`);
  mdLines.push(`- verdict: ${audit.verdict}`);
  mdLines.push(`- health_status: ${safeText(healthBefore?.status)}`);
  mdLines.push(`- brain_like_detected: ${brainLikeDetected}`);
  mdLines.push("");
  mdLines.push("## Failed checks");
  const failed = allChecks.filter((x) => !x.pass);
  if (!failed.length) {
    mdLines.push("- none");
  } else {
    for (const item of failed) {
      mdLines.push(`- ${item.id || item.action_id || "unknown"}`);
    }
  }
  mdLines.push("");
  mdLines.push("## Screenshots");
  for (const item of audit.screenshots) {
    mdLines.push(`- ${item.name}: ${item.path}`);
  }

  const mdPath = path.join(outDir, `PLAYWRIGHT_TRUTH_AUDIT_${args.label.toUpperCase()}.md`);
  fs.writeFileSync(mdPath, mdLines.join("\n"));

  fs.writeFileSync(path.join(outDir, `STATE_${args.label.toUpperCase()}_SNAPSHOT.json`), JSON.stringify(stateAfter, null, 2));

  await browser.close();

  const summary = {
    verdict: audit.verdict,
    json_report: jsonPath,
    md_report: mdPath,
    screenshots_dir: shotsDir,
    gap_count: audit.gaps.length,
  };
  console.log(JSON.stringify(summary, null, 2));
}

run().catch((error) => {
  console.error("PLAYWRIGHT_AUDIT_FATAL", error);
  process.exitCode = 1;
});

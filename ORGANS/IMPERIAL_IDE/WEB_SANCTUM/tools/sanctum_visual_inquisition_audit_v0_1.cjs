#!/usr/bin/env node
/*
IMPERIUM NEW REALITY · WEB SANCTUM
Playwright / Visual Inquisition Audit v0.1

A built-in IDE evidence spine for agents and owner review.
Outputs are written outside source repo into LOCAL_HANDOFF/SERVITOR_OUTPUTS.
*/

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const child = require("child_process");

const VERSION = "0.1.0";
const SURFACE = "WEB_SANCTUM_PLAYWRIGHT_VISUAL_INQUISITION_AUDIT_V0_1";

function parseArgs(argv) {
  const args = {
    base: process.env.SANCTUM_BASE_URL || "http://127.0.0.1:8792",
    profile: process.env.AUDIT_PROFILE || "balanced",
    out: process.env.MEGA_AUDIT_OUT || process.env.VISUAL_INQUISITION_OUT || "",
    headed: false,
    safeActions: false,
    dryRun: false,
    slowMo: 60,
  };
  for (let i = 2; i < argv.length; i += 1) {
    const a = argv[i];
    if (a === "--base") args.base = argv[++i];
    else if (a === "--profile") args.profile = argv[++i];
    else if (a === "--out") args.out = argv[++i];
    else if (a === "--headed") args.headed = true;
    else if (a === "--safe-actions") args.safeActions = true;
    else if (a === "--dry-run") args.dryRun = true;
    else if (a === "--slow-mo") args.slowMo = Number(argv[++i] || 60);
  }
  args.profile = ["light", "balanced", "full"].includes(args.profile) ? args.profile : "balanced";
  return args;
}

function evidencePolicy(profile) {
  const quality = Number(process.env.AUDIT_JPEG_QUALITY || (profile === "full" ? 85 : profile === "light" ? 70 : 76));
  if (profile === "light") {
    return { profile, keyType: "jpeg", bulkType: "jpeg", jpegQuality: quality, navLimit: 8, maxTilesPerContainer: 4, captureDom: false, fullPage: false };
  }
  if (profile === "full") {
    return { profile, keyType: "png", bulkType: "jpeg", jpegQuality: quality, navLimit: 30, maxTilesPerContainer: 28, captureDom: true, fullPage: true };
  }
  return { profile, keyType: "png", bulkType: "jpeg", jpegQuality: quality, navLimit: 18, maxTilesPerContainer: 12, captureDom: false, fullPage: false };
}

function stamp() {
  const d = new Date();
  const z = n => String(n).padStart(2, "0");
  return `${d.getFullYear()}${z(d.getMonth()+1)}${z(d.getDate())}-${z(d.getHours())}${z(d.getMinutes())}${z(d.getSeconds())}`;
}

function handoffRoot() {
  return process.env.IMPERIUM_LOCAL_HANDOFF || process.env.LOCAL_HANDOFF || "E:/_LOCAL_HANDOFF";
}

function defaultOut(profile) {
  return path.join(handoffRoot(), "SERVITOR_OUTPUTS", `MEGA_PLAYWRIGHT_AUDIT_${profile.toUpperCase()}_${stamp()}`);
}

function ensureDir(p) { fs.mkdirSync(p, { recursive: true }); }
function writeText(file, value) { ensureDir(path.dirname(file)); fs.writeFileSync(file, String(value), "utf8"); }
function writeJson(file, value) { writeText(file, JSON.stringify(value, null, 2)); }
function safeName(s) { return String(s || "item").replace(/[^a-zA-Z0-9_\-.]+/g, "_").slice(0, 120); }
function sha256(buf) { return crypto.createHash("sha256").update(buf).digest("hex"); }
function rel(root, file) { return path.relative(root, file).replaceAll("\\", "/"); }
function csvCell(v) { return `"${String(v ?? "").replaceAll('"', '""').replace(/[\r\n]+/g, " ")}"`; }
function writeCsv(file, rows, headers) {
  const lines = [headers.map(csvCell).join(",")];
  for (const row of rows) lines.push(headers.map(h => csvCell(row[h])).join(","));
  writeText(file, lines.join("\n") + "\n");
}

function repoRootFromWebRoot(webRoot) { return path.resolve(webRoot, "..", "..", ".."); }
function runGit(repoRoot, args) {
  try {
    const out = child.spawnSync("git", ["-C", repoRoot, ...args], { encoding: "utf8", shell: false, timeout: 30000 });
    return { status: out.status === 0 ? "PASS" : "FAIL", stdout: out.stdout || "", stderr: out.stderr || "" };
  } catch (err) { return { status: "FAIL", stdout: "", stderr: err.stack || err.message }; }
}

function resolvePlaywright(webRoot) {
  const candidates = [
    path.join(webRoot, "node_modules", "playwright"),
    path.join(webRoot, "node_modules", "@playwright", "test", "node_modules", "playwright"),
    "playwright",
  ];
  const errors = [];
  for (const c of candidates) {
    try {
      const mod = require(c);
      if (mod?.chromium) return mod;
    } catch (err) { errors.push(`${c}: ${err.message}`); }
  }
  const e = new Error("PLAYWRIGHT_MODULE_NOT_FOUND: run npm ci inside WEB_SANCTUM first.");
  e.details = errors;
  throw e;
}

async function fetchJson(base, apiPath, timeoutMs = 60000) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  const started = Date.now();
  try {
    const response = await fetch(`${base}${apiPath}`, { signal: ctrl.signal });
    const text = await response.text();
    let body;
    try { body = JSON.parse(text); } catch { body = { status: "FAIL", reason: "JSON_PARSE_FAILED", raw: text.slice(0, 5000) }; }
    return { ok: response.ok, status_code: response.status, duration_ms: Date.now() - started, body };
  } catch (err) {
    return { ok: false, status_code: 0, duration_ms: Date.now() - started, body: { status: "FAIL", reason: err.name || "FETCH_FAILED", message: err.message } };
  } finally { clearTimeout(timer); }
}

function screenshotOptions(type, quality) {
  if (type === "jpeg") return { type: "jpeg", quality };
  return { type: "png" };
}

async function main() {
  const args = parseArgs(process.argv);
  const policy = evidencePolicy(args.profile);
  const webRoot = process.cwd();
  const repoRoot = repoRootFromWebRoot(webRoot);
  const out = path.resolve(args.out || defaultOut(policy.profile));
  const dirs = {
    api: path.join(out, "api_json"),
    git: path.join(out, "git"),
    key: path.join(out, "screenshots_key"),
    bulk: path.join(out, "screenshots_bulk_jpeg"),
    containers: path.join(out, "screenshots_scroll_containers"),
    csv: path.join(out, "tables_csv"),
    browser: path.join(out, "browser_logs"),
    report: path.join(out, "report"),
    dom: path.join(out, "dom_snapshots"),
  };
  ensureDir(out); Object.values(dirs).forEach(ensureDir);

  const manifest = {
    status: "STARTED",
    surface: SURFACE,
    version: VERSION,
    profile: policy.profile,
    generated_at_utc: new Date().toISOString(),
    base_url: args.base,
    web_root: webRoot,
    repo_root: repoRoot,
    output_root: out,
    evidence_policy: {
      key_screenshots: policy.keyType,
      bulk_screenshots: `${policy.bulkType} quality ${policy.jpegQuality}`,
      csv_maps: true,
      json_truth: true,
      markdown_report: true,
      source_repo_writes: false,
    },
  };
  writeJson(path.join(out, "MANIFEST.json"), manifest);

  let playwright;
  try { playwright = resolvePlaywright(webRoot); }
  catch (err) {
    manifest.status = "FAIL"; manifest.reason = err.message; manifest.details = err.details || [];
    writeJson(path.join(out, "MANIFEST.json"), manifest);
    console.error(JSON.stringify(manifest, null, 2));
    process.exit(2);
  }

  if (args.dryRun) {
    manifest.status = "PASS"; manifest.dry_run = true;
    writeJson(path.join(out, "MANIFEST.json"), manifest);
    console.log(JSON.stringify(manifest, null, 2));
    return;
  }

  const gitHead = runGit(repoRoot, ["rev-parse", "HEAD"]);
  const gitStatusBefore = runGit(repoRoot, ["status", "--short", "--branch"]);
  const gitLog10 = runGit(repoRoot, ["log", "--oneline", "--decorate", "-10"]);
  writeText(path.join(dirs.git, "head.txt"), gitHead.stdout || gitHead.stderr);
  writeText(path.join(dirs.git, "status_before.txt"), gitStatusBefore.stdout || gitStatusBefore.stderr);
  writeText(path.join(dirs.git, "log_10.txt"), gitLog10.stdout || gitLog10.stderr);

  const apiMap = {
    health: ["/api/health", 60000],
    actions: ["/api/actions", 60000],
    snapshot: ["/api/snapshot", 60000],
    jobs_before: ["/api/jobs", 60000],
    data_atlas_force: ["/api/data-atlas?force=1", 240000],
  };
  const api = {};
  for (const [name, [apiPath, timeout]] of Object.entries(apiMap)) {
    api[name] = await fetchJson(args.base, apiPath, timeout);
    writeJson(path.join(dirs.api, `${name}.json`), api[name]);
  }

  const browserEvents = { console: [], page_errors: [], request_failed: [], response_errors: [] };
  const navigationRows = [];
  const screenshotRows = [];
  const actionRows = [];
  const painRows = [];
  const sectionRows = [];
  const hashMap = {};

  const browser = await playwright.chromium.launch({ headless: !args.headed, slowMo: args.headed ? args.slowMo : 0 });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  page.on("console", msg => browserEvents.console.push({ type: msg.type(), text: msg.text(), location: msg.location() }));
  page.on("pageerror", err => browserEvents.page_errors.push({ message: err.message, stack: err.stack || "" }));
  page.on("requestfailed", req => browserEvents.request_failed.push({ url: req.url(), method: req.method(), failure: JSON.stringify(req.failure() || {}) }));
  page.on("response", res => { if (res.status() >= 400) browserEvents.response_errors.push({ url: res.url(), status: res.status(), statusText: res.statusText() }); });

  async function saveScreenshot(target, name, kind = "bulk", options = {}) {
    const type = kind === "key" ? policy.keyType : policy.bulkType;
    const ext = type === "jpeg" ? "jpg" : "png";
    const dir = kind === "key" ? dirs.key : dirs.bulk;
    const file = path.join(dir, `${name}.${ext}`);
    const opts = { path: file, ...screenshotOptions(type, policy.jpegQuality), fullPage: !!options.fullPage };
    if (target === page) await page.screenshot(opts);
    else await target.screenshot(opts);
    const buf = fs.readFileSync(file);
    const hash = sha256(buf);
    hashMap[hash] = hashMap[hash] || [];
    hashMap[hash].push(name);
    const row = { name, kind, type, file: rel(out, file), bytes: buf.length, sha256: hash, note: options.note || "" };
    screenshotRows.push(row);
    console.log(`SHOT ${name}.${ext} ${Math.round(buf.length/1024)}KB`);
    return row;
  }

  async function clickAction(label, testid, actionId) {
    const before = await page.evaluate(() => document.body.innerText || "");
    let ok = false, message = "";
    try {
      await page.getByTestId(testid).click({ timeout: 8000 });
      ok = true;
    } catch (err) {
      message = err.message;
      painRows.push({ severity: "WARN", kind: "ACTION_CLICK_FAILED", target: label, detail: message.slice(0, 300) });
    }
    await page.waitForTimeout(1500);
    const after = await page.evaluate(() => document.body.innerText || "");
    actionRows.push({ label, action_id: actionId || "", testid, ok, changed_text: before !== after, message });
    return ok;
  }

  async function openPage(pageId, label, testid) {
    const before = await page.evaluate(() => ({ y: window.scrollY, text: document.body.innerText.slice(0, 500) }));
    let ok = false, message = "";
    try {
      await page.getByTestId(testid).click({ timeout: 8000 });
      ok = true;
    } catch (err) {
      message = err.message;
      painRows.push({ severity: "WARN", kind: "NAV_CLICK_FAILED", target: label, detail: message.slice(0, 300) });
    }
    await page.waitForTimeout(1200);
    const after = await page.evaluate(() => ({ y: window.scrollY, text: document.body.innerText.slice(0, 500) }));
    const locator = page.locator(`#page-${pageId}`).first();
    let visible = false;
    try { visible = await locator.isVisible({ timeout: 3000 }); } catch { visible = false; }
    navigationRows.push({ page_id: pageId, label, testid, click_ok: ok, visible, changed_y: before.y !== after.y, changed_text: before.text !== after.text, message });
    if (!visible) painRows.push({ severity: "WARN", kind: "SECTION_NOT_VISIBLE_AFTER_NAV", target: label, detail: `#page-${pageId}` });
    try {
      const box = await locator.boundingBox();
      sectionRows.push({ page_id: pageId, label, visible, width: Math.round(box?.width || 0), height: Math.round(box?.height || 0) });
      if (visible) await saveScreenshot(locator, `NAV_${safeName(pageId)}_${safeName(label)}`, ["sanctum", "atlas", "playwright", "jobs"].includes(pageId) ? "key" : "bulk");
    } catch (err) {
      painRows.push({ severity: "WARN", kind: "SECTION_SCREENSHOT_FAILED", target: label, detail: err.message.slice(0, 300) });
    }
  }

  async function waitAtlasLoaded() {
    const ok = await page.waitForFunction(() => {
      const txt = document.body.innerText || "";
      return txt.includes("Entities / Сущности") && !txt.includes("Атлас ещё не загружен") && /\b[1-9][0-9]{3,}\b/.test(txt);
    }, null, { timeout: 240000 }).then(() => true).catch(() => false);
    if (!ok) painRows.push({ severity: "WARN", kind: "DATA_ATLAS_UI_LOAD_TIMEOUT", target: "Data Atlas", detail: "Atlas did not show entity counts within timeout." });
    await page.waitForTimeout(policy.profile === "light" ? 2500 : 6000);
    return ok;
  }

  await page.goto(args.base, { waitUntil: "domcontentloaded", timeout: 60000 });
  await page.waitForTimeout(2500);
  await saveScreenshot(page, "00_SANCTUM_INITIAL_VIEWPORT", "key");
  if (policy.fullPage) await saveScreenshot(page, "00_SANCTUM_DOCUMENT_FULLPAGE", "bulk", { fullPage: true });

  const pages = [
    ["sanctum", "Sanctum", "nav-sanctum"],
    ["warp", "WARP", "nav-warp"],
    ["register", "Task Register", "nav-register"],
    ["astronomicon", "Astronomicon", "nav-astronomicon"],
    ["mechanicus", "Mechanicus", "nav-mechanicus"],
    ["jobs", "Jobs", "nav-jobs"],
    ["stage", "Stage Control", "nav-stage"],
    ["hygiene", "Runtime Hygiene", "nav-hygiene"],
    ["atlas", "Data Atlas", "nav-atlas"],
    ["validation", "Inquisition", "nav-validation"],
    ["reports", "Report Bundle", "nav-reports"],
    ["promotion", "Promotion Preview", "nav-promotion"],
    ["playwright", "Playwright / Visual Inquisition", "nav-playwright"],
  ];
  for (const row of pages.slice(0, policy.navLimit)) await openPage(...row);

  await openPage("atlas", "Data Atlas", "nav-atlas");
  if (args.safeActions) {
    await clickAction("Scan Atlas", "data-atlas-scan", "data_atlas_scan");
    await waitAtlasLoaded();
  }
  const atlasSection = page.locator("#page-atlas").first();
  await saveScreenshot(atlasSection, "ATLAS_SECTION_AFTER_LOAD", "key");

  const atlasElements = [
    ["atlas-kpis", "ATLAS_KPIS"],
    ["atlas-organ-map", "ATLAS_ORGAN_MAP"],
    ["atlas-dirt-list", "ATLAS_PRIORITY_DIRT"],
    ["atlas-cleanup-lanes", "ATLAS_CLEANUP_LANES"],
    ["atlas-lifecycle-matrix", "ATLAS_LIFECYCLE_MATRIX"],
    ["atlas-explorer", "ATLAS_ENTITY_EXPLORER"],
    ["atlas-passport-trace", "ATLAS_PASSPORT_TRACE"],
  ];
  for (const [testid, name] of atlasElements) {
    try {
      const loc = page.getByTestId(testid).first();
      if (await loc.isVisible({ timeout: 3000 })) await saveScreenshot(loc, name, name.includes("EXPLORER") || name.includes("PASSPORT") ? "key" : "bulk");
    } catch (err) { painRows.push({ severity: "INFO", kind: "ATLAS_ELEMENT_CAPTURE_SKIPPED", target: name, detail: err.message.slice(0, 250) }); }
  }

  const scrollContainers = await page.evaluate(() => {
    let seq = 0;
    const nodes = Array.from(document.querySelectorAll("#page-atlas *"));
    return nodes.map((el) => {
      const r = el.getBoundingClientRect();
      const extra = el.scrollHeight - el.clientHeight;
      const text = (el.innerText || el.textContent || "").slice(0, 140);
      if (extra > 120 && r.width > 250 && r.height > 120) {
        const id = `visual-inquisition-scroll-${seq++}`;
        el.setAttribute("data-visual-inquisition-scroll-id", id);
        return { id, tag: el.tagName, element_id: el.id || "", class_name: String(el.className || "").slice(0, 120), width: Math.round(r.width), height: Math.round(r.height), client_height: el.clientHeight, scroll_height: el.scrollHeight, extra_y: extra, text };
      }
      return null;
    }).filter(Boolean).sort((a,b) => b.extra_y - a.extra_y).slice(0, 8);
  });

  let ci = 0;
  for (const c of scrollContainers) {
    const step = Math.max(220, Math.min(700, c.client_height - 80));
    let tile = 0;
    for (let y = 0; y <= c.extra_y; y += step) {
      await page.evaluate(({ id, y }) => {
        const el = document.querySelector(`[data-visual-inquisition-scroll-id="${id}"]`);
        if (el) el.scrollTop = y;
      }, { id: c.id, y });
      await page.waitForTimeout(250);
      const loc = page.locator(`[data-visual-inquisition-scroll-id="${c.id}"]`).first();
      const name = `SCROLL_${String(ci).padStart(2,"0")}_${safeName(c.element_id || c.class_name || c.tag)}_${String(tile).padStart(2,"0")}_y_${y}`;
      const file = path.join(dirs.containers, `${name}.jpg`);
      try {
        await loc.screenshot({ path: file, type: "jpeg", quality: policy.jpegQuality });
        const buf = fs.readFileSync(file);
        screenshotRows.push({ name, kind: "scroll_tile", type: "jpeg", file: rel(out, file), bytes: buf.length, sha256: sha256(buf), note: c.text });
      } catch (err) { painRows.push({ severity: "WARN", kind: "SCROLL_TILE_FAILED", target: name, detail: err.message.slice(0, 250) }); break; }
      tile += 1;
      if (tile >= policy.maxTilesPerContainer) break;
    }
    ci += 1;
  }

  if (policy.captureDom) writeText(path.join(dirs.dom, "document_body_text.txt"), await page.evaluate(() => document.body.innerText || ""));

  const apiJobsAfter = await fetchJson(args.base, "/api/jobs", 60000);
  writeJson(path.join(dirs.api, "jobs_after.json"), apiJobsAfter);
  const gitStatusAfter = runGit(repoRoot, ["status", "--short", "--branch"]);
  writeText(path.join(dirs.git, "status_after.txt"), gitStatusAfter.stdout || gitStatusAfter.stderr);

  for (const [hash, names] of Object.entries(hashMap)) {
    if (names.length > 1) painRows.push({ severity: "INFO", kind: "DUPLICATE_SCREENSHOT_HASH", target: names.join(" | "), detail: hash });
  }
  if (browserEvents.page_errors.length) painRows.push({ severity: "WARN", kind: "BROWSER_PAGE_ERRORS", target: "browser", detail: String(browserEvents.page_errors.length) });
  if (browserEvents.response_errors.length) painRows.push({ severity: "WARN", kind: "HTTP_RESPONSE_ERRORS", target: "network", detail: String(browserEvents.response_errors.length) });

  writeJson(path.join(dirs.browser, "console.json"), browserEvents.console);
  writeJson(path.join(dirs.browser, "page_errors.json"), browserEvents.page_errors);
  writeJson(path.join(dirs.browser, "request_failed.json"), browserEvents.request_failed);
  writeJson(path.join(dirs.browser, "response_errors.json"), browserEvents.response_errors);

  writeCsv(path.join(dirs.csv, "navigation_map.csv"), navigationRows, ["page_id", "label", "testid", "click_ok", "visible", "changed_y", "changed_text", "message"]);
  writeCsv(path.join(dirs.csv, "section_inventory.csv"), sectionRows, ["page_id", "label", "visible", "width", "height"]);
  writeCsv(path.join(dirs.csv, "action_results.csv"), actionRows, ["label", "action_id", "testid", "ok", "changed_text", "message"]);
  writeCsv(path.join(dirs.csv, "screenshot_manifest.csv"), screenshotRows, ["name", "kind", "type", "file", "bytes", "sha256", "note"]);
  writeCsv(path.join(dirs.csv, "pain_map.csv"), painRows, ["severity", "kind", "target", "detail"]);

  const atlasSummary = api.data_atlas_force?.body?.summary || {};
  writeCsv(path.join(dirs.csv, "atlas_summary.csv"), Object.entries(atlasSummary).map(([metric, value]) => ({ metric, value })), ["metric", "value"]);

  const report = `# Playwright / Visual Inquisition Audit\n\n` +
    `Profile: ${policy.profile}\n\n` +
    `Base URL: ${args.base}\n\n` +
    `Repo: ${repoRoot}\n\n` +
    `Git HEAD: ${(gitHead.stdout || "").trim()}\n\n` +
    `## Evidence policy\n\n` +
    `- Key screenshots: ${policy.keyType}\n` +
    `- Bulk screenshots: ${policy.bulkType} quality ${policy.jpegQuality}\n` +
    `- Tables: CSV\n` +
    `- Truth: JSON\n` +
    `- Source writes: none\n\n` +
    `## Data Atlas facts\n\n` +
    `- Entities: ${atlasSummary.entities_total ?? "unknown"}\n` +
    `- Dirty: ${atlasSummary.dirty_total ?? "unknown"}\n` +
    `- Critical: ${atlasSummary.critical_total ?? "unknown"}\n` +
    `- Duplicate groups: ${atlasSummary.duplicate_groups_total ?? "unknown"}\n` +
    `- Source/runtime leaks: ${atlasSummary.source_runtime_leaks_total ?? "unknown"}\n\n` +
    `## Browser/UX facts\n\n` +
    `- Screenshots: ${screenshotRows.length}\n` +
    `- Navigation rows: ${navigationRows.length}\n` +
    `- Pain points: ${painRows.length}\n` +
    `- Console messages: ${browserEvents.console.length}\n` +
    `- HTTP response errors: ${browserEvents.response_errors.length}\n\n` +
    `## Owner note\n\n` +
    `Это штатный Visual Inquisition bundle: он не чистит файлы, не коммитит, не пушит. Его задача — собрать карту видимости, боли UI/UX и сверку UI/API/git truth.\n`;
  writeText(path.join(dirs.report, "OWNER_READABLE_AUDIT_RU.md"), report);

  manifest.status = painRows.some(p => p.severity === "WARN") ? "PASS_WITH_WARNINGS" : "PASS";
  manifest.finished_at_utc = new Date().toISOString();
  manifest.summary = {
    screenshots: screenshotRows.length,
    navigation_rows: navigationRows.length,
    pain_points: painRows.length,
    console_messages: browserEvents.console.length,
    response_errors: browserEvents.response_errors.length,
    output_root: out,
    owner_report: path.join(dirs.report, "OWNER_READABLE_AUDIT_RU.md"),
  };
  writeJson(path.join(out, "MANIFEST.json"), manifest);
  await browser.close();

  const result = {
    status: manifest.status,
    surface: SURFACE,
    version: VERSION,
    profile: policy.profile,
    output_root: out,
    owner_report: path.join(dirs.report, "OWNER_READABLE_AUDIT_RU.md"),
    screenshot_manifest: path.join(dirs.csv, "screenshot_manifest.csv"),
    pain_map: path.join(dirs.csv, "pain_map.csv"),
    navigation_map: path.join(dirs.csv, "navigation_map.csv"),
    evidence_policy: manifest.evidence_policy,
    summary: manifest.summary,
  };
  console.log(JSON.stringify(result, null, 2));
}

main().catch((err) => {
  console.error(JSON.stringify({ status: "FAIL", surface: SURFACE, error: err.stack || err.message }, null, 2));
  process.exit(1);
});

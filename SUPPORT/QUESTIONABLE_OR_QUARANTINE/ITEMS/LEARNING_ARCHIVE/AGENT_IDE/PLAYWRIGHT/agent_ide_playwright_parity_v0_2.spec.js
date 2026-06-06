const { test, expect } = require("@playwright/test");
const fs = require("fs");
const path = require("path");

const baseUrl = process.env.AGENT_IDE_BASE_URL || "http://127.0.0.1:4173";
const screenshotDir = process.env.AGENT_IDE_SCREENSHOT_DIR || "";
const markerSnapshotPath = process.env.AGENT_IDE_MARKER_SNAPSHOT_PATH || "";

const panels = [
  { name: "overview", selector: "#overview" },
  { name: "organs", selector: "#organs" },
  { name: "file_atlas", selector: "#file-atlas" },
  { name: "viewer", selector: "#viewer" },
  { name: "officio_language_gate", selector: "#officio-language-gate" },
  { name: "owner_pain_map", selector: "#owner-pain-map" },
  { name: "routes", selector: "#routes" },
  { name: "reports", selector: "#reports" },
  { name: "checks", selector: "#checks" },
  { name: "block_foundation", selector: "#block-foundation" },
  { name: "plugins", selector: "#plugins" },
];

async function collectTruthParity(page) {
  return await page.evaluate(async () => {
    const markerNames = [
      "organ-count",
      "passport-count",
      "unknown-file-kind-count",
      "owner-pain-count",
      "route-alias",
      "current-head",
      "self-validator-verdict",
    ];

    const dom = {};
    for (const name of markerNames) {
      const el = document.querySelector(`[data-truth="${name}"]`);
      dom[name] = el ? String(el.textContent || "").trim() : "";
    }

    const model = await fetch("/api/view-model", { cache: "no-store" }).then((r) => r.json());
    const expected = {
      "organ-count": String((model.organs || []).length),
      "passport-count": String(model.atlas_summary?.passport_count ?? 0),
      "unknown-file-kind-count": String(model.atlas_summary?.unknown_file_kind_count ?? 0),
      "owner-pain-count": String(model.owner_pain_surface?.pain_count ?? 0),
      "route-alias": String(model.truth?.required_route_alias || "imperium-vm3"),
      "current-head": String(model.truth?.git?.head || "UNKNOWN"),
      "self-validator-verdict": String(model.self_validator_surface?.status || "UNPROVEN"),
    };

    const mismatches = [];
    for (const key of Object.keys(expected)) {
      if (dom[key] !== expected[key]) {
        mismatches.push(`${key}: dom=${dom[key]} expected=${expected[key]}`);
      }
    }

    return { dom, expected, mismatches };
  });
}

test("Agent IDE parity markers and panel screenshots", async ({ page }) => {
  await page.goto(baseUrl, { waitUntil: "networkidle" });
  await page.waitForSelector('[data-truth="organ-count"]', { timeout: 20000 });

  const parity = await collectTruthParity(page);
  expect(parity.mismatches, "DOM truth marker mismatches").toEqual([]);

  if (screenshotDir) {
    fs.mkdirSync(screenshotDir, { recursive: true });
  }

  for (const panel of panels) {
    const locator = page.locator(panel.selector).first();
    await expect(locator).toBeVisible();
    if (screenshotDir) {
      await locator.screenshot({ path: path.join(screenshotDir, `${panel.name}.png`) });
    }
  }

  if (markerSnapshotPath) {
    fs.mkdirSync(path.dirname(markerSnapshotPath), { recursive: true });
    fs.writeFileSync(markerSnapshotPath, JSON.stringify(parity, null, 2), "utf-8");
  }
});

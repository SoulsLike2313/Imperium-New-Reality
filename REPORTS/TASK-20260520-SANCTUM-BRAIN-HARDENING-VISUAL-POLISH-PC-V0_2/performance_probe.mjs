import { chromium } from "playwright";
import fs from "node:fs";
import path from "node:path";

const baseUrl = process.argv[2] || "http://127.0.0.1:8876";
const outPath = process.argv[3] || path.resolve("PERFORMANCE_PROBE.json");

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
const page = await context.newPage();

const navStart = Date.now();
await page.goto(baseUrl, { waitUntil: "domcontentloaded" });
await page.waitForSelector("#brainZoneMap", { timeout: 20000 });
await page.waitForTimeout(1200);

const metrics = await page.evaluate(async () => {
  const nav = performance.getEntriesByType("navigation")[0];
  const paints = performance.getEntriesByType("paint");

  const sampleFrames = 180;
  const deltas = [];
  let prev = performance.now();
  await new Promise((resolve) => {
    let frames = 0;
    const tick = (ts) => {
      deltas.push(ts - prev);
      prev = ts;
      frames += 1;
      if (frames >= sampleFrames) {
        resolve();
        return;
      }
      requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  });

  const valid = deltas.filter((x) => x > 0);
  const avgMs = valid.reduce((a, b) => a + b, 0) / Math.max(valid.length, 1);
  const fps = 1000 / avgMs;
  const sorted = [...valid].sort((a, b) => a - b);
  const p95 = sorted[Math.floor(sorted.length * 0.95)] || 0;

  return {
    navigation: nav
      ? {
          domContentLoadedMs: Math.round(nav.domContentLoadedEventEnd),
          loadEventEndMs: Math.round(nav.loadEventEnd),
          transferSize: nav.transferSize,
          encodedBodySize: nav.encodedBodySize,
          decodedBodySize: nav.decodedBodySize,
        }
      : null,
    paints: paints.map((p) => ({ name: p.name, startTimeMs: Number(p.startTime.toFixed(2)) })),
    raf_sample: {
      frames: valid.length,
      avg_frame_ms: Number(avgMs.toFixed(3)),
      approx_fps: Number(fps.toFixed(2)),
      p95_frame_ms: Number(p95.toFixed(3)),
    },
  };
});

const report = {
  schema_version: "SANCTUM_BRAIN_PERFORMANCE_PROBE_V0_1",
  generated_at_utc: new Date().toISOString(),
  base_url: baseUrl,
  wall_clock_probe_ms: Date.now() - navStart,
  metrics,
};

fs.writeFileSync(outPath, JSON.stringify(report, null, 2));
console.log(JSON.stringify({ outPath, approx_fps: report.metrics.raf_sample.approx_fps }, null, 2));

await browser.close();

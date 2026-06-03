import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { chromium } from "playwright";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const foundryRoot = path.resolve(__dirname, "..");
const conceptRoot = path.resolve(foundryRoot, "CONCEPT_STRIKE");
const screenshotRoot = path.resolve(conceptRoot, "SCREENSHOTS");

const concepts = [
  { id: "A", folder: "CONCEPT_A_NEURAL_THRONE_CORE" },
  { id: "B", folder: "CONCEPT_B_MECHANICUS_FORGE_CORTEX" },
  { id: "C", folder: "CONCEPT_C_HOLOGRAPH_COMMAND_SPINE" },
  { id: "D", folder: "CONCEPT_D_SECOND_MIND_WAR_ROOM" },
  { id: "E", folder: "CONCEPT_E_LIVING_ORGAN_MAP" }
];

async function main() {
  await fs.mkdir(screenshotRoot, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  const allFiles = [];

  for (const concept of concepts) {
    const htmlPath = path.resolve(conceptRoot, concept.folder, "index.html");
    const url = pathToFileURL(htmlPath).href;

    await page.goto(url);
    await page.waitForTimeout(450);

    await page.setViewportSize({ width: 1366, height: 768 });
    await page.waitForTimeout(250);
    const out1366 = `${concept.id}_1366x768.png`;
    await page.screenshot({ path: path.resolve(screenshotRoot, out1366), fullPage: true });
    allFiles.push(out1366);

    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.waitForTimeout(250);
    const out1920 = `${concept.id}_1920x1080.png`;
    await page.screenshot({ path: path.resolve(screenshotRoot, out1920), fullPage: true });
    allFiles.push(out1920);
  }

  const index = {
    generated_at_utc: new Date().toISOString(),
    concept_count: concepts.length,
    viewports: ["1366x768", "1920x1080"],
    files: allFiles
  };

  await fs.writeFile(path.resolve(screenshotRoot, "screenshot_index.json"), `${JSON.stringify(index, null, 2)}\n`, "utf8");

  await browser.close();
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

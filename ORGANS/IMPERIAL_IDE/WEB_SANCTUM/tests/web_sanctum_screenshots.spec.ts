import { test, expect } from '@playwright/test';

const pages = [['sanctum', 'nav-sanctum', 'page-sanctum'], ['warp', 'nav-warp', 'page-warp'], ['register', 'nav-register', 'page-register'], ['astronomicon', 'nav-astronomicon', 'page-astronomicon'], ['mechanicus', 'nav-mechanicus', 'page-mechanicus'], ['jobs', 'nav-jobs', 'page-jobs'], ['stage', 'nav-stage', 'page-stage'], ['hygiene', 'nav-hygiene', 'page-hygiene'], ['validation', 'nav-validation', 'page-validation'], ['reports', 'nav-reports', 'page-reports'], ['promotion', 'nav-promotion', 'page-promotion'], ['playwright', 'nav-playwright', 'page-playwright']] as const;
const screenshotRoot = process.env.IMPERIUM_PLAYWRIGHT_OUTPUT_ROOT || 'E:/IMPERIUM_LOCAL_HANDOFF/SERVITOR_OUTPUTS/H-TASK-NEWREALITY-PC-SERVITOR-WARP-RUNTIME-FULL-STAGE-LOOP-V0_8_1/playwright';

test('collect owner-visible Web Sanctum v0.8.1 screenshots', async ({ page }) => {
  await page.goto('/');
  await page.waitForFunction(() => (window as any).__SANCTUM_READY === true);
  for (const [name, nav, panel] of pages) {
    await page.getByTestId(nav).click();
    await expect(page.getByTestId(panel)).toBeVisible();
    await page.waitForTimeout(200);
    await page.screenshot({ path: `${screenshotRoot}/screenshots/v081-stage-loop-${name}.png`, fullPage: true });
  }
});

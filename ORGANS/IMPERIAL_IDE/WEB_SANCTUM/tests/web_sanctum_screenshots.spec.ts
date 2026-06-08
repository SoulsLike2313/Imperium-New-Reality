import { test, expect } from '@playwright/test';
const pages = [['sanctum','nav-sanctum','page-sanctum'],['warp','nav-warp','page-warp'],['register','nav-register','page-register'],['astronomicon','nav-astronomicon','page-astronomicon'],['mechanicus','nav-mechanicus','page-mechanicus'],['validation','nav-validation','page-validation'],['reports','nav-reports','page-reports'],['playwright','nav-playwright','page-playwright']] as const;
test('collect owner-visible Web Sanctum v0.5 screenshots', async ({ page }) => {
  await page.goto('/'); await page.waitForFunction(() => (window as any).__SANCTUM_READY === true);
  for (const [name, nav, panel] of pages) {
    await page.getByTestId(nav).click(); await expect(page.getByTestId(panel)).toBeVisible(); await page.waitForTimeout(200);
    await page.screenshot({ path: `test-results/screenshots/v050-operational-spine-${name}.png`, fullPage: true });
  }
});

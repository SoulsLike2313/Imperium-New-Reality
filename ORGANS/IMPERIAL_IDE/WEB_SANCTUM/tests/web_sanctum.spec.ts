import { test, expect } from '@playwright/test';
async function ready(page:any){ await page.goto('/'); await page.waitForFunction(() => (window as any).__SANCTUM_READY === true); }

test('web sanctum v0.5 opens operational spine', async ({ page }) => {
  await ready(page);
  await expect(page.getByRole('heading', { name: 'IMPERIAL SANCTUM' })).toBeVisible();
  await expect(page.getByTestId('version-pill')).toContainText('V0.5');
  await expect(page.getByTestId('contour')).toContainText(/H_CONTOUR|MAIN_OR_UNKNOWN/);
  await expect(page.getByTestId('create-warp')).toBeVisible();
  await expect(page.getByTestId('export-task-template')).toBeVisible();
});

test('navigation covers WARP, task registration, organs, validation and reports', async ({ page }) => {
  await ready(page);
  for (const [nav,panel] of [['nav-warp','page-warp'],['nav-register','page-register'],['nav-astronomicon','page-astronomicon'],['nav-mechanicus','page-mechanicus'],['nav-validation','page-validation'],['nav-reports','page-reports'],['nav-playwright','page-playwright']] as const) {
    await page.getByTestId(nav).click(); await expect(page.getByTestId(panel)).toBeVisible();
  }
  await expect(page.getByTestId('page-register')).toBeHidden();
});

test('command palette deterministic page navigation and quality modes', async ({ page }) => {
  await ready(page);
  await page.keyboard.press('Control+K');
  await expect(page.getByTestId('command-palette')).toBeVisible();
  await page.locator('#paletteSearch').fill('mechanicus');
  await expect(page.locator('#paletteList .paletteItem').first()).toContainText(/Go Mechanicus/i);
  await page.locator('#paletteSearch').press('Enter');
  await expect(page.getByTestId('page-mechanicus')).toBeVisible();
  await page.getByTestId('quality-button').click(); await expect(page.getByTestId('contour')).toContainText(/Balanced/);
  await page.getByTestId('quality-button').click(); await expect(page.getByTestId('contour')).toContainText(/Cinematic/);
});

test('read-only bridge blocks arbitrary action surface', async ({ page, request }) => {
  await ready(page);
  const health = await request.get('/api/health'); expect(health.ok()).toBeTruthy();
  const data = await health.json(); expect(data.status).toBe('PASS'); expect(data.actions_enabled).toBeFalsy();
  await page.getByTestId('create-warp').click(); await expect(page.getByTestId('toast')).toContainText(/actions disabled|command copied/i);
});

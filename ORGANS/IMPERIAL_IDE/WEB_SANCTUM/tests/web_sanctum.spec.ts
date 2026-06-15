import { test, expect } from '@playwright/test';

async function ready(page: any) {
  await page.goto('/');
  await page.waitForFunction(() => (window as any).__SANCTUM_READY === true);
}

test('web sanctum v0.8.3 opens full stage loop and data atlas surface', async ({ page }) => {
  await ready(page);
  await expect(page.getByRole('heading', { name: 'IMPERIAL SANCTUM' })).toBeVisible();
  await expect(page.getByTestId('version-pill')).toContainText(/V0.8.3/);
  await expect(page.getByTestId('contour')).toContainText(/WARP_CONTOUR|H_CONTOUR|MAIN_OR_UNKNOWN/);
  await expect(page.getByTestId('create-warp')).toBeVisible();
  await expect(page.getByTestId('nav-jobs')).toBeVisible();
  await expect(page.getByTestId('nav-atlas')).toBeVisible();
});

test('navigation covers WARP, task registration, stage loop, hygiene, data atlas, validation, reports and promotion preview', async ({ page }) => {
  await ready(page);
  for (const [nav, panel] of [['nav-warp', 'page-warp'], ['nav-register', 'page-register'], ['nav-astronomicon', 'page-astronomicon'], ['nav-mechanicus', 'page-mechanicus'], ['nav-jobs', 'page-jobs'], ['nav-stage', 'page-stage'], ['nav-hygiene', 'page-hygiene'], ['nav-atlas', 'page-atlas'], ['nav-validation', 'page-validation'], ['nav-reports', 'page-reports'], ['nav-promotion', 'page-promotion'], ['nav-playwright', 'page-playwright']] as const) {
    await page.getByTestId(nav).click();
    await expect(page.getByTestId(panel)).toBeVisible();
  }
  await expect(page.getByTestId('page-register')).toBeHidden();
  await expect(page.getByTestId('page-hygiene')).toBeHidden();
});

test('WARP page exposes identity, active task, stage and dirty status', async ({ page }) => {
  await ready(page);
  await page.getByTestId('nav-warp').click();
  await expect(page.getByTestId('warp-vitals')).toBeVisible();
  await expect(page.getByTestId('warp-id')).not.toHaveText('');
  await expect(page.getByTestId('warp-path')).toContainText(/IMPERIUM_WARPS|none/);
  await expect(page.getByTestId('warp-base')).not.toHaveText('');
  await expect(page.getByTestId('warp-current-stage')).not.toHaveText('');
  await expect(page.getByTestId('warp-dirty')).toContainText(/DIRTY|CLEAN|unknown/);
  await expect(page.getByTestId('copy-warp-path')).toBeVisible();
});

test('registration page exposes admission receipt summary fields', async ({ page }) => {
  await ready(page);
  await page.getByTestId('nav-register').click();
  await expect(page.getByTestId('admission-summary')).toBeVisible();
  await expect(page.locator('#admissionVerdict')).toContainText(/NOT_RUN|PASS|BLOCKED|FAIL/);
  await expect(page.getByTestId('task-zip-path')).toBeVisible();
  await expect(page.getByTestId('register-taskpack-pc')).toBeVisible();
});

test('command palette deterministic page navigation and quality modes', async ({ page }) => {
  await ready(page);
  await page.keyboard.press('Control+K');
  await expect(page.getByTestId('command-palette')).toBeVisible();
  await page.locator('#paletteSearch').fill('jobs');
  await expect(page.locator('#paletteList .paletteItem').first()).toContainText(/Go Jobs/i);
  await page.locator('#paletteSearch').press('Enter');
  await expect(page.getByTestId('page-jobs')).toBeVisible();
  await page.getByTestId('quality-button').click();
  await expect(page.getByTestId('contour')).toContainText(/Balanced/);
  await page.getByTestId('quality-button').click();
  await expect(page.getByTestId('contour')).toContainText(/Cinematic/);
});

test('read-only bridge exposes action metadata and blocks execution', async ({ page, request }) => {
  await ready(page);
  const health = await request.get('/api/health');
  expect(health.ok()).toBeTruthy();
  const data = await health.json();
  expect(data.status).toBe('PASS');
  expect(data.job_runner).toBeTruthy();
  expect(data.actions_enabled).toBeFalsy();
  const actions = await (await request.get('/api/actions')).json();
  expect(actions.actions.start_work.allowed_write_roots).toContain('E:/IMPERIUM_LOCAL_HANDOFF/WARP_RUNS');
  await page.getByTestId('create-warp').click();
  await expect(page.getByTestId('toast')).toContainText(/actions disabled|read-only/i);
});


test('stage control and promotion preview controls are visible and safe', async ({ page, request }) => {
  await ready(page);
  await page.getByTestId('nav-stage').click();
  await expect(page.getByTestId('page-stage')).toBeVisible();
  await expect(page.getByTestId('stage-start-current')).toBeVisible();
  await expect(page.getByTestId('stage-submit-evidence')).toBeVisible();
  await expect(page.getByTestId('stage-run-gate')).toBeVisible();
  await expect(page.getByTestId('stage-close-stage')).toBeVisible();
  await page.getByTestId('nav-promotion').click();
  await expect(page.getByTestId('page-promotion')).toBeVisible();
  await expect(page.getByTestId('promotion-preview-run')).toBeVisible();
  await expect(page.getByTestId('promotion-route')).toBeVisible();
  const actions = await (await request.get('/api/actions')).json();
  expect(actions.actions.promotion_preview.safety).toContain('NO_COMMIT');
  expect(actions.actions.stage_run_gate.arbitrary_shell).toBeFalsy();
});


test('runtime hygiene and node probe controls are visible and read-safe', async ({ page, request }) => {
  await ready(page);
  await page.getByTestId('nav-hygiene').click();
  await expect(page.getByTestId('page-hygiene')).toBeVisible();
  await expect(page.getByTestId('runtime-hygiene-scan')).toBeVisible();
  await expect(page.getByTestId('node-probe')).toBeVisible();
  const actions = await (await request.get('/api/actions')).json();
  expect(actions.actions.runtime_hygiene_scan.safety).toContain('SCAN');
  expect(actions.actions.data_atlas_scan.safety).toContain('READ_ONLY');
  expect(actions.actions.data_atlas_scan.arbitrary_shell).toBeFalsy();
  expect(actions.actions.node_probe.arbitrary_shell).toBeFalsy();
});

test('data atlas exposes owner-visible file map, dirt and passport drawer', async ({ page, request }) => {
  await ready(page);
  await page.getByTestId('nav-atlas').click();
  await expect(page.getByTestId('page-atlas')).toBeVisible();
  await expect(page.getByTestId('atlas-kpis')).toBeVisible();
  await expect(page.getByTestId('atlas-organ-map')).toBeVisible();
  await expect(page.getByTestId('atlas-explorer')).toBeVisible();
  await expect(page.getByTestId('atlas-passport-trace')).toBeVisible();
  await expect(page.getByTestId('atlas-cleanup-lanes')).toBeVisible();
  await expect(page.getByTestId('atlas-lifecycle-matrix')).toBeVisible();
  const atlas = await (await request.get('/api/data-atlas')).json();
  expect(atlas.status).toMatch(/PASS|PASS_WITH_WARNINGS/);
  expect(atlas.summary.entities_total).toBeGreaterThan(0);
  expect(atlas.entities.length).toBeGreaterThan(0);
});

import { defineConfig, devices } from '@playwright/test';

const outputRoot = process.env.IMPERIUM_PLAYWRIGHT_OUTPUT_ROOT || 'E:/IMPERIUM_LOCAL_HANDOFF/SERVITOR_OUTPUTS/H-TASK-NEWREALITY-PC-SERVITOR-WARP-RUNTIME-FULL-STAGE-LOOP-V0_8_1/playwright';

export default defineConfig({
  testDir: './tests',
  timeout: 45000,
  expect: { timeout: 12000 },
  outputDir: `${outputRoot}/test-results`,
  reporter: [['html', { open: 'never', outputFolder: `${outputRoot}/report` }], ['list']],
  use: { baseURL: 'http://127.0.0.1:8799', trace: 'retain-on-failure', screenshot: 'only-on-failure', video: 'retain-on-failure' },
  webServer: { command: 'python ./tools/local_bridge.py --repo-root ../../.. --port 8799', url: 'http://127.0.0.1:8799/api/health', reuseExistingServer: false, timeout: 20000 },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
});

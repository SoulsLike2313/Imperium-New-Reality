import { defineConfig, devices } from '@playwright/test';
export default defineConfig({
  testDir: './tests',
  timeout: 30000,
  expect: { timeout: 10000 },
  reporter: [['html', { open: 'never' }], ['list']],
  use: { baseURL: 'http://127.0.0.1:8798', trace: 'retain-on-failure', screenshot: 'only-on-failure', video: 'retain-on-failure' },
  webServer: { command: 'python ./tools/local_bridge.py --repo-root ../../.. --port 8798', url: 'http://127.0.0.1:8798', reuseExistingServer: false, timeout: 15000 },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }]
});

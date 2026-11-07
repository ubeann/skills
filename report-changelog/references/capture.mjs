#!/usr/bin/env node
// capture.mjs: screenshot every screen a change touches, for one changelog entry.
//   node <entry>/capture.mjs before|after
// Copy this into the entry folder as capture.mjs and fill SCREENS; it is committed with the entry so the
// shots can be retaken. Run it from a folder where playwright-core is installed (the project root, or the
// scratchpad). The app URL, the seeded login and the seeded records come from the project's agent doc.
import { mkdirSync, existsSync, readdirSync } from 'node:fs';
import { createRequire } from 'node:module';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { homedir } from 'node:os';

const here = dirname(fileURLToPath(import.meta.url));
const phase = process.argv[2];
if (!['before', 'after'].includes(phase)) { console.error('usage: node capture.mjs before|after'); process.exit(1); }

const APP = process.env.APP_URL ?? 'http://127.0.0.1:8000';
const LOGIN = { url: '/login', email: process.env.SHOT_EMAIL, password: process.env.SHOT_PASSWORD };

// One entry per screen. `expect` is the text that proves the crop holds the change: the old string
// before, the new one after. A crop that misses it fails here instead of in someone's eyes later.
// `act` drives the page into the state to show (open a tab, add a row, fill a field); it runs in both phases,
// so write it against what both versions share (roles, ids, field names) rather than the text being changed.
const SCREENS = [
  {
    name: '01-form-empty',
    path: '/invoices/SEEDED-ID/settle',
    locate: (page) => page.locator('section').filter({ hasText: 'Billing Details' }).last(),
    expect: { before: 'Vendor Lines', after: 'Shipment Lines' },
  },
  {
    name: '02-form-one-line',
    path: '/invoices/SEEDED-ID/settle',
    act: async (page) => {
      await page.locator('[data-test="add-line"]').click();
      await page.locator('input[id$="unit_price"]').first().fill('1500000');
    },
    locate: (page) => page.locator('section').filter({ hasText: 'Billing Details' }).last(),
    expect: { before: 'Vendor Total', after: 'Shipment Lines Total' },
  },
];

const require = createRequire(join(process.cwd(), 'noop.js'));
const { chromium } = require('playwright-core');
async function launch() {
  if (process.env.CHROME_PATH) return chromium.launch({ executablePath: process.env.CHROME_PATH });
  try { return await chromium.launch({ channel: 'chrome' }); } catch {}
  const cache = join(homedir(), 'Library/Caches/ms-playwright');
  const shell = existsSync(cache) && readdirSync(cache).filter((d) => d.startsWith('chromium_headless_shell-')).sort().pop();
  if (!shell) throw new Error('no Chrome found: install Google Chrome or set CHROME_PATH');
  const sub = readdirSync(join(cache, shell)).find((x) => x.startsWith('chrome-headless-shell'));
  return chromium.launch({ executablePath: join(cache, shell, sub, 'chrome-headless-shell') });
}

const out = join(here, 'shots', phase);
mkdirSync(out, { recursive: true });
const browser = await launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 2 });
if (LOGIN.email) {
  await page.goto(APP + LOGIN.url);
  await page.fill('input[type=email]', LOGIN.email);
  await page.fill('input[type=password]', LOGIN.password);
  await page.click('button[type=submit]');
  await page.waitForURL((u) => !u.pathname.startsWith(LOGIN.url));
}
const failed = [];
for (const s of SCREENS) {
  await page.goto(APP + s.path, { waitUntil: 'networkidle' });
  if (s.act) await s.act(page);
  await page.waitForTimeout(500);
  const el = s.locate(page);
  await el.scrollIntoViewIfNeeded();
  const text = await el.innerText();
  if (!text.includes(s.expect[phase])) { failed.push(`${s.name}: the crop does not contain "${s.expect[phase]}"`); continue; }
  await el.screenshot({ path: join(out, `${s.name}.png`) });
  console.log(`✓ shots/${phase}/${s.name}.png`);
}
await browser.close();
if (failed.length) { console.error(failed.map((f) => `✗ ${f}`).join('\n')); process.exit(1); }

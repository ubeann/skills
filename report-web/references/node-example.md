# Node example

One implementation of the pipeline: a Node renderer, Playwright driving the installed Chrome, `node --test` gates. Treat it as a worked example, not the only shape.

## Layout

```
cmd/analysis/      slow pass; writes out/analysis/report.json
report-web/
  package.json     "type": "module"; scripts: render, check, test
  render.js        load JSON, write out/analysis/report-web.html; paths resolve from the script, not the cwd
  sections.js      one function per section, each returning a section.part string
  charts.js        SVG builders
  format.js        num, pct, rupiah and friends
  style.css        inlined by render.js
  web.js           inlined by render.js
  overflow-web.js  evaluated by check.js
  check.js         three widths: gate, then screenshot one section or the full page
  icons/           copied from the PDF renderer so this folder is self-contained
  test/            gates
```

Install Playwright without downloading a browser and use the Chrome already on the machine:

```sh
npm install --save-dev playwright
```

```js
const browser = await chromium.launch({ channel: 'chrome' });
```

## Check with the overflow gate

```js
// check.js: node check.js [section-id | --full] [--out dir]
// Exits non-zero when any width has an element wider than the viewport or clipped text.
import { readFileSync } from 'node:fs';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { dirname } from 'node:path';
import { chromium } from 'playwright';

const WIDTHS = { laptop: 1280, tablet: 768, phone: 375 };
const here = dirname(fileURLToPath(import.meta.url));
const overflowJS = readFileSync(`${here}/overflow-web.js`, 'utf8');
const args = process.argv.slice(2);
const arg = (name, def) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : def; };
const file = pathToFileURL(arg('--file', `${here}/../out/analysis/report-web.html`)).href;
const outDir = arg('--out', '/tmp');
const full = args.includes('--full');
const id = args.find(a => !a.startsWith('--') && a !== arg('--out') && a !== arg('--file'));

const browser = await chromium.launch({ channel: 'chrome' });
let failed = false;
for (const [name, width] of Object.entries(WIDTHS)) {
  const page = await browser.newPage({ viewport: { width, height: 900 } });
  await page.goto(file);
  const overflow = JSON.parse(await page.evaluate(overflowJS));
  if (overflow.length) {
    failed = true;
    console.error(`${name} (${width}px): ${overflow.length} element(s) leave the viewport or clip text\n` + JSON.stringify(overflow, null, 1));
  } else {
    console.log(`${name} (${width}px): overflow gate clean`);
  }
  if (id) await page.locator('#' + id).screenshot({ path: `${outDir}/${id}-${name}.png` });
  if (full) await page.screenshot({ path: `${outDir}/report-web-${width}.png`, fullPage: true });
  await page.close();
}
await browser.close();
process.exit(failed ? 1 : 0);
```

The script returns a JSON string, so `evaluate` gives a string to parse. Print it raw on failure; the `part` and `el` fields point at the offender and `text` matches it to the PNG.

## Gates as tests

```js
// test/render.test.js
import test from 'node:test';
import assert from 'node:assert/strict';
import { render } from '../render.js';
import { num, pct, rupiah } from '../format.js';
import { fixture } from './fixture.js';

test('formatters', () => {
  for (const [got, want] of [
    [num(2984202), '2.984.202'],
    [num(-1500), '-1.500'],
    [pct(0.2043, 1), '20,4%'],
    [pct(0.0000003, 2), '<0,01%'],
    [pct(0.99998, 1), '>99,9%'],
    [rupiah(65_100_000_000_000), 'Rp 65,1 T'],
  ]) assert.equal(got, want);
});

test('render', () => {
  const html = render(fixture());
  const content = html.replace(/<script>[\s\S]*?<\/script>/g, ''); // banned strings are about what the reader sees
  const ids = [...html.matchAll(/<section class="part" id="([^"]+)"/g)].map(m => m[1]);
  assert.equal(ids.length, 9);
  assert.equal(new Set(ids).size, ids.length);
  const targets = new Set([...ids, 'awal']); // the head's id
  for (const [, href] of html.matchAll(/href="#([^"]+)"/g)) assert.ok(targets.has(href), `link to #${href}`);
  for (const want of ['14 Oktober 2026', 'Rp 3,0 T', 'Rencana &lt;Rp 0&gt;']) assert.ok(html.includes(want), want);
  for (const bad of ['NaN', 'Inf', 'undefined', '[object Object]']) assert.ok(!content.includes(bad), `contains ${bad}`);
  for (const bad of ['<script src', '<link rel="stylesheet"', 'src="http', 'url(http', 'type="module"', 'fetch(']) assert.ok(!html.includes(bad), `not one file: ${bad}`);
  const tips = html.match(/data-tip="/g)?.length ?? 0;
  assert.equal(html.match(/data-tip="[^"]*" tabindex="0"/g)?.length ?? 0, tips, 'a tip without tabindex');
});
```

Write the fixture so that every sentinel is a value the section computes from it, with the arithmetic in a comment beside the fixture field. A sentinel copied from real output tests nothing.

## Section function comment

```js
// realisasi is the section "Realisasi", id "realisasi": investment by quarter, 2025 vs 2026.
export function realisasi(d) {
```

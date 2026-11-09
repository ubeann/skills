#!/usr/bin/env node
// render.mjs: render one changelog entry from its changelog.json.
//   node <skill>/references/render.mjs <entry-dir> [--pdf] [--context] [--lang en,id] [--no-png]
// Run it from a folder where playwright-core (or playwright) is installed; it drives the installed Chrome,
// or the newest Playwright headless shell, or $CHROME_PATH. It writes README.md in the entry and the
// outputs under <entry>/out/<lang>/, and exits non-zero when a gate fails. The context (with its evidence)
// always goes into README.md, the repository's record; the outputs carry it only with --context.
// One layout feeds both outputs: the sections are packed in order into pages of PAGE_H, and each page is
// one album image and one PDF page, so the PDF reads exactly like the album.
import { readFileSync, writeFileSync, mkdirSync, existsSync, readdirSync } from 'node:fs';
import { createRequire } from 'node:module';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { homedir } from 'node:os';

const here = dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const valued = ['--lang'];
const opt = (n) => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : undefined; };
// `--pdf portrait|landscape` from before the shared layout still works; the value is ignored.
const legacy = ['portrait', 'landscape'];
const entryDir = resolve(args.find((a, i) => !a.startsWith('--') && !valued.includes(args[i - 1]) && !legacy.includes(a)) ?? '.');
const entry = JSON.parse(readFileSync(join(entryDir, 'changelog.json'), 'utf8'));
const withPdf = args.includes('--pdf');
const withContext = args.includes('--context');
const langs = (opt('--lang') ?? (entry.langs ?? []).join(',')).split(',').filter(Boolean);

const TYPES = ['copy', 'ui', 'fix', 'feature'];
// The layout width in CSS px, close to the 1440 px viewport capture.mjs shoots at, so a screenshot shows near
// its captured size. A page is A4-proportioned at that width: one album image (1.5x, so at most ~2970 px tall,
// a size chat apps send sharp) and one PDF page. SHOT_DPR is capture.mjs's deviceScaleFactor.
const WIDTH = 1400;
const PAGE_H = Math.round(WIDTH * 297 / 210);
const SHOT_DPR = 2;
// Gate 3: a screenshot shown below this share of its captured size has app text under ~7pt.
const MIN_SCALE = 0.5;
// A before/after pair sits side by side only when both shots keep this share of their size; otherwise it stacks.
const PAIR_SCALE = 0.75;
const LABELS = {
  en: {
    before: 'Before', after: 'After', now: 'New', where: 'Where', steps: 'How to use it', changes: 'Changes',
    types: { copy: 'Copy update', ui: 'UI update', fix: 'Bug fix', feature: 'New feature' },
    context: 'Context', background: 'Background', reason: 'Reason', source: 'Source', people: 'People',
    decisions: 'Decisions', scope: 'Scope', verification: 'Verification', unchanged: 'Not changed',
    risks: 'Risks', followups: 'Follow-ups', rollback: 'Rollback', evidence: 'Evidence', chosen: 'chosen', over: 'over', by: 'by',
    why: 'Why', shipped: 'What shipped', open: 'Still open', pr: 'PR', branch: 'Branch', commits: 'Commits', files: 'Files', alternatives: 'Considered', more: 'more', folders: 'folders', fileCount: 'files',
  },
  id: {
    before: 'Sebelum', after: 'Sesudah', now: 'Baru', where: 'Lokasi', steps: 'Cara pakai', changes: 'Perubahan',
    types: { copy: 'Perubahan teks', ui: 'Perubahan tampilan', fix: 'Perbaikan bug', feature: 'Fitur baru' },
    context: 'Konteks', background: 'Latar belakang', reason: 'Alasan', source: 'Sumber', people: 'Pihak terkait',
    decisions: 'Keputusan', scope: 'Cakupan', verification: 'Verifikasi', unchanged: 'Tidak berubah',
    risks: 'Risiko', followups: 'Tindak lanjut', rollback: 'Rollback', evidence: 'Bukti', chosen: 'dipilih', over: 'dibanding', by: 'oleh',
    why: 'Alasan perubahan', shipped: 'Yang dirilis', open: 'Masih terbuka', pr: 'PR', branch: 'Branch', commits: 'Commit', files: 'File', alternatives: 'Opsi lain', more: 'lainnya', folders: 'folder', fileCount: 'file',
  },
};
const labels = (lang) => ({ ...LABELS.en, ...(LABELS[lang] ?? {}), ...(entry.labels?.[lang] ?? {}) });

// Gate 1: the entry is complete and every screenshot exists.
const errors = [];
const need = (cond, msg) => { if (!cond) errors.push(msg); };
need(/^\d{4}-\d{2}-\d{2}$/.test(entry.date ?? ''), 'date must be YYYY-MM-DD');
need(entry.slug, 'slug is missing');
need(TYPES.includes(entry.type), `type must be one of ${TYPES.join(', ')}`);
need(langs.length, 'langs is empty');
need(entry.sections?.length, 'sections is empty');
for (const lang of langs) {
  need(entry.head?.[lang]?.title, `head.${lang}.title is missing`);
  (entry.sections ?? []).forEach((s, i) => need(s.text?.[lang]?.title, `sections[${i}].text.${lang}.title is missing`));
}
(entry.sections ?? []).forEach((s, i) => {
  const shots = s.kind === 'pair' ? [s.before, s.after] : s.kind === 'single' ? [s.shot] : [];
  need(['pair', 'single', 'table'].includes(s.kind), `sections[${i}].kind must be pair, single or table`);
  for (const p of shots) need(p && existsSync(join(entryDir, p)), `sections[${i}]: screenshot ${p} does not exist`);
  if (s.kind === 'table') for (const lang of langs) need(s.text?.[lang]?.rows?.length, `sections[${i}].text.${lang}.rows is empty`);
});
(entry.context?.evidence ?? []).forEach((e, i) => need(e.file && existsSync(join(entryDir, e.file)), `context.evidence[${i}]: ${e.file} does not exist`));
if (errors.length) fail(errors);

const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
// Inline markup: **bold** for the app's own labels, `code` for identifiers.
const md = (s) => esc(s).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>').replace(/`(.+?)`/g, '<code>$1</code>');
const titleHtml = (t) => typeof t === 'string' ? md(t) : `<span class="old">${esc(t.old)}</span><span class="arrow">→</span>${esc(t.new)}`;
const titleText = (t) => typeof t === 'string' ? t.replace(/\*\*/g, '') : `${t.old} → ${t.new}`;
const fmtDate = (d, lang) => new Intl.DateTimeFormat(lang, { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' }).format(new Date(d + 'T00:00:00Z'));
const caption = (e) => [e.what, e.from, e.date].filter(Boolean).join(' · ');
const list = (xs) => `<ul>${xs.map((x) => `<li>${md(x)}</li>`).join('')}</ul>`;

// Scope on a big change: the card shows at most LIMIT commits and LIMIT files; past that, files fold into
// their folders with a count. README.md keeps every commit and file, folded in <details>.
const LIMIT = 6;
const SCOPE = '\u0000scope';
const commit = (x) => typeof x === 'string' ? { sha: x } : x;
// A long path keeps its tail: "…/Invoices/Pages/" says more than "app/Filament/Resou…".
const short = (path, max = 44) => {
  if (path.length <= max) return path;
  const slash = path.endsWith('/') ? '/' : '';
  const parts = path.split('/').filter(Boolean);
  let tail = '';
  for (let i = parts.length - 1; i >= 0; i--) {
    const next = parts[i] + (tail ? '/' + tail : slash);
    if (tail && ('…/' + next).length > max) break;
    tail = next;
  }
  return '…/' + tail;
};
const counted = (label, n) => n > 1 ? `${label} (${n})` : label;
const commitsHtml = (cs, L) => cs.slice(0, LIMIT).map((c) => `<div class="commit"><code>${esc(c.sha.slice(0, 7))}</code>${c.subject ? `<span>${md(c.subject)}</span>` : ''}</div>`).join('')
  + (cs.length > LIMIT ? `<div class="muted">+${cs.length - LIMIT} ${esc(L.more)}</div>` : '');
function filesHtml(files, L) {
  if (files.length <= LIMIT) return files.map((f) => `<code class="file">${esc(short(f))}</code>`).join('');
  const dirs = new Map();
  for (const f of files) { const d = f.includes('/') ? f.slice(0, f.lastIndexOf('/') + 1) : './'; dirs.set(d, (dirs.get(d) ?? 0) + 1); }
  const sorted = [...dirs].sort((a, b) => b[1] - a[1]);
  return sorted.slice(0, LIMIT).map(([d, n]) => `<div class="dir"><code>${esc(short(d))}</code><span class="muted">${n} ${esc(L.fileCount)}</span></div>`).join('')
    + (sorted.length > LIMIT ? `<div class="muted">+${sorted.length - LIMIT} ${esc(L.folders)}</div>` : '');
}
// Header icons, inline so the report needs no network: one per group, never per field.
const svg = (d) => `<svg class="ic" viewBox="0 0 24 24" aria-hidden="true">${d}</svg>`;
const ICON = {
  people: svg('<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c0-3.6 2.9-6 6.5-6s6.5 2.4 6.5 6"/><circle cx="17" cy="9" r="2.5"/><path d="M16.5 14.2c2.8.3 5 2.4 5 5.8"/>'),
  source: svg('<path d="M4 5h16v11H9l-5 4z"/>'),
  shipped: svg('<circle cx="12" cy="12" r="3.5"/><path d="M3 12h5.5M15.5 12H21"/>'),
  rollback: svg('<path d="M9 14 4 9l5-5"/><path d="M4 9h10.5a5.5 5.5 0 0 1 0 11H11"/>'),
  open: svg('<path d="M12 3 2 20h20z"/><path d="M12 10v4.5M12 17.5v.01"/>'),
  evidence: svg('<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="10" r="2"/><path d="m21 16-5-5-9 9"/>'),
};

function contextRows(L) {
  const c = entry.context ?? {};
  const rows = [];
  const add = (label, html) => { if (html) rows.push([label, html]); };
  add(L.background, c.background && md(c.background));
  add(L.reason, c.reason && md(c.reason));
  add(L.source, c.source?.length && list(c.source.map((s) => [s.kind, s.ref, s.note].filter(Boolean).join(' · '))));
  add(L.people, c.people?.length && list(c.people.map((p) => `${p.role}: ${p.name}`)));
  add(L.decisions, c.decisions?.length && list(c.decisions.map((d) =>
    `${d.question} **${d.chosen}** ${L.chosen}${d.by ? ` ${L.by} ${d.by}` : ''}${d.options?.length ? `, ${L.over} ${d.options.join(', ')}` : ''}${d.why ? `. ${d.why}` : ''}`)));
  const sc = c.scope ?? {};
  add(L.scope, (sc.pr || sc.branch || sc.commits?.length || sc.files?.length) && SCOPE);
  add(L.verification, c.verification?.length && list(c.verification));
  add(L.unchanged, c.unchanged?.length && list(c.unchanged));
  add(L.risks, c.risks?.length && list(c.risks));
  add(L.followups, c.followups?.length && list(c.followups));
  add(L.rollback, c.rollback && md(c.rollback));
  for (const x of c.extra ?? []) add(esc(x.label), md(x.text));
  return rows;
}

// The context page: the story on the left (why, decisions, what was checked), the facts in a side column
// (people, source, scope, rollback), what is still open in a band below, then the evidence.
function contextHtml(L, crumbHtml) {
  const c = entry.context;
  const block = (label, body) => body ? `<div class="block"><h4>${esc(label)}</h4>${body}</div>` : '';
  const ul = (xs, cls = '') => xs?.length ? `<ul class="${cls}">${xs.map((x) => `<li>${md(x)}</li>`).join('')}</ul>` : '';
  const decisions = (c.decisions ?? []).map((d) => `<div class="decision"><p class="q">${md(d.question)}</p>
    <p class="chips"><span class="chip yes">✓ ${esc(d.chosen)}</span>${(d.options ?? []).map((o) => `<span class="chip no">${esc(o)}</span>`).join('')}</p>
    ${d.by || d.why ? `<p class="why">${d.by ? `${esc(L.chosen)} ${esc(L.by)} <b>${esc(d.by)}</b>` : ''}${d.by && d.why ? '. ' : ''}${d.why ? md(d.why) : ''}</p>` : ''}</div>`).join('');
  const sc = c.scope ?? {};
  const commits = (sc.commits ?? []).map(commit);
  const files = sc.files ?? [];
  const pr = sc.pr && (sc.pr.match(/github\.com\/([^/]+\/[^/]+)\/pull\/(\d+)/) ?? null);
  const kv = [
    [L.pr, sc.pr && (pr ? `<b>#${pr[2]}</b> <span class="muted">${esc(pr[1])}</span>` : esc(sc.pr))],
    [L.branch, sc.branch && `<code>${esc(sc.branch)}</code>`],
    [counted(L.commits, commits.length), commits.length && commitsHtml(commits, L)],
    [counted(L.files, files.length), files.length && filesHtml(files, L)],
  ].filter(([, v]) => v);
  const card = (label, body, icon) => body ? `<div class="card"><h4>${ICON[icon] ?? ''}${esc(label)}</h4>${body}</div>` : '';
  const people = c.people?.length && `<dl class="people">${c.people.map((p) => `<dt>${esc(p.role)}</dt><dd>${esc(p.name)}</dd>`).join('')}</dl>`;
  const source = c.source?.length && `<ul class="source">${c.source.map((x) => `<li><span class="pill">${esc(x.kind)}</span>${md(x.ref)}${x.note ? `<span class="muted">${md(x.note)}</span>` : ''}</li>`).join('')}</ul>`;
  const dl = (rows) => `<dl class="kv">${rows.map(([k, v]) => `<dt>${esc(k)}</dt><dd>${v}</dd>`).join('')}</dl>`;
  // A big scope would stretch the side column far past the story; it gets a full-width card below instead.
  const big = commits.length > 3 || files.length > LIMIT;
  const scope = kv.length && !big && dl(kv);
  const wide = kv.length && big && `<div class="card wide"><h4>${ICON.shipped}${esc(L.shipped)}</h4><div class="scope-cols">${dl(kv.filter(([k]) => !k.startsWith(L.files)))}${dl(kv.filter(([k]) => k.startsWith(L.files)))}</div></div>`;
  const extra = (c.extra ?? []).map((x) => block(x.label, `<p>${md(x.text)}</p>`)).join('');
  const open = [block(L.risks, ul(c.risks)), block(L.followups, ul(c.followups))].join('');
  const evidence = c.evidence ?? [];
  return `<section class="sec ctx" id="context">${crumbHtml}<h2>${esc(L.context)}</h2>
<div class="ctx-grid"><div class="ctx-main">
${block(L.background, c.background && `<p>${md(c.background)}</p>`)}
${block(L.reason, c.reason && `<p>${md(c.reason)}</p>`)}
${block(L.decisions, decisions)}
${block(L.verification, ul(c.verification, 'ticks'))}
${block(L.unchanged, ul(c.unchanged, 'ticks'))}
${extra}
</div><aside class="ctx-side">
${card(L.people, people, 'people')}${card(L.source, source, 'source')}${card(L.shipped, scope, 'shipped')}${card(L.rollback, c.rollback && `<p>${md(c.rollback)}</p>`, 'rollback')}
</aside></div>
${wide || ''}
${open ? `<div class="open"><h3>${ICON.open}${esc(L.open)}</h3><div class="open-grid">${open}</div></div>` : ''}
${evidence.length ? `<h3>${ICON.evidence}${esc(L.evidence)}</h3><div class="evidence">${evidence.map((e) => `<figure><img src="${esc(e.file)}" alt=""><figcaption>${md(caption(e))}</figcaption></figure>`).join('')}</div>` : ''}
</section>`;
}

function html(lang, mode) {
  const L = labels(lang);
  const h = entry.head[lang];
  const n = entry.sections.length;
  const eyebrow = [entry.project, entry.module].filter(Boolean).map(esc).join(' · ');
  const badge = `<span class="badge t-${entry.type}">${esc(L.types[entry.type])}</span>`;
  const crumb = (i) => `<p class="crumb">${esc([entry.project, titleText(h.title)].filter(Boolean).join(' · '))}${i ? ` · ${i}/${n}` : ''}</p>`;
  const sections = entry.sections.map((s, i) => {
    const t = s.text[lang];
    const top = `${crumb(i + 1)}<h2><span>${i + 1}</span>${md(t.title)}</h2>${t.where ? `<p class="where">${md(t.where)}</p>` : ''}`;
    const notes = `${t.bullets?.length ? `<ul class="changes">${t.bullets.map((b) => `<li>${md(b)}</li>`).join('')}</ul>` : ''}`
      + `${t.steps?.length ? `<p class="where">${esc(L.steps)}</p><ol class="steps">${t.steps.map((b) => `<li>${md(b)}</li>`).join('')}</ol>` : ''}`;
    const fig = (src, tag, cls) => `<figure class="shot"><figcaption class="tag ${cls}">${esc(tag)}</figcaption><img src="${esc(src)}" alt=""></figure>`;
    if (s.kind === 'pair') return `<section class="sec sec-pair" id="s${i + 1}">${top}<div class="pair">${fig(s.before, L.before, 'b')}${fig(s.after, L.after, 'a')}</div>${notes}</section>`;
    if (s.kind === 'single') return `<section class="sec sec-single" id="s${i + 1}">${top}${fig(s.shot, s.tag ?? L.now, 'a')}${notes}</section>`;
    const cols = t.columns ?? [L.where, L.before, L.after];
    const rows = t.rows.map((r) => `<tr>${r.map((c, j) => `<td class="${cols.length === 3 ? ['', 'o', 'n'][j] : ''}">${md(c)}</td>`).join('')}</tr>`).join('');
    return `<section class="sec sec-table" id="s${i + 1}">${top}<table><thead><tr>${cols.map((c) => `<th>${esc(c)}</th>`).join('')}</tr></thead><tbody>${rows}</tbody></table>${notes}</section>`;
  }).join('\n');
  const cL = labels(entry.context?.lang ?? langs[0]);
  const evidence = entry.context?.evidence ?? [];
  const ctx = withContext && entry.context ? contextHtml(cL, crumb()) : '';
  return `<!doctype html><html lang="${esc(lang)}"><head><meta charset="utf-8"><base href="${pathToFileURL(entryDir + '/').href}">
<title>${esc(titleText(h.title))}</title><style>${readFileSync(join(here, 'style.css'), 'utf8')}</style></head>
<body class="${mode}"><div class="page">
<div class="cover" id="cover"><header class="head"><div><p class="eyebrow">${badge}${eyebrow}</p><h1>${titleHtml(h.title)}</h1></div>
<div class="meta"><b>${esc(fmtDate(entry.date, lang))}</b>${h.meta ? `<br>${md(h.meta)}` : ''}</div></header>
${h.summary?.length ? `<div class="summary">${h.summary.map((c) => `<div><b>${esc(c.label)}</b>${md(c.text)}</div>`).join('')}</div>` : ''}
${h.footer ? `<p class="footnote">${md(h.footer)}</p>` : ''}</div>
${sections}
${h.footer ? `<footer class="foot">${md(h.footer)}</footer>` : ''}
${ctx}
</div></body></html>`;
}

// README.md: the backtrack record, readable on the forge without rendering anything.
function readme() {
  const lang = entry.context?.lang ?? langs[0];
  const L = labels(lang);
  const h = entry.head[lang] ?? entry.head[langs[0]];
  const tl = (lang in entry.head) ? lang : langs[0];
  const plain = (s) => String(s ?? '');
  const out = [`# ${titleText(h.title)}`, '',
    `${entry.date} · ${L.types[entry.type]}${entry.project ? ` · ${entry.project}` : ''}${entry.module ? ` / ${entry.module}` : ''}`, '',
    '<!-- Generated by report-changelog from changelog.json. Edit the JSON and re-render. -->', ''];
  for (const c of h.summary ?? []) out.push(`- **${c.label}:** ${plain(c.text)}`);
  out.push('', `## ${L.context}`, '');
  const sc = entry.context?.scope ?? {};
  const fold = (title, lines) => lines.length > LIMIT
    ? ['', `<details><summary>${title}</summary>`, '', ...lines, '', '</details>']
    : ['', `${title}:`, '', ...lines];
  const scopeMd = () => [
    ...[sc.pr && `- ${L.pr}: ${sc.pr}`, sc.branch && `- ${L.branch}: \`${sc.branch}\``].filter(Boolean),
    ...(sc.commits?.length ? fold(counted(L.commits, sc.commits.length), sc.commits.map(commit).map((x) => `- \`${x.sha}\`${x.subject ? ` ${x.subject}` : ''}`)) : []),
    ...(sc.files?.length ? fold(counted(L.files, sc.files.length), sc.files.map((f) => `- \`${f}\``)) : []),
  ].join('\n');
  for (const [k, v] of contextRows(L)) {
    if (v === SCOPE) { out.push(`**${k}**`, '', scopeMd(), ''); continue; }
    const text = v.replace(/<li>/g, '\n- ').replace(/<b>(.*?)<\/b>/g, '**$1**').replace(/<code>(.*?)<\/code>/g, '`$1`')
      .replace(/<\/?(ul|li)>/g, '').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&amp;/g, '&');
    out.push(`**${k}**${text.startsWith('\n') ? text : ` ${text}`}`, '');
  }
  const evidence = entry.context?.evidence ?? [];
  if (evidence.length) {
    out.push(`### ${L.evidence}`, '');
    for (const e of evidence) out.push(`![${plain(e.what)}](${e.file})`, '', `_${caption(e)}_${e.thread ? ` · ${e.thread}` : ''}`, '');
  }
  out.push(`## ${L.changes}`, '');
  entry.sections.forEach((s, i) => {
    const t = s.text[tl] ?? s.text[langs[0]];
    out.push(`### ${i + 1}. ${plain(t.title)}`, '');
    if (t.where) out.push(plain(t.where), '');
    if (s.kind === 'pair') out.push(`| ${L.before} | ${L.after} |`, '|---|---|', `| ![](${s.before}) | ![](${s.after}) |`, '');
    if (s.kind === 'single') out.push(`![](${s.shot})`, '');
    if (s.kind === 'table') {
      const cols = t.columns ?? [L.where, L.before, L.after];
      out.push(`| ${cols.join(' | ')} |`, `|${cols.map(() => '---').join('|')}|`, ...t.rows.map((r) => `| ${r.map((c) => plain(c).replace(/\|/g, '\\|')).join(' | ')} |`), '');
    }
    for (const b of t.bullets ?? []) out.push(`- ${plain(b)}`);
    (t.steps ?? []).forEach((b, j) => out.push(`${j + 1}. ${plain(b)}`));
    if (t.bullets?.length || t.steps?.length) out.push('');
  });
  if (h.footer) out.push(`_${plain(h.footer)}_`, '');
  return out.join('\n');
}

async function launch() {
  const require = createRequire(join(process.cwd(), 'noop.js'));
  let pw;
  for (const name of ['playwright-core', 'playwright']) { try { pw = require(name); break; } catch {} }
  if (!pw) fail([`playwright-core not found from ${process.cwd()}: run "npm i playwright-core" in this folder (no browser download needed)`]);
  if (process.env.CHROME_PATH) return pw.chromium.launch({ executablePath: process.env.CHROME_PATH });
  try { return await pw.chromium.launch({ channel: 'chrome' }); } catch {}
  const cache = join(homedir(), 'Library/Caches/ms-playwright');
  const shells = existsSync(cache) ? readdirSync(cache).filter((d) => d.startsWith('chromium_headless_shell-')).sort() : [];
  for (const d of shells.reverse()) {
    const dir = join(cache, d);
    const sub = readdirSync(dir).find((x) => x.startsWith('chrome-headless-shell'));
    if (sub) return pw.chromium.launch({ executablePath: join(dir, sub, 'chrome-headless-shell') });
  }
  fail(['no Chrome found: install Google Chrome or set CHROME_PATH']);
}

function fail(msgs) { console.error(msgs.map((m) => `✗ ${m}`).join('\n')); process.exit(1); }

writeFileSync(join(entryDir, 'README.md'), readme());
const browser = await launch();
const warnings = [];
const written = [join(entryDir, 'README.md')];
const name = (ids) => ids.map((id) => id === 'cover' || id === 'context' ? id : id.slice(1)).join('-');
for (const lang of langs) {
  const dir = join(entryDir, 'out', lang);
  mkdirSync(join(dir, 'album'), { recursive: true });
  const base = `${entry.slug}-${lang}`;
  const screen = html(lang, 'album');
  // Gate 2: nothing broken reaches the reader.
  const content = screen.replace(/<style>[\s\S]*?<\/style>/g, '');
  for (const bad of ['undefined', 'NaN', '[object Object]']) if (content.includes(bad)) errors.push(`${lang}: the report contains "${bad}"`);
  writeFileSync(join(dir, `${base}.html`), screen);
  const page = await browser.newPage({ viewport: { width: WIDTH, height: 900 }, deviceScaleFactor: 1.5 });
  await page.goto(pathToFileURL(join(dir, `${base}.html`)).href, { waitUntil: 'load' });
  // Stack a pair whose shots would shrink side by side, then measure every shot and every block.
  const { small, blocks } = await page.evaluate(({ SHOT_DPR, PAIR_SCALE }) => {
    const shown = (img) => img.getBoundingClientRect().width / (img.naturalWidth / SHOT_DPR);
    for (const pair of document.querySelectorAll('.pair')) if ([...pair.querySelectorAll('img')].some((i) => shown(i) < PAIR_SCALE)) pair.classList.add('stack');
    const small = [...document.querySelectorAll('.shot img')].map((i) => [i.closest('section, .cover').id, i.getAttribute('src'), shown(i)]);
    const blocks = [...document.querySelectorAll('#cover, section.sec')].map((e) => {
      const r = e.getBoundingClientRect();
      return { id: e.id, x: r.x, y: r.y + scrollY, width: r.width, height: r.height };
    });
    return { small, blocks };
  }, { SHOT_DPR, PAIR_SCALE });
  // Let Chrome repaint the restacked layout first, or a full-page capture repeats stale tiles.
  await page.evaluate(() => new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done))));
  for (const [id, src, k] of small) if (k < MIN_SCALE) errors.push(`${lang} ${id}: ${src} shows at ${Math.round(k * 100)}% of its captured size; crop it in capture.mjs to the part that changed`);
  // Pack the blocks in order into pages. A section with "break": true, and the context, start a new page.
  const forced = new Set([...entry.sections.flatMap((s, i) => s.break ? [`s${i + 1}`] : []), 'context']);
  const pages = [];
  for (const b of blocks) {
    const last = pages.at(-1);
    if (last && !forced.has(b.id) && last.height + b.height <= PAGE_H) { last.blocks.push(b); last.height += b.height; }
    else pages.push({ blocks: [b], height: b.height });
  }
  // Gate 4: a screen section fits on one page, so its screenshots never split across PDF pages.
  for (const b of blocks) {
    const shot = entry.sections[Number(b.id.slice(1)) - 1]?.kind !== 'table' && b.id.startsWith('s');
    if (shot && b.height > PAGE_H) (withPdf ? errors : warnings).push(`${lang} ${b.id}: ${Math.round(b.height)}px is taller than a ${PAGE_H}px page; crop its screenshots in capture.mjs or split the section`);
  }
  if (!args.includes('--no-png')) {
    for (const [i, p] of pages.entries()) {
      const [first, last] = [p.blocks[0], p.blocks.at(-1)];
      const file = join(dir, 'album', `${String(i + 1).padStart(2, '0')}-${name(p.blocks.map((b) => b.id))}.png`);
      await page.screenshot({ path: file, fullPage: true, clip: { x: first.x, y: first.y, width: first.width, height: last.y + last.height - first.y } });
      written.push(file);
    }
  }
  if (withPdf) {
    await page.evaluate((starts) => {
      document.body.classList.add('pdf');
      for (const id of starts) document.getElementById(id).classList.add('page-start');
    }, pages.slice(1).map((p) => p.blocks[0].id));
    await page.addStyleTag({ content: `@page { size: ${WIDTH}px ${PAGE_H}px; margin: 0; }` });
    const file = join(dir, `${base}.pdf`);
    await page.pdf({ path: file, preferCSSPageSize: true, printBackground: true });
    written.push(file);
  }
  await page.close();
}
await browser.close();
for (const w of warnings) console.warn(`! ${w}`);
if (errors.length) fail(errors);
console.log(written.map((f) => `✓ ${f}`).join('\n'));

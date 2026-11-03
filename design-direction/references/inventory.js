// design-direction inventory: the design system a rendered page actually uses.
// Evaluate in the page (preview evaluate tool, Playwright page.evaluate, or the DevTools console)
// and save the returned object as JSON. Measures the whole document, not only the viewport.
// On a reference it shows the system to borrow from; on your own screen, drift.py compares it with DESIGN.md.
// Elements inside [data-drift-ignore] (user content, embeds, third-party widgets) are skipped.
(() => {
  const visible = (el) => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none' && +s.opacity > 0;
  };
  const skipped = (el) => el.closest('svg,script,style,noscript,template,[data-drift-ignore]');
  const els = [...document.querySelectorAll('body *')].filter((el) => !skipped(el) && visible(el));
  const sample = (el) => (el.getAttribute('aria-label') || el.innerText || el.value || el.tagName.toLowerCase())
    .trim().replace(/\s+/g, ' ').slice(0, 40) || el.tagName.toLowerCase();
  const tally = (map, key, el) => {
    if (!key) return;
    const e = (map[key] ||= { count: 0, samples: [] });
    e.count += 1;
    if (e.samples.length < 3) e.samples.push(sample(el));
  };
  const ownText = (el) => [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim()) ||
    (el.matches('input,textarea,select,button') && !!(el.value || el.placeholder || el.innerText));
  const alpha = (c) => {
    if (!c || c === 'transparent') return 0;
    const m = c.match(/rgba?\(([^)]+)\)/);
    if (!m) return 1;
    const parts = m[1].split(/[\s,/]+/).filter(Boolean);
    return parts.length > 3 ? parseFloat(parts[3]) : 1;
  };
  const family = (f) => f.split(',')[0].trim().replace(/^["']|["']$/g, '');

  const type = { sizes: {}, weights: {}, families: {}, lineHeights: {} };
  const color = { text: {}, background: {}, border: {} };
  const spacing = {}, radius = {}, shadow = {};
  const SPACE_PROPS = ['paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft', 'marginTop', 'marginBottom'];

  for (const el of els) {
    const s = getComputedStyle(el);
    if (ownText(el)) {
      tally(type.sizes, s.fontSize, el);
      tally(type.weights, s.fontWeight, el);
      tally(type.families, family(s.fontFamily), el);
      tally(type.lineHeights, s.lineHeight, el);
      tally(color.text, s.color, el);
    }
    const painted = alpha(s.backgroundColor) > 0;
    if (painted) tally(color.background, s.backgroundColor, el);
    const bordered = parseFloat(s.borderTopWidth) > 0 && s.borderTopStyle !== 'none';
    if (bordered) tally(color.border, s.borderTopColor, el);
    for (const p of SPACE_PROPS) {
      const v = parseFloat(s[p]);
      if (v > 0) tally(spacing, `${+v.toFixed(2)}px`, el);
    }
    if (/flex|grid/.test(s.display)) {
      for (const p of ['rowGap', 'columnGap']) {
        const v = parseFloat(s[p]);
        if (v > 0) tally(spacing, `${+v.toFixed(2)}px`, el);
      }
    }
    const shaped = painted || bordered || s.boxShadow !== 'none' || el.matches('img,video,canvas,picture');
    if (shaped && parseFloat(s.borderTopLeftRadius) > 0) tally(radius, s.borderRadius, el);
    if (s.boxShadow !== 'none') tally(shadow, s.boxShadow, el);
  }

  // Background area by colour: each painted box minus the painted boxes nearest inside it.
  const docW = document.documentElement.scrollWidth, docH = document.documentElement.scrollHeight;
  const area = (el) => {
    const r = el.getBoundingClientRect();
    return Math.max(0, Math.min(r.right, docW) - Math.max(r.left, 0)) * Math.max(0, r.height);
  };
  const paintKey = (el) => {
    const s = getComputedStyle(el);
    if (el.matches('img,video,canvas,picture') || /url\(/.test(s.backgroundImage)) return 'media';
    if (/gradient/.test(s.backgroundImage)) return 'gradient';
    return alpha(s.backgroundColor) > 0 ? s.backgroundColor : null;
  };
  const painters = new Map();
  for (const el of els) {
    const k = paintKey(el);
    if (k) painters.set(el, { key: k, area: area(el), inner: 0 });
  }
  const rootBg = [document.documentElement, document.body].map((e) => getComputedStyle(e).backgroundColor)
    .find((c) => alpha(c) > 0) || 'rgb(255, 255, 255)';
  const root = { key: rootBg, area: docW * docH, inner: 0 };
  for (const [el, p] of painters) {
    let a = el.parentElement;
    while (a && !painters.has(a)) a = a.parentElement;
    (a ? painters.get(a) : root).inner += p.area;
  }
  const byColour = {};
  for (const p of [root, ...painters.values()]) byColour[p.key] = (byColour[p.key] || 0) + Math.max(0, p.area - p.inner);
  const total = Object.values(byColour).reduce((a, b) => a + b, 0) || 1;
  const areaShare = Object.entries(byColour).map(([c, a]) => ({ colour: c, share: +(a / total).toFixed(3) }))
    .sort((a, b) => b.share - a.share).filter((x) => x.share >= 0.001);

  // Per-role type, the DevTools Computed read the borrow-a-scale step needs.
  const roles = {};
  for (const sel of ['h1', 'h2', 'h3', 'h4', 'p', 'li', 'a', 'button', 'label', 'input', 'small', 'th', 'td', '[role=tab]', 'nav a']) {
    const el = els.find((e) => e.matches(sel) && ownText(e));
    if (!el) continue;
    const s = getComputedStyle(el);
    roles[sel] = { fontFamily: s.fontFamily, fontSize: s.fontSize, fontWeight: s.fontWeight, lineHeight: s.lineHeight,
      letterSpacing: s.letterSpacing, color: s.color, sample: sample(el) };
  }

  const sorted = (map) => Object.entries(map).map(([value, e]) => ({ value, ...e })).sort((a, b) => b.count - a.count);
  return {
    url: location.href,
    viewport: { w: innerWidth, h: innerHeight },
    page: { w: docW, h: docH },
    counts: {
      elements: els.length, fontSizes: Object.keys(type.sizes).length, fontWeights: Object.keys(type.weights).length,
      fontFamilies: Object.keys(type.families).length, textColours: Object.keys(color.text).length,
      backgrounds: Object.keys(color.background).length, spacingValues: Object.keys(spacing).length,
      radii: Object.keys(radius).length, shadows: Object.keys(shadow).length,
    },
    type: { sizes: sorted(type.sizes), weights: sorted(type.weights), families: sorted(type.families), lineHeights: sorted(type.lineHeights) },
    colour: { text: sorted(color.text), background: sorted(color.background), border: sorted(color.border), areaShare },
    spacing: sorted(spacing),
    radius: sorted(radius),
    shadow: sorted(shadow),
    roles,
  };
})();

// Evaluate in the page (preview evaluate tool, Playwright page.evaluate, or the DevTools console).
// Returns behaviour evidence for the lens checks: A2, A3, A5, D1, D2, D5, S8.
// Measures only what is rendered at the current viewport; run it once at a phone width and once at a desktop width.
(() => {
  const vw = innerWidth, vh = innerHeight;
  const visible = (el) => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none' && +s.opacity > 0;
  };
  const name = (el) => (
    el.matches('input,textarea,select')
      ? el.getAttribute('aria-label') || el.labels?.[0]?.innerText || el.placeholder || el.name || el.type
      : el.getAttribute('aria-label') || el.innerText || el.value || el.title ||
        el.querySelector('img[alt]')?.alt || el.querySelector('svg title')?.textContent || ''
  ).trim().replace(/\s+/g, ' ').slice(0, 50);
  const box = (el) => {
    const r = el.getBoundingClientRect();
    return { w: Math.round(r.width), h: Math.round(r.height), x: Math.round(r.left), y: Math.round(r.top + scrollY) };
  };
  const labelled = (el) =>
    el.getAttribute('aria-label') || el.getAttribute('aria-labelledby') || el.closest('label') ||
    (el.id && document.querySelector(`label[for="${CSS.escape(el.id)}"]`));

  const interactive = [...document.querySelectorAll(
    'a[href],button,select,summary,input:not([type=hidden]),textarea,[role=button],[role=tab],[role=link],[onclick],[tabindex]:not([tabindex="-1"])'
  )].filter(visible);

  // A3: targets under 44x44. Inline links inside running text are exempt.
  const smallTargets = interactive
    .filter((el) => !(el.matches('a') && el.closest('p,li,td')))
    .map((el) => ({ el, b: box(el) }))
    .filter(({ b }) => b.w < 44 || b.h < 44)
    .slice(0, 40)
    .map(({ el, b }) => ({ name: name(el) || el.tagName.toLowerCase(), ...b }));

  // D5: dropdowns and how much they hide.
  const selects = [...document.querySelectorAll('select')].filter(visible)
    .map((el) => ({ name: name(el), options: el.options.length }));
  const customDropdowns = interactive.filter((el) => el.getAttribute('aria-haspopup') === 'listbox' ||
    el.getAttribute('role') === 'combobox').map((el) => name(el));

  const fields = [...document.querySelectorAll('input,textarea,select')].filter(visible)
    .filter((el) => !['hidden', 'submit', 'button', 'checkbox', 'radio', 'range'].includes(el.type));
  // D1: empty fields the user must fill from scratch.
  const emptyFields = fields.filter((el) => !el.value).map(name);
  // S8 and accessibility: fields with no label (placeholder-only counts as unlabelled).
  const unlabelled = fields.filter((el) => !labelled(el)).map((el) => el.placeholder || el.name || el.type);

  // D2, A2: primary-looking actions, their copy, and where they sit.
  const ctas = interactive.filter((el) => el.matches('button,input[type=submit],[role=button]') ||
    (el.matches('a') && getComputedStyle(el).backgroundColor !== 'rgba(0, 0, 0, 0)'))
    .map((el) => {
      const r = el.getBoundingClientRect();
      return {
        text: name(el), ...box(el), disabled: !!el.disabled || el.getAttribute('aria-disabled') === 'true',
        aboveFold: r.top + scrollY < vh, thumbZone: r.top >= vh * 0.55 && r.bottom <= vh,
      };
    }).slice(0, 30);

  // A5, O1: bars that stay on screen while scrolling.
  const pinned = [...document.querySelectorAll('body *')].filter((el) => {
    const p = getComputedStyle(el).position;
    return (p === 'fixed' || p === 'sticky') && visible(el);
  }).map((el) => {
    const r = el.getBoundingClientRect();
    return { name: name(el).slice(0, 40), edge: r.top < vh / 2 ? 'top' : 'bottom', h: Math.round(r.height) };
  }).slice(0, 10);

  // S8: running text below 12px.
  const tinyText = [...document.querySelectorAll('body *')].filter((el) =>
    [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim()) && visible(el) &&
    parseFloat(getComputedStyle(el).fontSize) < 12).map((el) => el.innerText.trim().slice(0, 40)).slice(0, 20);

  return {
    url: location.href, viewport: { w: vw, h: vh }, pageHeight: document.documentElement.scrollHeight,
    counts: { interactive: interactive.length, smallTargets: smallTargets.length, selects: selects.length,
      emptyFields: emptyFields.length, unlabelled: unlabelled.length, tinyText: tinyText.length },
    smallTargets, selects, customDropdowns, emptyFields, unlabelled, ctas, pinned, tinyText,
  };
})();

// Interaction layer for the scrolling report. Inline it after the last
// section.part as a classic script: the file opens from file://, where modules
// and fetch are blocked.
//
// Rail: the nav.rail link whose section is most in view gets .current.
// Tips: a [data-tip] element shows its value in .tip on hover and on focus;
// give value marks tabindex="0" so the keyboard reaches them.
(() => {
  const links = new Map();
  document.querySelectorAll('nav.rail a[href^="#"]').forEach(a => links.set(a.getAttribute('href').slice(1), a));
  const parts = Array.from(document.querySelectorAll('section.part[id]'));
  if ('IntersectionObserver' in window && parts.length) {
    const seen = new Map();
    const io = new IntersectionObserver(entries => {
      entries.forEach(e => seen.set(e.target.id, e.intersectionRatio));
      let best = null;
      seen.forEach((r, id) => { if (r > 0 && (!best || r > seen.get(best))) best = id; });
      links.forEach((a, id) => a.classList.toggle('current', id === best));
    }, { threshold: [0, .25, .5, .75, 1] });
    parts.forEach(p => io.observe(p));
  }

  const tip = document.createElement('div');
  tip.className = 'tip';
  tip.hidden = true;
  document.body.appendChild(tip);
  const showAt = (el, x, y) => {
    tip.textContent = el.dataset.tip;
    tip.hidden = false;
    tip.style.left = Math.min(x + 12, innerWidth - tip.offsetWidth - 8) + 'px';
    tip.style.top = (y + 12) + 'px';
  };
  addEventListener('mousemove', e => {
    const el = e.target.closest ? e.target.closest('[data-tip]') : null;
    if (el) showAt(el, e.clientX, e.clientY); else if (!(document.activeElement && document.activeElement.hasAttribute('data-tip'))) tip.hidden = true;
  });
  addEventListener('focusin', e => {
    const el = e.target.closest ? e.target.closest('[data-tip]') : null;
    if (!el) return;
    const r = el.getBoundingClientRect();
    showAt(el, r.left + r.width / 2, r.bottom);
  });
  addEventListener('focusout', () => { tip.hidden = true; });
})();

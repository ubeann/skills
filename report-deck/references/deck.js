// Deck controller. Inline it in the deck HTML after the last section.page,
// as a classic script: the file opens from file://, where modules and fetch
// are blocked. It adds body.deck and shows one page at a time, scaled to the
// window; the CSS for that state is the "Deck" block of style.css.
//
// Keys cover what a presentation clicker sends (PageDown/PageUp) and what a
// hand on the keyboard expects:
//   next   ArrowRight ArrowDown PageDown Space Enter, click on the right half
//   prev   ArrowLeft ArrowUp PageUp Backspace, click on the left half
//   Home End   first and last page
//   F          fullscreen on or off
//   B or .     blank screen on or off
// #N in the URL is page N; it updates as you move, so a refresh keeps the place.
//
// .fragment children of the current page appear one per "next" press, in DOM
// order, before the deck moves on. [data-tip] elements show their value on
// hover. Both are inert in print: see the @media print block of style.css.
(() => {
  const pages = Array.from(document.querySelectorAll('section.page'));
  if (!pages.length) return;
  const W = pages[0].offsetWidth, H = pages[0].offsetHeight;
  document.body.classList.add('deck');
  let cur = -1;

  const clamp = i => Math.min(Math.max(i, 0), pages.length - 1);
  const fromHash = () => { const n = parseInt(location.hash.slice(1), 10); return clamp(isNaN(n) ? 0 : n - 1); };
  const fit = () => {
    const s = Math.min(innerWidth / W, innerHeight / H);
    pages[cur].style.transform = `translate(-50%, -50%) scale(${s})`;
  };
  const show = i => {
    i = clamp(i);
    if (i === cur) return;
    pages.forEach((p, k) => p.classList.toggle('current', k === i));
    cur = i;
    if (location.hash !== '#' + (i + 1)) history.replaceState(null, '', '#' + (i + 1));
    fit();
  };
  const fragments = () => Array.from(pages[cur].querySelectorAll('.fragment'));
  const next = () => {
    const f = fragments().find(el => !el.classList.contains('shown'));
    if (f) f.classList.add('shown'); else show(cur + 1);
  };
  const prev = () => {
    const shown = fragments().filter(el => el.classList.contains('shown'));
    if (shown.length) shown[shown.length - 1].classList.remove('shown'); else show(cur - 1);
  };

  addEventListener('keydown', e => {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    switch (e.key) {
      case 'ArrowRight': case 'ArrowDown': case 'PageDown': case ' ': case 'Enter': next(); break;
      case 'ArrowLeft': case 'ArrowUp': case 'PageUp': case 'Backspace': prev(); break;
      case 'Home': show(0); break;
      case 'End': show(pages.length - 1); break;
      case 'f': case 'F':
        if (document.fullscreenElement) document.exitFullscreen(); else document.documentElement.requestFullscreen();
        break;
      case 'b': case 'B': case '.': document.body.classList.toggle('blank'); break;
      default: return;
    }
    e.preventDefault();
  });
  addEventListener('click', e => {
    if (e.target.closest('a, button')) return;
    (e.clientX > innerWidth / 2 ? next : prev)();
  });
  addEventListener('resize', fit);
  addEventListener('hashchange', () => show(fromHash()));

  const tip = document.createElement('div');
  tip.className = 'tip';
  tip.hidden = true;
  document.body.appendChild(tip);
  addEventListener('mousemove', e => {
    const el = e.target.closest ? e.target.closest('[data-tip]') : null;
    tip.hidden = !el;
    if (!el) return;
    tip.textContent = el.dataset.tip;
    tip.style.left = (e.clientX + 12) + 'px';
    tip.style.top = (e.clientY + 12) + 'px';
  });

  show(fromHash());
})();

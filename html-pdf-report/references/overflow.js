// Overflow gate. Evaluate in the rendered HTML before printing.
// Returns a JSON array, one entry per element that escapes its section.page
// box or clips its own content. An empty array is a pass; fail the render on
// anything else and print the list.
//
// Entry: {page, el, escape, clipped, text}
//   page    1-based page number
//   el      tag#id.class selector of the offender
//   escape  pixels outside the page box (0 when only clipped)
//   clipped true when scrollWidth/scrollHeight exceed the client box, i.e.
//           text hidden by overflow: hidden, ellipsis, or nowrap
//   text    first 40 characters, to recognise the element in the PNG
//
// Mark an element that clips on purpose (a progress bar track, an avatar
// crop) with data-clip; it and its descendants are skipped.
(() => {
  const TOL = 1; // px of slack for subpixel rounding of borders and shadows
  const out = [];
  const sel = el => {
    let s = el.tagName.toLowerCase();
    if (el.id) s += '#' + el.id;
    if (typeof el.className === 'string' && el.className.trim()) s += '.' + el.className.trim().split(/\s+/).join('.');
    return s;
  };
  document.querySelectorAll('section.page').forEach((page, i) => {
    const box = page.getBoundingClientRect();
    page.querySelectorAll('*').forEach(el => {
      if (el.closest('[data-clip]')) return;
      const r = el.getBoundingClientRect();
      if (r.width === 0 && r.height === 0) return;
      const escape = Math.max(r.right - box.right, r.bottom - box.bottom, box.left - r.left, box.top - r.top);
      const cs = getComputedStyle(el);
      const clips = cs.overflow !== 'visible' || cs.overflowX !== 'visible' || cs.overflowY !== 'visible';
      const clipped = clips && (el.scrollWidth > el.clientWidth + TOL || el.scrollHeight > el.clientHeight + TOL);
      if (escape > TOL || clipped) {
        out.push({ page: i + 1, el: sel(el), escape: Math.max(0, Math.round(escape)), clipped, text: (el.textContent || '').trim().slice(0, 40) });
      }
    });
  });
  return JSON.stringify(out);
})()

// Overflow gate for a scrolling report. Evaluate at each viewport width.
// Returns a JSON array, one entry per element wider than the viewport or
// clipping its own content, plus one for the document when it scrolls
// sideways. An empty array is a pass; fail the check on anything else and
// print the list.
//
// Entry: {part, el, escape, clipped, text}
//   part    id of the enclosing section.part, or "document"
//   el      tag#id.class selector of the offender
//   escape  pixels outside the viewport width (0 when only clipped)
//   clipped true when scrollWidth/scrollHeight exceed the client box, i.e.
//           text hidden by overflow: hidden, ellipsis, or nowrap
//   text    first 40 characters, to recognise the element in the PNG
//
// Mark an element that clips on purpose (a scrolling table wrapper, an avatar
// crop) with data-clip; it and its descendants are skipped.
(() => {
  const TOL = 1;
  const out = [];
  const sel = el => {
    let s = el.tagName.toLowerCase();
    if (el.id) s += '#' + el.id;
    if (typeof el.className === 'string' && el.className.trim()) s += '.' + el.className.trim().split(/\s+/).join('.');
    return s;
  };
  const doc = document.documentElement;
  if (doc.scrollWidth > doc.clientWidth + TOL) {
    out.push({ part: 'document', el: 'html', escape: doc.scrollWidth - doc.clientWidth, clipped: false, text: '' });
  }
  const vw = doc.clientWidth;
  document.querySelectorAll('body *').forEach(el => {
    if (el.closest('[data-clip]')) return;
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) return;
    const escape = Math.max(r.right - vw, -r.left);
    const cs = getComputedStyle(el);
    const clips = cs.overflow !== 'visible' || cs.overflowX !== 'visible' || cs.overflowY !== 'visible';
    const clipped = clips && (el.scrollWidth > el.clientWidth + TOL || el.scrollHeight > el.clientHeight + TOL);
    if (escape > TOL || clipped) {
      const part = el.closest('section.part');
      out.push({ part: part ? part.id : 'document', el: sel(el), escape: Math.max(0, Math.round(escape)), clipped, text: (el.textContent || '').trim().slice(0, 40) });
    }
  });
  return JSON.stringify(out);
})()

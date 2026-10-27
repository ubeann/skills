# Section checklist

Every section passes all of these at the laptop, tablet, and phone widths. The review delegate checks them; the author checks them before asking for the review.

1. **One claim.** The heading states the section's single claim as a sentence. The kicker names the topic; the lede says why the claim matters. A heading that only names a topic fails.
2. **Numbers trace.** Every number in the section comes from one field of the JSON, formatted but not recomputed. A number the reviewer cannot find in the data is a must-fix.
3. **Exclusions sit beside totals.** A total that leaves something out says what and how much, next to the total, not in a footnote.
4. **Contrast.** Body text is at least 4.5:1 against its background; large headings at least 3:1. Muted text counts as body text.
5. **Legend order matches visual order.** Series in a legend appear in the order the eye meets them on the chart: top to bottom for stacked bars, left to right for grouped.
6. **Tabular numerals.** Every column of numbers uses tabular figures and right alignment, so digits line up.
7. **Headers read horizontally.** Table and axis labels are horizontal at every width. Shorten the label, widen the column, or let the wrapper scroll instead of rotating.
8. **Fits the width.** Nothing is wider than the viewport and no text is clipped at any of the three widths. A wide table or chart scrolls inside a wrapper marked `data-clip` with its key column pinned and a visible cue at the edge; a visual whose claim sits in its right half restacks on the phone instead. The overflow gate covers the first sentence mechanically; the review confirms the PNGs agree.
9. **Every value mark has a tip.** A bar, point, or cell that carries a number has `data-tip` with that number formatted as the text shows it, and the keyboard reaches it.
10. **Complete without the pointer.** The chart's claim reads from the marks, labels, and legend alone; tips add precision, never the only copy of a value.
11. **The rail follows.** Scrolling into the section marks its rail link; the link's label is the kicker.

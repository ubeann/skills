# Page checklist

Every page passes all of these. The review delegate checks them; the author checks them before asking for the review.

1. **One claim.** The title states the page's single claim as a sentence. The kicker names the topic; the lede says why the claim matters. A title that only names a topic fails.
2. **Numbers trace.** Every number on the page comes from one field of the JSON, formatted but not recomputed. A number the reviewer cannot find in the data is a must-fix.
3. **Exclusions sit beside totals.** A total that leaves something out says what and how much, next to the total, not in a footnote.
4. **Contrast.** Body text is at least 4.5:1 against its background; large headings at least 3:1. Muted text counts as body text.
5. **Legend order matches visual order.** Series in a legend appear in the order the eye meets them on the chart: top to bottom for stacked bars, left to right for grouped.
6. **Tabular numerals.** Every column of numbers uses tabular figures and right alignment, so digits line up.
7. **Headers read horizontally.** Table and axis labels are horizontal. Shorten the label or widen the column instead of rotating.
8. **Inside the box.** Nothing escapes the page and no text is clipped. The overflow gate covers this mechanically; the review confirms the PNG agrees.
9. **Every value mark has a tip.** A bar, point, or cell that carries a number has `data-tip` with that number formatted as the print shows it, so hovering in the deck reads the exact value.
10. **Fragments resolve to one claim.** A page with `.fragment` children reads correctly fully revealed, which is how the PDF prints it and how the deck ends the page. One fragment per series in legend order, the value labels last, and every fragment reveals a mark at least 1px tall; a series too small to see joins the last fragment.

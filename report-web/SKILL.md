---
name: report-web
description: Build a scrolling web report from computed data as one offline HTML file, read in a browser on a laptop, a tablet, or a phone. A slow analysis pass writes the numbers to JSON, the renderer emits one section per claim with a contents rail and hover values, and headless Chrome checks every section at three widths and screenshots it before it is committed. Use when a report is read by scrolling rather than presented or printed. A PDF or a meeting deck is the report-deck skill.
---

# Report web

Two programs, one contract. The **slow pass** computes and writes one JSON file. The **renderer** is a pure function of that file: it reads nothing else, so a section can be changed and re-rendered in seconds. The output is one HTML file with the stylesheet, script, fonts, and icons inline: it opens from disk with no network, which is also what rules out modules, `fetch`, and CDNs. The stack is yours; the Node and Playwright version that piloted this skill is in `references/node-example.md`.

## What the project provides

Before step 1 the repository has these, or you add them:

- a slow pass that writes the JSON;
- a renderer that loads it and writes the one file;
- a check command that opens the file at three widths, runs the overflow gate, and screenshots one section;
- a test suite that holds the gates of step 4.

Done when each of these runs from one command named in the project's agent doc.

## Steps

### 1. Save the numbers

Put every figure the report will show into one JSON file written by the slow pass: totals, shares, rows, labels, the generation time. Derive nothing in the renderer beyond formatting.

Done when the renderer loads that one file and re-renders the whole report in seconds.

### 2. One section, one claim

The report opens with a `header.head` that has an id: title, lede, byline, the key tiles, and the contents by part. Each section is one `section.part` with an `id` from its kicker, an `h2` that states the claim, a lede, and a body. A contents rail lists the head and every section by kicker and links to their ids; a cross-reference inside a section is a link to the target id labelled with its kicker, never a page number. Start from `references/style.css`.

The stylesheet fixes the content width: 980px beside the rail on a laptop, one column with the rail above it under the tablet width. Draw an SVG chart at the width of the column it sits in, since a chart that scales down scales its labels with it. A chart that needs the full laptop width goes in a `.wide` wrapper marked `data-clip` and scrolls sideways on narrower screens, with its key labels pinned and a fade at the edge as the cue. A visual whose claim sits in its right half (a mirrored bar chart, a wide table) restacks on the phone instead of scrolling.

Give each section function a one-line comment naming its kicker and id so the next edit finds it by search instead of by reading.

Done when every rail link and cross-reference resolves to an id in the file and every id is unique.

### 3. Add the interaction layer

Inline `references/web.js` after the last section. It marks the section in view on the rail and shows the value of any `[data-tip]` element on hover and on keyboard focus. A mark that carries a value (a bar, a point, a cell) gets `data-tip` with the value formatted as the text shows it and `tabindex="0"` so a keyboard reaches it. A table wider than a phone scrolls inside a wrapper marked `data-clip`.

Done when the file opens from `file://` with the network off, the rail follows the scroll, and Tab reaches a tip.

### 4. Render and look at three widths

Render, then screenshot just the section you touched at the laptop, tablet, and phone widths and look at all three. Read the PNGs and embed them in your message. A full-page PNG at the laptop and phone widths is for the handover only; at thirteen sections it is too tall to review. A change the user has to judge (layout, emphasis, wording) renders to a temp path and is shown before step 7 commits it.

Done when you have seen the changed section at all three widths and the user has seen any taste change.

### 5. Mechanical gates

Wire these into the check command and the test suite so they run every time:

- **Overflow at every width.** At each of the three widths, evaluate `references/overflow-web.js` in the page. It returns one entry per element wider than the viewport or whose content is clipped, with 1px of slack, plus one for the document itself when it scrolls sideways. Fail the check on a non-empty result and print the list.
- **Links.** Every `href="#..."` resolves to an id in the file.
- **Sentinels.** One distinctive string per section, from the test fixture, is present in the HTML.
- **Banned strings.** `NaN`, `Inf`, `undefined`, and `[object Object]` are absent from the content, which is the HTML with its `<script>` and `<style>` blocks removed.
- **One file.** No `<script src`, no stylesheet `<link`, no `src="http`, no `url(http`, no `type="module"`, and no `fetch(`.
- **Formatters.** A table test for every number, percent, and currency formatter, including negatives, zero, and values that round to zero or to one hundred.

Done when the check exits non-zero on an overflow at any width and the tests pass.

### 6. Read-only review

Send a delegate the brief in `references/review-brief.md` with the three PNG paths and the section's JSON slice. The delegate loads `dataviz` and `interfaces:better-interface`, checks the section against `references/section-checklist.md`, and returns findings under two headings: must-fix and nice-to-have. The brief states that the delegate edits nothing and commits nothing.

When the delegate's answer arrives, your next message restates the change you proposed and the question still open, then the findings. The user has moved on while it ran.

Done when every must-fix is either applied or answered with a reason.

### 7. Commit per section

Scope each commit to one section. A mechanical fix (overflow, contrast, a wrong number) commits at once. A taste change commits after the user accepts the PNGs from step 4. A follow-up to a section whose commit is unpushed amends that commit.

Done when each commit touches one section's scope and no unpushed section has a fixup commit behind it.

## Working habits

- Edit the section file with the Edit tool. A heredoc that carries the full old and new strings costs several times the tokens for the same change.
- Keep language, palette, source names, and the data model in the repo. This skill holds only the pipeline and the gates.
- Chart design is the `dataviz` skill. Invoke it before the first chart, not after the review finds the problem.
- Interaction earns its place: a tip with the exact value, a toggle between two cuts of the same numbers, a rail that follows the reader. Motion respects `prefers-reduced-motion`, and a chart reads completely with the mouse away.

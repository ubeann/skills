---
name: report-deck
description: Build a paged data report as a PDF for sending and a single offline HTML deck for presenting, from one set of fixed-size HTML pages. A slow analysis pass writes the numbers to JSON, the renderer prints the pages through headless Chrome and wraps the same pages with keyboard navigation, and every page passes an overflow gate and a PNG look before it is committed. Use when generating a multi-page PDF or a meeting deck from data, or iterating on its pages. A report read by scrolling in a browser is the report-web skill; editing an existing PDF is the pdf skill; PowerPoint output is the pptx skill.
---

# Report deck

Two programs, one contract. The **slow pass** computes and writes one JSON file. The **renderer** is a pure function of that file: it reads nothing else, so a page can be changed and re-rendered in seconds. Pages are fixed-size HTML sections. Headless Chrome prints them to the PDF, and the same sections with `references/deck.js` inlined are the deck: one HTML file that opens from disk with no network, for a meeting. The stack is yours; the Go and chromedp version that produced this skill is in `references/go-example.md`.

## What the project provides

Before step 1 the repository has these, or you add them:

- a slow pass that writes the JSON;
- a renderer that loads it and emits one `section.page` per page, with the stylesheet, scripts, fonts, and icons inline so each output is one file;
- a print command that runs the overflow gate and writes the PDF, and a deck command that writes the HTML;
- a screenshot command for one page;
- a test suite that holds the gates of step 4.

Done when each of these runs from one command named in the project's agent doc.

## Steps

### 1. Save the numbers

Put every figure the report will show into one JSON file written by the slow pass: totals, shares, rows, labels, the generation time. Derive nothing in the renderer beyond formatting.

Done when the renderer loads that one file and re-renders the whole PDF in seconds.

### 2. One page, one box

Each page is one `section.page`. One `@page { size: W H; margin: 0 }` rule sets the size and `.page` has the same width and height. Print with `printBackground` and `preferCSSPageSize` on. Start from `references/style.css`.

Give each page function a one-line comment naming its kicker and page number so the next edit finds it by search instead of by reading.

A mark that carries a value (a bar, a point, a cell) gets `data-tip` reading value, then series, then category, formatted as the print shows it: `Rp 13,3 T · Disetujui BKPM · TW I 2025`. Put it on the element the pointer can hit: the track of a thin bar, the whole tile of a map. A series that the presenter builds up while talking gets `class="fragment"` on each step, one per series in legend order with the value labels last. Both are inert in print.

Done when the PDF page count equals the number of sections.

### 3. Wrap the pages as a deck

The deck is the PDF's HTML with `references/deck.js` inlined after the last section and the Deck block of `references/style.css` in the stylesheet. The script shows one page scaled to the window, binds the keys a clicker sends, routes `#N` to page N, toggles fullscreen and blank, shows tips on hover, and reveals fragments one per press.

Done when the deck test in `references/go-example.md` passes: it opens the deck from `file://`, checks that `#N` lands on page N, that PageDown moves one page, and that printing it gives the PDF's page count. Before a meeting the user opens it fullscreen on the presenting laptop and projector; put that line in the handover message, since it is the one check this pipeline cannot run.

### 4. Render only what changed

Render, then rasterise just the page you touched and look at it:

```sh
pdftoppm -r 90 -f N -l N -png out/report.pdf /tmp/page
```

For a page with fragments, also screenshot the deck at `#N` in headless Chrome at the page size with every fragment shown; a page without them renders the same in both outputs. Read the PNG and embed it in your message. A change the user has to judge (layout, emphasis, wording) renders to a temp path and is shown before step 7 commits it.

Done when you have seen the changed page and the user has seen any taste change.

### 5. Mechanical gates

Wire these into the render and the test suite so they run every time:

- **Overflow.** Before printing, evaluate `references/overflow.js` in the page. It returns one entry per element whose box leaves its page or whose content is clipped, with 1px of slack. Fail the render on a non-empty result and print the list. `.page { overflow: hidden }` stays in the stylesheet as the last resort, never as the check.
- **Page count.** Rendered sections equal the expected count, in the PDF HTML and in the deck.
- **Sentinels.** One distinctive string per page, from the test fixture, is present in the HTML.
- **Banned strings.** `NaN`, `Inf`, and the printf failure marker `%!` are absent.
- **One file.** The deck has no `<script src`, no stylesheet `<link`, no `src="http`, no `url(http`, no `type="module"`, and no `fetch(`.
- **Formatters.** A table test for every number, percent, and currency formatter, including negatives, zero, and values that round to zero or to one hundred.

Done when the render exits non-zero on an overflow and the tests pass.

### 6. Read-only review

Send a delegate the brief in `references/review-brief.md` with the PNG path and the page's JSON slice. The delegate loads `dataviz` and `interfaces:better-interface`, checks the page against `references/page-checklist.md`, and returns findings under two headings: must-fix and nice-to-have. The brief states that the delegate edits nothing and commits nothing.

When the delegate's answer arrives, your next message restates the change you proposed and the question still open, then the findings. The user has moved on while it ran.

Done when every must-fix is either applied or answered with a reason.

### 7. Commit per page

Scope each commit to one page. A mechanical fix (overflow, contrast, a wrong number) commits at once. A taste change commits after the user accepts the PNG from step 4. A follow-up to a page whose commit is unpushed amends that commit.

Done when each commit touches one page's scope and no unpushed page has a fixup commit behind it.

## Working habits

- Edit the page file with the Edit tool. A heredoc that carries the full old and new strings costs several times the tokens for the same change.
- Keep language, palette, source names, and the data model in the repo. This skill holds only the pipeline and the gates.
- Chart design is the `dataviz` skill. Invoke it before the first chart, not after the review finds the problem.
- Interaction earns its place: a tip with the exact value, a fragment that reveals a series in legend order, a toggle between two cuts of the same numbers. The deck and the PDF are one report, so pages carry the same type, palette, and layout in both.

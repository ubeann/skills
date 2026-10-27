---
name: html-pdf-report
description: Build a PDF report or PDF deck from computed data. A slow analysis pass writes the numbers to JSON, fixed-size HTML pages render from that file, headless Chrome prints them, and every page passes an overflow gate and a PNG look before it is committed. Use when generating a multi-page PDF from data or iterating on its pages. Editing an existing PDF is the pdf skill; PowerPoint output is the pptx skill.
---

# HTML to PDF report

Two programs, one contract. The **slow pass** computes and writes one JSON file. The **renderer** is a pure function of that file: it reads nothing else, so a page can be changed and re-rendered in seconds. Pages are fixed-size HTML sections printed by headless Chrome. The stack is yours; the Go and chromedp version that produced this skill is in `references/go-example.md`.

## Steps

### 1. Save the numbers

Put every figure the report will show into one JSON file written by the slow pass: totals, shares, rows, labels, the generation time. Derive nothing in the renderer beyond formatting.

Done when the renderer loads that one file and re-renders the whole PDF in seconds.

### 2. One page, one box

Each page is one `section.page`. One `@page { size: W H; margin: 0 }` rule sets the size and `.page` has the same width and height. Print with `printBackground` and `preferCSSPageSize` on. Start from `references/style.css`.

Give each page function a one-line comment naming its kicker and page number so the next edit finds it by search instead of by reading.

Done when the PDF page count equals the number of sections.

### 3. Render only what changed

Render, then rasterise just the page you touched and look at it:

```sh
pdftoppm -r 90 -f N -l N -png out/report.pdf /tmp/page
```

Read the PNG and embed it in your message. A change the user has to judge (layout, emphasis, wording) renders to a temp path and is shown before step 6 commits it.

Done when you have seen the changed page and the user has seen any taste change.

### 4. Mechanical gates

Wire these into the render and the test suite so they run every time:

- **Overflow.** Before printing, evaluate `references/overflow.js` in the page. It returns one entry per element whose box leaves its page or whose content is clipped, with 1px of slack. Fail the render on a non-empty result and print the list. `.page { overflow: hidden }` stays in the stylesheet as the last resort, never as the check.
- **Page count.** Rendered sections equal the expected count.
- **Sentinels.** One distinctive string per page, from the test fixture, is present in the HTML.
- **Banned strings.** `NaN`, `Inf`, and the printf failure marker `%!` are absent.
- **Formatters.** A table test for every number, percent, and currency formatter, including negatives, zero, and values that round to zero or to one hundred.

Done when the render exits non-zero on an overflow and the tests pass.

### 5. Read-only review

Send a delegate the brief in `references/review-brief.md` with the PNG path and the page's JSON slice. The delegate loads `dataviz` and `interfaces:better-interface`, checks the page against `references/page-checklist.md`, and returns findings under two headings: must-fix and nice-to-have. The brief states that the delegate edits nothing and commits nothing.

When the delegate's answer arrives, your next message restates the change you proposed and the question still open, then the findings. The user has moved on while it ran.

Done when every must-fix is either applied or answered with a reason.

### 6. Commit per page

Scope each commit to one page. A mechanical fix (overflow, contrast, a wrong number) commits at once. A taste change commits after the user accepts the PNG from step 3. A follow-up to a page whose commit is unpushed amends that commit.

Done when each commit touches one page's scope and no unpushed page has a fixup commit behind it.

## Working habits

- Edit the page file with the Edit tool. A heredoc that carries the full old and new strings costs several times the tokens for the same change.
- Keep language, palette, source names, and the data model in the repo. This skill holds only the pipeline and the gates.
- Chart design is the `dataviz` skill. Read it before the first chart, not after the review finds the problem.

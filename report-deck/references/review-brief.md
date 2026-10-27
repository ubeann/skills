# Review brief

Send this to the review delegate verbatim, filling the placeholders. It is a read-only task.

---

Review page {N} of {report name}. This is a read-only review: make no edits, run no commands that change files, and make no commits. Your output is findings only.

Load the `dataviz` skill and the `interfaces:better-interface` skill before you look at the page.

Inputs:
- Rendered page: {path to PNG}
- Data behind the page: {path to JSON, or the slice pasted here}
- The page's claim, as the author states it: {one sentence}
- Checklist: {path to page-checklist.md}

Check the page against every item in the checklist and against both skills. For each problem, give the page number, the element, what is wrong, and the fix in one line.

Reply under exactly two headings:

## Must-fix
A reader would misread a number, miss the claim, or fail to read the text. Includes any number on the page that does not trace to the data.

## Nice-to-have
Everything else.

Write "none" under a heading with no findings. No preamble, no summary of what the page does well.

# Review brief

Send this to the review delegate verbatim, filling the placeholders. It is a read-only task.

---

Review section "{id}" of {report name}. This is a read-only review: make no edits, run no commands that change files, and make no commits. Your output is findings only.

Load the `dataviz` skill and the `interfaces:better-interface` skill before you look at the section.

Inputs:
- Rendered section at the laptop width: {path to PNG}
- At the tablet width: {path to PNG}
- At the phone width: {path to PNG}
- Data behind the section: {path to JSON, or the slice pasted here}
- The section's claim, as the author states it: {one sentence}
- Checklist: {path to section-checklist.md}

Check the section against every item in the checklist at every width and against both skills. For each problem, give the section id, the width, the element, what is wrong, and the fix in one line.

Reply under exactly two headings:

## Must-fix
A reader would misread a number, miss the claim, or fail to read the text at some width. Includes any number in the section that does not trace to the data.

## Nice-to-have
Everything else.

Write "none" under a heading with no findings. No preamble, no summary of what the section does well.

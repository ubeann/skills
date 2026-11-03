---
name: ux-behaviour-audit
description: Audit a UI by how users behave on it. Walk one task as the user, check each screen through six behaviour lenses (decide, scan, act, trust, commit, orient), place every screen on a junior-to-staff ladder, flag persuasion that crosses into a dark pattern, and render the report in chat. Use when asked for a UX audit, a usability review of a flow, or why users hesitate or drop off, from screenshots, a live URL, or frontend code. Visual polish is the impeccable skill; brand and token drift across screens is the design-direction skill; a report file to keep is the report-web skill.
---

# UX behaviour audit

A screen is judged by what it asks of the person using it. Every element asks the user a **question**, and the audit's unit is that question: what the user must decide, read, tap, doubt, or remember to get through one **task**. A screen can look simpler while making the decision harder, because the work moved onto the user. The audit finds where that happened, says which behaviour it blocks, and names the change that would move the screen up one level.

The audit edits nothing. Fixes are a follow-up the user asks for after reading the report.

## Steps

### 1. Frame the task

Write one line: `<who> wants to <task> on <device>, <how often>; done when <observable end state>`. Infer it from the product, the screens, or the code. Ask the user only for what you cannot infer, and ask once. How often the task happens decides several checks: a one-off setup tolerates a scroll wheel, a daily log does not.

When the user brings a **symptom** instead of a screen ("users abandon the filter", "trials don't convert"), look it up in the symptom index in `references/case-studies.md`. Frame the task where the symptom happens, and note the checks the index names so step 4 runs them first.

Done when the frame line is written and names one task, plus the symptom and its first checks when there is one. A request covering several tasks gets one frame per task and one report per frame.

### 2. Capture the path

Collect every screen and state the user passes through on that task, in order, and label them `S1`, `S2`, and so on. The recipe depends on the input; `references/inputs.md` has one branch each for screenshots, a live URL, and frontend code. On a live page, run `references/measure.js` at a phone width and at a desktop width to get tap targets, dropdowns, unlabelled inputs, empty defaults, and button copy as evidence.

Include the states that decide behaviour when they are reachable: the empty state, the loading state, the error state, and the screen right after the main action.

Done when every screen has an image, or a `file:line` for a code-only audit. The taps and decisions to finish the task are counted, and any state you could not reach is listed by name.

### 3. Walk it as the user

For each screen write four lines:

- **Question:** what the screen asks the user, in their words ("Is this worth $19 a month?", "How many homes will I get?").
- **Cost:** the taps, the decisions, and what the user must remember from an earlier screen.
- **Blind spot:** what the user needs and cannot see here (the result count, the total, a previous choice, the way back).
- **Exit risk:** where a user who hesitates would most likely stop.

Done when every screen in the path has all four lines.

### 4. Apply the six lenses

Run every check in `references/lenses.md` against the path. Mark each check pass, fail, or not applicable. A failure becomes a **finding** with these fields:

- the screen and the element;
- the lens;
- the behaviour it blocks, in one sentence;
- the evidence: what the image shows, a `measure.js` value, or a `file:line`;
- the fix, in one line;
- the **precedent**: the closest case in `references/case-studies.md`, by id (search the file for the check id), or "none" when no case fits;
- the **watch** metric that would show the fix working in production, taken from the precedent and adapted to this product;
- the severity: **blocker** (the user cannot finish or picks wrongly), **friction** (extra taps, memory, or time), **doubt** (an unanswered question that makes them hesitate), or **polish**.

Done when every check has a mark and every fail is a finding with all eight fields.

### 5. Place each screen on the ladder

Rate each screen junior, mid, senior, or staff using `references/ladder.md`, after reading the ladder case it names that is closest to the screen. Write the one change that would move the screen up a level. A staff rating still names what it would cost in noise.

Done when every screen has a level and a next-level change.

### 6. Draw the persuasion line

List every persuasion technique the path uses: defaults, anchors, badges, countdowns, progress, loss framing, dismiss copy. Test each against `references/persuasion.md`. A technique that fails a test is a **flag**. It goes in its own section of the report and is never written up as a recommendation.

Done when every technique on the path is listed as either helping the user or flagged, and each flag names the test it fails.

### 7. Render the report in chat

Fill `references/report.html`: the frame, the tiles, the screen strip with ladder levels, the findings ranked by severity, the lens-by-screen matrix, the flags, and what was not checked. Screens go in as absolute image paths; the preview inlines them. Pass the page to the host's inline HTML preview at 728px and at 390px, read both PNGs, and fix any overflow or clipped text. Then render it with the host's inline HTML tool (in T3 Code: `html_preview`, then `html_render`, using the measured height). If the host has no inline renderer, publish the page as an Artifact and give the link.

Below the rendered page, reply only with what the page does not say: the three fixes to make first, each with its watch metric, any state you could not reach, and an offer to apply fixes when the input was code.

Done when the page renders with no overflow at both widths and every finding from step 4 appears in it with its precedent linked to the video moment.

## Working habits

- Write findings in terms of behaviour, not taste. "The count is hidden until after the tap, so users apply filters blind" is a finding. "The button looks plain" is polish at most.
- The statistics behind many principles (choice overload, default rates, sampling uplift) come from design-education sources and are not always replicated. Give the behaviour as the reason, and leave the numbers out of the report.
- An S5 failure that repeats across screens is a system problem, not a screen one. Name it once and point to the design-direction skill's drift check.
- Judge the screen against its own task and frequency. Staff-level context on a screen used once a year is noise.
- One task per audit. A second flow is a second report.
- To compare a screen against a case visually, run the `video-context` skill on the case's video into a temporary folder. Then open the frames whose seconds fall in the minute after the link's `&t=` value. The frames stay in that folder and the repository keeps only the links, because the videos belong to their creator.

---
name: ux-behaviour-audit
description: Audit a UI by how users behave on it. Walk one task as the user, or every edge case of one behaviour bug, check each screen through six behaviour lenses (decide, scan, act, trust, commit, orient), weigh each fix against the product's own philosophy, place every screen on a junior-to-staff ladder, flag persuasion that crosses into a dark pattern, and render the report in chat. Use when asked for a UX audit, a usability review of a flow, the edge cases of a behaviour, or why users hesitate or drop off, from screenshots, a live URL, frontend code or a native app. Visual polish is the impeccable skill; brand and token drift across screens is the design-direction skill; a report file to keep is the report-web skill.
---

# UX behaviour audit

A screen is judged by what it asks of the person using it. Every element asks the user a **question**, and the audit's unit is that question: what the user must decide, read, tap, doubt, or remember to get through one **task**. A screen can look simpler while making the decision harder, because the work moved onto the user. The audit finds where that happened, says which behaviour it blocks, and names the change that would move the screen up one level.

The audit edits nothing. Fixes are a follow-up the user asks for after reading the report; `references/evidence.md` is how to ship them. `<skill-dir>` below is the folder holding this file.

## Steps

### 1. Frame the task

Write one line: `<who> wants to <task> on <device>, <how often>; done when <observable end state>`. Infer it from the product, the screens, or the code. Ask the user only for what you cannot infer, and ask once. How often the task happens decides several checks: a one-off setup tolerates a scroll wheel, a daily log does not.

Pick the branch:

- **Flow** (the default): one task, walked screen by screen.
- **Bug**: the user brings one behaviour that goes wrong, or asks for its edge cases. The frame names the behaviour the user expects ("undo a tab closed by mistake"), step 2 captures cases instead of a path, and steps 3 to 5 run only on the screens a failing case touches.

When the user brings a **symptom** instead of a screen ("users abandon the filter", "trials don't convert"), look it up in the symptom index in `references/case-studies.md`. Frame the task where the symptom happens, and note the checks the index names so step 4 runs them first.

Then read the product's **philosophy**: what it has already decided about itself. Look in `PRODUCT.md`, `DESIGN.md`, `CONTRIBUTING`, the roadmap, the token file, and the comments and commit messages on the code the task touches. Write each rule as one line with its source, for example `Omnibox.placeOffers: open pages stay out of ⌘T ("⌘K exists for those")`. A fix that breaks a rule is reported as that rule's cost for the owner to weigh, never as a recommendation.

Done when the frame line is written and names one task or one behaviour, the branch is picked, the symptom and its first checks are noted when there is one, and the philosophy is listed with sources (or "none found" with the places searched). A request covering several tasks gets one frame per task and one report per frame.

### 2. Capture the path

Collect every screen and state the user passes through on that task, in order, and label them `S1`, `S2`, and so on. The recipe depends on the input; `references/inputs.md` has one branch each for screenshots, a live URL, frontend code, and a native app. On a live web page, `references/measure.js` returns tap targets, dropdowns, unlabelled inputs, empty defaults and button copy as evidence.

Include the states that decide behaviour when they are reachable: the empty state, the loading state, the error state, and the screen right after the main action.

On the bug branch, list the **cases** instead: the plain path first, then each variation that changes the state the behaviour depends on (asleep, pinned, private, split, a closed window, an app page, after a relaunch). Run every case in the app and record steps, expected, seen, and pass or fail. The case table is the core of a bug report.

Done when every screen has an image, or a `file:line` for a code-only audit, the taps and decisions to finish the task are counted, and any state you could not reach is listed by name. On the bug branch: every case has a seen result from a run, or is listed as not reached.

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
- the evidence: what the image shows, a measured value, a case from the table, or a `file:line`;
- the fix, in one line;
- the **precedent**: the closest case in `references/case-studies.md` by id (search the file for the check id), a named peer product doing it with a link, or "none";
- the **watch** that would show the fix working: the precedent's metric adapted to this product, or, when the product has no telemetry, the test or probe that fails without the fix, labelled "test";
- the severity: **blocker** (the user cannot finish or picks wrongly), **friction** (extra taps, memory, or time), **doubt** (an unanswered question that makes them hesitate), or **polish**.

Check each fix against the philosophy from step 1. A fix that breaks a rule moves to the report's note with the rule it breaks.

Done when every check has a mark and every fail is a finding with all eight fields.

### 5. Place each screen on the ladder

Rate each screen junior, mid, senior, or staff using `references/ladder.md`, after reading the ladder case it names that is closest to the screen. Write the one change that would move the screen up a level. A staff rating still names what it would cost in noise.

Done when every screen has a level and a next-level change.

### 6. Draw the persuasion line

List every persuasion technique the path uses: defaults, anchors, badges, countdowns, progress, loss framing, dismiss copy. Test each against `references/persuasion.md`. A technique that fails a test is a **flag**. It goes in its own section of the report and is never written up as a recommendation.

Done when every technique on the path is listed as either helping the user or flagged, and each flag names the test it fails. When the path uses none, the report's note says so.

### 7. Render the report in chat

Fill `references/report.html`: the frame, the tiles, the screen strip with ladder levels, the case table on the bug branch, the findings ranked by severity, the lens-by-screen matrix, the flags, and what was not checked. Screens go in as absolute image paths; the preview inlines them. Then check the filled file:

```sh
python3 <skill-dir>/references/check_report.py report.html
```

Preview it with the host's inline HTML preview once at 728px and once at 390px. The page logs `overflow: none` or each overflowing element to the console; read that line, since a capture stops at about 4000px and cannot show the bottom of a long page. Fix and preview again only the width that failed. Then render it once with the host's inline HTML tool (in T3 Code: `html_render` with the preview's `contentHeight`, capped at 2000; the frame grows to fit). If the host has no inline renderer, publish the page as an Artifact and give the link.

Below the rendered page, reply only with what the page does not say: the three fixes to make first, each with its watch, any state you could not reach, and an offer to apply fixes when the input was code or a running app.

Done when `check_report.py` passes, both previews log `overflow: none`, and the page is rendered once.

## Working habits

- Write findings in terms of behaviour, not taste. "The count is hidden until after the tap, so users apply filters blind" is a finding. "The button looks plain" is polish at most.
- The statistics behind many principles (choice overload, default rates, sampling uplift) come from design-education sources and are not always replicated. Give the behaviour as the reason, and leave the numbers out of the report.
- An S5 failure that repeats across screens is a system problem, not a screen one. Name it once and point to the design-direction skill's drift check.
- Judge the screen against its own task and frequency. Staff-level context on a screen used once a year is noise.
- One task per audit. A second flow is a second report.
- Read screenshots shrunk to 1200px on the long side (`sips -Z 1200 shot.png --out small.png`) and crop for detail. A full Retina capture costs more context than the rest of the step.
- To compare a screen against a case visually, run the `video-context` skill on the case's video into a temporary folder. Then open the frames whose seconds fall in the minute after the link's `&t=` value. The frames stay in that folder and the repository keeps only the links, because the videos belong to their creator.

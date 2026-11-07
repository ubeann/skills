# Watching and measuring motion

## Capture

Two ways to get frames, by runtime.

**Seek (CSS, WAAPI, View Transitions).** Exact frames at each beat's time. Pause every animation and set its time, then screenshot:

```js
// Playwright, after the trigger has fired
for (const t of beatTimes) {            // ms, from the beat sheet
  await page.evaluate((t) => {
    for (const a of document.getAnimations()) { a.pause(); a.currentTime = t; }
  }, t);
  await page.screenshot({ path: `${out}/beat-${String(t).padStart(5, "0")}.png` });
}
```

**Record (JS-driven, canvas, Rive, Lottie, native, video).** Real time, so it also shows dropped frames:

- Web: a Playwright context with `recordVideo: { dir, size }` at the review viewport, or the host's preview recording (`preview_recording_start` and `_stop` in T3 Code). Hidden preview tabs pause CSS animations, so record from a visible tab or headless Playwright.
- iOS simulator: `xcrun simctl io booted recordVideo out.mp4`. Android: `adb shell screenrecord /sdcard/out.mp4`.
- macOS app: run a disposable copy (its own profile or probe mode, never the owner's running app), drive it with the project's test driver, and record the window with `screencapture -v -l <window-id> out.mov` (the window's id from the driver, or from `CGWindowListCopyWindowInfo`). A hidden or off-screen test window renders no animation in real time, so for motion use a visible window, or host the view in a test that renders frames at set times and stitch them with `ffmpeg -f concat`. Render off-screen frames in light appearance unless dark is the point: dark colours can resolve inconsistently off screen.
- Video: the render itself, or the frames `hyperframes-cli` shows.

Then turn the recording into frames with `video-context`:

```sh
INTERVAL=0.1 sh ~/.claude/skills/video-context/references/extract.sh <recording> <tmp-dir>
```

Capture each sequence twice: once normally and once with reduced motion (`page.emulateMedia({ reducedMotion: "reduce" })`, or the device setting). When the setting cannot be switched from a test (the macOS one is the system's), add a test override to the token type's reduced flag, or check the code path: the inventory's `unguarded-literal` list, then the owner turns the setting on by hand. Capture at the smallest and largest review viewport the project lists.

## Check every beat

For each row of the beat sheet, open the frames around its start and its end and record:

| Check | Passes when |
|---|---|
| Start | the element starts moving within one frame interval of the planned start |
| End state | the last frame matches the row's "to" exactly, and the element then stays still |
| Clipping | no frame cuts the element at a container edge, mask edge or overflow boundary |
| Jumps | no frame where the element skips position, blinks out or flashes unstyled |
| Layout shift | nothing outside the beat's element moves |
| Rest | a stateful piece reaches rest after every reaction |
| Reduced motion | the reduced capture shows the row's reduced-motion behaviour |
| Sound | a row with a sound hits one frame after its picture: `npx hyperframes audio <render> --json` lists where each sound hits, so compare it with the beat grid. Frames carry no sound, so this is the only check that hears |

Agents miss single-frame faults that a person sees at once, so open the frames around every end state rather than sampling ([video at 19:31](https://www.youtube.com/watch?v=f-Ar8mwm3kQ&t=1171s)).

## Craft bar

Apply `review-animations`' ten standards to the changed motion code. That skill is user-invoked, so read its file instead of calling it: `~/.agents/skills/review-animations/SKILL.md`, and its `STANDARDS.md` when a finding needs a value. The project's tokens and decision records win where the two disagree.

## Video numbers

A video or animated scene also passes these, each a count, not a taste ([video at 6:48](https://www.youtube.com/watch?v=Zk4Qzd-NJ_0&t=408s)):

| Check | Passes when |
|---|---|
| Text size | every line is at least 4.5% of the frame height |
| Read time | each line stays on screen at least its character count divided by 15, in seconds |
| Frame edge | nothing slides off the edge by accident, and the camera never jerks |
| Depth | each shot has a background, a subject and a near layer; a flat card with fading text is "a slide that wiggles" ([video at 3:34](https://www.youtube.com/watch?v=Zk4Qzd-NJ_0&t=214s)) |
| Fonts | every glyph the copy uses exists in the chosen font, so no fallback font slips in |
| Default look | none of the generic AI-video set: navy with gold, tiny widely spaced capitals, glowing lines, floating dust, words blurring in one at a time, Space Grotesk, Inter or a monospace label font, dot separators, invented codes like "FIG. 03" ([video at 1:21](https://www.youtube.com/watch?v=Zk4Qzd-NJ_0&t=81s)) |

Findings that block release come first, each with its timestamp and fix. One defect means checking every similar shot for it.

## Drift

Rerun the inventory with `--json` and compare it with step 1's run:

```sh
python3 <skill-dir>/references/motion_inventory.py <src> --tokens <token-file> --json motion-after.json
```

| Metric | Budget |
|---|---|
| Off-scale literals in code this change touched | 0 |
| Unnamed tokens (a literal equal to a token) | 0 |
| Libraries | only those step 4 chose |
| `transition-all`, `layout-property`, `scale-zero` flags in touched code | 0 |
| `no-reduced-motion-ref` | 0, or the shared helper that gates it is named |
| `unguarded-literal` (Swift) in touched code | 0, or the place that checks reduced motion is named |
| `forever-loop` | each one starts only without reduced motion and stops off screen |

Literals in untouched vendored components are listed, not fixed, unless the change touched that component.

## Critique loop

Score each sequence from 1 to 5 on every row, fix the lowest score first, capture again, and stop when every score is 4 or more or after three rounds. Then hand it to the owner to watch at native size on their own device.

| Row | 5 looks like |
|---|---|
| Purpose | every beat has a job from the brief; nothing moves for decoration on an operate surface |
| Timing | every beat lands on the sheet's time and token |
| Easing | the feel matches the three adjectives: an unhurried product never snaps, a crisp one never floats |
| Choreography | one thing leads at a time, in the order the sheet gives |
| Finish | no clipping, jumps, blank frames or layout shift in either capture |
| Cohesion | it moves like the rest of the product and uses the signature motion where the brief says |
| Reduced motion | the reduced capture reads completely and shows every finished state |

## Report

Render in chat:

1. Per sequence: | Beat | Planned | Seen | Status |, then the rubric scores by round.
2. The drift table: | Metric | Budget | Found | Status |.
3. Findings: | File:line | Seen | Fix |, most severe first.
4. The capture folders, so the owner can open the frames.

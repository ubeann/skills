---
name: motion-direction
description: Decide how a product moves before any animation is built, then watch and measure the built motion against that decision. Writes the motion brief (one focal moment, a personality, what stays still), locks duration, delay and easing tokens, picks one runtime per job (CSS and platform built-ins, Motion, GSAP, Rive, Lottie, HyperFrames) inside the project's budget, storyboards every sequence as a beat sheet approved before code, and reviews recordings frame by frame with a motion drift count. Use when adding or reviewing animation, micro-interactions, scroll motion, an animated mascot or a launch video, when motion feels generic or inconsistent, or when choosing between Rive, Lottie and code. Static UI tokens are design-direction; mascot and scene art is brand-art; collecting motion references is moodboard; exact polish values per component are interfaces:better-ui.
---

# Motion direction

A model told to "add animations" returns the **average**: a fade-and-rise on every section, a bounce on every button, durations picked one file at a time. It cannot feel motion, so it has no way to tell good from bad ([video at 3:30](https://www.youtube.com/watch?v=f-Ar8mwm3kQ&t=210s)). It moves well when it is told which **technique**, how long, on which curve and why, and when someone watches the result. That is **direction**, and it is most of the work: the prompt is the small part, the harness around it the large one ([video at 1:02](https://www.youtube.com/watch?v=747ZnEtsRbg&t=62s)).

This skill writes the direction down as tokens, a runtime per job and a **beat sheet** per sequence, then checks recordings of the built motion against them. Three outcomes the user can see: the product moves with one personality, every animation has a job, and it ships within budget and reads with reduced motion.

## Steps

### 1. Read what exists

Find the platforms, `DESIGN.md` and `PRODUCT.md` (from `design-direction`), the token source (CSS custom properties, a Tailwind theme, a `motion.ts` mirror, native constants), every decision record that rules on motion (ADRs, a design workflow doc, Do's and Don'ts), and the motion already in the code. Inventory it (`<skill-dir>` is the folder holding this file):

```sh
python3 <skill-dir>/references/motion_inventory.py <src> --tokens <token-file> [--tokens motion.ts]
```

It reads web code and Swift. In a Swift app, pass the file that holds the motion constants (a `Design.swift`) as `--tokens`, and the project's own reduced-motion check as `--guard 'Motion\.reduced'`.

Pick the branch:

- **New:** no motion yet. Run steps 2 to 7 in order.
- **Existing:** a product or revamp with motion in it. The recorded decisions bind every later step: a library an ADR rejects stays rejected unless step 4 drafts a superseding record. Step 2 fills only the gaps, step 3 adopts the existing tokens and adds only what a new job needs, and the inventory's off-scale literals become step 7 findings.
- **One sequence:** a launch video, a mascot, one hero. Use the product's tokens if they exist, then run steps 4 to 7 for that sequence.

Done when the platforms, the branch, every token source and every binding decision (with its file) are written down, and the inventory has run.

### 2. Write the motion brief

Fill every field in `references/brief.md`: each surface's **mode** (operate or persuade), three motion adjectives each with a visible consequence, the one **focal moment** (taken from the brief's peak and end moments), the frequency map, what never moves, the reduced-motion stance, the budget, and one **signature motion**. Infer from the product, the code and the conversation; ask the user once for what you cannot infer. On the existing branch, `find-animation-opportunities` lists where motion is missing; each candidate that survives its gate becomes a frequency-map row or a beat sheet. Write the result into `DESIGN.md`'s Motion section, or into the project's own home for it when step 1 found one.

Done when every field has an answer or is marked open, the focal moment names one screen and one event, and each adjective names something visible ("unhurried: nothing on the landing finishes under 400 ms"), not a mood.

### 3. Lock the tokens

Start from the preset in `references/tokens.md`, apply its rules, and keep one token per job: durations by distance and consequence, delays and staggers for choreography, a small set of easings, springs where the runtime has them. On the existing branch the code's tokens are the preset. Write them where the code reads them, mirror them into `DESIGN.md` as the project already does, and comment each with its job.

Done when every duration and easing the brief implies maps to a token, each token has a job comment, and no two tokens share a job.

### 4. Pick one runtime per job

List the jobs the brief implies (feedback, panels, route changes, lists, scroll sections, stateful art, loops, video) and give each one runtime from `references/runtimes.md` (a web table and a native one), cheapest first: the platform's built-ins before any library. A library the project has not adopted needs its weight measured or cited and a decision record drafted for the user; once adopted, install its official skill into that project, not globally. A stateful mascot needs its art as parts first, from `brand-art`.

Done when every job has exactly one runtime with its cost written beside it, and every new dependency has a drafted decision record.

### 5. Storyboard every sequence as a beat sheet

Write one beat sheet per sequence with the templates in `references/beat-sheet.md`: the trigger, then one row per beat (start, duration token, element, from and to, the technique's name, easing token, sound), then the interruption and reduced-motion rows. A stateful piece also gets a state table in which every state returns to **rest**. A video also gets its shot list and beat grid. When a reference clip shows the feel, read its **grammar** from frames (the template's recipe) and take that, never its content.

For anything with art, approve still **style frames** of the key poses before any motion. Show the beat sheet and the style frames to the user.

Done when every beat has a token, a named technique and an end state, every stateful piece returns to rest, and the user has approved the beat sheet.

### 6. Build from the beat sheet

Hand the builder the beat sheet, the tokens and the runtime, with the contract at the top of `references/beat-sheet.md`: build what the sheet says and list every deviation. Route by runtime: `impeccable animate` or `interfaces:better-ui` for UI motion, the Rive CLI for stateful art, `hyperframes` for video, the library's own skill for scroll choreography. Build a **draft** first: one breakpoint, or a 480p render.

Done when the sequence plays on its target from a real trigger, and the builder's deviation list exists (an empty list is fine).

### 7. Watch and measure

Record every sequence and read the frames as `references/review.md` describes. Check each beat against the sheet: it starts at its time, lands on its end state, and nothing clips, jumps or shifts layout. Play it again with reduced motion on. Rerun the inventory for drift and apply `review-animations`' standards to the changed code. Score each sequence on the review rubric and fix the lowest score first, for at most three rounds; then the owner watches it at native size on their own device.

Render the result in chat: one table per sequence (beat, planned, seen, status), the drift table from the inventory, then the findings, each with file and line, what was seen and the fix.

Done when every beat has a seen status, every off-scale literal and flag is a finding or a recorded exception, and the owner has watched every sequence.

## Working habits

- **Restraint first.** Motion a user meets a hundred times a day gets none; delight lives in rare moments. Deleting an animation is often the best fix.
- **Name the technique** when steering a builder: stagger, shared element, spring settle, mask reveal, follow path. `animation-vocabulary` turns a described feel into the term.
- **Everything comes to rest.** Entrances settle and stop; ambient loops stop off screen and offer a pause past five seconds (WCAG 2.2.2).
- **Gate the expensive step.** Stills before motion, a draft before the final render, one sequence approved before the next is storyboarded ([video at 13:30](https://www.youtube.com/watch?v=J4oygRI6mN0&t=810s)).
- **Watch it yourself.** Agents miss a frame of clipping or a crooked morph; a recording at native speed shows it ([video at 19:31](https://www.youtube.com/watch?v=f-Ar8mwm3kQ&t=1171s)).
- The source videos are cited by timestamp, not stored. To see one, run `video-context` on the link into a temporary folder.

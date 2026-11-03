---
name: design-direction
description: Set a product's design direction before any UI is generated, then measure built screens for drift from it. Writes the brief (who it serves, the category assumption it bets against, its peak and end moments), gives each reference one job, locks a token system into DESIGN.md for app, website or desktop, and counts drift in type, spacing, colour and radius. Use when starting UI from references, when generated screens look generic or off-brand, or when screens stop matching each other. Building and polishing screens is the impeccable skill; how users behave on a flow is ux-behaviour-audit.
---

# Design direction

A model asked for UI with no direction returns the **average** of every app it has seen: clean, consistent and forgettable. Handing it more references does not fix that; past one reference per job, each pulls a different way and the result is a **Frankenstein** whose components stop matching ([video at 5:07](https://www.youtube.com/watch?v=YS7uOXjmJTA&t=307s)). **Direction** is the missing input: a person deciding what the product is, which reference supplies what, and what to cut. This skill writes that direction down as files the generator and `impeccable` both read, then measures the built screens against it.

Everything here serves three outcomes the user can see: the brand survives generation, the product has a point of view, and screen 80 matches screen 1.

## Steps

### 1. Read what exists

Find the platforms (app, website, desktop; one product can have several), any `PRODUCT.md` and `DESIGN.md`, and where the code keeps its tokens (CSS custom properties, a Tailwind theme, a theme file, native style constants). Pick the branch:

- **New:** no UI yet. Run steps 2 to 6 in order.
- **Existing:** UI exists. Run step 6 first on two or three core screens to see the system actually in use, then steps 2 to 4 keep what works and settle the rest, then step 6 again.
- **Redesign:** the user wants a new look. Treat the current UI as evidence of what the product does, never as a source of tokens.

Done when the platforms, the branch, and the location of every existing token source are written down.

### 2. Write the brief

Fill every field in `references/brief.md`: who and their job, the surfaces, three adjectives each translated into something visible, three things the product is not, the **bet** against the category's hidden assumption, the peak and end moments of the core flow, the hard moments, and a candidate **signature element**. Infer from the product, the code and the conversation; ask the user once for what you cannot infer.

Write the product fields into `PRODUCT.md` and keep the visual fields for `DESIGN.md` in step 4, as `references/brief.md` maps them. Update an existing `PRODUCT.md` in place.

Done when every field has an answer or is marked open, each adjective names a visible consequence, and each "not" names a concrete pattern, not a mood.

### 3. Give each reference one job

Take at most one reference per **job**: type, colour, surfaces and shape. Add one **pattern reference** per core flow, which supplies structure only (what is on the screen and in what order), never its look. A reference with no job is dropped, and "make it look like X" is never an instruction.

Measure every reference that has a URL with `references/inventory.js` and take only the values its job covers; `references/measure.md` has the recipe for URLs, screenshots and native apps. Record a table: reference, job, values taken, and the line "everything else from this reference is ignored".

Done when every reference holds exactly one job and its taken values are written down with the measurement they came from (or "estimated from a screenshot").

### 4. Lock the system

Start from the platform preset in `references/presets.md`, replace each value a reference's job supplies, and apply the rules in that file's first section. Write `DESIGN.md` in the format `impeccable` reads: YAML frontmatter tokens, then the canonical sections (`references/presets.md` lists them). Put the adjectives and the signature element in Overview, and each "not" from the brief in Do's and Don'ts beside the positive rule that replaces it. Mark the source of every token in a comment: a reference, the preset, or a brief decision.

Then check the tokens themselves (`<skill-dir>` is the folder holding this file):

```sh
python3 <skill-dir>/references/drift.py DESIGN.md --platform <app|web|desktop>
```

Done when `drift.py` reports the token system within budget for every platform the product ships on, and every token has a source comment.

### 5. Build the core flow first

Generate or build the core flow before anything else, from `DESIGN.md`, `PRODUCT.md` and that flow's pattern reference only, using the contract in `references/handoff.md`. Build the peak screen, the end screen and the hard-moment states in the same pass. When `impeccable` is installed, hand it the build: it reads both files.

Done when the core flow renders at the platform's check widths with its empty, loading, error and end states, and the generator's deviation list exists (an empty list is fine).

### 6. Measure drift

Run `references/inventory.js` on each built screen at each check width, save each result as JSON, and compare them all against the tokens:

```sh
python3 <skill-dir>/references/drift.py DESIGN.md screen-*.json --platform <app|web|desktop>
```

Put the first screen built and the latest screen side by side in one image and look for what the counts miss: two cards that do not feel like the same product, a second icon style, an accent that moved. For each drift, either snap the value to its nearest token or, when the deviation is deliberate and recurs on three or more screens, promote it to a token and record why.

Render the result in chat as one table per screen (metric, budget, found, status), then the findings, each with element, value, nearest token and fix.

Done when every count is within budget or each excess is a finding with its element and fix, and the side-by-side image has been looked at.

## Working habits

- Cut before adding. Remove everything from a screen, then add back only what the brief or the task needs ([video at 10:16](https://www.youtube.com/watch?v=doiaMtD80p8&t=616s)).
- Expression belongs on selling surfaces (landing pages, onboarding, the peak and end moments). Doing surfaces (lists, settings, editors) carry the brand through the signature element, the copy voice and precise details, and stay calm everywhere else.
- When the model drifts, tighten the input before adding to it: a clearer brief or one fewer reference fixes more than an extra skill file.
- The source videos are cited by timestamp, not stored as frames. To see one, run the `video-context` skill on the link into a temporary folder.

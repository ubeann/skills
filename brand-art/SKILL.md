---
name: brand-art
description: Make a product's mascots, illustration sets, scene and background art, and app icons that keep one identity across every image, through Recraft or Higgsfield. Locks an art bible and an identity pack (the owner's seed, an approved hero, a turnaround, fixed identity text, palette, style IDs) before generating, changes one thing per call, cleans the files (WebP, SVG backgrounds, palette snap, texture, edge, sizes) and scores every image for drift against the hero. Use when generating illustrations, a mascot or character, landscapes or backgrounds, or an app icon, when AI art looks generic or loses its identity, or to compare image vendors. UI tokens are design-direction; collecting and breaking down references is moodboard; logo marks are ui-ux-pro-max:design; assets cut from an approved mockup are impeccable.
---

# Brand art

An image model given a prompt returns the **average**; given someone else's art, it returns that art. Identity comes from three things the model cannot supply: an **original seed** the owner made, an **art bible** that decides shape, line, rendering, light, palette and subjects, and an **identity pack** every later image is generated from and scored against. The approved image is the **hero**. Everything after it is a variation of the hero, one change at a time.

The work lives in the product repo under `art/<name>/`, one folder per asset family. `<skill-dir>` below is the folder holding this file. The scripts need Pillow and numpy (`python3 -m pip install pillow numpy`).

## Steps

### 1. Read the direction

Read `DESIGN.md` and `PRODUCT.md` when they exist; the palette and adjectives start there, and a product with UI but no `DESIGN.md` runs the `design-direction` skill first. Pick the **family**:

- **mascot**: a character that recurs (empty states, loading, onboarding, the app icon).
- **set**: spot illustrations or chapter art that must read as one series.
- **scene**: landscapes, hero backgrounds, banners.
- **icon**: an app icon, usually built from the mascot.

List every target surface with its size and format (a 1024 app icon, a 1200x630 social card, art printed 34 mm wide). Check vendor access and credits: `higgsfield account` for Higgsfield, `get_user` on the Recraft MCP. `references/vendors.md` has setup for both. Create `art/<name>/` with the folders `references/identity-pack.md` lists.

Done when the family, every target with size and format, and each vendor's credit balance are written in `art/<name>/README.md`.

### 2. Write the art bible

Fill every field of `references/art-bible.md` into `art/<name>/README.md`. References arrive from the `moodboard` skill with one job each; a bare link gets one job here, and a technique flagged as a trend enters as one ingredient, never the whole style.

Done when every field has a value, each adjective names a visible consequence, the palette has dominant, secondary and accent roles in hex, and the subject vocabulary names an owned metaphor for every subject the targets need.

### 3. Get the original seed

Ask the owner once for something they made: a phone photo of a sketch or silhouette, a scanned texture, a doodle, a hand-tuned SVG. With a seed, every generation starts from it. Without one, run a **thumbnail round**: four to six images of the silhouette only, on the cheapest model and quality, shown as a gallery for the owner to pick from; the pick plus their notes becomes the seed.

Done when `art/<name>/seed/` holds at least one file the owner made or picked, with a line in the README saying what to keep from it.

### 4. Build the identity pack

Follow `references/identity-pack.md` for the family: generate the hero from the seed and the bible, get the owner's approval, then build the sheet (a mascot's turnaround and expressions, or a set's two siblings and its custom style). Write `pack.json`, then validate it and score the sheet against the hero:

```sh
python3 <skill-dir>/references/check.py --pack art/<name>/pack.json
python3 <skill-dir>/references/check.py art/<name>/pack.json art/<name>/sheet/* --sheet art/<name>/sheet.png
```

Done when the owner approved the hero, `check.py --pack` reports 0 errors, and every sheet panel passes against the hero.

### 5. Generate

Generate each target from the pack through the loop in `references/generate.md`: the hero and the closest sheet panel as references, one change per call, the prompt template, a cost quote before any batch, and a log line per call. `references/vendors.md` says which model handles which operation.

Done when every target has a raw file in `art/<name>/raw/` and a line in `art/<name>/log.jsonl` with prompt, model, references, cost and job ID.

### 6. Clean

```sh
python3 <skill-dir>/references/postprocess.py normalize art/<name>/raw/* --out art/<name>/out/
```

Then, as the bible says: `snap` SVG colours to the palette, lay the owner's `texture` over raster art, cut an `edge`, and `export` each target size or the `--icon` set. Run `postprocess.py --help` for each command's flags.

Done when every file in `art/<name>/out/` opens as its extension says, every SVG has no full-canvas background, and every target exists at its size with no upscale warning.

### 7. Check drift

```sh
python3 <skill-dir>/references/check.py art/<name>/pack.json art/<name>/out/* --sheet art/<name>/drift.png
```

Open `drift.png`: the hero first, each image beside it, and a greyscale row underneath for the value test. `check.py` scores identity, not obedience, so judge two things per image by eye and add them as columns: **change made** (a near-copy of the hero passes every metric) and **identity held** (each feature the identity text rules out is still absent, such as a mouth on a mouthless mascot). Look also for what the numbers miss: a second rendering style, a light from the other side, a stock metaphor. For each finding, regenerate from the hero with the one fix as the change, or `snap` flat art; when a deliberate change recurs on three or more images, promote it into the bible and record why.

Render the result in chat: the `check.py` table, then each finding with its fix, then `drift.png`.

Done when every image passes or has a finding with its fix, and `drift.png` has been looked at.

## Working habits

- Restart from the hero, in a fresh call or chat, when two variations in a row drift. A drifted image is evidence, never a new base.
- A new hero is a new pack version: `pack.json` `version` goes up and earlier outputs keep the version they were made with.
- Report the credit balance before and after each round, and the cost of each retry.
- The owner reads galleries, not descriptions: show images, then one line per choice.

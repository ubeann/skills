# The identity pack

Everything a later image is generated from and scored against, versioned in one folder.

## Folder

```
art/<name>/
  README.md     the art bible, targets, credit balances, decisions
  pack.json     machine-readable identity (below)
  seed/         what the owner made or picked
  hero/         the approved hero, one file per version (hero-v1.png, hero-v2.png)
  sheet/        turnaround and expressions (mascot), siblings (set)
  raw/          vendor downloads, untouched
  out/          cleaned, shippable files
  log.jsonl     one line per generation call
  drift.png     the latest contact sheet
  rig/          parts and state poses, for a mascot that will move (below)
```

## pack.json

```json
{
  "name": "oliver",
  "version": 1,
  "family": "mascot",
  "hero": "hero/hero-v1.png",
  "sheet": ["sheet/front.png", "sheet/three-quarter.png", "sheet/side.png", "sheet/back.png",
            "sheet/happy.png", "sheet/thinking.png"],
  "identity_text": "A small round snow monster, body 1.2 heads tall, white fur with pale blue #cfe3f7 shading, two short rounded horns, large black oval eyes set wide, no mouth, stubby arms, no feet visible. Flat vector with soft cel shading, no outlines, light from the upper left.",
  "prompt_suffix": "",
  "palette": {
    "dominant": ["#ffffff", "#cfe3f7"],
    "secondary": ["#6d3df5"],
    "accent": ["#ffb020"],
    "neutral": ["#111111"]
  },
  "styles": {"recraft": {"style_id": "<uuid>", "model": "recraftv4_1_raster"}},
  "soul_id": null,
  "checks": {"shape_min": 0.75}
}
```

- `family` is `mascot`, `set`, `scene` or `icon`. Mascot and icon packs get the silhouette check.
- `palette` roles are `dominant`, `secondary`, `accent`, `neutral`; values are `#RRGGBB`.
- `checks` overrides any default threshold in `check.py` (its source lists them). Loosen one only with a reason in the README.
- `styles` holds one entry per vendor model: a Recraft style ID works only with the model it was created for.

## Mascot

1. **Hero**: one front-facing, full-body image in a neutral pose on a plain light background, made from the seed. The owner approves it before anything else is generated.
2. **Identity text**: 30 to 90 words naming body shape, proportions, colours in hex, eyes, the one memorable feature, and the rendering and light. Paste it into every prompt **verbatim**; a reworded description slowly changes the character. Describe what the character has, completely: "its face is only two small black ovals" holds where "no mouth" does not. In the toolbox comparison, two of four models added a smile to a "no mouth" mascot as soon as the prompt asked for a happy expression.
3. **Turnaround**: front, three-quarter, side, back, same scale, same plain background, flat even light, generated from the hero. A sheet whose panels disagree teaches the disagreement to every later image, so score each panel against the hero before keeping it.
4. **Expressions**: one per product state the mascot will appear in, generated from the front panel: neutral, happy (success), thinking (loading), surprised, sorry (error), working (empty state).
5. **Base construction**: when several mascots form a family, they share the eye and face design, the line and the rendering, and differ in silhouette and colour.

Ask for one figure per image; a sheet given as a reference is copied as a layout unless the prompt says the sheet is for identity only.

## Rig pack

For a mascot that `motion-direction` will animate, in Rive or in code. A runtime moves parts, and one flat image has none: a mascot rigged from a single generated image moved clunkily until the same character was generated in more poses ([video at 8:30](https://www.youtube.com/watch?v=Hrcq00y9EhU&t=510s)).

1. **States first.** Take the state list from the motion beat sheet's state table (rest, wave, celebrate, sorry). Every state needs a pose; rest is the hero's pose.
2. **Poses as style frames.** Generate one still per state from the front panel, one change per call (the pose), and score each against the hero like any sheet panel. These are the frames the owner approves before any motion, and the targets the animation lands on.
3. **Parts.** Split the rest pose into the layers the states move: body, head, each eye open and closed, each mouth shape the states need (none for a mouthless mascot), each limb, each prop. Flat vector art: `vectorize_image` on Recraft, then group the paths by part and name each group. Raster or soft 3D art: cut each part's mask from the approved pose and fill the hole behind it with `erase_region` or `inpaint_image`, so the part can move without exposing a gap. Generate a missing part (closed eyes, a raised arm) from the hero with the part as the one change.
4. **Pivots and order.** For each part, record its pivot (where it rotates from: a shoulder, the neck, the base) in rest-pose pixels, and the drawing order from back to front.

```
rig/
  parts.svg       or parts/<part>.png at the rest pose's size and position
  poses/<state>.png
  rig.md          | Part | File or group | Pivot (x, y) | Order | Moves in states |
```

Done when the parts, stacked in order at their positions, reproduce the rest pose (lay them over the hero and compare), and every state in the beat sheet has an approved pose.

## Set and scene

1. **Hero**: the first image the owner approves, chosen from the thumbnail round or generated from the seed.
2. **Siblings**: two more images with different subjects in the same bible, approved by the owner. Hero plus siblings define the style.
3. **Custom style**: on Recraft, create the style from the hero and the siblings, your own approved images. A style built from someone else's crops keeps their identity.
4. **Prompt suffix**: one shared ending with rendering, light, palette hex and composition, appended to every prompt unchanged. The subject varies; the suffix never does.

## Icon

An app icon wins on appeal and clarity, so a character beats an abstract mark ([post](https://x.com/Kubai087/status/2116744536034824457)):

- The **character carries the personality, the canvas or an accessory carries the function**: the mascot holds the product's object, or the background shows it.
- **Few details** on the subject, so it reads at 29 px.
- **Contrast as high as the palette allows**; add an outline and a drop shadow when the subject does not separate from the background.
- **Peek crop**: tilt the subject and let it enter from an edge so only part shows. The eye goes to the face, and small flaws fall outside the frame.

Generate at 1024 on the mascot pack's hero and sheet, then `postprocess.py export --icon` writes every size and the favicon. Check it at 16 and 29 px before approving.

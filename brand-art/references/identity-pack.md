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

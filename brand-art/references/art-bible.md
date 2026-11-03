# The art bible

Every decision the model would otherwise make for you, written down before generation. Fill each field in `art/<name>/README.md`. The sources behind each rule are linked at their field.

## 1. Three adjectives, each made visible

An adjective the model cannot see is a mood. Tie each to something drawn:

| Adjective | Visible consequence |
|---|---|
| calm | one subject per image, 40% empty sky, no motion lines |
| warm | key light from the upper left in gold, shadows in teal, never grey |
| crafted | visible paper grain over everything, a torn edge on every frame |

## 2. Three nots, each a concrete pattern

"Not generic" is a mood. "Not a glossy 3D render beside flat shapes" is a pattern the check can catch. Write each not beside the positive rule that replaces it.

## 3. Shape language

- **Primary shape** and what it says: circles read friendly, squares stable, triangles energetic.
- **Corners**: one treatment for everything (soft, sharp, or squircle).
- **Proportion**: for a mascot the head-to-body ratio and the size of the eyes relative to the head; for a set, how much of the frame the subject fills.

## 4. Line

None, or one weight as a share of the canvas (for example 1.5% of the short side), and its colour. A line weight that changes between images is the fastest way a set stops matching.

## 5. Rendering and light

- **Rendering**, one of: flat, flat with grain, soft 3D, painterly, engraved or halftone, pixel, paper cut. Mixing two inside one set is a not.
- **Shading steps**: how many tones per colour (flat 2, soft 3D continuous).
- **One light**: direction, key colour, shadow colour. Every image in the family shares it.

## 6. Palette

Hex values with roles, in the proportion **60-30-10**: 60% dominant sets the mood, 30% secondary keeps it interesting, 10% accent is the focal point ([video at 4:55](https://www.youtube.com/watch?v=krFQKuxwBZg&t=295s)). Add the neutrals the art uses (paper, ink). These go into `pack.json`, and `check.py` scores against them.

- **Saturation belongs to the focal point**; background elements stay muted ([video at 5:40](https://www.youtube.com/watch?v=krFQKuxwBZg&t=340s)).
- **Value beats hue**: the image must still read in greyscale ([video at 4:15](https://www.youtube.com/watch?v=krFQKuxwBZg&t=255s)). Decide whether the subject is light on dark or dark on light.
- A palette named in the prompt is a request, not a guarantee; Recraft says colours carried from references are "not guaranteed". The check and `snap` enforce it.

## 7. Texture

Where the grain or surface comes from: a texture the owner scanned or photographed (paper, fabric, rock), the vendor style, or none. An owned texture laid over in post (`postprocess.py texture`) is the cheapest identity there is: one scan carries detail no other product has ([video at 1:00](https://www.youtube.com/watch?v=dEbFRb_fZKQ&t=60s)).

## 8. Composition

- Subjects per image, and how much of the frame they fill.
- Background: transparent, a flat colour, or full bleed.
- Safe zones where text sits on top (a cover's title band), kept calm.
- Crop rules: centred, rule of thirds, or the icon **peek crop** (`references/identity-pack.md`).
- Work large to small: the big shapes read first, detail comes last.

## 9. Subject vocabulary

One row per subject the targets need, with the metaphor this product owns. A stock metaphor (a compass for "introduction", a cylinder for "database") belongs to every product and so to none. Take metaphors from the product's own world: its place, its users' tools, its mascot.

| Subject | Stock metaphor (avoid) | Owned metaphor |
|---|---|---|
| introduction | compass on a map | the mascot opening the handbook's own cover |
| data checks | magnifier over a cylinder | the mascot sorting rice-field terraces into rows |

Gaps in what you can describe convincingly are filled with **studies**: collect references for that one thing and note its shapes before generating ([video at 22:44](https://www.youtube.com/watch?v=aLMS8IVKbPo&t=1364s)).

## 10. Signature quirk

One small recurring detail that is yours, repeated in every image: a gold thread, the mascot's scarf, a volume pressing against a face. It is what makes a style a style ([video at 7:05](https://www.youtube.com/watch?v=aLMS8IVKbPo&t=425s)). Link it to the signature element in `DESIGN.md` when one exists.

## 11. References, one job each

| Reference | Job | What is taken | Everything else |
|---|---|---|---|
| a halftone landing page from the moodboard | technique: halftone on a classical subject | dot size and density | ignored |

A job is one of: technique, palette, shape, pose, composition. One reference per job. A reference copied whole ("match that feel exactly") hands over its author's identity, not yours. A custom style built from someone else's crops is still their style; build it from your own approved outputs (`references/identity-pack.md`).

## Worked example: the handbook set

Its custom style (built from three crops of another designer's posters) gave all 13 images one grain and one sky. That was the only locked field. What drifted:

- **Rendering** was not fixed: a glossy 3D database cylinder sits beside a flat book.
- **Accent** was not enforced: the warning triangle came out orange, off palette. `check.py` flags exactly that image (off-palette 7.4%), and one laptop needed a "not orange" retry.
- **Subjects** were stock: compass, cylinder, magnifier, warning sign. The set could illustrate any handbook.
- **Style** came from the reference crops, so the identity belonged to the designer who made them.

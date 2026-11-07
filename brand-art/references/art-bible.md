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
- **Proportion**: for a mascot the head-to-body ratio and the size of the eyes relative to the head; for a set, how much of the frame the subject fills. Write proportions as numbers and push the distinctive ones further than feels right: the model pulls every proportion back toward the average ([video at 6:15](https://www.youtube.com/watch?v=QeuEpK4KBVw&t=375s)).
- **One shape leads.** A costume or prop adds at most one secondary shape, and it can live in the accessories ([video at 12:05](https://www.youtube.com/watch?v=4iw8XLusQ7s&t=725s)).
- **Rest areas**: detail on the one piece that identifies the subject, plain shapes elsewhere. When everything is detailed nothing reads ([video at 26:13](https://www.youtube.com/watch?v=4iw8XLusQ7s&t=1573s)).
- **A dark body needs air**: gaps between limbs and body, a light rim where a dark limb crosses the dark body, and props in bright colours (a navy notebook and a blue chair vanished on this repo's navy character), or they merge into one shape ([video at 12:08](https://www.youtube.com/watch?v=t-8FuHla3H0&t=728s)).

## 4. Line

None, or one weight as a share of the canvas (for example 1.5% of the short side), and its colour. Hand-inked art fixes a pair instead: the silhouette weight and a thinner interior weight, thicker again at contact shadows and tight curves ([video at 5:42](https://www.youtube.com/watch?v=-wK7gADHjJ0&t=342s)). A line weight that changes between images is the fastest way a set stops matching.

Line colour is an identity lever: a tinted ink (deep maroon, violet) reads softer and more owned than black ([video at 6:06](https://www.youtube.com/watch?v=RQA_t-H_ZKM&t=366s)). Cleanup and vectorising straighten the gesture out of a line; compare the cleaned file with the raw one at viewing size ([video at 1:30](https://www.youtube.com/watch?v=-wK7gADHjJ0&t=90s)).

## 5. Rendering and light

- **Rendering**, one of: flat, flat with grain, soft 3D, painterly, engraved or halftone, pixel, paper cut. Mixing two inside one set is a not.
- **Shading steps**: how many tones per colour (flat 2, soft 3D continuous).
- **One light**: direction, key colour, shadow colour. Every image in the family shares it.

## 6. Palette

Hex values with roles, in the proportion **60-30-10**: 60% dominant sets the mood, 30% secondary keeps it interesting, 10% accent is the focal point ([video at 4:55](https://www.youtube.com/watch?v=krFQKuxwBZg&t=295s)). Add the neutrals the art uses (paper, ink). These go into `pack.json`, and `check.py` scores against them.

- **Saturation belongs to the focal point**; background elements stay muted ([video at 5:40](https://www.youtube.com/watch?v=krFQKuxwBZg&t=340s)).
- **Value beats hue**: the image must still read in greyscale ([video at 4:15](https://www.youtube.com/watch?v=krFQKuxwBZg&t=255s)). Decide whether the subject is light on dark or dark on light.
- **Tint the extremes.** A large pure-white area reads unfinished and a large black one heavy; tint both, and keep the brightest light and the strongest accent above the centre line, near the face. A bright accent at the feet pulls the eye off the face ([video at 13:24](https://www.youtube.com/watch?v=-t8DGGYVne8&t=804s); [video at 9:03](https://www.youtube.com/watch?v=-t8DGGYVne8&t=543s)).
- A palette named in the prompt is a request, not a guarantee; Recraft says colours carried from references are "not guaranteed". The check and `snap` enforce it.

## 7. Texture

Where the grain or surface comes from: a texture the owner scanned or photographed (paper, fabric, rock), the vendor style, or none. An owned texture laid over in post (`postprocess.py texture`) is the cheapest identity there is: one scan carries detail no other product has ([video at 1:00](https://www.youtube.com/watch?v=dEbFRb_fZKQ&t=60s)).

## 8. Composition

- Subjects per image, and how much of the frame they fill.
- Background: transparent, a flat colour, or full bleed.
- Safe zones where text sits on top (a cover's title band), kept calm.
- Crop rules: centred, rule of thirds, or the icon **peek crop** (`references/identity-pack.md`).
- Work large to small: the big shapes read first, detail comes last.
- A layout of several figures or with text (a banner, a card set) follows `compose.md`.

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

## 12. Costumes and casts

When one character wears a costume per job, or several characters form a cast:

- **An intent sentence per costume**, one lead theme tied by one idea. A costume that needs a paragraph to justify it fails ([video at 4:22](https://www.youtube.com/watch?v=4iw8XLusQ7s&t=262s); [video at 1:05](https://www.youtube.com/watch?v=bXcMQbmJuQw&t=65s)).
- **Hallmarks**: the character's constants plus two or three tools the job really uses, each drawn with its category's telltale part (a film reel's sprocket holes, a compass's needle) ([video at 5:27](https://www.youtube.com/watch?v=bXcMQbmJuQw&t=327s); [video at 9:22](https://www.youtube.com/watch?v=j9cHhwmeNRM&t=562s)).
- **Worn, not cosplay**: every prop is held, strapped or worn, and a strap can carry the accent colour ([video at 18:19](https://www.youtube.com/watch?v=-t8DGGYVne8&t=1099s)).
- **The identifying piece on or near the head**, because avatars and icon tiles crop to the head ([video at 22:51](https://www.youtube.com/watch?v=4iw8XLusQ7s&t=1371s)).
- **Unity**: one organising colour and one motif shared by every costume (a badge, a stitch, a tag) ([video at 7:11](https://www.youtube.com/watch?v=rm0wi0afoKM&t=431s); [video at 15:41](https://www.youtube.com/watch?v=bXcMQbmJuQw&t=941s)).
- **Guess test**: show each costume without its label; the job is named from it, and an item that names another job comes out ([video at 6:31](https://www.youtube.com/watch?v=bXcMQbmJuQw&t=391s)).
- **Review as a lineup**: the whole cast side by side at one scale, so two costumes with the same silhouette show ([video at 16:30](https://www.youtube.com/watch?v=rm0wi0afoKM&t=990s)).

## Worked example: the handbook set

Its custom style (built from three crops of another designer's posters) gave all 13 images one grain and one sky. That was the only locked field. What drifted:

- **Rendering** was not fixed: a glossy 3D database cylinder sits beside a flat book.
- **Accent** was not enforced: the warning triangle came out orange, off palette. `check.py` flags exactly that image (off-palette 7.4%), and one laptop needed a "not orange" retry.
- **Subjects** were stock: compass, cylinder, magnifier, warning sign. The set could illustrate any handbook.
- **Style** came from the reference crops, so the identity belonged to the designer who made them.

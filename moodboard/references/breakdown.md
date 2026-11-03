# Breaking down a reference

Fill these fields in `card.json`. The palette is already measured by `fetch.py`; correct it only when the image is mostly UI chrome or background.

| Field | What goes in |
|---|---|
| `techniques` | tags from the vocabulary below, most distinctive first |
| `jobs` | the jobs this reference could do on a board, from the job list |
| `subject` | what it depicts or what kind of screen it is, in a few words |
| `identity` | the part that makes it its author's: the specific subject, scene, character, copy or brand. A project never takes this part |
| `notes` | measured values (sizes, dot pitch, a hex), and anything the next reader needs without opening the images |

## Jobs

A board gives each reference one of these, and each job one reference.

| Job | Taken from the reference |
|---|---|
| `technique` | a rendering method: grain, halftone, engraving, soft 3D |
| `palette` | colour values and their proportion |
| `type` | family, scale, weight, letter-spacing (measured with `inventory.js`) |
| `layout` | structure: what is on the screen and in what order |
| `shape` | corner treatment, shape language, silhouette |
| `pose` | a character pose or gesture |
| `composition` | framing and crop: centred, peek crop, safe zones |
| `motion` | how something moves or changes state |
| `copy` | voice and tone |

## Technique vocabulary

Use an existing tag when it fits, so the trend count works; add a new one only for a technique none of these name, in lowercase with hyphens, and add it to this list in the same change.

- **Rendering**: `flat-vector`, `flat-grain`, `soft-3d`, `clay`, `glass`, `painterly`, `gouache`, `watercolour`, `grain-print`, `risograph`, `halftone`, `dither`, `engraving`, `line-art`, `pixel`, `paper-cut`, `collage`, `photo-cutout`, `gradient-mesh`
- **Character**: `mascot-icon`, `mascot-empty-state`, `kawaii`, `blob-character`, `object-with-face`, `character-family`
- **Composition**: `image-behind-type`, `peek-crop`, `full-bleed-scene`, `single-object-on-sky`, `torn-edge`, `sticker-outline`, `centred-subject`
- **Interaction and motion**: `time-of-day`, `scroll-reveal`, `cursor-reactive`, `state-morph`
- **Type**: `serif-display`, `grotesk-tight`, `mono-accent`, `mixed-serif-sans`

## Worked examples

Four posts saved on 2026-11-03:

| Reference | techniques | jobs | identity (never taken) |
|---|---|---|---|
| [@PranavOriginals](https://x.com/PranavOriginals/status/2116568393809883579): three agency heroes | `grain-print`, `image-behind-type` | technique, palette | the roof, rose and dune scenes and that exact cerulean-to-peach sky |
| [@yasirahmadnoori](https://x.com/yasirahmadnoori/status/2116457744337391974): four AI-tool landing pages from one prompt | `halftone`, `engraving`, `dither`, `image-behind-type` | technique | the prompt template: its logo row and copy repeat on every page made with it |
| [@Kubai087](https://x.com/Kubai087/status/2116744536034824457): six mascot app icons, with written rules | `mascot-icon`, `peek-crop`, `soft-3d` | composition | each app's own creature |
| [@kshvbgde](https://x.com/kshvbgde/status/2117179351477497970): a portfolio hero with a day-to-night slider | `dither`, `pixel`, `time-of-day` | technique, motion | the temple scene and its labels |

Three of the four share one family of techniques within three days: print-like imagery (grain, halftone, dither) behind clean type. That is what a trend looks like in the library, and why one of them entering a project is enough. The handbook illustrations took the first post's technique, palette and subjects together, so their identity was the author's.
